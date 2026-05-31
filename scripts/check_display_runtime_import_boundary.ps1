param(
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$scriptName = "scripts/check_display_runtime_import_boundary.ps1"
$bannedImports = @(
    "import PyQt6",
    "from PyQt6",
    "import PySide6",
    "from PySide6",
    "import taichi",
    "from taichi",
    "import matplotlib",
    "from matplotlib",
    "import plotly",
    "from plotly",
    "import vispy",
    "from vispy",
    "import pyvista",
    "from pyvista",
    "import vtk",
    "from vtk"
)

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.display_runtime_import_boundary_check.v1"
        source = $scriptName
        status = "contract_only_no_launch_side_effect"
        checked_scope = "display_runtime/*.py"
        banned_imports = $bannedImports
        boundary = "display_runtime skeletons may define landing zones, but concrete renderer packages stay out until adapter parity exists."
        portable = $true
    } | ConvertTo-Json -Depth 8
    exit 0
}

$hits = @()
$checkedFiles = @(Get-ChildItem -LiteralPath "display_runtime" -Filter "*.py" -File | Sort-Object Name)

foreach ($file in $checkedFiles) {
    $sourceLines = Get-Content -LiteralPath $file.FullName -Encoding UTF8
    foreach ($bannedImport in $bannedImports) {
        foreach ($line in $sourceLines) {
            $trimmedLine = $line.Trim()
            if ($trimmedLine -like "$bannedImport*") {
                $hits += [ordered]@{
                    file = $file.FullName.Replace($RepoRoot + "\", "")
                    banned_import = $bannedImport
                    line = $trimmedLine
                }
            }
        }
    }
}

$status = "pass"
if ($hits.Count -gt 0) {
    $status = "fail"
}

$result = [ordered]@{
    schema = "rrkal_displaytools.display_runtime_import_boundary_check.v1"
    source = $scriptName
    status = $status
    checked_scope = "display_runtime/*.py"
    checked_file_count = $checkedFiles.Count
    checked_files = @($checkedFiles | ForEach-Object { $_.FullName.Replace($RepoRoot + "\", "") })
    banned_imports = $bannedImports
    banned_import_hits = $hits
    boundary = "display_runtime currently defines landing-zone contracts only; renderer packages enter later through explicit adapter slices."
}

$result | ConvertTo-Json -Depth 10
if ($hits.Count -gt 0) {
    exit 1
}
