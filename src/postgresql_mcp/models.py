"""Pydantic models for PostgreSQL MCP Server.

All models follow Pydantic v2 patterns with proper validation and serialization.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from postgresql_mcp.env import apply_legacy_env


class PostgreSQLConfig(BaseSettings):
    """PostgreSQL connection configuration.

    Canonical env prefix is ``DB_BRIDGE_`` (for example ``DB_BRIDGE_DSN``).
    Legacy ``POSTGRES_*`` and ``POSTGRESQL_MCP_*`` names are mapped when unset.
    """

    dsn: str = Field(
        default="postgresql://postgres:***@localhost:5432/postgres",
        description="PostgreSQL connection string",
    )
    pool_size: int = Field(default=10, ge=1, le=100, description="Connection pool size")
    read_only: bool = Field(default=False, description="Enforce read-only transactions")
    query_timeout: float = Field(default=30.0, gt=0, le=300, description="Query timeout in seconds")
    log_level: str = Field(default="INFO", description="Logging level")

    model_config = SettingsConfigDict(
        env_prefix="DB_BRIDGE_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # Rebuild env sources after mapping so a snapshot taken at
        # construction time cannot miss newly copied DB_BRIDGE_* values.
        del env_settings
        apply_legacy_env()
        mapped_env = EnvSettingsSource(settings_cls)
        return (init_settings, mapped_env, dotenv_settings, file_secret_settings)


class QueryRequest(BaseModel):
    """Request for executing a parameterized SELECT query."""

    sql: str = Field(
        ...,
        min_length=1,
        description="Parameterized SQL query (use $1, $2, etc. for parameters)",
    )
    params: list[Any] | None = Field(
        default=None,
        description="Optional list of query parameters",
    )


class QueryResponse(BaseModel):
    """Response for a SELECT query."""

    rows: list[dict[str, Any]]
    row_count: int
    columns: list[str]
    execution_time_ms: float


class ExecuteRequest(BaseModel):
    """Request for executing a parameterized INSERT, UPDATE, or DELETE."""

    sql: str = Field(
        ...,
        min_length=1,
        description="Parameterized SQL statement (use $1, $2, etc. for parameters)",
    )
    params: list[Any] | None = Field(
        default=None,
        description="Optional list of statement parameters",
    )


class ExecuteResponse(BaseModel):
    """Response for an INSERT, UPDATE, or DELETE statement."""

    affected_rows: int
    execution_time_ms: float


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
    schema_name: str
    table_count: int


class ColumnInfo(BaseModel):
    """Information about a table column."""

    name: str
    data_type: str
    is_nullable: bool
    default: str | None = None
    is_primary_key: bool = False
    is_unique: bool = False


class IndexInfo(BaseModel):
    """Information about a table index."""

    name: str
    columns: list[str]
    is_unique: bool
    is_primary: bool = False
    index_type: str = "btree"


class ConstraintInfo(BaseModel):
    """Information about a table constraint."""

    name: str
    constraint_type: str = Field(..., alias="type")
    columns: list[str]
    referenced_table: str | None = None
    referenced_columns: list[str] | None = None

    @property
    def type(self) -> str:
        """Return constraint_type for compatibility with tests."""
        return self.constraint_type


class DescribeTableRequest(BaseModel):
    """Request for describing a table."""

    table: str = Field(
        ...,
        min_length=1,
        description="Table name to describe",
    )
    schema_name: str = Field(
        default="public",
        min_length=1,
        description="Schema name",
        alias="schema",
    )


class DescribeTableResponse(BaseModel):
    """Response for describing a table."""

    table: str
    schema_name: str = Field(..., alias="schema")
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

    plan: list[dict[str, Any]]
    execution_time_ms: float
    planning_time_ms: float
