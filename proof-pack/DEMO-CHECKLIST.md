# Demo checklist

Build class: **UNSIGNED INTERNAL**.

A full database demo **needs Postgres**. Protocol-only success is not enough to claim the tools work.

## 1. Clean tree

- [ ] Working copy contains only the product tree (`src/`, `tests/`, `installer/`, `scripts/`, `proof-pack/`, packaging config, README).
- [ ] No nested vault folders (`00_Master`, `01_Obi-Wan`, `02_Sub-Agents`, `03_Context`, `04_Daily_Logs`, `05_Skills`, `05_Studies`, `Anakin`, `Chat Logs`, `July 2026`, `masters-profile`, `projects`).
- [ ] No stale `db-bridge-1.0.0*` / `db_bridge-1.0.0*` / `postgresql-mcp-1.0.0*` artefacts in `dist/` or the repository root.

## 2. Windows install (recommended)

- [ ] `Set-ExecutionPolicy -Scope Process Bypass`
- [ ] `.\installer\Install-DbBridge.ps1 -Dsn "postgresql://…"`
- [ ] Console shows **UNSIGNED INTERNAL** and thumbprint `(none — unsigned)`.
- [ ] Post-install protocol-only self-test runs (unless `-SkipSelfTest`).

## 3. Self-test honesty

- [ ] `.\scripts\self_test.ps1 -ProtocolOnly` — expect PASS plus the caveat that this is **not** full tool coverage.
- [ ] Without a DSN, `.\scripts\self_test.ps1 -Full` **fails loudly**.
- [ ] With Postgres up and a real DSN, `.\scripts\self_test.ps1 -Full -Dsn "…"` calls `list_tables`.

## 4. Verify / uninstall

- [ ] MCP example config exists under `%LOCALAPPDATA%\AirgapFleet\db-bridge\mcp-config.example.json` and uses `DB_BRIDGE_DSN`.
- [ ] `.\installer\Uninstall-DbBridge.ps1` removes the per-user directory.

## 5. Hashes and egress (optional observation)

- [ ] `.\proof-pack\Compute-Hashes.ps1` writes `SHA256SUMS` (do not treat the template as live hashes).
- [ ] `.\proof-pack\observe-egress.ps1` around a protocol-only run — observation only, not a certification.

## 6. Advanced (pip / uvx)

Only if the Windows installer is not in use:

```powershell
pip install airgap-db-bridge
# or
uvx airgap-db-bridge
```

Still set `DB_BRIDGE_DSN` for any live database work.
