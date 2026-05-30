param(
    [string]$BaselinePath = "state/compose_parity/baseline_sequential_frame_rgba.png",
    [string]$CandidatePath = "state/compose_parity/merged_candidate_frame_rgba.png",
    [string]$ManifestPath = "state/render_compose_parity_smoke_manifest.json",
    [int]$ToleranceMaxAbsDiff = 0,
    [int]$ToleranceChangedPixelCount = 0,
    [switch]$ContractOnly,
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
$artifactsPresent = [bool]($baseline.exists -and $candidate.exists)
$runDiff = [bool]($artifactsPresent -and -not $ContractOnly)
$diffStatus = "not_run_missing_artifacts"
$maxAbsDiff = $null
$changedPixelCount = $null
$imageSize = $null
$diffError = $null
$passed = $false
$exitCode = 0

if ($ContractOnly) {
    $diffStatus = "contract_only_forced"
} elseif ($runDiff) {
    try {
        Add-Type -AssemblyName System.Drawing
        $baselineBitmap = [System.Drawing.Bitmap]::new($baseline.resolved_path)
        $candidateBitmap = [System.Drawing.Bitmap]::new($candidate.resolved_path)
        try {
            if (($baselineBitmap.Width -ne $candidateBitmap.Width) -or ($baselineBitmap.Height -ne $candidateBitmap.Height)) {
                $diffStatus = "failed_dimension_mismatch"
                $imageSize = [ordered]@{
                    baseline = @($baselineBitmap.Width, $baselineBitmap.Height)
                    candidate = @($candidateBitmap.Width, $candidateBitmap.Height)
                }
                $changedPixelCount = -1
                $exitCode = 1
            } else {
                $diffStatus = "rgba_diff_completed"
                $imageSize = @($baselineBitmap.Width, $baselineBitmap.Height)
                $maxAbsDiff = 0
                $changedPixelCount = 0
                for ($y = 0; $y -lt $baselineBitmap.Height; $y++) {
                    for ($x = 0; $x -lt $baselineBitmap.Width; $x++) {
                        $a = $baselineBitmap.GetPixel($x, $y)
                        $b = $candidateBitmap.GetPixel($x, $y)
                        $pixelMax = [Math]::Max(
                            [Math]::Max([Math]::Abs([int]$a.A - [int]$b.A), [Math]::Abs([int]$a.R - [int]$b.R)),
                            [Math]::Max([Math]::Abs([int]$a.G - [int]$b.G), [Math]::Abs([int]$a.B - [int]$b.B))
                        )
                        if ($pixelMax -gt 0) {
                            $changedPixelCount += 1
                            if ($pixelMax -gt $maxAbsDiff) {
                                $maxAbsDiff = $pixelMax
                            }
                        }
                    }
                }
                $passed = [bool](($maxAbsDiff -le $ToleranceMaxAbsDiff) -and ($changedPixelCount -le $ToleranceChangedPixelCount))
                $diffStatus = if ($passed) { "visual_parity_passed" } else { "visual_parity_failed" }
                if (-not $passed) {
                    $exitCode = 1
                }
            }
        } finally {
            if ($null -ne $baselineBitmap) {
                $baselineBitmap.Dispose()
            }
            if ($null -ne $candidateBitmap) {
                $candidateBitmap.Dispose()
            }
        }
    } catch {
        $diffStatus = "diff_error"
        $diffError = $_.Exception.Message
        $exitCode = 2
    }
}

$packet = [ordered]@{
    schema = "rrkal_displaytools.render_compose_parity_smoke.v1"
    source = "scripts/render_compose_parity_smoke.ps1"
    status = if ($runDiff -or $ContractOnly) { $diffStatus } else { "contract_ready_missing_artifacts" }
    mode = if ($runDiff) { "artifact_rgba_diff" } else { "contract_only_no_render_side_effect" }
    runtime_merge_enabled = $false
    compare_method = "sequential_compose_queue_vs_merged_candidate_rgba_diff"
    diff_engine = "System.Drawing.Bitmap.GetPixel"
    contract_only = [bool]$ContractOnly
    artifacts_present = $artifactsPresent
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
    diff_status = $diffStatus
    passed = $passed
    max_abs_diff = $maxAbsDiff
    changed_pixel_count = $changedPixelCount
    image_size = $imageSize
    error = $diffError
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

if ($exitCode -ne 0) {
    exit $exitCode
}
