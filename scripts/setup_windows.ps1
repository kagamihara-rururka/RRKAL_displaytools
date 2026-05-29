param(
    [switch]$UserInstall
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$python = "py"
$pythonArgs = @("-3")

Write-Host "RRKAL_displaytools setup"
Write-Host "Repo: $RepoRoot"

& $python @pythonArgs -m pip install --upgrade pip

$installArgs = @("-3", "-m", "pip", "install", "-r", "requirements.txt")
if ($UserInstall) {
    $installArgs += "--user"
}
& $python @installArgs

Write-Host ""
Write-Host "Setup complete."
Write-Host "Run: py -3 rrkal_displaytools_qt_panel.py"
