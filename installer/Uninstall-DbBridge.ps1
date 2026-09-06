<#
.SYNOPSIS
    Remove a per-user Airgap Fleet DB Bridge install.

.DESCRIPTION
    Deletes the per-user install directory created by Install-DbBridge.ps1.
    If the installer wrote DB_BRIDGE_DSN for this user, that user environment
    variable is removed. PostgreSQL itself is not touched.

    Build class: UNSIGNED INTERNAL

.PARAMETER InstallDir
    Override the per-user install directory.

.PARAMETER Quiet
    Reduce console output. The UNSIGNED INTERNAL label is still printed.
#>
[CmdletBinding()]
param(
    [string]$InstallDir = "",
    [switch]$Quiet
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Info {
    param([string]$Message)
    if (-not $Quiet) {
        Write-Host $Message
    }
}

Write-Host "Airgap Fleet DB Bridge uninstaller — UNSIGNED INTERNAL (not Authenticode-signed)"

if (-not $InstallDir) {
    $InstallDir = Join-Path $env:LOCALAPPDATA "AirgapFleet\db-bridge"
}

if (-not (Test-Path $InstallDir)) {
    Write-Info "Nothing to remove at $InstallDir"
    exit 0
}

$infoPath = Join-Path $InstallDir "INSTALL-INFO.json"
$removeDsn = $false
if (Test-Path $infoPath) {
    try {
        $info = Get-Content -Raw -Path $infoPath | ConvertFrom-Json
        if ($info.dsnSetByInstaller -eq $true) {
            $removeDsn = $true
        }
    } catch {
        Write-Warning "Could not parse INSTALL-INFO.json; user DB_BRIDGE_DSN will be left in place."
    }
}

Write-Info "Removing $InstallDir"
Remove-Item -LiteralPath $InstallDir -Recurse -Force

if ($removeDsn) {
    Write-Info "Removing user environment variable DB_BRIDGE_DSN (set by this installer)"
    [Environment]::SetEnvironmentVariable("DB_BRIDGE_DSN", $null, "User")
}

Write-Host "Uninstall complete. PostgreSQL data was not modified."
exit 0
