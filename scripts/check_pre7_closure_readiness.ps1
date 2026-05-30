[CmdletBinding()]
param(
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function Get-RepoText {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RelativePath
    )
    $path = Join-Path $RepoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $path)) {
        return $null
    }
    return Get-Content -LiteralPath $path -Raw -Encoding UTF8
}

function Test-RepoFileContains {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RelativePath,
        [Parameter(Mandatory = $true)]
        [string]$Needle
    )
    $text = Get-RepoText -RelativePath $RelativePath
    if ($null -eq $text) {
        return $false
    }
    return $text.Contains($Needle)
}

function Add-Check {
    param(
        [System.Collections.Generic.List[object]]$Checks,
        [Parameter(Mandatory = $true)]
        [string]$Id,
        [Parameter(Mandatory = $true)]
        [string]$Description,
        [Parameter(Mandatory = $true)]
        [bool]$Passed,
        [Parameter(Mandatory = $true)]
        [string]$Evidence
    )
    $Checks.Add([ordered]@{
        id = $Id
        description = $Description
        passed = $Passed
        evidence = $Evidence
    }) | Out-Null
}

$contract = [ordered]@{
    schema = "rrkal_displaytools.pre7_closure_readiness_check.contract.v1"
    output_schema = "rrkal_displaytools.pre7_closure_readiness_check.v1"
    scope = "pre-7 no-code-move closure gate"
    no_code_move = $true
    checked_surfaces = @(
        "Qt Replay/contracts reviewer route",
        "Qt capability summary",
        "Qt UIUX closure",
        "Qt workspace map",
        "Qt extraction dry-run",
        "render-plan compose source map",
        "clone quickstart reviewer path",
        "post-07 decoupling runbook",
        "formal pre-decoupling gate presence"
    )
}

if ($ContractOnly) {
    $contract | ConvertTo-Json -Depth 8
    exit 0
}

$checks = [System.Collections.Generic.List[object]]::new()

Add-Check $checks "qt_reviewer_route_action" "Qt exposes the cloned-machine reviewer route action." `
    (Test-RepoFileContains "rrkal_displaytools_qt_panel.py" "Inspect: Reviewer route") `
    "rrkal_displaytools_qt_panel.py contains Inspect: Reviewer route"

Add-Check $checks "qt_capability_summary_action" "Qt exposes the current/planned capability summary action." `
    (Test-RepoFileContains "rrkal_displaytools_qt_panel.py" "Inspect: Capability summary") `
    "rrkal_displaytools_qt_panel.py contains Inspect: Capability summary"

Add-Check $checks "qt_uiux_closure_action" "Qt exposes the UIUX closure board action." `
    (Test-RepoFileContains "rrkal_displaytools_qt_panel.py" "Inspect: UIUX closure") `
    "rrkal_displaytools_qt_panel.py contains Inspect: UIUX closure"

Add-Check $checks "qt_workspace_map_action" "Qt exposes the Photoshop-like workspace map action." `
    (Test-RepoFileContains "rrkal_displaytools_qt_panel.py" "Inspect: Workspace map") `
    "rrkal_displaytools_qt_panel.py contains Inspect: Workspace map"

Add-Check $checks "qt_extraction_dry_run_action" "Qt exposes the no-code-move extraction dry-run action." `
    (Test-RepoFileContains "rrkal_displaytools_qt_panel.py" "Inspect: Extraction dry-run") `
    "rrkal_displaytools_qt_panel.py contains Inspect: Extraction dry-run"

Add-Check $checks "qt_reviewer_path_hint" "Qt shows the intended reviewer route before Actions." `
    (Test-RepoFileContains "rrkal_displaytools_qt_panel.py" "Review path: Clone ready -> Reviewer route -> Capability summary -> UIUX closure -> Workspace map") `
    "rrkal_displaytools_qt_panel.py contains the reviewer path hint"

Add-Check $checks "quickstart_extraction_dry_run_path" "Clone quickstart points reviewers to the extraction dry-run action." `
    (Test-RepoFileContains "docs/QUICKSTART_CLONE.zh-TW.md" "Inspect: Extraction dry-run") `
    "docs/QUICKSTART_CLONE.zh-TW.md contains Inspect: Extraction dry-run"

Add-Check $checks "uiux_readiness_gate_exists" "UIUX readiness check exists before post-7 code movement." `
    (Test-Path -LiteralPath (Join-Path $RepoRoot "scripts/check_uiux_closure_readiness.ps1")) `
    "scripts/check_uiux_closure_readiness.ps1 exists"

Add-Check $checks "extraction_dry_run_exists" "Render-plan extraction dry-run inspector exists." `
    (Test-Path -LiteralPath (Join-Path $RepoRoot "scripts/inspect_render_plan_extraction_dry_run.ps1")) `
    "scripts/inspect_render_plan_extraction_dry_run.ps1 exists"

Add-Check $checks "render_plan_compose_source_map_exists" "Render-plan compose source-map inspector exists before code move." `
    (Test-Path -LiteralPath (Join-Path $RepoRoot "scripts/inspect_render_plan_compose_source_map.ps1")) `
    "scripts/inspect_render_plan_compose_source_map.ps1 exists"

Add-Check $checks "formal_pre_decoupling_gate_exists" "Formal pre-decoupling gate exists and remains the post-7 entry." `
    (Test-Path -LiteralPath (Join-Path $RepoRoot "scripts/pre_decoupling_gate.ps1")) `
    "scripts/pre_decoupling_gate.ps1 exists"

Add-Check $checks "not_before_gate_declared" "The 07:00 +08:00 not-before gate is still declared." `
    (Test-RepoFileContains "decoupling_readiness.py" "2026-05-31T07:00:00+08:00") `
    "decoupling_readiness.py contains 2026-05-31T07:00:00+08:00"

Add-Check $checks "post0700_decoupling_runbook" "Post-07 decoupling runbook documents the first code-move scope." `
    ((Test-RepoFileContains "docs/POST_0700_DECOUPLING_RUNBOOK.zh-TW.md" "render_plan_compose") -and (Test-RepoFileContains "docs/POST_0700_DECOUPLING_RUNBOOK.zh-TW.md" "runtime_merge=false")) `
    "docs/POST_0700_DECOUPLING_RUNBOOK.zh-TW.md contains render_plan_compose and runtime_merge=false"

Add-Check $checks "first_extraction_target_documented" "GTD points the first post-7 extraction to render-plan compose." `
    (Test-RepoFileContains "docs/PROJECT_GTD.md" "Start with render-plan compose extraction after the 7:00 decoupling gate.") `
    "docs/PROJECT_GTD.md documents render-plan compose as first extraction"

$failed = @($checks | Where-Object { -not $_.passed })
$status = if ($failed.Count -eq 0) { "pass" } else { "fail" }

$result = [ordered]@{
    schema = "rrkal_displaytools.pre7_closure_readiness_check.v1"
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    status = $status
    ready_for_post7_gate = ($status -eq "pass")
    no_code_move = $true
    failed_checks = @($failed | ForEach-Object { $_.id })
    checks = $checks
    next_action = if ($status -eq "pass") {
        "At or after 2026-05-31T07:00:00+08:00, run scripts/pre_decoupling_gate.ps1 before moving render-plan code."
    } else {
        "Fix failed pre-7 closure checks before entering post-7 decoupling."
    }
}

$result | ConvertTo-Json -Depth 8
if ($status -ne "pass") {
    exit 1
}
