param(
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$scriptName = "scripts/inspect_render_plan_metadata_summary.ps1"
$schema = "rrkal_displaytools.render_plan_metadata_summary_inspector.v1"
$summarySchema = "rrkal_displaytools.layer_render_plan_metadata_summary.v1"
$adapterPayloadSchema = "rrkal_displaytools.layer_render_plan_adapter_payload_summary.v1"
$adapterPayloadContractSchema = "rrkal_displaytools.layer_render_plan_adapter_payload_contract.v1"

if ($ContractOnly) {
    [ordered]@{
        schema = $schema
        source = $scriptName
        status = "contract_only_no_runtime"
        verifies_schema = $summarySchema
        verifies_adapter_payload_schema = $adapterPayloadSchema
        verifies_adapter_payload_contract_schema = $adapterPayloadContractSchema
        full_plan_field = "layer_render_plan"
        summary_field = "layer_render_plan_summary"
        adapter_payload_status_field = "adapter_payload_status"
        adapter_payload_contract_status_field = "adapter_payload_contract_status"
        boundary = "Inspector only; it does not launch Qt, Taichi, render frames, or write metadata files."
        portable = $true
    } | ConvertTo-Json -Depth 8
    exit 0
}

$renderPlanSource = Get-Content -LiteralPath (Join-Path $RepoRoot "render_core\render_plan.py") -Raw -Encoding UTF8
$rendererSource = Get-Content -LiteralPath (Join-Path $RepoRoot "taichi_global_bathymetry.py") -Raw -Encoding UTF8
$markers = [ordered]@{
    summary_schema = $renderPlanSource -like "*$summarySchema*"
    summary_builder = $renderPlanSource -like "*build_layer_render_plan_metadata_summary*"
    full_plan_field = $rendererSource -like '*"layer_render_plan": layer_render_plan*'
    summary_sidecar_field = $rendererSource -like '*"layer_render_plan_summary": build_layer_render_plan_metadata_summary(layer_render_plan)*'
    adapter_payload_schema = $renderPlanSource -like "*$adapterPayloadSchema*"
    adapter_payload_status_field = $renderPlanSource -like "*adapter_payload_status*"
    adapter_payload_contract_schema = $renderPlanSource -like "*$adapterPayloadContractSchema*"
    adapter_payload_contract_status_field = $renderPlanSource -like "*adapter_payload_contract_status*"
    full_plan_preserved_boundary = $renderPlanSource -like "*full layer_render_plan remains the renderer parity/debugging contract*"
    no_io_boundary = $rendererSource -like "*metadata_path.write_text*"
}
$missing = @()
foreach ($marker in $markers.GetEnumerator()) {
    if (-not $marker.Value) {
        $missing += $marker.Key
    }
}

[ordered]@{
    schema = $schema
    source = $scriptName
    status = if ($missing.Count -eq 0) { "ready" } else { "incomplete" }
    verifies_schema = $summarySchema
    verifies_adapter_payload_schema = $adapterPayloadSchema
    verifies_adapter_payload_contract_schema = $adapterPayloadContractSchema
    full_plan_field = "layer_render_plan"
    summary_field = "layer_render_plan_summary"
    adapter_payload_status_field = "adapter_payload_status"
    adapter_payload_contract_status_field = "adapter_payload_contract_status"
    markers = $markers
    missing_markers = $missing
    next_step = "Use this inspector when reviewing renderer output metadata sidecar readiness after clone."
    boundary = "Inspector only; it reads source markers and does not launch Qt, Taichi, render frames, or write metadata files."
    portable = $true
} | ConvertTo-Json -Depth 8
