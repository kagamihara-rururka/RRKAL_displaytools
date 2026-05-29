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
if ($launchPacket.active_layer_diagnostics.layer_capability_matrix_schema -ne "rrkal_displaytools.layer_capability_matrix.v1") {
    throw "Launch packet active_layer_diagnostics layer capability matrix schema link missing"
}
if ($launchPacket.active_layer_diagnostics.layer_runtime_evidence_schema -ne "rrkal_displaytools.layer_runtime_evidence.v1") {
    throw "Launch packet active_layer_diagnostics layer runtime evidence schema link missing"
}
if ($launchPacket.active_layer_diagnostics.layer_runtime_evidence_summary_schema -ne "rrkal_displaytools.layer_runtime_evidence_summary.v1") {
    throw "Launch packet active_layer_diagnostics layer runtime evidence summary schema link missing"
}
if ($launchPacket.active_layer_diagnostics.layer_runtime_badge_summary_schema -ne "rrkal_displaytools.layer_runtime_badge_summary.v1") {
    throw "Launch packet active_layer_diagnostics layer runtime badge summary schema link missing"
}
if ($launchPacket.active_layer_diagnostics.layer_runtime_warning_list_schema -ne "rrkal_displaytools.layer_runtime_warning_list.v1") {
    throw "Launch packet active_layer_diagnostics layer runtime warning list schema link missing"
}
if ($launchPacket.layer_capability_matrix.schema -ne "rrkal_displaytools.layer_capability_matrix.v1") {
    throw "Launch packet layer_capability_matrix schema missing or invalid"
}
if ($launchPacket.layer_capability_matrix.runtime_evidence.schema -ne "rrkal_displaytools.layer_runtime_evidence.v1") {
    throw "Launch packet layer_capability_matrix runtime evidence schema missing or invalid"
}
if ($launchPacket.layer_capability_matrix.runtime_evidence_summary.schema -ne "rrkal_displaytools.layer_runtime_evidence_summary.v1") {
    throw "Launch packet layer_capability_matrix runtime evidence summary schema missing or invalid"
}
if ($launchPacket.layer_capability_matrix.runtime_evidence_summary.status -ne "unavailable") {
    throw "Launch packet layer_capability_matrix runtime evidence summary should be unavailable in no-GUI export"
}
if ($launchPacket.layer_capability_matrix.runtime_badge_summary.schema -ne "rrkal_displaytools.layer_runtime_badge_summary.v1") {
    throw "Launch packet layer_capability_matrix runtime badge summary schema missing or invalid"
}
if ($launchPacket.layer_capability_matrix.runtime_badge_summary.copyable_provenance -ne $true) {
    throw "Launch packet layer_capability_matrix runtime badge summary should be copyable provenance"
}
if ($launchPacket.layer_capability_matrix.runtime_warning_list.schema -ne "rrkal_displaytools.layer_runtime_warning_list.v1") {
    throw "Launch packet layer_capability_matrix runtime warning list schema missing or invalid"
}
if ($launchPacket.layer_capability_matrix.runtime_warning_list.copyable_provenance -ne $true) {
    throw "Launch packet layer_capability_matrix runtime warning list should be copyable provenance"
}
if ($launchPacket.layer_capability_matrix.runtime_status_legend.schema -ne "rrkal_displaytools.layer_runtime_status_legend.v1") {
    throw "Launch packet layer_capability_matrix runtime status legend missing or invalid"
}
if ($launchPacket.layer_capability_matrix.runtime_evidence.available -ne $false) {
    throw "Launch packet layer_capability_matrix should not claim runtime evidence in no-GUI export"
}
if ([int]$launchPacket.layer_capability_matrix.live_counts.opacity -le 0) {
    throw "Launch packet layer_capability_matrix opacity live count missing"
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
if ($launchPacket.timeline_playback_readiness.animation_export -ne $true) {
    throw "Launch packet timeline playback readiness must claim PNG animation export"
}
if ($launchPacket.timeline_playback_readiness.camera_keyframes -ne $true) {
    throw "Launch packet timeline playback readiness must claim discrete camera keyframes"
}
if ($launchPacket.timeline_playback_readiness.camera_keyframe_interpolation -ne $true) {
    throw "Launch packet timeline playback readiness must claim camera keyframe interpolation"
}
if ($launchPacket.timeline_playback_readiness.layer_opacity_interpolation -ne $true) {
    throw "Launch packet timeline playback readiness must claim layer opacity interpolation"
}
if ($launchPacket.timeline_playback_readiness.layer_discrete_hold -ne $true) {
    throw "Launch packet timeline playback readiness must claim layer discrete hold"
}
if ($launchPacket.timeline_playback_plan.schema -ne "rrkal_displaytools.timeline_playback_plan.v1") {
    throw "Launch packet timeline playback plan schema missing or invalid"
}
if ($launchPacket.timeline_playback_plan.planned_apply_scope -notcontains "camera") {
    throw "Launch packet timeline playback plan missing camera apply scope"
}
if ($launchPacket.timeline_playback_plan.planned_apply_scope -notcontains "layer_opacity") {
    throw "Launch packet timeline playback plan missing layer opacity apply scope"
}
if ($launchPacket.timeline_playback_plan.planned_apply_scope -notcontains "layer_discrete_hold") {
    throw "Launch packet timeline playback plan missing layer discrete hold apply scope"
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
if ($launchPacket.timeline_animation_export.schema -ne "rrkal_displaytools.timeline_animation_export.v1") {
    throw "Launch packet timeline animation export schema missing or invalid"
}
if ($launchPacket.timeline_animation_export.applies -notcontains "timeline_gif_animation") {
    throw "Launch packet timeline animation export missing GIF animation capability"
}
if ($launchPacket.timeline_animation_export.applies -notcontains "timeline_mp4_video") {
    throw "Launch packet timeline animation export missing MP4 video capability"
}
if ($launchPacket.timeline_export_options.schema -ne "rrkal_displaytools.timeline_export_options.v1") {
    throw "Launch packet timeline_export_options schema missing or invalid"
}
if ($launchPacket.timeline_camera_keyframe.schema -ne "rrkal_displaytools.timeline_camera_keyframe.v1") {
    throw "Launch packet timeline camera keyframe schema missing or invalid"
}
if ($launchPacket.timeline_camera_interpolation.schema -ne "rrkal_displaytools.timeline_camera_interpolation.v1") {
    throw "Launch packet timeline camera interpolation schema missing or invalid"
}
if ($launchPacket.timeline_layer_opacity_interpolation.schema -ne "rrkal_displaytools.timeline_layer_opacity_interpolation.v1") {
    throw "Launch packet timeline layer opacity interpolation schema missing or invalid"
}
if ($launchPacket.timeline_layer_discrete_hold.schema -ne "rrkal_displaytools.timeline_layer_discrete_hold.v1") {
    throw "Launch packet timeline layer discrete hold schema missing or invalid"
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
if ($launchPacket.timeline_runtime_state.animation_export.schema -ne "rrkal_displaytools.timeline_animation_export.v1") {
    throw "Launch packet timeline_runtime_state animation export missing or invalid"
}
if ($launchPacket.timeline_runtime_state.animation_export.applies -notcontains "timeline_gif_animation") {
    throw "Launch packet timeline_runtime_state animation export missing GIF capability"
}
if ($launchPacket.timeline_runtime_state.animation_export.applies -notcontains "timeline_mp4_video") {
    throw "Launch packet timeline_runtime_state animation export missing MP4 capability"
}
if ($launchPacket.timeline_runtime_state.camera_keyframe.schema -ne "rrkal_displaytools.timeline_camera_keyframe.v1") {
    throw "Launch packet timeline_runtime_state camera keyframe missing or invalid"
}
if ($launchPacket.timeline_runtime_state.camera_interpolation.schema -ne "rrkal_displaytools.timeline_camera_interpolation.v1") {
    throw "Launch packet timeline_runtime_state camera interpolation missing or invalid"
}
if ($launchPacket.timeline_runtime_state.layer_opacity_interpolation.schema -ne "rrkal_displaytools.timeline_layer_opacity_interpolation.v1") {
    throw "Launch packet timeline_runtime_state layer opacity interpolation missing or invalid"
}
if ($launchPacket.timeline_runtime_state.layer_discrete_hold.schema -ne "rrkal_displaytools.timeline_layer_discrete_hold.v1") {
    throw "Launch packet timeline_runtime_state layer discrete hold missing or invalid"
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
$timelineExportDir = Join-Path $env:TEMP "rrkal_displaytools_smoke_timeline_export"
$timelineExportGif = Join-Path $timelineExportDir "smoke.gif"
$timelineExportMp4 = Join-Path $timelineExportDir "smoke.mp4"
$timelineExportPacketText = & py -3 scripts\export_launch_packet.py --template fast_synthetic --timeline-export-dir $timelineExportDir --timeline-export-frames 3 --timeline-export-fps 12 --timeline-export-gif $timelineExportGif --timeline-export-mp4 $timelineExportMp4
if ($LASTEXITCODE -ne 0) {
    throw "Command failed: py -3 scripts\export_launch_packet.py --template fast_synthetic --timeline-export-dir"
}
$timelineExportPacket = $timelineExportPacketText | ConvertFrom-Json
if ($timelineExportPacket.timeline_export_options.enabled -ne $true) {
    throw "No-GUI timeline export options did not enable export"
}
if ($timelineExportPacket.timeline_export_options.mp4_enabled -ne $true) {
    throw "No-GUI timeline export options did not enable MP4"
}
if ($timelineExportPacket.portable_command -notcontains "--timeline-export-dir") {
    throw "No-GUI timeline export portable command missing --timeline-export-dir"
}
if ($timelineExportPacket.portable_command -notcontains "--timeline-export-mp4") {
    throw "No-GUI timeline export portable command missing --timeline-export-mp4"
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
if ($timelineAck.animation_export.schema -ne "rrkal_displaytools.timeline_animation_export.v1") {
    throw "Renderer timeline ack endpoint animation export missing or invalid"
}
if ($timelineAck.animation_export.applies -notcontains "timeline_gif_animation") {
    throw "Renderer timeline ack endpoint animation export missing GIF capability"
}
if ($timelineAck.animation_export.applies -notcontains "timeline_mp4_video") {
    throw "Renderer timeline ack endpoint animation export missing MP4 capability"
}
if ($timelineAck.camera_keyframe.schema -ne "rrkal_displaytools.timeline_camera_keyframe.v1") {
    throw "Renderer timeline ack endpoint camera keyframe missing or invalid"
}
if ($timelineAck.camera_interpolation.schema -ne "rrkal_displaytools.timeline_camera_interpolation.v1") {
    throw "Renderer timeline ack endpoint camera interpolation missing or invalid"
}
if ($timelineAck.layer_opacity_interpolation.schema -ne "rrkal_displaytools.timeline_layer_opacity_interpolation.v1") {
    throw "Renderer timeline ack endpoint layer opacity interpolation missing or invalid"
}
if ($timelineAck.layer_discrete_hold.schema -ne "rrkal_displaytools.timeline_layer_discrete_hold.v1") {
    throw "Renderer timeline ack endpoint layer discrete hold missing or invalid"
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
if ($null -eq $timelineAck.first_keyframe_apply.changed.camera) {
    throw "Renderer timeline first keyframe apply camera changed field missing"
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
if ($capabilities.layer_capability_matrix.schema -ne "rrkal_displaytools.layer_capability_matrix.v1") {
    throw "Renderer layer_capability_matrix capability missing or invalid"
}
if ($capabilities.layer_capability_matrix.runtime_evidence.schema -ne "rrkal_displaytools.layer_runtime_evidence.v1") {
    throw "Renderer layer_capability_matrix runtime evidence schema missing or invalid"
}
if ($capabilities.layer_capability_matrix.runtime_evidence_summary.schema -ne "rrkal_displaytools.layer_runtime_evidence_summary.v1") {
    throw "Renderer layer_capability_matrix runtime evidence summary schema missing or invalid"
}
if ($capabilities.layer_capability_matrix.runtime_badge_summary.schema -ne "rrkal_displaytools.layer_runtime_badge_summary.v1") {
    throw "Renderer layer_capability_matrix runtime badge summary schema missing or invalid"
}
if ($capabilities.layer_capability_matrix.runtime_warning_list.schema -ne "rrkal_displaytools.layer_runtime_warning_list.v1") {
    throw "Renderer layer_capability_matrix runtime warning list schema missing or invalid"
}
if ($capabilities.layer_capability_matrix.runtime_status_legend.schema -ne "rrkal_displaytools.layer_runtime_status_legend.v1") {
    throw "Renderer layer_capability_matrix runtime status legend missing or invalid"
}
if ([int]$capabilities.layer_capability_matrix.live_counts.selected_layer_pick -le 0) {
    throw "Renderer layer_capability_matrix selected-layer pick count missing"
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
if ($capabilities.timeline_handoff.animation_export_schema -ne "rrkal_displaytools.timeline_animation_export.v1") {
    throw "Renderer timeline_handoff animation export schema missing or invalid"
}
if ($capabilities.timeline_handoff.camera_keyframe_schema -ne "rrkal_displaytools.timeline_camera_keyframe.v1") {
    throw "Renderer timeline_handoff camera keyframe schema missing or invalid"
}
if ($capabilities.timeline_handoff.camera_interpolation_schema -ne "rrkal_displaytools.timeline_camera_interpolation.v1") {
    throw "Renderer timeline_handoff camera interpolation schema missing or invalid"
}
if ($capabilities.timeline_handoff.layer_opacity_interpolation_schema -ne "rrkal_displaytools.timeline_layer_opacity_interpolation.v1") {
    throw "Renderer timeline_handoff layer opacity interpolation schema missing or invalid"
}
if ($capabilities.timeline_handoff.layer_discrete_hold_schema -ne "rrkal_displaytools.timeline_layer_discrete_hold.v1") {
    throw "Renderer timeline_handoff layer discrete hold schema missing or invalid"
}
if ($capabilities.timeline_handoff.input_contracts -notcontains "rrkal_displaytools.timeline_camera_keyframe.v1") {
    throw "Renderer timeline_handoff camera keyframe input contract missing"
}
if ($capabilities.timeline_handoff.input_contracts -notcontains "rrkal_displaytools.timeline_camera_interpolation.v1") {
    throw "Renderer timeline_handoff camera interpolation input contract missing"
}
if ($capabilities.timeline_handoff.input_contracts -notcontains "rrkal_displaytools.timeline_layer_opacity_interpolation.v1") {
    throw "Renderer timeline_handoff layer opacity interpolation input contract missing"
}
if ($capabilities.timeline_handoff.input_contracts -notcontains "rrkal_displaytools.timeline_layer_discrete_hold.v1") {
    throw "Renderer timeline_handoff layer discrete hold input contract missing"
}
if ($capabilities.timeline_handoff.controls -notcontains "timeline-export-dir") {
    throw "Renderer timeline_handoff timeline-export-dir control missing"
}
if ($capabilities.timeline_handoff.controls -notcontains "timeline-export-gif") {
    throw "Renderer timeline_handoff timeline-export-gif control missing"
}
if ($capabilities.timeline_handoff.controls -notcontains "timeline-export-mp4") {
    throw "Renderer timeline_handoff timeline-export-mp4 control missing"
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
if ($handoff.launch_packet_contracts.layer_capability_matrix -ne "rrkal_displaytools.layer_capability_matrix.v1") {
    throw "Handoff inspection layer_capability_matrix contract missing or invalid"
}
if ($handoff.layer_capability_matrix.schema -ne "rrkal_displaytools.layer_capability_matrix.v1") {
    throw "Handoff inspection layer_capability_matrix summary missing or invalid"
}
if ($handoff.layer_capability_matrix.runtime_evidence_schema -ne "rrkal_displaytools.layer_runtime_evidence.v1") {
    throw "Handoff inspection layer runtime evidence schema missing or invalid"
}
if ($handoff.layer_capability_matrix.runtime_evidence_summary_schema -ne "rrkal_displaytools.layer_runtime_evidence_summary.v1") {
    throw "Handoff inspection layer runtime evidence summary schema missing or invalid"
}
if ($handoff.layer_capability_matrix.runtime_badge_summary_schema -ne "rrkal_displaytools.layer_runtime_badge_summary.v1") {
    throw "Handoff inspection layer runtime badge summary schema missing or invalid"
}
if ($handoff.layer_capability_matrix.runtime_warning_list_schema -ne "rrkal_displaytools.layer_runtime_warning_list.v1") {
    throw "Handoff inspection layer runtime warning list schema missing or invalid"
}
if ($handoff.layer_capability_matrix.runtime_status_legend_schema -ne "rrkal_displaytools.layer_runtime_status_legend.v1") {
    throw "Handoff inspection layer runtime status legend schema missing or invalid"
}
if ([int]$handoff.layer_capability_matrix.live_counts.blend -le 0) {
    throw "Handoff inspection layer_capability_matrix blend live count missing"
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

