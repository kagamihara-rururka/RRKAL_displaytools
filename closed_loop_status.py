"""Shared closed-loop status contract for RRKAL_displaytools."""

from __future__ import annotations


def renderer_closed_loop_status_packet() -> dict[str, object]:
    return {
        "schema": "rrkal_displaytools.closed_loop_status.v1",
        "closed": [
            {
                "id": "qt_profile_launch_packet",
                "scope": ["profile templates", "profile schema", "launch packet export"],
                "evidence": ["profile_schema.py", "profiles/*.json", "scripts/export_launch_packet.py"],
            },
            {
                "id": "layer_runtime_bridge",
                "scope": ["visibility", "lock guard", "opacity", "blend", "selected renderer target"],
                "evidence": ["layer-runtime-state-file", "layer-runtime-ack-file"],
            },
            {
                "id": "selected_layer_picking_bridge",
                "scope": ["Pin", "traffic point", "boundary line", "hydrology line"],
                "evidence": ["layer-pick-state-file", "rrkal_displaytools.renderer_layer_pick_state.v1"],
            },
            {
                "id": "layer_stack_undo_snapshots",
                "scope": ["visibility", "lock", "opacity", "blend mode", "active layer"],
                "evidence": [
                    "Qt Layers Undo 圖層狀態",
                    "rrkal_displaytools.layer_stack_undo.v1",
                    "launch_packet layer_undo",
                ],
            },
            {
                "id": "session_journal_handoff",
                "scope": ["layer runtime history", "Pin pick history", "renderer ack presence", "session event portability"],
                "evidence": [
                    "launch_packet session_journal",
                    "research provenance session_journal",
                    "rrkal_displaytools.session_journal.v1",
                ],
            },
            {
                "id": "renderer_capability_discovery",
                "scope": ["renderer capabilities", "layer manifest", "profile templates"],
                "evidence": [
                    "--print-renderer-capabilities",
                    "--print-layer-manifest",
                    "rrkal_displaytools_qt_panel.py --list-templates",
                ],
            },
            {
                "id": "diagnostics_handoff_contracts",
                "scope": [
                    "active_layer_diagnostics",
                    "boundary_highlight.identity_status",
                    "layer_undo",
                    "session_journal",
                    "canvas_preview stream provenance",
                ],
                "evidence": [
                    "launch_packet active_layer_diagnostics",
                    "launch_packet boundary_highlight.identity_status",
                    "launch_packet layer_undo",
                    "launch_packet session_journal",
                    "renderer capabilities active_layer_diagnostics",
                    "renderer capabilities ui_handoff_contracts",
                    "profile_schema optional canvas_preview",
                ],
            },
            {
                "id": "cross_machine_bootstrap_docs",
                "scope": ["clone", "venv setup", "smoke", "Qt panel launch"],
                "evidence": ["scripts/run_qt_panel.ps1", "docs/QUICKSTART_CLONE.zh-TW.md", "README.md"],
            },
        ],
        "partial": [
            {
                "id": "boundary_highlight_mask",
                "applies": [
                    "line hover mask",
                    "outline glow",
                    "closed-ring polygon fill preview",
                    "closed-ring fill contrast/gamma",
                    "closed-ring area hit test",
                    "source-property feature identity",
                    "maritime property key identity",
                    "boundary identity-status handoff",
                ],
                "pending": ["authoritative_polygon_territory_identity", "open_line_area_inference"],
                "evidence": ["boundary-highlight-json", "boundary-highlight-ack-file"],
            },
            {
                "id": "qt_renderer_preview",
                "applies": [
                    "Qt canvas state preview",
                    "runtime JSON inspectors",
                    "static renderer output thumbnail",
                    "static thumbnail auto-refresh",
                    "file-based live renderer frame stream",
                ],
                "pending": ["low-latency IPC/GPU frame stream"],
                "evidence": [
                    "Qt Canvas Preview",
                    "state/showcase/*.png",
                    "state/renderer_preview_frame.png",
                    "renderer_layer_runtime_state.json",
                    "renderer_layer_pick_state.json",
                ],
            },
            {
                "id": "qt_timeline_panel",
                "applies": [
                    "visible timeline dock",
                    "UI-only keyframe storage",
                    "UI-only keyframe restore",
                    "UI-only playback controls",
                    "No-GUI profile keyframe handoff",
                    "launch packet timeline_state contract",
                    "provenance timeline_state",
                ],
                "pending": ["renderer_timeline_playback", "animation_export"],
                "evidence": ["Timeline dock controls", "rrkal_displaytools.timeline_state.v1"],
            },
            {
                "id": "renderer_output_provenance",
                "applies": ["image output metadata sidecar", "RRKAL manifest reference passthrough"],
                "pending": [],
                "external_dependencies": ["RRKAL-side data manifest validation/ingest/governance"],
                "evidence": ["--output", "--rrkal-data-manifest-ref", "renderer_output_metadata.v1"],
            },
        ],
        "pending": [
            "authoritative polygon territory/EEZ identity",
            "open-line area inference",
            "low-latency IPC/GPU frame stream",
        ],
        "external_dependencies": ["RRKAL data manifest validation/ingest/governance"],
    }
