param(
    [string]$OutputDir = "state\style_previews",
    [string[]]$StyleProfiles = @("scientific", "nautical", "parchment", "tactical"),
    [int]$Width = 640,
    [int]$Height = 360,
    [int]$TopoStep = 96
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$validStyles = @("scientific", "nautical", "parchment", "tactical")
$outputRoot = Join-Path $RepoRoot $OutputDir
New-Item -ItemType Directory -Force -Path $outputRoot | Out-Null

foreach ($style in $StyleProfiles) {
    if ($validStyles -notcontains $style) {
        throw "Unsupported style profile for preview: $style"
    }

    $outputPath = Join-Path $outputRoot "$style.png"
    $previewFramePath = Join-Path $outputRoot "$style.preview_frame.png"

    py -3 taichi_global_bathymetry.py `
        --headless `
        --once `
        --demo-closed-loop `
        --style-profile $style `
        --topo-source synthetic `
        --topo-step $TopoStep `
        --width $Width `
        --height $Height `
        --no-lake-layer `
        --no-river-layer `
        --no-border-layer `
        --no-territorial-sea-layer `
        --no-eez-layer `
        --no-high-seas-layer `
        --no-aircraft-layer `
        --no-pin-layer `
        --output $outputPath `
        --preview-frame-file $previewFramePath `
        --preview-frame-interval 0.05

    if (-not (Test-Path -LiteralPath $outputPath)) {
        throw "Style preview output missing: $outputPath"
    }
    if ((Get-Item -LiteralPath $outputPath).Length -le 0) {
        throw "Style preview output is empty: $outputPath"
    }

    $metadataPath = "$outputPath.metadata.json"
    if (-not (Test-Path -LiteralPath $metadataPath)) {
        throw "Style preview metadata missing: $metadataPath"
    }

    $metadata = Get-Content -LiteralPath $metadataPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($metadata.schema -ne "rrkal_displaytools.renderer_output_metadata.v1") {
        throw "Unexpected style preview metadata schema: $($metadata.schema)"
    }

    Write-Host "Style preview output: $outputPath"
    Write-Host "Style preview metadata: $metadataPath"
}
