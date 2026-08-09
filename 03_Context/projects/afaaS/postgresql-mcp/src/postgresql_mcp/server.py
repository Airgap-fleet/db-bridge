"""PostgreSQL MCP Server — FastMCP application with 6 database tools."""

from __future__ import annotations

import logging
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastmcp import FastMCP

from postgresql_mcp.core import PostgreSQLCore
from postgresql_mcp.models import (
    DescribeTableRequest,
    ExecuteRequest,
    ExplainAnalyzeRequest,
    ListTablesRequest,
    PostgreSQLConfig,
    QueryRequest,
    RunMigrationRequest,
)

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

# Global core instance
_core: PostgreSQLCore | None = None


def get_core() -> PostgreSQLCore:
    """Get the global PostgreSQLCore instance."""
    global _core
    if _core is None:
        config = PostgreSQLConfig()
        _core = PostgreSQLCore(config)
    return _core


@asynccontextmanager
async def lifespan(app: FastMCP) -> AsyncIterator[None]:
    """Application lifespan handler for startup/shutdown."""
    global _core
    config = PostgreSQLConfig()
    _core = PostgreSQLCore(config)
    await _core.initialize()
    logger.info("postgresql_mcp_started", pool_size=config.pool_size, read_only=config.read_only)
    try:
        yield
    finally:
        if _core:
            await _core.close()
            logger.info("postgresql_mcp_stopped")


# Create FastMCP app with lifespan
mcp = FastMCP("PostgreSQL MCP Server", lifespan=lifespan)


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
    core = get_core()
    request = QueryRequest(sql=sql, params=params)
    response = await core.query(request)
    return response.model_dump()


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
    core = get_core()
    request = ExecuteRequest(sql=sql, params=params)
    response = await core.execute(request)
    return response.model_dump()


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
    core = get_core()
    request = ListTablesRequest(schema_name=schema)
    response = await core.list_tables(request)
    return response.model_dump()


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
    core = get_core()
    request = DescribeTableRequest(table=table, schema_name=schema)
    response = await core.describe_table(request)
    return response.model_dump()


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
    core = get_core()
    request = RunMigrationRequest(sql=sql)
    response = await core.run_migration(request)
    return response.model_dump()


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
    core = get_core()
    request = ExplainAnalyzeRequest(sql=sql, params=params)
    response = await core.explain_analyze(request)
    return response.model_dump()


def main() -> None:
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
