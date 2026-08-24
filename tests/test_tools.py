"""Integration tests for PostgreSQL MCP Server tools.

These tests require a running PostgreSQL instance and are marked as integration tests.
Run with: pytest -m integration
"""

import pytest

from postgresql_mcp.core import PostgreSQLCore


class TestMCPTools:
    """Integration tests for MCP tools."""

    @pytest.mark.integration
    async def test_query_tool(self, core: PostgreSQLCore):
        """Test query tool."""
        result = await core.query("SELECT * FROM test_users ORDER BY id")
        assert result["row_count"] == 3
        assert len(result["rows"]) == 3
        assert "id" in result["columns"]

    @pytest.mark.integration
    async def test_query_tool_with_params(self, core: PostgreSQLCore):
        """Test query tool with parameters."""
        result = await core.query("SELECT * FROM test_users WHERE id = $1", [1])
        assert result["row_count"] == 1
        assert result["rows"][0]["name"] == "Alice"

    @pytest.mark.integration
    async def test_execute_tool_insert(self, core: PostgreSQLCore):
        """Test execute tool for INSERT."""
        result = await core.execute(
            "INSERT INTO test_users (name, email, age) VALUES ($1, $2, $3)",
            ["Eve", "eve@example.com", 22]
        )
        assert result["affected_rows"] == 1

        # Verify
        verify = await core.query("SELECT * FROM test_users WHERE email = $1", ["eve@example.com"])
        assert verify["row_count"] == 1
        assert verify["rows"][0]["name"] == "Eve"

    @pytest.mark.integration
    async def test_execute_tool_update(self, core: PostgreSQLCore):
        """Test execute tool for UPDATE."""
        result = await core.execute(
            "UPDATE test_users SET age = $1 WHERE id = $2",
            [32, 1]
        )
        assert result["affected_rows"] == 1

        # Verify
        verify = await core.query("SELECT age FROM test_users WHERE id = 1")
        assert verify["rows"][0]["age"] == 32

    @pytest.mark.integration
    async def test_execute_tool_delete(self, core: PostgreSQLCore):
        """Test execute tool for DELETE."""
        # First insert a test user
        await core.execute(
            "INSERT INTO test_users (name, email, age) VALUES ($1, $2, $3)",
            ["Frank", "frank@example.com", 40]
        )

        result = await core.execute("DELETE FROM test_users WHERE email = $1", ["frank@example.com"])
        assert result["affected_rows"] == 1

        # Verify
        verify = await core.query("SELECT * FROM test_users WHERE email = $1", ["frank@example.com"])
        assert verify["row_count"] == 0

    @pytest.mark.integration
    async def test_list_tables_tool(self, core: PostgreSQLCore):
        """Test list_tables tool."""
        result = await core.list_tables("public")
        assert result["schema"] == "public"
        assert "test_users" in result["tables"]
        assert "test_orders" in result["tables"]

    @pytest.mark.integration
    async def test_describe_table_tool(self, core: PostgreSQLCore):
        """Test describe_table tool."""
        result = await core.describe_table("test_users")
        assert result["table"] == "test_users"
        assert result["schema"] == "public"
        assert len(result["columns"]) == 5

        # Check column details
        col_names = [c["name"] for c in result["columns"]]
        assert "id" in col_names
        assert "email" in col_names

        # Check primary key
        id_col = next(c for c in result["columns"] if c["name"] == "id")
        assert id_col["is_primary_key"] is True

        # Check indexes
        index_names = [i["name"] for i in result["indexes"]]
        assert "idx_test_users_email" in index_names

    @pytest.mark.integration
    async def test_run_migration_tool(self, core: PostgreSQLCore):
        """Test run_migration tool."""
        sql = """
            CREATE TABLE tool_migration_test (
                id SERIAL PRIMARY KEY,
                value TEXT
            )
        """
        result = await core.run_migration(sql)
        assert result["success"] is True
        assert result["statements_executed"] == 1

        # Verify
        tables = await core.list_tables("public")
        assert "tool_migration_test" in tables["tables"]

        # Clean up
        await core.execute("DROP TABLE tool_migration_test")

    @pytest.mark.integration
    async def test_explain_analyze_tool(self, core: PostgreSQLCore):
        """Test explain_analyze tool."""
        result = await core.explain_analyze("SELECT * FROM test_users WHERE id = $1", [1])
        assert len(result["plan"]) > 0
        assert result["execution_time_ms"] > 0
        assert "Node Type" in result["plan"][0]

    @pytest.mark.integration
    async def test_tool_chaining(self, core: PostgreSQLCore):
        """Test chaining multiple tools together."""
        # Create table
        await core.run_migration("CREATE TABLE chain_test (id SERIAL PRIMARY KEY, data TEXT)")

        # Insert data
        await core.execute("INSERT INTO chain_test (data) VALUES ($1)", ["test1"])
        await core.execute("INSERT INTO chain_test (data) VALUES ($1)", ["test2"])

        # Query data
        result = await core.query("SELECT * FROM chain_test ORDER BY id")
        assert result["row_count"] == 2

        # Describe table
        desc = await core.describe_table("chain_test")
        assert desc["table"] == "chain_test"

        # Analyze query
        plan = await core.explain_analyze("SELECT * FROM chain_test WHERE data = $1", ["test1"])
        assert len(plan["plan"]) > 0

        # List tables
        tables = await core.list_tables("public")
        assert "chain_test" in tables["tables"]

        # Clean up
        await core.execute("DROP TABLE chain_test")
