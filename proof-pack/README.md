# Proof pack — airgap-db-bridge

Evidence notes for an **UNSIGNED INTERNAL** Private Desk build of DB Bridge.

This folder is not a certification. It does not claim Cyber Essentials, ISO 27001, NCSC approval, or any other mark.

## What is in here

| File | Purpose |
|------|---------|
| [DEMO-CHECKLIST.md](DEMO-CHECKLIST.md) | Steps to demonstrate the installer and self-test |
| [SIGNING.md](SIGNING.md) | UNSIGNED INTERNAL labelling and thumbprint placeholder |
| [EGRESS.md](EGRESS.md) | Observation notes for outbound connections |
| [observe-egress.ps1](observe-egress.ps1) | Windows helper to snapshot TCP endpoints around a self-test |
| [Compute-Hashes.ps1](Compute-Hashes.ps1) | SHA-256 listing of product files |
| [SHA256SUMS.template](SHA256SUMS.template) | Template for recorded hashes |
| [KNOWN-LIMITATIONS.md](KNOWN-LIMITATIONS.md) | Honest limits |
| [VERSION.md](VERSION.md) | Package version note |

## Honesty

- **Protocol-only PASS is not full tool coverage.** `initialize` + `tools/list` can succeed with no PostgreSQL.
- **A full database demo needs Postgres.** Use a local instance or `docker compose up postgresql`.
- **This build is UNSIGNED INTERNAL.** There is no Authenticode signature and no thumbprint.
- **No telemetry.** The running bridge does not phone home. Installer setup may use the network for wheels.

## Product tree only

Ship `src/`, `tests/`, `installer/`, `scripts/`, `proof-pack/`, packaging config, and the product README. Do not nest vault folders (`00_Master`, `01_Obi-Wan`, `Anakin`, `Chat Logs`, and similar) in a release commit.
