param(
    [string]$Template = "fast_synthetic",
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$scriptName = "scripts/inspect_layer_operator_shortcuts.ps1"

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.layer_operator_shortcuts_inspector.v1"
        source = $scriptName
        status = "contract_only_no_launch_side_effect"
        launch_packet_fields = @(
            "layer_operator_shortcuts",
            "layer_operator_groups",
            "layer_selection_affordance",
            "layer_operation_feedback"
        )
        launch_packet_script = "scripts/export_launch_packet.py"
        required_contracts = @(
            "rrkal_displaytools.layer_operator_shortcuts.v1",
            "rrkal_displaytools.layer_operator_groups.v1",
            "rrkal_displaytools.layer_selection_affordance.v1",
            "rrkal_displaytools.layer_operation_feedback.v1"
        )
        default_template = $Template
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_layer_operator_shortcuts.ps1"
        boundary = "Inspector reads launch-packet layer operator shortcut contracts only; it does not launch Qt, Taichi, provider IO, dataset discovery, import or cache governance."
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
    throw "Launch packet export failed while inspecting layer operator shortcuts"
}

$launchPacket = ($launchPacketText -join "`n") | ConvertFrom-Json
$requiredFields = @(
    "layer_operator_shortcuts",
    "layer_operator_groups",
    "layer_selection_affordance",
    "layer_operation_feedback"
)
foreach ($field in $requiredFields) {
    if (-not $launchPacket.$field) {
        throw "Launch packet $field field is missing"
    }
}

$shortcuts = $launchPacket.layer_operator_shortcuts
$groups = $launchPacket.layer_operator_groups
$affordance = $launchPacket.layer_selection_affordance
$feedback = $launchPacket.layer_operation_feedback

[ordered]@{
    schema = "rrkal_displaytools.layer_operator_shortcuts_inspection.v1"
    source = $scriptName
    template = $Template
    shortcuts_schema = $shortcuts.schema
    ui_direction = $shortcuts.ui_direction
    action_count = $shortcuts.action_count
    implemented_action_ids = @($shortcuts.implemented_action_ids)
    keyboard_shortcut_count = $shortcuts.keyboard_shortcut_count
    installed_shortcut_ids = @($shortcuts.installed_shortcut_ids)
    keyboard_shortcuts = $shortcuts.keyboard_shortcuts
    group_schema = $groups.schema
    group_count = $groups.group_count
    complete_group_count = $groups.complete_group_count
    workflow_order = @($groups.workflow_order)
    selection_affordance_schema = $affordance.schema
    active_quick_actions = @($affordance.active_quick_actions)
    focus_aids = @($affordance.focus_aids)
    operation_feedback_schema = $feedback.schema
    operator_group_summary = $feedback.operator_group_summary
    undo_depth = $feedback.undo_depth
    copyable_provenance = $shortcuts.copyable_provenance
    ready_for_clone_review = $true
    boundary = "Layer operator shortcut inspection is displaytools UI/contract review only; shortcuts mutate Qt layer UI state, not RRKAL data governance."
    portable = $true
} | ConvertTo-Json -Depth 12
