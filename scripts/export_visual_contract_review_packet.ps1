param(
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$scriptName = "scripts/export_visual_contract_review_packet.ps1"
$indexScript = Join-Path $RepoRoot "scripts\list_visual_contract_inspectors.ps1"

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.visual_contract_review_packet_export.v1"
        source = $scriptName
        status = "contract_only_no_launch_side_effect"
        output_schema = "rrkal_displaytools.visual_contract_review_packet.v1"
        inspector_index_command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\list_visual_contract_inspectors.ps1"
        output_mode = "stdout_json"
        boundary = "Exporter reads no-GUI inspector metadata only; it does not launch Qt, Taichi, provider IO, dataset discovery, import or cache governance."
        portable = $true
    } | ConvertTo-Json -Depth 8
    exit 0
}

$indexText = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $indexScript
if ($LASTEXITCODE -ne 0) {
    throw "Visual contract inspector index export failed"
}

$index = ($indexText -join "`n") | ConvertFrom-Json
$gitHead = (& git rev-parse --short HEAD 2>$null)
if ($LASTEXITCODE -ne 0) {
    $gitHead = "unknown"
}

[ordered]@{
    schema = "rrkal_displaytools.visual_contract_review_packet.v1"
    source = $scriptName
    status = "ready"
    git_head = "$gitHead"
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    inspector_index_schema = $index.schema
    inspector_entry_count = $index.entry_count
    inspector_entry_ids = $index.entry_ids
    recommended_cross_machine_sequence = $index.recommended_cross_machine_sequence
    first_commands = @(
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\list_visual_contract_inspectors.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_renderer_config_gateway.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_style_renderer_routes.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_layer_workflow.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_qt_uiux_surface.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_uiux_closure_status.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_timeline_uiux.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_uiux_closure_readiness.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_pre7_closure_readiness.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_cross_machine_review_readiness.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_reviewer_first_run_route.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\export_capability_summary.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_layer_visual_presets.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_layer_operator_shortcuts.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_research_interaction.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_hydrology_lod.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_ocean_material.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_layer_render_plan_performance.ps1"
    )
    pre_decoupling_commands = @(
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\performance_smoke.ps1 -ContractOnly",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_decoupling_boundaries.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_render_plan_compose_work_order.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_render_plan_extraction_dry_run.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_render_plan_compose_source_map.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\export_pre_decoupling_readiness_bundle.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_pre_decoupling_readiness.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\export_pre_decoupling_snapshot.ps1 -ContractOnly",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\pre_decoupling_gate.ps1 -ContractOnly"
    )
    inspector_index = $index
    boundary = "Review packet is displaytools no-GUI handoff metadata only; RRKAL owns discovery/download/import/cache governance."
    portable = $true
} | ConvertTo-Json -Depth 14
