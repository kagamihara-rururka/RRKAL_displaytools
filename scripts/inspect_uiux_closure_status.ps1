param(
    [string]$Template = "fast_synthetic",
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$scriptName = "scripts/inspect_uiux_closure_status.ps1"

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.uiux_closure_status_inspector.v1"
        source = $scriptName
        status = "contract_only_no_launch_side_effect"
        launch_packet_fields = @(
            "visual_feature_closure_matrix",
            "goal_closure_scorecard",
            "closed_loop_status",
            "visual_review_readiness"
        )
        launch_packet_script = "scripts/export_launch_packet.py"
        required_contracts = @(
            "rrkal_displaytools.visual_feature_closure_matrix.v1",
            "rrkal_displaytools.goal_closure_scorecard.v1",
            "rrkal_displaytools.closed_loop_status.v1",
            "rrkal_displaytools.visual_review_readiness.v1"
        )
        default_template = $Template
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_uiux_closure_status.ps1"
        boundary = "Inspector reads launch-packet UIUX closure contracts only; it does not launch Qt, Taichi, provider IO, dataset discovery, import or cache governance."
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
    throw "Launch packet export failed while inspecting UIUX closure status"
}

$launchPacket = ($launchPacketText -join "`n") | ConvertFrom-Json
$requiredFields = @(
    "visual_feature_closure_matrix",
    "goal_closure_scorecard",
    "closed_loop_status",
    "visual_review_readiness"
)
foreach ($field in $requiredFields) {
    if (-not $launchPacket.$field) {
        throw "Launch packet $field field is missing"
    }
}

$matrix = $launchPacket.visual_feature_closure_matrix
$scorecard = $launchPacket.goal_closure_scorecard
$closedLoop = $launchPacket.closed_loop_status
$visualReview = $launchPacket.visual_review_readiness

[ordered]@{
    schema = "rrkal_displaytools.uiux_closure_status_inspection.v1"
    source = $scriptName
    template = $Template
    visual_feature_closure_schema = $matrix.schema
    visual_feature_status = $matrix.status
    feature_count = $matrix.feature_count
    ready_feature_count = $matrix.ready_feature_count
    required_feature_ids = @($matrix.required_feature_ids)
    goal_scorecard_schema = $scorecard.schema
    goal_scorecard_status = $scorecard.status
    goal_ready_category_count = $scorecard.ready_category_count
    goal_queued_category_count = $scorecard.queued_category_count
    objective_scope = @($scorecard.objective_scope)
    closed_loop_schema = $closedLoop.schema
    closed_loop_closed_count = @($closedLoop.closed).Count
    closed_loop_partial_count = @($closedLoop.partial).Count
    closed_loop_pending = @($closedLoop.pending)
    external_dependencies = @($closedLoop.external_dependencies)
    visual_review_schema = $visualReview.schema
    visual_review_status = $visualReview.status
    visual_review_actions = @($visualReview.visual_review_actions)
    renderer_thumbnail_ready = $visualReview.renderer_thumbnail_ready
    live_preview_ready = $visualReview.live_preview_ready
    excluded_tools = @("brush_tools", "mask_painting_tools")
    construction_status = "queued_items_visible_not_claimed_done"
    construction_items = @($closedLoop.pending)
    performance_followup_status = "queued_until_render_plan_decoupling_and_parity"
    ready_for_clone_review = $true
    boundary = "UIUX closure status is displaytools contract review only; queued items stay visible and are not reported as complete."
    portable = $true
} | ConvertTo-Json -Depth 12
