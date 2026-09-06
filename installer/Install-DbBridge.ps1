<#
.SYNOPSIS
    Per-user installer for Airgap Fleet DB Bridge (Private Desk).

.DESCRIPTION
    Installs airgap-db-bridge into a per-user directory. Setup may use the
    network for prerequisites (Python packages, uv). The running bridge does
    not phone home.

    Build class: UNSIGNED INTERNAL
    This installer is not Authenticode-signed. Thumbprint: (none — unsigned).

.PARAMETER Dsn
    PostgreSQL connection string. Also accepted from DB_BRIDGE_DSN,
    POSTGRES_DSN, or POSTGRESQL_MCP_DSN when this switch is omitted.

.PARAMETER Quiet
    Reduce console output. The UNSIGNED INTERNAL label is still printed.

.PARAMETER SkipSelfTest
    Skip the post-install protocol-only self-test hook.

.PARAMETER FullSelfTest
    Run the full-DB self-test after install. Requires a reachable DSN.
    Protocol-only PASS is not full tool coverage.

.PARAMETER InstallDir
    Override the per-user install directory.

.PARAMETER RepoRoot
    Source tree to install from (defaults to the repository containing this script).
#>
[CmdletBinding()]
param(
    [string]$Dsn = "",
    [switch]$Quiet,
    [switch]$SkipSelfTest,
    [switch]$FullSelfTest,
    [string]$InstallDir = "",
    [string]$RepoRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Info {
    param([string]$Message)
    if (-not $Quiet) {
        Write-Host $Message
    }
}

function Write-UnsignedLabel {
    Write-Host ""
    Write-Host "============================================================"
    Write-Host "  Airgap Fleet — DB Bridge installer"
    Write-Host "  Build class : UNSIGNED INTERNAL"
    Write-Host "  Authenticode: not signed"
    Write-Host "  Thumbprint  : (none — unsigned)"
    Write-Host "============================================================"
    Write-Host ""
}

function Resolve-Dsn {
    param([string]$Explicit)
    if ($Explicit) { return $Explicit }
    foreach ($name in @("DB_BRIDGE_DSN", "POSTGRES_DSN", "POSTGRESQL_MCP_DSN")) {
        $value = [Environment]::GetEnvironmentVariable($name, "Process")
        if (-not $value) {
            $value = [Environment]::GetEnvironmentVariable($name, "User")
        }
        if ($value) { return $value }
    }
    return ""
}

function Find-Python {
    $candidates = @(
        @{ Cmd = "py"; Args = @("-3.12") },
        @{ Cmd = "py"; Args = @("-3.11") },
        @{ Cmd = "py"; Args = @("-3") },
        @{ Cmd = "python3"; Args = @() },
        @{ Cmd = "python"; Args = @() }
    )
    foreach ($item in $candidates) {
        $cmd = Get-Command $item.Cmd -ErrorAction SilentlyContinue
        if (-not $cmd) { continue }
        try {
            $versionOutput = & $cmd.Source @($item.Args + @("-c", "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')")) 2>$null
            if ($LASTEXITCODE -ne 0 -or -not $versionOutput) { continue }
            $parts = $versionOutput.Trim().Split(".")
            if ([int]$parts[0] -gt 3 -or ([int]$parts[0] -eq 3 -and [int]$parts[1] -ge 11)) {
                return @{ Executable = $cmd.Source; Args = $item.Args }
            }
        } catch {
            continue
        }
    }
    throw "Python 3.11 or newer is required. Install Python, then re-run this installer."
}

function Find-Uv {
    $uv = Get-Command uv -ErrorAction SilentlyContinue
    if ($uv) { return $uv.Source }
    return $null
}

Write-UnsignedLabel

if (-not $RepoRoot) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}
if (-not $InstallDir) {
    $InstallDir = Join-Path $env:LOCALAPPDATA "AirgapFleet\db-bridge"
}

$ResolvedDsn = Resolve-Dsn -Explicit $Dsn
$PinSource = "unpinned (uv.lock not applied)"

Write-Info "Repository : $RepoRoot"
Write-Info "Install dir: $InstallDir"
if ($ResolvedDsn) {
    Write-Info "DSN        : (provided; stored as DB_BRIDGE_DSN for this user)"
} else {
    Write-Info "DSN        : not provided — protocol-only self-test still works; full DB tools need a DSN"
}

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
$VenvDir = Join-Path $InstallDir "venv"
$ScriptsDir = Join-Path $InstallDir "scripts"

$python = Find-Python
Write-Info "Creating per-user virtual environment..."
& $python.Executable @($python.Args + @("-m", "venv", $VenvDir))
if ($LASTEXITCODE -ne 0) {
    throw "Failed to create virtual environment at $VenvDir"
}

$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    throw "venv python not found at $VenvPython"
}

& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw "pip upgrade failed"
}

$Lockfile = Join-Path $RepoRoot "uv.lock"
$uv = Find-Uv
if ((Test-Path $Lockfile) -and $uv) {
    Write-Info "Pinning environment from uv.lock via uv export --frozen..."
    $ReqFile = Join-Path $InstallDir "requirements.lock.txt"
    & $uv export --frozen --no-dev --project $RepoRoot -o $ReqFile
    if ($LASTEXITCODE -eq 0) {
        & $VenvPython -m pip install -r $ReqFile
        if ($LASTEXITCODE -ne 0) { throw "Lockfile pip install failed" }
        & $VenvPython -m pip install --no-deps --editable $RepoRoot
        if ($LASTEXITCODE -ne 0) { throw "Editable install failed" }
        $PinSource = "uv.lock"
    } else {
        Write-Warning "uv export failed; falling back to unpinned editable install."
        & $VenvPython -m pip install --editable $RepoRoot
        if ($LASTEXITCODE -ne 0) { throw "Editable install failed" }
    }
} elseif (Test-Path $Lockfile) {
    Write-Warning "uv.lock is present but uv was not found. Install will not be lockfile-pinned."
    Write-Info "Installing airgap-db-bridge in editable mode (network required for wheels)..."
    & $VenvPython -m pip install --editable $RepoRoot
    if ($LASTEXITCODE -ne 0) { throw "Editable install failed" }
} else {
    Write-Info "Installing airgap-db-bridge in editable mode (network required for wheels)..."
    & $VenvPython -m pip install --editable $RepoRoot
    if ($LASTEXITCODE -ne 0) { throw "Editable install failed" }
}

New-Item -ItemType Directory -Force -Path $ScriptsDir | Out-Null
Copy-Item -Force (Join-Path $RepoRoot "scripts\self_test.py") (Join-Path $ScriptsDir "self_test.py")
Copy-Item -Force (Join-Path $RepoRoot "scripts\self_test.ps1") (Join-Path $ScriptsDir "self_test.ps1")

$Launcher = Join-Path $InstallDir "airgap-db-bridge.cmd"
@"
@echo off
REM UNSIGNED INTERNAL — not Authenticode-signed
"$VenvPython" -m postgresql_mcp %*
"@ | Set-Content -Encoding ASCII -Path $Launcher

$DsnSetByInstaller = $false
if ($ResolvedDsn) {
    [Environment]::SetEnvironmentVariable("DB_BRIDGE_DSN", $ResolvedDsn, "User")
    [Environment]::SetEnvironmentVariable("DB_BRIDGE_DSN", $ResolvedDsn, "Process")
    $DsnSetByInstaller = $true
}

$McpExample = Join-Path $InstallDir "mcp-config.example.json"
$dsnForExample = if ($ResolvedDsn) { $ResolvedDsn } else { "postgresql://user:pass@localhost:5432/dbname" }
$mcp = [ordered]@{
    mcpServers = [ordered]@{
        database = [ordered]@{
            command = (Join-Path $VenvDir "Scripts\airgap-db-bridge.exe")
            env     = [ordered]@{
                DB_BRIDGE_DSN = $dsnForExample
            }
        }
    }
}
$mcp | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 -Path $McpExample

$info = [ordered]@{
    product            = "airgap-db-bridge"
    version            = "1.0.3"
    buildClass         = "UNSIGNED INTERNAL"
    authenticode       = "unsigned"
    thumbprint         = $null
    pinSource          = $PinSource
    installDir         = $InstallDir
    repoRoot           = $RepoRoot
    dsnSetByInstaller  = $DsnSetByInstaller
    installedAtUtc     = [DateTime]::UtcNow.ToString("o")
    telemetry          = "none"
}
$info | ConvertTo-Json | Set-Content -Encoding UTF8 -Path (Join-Path $InstallDir "INSTALL-INFO.json")
"UNSIGNED INTERNAL`r`nAuthenticode: not signed`r`nThumbprint: (none — unsigned)`r`n" |
    Set-Content -Encoding ASCII -Path (Join-Path $InstallDir "UNSIGNED-INTERNAL.txt")

Write-Host "Installed airgap-db-bridge (UNSIGNED INTERNAL). Pin source: $PinSource"
Write-Host "Launcher : $Launcher"
Write-Host "MCP example config: $McpExample"
Write-Host ""
Write-Host "Self-test caveat: protocol-only PASS is not full tool coverage and does not prove a live PostgreSQL connection."

if (-not $SkipSelfTest) {
    $selfTest = Join-Path $ScriptsDir "self_test.ps1"
    if ($FullSelfTest) {
        if (-not $ResolvedDsn) {
            throw "Full self-test requires a DSN. Pass -Dsn or set DB_BRIDGE_DSN. Protocol-only PASS is not full tool coverage."
        }
        Write-Info "Running full DB self-test..."
        & $selfTest -Full -Dsn $ResolvedDsn -Python $VenvPython
    } else {
        Write-Info "Running protocol-only self-test (not full tool coverage)..."
        & $selfTest -ProtocolOnly -Python $VenvPython
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Post-install self-test failed with exit code $LASTEXITCODE"
    }
}

Write-Host "Install complete."
exit 0
