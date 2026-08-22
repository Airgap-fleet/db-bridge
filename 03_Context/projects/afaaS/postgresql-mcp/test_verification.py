#!/usr/bin/env python3
"""Simple verification script to test PostgreSQL MCP Server connection."""

import asyncio
import sys

print("=== PostgreSQL MCP Server Connection Test ===")

async def test_connection():
    """Test direct connection to PostgreSQL."""
    print("\n1. Testing direct PostgreSQL connection...")

    try:
        import asyncpg
        print(f"✓ asyncpg imported successfully, version: {asyncpg.__version__}")
    except ImportError as e:
        print(f"✗ Cannot import asyncpg: {e}")
        return False

    try:
        # Try to connect with the correct password
        dsn = "postgresql://postgres:postgres@localhost:5432/postgres"
        print(f"Trying to connect with DSN: {dsn}")

        pool = await asyncpg.create_pool(dsn, min_size=1, max_size=3)
        print("✓ Pool created successfully")

        async with pool.acquire() as conn:
            # Test basic query
            result = await conn.fetch("SELECT version()")
            print(f"✓ Connection successful, version: {result[0]['version']}")

            # Check if test tables exist
            result = await conn.fetch("SELECT COUNT(*) as count FROM test_users")
            print(f"✓ test_users table has {result[0]['count']} rows")

            result = await conn.fetch("SELECT COUNT(*) as count FROM test_orders")
            print(f"✓ test_orders table has {result[0]['count']} rows")

        pool.close()
        await pool.wait_closed()
        print("✓ Pool closed")

        return True

    except Exception as e:
        print(f"✗ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_core():
    """Test core functionality."""
    print("\n2. Testing core functionality...")

    try:
        # Add src to path
        sys.path.insert(0, 'src')

        # Import core modules
        from postgresql_mcp.core import PostgreSQLCore
        from postgresql_mcp.models import PostgreSQLConfig, QueryRequest
        print("✓ Imported core modules")

        # Create config
        config = PostgreSQLConfig(
            dsn="postgresql://postgres:postgres@localhost:5432/postgres",
            pool_size=5,
            read_only=False,
            query_timeout=10.0
        )
        print("✓ Created PostgreSQLConfig")

        # Create core instance
        core = PostgreSQLCore(config)
        print("✓ Created PostgreSQLCore instance")

        # Initialize
        await core.initialize()
        print("✓ Core initialized")

        # Test query
        request = QueryRequest(sql="SELECT * FROM test_users ORDER BY id")
        response = await core.query(request)
        print(f"✓ Query successful, returned {response.row_count} rows")

        # Test list tables
        from postgresql_mcp.models import ListTablesRequest
        tables_request = ListTablesRequest(schema_name="public")
        tables_response = await core.list_tables(tables_request)
        print(f"✓ List tables successful: {tables_response.tables}")

        # Clean up
        await core.close()
        print("✓ Core closed")

        return True

    except Exception as e:
        print(f"✗ Core functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("Starting PostgreSQL MCP Server verification...")

    # Test basic connection
    connection_test = await test_connection()

    # Test core functionality
    core_test = await test_core()

    # Summary
    print("\n=== Test Summary ===")
    print(f"Direct connection test: {'✓ PASSED' if connection_test else '✗ FAILED'}")
    print(f"Core functionality test: {'✓ PASSED' if core_test else '✗ FAILED'}")

    if connection_test and core_test:
        print("\n🎉 ALL TESTS PASSED!")
        print("The PostgreSQL MCP Server is working correctly with the password fix.")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("The test suite needs more fixes.")
        return 1

if __name__ == "__main__":
    # Set up path
    sys.path.insert(0, '.')

    # Run tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code)