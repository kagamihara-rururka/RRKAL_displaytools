param(
    [string]$OutputDir = "state/performance",
    [switch]$ContractOnly,
    [switch]$ThresholdGuardOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$venvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$useLocalVenv = Test-Path -LiteralPath $venvPython
$pythonCommand = if ($useLocalVenv) { $venvPython } else { "py" }

if ($ContractOnly) {
    if ($useLocalVenv) {
        & $pythonCommand "performance_telemetry.py" "--contract-only"
    } else {
        & $pythonCommand "-3" "performance_telemetry.py" "--contract-only"
    }
    exit $LASTEXITCODE
}

if ($ThresholdGuardOnly) {
    if ($useLocalVenv) {
        & $pythonCommand "performance_telemetry.py" "--threshold-guard-only"
    } else {
        & $pythonCommand "-3" "performance_telemetry.py" "--threshold-guard-only"
    }
    exit $LASTEXITCODE
}

if ($useLocalVenv) {
    & $pythonCommand "performance_telemetry.py" "--output-dir" $OutputDir
} else {
    & $pythonCommand "-3" "performance_telemetry.py" "--output-dir" $OutputDir
}
exit $LASTEXITCODE
