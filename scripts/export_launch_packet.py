from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = ROOT / "profiles"
PREVIEW_FRAME_PATH = "state/renderer_preview_frame.png"
PREVIEW_FRAME_INTERVAL_S = 0.75
TIMELINE_STATE_PATH = "state/renderer_timeline_state.json"
TIMELINE_ACK_PATH = "state/renderer_timeline_ack.json"
sys.path.insert(0, str(ROOT))

from closed_loop_status import renderer_closed_loop_status_packet  # noqa: E402
from profile_schema import load_profile_payload, profile_payload_errors  # noqa: E402


BOOL_FLAGS = {
    "show_grid": "show-grid",
    "show_stars": "show-stars",
    "lake_layer": "lake-layer",
    "river_layer": "river-layer",
    "border_layer": "border-layer",
    "territorial_sea_layer": "territorial-sea-layer",
    "eez_layer": "eez-layer",
    "high_seas_layer": "high-seas-layer",
    "aircraft_layer": "aircraft-layer",
    "pin_layer": "pin-layer",
    "ocean_material": "ocean-material",
    "terrain_contours": "terrain-contours",
    "scale_bar": "scale-bar",
    "vehicle_icons": "vehicle-icons",
    "demo_closed_loop": "demo-closed-loop",
}
LAYER_RUNTIME_ID_ALIASES = {
    "show_grid": "grid",
    "show_stars": "stars",
    "lake_layer": "lakes",
    "river_layer": "rivers",
    "border_layer": "borders",
    "territorial_sea_layer": "territorial_sea",
    "eez_layer": "eez",
    "high_seas_layer": "high_seas",
    "aircraft_layer": "aircraft",
    "pin_layer": "pins",
    "ocean_material": "ocean_material",
    "terrain_contours": "contours",
    "scale_bar": "scale",
    "vehicle_icons": "vehicle_icons",
}

DEFAULT_CANVAS_PREVIEW = {
    "schema": "rrkal_displaytools.canvas_preview.v1",
    "mode": "state",
    "renderer_thumbnail_path": None,
    "preview_frame_path": PREVIEW_FRAME_PATH,
    "preview_frame_interval_s": PREVIEW_FRAME_INTERVAL_S,
    "renderer_sync": "ui_state_preview",
}
DEFAULT_BOUNDARY_IDENTITY_STATUS = {
    "schema": "rrkal_displaytools.boundary_identity_status.v1",
    "applied": [
        "source_property_feature_identity",
        "maritime_property_key_identity",
        "closed_ring_area_hit_test",
        "closed_ring_fill_preview",
    ],
    "pending": [
        "authoritative_polygon_territory_identity",
        "open_line_area_inference",
    ],
    "boundary": "visual/source-property preview only; not an authoritative legal boundary resolution",
}
DEFAULT_BOUNDARY_HIGHLIGHT = {
    "schema": "rrkal_displaytools.boundary_highlight_mask.v1",
    "enabled": True,
    "trigger": "hover",
    "target_layers": ["border_layer", "territorial_sea_layer", "eez_layer", "high_seas_layer"],
    "color_rgb": [255, 190, 72],
    "contrast": 45,
    "alpha": 48,
    "gamma": 100,
    "feather": 14,
    "breathing": {
        "enabled": True,
        "speed": 42,
        "amplitude": 16,
    },
    "renderer_sync": "renderer_line_fill_identity_status_handoff",
    "identity_status": DEFAULT_BOUNDARY_IDENTITY_STATUS,
}


def resolve_profile(profile: Path | None, template: str | None) -> Path:
    if profile is not None:
        return profile
    if not template:
        raise ValueError("Either --profile or --template is required")
    template_name = template[:-5] if template.endswith(".json") else template
    return PROFILE_DIR / f"{template_name}.json"


def renderer_args(
    profile: dict[str, object],
    rrkal_data_manifest_ref: str = "",
    timeline_state_file: str = TIMELINE_STATE_PATH,
    timeline_ack_file: str = TIMELINE_ACK_PATH,
) -> list[str]:
    renderer = profile["renderer"]
    material = profile["ocean_material"]
    layers = profile["layers"]
    assert isinstance(renderer, dict)
    assert isinstance(material, dict)
    assert isinstance(layers, dict)
    args = [
        "--style-profile",
        str(renderer["style_profile"]),
        "--ui",
        str(renderer["ui_backend"]),
        "--topo-source",
        str(renderer["topo_source"]),
        "--data-mode",
        str(renderer["data_mode"]),
        "--width",
        str(renderer["width"]),
        "--height",
        str(renderer["height"]),
        "--topo-step",
        str(renderer["topo_step"]),
        "--ti-arch",
        str(renderer["taichi_arch"]),
        "--ocean-wave-strength",
        str(material["wave_strength"]),
        "--ocean-roughness",
        str(material["roughness"]),
        "--ocean-foam",
        str(material["foam"]),
        "--preview-frame-file",
        PREVIEW_FRAME_PATH,
        "--preview-frame-interval",
        str(PREVIEW_FRAME_INTERVAL_S),
        "--timeline-state-file",
        timeline_state_file,
        "--timeline-ack-file",
        timeline_ack_file,
    ]
    for key, flag in BOOL_FLAGS.items():
        args.append(f"--{flag}" if layers[key] else f"--no-{flag}")
    manifest_ref = rrkal_data_manifest_ref or str(renderer.get("rrkal_data_manifest_ref", "")).strip()
    if manifest_ref:
        args.extend(["--rrkal-data-manifest-ref", manifest_ref])
    return args


def profile_display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def canvas_preview_packet(profile: dict[str, object]) -> dict[str, object]:
    payload = profile.get("canvas_preview")
    if isinstance(payload, dict):
        merged = dict(DEFAULT_CANVAS_PREVIEW)
        merged.update(payload)
        return merged
    return dict(DEFAULT_CANVAS_PREVIEW)


def boundary_highlight_packet(profile: dict[str, object]) -> dict[str, object] | None:
    merged = dict(DEFAULT_BOUNDARY_HIGHLIGHT)
    payload = profile.get("boundary_highlight")
    if isinstance(payload, dict):
        merged.update(payload)
    identity_status = merged.get("identity_status")
    if isinstance(identity_status, dict):
        merged["identity_status"] = {
            **DEFAULT_BOUNDARY_IDENTITY_STATUS,
            **identity_status,
        }
    else:
        merged["identity_status"] = dict(DEFAULT_BOUNDARY_IDENTITY_STATUS)
    return merged


def active_layer_diagnostics_packet(profile: dict[str, object]) -> dict[str, object]:
    selected_layer = profile.get("selected_layer")
    selected_layer = selected_layer if isinstance(selected_layer, str) else None
    renderer_target = LAYER_RUNTIME_ID_ALIASES.get(selected_layer) if selected_layer else None
    return {
        "schema": "rrkal_displaytools.active_layer_diagnostics.v1",
        "selected_layer": selected_layer,
        "renderer_target": renderer_target,
        "diagnostics_text": "no runtime ack/pick in no-GUI export",
        "runtime_ack_file": "state/renderer_layer_runtime_ack.json",
        "runtime_ack": None,
        "pick_state_file": "state/renderer_layer_pick_state.json",
        "pick_state": None,
    }


def layer_filter_packet(profile: dict[str, object]) -> dict[str, object]:
    payload = profile.get("layer_filter")
    if isinstance(payload, dict):
        query = str(payload.get("query", ""))
        preset = str(payload.get("preset", "custom"))
    else:
        query = ""
        preset = "all"
    preset_queries = {
        "all": "",
        "hydrology": "hydro",
        "maritime": "maritime",
        "traffic": "traffic",
        "visual_aids": "aids",
    }
    if not query and preset in preset_queries:
        query = preset_queries[preset]
    aliases = {
        "show_grid": "visual aids grid graticule",
        "show_stars": "visual aids stars background",
        "lake_layer": "hydro hydrology water lake lakes",
        "river_layer": "hydro hydrology water river rivers",
        "border_layer": "boundary border country territory sovereign",
        "territorial_sea_layer": "boundary maritime territorial sea territory",
        "eez_layer": "boundary maritime eez economic exclusive zone",
        "high_seas_layer": "boundary maritime high seas ocean",
        "aircraft_layer": "traffic aircraft adsb ads-b",
        "pin_layer": "pin marker annotation research",
        "ocean_material": "ocean material sea surface",
        "terrain_contours": "visual aids terrain contours",
        "scale_bar": "visual aids scale bar",
        "vehicle_icons": "traffic vehicle ais vessel ship",
    }
    query_parts = query.lower().split()
    matched_layers = [
        key for key in BOOL_FLAGS
        if key != "demo_closed_loop"
        and (
            not query_parts
            or all(part in f"{key} {BOOL_FLAGS[key]} {aliases.get(key, '')}".lower() for part in query_parts)
        )
    ]
    return {
        "schema": "rrkal_displaytools.layer_filter.v1",
        "mode": "no_gui_export_status",
        "preset": preset if preset else "all",
        "available_presets": ["all", "hydrology", "maritime", "traffic", "visual_aids", "custom"],
        "query": query,
        "matched_layers": matched_layers,
        "matched_count": len(matched_layers),
        "total_layers": len([key for key in BOOL_FLAGS if key != "demo_closed_loop"]),
        "boundary": "No-GUI launch packet preserves Qt row-filter state only; renderer layer state is unchanged.",
    }


def layer_undo_packet() -> dict[str, object]:
    return {
        "schema": "rrkal_displaytools.layer_stack_undo.v1",
        "depth": 0,
        "capacity": 0,
        "tracking_enabled": False,
        "covers": ["visibility", "lock", "opacity", "blend_mode", "active_layer"],
        "source": "no_gui_export_no_runtime_stack",
        "global_document_undo": "manual_document_snapshot_undo",
    }


def session_journal_packet() -> dict[str, object]:
    return {
        "schema": "rrkal_displaytools.session_journal.v1",
        "mode": "no_gui_export_no_runtime_history",
        "history_limit": 0,
        "layer_runtime_history": [],
        "pin_pick_history": [],
        "layer_undo_depth": 0,
        "latest_ack_presence": {
            "layer_runtime_ack": False,
            "pin_input_ack": False,
            "pin_pick_ack": False,
            "boundary_highlight_ack": False,
        },
        "boundary": "Recent UI/runtime bridge journal only; not a persisted lab notebook or global document history.",
    }


def document_undo_packet() -> dict[str, object]:
    return {
        "schema": "rrkal_displaytools.document_snapshot_undo.v1",
        "mode": "no_gui_export_status_only",
        "undo_depth": 0,
        "redo_depth": 0,
        "capacity": 0,
        "implemented": [
            "manual_snapshot_capture",
            "limited_automatic_change_capture",
            "profile_state_undo",
            "profile_state_redo",
            "history_panel_controls",
            "launch_packet_status_contract",
            "provenance_status_contract",
        ],
        "auto_capture_points": [
            "profile_apply",
            "renderer_preset_apply",
            "timeline_keyframe_apply",
            "timeline_keyframe_clear",
            "layer_stack_reset",
        ],
        "pending": [
            "operation_level_history",
            "persisted_lab_notebook",
        ],
        "auto_snapshot_count": 0,
        "boundary": "No-GUI export reports the UI contract only; runtime snapshots are created in the Qt panel.",
    }


def timeline_state_packet(profile: dict[str, object]) -> dict[str, object]:
    profile_keyframes = profile.get("timeline_keyframes")
    keyframes = []
    if isinstance(profile_keyframes, list):
        for keyframe in profile_keyframes[:12]:
            if not isinstance(keyframe, dict):
                continue
            keyframes.append(
                {
                    "id": str(keyframe.get("id", "")),
                    "label": str(keyframe.get("label", "")),
                    "style_profile": str(keyframe.get("style_profile", "")),
                    "selected_layer": keyframe.get("selected_layer"),
                }
            )
    return {
        "schema": "rrkal_displaytools.timeline_state.v1",
        "status": "profile_keyframes_exported" if keyframes else "no_gui_export_no_runtime_keyframes",
        "implemented": ["launch_packet_status_contract", "profile_timeline_keyframe_handoff"],
        "pending": [
            "visible_qt_timeline_dock",
            "keyframe_storage",
            "keyframe_restore",
            "playback_controls",
            "renderer_timeline_playback",
            "animation_export",
            "ocean_material_keyframes",
            "camera_keyframes",
        ],
        "playhead": 0,
        "keyframe_count": len(keyframes),
        "keyframes": keyframes,
        "profile_keyframes_present": bool(keyframes),
        "playback": {
            "mode": "no_gui_export_no_runtime_playback",
            "active": False,
            "interval_ms": 0,
            "next_index": 0,
        },
        "boundary": "UIUX placeholder/status contract only; no renderer animation playback is claimed yet.",
    }


def timeline_runtime_state_packet(profile: dict[str, object], target_file: str = TIMELINE_STATE_PATH) -> dict[str, object]:
    profile_keyframes = profile.get("timeline_keyframes")
    keyframes = [dict(keyframe) for keyframe in profile_keyframes if isinstance(keyframe, dict)] if isinstance(profile_keyframes, list) else []
    return {
        "schema": "rrkal_displaytools.timeline_runtime_state.v1",
        "updated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "timeline_state": timeline_state_packet(profile),
        "timeline_keyframes": keyframes,
        "source": "scripts/export_launch_packet.py",
        "target_file": target_file,
        "boundary": "Save this payload to the target file before launching the renderer; renderer playback/export remain pending.",
    }


def launch_packet(
    profile_path: Path,
    profile: dict[str, object],
    rrkal_data_manifest_ref: str = "",
    timeline_state_file: str = TIMELINE_STATE_PATH,
    timeline_ack_file: str = TIMELINE_ACK_PATH,
) -> dict[str, object]:
    portable_command = [
        "py",
        "-3",
        "taichi_global_bathymetry.py",
        *renderer_args(profile, rrkal_data_manifest_ref, timeline_state_file, timeline_ack_file),
    ]
    manifest_ref = rrkal_data_manifest_ref or str(profile.get("renderer", {}).get("rrkal_data_manifest_ref", "")).strip()
    return {
        "schema": "rrkal_displaytools.launch_packet.v1",
        "created_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source_profile": profile_display_path(profile_path),
        "repo_role": "RRKAL displaytools renderer launch state",
        "rrkal_boundary": {
            "rrkal_owns": [
                "dataset discovery",
                "download/import/install registry",
                "manifest/cache governance",
            ],
            "displaytools_owns": [
                "renderer launch flags",
                "layer/style/material operator state",
                "visualization frontend",
            ],
        },
        "profile": profile,
        "rrkal_data_manifest_ref": manifest_ref,
        "rrkal_data_manifest_ref_boundary": "Reference-only handoff field; displaytools does not discover, download, validate, import, or govern this manifest.",
        "layer_filter": layer_filter_packet(profile),
        "canvas_preview": canvas_preview_packet(profile),
        "boundary_highlight": boundary_highlight_packet(profile),
        "active_layer_diagnostics": active_layer_diagnostics_packet(profile),
        "layer_undo": layer_undo_packet(),
        "session_journal": session_journal_packet(),
        "document_undo": document_undo_packet(),
        "timeline_state": timeline_state_packet(profile),
        "timeline_runtime_state": timeline_runtime_state_packet(profile, timeline_state_file),
        "timeline_runtime_state_file": timeline_state_file,
        "timeline_ack_file": timeline_ack_file,
        "closed_loop_status": renderer_closed_loop_status_packet(),
        "portable_command": portable_command,
        "portable_command_line": " ".join(portable_command),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export an RRKAL_displaytools launch packet")
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--template")
    parser.add_argument("--rrkal-data-manifest-ref", default="")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeline-state-out", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        profile_path = resolve_profile(args.profile, args.template)
        profile = load_profile_payload(profile_path)
    except Exception as exc:
        print(f"Profile load failed: {exc}", file=sys.stderr)
        return 1
    errors = profile_payload_errors(profile)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    timeline_state_file = str(args.timeline_state_out) if args.timeline_state_out else TIMELINE_STATE_PATH
    packet = launch_packet(
        profile_path,
        profile,
        str(args.rrkal_data_manifest_ref or "").strip(),
        timeline_state_file,
    )
    if args.timeline_state_out:
        args.timeline_state_out.parent.mkdir(parents=True, exist_ok=True)
        args.timeline_state_out.write_text(
            json.dumps(packet["timeline_runtime_state"], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    text = json.dumps(packet, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
