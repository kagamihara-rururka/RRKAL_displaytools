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
        layer_research_workflow = $launchPacket.layer_research_workflow.schema
        boundary_emphasis_control = $launchPacket.boundary_emphasis_control.schema
        cursor_geodesy_readout = $launchPacket.cursor_geodesy_readout.schema
        pin_overlay = $launchPacket.pin_overlay.schema
        style_renderer_entries = $launchPacket.style_renderer_entries.schema
        style_profile_renderer_routes = $launchPacket.style_profile_renderer_routes.schema
        module_boundary_registry = $launchPacket.module_boundary_registry.schema
        cross_machine_clone_readiness = $launchPacket.cross_machine_clone_readiness.schema
        profile_launch_readiness = $launchPacket.profile_launch_readiness.schema
        profile_launch_readiness_ui = $launchPacket.profile_launch_readiness_ui.schema
        layer_visual_presets = $launchPacket.layer_visual_presets.schema
        layer_visual_preset_runtime_feedback = $launchPacket.layer_visual_preset_runtime_feedback.schema
        hydrology_lod_readiness = $launchPacket.hydrology_lod_readiness.schema
        hydrology_lod_runtime_evidence = $launchPacket.hydrology_lod_runtime_evidence.schema
        ocean_material_control_port = $launchPacket.ocean_material_control_port.schema
        layer_undo = $launchPacket.layer_undo.schema
        session_journal = $launchPacket.session_journal.schema
        timeline_state = $launchPacket.timeline_state.schema
        boundary_identity_status = $launchPacket.boundary_highlight.identity_status.schema
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
    layer_selection_tool = @{
        launch_packet_schema = $launchPacket.layer_selection_tool.schema
        renderer_capabilities_schema = $capabilities.layer_selection_tool.schema
        status = $launchPacket.layer_selection_tool.status
        tool_mode = $launchPacket.layer_selection_tool.tool_mode
        pick_state_file = $launchPacket.layer_selection_tool.renderer_pick_bridge.pick_state_file
        selectable_layer_count = $launchPacket.layer_selection_tool.selectable_layer_count
        brush_mask_scope = $launchPacket.layer_selection_tool.brush_mask_scope
    }
    layer_research_workflow = @{
        launch_packet_schema = $launchPacket.layer_research_workflow.schema
        renderer_capabilities_schema = $capabilities.layer_research_workflow.schema
        status = $launchPacket.layer_research_workflow.status
        selected_layer = $launchPacket.layer_research_workflow.selected_layer
        runtime_warning_severity = $launchPacket.layer_research_workflow.runtime_warning_severity
        runtime_warning_count = $launchPacket.layer_research_workflow.runtime_warning_count
        remediation_hint_count = $launchPacket.layer_research_workflow.remediation_hint_count
        qt_surface = $launchPacket.layer_research_workflow.qt_surface
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
        pending_renderer_refinements = $launchPacket.boundary_emphasis_control.pending_renderer_refinements
        row_double_click_binding = $launchPacket.boundary_emphasis_control.row_double_click_binding
        row_double_click_layer_keys = $launchPacket.boundary_emphasis_control.row_double_click_layer_keys
        qt_surface = $launchPacket.boundary_emphasis_control.qt_surface
    }
    style_renderer_entries = @{
        launch_packet_schema = $launchPacket.style_renderer_entries.schema
        renderer_capabilities_schema = $capabilities.style_renderer_entries.schema
        entry_count = $launchPacket.style_renderer_entries.entry_count
        entry_ids = $launchPacket.style_renderer_entries.entry_ids
        parchment_entry_available = $launchPacket.style_renderer_entries.parchment_entry_available
        tactical_entry_available = $launchPacket.style_renderer_entries.tactical_entry_available
    }
    style_profile_renderer_routes = @{
        launch_packet_schema = $launchPacket.style_profile_renderer_routes.schema
        renderer_capabilities_schema = $capabilities.style_profile_renderer_routes.schema
        status = $launchPacket.style_profile_renderer_routes.status
        route_count = $launchPacket.style_profile_renderer_routes.route_count
        route_ids = $launchPacket.style_profile_renderer_routes.route_ids
        required_routes = $launchPacket.style_profile_renderer_routes.required_routes
    }
    module_boundary_registry = @{
        launch_packet_schema = $launchPacket.module_boundary_registry.schema
        renderer_capabilities_schema = $capabilities.module_boundary_registry.schema
        module_count = $launchPacket.module_boundary_registry.module_count
        target_modules = $launchPacket.module_boundary_registry.target_modules
        qt_first = $launchPacket.module_boundary_registry.qt_first
        tk_primary_ui_allowed = $launchPacket.module_boundary_registry.tk_primary_ui_allowed
        rrkal_data_governance_boundary = $launchPacket.module_boundary_registry.rrkal_data_governance_boundary
    }
    cross_machine_clone_readiness = @{
        launch_packet_schema = $launchPacket.cross_machine_clone_readiness.schema
        renderer_capabilities_schema = $capabilities.cross_machine_clone_readiness.schema
        status = $launchPacket.cross_machine_clone_readiness.status
        repo_url = $launchPacket.cross_machine_clone_readiness.repo_url
        setup_doc = $launchPacket.cross_machine_clone_readiness.setup_doc
        required_commands = $launchPacket.cross_machine_clone_readiness.required_commands
        launcher_options = $launchPacket.cross_machine_clone_readiness.launcher_options
        handoff_first_command = $launchPacket.cross_machine_clone_readiness.handoff_first_command
        smoke_required_before_push = $launchPacket.cross_machine_clone_readiness.smoke_required_before_push
        qt_first = $launchPacket.cross_machine_clone_readiness.qt_first
    }
    profile_launch_readiness = @{
        launch_packet_schema = $launchPacket.profile_launch_readiness.schema
        renderer_capabilities_schema = $capabilities.profile_launch_readiness.schema
        readiness = $launchPacket.profile_launch_readiness.readiness
        renderer_readiness = $capabilities.profile_launch_readiness.readiness
        ready_check_count = $launchPacket.profile_launch_readiness.ready_check_count
        check_count = $launchPacket.profile_launch_readiness.check_count
        cross_machine_commands = $launchPacket.profile_launch_readiness.cross_machine_commands
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
    }
    hydrology_lod_runtime_evidence = @{
        launch_packet_schema = $launchPacket.hydrology_lod_runtime_evidence.schema
        renderer_capabilities_schema = $capabilities.hydrology_lod_runtime_evidence.schema
        status = $launchPacket.hydrology_lod_runtime_evidence.status
        runtime_ack_available = $launchPacket.hydrology_lod_runtime_evidence.runtime_ack_available
        pick_state_available = $launchPacket.hydrology_lod_runtime_evidence.pick_state_available
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
        renderer_flags = $launchPacket.ocean_material_control_port.renderer_flags
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
