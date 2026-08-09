# PostgreSQL MCP Server

A Model Context Protocol (MCP) server providing PostgreSQL database operations via FastMCP. Enables secure, parameterized database access for AI assistants and automation tools.

## Features

- **6 Database Tools**: Query, Execute, List Tables, Describe Table, Run Migration, Explain Analyze
- **Security First**: Parameterized queries only, read-only mode, connection pooling, audit logging
- **Production Ready**: Async connection pooling, configurable timeouts, structured logging
- **Developer Experience**: Type-safe Pydantic models, comprehensive tests, MCP Inspector compatible

## Installation

### From PyPI (when published)
```bash
pip install postgresql-mcp
```

### From Source
```bash
git clone https://github.com/afaaS/postgresql-mcp.git
cd postgresql-mcp
pip install -e .
```

### Docker
```bash
docker pull afaaS/postgresql-mcp:latest
```

## Quick Start

### 1. Configure Environment
```bash
cp .env.example .env
# Edit .env with your PostgreSQL connection details
```

### 2. Run Server
```bash
# Direct execution
postgresql-mcp

# Or with Docker Compose (includes PostgreSQL)
docker-compose up -d
```

### 3. Configure MCP Client
Add to your MCP client configuration (Claude Desktop, Cursor, VS Code, etc.):

```json
{
  "mcpServers": {
    "postgresql": {
      "command": "postgresql-mcp",
      "env": {
        "POSTGRESQL_MCP_DSN": "postgresql://user:pass@localhost:5432/db"
      }
    }
  }
}
```

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `POSTGRESQL_MCP_DSN` | `postgresql://postgres:postgres@localhost:5432/postgres` | PostgreSQL connection string |
| `POSTGRESQL_MCP_POOL_SIZE` | `10` | Connection pool size (1-100) |
| `POSTGRESQL_MCP_READ_ONLY` | `false` | Enable read-only mode (blocks write operations) |
| `POSTGRESQL_MCP_QUERY_TIMEOUT` | `30.0` | Query timeout in seconds (0-300) |
| `POSTGRESQL_MCP_LOG_LEVEL` | `INFO` | Structured logging level |

## Tools Reference

| Tool | Description | Parameters | Read-Only Safe |
|------|-------------|------------|----------------|
| `query` | Execute parameterized SELECT query | `sql` (string), `params` (array, optional) | ✅ |
| `execute` | Execute INSERT/UPDATE/DELETE | `sql` (string), `params` (array, optional) | ❌ |
| `list_tables` | List tables in a schema | `schema` (string, default: "public") | ✅ |
| `describe_table` | Get table structure (columns, indexes, constraints) | `table` (string), `schema` (string, default: "public") | ✅ |
| `run_migration` | Run DDL statements in transaction | `sql` (string) | ❌ |
| `explain_analyze` | Get query execution plan with costs | `sql` (string), `params` (array, optional) | ✅ |

## Usage Examples

### Query Data
```json
{
  "tool": "query",
  "arguments": {
    "sql": "SELECT * FROM users WHERE age > $1 AND active = $2",
    "params": [18, true]
  }
}
```

### Insert Data
```json
{
  "tool": "execute",
  "arguments": {
    "sql": "INSERT INTO users (name, email, age) VALUES ($1, $2, $3)",
    "params": ["John Doe", "john@example.com", 30]
  }
}
```

### List Tables
```json
{
  "tool": "list_tables",
  "arguments": {
    "schema": "public"
  }
}
```

### Describe Table Structure
```json
{
  "tool": "describe_table",
  "arguments": {
    "table": "users",
    "schema": "public"
  }
}
```

### Run Migration
```json
{
  "tool": "run_migration",
  "arguments": {
    "sql": "CREATE TABLE products (id SERIAL PRIMARY KEY, name TEXT NOT NULL, price DECIMAL(10,2)); CREATE INDEX idx_products_name ON products(name);"
  }
}
```

### Analyze Query Plan
```json
{
  "tool": "explain_analyze",
  "arguments": {
    "sql": "SELECT * FROM users JOIN orders ON users.id = orders.user_id WHERE users.id = $1",
    "params": [1]
  }
}
```

## Security Model

### Parameterized Queries Only
All SQL execution uses parameterized queries (`$1`, `$2`, etc.). String concatenation or interpolation is **not supported** — this prevents SQL injection by design.

### Read-Only Mode
Set `POSTGRESQL_MCP_READ_ONLY=true` to disable:
- `execute` (INSERT/UPDATE/DELETE)
- `run_migration` (DDL)

Read operations (`query`, `list_tables`, `describe_table`, `explain_analyze`) remain available.

### Connection Pooling
- Configurable pool size (1-100 connections)
- Automatic connection lifecycle management
- Query timeout enforcement

### Audit Logging
All operations are logged with structured JSON including:
- Operation type and parameters (sanitized)
- Execution time
- Row counts affected
- Error details (if any)

## Development

### Prerequisites
- Python 3.11+
- PostgreSQL 14+ (for local development)
- uv (recommended) or pip

### Setup
```bash
# Install uv if not present
pip install uv

# Create virtual environment and install dependencies
uv sync --dev

# Run tests
uv run pytest

# Type check
uv run mypy src/postgresql_mcp

# Lint and format
uv run ruff check .
uv run ruff format .
```

### Running Tests with Local PostgreSQL
```bash
# Start PostgreSQL (Docker)
docker run -d --name pg-test -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16

# Run tests
POSTGRESQL_MCP_TEST_DSN=postgresql://postgres:postgres@localhost:5432/postgres uv run pytest

# Cleanup
docker rm -f pg-test
```

### MCP Inspector
```bash
npx @modelcontextprotocol/inspector uv run postgresql-mcp
```

## Architecture

```
postgresql-mcp/
├── src/postgresql_mcp/
│   ├── __init__.py          # Package exports
│   ├── models.py            # Pydantic models (requests/responses/config)
│   ├── core.py              # Business logic (asyncpg, zero FastMCP imports)
│   └── server.py            # FastMCP app, tool registration, lifespan
├── tests/
│   ├── conftest.py          # Test fixtures and setup
│   ├── test_models.py       # Model validation tests
│   ├── test_core.py         # Core business logic tests
│   └── test_tools.py        # MCP tool integration tests
├── .github/workflows/ci.yml # CI/CD pipeline
├── Dockerfile               # Multi-stage container build
├── docker-compose.yml       # Local development stack
├── pyproject.toml           # Project configuration (hatch)
└── README.md                # This file
```

### Design Principles

1. **Separation of Concerns**: `core.py` contains zero FastMCP imports — fully testable in isolation
2. **Type Safety**: Pydantic v2 for all boundaries, mypy strict mode
3. **Async First**: asyncpg for non-blocking database operations
4. **Security by Default**: Parameterized queries, read-only mode, least privilege
5. **Observability**: Structured JSON logging, execution timing, audit trails

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push/PR:

1. **Lint** — ruff check + format
2. **Type Check** — mypy strict
3. **Test** — pytest with PostgreSQL service, coverage ≥90%
4. **Build** — hatch build + twine verify
5. **Publish** — PyPI on release (trusted publishing)
6. **Docker** — Multi-platform image on release

## License

MIT License — see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Ensure CI passes (lint, typecheck, test, coverage)
5. Submit a pull request

## Support

- Issues: GitHub Issues
- Documentation: This README + inline docstrings
- MCP Specification: https://modelcontextprotocol.io