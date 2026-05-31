param(
    [string]$Template = "fast_synthetic",
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$scriptName = "scripts/inspect_render_plan_compose_work_order.ps1"

function Invoke-JsonPython {
    param([string[]]$ArgumentList)

    $text = & py -3 @ArgumentList
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: py -3 $($ArgumentList -join ' ')"
    }
    $raw = $text -join "`n"
    $jsonStart = $raw.IndexOf("{")
    if ($jsonStart -lt 0) {
        throw "JSON payload not found: py -3 $($ArgumentList -join ' ')"
    }
    return $raw.Substring($jsonStart) | ConvertFrom-Json
}

function Invoke-JsonPowerShell {
    param([string[]]$ArgumentList)

    $text = & powershell @ArgumentList
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: powershell $($ArgumentList -join ' ')"
    }
    $raw = $text -join "`n"
    $jsonStart = $raw.IndexOf("{")
    if ($jsonStart -lt 0) {
        throw "JSON payload not found: powershell $($ArgumentList -join ' ')"
    }
    return $raw.Substring($jsonStart) | ConvertFrom-Json
}

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.render_plan_compose_work_order_inspector.v1"
        source = $scriptName
        status = "contract_only_no_launch_side_effect"
        launch_packet_command = "py -3 scripts/export_launch_packet.py --template $Template"
        boundary_inspector_command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_decoupling_boundaries.ps1"
        output_schema = "rrkal_displaytools.render_plan_compose_work_order.v1"
        target_module = "render_core/render_plan.py"
        required_contracts = @(
            "rrkal_displaytools.layer_render_plan_performance.v1",
            "rrkal_displaytools.compiled_layer_render_plan.v1",
            "rrkal_displaytools.layer_render_plan_compose_queue.v1",
            "rrkal_displaytools.layer_render_plan_compose_runs.v1",
            "rrkal_displaytools.layer_render_plan_compose_run_parity_contract.v1"
        )
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_render_plan_compose_work_order.ps1"
        boundary = "Inspector builds a read-only work order for post-7 render_plan_compose extraction; it does not move code, enable runtime compose merging, launch Qt/Taichi, or touch RRKAL data/cache governance."
        portable = $true
    } | ConvertTo-Json -Depth 8
    exit 0
}

$launchPacket = Invoke-JsonPython @("scripts/export_launch_packet.py", "--template", $Template)
$boundaryInspection = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\inspect_decoupling_boundaries.ps1")

if (-not $launchPacket.layer_render_plan_performance) {
    throw "Launch packet layer_render_plan_performance field is missing"
}
if ($boundaryInspection.first_extraction_id -ne "render_plan_compose") {
    throw "Boundary inspection first extraction is not render_plan_compose"
}
if ($boundaryInspection.first_extraction_target -ne "render_core/render_plan.py") {
    throw "Boundary inspection first extraction target mismatch"
}

$renderPlan = $launchPacket.layer_render_plan_performance
if ($renderPlan.schema -ne "rrkal_displaytools.layer_render_plan_performance.v1") {
    throw "Layer render plan performance schema missing"
}
if ($renderPlan.compiled_plan_schema -ne "rrkal_displaytools.compiled_layer_render_plan.v1") {
    throw "Compiled layer render plan schema missing"
}
if ($renderPlan.compiled_plan_compose_queue_schema -ne "rrkal_displaytools.layer_render_plan_compose_queue.v1") {
    throw "Compose queue schema missing"
}
if ($renderPlan.compiled_plan_compose_runs_schema -ne "rrkal_displaytools.layer_render_plan_compose_runs.v1") {
    throw "Compose runs schema missing"
}
if ($renderPlan.compiled_plan_compose_run_parity_contract_schema -ne "rrkal_displaytools.layer_render_plan_compose_run_parity_contract.v1") {
    throw "Compose run parity contract schema missing"
}

[ordered]@{
    schema = "rrkal_displaytools.render_plan_compose_work_order.v1"
    source = $scriptName
    status = "ready_for_post_07_extraction"
    first_extraction_id = $boundaryInspection.first_extraction_id
    target_module = $boundaryInspection.first_extraction_target
    source_owner = "HybridRenderController runtime facts plus render_core/render_plan.py pure helpers"
    source_helpers = @(
        $renderPlan.runtime_snapshot_helper,
        $renderPlan.runtime_snapshot_input_collector,
        $renderPlan.compiled_plan_helper,
        $renderPlan.compiled_plan_cache_key_helper,
        $renderPlan.composition_steps_helper,
        $renderPlan.composition_steps_input_collector,
        $renderPlan.composition_apply_helper,
        $renderPlan.compiled_plan_compose_queue_helper,
        $renderPlan.compiled_plan_compose_runs_helper,
        $renderPlan.compiled_plan_compose_run_parity_contract_helper
    )
    keep_contracts = @($boundaryInspection.first_extraction_keep_contracts)
    required_schemas = @(
        $renderPlan.schema,
        $renderPlan.compiled_plan_schema,
        $renderPlan.compiled_plan_compose_queue_schema,
        $renderPlan.compiled_plan_compose_runs_schema,
        $renderPlan.compiled_plan_compose_run_parity_contract_schema,
        $renderPlan.compose_pass_budget_schema
    )
    smoke_gates = @(
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\performance_smoke.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\render_compose_parity_smoke.ps1 -ContractOnly"
    )
    non_goals = @(
        "Do not enable runtime compose-run merging before zero-diff parity artifacts exist.",
        "Do not move RRKAL discovery/download/import/cache governance into displaytools.",
        "Do not change the Qt-primary UI boundary or introduce Tk as primary UI."
    )
    runtime_optimization_applied = $renderPlan.runtime_optimization_applied
    compose_queue_field = $renderPlan.compiled_plan_compose_queue_field
    compose_runs_field = $renderPlan.compiled_plan_compose_runs_field
    parity_contract_field = $renderPlan.compiled_plan_compose_run_parity_contract_field
    ready_for_07_gate_review = $boundaryInspection.ready_for_07_gate_review
    boundary = "Work order is read-only extraction guidance; code movement starts only after the 2026-05-31T07:00:00+08:00 gate and clean pre-decoupling smoke."
    portable = $true
} | ConvertTo-Json -Depth 12
