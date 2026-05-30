param(
    [string]$Template = "fast_synthetic",
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$scriptName = "scripts/inspect_layer_workflow.ps1"

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.layer_workflow_inspector.v1"
        source = $scriptName
        status = "contract_only_no_launch_side_effect"
        launch_packet_fields = @(
            "layer_research_workflow",
            "layer_selection_tool",
            "layer_operator_groups"
        )
        launch_packet_script = "scripts/export_launch_packet.py"
        required_contracts = @(
            "rrkal_displaytools.layer_research_workflow.v1",
            "rrkal_displaytools.layer_navigation_hint.v1",
            "rrkal_displaytools.layer_navigation_summary_contract.v1",
            "rrkal_displaytools.layer_selection_tool.v1",
            "rrkal_displaytools.layer_operator_groups.v1"
        )
        default_template = $Template
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_layer_workflow.ps1"
        boundary = "Inspector reads launch-packet layer workflow contracts only; it does not launch Qt, Taichi, provider IO, dataset discovery, import or cache governance."
        portable = $true
    } | ConvertTo-Json -Depth 8
    exit 0
}

$venvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$useLocalVenv = Test-Path -LiteralPath $venvPython
$pythonCommand = if ($useLocalVenv) { $venvPython } else { "py" }

if ($useLocalVenv) {
    $launchPacketText = & $pythonCommand "scripts\export_launch_packet.py" "--template" $Template
} else {
    $launchPacketText = & $pythonCommand "-3" "scripts\export_launch_packet.py" "--template" $Template
}
if ($LASTEXITCODE -ne 0) {
    throw "Launch packet export failed while inspecting layer workflow"
}

$launchPacket = ($launchPacketText -join "`n") | ConvertFrom-Json
if (-not $launchPacket.layer_research_workflow) {
    throw "Launch packet layer_research_workflow field is missing"
}
if (-not $launchPacket.layer_selection_tool) {
    throw "Launch packet layer_selection_tool field is missing"
}
if (-not $launchPacket.layer_operator_groups) {
    throw "Launch packet layer_operator_groups field is missing"
}

$workflow = $launchPacket.layer_research_workflow
$navigation = $workflow.navigation_hint
$selection = $launchPacket.layer_selection_tool
$operatorGroups = $launchPacket.layer_operator_groups

[ordered]@{
    schema = "rrkal_displaytools.layer_workflow_inspection.v1"
    source = $scriptName
    layer_research_workflow = $workflow
    layer_selection_tool = $selection
    layer_operator_groups = $operatorGroups
    workflow_schema = $workflow.schema
    workflow_status = $workflow.status
    navigation_hint_schema = $navigation.schema
    navigation_summary_contract_schema = $navigation.navigation_summary_contract.schema
    navigation_copy_action = $navigation.navigation_summary_contract.qt_copy_action
    selected_layer = $workflow.selected_layer
    navigation_state = $navigation.state
    next_action = $navigation.next_action
    first_matched_layer = $navigation.first_matched_layer
    visible_row_count = $navigation.visible_row_count
    qt_label_object = $navigation.qt_label_object
    operator_group_count = $operatorGroups.complete_group_count
    selection_summary_contract_schema = $selection.selection_summary_contract.schema
    boundary = "Layer workflow inspection is displaytools UI/contract review only; RRKAL owns data/cache governance."
    portable = $true
} | ConvertTo-Json -Depth 12
