# DB Bridge - Client guide

**For:** COLP, practice manager, and firm IT evaluating or installing DB Bridge  
**Product:** DB Bridge (Airgap Fleet) - a local connector your AI desk uses to query PostgreSQL on your own network  
**Version:** 1.0.3 (see `proof-pack\VERSION.txt`)  
**Build status:** UNSIGNED INTERNAL - no Authenticode certificate on this build yet. SmartScreen or firm policy may warn; treat as an internal / pilot artefact until a signed release is issued.

Plain English for install and evaluation. Developer detail lives in `README.md`.

---

## 1. What this is / who it is for

DB Bridge lets your AI desk (Claude Desktop, Cursor, and similar) run **controlled operations against a PostgreSQL database you choose** - usually on this PC or your firm network - without sending results to a DB Bridge vendor cloud.

The bridge is a small local program: it talks to the AI desk on the same machine and to the DSN you configure.

**For:** UK solicitors / small firms evaluating Private Desk / Airgap Fleet; COLP / practice managers needing a clear data-boundary story; firm IT needing install, verify, and uninstall steps.

**Not yet for:** package-manager or Docker-first developer workflows (see `README.md`); signed MSI / Intune rollouts (PowerShell one-command install is the supported Windows path today).

---

## 2. What never leaves your PC

In default local mode:

- Tool traffic goes only to **the PostgreSQL DSN you supply** (localhost or firm host) - not to a vendor API.
- The bridge uses a **local process connection** (stdio JSON-RPC; no listening port in the air-gap demo path).
- **No telemetry**, no vendor cloud sync of query results, and no model API call by the bridge itself.
- Logs stay local (structured logging on stderr).

**Honest boundary:** Claude Desktop / Cursor are separate products with their own network behaviour. This pack shows the **DB Bridge process** does not open vendor outbound connections; it does not certify third-party AI clients.

**Setup vs day-to-day:** the installer may use the internet **during setup only**. Runtime uses stdio plus your DSN.

We do **not** claim ISO 27001, SOC 2, Cyber Essentials, Lexcel, or similar. Use the proof pack as evidence for *your* auditor. Live demo: `proof-pack\DEMO-CHECKLIST.md` (prefer local Postgres when proving DB tools).

---

## 3. System requirements

| Item | Requirement |
|------|-------------|
| OS | Windows 10 or 11 |
| Shell | PowerShell 5.1+ |
| Database | Reachable PostgreSQL DSN for full use |
| AI desk | Claude Desktop and/or Cursor (optional for self-test only) |
| Network | Internet may be needed **at setup**; runtime needs your DSN, not vendor internet |
| Privileges | Per-user under `%LOCALAPPDATA%\AirgapFleet\db-bridge` (no machine-wide admin by default) |

Use the extracted product tree (`installer\`, `scripts\`, `proof-pack\`, `pyproject.toml`, `uv.lock`). Do **not** clone from GitHub as a client install step.

---

## 4. Install (one command - aim under 15 minutes; must be under 30)

1. Extract the bundle to a short path (example: `C:\AirgapFleet\db-bridge-bundle`).
2. Open PowerShell and `cd` to the folder that contains `installer\` and `pyproject.toml`.
3. Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\installer\Install-DbBridge.ps1 -Dsn "postgresql://user:pass@localhost:5432/dbname"
```

The installer checks prerequisites, may download setup tools once, installs under `%LOCALAPPDATA%\AirgapFleet\db-bridge`, registers "DB Bridge (Airgap Fleet)" in Add/Remove Programs, optionally writes AI-desk connector settings, and runs a self-test - **failing loudly** if that does not pass.

**Silent / unattended:** add `-Quiet`. Optional: `-SkipClientConfig`, `-SkipSelfTest` (not recommended), `-Client claude_desktop|cursor|both|none` (see `installer\README.md`). Or set `DB_BRIDGE_DSN` and omit `-Dsn`.

First clean-laptop install often takes **10-20 minutes** (setup downloads); target **under 15** when ready, hard ceiling **under 30**.

---

## 5. First run / smoke check

**Full check (preferred - needs live Postgres):**

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\self_test.ps1 -Dsn "postgresql://user:pass@localhost:5432/dbname" -RequireDb
```

**Pass:** `[OK] self-test passed` after a real DB tool exercise (for example list tables).

**Protocol-only caveat:** if Postgres is unreachable:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\self_test.ps1 -AllowProtocolOnly
```

That only confirms **initialize + tools/list** over stdio. It does **not** prove query / list / describe work against your database. Use protocol-only as a connector smoke check; require `-Dsn` + `-RequireDb` before go-live.

Then confirm the connector in your AI desk and try a simple list-tables request. On `[FAIL]`, fix the stated issue and re-run - do not leave a half-finished install.

---

## 6. Verify download

```powershell
Get-FileHash -Algorithm SHA256 .\installer\Install-DbBridge.ps1
Get-FileHash -Algorithm SHA256 .\scripts\self_test.ps1
Get-FileHash -Algorithm SHA256 .\uv.lock
```

Match each hash to `proof-pack\SHA256SUMS` (refresh with `proof-pack\Compute-Hashes.ps1` after rebuilds).

**Signing:** **UNSIGNED INTERNAL** - Digital Signatures tab empty until Authenticode ships (`proof-pack\SIGNING.md`). Do not present this build as signed.

---

## 7. Uninstall

```powershell
powershell -ExecutionPolicy Bypass -File .\installer\Uninstall-DbBridge.ps1
```

Or **Settings > Apps > DB Bridge (Airgap Fleet)**. Removes the per-user install and Add/Remove entry. AI-desk connector lines (if any) stay for manual cleanup. PostgreSQL data is never deleted.

---

## 8. Support / escalate

- Escalate via your **Airgap Fleet / firm channel** (pilot contact: Brooke).
- Do not post DSNs, passwords, or client data on public forums.
- Evaluation pack: self-test output (prefer full `-RequireDb`), plus `proof-pack\Observe-Egress.ps1` / `DEMO-CHECKLIST.md` evidence if used.

---

## Quick reference

| Task | Command / place |
|------|-----------------|
| Install | `.\installer\Install-DbBridge.ps1 -Dsn "..."` |
| Full smoke | `.\scripts\self_test.ps1 -Dsn "..." -RequireDb` |
| Protocol-only | `.\scripts\self_test.ps1 -AllowProtocolOnly` |
| Checksums | `Get-FileHash` + `proof-pack\SHA256SUMS` |
| Uninstall | `.\installer\Uninstall-DbBridge.ps1` |
| Developer docs | `README.md` |
