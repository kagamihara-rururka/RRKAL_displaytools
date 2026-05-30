param(
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

function Write-JsonObject {
    param([object]$Value)
    $Value | ConvertTo-Json -Depth 30
}

if ($ContractOnly) {
    Write-JsonObject ([ordered]@{
        schema = "rrkal_displaytools.reviewer_first_run_route_inspector.v1"
        output_schema = "rrkal_displaytools.reviewer_first_run_route.v1"
        required_contracts = @(
            "rrkal_displaytools.cross_machine_review_readiness_check_result.v1",
            "rrkal_displaytools.uiux_closure_readiness_check_result.v1",
            "rrkal_displaytools.research_interaction_review.v1",
            "rrkal_displaytools.ocean_material_review.v1"
        )
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_reviewer_first_run_route.ps1"
        boundary = @(
            "review route only",
            "does not launch Qt",
            "does not move renderer code",
            "does not perform RRKAL discovery/download/import/cache governance"
        )
    })
    exit 0
}

$route = [ordered]@{
    schema = "rrkal_displaytools.reviewer_first_run_route.v1"
    status = "ready"
    route_id = "clone_to_scientific_ui_review"
    audience = "researcher_or_cross_machine_reviewer"
    qt_first = $true
    tk_primary_ui_allowed = $false
    no_data_governance = $true
    renderer_code_move_allowed_before_0700 = $false
    phases = @(
        [ordered]@{
            id = "clone_setup"
            command = "git clone https://github.com/Kagamihara-Ruruka/RRKAL_displaytools.git"
            next = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup_windows.ps1"
            expected = "public main branch clone with Windows helper available"
        },
        [ordered]@{
            id = "smoke"
            command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1"
            expected = "no-GUI smoke passes before review or push"
        },
        [ordered]@{
            id = "handoff"
            command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_handoff.ps1"
            expected = "launch packet, renderer capabilities and reviewer packet are visible"
        },
        [ordered]@{
            id = "qt_review"
            command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_qt_panel.ps1"
            expected = "Qt-first control board opens with Layers, Renderer diagnostics, Replay/contracts and Ocean 3D controls"
            surfaces = @(
                "Layers dock selection and visibility",
                "Profile/templates launcher",
                "Renderer diagnostics",
                "Replay/contracts",
                "Ocean 3D control board",
                "Timeline panel"
            )
        },
        [ordered]@{
            id = "research_interaction"
            command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_research_interaction.ps1"
            expected = "researcher interactions are reviewable without guessing the UI state"
            tools = @(
                "select_layer",
                "cursor_geodesy",
                "pin_pick_with_occlusion",
                "boundary_emphasis",
                "copyable_provenance"
            )
        }
    )
    uiux_surfaces = @(
        "layer selection",
        "cursor latitude/longitude",
        "pin marker with globe occlusion",
        "boundary/EEZ emphasis RGB contrast opacity gamma breathing controls",
        "Ocean 3D safe preview and cost estimate",
        "timeline playback/export readiness"
    )
    done_when = @(
        "smoke passes",
        "UIUX closure readiness passes",
        "cross-machine review readiness passes",
        "handoff inspection exposes launch and reviewer packet state"
    )
    visible_pending_items = @(
        "blend crossfade remains visible pending",
        "visibility fade remains visible pending",
        "authoritative polygon/EEZ identity is separate from displaytools visual emphasis",
        "render-plan compose optimization starts after the post-07 decoupling gate"
    )
    next_commands = @(
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_cross_machine_review_readiness.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_uiux_closure_readiness.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_research_interaction.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_ocean_material.ps1"
    )
}

Write-JsonObject $route
