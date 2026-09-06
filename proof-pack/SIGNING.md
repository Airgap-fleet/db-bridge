# Signing

**Build class: UNSIGNED INTERNAL**

This repository ships a per-user PowerShell installer, not a WiX/MSI package. Authenticode signing spend is out of scope for this release.

| Field | Value |
|-------|--------|
| Product | airgap-db-bridge |
| Version | 1.0.3 (see `pyproject.toml`) |
| Authenticode | not signed |
| **Thumbprint** | `(none — unsigned)` — placeholder until a signed release exists |
| Timestamp server | n/a |

## What you should see

Installer, uninstaller, self-test, and this proof pack all carry the **UNSIGNED INTERNAL** label. Treat binaries and scripts as unsigned internal builds.

Do not claim the installer is signed. Do not invent a certificate thumbprint.

## How to record hashes instead

```powershell
.\proof-pack\Compute-Hashes.ps1
```

Compare the generated `proof-pack/SHA256SUMS` against the files you actually ran. `SHA256SUMS.template` is a layout only.
