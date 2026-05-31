param(
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$scriptName = "scripts/inspect_earth_canvas_runtime_boundary.ps1"

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.earth_canvas_runtime_boundary_inspector.v1"
        source = $scriptName
        status = "contract_only_no_code_move"
        target_canvas = "earth"
        current_runtime_owner = "taichi_global_bathymetry.py::HybridRenderController"
        future_module = "display_runtime/earth_canvas.py"
        boundary = "Inspector maps the future EarthCanvas extraction seam only; it does not move renderer code."
        portable = $true
    } | ConvertTo-Json -Depth 8
    exit 0
}

$rendererSource = Get-Content -LiteralPath "taichi_global_bathymetry.py" -Raw -Encoding UTF8
$displayCoreSource = Get-Content -LiteralPath "display_core\render_matrix.py" -Raw -Encoding UTF8
$earthRuntimePath = "display_runtime\earth_canvas.py"
$earthRuntimeSource = ""
if (Test-Path -LiteralPath $earthRuntimePath) {
    $earthRuntimeSource = Get-Content -LiteralPath $earthRuntimePath -Raw -Encoding UTF8
}

$evidence = [ordered]@{
    has_hybrid_render_controller = $rendererSource -like "*class HybridRenderController*"
    has_render_if_needed = $rendererSource -like "*def render_if_needed*"
    has_layer_composition_boundary = $rendererSource -like "*apply_layer_render_plan_composition*"
    has_earth_canvas_descriptor = $displayCoreSource -like "*CANVAS_EARTH = `"earth`"*"
    has_geo_layer_contract = $displayCoreSource -like "*LAYER_GEO = `"geo_layer`"*"
    has_earth_renderer_adapter_marker = $displayCoreSource -like "*class DisplayToolsGeoRendererAdapter*"
    has_view_model_render_plan_contract = $displayCoreSource -like "*rrkal_displaytools.view_model_render_plan.v1*"
    has_future_module_file = Test-Path -LiteralPath $earthRuntimePath
    has_earth_canvas_runtime_contract = $earthRuntimeSource -like "*rrkal_displaytools.earth_canvas_runtime_contract.v1*"
}

$missing = @()
foreach ($entry in $evidence.GetEnumerator()) {
    if ($entry.Value -ne $true) {
        $missing += $entry.Key
    }
}

$status = "ready"
if ($missing.Count -gt 0) {
    $status = "needs-source-alignment"
}

[ordered]@{
    schema = "rrkal_displaytools.earth_canvas_runtime_boundary_inspector.v1"
    source = $scriptName
    status = $status
    target_canvas = "earth"
    current_runtime_owner = "taichi_global_bathymetry.py::HybridRenderController"
    future_module = "display_runtime/earth_canvas.py"
    evidence = $evidence
    missing_evidence = $missing
    first_extractable_boundary = @(
        "EarthCanvas runtime wrapper consumes ViewModel render plan metadata",
        "DisplayToolsGeoRendererAdapter remains a marker until runtime wrapper parity exists",
        "Keep ndarray composition and Taichi kernel execution in the current controller until smoke/parity gates are stronger"
    )
    keep_out_of_display_core = @(
        "Qt widgets",
        "Taichi kernels",
        "Matplotlib/Plotly/VisPy/PyVista imports",
        "RRKAL dataset discovery/download/import/cache governance"
    )
    stop_conditions = @(
        "Do not move runtime renderer code without smoke passing",
        "Do not enable canvas switching before EarthCanvas wrapper has parity evidence",
        "Do not import renderer packages from display_core"
    )
    boundary = "This is a no-code-move extraction map for the current globe runtime boundary."
} | ConvertTo-Json -Depth 10

if ($missing.Count -gt 0) {
    exit 1
}
