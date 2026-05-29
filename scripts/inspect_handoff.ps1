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
        style_renderer_entries = $launchPacket.style_renderer_entries.schema
        profile_launch_readiness = $launchPacket.profile_launch_readiness.schema
        profile_launch_readiness_ui = $launchPacket.profile_launch_readiness_ui.schema
        layer_visual_presets = $launchPacket.layer_visual_presets.schema
        layer_visual_preset_runtime_feedback = $launchPacket.layer_visual_preset_runtime_feedback.schema
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
    style_renderer_entries = @{
        launch_packet_schema = $launchPacket.style_renderer_entries.schema
        renderer_capabilities_schema = $capabilities.style_renderer_entries.schema
        entry_count = $launchPacket.style_renderer_entries.entry_count
        entry_ids = $launchPacket.style_renderer_entries.entry_ids
        parchment_entry_available = $launchPacket.style_renderer_entries.parchment_entry_available
        tactical_entry_available = $launchPacket.style_renderer_entries.tactical_entry_available
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
