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
if ($launchPacket.active_layer_diagnostics.layer_runtime_interaction_context_schema -ne "rrkal_displaytools.layer_runtime_interaction_context.v1") {
    throw "Launch packet active_layer_diagnostics layer runtime interaction context schema link missing"
}
if ($launchPacket.active_layer_diagnostics.layer_territory_identity_context_schema -ne "rrkal_displaytools.layer_territory_identity_context.v1") {
    throw "Launch packet active_layer_diagnostics layer territory identity context schema link missing"
}
if ($launchPacket.active_layer_diagnostics.layer_authoritative_identity_source_schema -ne "rrkal_displaytools.layer_authoritative_identity_source.v1") {
    throw "Launch packet active_layer_diagnostics layer authoritative identity source schema link missing"
}
if ($launchPacket.active_layer_diagnostics.layer_renderer_diagnostics_summary_schema -ne "rrkal_displaytools.layer_renderer_diagnostics_summary.v1") {
    throw "Launch packet active_layer_diagnostics layer renderer diagnostics summary schema link missing"
}
if ($launchPacket.active_layer_diagnostics.layer_renderer_diagnostics_detail_schema -ne "rrkal_displaytools.layer_renderer_diagnostics_detail.v1") {
    throw "Launch packet active_layer_diagnostics layer renderer diagnostics detail schema link missing"
}
if ($launchPacket.active_layer_diagnostics.layer_renderer_diagnostics_remediation_schema -ne "rrkal_displaytools.layer_renderer_diagnostics_remediation.v1") {
    throw "Launch packet active_layer_diagnostics layer renderer diagnostics remediation schema link missing"
}
if ($launchPacket.active_layer_diagnostics.layer_pick_screen_position_field -ne "screen_position") {
    throw "Launch packet active_layer_diagnostics screen position field missing"
}
if ($launchPacket.active_layer_diagnostics.layer_pick_screen_position_source -ne "state/renderer_layer_pick_state.json") {
    throw "Launch packet active_layer_diagnostics screen position source mismatch"
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
if ($launchPacket.layer_capability_matrix.runtime_interaction_context.schema -ne "rrkal_displaytools.layer_runtime_interaction_context.v1") {
    throw "Launch packet layer_capability_matrix runtime interaction context schema missing or invalid"
}
if ($launchPacket.layer_capability_matrix.runtime_interaction_context.pick_context_available -ne $false) {
    throw "Launch packet layer_capability_matrix runtime interaction context should not claim live pick context"
}
if ($launchPacket.layer_capability_matrix.territory_identity_context.schema -ne "rrkal_displaytools.layer_territory_identity_context.v1") {
    throw "Launch packet layer_capability_matrix territory identity context schema missing or invalid"
}
if ($launchPacket.layer_capability_matrix.territory_identity_context.authoritative_identity_available -ne $false) {
    throw "Launch packet layer_capability_matrix should not claim authoritative territory identity"
}
if ($launchPacket.layer_capability_matrix.authoritative_identity_source.schema -ne "rrkal_displaytools.layer_authoritative_identity_source.v1") {
    throw "Launch packet layer_capability_matrix authoritative identity source schema missing or invalid"
}
if ($launchPacket.layer_capability_matrix.authoritative_identity_source.displaytools_role -ne "reference_only_handoff") {
    throw "Launch packet layer_capability_matrix authoritative identity source must be reference-only"
}
if ($launchPacket.layer_capability_matrix.renderer_diagnostics_summary.schema -ne "rrkal_displaytools.layer_renderer_diagnostics_summary.v1") {
    throw "Launch packet layer_capability_matrix renderer diagnostics summary schema missing or invalid"
}
if ($launchPacket.layer_capability_matrix.renderer_diagnostics_summary.runtime_ack_available -ne $false) {
    throw "Launch packet layer_capability_matrix renderer diagnostics summary should not claim runtime ack in no-GUI export"
}
if ($launchPacket.layer_capability_matrix.renderer_diagnostics_detail.schema -ne "rrkal_displaytools.layer_renderer_diagnostics_detail.v1") {
    throw "Launch packet layer_capability_matrix renderer diagnostics detail schema missing or invalid"
}
if ([int]$launchPacket.layer_capability_matrix.renderer_diagnostics_detail.bridge_count -lt 5) {
    throw "Launch packet layer_capability_matrix renderer diagnostics detail bridge count missing"
}
if ($launchPacket.layer_capability_matrix.renderer_diagnostics_remediation.schema -ne "rrkal_displaytools.layer_renderer_diagnostics_remediation.v1") {
    throw "Launch packet layer_capability_matrix renderer diagnostics remediation schema missing or invalid"
}
if ([int]$launchPacket.layer_capability_matrix.renderer_diagnostics_remediation.hint_count -lt 1) {
    throw "Launch packet layer_capability_matrix renderer diagnostics remediation hint count missing"
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
if ($launchPacket.layer_operator_shortcuts.schema -ne "rrkal_displaytools.layer_operator_shortcuts.v1") {
    throw "Launch packet layer_operator_shortcuts schema missing or invalid"
}
$launchLayerOperatorActions = @($launchPacket.layer_operator_shortcuts.implemented_action_ids)
if ($launchLayerOperatorActions -notcontains "solo_selected_layer") {
    throw "Launch packet layer_operator_shortcuts missing solo action"
}
if ($launchLayerOperatorActions -notcontains "restore_solo_visibility") {
    throw "Launch packet layer_operator_shortcuts missing restore solo action"
}
if ($launchLayerOperatorActions -notcontains "undo_layer_state") {
    throw "Launch packet layer_operator_shortcuts missing layer undo action"
}
if ($launchLayerOperatorActions -notcontains "open_boundary_emphasis") {
    throw "Launch packet layer_operator_shortcuts missing boundary emphasis action"
}
if ([int]$launchPacket.layer_operator_shortcuts.keyboard_shortcut_count -lt 7) {
    throw "Launch packet layer_operator_shortcuts keyboard shortcut count missing"
}
if ($launchPacket.layer_operator_shortcuts.keyboard_shortcuts.solo_selected_layer -ne "Ctrl+Alt+S") {
    throw "Launch packet layer_operator_shortcuts solo shortcut mismatch"
}
if ($launchPacket.layer_operator_groups.schema -ne "rrkal_displaytools.layer_operator_groups.v1") {
    throw "Launch packet layer_operator_groups schema missing or invalid"
}
if ([int]$launchPacket.layer_operator_groups.group_count -lt 5) {
    throw "Launch packet layer_operator_groups group count missing"
}
if ([int]$launchPacket.layer_operator_groups.complete_group_count -lt 5) {
    throw "Launch packet layer_operator_groups incomplete"
}
if ($launchPacket.layer_selection_tool.schema -ne "rrkal_displaytools.layer_selection_tool.v1") {
    throw "Launch packet layer_selection_tool schema missing or invalid"
}
if ($launchPacket.layer_selection_tool.tool_mode -ne "select_layer") {
    throw "Launch packet layer_selection_tool mode mismatch"
}
if ($launchPacket.layer_selection_tool.renderer_pick_bridge.pick_state_file -ne "state/renderer_layer_pick_state.json") {
    throw "Launch packet layer_selection_tool pick state file mismatch"
}
if ([int]$launchPacket.layer_selection_tool.selectable_layer_count -le 0) {
    throw "Launch packet layer_selection_tool selectable layer count missing"
}
if ($launchPacket.layer_selection_tool.brush_mask_scope -ne "excluded") {
    throw "Launch packet layer_selection_tool must exclude brush/mask scope"
}
if ($launchPacket.layer_selection_tool.qt_surfaces -notcontains "Boundary row emphasis action badge") {
    throw "Launch packet layer_selection_tool boundary action badge surface missing"
}
if ($launchPacket.layer_research_workflow.schema -ne "rrkal_displaytools.layer_research_workflow.v1") {
    throw "Launch packet layer_research_workflow schema missing or invalid"
}
if ($launchPacket.layer_research_workflow.status -ne "ready") {
    throw "Launch packet layer_research_workflow not ready"
}
if ($launchPacket.layer_research_workflow.qt_surface -ne "Layers dock research workflow label") {
    throw "Launch packet layer_research_workflow Qt surface mismatch"
}
if ($launchPacket.layer_research_workflow.researcher_path -notcontains "Select or reveal a layer") {
    throw "Launch packet layer_research_workflow researcher path incomplete"
}
if ($launchPacket.boundary_emphasis_control.schema -ne "rrkal_displaytools.boundary_emphasis_control.v1") {
    throw "Launch packet boundary_emphasis_control schema missing or invalid"
}
if ($launchPacket.boundary_emphasis_control.status -ne "ui_ready") {
    throw "Launch packet boundary_emphasis_control not UI ready"
}
if ([int]$launchPacket.boundary_emphasis_control.control_count -lt 7) {
    throw "Launch packet boundary_emphasis_control controls missing"
}
if ($launchPacket.boundary_emphasis_control.target_layer_types -notcontains "exclusive_economic_zone") {
    throw "Launch packet boundary_emphasis_control EEZ target missing"
}
if ($launchPacket.boundary_emphasis_control.renderer_hook_status -ne "wired_via_boundary_highlight_mask") {
    throw "Launch packet boundary_emphasis_control renderer hook is not wired through boundary highlight mask"
}
if ($launchPacket.boundary_emphasis_control.renderer_bridge_contract -ne "rrkal_displaytools.boundary_highlight_mask.v1") {
    throw "Launch packet boundary_emphasis_control renderer bridge contract missing"
}
if ($launchPacket.boundary_emphasis_control.renderer_controls_mapped -notcontains "gamma") {
    throw "Launch packet boundary_emphasis_control gamma bridge mapping missing"
}
if ($launchPacket.boundary_emphasis_control.dialog_feedback -notcontains "rgb_swatch") {
    throw "Launch packet boundary_emphasis_control RGB swatch feedback missing"
}
if ($launchPacket.boundary_emphasis_control.dialog_feedback -notcontains "live_numeric_readout") {
    throw "Launch packet boundary_emphasis_control live numeric readout missing"
}
if ($launchPacket.boundary_emphasis_control.value_preview_fields -notcontains "target_alignment") {
    throw "Launch packet boundary_emphasis_control target alignment preview missing"
}
if (-not $launchPacket.boundary_emphasis_control.target_alignment) {
    throw "Launch packet boundary_emphasis_control target alignment field missing"
}
if ($launchPacket.boundary_emphasis_control.row_double_click_binding -ne "ready") {
    throw "Launch packet boundary_emphasis_control row double-click binding missing"
}
if ($launchPacket.boundary_emphasis_control.row_double_click_layer_keys -notcontains "eez_layer") {
    throw "Launch packet boundary_emphasis_control row double-click EEZ layer missing"
}
if ($launchPacket.style_renderer_entries.schema -ne "rrkal_displaytools.style_renderer_entries.v1") {
    throw "Launch packet style_renderer_entries schema missing or invalid"
}
if ([int]$launchPacket.style_renderer_entries.entry_count -lt 4) {
    throw "Launch packet style_renderer_entries entry count missing"
}
if ($launchPacket.style_renderer_entries.entry_ids -notcontains "parchment") {
    throw "Launch packet style_renderer_entries missing parchment entry"
}
if ($launchPacket.style_renderer_entries.entry_ids -notcontains "tactical") {
    throw "Launch packet style_renderer_entries missing tactical entry"
}
if ($launchPacket.style_profile_renderer_routes.schema -ne "rrkal_displaytools.style_profile_renderer_routes.v1") {
    throw "Launch packet style_profile_renderer_routes schema missing or invalid"
}
if ($launchPacket.style_profile_renderer_routes.status -ne "ready") {
    throw "Launch packet style_profile_renderer_routes not ready"
}
if ($launchPacket.style_profile_renderer_routes.route_ids -notcontains "parchment") {
    throw "Launch packet style_profile_renderer_routes missing parchment route"
}
if ($launchPacket.style_profile_renderer_routes.route_ids -notcontains "tactical") {
    throw "Launch packet style_profile_renderer_routes missing tactical route"
}
if ($launchPacket.module_boundary_registry.schema -ne "rrkal_displaytools.module_boundary_registry.v1") {
    throw "Launch packet module_boundary_registry schema missing or invalid"
}
if ([int]$launchPacket.module_boundary_registry.module_count -lt 8) {
    throw "Launch packet module_boundary_registry module count missing"
}
if ($launchPacket.module_boundary_registry.target_modules -notcontains "render_core/taichi_globe.py") {
    throw "Launch packet module_boundary_registry missing render_core boundary"
}
if ($launchPacket.module_boundary_registry.tk_primary_ui_allowed -ne $false) {
    throw "Launch packet module_boundary_registry must keep Tk out of primary UI"
}
if ($launchPacket.cross_machine_clone_readiness.schema -ne "rrkal_displaytools.cross_machine_clone_readiness.v1") {
    throw "Launch packet cross_machine_clone_readiness schema missing or invalid"
}
if ($launchPacket.cross_machine_clone_readiness.status -ne "ready") {
    throw "Launch packet cross_machine_clone_readiness not ready"
}
if ($launchPacket.cross_machine_clone_readiness.required_commands -notcontains "scripts/setup_windows.ps1") {
    throw "Launch packet cross_machine_clone_readiness missing setup command"
}
if ($launchPacket.cross_machine_clone_readiness.setup_doc -ne "docs/SETUP_WINDOWS.zh-TW.md") {
    throw "Launch packet cross_machine_clone_readiness setup doc mismatch"
}
if ($launchPacket.cross_machine_clone_readiness.qt_surface -ne "Layers dock cross-machine readiness label") {
    throw "Launch packet cross_machine_clone_readiness Qt surface mismatch"
}
if ($launchPacket.cross_machine_clone_readiness.launcher_options -notcontains "-HandoffFirst") {
    throw "Launch packet cross_machine_clone_readiness missing HandoffFirst launcher option"
}
if ($launchPacket.cross_machine_clone_readiness.handoff_first_command -notlike "*run_qt_panel.ps1 -HandoffFirst") {
    throw "Launch packet cross_machine_clone_readiness handoff-first command mismatch"
}
if ($launchPacket.profile_ui_state_replay.qt_inspector_action_ids -notcontains "boundary_json") {
    throw "Launch packet profile_ui_state_replay Boundary inspector action missing"
}
if ([int]$launchPacket.profile_ui_state_replay.qt_inspector_action_count -lt 9) {
    throw "Launch packet profile_ui_state_replay inspector action count missing"
}
if ($launchPacket.profile_launch_readiness.schema -ne "rrkal_displaytools.profile_launch_readiness.v1") {
    throw "Launch packet profile_launch_readiness schema missing or invalid"
}
if ($launchPacket.profile_launch_readiness.readiness -ne "ready") {
    throw "Launch packet profile_launch_readiness should be ready"
}
if ([int]$launchPacket.profile_launch_readiness.ready_check_count -lt 7) {
    throw "Launch packet profile_launch_readiness ready check count missing"
}
if ($launchPacket.profile_launch_readiness_ui.schema -ne "rrkal_displaytools.profile_launch_readiness_ui.v1") {
    throw "Launch packet profile_launch_readiness_ui schema missing or invalid"
}
if ($launchPacket.profile_launch_readiness_ui.readiness -ne "ready") {
    throw "Launch packet profile_launch_readiness_ui should be ready"
}
if ($launchPacket.profile_launch_readiness_ui.qt_surface -ne "Layers dock readiness label") {
    throw "Launch packet profile_launch_readiness_ui surface mismatch"
}
if ($launchPacket.layer_visual_presets.schema -ne "rrkal_displaytools.layer_visual_presets.v1") {
    throw "Launch packet layer_visual_presets schema missing or invalid"
}
if ([int]$launchPacket.layer_visual_presets.preset_count -lt 4) {
    throw "Launch packet layer_visual_presets preset count missing"
}
if ($launchPacket.layer_visual_presets.preset_ids -notcontains "hydrology_focus") {
    throw "Launch packet layer_visual_presets missing hydrology preset"
}
if ($launchPacket.layer_visual_presets.preset_ids -notcontains "boundary_focus") {
    throw "Launch packet layer_visual_presets missing boundary preset"
}
if ($launchPacket.layer_visual_presets.respects_layer_locks -ne $true) {
    throw "Launch packet layer_visual_presets must preserve locked layers"
}
if ($launchPacket.layer_visual_preset_runtime_feedback.schema -ne "rrkal_displaytools.layer_visual_preset_runtime_feedback.v1") {
    throw "Launch packet layer_visual_preset_runtime_feedback schema missing or invalid"
}
if ($launchPacket.layer_visual_preset_runtime_feedback.qt_surface -ne "Layers dock preset renderer ack label") {
    throw "Launch packet layer_visual_preset_runtime_feedback surface mismatch"
}
if ($launchPacket.layer_visual_preset_runtime_feedback.requires_renderer_ack_for_reproducibility -ne $true) {
    throw "Launch packet layer_visual_preset_runtime_feedback must require renderer ack"
}
if ($launchPacket.hydrology_lod_readiness.schema -ne "rrkal_displaytools.hydrology_lod_readiness.v1") {
    throw "Launch packet hydrology_lod_readiness schema missing or invalid"
}
if ($launchPacket.hydrology_lod_readiness.readiness -ne "ready") {
    throw "Launch packet hydrology_lod_readiness should be ready for lake/river layers"
}
if ([int]$launchPacket.hydrology_lod_readiness.live_hydrology_layer_count -lt 2) {
    throw "Launch packet hydrology_lod_readiness live hydrology layer count missing"
}
if ($launchPacket.hydrology_lod_readiness.stable_renderer_targets -notcontains "lakes") {
    throw "Launch packet hydrology_lod_readiness missing lakes renderer target"
}
if ($launchPacket.hydrology_lod_readiness.lod_hook_status -ne "contract_ready") {
    throw "Launch packet hydrology_lod_readiness LOD hook not contract-ready"
}
if ($launchPacket.hydrology_lod_runtime_evidence.schema -ne "rrkal_displaytools.hydrology_lod_runtime_evidence.v1") {
    throw "Launch packet hydrology_lod_runtime_evidence schema missing or invalid"
}
if ($launchPacket.hydrology_lod_runtime_evidence.ack_file -ne "state/renderer_layer_runtime_ack.json") {
    throw "Launch packet hydrology_lod_runtime_evidence ack file mismatch"
}
if ($launchPacket.hydrology_lod_runtime_evidence.pick_state_file -ne "state/renderer_layer_pick_state.json") {
    throw "Launch packet hydrology_lod_runtime_evidence pick state file mismatch"
}
if ($launchPacket.ocean_material_control_port.schema -ne "rrkal_displaytools.ocean_material_control_port.v1") {
    throw "Launch packet ocean_material_control_port schema missing or invalid"
}
if ($launchPacket.ocean_material_control_port.renderer_flags -notcontains "--ocean-wave-strength") {
    throw "Launch packet ocean_material_control_port missing wave flag"
}
if ($launchPacket.ocean_material_control_port.sea_state_port.normalized_fields -notcontains "wave_strength") {
    throw "Launch packet ocean_material_control_port sea-state normalized fields missing"
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
if ($launchPacket.timeline_playback_plan.planned_apply_scope -notcontains "boundary_emphasis_control") {
    throw "Launch packet timeline playback plan missing boundary emphasis apply scope"
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
if ($launchPacket.boundary_highlight.identity_status.applied -notcontains "closed_ring_area_hit_test") {
    throw "Launch packet boundary_highlight identity_status closed ring hit test missing"
}
if ($launchPacket.boundary_highlight.identity_status.pending -notcontains "authoritative_polygon_territory_identity") {
    throw "Launch packet boundary_highlight identity_status authoritative polygon pending marker missing"
}
if ($launchPacket.boundary_highlight.ack_history_contract -ne "boundary_highlight_ack_history") {
    throw "Launch packet boundary_highlight ack history contract missing"
}
if ($launchPacket.boundary_highlight.ack_history_fields -notcontains "pending") {
    throw "Launch packet boundary_highlight ack history pending field missing"
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
if ($launchPacket.portable_command -notcontains "--cursor-geodesy-state-file") {
    throw "Launch packet portable command is missing --cursor-geodesy-state-file"
}
if ($launchPacket.portable_command -notcontains "--cursor-geodesy-ack-file") {
    throw "Launch packet portable command is missing --cursor-geodesy-ack-file"
}
if ($launchPacket.canvas_preview.preview_frame_path -ne "state/renderer_preview_frame.png") {
    throw "Launch packet canvas_preview preview_frame_path missing or invalid"
}
if ([double]$launchPacket.canvas_preview.preview_frame_interval_s -le 0) {
    throw "Launch packet canvas_preview preview_frame_interval_s missing or invalid"
}
if ($launchPacket.cursor_geodesy_readout.schema -ne "rrkal_displaytools.cursor_geodesy_readout.v1") {
    throw "Launch packet cursor_geodesy_readout schema missing or invalid"
}
if ($launchPacket.cursor_geodesy_readout.event_position_guard -ne "QMouseEvent.position with QMouseEvent.pos fallback") {
    throw "Launch packet cursor_geodesy_readout event guard missing"
}
if ($launchPacket.cursor_geodesy_readout.backend_raycast_status -ne "renderer_globe_intersection_contract_ready") {
    throw "Launch packet cursor_geodesy_readout backend raycast status mismatch"
}
if ($launchPacket.cursor_geodesy_readout.renderer_raycast_helper -ne "cursor_geodesy.viewport_sphere_raycast") {
    throw "Launch packet cursor_geodesy_readout raycast helper missing"
}
if ($launchPacket.cursor_geodesy_readout.raycast_smoke_cases -notcontains "center_hit") {
    throw "Launch packet cursor_geodesy_readout center raycast smoke case missing"
}
if ($launchPacket.cursor_geodesy_readout.runtime_bridge_status -ne "renderer_mouse_state_wired") {
    throw "Launch packet cursor_geodesy_readout runtime bridge status mismatch"
}
if ($launchPacket.cursor_geodesy_readout.renderer_raycast_state_file -ne "state/renderer_cursor_geodesy_state.json") {
    throw "Launch packet cursor_geodesy_readout state file mismatch"
}
if ($launchPacket.cursor_geodesy_readout.runtime_bridge_fields -notcontains "latitude") {
    throw "Launch packet cursor_geodesy_readout latitude bridge field missing"
}
if ($launchPacket.cursor_geodesy_readout.runtime_bridge_fields -notcontains "updated_at_utc") {
    throw "Launch packet cursor_geodesy_readout updated_at_utc bridge field missing"
}
if ($launchPacket.cursor_geodesy_readout.renderer_controls -notcontains "cursor-geodesy-state-file") {
    throw "Launch packet cursor_geodesy_readout state-file renderer control missing"
}
if ($launchPacket.pin_overlay.schema -ne "rrkal_displaytools.pin_projection.v1") {
    throw "Launch packet pin_overlay schema missing or invalid"
}
if ($launchPacket.pin_overlay.rotation_rule -notlike "*every frame*") {
    throw "Launch packet pin_overlay rotation rule missing"
}
if ($launchPacket.pin_overlay.occlusion_rule -notlike "*view_z <= horizon_eps*") {
    throw "Launch packet pin_overlay occlusion rule missing"
}
if ($launchPacket.pin_overlay.renderer_overlay_status -ne "wired_to_pin_overlay_rgba_and_frame_composition") {
    throw "Launch packet pin_overlay renderer overlay status mismatch"
}
if ($launchPacket.pin_overlay.cursor_fill_priority -ne "renderer_cursor_geodesy_state_then_ui_estimate") {
    throw "Launch packet pin_overlay cursor fill priority mismatch"
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
if ($null -eq $timelineAck.first_keyframe_apply.changed.boundary_emphasis_control) {
    throw "Renderer timeline first keyframe apply boundary emphasis changed field missing"
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
if ($capabilities.active_layer_diagnostics.runtime_fields -notcontains "screen_position") {
    throw "Renderer active_layer_diagnostics screen_position runtime field missing"
}
if ($capabilities.layer_operator_shortcuts.schema -ne "rrkal_displaytools.layer_operator_shortcuts.v1") {
    throw "Renderer layer_operator_shortcuts schema missing or invalid"
}
if ($capabilities.layer_operator_shortcuts.implemented_action_ids -notcontains "solo_selected_layer") {
    throw "Renderer layer_operator_shortcuts missing solo action"
}
if ($capabilities.layer_operator_shortcuts.implemented_action_ids -notcontains "open_boundary_emphasis") {
    throw "Renderer layer_operator_shortcuts missing boundary emphasis action"
}
if ([int]$capabilities.layer_operator_shortcuts.keyboard_shortcut_count -lt 7) {
    throw "Renderer layer_operator_shortcuts keyboard shortcut count missing"
}
if ($capabilities.layer_operator_groups.schema -ne "rrkal_displaytools.layer_operator_groups.v1") {
    throw "Renderer layer_operator_groups schema missing or invalid"
}
if ([int]$capabilities.layer_operator_groups.complete_group_count -lt 5) {
    throw "Renderer layer_operator_groups incomplete"
}
if ($capabilities.layer_selection_tool.schema -ne "rrkal_displaytools.layer_selection_tool.v1") {
    throw "Renderer layer_selection_tool schema missing or invalid"
}
if ($capabilities.layer_selection_tool.renderer_pick_bridge.live_control -ne "selected_layer_pick") {
    throw "Renderer layer_selection_tool live control mismatch"
}
if ($capabilities.layer_selection_tool.supported_renderer_pick_scopes -notcontains "boundary_line") {
    throw "Renderer layer_selection_tool boundary pick scope missing"
}
if ($capabilities.layer_selection_tool.brush_mask_scope -ne "excluded") {
    throw "Renderer layer_selection_tool must exclude brush/mask scope"
}
if ($capabilities.layer_selection_tool.qt_surfaces -notcontains "Boundary row emphasis action badge") {
    throw "Renderer layer_selection_tool boundary action badge surface missing"
}
if ($capabilities.layer_research_workflow.schema -ne "rrkal_displaytools.layer_research_workflow.v1") {
    throw "Renderer layer_research_workflow schema missing or invalid"
}
if ($capabilities.layer_research_workflow.status -ne "ready") {
    throw "Renderer layer_research_workflow not ready"
}
if ($capabilities.cursor_geodesy_readout.schema -ne "rrkal_displaytools.cursor_geodesy_readout.v1") {
    throw "Renderer cursor_geodesy_readout schema missing or invalid"
}
if ($capabilities.cursor_geodesy_readout.projection_method -ne "viewport_equirectangular_preview_estimate") {
    throw "Renderer cursor_geodesy_readout projection method mismatch"
}
if ($capabilities.cursor_geodesy_readout.backend_raycast_status -ne "renderer_globe_intersection_contract_ready") {
    throw "Renderer cursor_geodesy_readout backend raycast status mismatch"
}
if ($capabilities.cursor_geodesy_readout.renderer_raycast_schema -ne "rrkal_displaytools.cursor_geodesy_raycast.v1") {
    throw "Renderer cursor_geodesy_readout raycast schema missing"
}
if ($capabilities.cursor_geodesy_readout.raycast_smoke_cases -notcontains "outside_globe_miss") {
    throw "Renderer cursor_geodesy_readout outside-globe raycast smoke case missing"
}
if ($capabilities.cursor_geodesy_readout.runtime_bridge_status -ne "renderer_mouse_state_wired") {
    throw "Renderer cursor_geodesy_readout runtime bridge status mismatch"
}
if ($capabilities.cursor_geodesy_readout.renderer_raycast_ack_file -ne "state/renderer_cursor_geodesy_ack.json") {
    throw "Renderer cursor_geodesy_readout ack file mismatch"
}
if ($capabilities.cursor_geodesy_readout.runtime_bridge_fields -notcontains "hit") {
    throw "Renderer cursor_geodesy_readout hit bridge field missing"
}
if ($capabilities.cursor_geodesy_readout.runtime_events -notcontains "qt_mouse_move") {
    throw "Renderer cursor_geodesy_readout qt_mouse_move runtime event missing"
}
if ($capabilities.pin_overlay.schema -ne "rrkal_displaytools.pin_projection.v1") {
    throw "Renderer pin_overlay schema missing or invalid"
}
if ($capabilities.pin_overlay.renderer_overlay_status -ne "wired_to_pin_overlay_rgba_and_frame_composition") {
    throw "Renderer pin_overlay renderer overlay status mismatch"
}
if ($capabilities.pin_overlay.horizon_control -ne "--pin-horizon-eps / PIN_HORIZON_EPS") {
    throw "Renderer pin_overlay horizon control missing"
}
if ($capabilities.pin_overlay.cursor_fill_sources -notcontains "renderer_cursor_geodesy_state") {
    throw "Renderer pin_overlay cursor fill source missing"
}
if ($capabilities.boundary_emphasis_control.schema -ne "rrkal_displaytools.boundary_emphasis_control.v1") {
    throw "Renderer boundary_emphasis_control schema missing or invalid"
}
if ($capabilities.boundary_emphasis_control.status -ne "ui_ready") {
    throw "Renderer boundary_emphasis_control not UI ready"
}
if ($capabilities.boundary_emphasis_control.renderer_hook_status -ne "wired_via_boundary_highlight_mask") {
    throw "Renderer boundary_emphasis_control hook is not wired through boundary highlight mask"
}
if ($capabilities.boundary_emphasis_control.renderer_bridge_contract -ne "rrkal_displaytools.boundary_highlight_mask.v1") {
    throw "Renderer boundary_emphasis_control bridge contract missing"
}
if ($capabilities.boundary_emphasis_control.renderer_controls_mapped -notcontains "breathing") {
    throw "Renderer boundary_emphasis_control breathing bridge mapping missing"
}
if ($capabilities.boundary_emphasis_control.dialog_feedback -notcontains "rgb_swatch") {
    throw "Renderer boundary_emphasis_control RGB swatch feedback missing"
}
if ($capabilities.boundary_emphasis_control.dialog_feedback -notcontains "live_numeric_readout") {
    throw "Renderer boundary_emphasis_control live numeric readout missing"
}
if ($capabilities.boundary_emphasis_control.value_preview_fields -notcontains "target_alignment") {
    throw "Renderer boundary_emphasis_control target alignment preview missing"
}
if (-not $capabilities.boundary_emphasis_control.target_alignment) {
    throw "Renderer boundary_emphasis_control target alignment field missing"
}
if ($capabilities.boundary_emphasis_control.row_double_click_binding -ne "ready") {
    throw "Renderer boundary_emphasis_control row double-click binding missing"
}
if ($capabilities.style_renderer_entries.schema -ne "rrkal_displaytools.style_renderer_entries.v1") {
    throw "Renderer style_renderer_entries schema missing or invalid"
}
if ($capabilities.style_renderer_entries.entry_ids -notcontains "parchment") {
    throw "Renderer style_renderer_entries missing parchment entry"
}
if ($capabilities.style_renderer_entries.entry_ids -notcontains "tactical") {
    throw "Renderer style_renderer_entries missing tactical entry"
}
if ($capabilities.style_profile_renderer_routes.schema -ne "rrkal_displaytools.style_profile_renderer_routes.v1") {
    throw "Renderer style_profile_renderer_routes schema missing or invalid"
}
if ($capabilities.style_profile_renderer_routes.route_ids -notcontains "parchment") {
    throw "Renderer style_profile_renderer_routes missing parchment route"
}
if ($capabilities.style_profile_renderer_routes.route_ids -notcontains "tactical") {
    throw "Renderer style_profile_renderer_routes missing tactical route"
}
if ($capabilities.module_boundary_registry.schema -ne "rrkal_displaytools.module_boundary_registry.v1") {
    throw "Renderer module_boundary_registry schema missing or invalid"
}
if ($capabilities.module_boundary_registry.target_modules -notcontains "data_sources/*") {
    throw "Renderer module_boundary_registry missing RRKAL data boundary"
}
if ($capabilities.cross_machine_clone_readiness.schema -ne "rrkal_displaytools.cross_machine_clone_readiness.v1") {
    throw "Renderer cross_machine_clone_readiness schema missing or invalid"
}
if ($capabilities.cross_machine_clone_readiness.required_commands -notcontains "scripts/run_qt_panel.ps1") {
    throw "Renderer cross_machine_clone_readiness missing run command"
}
if ($capabilities.cross_machine_clone_readiness.qt_surface -ne "Layers dock cross-machine readiness label") {
    throw "Renderer cross_machine_clone_readiness Qt surface mismatch"
}
if ($capabilities.cross_machine_clone_readiness.launcher_options -notcontains "-HandoffFirst") {
    throw "Renderer cross_machine_clone_readiness missing HandoffFirst launcher option"
}
if ($capabilities.cross_machine_clone_readiness.handoff_first_command -notlike "*run_qt_panel.ps1 -HandoffFirst") {
    throw "Renderer cross_machine_clone_readiness handoff-first command mismatch"
}
if ($capabilities.profile_ui_state_replay.qt_inspector_action_ids -notcontains "cursor_geo") {
    throw "Renderer profile_ui_state_replay Cursor inspector action missing"
}
if ($capabilities.profile_ui_state_replay.qt_inspector_action_labels -notcontains "Inspect: Clone ready") {
    throw "Renderer profile_ui_state_replay Clone inspector label missing"
}
if ($capabilities.profile_launch_readiness.schema -ne "rrkal_displaytools.profile_launch_readiness.v1") {
    throw "Renderer profile_launch_readiness schema missing or invalid"
}
if ($capabilities.profile_launch_readiness.readiness -ne "ready") {
    throw "Renderer profile_launch_readiness should be ready"
}
if ([int]$capabilities.profile_launch_readiness.ready_check_count -lt 7) {
    throw "Renderer profile_launch_readiness ready check count missing"
}
if ($capabilities.profile_launch_readiness_ui.schema -ne "rrkal_displaytools.profile_launch_readiness_ui.v1") {
    throw "Renderer profile_launch_readiness_ui schema missing or invalid"
}
if ($capabilities.profile_launch_readiness_ui.readiness -ne "ready") {
    throw "Renderer profile_launch_readiness_ui should be ready"
}
if ($capabilities.layer_visual_presets.schema -ne "rrkal_displaytools.layer_visual_presets.v1") {
    throw "Renderer layer_visual_presets schema missing or invalid"
}
if ($capabilities.layer_visual_presets.preset_ids -notcontains "boundary_focus") {
    throw "Renderer layer_visual_presets missing boundary preset"
}
if ($capabilities.layer_visual_presets.respects_layer_locks -ne $true) {
    throw "Renderer layer_visual_presets must preserve locked layers"
}
if ($capabilities.layer_visual_preset_runtime_feedback.schema -ne "rrkal_displaytools.layer_visual_preset_runtime_feedback.v1") {
    throw "Renderer layer_visual_preset_runtime_feedback schema missing or invalid"
}
if ($capabilities.layer_visual_preset_runtime_feedback.ack_file -ne "state/renderer_layer_runtime_ack.json") {
    throw "Renderer layer_visual_preset_runtime_feedback ack file mismatch"
}
if ($capabilities.hydrology_lod_readiness.schema -ne "rrkal_displaytools.hydrology_lod_readiness.v1") {
    throw "Renderer hydrology_lod_readiness schema missing or invalid"
}
if ($capabilities.hydrology_lod_readiness.stable_renderer_targets -notcontains "rivers") {
    throw "Renderer hydrology_lod_readiness missing rivers renderer target"
}
if ($capabilities.hydrology_lod_readiness.lod_hook_status -ne "contract_ready") {
    throw "Renderer hydrology_lod_readiness LOD hook not contract-ready"
}
if ($capabilities.hydrology_lod_runtime_evidence.schema -ne "rrkal_displaytools.hydrology_lod_runtime_evidence.v1") {
    throw "Renderer hydrology_lod_runtime_evidence schema missing or invalid"
}
if ($capabilities.hydrology_lod_runtime_evidence.qt_surface -ne "Layers dock Hydrology runtime evidence label") {
    throw "Renderer hydrology_lod_runtime_evidence qt surface mismatch"
}
if ($capabilities.ocean_material_control_port.schema -ne "rrkal_displaytools.ocean_material_control_port.v1") {
    throw "Renderer ocean_material_control_port schema missing or invalid"
}
if ($capabilities.ocean_material_control_port.taichi_uniforms -notcontains "wave_strength") {
    throw "Renderer ocean_material_control_port Taichi uniforms missing"
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
if ($capabilities.layer_capability_matrix.runtime_interaction_context.schema -ne "rrkal_displaytools.layer_runtime_interaction_context.v1") {
    throw "Renderer layer_capability_matrix runtime interaction context schema missing or invalid"
}
if ($capabilities.layer_capability_matrix.territory_identity_context.schema -ne "rrkal_displaytools.layer_territory_identity_context.v1") {
    throw "Renderer layer_capability_matrix territory identity context schema missing or invalid"
}
if ($capabilities.layer_capability_matrix.authoritative_identity_source.schema -ne "rrkal_displaytools.layer_authoritative_identity_source.v1") {
    throw "Renderer layer_capability_matrix authoritative identity source schema missing or invalid"
}
if ($capabilities.layer_capability_matrix.renderer_diagnostics_summary.schema -ne "rrkal_displaytools.layer_renderer_diagnostics_summary.v1") {
    throw "Renderer layer_capability_matrix renderer diagnostics summary schema missing or invalid"
}
if ($capabilities.layer_capability_matrix.renderer_diagnostics_detail.schema -ne "rrkal_displaytools.layer_renderer_diagnostics_detail.v1") {
    throw "Renderer layer_capability_matrix renderer diagnostics detail schema missing or invalid"
}
if ($capabilities.layer_capability_matrix.renderer_diagnostics_remediation.schema -ne "rrkal_displaytools.layer_renderer_diagnostics_remediation.v1") {
    throw "Renderer layer_capability_matrix renderer diagnostics remediation schema missing or invalid"
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
if ($capabilities.ui_handoff_contracts.contracts -notcontains "cursor_geodesy_readout") {
    throw "Renderer ui_handoff_contracts cursor_geodesy_readout contract missing"
}
if ($capabilities.ui_handoff_contracts.contracts -notcontains "pin_overlay") {
    throw "Renderer ui_handoff_contracts pin_overlay contract missing"
}
if ($capabilities.ui_handoff_contracts.contracts -notcontains "boundary_emphasis_control") {
    throw "Renderer ui_handoff_contracts boundary_emphasis_control contract missing"
}
if ($capabilities.ui_handoff_contracts.contracts -notcontains "boundary_highlight.ack_history") {
    throw "Renderer ui_handoff_contracts boundary ack history contract missing"
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
if ($capabilities.boundary_highlight.identity_status_applied -notcontains "closed_ring_fill_preview") {
    throw "Renderer boundary_highlight identity_status applied fill preview missing"
}
if ($capabilities.boundary_highlight.identity_status_pending -notcontains "open_line_area_inference") {
    throw "Renderer boundary_highlight identity_status open-line pending marker missing"
}
if ($capabilities.boundary_highlight.ack_history_contract -ne "boundary_highlight_ack_history") {
    throw "Renderer boundary_highlight ack history contract missing"
}
if ($capabilities.boundary_highlight.ack_history_provenance_field -ne "boundary_highlight_ack_history") {
    throw "Renderer boundary_highlight ack history provenance field missing"
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
if ($closedLoopIds -notcontains "pin_boundary_ui_handoff") {
    throw "Closed-loop pin_boundary_ui_handoff missing"
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
if ($handoff.layer_operator_shortcuts.launch_packet_schema -ne "rrkal_displaytools.layer_operator_shortcuts.v1") {
    throw "Handoff inspection layer_operator_shortcuts launch schema missing or invalid"
}
if ($handoff.layer_operator_shortcuts.renderer_capabilities_schema -ne "rrkal_displaytools.layer_operator_shortcuts.v1") {
    throw "Handoff inspection layer_operator_shortcuts renderer schema missing or invalid"
}
if ([int]$handoff.layer_operator_shortcuts.keyboard_shortcut_count -lt 7) {
    throw "Handoff inspection layer_operator_shortcuts keyboard shortcut count missing"
}
if ($handoff.launch_packet_contracts.layer_operator_groups -ne "rrkal_displaytools.layer_operator_groups.v1") {
    throw "Handoff inspection layer_operator_groups launch contract missing or invalid"
}
if ($handoff.layer_operator_groups.launch_packet_schema -ne "rrkal_displaytools.layer_operator_groups.v1") {
    throw "Handoff inspection layer_operator_groups launch schema missing or invalid"
}
if ($handoff.layer_operator_groups.renderer_capabilities_schema -ne "rrkal_displaytools.layer_operator_groups.v1") {
    throw "Handoff inspection layer_operator_groups renderer schema missing or invalid"
}
if ([int]$handoff.layer_operator_groups.complete_group_count -lt 5) {
    throw "Handoff inspection layer_operator_groups incomplete"
}
if ($handoff.launch_packet_contracts.layer_selection_tool -ne "rrkal_displaytools.layer_selection_tool.v1") {
    throw "Handoff inspection layer_selection_tool launch contract missing or invalid"
}
if ($handoff.launch_packet_contracts.layer_research_workflow -ne "rrkal_displaytools.layer_research_workflow.v1") {
    throw "Handoff inspection layer_research_workflow launch contract missing or invalid"
}
if ($handoff.layer_selection_tool.launch_packet_schema -ne "rrkal_displaytools.layer_selection_tool.v1") {
    throw "Handoff inspection layer_selection_tool launch schema missing or invalid"
}
if ($handoff.layer_selection_tool.renderer_capabilities_schema -ne "rrkal_displaytools.layer_selection_tool.v1") {
    throw "Handoff inspection layer_selection_tool renderer schema missing or invalid"
}
if ($handoff.layer_selection_tool.pick_state_file -ne "state/renderer_layer_pick_state.json") {
    throw "Handoff inspection layer_selection_tool pick state file mismatch"
}
if ($handoff.layer_selection_tool.brush_mask_scope -ne "excluded") {
    throw "Handoff inspection layer_selection_tool must exclude brush/mask scope"
}
if ($handoff.layer_research_workflow.launch_packet_schema -ne "rrkal_displaytools.layer_research_workflow.v1") {
    throw "Handoff inspection layer_research_workflow launch schema missing or invalid"
}
if ($handoff.layer_research_workflow.renderer_capabilities_schema -ne "rrkal_displaytools.layer_research_workflow.v1") {
    throw "Handoff inspection layer_research_workflow renderer schema missing or invalid"
}
if ($handoff.layer_research_workflow.qt_surface -ne "Layers dock research workflow label") {
    throw "Handoff inspection layer_research_workflow Qt surface mismatch"
}
if ($handoff.launch_packet_contracts.cursor_geodesy_readout -ne "rrkal_displaytools.cursor_geodesy_readout.v1") {
    throw "Handoff inspection cursor_geodesy_readout launch contract missing or invalid"
}
if ($handoff.cursor_geodesy_readout.launch_packet_schema -ne "rrkal_displaytools.cursor_geodesy_readout.v1") {
    throw "Handoff inspection cursor_geodesy_readout launch schema missing or invalid"
}
if ($handoff.cursor_geodesy_readout.renderer_capabilities_schema -ne "rrkal_displaytools.cursor_geodesy_readout.v1") {
    throw "Handoff inspection cursor_geodesy_readout renderer schema missing or invalid"
}
if ($handoff.cursor_geodesy_readout.event_position_guard -ne "QMouseEvent.position with QMouseEvent.pos fallback") {
    throw "Handoff inspection cursor_geodesy_readout event guard missing"
}
if ($handoff.cursor_geodesy_readout.backend_raycast_status -ne "renderer_globe_intersection_contract_ready") {
    throw "Handoff inspection cursor_geodesy_readout backend raycast status mismatch"
}
if ($handoff.cursor_geodesy_readout.renderer_raycast_helper -ne "cursor_geodesy.viewport_sphere_raycast") {
    throw "Handoff inspection cursor_geodesy_readout raycast helper missing"
}
if ($handoff.cursor_geodesy_readout.runtime_bridge_status -ne "renderer_mouse_state_wired") {
    throw "Handoff inspection cursor_geodesy_readout runtime bridge status mismatch"
}
if ($handoff.cursor_geodesy_readout.renderer_raycast_state_file -ne "state/renderer_cursor_geodesy_state.json") {
    throw "Handoff inspection cursor_geodesy_readout state file mismatch"
}
if ($handoff.cursor_geodesy_readout.renderer_raycast_ack_file -ne "state/renderer_cursor_geodesy_ack.json") {
    throw "Handoff inspection cursor_geodesy_readout ack file mismatch"
}
if ($handoff.cursor_geodesy_readout.renderer_controls -notcontains "cursor-geodesy-ack-file") {
    throw "Handoff inspection cursor_geodesy_readout ack-file renderer control missing"
}
if ($handoff.launch_packet_contracts.pin_overlay -ne "rrkal_displaytools.pin_projection.v1") {
    throw "Handoff inspection pin_overlay launch contract missing or invalid"
}
if ($handoff.active_layer_diagnostics.launch_packet_schema -ne "rrkal_displaytools.active_layer_diagnostics.v1") {
    throw "Handoff inspection active_layer_diagnostics launch schema missing or invalid"
}
if ($handoff.active_layer_diagnostics.layer_pick_screen_position_field -ne "screen_position") {
    throw "Handoff inspection active_layer_diagnostics screen position field missing"
}
if ($handoff.active_layer_diagnostics.renderer_runtime_fields -notcontains "screen_position") {
    throw "Handoff inspection active_layer_diagnostics renderer screen_position field missing"
}
if ($handoff.pin_overlay.launch_packet_schema -ne "rrkal_displaytools.pin_projection.v1") {
    throw "Handoff inspection pin_overlay launch schema missing or invalid"
}
if ($handoff.pin_overlay.renderer_capabilities_schema -ne "rrkal_displaytools.pin_projection.v1") {
    throw "Handoff inspection pin_overlay renderer schema missing or invalid"
}
if ($handoff.pin_overlay.renderer_overlay_status -ne "wired_to_pin_overlay_rgba_and_frame_composition") {
    throw "Handoff inspection pin_overlay renderer overlay status mismatch"
}
if ($handoff.pin_overlay.horizon_control -ne "--pin-horizon-eps / PIN_HORIZON_EPS") {
    throw "Handoff inspection pin_overlay horizon control missing"
}
if ($handoff.pin_overlay.cursor_fill_priority -ne "renderer_cursor_geodesy_state_then_ui_estimate") {
    throw "Handoff inspection pin_overlay cursor fill priority mismatch"
}
if ($handoff.pin_overlay.cursor_fill_sources -notcontains "qt_canvas_estimate") {
    throw "Handoff inspection pin_overlay cursor fill fallback missing"
}
if ($handoff.pin_overlay.coordinate_source_fields -notcontains "coordinate_source") {
    throw "Handoff inspection pin_overlay coordinate source field missing"
}
if ($handoff.pin_overlay.coordinate_source_values -notcontains "renderer_globe_raycast") {
    throw "Handoff inspection pin_overlay renderer coordinate source missing"
}
if ($handoff.pin_overlay.qt_ui_affordances -notcontains "projection_rotation_occlusion_note") {
    throw "Handoff inspection pin_overlay projection note affordance missing"
}
if ($handoff.pin_overlay.pin_list_summary_format -ne "source=<coordinate_source_label>") {
    throw "Handoff inspection pin_overlay list summary format missing"
}
if ($handoff.launch_packet_contracts.boundary_emphasis_control -ne "rrkal_displaytools.boundary_emphasis_control.v1") {
    throw "Handoff inspection boundary_emphasis_control launch contract missing or invalid"
}
if ($handoff.boundary_emphasis_control.launch_packet_schema -ne "rrkal_displaytools.boundary_emphasis_control.v1") {
    throw "Handoff inspection boundary_emphasis_control launch schema missing or invalid"
}
if ($handoff.boundary_emphasis_control.renderer_capabilities_schema -ne "rrkal_displaytools.boundary_emphasis_control.v1") {
    throw "Handoff inspection boundary_emphasis_control renderer schema missing or invalid"
}
if ([int]$handoff.boundary_emphasis_control.control_count -lt 7) {
    throw "Handoff inspection boundary_emphasis_control controls missing"
}
if ($handoff.boundary_emphasis_control.row_double_click_binding -ne "ready") {
    throw "Handoff inspection boundary_emphasis_control row double-click binding missing"
}
if ($handoff.boundary_emphasis_control.row_double_click_layer_keys -notcontains "eez_layer") {
    throw "Handoff inspection boundary_emphasis_control row double-click EEZ layer missing"
}
if ($handoff.boundary_emphasis_control.renderer_hook_status -ne "wired_via_boundary_highlight_mask") {
    throw "Handoff inspection boundary_emphasis_control renderer hook is not wired"
}
if ($handoff.boundary_emphasis_control.renderer_bridge_contract -ne "rrkal_displaytools.boundary_highlight_mask.v1") {
    throw "Handoff inspection boundary_emphasis_control renderer bridge contract missing"
}
if ($handoff.boundary_emphasis_control.renderer_controls_mapped -notcontains "alpha") {
    throw "Handoff inspection boundary_emphasis_control alpha bridge mapping missing"
}
if ($handoff.boundary_emphasis_control.dialog_feedback -notcontains "rgb_swatch") {
    throw "Handoff inspection boundary_emphasis_control RGB swatch feedback missing"
}
if ($handoff.boundary_emphasis_control.value_preview_fields -notcontains "target_alignment") {
    throw "Handoff inspection boundary_emphasis_control target alignment preview missing"
}
if (-not $handoff.boundary_emphasis_control.target_alignment) {
    throw "Handoff inspection boundary_emphasis_control target alignment field missing"
}
if ($handoff.boundary_emphasis_control.qt_surface -ne "Layers dock boundary emphasis dialog") {
    throw "Handoff inspection boundary_emphasis_control Qt surface mismatch"
}
if ($handoff.boundary_highlight.ack_history_contract -ne "boundary_highlight_ack_history") {
    throw "Handoff inspection boundary_highlight ack history contract missing"
}
if ($handoff.boundary_highlight.identity_status_applied -notcontains "maritime_property_key_identity") {
    throw "Handoff inspection boundary_highlight identity applied marker missing"
}
if ($handoff.boundary_highlight.renderer_identity_status_pending -notcontains "authoritative_polygon_territory_identity") {
    throw "Handoff inspection boundary_highlight renderer identity pending marker missing"
}
if ($handoff.boundary_highlight.ack_history_fields -notcontains "updated_at_utc") {
    throw "Handoff inspection boundary_highlight ack history timestamp field missing"
}
if ($handoff.launch_packet_contracts.style_renderer_entries -ne "rrkal_displaytools.style_renderer_entries.v1") {
    throw "Handoff inspection style_renderer_entries launch contract missing or invalid"
}
if ($handoff.style_renderer_entries.launch_packet_schema -ne "rrkal_displaytools.style_renderer_entries.v1") {
    throw "Handoff inspection style_renderer_entries launch schema missing or invalid"
}
if ($handoff.style_renderer_entries.renderer_capabilities_schema -ne "rrkal_displaytools.style_renderer_entries.v1") {
    throw "Handoff inspection style_renderer_entries renderer schema missing or invalid"
}
if ($handoff.style_renderer_entries.entry_ids -notcontains "parchment") {
    throw "Handoff inspection style_renderer_entries missing parchment entry"
}
if ($handoff.style_renderer_entries.entry_ids -notcontains "tactical") {
    throw "Handoff inspection style_renderer_entries missing tactical entry"
}
if ($handoff.launch_packet_contracts.style_profile_renderer_routes -ne "rrkal_displaytools.style_profile_renderer_routes.v1") {
    throw "Handoff inspection style_profile_renderer_routes launch contract missing or invalid"
}
if ($handoff.style_profile_renderer_routes.launch_packet_schema -ne "rrkal_displaytools.style_profile_renderer_routes.v1") {
    throw "Handoff inspection style_profile_renderer_routes launch schema missing or invalid"
}
if ($handoff.style_profile_renderer_routes.renderer_capabilities_schema -ne "rrkal_displaytools.style_profile_renderer_routes.v1") {
    throw "Handoff inspection style_profile_renderer_routes renderer schema missing or invalid"
}
if ($handoff.style_profile_renderer_routes.route_ids -notcontains "tactical") {
    throw "Handoff inspection style_profile_renderer_routes missing tactical route"
}
if ($handoff.launch_packet_contracts.module_boundary_registry -ne "rrkal_displaytools.module_boundary_registry.v1") {
    throw "Handoff inspection module_boundary_registry launch contract missing or invalid"
}
if ($handoff.module_boundary_registry.launch_packet_schema -ne "rrkal_displaytools.module_boundary_registry.v1") {
    throw "Handoff inspection module_boundary_registry launch schema missing or invalid"
}
if ($handoff.module_boundary_registry.renderer_capabilities_schema -ne "rrkal_displaytools.module_boundary_registry.v1") {
    throw "Handoff inspection module_boundary_registry renderer schema missing or invalid"
}
if ($handoff.module_boundary_registry.tk_primary_ui_allowed -ne $false) {
    throw "Handoff inspection module_boundary_registry primary UI boundary invalid"
}
if ($handoff.launch_packet_contracts.cross_machine_clone_readiness -ne "rrkal_displaytools.cross_machine_clone_readiness.v1") {
    throw "Handoff inspection cross_machine_clone_readiness launch contract missing or invalid"
}
if ($handoff.cross_machine_clone_readiness.launch_packet_schema -ne "rrkal_displaytools.cross_machine_clone_readiness.v1") {
    throw "Handoff inspection cross_machine_clone_readiness launch schema missing or invalid"
}
if ($handoff.cross_machine_clone_readiness.renderer_capabilities_schema -ne "rrkal_displaytools.cross_machine_clone_readiness.v1") {
    throw "Handoff inspection cross_machine_clone_readiness renderer schema missing or invalid"
}
if ($handoff.cross_machine_clone_readiness.required_commands -notcontains "scripts/inspect_handoff.ps1") {
    throw "Handoff inspection cross_machine_clone_readiness missing handoff command"
}
if ($handoff.cross_machine_clone_readiness.launcher_options -notcontains "-HandoffFirst") {
    throw "Handoff inspection cross_machine_clone_readiness missing HandoffFirst launcher option"
}
if ($handoff.cross_machine_clone_readiness.handoff_first_command -notlike "*run_qt_panel.ps1 -HandoffFirst") {
    throw "Handoff inspection cross_machine_clone_readiness handoff-first command mismatch"
}
if ($handoff.launch_packet_contracts.profile_launch_readiness -ne "rrkal_displaytools.profile_launch_readiness.v1") {
    throw "Handoff inspection profile_launch_readiness launch contract missing or invalid"
}
if ($handoff.profile_launch_readiness.launch_packet_schema -ne "rrkal_displaytools.profile_launch_readiness.v1") {
    throw "Handoff inspection profile_launch_readiness launch schema missing or invalid"
}
if ($handoff.profile_launch_readiness.renderer_capabilities_schema -ne "rrkal_displaytools.profile_launch_readiness.v1") {
    throw "Handoff inspection profile_launch_readiness renderer schema missing or invalid"
}
if ($handoff.profile_launch_readiness.readiness -ne "ready") {
    throw "Handoff inspection profile_launch_readiness should be ready"
}
if ([int]$handoff.profile_launch_readiness.ready_check_count -lt 7) {
    throw "Handoff inspection profile_launch_readiness ready check count missing"
}
if ($handoff.launch_packet_contracts.profile_launch_readiness_ui -ne "rrkal_displaytools.profile_launch_readiness_ui.v1") {
    throw "Handoff inspection profile_launch_readiness_ui launch contract missing or invalid"
}
if ($handoff.profile_launch_readiness_ui.launch_packet_schema -ne "rrkal_displaytools.profile_launch_readiness_ui.v1") {
    throw "Handoff inspection profile_launch_readiness_ui launch schema missing or invalid"
}
if ($handoff.profile_launch_readiness_ui.renderer_capabilities_schema -ne "rrkal_displaytools.profile_launch_readiness_ui.v1") {
    throw "Handoff inspection profile_launch_readiness_ui renderer schema missing or invalid"
}
if ($handoff.profile_launch_readiness_ui.qt_surface -ne "Layers dock readiness label") {
    throw "Handoff inspection profile_launch_readiness_ui surface mismatch"
}
if ($handoff.launch_packet_contracts.layer_visual_presets -ne "rrkal_displaytools.layer_visual_presets.v1") {
    throw "Handoff inspection layer_visual_presets launch contract missing or invalid"
}
if ($handoff.layer_visual_presets.launch_packet_schema -ne "rrkal_displaytools.layer_visual_presets.v1") {
    throw "Handoff inspection layer_visual_presets launch schema missing or invalid"
}
if ($handoff.layer_visual_presets.renderer_capabilities_schema -ne "rrkal_displaytools.layer_visual_presets.v1") {
    throw "Handoff inspection layer_visual_presets renderer schema missing or invalid"
}
if ($handoff.layer_visual_presets.preset_ids -notcontains "hydrology_focus") {
    throw "Handoff inspection layer_visual_presets missing hydrology preset"
}
if ($handoff.layer_visual_presets.respects_layer_locks -ne $true) {
    throw "Handoff inspection layer_visual_presets must preserve locked layers"
}
if ($handoff.launch_packet_contracts.layer_visual_preset_runtime_feedback -ne "rrkal_displaytools.layer_visual_preset_runtime_feedback.v1") {
    throw "Handoff inspection layer_visual_preset_runtime_feedback launch contract missing or invalid"
}
if ($handoff.layer_visual_preset_runtime_feedback.launch_packet_schema -ne "rrkal_displaytools.layer_visual_preset_runtime_feedback.v1") {
    throw "Handoff inspection layer_visual_preset_runtime_feedback launch schema missing or invalid"
}
if ($handoff.layer_visual_preset_runtime_feedback.renderer_capabilities_schema -ne "rrkal_displaytools.layer_visual_preset_runtime_feedback.v1") {
    throw "Handoff inspection layer_visual_preset_runtime_feedback renderer schema missing or invalid"
}
if ($handoff.layer_visual_preset_runtime_feedback.requires_renderer_ack_for_reproducibility -ne $true) {
    throw "Handoff inspection layer_visual_preset_runtime_feedback must require renderer ack"
}
if ($handoff.launch_packet_contracts.hydrology_lod_readiness -ne "rrkal_displaytools.hydrology_lod_readiness.v1") {
    throw "Handoff inspection hydrology_lod_readiness launch contract missing or invalid"
}
if ($handoff.hydrology_lod_readiness.launch_packet_schema -ne "rrkal_displaytools.hydrology_lod_readiness.v1") {
    throw "Handoff inspection hydrology_lod_readiness launch schema missing or invalid"
}
if ($handoff.hydrology_lod_readiness.renderer_capabilities_schema -ne "rrkal_displaytools.hydrology_lod_readiness.v1") {
    throw "Handoff inspection hydrology_lod_readiness renderer schema missing or invalid"
}
if ([int]$handoff.hydrology_lod_readiness.live_hydrology_layer_count -lt 2) {
    throw "Handoff inspection hydrology_lod_readiness live hydrology layer count missing"
}
if ($handoff.hydrology_lod_readiness.lod_hook_status -ne "contract_ready") {
    throw "Handoff inspection hydrology_lod_readiness LOD hook not contract-ready"
}
if ($handoff.launch_packet_contracts.hydrology_lod_runtime_evidence -ne "rrkal_displaytools.hydrology_lod_runtime_evidence.v1") {
    throw "Handoff inspection hydrology_lod_runtime_evidence launch contract missing or invalid"
}
if ($handoff.hydrology_lod_runtime_evidence.launch_packet_schema -ne "rrkal_displaytools.hydrology_lod_runtime_evidence.v1") {
    throw "Handoff inspection hydrology_lod_runtime_evidence launch schema missing or invalid"
}
if ($handoff.hydrology_lod_runtime_evidence.renderer_capabilities_schema -ne "rrkal_displaytools.hydrology_lod_runtime_evidence.v1") {
    throw "Handoff inspection hydrology_lod_runtime_evidence renderer schema missing or invalid"
}
if ($handoff.hydrology_lod_runtime_evidence.ack_file -ne "state/renderer_layer_runtime_ack.json") {
    throw "Handoff inspection hydrology_lod_runtime_evidence ack file mismatch"
}
if ($handoff.launch_packet_contracts.ocean_material_control_port -ne "rrkal_displaytools.ocean_material_control_port.v1") {
    throw "Handoff inspection ocean_material_control_port launch contract missing or invalid"
}
if ($handoff.ocean_material_control_port.launch_packet_schema -ne "rrkal_displaytools.ocean_material_control_port.v1") {
    throw "Handoff inspection ocean_material_control_port launch schema missing or invalid"
}
if ($handoff.ocean_material_control_port.renderer_capabilities_schema -ne "rrkal_displaytools.ocean_material_control_port.v1") {
    throw "Handoff inspection ocean_material_control_port renderer schema missing or invalid"
}
if ($handoff.ocean_material_control_port.renderer_flags -notcontains "--ocean-foam") {
    throw "Handoff inspection ocean_material_control_port renderer flags missing"
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
if ($handoff.layer_capability_matrix.runtime_interaction_context_schema -ne "rrkal_displaytools.layer_runtime_interaction_context.v1") {
    throw "Handoff inspection layer runtime interaction context schema missing or invalid"
}
if ($handoff.layer_capability_matrix.territory_identity_context_schema -ne "rrkal_displaytools.layer_territory_identity_context.v1") {
    throw "Handoff inspection layer territory identity context schema missing or invalid"
}
if ($handoff.layer_capability_matrix.authoritative_identity_source_schema -ne "rrkal_displaytools.layer_authoritative_identity_source.v1") {
    throw "Handoff inspection layer authoritative identity source schema missing or invalid"
}
if ($handoff.layer_capability_matrix.renderer_diagnostics_summary_schema -ne "rrkal_displaytools.layer_renderer_diagnostics_summary.v1") {
    throw "Handoff inspection layer renderer diagnostics summary schema missing or invalid"
}
if ($handoff.layer_capability_matrix.renderer_diagnostics_detail_schema -ne "rrkal_displaytools.layer_renderer_diagnostics_detail.v1") {
    throw "Handoff inspection layer renderer diagnostics detail schema missing or invalid"
}
if ($handoff.layer_capability_matrix.renderer_diagnostics_remediation_schema -ne "rrkal_displaytools.layer_renderer_diagnostics_remediation.v1") {
    throw "Handoff inspection layer renderer diagnostics remediation schema missing or invalid"
}
if ($handoff.layer_capability_matrix.runtime_status_legend_schema -ne "rrkal_displaytools.layer_runtime_status_legend.v1") {
    throw "Handoff inspection layer runtime status legend schema missing or invalid"
}
if ([int]$handoff.layer_capability_matrix.live_counts.blend -le 0) {
    throw "Handoff inspection layer_capability_matrix blend live count missing"
}
Invoke-CheckedNative py @("-3", "taichi_global_bathymetry.py", "--print-layer-manifest") | Out-Null
Invoke-CheckedNative py @("-3", "rrkal_displaytools_qt_panel.py", "--list-templates") | Out-Null
Invoke-CheckedNative py @("-3", "-c", "from cursor_geodesy import viewport_sphere_raycast, cursor_raycast_state_payload, cursor_raycast_ack_payload; c=viewport_sphere_raycast(50,50,100,100); m=viewport_sphere_raycast(120,120,100,100); s=cursor_raycast_state_payload(50,50,100,100,event='smoke',frame_index=7); a=cursor_raycast_ack_payload('state/renderer_cursor_geodesy_state.json',s); assert c['hit'] and abs(c['latitude']) < 1e-9 and abs(c['longitude']) < 1e-9 and not m['hit'] and s['screen_x']==50.0 and s['frame_index']==7 and a['schema']=='rrkal_displaytools.renderer_cursor_geodesy_ack.v1'") | Out-Null

$qtPanelSource = Get-Content -Raw -Encoding UTF8 rrkal_displaytools_qt_panel.py
if ($qtPanelSource -like "*Boundary emphasis: UI ready, renderer mask hook queued*") {
    throw "Qt boundary emphasis label still reports queued renderer mask hook"
}
if ($qtPanelSource -like "*Renderer mask rasterization is queued for the backend pass*") {
    throw "Qt boundary emphasis dialog still reports queued renderer mask rasterization"
}
if ($qtPanelSource -notlike "*Boundary emphasis preview:*") {
    throw "Qt boundary emphasis preview readout missing"
}
if ($qtPanelSource -notlike "*boundaryEmphasisSwatch*") {
    throw "Qt boundary emphasis RGB swatch missing"
}
if ($qtPanelSource -notlike "*layerActionBadge*") {
    throw "Qt layer action badge missing"
}
if ($qtPanelSource -notlike "*Emphasis*") {
    throw "Qt boundary layer emphasis action label missing"
}
if ($qtPanelSource -notlike "*target_alignment_label*") {
    throw "Qt boundary emphasis target alignment label missing"
}
if ($qtPanelSource -notlike "*Boundary target:*") {
    throw "Qt canvas boundary target summary line missing"
}
if ($qtPanelSource -notlike "*boundary_emphasis_target_alignment*") {
    throw "Qt canvas provenance boundary emphasis target alignment missing"
}
if ($qtPanelSource -notlike "*timeline_keyframe_list_text*") {
    throw "Qt timeline keyframe list formatter missing"
}
if ($qtPanelSource -notlike "*boundary=*") {
    throw "Qt timeline keyframe boundary target summary missing"
}
if ($qtPanelSource -notlike "*Boundary identity:*") {
    throw "Qt canvas boundary identity summary line missing"
}
if ($qtPanelSource -notlike "*applied_text*") {
    throw "Qt boundary identity applied marker summary missing"
}
if ($qtPanelSource -notlike "*Boundary emphasis: UI ready, renderer bridge wired*") {
    throw "Qt boundary emphasis label missing renderer bridge wired status"
}
if ($qtPanelSource -notlike "*refresh_cursor_geodesy_bridge_state*") {
    throw "Qt panel cursor geodesy bridge refresh hook missing"
}
if ($qtPanelSource -notlike "*Renderer cursor geodesy: waiting for state/ack*") {
    throw "Qt panel cursor geodesy bridge label missing"
}
if ($qtPanelSource -notlike "*renderer_cursor_geodesy_state*") {
    throw "Qt panel cursor geodesy provenance payload missing"
}
if ($qtPanelSource -notlike "*renderer_cursor_geodesy_lat_lon*") {
    throw "Qt panel Pin cursor fill does not prefer renderer cursor geodesy"
}
if ($qtPanelSource -notlike "*Pin cursor fill:*") {
    throw "Qt panel Pin cursor fill source status is not visible"
}
if ($qtPanelSource -notlike "*pin_cursor_fill_source_text*") {
    throw "Qt panel Pin cursor fill source helper missing"
}
if ($qtPanelSource -notlike "*pin_cursor_fill_label*") {
    throw "Qt panel Pin cursor fill fixed label missing"
}
if ($qtPanelSource -notlike "*Cursor Fill*") {
    throw "Qt panel Pin cursor fill form row missing"
}
if ($qtPanelSource -notlike "*coordinate_source*") {
    throw "Qt panel Pin coordinate source metadata missing"
}
if ($qtPanelSource -notlike "*source=*") {
    throw "Qt panel Pin list coordinate source summary missing"
}
if ($qtPanelSource -notlike "*Pin projection: renderer rotates geodetic markers with the globe every frame*") {
    throw "Qt panel Pin projection rotation note missing"
}
if ($qtPanelSource -notlike "*back-side pins are hidden by horizon/depth occlusion*") {
    throw "Qt panel Pin projection occlusion note missing"
}
if ($qtPanelSource -notlike "*screen_position*") {
    throw "Qt panel layer pick screen position diagnostics missing"
}
if ($qtPanelSource -notlike "*Layer pick history*") {
    throw "Qt panel layer pick history entry missing"
}
if ($qtPanelSource -notlike "*Boundary ack history*") {
    throw "Qt panel boundary ack history entry missing"
}
if ($qtPanelSource -notlike "*boundary_highlight_ack_history*") {
    throw "Qt panel boundary ack history provenance missing"
}
if ($qtPanelSource -notlike "*layerWorkflowHint*") {
    throw "Qt Layers workflow hint is missing"
}
if ($qtPanelSource -notlike "*click a row to select the active research layer*") {
    throw "Qt Layers workflow row-selection hint is missing"
}
if ($qtPanelSource -notlike "*not authoritative polygon/EEZ resolution*") {
    throw "Qt Layers workflow identity warning hint is missing"
}
if ($qtPanelSource -notlike "*profileUiStateReplay*") {
    throw "Qt profile UI state replay label is missing"
}
if ($qtPanelSource -notlike "*profile_ui_state_replay_packet*") {
    throw "Qt profile UI state replay contract is missing"
}
if ($qtPanelSource -notlike "*show_profile_ui_state_replay*") {
    throw "Qt profile UI state replay JSON action is missing"
}
if ($qtPanelSource -notlike "*Profile replay*") {
    throw "Qt Profile replay action button is missing"
}
if ($qtPanelSource -notlike "*show_ocean_material_control_port*") {
    throw "Qt ocean material control port JSON action is missing"
}
if ($qtPanelSource -notlike "*Ocean port*") {
    throw "Qt Ocean port action button is missing"
}
if ($qtPanelSource -notlike "*show_hydrology_lod_status*") {
    throw "Qt hydrology LOD JSON action is missing"
}
if ($qtPanelSource -notlike "*Hydro LOD*") {
    throw "Qt Hydro LOD action button is missing"
}
if ($qtPanelSource -notlike "*show_style_renderer_routes*") {
    throw "Qt style renderer routes JSON action is missing"
}
if ($qtPanelSource -notlike "*Style routes*") {
    throw "Qt Style routes action button is missing"
}
if ($qtPanelSource -notlike "*show_module_boundary_registry*") {
    throw "Qt module boundary registry JSON action is missing"
}
if ($qtPanelSource -notlike "*Module seams*") {
    throw "Qt Module seams action button is missing"
}
if ($qtPanelSource -notlike "*show_cross_machine_clone_readiness*") {
    throw "Qt cross-machine clone readiness JSON action is missing"
}
if ($qtPanelSource -notlike "*Clone ready*") {
    throw "Qt Clone ready action button is missing"
}
if ($qtPanelSource -notlike "*Inspect portable UI/profile replay coverage JSON*") {
    throw "Qt contract inspector tooltips are missing"
}
if ($qtPanelSource -notlike "*setAccessibleDescription*") {
    throw "Qt contract inspector accessible descriptions are missing"
}
if ($qtPanelSource -notlike "*Pin pick*") {
    throw "Qt Pin pick action button is missing"
}
if ($qtPanelSource -notlike "*Inspect renderer Pin hover/click pick bridge JSON*") {
    throw "Qt Pin pick action tooltip is missing"
}
if ($qtPanelSource -notlike "*Cursor geo*") {
    throw "Qt Cursor geo action button is missing"
}
if ($qtPanelSource -notlike "*show_cursor_geodesy_state*") {
    throw "Qt Cursor geo JSON action is missing"
}
if ($qtPanelSource -notlike "*Inspect mouse cursor latitude/longitude geodesy bridge JSON*") {
    throw "Qt Cursor geo action tooltip is missing"
}
if ($qtPanelSource -notlike "*Boundary JSON*") {
    throw "Qt Boundary JSON action button is missing"
}
if ($qtPanelSource -notlike "*Inspect: Profile replay*") {
    throw "Qt inspector action prefix is missing"
}
if ($qtPanelSource -notlike "*Inspect: Boundary JSON*") {
    throw "Qt Boundary JSON inspector prefix is missing"
}
if ($qtPanelSource -notlike "*show_boundary_state*") {
    throw "Qt Boundary JSON action is missing"
}
if ($qtPanelSource -notlike "*Inspect Boundary emphasis, identity warning and renderer ack JSON*") {
    throw "Qt Boundary JSON action tooltip is missing"
}
if ($qtPanelSource -notlike "*saved_state_groups*") {
    throw "Qt profile UI state replay saved groups are missing"
}
if ($qtPanelSource -notlike "*replay_surfaces*") {
    throw "Qt profile UI state replay surfaces are missing"
}
if ($qtPanelSource -notlike "*Qt Inspect actions*") {
    throw "Qt profile UI state replay Inspect surface is missing"
}
if ($qtPanelSource -notlike "*qt_inspector_action_ids*") {
    throw "Qt profile UI state replay inspector action ids are missing"
}

$rendererSource = Get-Content -Raw -Encoding UTF8 taichi_global_bathymetry.py
if ($rendererSource -notlike "*last_layer_pick_screen*") {
    throw "Renderer layer pick screen position state missing"
}
if ($rendererSource -notlike "*workflow_hint_surface*") {
    throw "Renderer capability layer workflow hint surface missing"
}
if ($rendererSource -notlike "*double-click Boundary/territorial sea/EEZ/high-seas rows*") {
    throw "Renderer capability layer workflow boundary emphasis hint missing"
}
if ($rendererSource -notlike "*profile_ui_state_replay_packet*") {
    throw "Renderer capability profile UI state replay contract missing"
}
if ($rendererSource -notlike "*saved_state_groups*") {
    throw "Renderer capability profile UI state replay saved groups missing"
}
if ($rendererSource -notlike "*replay_surfaces*") {
    throw "Renderer capability profile UI state replay surfaces missing"
}
if ($rendererSource -notlike "*Qt Inspect actions*") {
    throw "Renderer capability profile UI state replay Inspect surface missing"
}
if ($rendererSource -notlike "*qt_inspector_action_ids*") {
    throw "Renderer capability profile UI state replay inspector ids missing"
}

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

# Boundary identity source hint smoke gate
$BoundaryIdentityRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$boundaryIdentityFiles = @(
    "taichi_global_bathymetry.py",
    "rrkal_displaytools_qt_panel.py",
    "scripts\export_launch_packet.py",
    "closed_loop_status.py"
)
foreach ($boundaryIdentityFile in $boundaryIdentityFiles) {
    $boundaryIdentityPath = Join-Path $BoundaryIdentityRoot $boundaryIdentityFile
    $boundaryIdentityText = Get-Content -LiteralPath $boundaryIdentityPath -Raw -Encoding UTF8
    if ($boundaryIdentityText -notmatch 'identity_source_hint') {
        throw "Missing boundary identity source hint in $boundaryIdentityFile"
    }
    if ($boundaryIdentityText -notmatch 'pending_backend_geometry_closure') {
        throw "Missing open-line inference pending marker in $boundaryIdentityFile"
    }
    if ($boundaryIdentityText -notmatch 'identity_source_hint_summary') {
        throw "Missing boundary identity source summary in $boundaryIdentityFile"
    }
}

$qtBoundaryIdentitySource = Get-Content -LiteralPath (Join-Path $BoundaryIdentityRoot "rrkal_displaytools_qt_panel.py") -Raw -Encoding UTF8
if ($qtBoundaryIdentitySource -notmatch 'source_hint=') {
    throw "Qt Boundary identity summary is not visible in Properties/Canvas Preview text"
}
if ($qtBoundaryIdentitySource -notmatch 'boundaryIdentityWarningBadge') {
    throw "Qt Boundary identity warning badge is missing"
}
if ($qtBoundaryIdentitySource -notmatch 'Pending authoritative identity') {
    throw "Qt Boundary identity pending warning text is missing"
}
if ($qtBoundaryIdentitySource -notmatch 'boundary_identity_warning') {
    throw "Qt Canvas Preview boundary identity warning provenance is missing"
}
if ($qtBoundaryIdentitySource -notmatch 'Boundary warning:') {
    throw "Qt Canvas Preview visible boundary warning line is missing"
}

$launchPacketSource = Get-Content -LiteralPath (Join-Path $BoundaryIdentityRoot "scripts\export_launch_packet.py") -Raw -Encoding UTF8
if ($launchPacketSource -notmatch 'boundary_identity_warning') {
    throw "No-GUI launch packet canvas preview boundary identity warning is missing"
}
if ($launchPacketSource -notmatch 'No-GUI launch packet / Qt Canvas Preview / research provenance') {
    throw "No-GUI launch packet boundary warning surface is missing"
}

$handoffInspectorSource = Get-Content -LiteralPath (Join-Path $BoundaryIdentityRoot "scripts\inspect_handoff.ps1") -Raw -Encoding UTF8
if ($handoffInspectorSource -notmatch 'boundary_identity_warning') {
    throw "Handoff inspection boundary identity warning output is missing"
}
if ($handoffInspectorSource -notmatch 'boundary_identity_warning_surface') {
    throw "Handoff inspection boundary identity warning surface output is missing"
}
if ($handoffInspectorSource -notmatch 'workflow_hint') {
    throw "Handoff inspection layer workflow hint output is missing"
}
if ($launchPacketSource -notmatch 'workflow_hint_surface') {
    throw "Launch packet layer workflow hint surface is missing"
}
if ($launchPacketSource -notmatch 'double-click Boundary/territorial sea/EEZ/high-seas rows') {
    throw "Launch packet layer workflow boundary emphasis hint is missing"
}
if ($launchPacketSource -notmatch 'profile_ui_state_replay') {
    throw "Launch packet profile UI state replay contract is missing"
}
if ($launchPacketSource -notmatch 'saved_state_groups') {
    throw "Launch packet profile UI state replay saved groups missing"
}
if ($launchPacketSource -notmatch 'replay_surfaces') {
    throw "Launch packet profile UI state replay surfaces missing"
}
if ($launchPacketSource -notmatch 'Qt Inspect actions') {
    throw "Launch packet profile UI state replay Inspect surface missing"
}
if ($launchPacketSource -notmatch 'qt_inspector_action_ids') {
    throw "Launch packet profile UI state replay inspector ids missing"
}
if ($handoffInspectorSource -notmatch 'profile_ui_state_replay') {
    throw "Handoff inspection profile UI state replay output is missing"
}
if ($handoffInspectorSource -notmatch 'saved_state_groups') {
    throw "Handoff inspection profile UI state replay saved groups output is missing"
}
if ($handoffInspectorSource -notmatch 'replay_surfaces') {
    throw "Handoff inspection profile UI state replay surfaces output is missing"
}

$closedLoopSource = Get-Content -LiteralPath (Join-Path $BoundaryIdentityRoot "closed_loop_status.py") -Raw -Encoding UTF8
if ($closedLoopSource -notmatch 'boundary_identity_warning_handoff') {
    throw "Closed-loop boundary identity warning handoff evidence is missing"
}
if ($closedLoopSource -notmatch 'Closed warning/provenance loop only') {
    throw "Closed-loop boundary identity warning boundary note is missing"
}
if ($closedLoopSource -notmatch 'layer_workflow_hint_handoff') {
    throw "Closed-loop layer workflow hint handoff evidence is missing"
}
if ($closedLoopSource -notmatch 'Closed UI/operator guidance loop only') {
    throw "Closed-loop layer workflow hint boundary note is missing"
}
if ($closedLoopSource -notmatch 'profile_ui_state_replay_handoff') {
    throw "Closed-loop profile UI state replay evidence is missing"
}

$profileSchemaDoc = Get-Content -LiteralPath (Join-Path $BoundaryIdentityRoot "docs\PROFILE_SCHEMA.zh-TW.md") -Raw -Encoding UTF8
if ($profileSchemaDoc -notmatch 'profile_ui_state_replay') {
    throw "Profile schema docs missing profile_ui_state_replay section"
}
if ($profileSchemaDoc -notmatch 'saved_state_groups') {
    throw "Profile schema docs missing profile UI state replay saved groups"
}
if ($profileSchemaDoc -notmatch 'replay_surfaces') {
    throw "Profile schema docs missing profile UI state replay surfaces"
}
if ($profileSchemaDoc -notmatch 'Qt Inspect actions') {
    throw "Profile schema docs missing profile UI state replay Inspect surface"
}
if ($profileSchemaDoc -notmatch 'qt_inspector_action_ids') {
    throw "Profile schema docs missing profile UI state replay inspector action ids"
}

$cloneQuickstartDoc = Get-Content -LiteralPath (Join-Path $BoundaryIdentityRoot "docs\QUICKSTART_CLONE.zh-TW.md") -Raw -Encoding UTF8
if ($cloneQuickstartDoc -notmatch 'Inspect: Clone ready') {
    throw "Clone quickstart missing Qt Inspect Clone ready guidance"
}
if ($cloneQuickstartDoc -notmatch 'Inspect: Boundary JSON') {
    throw "Clone quickstart missing Qt Inspect Boundary JSON guidance"
}

Write-Host "Smoke passed."
