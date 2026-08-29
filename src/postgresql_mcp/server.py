"""DB Bridge — Bridge your AI assistant to PostgreSQL databases.
Stateless protocol (2026-07-28): no global session state, explicit config per request.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from fastmcp import FastMCP

from postgresql_mcp.core import PostgreSQLCore
from postgresql_mcp.models import PostgreSQLConfig

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

logger = structlog.get_logger(__name__)

# Module-level connection pool (infrastructure, not session state)
_pool: Any | None = None
_pool_config: PostgreSQLConfig | None = None


async def _ensure_pool(config: PostgreSQLConfig) -> None:
    """Ensure the connection pool exists (lazy initialization)."""
    global _pool, _pool_config
    if _pool is None or _pool_config != config:
        from asyncpg import create_pool
        _pool = await create_pool(
            dsn=str(config.dsn),
            min_size=1,
            max_size=config.pool_size,
            command_timeout=config.query_timeout,
        )
        _pool_config = config


def create_core(config: PostgreSQLConfig | None = None) -> PostgreSQLCore:
    """Create a PostgreSQLCore instance with shared pool (stateless - no session state)."""
    config = config or PostgreSQLConfig()
    core = PostgreSQLCore(config)
    return core


async def _get_core(config: PostgreSQLConfig | None = None) -> PostgreSQLCore:
    """Get a fresh core instance with initialized pool."""
    config = config or PostgreSQLConfig()
    await _ensure_pool(config)
    core = create_core(config)
    core.pool = _pool
    return core


# Create FastMCP app (no lifespan - stateless)
mcp = FastMCP("DB Bridge")


@mcp.tool()
async def query(sql: str, params: list[Any] | None = None) -> dict[str, Any]:
    """Execute a parameterized SELECT query and return rows.

    Args:
        sql: Parameterized SELECT SQL query (use $1, $2, etc. for parameters)
        params: Optional list of query parameters

    Returns:
        Dictionary with rows, row_count, columns, and execution_time_ms

    Example:
        query("SELECT * FROM users WHERE id = $1", [1])
        query("SELECT * FROM users WHERE name ILIKE $1", ["%john%"])
    """
    core = await _get_core()
    return await core.query(sql, params)


@mcp.tool()
async def execute(sql: str, params: list[Any] | None = None) -> dict[str, Any]:
    """Execute a parameterized INSERT, UPDATE, or DELETE statement.

    Args:
        sql: Parameterized DML SQL statement (use $1, $2, etc. for parameters)
        params: Optional list of statement parameters

    Returns:
        Dictionary with affected_rows and execution_time_ms

    Raises:
        Error if server is in read-only mode

    Example:
        execute("INSERT INTO users (name, email) VALUES ($1, $2)", ["John", "john@example.com"])
        execute("UPDATE users SET name = $1 WHERE id = $2", ["Jane", 1])
        execute("DELETE FROM users WHERE id = $1", [1])
    """
    core = await _get_core()
    return await core.execute(sql, params)


@mcp.tool()
async def list_tables(schema: str = "public") -> dict[str, Any]:
    """List all tables in a schema.

    Args:
        schema: Schema name to list tables from (default: "public")

    Returns:
        Dictionary with tables list and schema name

    Example:
        list_tables("public")
        list_tables("information_schema")
    """
    core = await _get_core()
    tables = await core.list_tables(schema)
    return {"tables": tables, "schema_name": schema}


@mcp.tool()
async def describe_table(table: str, schema: str = "public") -> dict[str, Any]:
    """Describe a table's structure including columns, indexes, and constraints.

    Args:
        table: Table name to describe
        schema: Schema name containing the table (default: "public")

    Returns:
        Dictionary with table, schema, columns, indexes, and constraints

    Example:
        describe_table("users")
        describe_table("orders", "sales")
    """
    core = await _get_core()
    return await core.describe_table(table, schema)


@mcp.tool()
async def run_migration(sql: str) -> dict[str, Any]:
    """Run a database migration (DDL statements) in a transaction.

    Args:
        sql: Migration SQL containing one or more DDL statements separated by semicolons

    Returns:
        Dictionary with success, execution_time_ms, and statements_executed

    Raises:
        Error if server is in read-only mode

    Example:
        run_migration("CREATE TABLE test (id SERIAL PRIMARY KEY, name TEXT); CREATE INDEX idx_test_name ON test(name);")
    """
    core = await _get_core()
    return await core.run_migration(sql)


@mcp.tool()
async def explain_analyze(sql: str, params: list[Any] | None = None) -> dict[str, Any]:
    """Get query execution plan with costs using EXPLAIN ANALYZE.

    Args:
        sql: Parameterized SQL query to analyze (use $1, $2, etc. for parameters)
        params: Optional list of query parameters

    Returns:
        Dictionary with plan (list of plan nodes), execution_time_ms, and planning_time_ms

    Example:
        explain_analyze("SELECT * FROM users WHERE id = $1", [1])
        explain_analyze("SELECT * FROM users WHERE name ILIKE $1", ["%john%"])
    """
    core = await _get_core()
    return await core.explain_analyze(sql, params)


def main() -> None:
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
