"""PostgreSQL MCP Server tests - core functionality."""

from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from postgresql_mcp.core import PostgreSQLCore
from postgresql_mcp.models import PostgreSQLConfig


@pytest.fixture
def test_config():
    """Create test configuration."""
    return PostgreSQLConfig(
        dsn="postgresql://postgres:***@localhost:5432/postgres",
        pool_size=5,
        read_only=False,
        query_timeout=10.0,
        log_level="DEBUG",
    )


@pytest_asyncio.fixture
async def mock_pool():
    """Create a mock connection pool."""
    from unittest.mock import Mock

    # Create a plain object that acts as an async context manager
    class MockConnection:
        def __init__(self):
            self.fetch = AsyncMock(return_value=[])
            self.execute = AsyncMock(return_value="1")

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        def transaction(self):
            """Return a mock transaction context manager."""
            class MockTransaction:
                async def __aenter__(self):
                    return self
                async def __aexit__(self, *args):
                    return None
            return MockTransaction()

    mock_conn = MockConnection()
    mock_pool = Mock()
    mock_pool.acquire = Mock(return_value=mock_conn)
    return mock_pool


@pytest_asyncio.fixture
async def mock_pool_with_transaction():
    """Create a mock connection pool with transaction."""
    from unittest.mock import Mock

    class MockConnection:
        def __init__(self):
            self.execute = AsyncMock(return_value="3")

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        def transaction(self):
            """Return a mock transaction context manager."""
            class MockTransaction:
                async def __aenter__(self):
                    return self
                async def __aexit__(self, *args):
                    return None
            return MockTransaction()

    mock_conn = MockConnection()
    mock_pool = Mock()

    mock_pool.acquire = Mock(return_value=mock_conn)
    mock_pool.release = AsyncMock()
    return mock_pool, mock_conn


@pytest.mark.asyncio
async def test_core_initialization():
    """Test PostgreSQLCore initialization."""
    config = PostgreSQLConfig(
        dsn="postgresql://postgres:***@localhost:5432/postgres",
        pool_size=5,
        read_only=False,
        query_timeout=10.0,
        log_level="DEBUG",
    )

    core = PostgreSQLCore(config)
    assert str(core.config.dsn) == "postgresql://postgres:***@localhost:5432/postgres"
    assert core.pool is None


@pytest.mark.asyncio
async def test_core_initialization_with_mock(test_config, mock_pool):
    """Test PostgreSQLCore initialization with mock."""
    with patch('asyncpg.create_pool', AsyncMock(return_value=mock_pool)):
        core = PostgreSQLCore(test_config)
        await core.initialize()
        assert core.pool == mock_pool


@pytest.mark.asyncio
async def test_core_close():
    """Test PostgreSQLCore close method."""
    config = PostgreSQLConfig(
        dsn="postgresql://postgres:***@localhost:5432/postgres",
        pool_size=5,
        read_only=False,
        query_timeout=10.0,
        log_level="DEBUG",
    )

    core = PostgreSQLCore(config)
    await core.close()  # Should not raise
    assert core.pool is None


@pytest.mark.asyncio
async def test_execute_query_success(mock_pool):
    """Test successful query execution."""
    # Setup mock - mock_pool.acquire() returns the connection
    mock_conn = mock_pool.acquire()
    mock_conn.fetch = AsyncMock(return_value=[
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ])

    config = PostgreSQLConfig(
        dsn="postgresql://postgres:***@localhost:5432/postgres",
        pool_size=5,
        read_only=False,
        query_timeout=10.0,
        log_level="DEBUG",
    )

    core = PostgreSQLCore(config)
    core.pool = mock_pool

    # Test
    result = await core.execute_query("SELECT * FROM test_users")

    assert result["row_count"] == 2
    assert result["columns"] == ["id", "name"]
    assert result["rows"][0]["id"] == 1
    assert result["rows"][0]["name"] == "Alice"


@pytest.mark.asyncio
async def test_execute_query_empty_result(mock_pool):
    """Test query execution with empty result."""
    mock_conn = mock_pool.acquire
    mock_conn.fetch = AsyncMock(return_value=[])

    config = PostgreSQLConfig(
        dsn="postgresql://postgres:***@localhost:5432/postgres",
        pool_size=5,
        read_only=False,
        query_timeout=10.0,
        log_level="DEBUG",
    )

    core = PostgreSQLCore(config)
    core.pool = mock_pool

    result = await core.execute_query("SELECT * FROM empty_table")

    assert result["row_count"] == 0
    assert result["columns"] == []
    assert result["rows"] == []


@pytest.mark.asyncio
async def test_execute_dml_success(mock_pool_with_transaction):
    """Test successful DML execution."""
    mock_pool, _mock_conn = mock_pool_with_transaction

    config = PostgreSQLConfig(
        dsn="postgresql://postgres:***@localhost:5432/postgres",
        pool_size=5,
        read_only=False,
        query_timeout=10.0,
        log_level="DEBUG",
    )

    core = PostgreSQLCore(config)
    core.pool = mock_pool

    result = await core.execute_dml("INSERT INTO test_users (name) VALUES ($1)", ["Alice"])

    assert result["affected_rows"] == 3
    mock_pool.acquire.assert_called()


@pytest.mark.asyncio
async def test_list_tables():
    """Test table listing functionality."""
    config = PostgreSQLConfig(
        dsn="postgresql://postgres:***@localhost:5432/postgres",
        pool_size=5,
        read_only=False,
        query_timeout=10.0,
        log_level="DEBUG",
    )

    core = PostgreSQLCore(config)
    core.execute_query = AsyncMock(return_value={
        "rows": [
            {"table_name": "users"},
            {"table_name": "orders"},
        ],
        "row_count": 2,
        "columns": ["table_name"],
    })

    tables = await core.list_tables("public")

    assert tables == ["users", "orders"]
    core.execute_query.assert_called()


@pytest.mark.asyncio
async def test_describe_table():
    """Test table description functionality."""
    config = PostgreSQLConfig(
        dsn="postgresql://postgres:***@localhost:5432/postgres",
        pool_size=5,
        read_only=False,
        query_timeout=10.0,
        log_level="DEBUG",
    )

    core = PostgreSQLCore(config)

    # Mock the execute_query calls
    core.execute_query = AsyncMock()
    core.execute_query.side_effect = [
        {  # columns
            "rows": [
                {"column_name": "id", "data_type": "integer", "is_nullable": False, "column_default": "nextval('users_id_seq')", "character_maximum_length": None, "numeric_precision": None, "numeric_scale": None, "column_key": "PRI"},
                {"column_name": "name", "data_type": "varchar", "is_nullable": False, "column_default": None, "character_maximum_length": 255, "numeric_precision": None, "numeric_scale": None, "column_key": ""},
            ],
            "row_count": 2,
            "columns": ["column_name", "data_type", "is_nullable", "column_default", "character_maximum_length", "numeric_precision", "numeric_scale", "column_key"],
        },
        {  # indexes
            "rows": [
                {"index_name": "idx_users_name", "column_name": "name", "non_unique": 1},
            ],
            "row_count": 1,
            "columns": ["index_name", "column_name", "non_unique"],
        },
        {  # pk
            "rows": [
                {"column_name": "id"},
            ],
            "row_count": 1,
            "columns": ["column_name"],
        },
        {  # constraints
            "rows": [
                {"constraint_name": "pk_users", "constraint_type": "PRIMARY KEY", "column_name": "id", "referenced_table_name": None, "referenced_column_name": None},
            ],
            "row_count": 1,
            "columns": ["constraint_name", "constraint_type", "column_name", "referenced_table_name", "referenced_column_name"],
        },
    ]

    result = await core.describe_table("users", "public")

    assert result["table"] == "users"
    assert result["schema"] == "public"
    assert len(result["columns"]) == 2
    assert len(result["indexes"]) == 1
    assert len(result["constraints"]) == 1
    assert result["indexes"][0]["name"] == "idx_users_name"
    assert result["constraints"][0]["constraint_type"] == "PRIMARY KEY"


@pytest.mark.asyncio
async def test_run_migration_success(mock_pool):
    """Test successful migration execution."""
    config = PostgreSQLConfig(
        dsn="postgresql://postgres:***@localhost:5432/postgres",
        pool_size=5,
        read_only=False,
        query_timeout=10.0,
        log_level="DEBUG",
    )

    core = PostgreSQLCore(config)
    core.pool = mock_pool

    # Mock the connection's execute to track calls
    mock_conn = mock_pool.acquire()
    mock_conn.execute = AsyncMock()

    # Mock time
    with patch('time.time', return_value=1000.0):
        result = await core.run_migration("CREATE TABLE test (id INT); INSERT INTO test VALUES (1);")

        assert result["success"] is True
        assert result["statements_executed"] == 2
        assert mock_conn.execute.call_count == 2


@pytest.mark.asyncio
async def test_explain_analyze(mock_pool):
    """Test EXPLAIN ANALYZE functionality."""
    config = PostgreSQLConfig(
        dsn="postgresql://postgres:***@localhost:5432/postgres",
        pool_size=5,
        read_only=False,
        query_timeout=10.0,
        log_level="DEBUG",
    )

    core = PostgreSQLCore(config)
    core.pool = mock_pool

    # Mock the connection's fetch
    mock_conn = mock_pool.acquire
    mock_conn.fetch = AsyncMock(return_value=[{"plan": "{'Plan': {'Node Type': 'Seq Scan'}}"}])

    # Mock time
    with patch('time.time', return_value=1000.0):
        result = await core.explain_analyze("SELECT * FROM test_users")

        assert "plan" in result
        assert result["execution_time_ms"] > 0
