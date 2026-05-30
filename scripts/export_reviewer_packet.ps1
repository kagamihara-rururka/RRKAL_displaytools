param(
    [string]$Output = "state/showcase/reviewer_packet.json",
    [string]$LaunchPacketOut = "",
    [string]$Profile = "",
    [string]$Template = "",
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

function Resolve-ExporterPath {
    param([string]$PathValue)
    if ([System.IO.Path]::IsPathRooted($PathValue)) {
        return $PathValue
    }
    return Join-Path $RepoRoot $PathValue
}

$defaultOutput = "state/showcase/reviewer_packet.json"
$noGuiCommand = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\export_reviewer_packet.ps1"

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.no_gui_reviewer_packet_export.v1"
        source = "scripts/export_reviewer_packet.ps1"
        status = "contract_only_no_launch_side_effect"
        reviewer_packet_schema = "rrkal_displaytools.reviewer_packet.v1"
        default_output = $defaultOutput
        no_gui_command = $noGuiCommand
        writes_output = $false
        compose_performance_summary_field = "compose_performance_summary"
        decoupling_readiness_field = "decoupling_readiness"
        controlled_interception_policy_field = "controlled_interception_policy"
        renderer_config_gateway_field = "renderer_config_gateway"
        boundary = "Contract-only mode is for smoke checks; normal mode writes a local reviewer packet under state/."
    } | ConvertTo-Json -Depth 8
    exit 0
}

$venvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$useLocalVenv = Test-Path -LiteralPath $venvPython
$pythonCommand = if ($useLocalVenv) { $venvPython } else { "py" }
$pythonArgs = if ($useLocalVenv) { @() } else { @("-3") }

$launchPacketPath = if ($LaunchPacketOut) {
    Resolve-ExporterPath $LaunchPacketOut
} else {
    Join-Path ([System.IO.Path]::GetTempPath()) ("rrkal_displaytools_launch_packet_{0}.json" -f $PID)
}

$launchArgs = $pythonArgs + @("scripts\export_launch_packet.py", "--output", $launchPacketPath)
if ($Profile) {
    $launchArgs += @("--profile", $Profile)
}
if ($Template) {
    $launchArgs += @("--template", $Template)
}

& $pythonCommand $launchArgs
if ($LASTEXITCODE -ne 0) {
    throw "No-GUI launch packet export failed with exit code $LASTEXITCODE"
}

$launchPacket = Get-Content -LiteralPath $launchPacketPath -Raw -Encoding UTF8 | ConvertFrom-Json
$performance = $launchPacket.layer_render_plan_performance
$budget = $performance.compose_pass_budget
$workflow = $performance.compose_run_parity_artifact_workflow
$adviceRules = $budget.bottleneck_advice_rules
$composeAdvice = if ($adviceRules.unknown) { $adviceRules.unknown } else { "await_runtime_metadata" }

$composePerformanceSummary = "Compose budget: status={0}; runs=-; merge=-; compose_ms=-; slowest=-; advice={1}; target={2}; runtime_merge=false | Compose parity runner: ready=True; script={3}; manifest={4}; runtime_merge=false" -f @(
    $budget.status,
    $composeAdvice,
    $budget.target_pass_model,
    $performance.compose_run_parity_artifact_runner_script,
    $workflow.runner_manifest
)
$decouplingFirst = @($launchPacket.decoupling_readiness.first_extraction_order | Select-Object -First 1)[0]
$decouplingReadinessSummary = "Decoupling readiness: phase=$($launchPacket.decoupling_readiness.phase); first=$($decouplingFirst.id); extractions=$(@($launchPacket.decoupling_readiness.first_extraction_order).Count); boundary=$($launchPacket.decoupling_readiness.rrkal_boundary.rule)"
$controlledInterceptionSummary = "Controlled interception: allowed=$(@($launchPacket.controlled_interception_policy.allowed_patterns).Count); blocked=$(@($launchPacket.controlled_interception_policy.blocked_patterns).Count); first_use=$($launchPacket.controlled_interception_policy.first_decoupling_use.target); rule=scoped_visible_removable"
$rendererConfigChanged = @($launchPacket.renderer_config_gateway.changed_defaults) -join ","
if (-not $rendererConfigChanged) { $rendererConfigChanged = "none" }
$rendererConfigGatewaySummary = "Renderer config gateway: schema=$($launchPacket.renderer_config_gateway.schema); style=$($launchPacket.renderer_config_gateway.config.style_profile); size=$($launchPacket.renderer_config_gateway.config.width)x$($launchPacket.renderer_config_gateway.config.height); topo_step=$($launchPacket.renderer_config_gateway.config.topo_step); changed=$rendererConfigChanged; boundary=config_only_no_qt_taichi_data_governance"

$reviewerPacket = [ordered]@{
    schema = "rrkal_displaytools.reviewer_packet.v1"
    created_at_utc = [DateTimeOffset]::UtcNow.ToString("o")
    source = "scripts/export_reviewer_packet.ps1"
    reviewer_packet_export = $launchPacket.reviewer_packet_export
    clone_reviewer_summary = "Clone reviewer: status=$($launchPacket.cross_machine_clone_readiness.status); repo=$($launchPacket.cross_machine_clone_readiness.repo_url); smoke_required=$($launchPacket.cross_machine_clone_readiness.smoke_required_before_push)"
    launch_reviewer_summary = "Launch reviewer: readiness=$($launchPacket.profile_launch_readiness.readiness); portable=$($launchPacket.portable_command_line)"
    research_interaction_summary = "Research interaction: no_gui_packet=available; open Qt for live canvas and layer-pick runtime state"
    visual_review_summary = "Visual review: readiness=$($launchPacket.visual_review_readiness.status); renderer_thumbnail=$($launchPacket.visual_review_readiness.renderer_thumbnail_status); live_preview=$($launchPacket.visual_review_readiness.live_preview_status)"
    hydrology_lod_summary = "Hydrology/LOD: readiness=$($launchPacket.hydrology_lod_readiness.readiness); lod=$($launchPacket.hydrology_lod_readiness.lod_hook_status)"
    ocean_material_summary = "Ocean material: status=$($launchPacket.ocean_material_control_port.status); control_panel=$($launchPacket.ocean_material_control_port.taichi_ocean_3d_control_panel_schema)"
    style_routes_summary = "Style routes: selected=$($launchPacket.style_profile_renderer_routes.selected_style); profiles=$($launchPacket.style_profile_renderer_routes.route_count)"
    module_boundary_summary = "Module seams: modules=$($launchPacket.module_boundary_registry.module_count); boundary=RRKAL-owned data/cache"
    decoupling_readiness_summary = $decouplingReadinessSummary
    controlled_interception_summary = $controlledInterceptionSummary
    renderer_config_gateway_summary = $rendererConfigGatewaySummary
    compose_performance_summary = $composePerformanceSummary
    cross_machine_clone_readiness = $launchPacket.cross_machine_clone_readiness
    profile_launch_readiness = $launchPacket.profile_launch_readiness
    profile_ui_state_replay = $launchPacket.profile_ui_state_replay
    hydrology_lod_readiness = $launchPacket.hydrology_lod_readiness
    hydrology_lod_runtime_evidence = $launchPacket.hydrology_lod_runtime_evidence
    ocean_material_control_port = $launchPacket.ocean_material_control_port
    style_profile_renderer_routes = $launchPacket.style_profile_renderer_routes
    module_boundary_registry = $launchPacket.module_boundary_registry
    decoupling_readiness = $launchPacket.decoupling_readiness
    controlled_interception_policy = $launchPacket.controlled_interception_policy
    renderer_config_gateway = $launchPacket.renderer_config_gateway
    visual_feature_closure_matrix = $launchPacket.visual_feature_closure_matrix
    renderer_output_artifact_contract = $launchPacket.renderer_output_artifact_contract
    layer_render_plan_performance = $performance
    launch_packet_snapshot = $launchPacket
    python_command = $pythonCommand
    python_uses_local_venv = [bool]$useLocalVenv
    launch_packet_path = $launchPacketPath
    boundary = "No-GUI reviewer packet uses launch-packet contract evidence; live Qt-only interaction state still requires opening Qt."
}

$json = $reviewerPacket | ConvertTo-Json -Depth 12
$outputPath = Resolve-ExporterPath $Output
$outputDir = Split-Path -Parent $outputPath
if ($outputDir) {
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
}
[System.IO.File]::WriteAllText($outputPath, $json, [System.Text.UTF8Encoding]::new($false))
$json
