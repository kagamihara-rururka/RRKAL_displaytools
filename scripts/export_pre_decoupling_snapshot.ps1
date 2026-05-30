param(
    [string]$Output = "state/decoupling/pre_decoupling_snapshot.json",
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

function Resolve-SnapshotPath {
    param([string]$PathValue)
    if ([System.IO.Path]::IsPathRooted($PathValue)) {
        return $PathValue
    }
    return Join-Path $RepoRoot $PathValue
}

function Invoke-JsonPython {
    param([string[]]$ArgumentList)

    $text = $null
    $lastOutput = $null
    for ($attempt = 1; $attempt -le 4; $attempt++) {
        $text = & py -3 @ArgumentList 2>&1
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
        throw "Command failed: py -3 $($ArgumentList -join ' ')`n$($lastOutput -join "`n")"
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
        schema = "rrkal_displaytools.pre_decoupling_snapshot_export.v1"
        source = "scripts/export_pre_decoupling_snapshot.ps1"
        status = "contract_only_no_state_write"
        output = $Output
        output_schema = "rrkal_displaytools.pre_decoupling_snapshot.v1"
        included_fields = @(
            "decoupling_readiness",
            "pre_decoupling_gate",
            "uiux_closure_readiness_check",
            "decoupling_boundary_inspection",
            "render_plan_compose_work_order",
            "performance_smoke_telemetry",
            "renderer_config_gateway",
            "controlled_interception_policy",
            "git_state"
        )
        boundary = "Snapshot export is a handoff/readiness packet only; it does not move renderer code, launch Qt, run live network, or touch RRKAL data/cache governance."
        portable = $true
    } | ConvertTo-Json -Depth 8
    exit 0
}

$readiness = Invoke-JsonPython @("decoupling_readiness.py", "--phase", "post_07_decoupling")
$performanceContract = Invoke-JsonPython @("performance_telemetry.py", "--contract-only")
$rendererConfigGateway = Invoke-JsonPython @("renderer_config_gateway.py", "--sample-map-projection", "globe")
$controlledInterception = Invoke-JsonPython @("controlled_interception.py", "--source", "pre_decoupling_snapshot")
$preDecouplingGate = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\pre_decoupling_gate.ps1", "-ContractOnly")
$uiuxReadiness = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\check_uiux_closure_readiness.ps1")
$decouplingBoundaryInspection = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\inspect_decoupling_boundaries.ps1")
$renderPlanComposeWorkOrder = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\inspect_render_plan_compose_work_order.ps1")

$head = (git rev-parse --short HEAD).Trim()
if ($LASTEXITCODE -ne 0) {
    throw "git rev-parse failed"
}
$branch = (git branch --show-current).Trim()
if ($LASTEXITCODE -ne 0) {
    throw "git branch failed"
}
$porcelain = @(git status --porcelain)
if ($LASTEXITCODE -ne 0) {
    throw "git status failed"
}

$snapshot = [ordered]@{
    schema = "rrkal_displaytools.pre_decoupling_snapshot.v1"
    created_at_utc = [DateTimeOffset]::UtcNow.ToString("o")
    source = "scripts/export_pre_decoupling_snapshot.ps1"
    git_state = [ordered]@{
        branch = $branch
        head = $head
        clean_worktree = ($porcelain.Count -eq 0)
        changed_path_count = $porcelain.Count
    }
    decoupling_readiness = $readiness
    pre_decoupling_gate = $preDecouplingGate
    uiux_closure_readiness_check = $uiuxReadiness
    decoupling_boundary_inspection = $decouplingBoundaryInspection
    render_plan_compose_work_order = $renderPlanComposeWorkOrder
    performance_smoke_telemetry = $performanceContract
    renderer_config_gateway = $rendererConfigGateway
    controlled_interception_policy = $controlledInterception
    next_action = "After 2026-05-31T07:00:00+08:00, run scripts/pre_decoupling_gate.ps1, then start render_plan_compose extraction."
    boundary = "Snapshot is for handoff and preflight only; no renderer module extraction is performed here."
}

$outputPath = Resolve-SnapshotPath $Output
$outputDir = Split-Path -Parent $outputPath
if ($outputDir) {
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
}
$snapshot | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $outputPath -Encoding UTF8
$snapshot | ConvertTo-Json -Depth 20
