param(
    [string]$Template = "fast_synthetic",
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$scriptName = "scripts/inspect_research_interaction.ps1"

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.research_interaction_inspector.v1"
        source = $scriptName
        status = "contract_only_no_launch_side_effect"
        launch_packet_fields = @(
            "layer_research_workflow",
            "layer_selection_tool",
            "cursor_geodesy_readout",
            "pin_overlay",
            "boundary_highlight",
            "boundary_emphasis_control",
            "profile_ui_state_replay"
        )
        launch_packet_script = "scripts/export_launch_packet.py"
        required_contracts = @(
            "rrkal_displaytools.layer_research_workflow.v1",
            "rrkal_displaytools.layer_selection_tool.v1",
            "rrkal_displaytools.cursor_geodesy_readout.v1",
            "rrkal_displaytools.cursor_geodesy_summary_contract.v1",
            "rrkal_displaytools.pin_projection.v1",
            "rrkal_displaytools.pin_summary_contract.v1",
            "rrkal_displaytools.boundary_highlight_mask.v1",
            "rrkal_displaytools.boundary_emphasis_control.v1",
            "rrkal_displaytools.research_interaction_summary_contract.v1"
        )
        default_template = $Template
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_research_interaction.ps1"
        boundary = "Inspector reads launch-packet research interaction contracts only; it does not launch Qt, Taichi, provider IO, dataset discovery, import or cache governance."
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
    throw "Launch packet export failed while inspecting research interaction"
}

$launchPacket = ($launchPacketText -join "`n") | ConvertFrom-Json
$requiredFields = @(
    "layer_research_workflow",
    "layer_selection_tool",
    "cursor_geodesy_readout",
    "pin_overlay",
    "boundary_highlight",
    "boundary_emphasis_control",
    "profile_ui_state_replay"
)
foreach ($field in $requiredFields) {
    if (-not $launchPacket.$field) {
        throw "Launch packet $field field is missing"
    }
}

$workflow = $launchPacket.layer_research_workflow
$selection = $launchPacket.layer_selection_tool
$cursor = $launchPacket.cursor_geodesy_readout
$pin = $launchPacket.pin_overlay
$boundaryHighlight = $launchPacket.boundary_highlight
$boundaryEmphasis = $launchPacket.boundary_emphasis_control
$replay = $launchPacket.profile_ui_state_replay
$researchGroup = @($replay.qt_inspector_action_groups | Where-Object { $_.id -eq "research_interaction" } | Select-Object -First 1)[0]

[ordered]@{
    schema = "rrkal_displaytools.research_interaction_inspection.v1"
    source = $scriptName
    template = $Template
    workflow_schema = $workflow.schema
    selection_tool_schema = $selection.schema
    cursor_geodesy_schema = $cursor.schema
    cursor_summary_contract_schema = $cursor.cursor_summary_contract_schema
    pin_overlay_schema = $pin.schema
    pin_summary_contract_schema = $pin.pin_summary_contract_schema
    boundary_highlight_schema = $boundaryHighlight.schema
    boundary_emphasis_control_schema = $boundaryEmphasis.schema
    research_summary_contract_schema = $workflow.research_summary_contract_schema
    selected_layer = $workflow.selected_layer
    cursor_runtime_bridge_status = $cursor.runtime_bridge_status
    cursor_state_file = $cursor.renderer_raycast_state_file
    cursor_ack_file = $cursor.renderer_raycast_ack_file
    pin_occlusion_status = $pin.occlusion_status
    pin_cursor_fill_priority = $pin.cursor_fill_priority
    boundary_trigger = $boundaryHighlight.trigger
    boundary_target_mode = $boundaryEmphasis.target_mode
    qt_inspector_action_ids = @($replay.qt_inspector_action_ids)
    research_interaction_action_ids = @($researchGroup.action_ids)
    ready_for_clone_review = $true
    boundary = "Research interaction inspection is displaytools UI/contract review only; RRKAL owns data/cache governance and authoritative geospatial identity."
    portable = $true
} | ConvertTo-Json -Depth 12
