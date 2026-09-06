<#
.SYNOPSIS
    Run the DB Bridge MCP stdio self-test.

.DESCRIPTION
    Default mode is protocol-only (initialize + tools/list). That PASS is not
    full tool coverage and does not prove a live PostgreSQL connection.

    Build class: UNSIGNED INTERNAL

.PARAMETER ProtocolOnly
    initialize + tools/list only (default).

.PARAMETER Full
    Also call list_tables. Fails loudly if no DSN is available.

.PARAMETER Dsn
    PostgreSQL DSN (or set DB_BRIDGE_DSN).

.PARAMETER Python
    Interpreter that has airgap-db-bridge installed.
#>
[CmdletBinding()]
param(
    [switch]$ProtocolOnly,
    [switch]$Full,
    [string]$Dsn = "",
    [string]$Python = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "airgap-db-bridge self-test — UNSIGNED INTERNAL (not Authenticode-signed)"

if ($Full -and $ProtocolOnly) {
    throw "Specify only one of -ProtocolOnly or -Full."
}

$here = $PSScriptRoot
$pyScript = Join-Path $here "self_test.py"
if (-not (Test-Path $pyScript)) {
    throw "self_test.py not found next to this script: $pyScript"
}

$pythonExe = $Python
if (-not $pythonExe) {
    foreach ($name in @("python", "python3", "py")) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) {
            $pythonExe = $cmd.Source
            break
        }
    }
}
if (-not $pythonExe) {
    throw "Python was not found. Pass -Python or install Python 3.11+."
}

$argList = @($pyScript)
if ($Full) {
    $argList += "--full"
    if (-not $Dsn) {
        $Dsn = $env:DB_BRIDGE_DSN
        if (-not $Dsn) { $Dsn = $env:POSTGRES_DSN }
        if (-not $Dsn) { $Dsn = $env:POSTGRESQL_MCP_DSN }
    }
    if (-not $Dsn) {
        Write-Error "Full DB self-test requires a DSN. Pass -Dsn or set DB_BRIDGE_DSN. Protocol-only PASS is not full tool coverage."
        exit 2
    }
    $argList += @("--dsn", $Dsn)
} else {
    $argList += "--protocol-only"
}

Write-Host "NOTE: protocol-only PASS is not full tool coverage and does not prove a live PostgreSQL connection."
& $pythonExe @argList
exit $LASTEXITCODE
