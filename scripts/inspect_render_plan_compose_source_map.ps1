param(
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$SourcePath = Join-Path $RepoRoot "taichi_global_bathymetry.py"
$scriptName = "scripts/inspect_render_plan_compose_source_map.ps1"

$targets = @(
    [ordered]@{ id = "alpha_compose"; pattern = "^def alpha_compose\(" },
    [ordered]@{ id = "alpha_blend_compose"; pattern = "^def alpha_blend_compose\(" },
    [ordered]@{ id = "alpha_compose_transparent"; pattern = "^def alpha_compose_transparent\(" },
    [ordered]@{ id = "compose_runtime_overlay"; pattern = "^\s+def compose_runtime_overlay\(" },
    [ordered]@{ id = "compose_runtime_blend"; pattern = "^\s+def compose_runtime_blend\(" },
    [ordered]@{ id = "layer_render_plan_runtime_snapshot"; pattern = "^\s+def layer_render_plan_runtime_snapshot\(" },
    [ordered]@{ id = "layer_render_plan_composition_steps"; pattern = "^\s+def layer_render_plan_composition_steps\(" },
    [ordered]@{ id = "layer_render_plan_step_overlay"; pattern = "^\s+def layer_render_plan_step_overlay\(" },
    [ordered]@{ id = "layer_render_plan_step_visible"; pattern = "^\s+def layer_render_plan_step_visible\(" },
    [ordered]@{ id = "layer_render_plan_overlay_is_transparent"; pattern = "^\s+def layer_render_plan_overlay_is_transparent\(" },
    [ordered]@{ id = "layer_render_plan_compose_queue"; pattern = "^\s+def layer_render_plan_compose_queue\(" },
    [ordered]@{ id = "layer_render_plan_compose_runs"; pattern = "^\s+def layer_render_plan_compose_runs\(" },
    [ordered]@{ id = "layer_render_plan_compose_run_parity_contract"; pattern = "^\s+def layer_render_plan_compose_run_parity_contract\(" },
    [ordered]@{ id = "apply_layer_render_plan_composition"; pattern = "^\s+def apply_layer_render_plan_composition\(" },
    [ordered]@{ id = "merge_alpha_compose_overlay_run"; pattern = "^\s+def merge_alpha_compose_overlay_run\(" },
    [ordered]@{ id = "apply_layer_render_plan_merged_candidate_composition"; pattern = "^\s+def apply_layer_render_plan_merged_candidate_composition\(" },
    [ordered]@{ id = "layer_render_plan_cache_key"; pattern = "^\s+def layer_render_plan_cache_key\(" },
    [ordered]@{ id = "layer_render_plan_cache_invalidation_reasons"; pattern = "^\s+def layer_render_plan_cache_invalidation_reasons\(" },
    [ordered]@{ id = "layer_render_plan_cache_invalidation_scope"; pattern = "^\s+def layer_render_plan_cache_invalidation_scope\(" },
    [ordered]@{ id = "layer_render_plan_batch_decisions"; pattern = "^\s+def layer_render_plan_batch_decisions\(" },
    [ordered]@{ id = "layer_render_plan_apply_path"; pattern = "^\s+def layer_render_plan_apply_path\(" },
    [ordered]@{ id = "layer_render_plan_execution_summary"; pattern = "^\s+def layer_render_plan_execution_summary\(" },
    [ordered]@{ id = "layer_render_plan_execution_phases"; pattern = "^\s+def layer_render_plan_execution_phases\(" },
    [ordered]@{ id = "layer_render_plan_phase_timing_contract"; pattern = "^\s+def layer_render_plan_phase_timing_contract\(" },
    [ordered]@{ id = "layer_render_plan_bottleneck_recommendation"; pattern = "^\s+def layer_render_plan_bottleneck_recommendation\(" },
    [ordered]@{ id = "layer_render_plan_phase_timing_runtime_packet"; pattern = "^\s+def layer_render_plan_phase_timing_runtime_packet\(" },
    [ordered]@{ id = "compile_layer_render_plan"; pattern = "^\s+def compile_layer_render_plan\(" }
)

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.render_plan_compose_source_map_inspector.v1"
        source = $scriptName
        status = "contract_only_no_code_move"
        output_schema = "rrkal_displaytools.render_plan_compose_source_map.v1"
        source_file = "taichi_global_bathymetry.py"
        target_module = "render_core/render_plan.py"
        target_count = $targets.Count
        boundary = "Source map only; it reads monolith helper positions and does not move code, launch Qt/Taichi, enable runtime merge, or touch RRKAL data/cache governance."
        portable = $true
    } | ConvertTo-Json -Depth 8
    exit 0
}

if (-not (Test-Path -LiteralPath $SourcePath)) {
    throw "Source file not found: $SourcePath"
}

$matches = @()
$missing = @()
foreach ($target in $targets) {
    $match = Select-String -LiteralPath $SourcePath -Pattern $target.pattern | Select-Object -First 1
    if ($null -eq $match) {
        $missing += $target.id
        $matches += [ordered]@{
            id = $target.id
            found = $false
            line = $null
            pattern = $target.pattern
        }
    } else {
        $matches += [ordered]@{
            id = $target.id
            found = $true
            line = $match.LineNumber
            pattern = $target.pattern
        }
    }
}

[ordered]@{
    schema = "rrkal_displaytools.render_plan_compose_source_map.v1"
    source = $scriptName
    status = if ($missing.Count -eq 0) { "ready" } else { "incomplete" }
    source_file = "taichi_global_bathymetry.py"
    target_module = "render_core/render_plan.py"
    source_owner = "HybridRenderController and alpha compose helpers"
    no_code_move = $true
    runtime_merge_enabled = $false
    targets = $matches
    missing_targets = $missing
    first_move_hint = "Extract data-oriented render-plan compose helpers first; keep runtime merge disabled until parity evidence exists."
    boundary = "Source map only; code movement starts after the formal post-07 gate."
    portable = $true
} | ConvertTo-Json -Depth 10
