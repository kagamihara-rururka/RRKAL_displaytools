param(
    [string]$Template = "fast_synthetic",
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$scriptName = "scripts/inspect_timeline_uiux.ps1"

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.timeline_uiux_inspector.v1"
        source = $scriptName
        status = "contract_only_no_launch_side_effect"
        launch_packet_fields = @(
            "timeline_state",
            "timeline_playback_readiness",
            "timeline_runtime_state",
            "timeline_animation_export",
            "timeline_layer_opacity_interpolation",
            "timeline_layer_discrete_hold"
        )
        launch_packet_script = "scripts/export_launch_packet.py"
        required_contracts = @(
            "rrkal_displaytools.timeline_state.v1",
            "rrkal_displaytools.timeline_playback_readiness.v1",
            "rrkal_displaytools.timeline_runtime_state.v1",
            "rrkal_displaytools.timeline_animation_export.v1",
            "rrkal_displaytools.timeline_layer_opacity_interpolation.v1",
            "rrkal_displaytools.timeline_layer_discrete_hold.v1"
        )
        default_template = $Template
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_timeline_uiux.ps1"
        boundary = "Inspector reads launch-packet timeline UIUX contracts only; it does not launch Qt, Taichi, provider IO, dataset discovery, import or cache governance."
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
    throw "Launch packet export failed while inspecting timeline UIUX"
}

$launchPacket = ($launchPacketText -join "`n") | ConvertFrom-Json
$requiredFields = @(
    "timeline_state",
    "timeline_playback_readiness",
    "timeline_runtime_state",
    "timeline_animation_export",
    "timeline_layer_opacity_interpolation",
    "timeline_layer_discrete_hold"
)
foreach ($field in $requiredFields) {
    if (-not $launchPacket.$field) {
        throw "Launch packet $field field is missing"
    }
}

$state = $launchPacket.timeline_state
$readiness = $launchPacket.timeline_playback_readiness
$runtime = $launchPacket.timeline_runtime_state
$animation = $launchPacket.timeline_animation_export
$opacity = $launchPacket.timeline_layer_opacity_interpolation
$discreteHold = $launchPacket.timeline_layer_discrete_hold

[ordered]@{
    schema = "rrkal_displaytools.timeline_uiux_inspection.v1"
    source = $scriptName
    template = $Template
    timeline_state_schema = $state.schema
    timeline_status = $state.status
    keyframe_count = $state.keyframe_count
    implemented = @($state.implemented)
    pending = @($state.pending)
    playback_readiness_schema = $readiness.schema
    ui_preview_playback_available = $readiness.ui_preview_playback_available
    renderer_ack_available = $readiness.renderer_ack_available
    renderer_timeline_playback = $readiness.renderer_timeline_playback
    renderer_playback_mode = $readiness.renderer_playback_mode
    ocean_material_interpolation = $readiness.ocean_material_interpolation
    camera_keyframes = $readiness.camera_keyframes
    camera_keyframe_interpolation = $readiness.camera_keyframe_interpolation
    layer_opacity_interpolation = $readiness.layer_opacity_interpolation
    layer_discrete_hold = $readiness.layer_discrete_hold
    animation_export = $readiness.animation_export
    animation_export_mode = $readiness.animation_export_mode
    readiness_pending = @($readiness.pending)
    runtime_state_schema = $runtime.schema
    runtime_target_file = $runtime.target_file
    runtime_timeline_keyframe_count = @($runtime.timeline_keyframes).Count
    animation_export_schema = $animation.schema
    animation_supported = $animation.supported
    animation_executed = $animation.executed
    animation_applies = @($animation.applies)
    layer_opacity_schema = $opacity.schema
    layer_opacity_supported = $opacity.supported
    layer_opacity_active = $opacity.active
    layer_discrete_hold_schema = $discreteHold.schema
    layer_discrete_hold_supported = $discreteHold.supported
    layer_discrete_hold_active_index = $discreteHold.active_index
    construction_status = "timeline_contract_ready_with_visible_pending_items"
    ready_for_clone_review = $true
    boundary = "Timeline UIUX inspection is displaytools contract review only; pending interpolation items stay visible and are not reported as complete."
    portable = $true
} | ConvertTo-Json -Depth 12
