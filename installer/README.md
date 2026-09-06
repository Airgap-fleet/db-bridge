# DB Bridge Windows installer

Recommended install path for Private Desk on Windows.

**Build class: UNSIGNED INTERNAL.** These scripts are not Authenticode-signed. Thumbprint: (none — unsigned). WiX/MSI Authenticode packaging is out of scope.

Setup may use the network to fetch Python wheels or `uv`. **The running bridge does not phone home.**

## Install (per-user)

From a clone of this repository, in PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\installer\Install-DbBridge.ps1 -Dsn "postgresql://user:pass@localhost:5432/dbname"
```

Silent / unattended (label still printed):

```powershell
.\installer\Install-DbBridge.ps1 -Dsn "postgresql://user:pass@localhost:5432/dbname" -Quiet
```

DSN may also come from `DB_BRIDGE_DSN`, or from legacy `POSTGRES_DSN` / `POSTGRESQL_MCP_DSN` when the canonical name is unset.

Default location: `%LOCALAPPDATA%\AirgapFleet\db-bridge`.

The installer:

- creates a per-user virtual environment
- pins dependencies from `uv.lock` when `uv` is available
- writes `INSTALL-INFO.json` and an `UNSIGNED-INTERNAL.txt` marker
- writes `mcp-config.example.json` for Cursor / Claude Desktop
- runs a **protocol-only** self-test unless you pass `-SkipSelfTest`

## Verify

```powershell
.\scripts\self_test.ps1 -ProtocolOnly
```

**Caveat:** protocol-only PASS means `initialize` and `tools/list` succeeded. It is **not** full tool coverage and does **not** prove a live PostgreSQL connection.

Full database check (fails loudly without a DSN):

```powershell
.\scripts\self_test.ps1 -Full -Dsn "postgresql://user:pass@localhost:5432/dbname"
```

Or ask the installer to run the full check:

```powershell
.\installer\Install-DbBridge.ps1 -Dsn "postgresql://..." -FullSelfTest
```

## Uninstall

```powershell
.\installer\Uninstall-DbBridge.ps1
```

This removes the per-user install directory. If the installer stored `DB_BRIDGE_DSN` for the user, that variable is removed. PostgreSQL itself is left alone.

## After install

Point your MCP client at the generated `airgap-db-bridge.exe` (or `airgap-db-bridge.cmd`) and set `DB_BRIDGE_DSN`. See the repository README.
