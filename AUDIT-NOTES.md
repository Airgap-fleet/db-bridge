# Audit notes

Short record of the Stage 2 packaging audit for `airgap-db-bridge` 1.0.3.

## stdio logging

Structured logs (stdlib + structlog) go to **stderr only**. MCP JSON-RPC must keep stdout clean. Regression: `tests/test_stdio_logging.py`.

## Environment prefix

Canonical prefix is **`DB_BRIDGE_*`**, especially `DB_BRIDGE_DSN`.

When a canonical variable is unset, these legacy names are copied across:

- `POSTGRES_DSN` → `DB_BRIDGE_DSN` (same for `POOL_SIZE`, `READ_ONLY`, `QUERY_TIMEOUT`, `LOG_LEVEL`)
- `POSTGRESQL_MCP_DSN` → `DB_BRIDGE_DSN` (and the same field suffixes)

`DB_BRIDGE_*` always wins if both are set. See `src/postgresql_mcp/env.py` and `.env.example`.

## Telemetry

No phone-home, crash reporter, or usage beacon. Installer setup may download wheels. Runtime talks to the DSN you set and to the local MCP client.

## Signing

**UNSIGNED INTERNAL.** No Authenticode thumbprint. See `proof-pack/SIGNING.md`.

## Self-test honesty

`scripts/self_test.py --protocol-only` is `initialize` + `tools/list`. That PASS is not full tool coverage. `--full` requires an explicit DSN and a reachable Postgres.

## Tree hygiene

Do not ship nested vault folders or stale `db-bridge-1.0.0*` / `db_bridge-1.0.0*` artefacts. `dist/` stays gitignored.
