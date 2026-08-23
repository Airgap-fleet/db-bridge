"""Core database operations for PostgreSQL MCP Server.

This module contains the synchronous core functionality for PostgreSQL database operations.
FastMCP imports should NOT be present in this module for testability.
"""

import time
import logging
from typing import Any, Dict, List, Optional, Union

from asyncpg import Pool  # type: ignore[import-untyped]
from pydantic import PostgresDsn  # type: ignore[import-untyped]

from postgresql_mcp.models import PostgreSQLConfig

logger = logging.getLogger(__name__)


class PostgreSQLCore:
    """Core database operations for PostgreSQL MCP Server."""

    def __init__(self, config: PostgreSQLConfig):
        self.config = config
        self.pool: Optional[Pool] = None

    async def initialize(self) -> None:
        """Initialize database connection pool."""
        try:
            self.pool = await self._create_pool()
            logger.info("PostgreSQL connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL pool: {e}")
            raise

    async def _create_pool(self) -> Pool:
        """Create and return a connection pool."""
        from asyncpg import create_pool

        return await create_pool(
            dsn=str(self.config.dsn),
            min_size=1,
            max_size=self.config.pool_size,
            command_timeout=self.config.query_timeout,
        )

    async def close(self) -> None:
        """Close the connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("PostgreSQL connection pool closed")

    # --- Methods expected by tests (backward compatible names) ---

    async def execute_query(self, sql: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        """Execute a SELECT query and return results with timing."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")

        start_time = time.perf_counter()
        async with self.pool.acquire() as conn:
            try:
                rows = await conn.fetch(sql, *(params or []))
                columns = list(rows[0].keys()) if rows else []

                execution_time_ms = (time.perf_counter() - start_time) * 1000

                result = {
                    "rows": [dict(row) for row in rows],
                    "row_count": len(rows),
                    "columns": columns,
                    "execution_time_ms": execution_time_ms,
                }
                logger.debug(f"Query executed successfully: {sql[:100]}...")
                return result

            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                raise

    async def execute_dml(self, sql: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        """Execute a DML (INSERT, UPDATE, DELETE) statement with timing."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")

        start_time = time.perf_counter()
        async with self.pool.acquire() as conn:
            try:
                async with conn.transaction():
                    result = await conn.execute(sql, *(params or []))
                    affected_rows = int(result.split()[0]) if result else 0

                    execution_time_ms = (time.perf_counter() - start_time) * 1000

                    dml_result = {
                        "affected_rows": affected_rows,
                        "execution_time_ms": execution_time_ms,
                    }
                    logger.debug(f"DML executed successfully: {sql[:100]}...")
                    return dml_result

            except Exception as e:
                logger.error(f"DML execution failed: {e}")
                raise

    # --- New API methods (used by server.py tools) ---

    async def query(self, sql: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        """Execute a parameterized SELECT query and return rows (new API)."""
        return await self.execute_query(sql, params)

    async def execute(self, sql: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        """Execute a parameterized INSERT, UPDATE, or DELETE statement (new API)."""
        return await self.execute_dml(sql, params)

    async def list_tables(self, schema_name: str = "public") -> List[str]:
        """List all tables in a schema."""
        sql = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = $1 AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """

        result = await self.execute_query(sql, [schema_name])
        return [row["table_name"] for row in result["rows"]]

    async def describe_table(self, table: str, schema: str = "public") -> Dict[str, Any]:
        """Get detailed information about a table."""
        # Get column information
        columns_sql = """
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length,
            numeric_precision,
            numeric_scale,
            column_key
        FROM information_schema.columns
        WHERE table_schema = $1 AND table_name = $2
        ORDER BY ordinal_position
        """

        columns_result = await self.execute_query(columns_sql, [schema, table])
        columns = columns_result["rows"]

        # Get index information
        indexes_sql = """
        SELECT
            index_name,
            column_name,
            non_unique
        FROM information_schema.statistics
        WHERE table_schema = $1 AND table_name = $2 AND index_name IS NOT NULL
        ORDER BY index_name, seq_in_index
        """

        indexes_result = await self.execute_query(indexes_sql, [schema, table])
        indexes_by_name = {}

        for index_row in indexes_result["rows"]:
            index_name = index_row["index_name"]
            if index_name not in indexes_by_name:
                indexes_by_name[index_name] = {
                    "name": index_name,
                    "columns": [],
                    "is_unique": index_row["non_unique"] == 0,
                    "is_primary": False,
                }
            indexes_by_name[index_name]["columns"].append(index_row["column_name"])

        # Get primary key information
        pk_sql = """
        SELECT
            column_name
        FROM information_schema.key_column_usage
        WHERE table_schema = $1 AND table_name = $2 AND constraint_name IN (
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_schema = $1 AND table_name = $2 AND constraint_type = 'PRIMARY KEY'
        )
        ORDER BY ordinal_position
        """

        pk_result = await self.execute_query(pk_sql, [schema, table])

        for index in indexes_by_name.values():
            if set(index["columns"]) == set([row["column_name"] for row in pk_result["rows"]]):
                index["is_primary"] = True

        indexes = list(indexes_by_name.values())

        # Get constraint information
        constraints_sql = """
        SELECT
            constraint_name,
            constraint_type,
            column_name,
            referenced_table_name,
            referenced_column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
            AND tc.table_name = kcu.table_name
        WHERE tc.table_schema = $1 AND tc.table_name = $2
        ORDER BY constraint_name
        """

        constraints_result = await self.execute_query(constraints_sql, [schema, table])

        constraints_by_name = {}

        for constraint_row in constraints_result["rows"]:
            constraint_name = constraint_row["constraint_name"]

            if constraint_name not in constraints_by_name:
                constraints_by_name[constraint_name] = {
                    "name": constraint_name,
                    "constraint_type": constraint_row["constraint_type"],
                    "columns": [],
                    "referenced_table": constraint_row["referenced_table_name"],
                    "referenced_columns": [],
                }

            constraints_by_name[constraint_name]["columns"].append(constraint_row["column_name"])
            if constraint_row["referenced_column_name"]:
                constraints_by_name[constraint_name]["referenced_columns"].append(
                    constraint_row["referenced_column_name"]
                )

        constraints = list(constraints_by_name.values())

        return {
            "table": table,
            "schema": schema,
            "columns": columns,
            "indexes": indexes,
            "constraints": constraints,
        }

    async def run_migration(self, sql: str) -> Dict[str, Any]:
        """Run a database migration (DDL statements)."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")

        async with self.pool.acquire() as conn:
            try:
                statements_executed = 0
                execution_time_ms: float = 0.0

                # Split SQL by semicolons and execute each statement
                statements = [stmt.strip() for stmt in sql.split(";") if stmt.strip()]

                async with conn.transaction():
                    for statement in statements:
                        start_time = time.perf_counter()
                        await conn.execute(statement)
                        execution_time_ms += (time.perf_counter() - start_time) * 1000
                        statements_executed += 1

                return {
                    "success": True,
                    "execution_time_ms": execution_time_ms,
                    "statements_executed": statements_executed,
                }

            except Exception as e:
                logger.error(f"Migration failed: {e}")
                return {
                    "success": False,
                    "execution_time_ms": 0,
                    "statements_executed": 0,
                }

    async def explain_analyze(self, sql: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        """Execute EXPLAIN ANALYZE on a query."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")

        async with self.pool.acquire() as conn:
            try:
                # Format parameters for EXPLAIN
                if params:
                    formatted_sql = sql
                    for i, param in enumerate(params):
                        placeholder = f"${i + 1}"
                        formatted_sql = formatted_sql.replace(placeholder, repr(param))
                    explain_sql = f"EXPLAIN ANALYZE {formatted_sql}"
                else:
                    explain_sql = f"EXPLAIN ANALYZE {sql}"

                start_time = time.perf_counter()
                plan_result = await conn.fetch(explain_sql)
                execution_time_ms = (time.perf_counter() - start_time) * 1000

                # Parse the plan result
                plan = []
                for row in plan_result:
                    plan.append(dict(row))

                return {
                    "plan": plan,
                    "execution_time_ms": execution_time_ms,
                    "planning_time_ms": 0,
                }

            except Exception as e:
                logger.error(f"EXPLAIN ANALYZE failed: {e}")
                raise