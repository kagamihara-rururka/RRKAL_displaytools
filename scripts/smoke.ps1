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
if ($launchPacket.layer_selection_tool.selection_summary_contract_schema -ne "rrkal_displaytools.layer_selection_summary_contract.v1") {
    throw "Launch packet layer_selection_tool selection summary contract schema missing or invalid"
}
if ($launchPacket.layer_selection_tool.selection_summary_contract.qt_label_object -ne "selectedLayer") {
    throw "Launch packet layer_selection_tool selection summary label object missing or invalid"
}
if ($launchPacket.layer_selection_tool.selection_summary_contract.qt_copy_action -ne "copy_layer_selection_summary") {
    throw "Launch packet layer_selection_tool selection summary copy action missing or invalid"
}
if (-not $launchPacket.layer_selection_tool.selection_summary_contract.portable) {
    throw "Launch packet layer_selection_tool selection summary portability flag missing"
}
if ($launchPacket.layer_selection_affordance.schema -ne "rrkal_displaytools.layer_selection_affordance.v1") {
    throw "Launch packet layer_selection_affordance schema missing or invalid"
}
if ($launchPacket.layer_selection_affordance.qt_label_object -ne "layerSelectionAffordance") {
    throw "Launch packet layer_selection_affordance label object missing"
}
if ($launchPacket.layer_selection_affordance.selected_row_property -ne "selected") {
    throw "Launch packet layer_selection_affordance selected row property mismatch"
}
if ($launchPacket.layer_selection_affordance.focus_aids -notcontains "layerControlFeedbackStrip") {
    throw "Launch packet layer_selection_affordance feedback strip focus aid missing"
}
if ($launchPacket.layer_hover_affordance.schema -ne "rrkal_displaytools.layer_hover_affordance.v1") {
    throw "Launch packet layer_hover_affordance schema missing or invalid"
}
if ($launchPacket.layer_hover_affordance.qt_label_object -ne "layerHoverAffordance") {
    throw "Launch packet layer_hover_affordance label object missing"
}
if ($launchPacket.layer_hover_affordance.event_filter -ne "layer_hover_event_targets") {
    throw "Launch packet layer_hover_affordance event filter mismatch"
}
if ($launchPacket.layer_lock_affordance.schema -ne "rrkal_displaytools.layer_lock_affordance.v1") {
    throw "Launch packet layer_lock_affordance schema missing or invalid"
}
if ($launchPacket.layer_lock_affordance.locked_row_property -ne "locked") {
    throw "Launch packet layer_lock_affordance row property mismatch"
}
if ($launchPacket.layer_lock_affordance.locked_row_stylesheet_selector -ne 'QWidget#layerRow[locked="true"]') {
    throw "Launch packet layer_lock_affordance stylesheet selector mismatch"
}
if ($launchPacket.layer_lock_affordance.visibility_control_disabled_when_locked -ne $true) {
    throw "Launch packet layer_lock_affordance disabled visibility control flag missing"
}
if ($launchPacket.layer_lock_affordance.disabled_controls_when_locked -notcontains "opacity_slider") {
    throw "Launch packet layer_lock_affordance disabled opacity slider missing"
}
if ($launchPacket.layer_lock_affordance.disabled_controls_when_locked -notcontains "blend_combo") {
    throw "Launch packet layer_lock_affordance disabled blend combo missing"
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
if ($launchPacket.layer_research_workflow.research_summary_contract_schema -ne "rrkal_displaytools.research_interaction_summary_contract.v1") {
    throw "Launch packet research interaction summary contract schema missing or invalid"
}
if ($launchPacket.layer_research_workflow.research_summary_contract.qt_copy_action -ne "copy_research_interaction_summary") {
    throw "Launch packet research interaction summary copy action missing or invalid"
}
if ($launchPacket.layer_research_workflow.research_summary_contract.component_contract_fields -notcontains "cursor_geodesy_readout.cursor_summary_contract") {
    throw "Launch packet research interaction summary component contracts incomplete"
}
if (-not $launchPacket.layer_research_workflow.research_summary_contract.portable) {
    throw "Launch packet research interaction summary portability flag missing"
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
if ($launchPacket.boundary_emphasis_control.boundary_summary_contract_schema -ne "rrkal_displaytools.boundary_emphasis_summary_contract.v1") {
    throw "Launch packet boundary_emphasis_control summary contract schema missing or invalid"
}
if ($launchPacket.boundary_emphasis_control.boundary_summary_contract.qt_copy_action -ne "copy_boundary_emphasis_summary") {
    throw "Launch packet boundary_emphasis_control summary copy action missing or invalid"
}
if ($launchPacket.boundary_emphasis_control.boundary_summary_contract.summary_format -notlike "*contrast={contrast}*gamma={gamma}*breathing={breathing_enabled}@{breathing_period_s}s*") {
    throw "Launch packet boundary_emphasis_control summary tuning format missing"
}
if ($launchPacket.boundary_emphasis_control.boundary_summary_contract.summary_parameter_fields -notcontains "breathing_period_s") {
    throw "Launch packet boundary_emphasis_control summary tuning fields missing"
}
if ($launchPacket.boundary_emphasis_control.summary_parameter_fields -notcontains "gamma") {
    throw "Launch packet boundary_emphasis_control portable summary parameter fields missing"
}
if (-not $launchPacket.boundary_emphasis_control.boundary_summary_contract.portable) {
    throw "Launch packet boundary_emphasis_control summary portability flag missing"
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
if ($launchPacket.style_renderer_entries.renderer_entry_contract_schema -ne "rrkal_displaytools.style_renderer_entry_contract.v1") {
    throw "Launch packet style_renderer_entries entry contract schema missing"
}
if ($launchPacket.style_renderer_entries.entries[2].renderer_entry_contract.schema -ne "rrkal_displaytools.style_renderer_entry_contract.v1") {
    throw "Launch packet style renderer entry nested contract missing"
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
if ($launchPacket.style_profile_renderer_routes.renderer_entry_contract_schema -ne "rrkal_displaytools.style_renderer_entry_contract.v1") {
    throw "Launch packet style_profile_renderer_routes entry contract schema missing"
}
if ($launchPacket.style_profile_renderer_routes.style_routes_summary_contract.schema -ne "rrkal_displaytools.style_routes_summary_contract.v1") {
    throw "Launch packet style routes summary contract missing or invalid"
}
if ($launchPacket.style_profile_renderer_routes.style_routes_summary_contract.qt_copy_action -ne "copy_style_routes_summary") {
    throw "Launch packet style routes summary copy action missing"
}
if ($launchPacket.style_profile_renderer_routes.style_routes_summary_contract.summary_format -notlike "*parchment={parchment_command}*tactical={tactical_command}*boundary=RRKAL-owned data/cache*") {
    throw "Launch packet style routes summary format missing required route commands"
}
if ($launchPacket.style_profile_renderer_routes.summary_parameter_fields -notcontains "portable_route_commands") {
    throw "Launch packet style routes summary parameter fields missing"
}
if ($launchPacket.style_profile_renderer_routes.required_route_contract_ids -notcontains "parchment") {
    throw "Launch packet style_profile_renderer_routes missing parchment route contract"
}
if ($launchPacket.style_template_visual_preview.schema -ne "rrkal_displaytools.style_template_visual_preview.v1") {
    throw "Launch packet style_template_visual_preview schema missing or invalid"
}
if ($launchPacket.style_template_visual_preview.status -ne "ready") {
    throw "Launch packet style_template_visual_preview not ready"
}
if ($launchPacket.style_template_visual_preview.preview_ids -notcontains "parchment") {
    throw "Launch packet style_template_visual_preview missing parchment preview"
}
if ($launchPacket.style_template_visual_preview.preview_ids -notcontains "tactical") {
    throw "Launch packet style_template_visual_preview missing tactical preview"
}
if ($launchPacket.style_template_visual_preview.qt_surface -ne "Looks/templates visual preview cards") {
    throw "Launch packet style_template_visual_preview Qt surface mismatch"
}
if ($launchPacket.style_template_visual_preview.qt_interaction -ne "clickable_preview_cards_select_style_profile") {
    throw "Launch packet style_template_visual_preview interaction missing"
}
if ($launchPacket.style_template_visual_preview.card_click_action -ne "apply_style_template_preview_card") {
    throw "Launch packet style_template_visual_preview click action missing"
}
if (-not $launchPacket.style_template_visual_preview.thumbnail_slots_enabled) {
    throw "Launch packet style_template_visual_preview thumbnail slots not enabled"
}
if ($launchPacket.style_template_visual_preview.thumbnail_artifact_dir -ne "state/style_previews") {
    throw "Launch packet style_template_visual_preview thumbnail artifact dir mismatch"
}
if ($launchPacket.style_template_visual_preview.preview_cards[0].thumbnail_path -notlike "state/style_previews/*.png") {
    throw "Launch packet style_template_visual_preview thumbnail path missing"
}
if ($launchPacket.style_template_visual_preview.qt_inspector_action_id -ne "style_thumbnail_slots") {
    throw "Launch packet style_template_visual_preview thumbnail inspector action missing"
}
if ($launchPacket.style_template_visual_preview.qt_inspector_handler -ne "show_style_thumbnail_slots") {
    throw "Launch packet style_template_visual_preview thumbnail inspector handler missing"
}
if ($launchPacket.style_template_visual_preview.thumbnail_icon_loading -ne "qt_loads_existing_png_as_card_icon") {
    throw "Launch packet style_template_visual_preview icon loading contract missing"
}
if ($launchPacket.style_template_visual_preview.preview_cards[0].qt_card_icon_supported -ne $true) {
    throw "Launch packet style_template_visual_preview card icon support missing"
}
if ($launchPacket.style_template_visual_preview.thumbnail_batch_script -ne "scripts/render_style_previews.ps1") {
    throw "Launch packet style_template_visual_preview batch script missing"
}
if ($launchPacket.style_template_visual_preview.thumbnail_batch_command -notcontains "scripts/render_style_previews.ps1") {
    throw "Launch packet style_template_visual_preview batch command missing"
}
if ($launchPacket.style_template_visual_preview.thumbnail_batch_validates -notcontains "metadata_sidecar_schema") {
    throw "Launch packet style_template_visual_preview batch validation metadata missing"
}
if ($launchPacket.style_template_visual_preview.thumbnail_readiness_schema -ne "rrkal_displaytools.style_thumbnail_readiness.v1") {
    throw "Launch packet style_template_visual_preview thumbnail readiness schema missing"
}
if ($launchPacket.style_template_visual_preview.thumbnail_readiness_label_object -ne "styleThumbnailReadiness") {
    throw "Launch packet style_template_visual_preview thumbnail readiness label object missing"
}
if ($launchPacket.style_template_visual_preview.thumbnail_readiness_fields -notcontains "missing_ids") {
    throw "Launch packet style_template_visual_preview thumbnail readiness missing_ids field missing"
}
if ($launchPacket.style_template_visual_preview.thumbnail_readiness_copy_action -ne "copy_style_thumbnail_readiness_summary") {
    throw "Launch packet style_template_visual_preview thumbnail readiness copy action missing"
}
if ($launchPacket.style_template_visual_preview.local_thumbnail_readiness_schema -ne "rrkal_displaytools.local_style_thumbnail_readiness.v1") {
    throw "Launch packet style_template_visual_preview local thumbnail readiness schema missing"
}
if ($launchPacket.style_template_visual_preview.local_thumbnail_readiness_fields -notcontains "slots") {
    throw "Launch packet style_template_visual_preview local thumbnail readiness slots field missing"
}
if ($launchPacket.visual_feature_closure_matrix.schema -ne "rrkal_displaytools.visual_feature_closure_matrix.v1") {
    throw "Launch packet visual feature closure matrix schema missing or invalid"
}
if ($launchPacket.visual_feature_closure_matrix.feature_ids -notcontains "pin_overlay") {
    throw "Launch packet visual feature closure matrix missing Pin evidence"
}
if ($launchPacket.visual_feature_closure_matrix.feature_ids -notcontains "hydrology_lod") {
    throw "Launch packet visual feature closure matrix missing Hydrology evidence"
}
if ($launchPacket.visual_feature_closure_matrix.feature_ids -notcontains "renderer_performance") {
    throw "Launch packet visual feature closure matrix missing renderer performance queue"
}
if ($launchPacket.visual_feature_closure_matrix.smoke_gate -ne "visual_feature_closure_matrix") {
    throw "Launch packet visual feature closure matrix smoke gate mismatch"
}
if ($launchPacket.renderer_output_artifact_contract.schema -ne "rrkal_displaytools.renderer_output_artifact_contract.v1") {
    throw "Launch packet renderer output artifact contract schema missing or invalid"
}
if ($launchPacket.renderer_output_artifact_contract.metadata_sidecar_schema -ne "rrkal_displaytools.renderer_output_metadata.v1") {
    throw "Launch packet renderer output artifact metadata schema missing"
}
if ($launchPacket.renderer_output_artifact_contract.quick_render_smoke_validates -notcontains "preview_frame_png_nonempty") {
    throw "Launch packet renderer output artifact quick smoke preview check missing"
}
if ($launchPacket.renderer_output_artifact_contract.metadata_fields -notcontains "layer_render_plan") {
    throw "Launch packet renderer output artifact metadata fields missing layer render plan"
}
if ($launchPacket.layer_render_plan_performance.schema -ne "rrkal_displaytools.layer_render_plan_performance.v1") {
    throw "Launch packet layer_render_plan_performance schema missing or invalid"
}
if ($launchPacket.layer_render_plan_performance.status -ne "queued_after_module_decoupling") {
    throw "Launch packet layer_render_plan_performance status mismatch"
}
if ([int]$launchPacket.layer_render_plan_performance.post_decoupling_priority -ne 1) {
    throw "Launch packet layer_render_plan_performance priority mismatch"
}
if ($launchPacket.layer_render_plan_performance.stage_order -notcontains "submit_single_taichi_render_pass") {
    throw "Launch packet layer_render_plan_performance single-pass stage missing"
}
if ($launchPacket.layer_render_plan_performance.runtime_optimization_applied -ne $false) {
    throw "Launch packet layer_render_plan_performance must not claim applied runtime optimization"
}
if ($launchPacket.layer_render_plan_performance.runtime_snapshot_schema -ne "rrkal_displaytools.layer_render_plan_runtime_snapshot.v1") {
    throw "Launch packet layer_render_plan_performance runtime snapshot schema missing"
}
if ($launchPacket.layer_render_plan_performance.metadata_sidecar_field -ne "layer_render_plan") {
    throw "Launch packet layer_render_plan_performance metadata sidecar field missing"
}
if ($launchPacket.layer_render_plan_performance.composition_apply_helper -ne "HybridRenderController.apply_layer_render_plan_composition") {
    throw "Launch packet layer_render_plan_performance composition apply helper missing"
}
if ($launchPacket.layer_render_plan_performance.compiled_plan_schema -ne "rrkal_displaytools.compiled_layer_render_plan.v1") {
    throw "Launch packet layer_render_plan_performance compiled plan schema missing"
}
if ($launchPacket.layer_render_plan_performance.compiled_plan_cache_status_field -ne "cache_status") {
    throw "Launch packet layer_render_plan_performance compiled plan cache status field missing"
}
if ($launchPacket.layer_render_plan_performance.cache_diagnostics_schema -ne "rrkal_displaytools.layer_render_plan_cache_diagnostics.v1") {
    throw "Launch packet layer_render_plan_performance cache diagnostics schema missing"
}
if ($launchPacket.layer_render_plan_performance.cache_diagnostics_qt_action -ne "show_layer_render_plan_performance") {
    throw "Launch packet layer_render_plan_performance cache diagnostics Qt action missing"
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
if ($launchPacket.module_boundary_registry.decoupling_boundary_contract.schema -ne "rrkal_displaytools.module_decoupling_boundary_contract.v1") {
    throw "Launch packet module decoupling boundary contract missing or invalid"
}
if ($launchPacket.module_boundary_registry.decoupling_boundary_contract.extraction_order -notcontains "render_core/taichi_globe.py") {
    throw "Launch packet module decoupling boundary missing render core extraction order"
}
if ($launchPacket.module_boundary_registry.decoupling_boundary_contract.rrkal_owns -notcontains "dataset discovery") {
    throw "Launch packet module decoupling boundary missing RRKAL ownership"
}
if ($launchPacket.module_boundary_registry.decoupling_boundary_contract.tk_primary_ui_allowed -ne $false) {
    throw "Launch packet module decoupling boundary must keep Tk out of primary UI"
}
if ($launchPacket.module_boundary_registry.module_boundary_summary_contract.schema -ne "rrkal_displaytools.module_boundary_summary_contract.v1") {
    throw "Launch packet module boundary summary contract missing or invalid"
}
if ($launchPacket.module_boundary_registry.module_boundary_summary_contract.qt_copy_action -ne "copy_module_boundary_summary") {
    throw "Launch packet module boundary summary copy action missing"
}
if ($launchPacket.module_boundary_registry.module_boundary_summary_contract.summary_format -notlike "*first={first_extraction}*tk_primary={tk_primary_ui_allowed}*boundary=RRKAL-owned data/cache*") {
    throw "Launch packet module boundary summary format missing extraction/governance fields"
}
if ($launchPacket.module_boundary_registry.summary_parameter_fields -notcontains "rrkal_owns") {
    throw "Launch packet module boundary summary parameter fields missing"
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
if ($launchPacket.cross_machine_clone_readiness.clone_command -notlike "git clone *RRKAL_displaytools.git") {
    throw "Launch packet cross_machine_clone_readiness clone command missing"
}
if ($launchPacket.cross_machine_clone_readiness.default_branch -ne "main") {
    throw "Launch packet cross_machine_clone_readiness default branch mismatch"
}
if ($launchPacket.cross_machine_clone_readiness.repo_visibility -ne "public") {
    throw "Launch packet cross_machine_clone_readiness repo visibility mismatch"
}
if ($launchPacket.cross_machine_clone_readiness.setup_doc -ne "docs/SETUP_WINDOWS.zh-TW.md") {
    throw "Launch packet cross_machine_clone_readiness setup doc mismatch"
}
if ($launchPacket.cross_machine_clone_readiness.qt_surface -ne "Layers dock cross-machine readiness label") {
    throw "Launch packet cross_machine_clone_readiness Qt surface mismatch"
}
if ($launchPacket.cross_machine_clone_readiness.qt_visible_fields -notcontains "first_run_smoke_command") {
    throw "Launch packet cross_machine_clone_readiness Qt visible first-run smoke field missing"
}
if ($launchPacket.cross_machine_clone_readiness.qt_visible_fields -notcontains "repo_visibility") {
    throw "Launch packet cross_machine_clone_readiness Qt visible repo visibility field missing"
}
if ($launchPacket.cross_machine_clone_readiness.first_run_order -notcontains "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/inspect_handoff.ps1") {
    throw "Launch packet cross_machine_clone_readiness first-run handoff order missing"
}
if ($launchPacket.cross_machine_clone_readiness.launcher_options -notcontains "-HandoffFirst") {
    throw "Launch packet cross_machine_clone_readiness missing HandoffFirst launcher option"
}
if ($launchPacket.cross_machine_clone_readiness.handoff_first_command -notlike "*run_qt_panel.ps1 -HandoffFirst") {
    throw "Launch packet cross_machine_clone_readiness handoff-first command mismatch"
}
if ($launchPacket.cross_machine_clone_readiness.first_run_smoke_command -notlike "*scripts/smoke.ps1") {
    throw "Launch packet cross_machine_clone_readiness first-run smoke command missing"
}
if ($launchPacket.cross_machine_clone_readiness.first_run_handoff_command -notlike "*scripts/inspect_handoff.ps1") {
    throw "Launch packet cross_machine_clone_readiness first-run handoff command missing"
}
if ($launchPacket.cross_machine_clone_readiness.clone_reviewer_summary_contract_schema -ne "rrkal_displaytools.clone_reviewer_summary_contract.v1") {
    throw "Launch packet clone reviewer summary contract schema missing or invalid"
}
if ($launchPacket.cross_machine_clone_readiness.clone_reviewer_summary_contract.qt_copy_action -ne "copy_clone_reviewer_summary") {
    throw "Launch packet clone reviewer summary copy action missing or invalid"
}
if ($launchPacket.cross_machine_clone_readiness.clone_reviewer_summary_contract.component_contract_fields -notcontains "profile_launch_readiness") {
    throw "Launch packet clone reviewer summary component contracts incomplete"
}
if ($launchPacket.cross_machine_clone_readiness.clone_reviewer_summary_contract.summary_format -notlike "*first_smoke*") {
    throw "Launch packet clone reviewer summary format missing first-run smoke"
}
if ($launchPacket.cross_machine_clone_readiness.clone_reviewer_summary_contract.summary_format -notlike "*clone={clone_command}*") {
    throw "Launch packet clone reviewer summary format missing clone command"
}
if (-not $launchPacket.cross_machine_clone_readiness.clone_reviewer_summary_contract.portable) {
    throw "Launch packet clone reviewer summary portability flag missing"
}
if ($launchPacket.profile_ui_state_replay.qt_inspector_action_ids -notcontains "boundary_json") {
    throw "Launch packet profile_ui_state_replay Boundary inspector action missing"
}
if ($launchPacket.profile_ui_state_replay.qt_inspector_action_ids -notcontains "clone_summary") {
    throw "Launch packet profile_ui_state_replay clone summary action missing"
}
if ($launchPacket.profile_ui_state_replay.qt_inspector_action_ids -notcontains "renderer_thumbnail") {
    throw "Launch packet profile_ui_state_replay Renderer thumbnail inspector action missing"
}
if ($launchPacket.profile_ui_state_replay.qt_inspector_action_ids -notcontains "visual_readiness") {
    throw "Launch packet profile_ui_state_replay Visual readiness inspector action missing"
}
if ($launchPacket.profile_ui_state_replay.qt_inspector_action_ids -notcontains "live_preview") {
    throw "Launch packet profile_ui_state_replay Live preview inspector action missing"
}
if ([int]$launchPacket.profile_ui_state_replay.qt_inspector_action_count -lt 19) {
    throw "Launch packet profile_ui_state_replay inspector action count missing"
}
if ($launchPacket.profile_ui_state_replay.qt_inspector_action_ids -notcontains "canvas_state") {
    throw "Launch packet profile_ui_state_replay Canvas state inspector action missing"
}
if ($launchPacket.profile_ui_state_replay.qt_inspector_action_ids -notcontains "timeline") {
    throw "Launch packet profile_ui_state_replay Timeline inspector action missing"
}
if ($launchPacket.profile_ui_state_replay.qt_inspector_action_ids -notcontains "layer_matrix") {
    throw "Launch packet profile_ui_state_replay layer matrix inspector action missing"
}
if ($launchPacket.profile_ui_state_replay.qt_inspector_action_ids -notcontains "layer_runtime") {
    throw "Launch packet profile_ui_state_replay layer runtime inspector action missing"
}
if ($launchPacket.profile_ui_state_replay.qt_inspector_action_ids -notcontains "selection_state") {
    throw "Launch packet profile_ui_state_replay selection state inspector action missing"
}
if ($launchPacket.profile_ui_state_replay.qt_inspector_action_ids -notcontains "layer_ops") {
    throw "Launch packet profile_ui_state_replay layer ops inspector action missing"
}
if ([int]$launchPacket.profile_ui_state_replay.qt_inspector_group_count -lt 4) {
    throw "Launch packet profile_ui_state_replay inspector group count missing"
}
if ($launchPacket.profile_ui_state_replay.qt_inspector_action_groups.id -notcontains "research_interaction") {
    throw "Launch packet profile_ui_state_replay research interaction group missing"
}
if ($launchPacket.layer_operation_feedback.schema -ne "rrkal_displaytools.layer_operation_feedback.v1") {
    throw "Launch packet layer_operation_feedback schema missing or invalid"
}
if ($launchPacket.layer_control_feedback_strip.schema -ne "rrkal_displaytools.layer_control_feedback_strip.v1") {
    throw "Launch packet layer_control_feedback_strip schema missing or invalid"
}
if ($launchPacket.layer_control_feedback_strip.qt_label_object -ne "layerControlFeedbackStrip") {
    throw "Launch packet layer_control_feedback_strip label object missing"
}
if ($launchPacket.layer_control_feedback_strip.visible_fields -notcontains "opacity") {
    throw "Launch packet layer_control_feedback_strip opacity field missing"
}
if ($launchPacket.layer_control_feedback_strip.visible_fields -notcontains "renderer_sync") {
    throw "Launch packet layer_control_feedback_strip renderer sync field missing"
}
if ($launchPacket.profile_ui_state_replay.qt_inspector_action_groups.id -notcontains "visual_review") {
    throw "Launch packet profile_ui_state_replay visual review group missing"
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
if ($launchPacket.profile_launch_readiness.launch_reviewer_summary_contract_schema -ne "rrkal_displaytools.launch_reviewer_summary_contract.v1") {
    throw "Launch packet launch reviewer summary contract schema missing or invalid"
}
if ($launchPacket.profile_launch_readiness.launch_reviewer_summary_contract.qt_copy_action -ne "copy_launch_reviewer_summary") {
    throw "Launch packet launch reviewer summary copy action missing or invalid"
}
if ($launchPacket.profile_launch_readiness.launch_reviewer_summary_contract.component_contract_fields -notcontains "portable_command") {
    throw "Launch packet launch reviewer summary component contracts incomplete"
}
if (-not $launchPacket.profile_launch_readiness.launch_reviewer_summary_contract.portable) {
    throw "Launch packet launch reviewer summary portability flag missing"
}
if ($launchPacket.profile_ui_state_replay.qt_inspector_action_ids -notcontains "launch_summary") {
    throw "Launch packet profile_ui_state_replay launch summary action missing"
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
if ($launchPacket.reviewer_packet_export.schema -ne "rrkal_displaytools.reviewer_packet_export.v1") {
    throw "Launch packet reviewer_packet_export schema missing or invalid"
}
if ($launchPacket.reviewer_packet_export.reviewer_packet_schema -ne "rrkal_displaytools.reviewer_packet.v1") {
    throw "Launch packet reviewer packet schema missing or invalid"
}
if ($launchPacket.reviewer_packet_export.qt_action -ne "export_reviewer_packet_dialog") {
    throw "Launch packet reviewer packet Qt action missing or invalid"
}
if ($launchPacket.reviewer_packet_export.included_summary_fields -notcontains "launch_reviewer_summary") {
    throw "Launch packet reviewer packet launch summary field missing"
}
if ($launchPacket.reviewer_packet_export.included_summary_fields -notcontains "hydrology_lod_summary") {
    throw "Launch packet reviewer packet hydrology summary field missing"
}
if ($launchPacket.reviewer_packet_export.included_summary_fields -notcontains "ocean_material_summary") {
    throw "Launch packet reviewer packet ocean summary field missing"
}
if ($launchPacket.reviewer_packet_export.included_summary_fields -notcontains "style_routes_summary") {
    throw "Launch packet reviewer packet style routes summary field missing"
}
if ($launchPacket.reviewer_packet_export.included_summary_fields -notcontains "module_boundary_summary") {
    throw "Launch packet reviewer packet module boundary summary field missing"
}
if ($launchPacket.reviewer_packet_export.included_packet_fields -notcontains "launch_packet_snapshot") {
    throw "Launch packet reviewer packet snapshot field missing"
}
if ($launchPacket.reviewer_packet_export.included_packet_fields -notcontains "hydrology_lod_readiness") {
    throw "Launch packet reviewer packet hydrology readiness packet field missing"
}
if ($launchPacket.reviewer_packet_export.included_packet_fields -notcontains "hydrology_lod_runtime_evidence") {
    throw "Launch packet reviewer packet hydrology runtime evidence packet field missing"
}
if ($launchPacket.reviewer_packet_export.included_packet_fields -notcontains "ocean_material_control_port") {
    throw "Launch packet reviewer packet ocean material packet field missing"
}
if ($launchPacket.reviewer_packet_export.included_packet_fields -notcontains "style_profile_renderer_routes") {
    throw "Launch packet reviewer packet style routes packet field missing"
}
if ($launchPacket.reviewer_packet_export.included_packet_fields -notcontains "module_boundary_registry") {
    throw "Launch packet reviewer packet module boundary packet field missing"
}
if ($launchPacket.reviewer_packet_export.included_packet_fields -notcontains "layer_render_plan_performance") {
    throw "Launch packet reviewer packet render plan performance packet field missing"
}
if (-not $launchPacket.reviewer_packet_export.portable) {
    throw "Launch packet reviewer packet portability flag missing"
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
if ($launchPacket.hydrology_lod_readiness.hydrology_lod_summary_contract.schema -ne "rrkal_displaytools.hydrology_lod_summary_contract.v1") {
    throw "Launch packet hydrology_lod summary contract missing or invalid"
}
if ($launchPacket.hydrology_lod_readiness.hydrology_lod_summary_contract.qt_copy_action -ne "copy_hydrology_lod_summary") {
    throw "Launch packet hydrology_lod summary copy action missing"
}
if ($launchPacket.hydrology_lod_readiness.hydrology_lod_summary_contract.summary_format -notlike "*readiness={readiness}*hits={hydrology_runtime_hit_count}*pick_state={pick_state_file}*") {
    throw "Launch packet hydrology_lod summary format missing runtime handoff fields"
}
if ($launchPacket.hydrology_lod_readiness.summary_parameter_fields -notcontains "ack_file") {
    throw "Launch packet hydrology_lod summary parameter fields missing"
}
if ($launchPacket.hydrology_lod_readiness.renderer_apply_contract.schema -ne "rrkal_displaytools.hydrology_lod_renderer_apply_contract.v1") {
    throw "Launch packet hydrology_lod renderer apply contract missing or invalid"
}
if ($launchPacket.hydrology_lod_readiness.renderer_apply_contract.runtime_state_file -ne "state/renderer_layer_runtime_state.json") {
    throw "Launch packet hydrology_lod renderer apply runtime state file mismatch"
}
if ($launchPacket.hydrology_lod_readiness.renderer_apply_contract.runtime_ack_file -ne "state/renderer_layer_runtime_ack.json") {
    throw "Launch packet hydrology_lod renderer apply runtime ack file mismatch"
}
if ($launchPacket.hydrology_lod_readiness.renderer_apply_contract.renderer_targets -notcontains "rivers") {
    throw "Launch packet hydrology_lod renderer apply contract missing rivers target"
}
if (-not $launchPacket.hydrology_lod_readiness.renderer_apply_contract.portable) {
    throw "Launch packet hydrology_lod renderer apply contract is not portable"
}
if ($launchPacket.hydrology_lod_runtime_evidence.schema -ne "rrkal_displaytools.hydrology_lod_runtime_evidence.v1") {
    throw "Launch packet hydrology_lod_runtime_evidence schema missing or invalid"
}
if ($launchPacket.hydrology_lod_runtime_evidence.renderer_apply_contract_schema -ne "rrkal_displaytools.hydrology_lod_renderer_apply_contract.v1") {
    throw "Launch packet hydrology_lod_runtime_evidence renderer apply contract schema missing"
}
if ($launchPacket.hydrology_lod_runtime_evidence.runtime_state_file -ne "state/renderer_layer_runtime_state.json") {
    throw "Launch packet hydrology_lod_runtime_evidence runtime state file mismatch"
}
if ($launchPacket.hydrology_lod_runtime_evidence.ack_file -ne "state/renderer_layer_runtime_ack.json") {
    throw "Launch packet hydrology_lod_runtime_evidence ack file mismatch"
}
if ($launchPacket.hydrology_lod_runtime_evidence.pick_state_file -ne "state/renderer_layer_pick_state.json") {
    throw "Launch packet hydrology_lod_runtime_evidence pick state file mismatch"
}
if ($launchPacket.hydrology_lod_runtime_evidence.summary_runtime_fields -notcontains "pick_matches_hydrology") {
    throw "Launch packet hydrology_lod_runtime_evidence summary runtime fields missing"
}
if ($launchPacket.ocean_material_control_port.schema -ne "rrkal_displaytools.ocean_material_control_port.v1") {
    throw "Launch packet ocean_material_control_port schema missing or invalid"
}
if ($launchPacket.ocean_material_control_port.renderer_flags -notcontains "--ocean-wave-strength") {
    throw "Launch packet ocean_material_control_port missing wave flag"
}
if ($launchPacket.ocean_material_control_port.qt_control_panel.schema -ne "rrkal_displaytools.taichi_ocean_3d_control_panel.v1") {
    throw "Launch packet Taichi ocean 3D control panel schema missing or invalid"
}
if ($launchPacket.ocean_material_control_port.qt_control_panel.qt_dialog_action -ne "open_taichi_ocean_3d_controls") {
    throw "Launch packet Taichi ocean 3D control panel dialog action missing"
}
if ($launchPacket.ocean_material_control_port.qt_control_panel.render_pipeline_followup -ne "post_decoupling_precompute_layer_render_plan_then_single_render_pass") {
    throw "Launch packet Taichi ocean 3D control panel performance followup missing"
}
if ($launchPacket.ocean_material_control_port.qt_control_panel.control_board_label_object -ne "ocean3DControlBoardStrip") {
    throw "Launch packet Taichi ocean 3D control board strip missing"
}
if ($launchPacket.ocean_material_control_port.qt_control_panel.control_board_button_object -ne "ocean3DControlBoardButton") {
    throw "Launch packet Taichi ocean 3D control board button missing"
}
if ($launchPacket.ocean_material_control_port.qt_control_panel.control_board_default_visible -ne $true) {
    throw "Launch packet Taichi ocean 3D control board visibility flag missing"
}
if ($launchPacket.ocean_material_control_port.ocean_material_summary_contract.schema -ne "rrkal_displaytools.ocean_material_summary_contract.v1") {
    throw "Launch packet ocean material summary contract missing or invalid"
}
if ($launchPacket.ocean_material_control_port.ocean_material_summary_contract.qt_copy_action -ne "copy_ocean_material_summary") {
    throw "Launch packet ocean material summary copy action missing"
}
if ($launchPacket.ocean_material_control_port.ocean_material_summary_contract.summary_format -notlike "*wave={wave_strength}*sea_state={sea_state_status}*governance=RRKAL-owned provider/cache*") {
    throw "Launch packet ocean material summary format missing handoff fields"
}
if ($launchPacket.ocean_material_control_port.summary_parameter_fields -notcontains "sea_state_scalar_sample_schema") {
    throw "Launch packet ocean material summary parameter fields missing"
}
if ($launchPacket.ocean_material_control_port.renderer_apply_contract.schema -ne "rrkal_displaytools.ocean_material_renderer_apply_contract.v1") {
    throw "Launch packet ocean material renderer apply contract missing or invalid"
}
if ($launchPacket.ocean_material_control_port.renderer_apply_contract.status -ne "startup_cli_and_timeline_ready") {
    throw "Launch packet ocean material renderer apply status mismatch"
}
if ($launchPacket.ocean_material_control_port.renderer_apply_contract.taichi_uniforms -notcontains "foam") {
    throw "Launch packet ocean material renderer apply uniforms missing foam"
}
if (-not $launchPacket.ocean_material_control_port.renderer_apply_contract.portable) {
    throw "Launch packet ocean material renderer apply contract is not portable"
}
if ($launchPacket.ocean_material_control_port.sea_state_port.normalized_fields -notcontains "wave_strength") {
    throw "Launch packet ocean_material_control_port sea-state normalized fields missing"
}
if ($launchPacket.ocean_material_control_port.sea_state_port.scalar_sample_contract.schema -ne "rrkal_displaytools.sea_state_scalar_sample.v1") {
    throw "Launch packet ocean material sea-state scalar sample contract missing"
}
if ($launchPacket.ocean_material_control_port.sea_state_port.scalar_sample_contract.displaytools_role -ne "consume_normalized_scalars_only") {
    throw "Launch packet ocean material sea-state displaytools role mismatch"
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
if ($launchPacket.cursor_geodesy_readout.cursor_summary_contract_schema -ne "rrkal_displaytools.cursor_geodesy_summary_contract.v1") {
    throw "Launch packet cursor_geodesy_readout summary contract schema missing or invalid"
}
if ($launchPacket.cursor_geodesy_readout.cursor_summary_contract.qt_copy_action -ne "copy_cursor_geodesy_summary") {
    throw "Launch packet cursor_geodesy_readout summary copy action missing or invalid"
}
if (-not $launchPacket.cursor_geodesy_readout.cursor_summary_contract.portable) {
    throw "Launch packet cursor_geodesy_readout summary portability flag missing"
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
if ($launchPacket.pin_overlay.occlusion_status_values -notcontains "behind_horizon") {
    throw "Launch packet pin_overlay occlusion status values missing behind_horizon"
}
if ($launchPacket.pin_overlay.qt_occlusion_legend_object -ne "pinOcclusionLegend") {
    throw "Launch packet pin_overlay occlusion legend object missing"
}
if ($launchPacket.pin_overlay.renderer_overlay_status -ne "wired_to_pin_overlay_rgba_and_frame_composition") {
    throw "Launch packet pin_overlay renderer overlay status mismatch"
}
if ($launchPacket.pin_overlay.cursor_fill_priority -ne "renderer_cursor_geodesy_state_then_ui_estimate") {
    throw "Launch packet pin_overlay cursor fill priority mismatch"
}
if ($launchPacket.pin_overlay.pin_summary_contract_schema -ne "rrkal_displaytools.pin_summary_contract.v1") {
    throw "Launch packet pin_overlay summary contract schema missing or invalid"
}
if ($launchPacket.pin_overlay.pin_summary_contract.qt_list_object -ne "pinList") {
    throw "Launch packet pin_overlay summary list object missing or invalid"
}
if ($launchPacket.pin_overlay.pin_summary_contract.qt_copy_action -ne "copy_pin_overlay_summary") {
    throw "Launch packet pin_overlay summary copy action missing or invalid"
}
if ($launchPacket.pin_overlay.pin_summary_contract.summary_format -notlike "*occlusion_statuses*") {
    throw "Launch packet pin_overlay summary format missing occlusion statuses"
}
if (-not $launchPacket.pin_overlay.pin_summary_contract.portable) {
    throw "Launch packet pin_overlay summary portability flag missing"
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
if ($capabilities.layer_selection_tool.selection_summary_contract_schema -ne "rrkal_displaytools.layer_selection_summary_contract.v1") {
    throw "Renderer layer_selection_tool selection summary contract schema missing or invalid"
}
if ($capabilities.layer_selection_tool.selection_summary_contract.qt_copy_action -ne "copy_layer_selection_summary") {
    throw "Renderer layer_selection_tool selection summary copy action missing or invalid"
}
if ($capabilities.layer_selection_affordance.schema -ne "rrkal_displaytools.layer_selection_affordance.v1") {
    throw "Renderer layer_selection_affordance schema missing or invalid"
}
if ($capabilities.layer_selection_affordance.qt_surface -ne "Layers dock selected row highlight / layerSelectionAffordance label") {
    throw "Renderer layer_selection_affordance Qt surface mismatch"
}
if ($capabilities.layer_selection_affordance.selected_row_property -ne "selected") {
    throw "Renderer layer_selection_affordance selected row property mismatch"
}
if ($capabilities.layer_hover_affordance.schema -ne "rrkal_displaytools.layer_hover_affordance.v1") {
    throw "Renderer layer_hover_affordance schema missing or invalid"
}
if ($capabilities.layer_hover_affordance.hover_events -notcontains "QEvent.Enter") {
    throw "Renderer layer_hover_affordance enter event missing"
}
if ($capabilities.layer_lock_affordance.schema -ne "rrkal_displaytools.layer_lock_affordance.v1") {
    throw "Renderer layer_lock_affordance schema missing or invalid"
}
if ($capabilities.layer_lock_affordance.qt_surface -ne "Layers dock locked row tint / disabled visibility checkbox") {
    throw "Renderer layer_lock_affordance Qt surface mismatch"
}
if ($capabilities.layer_lock_affordance.visibility_control_disabled_when_locked -ne $true) {
    throw "Renderer layer_lock_affordance disabled visibility control flag missing"
}
if ($capabilities.layer_lock_affordance.disabled_controls_when_locked -notcontains "opacity_slider") {
    throw "Renderer layer_lock_affordance disabled opacity slider missing"
}
if ($capabilities.layer_research_workflow.schema -ne "rrkal_displaytools.layer_research_workflow.v1") {
    throw "Renderer layer_research_workflow schema missing or invalid"
}
if ($capabilities.layer_research_workflow.status -ne "ready") {
    throw "Renderer layer_research_workflow not ready"
}
if ($capabilities.layer_research_workflow.research_summary_contract_schema -ne "rrkal_displaytools.research_interaction_summary_contract.v1") {
    throw "Renderer research interaction summary contract schema missing or invalid"
}
if ($capabilities.layer_research_workflow.research_summary_contract.qt_copy_action -ne "copy_research_interaction_summary") {
    throw "Renderer research interaction summary copy action missing or invalid"
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
if ($capabilities.cursor_geodesy_readout.cursor_summary_contract_schema -ne "rrkal_displaytools.cursor_geodesy_summary_contract.v1") {
    throw "Renderer cursor_geodesy_readout summary contract schema missing or invalid"
}
if ($capabilities.cursor_geodesy_readout.cursor_summary_contract.qt_copy_action -ne "copy_cursor_geodesy_summary") {
    throw "Renderer cursor_geodesy_readout summary copy action missing or invalid"
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
if ($capabilities.pin_overlay.qt_occlusion_legend_object -ne "pinOcclusionLegend") {
    throw "Renderer pin_overlay occlusion legend object missing"
}
if ($capabilities.pin_overlay.occlusion_status_values -notcontains "off_viewport") {
    throw "Renderer pin_overlay occlusion status values missing off_viewport"
}
if ($capabilities.pin_overlay.cursor_fill_sources -notcontains "renderer_cursor_geodesy_state") {
    throw "Renderer pin_overlay cursor fill source missing"
}
if ($capabilities.pin_overlay.pin_summary_contract_schema -ne "rrkal_displaytools.pin_summary_contract.v1") {
    throw "Renderer pin_overlay summary contract schema missing or invalid"
}
if ($capabilities.pin_overlay.pin_summary_contract.qt_copy_action -ne "copy_pin_overlay_summary") {
    throw "Renderer pin_overlay summary copy action missing or invalid"
}
if ($capabilities.pin_overlay.pin_summary_contract.summary_format -notlike "*legend={qt_occlusion_legend_object}*") {
    throw "Renderer pin_overlay summary format missing occlusion legend"
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
if ($capabilities.boundary_emphasis_control.boundary_summary_contract_schema -ne "rrkal_displaytools.boundary_emphasis_summary_contract.v1") {
    throw "Renderer boundary_emphasis_control summary contract schema missing or invalid"
}
if ($capabilities.boundary_emphasis_control.boundary_summary_contract.qt_copy_action -ne "copy_boundary_emphasis_summary") {
    throw "Renderer boundary_emphasis_control summary copy action missing or invalid"
}
if ($capabilities.boundary_emphasis_control.boundary_summary_contract.summary_format -notlike "*contrast={contrast}*gamma={gamma}*breathing={breathing_enabled}@{breathing_period_s}s*") {
    throw "Renderer boundary_emphasis_control summary tuning format missing"
}
if ($capabilities.boundary_emphasis_control.summary_parameter_fields -notcontains "contrast") {
    throw "Renderer boundary_emphasis_control portable summary parameter fields missing"
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
if ($capabilities.style_renderer_entries.renderer_entry_contract_schema -ne "rrkal_displaytools.style_renderer_entry_contract.v1") {
    throw "Renderer style_renderer_entries entry contract schema missing"
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
if ($capabilities.style_profile_renderer_routes.renderer_entry_contract_schema -ne "rrkal_displaytools.style_renderer_entry_contract.v1") {
    throw "Renderer style_profile_renderer_routes entry contract schema missing"
}
if ($capabilities.style_profile_renderer_routes.style_routes_summary_contract.schema -ne "rrkal_displaytools.style_routes_summary_contract.v1") {
    throw "Renderer style routes summary contract missing or invalid"
}
if ($capabilities.style_profile_renderer_routes.style_routes_summary_contract.qt_copy_action -ne "copy_style_routes_summary") {
    throw "Renderer style routes summary copy action missing"
}
if ($capabilities.style_template_visual_preview.schema -ne "rrkal_displaytools.style_template_visual_preview.v1") {
    throw "Renderer style_template_visual_preview schema missing or invalid"
}
if ($capabilities.style_template_visual_preview.preview_ids -notcontains "parchment") {
    throw "Renderer style_template_visual_preview missing parchment preview"
}
if ($capabilities.style_template_visual_preview.preview_ids -notcontains "tactical") {
    throw "Renderer style_template_visual_preview missing tactical preview"
}
if ($capabilities.style_template_visual_preview.qt_card_object_prefix -ne "styleTemplateCard_") {
    throw "Renderer style_template_visual_preview Qt card object prefix missing"
}
if ($capabilities.style_template_visual_preview.thumbnail_source_contract -ne "rrkal_displaytools.renderer_output_artifact_contract.v1") {
    throw "Renderer style_template_visual_preview thumbnail source contract mismatch"
}
if ($capabilities.style_template_visual_preview.preview_cards[0].thumbnail_review_command -notcontains "--output") {
    throw "Renderer style_template_visual_preview thumbnail review command missing output flag"
}
if ($capabilities.style_template_visual_preview.qt_inspector_action_label -ne "Inspect: Style thumbs") {
    throw "Renderer style_template_visual_preview thumbnail inspector label missing"
}
if ($capabilities.style_template_visual_preview.qt_icon_loader -ne "refresh_style_template_preview_cards") {
    throw "Renderer style_template_visual_preview icon loader mismatch"
}
if ($capabilities.style_template_visual_preview.thumbnail_icon_size[0] -ne 96) {
    throw "Renderer style_template_visual_preview icon width mismatch"
}
if ($capabilities.style_template_visual_preview.thumbnail_batch_outputs -notcontains "state/style_previews/tactical.png") {
    throw "Renderer style_template_visual_preview tactical thumbnail batch output missing"
}
if ($capabilities.style_template_visual_preview.thumbnail_readiness_schema -ne "rrkal_displaytools.style_thumbnail_readiness.v1") {
    throw "Renderer style_template_visual_preview thumbnail readiness schema missing"
}
if ($capabilities.style_template_visual_preview.thumbnail_readiness_summary_format -notlike "*ready={ready_count}*") {
    throw "Renderer style_template_visual_preview thumbnail readiness summary format missing"
}
if ($capabilities.style_template_visual_preview.thumbnail_readiness_copy_label -ne "Copy style thumb status") {
    throw "Renderer style_template_visual_preview thumbnail readiness copy label missing"
}
if ($capabilities.style_template_visual_preview.local_thumbnail_readiness_qt_action -ne "show_style_thumbnail_slots") {
    throw "Renderer style_template_visual_preview local thumbnail readiness Qt action missing"
}
if ($capabilities.visual_feature_closure_matrix.schema -ne "rrkal_displaytools.visual_feature_closure_matrix.v1") {
    throw "Renderer visual feature closure matrix schema missing or invalid"
}
if ($capabilities.visual_feature_closure_matrix.feature_ids -notcontains "ocean_material") {
    throw "Renderer visual feature closure matrix missing ocean material evidence"
}
if ($capabilities.visual_feature_closure_matrix.feature_ids -notcontains "renderer_performance") {
    throw "Renderer visual feature closure matrix missing renderer performance queue"
}
if ($capabilities.renderer_output_artifact_contract.schema -ne "rrkal_displaytools.renderer_output_artifact_contract.v1") {
    throw "Renderer output artifact contract schema missing or invalid"
}
if ($capabilities.renderer_output_artifact_contract.image_output_control -ne "--output") {
    throw "Renderer output artifact contract output control mismatch"
}
if ($capabilities.renderer_output_artifact_contract.metadata_fields -notcontains "layer_render_plan") {
    throw "Renderer output artifact metadata fields missing layer render plan"
}
if ($capabilities.layer_render_plan_performance.schema -ne "rrkal_displaytools.layer_render_plan_performance.v1") {
    throw "Renderer layer_render_plan_performance schema missing or invalid"
}
if ($capabilities.layer_render_plan_performance.optimization_target -ne "precompute_layer_state_then_single_render_pass") {
    throw "Renderer layer_render_plan_performance optimization target mismatch"
}
if ($capabilities.layer_render_plan_performance.stage_order -notcontains "submit_single_taichi_render_pass") {
    throw "Renderer layer_render_plan_performance single-pass stage missing"
}
if ($capabilities.layer_render_plan_performance.runtime_optimization_applied -ne $false) {
    throw "Renderer layer_render_plan_performance must not claim applied runtime optimization"
}
if ($capabilities.layer_render_plan_performance.runtime_snapshot_schema -ne "rrkal_displaytools.layer_render_plan_runtime_snapshot.v1") {
    throw "Renderer layer_render_plan_performance runtime snapshot schema missing"
}
if ($capabilities.layer_render_plan_performance.runtime_snapshot_helper -ne "HybridRenderController.layer_render_plan_runtime_snapshot") {
    throw "Renderer layer_render_plan_performance runtime snapshot helper missing"
}
if ($capabilities.layer_render_plan_performance.composition_apply_helper -ne "HybridRenderController.apply_layer_render_plan_composition") {
    throw "Renderer layer_render_plan_performance composition apply helper missing"
}
if ($capabilities.layer_render_plan_performance.compiled_plan_helper -ne "HybridRenderController.compile_layer_render_plan") {
    throw "Renderer layer_render_plan_performance compiled plan helper missing"
}
if ($capabilities.layer_render_plan_performance.compiled_plan_cache_key_helper -ne "HybridRenderController.layer_render_plan_cache_key") {
    throw "Renderer layer_render_plan_performance cache key helper missing"
}
if ($capabilities.layer_render_plan_performance.cache_diagnostics_schema -ne "rrkal_displaytools.layer_render_plan_cache_diagnostics.v1") {
    throw "Renderer layer_render_plan_performance cache diagnostics schema missing"
}
if ($capabilities.layer_render_plan_performance.cache_diagnostics_metadata_source -ne "renderer_output_metadata.layer_render_plan") {
    throw "Renderer layer_render_plan_performance cache diagnostics metadata source missing"
}
if ($capabilities.module_boundary_registry.schema -ne "rrkal_displaytools.module_boundary_registry.v1") {
    throw "Renderer module_boundary_registry schema missing or invalid"
}
if ($capabilities.module_boundary_registry.target_modules -notcontains "data_sources/*") {
    throw "Renderer module_boundary_registry missing RRKAL data boundary"
}
if ($capabilities.module_boundary_registry.decoupling_boundary_contract.schema -ne "rrkal_displaytools.module_decoupling_boundary_contract.v1") {
    throw "Renderer module decoupling boundary contract missing or invalid"
}
if ($capabilities.module_boundary_registry.decoupling_boundary_contract.stable_contracts_before_move -notcontains "smoke_gates") {
    throw "Renderer module decoupling boundary stable contract list incomplete"
}
if ($capabilities.module_boundary_registry.module_boundary_summary_contract.schema -ne "rrkal_displaytools.module_boundary_summary_contract.v1") {
    throw "Renderer module boundary summary contract missing or invalid"
}
if ($capabilities.module_boundary_registry.module_boundary_summary_contract.qt_copy_action -ne "copy_module_boundary_summary") {
    throw "Renderer module boundary summary copy action missing"
}
if ($capabilities.cross_machine_clone_readiness.schema -ne "rrkal_displaytools.cross_machine_clone_readiness.v1") {
    throw "Renderer cross_machine_clone_readiness schema missing or invalid"
}
if ($capabilities.cross_machine_clone_readiness.required_commands -notcontains "scripts/run_qt_panel.ps1") {
    throw "Renderer cross_machine_clone_readiness missing run command"
}
if ($capabilities.cross_machine_clone_readiness.clone_command -notlike "git clone *RRKAL_displaytools.git") {
    throw "Renderer cross_machine_clone_readiness clone command missing"
}
if ($capabilities.cross_machine_clone_readiness.default_branch -ne "main") {
    throw "Renderer cross_machine_clone_readiness default branch mismatch"
}
if ($capabilities.cross_machine_clone_readiness.qt_surface -ne "Layers dock cross-machine readiness label") {
    throw "Renderer cross_machine_clone_readiness Qt surface mismatch"
}
if ($capabilities.cross_machine_clone_readiness.qt_visible_fields -notcontains "first_run_handoff_command") {
    throw "Renderer cross_machine_clone_readiness Qt visible first-run handoff field missing"
}
if ($capabilities.cross_machine_clone_readiness.qt_visible_fields -notcontains "default_branch") {
    throw "Renderer cross_machine_clone_readiness Qt visible default branch field missing"
}
if ($capabilities.cross_machine_clone_readiness.launcher_options -notcontains "-HandoffFirst") {
    throw "Renderer cross_machine_clone_readiness missing HandoffFirst launcher option"
}
if ($capabilities.cross_machine_clone_readiness.handoff_first_command -notlike "*run_qt_panel.ps1 -HandoffFirst") {
    throw "Renderer cross_machine_clone_readiness handoff-first command mismatch"
}
if ($capabilities.cross_machine_clone_readiness.first_run_smoke_command -notlike "*scripts/smoke.ps1") {
    throw "Renderer cross_machine_clone_readiness first-run smoke command missing"
}
if ($capabilities.cross_machine_clone_readiness.clone_reviewer_summary_contract_schema -ne "rrkal_displaytools.clone_reviewer_summary_contract.v1") {
    throw "Renderer clone reviewer summary contract schema missing or invalid"
}
if ($capabilities.cross_machine_clone_readiness.clone_reviewer_summary_contract.qt_copy_action -ne "copy_clone_reviewer_summary") {
    throw "Renderer clone reviewer summary copy action missing or invalid"
}
if ($capabilities.profile_ui_state_replay.qt_inspector_action_ids -notcontains "cursor_geo") {
    throw "Renderer profile_ui_state_replay Cursor inspector action missing"
}
if ($capabilities.profile_ui_state_replay.qt_inspector_action_ids -notcontains "clone_summary") {
    throw "Renderer profile_ui_state_replay clone summary action missing"
}
if ($capabilities.profile_ui_state_replay.qt_inspector_action_labels -notcontains "Inspect: Clone ready") {
    throw "Renderer profile_ui_state_replay Clone inspector label missing"
}
if ($capabilities.profile_ui_state_replay.qt_inspector_action_ids -notcontains "layer_pick") {
    throw "Renderer profile_ui_state_replay layer pick inspector action missing"
}
if ($capabilities.profile_ui_state_replay.qt_inspector_action_labels -notcontains "Inspect: Timeline") {
    throw "Renderer profile_ui_state_replay Timeline inspector label missing"
}
if ($capabilities.profile_ui_state_replay.qt_inspector_action_labels -notcontains "Inspect: Canvas state") {
    throw "Renderer profile_ui_state_replay Canvas state inspector label missing"
}
if ($capabilities.profile_ui_state_replay.qt_inspector_action_labels -notcontains "Inspect: Layer matrix") {
    throw "Renderer profile_ui_state_replay layer matrix inspector label missing"
}
if ($capabilities.profile_ui_state_replay.qt_inspector_action_labels -notcontains "Inspect: Selection state") {
    throw "Renderer profile_ui_state_replay Selection state inspector label missing"
}
if ($capabilities.profile_ui_state_replay.qt_inspector_action_labels -notcontains "Inspect: Layer ops") {
    throw "Renderer profile_ui_state_replay Layer ops inspector label missing"
}
if ($capabilities.profile_ui_state_replay.qt_inspector_action_labels -notcontains "Inspect: Renderer thumbnail") {
    throw "Renderer profile_ui_state_replay Renderer thumbnail inspector label missing"
}
if ($capabilities.profile_ui_state_replay.qt_inspector_action_labels -notcontains "Inspect: Visual readiness") {
    throw "Renderer profile_ui_state_replay Visual readiness inspector label missing"
}
if ($capabilities.profile_ui_state_replay.qt_inspector_action_labels -notcontains "Inspect: Live preview") {
    throw "Renderer profile_ui_state_replay Live preview inspector label missing"
}
if ($capabilities.profile_ui_state_replay.qt_inspector_action_groups.id -notcontains "renderer_ports") {
    throw "Renderer profile_ui_state_replay renderer ports group missing"
}
if ($capabilities.layer_operation_feedback.schema -ne "rrkal_displaytools.layer_operation_feedback.v1") {
    throw "Renderer layer_operation_feedback capability missing or invalid"
}
if ($capabilities.layer_control_feedback_strip.schema -ne "rrkal_displaytools.layer_control_feedback_strip.v1") {
    throw "Renderer layer_control_feedback_strip capability missing or invalid"
}
if ($capabilities.layer_control_feedback_strip.qt_surface -ne "Layers dock layerControlFeedbackStrip label") {
    throw "Renderer layer_control_feedback_strip Qt surface missing"
}
if ($capabilities.profile_ui_state_replay.qt_inspector_action_groups.id -notcontains "visual_review") {
    throw "Renderer profile_ui_state_replay visual review group missing"
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
if ($capabilities.profile_launch_readiness.launch_reviewer_summary_contract_schema -ne "rrkal_displaytools.launch_reviewer_summary_contract.v1") {
    throw "Renderer launch reviewer summary contract schema missing or invalid"
}
if ($capabilities.profile_launch_readiness.launch_reviewer_summary_contract.qt_copy_action -ne "copy_launch_reviewer_summary") {
    throw "Renderer launch reviewer summary copy action missing or invalid"
}
if ($capabilities.profile_ui_state_replay.qt_inspector_action_ids -notcontains "launch_summary") {
    throw "Renderer profile_ui_state_replay launch summary action missing"
}
if ($capabilities.profile_launch_readiness_ui.schema -ne "rrkal_displaytools.profile_launch_readiness_ui.v1") {
    throw "Renderer profile_launch_readiness_ui schema missing or invalid"
}
if ($capabilities.profile_launch_readiness_ui.readiness -ne "ready") {
    throw "Renderer profile_launch_readiness_ui should be ready"
}
if ($capabilities.reviewer_packet_export.schema -ne "rrkal_displaytools.reviewer_packet_export.v1") {
    throw "Renderer reviewer_packet_export schema missing or invalid"
}
if ($capabilities.reviewer_packet_export.qt_action -ne "export_reviewer_packet_dialog") {
    throw "Renderer reviewer packet Qt action missing or invalid"
}
if ($capabilities.reviewer_packet_export.included_summary_fields -notcontains "clone_reviewer_summary") {
    throw "Renderer reviewer packet clone summary field missing"
}
if ($capabilities.reviewer_packet_export.included_summary_fields -notcontains "hydrology_lod_summary") {
    throw "Renderer reviewer packet hydrology summary field missing"
}
if ($capabilities.reviewer_packet_export.included_summary_fields -notcontains "ocean_material_summary") {
    throw "Renderer reviewer packet ocean summary field missing"
}
if ($capabilities.reviewer_packet_export.included_summary_fields -notcontains "style_routes_summary") {
    throw "Renderer reviewer packet style routes summary field missing"
}
if ($capabilities.reviewer_packet_export.included_summary_fields -notcontains "module_boundary_summary") {
    throw "Renderer reviewer packet module boundary summary field missing"
}
if ($capabilities.reviewer_packet_export.included_packet_fields -notcontains "hydrology_lod_readiness") {
    throw "Renderer reviewer packet hydrology readiness packet field missing"
}
if ($capabilities.reviewer_packet_export.included_packet_fields -notcontains "hydrology_lod_runtime_evidence") {
    throw "Renderer reviewer packet hydrology runtime evidence packet field missing"
}
if ($capabilities.reviewer_packet_export.included_packet_fields -notcontains "ocean_material_control_port") {
    throw "Renderer reviewer packet ocean material packet field missing"
}
if ($capabilities.reviewer_packet_export.included_packet_fields -notcontains "style_profile_renderer_routes") {
    throw "Renderer reviewer packet style routes packet field missing"
}
if ($capabilities.reviewer_packet_export.included_packet_fields -notcontains "module_boundary_registry") {
    throw "Renderer reviewer packet module boundary packet field missing"
}
if ($capabilities.reviewer_packet_export.included_packet_fields -notcontains "layer_render_plan_performance") {
    throw "Renderer reviewer packet render plan performance packet field missing"
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
if ($capabilities.hydrology_lod_readiness.hydrology_lod_summary_contract.schema -ne "rrkal_displaytools.hydrology_lod_summary_contract.v1") {
    throw "Renderer hydrology_lod summary contract missing or invalid"
}
if ($capabilities.hydrology_lod_readiness.hydrology_lod_summary_contract.qt_copy_action -ne "copy_hydrology_lod_summary") {
    throw "Renderer hydrology_lod summary copy action missing"
}
if ($capabilities.hydrology_lod_readiness.renderer_apply_contract.schema -ne "rrkal_displaytools.hydrology_lod_renderer_apply_contract.v1") {
    throw "Renderer hydrology_lod renderer apply contract missing or invalid"
}
if ($capabilities.hydrology_lod_readiness.renderer_apply_contract.runtime_state_file -ne "state/renderer_layer_runtime_state.json") {
    throw "Renderer hydrology_lod renderer apply runtime state file mismatch"
}
if ($capabilities.hydrology_lod_readiness.renderer_apply_contract.renderer_targets -notcontains "lakes") {
    throw "Renderer hydrology_lod renderer apply contract missing lakes target"
}
if ($capabilities.hydrology_lod_runtime_evidence.schema -ne "rrkal_displaytools.hydrology_lod_runtime_evidence.v1") {
    throw "Renderer hydrology_lod_runtime_evidence schema missing or invalid"
}
if ($capabilities.hydrology_lod_runtime_evidence.renderer_apply_contract_schema -ne "rrkal_displaytools.hydrology_lod_renderer_apply_contract.v1") {
    throw "Renderer hydrology_lod_runtime_evidence renderer apply contract schema missing"
}
if ($capabilities.hydrology_lod_runtime_evidence.qt_surface -ne "Layers dock Hydrology runtime evidence label") {
    throw "Renderer hydrology_lod_runtime_evidence qt surface mismatch"
}
if ($capabilities.hydrology_lod_runtime_evidence.summary_runtime_fields -notcontains "hydrology_runtime_hit_count") {
    throw "Renderer hydrology_lod_runtime_evidence summary runtime fields missing"
}
if ($capabilities.ocean_material_control_port.schema -ne "rrkal_displaytools.ocean_material_control_port.v1") {
    throw "Renderer ocean_material_control_port schema missing or invalid"
}
if ($capabilities.ocean_material_control_port.taichi_uniforms -notcontains "wave_strength") {
    throw "Renderer ocean_material_control_port Taichi uniforms missing"
}
if ($capabilities.ocean_material_control_port.qt_control_panel.schema -ne "rrkal_displaytools.taichi_ocean_3d_control_panel.v1") {
    throw "Renderer Taichi ocean 3D control panel schema missing or invalid"
}
if ($capabilities.ocean_material_control_port.qt_control_panel.qt_dialog_action -ne "open_taichi_ocean_3d_controls") {
    throw "Renderer Taichi ocean 3D control panel dialog action missing"
}
if ($capabilities.ocean_material_control_port.qt_control_panel.render_pipeline_followup -ne "post_decoupling_precompute_layer_render_plan_then_single_render_pass") {
    throw "Renderer Taichi ocean 3D control panel performance followup missing"
}
if ($capabilities.ocean_material_control_port.qt_control_panel.control_board_label_object -ne "ocean3DControlBoardStrip") {
    throw "Renderer Taichi ocean 3D control board strip missing"
}
if ($capabilities.ocean_material_control_port.qt_control_panel.control_board_default_visible -ne $true) {
    throw "Renderer Taichi ocean 3D control board visibility flag missing"
}
if ($capabilities.ocean_material_control_port.ocean_material_summary_contract.schema -ne "rrkal_displaytools.ocean_material_summary_contract.v1") {
    throw "Renderer ocean material summary contract missing or invalid"
}
if ($capabilities.ocean_material_control_port.ocean_material_summary_contract.qt_copy_action -ne "copy_ocean_material_summary") {
    throw "Renderer ocean material summary copy action missing"
}
if ($capabilities.ocean_material_control_port.renderer_apply_contract.schema -ne "rrkal_displaytools.ocean_material_renderer_apply_contract.v1") {
    throw "Renderer ocean material apply contract missing or invalid"
}
if ($capabilities.ocean_material_control_port.renderer_apply_contract.input_sources -notcontains "timeline_ocean_material_interpolation") {
    throw "Renderer ocean material apply contract timeline source missing"
}
if ($capabilities.ocean_material_control_port.sea_state_port.scalar_sample_contract.schema -ne "rrkal_displaytools.sea_state_scalar_sample.v1") {
    throw "Renderer ocean material sea-state scalar sample contract missing"
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
if ($handoff.launch_packet_contracts.layer_operation_feedback -ne "rrkal_displaytools.layer_operation_feedback.v1") {
    throw "Handoff inspection launch packet layer_operation_feedback schema missing or invalid"
}
if ($handoff.layer_operation_feedback.launch_packet_schema -ne "rrkal_displaytools.layer_operation_feedback.v1") {
    throw "Handoff inspection layer_operation_feedback launch packet schema missing or invalid"
}
if ($handoff.layer_operation_feedback.renderer_capabilities_schema -ne "rrkal_displaytools.layer_operation_feedback.v1") {
    throw "Handoff inspection layer_operation_feedback renderer capability schema missing or invalid"
}
if ($handoff.launch_packet_contracts.layer_control_feedback_strip -ne "rrkal_displaytools.layer_control_feedback_strip.v1") {
    throw "Handoff inspection launch packet layer_control_feedback_strip schema missing or invalid"
}
if ($handoff.layer_control_feedback_strip.launch_packet_schema -ne "rrkal_displaytools.layer_control_feedback_strip.v1") {
    throw "Handoff inspection layer_control_feedback_strip launch packet schema missing or invalid"
}
if ($handoff.layer_control_feedback_strip.qt_label_object -ne "layerControlFeedbackStrip") {
    throw "Handoff inspection layer_control_feedback_strip label object missing"
}
if ($handoff.profile_visual_quick_review.launch_packet_schema -ne "rrkal_displaytools.profile_ui_state_replay.v1") {
    throw "Handoff inspection profile visual quick review schema missing or invalid"
}
if ($handoff.profile_visual_quick_review.qt_inspector_group_ids -notcontains "research_interaction") {
    throw "Handoff inspection profile visual quick review missing research interaction group"
}
if ($handoff.profile_visual_quick_review.qt_inspector_group_ids -notcontains "visual_review") {
    throw "Handoff inspection profile visual quick review missing visual review group"
}
if ($handoff.profile_visual_quick_review.research_interaction_actions -notcontains "layer_ops") {
    throw "Handoff inspection profile visual quick review missing Layer ops action"
}
if ($handoff.profile_visual_quick_review.visual_review_actions -notcontains "visual_readiness") {
    throw "Handoff inspection profile visual quick review missing visual readiness action"
}
if ($handoff.profile_visual_quick_review.visual_review_actions -notcontains "renderer_thumbnail") {
    throw "Handoff inspection profile visual quick review missing renderer thumbnail action"
}
if ($handoff.profile_visual_quick_review.visual_review_actions -notcontains "live_preview") {
    throw "Handoff inspection profile visual quick review missing live preview action"
}
if ($handoff.visual_review_readiness.schema -ne "rrkal_displaytools.visual_review_readiness.v1") {
    throw "Handoff inspection visual review readiness schema missing or invalid"
}
if ($handoff.visual_review_readiness.launch_packet_schema -ne "rrkal_displaytools.visual_review_readiness.v1") {
    throw "Handoff inspection visual review readiness launch packet schema missing or invalid"
}
if ($handoff.visual_review_readiness.renderer_capabilities_schema -ne "rrkal_displaytools.visual_review_readiness.v1") {
    throw "Handoff inspection visual review readiness renderer capability schema missing or invalid"
}
if ($handoff.visual_review_readiness.qt_inspector_action_id -ne "visual_readiness") {
    throw "Handoff inspection visual review readiness Qt action id missing or invalid"
}
if ($handoff.visual_review_readiness.visual_review_actions -notcontains "visual_readiness") {
    throw "Handoff inspection visual review readiness missing visual readiness action"
}
if (-not $handoff.visual_review_readiness.renderer_thumbnail_ready) {
    throw "Handoff inspection visual review readiness missing renderer thumbnail readiness"
}
if (-not $handoff.visual_review_readiness.live_preview_ready) {
    throw "Handoff inspection visual review readiness missing live preview readiness"
}
if ($handoff.visual_review_readiness.frame_status_schema -ne "rrkal_displaytools.visual_review_frame_status.v1") {
    throw "Handoff inspection visual review readiness frame status schema missing or invalid"
}
if ($handoff.visual_review_readiness.frame_status.renderer_thumbnail.status -ne "inspect_action_available") {
    throw "Handoff inspection visual review readiness renderer thumbnail frame status missing or invalid"
}
if ($handoff.visual_review_readiness.frame_status.live_preview.status -ne "inspect_action_available") {
    throw "Handoff inspection visual review readiness live preview frame status missing or invalid"
}
if ($handoff.visual_review_readiness.frame_status.renderer_thumbnail.artifact_state -ne "runtime_dependent") {
    throw "Handoff inspection visual review readiness renderer thumbnail artifact state missing or invalid"
}
if ($handoff.visual_review_readiness.frame_status.live_preview.artifact_state -ne "runtime_dependent") {
    throw "Handoff inspection visual review readiness live preview artifact state missing or invalid"
}
if ($handoff.visual_review_readiness.inspector_view_schema -ne "rrkal_displaytools.visual_review_inspector_view.v1") {
    throw "Handoff inspection visual review readiness inspector view schema missing or invalid"
}
if ($handoff.visual_review_readiness.inspector_view.title -ne "Visual readiness") {
    throw "Handoff inspection visual review readiness inspector view title missing or invalid"
}
if ($handoff.visual_review_readiness.inspector_view.surface -ne "Qt Visual review inspector") {
    throw "Handoff inspection visual review readiness inspector view surface missing or invalid"
}
if ($handoff.visual_review_readiness.inspector_view.rows.Count -lt 2) {
    throw "Handoff inspection visual review readiness inspector view rows missing"
}
if (-not $handoff.visual_review_readiness.inspector_view.copyable) {
    throw "Handoff inspection visual review readiness inspector view copyable flag missing"
}
if ($handoff.visual_review_readiness.qt_command_contract_schema -ne "rrkal_displaytools.visual_review_qt_command_contract.v1") {
    throw "Handoff inspection visual review readiness Qt command contract schema missing or invalid"
}
if ($handoff.visual_review_readiness.qt_command_contract.action_id -ne "visual_readiness") {
    throw "Handoff inspection visual review readiness Qt command contract action id missing or invalid"
}
if ($handoff.visual_review_readiness.qt_command_contract.payload_field -ne "visual_review_readiness.inspector_view") {
    throw "Handoff inspection visual review readiness Qt command contract payload field missing or invalid"
}
if ($handoff.visual_review_readiness.qt_command_contract.dispatch_status -ne "contract_ready") {
    throw "Handoff inspection visual review readiness Qt command contract dispatch status missing or invalid"
}
if ($handoff.visual_review_readiness.qt_command_contract.implementation_status -ne "wired_in_qt_panel") {
    throw "Handoff inspection visual review readiness Qt command contract implementation status missing or invalid"
}
if ($handoff.visual_review_readiness.copy_summary_contract_schema -ne "rrkal_displaytools.visual_review_copy_summary_contract.v1") {
    throw "Handoff inspection visual review readiness copy summary contract schema missing or invalid"
}
if ($handoff.visual_review_readiness.copy_summary_contract.qt_label_object -ne "visualReviewReadiness") {
    throw "Handoff inspection visual review readiness copy summary label object missing or invalid"
}
if ($handoff.visual_review_readiness.copy_summary_contract.qt_copy_action -ne "copy_visual_review_readiness_summary") {
    throw "Handoff inspection visual review readiness copy summary action missing or invalid"
}
if (-not $handoff.visual_review_readiness.copy_summary_contract.portable) {
    throw "Handoff inspection visual review readiness copy summary portability flag missing"
}
$visualReviewGuidance = ($handoff.visual_review_readiness.missing_frame_guidance -join " ")
if ($visualReviewGuidance -notmatch 'Inspect: Renderer thumbnail') {
    throw "Handoff inspection visual review readiness missing renderer thumbnail guidance"
}
if ($visualReviewGuidance -notmatch 'Inspect: Live preview') {
    throw "Handoff inspection visual review readiness missing live preview guidance"
}
if ($handoff.launch_packet_contracts.visual_feature_closure_matrix -ne "rrkal_displaytools.visual_feature_closure_matrix.v1") {
    throw "Handoff inspection visual feature closure matrix launch contract missing or invalid"
}
if ($handoff.visual_feature_closure_matrix.launch_packet_schema -ne "rrkal_displaytools.visual_feature_closure_matrix.v1") {
    throw "Handoff inspection visual feature closure matrix launch schema missing"
}
if ($handoff.visual_feature_closure_matrix.renderer_capabilities_schema -ne "rrkal_displaytools.visual_feature_closure_matrix.v1") {
    throw "Handoff inspection visual feature closure matrix renderer schema missing"
}
if ($handoff.visual_feature_closure_matrix.feature_ids -notcontains "boundary_emphasis") {
    throw "Handoff inspection visual feature closure matrix missing boundary evidence"
}
if ($handoff.visual_feature_closure_matrix.feature_ids -notcontains "renderer_performance") {
    throw "Handoff inspection visual feature closure matrix missing renderer performance queue"
}
if ($handoff.launch_packet_contracts.renderer_output_artifact_contract -ne "rrkal_displaytools.renderer_output_artifact_contract.v1") {
    throw "Handoff inspection renderer output artifact contract missing or invalid"
}
if ($handoff.renderer_output_artifact_contract.launch_packet_schema -ne "rrkal_displaytools.renderer_output_artifact_contract.v1") {
    throw "Handoff inspection renderer output artifact launch schema missing"
}
if ($handoff.renderer_output_artifact_contract.renderer_capabilities_schema -ne "rrkal_displaytools.renderer_output_artifact_contract.v1") {
    throw "Handoff inspection renderer output artifact renderer schema missing"
}
if ($handoff.renderer_output_artifact_contract.quick_render_smoke_validates -notcontains "metadata_sidecar_schema") {
    throw "Handoff inspection renderer output artifact metadata quick smoke check missing"
}
if ($handoff.renderer_output_artifact_contract.metadata_fields -notcontains "layer_render_plan") {
    throw "Handoff inspection renderer output artifact metadata fields missing layer render plan"
}
if ($handoff.launch_packet_contracts.layer_render_plan_performance -ne "rrkal_displaytools.layer_render_plan_performance.v1") {
    throw "Handoff inspection layer render plan performance launch contract missing or invalid"
}
if ($handoff.layer_render_plan_performance.launch_packet_schema -ne "rrkal_displaytools.layer_render_plan_performance.v1") {
    throw "Handoff inspection layer render plan performance launch schema missing"
}
if ($handoff.layer_render_plan_performance.renderer_capabilities_schema -ne "rrkal_displaytools.layer_render_plan_performance.v1") {
    throw "Handoff inspection layer render plan performance renderer schema missing"
}
if ($handoff.layer_render_plan_performance.status -ne "queued_after_module_decoupling") {
    throw "Handoff inspection layer render plan performance status mismatch"
}
if ($handoff.layer_render_plan_performance.stage_order -notcontains "submit_single_taichi_render_pass") {
    throw "Handoff inspection layer render plan performance single-pass stage missing"
}
if ($handoff.layer_render_plan_performance.runtime_optimization_applied -ne $false) {
    throw "Handoff inspection layer render plan performance must not claim applied runtime optimization"
}
if ($handoff.layer_render_plan_performance.runtime_snapshot_schema -ne "rrkal_displaytools.layer_render_plan_runtime_snapshot.v1") {
    throw "Handoff inspection layer render plan performance runtime snapshot schema missing"
}
if ($handoff.layer_render_plan_performance.runtime_snapshot_helper -ne "HybridRenderController.layer_render_plan_runtime_snapshot") {
    throw "Handoff inspection layer render plan performance runtime snapshot helper missing"
}
if ($handoff.layer_render_plan_performance.composition_apply_helper -ne "HybridRenderController.apply_layer_render_plan_composition") {
    throw "Handoff inspection layer render plan performance composition apply helper missing"
}
if ($handoff.layer_render_plan_performance.compiled_plan_schema -ne "rrkal_displaytools.compiled_layer_render_plan.v1") {
    throw "Handoff inspection layer render plan performance compiled plan schema missing"
}
if ($handoff.layer_render_plan_performance.compiled_plan_cache_key_helper -ne "HybridRenderController.layer_render_plan_cache_key") {
    throw "Handoff inspection layer render plan performance cache key helper missing"
}
if ($handoff.layer_render_plan_performance.cache_diagnostics_schema -ne "rrkal_displaytools.layer_render_plan_cache_diagnostics.v1") {
    throw "Handoff inspection layer render plan performance cache diagnostics schema missing"
}
if ($handoff.layer_render_plan_performance.cache_diagnostics_qt_action -ne "show_layer_render_plan_performance") {
    throw "Handoff inspection layer render plan performance cache diagnostics Qt action missing"
}
if ($handoff.launch_packet_contracts.layer_selection_tool -ne "rrkal_displaytools.layer_selection_tool.v1") {
    throw "Handoff inspection layer_selection_tool launch contract missing or invalid"
}
if ($handoff.launch_packet_contracts.layer_selection_affordance -ne "rrkal_displaytools.layer_selection_affordance.v1") {
    throw "Handoff inspection layer_selection_affordance launch contract missing or invalid"
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
if ($handoff.layer_selection_tool.selection_summary_contract_schema -ne "rrkal_displaytools.layer_selection_summary_contract.v1") {
    throw "Handoff inspection layer_selection_tool selection summary contract schema missing or invalid"
}
if ($handoff.layer_selection_tool.selection_summary_contract.qt_label_object -ne "selectedLayer") {
    throw "Handoff inspection layer_selection_tool selection summary label object missing or invalid"
}
if ($handoff.layer_selection_tool.selection_summary_contract.qt_copy_action -ne "copy_layer_selection_summary") {
    throw "Handoff inspection layer_selection_tool selection summary copy action missing or invalid"
}
if (-not $handoff.layer_selection_tool.selection_summary_contract.portable) {
    throw "Handoff inspection layer_selection_tool selection summary portability flag missing"
}
if ($handoff.layer_selection_affordance.launch_packet_schema -ne "rrkal_displaytools.layer_selection_affordance.v1") {
    throw "Handoff inspection layer_selection_affordance launch schema missing or invalid"
}
if ($handoff.layer_selection_affordance.renderer_capabilities_schema -ne "rrkal_displaytools.layer_selection_affordance.v1") {
    throw "Handoff inspection layer_selection_affordance renderer schema missing or invalid"
}
if ($handoff.layer_selection_affordance.qt_label_object -ne "layerSelectionAffordance") {
    throw "Handoff inspection layer_selection_affordance label object missing"
}
if ($handoff.launch_packet_contracts.layer_hover_affordance -ne "rrkal_displaytools.layer_hover_affordance.v1") {
    throw "Handoff inspection layer_hover_affordance launch contract missing or invalid"
}
if ($handoff.layer_hover_affordance.launch_packet_schema -ne "rrkal_displaytools.layer_hover_affordance.v1") {
    throw "Handoff inspection layer_hover_affordance launch schema missing or invalid"
}
if ($handoff.layer_hover_affordance.qt_label_object -ne "layerHoverAffordance") {
    throw "Handoff inspection layer_hover_affordance label object missing"
}
if ($handoff.launch_packet_contracts.layer_lock_affordance -ne "rrkal_displaytools.layer_lock_affordance.v1") {
    throw "Handoff inspection layer_lock_affordance launch contract missing or invalid"
}
if ($handoff.layer_lock_affordance.launch_packet_schema -ne "rrkal_displaytools.layer_lock_affordance.v1") {
    throw "Handoff inspection layer_lock_affordance launch schema missing or invalid"
}
if ($handoff.layer_lock_affordance.renderer_capabilities_schema -ne "rrkal_displaytools.layer_lock_affordance.v1") {
    throw "Handoff inspection layer_lock_affordance renderer schema missing or invalid"
}
if ($handoff.layer_lock_affordance.locked_row_property -ne "locked") {
    throw "Handoff inspection layer_lock_affordance row property mismatch"
}
if ($handoff.layer_lock_affordance.disabled_controls_when_locked -notcontains "blend_combo") {
    throw "Handoff inspection layer_lock_affordance disabled blend combo missing"
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
if ($handoff.layer_research_workflow.research_summary_contract_schema -ne "rrkal_displaytools.research_interaction_summary_contract.v1") {
    throw "Handoff inspection research interaction summary contract schema missing or invalid"
}
if ($handoff.layer_research_workflow.research_summary_contract.qt_copy_action -ne "copy_research_interaction_summary") {
    throw "Handoff inspection research interaction summary copy action missing or invalid"
}
if (-not $handoff.layer_research_workflow.research_summary_contract.portable) {
    throw "Handoff inspection research interaction summary portability flag missing"
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
if ($handoff.cursor_geodesy_readout.cursor_summary_contract_schema -ne "rrkal_displaytools.cursor_geodesy_summary_contract.v1") {
    throw "Handoff inspection cursor_geodesy_readout summary contract schema missing or invalid"
}
if ($handoff.cursor_geodesy_readout.cursor_summary_contract.qt_copy_action -ne "copy_cursor_geodesy_summary") {
    throw "Handoff inspection cursor_geodesy_readout summary copy action missing or invalid"
}
if (-not $handoff.cursor_geodesy_readout.cursor_summary_contract.portable) {
    throw "Handoff inspection cursor_geodesy_readout summary portability flag missing"
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
if ($handoff.pin_overlay.qt_ui_affordances -notcontains "pin_occlusion_legend") {
    throw "Handoff inspection pin_overlay occlusion legend affordance missing"
}
if ($handoff.pin_overlay.qt_occlusion_legend_object -ne "pinOcclusionLegend") {
    throw "Handoff inspection pin_overlay occlusion legend object missing"
}
if ($handoff.pin_overlay.occlusion_status_values -notcontains "invalid") {
    throw "Handoff inspection pin_overlay occlusion status values missing invalid"
}
if ($handoff.pin_overlay.pin_list_summary_format -ne "source=<coordinate_source_label>") {
    throw "Handoff inspection pin_overlay list summary format missing"
}
if ($handoff.pin_overlay.pin_summary_contract_schema -ne "rrkal_displaytools.pin_summary_contract.v1") {
    throw "Handoff inspection pin_overlay summary contract schema missing or invalid"
}
if ($handoff.pin_overlay.pin_summary_contract.qt_list_object -ne "pinList") {
    throw "Handoff inspection pin_overlay summary list object missing or invalid"
}
if ($handoff.pin_overlay.pin_summary_contract.qt_copy_action -ne "copy_pin_overlay_summary") {
    throw "Handoff inspection pin_overlay summary copy action missing or invalid"
}
if ($handoff.pin_overlay.pin_summary_contract.summary_format -notlike "*occlusion_statuses*") {
    throw "Handoff inspection pin_overlay summary format missing occlusion statuses"
}
if (-not $handoff.pin_overlay.pin_summary_contract.portable) {
    throw "Handoff inspection pin_overlay summary portability flag missing"
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
if ($handoff.boundary_emphasis_control.summary_parameter_fields -notcontains "breathing_enabled") {
    throw "Handoff inspection boundary_emphasis_control summary parameter fields missing"
}
if (-not $handoff.boundary_emphasis_control.target_alignment) {
    throw "Handoff inspection boundary_emphasis_control target alignment field missing"
}
if ($handoff.boundary_emphasis_control.qt_surface -ne "Layers dock boundary emphasis dialog") {
    throw "Handoff inspection boundary_emphasis_control Qt surface mismatch"
}
if ($handoff.boundary_emphasis_control.boundary_summary_contract_schema -ne "rrkal_displaytools.boundary_emphasis_summary_contract.v1") {
    throw "Handoff inspection boundary_emphasis_control summary contract schema missing or invalid"
}
if ($handoff.boundary_emphasis_control.boundary_summary_contract.qt_label_object -ne "boundary_emphasis_label") {
    throw "Handoff inspection boundary_emphasis_control summary label object missing or invalid"
}
if ($handoff.boundary_emphasis_control.boundary_summary_contract.qt_copy_action -ne "copy_boundary_emphasis_summary") {
    throw "Handoff inspection boundary_emphasis_control summary copy action missing or invalid"
}
if ($handoff.boundary_emphasis_control.boundary_summary_contract.summary_format -notlike "*contrast={contrast}*gamma={gamma}*breathing={breathing_enabled}@{breathing_period_s}s*") {
    throw "Handoff inspection boundary_emphasis_control summary tuning format missing"
}
if (-not $handoff.boundary_emphasis_control.boundary_summary_contract.portable) {
    throw "Handoff inspection boundary_emphasis_control summary portability flag missing"
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
if ($handoff.launch_packet_contracts.style_renderer_entry_contract -ne "rrkal_displaytools.style_renderer_entry_contract.v1") {
    throw "Handoff inspection style renderer entry contract missing or invalid"
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
if ($handoff.style_renderer_entries.renderer_entry_contract_schema -ne "rrkal_displaytools.style_renderer_entry_contract.v1") {
    throw "Handoff inspection style_renderer_entries entry contract schema missing"
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
if ($handoff.style_profile_renderer_routes.required_route_contract_ids -notcontains "parchment") {
    throw "Handoff inspection style_profile_renderer_routes missing parchment route contract"
}
if ($handoff.style_profile_renderer_routes.style_routes_summary_contract_schema -ne "rrkal_displaytools.style_routes_summary_contract.v1") {
    throw "Handoff inspection style routes summary contract missing or invalid"
}
if ($handoff.style_profile_renderer_routes.style_routes_summary_contract.qt_copy_action -ne "copy_style_routes_summary") {
    throw "Handoff inspection style routes summary copy action missing"
}
if ($handoff.style_profile_renderer_routes.summary_parameter_fields -notcontains "required_routes") {
    throw "Handoff inspection style routes summary parameter fields missing"
}
if ($handoff.launch_packet_contracts.style_template_visual_preview -ne "rrkal_displaytools.style_template_visual_preview.v1") {
    throw "Handoff inspection style_template_visual_preview launch contract missing or invalid"
}
if ($handoff.style_template_visual_preview.launch_packet_schema -ne "rrkal_displaytools.style_template_visual_preview.v1") {
    throw "Handoff inspection style_template_visual_preview launch schema missing or invalid"
}
if ($handoff.style_template_visual_preview.renderer_capabilities_schema -ne "rrkal_displaytools.style_template_visual_preview.v1") {
    throw "Handoff inspection style_template_visual_preview renderer schema missing or invalid"
}
if ($handoff.style_template_visual_preview.preview_ids -notcontains "parchment") {
    throw "Handoff inspection style_template_visual_preview missing parchment preview"
}
if ($handoff.style_template_visual_preview.preview_ids -notcontains "tactical") {
    throw "Handoff inspection style_template_visual_preview missing tactical preview"
}
if ($handoff.style_template_visual_preview.card_click_action -ne "apply_style_template_preview_card") {
    throw "Handoff inspection style_template_visual_preview click action missing"
}
if (-not $handoff.style_template_visual_preview.thumbnail_slots_enabled) {
    throw "Handoff inspection style_template_visual_preview thumbnail slots not enabled"
}
if ($handoff.style_template_visual_preview.thumbnail_artifact_dir -ne "state/style_previews") {
    throw "Handoff inspection style_template_visual_preview thumbnail artifact dir mismatch"
}
if ($handoff.style_template_visual_preview.qt_inspector_action_id -ne "style_thumbnail_slots") {
    throw "Handoff inspection style_template_visual_preview thumbnail inspector action missing"
}
if ($handoff.style_template_visual_preview.thumbnail_icon_loading -ne "qt_loads_existing_png_as_card_icon") {
    throw "Handoff inspection style_template_visual_preview icon loading contract missing"
}
if ($handoff.style_template_visual_preview.thumbnail_batch_script -ne "scripts/render_style_previews.ps1") {
    throw "Handoff inspection style_template_visual_preview batch script missing"
}
if ($handoff.style_template_visual_preview.thumbnail_readiness_schema -ne "rrkal_displaytools.style_thumbnail_readiness.v1") {
    throw "Handoff inspection style_template_visual_preview thumbnail readiness schema missing"
}
if ($handoff.style_template_visual_preview.thumbnail_readiness_label_object -ne "styleThumbnailReadiness") {
    throw "Handoff inspection style_template_visual_preview thumbnail readiness label object missing"
}
if ($handoff.style_template_visual_preview.thumbnail_readiness_copy_action -ne "copy_style_thumbnail_readiness_summary") {
    throw "Handoff inspection style_template_visual_preview thumbnail readiness copy action missing"
}
if ($handoff.style_template_visual_preview.local_thumbnail_readiness_schema -ne "rrkal_displaytools.local_style_thumbnail_readiness.v1") {
    throw "Handoff inspection style_template_visual_preview local thumbnail readiness schema missing"
}
if ($handoff.style_template_visual_preview.local_thumbnail_readiness_fields -notcontains "missing_ids") {
    throw "Handoff inspection style_template_visual_preview local thumbnail readiness missing_ids field missing"
}
if ($handoff.launch_packet_contracts.module_boundary_registry -ne "rrkal_displaytools.module_boundary_registry.v1") {
    throw "Handoff inspection module_boundary_registry launch contract missing or invalid"
}
if ($handoff.launch_packet_contracts.module_decoupling_boundary_contract -ne "rrkal_displaytools.module_decoupling_boundary_contract.v1") {
    throw "Handoff inspection module decoupling boundary contract missing or invalid"
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
if ($handoff.module_boundary_registry.decoupling_boundary_contract_schema -ne "rrkal_displaytools.module_decoupling_boundary_contract.v1") {
    throw "Handoff inspection module decoupling boundary schema missing"
}
if ($handoff.module_boundary_registry.extraction_order -notcontains "contracts/launch_packets.py") {
    throw "Handoff inspection module decoupling extraction order missing contracts first step"
}
if ($handoff.module_boundary_registry.module_boundary_summary_contract_schema -ne "rrkal_displaytools.module_boundary_summary_contract.v1") {
    throw "Handoff inspection module boundary summary contract missing or invalid"
}
if ($handoff.module_boundary_registry.module_boundary_summary_contract.qt_copy_action -ne "copy_module_boundary_summary") {
    throw "Handoff inspection module boundary summary copy action missing"
}
if ($handoff.module_boundary_registry.summary_parameter_fields -notcontains "tk_primary_ui_allowed") {
    throw "Handoff inspection module boundary summary parameter fields missing"
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
if ($handoff.cross_machine_clone_readiness.clone_command -notlike "git clone *RRKAL_displaytools.git") {
    throw "Handoff inspection cross_machine_clone_readiness clone command missing"
}
if ($handoff.cross_machine_clone_readiness.repo_visibility -ne "public") {
    throw "Handoff inspection cross_machine_clone_readiness repo visibility mismatch"
}
if ($handoff.cross_machine_clone_readiness.qt_visible_fields -notcontains "first_run_smoke_command") {
    throw "Handoff inspection cross_machine_clone_readiness Qt visible first-run smoke field missing"
}
if ($handoff.cross_machine_clone_readiness.launcher_options -notcontains "-HandoffFirst") {
    throw "Handoff inspection cross_machine_clone_readiness missing HandoffFirst launcher option"
}
if ($handoff.cross_machine_clone_readiness.handoff_first_command -notlike "*run_qt_panel.ps1 -HandoffFirst") {
    throw "Handoff inspection cross_machine_clone_readiness handoff-first command mismatch"
}
if ($handoff.cross_machine_clone_readiness.first_run_smoke_command -notlike "*scripts/smoke.ps1") {
    throw "Handoff inspection cross_machine_clone_readiness first-run smoke command missing"
}
if ($handoff.cross_machine_clone_readiness.first_run_handoff_command -notlike "*scripts/inspect_handoff.ps1") {
    throw "Handoff inspection cross_machine_clone_readiness first-run handoff command missing"
}
if ($handoff.cross_machine_clone_readiness.clone_reviewer_summary_contract_schema -ne "rrkal_displaytools.clone_reviewer_summary_contract.v1") {
    throw "Handoff inspection clone reviewer summary contract schema missing or invalid"
}
if ($handoff.cross_machine_clone_readiness.clone_reviewer_summary_contract.qt_copy_action -ne "copy_clone_reviewer_summary") {
    throw "Handoff inspection clone reviewer summary copy action missing or invalid"
}
if (-not $handoff.cross_machine_clone_readiness.clone_reviewer_summary_contract.portable) {
    throw "Handoff inspection clone reviewer summary portability flag missing"
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
if ($handoff.profile_launch_readiness.launch_reviewer_summary_contract_schema -ne "rrkal_displaytools.launch_reviewer_summary_contract.v1") {
    throw "Handoff inspection launch reviewer summary contract schema missing or invalid"
}
if ($handoff.profile_launch_readiness.launch_reviewer_summary_contract.qt_copy_action -ne "copy_launch_reviewer_summary") {
    throw "Handoff inspection launch reviewer summary copy action missing or invalid"
}
if (-not $handoff.profile_launch_readiness.launch_reviewer_summary_contract.portable) {
    throw "Handoff inspection launch reviewer summary portability flag missing"
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
if ($handoff.launch_packet_contracts.reviewer_packet_export -ne "rrkal_displaytools.reviewer_packet_export.v1") {
    throw "Handoff inspection reviewer_packet_export launch contract missing or invalid"
}
if ($handoff.reviewer_packet_export.launch_packet_schema -ne "rrkal_displaytools.reviewer_packet_export.v1") {
    throw "Handoff inspection reviewer_packet_export launch schema missing or invalid"
}
if ($handoff.reviewer_packet_export.renderer_capabilities_schema -ne "rrkal_displaytools.reviewer_packet_export.v1") {
    throw "Handoff inspection reviewer_packet_export renderer schema missing or invalid"
}
if ($handoff.reviewer_packet_export.qt_action -ne "export_reviewer_packet_dialog") {
    throw "Handoff inspection reviewer packet Qt action missing or invalid"
}
if ($handoff.reviewer_packet_export.included_summary_fields -notcontains "research_interaction_summary") {
    throw "Handoff inspection reviewer packet research summary field missing"
}
if ($handoff.reviewer_packet_export.included_summary_fields -notcontains "hydrology_lod_summary") {
    throw "Handoff inspection reviewer packet hydrology summary field missing"
}
if ($handoff.reviewer_packet_export.included_summary_fields -notcontains "ocean_material_summary") {
    throw "Handoff inspection reviewer packet ocean summary field missing"
}
if ($handoff.reviewer_packet_export.included_summary_fields -notcontains "style_routes_summary") {
    throw "Handoff inspection reviewer packet style routes summary field missing"
}
if ($handoff.reviewer_packet_export.included_summary_fields -notcontains "module_boundary_summary") {
    throw "Handoff inspection reviewer packet module boundary summary field missing"
}
if ($handoff.reviewer_packet_export.included_packet_fields -notcontains "hydrology_lod_readiness") {
    throw "Handoff inspection reviewer packet hydrology readiness packet field missing"
}
if ($handoff.reviewer_packet_export.included_packet_fields -notcontains "hydrology_lod_runtime_evidence") {
    throw "Handoff inspection reviewer packet hydrology runtime evidence packet field missing"
}
if ($handoff.reviewer_packet_export.included_packet_fields -notcontains "ocean_material_control_port") {
    throw "Handoff inspection reviewer packet ocean material packet field missing"
}
if ($handoff.reviewer_packet_export.included_packet_fields -notcontains "style_profile_renderer_routes") {
    throw "Handoff inspection reviewer packet style routes packet field missing"
}
if ($handoff.reviewer_packet_export.included_packet_fields -notcontains "module_boundary_registry") {
    throw "Handoff inspection reviewer packet module boundary packet field missing"
}
if ($handoff.reviewer_packet_export.included_packet_fields -notcontains "layer_render_plan_performance") {
    throw "Handoff inspection reviewer packet render plan performance packet field missing"
}
if (-not $handoff.reviewer_packet_export.portable) {
    throw "Handoff inspection reviewer packet portability flag missing"
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
if ($handoff.launch_packet_contracts.hydrology_lod_renderer_apply_contract -ne "rrkal_displaytools.hydrology_lod_renderer_apply_contract.v1") {
    throw "Handoff inspection hydrology_lod renderer apply contract missing or invalid"
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
if ($handoff.hydrology_lod_readiness.hydrology_lod_summary_contract_schema -ne "rrkal_displaytools.hydrology_lod_summary_contract.v1") {
    throw "Handoff inspection hydrology_lod summary contract missing or invalid"
}
if ($handoff.hydrology_lod_readiness.hydrology_lod_summary_contract.qt_copy_action -ne "copy_hydrology_lod_summary") {
    throw "Handoff inspection hydrology_lod summary copy action missing"
}
if ($handoff.hydrology_lod_readiness.summary_parameter_fields -notcontains "runtime_state_file") {
    throw "Handoff inspection hydrology_lod summary parameter fields missing"
}
if ($handoff.hydrology_lod_readiness.renderer_apply_contract_schema -ne "rrkal_displaytools.hydrology_lod_renderer_apply_contract.v1") {
    throw "Handoff inspection hydrology_lod renderer apply contract schema missing"
}
if ($handoff.hydrology_lod_readiness.runtime_state_file -ne "state/renderer_layer_runtime_state.json") {
    throw "Handoff inspection hydrology_lod runtime state file mismatch"
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
if ($handoff.hydrology_lod_runtime_evidence.renderer_apply_contract_schema -ne "rrkal_displaytools.hydrology_lod_renderer_apply_contract.v1") {
    throw "Handoff inspection hydrology_lod_runtime_evidence renderer apply contract schema missing"
}
if ($handoff.hydrology_lod_runtime_evidence.ack_file -ne "state/renderer_layer_runtime_ack.json") {
    throw "Handoff inspection hydrology_lod_runtime_evidence ack file mismatch"
}
if ($handoff.hydrology_lod_runtime_evidence.summary_runtime_fields -notcontains "runtime_ack_available") {
    throw "Handoff inspection hydrology_lod runtime summary fields missing"
}
if ($handoff.launch_packet_contracts.ocean_material_control_port -ne "rrkal_displaytools.ocean_material_control_port.v1") {
    throw "Handoff inspection ocean_material_control_port launch contract missing or invalid"
}
if ($handoff.launch_packet_contracts.ocean_material_renderer_apply_contract -ne "rrkal_displaytools.ocean_material_renderer_apply_contract.v1") {
    throw "Handoff inspection ocean material renderer apply contract missing or invalid"
}
if ($handoff.launch_packet_contracts.taichi_ocean_3d_control_panel -ne "rrkal_displaytools.taichi_ocean_3d_control_panel.v1") {
    throw "Handoff inspection Taichi ocean 3D control panel contract missing or invalid"
}
if ($handoff.launch_packet_contracts.sea_state_scalar_sample -ne "rrkal_displaytools.sea_state_scalar_sample.v1") {
    throw "Handoff inspection sea-state scalar sample contract missing or invalid"
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
if ($handoff.ocean_material_control_port.qt_control_panel_schema -ne "rrkal_displaytools.taichi_ocean_3d_control_panel.v1") {
    throw "Handoff inspection Taichi ocean 3D control panel schema missing or invalid"
}
if ($handoff.ocean_material_control_port.qt_dialog_action -ne "open_taichi_ocean_3d_controls") {
    throw "Handoff inspection Taichi ocean 3D control panel dialog action missing"
}
if ($handoff.ocean_material_control_port.render_pipeline_followup -ne "post_decoupling_precompute_layer_render_plan_then_single_render_pass") {
    throw "Handoff inspection Taichi ocean 3D control panel performance followup missing"
}
if ($handoff.ocean_material_control_port.control_board_label_object -ne "ocean3DControlBoardStrip") {
    throw "Handoff inspection Taichi ocean 3D control board strip missing"
}
if ($handoff.ocean_material_control_port.control_board_default_visible -ne $true) {
    throw "Handoff inspection Taichi ocean 3D control board visibility flag missing"
}
if ($handoff.ocean_material_control_port.ocean_material_summary_contract_schema -ne "rrkal_displaytools.ocean_material_summary_contract.v1") {
    throw "Handoff inspection ocean material summary contract missing or invalid"
}
if ($handoff.ocean_material_control_port.ocean_material_summary_contract.qt_copy_action -ne "copy_ocean_material_summary") {
    throw "Handoff inspection ocean material summary copy action missing"
}
if ($handoff.ocean_material_control_port.summary_parameter_fields -notcontains "renderer_apply_status") {
    throw "Handoff inspection ocean material summary parameter fields missing"
}
if ($handoff.ocean_material_control_port.renderer_apply_contract_schema -ne "rrkal_displaytools.ocean_material_renderer_apply_contract.v1") {
    throw "Handoff inspection ocean material renderer apply contract schema missing"
}
if ($handoff.ocean_material_control_port.sea_state_scalar_sample_schema -ne "rrkal_displaytools.sea_state_scalar_sample.v1") {
    throw "Handoff inspection ocean material sea-state scalar sample schema missing"
}
if (-not $handoff.ocean_material_control_port.portable) {
    throw "Handoff inspection ocean material renderer apply contract is not portable"
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
if ($qtPanelSource -notlike "*boundary_highlight_ack_summary_text*") {
    throw "Qt boundary ack summary helper missing"
}
if ($qtPanelSource -notlike "*identity_warning={self.boundary_identity_warning_text()}*") {
    throw "Qt boundary copy summary identity warning missing"
}
if ($qtPanelSource -notlike "*renderer_ack={self.boundary_highlight_ack_summary_text()}*") {
    throw "Qt boundary copy summary renderer ack missing"
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
if ($qtPanelSource -notlike "*pinProjectionNote*") {
    throw "Qt panel Pin projection note object missing"
}
if ($qtPanelSource -notlike "*qt_projection_note*") {
    throw "Qt panel Pin projection note contract key missing"
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
if ($qtPanelSource -notlike "*layerOperationSummary*") {
    throw "Qt Layers operation summary label is missing"
}
if ($qtPanelSource -notlike "*Layer operation summary:*") {
    throw "Qt Layers operation summary text is missing"
}
if ($qtPanelSource -notlike "*active_layer_operation_summary_text*") {
    throw "Qt active layer operation summary helper is missing"
}
if ($qtPanelSource -notlike "*active_layer_operation_summary*") {
    throw "Qt launch packet active layer operation summary field is missing"
}
if ($qtPanelSource -notlike "*layerOperationEvent*") {
    throw "Qt Layers operation event label is missing"
}
if ($qtPanelSource -notlike "*Last layer operation:*") {
    throw "Qt Layers operation event text is missing"
}
if ($qtPanelSource -notlike "*set_layer_operation_status*") {
    throw "Qt layer operation status helper is missing"
}
if ($qtPanelSource -notlike '*self.set_layer_operation_status(f"已 Solo 選取圖層*') {
    throw "Qt Solo selected layer operation feedback is missing"
}
if ($qtPanelSource -notlike '*self.set_layer_operation_status("已還原 Solo 前圖層可見性"*') {
    throw "Qt restore Solo layer operation feedback is missing"
}
if ($qtPanelSource -notlike '*self.set_layer_operation_status("已回復上一個 layer undo snapshot"*') {
    throw "Qt layer undo operation feedback is missing"
}
if ($qtPanelSource -notlike "*Layer group toggle:*") {
    throw "Qt layer group toggle operation feedback is missing"
}
if ($qtPanelSource -notlike '*self.set_layer_operation_status(f"Applied layer preset:*') {
    throw "Qt layer preset operation feedback is missing"
}
if ($qtPanelSource -notlike "*last_layer_operation*") {
    throw "Qt launch packet last layer operation field is missing"
}
if ($qtPanelSource -notlike "*layer_operation_feedback*") {
    throw "Qt layer operation feedback packet field is missing"
}
if ($qtPanelSource -notlike "*rrkal_displaytools.layer_operation_feedback.v1*") {
    throw "Qt layer operation feedback schema is missing"
}
if ($qtPanelSource -notlike "*layerControlFeedbackStrip*") {
    throw "Qt layer control feedback strip label is missing"
}
if ($qtPanelSource -notlike "*collect_layer_control_feedback_strip*") {
    throw "Qt layer control feedback strip collector is missing"
}
if ($qtPanelSource -notlike "*rrkal_displaytools.layer_control_feedback_strip.v1*") {
    throw "Qt layer control feedback strip schema is missing"
}
if ($qtPanelSource -notlike "*layerSelectionAffordance*") {
    throw "Qt layer selection affordance label is missing"
}
if ($qtPanelSource -notlike "*collect_layer_selection_affordance*") {
    throw "Qt layer selection affordance collector is missing"
}
if ($qtPanelSource -notlike "*rrkal_displaytools.layer_selection_affordance.v1*") {
    throw "Qt layer selection affordance schema is missing"
}
if ($qtPanelSource -notlike "*layerHoverAffordance*") {
    throw "Qt layer hover affordance label is missing"
}
if ($qtPanelSource -notlike "*layer_hover_event_targets*") {
    throw "Qt layer hover event target map is missing"
}
if ($qtPanelSource -notlike "*layer_hover_layer_key*") {
    throw "Qt layer hover state key is missing"
}
if ($qtPanelSource -notlike "*set_layer_hover_affordance*") {
    throw "Qt layer hover affordance handler is missing"
}
if ($qtPanelSource -notlike "*rrkal_displaytools.layer_hover_affordance.v1*") {
    throw "Qt layer hover affordance schema is missing"
}
if ($qtPanelSource -notlike "*rrkal_displaytools.layer_lock_affordance.v1*") {
    throw "Qt layer lock affordance schema is missing"
}
if ($qtPanelSource -notlike "*collect_layer_lock_affordance*") {
    throw "Qt layer lock affordance collector is missing"
}
if ($qtPanelSource -notlike '*locked="true"*') {
    throw "Qt layer locked row stylesheet selector is missing"
}
if ($qtPanelSource -notlike '*setProperty("locked"*') {
    throw "Qt layer locked row property update is missing"
}
if ($qtPanelSource -notlike "*disabled_controls_when_locked*") {
    throw "Qt layer lock disabled controls contract is missing"
}
if ($qtPanelSource -notlike "*layer_opacity*setEnabled(not is_locked)*") {
    throw "Qt layer locked opacity disable behavior is missing"
}
if ($qtPanelSource -notlike "*layer_blends*setEnabled(not is_locked)*") {
    throw "Qt layer locked blend disable behavior is missing"
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
if ($qtPanelSource -notlike "*Copy launch summary*") {
    throw "Qt launch reviewer copy summary button is missing"
}
if ($qtPanelSource -notlike "*copy_launch_reviewer_summary*") {
    throw "Qt launch reviewer copy summary action is missing"
}
if ($qtPanelSource -notlike "*launch_reviewer_summary_text*") {
    throw "Qt launch reviewer summary formatter is missing"
}
if ($qtPanelSource -notlike "*Export reviewer packet*") {
    throw "Qt reviewer packet export button is missing"
}
if ($qtPanelSource -notlike "*export_reviewer_packet_dialog*") {
    throw "Qt reviewer packet export action is missing"
}
if ($qtPanelSource -notlike "*collect_reviewer_packet*") {
    throw "Qt reviewer packet collector is missing"
}
if ($qtPanelSource -notlike '*"hydrology_lod_summary": self.hydrology_lod_summary_text()*') {
    throw "Qt reviewer packet hydrology summary output is missing"
}
if ($qtPanelSource -notlike '*"ocean_material_summary": self.ocean_material_summary_text()*') {
    throw "Qt reviewer packet ocean summary output is missing"
}
if ($qtPanelSource -notlike '*"style_routes_summary": self.style_routes_summary_text()*') {
    throw "Qt reviewer packet style routes summary output is missing"
}
if ($qtPanelSource -notlike '*"module_boundary_summary": self.module_boundary_summary_text()*') {
    throw "Qt reviewer packet module boundary summary output is missing"
}
if ($qtPanelSource -notlike '*"hydrology_lod_readiness": self.collect_hydrology_lod_readiness()*') {
    throw "Qt reviewer packet hydrology readiness output is missing"
}
if ($qtPanelSource -notlike '*"hydrology_lod_runtime_evidence": self.collect_hydrology_lod_runtime_evidence()*') {
    throw "Qt reviewer packet hydrology runtime evidence output is missing"
}
if ($qtPanelSource -notlike '*"ocean_material_control_port": self.collect_ocean_material_control_port()*') {
    throw "Qt reviewer packet ocean material output is missing"
}
if ($qtPanelSource -notlike '*"style_profile_renderer_routes": self.collect_style_profile_renderer_routes()*') {
    throw "Qt reviewer packet style routes output is missing"
}
if ($qtPanelSource -notlike '*"module_boundary_registry": self.collect_module_boundary_registry()*') {
    throw "Qt reviewer packet module boundary registry output is missing"
}
if ($qtPanelSource -notlike '*"layer_render_plan_performance": self.collect_layer_render_plan_performance()*') {
    throw "Qt reviewer packet render plan performance output is missing"
}
if ($qtPanelSource -notlike "*show_ocean_material_control_port*") {
    throw "Qt ocean material control port JSON action is missing"
}
if ($qtPanelSource -notlike "*copy_ocean_material_summary*") {
    throw "Qt ocean material copy summary action is missing"
}
if ($qtPanelSource -notlike "*Ocean material: *governance=RRKAL-owned provider/cache*") {
    throw "Qt ocean material portable summary text missing"
}
if ($qtPanelSource -notlike "*Ocean port*") {
    throw "Qt Ocean port action button is missing"
}
if ($qtPanelSource -notlike "*Taichi 3D Ocean controls*") {
    throw "Qt Taichi 3D Ocean controls button is missing"
}
if ($qtPanelSource -notlike "*Open: Ocean 3D controls*") {
    throw "Qt Ocean 3D action button is missing"
}
if ($qtPanelSource -notlike "*open_taichi_ocean_3d_controls*") {
    throw "Qt Taichi ocean 3D control dialog handler is missing"
}
if ($qtPanelSource -notlike "*taichiOcean3DControlPanel*") {
    throw "Qt Taichi ocean 3D control panel label is missing"
}
if ($qtPanelSource -notlike "*ocean3DControlBoardStrip*") {
    throw "Qt Taichi ocean 3D default-visible control board strip is missing"
}
if ($qtPanelSource -notlike "*ocean3DControlBoardButton*") {
    throw "Qt Taichi ocean 3D default-visible control board button is missing"
}
if ($qtPanelSource -notlike "*control_board_default_visible*") {
    throw "Qt Taichi ocean 3D control board visibility contract is missing"
}
if ($qtPanelSource -notlike "*post_decoupling_precompute_layer_render_plan_then_single_render_pass*") {
    throw "Qt Taichi ocean 3D performance followup marker is missing"
}
if ($qtPanelSource -notlike "*show_hydrology_lod_status*") {
    throw "Qt hydrology LOD JSON action is missing"
}
if ($qtPanelSource -notlike "*copy_hydrology_lod_summary*") {
    throw "Qt hydrology LOD copy summary action is missing"
}
if ($qtPanelSource -notlike "*Hydrology/LOD: *governance=RRKAL-owned data/cache*") {
    throw "Qt hydrology LOD portable summary text missing"
}
if ($qtPanelSource -notlike "*Hydro LOD*") {
    throw "Qt Hydro LOD action button is missing"
}
if ($qtPanelSource -notlike "*show_style_renderer_routes*") {
    throw "Qt style renderer routes JSON action is missing"
}
if ($qtPanelSource -notlike "*copy_style_routes_summary*") {
    throw "Qt style routes copy summary action is missing"
}
if ($qtPanelSource -notlike "*Style routes: *boundary=RRKAL-owned data/cache*") {
    throw "Qt style routes portable summary text missing"
}
if ($qtPanelSource -notlike "*Style routes*") {
    throw "Qt Style routes action button is missing"
}
if ($qtPanelSource -notlike "*styleTemplateVisualPreview*") {
    throw "Qt style template visual preview surface is missing"
}
if ($qtPanelSource -notlike "*collect_style_template_visual_preview*") {
    throw "Qt style template visual preview collector is missing"
}
if ($qtPanelSource -notlike "*apply_style_template_preview_card*") {
    throw "Qt style template visual preview click action is missing"
}
if ($qtPanelSource -notlike "*styleTemplateCard_*") {
    throw "Qt style template visual preview cards are missing"
}
if ($qtPanelSource -notlike "*state/style_previews*") {
    throw "Qt style template thumbnail slot path is missing"
}
if ($qtPanelSource -notlike "*thumbnail_review_command*") {
    throw "Qt style template thumbnail review command is missing"
}
if ($qtPanelSource -notlike "*Inspect: Style thumbs*") {
    throw "Qt style thumbnail slots action button is missing"
}
if ($qtPanelSource -notlike "*show_style_thumbnail_slots*") {
    throw "Qt style thumbnail slots Inspect handler is missing"
}
if ($qtPanelSource -notlike "*local_style_thumbnail_path*") {
    throw "Qt style thumbnail local path resolver is missing"
}
if ($qtPanelSource -notlike "*setIcon(QtGui.QIcon*") {
    throw "Qt style thumbnail card icon loading is missing"
}
if ($qtPanelSource -notlike "*setIconSize(QtCore.QSize(96, 54))*") {
    throw "Qt style thumbnail card icon size is missing"
}
if ($qtPanelSource -notlike "*Copy style thumbs command*") {
    throw "Qt style thumbnail batch copy button is missing"
}
if ($qtPanelSource -notlike "*copy_style_thumbnail_batch_command*") {
    throw "Qt style thumbnail batch copy handler is missing"
}
if ($qtPanelSource -notlike "*thumbnail_batch_command*") {
    throw "Qt style thumbnail batch command contract is missing"
}
if ($qtPanelSource -notlike "*styleThumbnailReadiness*") {
    throw "Qt style thumbnail readiness label is missing"
}
if ($qtPanelSource -notlike "*Style thumbnails: ready=*") {
    throw "Qt style thumbnail readiness summary text is missing"
}
if ($qtPanelSource -notlike "*thumbnail_readiness_schema*") {
    throw "Qt style thumbnail readiness contract is missing"
}
if ($qtPanelSource -notlike "*Copy style thumb status*") {
    throw "Qt style thumbnail readiness copy button is missing"
}
if ($qtPanelSource -notlike "*copy_style_thumbnail_readiness_summary*") {
    throw "Qt style thumbnail readiness copy handler is missing"
}
if ($qtPanelSource -notlike "*style_thumbnail_readiness_summary_text*") {
    throw "Qt style thumbnail readiness summary formatter is missing"
}
if ($qtPanelSource -notlike "*collect_local_style_thumbnail_readiness*") {
    throw "Qt local style thumbnail readiness collector is missing"
}
if ($qtPanelSource -notlike "*local_thumbnail_readiness*") {
    throw "Qt style thumbnail slots JSON local readiness output is missing"
}
if ($qtPanelSource -notlike "*rrkal_displaytools.local_style_thumbnail_readiness.v1*") {
    throw "Qt local style thumbnail readiness schema is missing"
}
if ($qtPanelSource -like "*packet.get('preview_count')*selected={current_style}*") {
    throw "Qt style thumbnail readiness copy handler has stale undefined packet reference"
}
if ($qtPanelSource -like "*selected={current_style}*") {
    throw "Qt style thumbnail readiness copy handler has stale undefined current_style reference"
}
if ($qtPanelSource -notlike "*show_module_boundary_registry*") {
    throw "Qt module boundary registry JSON action is missing"
}
if ($qtPanelSource -notlike "*copy_module_boundary_summary*") {
    throw "Qt module boundary copy summary action is missing"
}
if ($qtPanelSource -notlike "*Module seams: *boundary=RRKAL-owned data/cache*") {
    throw "Qt module boundary portable summary text missing"
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
if ($qtPanelSource -notlike "*Copy clone summary*") {
    throw "Qt clone reviewer copy summary button is missing"
}
if ($qtPanelSource -notlike "*copy_clone_reviewer_summary*") {
    throw "Qt clone reviewer copy summary action is missing"
}
if ($qtPanelSource -notlike "*clone_reviewer_summary_text*") {
    throw "Qt clone reviewer summary formatter is missing"
}
if ($qtPanelSource -notlike "*first_run_smoke_command*") {
    throw "Qt clone readiness first-run smoke command is missing"
}
if ($qtPanelSource -notlike "*clone_command*") {
    throw "Qt clone readiness clone command field is missing"
}
if ($qtPanelSource -notlike "*visibility=*") {
    throw "Qt clone readiness visible repo visibility text is missing"
}
if ($qtPanelSource -notlike "*first smoke=*") {
    throw "Qt clone readiness label first smoke text is missing"
}
if ($qtPanelSource -notlike "*first handoff=*") {
    throw "Qt clone readiness label first handoff text is missing"
}
if ($qtPanelSource -notlike "*Replay/contracts: inspect portable UI/profile replay coverage JSON*") {
    throw "Qt contract inspector tooltips are missing"
}
if ($qtPanelSource -notlike "*Replay/contracts: inspect Timeline keyframes, runtime state and export options JSON*") {
    throw "Qt Timeline inspector tooltip is missing"
}
if ($qtPanelSource -notlike "*Renderer ports: inspect scalar ocean material and sea-state handoff JSON*") {
    throw "Qt Renderer ports inspector tooltip is missing"
}
if ($qtPanelSource -notlike "*Renderer ports: inspect layer capability matrix JSON*") {
    throw "Qt Layer matrix inspector tooltip is missing"
}
if ($qtPanelSource -notlike "*Inspect: Render plan perf*") {
    throw "Qt render plan performance inspector button is missing"
}
if ($qtPanelSource -notlike "*show_layer_render_plan_performance*") {
    throw "Qt render plan performance inspector handler is missing"
}
if ($qtPanelSource -notlike "*collect_layer_render_plan_performance*") {
    throw "Qt render plan performance collector is missing"
}
if ($qtPanelSource -notlike "*submit_single_taichi_render_pass*") {
    throw "Qt render plan performance single-pass marker is missing"
}
if ($qtPanelSource -notlike "*layer_render_plan_runtime_snapshot*") {
    throw "Qt/render source layer render plan runtime snapshot helper is missing"
}
if ($qtPanelSource -notlike "*metadata_sidecar_field*: *layer_render_plan*") {
    throw "Qt render plan performance metadata sidecar contract is missing"
}
if ($qtPanelSource -notlike "*apply_layer_render_plan_composition*") {
    throw "Qt render plan performance composition helper contract is missing"
}
if ($qtPanelSource -notlike "*compiled_layer_render_plan.v1*") {
    throw "Qt render plan performance compiled plan contract is missing"
}
if ($qtPanelSource -notlike "*layer_render_plan_cache_diagnostics.v1*") {
    throw "Qt render plan cache diagnostics contract is missing"
}
if ($qtPanelSource -notlike "*collect_layer_render_plan_cache_diagnostics*") {
    throw "Qt render plan cache diagnostics collector is missing"
}
if ($qtPanelSource -notlike "*latest_renderer_metadata_path*") {
    throw "Qt render plan cache diagnostics metadata resolver is missing"
}
if ($qtPanelSource -notlike "*metadata_sidecar_missing*") {
    throw "Qt render plan cache diagnostics missing-sidecar status is missing"
}
if ($qtPanelSource -notlike "*Displayed layer render-plan performance and cache diagnostics*") {
    throw "Qt render plan cache diagnostics inspector status is missing"
}
if ($qtPanelSource -notlike "*Research interaction: inspect Boundary emphasis, identity warning and renderer ack JSON*") {
    throw "Qt Research interaction inspector tooltip is missing"
}
if ($qtPanelSource -notlike "*Visual review: inspect latest renderer thumbnail PNG*") {
    throw "Qt Visual review renderer thumbnail tooltip is missing"
}
if ($qtPanelSource -notlike "*Visual review: inspect file-based live renderer preview frame*") {
    throw "Qt Visual review live preview tooltip is missing"
}
if ($qtPanelSource -notlike "*Research interaction: inspect Qt Canvas state, preview metadata and provenance summary*") {
    throw "Qt Canvas state inspector tooltip is missing"
}
if ($qtPanelSource -notlike "*Inspect: Layer matrix*") {
    throw "Qt Layer matrix inspector button is missing"
}
if ($qtPanelSource -notlike "*Inspect: Layer runtime*") {
    throw "Qt Layer runtime inspector button is missing"
}
if ($qtPanelSource -notlike "*Inspect: Layer pick*") {
    throw "Qt Layer pick inspector button is missing"
}
if ($qtPanelSource -notlike "*Inspect: Selection state*") {
    throw "Qt Selection state inspector button is missing"
}
if ($qtPanelSource -notlike "*Inspect: Layer ops*") {
    throw "Qt Layer ops inspector button is missing"
}
if ($qtPanelSource -notlike "*show_layer_operation_feedback*") {
    throw "Qt Layer operation feedback Inspect handler is missing"
}
if ($qtPanelSource -notlike "*setAccessibleDescription*") {
    throw "Qt contract inspector accessible descriptions are missing"
}
if ($qtPanelSource -notlike "*Pin pick*") {
    throw "Qt Pin pick action button is missing"
}
if ($qtPanelSource -notlike "*pinList*") {
    throw "Qt Pin list object name missing"
}
if ($qtPanelSource -notlike "*copy_pin_overlay_summary*") {
    throw "Qt Pin overlay copy summary action missing"
}
if ($qtPanelSource -notlike "*pin_overlay_summary_text*") {
    throw "Qt Pin overlay summary formatter missing"
}
if ($qtPanelSource -notlike "*occlusion_statuses*") {
    throw "Qt Pin overlay summary occlusion statuses missing"
}
if ($qtPanelSource -notlike "*pinOcclusionLegend*") {
    throw "Qt Pin occlusion legend object is missing"
}
if ($qtPanelSource -notlike "*Research interaction: inspect renderer Pin hover/click pick bridge JSON*") {
    throw "Qt Pin pick action tooltip is missing"
}
if ($qtPanelSource -notlike "*Selection state: inspect active Qt layer selection, pick history and renderer target JSON*") {
    throw "Qt Selection state inspector tooltip is missing"
}
if ($qtPanelSource -notlike "*Cursor geo*") {
    throw "Qt Cursor geo action button is missing"
}
if ($qtPanelSource -notlike "*show_cursor_geodesy_state*") {
    throw "Qt Cursor geo JSON action is missing"
}
if ($qtPanelSource -notlike "*Research interaction: inspect mouse cursor latitude/longitude geodesy bridge JSON*") {
    throw "Qt Cursor geo action tooltip is missing"
}
if ($qtPanelSource -notlike "*Copy cursor summary*") {
    throw "Qt Cursor geo copy summary button is missing"
}
if ($qtPanelSource -notlike "*copy_cursor_geodesy_summary*") {
    throw "Qt Cursor geo copy summary action is missing"
}
if ($qtPanelSource -notlike "*cursor_geodesy_summary_text*") {
    throw "Qt Cursor geo summary formatter is missing"
}
if ($qtPanelSource -notlike "*Copy research summary*") {
    throw "Qt research interaction copy summary button is missing"
}
if ($qtPanelSource -notlike "*copy_research_interaction_summary*") {
    throw "Qt research interaction copy summary action is missing"
}
if ($qtPanelSource -notlike "*research_interaction_summary_text*") {
    throw "Qt research interaction summary formatter is missing"
}
if ($qtPanelSource -notlike "*Boundary JSON*") {
    throw "Qt Boundary JSON action button is missing"
}
if ($qtPanelSource -notlike "*Inspect: Profile replay*") {
    throw "Qt inspector action prefix is missing"
}
if ($qtPanelSource -notlike "*Inspect: Timeline*") {
    throw "Qt Timeline inspector button is missing"
}
if ($qtPanelSource -notlike "*Inspect: Canvas state*") {
    throw "Qt Canvas state inspector button is missing"
}
if ($qtPanelSource -notlike "*Inspect: Boundary JSON*") {
    throw "Qt Boundary JSON inspector prefix is missing"
}
if ($qtPanelSource -notlike "*Inspect: Renderer thumbnail*") {
    throw "Qt Renderer thumbnail inspector button is missing"
}
if ($qtPanelSource -notlike "*Inspect: Live preview*") {
    throw "Qt Live preview inspector button is missing"
}
if ($qtPanelSource -notlike '*renderer_menu.addAction("Inspect: Renderer thumbnail"*') {
    throw "Qt Renderer menu thumbnail Inspect action is missing"
}
if ($qtPanelSource -notlike '*renderer_menu.addAction("Inspect: Live preview"*') {
    throw "Qt Renderer menu live preview Inspect action is missing"
}
if ($qtPanelSource -notlike "*show_timeline_runtime_state*") {
    throw "Qt Timeline runtime state action is missing"
}
if ($qtPanelSource -notlike "*actionSectionHeader*") {
    throw "Qt Actions section headers are missing"
}
if ($qtPanelSource -notlike "*Inspect: Replay/contracts*") {
    throw "Qt Actions Replay/contracts section is missing"
}
if ($qtPanelSource -notlike "*Inspect: Research interaction*") {
    throw "Qt Actions Research interaction section is missing"
}
if ($qtPanelSource -notlike "*Inspect: Visual review*") {
    throw "Qt Actions Visual review section is missing"
}
if ($qtPanelSource -notlike "*visual_review_readiness_packet*") {
    throw "Qt panel visual review readiness packet missing"
}
if ($qtPanelSource -notlike "*visual_readiness_button*") {
    throw "Qt panel Visual readiness button missing"
}
if ($qtPanelSource -notlike "*show_visual_review_readiness*") {
    throw "Qt panel Visual readiness Inspect action missing"
}
if ($qtPanelSource -notlike "*collect_visual_review_readiness*") {
    throw "Qt panel Visual readiness collector missing"
}
if ($qtPanelSource -notlike "*runtime_artifact_summary_schema*") {
    throw "Qt panel Visual readiness runtime artifact summary missing"
}
if ($qtPanelSource -notlike "*latest_renderer_thumbnail_path()*") {
    throw "Qt panel Visual readiness thumbnail artifact check missing"
}
if ($qtPanelSource -notlike "*RENDERER_PREVIEW_FRAME_PATH.exists()*") {
    throw "Qt panel Visual readiness live preview artifact check missing"
}
if ($qtPanelSource -notlike "*visualReviewReadiness*") {
    throw "Qt panel Visual readiness visible label missing"
}
if ($qtPanelSource -notlike "*visual_review_readiness_summary_text*") {
    throw "Qt panel Visual readiness summary formatter missing"
}
if ($qtPanelSource -notlike "*update_visual_review_readiness_label*") {
    throw "Qt panel Visual readiness label updater missing"
}
if ($qtPanelSource -notlike "*copy_visual_summary_button*") {
    throw "Qt panel Visual readiness copy summary button missing"
}
if ($qtPanelSource -notlike "*copy_visual_review_readiness_summary*") {
    throw "Qt panel Visual readiness copy summary action missing"
}
if ($qtPanelSource -notlike "*copy_summary_contract*") {
    throw "Qt panel Visual readiness copy summary contract missing"
}
if ($qtPanelSource -notlike "*copy_selection_summary_button*") {
    throw "Qt panel Layer selection copy summary button missing"
}
if ($qtPanelSource -notlike "*layer_selection_summary_text*") {
    throw "Qt panel Layer selection summary formatter missing"
}
if ($qtPanelSource -notlike "*copy_layer_selection_summary*") {
    throw "Qt panel Layer selection copy summary action missing"
}
if ($qtPanelSource -notlike "*show_boundary_state*") {
    throw "Qt Boundary JSON action is missing"
}
if ($qtPanelSource -notlike "*copy_boundary_summary_button*") {
    throw "Qt Boundary summary copy button missing"
}
if ($qtPanelSource -notlike "*boundary_emphasis_summary_text*") {
    throw "Qt Boundary summary formatter missing"
}
if ($qtPanelSource -notlike "*copy_boundary_emphasis_summary*") {
    throw "Qt Boundary summary copy action missing"
}
if ($qtPanelSource -notlike "*contrast={packet.get('contrast')}*gamma={packet.get('gamma')}*breathing={packet.get('breathing_enabled')}@{packet.get('breathing_period_s')}s*") {
    throw "Qt Boundary summary tuning fields missing"
}
if ($qtPanelSource -notlike "*Research interaction: inspect Boundary emphasis, identity warning and renderer ack JSON*") {
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
if ($qtPanelSource -notlike "*qt_inspector_action_groups*") {
    throw "Qt profile UI state replay inspector action groups are missing"
}

$rendererSource = Get-Content -Raw -Encoding UTF8 taichi_global_bathymetry.py
if ($rendererSource -notlike "*def layer_render_plan_runtime_snapshot*") {
    throw "Renderer layer render plan runtime snapshot helper is missing"
}
if ($rendererSource -notlike "*def layer_render_plan_composition_steps*") {
    throw "Renderer layer render plan composition steps helper is missing"
}
if ($rendererSource -notlike "*def apply_layer_render_plan_composition*") {
    throw "Renderer layer render plan composition apply helper is missing"
}
if ($rendererSource -notlike "*def compile_layer_render_plan*") {
    throw "Renderer compiled layer render plan helper is missing"
}
if ($rendererSource -notlike "*def layer_render_plan_cache_key*") {
    throw "Renderer layer render plan cache key helper is missing"
}
if ($rendererSource -notlike '*"cache_status": "compiled"*') {
    throw "Renderer compiled layer render plan cache status field is missing"
}
if ($rendererSource -notlike '*cache_status*reused*') {
    throw "Renderer compiled layer render plan reuse branch is missing"
}
if ($rendererSource -notlike '*"layer_render_plan": getattr(self, "layer_render_plan_snapshot"*') {
    if ($rendererSource -notlike '*"layer_render_plan": getattr(self, "compiled_layer_render_plan"*') {
        throw "Renderer metadata layer render plan sidecar field is missing"
    }
}
if ($rendererSource -notlike "*self.layer_render_plan_snapshot = self.layer_render_plan_runtime_snapshot*") {
    throw "Renderer render_if_needed does not update the layer render plan snapshot"
}
if ($rendererSource -notlike "*self.frame_rgba = self.apply_layer_render_plan_composition(*") {
    throw "Renderer render_if_needed is not using the layer render plan composition helper"
}
if ($rendererSource -notlike "*self.compiled_layer_render_plan = self.compile_layer_render_plan*") {
    throw "Renderer render_if_needed does not compile the layer render plan before composition"
}
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
if ($rendererSource -notlike "*research_interaction*") {
    throw "Renderer capability profile UI state replay inspector group missing"
}
if ($rendererSource -notlike "*visual_review*") {
    throw "Renderer capability profile UI state replay visual review group missing"
}
if ($rendererSource -notlike "*layer_operation_feedback_packet*") {
    throw "Renderer capability layer operation feedback contract missing"
}
if ($rendererSource -notlike "*layer_control_feedback_strip_packet*") {
    throw "Renderer capability layer control feedback strip contract missing"
}
if ($rendererSource -notlike "*layer_selection_affordance_packet*") {
    throw "Renderer capability layer selection affordance contract missing"
}
if ($rendererSource -notlike "*layer_hover_affordance_packet*") {
    throw "Renderer capability layer hover affordance contract missing"
}
if ($rendererSource -notlike "*layer_lock_affordance_packet*") {
    throw "Renderer capability layer lock affordance contract missing"
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
if ($launchPacketSource -notmatch 'qt_inspector_action_groups') {
    throw "Launch packet profile UI state replay inspector groups missing"
}
if ($launchPacketSource -notmatch 'visual_review') {
    throw "Launch packet profile UI state replay visual review group missing"
}
if ($launchPacketSource -notmatch 'layer_operation_feedback') {
    throw "Launch packet layer operation feedback field missing"
}
if ($launchPacketSource -notmatch 'layer_control_feedback_strip') {
    throw "Launch packet layer control feedback strip field missing"
}
if ($launchPacketSource -notmatch 'layer_selection_affordance') {
    throw "Launch packet layer selection affordance field missing"
}
if ($launchPacketSource -notmatch 'layer_hover_affordance') {
    throw "Launch packet layer hover affordance field missing"
}
if ($launchPacketSource -notmatch 'layer_lock_affordance') {
    throw "Launch packet layer lock affordance field missing"
}
if ($handoffInspectorSource -notmatch 'profile_ui_state_replay') {
    throw "Handoff inspection profile UI state replay output is missing"
}
if ($handoffInspectorSource -notmatch 'layer_operation_feedback') {
    throw "Handoff inspection layer operation feedback output is missing"
}
if ($handoffInspectorSource -notmatch 'layer_control_feedback_strip') {
    throw "Handoff inspection layer control feedback strip output is missing"
}
if ($handoffInspectorSource -notmatch 'layer_selection_affordance') {
    throw "Handoff inspection layer selection affordance output is missing"
}
if ($handoffInspectorSource -notmatch 'layer_hover_affordance') {
    throw "Handoff inspection layer hover affordance output is missing"
}
if ($handoffInspectorSource -notmatch 'layer_lock_affordance') {
    throw "Handoff inspection layer lock affordance output is missing"
}
if ($handoffInspectorSource -notmatch 'profile_visual_quick_review') {
    throw "Handoff inspection profile visual quick review output is missing"
}
if ($handoffInspectorSource -notmatch 'visual_review_readiness') {
    throw "Handoff inspection visual review readiness output is missing"
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
if ($profileSchemaDoc -notmatch 'layer_runtime') {
    throw "Profile schema docs missing layer runtime inspector action id"
}
if ($profileSchemaDoc -notmatch 'layer_matrix') {
    throw "Profile schema docs missing layer matrix inspector action id"
}
if ($profileSchemaDoc -notmatch 'timeline') {
    throw "Profile schema docs missing Timeline inspector action id"
}
if ($profileSchemaDoc -notmatch 'canvas_state') {
    throw "Profile schema docs missing Canvas state inspector action id"
}
if ($profileSchemaDoc -notmatch 'qt_inspector_action_groups') {
    throw "Profile schema docs missing profile UI state replay inspector action groups"
}
if ($profileSchemaDoc -notmatch 'visual_review') {
    throw "Profile schema docs missing visual review inspector action group"
}
if ($profileSchemaDoc -notmatch 'renderer_thumbnail') {
    throw "Profile schema docs missing renderer thumbnail inspector action"
}
if ($profileSchemaDoc -notmatch 'selection_state') {
    throw "Profile schema docs missing selection state inspector action"
}
if ($profileSchemaDoc -notmatch 'layer_operation_feedback') {
    throw "Profile schema docs missing layer operation feedback inspector action"
}

$cloneQuickstartDoc = Get-Content -LiteralPath (Join-Path $BoundaryIdentityRoot "docs\QUICKSTART_CLONE.zh-TW.md") -Raw -Encoding UTF8
if ($cloneQuickstartDoc -notmatch 'Inspect: Clone ready') {
    throw "Clone quickstart missing Qt Inspect Clone ready guidance"
}
if ($cloneQuickstartDoc -notmatch 'Inspect: Boundary JSON') {
    throw "Clone quickstart missing Qt Inspect Boundary JSON guidance"
}
if ($cloneQuickstartDoc -notmatch 'Inspect: Live preview') {
    throw "Clone quickstart missing Qt Inspect Live preview guidance"
}
if ($cloneQuickstartDoc -notmatch 'Inspect: Selection state') {
    throw "Clone quickstart missing Qt Inspect Selection state guidance"
}
if ($cloneQuickstartDoc -notmatch 'Inspect: Layer ops') {
    throw "Clone quickstart missing Qt Inspect Layer ops guidance"
}
if ($cloneQuickstartDoc -notmatch 'Replay/contracts') {
    throw "Clone quickstart missing Qt Inspect Replay/contracts group guidance"
}
if ($cloneQuickstartDoc -notmatch 'Research interaction') {
    throw "Clone quickstart missing Qt Inspect Research interaction group guidance"
}
if ($cloneQuickstartDoc -notmatch 'Inspect: Canvas state') {
    throw "Clone quickstart missing Qt Inspect Canvas state guidance"
}

Write-Host "Smoke passed."
