$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$entries = @(
    [ordered]@{
        id = "renderer_config_gateway"
        category = "replay_contracts"
        schema = "rrkal_displaytools.config_gateway_inspector.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_renderer_config_gateway.ps1"
        proves = @("typed renderer argument normalization", "changed defaults", "config-only boundary")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "style_routes"
        category = "style_renderer_entries"
        schema = "rrkal_displaytools.style_routes_inspector.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_style_renderer_routes.ps1"
        proves = @("scientific route", "nautical route", "parchment route", "tactical route")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "hydrology_lod"
        category = "renderer_ports"
        schema = "rrkal_displaytools.hydrology_lod_inspector.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_hydrology_lod.ps1"
        proves = @("lake target", "river target", "LOD hook", "runtime state/ack/pick bridge paths")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "layer_workflow"
        category = "research_interaction"
        schema = "rrkal_displaytools.layer_workflow_inspector.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_layer_workflow.ps1"
        proves = @("layer research workflow", "selection summary contract", "navigation hint", "copyable navigation handoff")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "qt_uiux_surface"
        category = "uiux"
        schema = "rrkal_displaytools.qt_uiux_surface_inspector.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_qt_uiux_surface.ps1"
        proves = @("Qt-first UI boundary", "Photoshop-like panel grouping", "research inspector groups", "cross-machine first-run order")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "uiux_closure_status"
        category = "uiux"
        schema = "rrkal_displaytools.uiux_closure_status_inspector.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_uiux_closure_status.ps1"
        proves = @("ready feature count", "queued followups", "under-construction items visible", "visual review readiness")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "timeline_uiux"
        category = "uiux"
        schema = "rrkal_displaytools.timeline_uiux_inspector.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_timeline_uiux.ps1"
        proves = @("timeline playback readiness", "animation export contract", "layer opacity interpolation", "pending timeline items visible")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "uiux_closure_readiness_check"
        category = "uiux"
        schema = "rrkal_displaytools.uiux_closure_readiness_check.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_uiux_closure_readiness.ps1"
        proves = @("aggregated UIUX pass/fail", "queued items visible", "Qt-first boundary", "runtime merge blocked")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "cross_machine_review_readiness_check"
        category = "cross_machine"
        schema = "rrkal_displaytools.cross_machine_review_readiness_check.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_cross_machine_review_readiness.ps1"
        proves = @("public clone readiness", "first-run command visibility", "review packet portability", "UIUX readiness", "pre-decoupling contract availability")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "reviewer_first_run_route"
        category = "cross_machine"
        schema = "rrkal_displaytools.reviewer_first_run_route_inspector.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_reviewer_first_run_route.ps1"
        proves = @("clone-to-review route", "researcher first-look surfaces", "Qt-first review checklist", "visible pending UIUX items")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "capability_summary"
        category = "handoff"
        schema = "rrkal_displaytools.capability_summary_export.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\export_capability_summary.ps1"
        proves = @("current capabilities", "planned capabilities", "repo boundaries", "post-push summary source")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "layer_visual_presets"
        category = "layer_control"
        schema = "rrkal_displaytools.layer_visual_presets_inspector.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_layer_visual_presets.ps1"
        proves = @("hydrology preset", "boundary preset", "annotation preset", "brush/mask excluded", "selection tool retained")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "layer_operator_shortcuts"
        category = "layer_control"
        schema = "rrkal_displaytools.layer_operator_shortcuts_inspector.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_layer_operator_shortcuts.ps1"
        proves = @("keyboard shortcuts", "active quick actions", "operation groups", "copyable provenance")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "research_interaction"
        category = "research_interaction"
        schema = "rrkal_displaytools.research_interaction_inspector.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_research_interaction.ps1"
        proves = @("selected layer review", "pin occlusion contract", "cursor geodesy bridge", "boundary emphasis state")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "ocean_material"
        category = "renderer_ports"
        schema = "rrkal_displaytools.ocean_material_inspector.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_ocean_material.ps1"
        proves = @("Ocean 3D control panel", "safe preview", "control-board audit", "sea-state scalar contract")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "performance_smoke"
        category = "performance"
        schema = "rrkal_displaytools.performance_smoke.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\performance_smoke.ps1 -ContractOnly"
        proves = @("stage timing schema", "render telemetry schema", "threshold guard contract")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "layer_render_plan_performance"
        category = "performance"
        schema = "rrkal_displaytools.layer_render_plan_performance_inspector.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_layer_render_plan_performance.ps1"
        proves = @("precompute render plan target", "single-pass optimization queue", "runtime merge disabled", "zero-diff parity required")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "pre_decoupling_snapshot"
        category = "decoupling"
        schema = "rrkal_displaytools.pre_decoupling_snapshot_export.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\export_pre_decoupling_snapshot.ps1 -ContractOnly"
        proves = @("snapshot schema", "included readiness fields", "post-7 handoff path")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "pre_decoupling_gate"
        category = "decoupling"
        schema = "rrkal_displaytools.pre_decoupling_gate.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\pre_decoupling_gate.ps1 -ContractOnly"
        proves = @("render_plan_compose first extraction", "clean-worktree requirement", "performance telemetry baseline")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "decoupling_boundaries"
        category = "decoupling"
        schema = "rrkal_displaytools.decoupling_boundary_inspector.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_decoupling_boundaries.ps1"
        proves = @("render_plan_compose target", "module boundary registry", "RRKAL data/cache boundary", "Qt-primary UI boundary")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "render_plan_compose_work_order"
        category = "decoupling"
        schema = "rrkal_displaytools.render_plan_compose_work_order_inspector.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_render_plan_compose_work_order.ps1"
        proves = @("target module", "source helpers", "keep contracts", "smoke gates", "runtime merge non-goal")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "render_plan_extraction_dry_run"
        category = "decoupling"
        schema = "rrkal_displaytools.render_plan_extraction_dry_run_inspector.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_render_plan_extraction_dry_run.ps1"
        proves = @("post-07 extraction checklist", "planned target files", "UIUX gate dependency", "stop conditions", "no code move")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "pre_decoupling_readiness_bundle"
        category = "decoupling"
        schema = "rrkal_displaytools.pre_decoupling_readiness_bundle_export.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\export_pre_decoupling_readiness_bundle.ps1"
        proves = @("single readiness bundle", "gate contract", "boundary inspection", "render plan work order", "snapshot contract")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "pre_decoupling_readiness_check"
        category = "decoupling"
        schema = "rrkal_displaytools.pre_decoupling_readiness_check.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_pre_decoupling_readiness.ps1"
        proves = @("readiness pass/fail", "first extraction target", "required-before-move completeness", "snapshot work-order inclusion")
        no_launch_side_effect = $true
    },
    [ordered]@{
        id = "handoff"
        category = "cross_machine"
        schema = "rrkal_displaytools.handoff_inspection.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_handoff.ps1"
        proves = @("launch packet contract list", "reviewer packet fields", "cross-machine clone handoff")
        no_launch_side_effect = $true
    }
)

[ordered]@{
    schema = "rrkal_displaytools.visual_contract_inspector_index.v1"
    source = "scripts/list_visual_contract_inspectors.ps1"
    status = "ready"
    entry_count = $entries.Count
    entry_ids = @($entries | ForEach-Object { $_.id })
    entries = $entries
    recommended_cross_machine_sequence = @(
        "renderer_config_gateway",
        "style_routes",
        "layer_workflow",
        "qt_uiux_surface",
        "uiux_closure_status",
        "timeline_uiux",
        "uiux_closure_readiness_check",
        "cross_machine_review_readiness_check",
        "reviewer_first_run_route",
        "capability_summary",
        "layer_visual_presets",
        "layer_operator_shortcuts",
        "research_interaction",
        "hydrology_lod",
        "ocean_material",
        "performance_smoke",
        "layer_render_plan_performance",
        "decoupling_boundaries",
        "render_plan_compose_work_order",
        "render_plan_extraction_dry_run",
        "pre_decoupling_readiness_bundle",
        "pre_decoupling_readiness_check",
        "pre_decoupling_snapshot",
        "pre_decoupling_gate"
    )
    boundary = "Index lists no-GUI displaytools review commands only; it does not launch Qt, Taichi, provider IO, dataset discovery, import or cache governance."
    portable = $true
} | ConvertTo-Json -Depth 12
