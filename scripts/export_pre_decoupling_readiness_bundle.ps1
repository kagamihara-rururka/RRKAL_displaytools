param(
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$scriptName = "scripts/export_pre_decoupling_readiness_bundle.ps1"

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
        schema = "rrkal_displaytools.pre_decoupling_readiness_bundle_export.v1"
        source = $scriptName
        status = "contract_only_no_state_write"
        output_schema = "rrkal_displaytools.pre_decoupling_readiness_bundle.v1"
        included_reports = @(
            "visual_contract_inspector_index",
            "visual_contract_review_packet",
            "uiux_closure_readiness_check",
            "pre_decoupling_gate_contract",
            "decoupling_boundary_inspection",
            "render_plan_compose_work_order",
            "pre_decoupling_snapshot_export_contract"
        )
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\export_pre_decoupling_readiness_bundle.ps1"
        boundary = "Bundle exports read-only pre-decoupling readiness JSON only; it does not write state, move renderer code, launch Qt/Taichi, or touch RRKAL discovery/download/import/cache governance."
        portable = $true
    } | ConvertTo-Json -Depth 8
    exit 0
}

$visualInspectorIndex = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\list_visual_contract_inspectors.ps1")
$visualReviewPacket = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\export_visual_contract_review_packet.ps1")
$uiuxReadiness = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\check_uiux_closure_readiness.ps1")
$preDecouplingGate = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\pre_decoupling_gate.ps1", "-ContractOnly")
$decouplingBoundaryInspection = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\inspect_decoupling_boundaries.ps1")
$renderPlanComposeWorkOrder = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\inspect_render_plan_compose_work_order.ps1")
$preDecouplingSnapshotExport = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\export_pre_decoupling_snapshot.ps1", "-ContractOnly")

$gitHead = (& git rev-parse --short HEAD 2>$null)
if ($LASTEXITCODE -ne 0) {
    $gitHead = "unknown"
}

[ordered]@{
    schema = "rrkal_displaytools.pre_decoupling_readiness_bundle.v1"
    source = $scriptName
    status = "ready"
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    git_head = "$gitHead"
    visual_contract_inspector_index = $visualInspectorIndex
    visual_contract_review_packet = $visualReviewPacket
    uiux_closure_readiness_check = $uiuxReadiness
    pre_decoupling_gate_contract = $preDecouplingGate
    decoupling_boundary_inspection = $decouplingBoundaryInspection
    render_plan_compose_work_order = $renderPlanComposeWorkOrder
    pre_decoupling_snapshot_export_contract = $preDecouplingSnapshotExport
    first_extraction_id = $preDecouplingGate.first_extraction_id
    first_extraction_target = $preDecouplingGate.first_extraction_target
    required_before_move = @($preDecouplingGate.required_before_move)
    ready_for_07_gate_review = (
        $preDecouplingGate.ready -eq $true -and
        $uiuxReadiness.status -eq "pass" -and
        $decouplingBoundaryInspection.ready_for_07_gate_review -eq $true -and
        $renderPlanComposeWorkOrder.status -eq "ready_for_post_07_extraction"
    )
    boundary = "Readiness bundle is displaytools no-GUI handoff metadata only; RRKAL owns discovery/download/import/cache governance."
    portable = $true
} | ConvertTo-Json -Depth 16
