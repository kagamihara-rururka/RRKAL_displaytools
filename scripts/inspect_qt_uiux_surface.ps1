param(
    [string]$Template = "fast_synthetic",
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$scriptName = "scripts/inspect_qt_uiux_surface.ps1"

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.qt_uiux_surface_inspector.v1"
        source = $scriptName
        status = "contract_only_no_launch_side_effect"
        launch_packet_fields = @(
            "profile",
            "profile_launch_readiness_ui",
            "profile_ui_state_replay",
            "layer_operator_groups",
            "layer_operator_shortcuts",
            "cross_machine_clone_readiness"
        )
        launch_packet_script = "scripts/export_launch_packet.py"
        required_contracts = @(
            "rrkal_displaytools.qt_panel_profile.v1",
            "rrkal_displaytools.profile_launch_readiness_ui.v1",
            "rrkal_displaytools.profile_ui_state_replay.v1",
            "rrkal_displaytools.layer_operator_groups.v1",
            "rrkal_displaytools.layer_operator_shortcuts.v1",
            "rrkal_displaytools.cross_machine_clone_readiness.v1"
        )
        default_template = $Template
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_qt_uiux_surface.ps1"
        boundary = "Inspector reads launch-packet Qt UIUX contracts only; it does not launch Qt, Taichi, provider IO, dataset discovery, import or cache governance."
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
    throw "Launch packet export failed while inspecting Qt UIUX surface"
}

$launchPacket = ($launchPacketText -join "`n") | ConvertFrom-Json
$requiredFields = @(
    "profile",
    "profile_launch_readiness_ui",
    "profile_ui_state_replay",
    "layer_operator_groups",
    "layer_operator_shortcuts",
    "cross_machine_clone_readiness"
)
foreach ($field in $requiredFields) {
    if (-not $launchPacket.$field) {
        throw "Launch packet $field field is missing"
    }
}

$profile = $launchPacket.profile
$readinessUi = $launchPacket.profile_launch_readiness_ui
$replay = $launchPacket.profile_ui_state_replay
$operatorGroups = $launchPacket.layer_operator_groups
$shortcuts = $launchPacket.layer_operator_shortcuts
$clone = $launchPacket.cross_machine_clone_readiness

$groups = @($replay.qt_inspector_action_groups)
$replayGroup = @($groups | Where-Object { $_.id -eq "replay_contracts" } | Select-Object -First 1)[0]
$rendererPortsGroup = @($groups | Where-Object { $_.id -eq "renderer_ports" } | Select-Object -First 1)[0]
$researchGroup = @($groups | Where-Object { $_.id -eq "research_interaction" } | Select-Object -First 1)[0]
$visualReviewGroup = @($groups | Where-Object { $_.id -eq "visual_review" } | Select-Object -First 1)[0]

if (-not $researchGroup) {
    throw "Research interaction Qt inspector group is missing"
}
if (-not $rendererPortsGroup) {
    throw "Renderer ports Qt inspector group is missing"
}

[ordered]@{
    schema = "rrkal_displaytools.qt_uiux_surface_inspection.v1"
    source = $scriptName
    template = $Template
    profile_schema = $profile.schema
    profile_name = $profile.name
    readiness_ui_schema = $readinessUi.schema
    readiness_ui_surface = $readinessUi.qt_surface
    readiness = $readinessUi.readiness
    profile_ui_state_replay_schema = $replay.schema
    qt_surface = $replay.qt_surface
    qt_inspector_group_count = $replay.qt_inspector_group_count
    qt_inspector_action_count = $replay.qt_inspector_action_count
    replay_action_ids = @($replayGroup.action_ids)
    renderer_port_action_ids = @($rendererPortsGroup.action_ids)
    research_interaction_action_ids = @($researchGroup.action_ids)
    visual_review_action_ids = @($visualReviewGroup.action_ids)
    layer_operator_groups_schema = $operatorGroups.schema
    layer_operator_workflow_order = @($operatorGroups.workflow_order)
    layer_operator_group_count = $operatorGroups.group_count
    layer_operator_complete_group_count = $operatorGroups.complete_group_count
    layer_operator_shortcuts_schema = $shortcuts.schema
    layer_keyboard_shortcut_count = $shortcuts.keyboard_shortcut_count
    layer_ui_direction = $shortcuts.ui_direction
    cross_machine_clone_schema = $clone.schema
    cross_machine_status = $clone.status
    qt_first = $clone.qt_first
    tk_primary_ui_allowed = $clone.tk_primary_ui_allowed
    repo_visibility = $clone.repo_visibility
    first_run_order = @($clone.first_run_order)
    photoshop_like_surface_summary = "Layers dock, Properties, Replay/contracts, Renderer ports, Research interaction and Visual review surfaces are represented through launch-packet contracts."
    ready_for_clone_review = $true
    boundary = "Qt UIUX surface inspection is displaytools UI/contract review only; RRKAL owns data/cache governance and authoritative dataset identity."
    portable = $true
} | ConvertTo-Json -Depth 12
