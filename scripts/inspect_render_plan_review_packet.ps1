param(
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$scriptName = "scripts/inspect_render_plan_review_packet.ps1"
$schema = "rrkal_displaytools.render_plan_review_packet.v1"

if ($ContractOnly) {
    [ordered]@{
        schema = $schema
        source = $scriptName
        status = "contract_only_no_runtime"
        inspectors = @(
            "scripts/inspect_render_plan_metadata_summary.ps1",
            "scripts/inspect_render_plan_single_pass_preflight.ps1"
        )
        boundary = "Reviewer packet only; it does not launch Qt, Taichi, render frames, write metadata, or enable runtime single-pass composition."
        portable = $true
    } | ConvertTo-Json -Depth 8
    exit 0
}

$metadataSummary = powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "scripts\inspect_render_plan_metadata_summary.ps1") | ConvertFrom-Json
$singlePassPreflight = powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $RepoRoot "scripts\inspect_render_plan_single_pass_preflight.ps1") | ConvertFrom-Json
$ready = $metadataSummary.status -eq "ready" -and $singlePassPreflight.status -eq "ready"

[ordered]@{
    schema = $schema
    source = $scriptName
    status = if ($ready) { "ready" } else { "incomplete" }
    metadata_summary_status = $metadataSummary.status
    metadata_summary_schema = $metadataSummary.verifies_schema
    metadata_summary_field = $metadataSummary.summary_field
    adapter_payload_summary_schema = $metadataSummary.verifies_adapter_payload_schema
    adapter_payload_status_field = $metadataSummary.adapter_payload_status_field
    single_pass_preflight_status = $singlePassPreflight.status
    single_pass_preflight_schema = $singlePassPreflight.verifies_schema
    runtime_single_pass_enabled = $singlePassPreflight.runtime_single_pass_enabled
    clone_first_review_commands = @(
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_render_plan_review_packet.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_render_plan_metadata_summary.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_render_plan_single_pass_preflight.ps1"
    )
    next_step = "Use this packet as the quick render-plan decoupling review entrypoint after clone."
    boundary = "Reviewer packet only; it aggregates source-only inspectors and does not launch Qt, Taichi, render frames, write metadata, or enable runtime single-pass composition."
    portable = $true
} | ConvertTo-Json -Depth 8
