# DB Bridge

Bridge your AI assistant to local PostgreSQL databases — query, inspect, and manage data without cloud dependencies.

## Quick Start (uvx — no install needed)

```bash
uvx airgap-db-bridge
```

## Installation

```bash
pip install airgap-db-bridge
```

## Usage

### CLI (Direct)
```bash
airgap-db-bridge
```

### MCP Client Config (Claude Desktop, Cursor, VS Code)

**Windows (requires full path to executable):**
```json
{
  "mcpServers": {
    "database": {
      "command": "C:\Users\<user>\AppData\Local\hermes\hermes-agent\venv\Scripts\airgap-db-bridge.exe",
      "env": {
        "POSTGRES_DSN": "postgresql://user:pass@localhost:5432/db"
      }
    }
  }
}
```

**macOS/Linux (if on PATH):**
```json
{
  "mcpServers": {
    "database": {
      "command": "airgap-db-bridge",
      "env": {
        "POSTGRES_DSN": "postgresql://user:pass@localhost:5432/db"
      }
    }
  }
}
```

### DXT (Claude Desktop 1-Click)
Download `airgap-db-bridge-1.0.0.dxt` from [Releases](https://github.com/airgap-fleet/db-bridge/releases) → drag into Claude Desktop.

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `POSTGRES_DSN` | Required | PostgreSQL connection string (e.g., `postgresql://user:pass@host:5432/db`) |
| `DB_BRIDGE_MAX_ROWS` | 1000 | Max rows returned per query |
| `DB_BRIDGE_STATEMENT_TIMEOUT` | 30000 | Query timeout in ms |
| `DB_BRIDGE_ALLOW_DDL` | false | Allow CREATE/ALTER/DROP statements |
| `DB_BRIDGE_ALLOW_WRITE` | false | Allow INSERT/UPDATE/DELETE |

## Available Tools

| Tool | Description |
|------|-------------|
| `query` | Execute a read-only SELECT query |
| `execute` | Execute a write query (requires `DB_BRIDGE_ALLOW_WRITE=true`) |
| `list_tables` | List all tables in the database |
| `describe_table` | Show columns, types, constraints for a table |
| `list_schemas` | List all schemas in the database |

## Transport Modes

- **stdio** (default) — For local MCP clients (Claude Desktop, etc.)
- **sse** — Server-Sent Events for HTTP clients
- **http** — Streamable HTTP for modern clients

Set via `DB_BRIDGE_TRANSPORT` environment variable.

## Windows-Specific Notes

- The executable is installed to `C:\Users\<user>\AppData\Local\hermes\hermes-agent\venv\Scripts\airgap-db-bridge.exe` when using Hermes
- **Always use the full `.exe` path in MCP client configs on Windows** — bare commands like `airgap-db-bridge` will fail with `ENOENT` because the venv Scripts folder is not on system PATH
- Use standard PostgreSQL DSN format in environment variables
- Escape backslashes in JSON command paths (`C:\Users\...`)

## Why DB Bridge?

- **Local-first** — Your data never leaves your machine
- **Air-gapped ready** — No cloud dependencies, works offline
- **Security hardened** — Read-only by default, optional write/DDL gates, row limits, statement timeouts
- **Multiple transports** — stdio, SSE, Streamable HTTP
- **PostgreSQL native** — Full protocol support, prepared statements, connection pooling
- **uvx compatible** — Zero-install usage like the competition

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
uv run pytest -v

# Check code quality
uv run ruff check .
uv run mypy .
```

## License

MIT
