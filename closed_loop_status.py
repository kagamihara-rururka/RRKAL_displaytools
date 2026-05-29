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
                "id": "renderer_capability_discovery",
                "scope": ["renderer capabilities", "layer manifest", "profile templates"],
                "evidence": [
                    "--print-renderer-capabilities",
                    "--print-layer-manifest",
                    "rrkal_displaytools_qt_panel.py --list-templates",
                ],
            },
            {
                "id": "cross_machine_bootstrap_docs",
                "scope": ["clone", "venv setup", "smoke", "Qt panel launch"],
                "evidence": ["docs/QUICKSTART_CLONE.zh-TW.md", "README.md"],
            },
        ],
        "partial": [
            {
                "id": "boundary_highlight_mask",
                "applies": ["line hover mask", "outline glow", "closed-ring polygon fill preview"],
                "pending": ["territory_feature_identity", "open_line_area_inference", "fill_shader_contrast_gamma"],
                "evidence": ["boundary-highlight-json", "boundary-highlight-ack-file"],
            },
            {
                "id": "qt_renderer_preview",
                "applies": ["Qt canvas state preview", "runtime JSON inspectors"],
                "pending": ["embedded renderer thumbnail"],
                "evidence": [
                    "Qt Canvas Preview",
                    "renderer_layer_runtime_state.json",
                    "renderer_layer_pick_state.json",
                ],
            },
            {
                "id": "renderer_output_provenance",
                "applies": ["image output metadata sidecar", "RRKAL manifest reference passthrough"],
                "pending": ["RRKAL data manifest validation/ingest"],
                "evidence": ["--output", "--rrkal-data-manifest-ref", "renderer_output_metadata.v1"],
            },
        ],
        "pending": [
            "full territory/EEZ feature identity",
            "open-line area inference",
            "embedded renderer thumbnail",
            "RRKAL data manifest validation/ingest",
        ],
    }
