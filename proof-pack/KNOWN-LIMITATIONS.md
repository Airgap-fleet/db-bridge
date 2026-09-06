# Known limitations

Honest limits for airgap-db-bridge 1.0.3. This is not a risk register and not a certification.

## Self-test

- **Protocol-only PASS is not full tool coverage.** It checks MCP `initialize` and `tools/list` only.
- The connection pool is lazy. Those two calls do not open PostgreSQL.
- **Full tool demonstration needs Postgres** and an explicit DSN. Without a DSN, full mode fails on purpose.

## Signing

- **UNSIGNED INTERNAL.** No Authenticode signature, no thumbprint, no MSI/WiX package.

## Runtime

- The bridge talks to the DSN you configure. It does not invent cloud backups or telemetry.
- `read_only` is a config flag on the core settings object; tool-level enforcement is not a substitute for PostgreSQL privileges.
- Features mentioned in older marketing copy (`DB_BRIDGE_ALLOW_DDL`, `DB_BRIDGE_ALLOW_WRITE`, `list_schemas`) are **not** implemented in this package. Do not demo them.

## Packaging

- The Windows installer is a per-user PowerShell script. It may download wheels during setup.
- Lockfile pinning requires `uv` plus `uv.lock`. If `uv` is missing, the installer warns and proceeds unpinned.
- Stale artefacts named `db-bridge-1.0.0*` / `db_bridge-1.0.0*` must not be uploaded as the 1.0.3 product.

## Out of scope

- WiX/MSI Authenticode spend
- Tags and PyPI publish (release checklist is owned separately)
- Compliance marks (Cyber Essentials, ISO, ICO certification, and similar)
