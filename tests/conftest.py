"""Test configuration and fixtures for PostgreSQL MCP Server tests."""

import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from asyncpg import Pool, create_pool

from postgresql_mcp.core import PostgreSQLCore
from postgresql_mcp.models import PostgreSQLConfig

# Use environment variable for test database DSN, fallback to default

def _first_env(*names: str, default: str) -> str:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


TEST_DSN = _first_env(
    "DB_BRIDGE_TEST_DSN",
    "DB_BRIDGE_DSN",
    "POSTGRESQL_MCP_TEST_DSN",
    "POSTGRES_DSN",
    default="postgresql://postgres:postgres@localhost:5432/postgres",
)

@pytest.fixture
def test_config() -> PostgreSQLConfig:
    """Create test configuration."""
    return PostgreSQLConfig(
        dsn=TEST_DSN,
        pool_size=5,
        read_only=False,
        query_timeout=10.0,
        log_level="DEBUG",
    )

@pytest.fixture
async def test_pool(test_config: PostgreSQLConfig) -> AsyncGenerator[Pool, None]:
    """Create a test connection pool."""
    try:
        pool = await create_pool(
            dsn=str(test_config.dsn),
            min_size=1,
            max_size=test_config.pool_size,
            command_timeout=test_config.query_timeout,
        )
        try:
            yield pool
        finally:
            await pool.close()
    except Exception:
        # Skip tests if PostgreSQL is not available
        pytest.skip("PostgreSQL not available")

@pytest_asyncio.fixture
async def core(test_config: PostgreSQLConfig) -> AsyncGenerator[PostgreSQLCore, None]:
    """Create a PostgreSQLCore instance for testing."""
    try:
        core_instance = PostgreSQLCore(test_config)
        await core_instance.initialize()
        try:
            yield core_instance
        finally:
            await core_instance.close()
    except Exception:
        pytest.skip("PostgreSQL not available")

@pytest_asyncio.fixture
async def core_read_only(test_config: PostgreSQLConfig) -> AsyncGenerator[PostgreSQLCore, None]:
    """Create a PostgreSQLCore instance in read-only mode."""
    try:
        config = test_config.model_copy(update={"read_only": True})
        core_instance = PostgreSQLCore(config)
        await core_instance.initialize()
        try:
            yield core_instance
        finally:
            await core_instance.close()
    except Exception:
        pytest.skip("PostgreSQL not available")

@pytest.fixture
async def setup_test_tables(test_pool: Pool):
    """Set up test tables before each test and clean up after."""
    try:
        # Create test tables
        async with test_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS test_users (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    age INT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS test_orders (
                    id SERIAL PRIMARY KEY,
                    user_id INT REFERENCES test_users(id),
                    product TEXT NOT NULL,
                    amount DECIMAL(10,2),
                    status TEXT DEFAULT 'pending'
                )
            """)

            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_test_users_email ON test_users(email)
            """)

            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_test_orders_user_id ON test_orders(user_id)
            """)

            # Clear existing data
            await conn.execute("TRUNCATE test_orders, test_users RESTART IDENTITY CASCADE")
            # Insert test data
            await conn.execute("""
                INSERT INTO test_users (name, email, age) VALUES
                    ('Alice', 'alice@example.com', 30),
                    ('Bob', 'bob@example.com', 25),
                    ('Charlie', 'charlie@example.com', 35)
            """)

            await conn.execute("""
                INSERT INTO test_orders (user_id, product, amount, status) VALUES
                    (1, 'Laptop', 999.99, 'completed'),
                    (1, 'Mouse', 29.99, 'completed'),
                    (2, 'Keyboard', 79.99, 'pending')
            """)

        yield

        # Clean up after test
        async with test_pool.acquire() as conn:
            await conn.execute("TRUNCATE test_orders, test_users RESTART IDENTITY CASCADE")
    except Exception:
        pytest.skip("PostgreSQL not available")
