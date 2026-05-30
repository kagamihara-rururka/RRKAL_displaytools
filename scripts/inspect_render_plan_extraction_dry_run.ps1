param(
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

function Invoke-JsonPowerShell {
    param([string[]]$ArgumentList)

    $text = & powershell @ArgumentList 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: powershell $($ArgumentList -join ' ')`n$($text -join "`n")"
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
        schema = "rrkal_displaytools.render_plan_extraction_dry_run_inspector.v1"
        output_schema = "rrkal_displaytools.render_plan_extraction_dry_run.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_render_plan_extraction_dry_run.ps1"
        writes = @()
        dry_run_only = $true
        boundary = "Dry-run checklist only; it does not move renderer code, create modules, launch Qt/Taichi, or touch RRKAL discovery/download/import/cache governance."
        portable = $true
    } | ConvertTo-Json -Depth 8
    exit 0
}

$gate = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\pre_decoupling_gate.ps1", "-ContractOnly")
$readiness = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\check_pre_decoupling_readiness.ps1")
$workOrder = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\inspect_render_plan_compose_work_order.ps1")

[ordered]@{
    schema = "rrkal_displaytools.render_plan_extraction_dry_run.v1"
    status = "ready"
    dry_run_only = $true
    code_move_performed = $false
    time_gate_open = $gate.time_gate_open
    decoupling_not_before = $gate.decoupling_not_before
    first_extraction_id = $gate.first_extraction_id
    first_extraction_target = $gate.first_extraction_target
    source_monolith = "taichi_global_bathymetry.py"
    planned_target_files = @(
        "render_core/render_plan.py",
        "render_core/__init__.py"
    )
    required_before_move = @($gate.required_before_move)
    readiness_status = $readiness.status
    uiux_readiness_required_before_move = $readiness.uiux_readiness_required_before_move
    uiux_readiness_passed_in_bundle = $readiness.uiux_readiness_passed_in_bundle
    work_order_status = $workOrder.status
    source_helpers = @($workOrder.source_helpers)
    non_goals = @(
        "Do not enable runtime compose-run merging before zero-diff parity artifacts exist.",
        "Do not move RRKAL discovery/download/import/cache governance into displaytools.",
        "Do not start before the formal 07:00 +08:00 gate opens.",
        "Do not bypass smoke, UIUX readiness, boundary inspector or work-order evidence."
    )
    stop_conditions = @(
        "dirty git worktree",
        "smoke failure",
        "UIUX readiness failure",
        "boundary inspector failure",
        "render-plan work-order mismatch",
        "time gate not open for formal extraction"
    )
    next_formal_command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\pre_decoupling_gate.ps1"
    boundary = "This packet is a reviewer checklist only; module extraction remains gated and is not performed here."
    portable = $true
} | ConvertTo-Json -Depth 12
