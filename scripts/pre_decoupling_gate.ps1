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

$readiness = Invoke-JsonPython @("decoupling_readiness.py", "--phase", "post_07_decoupling")
$firstExtraction = @($readiness.first_extraction_order | Select-Object -First 1)[0]
$gate = [ordered]@{
    schema = "rrkal_displaytools.pre_decoupling_gate.v1"
    source = "scripts/pre_decoupling_gate.ps1"
    contract_only = [bool]$ContractOnly
    phase = $readiness.phase
    ready = $false
    first_extraction_id = $firstExtraction.id
    first_extraction_target = $firstExtraction.target_module
    required_before_move = @(
        "scripts/smoke.ps1",
        "git diff --check",
        "docs/DEVELOPMENT_LOG.zh-TW.md smoke result"
    )
    blocked_scope = @($readiness.phase_policy.post_07_decoupling.blocked)
    rrkal_boundary_rule = $readiness.rrkal_boundary.rule
    smoke_executed = $false
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

if (-not $ContractOnly) {
    powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1
    if ($LASTEXITCODE -ne 0) {
        throw "Pre-decoupling smoke failed"
    }
    $gate.smoke_executed = $true
}

$gate.ready = $true
$gate | ConvertTo-Json -Depth 8
