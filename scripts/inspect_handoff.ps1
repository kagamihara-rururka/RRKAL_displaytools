$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

function Invoke-JsonPythonCommand {
    param(
        [string[]]$ArgumentList
    )

    $text = & py -3 @ArgumentList
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: py -3 $($ArgumentList -join ' ')"
    }
    $raw = $text -join "`n"
    $jsonStart = $raw.IndexOf("{")
    if ($jsonStart -lt 0) {
        throw "JSON payload not found: py -3 $($ArgumentList -join ' ')"
    }
    return $raw.Substring($jsonStart) | ConvertFrom-Json
}

$capabilities = Invoke-JsonPythonCommand @("taichi_global_bathymetry.py", "--print-renderer-capabilities")
$closedLoop = Invoke-JsonPythonCommand @("taichi_global_bathymetry.py", "--print-closed-loop-status")
$launchPacket = Invoke-JsonPythonCommand @("scripts\export_launch_packet.py", "--template", "fast_synthetic")

$profileUiGroups = @($launchPacket.profile_ui_state_replay.qt_inspector_action_groups)
$researchInteractionActions = @(($profileUiGroups | Where-Object { $_.id -eq "research_interaction" } | Select-Object -First 1).action_ids)
$visualReviewActions = @(($profileUiGroups | Where-Object { $_.id -eq "visual_review" } | Select-Object -First 1).action_ids)
$visualReviewReadiness = $launchPacket.visual_review_readiness
$visualReviewReadinessCapabilities = $capabilities.visual_review_readiness
$visualFeatureClosureMatrix = $launchPacket.visual_feature_closure_matrix
$visualFeatureClosureMatrixCapabilities = $capabilities.visual_feature_closure_matrix
$rendererOutputArtifactContract = $launchPacket.renderer_output_artifact_contract
$rendererOutputArtifactContractCapabilities = $capabilities.renderer_output_artifact_contract
$layerRenderPlanPerformance = $launchPacket.layer_render_plan_performance
$layerRenderPlanPerformanceCapabilities = $capabilities.layer_render_plan_performance

$summary = [ordered]@{
    schema = "rrkal_displaytools.handoff_inspection.v1"
    repo_role = "RRKAL displaytools renderer/UI handoff inspection"
    ui_handoff_contracts = @{
        schema = $capabilities.ui_handoff_contracts.schema
        contracts = @($capabilities.ui_handoff_contracts.contracts)
        pending = @($capabilities.ui_handoff_contracts.pending)
    }
    closed_loop_ids = @($closedLoop.closed | ForEach-Object { $_.id })
    partial_ids = @($closedLoop.partial | ForEach-Object { $_.id })
    launch_packet_contracts = @{
        canvas_preview = $launchPacket.canvas_preview.schema
        active_layer_diagnostics = $launchPacket.active_layer_diagnostics.schema
        layer_capability_matrix = $launchPacket.layer_capability_matrix.schema
        layer_operator_shortcuts = $launchPacket.layer_operator_shortcuts.schema
        layer_operator_groups = $launchPacket.layer_operator_groups.schema
        layer_selection_tool = $launchPacket.layer_selection_tool.schema
        layer_selection_affordance = $launchPacket.layer_selection_affordance.schema
        layer_hover_affordance = $launchPacket.layer_hover_affordance.schema
        layer_lock_affordance = $launchPacket.layer_lock_affordance.schema
        layer_research_workflow = $launchPacket.layer_research_workflow.schema
        layer_control_feedback_strip = $launchPacket.layer_control_feedback_strip.schema
        boundary_emphasis_control = $launchPacket.boundary_emphasis_control.schema
        cursor_geodesy_readout = $launchPacket.cursor_geodesy_readout.schema
        pin_overlay = $launchPacket.pin_overlay.schema
        style_renderer_entries = $launchPacket.style_renderer_entries.schema
        style_renderer_entry_contract = $launchPacket.style_renderer_entries.renderer_entry_contract_schema
        style_profile_renderer_routes = $launchPacket.style_profile_renderer_routes.schema
        style_template_visual_preview = $launchPacket.style_template_visual_preview.schema
        module_boundary_registry = $launchPacket.module_boundary_registry.schema
        module_decoupling_boundary_contract = $launchPacket.module_boundary_registry.decoupling_boundary_contract.schema
        cross_machine_clone_readiness = $launchPacket.cross_machine_clone_readiness.schema
        profile_launch_readiness = $launchPacket.profile_launch_readiness.schema
        profile_launch_readiness_ui = $launchPacket.profile_launch_readiness_ui.schema
        profile_ui_state_replay = $launchPacket.profile_ui_state_replay.schema
        visual_feature_closure_matrix = $launchPacket.visual_feature_closure_matrix.schema
        renderer_output_artifact_contract = $launchPacket.renderer_output_artifact_contract.schema
        layer_render_plan_performance = $launchPacket.layer_render_plan_performance.schema
        reviewer_packet_export = $launchPacket.reviewer_packet_export.schema
        layer_visual_presets = $launchPacket.layer_visual_presets.schema
        layer_visual_preset_runtime_feedback = $launchPacket.layer_visual_preset_runtime_feedback.schema
        layer_operation_feedback = $launchPacket.layer_operation_feedback.schema
        hydrology_lod_readiness = $launchPacket.hydrology_lod_readiness.schema
        hydrology_lod_renderer_apply_contract = $launchPacket.hydrology_lod_readiness.renderer_apply_contract.schema
        hydrology_lod_runtime_evidence = $launchPacket.hydrology_lod_runtime_evidence.schema
        ocean_material_control_port = $launchPacket.ocean_material_control_port.schema
        ocean_material_renderer_apply_contract = $launchPacket.ocean_material_control_port.renderer_apply_contract.schema
        taichi_ocean_3d_control_panel = $launchPacket.ocean_material_control_port.qt_control_panel.schema
        sea_state_scalar_sample = $launchPacket.ocean_material_control_port.sea_state_port.scalar_sample_contract.schema
        layer_undo = $launchPacket.layer_undo.schema
        session_journal = $launchPacket.session_journal.schema
        timeline_state = $launchPacket.timeline_state.schema
        boundary_identity_status = $launchPacket.boundary_highlight.identity_status.schema
    }
    canvas_preview = @{
        launch_packet_schema = $launchPacket.canvas_preview.schema
        renderer_sync = $launchPacket.canvas_preview.renderer_sync
        boundary_identity_warning = $launchPacket.canvas_preview.boundary_identity_warning
        boundary_identity_warning_surface = $launchPacket.canvas_preview.boundary_identity_warning_surface
    }
    active_layer_diagnostics = @{
        launch_packet_schema = $launchPacket.active_layer_diagnostics.schema
        renderer_capabilities_schema = $capabilities.active_layer_diagnostics.schema
        layer_pick_screen_position_field = $launchPacket.active_layer_diagnostics.layer_pick_screen_position_field
        layer_pick_screen_position_source = $launchPacket.active_layer_diagnostics.layer_pick_screen_position_source
        layer_pick_screen_position_status = $launchPacket.active_layer_diagnostics.layer_pick_screen_position_status
        renderer_runtime_fields = $capabilities.active_layer_diagnostics.runtime_fields
    }
    layer_operator_shortcuts = @{
        launch_packet_schema = $launchPacket.layer_operator_shortcuts.schema
        renderer_capabilities_schema = $capabilities.layer_operator_shortcuts.schema
        action_count = $launchPacket.layer_operator_shortcuts.action_count
        keyboard_shortcut_count = $launchPacket.layer_operator_shortcuts.keyboard_shortcut_count
        installed_shortcut_ids = $launchPacket.layer_operator_shortcuts.installed_shortcut_ids
        implemented_action_ids = $launchPacket.layer_operator_shortcuts.implemented_action_ids
    }
    layer_operator_groups = @{
        launch_packet_schema = $launchPacket.layer_operator_groups.schema
        renderer_capabilities_schema = $capabilities.layer_operator_groups.schema
        group_count = $launchPacket.layer_operator_groups.group_count
        complete_group_count = $launchPacket.layer_operator_groups.complete_group_count
        group_ids = @($launchPacket.layer_operator_groups.groups | ForEach-Object { $_.id })
    }
    layer_operation_feedback = @{
        launch_packet_schema = $launchPacket.layer_operation_feedback.schema
        renderer_capabilities_schema = $capabilities.layer_operation_feedback.schema
        selected_layer = $launchPacket.layer_operation_feedback.selected_layer
        active_layer_operation_summary = $launchPacket.layer_operation_feedback.active_layer_operation_summary
        last_layer_operation = $launchPacket.layer_operation_feedback.last_layer_operation
        operator_group_summary = $launchPacket.layer_operation_feedback.operator_group_summary
        undo_depth = $launchPacket.layer_operation_feedback.undo_depth
    }
    layer_control_feedback_strip = @{
        launch_packet_schema = $launchPacket.layer_control_feedback_strip.schema
        renderer_capabilities_schema = $capabilities.layer_control_feedback_strip.schema
        status = $launchPacket.layer_control_feedback_strip.status
        selected_layer = $launchPacket.layer_control_feedback_strip.selected_layer
        qt_label_object = $launchPacket.layer_control_feedback_strip.qt_label_object
        visible_fields = $launchPacket.layer_control_feedback_strip.visible_fields
        summary_text = $launchPacket.layer_control_feedback_strip.summary_text
    }
    layer_selection_tool = @{
        launch_packet_schema = $launchPacket.layer_selection_tool.schema
        renderer_capabilities_schema = $capabilities.layer_selection_tool.schema
        status = $launchPacket.layer_selection_tool.status
        tool_mode = $launchPacket.layer_selection_tool.tool_mode
        pick_state_file = $launchPacket.layer_selection_tool.renderer_pick_bridge.pick_state_file
        selectable_layer_count = $launchPacket.layer_selection_tool.selectable_layer_count
        brush_mask_scope = $launchPacket.layer_selection_tool.brush_mask_scope
        selection_summary_contract_schema = $launchPacket.layer_selection_tool.selection_summary_contract_schema
        selection_summary_contract = $launchPacket.layer_selection_tool.selection_summary_contract
    }
    layer_selection_affordance = @{
        launch_packet_schema = $launchPacket.layer_selection_affordance.schema
        renderer_capabilities_schema = $capabilities.layer_selection_affordance.schema
        selected_layer = $launchPacket.layer_selection_affordance.selected_layer
        qt_label_object = $launchPacket.layer_selection_affordance.qt_label_object
        selected_row_property = $launchPacket.layer_selection_affordance.selected_row_property
        focus_aids = $launchPacket.layer_selection_affordance.focus_aids
        summary_text = $launchPacket.layer_selection_affordance.summary_text
    }
    layer_hover_affordance = @{
        launch_packet_schema = $launchPacket.layer_hover_affordance.schema
        renderer_capabilities_schema = $capabilities.layer_hover_affordance.schema
        qt_label_object = $launchPacket.layer_hover_affordance.qt_label_object
        event_filter = $launchPacket.layer_hover_affordance.event_filter
        hover_events = $launchPacket.layer_hover_affordance.hover_events
        summary_text = $launchPacket.layer_hover_affordance.summary_text
    }
    layer_lock_affordance = @{
        launch_packet_schema = $launchPacket.layer_lock_affordance.schema
        renderer_capabilities_schema = $capabilities.layer_lock_affordance.schema
        locked_layer_count = $launchPacket.layer_lock_affordance.locked_layer_count
        locked_row_property = $launchPacket.layer_lock_affordance.locked_row_property
        locked_row_stylesheet_selector = $launchPacket.layer_lock_affordance.locked_row_stylesheet_selector
        visibility_control_disabled_when_locked = $launchPacket.layer_lock_affordance.visibility_control_disabled_when_locked
        disabled_controls_when_locked = $launchPacket.layer_lock_affordance.disabled_controls_when_locked
        summary_text = $launchPacket.layer_lock_affordance.summary_text
    }
    layer_research_workflow = @{
        launch_packet_schema = $launchPacket.layer_research_workflow.schema
        renderer_capabilities_schema = $capabilities.layer_research_workflow.schema
        status = $launchPacket.layer_research_workflow.status
        selected_layer = $launchPacket.layer_research_workflow.selected_layer
        runtime_warning_severity = $launchPacket.layer_research_workflow.runtime_warning_severity
        runtime_warning_count = $launchPacket.layer_research_workflow.runtime_warning_count
        remediation_hint_count = $launchPacket.layer_research_workflow.remediation_hint_count
        workflow_hint = $launchPacket.layer_research_workflow.workflow_hint
        workflow_hint_surface = $launchPacket.layer_research_workflow.workflow_hint_surface
        qt_surface = $launchPacket.layer_research_workflow.qt_surface
        research_summary_contract_schema = $launchPacket.layer_research_workflow.research_summary_contract_schema
        research_summary_contract = $launchPacket.layer_research_workflow.research_summary_contract
    }
    profile_ui_state_replay = @{
        launch_packet_schema = $launchPacket.profile_ui_state_replay.schema
        renderer_capabilities_schema = $capabilities.profile_ui_state_replay.schema
        status = $launchPacket.profile_ui_state_replay.status
        saved_state_groups = $launchPacket.profile_ui_state_replay.saved_state_groups
        replay_surfaces = $launchPacket.profile_ui_state_replay.replay_surfaces
        summary_text = $launchPacket.profile_ui_state_replay.summary_text
    }
    reviewer_packet_export = @{
        launch_packet_schema = $launchPacket.reviewer_packet_export.schema
        renderer_capabilities_schema = $capabilities.reviewer_packet_export.schema
        status = $launchPacket.reviewer_packet_export.status
        reviewer_packet_schema = $launchPacket.reviewer_packet_export.reviewer_packet_schema
        qt_action = $launchPacket.reviewer_packet_export.qt_action
        default_output = $launchPacket.reviewer_packet_export.default_output
        included_summary_fields = $launchPacket.reviewer_packet_export.included_summary_fields
        included_packet_fields = $launchPacket.reviewer_packet_export.included_packet_fields
        portable = $launchPacket.reviewer_packet_export.portable
    }
    profile_visual_quick_review = @{
        launch_packet_schema = $launchPacket.profile_ui_state_replay.schema
        renderer_capabilities_schema = $capabilities.profile_ui_state_replay.schema
        qt_inspector_action_count = $launchPacket.profile_ui_state_replay.qt_inspector_action_count
        qt_inspector_group_ids = @($profileUiGroups | ForEach-Object { $_.id })
        research_interaction_actions = $researchInteractionActions
        visual_review_actions = $visualReviewActions
        recommended_sequence = @("Inspect: Profile replay", "Inspect: Layer ops", "Inspect: Renderer thumbnail", "Inspect: Live preview")
    }
    visual_review_readiness = @{
        schema = "rrkal_displaytools.visual_review_readiness.v1"
        launch_packet_schema = $visualReviewReadiness.schema
        renderer_capabilities_schema = $visualReviewReadinessCapabilities.schema
        profile_ui_source_schema = $launchPacket.profile_ui_state_replay.schema
        visual_review_actions = $visualReviewReadiness.visual_review_actions
        qt_inspector_action_id = $visualReviewReadiness.qt_inspector_action_id
        renderer_thumbnail_ready = $visualReviewReadiness.renderer_thumbnail_ready
        live_preview_ready = $visualReviewReadiness.live_preview_ready
        frame_status_schema = $visualReviewReadiness.frame_status_schema
        frame_status = $visualReviewReadiness.frame_status
        inspector_view_schema = $visualReviewReadiness.inspector_view_schema
        inspector_view = $visualReviewReadiness.inspector_view
        qt_command_contract_schema = $visualReviewReadiness.qt_command_contract_schema
        qt_command_contract = $visualReviewReadiness.qt_command_contract
        copy_summary_contract_schema = $visualReviewReadiness.copy_summary_contract_schema
        copy_summary_contract = $visualReviewReadiness.copy_summary_contract
        recommended_sequence = $visualReviewReadiness.recommended_sequence
        missing_frame_guidance = $visualReviewReadiness.missing_frame_guidance
    }
    visual_feature_closure_matrix = @{
        schema = "rrkal_displaytools.visual_feature_closure_matrix.v1"
        launch_packet_schema = $visualFeatureClosureMatrix.schema
        renderer_capabilities_schema = $visualFeatureClosureMatrixCapabilities.schema
        status = $visualFeatureClosureMatrix.status
        feature_count = $visualFeatureClosureMatrix.feature_count
        ready_feature_count = $visualFeatureClosureMatrix.ready_feature_count
        feature_ids = $visualFeatureClosureMatrix.feature_ids
        smoke_gate = $visualFeatureClosureMatrix.smoke_gate
    }
    renderer_output_artifact_contract = @{
        schema = "rrkal_displaytools.renderer_output_artifact_contract.v1"
        launch_packet_schema = $rendererOutputArtifactContract.schema
        renderer_capabilities_schema = $rendererOutputArtifactContractCapabilities.schema
        status = $rendererOutputArtifactContract.status
        image_output_control = $rendererOutputArtifactContract.image_output_control
        metadata_sidecar_schema = $rendererOutputArtifactContract.metadata_sidecar_schema
        metadata_fields = $rendererOutputArtifactContract.metadata_fields
        quick_render_smoke_script = $rendererOutputArtifactContract.quick_render_smoke_script
        quick_render_smoke_validates = $rendererOutputArtifactContract.quick_render_smoke_validates
        runtime_artifact_scope = $rendererOutputArtifactContract.runtime_artifact_scope
    }
    layer_render_plan_performance = @{
        schema = "rrkal_displaytools.layer_render_plan_performance.v1"
        launch_packet_schema = $layerRenderPlanPerformance.schema
        renderer_capabilities_schema = $layerRenderPlanPerformanceCapabilities.schema
        status = $layerRenderPlanPerformance.status
        post_decoupling_priority = $layerRenderPlanPerformance.post_decoupling_priority
        optimization_target = $layerRenderPlanPerformance.optimization_target
        runtime_optimization_applied = $layerRenderPlanPerformance.runtime_optimization_applied
        runtime_snapshot_schema = $layerRenderPlanPerformance.runtime_snapshot_schema
        runtime_snapshot_helper = $layerRenderPlanPerformance.runtime_snapshot_helper
        composition_steps_helper = $layerRenderPlanPerformance.composition_steps_helper
        composition_apply_helper = $layerRenderPlanPerformance.composition_apply_helper
        compiled_plan_schema = $layerRenderPlanPerformance.compiled_plan_schema
        compiled_plan_helper = $layerRenderPlanPerformance.compiled_plan_helper
        compiled_plan_cache_key_helper = $layerRenderPlanPerformance.compiled_plan_cache_key_helper
        compiled_plan_cache_status_field = $layerRenderPlanPerformance.compiled_plan_cache_status_field
        compiled_plan_invalidation_reason_schema = $layerRenderPlanPerformance.compiled_plan_invalidation_reason_schema
        compiled_plan_invalidation_helper = $layerRenderPlanPerformance.compiled_plan_invalidation_helper
        compiled_plan_invalidation_reasons_field = $layerRenderPlanPerformance.compiled_plan_invalidation_reasons_field
        compiled_plan_invalidation_scope_schema = $layerRenderPlanPerformance.compiled_plan_invalidation_scope_schema
        compiled_plan_invalidation_scope_helper = $layerRenderPlanPerformance.compiled_plan_invalidation_scope_helper
        compiled_plan_invalidation_scope_field = $layerRenderPlanPerformance.compiled_plan_invalidation_scope_field
        compiled_plan_batch_decision_schema = $layerRenderPlanPerformance.compiled_plan_batch_decision_schema
        compiled_plan_batch_decision_helper = $layerRenderPlanPerformance.compiled_plan_batch_decision_helper
        compiled_plan_batch_decision_field = $layerRenderPlanPerformance.compiled_plan_batch_decision_field
        compiled_plan_apply_path_schema = $layerRenderPlanPerformance.compiled_plan_apply_path_schema
        compiled_plan_apply_path_helper = $layerRenderPlanPerformance.compiled_plan_apply_path_helper
        compiled_plan_apply_path_field = $layerRenderPlanPerformance.compiled_plan_apply_path_field
        compiled_plan_execution_summary_schema = $layerRenderPlanPerformance.compiled_plan_execution_summary_schema
        compiled_plan_execution_summary_helper = $layerRenderPlanPerformance.compiled_plan_execution_summary_helper
        compiled_plan_execution_summary_field = $layerRenderPlanPerformance.compiled_plan_execution_summary_field

        compiled_plan_execution_phases_schema = $layerRenderPlanPerformance.compiled_plan_execution_phases_schema

        compiled_plan_execution_phases_helper = $layerRenderPlanPerformance.compiled_plan_execution_phases_helper

        compiled_plan_execution_phases_field = $layerRenderPlanPerformance.compiled_plan_execution_phases_field

        compiled_plan_phase_timing_contract_schema = $layerRenderPlanPerformance.compiled_plan_phase_timing_contract_schema

        compiled_plan_phase_timing_contract_helper = $layerRenderPlanPerformance.compiled_plan_phase_timing_contract_helper

        compiled_plan_phase_timing_contract_field = $layerRenderPlanPerformance.compiled_plan_phase_timing_contract_field

        phase_timing_unit = $layerRenderPlanPerformance.phase_timing_unit

        compiled_plan_phase_timing_runtime_schema = $layerRenderPlanPerformance.compiled_plan_phase_timing_runtime_schema

        compiled_plan_phase_timing_runtime_helper = $layerRenderPlanPerformance.compiled_plan_phase_timing_runtime_helper

        compiled_plan_phase_timing_runtime_field = $layerRenderPlanPerformance.compiled_plan_phase_timing_runtime_field


        compiled_plan_bottleneck_recommendation_schema = $layerRenderPlanPerformance.compiled_plan_bottleneck_recommendation_schema


        compiled_plan_bottleneck_recommendation_helper = $layerRenderPlanPerformance.compiled_plan_bottleneck_recommendation_helper


        compiled_plan_bottleneck_recommendation_field = $layerRenderPlanPerformance.compiled_plan_bottleneck_recommendation_field



        compiled_plan_compose_queue_schema = $layerRenderPlanPerformance.compiled_plan_compose_queue_schema



        compiled_plan_compose_queue_helper = $layerRenderPlanPerformance.compiled_plan_compose_queue_helper



        compiled_plan_compose_queue_field = $layerRenderPlanPerformance.compiled_plan_compose_queue_field



        compiled_plan_compose_queue_skip_reasons = $layerRenderPlanPerformance.compiled_plan_compose_queue_skip_reasons




        compiled_plan_compose_runs_schema = $layerRenderPlanPerformance.compiled_plan_compose_runs_schema




        compiled_plan_compose_runs_helper = $layerRenderPlanPerformance.compiled_plan_compose_runs_helper




        compiled_plan_compose_runs_field = $layerRenderPlanPerformance.compiled_plan_compose_runs_field





        compiled_plan_compose_run_parity_contract_schema = $layerRenderPlanPerformance.compiled_plan_compose_run_parity_contract_schema





        compiled_plan_compose_run_parity_contract_helper = $layerRenderPlanPerformance.compiled_plan_compose_run_parity_contract_helper





        compiled_plan_compose_run_parity_contract_field = $layerRenderPlanPerformance.compiled_plan_compose_run_parity_contract_field
        compiled_plan_reuse_decision_field = $layerRenderPlanPerformance.compiled_plan_reuse_decision_field
        compiled_plan_reuse_policy = $layerRenderPlanPerformance.compiled_plan_reuse_policy
        compiled_plan_reuse_status_values = $layerRenderPlanPerformance.compiled_plan_reuse_status_values
        compiled_plan_reuse_boundary_field = $layerRenderPlanPerformance.compiled_plan_reuse_boundary_field
        compiled_plan_reuse_boundary = $layerRenderPlanPerformance.compiled_plan_reuse_boundary
        compiled_plan_reuse_runtime_fields = $layerRenderPlanPerformance.compiled_plan_reuse_runtime_fields
        cache_diagnostics_schema = $layerRenderPlanPerformance.cache_diagnostics_schema
        cache_diagnostics_qt_action = $layerRenderPlanPerformance.cache_diagnostics_qt_action
        cache_diagnostics_metadata_source = $layerRenderPlanPerformance.cache_diagnostics_metadata_source
        cache_diagnostics_control_board_schema = $layerRenderPlanPerformance.cache_diagnostics_control_board_schema
        cache_diagnostics_control_board_label_object = $layerRenderPlanPerformance.cache_diagnostics_control_board_label_object
        cache_diagnostics_control_board_button_object = $layerRenderPlanPerformance.cache_diagnostics_control_board_button_object
        cache_diagnostics_control_board_default_visible = $layerRenderPlanPerformance.cache_diagnostics_control_board_default_visible
        metadata_sidecar_field = $layerRenderPlanPerformance.metadata_sidecar_field
        runtime_snapshot_wired = $layerRenderPlanPerformance.runtime_snapshot_wired
        deferred_until = $layerRenderPlanPerformance.deferred_until
        stage_order = $layerRenderPlanPerformance.stage_order
        smoke_gate = $layerRenderPlanPerformance.smoke_gate
    }
    cursor_geodesy_readout = @{
        launch_packet_schema = $launchPacket.cursor_geodesy_readout.schema
        renderer_capabilities_schema = $capabilities.cursor_geodesy_readout.schema
        status = $launchPacket.cursor_geodesy_readout.status
        projection_method = $launchPacket.cursor_geodesy_readout.projection_method
        event_position_guard = $launchPacket.cursor_geodesy_readout.event_position_guard
        backend_raycast_status = $launchPacket.cursor_geodesy_readout.backend_raycast_status
        renderer_raycast_schema = $launchPacket.cursor_geodesy_readout.renderer_raycast_schema
        renderer_raycast_helper = $launchPacket.cursor_geodesy_readout.renderer_raycast_helper
        renderer_raycast_method = $launchPacket.cursor_geodesy_readout.renderer_raycast_method
        raycast_smoke_cases = $launchPacket.cursor_geodesy_readout.raycast_smoke_cases
        runtime_bridge_status = $launchPacket.cursor_geodesy_readout.runtime_bridge_status
        renderer_raycast_state_file = $launchPacket.cursor_geodesy_readout.renderer_raycast_state_file
        renderer_raycast_ack_file = $launchPacket.cursor_geodesy_readout.renderer_raycast_ack_file
        renderer_controls = $launchPacket.cursor_geodesy_readout.renderer_controls
        runtime_events = $launchPacket.cursor_geodesy_readout.runtime_events
        runtime_bridge_fields = $launchPacket.cursor_geodesy_readout.runtime_bridge_fields
        qt_surface = $launchPacket.cursor_geodesy_readout.qt_surface
        cursor_summary_contract_schema = $launchPacket.cursor_geodesy_readout.cursor_summary_contract_schema
        cursor_summary_contract = $launchPacket.cursor_geodesy_readout.cursor_summary_contract
    }
    pin_overlay = @{
        launch_packet_schema = $launchPacket.pin_overlay.schema
        renderer_capabilities_schema = $capabilities.pin_overlay.schema
        rotation_rule = $launchPacket.pin_overlay.rotation_rule
        occlusion_rule = $launchPacket.pin_overlay.occlusion_rule
        renderer_overlay_status = $launchPacket.pin_overlay.renderer_overlay_status
        horizon_control = $launchPacket.pin_overlay.horizon_control
        cursor_fill_priority = $launchPacket.pin_overlay.cursor_fill_priority
        cursor_fill_sources = $launchPacket.pin_overlay.cursor_fill_sources
        cursor_fill_contract = $launchPacket.pin_overlay.cursor_fill_contract
        coordinate_source_fields = $launchPacket.pin_overlay.coordinate_source_fields
        coordinate_source_values = $launchPacket.pin_overlay.coordinate_source_values
        qt_ui_affordances = $launchPacket.pin_overlay.qt_ui_affordances
        qt_projection_note = $launchPacket.pin_overlay.qt_projection_note
        qt_occlusion_legend_object = $launchPacket.pin_overlay.qt_occlusion_legend_object
        qt_occlusion_legend_text = $launchPacket.pin_overlay.qt_occlusion_legend_text
        occlusion_status_values = $launchPacket.pin_overlay.occlusion_status_values
        pin_list_summary_format = $launchPacket.pin_overlay.pin_list_summary_format
        pin_summary_contract_schema = $launchPacket.pin_overlay.pin_summary_contract_schema
        pin_summary_contract = $launchPacket.pin_overlay.pin_summary_contract
        current_status = $launchPacket.pin_overlay.current_status
    }
    boundary_emphasis_control = @{
        launch_packet_schema = $launchPacket.boundary_emphasis_control.schema
        renderer_capabilities_schema = $capabilities.boundary_emphasis_control.schema
        status = $launchPacket.boundary_emphasis_control.status
        control_count = $launchPacket.boundary_emphasis_control.control_count
        target_layer_types = $launchPacket.boundary_emphasis_control.target_layer_types
        renderer_hook_status = $launchPacket.boundary_emphasis_control.renderer_hook_status
        renderer_bridge_contract = $launchPacket.boundary_emphasis_control.renderer_bridge_contract
        renderer_controls_mapped = $launchPacket.boundary_emphasis_control.renderer_controls_mapped
        dialog_feedback = $launchPacket.boundary_emphasis_control.dialog_feedback
        value_preview_fields = $launchPacket.boundary_emphasis_control.value_preview_fields
        summary_parameter_fields = $launchPacket.boundary_emphasis_control.summary_parameter_fields
        target_layer_key = $launchPacket.boundary_emphasis_control.target_layer_key
        target_alignment = $launchPacket.boundary_emphasis_control.target_alignment
        target_alignment_label = $launchPacket.boundary_emphasis_control.target_alignment_label
        pending_renderer_refinements = $launchPacket.boundary_emphasis_control.pending_renderer_refinements
        row_double_click_binding = $launchPacket.boundary_emphasis_control.row_double_click_binding
        row_double_click_layer_keys = $launchPacket.boundary_emphasis_control.row_double_click_layer_keys
        qt_surface = $launchPacket.boundary_emphasis_control.qt_surface
        boundary_summary_contract_schema = $launchPacket.boundary_emphasis_control.boundary_summary_contract_schema
        boundary_summary_contract = $launchPacket.boundary_emphasis_control.boundary_summary_contract
    }
    boundary_highlight = @{
        launch_packet_schema = $launchPacket.boundary_highlight.schema
        renderer_capabilities_schema = $capabilities.boundary_highlight.schema
        ack_schema = $capabilities.boundary_highlight.ack_schema
        identity_status_schema = $launchPacket.boundary_highlight.identity_status.schema
        identity_status_applied = $launchPacket.boundary_highlight.identity_status.applied
        identity_status_pending = $launchPacket.boundary_highlight.identity_status.pending
        identity_status_boundary = $launchPacket.boundary_highlight.identity_status.boundary
        renderer_identity_status_applied = $capabilities.boundary_highlight.identity_status_applied
        renderer_identity_status_pending = $capabilities.boundary_highlight.identity_status_pending
        renderer_identity_status_boundary = $capabilities.boundary_highlight.identity_status_boundary
        ack_history_contract = $launchPacket.boundary_highlight.ack_history_contract
        ack_history_source = $launchPacket.boundary_highlight.ack_history_source
        ack_history_fields = $launchPacket.boundary_highlight.ack_history_fields
        ack_history_qt_surface = $launchPacket.boundary_highlight.ack_history_qt_surface
        ack_history_provenance_field = $launchPacket.boundary_highlight.ack_history_provenance_field
    }
    style_renderer_entries = @{
        launch_packet_schema = $launchPacket.style_renderer_entries.schema
        renderer_capabilities_schema = $capabilities.style_renderer_entries.schema
        entry_count = $launchPacket.style_renderer_entries.entry_count
        entry_ids = $launchPacket.style_renderer_entries.entry_ids
        renderer_entry_contract_schema = $launchPacket.style_renderer_entries.renderer_entry_contract_schema
        parchment_entry_available = $launchPacket.style_renderer_entries.parchment_entry_available
        tactical_entry_available = $launchPacket.style_renderer_entries.tactical_entry_available
    }
    style_profile_renderer_routes = @{
        launch_packet_schema = $launchPacket.style_profile_renderer_routes.schema
        renderer_capabilities_schema = $capabilities.style_profile_renderer_routes.schema
        status = $launchPacket.style_profile_renderer_routes.status
        route_count = $launchPacket.style_profile_renderer_routes.route_count
        route_ids = $launchPacket.style_profile_renderer_routes.route_ids
        renderer_entry_contract_schema = $launchPacket.style_profile_renderer_routes.renderer_entry_contract_schema
        required_route_contract_ids = $launchPacket.style_profile_renderer_routes.required_route_contract_ids
        required_routes = $launchPacket.style_profile_renderer_routes.required_routes
        portable_route_commands = $launchPacket.style_profile_renderer_routes.portable_route_commands
        style_routes_summary_contract_schema = $launchPacket.style_profile_renderer_routes.style_routes_summary_contract.schema
        style_routes_summary_contract = $launchPacket.style_profile_renderer_routes.style_routes_summary_contract
        summary_parameter_fields = $launchPacket.style_profile_renderer_routes.summary_parameter_fields
    }
    style_template_visual_preview = @{
        launch_packet_schema = $launchPacket.style_template_visual_preview.schema
        renderer_capabilities_schema = $capabilities.style_template_visual_preview.schema
        status = $launchPacket.style_template_visual_preview.status
        preview_count = $launchPacket.style_template_visual_preview.preview_count
        preview_ids = $launchPacket.style_template_visual_preview.preview_ids
        required_preview_ids = $launchPacket.style_template_visual_preview.required_preview_ids
        qt_surface = $launchPacket.style_template_visual_preview.qt_surface
        qt_interaction = $launchPacket.style_template_visual_preview.qt_interaction
        card_click_action = $launchPacket.style_template_visual_preview.card_click_action
        qt_card_object_prefix = $launchPacket.style_template_visual_preview.qt_card_object_prefix
        thumbnail_slots_enabled = $launchPacket.style_template_visual_preview.thumbnail_slots_enabled
        thumbnail_slot_count = $launchPacket.style_template_visual_preview.thumbnail_slot_count
        thumbnail_artifact_dir = $launchPacket.style_template_visual_preview.thumbnail_artifact_dir
        thumbnail_source_contract = $launchPacket.style_template_visual_preview.thumbnail_source_contract
        thumbnail_batch_script = $launchPacket.style_template_visual_preview.thumbnail_batch_script
        thumbnail_batch_command = $launchPacket.style_template_visual_preview.thumbnail_batch_command
        thumbnail_batch_validates = $launchPacket.style_template_visual_preview.thumbnail_batch_validates
        qt_inspector_action_id = $launchPacket.style_template_visual_preview.qt_inspector_action_id
        qt_inspector_action_label = $launchPacket.style_template_visual_preview.qt_inspector_action_label
        qt_inspector_handler = $launchPacket.style_template_visual_preview.qt_inspector_handler
        thumbnail_icon_loading = $launchPacket.style_template_visual_preview.thumbnail_icon_loading
        qt_icon_loader = $launchPacket.style_template_visual_preview.qt_icon_loader
        thumbnail_icon_size = $launchPacket.style_template_visual_preview.thumbnail_icon_size
        thumbnail_readiness_schema = $launchPacket.style_template_visual_preview.thumbnail_readiness_schema
        thumbnail_readiness_label_object = $launchPacket.style_template_visual_preview.thumbnail_readiness_label_object
        thumbnail_readiness_fields = $launchPacket.style_template_visual_preview.thumbnail_readiness_fields
        thumbnail_readiness_summary_format = $launchPacket.style_template_visual_preview.thumbnail_readiness_summary_format
        thumbnail_readiness_copy_action = $launchPacket.style_template_visual_preview.thumbnail_readiness_copy_action
        thumbnail_readiness_copy_label = $launchPacket.style_template_visual_preview.thumbnail_readiness_copy_label
        local_thumbnail_readiness_schema = $launchPacket.style_template_visual_preview.local_thumbnail_readiness_schema
        local_thumbnail_readiness_qt_action = $launchPacket.style_template_visual_preview.local_thumbnail_readiness_qt_action
        local_thumbnail_readiness_fields = $launchPacket.style_template_visual_preview.local_thumbnail_readiness_fields
    }
    module_boundary_registry = @{
        launch_packet_schema = $launchPacket.module_boundary_registry.schema
        renderer_capabilities_schema = $capabilities.module_boundary_registry.schema
        module_count = $launchPacket.module_boundary_registry.module_count
        target_modules = $launchPacket.module_boundary_registry.target_modules
        qt_first = $launchPacket.module_boundary_registry.qt_first
        tk_primary_ui_allowed = $launchPacket.module_boundary_registry.tk_primary_ui_allowed
        decoupling_boundary_contract_schema = $launchPacket.module_boundary_registry.decoupling_boundary_contract.schema
        decoupling_status = $launchPacket.module_boundary_registry.decoupling_boundary_contract.status
        extraction_order = $launchPacket.module_boundary_registry.decoupling_boundary_contract.extraction_order
        forbidden_cross_imports = $launchPacket.module_boundary_registry.decoupling_boundary_contract.forbidden_cross_imports
        module_boundary_summary_contract_schema = $launchPacket.module_boundary_registry.module_boundary_summary_contract.schema
        module_boundary_summary_contract = $launchPacket.module_boundary_registry.module_boundary_summary_contract
        summary_parameter_fields = $launchPacket.module_boundary_registry.summary_parameter_fields
        rrkal_data_governance_boundary = $launchPacket.module_boundary_registry.rrkal_data_governance_boundary
    }
    cross_machine_clone_readiness = @{
        launch_packet_schema = $launchPacket.cross_machine_clone_readiness.schema
        renderer_capabilities_schema = $capabilities.cross_machine_clone_readiness.schema
        status = $launchPacket.cross_machine_clone_readiness.status
        repo_url = $launchPacket.cross_machine_clone_readiness.repo_url
        clone_command = $launchPacket.cross_machine_clone_readiness.clone_command
        default_branch = $launchPacket.cross_machine_clone_readiness.default_branch
        repo_visibility = $launchPacket.cross_machine_clone_readiness.repo_visibility
        setup_doc = $launchPacket.cross_machine_clone_readiness.setup_doc
        qt_visible_fields = $launchPacket.cross_machine_clone_readiness.qt_visible_fields
        required_commands = $launchPacket.cross_machine_clone_readiness.required_commands
        launcher_options = $launchPacket.cross_machine_clone_readiness.launcher_options
        handoff_first_command = $launchPacket.cross_machine_clone_readiness.handoff_first_command
        first_run_smoke_command = $launchPacket.cross_machine_clone_readiness.first_run_smoke_command
        first_run_handoff_command = $launchPacket.cross_machine_clone_readiness.first_run_handoff_command
        smoke_required_before_push = $launchPacket.cross_machine_clone_readiness.smoke_required_before_push
        qt_first = $launchPacket.cross_machine_clone_readiness.qt_first
        clone_reviewer_summary_contract_schema = $launchPacket.cross_machine_clone_readiness.clone_reviewer_summary_contract_schema
        clone_reviewer_summary_contract = $launchPacket.cross_machine_clone_readiness.clone_reviewer_summary_contract
    }
    profile_launch_readiness = @{
        launch_packet_schema = $launchPacket.profile_launch_readiness.schema
        renderer_capabilities_schema = $capabilities.profile_launch_readiness.schema
        readiness = $launchPacket.profile_launch_readiness.readiness
        renderer_readiness = $capabilities.profile_launch_readiness.readiness
        ready_check_count = $launchPacket.profile_launch_readiness.ready_check_count
        check_count = $launchPacket.profile_launch_readiness.check_count
        cross_machine_commands = $launchPacket.profile_launch_readiness.cross_machine_commands
        launch_reviewer_summary_contract_schema = $launchPacket.profile_launch_readiness.launch_reviewer_summary_contract_schema
        launch_reviewer_summary_contract = $launchPacket.profile_launch_readiness.launch_reviewer_summary_contract
    }
    profile_launch_readiness_ui = @{
        launch_packet_schema = $launchPacket.profile_launch_readiness_ui.schema
        renderer_capabilities_schema = $capabilities.profile_launch_readiness_ui.schema
        readiness = $launchPacket.profile_launch_readiness_ui.readiness
        qt_surface = $launchPacket.profile_launch_readiness_ui.qt_surface
        visible_fields = $launchPacket.profile_launch_readiness_ui.visible_fields
    }
    layer_visual_presets = @{
        launch_packet_schema = $launchPacket.layer_visual_presets.schema
        renderer_capabilities_schema = $capabilities.layer_visual_presets.schema
        preset_count = $launchPacket.layer_visual_presets.preset_count
        preset_ids = $launchPacket.layer_visual_presets.preset_ids
        qt_surface = $launchPacket.layer_visual_presets.qt_surface
        respects_layer_locks = $launchPacket.layer_visual_presets.respects_layer_locks
    }
    layer_visual_preset_runtime_feedback = @{
        launch_packet_schema = $launchPacket.layer_visual_preset_runtime_feedback.schema
        renderer_capabilities_schema = $capabilities.layer_visual_preset_runtime_feedback.schema
        status = $launchPacket.layer_visual_preset_runtime_feedback.status
        qt_surface = $launchPacket.layer_visual_preset_runtime_feedback.qt_surface
        ack_file = $launchPacket.layer_visual_preset_runtime_feedback.ack_file
        requires_renderer_ack_for_reproducibility = $launchPacket.layer_visual_preset_runtime_feedback.requires_renderer_ack_for_reproducibility
    }
    hydrology_lod_readiness = @{
        launch_packet_schema = $launchPacket.hydrology_lod_readiness.schema
        renderer_capabilities_schema = $capabilities.hydrology_lod_readiness.schema
        readiness = $launchPacket.hydrology_lod_readiness.readiness
        live_hydrology_layer_count = $launchPacket.hydrology_lod_readiness.live_hydrology_layer_count
        hydrology_layer_count = $launchPacket.hydrology_lod_readiness.hydrology_layer_count
        stable_renderer_targets = $launchPacket.hydrology_lod_readiness.stable_renderer_targets
        lod_hook_status = $launchPacket.hydrology_lod_readiness.lod_hook_status
        hydrology_lod_summary_contract_schema = $launchPacket.hydrology_lod_readiness.hydrology_lod_summary_contract.schema
        hydrology_lod_summary_contract = $launchPacket.hydrology_lod_readiness.hydrology_lod_summary_contract
        summary_parameter_fields = $launchPacket.hydrology_lod_readiness.summary_parameter_fields
        renderer_apply_contract_schema = $launchPacket.hydrology_lod_readiness.renderer_apply_contract.schema
        renderer_apply_contract_status = $launchPacket.hydrology_lod_readiness.renderer_apply_contract.status
        runtime_state_file = $launchPacket.hydrology_lod_readiness.renderer_apply_contract.runtime_state_file
        runtime_ack_file = $launchPacket.hydrology_lod_readiness.renderer_apply_contract.runtime_ack_file
    }
    hydrology_lod_runtime_evidence = @{
        launch_packet_schema = $launchPacket.hydrology_lod_runtime_evidence.schema
        renderer_capabilities_schema = $capabilities.hydrology_lod_runtime_evidence.schema
        renderer_apply_contract_schema = $launchPacket.hydrology_lod_runtime_evidence.renderer_apply_contract_schema
        renderer_apply_contract_status = $launchPacket.hydrology_lod_runtime_evidence.renderer_apply_contract_status
        status = $launchPacket.hydrology_lod_runtime_evidence.status
        runtime_state_file = $launchPacket.hydrology_lod_runtime_evidence.runtime_state_file
        runtime_ack_available = $launchPacket.hydrology_lod_runtime_evidence.runtime_ack_available
        pick_state_available = $launchPacket.hydrology_lod_runtime_evidence.pick_state_available
        hydrology_runtime_hit_count = $launchPacket.hydrology_lod_runtime_evidence.hydrology_runtime_hit_count
        pick_matches_hydrology = $launchPacket.hydrology_lod_runtime_evidence.pick_matches_hydrology
        summary_runtime_fields = $launchPacket.hydrology_lod_runtime_evidence.summary_runtime_fields
        ack_file = $launchPacket.hydrology_lod_runtime_evidence.ack_file
        pick_state_file = $launchPacket.hydrology_lod_runtime_evidence.pick_state_file
    }
    ocean_material_control_port = @{
        launch_packet_schema = $launchPacket.ocean_material_control_port.schema
        renderer_capabilities_schema = $capabilities.ocean_material_control_port.schema
        wave_strength = $launchPacket.ocean_material_control_port.material_controls.wave_strength
        roughness = $launchPacket.ocean_material_control_port.material_controls.roughness
        foam = $launchPacket.ocean_material_control_port.material_controls.foam
        sea_state_status = $launchPacket.ocean_material_control_port.sea_state_port.status
        sea_state_scalar_sample_schema = $launchPacket.ocean_material_control_port.sea_state_port.scalar_sample_contract.schema
        ocean_material_summary_contract_schema = $launchPacket.ocean_material_control_port.ocean_material_summary_contract.schema
        ocean_material_summary_contract = $launchPacket.ocean_material_control_port.ocean_material_summary_contract
        summary_parameter_fields = $launchPacket.ocean_material_control_port.summary_parameter_fields
        renderer_apply_contract_schema = $launchPacket.ocean_material_control_port.renderer_apply_contract.schema
        renderer_apply_contract_status = $launchPacket.ocean_material_control_port.renderer_apply_contract.status
        portable = $launchPacket.ocean_material_control_port.renderer_apply_contract.portable
        renderer_flags = $launchPacket.ocean_material_control_port.renderer_flags
        qt_control_panel_schema = $launchPacket.ocean_material_control_port.qt_control_panel.schema
        qt_control_panel = $launchPacket.ocean_material_control_port.qt_control_panel
        control_board_label_object = $launchPacket.ocean_material_control_port.qt_control_panel.control_board_label_object
        control_board_button_object = $launchPacket.ocean_material_control_port.qt_control_panel.control_board_button_object
        control_board_default_visible = $launchPacket.ocean_material_control_port.qt_control_panel.control_board_default_visible
        qt_dialog_action = $launchPacket.ocean_material_control_port.qt_control_panel.qt_dialog_action
        render_pipeline_followup = $launchPacket.ocean_material_control_port.qt_control_panel.render_pipeline_followup
    }
    layer_capability_matrix = @{
        schema = $capabilities.layer_capability_matrix.schema
        launch_packet_schema = $launchPacket.layer_capability_matrix.schema
        runtime_evidence_schema = $capabilities.layer_capability_matrix.runtime_evidence.schema
        runtime_evidence_summary_schema = $capabilities.layer_capability_matrix.runtime_evidence_summary.schema
        runtime_badge_summary_schema = $capabilities.layer_capability_matrix.runtime_badge_summary.schema
        runtime_warning_list_schema = $capabilities.layer_capability_matrix.runtime_warning_list.schema
        runtime_interaction_context_schema = $capabilities.layer_capability_matrix.runtime_interaction_context.schema
        territory_identity_context_schema = $capabilities.layer_capability_matrix.territory_identity_context.schema
        authoritative_identity_source_schema = $capabilities.layer_capability_matrix.authoritative_identity_source.schema
        renderer_diagnostics_summary_schema = $capabilities.layer_capability_matrix.renderer_diagnostics_summary.schema
        renderer_diagnostics_detail_schema = $capabilities.layer_capability_matrix.renderer_diagnostics_detail.schema
        renderer_diagnostics_remediation_schema = $capabilities.layer_capability_matrix.renderer_diagnostics_remediation.schema
        runtime_evidence_available = $capabilities.layer_capability_matrix.runtime_evidence.available
        runtime_status_legend_schema = $capabilities.layer_capability_matrix.runtime_status_legend.schema
        layer_count = $capabilities.layer_capability_matrix.layer_count
        live_counts = $capabilities.layer_capability_matrix.live_counts
        selected_layer = $launchPacket.layer_capability_matrix.selected_layer
        selected_layer_capabilities = $launchPacket.layer_capability_matrix.selected_layer_capabilities
    }
    rrkal_boundary = $launchPacket.rrkal_boundary
    note = "Read-only inspection; does not discover, download, import, or govern datasets."
}

$summary | ConvertTo-Json -Depth 12
