$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

Write-Host "RRKAL_displaytools smoke"
Write-Host "Repo: $RepoRoot"

function Invoke-CheckedNative {
    param(
        [string]$FilePath,
        [string[]]$ArgumentList
    )

    & $FilePath @ArgumentList
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $FilePath $($ArgumentList -join ' ')"
    }
}

Invoke-CheckedNative py @("-3", "-m", "py_compile", "rrkal_displaytools_qt_panel.py", "taichi_global_bathymetry.py", "pin_projection.py", "closed_loop_status.py")
Invoke-CheckedNative py @("-3", "profile_schema.py") | Out-Null
Invoke-CheckedNative py @("-3", "scripts\validate_profiles.py")
$launchPacketText = & py -3 scripts\export_launch_packet.py --template fast_synthetic
if ($LASTEXITCODE -ne 0) {
    throw "Command failed: py -3 scripts\export_launch_packet.py --template fast_synthetic"
}
$launchPacket = $launchPacketText | ConvertFrom-Json
if ($launchPacket.canvas_preview.schema -ne "rrkal_displaytools.canvas_preview.v1") {
    throw "Launch packet canvas_preview schema missing or invalid"
}
if ($launchPacket.active_layer_diagnostics.schema -ne "rrkal_displaytools.active_layer_diagnostics.v1") {
    throw "Launch packet active_layer_diagnostics schema missing or invalid"
}
if ($launchPacket.layer_undo.schema -ne "rrkal_displaytools.layer_stack_undo.v1") {
    throw "Launch packet layer_undo schema missing or invalid"
}
if ($launchPacket.session_journal.schema -ne "rrkal_displaytools.session_journal.v1") {
    throw "Launch packet session_journal schema missing or invalid"
}
if ($launchPacket.boundary_highlight.identity_status.schema -ne "rrkal_displaytools.boundary_identity_status.v1") {
    throw "Launch packet boundary_highlight identity_status schema missing or invalid"
}
if ($launchPacket.portable_command -notcontains "--preview-frame-file") {
    throw "Launch packet portable command is missing --preview-frame-file"
}
if ($launchPacket.canvas_preview.preview_frame_path -ne "state/renderer_preview_frame.png") {
    throw "Launch packet canvas_preview preview_frame_path missing or invalid"
}
if ([double]$launchPacket.canvas_preview.preview_frame_interval_s -le 0) {
    throw "Launch packet canvas_preview preview_frame_interval_s missing or invalid"
}
$capabilitiesText = & py -3 taichi_global_bathymetry.py --print-renderer-capabilities
if ($LASTEXITCODE -ne 0) {
    throw "Command failed: py -3 taichi_global_bathymetry.py --print-renderer-capabilities"
}
$capabilitiesRaw = $capabilitiesText -join "`n"
$capabilitiesJsonStart = $capabilitiesRaw.IndexOf("{")
if ($capabilitiesJsonStart -lt 0) {
    throw "Renderer capabilities JSON payload not found"
}
$capabilities = $capabilitiesRaw.Substring($capabilitiesJsonStart) | ConvertFrom-Json
if ($capabilities.preview_frame_stream.schema -ne "rrkal_displaytools.preview_frame_stream.v1") {
    throw "Renderer preview_frame_stream capability missing or invalid"
}
if ($capabilities.active_layer_diagnostics.schema -ne "rrkal_displaytools.active_layer_diagnostics.v1") {
    throw "Renderer active_layer_diagnostics capability missing or invalid"
}
if ($capabilities.ui_handoff_contracts.schema -ne "rrkal_displaytools.ui_handoff_contracts.v1") {
    throw "Renderer ui_handoff_contracts capability missing or invalid"
}
if ($capabilities.boundary_highlight.identity_status_schema -ne "rrkal_displaytools.boundary_identity_status.v1") {
    throw "Renderer boundary_highlight identity_status capability missing or invalid"
}
$closedLoopText = & py -3 taichi_global_bathymetry.py --print-closed-loop-status
if ($LASTEXITCODE -ne 0) {
    throw "Command failed: py -3 taichi_global_bathymetry.py --print-closed-loop-status"
}
$closedLoopRaw = $closedLoopText -join "`n"
$closedLoopJsonStart = $closedLoopRaw.IndexOf("{")
if ($closedLoopJsonStart -lt 0) {
    throw "Closed-loop status JSON payload not found"
}
$closedLoop = $closedLoopRaw.Substring($closedLoopJsonStart) | ConvertFrom-Json
$closedLoopIds = @($closedLoop.closed | ForEach-Object { $_.id })
if ($closedLoopIds -notcontains "diagnostics_handoff_contracts") {
    throw "Closed-loop diagnostics_handoff_contracts missing"
}
if ($closedLoopIds -notcontains "layer_stack_undo_snapshots") {
    throw "Closed-loop layer_stack_undo_snapshots missing"
}
if ($closedLoopIds -notcontains "session_journal_handoff") {
    throw "Closed-loop session_journal_handoff missing"
}
Invoke-CheckedNative py @("-3", "taichi_global_bathymetry.py", "--print-layer-manifest") | Out-Null
Invoke-CheckedNative py @("-3", "rrkal_displaytools_qt_panel.py", "--list-templates") | Out-Null

$scripts = Get-ChildItem scripts -Filter *.ps1
foreach ($script in $scripts) {
    $tokens = $null
    $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile(
        $script.FullName,
        [ref]$tokens,
        [ref]$errors
    ) > $null
    if ($errors -and $errors.Count -gt 0) {
        $errors | Format-List *
        throw "PowerShell parse failed: $($script.Name)"
    }
}

Write-Host "Smoke passed."

