param(
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

function Invoke-JsonPython {
    param([string[]]$ArgumentList)

    $text = & py -3 @ArgumentList
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: py -3 $($ArgumentList -join ' ')"
    }
    $raw = $text -join "`n"
    $jsonStart = $raw.IndexOf("{")
    if ($jsonStart -lt 0) {
        throw "JSON payload not found: py -3 $($ArgumentList -join ' ')"
    }
    return $raw.Substring($jsonStart) | ConvertFrom-Json
}

function Invoke-JsonPowerShell {
    param([string[]]$ArgumentList)

    $text = & powershell @ArgumentList
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: powershell $($ArgumentList -join ' ')"
    }
    $raw = $text -join "`n"
    $jsonStart = $raw.IndexOf("{")
    if ($jsonStart -lt 0) {
        throw "JSON payload not found: powershell $($ArgumentList -join ' ')"
    }
    return $raw.Substring($jsonStart) | ConvertFrom-Json
}

$readiness = Invoke-JsonPython @("decoupling_readiness.py", "--phase", "post_07_decoupling")
$performanceContract = Invoke-JsonPython @("performance_telemetry.py", "--contract-only")
$workOrderContract = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\inspect_render_plan_compose_work_order.ps1", "-ContractOnly")
$firstExtraction = @($readiness.first_extraction_order | Select-Object -First 1)[0]
$decouplingNotBefore = [DateTimeOffset]::Parse($readiness.operation_schedule.decoupling_not_before)
$currentTime = [DateTimeOffset]::Now
$gate = [ordered]@{
    schema = "rrkal_displaytools.pre_decoupling_gate.v1"
    source = "scripts/pre_decoupling_gate.ps1"
    contract_only = [bool]$ContractOnly
    phase = $readiness.phase
    ready = $false
    decoupling_not_before = $readiness.operation_schedule.decoupling_not_before
    current_time_utc = $currentTime.ToUniversalTime().ToString("o")
    time_gate_enforced = $true
    time_gate_open = ($currentTime -ge $decouplingNotBefore)
    first_extraction_id = $firstExtraction.id
    first_extraction_target = $firstExtraction.target_module
    observability_baseline_schema = $readiness.observability_baseline.schema
    performance_smoke_schema = $readiness.observability_baseline.performance_smoke_schema
    stage_timing_schema = $readiness.observability_baseline.stage_timing_schema
    render_telemetry_schema = $readiness.observability_baseline.render_telemetry_schema
    performance_smoke_command = $readiness.observability_baseline.pre_move_command
    decoupling_boundary_inspector_command = $readiness.operation_schedule.decoupling_boundary_inspector_command
    render_plan_compose_work_order_command = $readiness.operation_schedule.render_plan_compose_work_order_command
    render_plan_compose_work_order_schema = $workOrderContract.output_schema
    required_before_move = @(
        "clean git worktree",
        "scripts/smoke.ps1",
        "scripts/performance_smoke.ps1",
        "scripts/inspect_decoupling_boundaries.ps1",
        "scripts/inspect_render_plan_compose_work_order.ps1",
        "git diff --check",
        "docs/DEVELOPMENT_LOG.zh-TW.md smoke result"
    )
    requires_clean_worktree = $true
    blocked_scope = @($readiness.phase_policy.post_07_decoupling.blocked)
    rrkal_boundary_rule = $readiness.rrkal_boundary.rule
    smoke_executed = $false
    performance_smoke_output_required = "state/performance/stage_timing.jsonl"
}

if ($gate.phase -ne "post_07_decoupling") {
    throw "Pre-decoupling gate requires post_07_decoupling phase"
}
if ($gate.first_extraction_id -ne "render_plan_compose") {
    throw "Pre-decoupling first extraction must be render_plan_compose"
}
if ($gate.rrkal_boundary_rule -notmatch "Do not move discovery/download/import/cache lifecycle") {
    throw "Pre-decoupling RRKAL boundary rule missing"
}
if ($gate.observability_baseline_schema -ne "rrkal_displaytools.decoupling_observability_baseline.v1") {
    throw "Pre-decoupling observability baseline schema missing"
}
if ($gate.performance_smoke_schema -ne "rrkal_displaytools.performance_smoke.v1") {
    throw "Pre-decoupling performance smoke schema missing"
}
if ($gate.stage_timing_schema -ne "rrkal_displaytools.stage_timing.v1") {
    throw "Pre-decoupling stage timing schema missing"
}
if ($gate.render_telemetry_schema -ne "rrkal_displaytools.render_telemetry.v1") {
    throw "Pre-decoupling render telemetry schema missing"
}
if ($performanceContract.schema -ne $gate.performance_smoke_schema) {
    throw "Pre-decoupling performance smoke contract-only command mismatch"
}
if ($gate.decoupling_boundary_inspector_command -notlike "*scripts/inspect_decoupling_boundaries.ps1") {
    throw "Pre-decoupling boundary inspector command missing"
}
if ($gate.render_plan_compose_work_order_command -notlike "*scripts/inspect_render_plan_compose_work_order.ps1") {
    throw "Pre-decoupling render plan compose work order command missing"
}
if ($gate.render_plan_compose_work_order_schema -ne "rrkal_displaytools.render_plan_compose_work_order.v1") {
    throw "Pre-decoupling render plan compose work order schema missing"
}

if (-not $ContractOnly) {
    if (-not $gate.time_gate_open) {
        throw "Pre-decoupling gate is not open before $($gate.decoupling_not_before); continue UI/contract handoff closure only"
    }
    $gitStatus = git status --porcelain
    if ($LASTEXITCODE -ne 0) {
        throw "Pre-decoupling git status failed"
    }
    if ($gitStatus) {
        throw "Pre-decoupling gate requires a clean git worktree before moving renderer code"
    }
    powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1
    if ($LASTEXITCODE -ne 0) {
        throw "Pre-decoupling smoke failed"
    }
    if (-not (Test-Path -LiteralPath $gate.performance_smoke_output_required)) {
        throw "Pre-decoupling performance smoke output missing after smoke"
    }
    powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_decoupling_boundaries.ps1
    if ($LASTEXITCODE -ne 0) {
        throw "Pre-decoupling boundary inspector failed"
    }
    powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_render_plan_compose_work_order.ps1
    if ($LASTEXITCODE -ne 0) {
        throw "Pre-decoupling render plan compose work order inspector failed"
    }
    $gate.smoke_executed = $true
}

$gate.ready = $true
$gate | ConvertTo-Json -Depth 8
