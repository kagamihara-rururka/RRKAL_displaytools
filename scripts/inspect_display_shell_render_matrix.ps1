$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$coreSource = Get-Content -Raw -Encoding UTF8 (Join-Path $repoRoot "display_core\render_matrix.py")
$initSource = Get-Content -Raw -Encoding UTF8 (Join-Path $repoRoot "display_core\__init__.py")

$packet = [ordered]@{
    schema = "rrkal_displaytools.display_shell_render_matrix_review.v1"
    source = "scripts\inspect_display_shell_render_matrix.ps1"
    status = "phase1_contract_ready"
    target_architecture = "DisplayShell + Canvas System + Layer System + Render Matrix"
    required_canvases = @("earth", "time_series")
    required_layer_types = @("geo_layer", "time_series_layer")
    proves = @(
        "display_core package exists",
        "LayerModel and ViewModel contracts exist",
        "register_renderer decorator exists",
        "lookup_renderers dispatcher exists",
        "display shell capability packet exists",
        "runtime globe path is not replaced"
    )
    has_layer_model = $coreSource -like "*class LayerModel*"
    has_view_model = $coreSource -like "*class ViewModel*"
    has_canvas_descriptor = $coreSource -like "*class CanvasDescriptor*"
    has_renderer_entry = $coreSource -like "*class RendererEntry*"
    has_canvas_registry = $coreSource -like "*rrkal_displaytools.canvas_registry.v1*"
    has_sample_view_models = $coreSource -like "*rrkal_displaytools.sample_view_models.v1*"
    has_register_renderer = $coreSource -like "*def register_renderer*"
    has_lookup_renderers = $coreSource -like "*def lookup_renderers*"
    has_capability_packet = $coreSource -like "*rrkal_displaytools.display_shell_render_matrix.v1*"
    exports_contracts = ($initSource -like "*build_display_shell_capability_packet*") -and ($initSource -like "*build_canvas_registry_packet*") -and ($initSource -like "*build_sample_view_models_packet*")
    sample_view_ids = @("rrkal_displaytools_earth_view_sample", "rrkal_displaytools_time_series_view_sample")
    runtime_canvas_switching_enabled = $false
    next_step = "Extract EarthCanvas boundary and add a minimal TimeSeriesCanvas adapter after render-plan composition seams are stable."
}

$packet | ConvertTo-Json -Depth 6
