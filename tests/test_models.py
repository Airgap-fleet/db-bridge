"""Tests for Pydantic models."""

from __future__ import annotations

import re

import pytest
from pydantic import ValidationError

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


def _parse_dsn_password(dsn) -> str:
    """Extract password from PostgresDsn (str() masks it for security)."""
    dsn_str = str(dsn)
    match = re.search(r"://[^:]+:([^@]+)@", dsn_str)
    return match.group(1) if match else ""


class TestPostgreSQLConfig:
    """Tests for PostgreSQLConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = PostgreSQLConfig()
        # str(dsn) masks password for security, so we check the host/port/db
        dsn_str = str(config.dsn)
        assert dsn_str.startswith("postgresql://postgres:")
        assert "@localhost:5432/postgres" in dsn_str
        assert config.pool_size == 10
        assert config.read_only is False
        assert config.query_timeout == 30.0
        assert config.log_level == "INFO"

    def test_custom_config(self):
        """Test custom configuration values."""
        config = PostgreSQLConfig(
            dsn="postgresql://user:password@host:5432/db",
            pool_size=20,
            read_only=True,
            query_timeout=60.0,
            log_level="DEBUG",
        )
        # str(dsn) masks password, so check host/port/db
        dsn_str = str(config.dsn)
        assert dsn_str.startswith("postgresql://user:")
        assert "@host:5432/db" in dsn_str
        assert config.pool_size == 20
        assert config.read_only is True
        assert config.query_timeout == 60.0
        assert config.log_level == "DEBUG"

    def test_pool_size_validation(self):
        """Test pool_size validation."""
        with pytest.raises(ValidationError):
            PostgreSQLConfig(pool_size=0)
        with pytest.raises(ValidationError):
            PostgreSQLConfig(pool_size=101)

    def test_query_timeout_validation(self):
        """Test query_timeout validation."""
        with pytest.raises(ValidationError):
            PostgreSQLConfig(query_timeout=0)
        with pytest.raises(ValidationError):
            PostgreSQLConfig(query_timeout=301)


class TestQueryModels:
    """Tests for Query request/response models."""

    def test_query_request_valid(self):
        """Test valid QueryRequest."""
        request = QueryRequest(sql="SELECT * FROM users", params=[1, "test"])
        assert request.sql == "SELECT * FROM users"
        assert request.params == [1, "test"]

    def test_query_request_no_params(self):
        """Test QueryRequest without params."""
        request = QueryRequest(sql="SELECT * FROM users")
        assert request.params is None

    def test_query_request_empty_sql(self):
        """Test QueryRequest with empty SQL fails."""
        with pytest.raises(ValidationError):
            QueryRequest(sql="")

    def test_query_response(self):
        """Test QueryResponse model."""
        response = QueryResponse(
            rows=[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
            row_count=2,
            columns=["id", "name"],
            execution_time_ms=15.5,
        )
        assert response.row_count == 2
        assert len(response.rows) == 2
        assert response.columns == ["id", "name"]


class TestExecuteModels:
    """Tests for Execute request/response models."""

    def test_execute_request_valid(self):
        """Test valid ExecuteRequest."""
        request = ExecuteRequest(sql="INSERT INTO users (name) VALUES ($1)", params=["Alice"])
        assert request.sql == "INSERT INTO users (name) VALUES ($1)"
        assert request.params == ["Alice"]

    def test_execute_response(self):
        """Test ExecuteResponse model."""
        response = ExecuteResponse(affected_rows=5, execution_time_ms=10.2)
        assert response.affected_rows == 5
        assert response.execution_time_ms == 10.2


class TestListTablesModels:
    """Tests for ListTables request/response models."""

    def test_list_tables_request_default(self):
            """Test ListTablesRequest with default schema."""
            request = ListTablesRequest()
            assert request.schema_name == "public"

    def test_list_tables_request_custom_schema(self):
                """Test ListTablesRequest with custom schema."""
                request = ListTablesRequest(schema_name="sales")
                assert request.schema_name == "sales"

    def test_list_tables_response(self):
            """Test ListTablesResponse model."""
            response = ListTablesResponse(tables=["users", "orders"], schema_name="public")
            assert response.tables == ["users", "orders"]
            assert response.schema_name == "public"


class TestDescribeTableModels:
    """Tests for DescribeTable models."""

    def test_describe_table_request(self):
        """Test DescribeTableRequest model."""
        request = DescribeTableRequest(table="users", schema_="public")
        assert request.table == "users"
        assert request.schema_ == "public"

    def test_describe_table_request_default_schema(self):
        """Test DescribeTableRequest with default schema."""
        request = DescribeTableRequest(table="users")
        assert request.schema_ == "public"

    def test_column_info(self):
        """Test ColumnInfo model."""
        col = ColumnInfo(
            name="id",
            data_type="integer",
            is_nullable=False,
            default="nextval('users_id_seq'::regclass)",
            is_primary_key=True,
            is_unique=False,
        )
        assert col.name == "id"
        assert col.is_primary_key is True
        assert col.is_nullable is False

    def test_index_info(self):
        """Test IndexInfo model."""
        idx = IndexInfo(
            name="idx_users_email",
            columns=["email"],
            is_unique=True,
            is_primary=False,
            index_type="btree",
        )
        assert idx.is_unique is True
        assert idx.is_primary is False

    def test_constraint_info(self):
        """Test ConstraintInfo model."""
        constraint = ConstraintInfo(
            name="users_email_key",
            type="UNIQUE",
            columns=["email"],
        )
        assert constraint.type == "UNIQUE"

    def test_foreign_key_constraint(self):
        """Test foreign key ConstraintInfo."""
        fk = ConstraintInfo(
            name="orders_user_id_fkey",
            type="FOREIGN KEY",
            columns=["user_id"],
            referenced_table="users",
            referenced_columns=["id"],
        )
        assert fk.type == "FOREIGN KEY"
        assert fk.referenced_table == "users"
        assert fk.referenced_columns == ["id"]

    def test_describe_table_response(self):
        """Test DescribeTableResponse model."""
        response = DescribeTableResponse(
            table="users",
            schema="public",
            columns=[
                ColumnInfo(name="id", data_type="integer", is_nullable=False, is_primary_key=True),
                ColumnInfo(name="name", data_type="text", is_nullable=False),
            ],
            indexes=[
                IndexInfo(name="idx_users_name", columns=["name"], is_unique=False, is_primary=False, index_type="btree"),
            ],
            constraints=[
                ConstraintInfo(name="users_pkey", type="PRIMARY KEY", columns=["id"]),
            ],
        )
        assert response.table == "users"
        assert len(response.columns) == 2
        assert len(response.indexes) == 1
        assert len(response.constraints) == 1


class TestRunMigrationModels:
    """Tests for RunMigration models."""

    def test_run_migration_request(self):
        """Test RunMigrationRequest model."""
        request = RunMigrationRequest(sql="CREATE TABLE test (id INT); CREATE INDEX idx ON test(id);")
        assert "CREATE TABLE" in request.sql
        assert "CREATE INDEX" in request.sql

    def test_run_migration_request_empty_fails(self):
        """Test RunMigrationRequest with empty SQL fails."""
        with pytest.raises(ValidationError):
            RunMigrationRequest(sql="")

    def test_run_migration_response(self):
        """Test RunMigrationResponse model."""
        response = RunMigrationResponse(
            success=True,
            execution_time_ms=100.5,
            statements_executed=2,
        )
        assert response.success is True
        assert response.statements_executed == 2


class TestExplainAnalyzeModels:
    """Tests for ExplainAnalyze models."""

    def test_explain_analyze_request(self):
        """Test ExplainAnalyzeRequest model."""
        request = ExplainAnalyzeRequest(sql="SELECT * FROM users WHERE id = $1", params=[1])
        assert request.sql == "SELECT * FROM users WHERE id = $1"
        assert request.params == [1]

    def test_explain_analyze_request_no_params(self):
        """Test ExplainAnalyzeRequest without params."""
        request = ExplainAnalyzeRequest(sql="SELECT * FROM users")
        assert request.params is None

    def test_explain_analyze_response(self):
        """Test ExplainAnalyzeResponse model."""
        response = ExplainAnalyzeResponse(
            plan=[{"Node Type": "Seq Scan", "Relation Name": "users", "Actual Total Time": 5.5}],
            execution_time_ms=10.0,
            planning_time_ms=0.5,
        )
        assert len(response.plan) == 1
        assert response.plan[0]["Node Type"] == "Seq Scan"
        assert response.planning_time_ms == 0.5


class TestModelSerialization:
    """Tests for model serialization/deserialization."""

    def test_query_request_json_roundtrip(self):
        """Test QueryRequest JSON serialization roundtrip."""
        original = QueryRequest(sql="SELECT * FROM users WHERE id = $1", params=[42])
        json_data = original.model_dump()
        restored = QueryRequest(**json_data)
        assert restored.sql == original.sql
        assert restored.params == original.params

    def test_describe_table_response_json_roundtrip(self):
            """Test DescribeTableResponse JSON serialization roundtrip."""
            original = DescribeTableResponse(
                table="users",
                schema_="public",
                columns=[
                    ColumnInfo(name="id", data_type="integer", is_nullable=False, is_primary_key=True),
                ],
            )
            json_data = original.model_dump(by_alias=True)
            restored = DescribeTableResponse(**json_data)
            assert restored.table == original.table
            assert len(restored.columns) == 1
            assert restored.columns[0].name == "id"

    def test_config_env_parsing(self, monkeypatch):
        """Test PostgreSQLConfig parsing from environment variables."""
        monkeypatch.setenv("POSTGRESQL_MCP_DSN", "postgresql://env:password@env:5432/env")
        monkeypatch.setenv("POSTGRESQL_MCP_POOL_SIZE", "25")
        monkeypatch.setenv("POSTGRESQL_MCP_READ_ONLY", "true")
        monkeypatch.setenv("POSTGRESQL_MCP_QUERY_TIMEOUT", "45.5")
        monkeypatch.setenv("POSTGRESQL_MCP_LOG_LEVEL", "WARNING")

        config = PostgreSQLConfig()
        assert _parse_dsn_password(config.dsn) == "password"
        assert str(config.dsn).startswith("postgresql://env:")
        assert config.pool_size == 25
        assert config.read_only is True
        assert config.query_timeout == 45.5
        assert config.log_level == "WARNING"
