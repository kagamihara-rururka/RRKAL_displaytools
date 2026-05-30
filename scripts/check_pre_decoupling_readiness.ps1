param(
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$scriptName = "scripts/check_pre_decoupling_readiness.ps1"

function Invoke-JsonPowerShell {
    param([string[]]$ArgumentList)

    $text = $null
    $lastOutput = $null
    for ($attempt = 1; $attempt -le 4; $attempt++) {
        $text = & powershell @ArgumentList 2>&1
        if ($LASTEXITCODE -eq 0) {
            $lastOutput = $text
            break
        }
        $lastOutput = $text
        if ($attempt -lt 4) {
            Start-Sleep -Milliseconds ([int](250 * $attempt))
        }
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: powershell $($ArgumentList -join ' ')`n$($lastOutput -join "`n")"
    }
    $raw = $text -join "`n"
    $jsonStart = $raw.IndexOf("{")
    if ($jsonStart -lt 0) {
        throw "JSON payload not found: powershell $($ArgumentList -join ' ')"
    }
    return $raw.Substring($jsonStart) | ConvertFrom-Json
}

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.pre_decoupling_readiness_check.v1"
        source = $scriptName
        status = "contract_only_no_state_write"
        bundle_command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\export_pre_decoupling_readiness_bundle.ps1"
        output_schema = "rrkal_displaytools.pre_decoupling_readiness_check_result.v1"
        checks = @(
            "bundle_ready",
            "first_extraction_render_plan_compose",
            "target_module_render_core_render_plan",
            "boundary_ready",
            "work_order_ready",
            "required_before_move_complete",
            "uiux_readiness_required_before_move",
            "uiux_readiness_passed_in_bundle",
            "snapshot_contract_contains_work_order"
        )
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_pre_decoupling_readiness.ps1"
        boundary = "Check reads the no-GUI readiness bundle only; it does not write state, move renderer code, launch Qt/Taichi, or touch RRKAL discovery/download/import/cache governance."
        portable = $true
    } | ConvertTo-Json -Depth 8
    exit 0
}

$bundle = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\export_pre_decoupling_readiness_bundle.ps1")

$requiredBeforeMove = @($bundle.required_before_move)
$inspectorIds = @($bundle.visual_contract_inspector_index.entry_ids)
$snapshotIncluded = @($bundle.pre_decoupling_snapshot_export_contract.included_fields)

$checks = [ordered]@{
    bundle_ready = ($bundle.ready_for_07_gate_review -eq $true)
    first_extraction_render_plan_compose = ($bundle.first_extraction_id -eq "render_plan_compose")
    target_module_render_core_render_plan = ($bundle.first_extraction_target -eq "render_core/render_plan.py")
    boundary_ready = ($bundle.decoupling_boundary_inspection.ready_for_07_gate_review -eq $true)
    work_order_ready = ($bundle.render_plan_compose_work_order.status -eq "ready_for_post_07_extraction")
    required_before_move_complete = (
        $requiredBeforeMove -contains "scripts/smoke.ps1" -and
        $requiredBeforeMove -contains "scripts/check_uiux_closure_readiness.ps1" -and
        $requiredBeforeMove -contains "scripts/performance_smoke.ps1" -and
        $requiredBeforeMove -contains "scripts/inspect_decoupling_boundaries.ps1" -and
        $requiredBeforeMove -contains "scripts/inspect_render_plan_compose_work_order.ps1"
    )
    uiux_readiness_required_before_move = ($requiredBeforeMove -contains "scripts/check_uiux_closure_readiness.ps1")
    uiux_readiness_passed_in_bundle = (
        $bundle.uiux_closure_readiness_check.schema -eq "rrkal_displaytools.uiux_closure_readiness_check_result.v1" -and
        $bundle.uiux_closure_readiness_check.status -eq "pass"
    )
    inspector_index_complete = (
        $inspectorIds -contains "pre_decoupling_readiness_bundle" -and
        $inspectorIds -contains "render_plan_compose_work_order" -and
        $inspectorIds -contains "decoupling_boundaries" -and
        $inspectorIds -contains "pre_decoupling_gate"
    )
    snapshot_contract_contains_work_order = ($snapshotIncluded -contains "render_plan_compose_work_order")
}

$failed = @($checks.GetEnumerator() | Where-Object { $_.Value -ne $true } | ForEach-Object { $_.Key })
if ($failed.Count -gt 0) {
    throw "Pre-decoupling readiness check failed: $($failed -join ', ')"
}

[ordered]@{
    schema = "rrkal_displaytools.pre_decoupling_readiness_check_result.v1"
    source = $scriptName
    status = "pass"
    ready_for_07_gate_review = $true
    first_extraction_id = $bundle.first_extraction_id
    first_extraction_target = $bundle.first_extraction_target
    uiux_readiness_required_before_move = $checks.uiux_readiness_required_before_move
    uiux_readiness_passed_in_bundle = $checks.uiux_readiness_passed_in_bundle
    checks = $checks
    failed_checks = @()
    next_command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\pre_decoupling_gate.ps1"
    boundary = "Readiness check is no-GUI preflight only; renderer extraction still starts only after the 2026-05-31T07:00:00+08:00 gate and clean worktree smoke."
    portable = $true
} | ConvertTo-Json -Depth 10
