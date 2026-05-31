param(
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$scriptName = "scripts/check_display_runtime_contracts.ps1"

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.display_runtime_contracts_check.v1"
        source = $scriptName
        status = "contract_only_no_launch_side_effect"
        exporter_command = "py -3 scripts\export_display_runtime_contracts.py"
        boundary = "Check validates runtime landing-zone contracts only; it does not launch renderer backends."
        portable = $true
    } | ConvertTo-Json -Depth 8
    exit 0
}

$packetText = & py -3 scripts\export_display_runtime_contracts.py
if ($LASTEXITCODE -ne 0) {
    throw "Display runtime contracts exporter failed"
}

$packet = ($packetText -join "`n") | ConvertFrom-Json
$failures = @()

if ($packet.schema -ne "rrkal_displaytools.display_runtime_contracts.v1") {
    $failures += "runtime contracts schema mismatch"
}
if ([int]$packet.contract_count -lt 2) {
    $failures += "expected at least two runtime canvas contracts"
}
if (@($packet.canvas_types) -notcontains "earth") {
    $failures += "EarthCanvas runtime contract missing"
}
if (@($packet.canvas_types) -notcontains "time_series") {
    $failures += "TimeSeriesCanvas runtime contract missing"
}
if ($packet.runtime_render_invoked -ne $false) {
    $failures += "runtime render should not be invoked"
}
if ($packet.imports_renderer_packages -ne $false) {
    $failures += "renderer packages should not be imported"
}

$status = "pass"
if ($failures.Count -gt 0) {
    $status = "fail"
}

$result = [ordered]@{
    schema = "rrkal_displaytools.display_runtime_contracts_check.v1"
    source = $scriptName
    status = $status
    exporter_schema = $packet.schema
    contract_count = [int]$packet.contract_count
    canvas_types = @($packet.canvas_types)
    runtime_render_invoked = [bool]$packet.runtime_render_invoked
    imports_renderer_packages = [bool]$packet.imports_renderer_packages
    failures = $failures
    boundary = "Pass/fail check validates runtime contract landing zones only."
}

$result | ConvertTo-Json -Depth 8
if ($failures.Count -gt 0) {
    exit 1
}
