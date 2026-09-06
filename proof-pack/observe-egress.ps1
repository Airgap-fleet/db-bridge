<#
.SYNOPSIS
    Snapshot TCP endpoints around a protocol-only DB Bridge self-test.

.DESCRIPTION
    Observation aid only — not a certification, not a telemetry audit report.

    Build class: UNSIGNED INTERNAL
#>
[CmdletBinding()]
param(
    [string]$OutputDir = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "DB Bridge egress observation — UNSIGNED INTERNAL (not a certification)"
Write-Host "NOTE: protocol-only PASS is not full tool coverage."

if (-not $OutputDir) {
    $OutputDir = Join-Path $PSScriptRoot "egress-observation"
}
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

function Get-TcpSnapshot {
    try {
        Get-NetTCPConnection -ErrorAction Stop |
            Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State, OwningProcess |
            Sort-Object RemoteAddress, RemotePort
    } catch {
        netstat -ano
    }
}

$before = Join-Path $OutputDir "tcp-before.txt"
$after = Join-Path $OutputDir "tcp-after.txt"
Get-TcpSnapshot | Out-File -Encoding utf8 $before

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$selfTest = Join-Path $repoRoot "scripts\self_test.ps1"
& $selfTest -ProtocolOnly
$selfTestExit = $LASTEXITCODE

Get-TcpSnapshot | Out-File -Encoding utf8 $after

@"
UNSIGNED INTERNAL observation
Self-test exit code: $selfTestExit
Protocol-only PASS is not full tool coverage.
Compare:
  $before
  $after
Expected: no new unexpected remote hosts. Protocol-only should not open Postgres.
This file is not a compliance certificate.
"@ | Set-Content -Encoding utf8 (Join-Path $OutputDir "NOTES.txt")

Write-Host "Wrote snapshots under $OutputDir"
exit $selfTestExit
