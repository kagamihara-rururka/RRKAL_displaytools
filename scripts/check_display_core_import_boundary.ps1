param(
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$scriptName = "scripts/check_display_core_import_boundary.ps1"
$bannedImports = @(
    "import PyQt6",
    "from PyQt6",
    "import taichi",
    "from taichi",
    "import matplotlib",
    "from matplotlib",
    "import plotly",
    "from plotly",
    "import vispy",
    "from vispy",
    "import vtk",
    "from vtk"
)

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.display_core_import_boundary_check.v1"
        source = $scriptName
        status = "contract_only_no_launch_side_effect"
        checked_scope = "display_core/*.py"
        banned_imports = $bannedImports
        boundary = "display_core must remain renderer-package-free; adapter modules own concrete Qt/Taichi/chart dependencies."
        portable = $true
    } | ConvertTo-Json -Depth 8
    exit 0
}

$hits = @()
$checkedFiles = @(Get-ChildItem -LiteralPath "display_core" -Filter "*.py" -File | Sort-Object Name)

foreach ($file in $checkedFiles) {
    $source = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8
    foreach ($bannedImport in $bannedImports) {
        if ($source -like "*$bannedImport*") {
            $hits += [ordered]@{
                file = $file.FullName.Replace($RepoRoot + "\", "")
                banned_import = $bannedImport
            }
        }
    }
}

$status = "pass"
if ($hits.Count -gt 0) {
    $status = "fail"
}

$result = [ordered]@{
    schema = "rrkal_displaytools.display_core_import_boundary_check.v1"
    source = $scriptName
    status = $status
    checked_scope = "display_core/*.py"
    checked_file_count = $checkedFiles.Count
    checked_files = @($checkedFiles | ForEach-Object { $_.FullName.Replace($RepoRoot + "\", "") })
    banned_imports = $bannedImports
    banned_import_hits = $hits
    boundary = "display_core defines contracts only; renderer adapters own Qt, Taichi and concrete chart package imports."
}

$result | ConvertTo-Json -Depth 10
if ($hits.Count -gt 0) {
    exit 1
}
