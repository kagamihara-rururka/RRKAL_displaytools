param(
    [string]$Output = "state\showcase\quick_smoke.png",
    [string]$PreviewFrame = "state\showcase\quick_smoke_preview_frame.png",
    [string]$StyleProfile = "scientific",
    [int]$Width = 640,
    [int]$Height = 360,
    [int]$TopoStep = 96
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$outputPath = Join-Path $RepoRoot $Output
$outputDir = Split-Path -Parent $outputPath
if ($outputDir) {
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
}
$previewFramePath = Join-Path $RepoRoot $PreviewFrame
$previewFrameDir = Split-Path -Parent $previewFramePath
if ($previewFrameDir) {
    New-Item -ItemType Directory -Force -Path $previewFrameDir | Out-Null
}

py -3 taichi_global_bathymetry.py `
    --headless `
    --once `
    --demo-closed-loop `
    --style-profile $StyleProfile `
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
    throw "Quick smoke render output missing: $outputPath"
}
if (-not (Test-Path -LiteralPath $previewFramePath)) {
    throw "Quick smoke preview frame missing: $previewFramePath"
}
if ((Get-Item -LiteralPath $previewFramePath).Length -le 0) {
    throw "Quick smoke preview frame is empty: $previewFramePath"
}

$metadataPath = "$outputPath.metadata.json"
if (-not (Test-Path -LiteralPath $metadataPath)) {
    throw "Quick smoke render metadata missing: $metadataPath"
}

$metadata = Get-Content -LiteralPath $metadataPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($metadata.schema -ne "rrkal_displaytools.renderer_output_metadata.v1") {
    throw "Unexpected quick smoke metadata schema: $($metadata.schema)"
}

Write-Host "Quick smoke render output: $outputPath"
Write-Host "Quick smoke preview frame: $previewFramePath"
Write-Host "Quick smoke render metadata: $metadataPath"
