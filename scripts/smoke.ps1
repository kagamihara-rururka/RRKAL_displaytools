$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

Write-Host "RRKAL_displaytools smoke"
Write-Host "Repo: $RepoRoot"

function Invoke-CheckedNative {
    param(
        [string]$FilePath,
        [string[]]$ArgumentList
    )

    & $FilePath @ArgumentList
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $FilePath $($ArgumentList -join ' ')"
    }
}

Invoke-CheckedNative py @("-3", "-m", "py_compile", "rrkal_displaytools_qt_panel.py", "taichi_global_bathymetry.py", "pin_projection.py", "closed_loop_status.py")
Invoke-CheckedNative py @("-3", "profile_schema.py") | Out-Null
Invoke-CheckedNative py @("-3", "scripts\validate_profiles.py")
$launchPacketText = & py -3 scripts\export_launch_packet.py --template fast_synthetic
if ($LASTEXITCODE -ne 0) {
    throw "Command failed: py -3 scripts\export_launch_packet.py --template fast_synthetic"
}
$launchPacket = $launchPacketText | ConvertFrom-Json
if ($launchPacket.canvas_preview.schema -ne "rrkal_displaytools.canvas_preview.v1") {
    throw "Launch packet canvas_preview schema missing or invalid"
}
if ($launchPacket.active_layer_diagnostics.schema -ne "rrkal_displaytools.active_layer_diagnostics.v1") {
    throw "Launch packet active_layer_diagnostics schema missing or invalid"
}
if ($launchPacket.layer_filter.schema -ne "rrkal_displaytools.layer_filter.v1") {
    throw "Launch packet layer_filter schema missing or invalid"
}
if ($launchPacket.layer_filter.available_presets -notcontains "hydrology") {
    throw "Launch packet layer_filter hydrology preset missing"
}
if ($launchPacket.layer_filter.available_presets -notcontains "visual_aids") {
    throw "Launch packet layer_filter visual_aids preset missing"
}
if ($null -eq $launchPacket.layer_filter.first_matched_layer) {
    throw "Launch packet layer_filter first_matched_layer missing"
}
if ($null -eq $launchPacket.layer_filter.selected_layer_reveal_available) {
    throw "Launch packet layer_filter reveal diagnostic missing"
}
if ($launchPacket.layer_group_view.schema -ne "rrkal_displaytools.layer_group_view.v1") {
    throw "Launch packet layer_group_view schema missing or invalid"
}
if ($null -eq $launchPacket.layer_group_view.available_groups.hydrology) {
    throw "Launch packet layer_group_view hydrology group missing"
}
if ($null -eq $launchPacket.layer_group_view.visible_counts_by_group.hydrology) {
    throw "Launch packet layer_group_view hydrology visible count missing"
}
if ($null -eq $launchPacket.layer_group_view.selected_layer_hidden_by_group) {
    throw "Launch packet layer_group_view selected-layer hidden diagnostic missing"
}
if ($launchPacket.layer_undo.schema -ne "rrkal_displaytools.layer_stack_undo.v1") {
    throw "Launch packet layer_undo schema missing or invalid"
}
if ($launchPacket.session_journal.schema -ne "rrkal_displaytools.session_journal.v1") {
    throw "Launch packet session_journal schema missing or invalid"
}
if ($launchPacket.document_undo.schema -ne "rrkal_displaytools.document_snapshot_undo.v1") {
    throw "Launch packet document_undo schema missing or invalid"
}
if ($launchPacket.document_undo.implemented -notcontains "limited_automatic_change_capture") {
    throw "Launch packet document_undo limited automatic capture missing"
}
if ($launchPacket.document_undo.auto_capture_points -notcontains "profile_apply") {
    throw "Launch packet document_undo auto_capture_points missing profile_apply"
}
if ($launchPacket.timeline_state.schema -ne "rrkal_displaytools.timeline_state.v1") {
    throw "Launch packet timeline_state schema missing or invalid"
}
if ($launchPacket.timeline_playback_readiness.schema -ne "rrkal_displaytools.timeline_playback_readiness.v1") {
    throw "Launch packet timeline playback readiness schema missing or invalid"
}
if ($launchPacket.timeline_playback_readiness.renderer_ack_available -ne $true) {
    throw "Launch packet timeline playback readiness renderer ack unavailable"
}
if ($launchPacket.timeline_playback_readiness.renderer_timeline_playback -ne $true) {
    throw "Launch packet timeline playback readiness must claim renderer discrete playback"
}
if ($launchPacket.timeline_playback_readiness.ocean_material_interpolation -ne $true) {
    throw "Launch packet timeline playback readiness must claim ocean material interpolation"
}
if ($launchPacket.timeline_playback_plan.schema -ne "rrkal_displaytools.timeline_playback_plan.v1") {
    throw "Launch packet timeline playback plan schema missing or invalid"
}
if ($launchPacket.timeline_segment_state.schema -ne "rrkal_displaytools.timeline_segment_state.v1") {
    throw "Launch packet timeline segment state schema missing or invalid"
}
if ($launchPacket.timeline_segment_state.mode -ne "active_segment_preview") {
    throw "Launch packet timeline segment state mode missing or invalid"
}
if ($launchPacket.timeline_active_step_state.schema -ne "rrkal_displaytools.timeline_active_step_state.v1") {
    throw "Launch packet timeline active step state schema missing or invalid"
}
if ($launchPacket.timeline_step_playback.schema -ne "rrkal_displaytools.timeline_step_playback.v1") {
    throw "Launch packet timeline step playback schema missing or invalid"
}
if ($launchPacket.timeline_ocean_material_interpolation.schema -ne "rrkal_displaytools.timeline_ocean_material_interpolation.v1") {
    throw "Launch packet timeline ocean material interpolation schema missing or invalid"
}
if ($launchPacket.timeline_state.implemented -notcontains "profile_timeline_keyframe_handoff") {
    throw "Launch packet timeline_state profile keyframe handoff missing"
}
if ($null -eq $launchPacket.timeline_state.keyframes) {
    throw "Launch packet timeline_state keyframes missing"
}
if ($launchPacket.timeline_runtime_state.schema -ne "rrkal_displaytools.timeline_runtime_state.v1") {
    throw "Launch packet timeline_runtime_state schema missing or invalid"
}
if ($launchPacket.timeline_runtime_state.timeline_state.schema -ne "rrkal_displaytools.timeline_state.v1") {
    throw "Launch packet timeline_runtime_state nested timeline_state schema missing or invalid"
}
if ($launchPacket.timeline_runtime_state.playback_readiness.schema -ne "rrkal_displaytools.timeline_playback_readiness.v1") {
    throw "Launch packet timeline_runtime_state playback readiness missing or invalid"
}
if ($launchPacket.timeline_runtime_state.playback_plan.schema -ne "rrkal_displaytools.timeline_playback_plan.v1") {
    throw "Launch packet timeline_runtime_state playback plan missing or invalid"
}
if ($launchPacket.timeline_runtime_state.segment_state.schema -ne "rrkal_displaytools.timeline_segment_state.v1") {
    throw "Launch packet timeline_runtime_state segment state missing or invalid"
}
if ($launchPacket.timeline_runtime_state.active_step_state.schema -ne "rrkal_displaytools.timeline_active_step_state.v1") {
    throw "Launch packet timeline_runtime_state active step state missing or invalid"
}
if ($launchPacket.timeline_runtime_state.step_playback.schema -ne "rrkal_displaytools.timeline_step_playback.v1") {
    throw "Launch packet timeline_runtime_state step playback missing or invalid"
}
if ($launchPacket.timeline_runtime_state.ocean_material_interpolation.schema -ne "rrkal_displaytools.timeline_ocean_material_interpolation.v1") {
    throw "Launch packet timeline_runtime_state ocean material interpolation missing or invalid"
}
if ($launchPacket.timeline_runtime_state_file -ne "state/renderer_timeline_state.json") {
    throw "Launch packet timeline runtime state file missing or invalid"
}
if ($launchPacket.timeline_ack_file -ne "state/renderer_timeline_ack.json") {
    throw "Launch packet timeline ack file missing or invalid"
}
if ($launchPacket.boundary_highlight.identity_status.schema -ne "rrkal_displaytools.boundary_identity_status.v1") {
    throw "Launch packet boundary_highlight identity_status schema missing or invalid"
}
if ($launchPacket.portable_command -notcontains "--preview-frame-file") {
    throw "Launch packet portable command is missing --preview-frame-file"
}
if ($launchPacket.portable_command -notcontains "--timeline-state-file") {
    throw "Launch packet portable command is missing --timeline-state-file"
}
if ($launchPacket.portable_command -notcontains "--timeline-ack-file") {
    throw "Launch packet portable command is missing --timeline-ack-file"
}
if ($launchPacket.canvas_preview.preview_frame_path -ne "state/renderer_preview_frame.png") {
    throw "Launch packet canvas_preview preview_frame_path missing or invalid"
}
if ([double]$launchPacket.canvas_preview.preview_frame_interval_s -le 0) {
    throw "Launch packet canvas_preview preview_frame_interval_s missing or invalid"
}
$timelineStateOut = Join-Path $env:TEMP "rrkal_displaytools_smoke_timeline_state.json"
if (Test-Path $timelineStateOut) {
    Remove-Item -LiteralPath $timelineStateOut -Force
}
$timelinePacketText = & py -3 scripts\export_launch_packet.py --template fast_synthetic --timeline-state-out $timelineStateOut
if ($LASTEXITCODE -ne 0) {
    throw "Command failed: py -3 scripts\export_launch_packet.py --template fast_synthetic --timeline-state-out"
}
if (!(Test-Path $timelineStateOut)) {
    throw "No-GUI timeline state output was not written"
}
$timelineRuntimeState = Get-Content -Raw -LiteralPath $timelineStateOut | ConvertFrom-Json
if ($timelineRuntimeState.schema -ne "rrkal_displaytools.timeline_runtime_state.v1") {
    throw "No-GUI timeline state output schema missing or invalid"
}
$timelinePacket = $timelinePacketText | ConvertFrom-Json
if ($timelinePacket.timeline_runtime_state_file -ne $timelineStateOut) {
    throw "No-GUI launch packet timeline runtime state file did not follow --timeline-state-out"
}
if ($timelinePacket.portable_command -notcontains $timelineStateOut) {
    throw "No-GUI launch packet portable command did not include --timeline-state-out path"
}
$timelineAckOut = Join-Path $env:TEMP "rrkal_displaytools_smoke_timeline_ack.json"
if (Test-Path $timelineAckOut) {
    Remove-Item -LiteralPath $timelineAckOut -Force
}
$timelineAckText = & py -3 taichi_global_bathymetry.py --ack-timeline-state-and-exit --timeline-state-file $timelineStateOut --timeline-ack-file $timelineAckOut
if ($LASTEXITCODE -ne 0) {
    throw "Command failed: py -3 taichi_global_bathymetry.py --ack-timeline-state-and-exit"
}
if (!(Test-Path $timelineAckOut)) {
    throw "Renderer timeline ack output was not written"
}
$timelineAckRaw = $timelineAckText -join "`n"
$timelineAckJsonStart = $timelineAckRaw.IndexOf("{")
if ($timelineAckJsonStart -lt 0) {
    throw "Renderer timeline ack JSON payload not found"
}
$timelineAck = $timelineAckRaw.Substring($timelineAckJsonStart) | ConvertFrom-Json
if ($timelineAck.schema -ne "rrkal_displaytools.renderer_timeline_ack.v1") {
    throw "Renderer timeline ack endpoint schema missing or invalid"
}
if ($timelineAck.received -ne $true) {
    throw "Renderer timeline ack endpoint did not receive the runtime state"
}
if ($timelineAck.timeline_runtime_state_schema -ne "rrkal_displaytools.timeline_runtime_state.v1") {
    throw "Renderer timeline ack endpoint runtime state schema missing or invalid"
}
if ($timelineAck.playback_readiness.schema -ne "rrkal_displaytools.timeline_playback_readiness.v1") {
    throw "Renderer timeline ack endpoint playback readiness missing or invalid"
}
if ($timelineAck.playback_plan.schema -ne "rrkal_displaytools.timeline_playback_plan.v1") {
    throw "Renderer timeline ack endpoint playback plan missing or invalid"
}
if ($timelineAck.segment_state.schema -ne "rrkal_displaytools.timeline_segment_state.v1") {
    throw "Renderer timeline ack endpoint segment state missing or invalid"
}
if ($timelineAck.segment_state.mode -ne "active_segment_preview") {
    throw "Renderer timeline ack endpoint segment state mode missing or invalid"
}
if ($timelineAck.active_step_state.schema -ne "rrkal_displaytools.timeline_active_step_state.v1") {
    throw "Renderer timeline ack endpoint active step state missing or invalid"
}
if ($timelineAck.step_playback.schema -ne "rrkal_displaytools.timeline_step_playback.v1") {
    throw "Renderer timeline ack endpoint step playback missing or invalid"
}
if ($timelineAck.ocean_material_interpolation.schema -ne "rrkal_displaytools.timeline_ocean_material_interpolation.v1") {
    throw "Renderer timeline ack endpoint ocean material interpolation missing or invalid"
}
if ($timelineAck.first_keyframe_apply.schema -ne "rrkal_displaytools.timeline_first_keyframe_apply.v1") {
    throw "Renderer timeline ack endpoint first keyframe apply packet missing or invalid"
}
if ($timelineAck.first_keyframe_apply.active_step_state.schema -ne "rrkal_displaytools.timeline_active_step_state.v1") {
    throw "Renderer timeline first keyframe apply active step state missing or invalid"
}
if ($null -eq $timelineAck.first_keyframe_apply.changed.pins) {
    throw "Renderer timeline first keyframe apply pins changed field missing"
}
if ($null -eq $timelineAck.first_keyframe_apply.changed.boundary_highlight) {
    throw "Renderer timeline first keyframe apply boundary changed field missing"
}
Remove-Item -LiteralPath $timelineAckOut -Force
Remove-Item -LiteralPath $timelineStateOut -Force
$capabilitiesText = & py -3 taichi_global_bathymetry.py --print-renderer-capabilities
if ($LASTEXITCODE -ne 0) {
    throw "Command failed: py -3 taichi_global_bathymetry.py --print-renderer-capabilities"
}
$capabilitiesRaw = $capabilitiesText -join "`n"
$capabilitiesJsonStart = $capabilitiesRaw.IndexOf("{")
if ($capabilitiesJsonStart -lt 0) {
    throw "Renderer capabilities JSON payload not found"
}
$capabilities = $capabilitiesRaw.Substring($capabilitiesJsonStart) | ConvertFrom-Json
if ($capabilities.preview_frame_stream.schema -ne "rrkal_displaytools.preview_frame_stream.v1") {
    throw "Renderer preview_frame_stream capability missing or invalid"
}
if ($capabilities.active_layer_diagnostics.schema -ne "rrkal_displaytools.active_layer_diagnostics.v1") {
    throw "Renderer active_layer_diagnostics capability missing or invalid"
}
if ($capabilities.ui_handoff_contracts.schema -ne "rrkal_displaytools.ui_handoff_contracts.v1") {
    throw "Renderer ui_handoff_contracts capability missing or invalid"
}
if ($capabilities.ui_handoff_contracts.contracts -notcontains "layer_filter") {
    throw "Renderer ui_handoff_contracts layer_filter contract missing"
}
if ($capabilities.ui_handoff_contracts.contracts -notcontains "layer_group_view") {
    throw "Renderer ui_handoff_contracts layer_group_view contract missing"
}
if ($capabilities.ui_handoff_contracts.contracts -notcontains "document_undo") {
    throw "Renderer ui_handoff_contracts document_undo contract missing"
}
if ($capabilities.timeline_handoff.schema -ne "rrkal_displaytools.timeline_handoff.v1") {
    throw "Renderer timeline_handoff capability missing or invalid"
}
if ($capabilities.timeline_handoff.ack_schema -ne "rrkal_displaytools.renderer_timeline_ack.v1") {
    throw "Renderer timeline_handoff ack schema missing or invalid"
}
if ($capabilities.timeline_handoff.playback_readiness.schema -ne "rrkal_displaytools.timeline_playback_readiness.v1") {
    throw "Renderer timeline_handoff playback readiness missing or invalid"
}
if ($capabilities.timeline_handoff.playback_plan_schema -ne "rrkal_displaytools.timeline_playback_plan.v1") {
    throw "Renderer timeline_handoff playback plan schema missing or invalid"
}
if ($capabilities.timeline_handoff.segment_state_schema -ne "rrkal_displaytools.timeline_segment_state.v1") {
    throw "Renderer timeline_handoff segment state schema missing or invalid"
}
if ($capabilities.timeline_handoff.active_step_state_schema -ne "rrkal_displaytools.timeline_active_step_state.v1") {
    throw "Renderer timeline_handoff active step state schema missing or invalid"
}
if ($capabilities.timeline_handoff.step_playback_schema -ne "rrkal_displaytools.timeline_step_playback.v1") {
    throw "Renderer timeline_handoff step playback schema missing or invalid"
}
if ($capabilities.timeline_handoff.ocean_material_interpolation_schema -ne "rrkal_displaytools.timeline_ocean_material_interpolation.v1") {
    throw "Renderer timeline_handoff ocean material interpolation schema missing or invalid"
}
if ($capabilities.timeline_handoff.first_keyframe_apply_schema -ne "rrkal_displaytools.timeline_first_keyframe_apply.v1") {
    throw "Renderer timeline_handoff first keyframe apply schema missing or invalid"
}
if ($capabilities.timeline_handoff.controls -notcontains "timeline-state-file") {
    throw "Renderer timeline_handoff timeline-state-file control missing"
}
if ($capabilities.timeline_handoff.controls -notcontains "ack-timeline-state-and-exit") {
    throw "Renderer timeline_handoff ack endpoint control missing"
}
if ($capabilities.boundary_highlight.identity_status_schema -ne "rrkal_displaytools.boundary_identity_status.v1") {
    throw "Renderer boundary_highlight identity_status capability missing or invalid"
}
$closedLoopText = & py -3 taichi_global_bathymetry.py --print-closed-loop-status
if ($LASTEXITCODE -ne 0) {
    throw "Command failed: py -3 taichi_global_bathymetry.py --print-closed-loop-status"
}
$closedLoopRaw = $closedLoopText -join "`n"
$closedLoopJsonStart = $closedLoopRaw.IndexOf("{")
if ($closedLoopJsonStart -lt 0) {
    throw "Closed-loop status JSON payload not found"
}
$closedLoop = $closedLoopRaw.Substring($closedLoopJsonStart) | ConvertFrom-Json
$closedLoopIds = @($closedLoop.closed | ForEach-Object { $_.id })
if ($closedLoopIds -notcontains "diagnostics_handoff_contracts") {
    throw "Closed-loop diagnostics_handoff_contracts missing"
}
if ($closedLoopIds -notcontains "layer_stack_undo_snapshots") {
    throw "Closed-loop layer_stack_undo_snapshots missing"
}
if ($closedLoopIds -notcontains "session_journal_handoff") {
    throw "Closed-loop session_journal_handoff missing"
}
$timelinePartial = @($closedLoop.partial | Where-Object { $_.id -eq "qt_timeline_panel" }) | Select-Object -First 1
if ($null -eq $timelinePartial) {
    throw "Closed-loop qt_timeline_panel partial status missing"
}
$timelineApplies = @($timelinePartial.applies)
if ($timelineApplies -notcontains "UI-only playback controls") {
    throw "Closed-loop qt_timeline_panel UI-only playback controls missing"
}
$handoffText = & powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_handoff.ps1
if ($LASTEXITCODE -ne 0) {
    throw "Command failed: powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_handoff.ps1"
}
$handoff = ($handoffText -join "`n") | ConvertFrom-Json
if ($handoff.schema -ne "rrkal_displaytools.handoff_inspection.v1") {
    throw "Handoff inspection schema missing or invalid"
}
if ($handoff.launch_packet_contracts.session_journal -ne "rrkal_displaytools.session_journal.v1") {
    throw "Handoff inspection session_journal contract missing or invalid"
}
if ($handoff.launch_packet_contracts.timeline_state -ne "rrkal_displaytools.timeline_state.v1") {
    throw "Handoff inspection timeline_state contract missing or invalid"
}
Invoke-CheckedNative py @("-3", "taichi_global_bathymetry.py", "--print-layer-manifest") | Out-Null
Invoke-CheckedNative py @("-3", "rrkal_displaytools_qt_panel.py", "--list-templates") | Out-Null

$scripts = Get-ChildItem scripts -Filter *.ps1
foreach ($script in $scripts) {
    $tokens = $null
    $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile(
        $script.FullName,
        [ref]$tokens,
        [ref]$errors
    ) > $null
    if ($errors -and $errors.Count -gt 0) {
        $errors | Format-List *
        throw "PowerShell parse failed: $($script.Name)"
    }
}

Write-Host "Smoke passed."

