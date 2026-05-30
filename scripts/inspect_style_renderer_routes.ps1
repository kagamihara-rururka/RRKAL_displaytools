param(
    [string]$Template = "fast_synthetic",
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$scriptName = "scripts/inspect_style_renderer_routes.ps1"

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.style_routes_inspector.v1"
        source = $scriptName
        status = "contract_only_no_launch_side_effect"
        launch_packet_field = "style_profile_renderer_routes"
        sibling_launch_packet_field = "style_renderer_entries"
        launch_packet_script = "scripts/export_launch_packet.py"
        required_route_ids = @("scientific", "nautical", "parchment", "tactical")
        default_template = $Template
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_style_renderer_routes.ps1"
        boundary = "Inspector reads launch-packet style renderer routes only; it does not launch Qt, Taichi, dataset discovery, import or cache governance."
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
    throw "Launch packet export failed while inspecting style renderer routes"
}

$launchPacket = ($launchPacketText -join "`n") | ConvertFrom-Json
if (-not $launchPacket.style_profile_renderer_routes) {
    throw "Launch packet style_profile_renderer_routes field is missing"
}

$launchPacket.style_profile_renderer_routes | ConvertTo-Json -Depth 12
