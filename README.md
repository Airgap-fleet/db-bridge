# DB Bridge

Local-first PostgreSQL MCP bridge for Private Desk. Query, inspect, and manage a database you already run — without sending that data to a cloud sidecar.

**Build class: UNSIGNED INTERNAL.** This tree is not Authenticode-signed. Thumbprint: `(none — unsigned)`.

Setup (installer, pip, uv) may use the network for wheels. **The running bridge does not phone home.**

## Recommended: Windows one-command installer

From a clone of this repository, in PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\installer\Install-DbBridge.ps1 -Dsn "postgresql://user:pass@localhost:5432/dbname"
```

Silent / unattended (the UNSIGNED INTERNAL label is still printed):

```powershell
.\installer\Install-DbBridge.ps1 -Dsn "postgresql://user:pass@localhost:5432/dbname" -Quiet
```

Default location: `%LOCALAPPDATA%\AirgapFleet\db-bridge`. Dependencies are pinned from `uv.lock` when `uv` is on `PATH`.

See [installer/README.md](installer/README.md).

### Verify

```powershell
.\scripts\self_test.ps1 -ProtocolOnly
```

**Caveat:** protocol-only PASS means MCP `initialize` and `tools/list` succeeded. It is **not** full tool coverage and does **not** prove a live PostgreSQL connection. The pool is lazy — those calls do not open the database.

A full check **needs Postgres** and a DSN. Without a DSN it fails on purpose:

```powershell
.\scripts\self_test.ps1 -Full -Dsn "postgresql://user:pass@localhost:5432/dbname"
```

### Uninstall

```powershell
.\installer\Uninstall-DbBridge.ps1
```

## Advanced: pip / uvx

```bash
pip install airgap-db-bridge
# or, no persistent install:
uvx airgap-db-bridge
```

Then point your MCP client at the `airgap-db-bridge` executable and set `DB_BRIDGE_DSN`.

### MCP client config

**Windows (use the full path to the executable):**

```json
{
  "mcpServers": {
    "database": {
      "command": "C:\\Users\\<user>\\AppData\\Local\\AirgapFleet\\db-bridge\\venv\\Scripts\\airgap-db-bridge.exe",
      "env": {
        "DB_BRIDGE_DSN": "postgresql://user:pass@localhost:5432/db"
      }
    }
  }
}
```

**macOS / Linux (if the script is on PATH):**

```json
{
  "mcpServers": {
    "database": {
      "command": "airgap-db-bridge",
      "env": {
        "DB_BRIDGE_DSN": "postgresql://user:pass@localhost:5432/db"
      }
    }
  }
}
```

## Configuration

Canonical prefix: **`DB_BRIDGE_*`**. Legacy `POSTGRES_*` and `POSTGRESQL_MCP_*` names are read only when the canonical variable is unset.

| Environment variable | Default | Description |
|----------------------|---------|-------------|
| `DB_BRIDGE_DSN` | required for DB tools | PostgreSQL connection string |
| `DB_BRIDGE_POOL_SIZE` | 10 | Connection pool size (1–100) |
| `DB_BRIDGE_READ_ONLY` | false | Recorded on the config object |
| `DB_BRIDGE_QUERY_TIMEOUT` | 30 | Query timeout in seconds |
| `DB_BRIDGE_LOG_LEVEL` | INFO | Structured logs (stderr only) |

Copy [.env.example](.env.example) to `.env` for local development. See [AUDIT-NOTES.md](AUDIT-NOTES.md).

## Available tools

| Tool | Description |
|------|-------------|
| `query` | Parameterised SELECT |
| `execute` | Parameterised INSERT / UPDATE / DELETE |
| `list_tables` | Tables in a schema |
| `describe_table` | Columns, indexes, constraints |
| `run_migration` | DDL statements in a transaction |
| `explain_analyze` | `EXPLAIN ANALYZE` plan |

stdio is the supported local MCP transport. Structured logs go to **stderr only** so stdout stays JSON-RPC clean.

## Proof pack

[proof-pack/](proof-pack/) has the demo checklist, UNSIGNED INTERNAL signing note, egress observation notes, and hash helpers. A full database demo needs Postgres.

This project does **not** claim Cyber Essentials, ISO 27001, or any other certification.

## Development

```bash
pip install -e ".[dev]"
uv run pytest -v
uv run ruff check src/postgresql_mcp
uv run mypy src/postgresql_mcp
python scripts/self_test.py --protocol-only
```

## Licence

MIT
