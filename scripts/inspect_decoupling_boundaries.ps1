param(
    [string]$Template = "fast_synthetic",
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$scriptName = "scripts/inspect_decoupling_boundaries.ps1"

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

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.decoupling_boundary_inspector.v1"
        source = $scriptName
        status = "contract_only_no_launch_side_effect"
        readiness_command = "py -3 decoupling_readiness.py --phase post_07_decoupling"
        launch_packet_command = "py -3 scripts/export_launch_packet.py --template $Template"
        required_packets = @(
            "rrkal_displaytools.decoupling_readiness.v1",
            "rrkal_displaytools.module_boundary_registry.v1",
            "rrkal_displaytools.module_decoupling_boundary_contract.v1"
        )
        default_template = $Template
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_decoupling_boundaries.ps1"
        boundary = "Inspector reads decoupling readiness and launch-packet module boundaries only; it does not move code, launch Qt, launch Taichi, or touch RRKAL discovery/download/import/cache governance."
        portable = $true
    } | ConvertTo-Json -Depth 8
    exit 0
}

$readiness = Invoke-JsonPython @("decoupling_readiness.py", "--phase", "post_07_decoupling")
$launchPacket = Invoke-JsonPython @("scripts/export_launch_packet.py", "--template", $Template)

if ($readiness.schema -ne "rrkal_displaytools.decoupling_readiness.v1") {
    throw "Decoupling readiness schema missing"
}
if (-not $launchPacket.module_boundary_registry) {
    throw "Launch packet module_boundary_registry field is missing"
}

$moduleRegistry = $launchPacket.module_boundary_registry
$boundaryContract = $moduleRegistry.decoupling_boundary_contract
$firstExtraction = @($readiness.first_extraction_order | Select-Object -First 1)[0]
$targetModules = @($readiness.first_extraction_order | ForEach-Object { $_.target_module })

if ($readiness.phase -ne "post_07_decoupling") {
    throw "Decoupling boundary inspection requires post_07_decoupling phase"
}
if ($firstExtraction.id -ne "render_plan_compose") {
    throw "First extraction must remain render_plan_compose"
}
if ($firstExtraction.target_module -ne "render_core/render_plan.py") {
    throw "First extraction target must remain render_core/render_plan.py"
}
if ($moduleRegistry.schema -ne "rrkal_displaytools.module_boundary_registry.v1") {
    throw "Module boundary registry schema missing"
}
if ($boundaryContract.schema -ne "rrkal_displaytools.module_decoupling_boundary_contract.v1") {
    throw "Module decoupling boundary contract schema missing"
}
if ($boundaryContract.tk_primary_ui_allowed -ne $false) {
    throw "Module boundary must keep Tk out of primary UI"
}
if ($readiness.rrkal_boundary.rule -notmatch "Do not move discovery/download/import/cache lifecycle") {
    throw "RRKAL data/cache governance boundary missing"
}

[ordered]@{
    schema = "rrkal_displaytools.decoupling_boundary_inspection.v1"
    source = $scriptName
    phase = $readiness.phase
    first_extraction_id = $firstExtraction.id
    first_extraction_target = $firstExtraction.target_module
    first_extraction_keep_contracts = @($firstExtraction.keep_contracts)
    extraction_count = @($readiness.first_extraction_order).Count
    target_modules = $targetModules
    operation_schedule = $readiness.operation_schedule
    observability_baseline_schema = $readiness.observability_baseline.schema
    smoke_gate_before_each_move = @($readiness.smoke_gate_before_each_move)
    module_boundary_registry_schema = $moduleRegistry.schema
    module_boundary_contract_schema = $boundaryContract.schema
    launch_boundary_target_modules = @($moduleRegistry.target_modules)
    launch_boundary_summary_contract_schema = $moduleRegistry.module_boundary_summary_contract.schema
    tk_primary_ui_allowed = $boundaryContract.tk_primary_ui_allowed
    rrkal_boundary = $readiness.rrkal_boundary
    blocked_scope = @($readiness.phase_policy.post_07_decoupling.blocked)
    ready_for_07_gate_review = $true
    boundary = "Decoupling boundary inspection is read-only displaytools contract review; RRKAL owns discovery/download/import/cache governance."
    portable = $true
} | ConvertTo-Json -Depth 12
