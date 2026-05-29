param(
    [string]$Profile,
    [string]$Template,
    [switch]$SmokeFirst,
    [switch]$HandoffFirst
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

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

if ($SmokeFirst) {
    Invoke-CheckedNative powershell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\smoke.ps1")
}

if ($HandoffFirst) {
    Invoke-CheckedNative powershell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts\inspect_handoff.ps1")
}

$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (Test-Path $VenvPython) {
    $python = $VenvPython
    $pythonArgs = @()
} else {
    $python = "py"
    $pythonArgs = @("-3")
}

$qtArgs = @("rrkal_displaytools_qt_panel.py")
if ($Profile) {
    $qtArgs += @("--profile", $Profile)
}
if ($Template) {
    $qtArgs += @("--template", $Template)
}

Write-Host "RRKAL_displaytools Qt launcher"
Write-Host "Repo: $RepoRoot"
Write-Host "Python: $python $($pythonArgs -join ' ')"
Write-Host "Options: SmokeFirst=$SmokeFirst HandoffFirst=$HandoffFirst"

Invoke-CheckedNative $python ($pythonArgs + $qtArgs)
