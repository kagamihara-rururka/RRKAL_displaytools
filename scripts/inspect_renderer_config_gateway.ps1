param(
    [string]$Template = "fast_synthetic",
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$scriptName = "scripts/inspect_renderer_config_gateway.ps1"

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.config_gateway_inspector.v1"
        source = $scriptName
        status = "contract_only_no_launch_side_effect"
        launch_packet_field = "renderer_config_gateway"
        launch_packet_script = "scripts/export_launch_packet.py"
        default_template = $Template
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_renderer_config_gateway.ps1"
        boundary = "Inspector reads the launch-packet config gateway only; it does not launch Qt, Taichi, data discovery, import or cache governance."
        portable = $true
    } | ConvertTo-Json -Depth 8
    exit 0
}

$venvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$useLocalVenv = Test-Path -LiteralPath $venvPython
$pythonCommand = if ($useLocalVenv) { $venvPython } else { "py" }

if ($useLocalVenv) {
    $launchPacketText = & $pythonCommand "scripts\export_launch_packet.py" "--template" $Template
} else {
    $launchPacketText = & $pythonCommand "-3" "scripts\export_launch_packet.py" "--template" $Template
}
if ($LASTEXITCODE -ne 0) {
    throw "Launch packet export failed while inspecting renderer config gateway"
}

$launchPacket = ($launchPacketText -join "`n") | ConvertFrom-Json
if (-not $launchPacket.renderer_config_gateway) {
    throw "Launch packet renderer_config_gateway field is missing"
}

$launchPacket.renderer_config_gateway | ConvertTo-Json -Depth 12
