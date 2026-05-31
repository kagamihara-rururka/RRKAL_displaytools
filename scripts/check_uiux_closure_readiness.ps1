param(
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$scriptName = "scripts/check_uiux_closure_readiness.ps1"

function Invoke-JsonPowerShell {
    param([string[]]$ArgumentList)

    $text = $null
    $lastOutput = $null
    for ($attempt = 1; $attempt -le 8; $attempt++) {
        $fileIndex = [Array]::IndexOf($ArgumentList, "-File")
        if ($fileIndex -ge 0 -and $ArgumentList.Count -gt ($fileIndex + 1)) {
            $scriptPath = $ArgumentList[$fileIndex + 1]
            $scriptArgs = @()
            if ($ArgumentList.Count -gt ($fileIndex + 2)) {
                $scriptArgs = $ArgumentList[($fileIndex + 2)..($ArgumentList.Count - 1)]
            }
            $quotedScript = "'" + $scriptPath.Replace("'", "''") + "'"
            $quotedArgs = @($scriptArgs | ForEach-Object {
                if ($_.StartsWith("-")) {
                    $_
                }
                else {
                    "'" + $_.Replace("'", "''") + "'"
                }
            })
            $command = "& $quotedScript"
            if ($quotedArgs.Count -gt 0) {
                $command = "$command $($quotedArgs -join ' ')"
            }
            $text = & powershell.exe -NoProfile -ExecutionPolicy Bypass -Command $command 2>&1
        }
        else {
            $text = & powershell.exe @ArgumentList 2>&1
        }
        if ($LASTEXITCODE -eq 0) {
            $lastOutput = $text
            break
        }
        $lastOutput = $text
        if ($attempt -lt 4) {
            Start-Sleep -Milliseconds ([int](750 * $attempt))
        }
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: powershell $($ArgumentList -join ' ')`n$($lastOutput -join "`n")"
    }
    $raw = $text -join "`n"
    $jsonStart = $raw.IndexOf("{")
    if ($jsonStart -lt 0) {
        throw "JSON payload not found: powershell $($ArgumentList -join ' ')"
    }
    return $raw.Substring($jsonStart) | ConvertFrom-Json
}

if ($ContractOnly) {
    [ordered]@{
        schema = "rrkal_displaytools.uiux_closure_readiness_check.v1"
        source = $scriptName
        status = "contract_only_no_state_write"
        output_schema = "rrkal_displaytools.uiux_closure_readiness_check_result.v1"
        checks = @(
            "review_packet_ready",
            "required_uiux_inspectors_registered",
            "qt_first_primary_ui",
            "uiux_closure_queued_items_visible",
            "timeline_pending_items_visible",
            "layer_preset_selection_scope_ok",
            "layer_shortcuts_ready",
            "research_interaction_ready",
            "renderer_ports_ready",
            "reviewer_route_and_capability_summary_ready",
            "qt_workspace_review_path_ready",
            "render_plan_runtime_merge_blocked"
        )
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_uiux_closure_readiness.ps1"
        boundary = "Check reads no-GUI UIUX/reviewer contracts only; it does not write state, launch Qt/Taichi, move renderer code, or touch RRKAL discovery/download/import/cache governance."
        portable = $true
    } | ConvertTo-Json -Depth 8
    exit 0
}

$reviewPacketScript = Join-Path $RepoRoot "scripts\export_visual_contract_review_packet.ps1"
$qtUiuxScript = Join-Path $RepoRoot "scripts\inspect_qt_uiux_surface.ps1"
$uiuxClosureScript = Join-Path $RepoRoot "scripts\inspect_uiux_closure_status.ps1"
$timelineScript = Join-Path $RepoRoot "scripts\inspect_timeline_uiux.ps1"
$layerPresetsScript = Join-Path $RepoRoot "scripts\inspect_layer_visual_presets.ps1"
$layerShortcutsScript = Join-Path $RepoRoot "scripts\inspect_layer_operator_shortcuts.ps1"
$researchScript = Join-Path $RepoRoot "scripts\inspect_research_interaction.ps1"
$hydrologyScript = Join-Path $RepoRoot "scripts\inspect_hydrology_lod.ps1"
$oceanScript = Join-Path $RepoRoot "scripts\inspect_ocean_material.ps1"
$reviewerRouteScript = Join-Path $RepoRoot "scripts\inspect_reviewer_first_run_route.ps1"
$capabilitySummaryScript = Join-Path $RepoRoot "scripts\export_capability_summary.ps1"
$renderPlanScript = Join-Path $RepoRoot "scripts\inspect_layer_render_plan_performance.ps1"

$reviewPacket = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $reviewPacketScript)
$qtUiux = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $qtUiuxScript)
$uiuxClosure = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $uiuxClosureScript)
$timeline = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $timelineScript)
$layerPresets = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $layerPresetsScript)
$layerShortcuts = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $layerShortcutsScript)
$research = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $researchScript)
$hydrology = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $hydrologyScript)
$ocean = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $oceanScript)
$reviewerRoute = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $reviewerRouteScript)
$capabilitySummary = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $capabilitySummaryScript)
$renderPlan = Invoke-JsonPowerShell @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $renderPlanScript)
$qtPanelSource = Get-Content -Raw -Encoding UTF8 "rrkal_displaytools_qt_panel.py"
$cloneQuickstartDoc = Get-Content -Raw -Encoding UTF8 "docs\QUICKSTART_CLONE.zh-TW.md"

$requiredInspectorIds = @(
    "qt_uiux_surface",
    "uiux_closure_status",
    "timeline_uiux",
    "layer_visual_presets",
    "layer_operator_shortcuts",
    "research_interaction",
    "reviewer_first_run_route",
    "capability_summary",
    "hydrology_lod",
    "ocean_material",
    "layer_render_plan_performance"
)
$inspectorIds = @($reviewPacket.inspector_entry_ids)

$checks = [ordered]@{
    review_packet_ready = ($reviewPacket.status -eq "ready")
    required_uiux_inspectors_registered = (@($requiredInspectorIds | Where-Object { $inspectorIds -notcontains $_ }).Count -eq 0)
    qt_first_primary_ui = ($qtUiux.qt_first -eq $true -and $qtUiux.tk_primary_ui_allowed -eq $false)
    uiux_closure_queued_items_visible = (
        $uiuxClosure.construction_status -eq "queued_items_visible_not_claimed_done" -and
        $uiuxClosure.performance_followup_status -eq "queued_until_render_plan_decoupling_and_parity"
    )
    timeline_pending_items_visible = (
        $timeline.construction_status -eq "timeline_contract_ready_with_visible_pending_items" -and
        @($timeline.readiness_pending) -contains "blend_crossfade_interpolation" -and
        @($timeline.readiness_pending) -contains "visibility_fade_interpolation"
    )
    layer_preset_selection_scope_ok = (
        @($layerPresets.preset_ids) -contains "hydrology_focus" -and
        @($layerPresets.preset_ids) -contains "boundary_focus" -and
        $layerPresets.brush_mask_scope -eq "excluded" -and
        $layerPresets.selection_tool_mode -eq "select_layer"
    )
    layer_shortcuts_ready = (
        $layerShortcuts.ui_direction -eq "qt_first_photoshop_like_layer_operations" -and
        @($layerShortcuts.implemented_action_ids) -contains "select_layer" -and
        @($layerShortcuts.installed_shortcut_ids) -contains "undo_layer_state"
    )
    research_interaction_ready = (
        @($research.research_interaction_action_ids) -contains "pin_pick" -and
        @($research.research_interaction_action_ids) -contains "cursor_geo" -and
        @($research.research_interaction_action_ids) -contains "boundary_json"
    )
    renderer_ports_ready = (
        $hydrology.schema -eq "rrkal_displaytools.hydrology_lod_inspection.v1" -and
        $ocean.schema -eq "rrkal_displaytools.ocean_material_inspection.v1"
    )
    reviewer_route_and_capability_summary_ready = (
        $reviewerRoute.schema -eq "rrkal_displaytools.reviewer_first_run_route.v1" -and
        $reviewerRoute.status -eq "ready" -and
        @($reviewerRoute.next_commands) -contains "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_cross_machine_review_readiness.ps1" -and
        $capabilitySummary.schema -eq "rrkal_displaytools.capability_summary.v1" -and
        $capabilitySummary.status -eq "ready" -and
        @($capabilitySummary.boundaries) -match "RRKAL owns dataset discovery"
    )
    qt_workspace_review_path_ready = (
        $qtPanelSource -like "*Review path: Clone ready -> Reviewer route -> Capability summary -> UIUX closure -> Workspace map*" -and
        $qtPanelSource -like "*Inspect: UIUX closure*" -and
        $qtPanelSource -like "*Inspect: Workspace map*" -and
        $cloneQuickstartDoc -match "Inspect: Reviewer route" -and
        $cloneQuickstartDoc -match "Inspect: Capability summary" -and
        $cloneQuickstartDoc -match "Inspect: UIUX closure" -and
        $cloneQuickstartDoc -match "Inspect: Workspace map"
    )
    render_plan_runtime_merge_blocked = (
        $renderPlan.optimization_target -eq "precompute_layer_state_then_single_render_pass" -and
        $renderPlan.compose_runtime_merge_enabled -eq $false -and
        $renderPlan.merge_preflight_runtime_merge_enabled -eq $false
    )
}

$failed = @($checks.GetEnumerator() | Where-Object { $_.Value -ne $true } | ForEach-Object { $_.Key })
if ($failed.Count -gt 0) {
    throw "UIUX closure readiness check failed: $($failed -join ', ')"
}

[ordered]@{
    schema = "rrkal_displaytools.uiux_closure_readiness_check_result.v1"
    source = $scriptName
    status = "pass"
    ready_for_pre_07_uiux_review = $true
    inspector_count = $reviewPacket.inspector_entry_count
    required_inspector_ids = $requiredInspectorIds
    checks = $checks
    failed_checks = @()
    queued_items_visible = $true
    runtime_merge_enabled = $false
    next_command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\export_visual_contract_review_packet.ps1"
    boundary = "UIUX closure readiness is no-GUI preflight only; renderer extraction still starts only after the 2026-05-31T07:00:00+08:00 gate."
    portable = $true
} | ConvertTo-Json -Depth 10
