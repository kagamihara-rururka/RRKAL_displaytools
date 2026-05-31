param(
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$scriptName = "scripts/check_display_shell_render_matrix.ps1"

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.display_shell_render_matrix_check.v1"
        source = $scriptName
        status = "contract_only_no_launch_side_effect"
        exporter_command = "py -3 scripts\export_display_shell_render_matrix.py"
        output_mode = "stdout_json"
        boundary = "Check reads the headless display shell exporter only; it does not launch Qt, Taichi or concrete renderer packages."
        portable = $true
    } | ConvertTo-Json -Depth 8
    exit 0
}

$packetText = & py -3 scripts\export_display_shell_render_matrix.py
if ($LASTEXITCODE -ne 0) {
    throw "Display shell render matrix exporter failed"
}

$packet = ($packetText -join "`n") | ConvertFrom-Json
$failures = @()

if ($packet.schema -ne "rrkal_displaytools.display_shell_render_matrix.v1") {
    $failures += "capability schema mismatch"
}
if ($packet.canvas_registry_schema -ne "rrkal_displaytools.canvas_registry.v1") {
    $failures += "canvas registry schema missing"
}
if ($packet.sample_view_models_schema -ne "rrkal_displaytools.sample_view_models.v1") {
    $failures += "sample ViewModel schema missing"
}
if ($packet.sample_view_model_render_plans_schema -ne "rrkal_displaytools.sample_view_model_render_plans.v1") {
    $failures += "sample ViewModel render plans schema missing"
}
if (@($packet.canvas_types) -notcontains "earth") {
    $failures += "EarthCanvas missing"
}
if (@($packet.canvas_types) -notcontains "time_series") {
    $failures += "TimeSeriesCanvas missing"
}
if (@($packet.layer_types) -notcontains "geo_layer") {
    $failures += "geo_layer missing"
}
if (@($packet.layer_types) -notcontains "time_series_layer") {
    $failures += "time_series_layer missing"
}
if ([int]$packet.registered_renderer_count -lt 2) {
    $failures += "registered renderer samples missing"
}
if ($packet.sample_view_model_render_plans.runtime_render_invoked -ne $false) {
    $failures += "runtime render should not be invoked"
}

$status = "pass"
if ($failures.Count -gt 0) {
    $status = "fail"
}

$result = [ordered]@{
    schema = "rrkal_displaytools.display_shell_render_matrix_check.v1"
    source = $scriptName
    status = $status
    exporter_schema = $packet.schema
    canvas_types = @($packet.canvas_types)
    layer_types = @($packet.layer_types)
    registered_renderer_count = [int]$packet.registered_renderer_count
    runtime_render_invoked = [bool]$packet.sample_view_model_render_plans.runtime_render_invoked
    failures = $failures
    boundary = "Pass/fail check validates display_core contracts only; runtime renderer execution remains out of scope."
}

$result | ConvertTo-Json -Depth 8
if ($failures.Count -gt 0) {
    exit 1
}
