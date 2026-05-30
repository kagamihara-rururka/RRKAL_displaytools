param(
    [string]$BaselinePath = "state\compose_parity\baseline_sequential_frame_rgba.png",
    [string]$CandidatePath = "state\compose_parity\merged_candidate_frame_rgba.png",
    [string]$ManifestPath = "state\render_compose_parity_smoke_manifest.json",
    [int]$ToleranceMaxAbsDiff = 0,
    [int]$ToleranceChangedPixelCount = 0,
    [switch]$WriteManifest
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

function Resolve-ContractPath {
    param([string]$PathValue)

    if ([System.IO.Path]::IsPathRooted($PathValue)) {
        return $PathValue
    }
    return Join-Path $RepoRoot $PathValue
}

function New-ArtifactStatus {
    param([string]$PathValue)

    $resolvedPath = Resolve-ContractPath $PathValue
    return [ordered]@{
        path = $PathValue
        resolved_path = $resolvedPath
        exists = Test-Path -LiteralPath $resolvedPath
    }
}

$baseline = New-ArtifactStatus $BaselinePath
$candidate = New-ArtifactStatus $CandidatePath
$artifactsReady = [bool]($baseline.exists -and $candidate.exists)
$packet = [ordered]@{
    schema = "rrkal_displaytools.render_compose_parity_smoke.v1"
    source = "scripts/render_compose_parity_smoke.ps1"
    status = if ($artifactsReady) { "artifacts_ready_diff_pending" } else { "contract_ready_missing_artifacts" }
    mode = "contract_only_no_render_side_effect"
    runtime_merge_enabled = $false
    compare_method = "sequential_compose_queue_vs_merged_candidate_rgba_diff"
    required_artifacts = @(
        "baseline_sequential_frame_rgba",
        "merged_candidate_frame_rgba",
        "max_abs_diff",
        "changed_pixel_count",
        "renderer_output_metadata"
    )
    baseline_sequential_frame_rgba = $baseline
    merged_candidate_frame_rgba = $candidate
    tolerance = [ordered]@{
        max_abs_diff = $ToleranceMaxAbsDiff
        changed_pixel_count = $ToleranceChangedPixelCount
    }
    pass_condition = "max_abs_diff <= tolerance.max_abs_diff and changed_pixel_count <= tolerance.changed_pixel_count"
    manifest_path = $ManifestPath
    writes_manifest = [bool]$WriteManifest
    precommit_required = $false
    recommended_by = "rrkal_displaytools.layer_render_plan_compose_run_parity_contract.v1"
    next_runtime_step = "Generate merged candidate RGBA artifacts, then add byte/pixel diff before enabling compose-run merge."
    boundary = "This entrypoint records the parity contract only; it does not render frames, mutate renderer state, or enable runtime compose merging."
}

$json = $packet | ConvertTo-Json -Depth 8

if ($WriteManifest) {
    $manifestResolvedPath = Resolve-ContractPath $ManifestPath
    $manifestDirectory = Split-Path -Parent $manifestResolvedPath
    if ($manifestDirectory) {
        New-Item -ItemType Directory -Force -Path $manifestDirectory | Out-Null
    }
    [System.IO.File]::WriteAllText(
        $manifestResolvedPath,
        $json,
        [System.Text.UTF8Encoding]::new($false)
    )
}

$json
