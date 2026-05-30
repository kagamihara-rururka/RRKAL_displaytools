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
$visualParityPassed = $null
$precommitGatePassed = $true
$notificationLevel = "info"
$notificationSuppressed = $true
$notificationReason = "pending_artifacts_not_a_precommit_failure"
$passed = $true
$exitCode = 0

if ($ContractOnly) {
    $diffStatus = "contract_only_forced"
    $notificationReason = "contract_only_no_render_side_effect"
} elseif ($runDiff) {
    $notificationSuppressed = $false
    $notificationReason = "artifact_diff_completed"
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
                $visualParityPassed = $false
                $precommitGatePassed = $false
                $notificationLevel = "error"
                $notificationReason = "artifact_dimensions_mismatch"
                $passed = $false
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
                $visualParityPassed = [bool](($maxAbsDiff -le $ToleranceMaxAbsDiff) -and ($changedPixelCount -le $ToleranceChangedPixelCount))
                $precommitGatePassed = $visualParityPassed
                $passed = $visualParityPassed
                $diffStatus = if ($visualParityPassed) { "visual_parity_passed" } else { "visual_parity_failed" }
                $notificationLevel = if ($visualParityPassed) { "ok" } else { "error" }
                $notificationReason = if ($visualParityPassed) { "zero_diff_artifact_parity" } else { "artifact_visual_parity_failed" }
                if (-not $visualParityPassed) {
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
        $visualParityPassed = $false
        $precommitGatePassed = $false
        $notificationLevel = "error"
        $notificationReason = "artifact_diff_error"
        $passed = $false
        $exitCode = 2
    }
}

$packet = [ordered]@{
    schema = "rrkal_displaytools.render_compose_parity_smoke.v1"
    source = "scripts/render_compose_parity_smoke.ps1"
    status = if ($runDiff -or $ContractOnly) { $diffStatus } else { "contract_ready_pending_artifacts" }
    mode = if ($runDiff) { "artifact_rgba_diff" } else { "contract_only_no_render_side_effect" }
    runtime_merge_enabled = $false
    compare_method = "sequential_compose_queue_vs_merged_candidate_rgba_diff"
    diff_engine = "System.Drawing.Bitmap.GetPixel"
    contract_only = [bool]$ContractOnly
    artifacts_present = $artifactsPresent
    artifact_parity_ready = [bool]$runDiff
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
    precommit_gate_passed = $precommitGatePassed
    visual_parity_passed = $visualParityPassed
    max_abs_diff = $maxAbsDiff
    changed_pixel_count = $changedPixelCount
    image_size = $imageSize
    error = $diffError
    pass_condition = "visual_parity_passed is true only after artifact diff reaches max_abs_diff <= tolerance.max_abs_diff and changed_pixel_count <= tolerance.changed_pixel_count"
    manifest_path = $ManifestPath
    writes_manifest = [bool]$WriteManifest
    precommit_required = $false
    notification_level = $notificationLevel
    notification_suppressed = $notificationSuppressed
    notification_reason = $notificationReason
    recommended_by = "rrkal_displaytools.layer_render_plan_compose_run_parity_contract.v1"
    next_runtime_step = "Generate merged candidate RGBA artifacts, then add byte/pixel diff before enabling compose-run merge."
    boundary = "Contract-only or missing-artifact runs are pending/info states, not failed smoke notifications; runtime compose merging stays disabled until artifact diff passes."
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