param(
    [string]$Template = "fast_synthetic",
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$scriptName = "scripts/inspect_ocean_material.ps1"

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.ocean_material_inspector.v1"
        source = $scriptName
        status = "contract_only_no_launch_side_effect"
        launch_packet_field = "ocean_material_control_port"
        launch_packet_script = "scripts/export_launch_packet.py"
        required_contracts = @(
            "rrkal_displaytools.ocean_material_control_port.v1",
            "rrkal_displaytools.taichi_ocean_3d_control_panel.v1",
            "rrkal_displaytools.taichi_ocean_3d_control_board_audit.v1",
            "rrkal_displaytools.ocean_material_renderer_apply_contract.v1",
            "rrkal_displaytools.sea_state_scalar_sample.v1"
        )
        default_template = $Template
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_ocean_material.ps1"
        boundary = "Inspector reads launch-packet ocean material contracts only; it does not launch Qt, Taichi, provider IO, dataset discovery, import or cache governance."
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
    throw "Launch packet export failed while inspecting ocean material"
}

$launchPacket = ($launchPacketText -join "`n") | ConvertFrom-Json
if (-not $launchPacket.ocean_material_control_port) {
    throw "Launch packet ocean_material_control_port field is missing"
}

$port = $launchPacket.ocean_material_control_port
[ordered]@{
    schema = "rrkal_displaytools.ocean_material_inspection.v1"
    source = $scriptName
    ocean_material_control_port = $port
    control_port_schema = $port.schema
    qt_control_panel_schema = $port.qt_control_panel.schema
    control_board_audit_schema = $port.control_board_audit.schema
    renderer_apply_contract_schema = $port.renderer_apply_contract.schema
    sea_state_scalar_sample_schema = $port.sea_state_port.scalar_sample_contract.schema
    safe_preview_action = $port.qt_control_panel.performance_guard_action
    control_board_status = $port.qt_control_panel.control_board_status
    render_pipeline_followup = $port.qt_control_panel.render_pipeline_followup
    boundary = "Ocean material inspection is displaytools scalar/control review only; RRKAL/provider modules own data/cache governance."
    portable = $true
} | ConvertTo-Json -Depth 12
