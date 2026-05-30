param(
    [string]$Template = "fast_synthetic",
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$scriptName = "scripts/inspect_hydrology_lod.ps1"

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.hydrology_lod_inspector.v1"
        source = $scriptName
        status = "contract_only_no_launch_side_effect"
        readiness_field = "hydrology_lod_readiness"
        runtime_evidence_field = "hydrology_lod_runtime_evidence"
        launch_packet_script = "scripts/export_launch_packet.py"
        stable_renderer_targets = @("lakes", "rivers")
        runtime_bridge_files = @(
            "state/renderer_layer_runtime_state.json",
            "state/renderer_layer_runtime_ack.json",
            "state/renderer_layer_pick_state.json"
        )
        default_template = $Template
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_hydrology_lod.ps1"
        boundary = "Inspector reads launch-packet Hydrology/LOD contracts only; it does not launch Qt, Taichi, dataset discovery, import or cache governance."
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
    throw "Launch packet export failed while inspecting Hydrology/LOD"
}

$launchPacket = ($launchPacketText -join "`n") | ConvertFrom-Json
if (-not $launchPacket.hydrology_lod_readiness) {
    throw "Launch packet hydrology_lod_readiness field is missing"
}
if (-not $launchPacket.hydrology_lod_runtime_evidence) {
    throw "Launch packet hydrology_lod_runtime_evidence field is missing"
}

[ordered]@{
    schema = "rrkal_displaytools.hydrology_lod_inspection.v1"
    source = $scriptName
    readiness = $launchPacket.hydrology_lod_readiness
    runtime_evidence = $launchPacket.hydrology_lod_runtime_evidence
    stable_renderer_targets = $launchPacket.hydrology_lod_readiness.stable_renderer_targets
    lod_hook_status = $launchPacket.hydrology_lod_readiness.lod_hook_status
    runtime_state_file = $launchPacket.hydrology_lod_runtime_evidence.runtime_state_file
    ack_file = $launchPacket.hydrology_lod_runtime_evidence.ack_file
    pick_state_file = $launchPacket.hydrology_lod_runtime_evidence.pick_state_file
    boundary = "Hydrology/LOD inspection is displaytools renderer-contract review only; RRKAL owns data/cache governance."
    portable = $true
} | ConvertTo-Json -Depth 12
