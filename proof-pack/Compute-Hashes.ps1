<#
.SYNOPSIS
    Write SHA-256 hashes for DB Bridge product files.

.DESCRIPTION
    Generates proof-pack/SHA256SUMS from the current tree. The
    SHA256SUMS.template file is a layout only.

    Build class: UNSIGNED INTERNAL
#>
[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [string]$Output = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}
if (-not $Output) {
    $Output = Join-Path $PSScriptRoot "SHA256SUMS"
}

$patterns = @(
    "pyproject.toml",
    "uv.lock",
    "server.json",
    ".env.example",
    "README.md",
    "AUDIT-NOTES.md",
    "installer\Install-DbBridge.ps1",
    "installer\Uninstall-DbBridge.ps1",
    "installer\README.md",
    "scripts\self_test.py",
    "scripts\self_test.ps1",
    "proof-pack\SIGNING.md",
    "src\postgresql_mcp\*.py"
)

$files = @()
foreach ($pattern in $patterns) {
    $files += Get-ChildItem -Path (Join-Path $RepoRoot $pattern) -File -ErrorAction SilentlyContinue
}

$lines = @(
    "# SHA256SUMS — airgap-db-bridge",
    "# Build class: UNSIGNED INTERNAL (not Authenticode-signed)",
    "# Thumbprint: (none — unsigned)",
    "# Generated (UTC): $([DateTime]::UtcNow.ToString('o'))",
    ""
)

foreach ($file in $files | Sort-Object FullName -Unique) {
    $hash = Get-FileHash -Algorithm SHA256 -Path $file.FullName
    $rel = $file.FullName.Substring($RepoRoot.Length).TrimStart("\", "/") -replace "\\", "/"
    $lines += "{0}  {1}" -f $hash.Hash.ToLowerInvariant(), $rel
}

$lines | Set-Content -Encoding ascii -Path $Output
Write-Host "Wrote $Output (UNSIGNED INTERNAL — hashes are not a signature)"
