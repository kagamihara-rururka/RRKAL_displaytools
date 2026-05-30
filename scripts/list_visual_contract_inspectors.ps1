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
        "hydrology_lod",
        "ocean_material",
        "performance_smoke",
        "decoupling_boundaries",
        "render_plan_compose_work_order",
        "pre_decoupling_readiness_bundle",
        "pre_decoupling_readiness_check",
        "pre_decoupling_snapshot",
        "pre_decoupling_gate"
    )
    boundary = "Index lists no-GUI displaytools review commands only; it does not launch Qt, Taichi, provider IO, dataset discovery, import or cache governance."
    portable = $true
} | ConvertTo-Json -Depth 12
