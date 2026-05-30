param(
    [string]$Template = "fast_synthetic",
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$scriptName = "scripts/inspect_layer_render_plan_performance.ps1"

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.layer_render_plan_performance_inspector.v1"
        source = $scriptName
        status = "contract_only_no_launch_side_effect"
        launch_packet_fields = @(
            "layer_render_plan_performance",
            "layer_capability_matrix",
            "module_boundary_registry"
        )
        launch_packet_script = "scripts/export_launch_packet.py"
        required_contracts = @(
            "rrkal_displaytools.layer_render_plan_performance.v1",
            "rrkal_displaytools.compiled_layer_render_plan.v1",
            "rrkal_displaytools.layer_render_plan_compose_pass_budget.v1",
            "rrkal_displaytools.compose_run_merge_preflight.v1",
            "rrkal_displaytools.compose_run_parity_artifact_workflow.v1",
            "rrkal_displaytools.module_boundary_registry.v1"
        )
        default_template = $Template
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_layer_render_plan_performance.ps1"
        boundary = "Inspector reads launch-packet render-plan performance contracts only; it does not launch Qt, Taichi, provider IO, dataset discovery, import or cache governance."
        portable = $true
    } | ConvertTo-Json -Depth 8
    exit 0
}

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$venvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$useLocalVenv = Test-Path -LiteralPath $venvPython
$pythonCommand = if ($useLocalVenv) { $venvPython } else { "py" }

if ($useLocalVenv) {
    $launchPacketText = & $pythonCommand "scripts\export_launch_packet.py" "--template" $Template
} else {
    $launchPacketText = & $pythonCommand "-3" "scripts\export_launch_packet.py" "--template" $Template
}
if ($LASTEXITCODE -ne 0) {
    throw "Launch packet export failed while inspecting layer render-plan performance"
}

$launchPacket = ($launchPacketText -join "`n") | ConvertFrom-Json
if (-not $launchPacket.layer_render_plan_performance) {
    throw "Launch packet layer_render_plan_performance field is missing"
}
if (-not $launchPacket.module_boundary_registry) {
    throw "Launch packet module_boundary_registry field is missing"
}

$perf = $launchPacket.layer_render_plan_performance
$moduleBoundary = $launchPacket.module_boundary_registry
$budget = $perf.compose_pass_budget
$preflight = $perf.compose_run_merge_preflight
$parityWorkflow = $perf.compose_run_parity_artifact_workflow

[ordered]@{
    schema = "rrkal_displaytools.layer_render_plan_performance_inspection.v1"
    source = $scriptName
    template = $Template
    performance_schema = $perf.schema
    status = $perf.status
    post_decoupling_priority = $perf.post_decoupling_priority
    optimization_target = $perf.optimization_target
    performance_strategy = $perf.performance_strategy
    runtime_optimization_applied = $perf.runtime_optimization_applied
    current_runtime_claim = $perf.current_runtime_claim
    deferred_until = $perf.deferred_until
    compiled_plan_schema = $perf.compiled_plan_schema
    compiled_plan_helper = $perf.compiled_plan_helper
    stage_order = @($perf.stage_order)
    dirty_flags = @($perf.dirty_flags)
    batching_targets = @($perf.batching_targets)
    compose_pass_budget_schema = $perf.compose_pass_budget_schema
    compose_pass_budget_status = $budget.status
    current_pass_model = $budget.current_pass_model
    target_pass_model = $budget.target_pass_model
    first_safe_optimization = $budget.first_safe_optimization
    compose_required_evidence = @($budget.required_evidence)
    compose_runtime_merge_enabled = $budget.runtime_merge_enabled
    merge_preflight_schema = $perf.compose_run_merge_preflight_schema
    merge_preflight_status = $preflight.status
    merge_preflight_runtime_merge_enabled = $preflight.runtime_merge_enabled
    merge_preflight_required_evidence = @($preflight.required_evidence)
    merge_preflight_failure_policy = $preflight.failure_policy
    parity_workflow_schema = $perf.compose_run_parity_artifact_workflow_schema
    parity_workflow_status = $parityWorkflow.status
    parity_precommit_command = $parityWorkflow.precommit_command
    parity_manual_diff_command = $parityWorkflow.manual_diff_command
    parity_runner_command = $parityWorkflow.runner_command
    module_boundary_schema = $moduleBoundary.schema
    module_boundary_qt_first = $moduleBoundary.qt_first
    module_boundary_tk_primary_ui_allowed = $moduleBoundary.tk_primary_ui_allowed
    ready_for_clone_review = $true
    boundary = "Layer render-plan performance inspection is displaytools contract review only; runtime compose merging remains disabled until zero-diff parity artifacts exist."
    portable = $true
} | ConvertTo-Json -Depth 12
