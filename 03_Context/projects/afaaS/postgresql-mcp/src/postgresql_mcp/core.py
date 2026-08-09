"""Business logic for PostgreSQL MCP Server - zero FastMCP imports, fully testable."""

from __future__ import annotations

import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import asyncpg
import structlog
from asyncpg import Pool

from postgresql_mcp.models import (
    ColumnInfo,
    ConstraintInfo,
    DescribeTableRequest,
    DescribeTableResponse,
    ExecuteRequest,
    ExecuteResponse,
    ExplainAnalyzeRequest,
    ExplainAnalyzeResponse,
    IndexInfo,
    ListTablesRequest,
    ListTablesResponse,
    PostgreSQLConfig,
    QueryRequest,
    QueryResponse,
    RunMigrationRequest,
    RunMigrationResponse,
)

logger = structlog.get_logger(__name__)


class PostgreSQLError(Exception):
    """Base exception for PostgreSQL MCP errors."""

    def __init__(self, message: str, code: str = "POSTGRESQL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class ReadOnlyError(PostgreSQLError):
    """Raised when write operation attempted in read-only mode."""

    def __init__(self, operation: str):
        super().__init__(
            f"Operation '{operation}' not allowed in read-only mode",
            code="READ_ONLY",
        )


class QueryTimeoutError(PostgreSQLError):
    """Raised when query exceeds timeout."""

    def __init__(self, timeout: float):
        super().__init__(
            f"Query exceeded timeout of {timeout}s",
            code="QUERY_TIMEOUT",
        )


class PostgreSQLCore:
    """Core business logic for PostgreSQL operations.

    This class contains zero FastMCP imports and is fully testable in isolation.
    All methods are synchronous wrappers around async operations for testability,
    but the actual implementation uses asyncpg for async database operations.
    """

    def __init__(self, config: PostgreSQLConfig):
        """Initialize PostgreSQLCore with configuration."""
        self.config = config
        self._pool: Pool | None = None

    @property
    def pool(self) -> Pool:
        """Get the connection pool, raising if not initialized."""
        if self._pool is None:
            raise PostgreSQLError("Connection pool not initialized", code="POOL_NOT_INITIALIZED")
        return self._pool

    async def initialize(self) -> None:
        """Initialize the connection pool."""
        if self._pool is not None:
            return

        logger.info("initializing_connection_pool", pool_size=self.config.pool_size)

        self._pool = await asyncpg.create_pool(
            dsn=str(self.config.dsn),
            min_size=1,
            max_size=self.config.pool_size,
            command_timeout=self.config.query_timeout,
        )

        logger.info("connection_pool_initialized", pool_size=self.config.pool_size)

    async def close(self) -> None:
        """Close the connection pool."""
        if self._pool is not None:
            logger.info("closing_connection_pool")
            await self._pool.close()
            self._pool = None
            logger.info("connection_pool_closed")

    @asynccontextmanager
    async def _acquire_connection(self) -> AsyncIterator[asyncpg.Connection]:
        """Acquire a connection from the pool."""
        async with self.pool.acquire() as conn:
            yield conn

    def _validate_read_only(self, operation: str) -> None:
        """Validate that write operations are allowed."""
        if self.config.read_only:
            raise ReadOnlyError(operation)

    async def query(self, request: QueryRequest) -> QueryResponse:
        """Execute a parameterized SELECT query.

        Args:
            request: QueryRequest with SQL and optional parameters

        Returns:
            QueryResponse with rows, column info, and execution time

        Raises:
            PostgreSQLError: On query execution failure
        """
        start_time = time.perf_counter()

        logger.info("executing_query", sql=request.sql[:100], params_count=len(request.params) if request.params else 0)

        try:
            async with self._acquire_connection() as conn:
                if request.params:
                    rows = await conn.fetch(request.sql, *request.params)
                else:
                    rows = await conn.fetch(request.sql)

            execution_time_ms = (time.perf_counter() - start_time) * 1000

            # Convert asyncpg Records to dicts
            result_rows = [dict(row) for row in rows]
            columns = list(rows[0].keys()) if rows else []

            logger.info("query_completed", row_count=len(result_rows), execution_time_ms=execution_time_ms)

            return QueryResponse(
                rows=result_rows,
                row_count=len(result_rows),
                columns=columns,
                execution_time_ms=execution_time_ms,
            )

        except asyncpg.PostgresError as e:
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            logger.error("query_failed", error=str(e), execution_time_ms=execution_time_ms)
            raise PostgreSQLError(f"Query failed: {e}", code="QUERY_FAILED") from e

    async def execute(self, request: ExecuteRequest) -> ExecuteResponse:
        """Execute a parameterized INSERT/UPDATE/DELETE statement.

        Args:
            request: ExecuteRequest with SQL and optional parameters

        Returns:
            ExecuteResponse with affected row count and execution time

        Raises:
            ReadOnlyError: If server is in read-only mode
            PostgreSQLError: On statement execution failure
        """
        self._validate_read_only("execute")

        start_time = time.perf_counter()

        logger.info("executing_dml", sql=request.sql[:100], params_count=len(request.params) if request.params else 0)

        try:
            async with self._acquire_connection() as conn:
                if request.params:
                    result = await conn.execute(request.sql, *request.params)
                else:
                    result = await conn.execute(request.sql)

            execution_time_ms = (time.perf_counter() - start_time) * 1000

            # asyncpg returns "INSERT 0 1", "UPDATE 5", "DELETE 3" etc.
            # Parse the affected row count
            affected_rows = 0
            if result:
                parts = result.split()
                if len(parts) >= 2:
                    try:
                        affected_rows = int(parts[-1])
                    except ValueError:
                        pass

            logger.info("dml_completed", affected_rows=affected_rows, execution_time_ms=execution_time_ms)

            return ExecuteResponse(
                affected_rows=affected_rows,
                execution_time_ms=execution_time_ms,
            )

        except asyncpg.PostgresError as e:
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            logger.error("dml_failed", error=str(e), execution_time_ms=execution_time_ms)
            raise PostgreSQLError(f"Execute failed: {e}", code="EXECUTE_FAILED") from e

    async def list_tables(self, request: ListTablesRequest) -> ListTablesResponse:
        """List all tables in a schema.

        Args:
            request: ListTablesRequest with schema name

        Returns:
            ListTablesResponse with table names
        """
        start_time = time.perf_counter()

        logger.info("listing_tables", schema=request.schema_name)

        sql = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = $1
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """

        try:
            async with self._acquire_connection() as conn:
                rows = await conn.fetch(sql, request.schema_name)

            execution_time_ms = (time.perf_counter() - start_time) * 1000
            tables = [row["table_name"] for row in rows]

            logger.info("tables_listed", schema=request.schema_name, count=len(tables), execution_time_ms=execution_time_ms)

            return ListTablesResponse(
                tables=tables,
                schema_name=request.schema_name,
            )

        except asyncpg.PostgresError as e:
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            logger.error("list_tables_failed", schema=request.schema, error=str(e), execution_time_ms=execution_time_ms)
            raise PostgreSQLError(f"List tables failed: {e}", code="LIST_TABLES_FAILED") from e

    async def describe_table(self, request: DescribeTableRequest) -> DescribeTableResponse:
        """Describe a table's structure including columns, indexes, and constraints.

        Args:
            request: DescribeTableRequest with table and schema names

        Returns:
            DescribeTableResponse with detailed table structure
        """
        start_time = time.perf_counter()

        logger.info("describing_table", table=request.table, schema=request.schema_name)

        # Query for columns
        columns_sql = """
            SELECT
                c.column_name,
                c.data_type,
                c.is_nullable = 'YES' as is_nullable,
                c.column_default,
                c.character_maximum_length,
                c.numeric_precision,
                c.numeric_scale,
                CASE WHEN pk.column_name IS NOT NULL THEN true ELSE false END as is_primary_key,
                CASE WHEN uk.column_name IS NOT NULL THEN true ELSE false END as is_unique
            FROM information_schema.columns c
            LEFT JOIN (
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                WHERE tc.constraint_type = 'PRIMARY KEY'
                AND tc.table_name = $1
                AND tc.table_schema = $2
            ) pk ON c.column_name = pk.column_name
            LEFT JOIN (
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                WHERE tc.constraint_type = 'UNIQUE'
                AND tc.table_name = $1
                AND tc.table_schema = $2
            ) uk ON c.column_name = uk.column_name
            WHERE c.table_name = $1
            AND c.table_schema = $2
            ORDER BY c.ordinal_position
        """

        # Query for indexes
        indexes_sql = """
            SELECT
                i.relname as index_name,
                array_agg(a.attname ORDER BY a.attnum) as columns,
                ix.indisunique as is_unique,
                ix.indisprimary as is_primary,
                am.amname as index_type
            FROM pg_index ix
            JOIN pg_class i ON i.oid = ix.indexrelid
            JOIN pg_class t ON t.oid = ix.indrelid
            JOIN pg_namespace n ON n.oid = t.relnamespace
            JOIN pg_am am ON am.oid = i.relam
            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
            WHERE t.relname = $1
            AND n.nspname = $2
            AND NOT ix.indisprimary  -- exclude primary key indexes (handled in constraints)
            GROUP BY i.relname, ix.indisunique, ix.indisprimary, am.amname
            ORDER BY i.relname
        """

        # Query for constraints
        constraints_sql = """
            SELECT
                tc.constraint_name,
                tc.constraint_type,
                array_agg(kcu.column_name ORDER BY kcu.ordinal_position) as columns,
                ccu.table_name as referenced_table,
                array_agg(ccu.column_name ORDER BY kcu.ordinal_position) as referenced_columns
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            LEFT JOIN information_schema.constraint_column_usage ccu
                ON tc.constraint_name = ccu.constraint_name
                AND tc.table_schema = ccu.table_schema
            WHERE tc.table_name = $1
            AND tc.table_schema = $2
            GROUP BY tc.constraint_name, tc.constraint_type, ccu.table_name
            ORDER BY tc.constraint_name
        """

        try:
            async with self._acquire_connection() as conn:
                # Fetch columns
                column_rows = await conn.fetch(columns_sql, request.table, request.schema_name)
                columns = [
                    ColumnInfo(
                        name=row["column_name"],
                        data_type=row["data_type"],
                        is_nullable=row["is_nullable"],
                        default=row["column_default"],
                        is_primary_key=row["is_primary_key"],
                        is_unique=row["is_unique"],
                        max_length=row["character_maximum_length"],
                        numeric_precision=row["numeric_precision"],
                        numeric_scale=row["numeric_scale"],
                    )
                    for row in column_rows
                ]

                # Fetch indexes
                index_rows = await conn.fetch(indexes_sql, request.table, request.schema_name)
                indexes = [
                    IndexInfo(
                        name=row["index_name"],
                        columns=row["columns"],
                        is_unique=row["is_unique"],
                        is_primary=row["is_primary"],
                        index_type=row["index_type"],
                    )
                    for row in index_rows
                ]

                # Fetch constraints
                constraint_rows = await conn.fetch(constraints_sql, request.table, request.schema_name)
                constraints = [
                    ConstraintInfo(
                        name=row["constraint_name"],
                        type=row["constraint_type"],
                        columns=row["columns"],
                        referenced_table=row["referenced_table"],
                        referenced_columns=row["referenced_columns"],
                    )
                    for row in constraint_rows
                ]

            execution_time_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                "table_described",
                table=request.table,
                schema=request.schema_name,
                column_count=len(columns),
                index_count=len(indexes),
                constraint_count=len(constraints),
                execution_time_ms=execution_time_ms,
            )

            return DescribeTableResponse(
                table=request.table,
                schema_name=request.schema_name,
                columns=columns,
                indexes=indexes,
                constraints=constraints,
            )

        except asyncpg.PostgresError as e:
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "describe_table_failed",
                table=request.table,
                schema=request.schema,
                error=str(e),
                execution_time_ms=execution_time_ms,
            )
            raise PostgreSQLError(f"Describe table failed: {e}", code="DESCRIBE_TABLE_FAILED") from e

    async def run_migration(self, request: RunMigrationRequest) -> RunMigrationResponse:
        """Run a database migration (DDL statements) in a transaction.

        Args:
            request: RunMigrationRequest with migration SQL

        Returns:
            RunMigrationResponse with execution results

        Raises:
            ReadOnlyError: If server is in read-only mode
            PostgreSQLError: On migration failure
        """
        self._validate_read_only("run_migration")

        start_time = time.perf_counter()

        logger.info("running_migration", sql_length=len(request.sql))

        # Split SQL into individual statements (simple split on semicolon)
        # Note: This is a simple implementation; production might need a proper SQL parser
        statements = [s.strip() for s in request.sql.split(";") if s.strip()]

        try:
            async with self._acquire_connection() as conn:
                async with conn.transaction():
                    for stmt in statements:
                        await conn.execute(stmt)

            execution_time_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                "migration_completed",
                statements_executed=len(statements),
                execution_time_ms=execution_time_ms,
            )

            return RunMigrationResponse(
                success=True,
                execution_time_ms=execution_time_ms,
                statements_executed=len(statements),
            )

        except asyncpg.PostgresError as e:
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            logger.error("migration_failed", error=str(e), execution_time_ms=execution_time_ms)
            raise PostgreSQLError(f"Migration failed: {e}", code="MIGRATION_FAILED") from e

    async def explain_analyze(self, request: ExplainAnalyzeRequest) -> ExplainAnalyzeResponse:
        """Get query execution plan with costs using EXPLAIN ANALYZE.

        Args:
            request: ExplainAnalyzeRequest with SQL and optional parameters

        Returns:
            ExplainAnalyzeResponse with query plan and timing
        """
        start_time = time.perf_counter()

        logger.info("explain_analyze_query", sql=request.sql[:100], params_count=len(request.params) if request.params else 0)

        # Wrap the query in EXPLAIN (ANALYZE, FORMAT JSON)
        explain_sql = "EXPLAIN (ANALYZE, FORMAT JSON) " + request.sql

        try:
            async with self._acquire_connection() as conn:
                if request.params:
                    rows = await conn.fetch(explain_sql, *request.params)
                else:
                    rows = await conn.fetch(explain_sql)

            execution_time_ms = (time.perf_counter() - start_time) * 1000

            # EXPLAIN FORMAT JSON returns a single row with a single column containing the plan
            plan = []
            planning_time_ms = 0.0

            if rows:
                # The result is a JSON array of plan objects
                plan_data = rows[0][0]
                if isinstance(plan_data, list):
                    plan = plan_data
                else:
                    plan = [plan_data]

                # Extract planning time from the plan
                if plan and "Planning Time" in plan[0]:
                    planning_time_ms = float(plan[0]["Planning Time"])

            logger.info("explain_analyze_completed", plan_nodes=len(plan), execution_time_ms=execution_time_ms)

            return ExplainAnalyzeResponse(
                plan=plan,
                execution_time_ms=execution_time_ms,
                planning_time_ms=planning_time_ms,
            )

        except asyncpg.PostgresError as e:
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            logger.error("explain_analyze_failed", error=str(e), execution_time_ms=execution_time_ms)
            raise PostgreSQLError(f"EXPLAIN ANALYZE failed: {e}", code="EXPLAIN_ANALYZE_FAILED") from e
