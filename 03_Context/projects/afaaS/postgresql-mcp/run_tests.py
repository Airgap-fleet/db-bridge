#!/usr/bin/env python3
"""Simple test runner for PostgreSQL MCP Server."""

import asyncio
import sys

print("=== PostgreSQL MCP Server Test Runner ===")

async def run_basic_tests():
    """Run basic tests manually."""
    print("\n=== Testing basic PostgreSQL connection ===")

    try:
        from asyncpg import create_pool
        print("✓ asyncpg imported successfully")

        # Try to connect to the test database
        dsn = "postgresql://postgres:postgres@localhost:5432/postgres"
        print(f"Trying to connect with DSN: {dsn}")

        pool = await create_pool(dsn, min_size=1, max_size=5)
        print("✓ Pool created successfully")

        # Test basic connection
        async with pool.acquire() as conn:
            result = await conn.fetch("SELECT version()")
            print(f"✓ Connection successful, PostgreSQL version: {result[0]['version']}")

            # Check if test_users table exists
            result = await conn.fetch("SELECT COUNT(*) as count FROM test_users")
            print(f"✓ test_users table has {result[0]['count']} rows")

            # Check if test_orders table exists
            result = await conn.fetch("SELECT COUNT(*) as count FROM test_orders")
            print(f"✓ test_orders table has {result[0]['count']} rows")

            # Verify test data
            result = await conn.fetch("SELECT name, email FROM test_users ORDER BY id")
            print("✓ test_users data:")
            for row in result:
                print(f"  - {row['name']}: {row['email']}")

            result = await conn.fetch("SELECT product, status FROM test_orders ORDER BY id")
            print("✓ test_orders data:")
            for row in result:
                print(f"  - {row['product']}: {row['status']}")

        pool.close()
        await pool.wait_closed()
        print("✓ Pool closed")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_core_tests():
    """Run core functionality tests."""
    print("\n=== Testing Core Functionality ===")

    try:
        from postgresql_mcp.models import PostgreSQLConfig
        from postgresql_mcp.core import PostgreSQLCore
        print("✓ Models and Core imported successfully")

        # Create config with correct password
        config = PostgreSQLConfig(
            dsn="postgresql://postgres:postgres@localhost:5432/postgres"
        )
        print(f"✓ Config created with dsn: {config.dsn}")

        # Create core instance
        core = PostgreSQLCore(config)
        print("✓ PostgreSQLCore instance created")

        # Initialize connection
        await core.initialize()
        print("✓ Core initialized")

        # Test query
        from postgresql_mcp.models import QueryRequest
        request = QueryRequest(sql="SELECT COUNT(*) as count FROM test_users")
        response = await core.query(request)
        print(f"✓ Query successful, returned {response.row_count} rows")

        # Test list tables
        from postgresql_mcp.models import ListTablesRequest
        tables_request = ListTablesRequest(schema_name="public")
        tables_response = await core.list_tables(tables_request)
        print(f"✓ List tables successful, found: {tables_response.tables}")

        # Clean up
        await core.close()
        print("✓ Core closed")

        return True

    except Exception as e:
        print(f"✗ Error in core tests: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test runner."""
    print("Starting PostgreSQL MCP Server tests...")

    # Test 1: Basic connection
    basic_test_passed = await run_basic_tests()

    # Test 2: Core functionality
    core_test_passed = await run_core_tests()

    # Summary
    print("\n=== Test Summary ===")
    print(f"Basic connection test: {'✓ PASSED' if basic_test_passed else '✗ FAILED'}")
    print(f"Core functionality test: {'✓ PASSED' if core_test_passed else '✗ FAILED'}")

    if basic_test_passed and core_test_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("The PostgreSQL MCP Server test suite is working correctly.")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("The test suite needs fixes.")
        return 1

if __name__ == "__main__":
    # Set up path
    sys.path.insert(0, '.')

    # Run tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code)