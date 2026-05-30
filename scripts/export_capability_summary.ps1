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
        schema = "rrkal_displaytools.capability_summary_export.v1"
        output_schema = "rrkal_displaytools.capability_summary.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\export_capability_summary.ps1"
        sections = @(
            "current_capabilities",
            "planned_capabilities",
            "boundaries",
            "recommended_next_stage"
        )
        boundary = @(
            "summary only",
            "does not launch Qt or Taichi",
            "does not move renderer code",
            "does not perform RRKAL discovery/download/import/cache governance"
        )
    })
    exit 0
}

$summary = [ordered]@{
    schema = "rrkal_displaytools.capability_summary.v1"
    status = "ready"
    summary_role = "post_push_user_report_source"
    current_capabilities = @(
        [ordered]@{
            id = "qt_first_control_panel"
            status = "mvp"
            description = "PyQt6-first control board with profile/templates, layer controls, renderer diagnostics, Replay/contracts, Ocean 3D controls and Timeline review surfaces."
            review_command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_qt_uiux_surface.ps1"
        },
        [ordered]@{
            id = "layer_control_and_selection"
            status = "mvp"
            description = "Layer visibility, selection, presets, shortcuts, lock/opacity/blend actions and copyable layer provenance; brush/mask tools are out of scope."
            review_command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_layer_operator_shortcuts.ps1"
        },
        [ordered]@{
            id = "research_interactions"
            status = "mvp"
            description = "Selected-layer review, cursor latitude/longitude, Pin pick with occlusion, Boundary/EEZ visual emphasis controls and copyable provenance."
            review_command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_research_interaction.ps1"
        },
        [ordered]@{
            id = "ocean_material_controls"
            status = "in_progress"
            description = "Ocean 3D scalar controls, safe preview, cost estimate and sea-state/material review port are visible and contract-gated."
            review_command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_ocean_material.ps1"
        },
        [ordered]@{
            id = "timeline_uiux"
            status = "mvp_with_visible_pending_items"
            description = "Timeline playback/export readiness, camera/ocean/layer interpolation and visible pending blend/visibility fade work."
            review_command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_timeline_uiux.ps1"
        },
        [ordered]@{
            id = "cross_machine_review"
            status = "mvp"
            description = "Public clone readiness, setup/smoke/handoff first-run route and reviewer packet portability are available without launching Qt."
            review_command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_cross_machine_review_readiness.ps1"
        },
        [ordered]@{
            id = "pre7_closure_readiness"
            status = "mvp"
            description = "Compact pre-7 closure readiness is available through a no-GUI checker, reviewer packet, clone quickstart and Qt Replay/contracts action."
            review_command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_pre7_closure_readiness.ps1"
        },
        [ordered]@{
            id = "pre_decoupling_gate"
            status = "armed_for_post_0700"
            description = "Formal pre-decoupling readiness, boundary inspection, render-plan compose work order and not-before gate protect the first code move."
            review_command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_pre_decoupling_readiness.ps1"
        },
        [ordered]@{
            id = "render_plan_compose_source_map"
            status = "ready_no_code_move"
            description = "No-code-move source map lists the monolith helper seams for the first post-7 render-plan compose extraction."
            review_command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_render_plan_compose_source_map.ps1"
        }
    )
    planned_capabilities = @(
        [ordered]@{
            id = "dockable_photoshop_like_panels"
            status = "planned_after_renderer_boundaries_stabilize"
            description = "Move grouped forms toward dockable scientific operator panels without introducing Tk as primary UI."
        },
        [ordered]@{
            id = "render_plan_compose_decoupling"
            status = "planned_after_0700_gate"
            description = "Extract render-plan compose into a module before enabling collapsed layer compose runs."
        },
        [ordered]@{
            id = "layer_render_plan_performance"
            status = "planned_after_decoupling"
            description = "Precompute layer state once and render through a single compose pass with zero-diff parity evidence."
        },
        [ordered]@{
            id = "timeline_blend_visibility_runtime"
            status = "queued"
            description = "Close blend crossfade and visibility fade only after runtime evidence exists."
        },
        [ordered]@{
            id = "authoritative_boundary_identity"
            status = "deferred_to_data_contract"
            description = "Displaytools owns visual emphasis; authoritative territory/EEZ identity must come from a verified RRKAL/data contract."
        }
    )
    boundaries = @(
        "Qt/PyQt6 is the primary UI path; Tk is not primary.",
        "RRKAL owns dataset discovery, download, import, install registry, cache lifecycle and asset repair.",
        "Displaytools owns renderer/UI contracts, material controls, visual review packets and no-GUI smoke evidence.",
        "Renderer code movement is blocked until the post-07 formal pre-decoupling gate."
    )
    recommended_next_stage = "Continue pre-07 UIUX reviewer closure, then start render-plan compose decoupling after the formal 07:00 +08:00 gate."
}

Write-JsonObject $summary
