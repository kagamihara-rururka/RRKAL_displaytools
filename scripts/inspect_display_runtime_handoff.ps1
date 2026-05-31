param(
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$scriptName = "scripts/inspect_display_runtime_handoff.ps1"

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.display_runtime_handoff_inspector.v1"
        source = $scriptName
        status = "contract_only_no_launch_side_effect"
        display_shell_command = "py -3 scripts\export_display_shell_render_matrix.py"
        display_runtime_command = "py -3 scripts\export_display_runtime_contracts.py"
        boundary = "Inspector aggregates no-GUI display shell and runtime contract packets only."
        portable = $true
    } | ConvertTo-Json -Depth 8
    exit 0
}

$displayShellText = & py -3 scripts\export_display_shell_render_matrix.py
if ($LASTEXITCODE -ne 0) {
    throw "Display shell render matrix exporter failed"
}

$displayRuntimeText = & py -3 scripts\export_display_runtime_contracts.py
if ($LASTEXITCODE -ne 0) {
    throw "Display runtime contracts exporter failed"
}

$displayShell = ($displayShellText -join "`n") | ConvertFrom-Json
$displayRuntime = ($displayRuntimeText -join "`n") | ConvertFrom-Json

$missingRuntimeCanvasTypes = @()
foreach ($canvasType in @($displayShell.canvas_types)) {
    if (@($displayRuntime.canvas_types) -notcontains $canvasType) {
        $missingRuntimeCanvasTypes += $canvasType
    }
}

$status = "ready"
if ($missingRuntimeCanvasTypes.Count -gt 0) {
    $status = "needs-runtime-contract"
}
if ($displayShell.sample_view_model_render_plans.runtime_render_invoked -ne $false) {
    $status = "runtime-render-invoked"
}
if ($displayRuntime.runtime_render_invoked -ne $false) {
    $status = "runtime-render-invoked"
}

[ordered]@{
    schema = "rrkal_displaytools.display_runtime_handoff_inspector.v1"
    source = $scriptName
    status = $status
    display_shell_schema = $displayShell.schema
    display_runtime_schema = $displayRuntime.schema
    display_shell_canvas_types = @($displayShell.canvas_types)
    display_runtime_canvas_types = @($displayRuntime.canvas_types)
    missing_runtime_canvas_types = $missingRuntimeCanvasTypes
    render_plan_schema = $displayShell.sample_view_model_render_plans_schema
    runtime_protocol_schema = $displayRuntime.protocol_schema
    sample_runtime_requests_schema = $displayRuntime.sample_runtime_requests_schema
    sample_runtime_request_count = [int]$displayRuntime.sample_runtime_requests.request_count
    runtime_render_invoked = [bool]($displayShell.sample_view_model_render_plans.runtime_render_invoked -or $displayRuntime.runtime_render_invoked)
    boundary = "Handoff inspector proves ViewModel render plan and runtime request/contract packets align without renderer execution."
} | ConvertTo-Json -Depth 10

if ($status -ne "ready") {
    exit 1
}
