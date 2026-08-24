"""Pydantic models for PostgreSQL MCP Server tools and configuration."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgreSQLConfig(BaseSettings):
    """Configuration for PostgreSQL MCP Server."""

    model_config = SettingsConfigDict(
        env_prefix="POSTGRESQL_MCP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    dsn: PostgresDsn = Field(
        default=PostgresDsn("postgresql://postgres:***@localhost:5432/postgres"),
        description="PostgreSQL connection string",
    )

    pool_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Connection pool size",
    )

    read_only: bool = Field(
        default=False,
        description="Enable read-only mode (blocks execute, run_migration)",
    )

    query_timeout: float = Field(
        default=30.0,
        gt=0,
        le=300,
        description="Query timeout in seconds",
    )

    log_level: str = Field(
        default="INFO",
        description="Structured logging level",
    )


class QueryRequest(BaseModel):
    """Request for parameterized SELECT query."""

    sql: str = Field(
        ...,
        min_length=1,
        description="Parameterized SELECT SQL query (use $1, $2, etc. for parameters)",
    )

    params: list[Any] | None = Field(
        default=None,
        description="Optional list of query parameters",
    )


class QueryResponse(BaseModel):
    """Response for SELECT query."""

    rows: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Query result rows as list of dictionaries",
    )

    row_count: int = Field(
        ...,
        ge=0,
        description="Number of rows returned",
    )

    columns: list[str] = Field(
        default_factory=list,
        description="Column names in result",
    )

    execution_time_ms: float = Field(
        ...,
        ge=0,
        description="Query execution time in milliseconds",
    )


class ExecuteRequest(BaseModel):
    """Request for parameterized INSERT, UPDATE, DELETE statement."""

    sql: str = Field(
        ...,
        min_length=1,
        description="Parameterized DML SQL statement (use $1, $2, etc. for parameters)",
    )

    params: list[Any] | None = Field(
        default=None,
        description="Optional list of statement parameters",
    )


class ExecuteResponse(BaseModel):
    """Response for INSERT, UPDATE, DELETE statement."""

    affected_rows: int = Field(
        ...,
        ge=0,
        description="Number of rows affected",
    )

    execution_time_ms: float = Field(
        ...,
        ge=0,
        description="Statement execution time in milliseconds",
    )


class ListTablesRequest(BaseModel):
    """Request for listing tables in a schema."""

    schema_name: str = Field(
        default="public",
        min_length=1,
        description="Schema name to list tables from",
    )


class ListTablesResponse(BaseModel):
    """Response for listing tables."""

    tables: list[str] = Field(
        default_factory=list,
        description="List of table names",
    )

    schema_name: str = Field(
        ...,
        description="Schema name that was queried",
    )


class ColumnInfo(BaseModel):
    """Information about a table column."""

    name: str
    data_type: str
    is_nullable: bool
    column_default: str | None = None
    character_maximum_length: int | None = None
    numeric_precision: int | None = None
    numeric_scale: int | None = None
    is_primary_key: bool = False
    is_unique: bool = False


class IndexInfo(BaseModel):
    """Information about a table index."""

    name: str
    columns: list[str]
    is_unique: bool
    is_primary: bool = False


class ConstraintInfo(BaseModel):
    """Information about a table constraint."""

    name: str
    constraint_type: str = Field(..., alias="type")
    columns: list[str]
    referenced_table: str | None = None
    referenced_columns: list[str] | None = None

    @property
    def type(self) -> str:
        """Alias for constraint_type to match test expectations."""
        return self.constraint_type


class DescribeTableRequest(BaseModel):
    """Request for describing a table."""

    table: str = Field(..., min_length=1, description="Table name to describe")
    schema_: str = Field(default="public", min_length=1, description="Schema name", alias="schema")


class DescribeTableResponse(BaseModel):
    """Response for describing a table."""

    model_config = ConfigDict(populate_by_name=True)

    table: str
    schema_: str = Field(..., alias="schema")
    columns: list[ColumnInfo]
    indexes: list[IndexInfo] = Field(default_factory=list)
    constraints: list[ConstraintInfo] = Field(default_factory=list)


class RunMigrationRequest(BaseModel):
    """Request for running a database migration."""

    sql: str = Field(
        ...,
        min_length=1,
        description="Migration SQL containing one or more DDL statements separated by semicolons",
    )


class RunMigrationResponse(BaseModel):
    """Response for running a migration."""

    success: bool
    execution_time_ms: float
    statements_executed: int


class ExplainAnalyzeRequest(BaseModel):
    """Request for query execution plan with costs."""

    sql: str = Field(
        ...,
        min_length=1,
        description="Parameterized SQL query to analyze (use $1, $2, etc. for parameters)",
    )

    params: list[Any] | None = Field(
        default=None,
        description="Optional list of query parameters",
    )


class ExplainAnalyzeResponse(BaseModel):
    """Response for EXPLAIN ANALYZE."""

    plan: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Query execution plan nodes",
    )

    execution_time_ms: float = Field(
        ...,
        ge=0,
        description="Query execution time in milliseconds",
    )

    planning_time_ms: float = Field(
        ...,
        ge=0,
        description="Query planning time in milliseconds",
    )
