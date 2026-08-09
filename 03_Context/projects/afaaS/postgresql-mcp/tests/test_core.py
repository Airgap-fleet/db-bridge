"""Tests for PostgreSQLCore business logic."""

from __future__ import annotations

import pytest

from postgresql_mcp.core import PostgreSQLCore, PostgreSQLError, ReadOnlyError
from postgresql_mcp.models import (
    DescribeTableRequest,
    ExecuteRequest,
    ExplainAnalyzeRequest,
    ListTablesRequest,
    QueryRequest,
    RunMigrationRequest,
)


class TestPostgreSQLCoreQuery:
    """Tests for query method."""

    async def test_query_simple_select(self, core):
        """Test simple SELECT query."""
        request = QueryRequest(sql="SELECT * FROM test_users ORDER BY id")
        response = await core.query(request)

        assert response.row_count == 3
        assert len(response.rows) == 3
        assert "id" in response.columns
        assert "name" in response.columns
        assert "email" in response.columns
        assert "age" in response.columns
        assert response.execution_time_ms > 0

    async def test_query_with_params(self, core):
        """Test parameterized SELECT query."""
        request = QueryRequest(sql="SELECT * FROM test_users WHERE id = $1", params=[1])
        response = await core.query(request)

        assert response.row_count == 1
        assert response.rows[0]["name"] == "Alice"
        assert response.rows[0]["email"] == "alice@example.com"

    async def test_query_with_multiple_params(self, core):
        """Test SELECT with multiple parameters."""
        request = QueryRequest(
            sql="SELECT * FROM test_users WHERE age > $1 AND age < $2",
            params=[20, 40]
        )
        response = await core.query(request)

        assert response.row_count == 3

    async def test_query_no_results(self, core):
        """Test SELECT returning no rows."""
        request = QueryRequest(sql="SELECT * FROM test_users WHERE id = $1", params=[999])
        response = await core.query(request)

        assert response.row_count == 0
        assert response.rows == []
        assert response.columns == []

    async def test_query_invalid_sql(self, core):
        """Test invalid SQL raises error."""
        request = QueryRequest(sql="SELECT * FROM nonexistent_table")
        with pytest.raises(PostgreSQLError) as exc:
            await core.query(request)
        assert exc.value.code == "QUERY_FAILED"

    async def test_query_malformed_params(self, core):
        """Test query with wrong parameter count."""
        request = QueryRequest(sql="SELECT * FROM test_users WHERE id = $1 AND name = $2", params=[1])
        with pytest.raises(PostgreSQLError) as exc:
            await core.query(request)
        assert exc.value.code == "QUERY_FAILED"


class TestPostgreSQLCoreExecute:
    """Tests for execute method."""

    async def test_execute_insert(self, core):
        """Test INSERT statement."""
        request = ExecuteRequest(
            sql="INSERT INTO test_users (name, email, age) VALUES ($1, $2, $3)",
            params=["David", "david@example.com", 28]
        )
        response = await core.execute(request)

        assert response.affected_rows == 1
        assert response.execution_time_ms > 0

        # Verify insertion
        verify = await core.query(QueryRequest(sql="SELECT * FROM test_users WHERE email = $1", params=["david@example.com"]))
        assert verify.row_count == 1
        assert verify.rows[0]["name"] == "David"

    async def test_execute_update(self, core):
        """Test UPDATE statement."""
        request = ExecuteRequest(
            sql="UPDATE test_users SET age = $1 WHERE id = $2",
            params=[31, 1]
        )
        response = await core.execute(request)

        assert response.affected_rows == 1

        # Verify update
        verify = await core.query(QueryRequest(sql="SELECT age FROM test_users WHERE id = 1"))
        assert verify.rows[0]["age"] == 31

    async def test_execute_delete(self, core):
        """Test DELETE statement."""
        request = ExecuteRequest(
            sql="DELETE FROM test_users WHERE id = $1",
            params=[3]
        )
        response = await core.execute(request)

        assert response.affected_rows == 1

        # Verify deletion
        verify = await core.query(QueryRequest(sql="SELECT * FROM test_users WHERE id = 3"))
        assert verify.row_count == 0

    async def test_execute_no_rows_affected(self, core):
        """Test UPDATE with no matching rows."""
        request = ExecuteRequest(
            sql="UPDATE test_users SET age = 99 WHERE id = $1",
            params=[999]
        )
        response = await core.execute(request)

        assert response.affected_rows == 0

    async def test_execute_invalid_sql(self, core):
        """Test invalid DML raises error."""
        request = ExecuteRequest(sql="INSERT INTO nonexistent (col) VALUES ($1)", params=["test"])
        with pytest.raises(PostgreSQLError) as exc:
            await core.execute(request)
        assert exc.value.code == "EXECUTE_FAILED"

    async def test_execute_read_only_mode(self, core_read_only):
        """Test execute raises ReadOnlyError in read-only mode."""
        request = ExecuteRequest(sql="INSERT INTO test_users (name, email) VALUES ($1, $2)", params=["Test", "test@test.com"])
        with pytest.raises(ReadOnlyError) as exc:
            await core_read_only.execute(request)
        assert exc.value.code == "READ_ONLY"


class TestPostgreSQLCoreListTables:
    """Tests for list_tables method."""

    async def test_list_tables_public_schema(self, core):
        """Test listing tables in public schema."""
        request = ListTablesRequest(schema="public")
        response = await core.list_tables(request)

        assert response.schema == "public"
        assert "test_users" in response.tables
        assert "test_orders" in response.tables

    async def test_list_tables_information_schema(self, core):
        """Test listing tables in information_schema."""
        request = ListTablesRequest(schema="information_schema")
        response = await core.list_tables(request)

        assert response.schema == "information_schema"
        assert len(response.tables) > 0  # Should have system tables

    async def test_list_tables_nonexistent_schema(self, core):
        """Test listing tables in non-existent schema."""
        request = ListTablesRequest(schema="nonexistent_schema")
        response = await core.list_tables(request)

        assert response.schema == "nonexistent_schema"
        assert response.tables == []


class TestPostgreSQLCoreDescribeTable:
    """Tests for describe_table method."""

    async def test_describe_table_users(self, core):
        """Test describing test_users table."""
        request = DescribeTableRequest(table="test_users", schema="public")
        response = await core.describe_table(request)

        assert response.table == "test_users"
        assert response.schema == "public"
        assert len(response.columns) == 5  # id, name, email, age, created_at

        # Check column details
        col_names = [c.name for c in response.columns]
        assert "id" in col_names
        assert "name" in col_names
        assert "email" in col_names
        assert "age" in col_names
        assert "created_at" in col_names

        # Check primary key
        id_col = next(c for c in response.columns if c.name == "id")
        assert id_col.is_primary_key is True
        assert id_col.is_nullable is False

        # Check unique column
        email_col = next(c for c in response.columns if c.name == "email")
        assert email_col.is_unique is True

        # Check indexes
        index_names = [i.name for i in response.indexes]
        assert "idx_test_users_email" in index_names

        # Check constraints
        constraint_names = [c.name for c in response.constraints]
        assert any("test_users_pkey" in name for name in constraint_names)
        assert any("test_users_email_key" in name for name in constraint_names)

    async def test_describe_table_orders(self, core):
        """Test describing test_orders table with foreign key."""
        request = DescribeTableRequest(table="test_orders", schema="public")
        response = await core.describe_table(request)

        assert response.table == "test_orders"
        assert len(response.columns) == 5  # id, user_id, product, amount, status

        # Check foreign key constraint
        fk_constraints = [c for c in response.constraints if c.type == "FOREIGN KEY"]
        assert len(fk_constraints) == 1
        assert fk_constraints[0].referenced_table == "test_users"
        assert fk_constraints[0].referenced_columns == ["id"]

    async def test_describe_table_nonexistent(self, core):
        """Test describing non-existent table."""
        request = DescribeTableRequest(table="nonexistent_table", schema="public")
        with pytest.raises(PostgreSQLError):
            await core.describe_table(request)
        # Note: This might not raise an error but return empty results
        # Depending on the query behavior


class TestPostgreSQLCoreRunMigration:
    """Tests for run_migration method."""

    async def test_run_migration_create_table(self, core):
        """Test running a CREATE TABLE migration."""
        sql = """
            CREATE TABLE migration_test (
                id SERIAL PRIMARY KEY,
                data TEXT NOT NULL
            );
            CREATE INDEX idx_migration_test_data ON migration_test(data);
        """
        request = RunMigrationRequest(sql=sql)
        response = await core.run_migration(request)

        assert response.success is True
        assert response.statements_executed == 2
        assert response.execution_time_ms > 0

        # Verify table exists
        tables = await core.list_tables(ListTablesRequest(schema="public"))
        assert "migration_test" in tables.tables

        # Clean up
        await core.execute(ExecuteRequest(sql="DROP TABLE migration_test"))

    async def test_run_migration_multiple_statements(self, core):
        """Test migration with multiple DDL statements."""
        sql = """
            CREATE TABLE multi_test_1 (id INT PRIMARY KEY);
            CREATE TABLE multi_test_2 (id INT PRIMARY KEY);
            CREATE TABLE multi_test_3 (id INT PRIMARY KEY);
        """
        request = RunMigrationRequest(sql=sql)
        response = await core.run_migration(request)

        assert response.success is True
        assert response.statements_executed == 3

        # Clean up
        await core.execute(ExecuteRequest(sql="DROP TABLE multi_test_1, multi_test_2, multi_test_3"))

    async def test_run_migration_transaction_rollback(self, core):
        """Test migration rolls back on error."""
        sql = """
            CREATE TABLE rollback_test (id INT PRIMARY KEY);
            INSERT INTO rollback_test (id) VALUES (1);
            INVALID SQL STATEMENT;
            CREATE TABLE should_not_exist (id INT PRIMARY KEY);
        """
        request = RunMigrationRequest(sql=sql)

        with pytest.raises(PostgreSQLError) as exc:
            await core.run_migration(request)
        assert exc.value.code == "MIGRATION_FAILED"

        # Verify rollback - tables should not exist
        tables = await core.list_tables(ListTablesRequest(schema="public"))
        assert "rollback_test" not in tables.tables
        assert "should_not_exist" not in tables.tables

    async def test_run_migration_read_only_mode(self, core_read_only):
        """Test migration raises ReadOnlyError in read-only mode."""
        request = RunMigrationRequest(sql="CREATE TABLE readonly_test (id INT)")
        with pytest.raises(ReadOnlyError) as exc:
            await core_read_only.run_migration(request)
        assert exc.value.code == "READ_ONLY"


class TestPostgreSQLCoreExplainAnalyze:
    """Tests for explain_analyze method."""

    async def test_explain_analyze_simple(self, core):
        """Test EXPLAIN ANALYZE on simple query."""
        request = ExplainAnalyzeRequest(sql="SELECT * FROM test_users WHERE id = $1", params=[1])
        response = await core.explain_analyze(request)

        assert len(response.plan) > 0
        assert response.execution_time_ms > 0
        assert response.planning_time_ms >= 0

        # Check plan structure
        plan_node = response.plan[0]
        assert "Node Type" in plan_node
        assert "Actual Total Time" in plan_node or "Total Cost" in plan_node

    async def test_explain_analyze_join(self, core):
        """Test EXPLAIN ANALYZE on join query."""
        request = ExplainAnalyzeRequest(
            sql="""
                SELECT u.name, o.product
                FROM test_users u
                JOIN test_orders o ON u.id = o.user_id
                WHERE u.id = $1
            """,
            params=[1]
        )
        response = await core.explain_analyze(request)

        assert len(response.plan) > 0
        plan_node = response.plan[0]
        assert "Node Type" in plan_node

    async def test_explain_analyze_invalid_sql(self, core):
        """Test EXPLAIN ANALYZE with invalid SQL."""
        request = ExplainAnalyzeRequest(sql="SELECT * FROM nonexistent_table")
        with pytest.raises(PostgreSQLError) as exc:
            await core.explain_analyze(request)
        assert exc.value.code == "EXPLAIN_ANALYZE_FAILED"


class TestPostgreSQLCoreErrors:
    """Tests for error handling."""

    async def test_pool_not_initialized(self):
        """Test using core without initialization raises error."""
        from postgresql_mcp.models import PostgreSQLConfig
        config = PostgreSQLConfig(dsn="postgresql://invalid")
        core = PostgreSQLCore(config)
        # Don't initialize

        with pytest.raises(PostgreSQLError) as exc:
            await core.query(QueryRequest(sql="SELECT 1"))
        assert exc.value.code == "POOL_NOT_INITIALIZED"

    async def test_connection_failure(self):
        """Test connection failure handling."""
        from postgresql_mcp.models import PostgreSQLConfig
        config = PostgreSQLConfig(dsn="postgresql://invalid:invalid@localhost:5432/invalid")
        core = PostgreSQLCore(config)

        with pytest.raises(PostgreSQLError):
            await core.initialize()
