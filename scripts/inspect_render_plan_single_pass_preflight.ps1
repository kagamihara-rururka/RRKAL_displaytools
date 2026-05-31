param(
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$scriptName = "scripts/inspect_render_plan_single_pass_preflight.ps1"
$schema = "rrkal_displaytools.render_plan_single_pass_preflight_inspector.v1"
$contractSchema = "rrkal_displaytools.layer_render_plan_single_pass_preflight_contract.v1"

if ($ContractOnly) {
    [ordered]@{
        schema = $schema
        source = $scriptName
        status = "contract_only_no_runtime"
        verifies_schema = $contractSchema
        runtime_single_pass_enabled = $false
        boundary = "Inspector only; it does not launch Qt, Taichi, render frames, or enable runtime single-pass composition."
        portable = $true
    } | ConvertTo-Json -Depth 8
    exit 0
}

$sourcePath = Join-Path $RepoRoot "render_core\render_plan.py"
$source = Get-Content -LiteralPath $sourcePath -Raw -Encoding UTF8
$markers = [ordered]@{
    contract_schema = $source -like "*$contractSchema*"
    disabled_runtime_gate = $source -like "*runtime_single_pass_enabled*"
    unchanged_runtime_path_gate = $source -like "*runtime_path_unchanged*"
    parity_smoke_gate = $source -like "*compose_run_parity_smoke*"
    phase_timing_gate = $source -like "*phase_timing_runtime_metadata*"
    manual_review_gate = $source -like "*manual_visual_review*"
    zero_diff_gate = $source -like "*zero_diff_against_sequential_compose_queue*"
}
$missing = @()
foreach ($marker in $markers.GetEnumerator()) {
    if (-not $marker.Value) {
        $missing += $marker.Key
    }
}

[ordered]@{
    schema = $schema
    source = $scriptName
    status = if ($missing.Count -eq 0) { "ready" } else { "incomplete" }
    verifies_schema = $contractSchema
    runtime_single_pass_enabled = $false
    runtime_path_unchanged = $true
    markers = $markers
    missing_markers = $missing
    next_step = "Use this inspector before prototyping opt-in single-pass composition."
    boundary = "Inspector only; it reads render_core source markers and does not launch Qt, Taichi, render frames, or enable runtime single-pass composition."
    portable = $true
} | ConvertTo-Json -Depth 8
