from __future__ import annotations

import argparse
import datetime
import json
import math
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = ROOT / "profiles"
PREVIEW_FRAME_PATH = "state/renderer_preview_frame.png"
PREVIEW_FRAME_INTERVAL_S = 0.75
CURSOR_GEODESY_STATE_PATH = "state/renderer_cursor_geodesy_state.json"
CURSOR_GEODESY_ACK_PATH = "state/renderer_cursor_geodesy_ack.json"
TIMELINE_STATE_PATH = "state/renderer_timeline_state.json"
TIMELINE_ACK_PATH = "state/renderer_timeline_ack.json"
TIMELINE_EXPORT_DIR = "state/timeline_exports"
TIMELINE_EXPORT_MANIFEST = "timeline_animation_manifest.json"
TIMELINE_EXPORT_GIF = "timeline_animation.gif"
TIMELINE_EXPORT_MP4 = "timeline_animation.mp4"
sys.path.insert(0, str(ROOT))

from closed_loop_status import renderer_closed_loop_status_packet  # noqa: E402
from pin_projection import pin_projection_contract_packet  # noqa: E402
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
LAYER_LABELS = (
    ("show_grid", "經緯網格"),
    ("show_stars", "星空背景"),
    ("lake_layer", "湖泊圖層"),
    ("river_layer", "河流圖層"),
    ("border_layer", "國界圖層"),
    ("territorial_sea_layer", "領海圖層"),
    ("eez_layer", "EEZ 圖層"),
    ("high_seas_layer", "公海圖層"),
    ("aircraft_layer", "航機圖層"),
    ("pin_layer", "科研 Pin 標記"),
    ("ocean_material", "海洋材質"),
    ("terrain_contours", "地形等高線"),
    ("scale_bar", "比例尺"),
    ("vehicle_icons", "交通工具圖示"),
)
LAYER_VISIBILITY_LIVE_KEYS = {
    "show_grid",
    "show_stars",
    "lake_layer",
    "river_layer",
    "border_layer",
    "territorial_sea_layer",
    "eez_layer",
    "high_seas_layer",
    "aircraft_layer",
    "pin_layer",
    "vehicle_icons",
    "ocean_material",
    "terrain_contours",
    "scale_bar",
}
LAYER_OPACITY_LIVE_KEYS = {
    "lake_layer",
    "river_layer",
    "border_layer",
    "territorial_sea_layer",
    "eez_layer",
    "high_seas_layer",
    "aircraft_layer",
    "pin_layer",
    "vehicle_icons",
    "terrain_contours",
    "scale_bar",
}
LAYER_BLEND_LIVE_KEYS = {
    "lake_layer",
    "river_layer",
    "border_layer",
    "territorial_sea_layer",
    "eez_layer",
    "high_seas_layer",
    "aircraft_layer",
    "pin_layer",
    "vehicle_icons",
}
LAYER_PICK_LIVE_KEYS = {
    "lake_layer",
    "river_layer",
    "border_layer",
    "territorial_sea_layer",
    "eez_layer",
    "high_seas_layer",
    "aircraft_layer",
    "pin_layer",
    "vehicle_icons",
}
LAYER_RUNTIME_BADGE_STYLES = {
    "no_ack": ("No ack", "#5c6470", "#f4f6f8"),
    "ok": ("No recent change", "#2f6f4e", "#e7f5ed"),
    "target": ("Selected renderer target", "#1f5f99", "#e7f1fb"),
    "changed": ("Renderer changed this layer", "#9a641f", "#fff4df"),
    "locked": ("Skipped because locked", "#7b4a9e", "#f4eafb"),
    "error": ("Renderer ack error", "#a53636", "#fdeaea"),
}


def layer_runtime_status_legend_packet() -> dict[str, object]:
    return {
        "schema": "rrkal_displaytools.layer_runtime_status_legend.v1",
        "statuses": [
            {"id": status_id, "label": label, "foreground": foreground, "background": background}
            for status_id, (label, foreground, background) in LAYER_RUNTIME_BADGE_STYLES.items()
        ],
        "boundary": "Qt badge colors summarize renderer ack evidence; they do not change renderer state.",
    }

DEFAULT_CANVAS_PREVIEW = {
    "schema": "rrkal_displaytools.canvas_preview.v1",
    "mode": "state",
    "renderer_thumbnail_path": None,
    "preview_frame_path": PREVIEW_FRAME_PATH,
    "preview_frame_interval_s": PREVIEW_FRAME_INTERVAL_S,
    "boundary_identity_warning": "Pending authoritative identity: authoritative_polygon_territory_identity, open_line_area_inference; open_line=pending_backend_geometry_closure; use RRKAL-governed polygon/EEZ source before authoritative boundary claims.",
    "boundary_identity_warning_surface": "No-GUI launch packet / Qt Canvas Preview / research provenance",
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
    "identity_source_hint": {
        "schema": "rrkal_displaytools.boundary_identity_source_hint.v1",
        "current_sources": [
            "source_properties",
            "maritime_property_keys",
            "closed_ring_geometry",
        ],
        "authoritative_source_required": "RRKAL-governed polygon/EEZ dataset manifest",
        "open_line_area_inference_status": "pending_backend_geometry_closure",
        "displaytools_scope": "consume identity fields and expose visual emphasis/provenance only",
    },
    "ui_summary_fields": ["applied", "pending", "boundary", "identity_source_hint", "identity_source_hint_summary"],
    "identity_source_hint_summary": "preview_sources=source_properties,maritime_property_keys,closed_ring_geometry; authoritative_source=RRKAL-governed polygon/EEZ dataset manifest; open_line_area_inference=pending_backend_geometry_closure",
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
    timeline_export_options: dict[str, object] | None = None,
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
        "--cursor-geodesy-state-file",
        CURSOR_GEODESY_STATE_PATH,
        "--cursor-geodesy-ack-file",
        CURSOR_GEODESY_ACK_PATH,
    ]
    for key, flag in BOOL_FLAGS.items():
        args.append(f"--{flag}" if layers[key] else f"--no-{flag}")
    manifest_ref = rrkal_data_manifest_ref or str(renderer.get("rrkal_data_manifest_ref", "")).strip()
    if manifest_ref:
        args.extend(["--rrkal-data-manifest-ref", manifest_ref])
    export_options = timeline_export_options if isinstance(timeline_export_options, dict) else {}
    if export_options.get("enabled") is True:
        args.extend(
            [
                "--timeline-export-dir",
                str(export_options["export_dir"]),
                "--timeline-export-frames",
                str(export_options["frame_count"]),
                "--timeline-export-fps",
                str(export_options["fps"]),
                "--timeline-export-manifest",
                str(export_options["manifest_file"]),
            ]
        )
        if export_options.get("gif_enabled") is True:
            args.extend(["--timeline-export-gif", str(export_options["gif_file"])])
        if export_options.get("mp4_enabled") is True:
            args.extend(["--timeline-export-mp4", str(export_options["mp4_file"])])
    return args


def timeline_export_options_packet(
    export_dir: str | None = None,
    frame_count: int = 24,
    fps: float = 24.0,
    gif_file: str | None = None,
    mp4_file: str | None = None,
) -> dict[str, object]:
    enabled = bool(export_dir)
    export_dir_value = export_dir or TIMELINE_EXPORT_DIR
    manifest_file = str(Path(export_dir_value) / TIMELINE_EXPORT_MANIFEST)
    return {
        "schema": "rrkal_displaytools.timeline_export_options.v1",
        "enabled": enabled,
        "export_dir": export_dir_value,
        "frame_count": max(1, int(frame_count)),
        "fps": max(1.0, float(fps)),
        "manifest_file": manifest_file,
        "gif_enabled": bool(gif_file),
        "gif_file": gif_file or str(Path(export_dir_value) / TIMELINE_EXPORT_GIF),
        "mp4_enabled": bool(mp4_file),
        "mp4_file": mp4_file or str(Path(export_dir_value) / TIMELINE_EXPORT_MP4),
        "applies": ["no_gui_timeline_export_options", "renderer_timeline_export_cli"],
        "boundary": "No-GUI launch packets prepare renderer Timeline export flags only; renderer writes PNG/GIF/MP4 artifacts, and RRKAL remains responsible for data governance.",
    }


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


def cursor_geodesy_readout_packet(canvas_preview: dict[str, object] | None, source: str) -> dict[str, object]:
    canvas_preview = canvas_preview if isinstance(canvas_preview, dict) else {}
    latitude = canvas_preview.get("cursor_latitude")
    longitude = canvas_preview.get("cursor_longitude")
    has_position = isinstance(latitude, (int, float)) and isinstance(longitude, (int, float))
    return {
        "schema": "rrkal_displaytools.cursor_geodesy_readout.v1",
        "source": source,
        "status": "ready",
        "last_known_position_available": has_position,
        "latitude": float(latitude) if isinstance(latitude, (int, float)) else None,
        "longitude": float(longitude) if isinstance(longitude, (int, float)) else None,
        "units": "degrees",
        "coordinate_order": "latitude_longitude",
        "input_surface": "Qt canvas preview mouse move",
        "projection_method": "viewport_equirectangular_preview_estimate",
        "event_position_guard": "QMouseEvent.position with QMouseEvent.pos fallback",
        "qt_surface": "Canvas meta label and launch packet",
        "backend_raycast_status": "renderer_globe_intersection_contract_ready",
        "renderer_raycast_schema": "rrkal_displaytools.cursor_geodesy_raycast.v1",
        "renderer_raycast_helper": "cursor_geodesy.viewport_sphere_raycast",
        "renderer_raycast_method": "orthographic_globe_disc_intersection",
        "renderer_raycast_inputs": ["screen_x", "screen_y", "viewport_width", "viewport_height", "camera_yaw_deg", "camera_pitch_deg"],
        "renderer_raycast_outputs": ["hit", "latitude", "longitude", "front_hemisphere"],
        "raycast_smoke_cases": ["center_hit", "outside_globe_miss"],
        "runtime_bridge_status": "renderer_mouse_state_wired",
        "renderer_raycast_state_file": "state/renderer_cursor_geodesy_state.json",
        "renderer_raycast_ack_file": "state/renderer_cursor_geodesy_ack.json",
        "renderer_controls": ["cursor-geodesy-state-file", "cursor-geodesy-ack-file"],
        "runtime_events": ["qt_mouse_press", "qt_mouse_move", "vispy_mouse_press", "vispy_mouse_move"],
        "runtime_bridge_fields": ["screen_x", "screen_y", "latitude", "longitude", "hit", "camera_yaw_deg", "camera_pitch_deg", "frame_index", "updated_at_utc"],
        "researcher_note": "Canvas preview gives immediate lon/lat feedback; renderer mouse events now write a smoke-gated state/ack bridge for Taichi globe raycast results.",
    }


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
    merged["ack_history_contract"] = "boundary_highlight_ack_history"
    merged["ack_history_source"] = "state/renderer_boundary_highlight_ack.json"
    merged["ack_history_fields"] = [
        "enabled",
        "trigger",
        "target_layers",
        "renderer_target_layers",
        "applies",
        "pending",
        "updated_at_utc",
    ]
    merged["ack_history_qt_surface"] = "History panel boundary ack history"
    merged["ack_history_provenance_field"] = "boundary_highlight_ack_history"
    return merged


def active_layer_diagnostics_packet(profile: dict[str, object], rrkal_data_manifest_ref: str | None = None) -> dict[str, object]:
    selected_layer = profile.get("selected_layer")
    selected_layer = selected_layer if isinstance(selected_layer, str) else None
    renderer_target = LAYER_RUNTIME_ID_ALIASES.get(selected_layer) if selected_layer else None
    selected_label = next((label for key, label in LAYER_LABELS if key == selected_layer), selected_layer)
    return {
        "schema": "rrkal_displaytools.active_layer_diagnostics.v1",
        "selected_layer": selected_layer,
        "renderer_target": renderer_target,
        "layer_pick_screen_position": None,
        "layer_pick_screen_position_field": "screen_position",
        "layer_pick_screen_position_source": "state/renderer_layer_pick_state.json",
        "layer_pick_screen_position_status": "runtime_file_dependent",
        "capabilities": layer_capability_packet(selected_layer, selected_label) if selected_layer else None,
        "layer_capability_matrix_schema": "rrkal_displaytools.layer_capability_matrix.v1",
        "layer_runtime_evidence_schema": "rrkal_displaytools.layer_runtime_evidence.v1",
        "layer_runtime_evidence_summary_schema": "rrkal_displaytools.layer_runtime_evidence_summary.v1",
        "layer_runtime_badge_summary_schema": "rrkal_displaytools.layer_runtime_badge_summary.v1",
        "layer_runtime_warning_list_schema": "rrkal_displaytools.layer_runtime_warning_list.v1",
        "layer_runtime_interaction_context_schema": "rrkal_displaytools.layer_runtime_interaction_context.v1",
        "layer_territory_identity_context_schema": "rrkal_displaytools.layer_territory_identity_context.v1",
        "layer_authoritative_identity_source_schema": "rrkal_displaytools.layer_authoritative_identity_source.v1",
        "layer_renderer_diagnostics_summary_schema": "rrkal_displaytools.layer_renderer_diagnostics_summary.v1",
        "layer_renderer_diagnostics_detail_schema": "rrkal_displaytools.layer_renderer_diagnostics_detail.v1",
        "layer_renderer_diagnostics_remediation_schema": "rrkal_displaytools.layer_renderer_diagnostics_remediation.v1",
        "runtime_evidence_summary": layer_runtime_evidence_summary_packet(None),
        "runtime_badge_summary": layer_capability_matrix_packet("scripts.export_launch_packet", selected_layer, rrkal_data_manifest_ref).get("runtime_badge_summary"),
        "runtime_warning_list": layer_capability_matrix_packet("scripts.export_launch_packet", selected_layer, rrkal_data_manifest_ref).get("runtime_warning_list"),
        "runtime_interaction_context": layer_capability_matrix_packet("scripts.export_launch_packet", selected_layer, rrkal_data_manifest_ref).get("runtime_interaction_context"),
        "territory_identity_context": layer_capability_matrix_packet("scripts.export_launch_packet", selected_layer, rrkal_data_manifest_ref).get("territory_identity_context"),
        "authoritative_identity_source": layer_capability_matrix_packet("scripts.export_launch_packet", selected_layer, rrkal_data_manifest_ref).get("authoritative_identity_source"),
        "renderer_diagnostics_summary": layer_capability_matrix_packet("scripts.export_launch_packet", selected_layer, rrkal_data_manifest_ref).get("renderer_diagnostics_summary"),
        "renderer_diagnostics_detail": layer_capability_matrix_packet("scripts.export_launch_packet", selected_layer, rrkal_data_manifest_ref).get("renderer_diagnostics_detail"),
        "renderer_diagnostics_remediation": layer_capability_matrix_packet("scripts.export_launch_packet", selected_layer, rrkal_data_manifest_ref).get("renderer_diagnostics_remediation"),
        "diagnostics_text": "no runtime ack/pick in no-GUI export",
        "runtime_ack_file": "state/renderer_layer_runtime_ack.json",
        "runtime_ack": None,
        "pick_state_file": "state/renderer_layer_pick_state.json",
        "pick_state": None,
    }


def layer_capability_packet(key: str, label: str | None = None) -> dict[str, object]:
    live = []
    if key in LAYER_VISIBILITY_LIVE_KEYS:
        live.append("visibility")
    if key in LAYER_OPACITY_LIVE_KEYS:
        live.append("opacity")
    if key in LAYER_BLEND_LIVE_KEYS:
        live.append("blend")
    if key in LAYER_PICK_LIVE_KEYS:
        live.append("selected_layer_pick")
    return {
        "key": key,
        "label": label or key,
        "renderer_target": LAYER_RUNTIME_ID_ALIASES.get(key),
        "visibility_live": key in LAYER_VISIBILITY_LIVE_KEYS,
        "opacity_live": key in LAYER_OPACITY_LIVE_KEYS,
        "blend_live": key in LAYER_BLEND_LIVE_KEYS,
        "pick_live": key in LAYER_PICK_LIVE_KEYS,
        "live_controls": live,
        "renderer_sync": f"live: {', '.join(live)}" if live else "planned",
}


def layer_runtime_evidence_summary_packet(evidence: dict[str, object] | None) -> dict[str, object]:
    evidence = evidence if isinstance(evidence, dict) else {}
    counts = evidence.get("counts")
    counts = counts if isinstance(counts, dict) else {}
    changed_visibility = int(counts.get("changed_visibility", 0) or 0)
    changed_opacity = int(counts.get("changed_opacity", 0) or 0)
    changed_blend = int(counts.get("changed_blend", 0) or 0)
    skipped_locked = int(counts.get("skipped_locked", 0) or 0)
    available = bool(evidence.get("available"))
    error = evidence.get("error")
    if not available:
        status = "unavailable"
        text = "No renderer ack evidence yet."
    elif error:
        status = "error"
        text = f"Renderer ack error: {error}"
    elif skipped_locked:
        status = "skipped_locked"
        text = f"Renderer skipped {skipped_locked} locked layer changes."
    elif changed_visibility or changed_opacity or changed_blend:
        status = "changed"
        text = f"Renderer applied visibility={changed_visibility}, opacity={changed_opacity}, blend={changed_blend} changes."
    else:
        status = "ok"
        text = "Renderer ack observed; no layer mutations in the latest apply."
    return {
        "schema": "rrkal_displaytools.layer_runtime_evidence_summary.v1",
        "available": available,
        "status": status,
        "text": text,
        "counts": {
            "changed_visibility": changed_visibility,
            "changed_opacity": changed_opacity,
            "changed_blend": changed_blend,
            "skipped_locked": skipped_locked,
        },
        "event": evidence.get("event"),
        "error": error,
        "selected_renderer_layer": evidence.get("selected_renderer_layer"),
        "frame_index": evidence.get("frame_index"),
        "updated_at_utc": evidence.get("updated_at_utc"),
        "boundary": "Human-readable summary of renderer layer runtime ack evidence; does not change renderer state.",
    }


def layer_runtime_badge_summary_packet(
    layers: list[dict[str, object]],
    selected_layer: str | None,
    source: str,
) -> dict[str, object]:
    status_counts = {status_id: 0 for status_id in LAYER_RUNTIME_BADGE_STYLES}
    noted_layers: list[dict[str, object]] = []
    selected_status: list[str] = []
    for layer in layers:
        statuses = layer.get("runtime_status")
        statuses = statuses if isinstance(statuses, list) else []
        layer_statuses = [str(status) for status in statuses if str(status)]
        for status_id in layer_statuses:
            status_counts[status_id] = status_counts.get(status_id, 0) + 1
        if layer.get("key") == selected_layer:
            selected_status = layer_statuses
        if any(status in {"changed", "locked", "error", "target"} for status in layer_statuses):
            noted_layers.append(
                {
                    "key": layer.get("key"),
                    "label": layer.get("label"),
                    "runtime_status": layer_statuses,
                    "renderer_target": layer.get("renderer_target"),
                }
            )
    return {
        "schema": "rrkal_displaytools.layer_runtime_badge_summary.v1",
        "source": source,
        "status_counts": status_counts,
        "selected_layer": selected_layer,
        "selected_layer_status": selected_status,
        "noted_layers": noted_layers,
        "noted_layer_count": len(noted_layers),
        "copyable_provenance": True,
        "boundary": "Copyable research provenance summary of layer Runtime badges; No-GUI export marks badges as no_ack until renderer evidence exists.",
    }


def layer_runtime_warning_list_packet(
    badge_summary: dict[str, object] | None,
    evidence_summary: dict[str, object] | None,
    source: str,
) -> dict[str, object]:
    badge_summary = badge_summary if isinstance(badge_summary, dict) else {}
    evidence_summary = evidence_summary if isinstance(evidence_summary, dict) else {}
    counts = badge_summary.get("status_counts")
    counts = counts if isinstance(counts, dict) else {}
    warnings: list[dict[str, object]] = []
    error_count = int(counts.get("error", 0) or 0)
    locked_count = int(counts.get("locked", 0) or 0)
    changed_count = int(counts.get("changed", 0) or 0)
    target_count = int(counts.get("target", 0) or 0)
    no_ack_count = int(counts.get("no_ack", 0) or 0)
    if error_count:
        warnings.append({"level": "error", "type": "renderer_ack_error", "text": f"{error_count} layer(s) report renderer ack error badges."})
    if locked_count:
        warnings.append({"level": "warning", "type": "locked_layer_skipped", "text": f"{locked_count} locked layer(s) were skipped by renderer runtime sync."})
    if evidence_summary.get("status") == "unavailable" or no_ack_count:
        warnings.append({"level": "info", "type": "runtime_ack_pending", "text": f"{no_ack_count} layer(s) have no renderer ack badge evidence yet."})
    if changed_count:
        warnings.append({"level": "info", "type": "runtime_change_applied", "text": f"{changed_count} layer(s) changed in the latest renderer runtime ack."})
    if target_count:
        warnings.append({"level": "info", "type": "selected_renderer_target", "text": f"{target_count} layer(s) are marked as selected renderer target."})
    severity = "ok"
    if error_count:
        severity = "error"
    elif locked_count:
        severity = "warning"
    elif warnings:
        severity = "info"
    summary_text = "No runtime badge warnings." if not warnings else " ".join(str(item["text"]) for item in warnings[:3])
    if len(warnings) > 3:
        summary_text += f" +{len(warnings) - 3} more."
    return {
        "schema": "rrkal_displaytools.layer_runtime_warning_list.v1",
        "source": source,
        "severity": severity,
        "summary_text": summary_text,
        "warning_count": len(warnings),
        "warnings": warnings,
        "copyable_provenance": True,
        "boundary": "Researcher-facing warning list derived from layer Runtime badge summaries; it is diagnostic only.",
    }


def layer_runtime_interaction_context_packet(
    warning_list: dict[str, object] | None,
    selected_layer: str | None,
    renderer_target: str | None,
    source: str,
) -> dict[str, object]:
    warning_list = warning_list if isinstance(warning_list, dict) else {}
    return {
        "schema": "rrkal_displaytools.layer_runtime_interaction_context.v1",
        "source": source,
        "selected_layer": selected_layer,
        "renderer_target": renderer_target,
        "warning_severity": warning_list.get("severity"),
        "warning_count": warning_list.get("warning_count"),
        "pick_context_available": False,
        "pick_event": "unavailable",
        "pick_renderer_layer": None,
        "pick_target_matches_selected_layer": False,
        "pick_hit": None,
        "feature_label": None,
        "feature_identity": {},
        "summary_text": "No-GUI launch packet has no renderer pick context yet.",
        "copyable_provenance": True,
        "boundary": "No-GUI handoff exposes the interaction-context schema; live feature identity arrives from renderer layer pick state.",
    }


def layer_territory_identity_context_packet(
    interaction_context: dict[str, object] | None,
    selected_layer: str | None,
    source: str,
) -> dict[str, object]:
    interaction_context = interaction_context if isinstance(interaction_context, dict) else {}
    feature_identity = interaction_context.get("feature_identity")
    feature_identity = feature_identity if isinstance(feature_identity, dict) else {}
    feature_label = interaction_context.get("feature_label")
    renderer_target = interaction_context.get("renderer_target")
    jurisdiction_kinds = {
        "border_layer": "land_or_administrative_boundary",
        "territorial_sea_layer": "territorial_sea",
        "eez_layer": "exclusive_economic_zone",
        "high_seas_layer": "high_seas",
    }
    jurisdiction_kind = jurisdiction_kinds.get(str(selected_layer), "not_territory_layer")
    source_identity_available = bool(feature_identity or (isinstance(feature_label, str) and feature_label.strip()))
    if jurisdiction_kind == "not_territory_layer":
        summary_text = "Selected layer is not a territory/EEZ identity layer."
    elif source_identity_available:
        summary_text = f"Source-property identity available for {jurisdiction_kind}; authoritative polygon identity pending."
    else:
        summary_text = f"No source-property identity yet for {jurisdiction_kind}; authoritative polygon identity pending."
    return {
        "schema": "rrkal_displaytools.layer_territory_identity_context.v1",
        "source": source,
        "selected_layer": selected_layer,
        "renderer_target": renderer_target,
        "jurisdiction_kind": jurisdiction_kind,
        "source_property_identity_available": source_identity_available,
        "source_property_feature_label": feature_label,
        "source_property_feature_identity": feature_identity,
        "authoritative_identity_available": False,
        "authoritative_identity_status": "pending_authoritative_polygon_identity",
        "open_line_area_inference": "pending",
        "summary_text": summary_text,
        "copyable_provenance": True,
        "boundary": "Source-property feature identity is runtime evidence; authoritative territory/EEZ polygon identity remains pending until a governed spatial identity source is connected.",
    }


def layer_authoritative_identity_source_packet(source_ref: str | None, source: str) -> dict[str, object]:
    ref = str(source_ref or "").strip()
    return {
        "schema": "rrkal_displaytools.layer_authoritative_identity_source.v1",
        "source": source,
        "source_ref": ref or None,
        "source_ref_configured": bool(ref),
        "owner": "RRKAL/APIkeys_collection",
        "displaytools_role": "reference_only_handoff",
        "supported_layers": ["border_layer", "territorial_sea_layer", "eez_layer", "high_seas_layer"],
        "expected_identity_types": [
            "authoritative_polygon_territory_identity",
            "exclusive_economic_zone_identity",
            "territorial_sea_identity",
            "high_seas_identity",
        ],
        "displaytools_non_goals": ["discovery", "download", "import", "cache_governance", "asset_repair"],
        "boundary": "Displaytools only carries this RRKAL-governed identity source reference; it does not discover, download, import, validate, repair, or govern identity datasets.",
    }



def layer_renderer_diagnostics_summary_packet(
    runtime_evidence: dict[str, object] | None,
    warning_list: dict[str, object] | None,
    interaction_context: dict[str, object] | None,
    identity_source: dict[str, object] | None,
    live_counts: dict[str, object] | None,
    selected_layer: str | None,
    source: str,
) -> dict[str, object]:
    runtime_evidence = runtime_evidence if isinstance(runtime_evidence, dict) else {}
    warning_list = warning_list if isinstance(warning_list, dict) else {}
    interaction_context = interaction_context if isinstance(interaction_context, dict) else {}
    identity_source = identity_source if isinstance(identity_source, dict) else {}
    live_counts = live_counts if isinstance(live_counts, dict) else {}
    ack_available = bool(runtime_evidence.get("available"))
    pick_available = bool(interaction_context.get("pick_context_available"))
    identity_ref_configured = bool(identity_source.get("source_ref_configured"))
    severity = str(warning_list.get("severity") or "unknown")
    summary_bits = [
        f"ack={'available' if ack_available else 'waiting'}",
        f"pick={'available' if pick_available else 'waiting'}",
        f"warnings={severity}",
        f"identity_source={'configured' if identity_ref_configured else 'not_configured'}",
    ]
    return {
        "schema": "rrkal_displaytools.layer_renderer_diagnostics_summary.v1",
        "source": source,
        "selected_layer": selected_layer,
        "runtime_ack_available": ack_available,
        "runtime_ack_event": runtime_evidence.get("event"),
        "runtime_ack_error": runtime_evidence.get("error"),
        "pick_context_available": pick_available,
        "pick_event": interaction_context.get("pick_event"),
        "pick_hit": interaction_context.get("pick_hit"),
        "warning_severity": severity,
        "warning_count": warning_list.get("warning_count"),
        "identity_source_configured": identity_ref_configured,
        "live_counts": live_counts,
        "summary_text": "; ".join(summary_bits),
        "copyable_provenance": True,
        "boundary": "Diagnostic summary only; renderer state and RRKAL data governance are not mutated.",
    }


def layer_renderer_diagnostics_detail_packet(
    renderer_summary: dict[str, object] | None,
    runtime_evidence: dict[str, object] | None,
    warning_list: dict[str, object] | None,
    interaction_context: dict[str, object] | None,
    identity_source: dict[str, object] | None,
    live_counts: dict[str, object] | None,
    selected_layer: str | None,
    source: str,
) -> dict[str, object]:
    renderer_summary = renderer_summary if isinstance(renderer_summary, dict) else {}
    runtime_evidence = runtime_evidence if isinstance(runtime_evidence, dict) else {}
    warning_list = warning_list if isinstance(warning_list, dict) else {}
    interaction_context = interaction_context if isinstance(interaction_context, dict) else {}
    identity_source = identity_source if isinstance(identity_source, dict) else {}
    live_counts = live_counts if isinstance(live_counts, dict) else {}
    live_total = sum(int(value) for value in live_counts.values() if isinstance(value, (int, float)))
    bridges = [
        {
            "name": "runtime_ack",
            "status": "available" if renderer_summary.get("runtime_ack_available") else "waiting",
            "schema": runtime_evidence.get("schema"),
            "event": runtime_evidence.get("event") or renderer_summary.get("runtime_ack_event"),
            "error": runtime_evidence.get("error") or renderer_summary.get("runtime_ack_error"),
            "frame_index": runtime_evidence.get("frame_index"),
            "evidence": "renderer ack observed" if renderer_summary.get("runtime_ack_available") else "waiting for renderer ack bridge evidence",
        },
        {
            "name": "layer_pick_state",
            "status": "available" if renderer_summary.get("pick_context_available") else "waiting",
            "schema": interaction_context.get("schema"),
            "pick_event": interaction_context.get("pick_event"),
            "pick_hit": interaction_context.get("pick_hit"),
            "renderer_target": interaction_context.get("renderer_target"),
            "feature_label": interaction_context.get("feature_label"),
            "evidence": "renderer pick context observed" if renderer_summary.get("pick_context_available") else "waiting for renderer pick bridge evidence",
        },
        {
            "name": "authoritative_identity_source",
            "status": "configured" if renderer_summary.get("identity_source_configured") else "not_configured",
            "schema": identity_source.get("schema"),
            "source_ref": identity_source.get("source_ref"),
            "displaytools_role": identity_source.get("displaytools_role"),
            "evidence": "RRKAL source ref configured" if renderer_summary.get("identity_source_configured") else "RRKAL source ref not configured",
        },
        {
            "name": "warning_list",
            "status": str(warning_list.get("severity") or renderer_summary.get("warning_severity") or "unknown"),
            "schema": warning_list.get("schema"),
            "warning_count": warning_list.get("warning_count") or renderer_summary.get("warning_count"),
            "evidence": warning_list.get("summary_text"),
        },
        {
            "name": "live_control_coverage",
            "status": "available" if live_total > 0 else "planned",
            "counts": live_counts,
            "live_total": live_total,
            "evidence": "renderer live controls exposed" if live_total > 0 else "no live renderer controls exposed",
        },
    ]
    return {
        "schema": "rrkal_displaytools.layer_renderer_diagnostics_detail.v1",
        "source": source,
        "selected_layer": selected_layer,
        "summary_schema": renderer_summary.get("schema"),
        "bridge_count": len(bridges),
        "bridges": bridges,
        "attention_required": any(bridge.get("status") in {"waiting", "warning", "error", "not_configured"} for bridge in bridges),
        "summary_text": ", ".join(f"{bridge.get('name')}={bridge.get('status')}" for bridge in bridges),
        "copyable_provenance": True,
        "boundary": "Read-only diagnostics detail; renderer state and RRKAL data governance are not mutated.",
    }


def layer_renderer_diagnostics_remediation_packet(
    renderer_detail: dict[str, object] | None,
    renderer_summary: dict[str, object] | None,
    selected_layer: str | None,
    source: str,
) -> dict[str, object]:
    renderer_detail = renderer_detail if isinstance(renderer_detail, dict) else {}
    renderer_summary = renderer_summary if isinstance(renderer_summary, dict) else {}
    bridge_items = renderer_detail.get("bridges")
    bridges = bridge_items if isinstance(bridge_items, list) else []
    hints: list[dict[str, object]] = []
    action_by_bridge = {
        "runtime_ack": "Launch or restart the renderer from Qt, then inspect state/renderer_layer_runtime_ack.json if the ack remains missing.",
        "layer_pick_state": "Move or click on a selectable renderer layer, then inspect state/renderer_layer_pick_state.json if pick context remains missing.",
        "authoritative_identity_source": "Set the RRKAL manifest reference when authoritative territory or EEZ identity is required; displaytools keeps this as reference-only handoff.",
        "warning_list": "Open Runtime warnings in Properties and compare the layer runtime badge summary before treating the layer state as reproducible.",
        "live_control_coverage": "Treat controls with no live renderer coverage as UI/profile state until renderer support is added.",
    }
    title_by_bridge = {
        "runtime_ack": "Renderer ack bridge",
        "layer_pick_state": "Layer pick bridge",
        "authoritative_identity_source": "RRKAL identity source",
        "warning_list": "Runtime warning list",
        "live_control_coverage": "Live-control coverage",
    }
    for bridge in bridges:
        if not isinstance(bridge, dict):
            continue
        name = str(bridge.get("name") or "unknown")
        status = str(bridge.get("status") or "unknown")
        if status not in {"waiting", "not_configured", "warning", "error", "planned", "unknown"}:
            continue
        severity = "error" if status == "error" else "warning" if status in {"warning", "waiting", "not_configured"} else "info"
        hints.append(
            {
                "bridge": name,
                "status": status,
                "severity": severity,
                "title": title_by_bridge.get(name, name),
                "action": action_by_bridge.get(name, "Inspect the corresponding diagnostics bridge before relying on this renderer state."),
                "evidence": bridge.get("evidence"),
            }
        )
    if not hints:
        hints.append(
            {
                "bridge": "renderer_diagnostics",
                "status": "ok",
                "severity": "info",
                "title": "Renderer diagnostics",
                "action": "No immediate remediation required; keep the diagnostics packet with exported provenance.",
                "evidence": renderer_summary.get("summary_text"),
            }
        )
    return {
        "schema": "rrkal_displaytools.layer_renderer_diagnostics_remediation.v1",
        "source": source,
        "selected_layer": selected_layer,
        "summary_schema": renderer_summary.get("schema"),
        "detail_schema": renderer_detail.get("schema"),
        "hint_count": len(hints),
        "hints": hints,
        "attention_required": any(hint.get("severity") in {"warning", "error"} for hint in hints),
        "summary_text": "; ".join(f"{hint.get('bridge')}:{hint.get('status')}" for hint in hints[:5]),
        "copyable_provenance": True,
        "boundary": "Read-only remediation hints; renderer state and RRKAL data governance are not mutated.",
    }


def style_renderer_entries_packet(
    source: str,
    selected_style: str | None = None,
) -> dict[str, object]:
    style_ids = ("scientific", "nautical", "parchment", "tactical")
    labels = {
        "scientific": "Scientific",
        "nautical": "Nautical",
        "parchment": "Parchment",
        "tactical": "Tactical",
    }
    selected = selected_style if selected_style in style_ids else None
    entries = []
    for style_id in style_ids:
        entries.append(
            {
                "id": style_id,
                "label": labels.get(style_id, style_id.title()),
                "cli_args": ["--style-profile", style_id],
                "profile_field": "style_profile",
                "qt_control": "Looks/templates style profile selector",
                "portable_command_supported": True,
                "template_supported": True,
                "renderer_entrypoint": f"taichi_global_bathymetry.py --style-profile {style_id}",
                "selected": style_id == selected,
            }
        )
    return {
        "schema": "rrkal_displaytools.style_renderer_entries.v1",
        "source": source,
        "selected_style": selected,
        "entry_count": len(entries),
        "entry_ids": [entry["id"] for entry in entries],
        "entries": entries,
        "parchment_entry_available": "parchment" in style_ids,
        "tactical_entry_available": "tactical" in style_ids,
        "launch_packet_fields": ["style_renderer_entries", "profile.style_profile", "portable_command"],
        "renderer_capability_field": "style_renderer_entries",
        "boundary": "Style entries are renderer launch/profile contracts; RRKAL data discovery and cache governance stay outside displaytools.",
    }


def style_profile_renderer_routes_packet(
    style_entries: dict[str, object] | None,
    source: str,
) -> dict[str, object]:
    style_entries = style_entries if isinstance(style_entries, dict) else style_renderer_entries_packet(source)
    raw_entries = style_entries.get("entries") if isinstance(style_entries.get("entries"), list) else []
    routes = []
    for entry in raw_entries:
        if not isinstance(entry, dict):
            continue
        style_id = str(entry.get("id", ""))
        if style_id not in {"scientific", "nautical", "parchment", "tactical"}:
            continue
        routes.append(
            {
                "id": style_id,
                "renderer_entrypoint": entry.get("renderer_entrypoint", f"taichi_global_bathymetry.py --style-profile {style_id}"),
                "portable_command": ["py", "-3", "taichi_global_bathymetry.py", "--style-profile", style_id],
                "cli_args": entry.get("cli_args", ["--style-profile", style_id]),
                "profile_field": "renderer.style_profile",
                "template_supported": bool(entry.get("template_supported", True)),
            }
        )
    route_ids = [str(route["id"]) for route in routes]
    required_routes = ["parchment", "tactical"]
    missing_routes = [route_id for route_id in required_routes if route_id not in route_ids]
    return {
        "schema": "rrkal_displaytools.style_profile_renderer_routes.v1",
        "source": source,
        "route_count": len(routes),
        "route_ids": route_ids,
        "routes": routes,
        "required_routes": required_routes,
        "missing_routes": missing_routes,
        "status": "ready" if not missing_routes else "partial",
        "qt_surface": "Looks/templates style profile selector",
        "launch_packet_fields": ["style_profile_renderer_routes", "style_renderer_entries", "portable_command"],
        "renderer_capability_field": "style_profile_renderer_routes",
        "boundary": "Style profile routes are renderer launch affordances only; data discovery/cache governance stays RRKAL-owned.",
    }


def profile_launch_readiness_packet(
    source: str,
    style_entries: dict[str, object] | None = None,
    layer_operator_groups: dict[str, object] | None = None,
) -> dict[str, object]:
    style_entries = style_entries if isinstance(style_entries, dict) else {}
    layer_operator_groups = layer_operator_groups if isinstance(layer_operator_groups, dict) else {}
    checks = [
        {
            "id": "profile_schema",
            "ready": True,
            "evidence": ["profile_schema.py", "docs/PROFILE_SCHEMA.zh-TW.md", "scripts/validate_profiles.py"],
        },
        {
            "id": "built_in_templates",
            "ready": True,
            "evidence": ["profiles/*.json", "rrkal_displaytools_qt_panel.py --list-templates"],
        },
        {
            "id": "launch_packet_export",
            "ready": True,
            "evidence": ["scripts/export_launch_packet.py", "Qt Export launch packet action"],
        },
        {
            "id": "portable_command",
            "ready": True,
            "evidence": ["launch_packet.portable_command", "Qt Copy portable command action"],
        },
        {
            "id": "renderer_capability_discovery",
            "ready": True,
            "evidence": ["taichi_global_bathymetry.py --print-renderer-capabilities"],
        },
        {
            "id": "style_renderer_entries",
            "ready": (
                style_entries.get("schema") == "rrkal_displaytools.style_renderer_entries.v1"
                and bool(style_entries.get("parchment_entry_available"))
                and bool(style_entries.get("tactical_entry_available"))
            ),
            "evidence": ["style_renderer_entries", "parchment", "tactical"],
        },
        {
            "id": "layer_operator_groups",
            "ready": (
                layer_operator_groups.get("schema") == "rrkal_displaytools.layer_operator_groups.v1"
                and int(layer_operator_groups.get("complete_group_count") or 0) >= 5
            ),
            "evidence": ["layer_operator_groups", "Selection/Edit/Isolation/History/Diagnostics"],
        },
    ]
    ready_check_count = sum(1 for check in checks if check["ready"])
    return {
        "schema": "rrkal_displaytools.profile_launch_readiness.v1",
        "source": source,
        "readiness": "ready" if ready_check_count == len(checks) else "partial",
        "check_count": len(checks),
        "ready_check_count": ready_check_count,
        "checks": checks,
        "cross_machine_commands": [
            "scripts/setup_windows.ps1",
            "scripts/smoke.ps1",
            "scripts/run_qt_panel.ps1",
            "scripts/inspect_handoff.ps1",
        ],
        "launch_packet_fields": ["profile_launch_readiness", "portable_command", "style_renderer_entries", "layer_operator_groups"],
        "renderer_capability_field": "profile_launch_readiness",
        "boundary": "Readiness summarizes displaytools launch/profile/renderer contracts only; RRKAL data discovery, download, import, and cache governance are out of scope.",
    }


def profile_launch_readiness_ui_packet(
    readiness: dict[str, object] | None,
    source: str,
) -> dict[str, object]:
    readiness = readiness if isinstance(readiness, dict) else {}
    return {
        "schema": "rrkal_displaytools.profile_launch_readiness_ui.v1",
        "source": source,
        "readiness_schema": readiness.get("schema"),
        "readiness": readiness.get("readiness", "unknown"),
        "ready_check_count": int(readiness.get("ready_check_count") or 0),
        "check_count": int(readiness.get("check_count") or 0),
        "qt_surface": "Layers dock readiness label",
        "label_prefix": "Profile/launch readiness",
        "visible_fields": ["readiness", "ready_check_count", "check_count"],
        "cross_machine_commands_visible": True,
        "launch_packet_fields": ["profile_launch_readiness_ui", "profile_launch_readiness"],
        "boundary": "Qt UI surface only; it displays readiness evidence without mutating RRKAL data governance.",
    }


def profile_ui_state_replay_packet(source: str) -> dict[str, object]:
    saved_groups = [
        "renderer_config",
        "selected_layer",
        "layer_stack_ui",
        "pins",
        "boundary_highlight",
        "boundary_emphasis_control",
        "canvas_preview",
        "timeline_keyframes",
        "timeline_export_options",
    ]
    replay_surfaces = [
        "Qt save/load profile",
        "Qt startup --profile/--template",
        "Qt Inspect actions",
        "No-GUI launch packet",
        "renderer first-keyframe apply",
        "research provenance summary",
    ]
    qt_inspector_actions = [
        ("profile_replay", "Inspect: Profile replay"),
        ("timeline", "Inspect: Timeline"),
        ("ocean_port", "Inspect: Ocean port"),
        ("hydro_lod", "Inspect: Hydro LOD"),
        ("style_routes", "Inspect: Style routes"),
        ("module_seams", "Inspect: Module seams"),
        ("clone_ready", "Inspect: Clone ready"),
        ("layer_matrix", "Inspect: Layer matrix"),
        ("layer_runtime", "Inspect: Layer runtime"),
        ("layer_pick", "Inspect: Layer pick"),
        ("selection_state", "Inspect: Selection state"),
        ("canvas_state", "Inspect: Canvas state"),
        ("pin_pick", "Inspect: Pin pick"),
        ("cursor_geo", "Inspect: Cursor geo"),
        ("boundary_json", "Inspect: Boundary JSON"),
        ("renderer_thumbnail", "Inspect: Renderer thumbnail"),
        ("live_preview", "Inspect: Live preview"),
    ]
    qt_inspector_groups = [
        {"id": "replay_contracts", "label": "Replay/contracts", "action_ids": ["profile_replay", "timeline", "clone_ready", "module_seams"]},
        {"id": "renderer_ports", "label": "Renderer ports", "action_ids": ["hydro_lod", "ocean_port", "style_routes", "layer_matrix", "layer_runtime"]},
        {"id": "research_interaction", "label": "Research interaction", "action_ids": ["layer_pick", "selection_state", "canvas_state", "pin_pick", "cursor_geo", "boundary_json"]},
        {"id": "visual_review", "label": "Visual review", "action_ids": ["renderer_thumbnail", "live_preview"]},
    ]
    return {
        "schema": "rrkal_displaytools.profile_ui_state_replay.v1",
        "source": source,
        "status": "ready",
        "saved_state_groups": saved_groups,
        "saved_state_group_count": len(saved_groups),
        "replay_surfaces": replay_surfaces,
        "replay_surface_count": len(replay_surfaces),
        "qt_inspector_action_ids": [action_id for action_id, _label in qt_inspector_actions],
        "qt_inspector_action_labels": [label for _action_id, label in qt_inspector_actions],
        "qt_inspector_action_count": len(qt_inspector_actions),
        "qt_inspector_action_groups": qt_inspector_groups,
        "qt_inspector_group_count": len(qt_inspector_groups),
        "qt_surface": "Layers dock profile UI replay label",
        "launch_packet_fields": ["profile_ui_state_replay", "profile", "timeline_keyframes", "timeline_runtime_state"],
        "renderer_capability_field": "profile_ui_state_replay",
        "handoff_field": "profile_ui_state_replay",
        "summary_text": "Profiles preserve renderer settings, layer stack, pins, Boundary emphasis/warnings and Timeline keyframes for cross-machine UI replay.",
        "boundary": "Replay coverage describes portable UI/profile state; it does not imply RRKAL data discovery/cache governance or authoritative geospatial identity resolution.",
    }


def layer_visual_presets_packet(
    source: str,
    selected_preset: str | None = None,
) -> dict[str, object]:
    presets = [
        {
            "id": "all_context",
            "label": "All context",
            "visible_layer_keys": ["__all__"],
            "intent": "Show every available layer for broad orientation and clone-after-setup review.",
        },
        {
            "id": "hydrology_focus",
            "label": "Hydrology focus",
            "visible_layer_keys": ["lake_layer", "river_layer", "bathymetry_layer", "coastline_layer"],
            "intent": "Focus water, bathymetry, coastline and river/lake layers for scientific hydrology review.",
        },
        {
            "id": "boundary_focus",
            "label": "Boundary focus",
            "visible_layer_keys": ["border_layer", "territorial_sea_layer", "eez_layer", "high_seas_layer"],
            "intent": "Focus border, territorial sea, EEZ and high-seas context for jurisdiction review.",
        },
        {
            "id": "annotation_focus",
            "label": "Annotation focus",
            "visible_layer_keys": ["pin_layer", "aircraft_layer", "vehicle_layer", "traffic_layer"],
            "intent": "Focus researcher annotations and operational point/icon overlays without brush or mask tools.",
        },
    ]
    preset_ids = [preset["id"] for preset in presets]
    selected = selected_preset if selected_preset in preset_ids else "custom"
    return {
        "schema": "rrkal_displaytools.layer_visual_presets.v1",
        "source": source,
        "selected_preset": selected,
        "preset_count": len(presets),
        "preset_ids": preset_ids,
        "presets": presets,
        "qt_surface": "Layers dock preset buttons",
        "profile_effect": "layer_stack_ui",
        "respects_layer_locks": True,
        "brush_mask_scope": "excluded",
        "launch_packet_fields": ["layer_visual_presets", "layer_stack_ui"],
        "renderer_capability_field": "layer_visual_presets",
        "boundary": "Qt layer visibility preset contract only; renderer state follows existing layer runtime sync and RRKAL data governance is not mutated.",
    }


def layer_visual_preset_runtime_feedback_packet(
    visual_presets: dict[str, object] | None,
    runtime_ack: dict[str, object] | None,
    source: str,
) -> dict[str, object]:
    visual_presets = visual_presets if isinstance(visual_presets, dict) else {}
    runtime_ack = runtime_ack if isinstance(runtime_ack, dict) else {}
    changed_layers = runtime_ack.get("changed_layers") if isinstance(runtime_ack.get("changed_layers"), list) else []
    changed_opacity_layers = runtime_ack.get("changed_opacity_layers") if isinstance(runtime_ack.get("changed_opacity_layers"), list) else []
    skipped_locked_layers = runtime_ack.get("skipped_locked_layers") if isinstance(runtime_ack.get("skipped_locked_layers"), list) else []
    ack_available = bool(runtime_ack)
    status = "ack_available" if ack_available else "waiting_for_renderer_ack"
    return {
        "schema": "rrkal_displaytools.layer_visual_preset_runtime_feedback.v1",
        "source": source,
        "preset_schema": visual_presets.get("schema"),
        "selected_preset": visual_presets.get("selected_preset", "custom"),
        "runtime_ack_available": ack_available,
        "runtime_ack_schema": runtime_ack.get("schema") if ack_available else "rrkal_displaytools.renderer_layer_runtime_ack.v1",
        "runtime_ack_event": runtime_ack.get("event"),
        "status": status,
        "changed_layer_count": len(changed_layers),
        "changed_opacity_layer_count": len(changed_opacity_layers),
        "skipped_locked_count": len(skipped_locked_layers),
        "qt_surface": "Layers dock preset renderer ack label",
        "ack_file": "state/renderer_layer_runtime_ack.json",
        "requires_renderer_ack_for_reproducibility": True,
        "launch_packet_fields": ["layer_visual_preset_runtime_feedback", "layer_visual_presets", "layer_runtime_evidence"],
        "renderer_capability_field": "layer_visual_preset_runtime_feedback",
        "boundary": "Preset feedback reads the existing renderer layer runtime ack bridge; it does not create a new renderer protocol or mutate RRKAL data governance.",
    }


def hydrology_lod_readiness_packet(
    source: str,
    capability_matrix: dict[str, object] | None = None,
) -> dict[str, object]:
    capability_matrix = capability_matrix if isinstance(capability_matrix, dict) else {}
    layers = capability_matrix.get("layers") if isinstance(capability_matrix.get("layers"), list) else []
    layers_by_key = {
        str(layer.get("key")): layer
        for layer in layers
        if isinstance(layer, dict) and layer.get("key")
    }
    hydrology_keys = ("lake_layer", "river_layer")
    fallback_targets = {"lake_layer": "lakes", "river_layer": "rivers"}
    hydrology_layers = []
    for key in hydrology_keys:
        layer = layers_by_key.get(
            key,
            {
                "key": key,
                "renderer_target": fallback_targets.get(key, key),
                "live_controls": ["visibility", "opacity", "blend", "selected_layer_pick"],
            },
        )
        live_controls = layer.get("live_controls") if isinstance(layer.get("live_controls"), list) else []
        hydrology_layers.append(
            {
                "key": key,
                "renderer_target": layer.get("renderer_target"),
                "visibility_live": "visibility" in live_controls,
                "opacity_live": "opacity" in live_controls,
                "blend_live": "blend" in live_controls,
                "selected_layer_pick_live": "selected_layer_pick" in live_controls,
            }
        )
    live_layer_count = sum(1 for layer in hydrology_layers if layer["visibility_live"])
    return {
        "schema": "rrkal_displaytools.hydrology_lod_readiness.v1",
        "source": source,
        "readiness": "ready" if live_layer_count == len(hydrology_layers) else "partial",
        "hydrology_layer_count": len(hydrology_layers),
        "live_hydrology_layer_count": live_layer_count,
        "hydrology_layers": hydrology_layers,
        "stable_qt_layer_keys": list(hydrology_keys),
        "stable_renderer_targets": ["lakes", "rivers"],
        "lod_hook_status": "contract_ready",
        "lod_hook_fields": ["renderer_target", "visible", "opacity", "blend_mode", "selected_layer_pick"],
        "deferred_context_layers": ["bathymetry_layer", "coastline_layer"],
        "qt_surface": "Layers dock Hydrology/LOD readiness label",
        "launch_packet_fields": ["hydrology_lod_readiness", "layer_capability_matrix", "layer_runtime_evidence"],
        "renderer_capability_field": "hydrology_lod_readiness",
        "boundary": "Displaytools owns hydrology renderer-facing layer contracts and LOD hook evidence; dataset discovery, download, import, and cache governance remain RRKAL-owned.",
    }


def hydrology_lod_runtime_evidence_packet(
    readiness: dict[str, object] | None,
    runtime_ack: dict[str, object] | None,
    pick_state: dict[str, object] | None,
    source: str,
) -> dict[str, object]:
    readiness = readiness if isinstance(readiness, dict) else {}
    runtime_ack = runtime_ack if isinstance(runtime_ack, dict) else {}
    pick_state = pick_state if isinstance(pick_state, dict) else {}
    hydrology_targets = set(readiness.get("stable_renderer_targets") if isinstance(readiness.get("stable_renderer_targets"), list) else ["lakes", "rivers"])
    changed_layers = runtime_ack.get("changed_layers") if isinstance(runtime_ack.get("changed_layers"), list) else []
    changed_opacity_layers = runtime_ack.get("changed_opacity_layers") if isinstance(runtime_ack.get("changed_opacity_layers"), list) else []
    changed_blend_layers = runtime_ack.get("changed_blend_layers") if isinstance(runtime_ack.get("changed_blend_layers"), list) else []
    hydrology_runtime_hits = [
        str(layer)
        for layer in [*changed_layers, *changed_opacity_layers, *changed_blend_layers]
        if str(layer) in hydrology_targets or str(layer) in {"lake_layer", "river_layer"}
    ]
    pick_result = pick_state.get("pick_result") if isinstance(pick_state.get("pick_result"), dict) else {}
    pick_layer = str(pick_result.get("layer") or pick_state.get("renderer_layer") or "")
    pick_matches_hydrology = pick_layer in hydrology_targets or pick_layer in {"lake_layer", "river_layer"}
    runtime_ack_available = bool(runtime_ack)
    pick_available = bool(pick_state)
    return {
        "schema": "rrkal_displaytools.hydrology_lod_runtime_evidence.v1",
        "source": source,
        "readiness_schema": readiness.get("schema"),
        "readiness": readiness.get("readiness", "unknown"),
        "runtime_ack_available": runtime_ack_available,
        "runtime_ack_schema": runtime_ack.get("schema") if runtime_ack_available else "rrkal_displaytools.renderer_layer_runtime_ack.v1",
        "pick_state_available": pick_available,
        "pick_layer": pick_layer or None,
        "pick_matches_hydrology": pick_matches_hydrology,
        "hydrology_runtime_hit_count": len(hydrology_runtime_hits),
        "hydrology_runtime_hits": hydrology_runtime_hits,
        "status": "runtime_evidence_available" if (runtime_ack_available or pick_available) else "waiting_for_runtime_evidence",
        "qt_surface": "Layers dock Hydrology runtime evidence label",
        "ack_file": "state/renderer_layer_runtime_ack.json",
        "pick_state_file": "state/renderer_layer_pick_state.json",
        "launch_packet_fields": ["hydrology_lod_runtime_evidence", "hydrology_lod_readiness", "layer_runtime_evidence"],
        "renderer_capability_field": "hydrology_lod_runtime_evidence",
        "boundary": "Runtime evidence summarizes existing renderer ack and selected-layer pick files; RRKAL data discovery/cache governance remain out of scope.",
    }


def ocean_material_control_port_packet(
    material: dict[str, object] | None,
    source: str,
) -> dict[str, object]:
    material = material if isinstance(material, dict) else {}

    def bounded_float(value: object, default: float, lower: float, upper: float) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = default
        return max(lower, min(number, upper))

    controls = {
        "wave_strength": bounded_float(material.get("wave_strength"), 0.22, 0.0, 1.0),
        "roughness": bounded_float(material.get("roughness"), 0.28, 0.02, 1.0),
        "foam": bounded_float(material.get("foam"), 0.12, 0.0, 1.0),
    }
    return {
        "schema": "rrkal_displaytools.ocean_material_control_port.v1",
        "source": source,
        "enabled": bool(material.get("enabled", True)),
        "material_controls": controls,
        "renderer_flags": ["--ocean-wave-strength", "--ocean-roughness", "--ocean-foam"],
        "taichi_uniforms": ["ocean_enabled", "wave_strength", "roughness", "foam", "time_seconds"],
        "sea_state_port": {
            "status": "manual_scalar_port_ready",
            "normalized_fields": ["wave_strength", "roughness", "foam", "timestamp"],
            "provider_ports": ["manual", "file", "url", "noaa_ww3", "hycom", "copernicus", "local_grid"],
            "renderer_consumes": ["wave_strength", "roughness", "foam"],
        },
        "qt_surface": "Properties dock ocean material controls",
        "launch_packet_fields": ["ocean_material_control_port", "profile.ocean_material", "command"],
        "renderer_capability_field": "ocean_material_control_port",
        "boundary": "Displaytools passes scalar ocean material controls and sea-state handoff fields only; RRKAL/provider modules own discovery, download, import and cache governance.",
    }


def module_boundary_registry_packet(source: str) -> dict[str, object]:
    boundaries = [
        {
            "module": "contracts/launch_packets.py",
            "owner": "displaytools-contracts",
            "responsibility": "Launch packets, renderer capabilities, handoff summaries and smoke-visible schemas.",
            "forbidden": ["Qt widgets", "Taichi kernels", "dataset discovery/download/cache eviction"],
        },
        {
            "module": "qt_ui/main_window.py",
            "owner": "displaytools-qt",
            "responsibility": "Qt-first Photoshop-like operator UI, layer controls, profiles, provenance and preview orchestration.",
            "forbidden": ["Tk primary UI", "provider cache governance", "Taichi kernel logic"],
        },
        {
            "module": "render_core/taichi_globe.py",
            "owner": "displaytools-render-core",
            "responsibility": "Taichi globe render loop, scalar uniforms, camera/projection draw calls and frame output.",
            "forbidden": ["Qt imports", "provider-specific IO", "RRKAL data repair"],
        },
        {
            "module": "render_core/ocean_material.py",
            "owner": "displaytools-render-core",
            "responsibility": "Map normalized sea-state scalars and style intent into ocean material uniforms.",
            "forbidden": ["provider discovery", "downloads", "cache lifecycle"],
        },
        {
            "module": "style_profiles.py",
            "owner": "displaytools-style",
            "responsibility": "Scientific, nautical, parchment and tactical visual intent, palettes and renderer routes.",
            "forbidden": ["Qt widget state", "provider IO", "cache governance"],
        },
        {
            "module": "overlays/vector_layers.py",
            "owner": "displaytools-overlays",
            "responsibility": "Layer composition, selected-layer picking, pins, hydrology/boundary drawing and diagnostics.",
            "forbidden": ["dataset discovery", "RRKAL manifest mutation", "Qt dialogs"],
        },
        {
            "module": "data_sources/*",
            "owner": "RRKAL-external",
            "responsibility": "Discovery, download, import, manifest and cache governance for hydrology, maritime and ocean-condition datasets.",
            "forbidden": ["displaytools-owned cache eviction", "renderer loop dependencies"],
        },
        {
            "module": "diagnostics/handoff.py",
            "owner": "displaytools-diagnostics",
            "responsibility": "Closed-loop status, smoke gates, renderer capability discovery and cross-machine handoff inspection.",
            "forbidden": ["mutating renderer state", "provider downloads"],
        },
    ]
    return {
        "schema": "rrkal_displaytools.module_boundary_registry.v1",
        "source": source,
        "module_count": len(boundaries),
        "target_modules": [boundary["module"] for boundary in boundaries],
        "boundaries": boundaries,
        "qt_first": True,
        "tk_primary_ui_allowed": False,
        "rrkal_data_governance_boundary": "RRKAL owns dataset discovery, download, import, manifest, cache lifecycle and repair; displaytools consumes governed references and renderer-ready contracts.",
        "displaytools_scope": "visualization UI, renderer contracts, launch packets, style/ocean/layer controls, diagnostics and handoff evidence.",
        "launch_packet_fields": ["module_boundary_registry"],
        "renderer_capability_field": "module_boundary_registry",
    }


def cross_machine_clone_readiness_packet(
    profile_readiness: dict[str, object] | None,
    module_boundaries: dict[str, object] | None,
    source: str,
) -> dict[str, object]:
    profile_readiness = profile_readiness if isinstance(profile_readiness, dict) else {}
    module_boundaries = module_boundaries if isinstance(module_boundaries, dict) else {}
    required_commands = [
        "scripts/setup_windows.ps1",
        "scripts/smoke.ps1",
        "scripts/run_qt_panel.ps1",
        "scripts/inspect_handoff.ps1",
    ]
    launcher_options = ["-SmokeFirst", "-HandoffFirst", "-Template", "-Profile"]
    handoff_first_command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_qt_panel.ps1 -HandoffFirst"
    first_run_order = [
        "git clone https://github.com/Kagamihara-Ruruka/RRKAL_displaytools.git",
        "cd RRKAL_displaytools",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup_windows.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/smoke.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_qt_panel.ps1",
    ]
    profile_ready = profile_readiness.get("readiness") == "ready"
    boundaries_ready = module_boundaries.get("schema") == "rrkal_displaytools.module_boundary_registry.v1"
    qt_first = module_boundaries.get("qt_first") is True
    tk_not_primary = module_boundaries.get("tk_primary_ui_allowed") is False
    return {
        "schema": "rrkal_displaytools.cross_machine_clone_readiness.v1",
        "source": source,
        "status": "ready" if profile_ready and boundaries_ready and qt_first and tk_not_primary else "partial",
        "repo_url": "https://github.com/Kagamihara-Ruruka/RRKAL_displaytools.git",
        "setup_doc": "docs/SETUP_WINDOWS.zh-TW.md",
        "qt_surface": "Layers dock cross-machine readiness label",
        "required_commands": required_commands,
        "launcher_options": launcher_options,
        "handoff_first_command": handoff_first_command,
        "first_run_order": first_run_order,
        "qt_first": qt_first,
        "tk_primary_ui_allowed": not tk_not_primary,
        "profile_launch_readiness_schema": profile_readiness.get("schema"),
        "profile_launch_readiness": profile_readiness.get("readiness", "unknown"),
        "module_boundary_registry_schema": module_boundaries.get("schema"),
        "smoke_required_before_push": True,
        "clone_after_setup_verification": ["smoke", "handoff inspection", "renderer capability discovery", "Qt panel launch", "handoff-first Qt launch"],
        "launch_packet_fields": ["cross_machine_clone_readiness", "profile_launch_readiness", "module_boundary_registry", "portable_command"],
        "renderer_capability_field": "cross_machine_clone_readiness",
        "boundary": "Cross-machine readiness covers clone/setup/smoke/run handoff only; data discovery, download, import and cache governance remain RRKAL-owned.",
    }


def layer_operator_shortcuts_packet(
    source: str,
    selected_layer: str | None = None,
    solo_snapshot_active: bool = False,
    undo_depth: int | None = None,
) -> dict[str, object]:
    keyboard_shortcuts = {
        "toggle_visibility": "Ctrl+Alt+V",
        "toggle_lock": "Ctrl+Alt+L",
        "solo_selected_layer": "Ctrl+Alt+S",
        "restore_solo_visibility": "Ctrl+Alt+R",
        "undo_layer_state": "Ctrl+Alt+Z",
        "reset_layer_ui_state": "Ctrl+Alt+0",
        "show_layer_diagnostics": "Ctrl+Alt+D",
    }
    actions = [
        {
            "id": "select_layer",
            "label": "Select layer",
            "surface": "Layers row",
            "state_scope": "selected_layer",
            "qt_available": True,
            "profile_effect": "selected_layer",
        },
        {
            "id": "toggle_visibility",
            "label": "Toggle visibility",
            "surface": "Layers row checkbox / Properties button",
            "state_scope": "layer_stack_ui.visible",
            "qt_available": True,
            "profile_effect": "layer_stack_ui",
        },
        {
            "id": "toggle_lock",
            "label": "Toggle lock",
            "surface": "Layers row lock",
            "state_scope": "layer_stack_ui.locked",
            "qt_available": True,
            "profile_effect": "layer_stack_ui",
        },
        {
            "id": "adjust_opacity",
            "label": "Adjust opacity",
            "surface": "Layers row slider",
            "state_scope": "layer_stack_ui.opacity",
            "qt_available": True,
            "profile_effect": "layer_stack_ui",
        },
        {
            "id": "set_blend_mode",
            "label": "Set blend mode",
            "surface": "Layers row blend combo",
            "state_scope": "layer_stack_ui.blend_mode",
            "qt_available": True,
            "profile_effect": "layer_stack_ui",
        },
        {
            "id": "open_boundary_emphasis",
            "label": "Open boundary emphasis controls",
            "surface": "Boundary layer row action badge / double-click",
            "state_scope": "boundary_emphasis_control",
            "qt_available": True,
            "profile_effect": "boundary_highlight",
        },
        {
            "id": "solo_selected_layer",
            "label": "Solo selected layer",
            "surface": "Layers actions",
            "state_scope": "layer_visibility_snapshot",
            "qt_available": True,
            "profile_effect": "runtime_state_only",
        },
        {
            "id": "restore_solo_visibility",
            "label": "Restore pre-solo visibility",
            "surface": "Layers actions",
            "state_scope": "layer_visibility_snapshot",
            "qt_available": True,
            "profile_effect": "runtime_state_only",
        },
        {
            "id": "undo_layer_state",
            "label": "Undo layer state",
            "surface": "Layers actions",
            "state_scope": "layer_undo",
            "qt_available": True,
            "profile_effect": "runtime_state_only",
        },
        {
            "id": "reset_layer_ui_state",
            "label": "Reset layer UI state",
            "surface": "Layers actions / Properties button",
            "state_scope": "layer_stack_ui",
            "qt_available": True,
            "profile_effect": "layer_stack_ui",
        },
        {
            "id": "show_layer_diagnostics",
            "label": "Show layer diagnostics",
            "surface": "Layers actions",
            "state_scope": "diagnostics_view",
            "qt_available": True,
            "profile_effect": "none",
        },
    ]
    for action in actions:
        shortcut = keyboard_shortcuts.get(str(action.get("id") or ""))
        if shortcut:
            action["keyboard_shortcut"] = shortcut
    return {
        "schema": "rrkal_displaytools.layer_operator_shortcuts.v1",
        "source": source,
        "ui_direction": "qt_first_photoshop_like_layer_operations",
        "selected_layer": selected_layer,
        "solo_snapshot_active": bool(solo_snapshot_active),
        "undo_depth": int(undo_depth or 0),
        "action_count": len(actions),
        "actions": actions,
        "implemented_action_ids": [action["id"] for action in actions if action.get("qt_available")],
        "keyboard_shortcut_count": len(keyboard_shortcuts),
        "keyboard_shortcuts": keyboard_shortcuts,
        "installed_shortcut_ids": [action["id"] for action in actions if action.get("keyboard_shortcut")],
        "profile_state_fields": ["selected_layer", "layer_stack_ui"],
        "launch_packet_fields": ["layer_operator_shortcuts", "layer_operator_groups", "layer_stack_ui", "layer_undo"],
        "summary_text": "select/toggle/lock/opacity/blend/solo/restore/undo/reset/diagnostics",
        "copyable_provenance": True,
        "boundary": "Qt operator shortcut contract only; renderer state and RRKAL data governance are not mutated.",
    }

def layer_operator_groups_packet(
    shortcuts: dict[str, object] | None,
    source: str,
) -> dict[str, object]:
    shortcuts = shortcuts if isinstance(shortcuts, dict) else {}
    raw_actions = shortcuts.get("actions") if isinstance(shortcuts.get("actions"), list) else []
    action_ids = {
        str(action.get("id"))
        for action in raw_actions
        if isinstance(action, dict) and action.get("id")
    }
    group_specs = (
        {
            "id": "selection",
            "label": "Selection",
            "action_ids": ["select_layer"],
            "purpose": "Choose the active layer before editing, isolation, provenance capture, or diagnostics.",
        },
        {
            "id": "edit_state",
            "label": "Edit state",
            "action_ids": ["toggle_visibility", "toggle_lock", "adjust_opacity", "set_blend_mode", "reset_layer_ui_state"],
            "purpose": "Control visibility, lock, opacity, blend mode, and reversible UI-only state for the selected layer.",
        },
        {
            "id": "isolation",
            "label": "Isolation",
            "action_ids": ["solo_selected_layer", "restore_solo_visibility"],
            "purpose": "Temporarily isolate a research layer and restore the previous visible-layer context.",
        },
        {
            "id": "history",
            "label": "History",
            "action_ids": ["undo_layer_state"],
            "purpose": "Recover the previous layer stack state during exploratory visual analysis.",
        },
        {
            "id": "diagnostics",
            "label": "Diagnostics",
            "action_ids": ["show_layer_diagnostics"],
            "purpose": "Expose renderer capability, runtime ack, and missing-live-control evidence for reproducibility.",
        },
    )
    groups = []
    for spec in group_specs:
        expected_ids = [str(action_id) for action_id in spec["action_ids"]]
        available_ids = [action_id for action_id in expected_ids if action_id in action_ids]
        missing_ids = [action_id for action_id in expected_ids if action_id not in action_ids]
        groups.append(
            {
                "id": spec["id"],
                "label": spec["label"],
                "purpose": spec["purpose"],
                "action_ids": expected_ids,
                "available_action_ids": available_ids,
                "missing_action_ids": missing_ids,
                "complete": not missing_ids,
            }
        )
    complete_group_count = sum(1 for group in groups if group["complete"])
    return {
        "schema": "rrkal_displaytools.layer_operator_groups.v1",
        "source": source,
        "shortcut_schema": shortcuts.get("schema"),
        "group_count": len(groups),
        "complete_group_count": complete_group_count,
        "groups": groups,
        "workflow_order": [group["id"] for group in groups],
        "summary_text": "Selection / Edit state / Isolation / History / Diagnostics",
        "copyable_provenance": True,
        "launch_packet_fields": ["layer_operator_groups", "layer_operator_shortcuts", "layer_stack_ui", "layer_undo"],
        "boundary": "Qt workflow grouping only; renderer state and RRKAL data governance are not mutated.",
    }


def layer_selection_tool_packet(source: str, selected_layer: str | None = None) -> dict[str, object]:
    selectable_layer_keys = sorted(
        globals().get(
            "LAYER_PICK_LIVE_KEYS",
            {"lake_layer", "river_layer", "border_layer", "traffic_layer", "pin_layer"},
        )
    )
    return {
        "schema": "rrkal_displaytools.layer_selection_tool.v1",
        "source": source,
        "status": "ready",
        "ui_direction": "qt_first_scientific_layer_selection",
        "tool_mode": "select_layer",
        "selection_model": "single_active_layer_with_renderer_pick_context",
        "selected_layer": selected_layer,
        "qt_surfaces": [
            "Layers dock row selection",
            "Select first filtered layer",
            "Reveal selected layer row",
            "Layer pick JSON inspector",
            "Boundary row emphasis action badge",
        ],
        "selection_sources": [
            "layer_row_click",
            "select_first_filtered_layer",
            "reveal_selected_layer_row",
            "renderer_layer_pick_state",
        ],
        "renderer_pick_bridge": {
            "schema": "rrkal_displaytools.renderer_layer_pick_state.v1",
            "pick_state_file": "state/renderer_layer_pick_state.json",
            "requires_selected_layer": True,
            "live_control": "selected_layer_pick",
        },
        "selectable_layer_count": len(selectable_layer_keys),
        "selectable_layer_keys": selectable_layer_keys,
        "supported_renderer_pick_scopes": ["pin", "traffic_point", "boundary_line", "hydrology_line"],
        "feature_identity_fields": ["feature_label", "source_properties", "name", "sovereignty", "iso_a3", "mrgid"],
        "brush_mask_scope": "excluded",
        "fallback_behavior": "If renderer pick state is unavailable, Qt row selection remains the authoritative active layer.",
        "launch_packet_fields": [
            "layer_selection_tool",
            "layer_capability_matrix",
            "layer_operator_shortcuts",
            "layer_research_workflow",
        ],
        "renderer_capability_field": "layer_selection_tool",
        "copyable_provenance": True,
        "boundary": "Selection tool state bridges Qt active-layer UX and renderer pick context only; brush/mask editing and RRKAL data governance stay out of scope.",
    }

def layer_research_workflow_packet(
    layer_filter: dict[str, object] | None,
    layer_group_view: dict[str, object] | None,
    operator_groups: dict[str, object] | None,
    capability_matrix: dict[str, object] | None,
    source: str,
) -> dict[str, object]:
    layer_filter = layer_filter if isinstance(layer_filter, dict) else {}
    layer_group_view = layer_group_view if isinstance(layer_group_view, dict) else {}
    operator_groups = operator_groups if isinstance(operator_groups, dict) else {}
    capability_matrix = capability_matrix if isinstance(capability_matrix, dict) else {}
    warning_list = capability_matrix.get("runtime_warning_list") if isinstance(capability_matrix.get("runtime_warning_list"), dict) else {}
    remediation = capability_matrix.get("renderer_diagnostics_remediation") if isinstance(capability_matrix.get("renderer_diagnostics_remediation"), dict) else {}
    selected_layer = capability_matrix.get("selected_layer") or layer_filter.get("selected_layer")
    ready = (
        capability_matrix.get("schema") == "rrkal_displaytools.layer_capability_matrix.v1"
        and operator_groups.get("schema") == "rrkal_displaytools.layer_operator_groups.v1"
        and int(operator_groups.get("complete_group_count") or 0) >= 5
    )
    return {
        "schema": "rrkal_displaytools.layer_research_workflow.v1",
        "source": source,
        "status": "ready" if ready else "partial",
        "selected_layer": selected_layer,
        "filter_schema": layer_filter.get("schema"),
        "filter_preset": layer_filter.get("preset"),
        "filter_query": layer_filter.get("query"),
        "first_matched_layer": layer_filter.get("first_matched_layer"),
        "selected_layer_visible": layer_filter.get("selected_layer_visible"),
        "group_view_schema": layer_group_view.get("schema"),
        "visible_row_count": layer_group_view.get("visible_row_count"),
        "selected_layer_hidden_by_group": layer_group_view.get("selected_layer_hidden_by_group"),
        "operator_group_count": operator_groups.get("group_count"),
        "complete_operator_group_count": operator_groups.get("complete_group_count"),
        "runtime_warning_severity": warning_list.get("severity", "unknown"),
        "runtime_warning_count": warning_list.get("warning_count", 0),
        "remediation_hint_count": remediation.get("hint_count", 0),
        "workflow_hint": "Layer workflow: click a row to select the active research layer; double-click Boundary/territorial sea/EEZ/high-seas rows or use Emphasis to open mask controls; identity warning badges mean preview/source-property identity only, not authoritative polygon/EEZ resolution.",
        "workflow_hint_surface": "Layers dock layerWorkflowHint / launch packet / handoff inspection",
        "researcher_path": [
            "Filter or group the layer list",
            "Select or reveal a layer",
            "Read runtime badge and warning summary",
            "Open renderer diagnostics/remediation before treating the state as reproducible",
        ],
        "qt_surface": "Layers dock research workflow label",
        "launch_packet_fields": ["layer_research_workflow", "layer_filter", "layer_group_view", "layer_capability_matrix"],
        "renderer_capability_field": "layer_research_workflow",
        "boundary": "Research workflow summarizes existing Qt layer controls and renderer diagnostics; it does not mutate renderer state or RRKAL data governance.",
    }


def boundary_emphasis_control_packet(
    state: dict[str, object] | None,
    selected_layer: str | None,
    source: str,
) -> dict[str, object]:
    state = state if isinstance(state, dict) else {}

    def _float_value(key: str, default: float) -> float:
        try:
            return float(state.get(key, default))
        except (TypeError, ValueError):
            return default

    color = state.get("color_rgb")
    if not isinstance(color, (list, tuple)) or len(color) != 3:
        color = [80, 180, 255]
    color_rgb = [max(0, min(255, int(channel))) for channel in color]
    target_mode = str(state.get("target_mode", "auto_selected_boundary_layer") or "auto_selected_boundary_layer")
    target_layer_by_mode = {
        "country_boundary": "border_layer",
        "territorial_sea": "territorial_sea_layer",
        "exclusive_economic_zone": "eez_layer",
        "maritime_boundary": "high_seas_layer",
    }
    boundary_layer_keys = set(target_layer_by_mode.values())
    selected_layer_key = selected_layer if isinstance(selected_layer, str) else None
    target_layer_key = target_layer_by_mode.get(target_mode)
    if target_mode == "auto_selected_boundary_layer":
        if selected_layer_key in boundary_layer_keys:
            target_layer_key = selected_layer_key
            target_alignment = "selected_layer_matches_target"
        elif selected_layer_key:
            target_alignment = "selected_layer_not_boundary_capable"
        else:
            target_alignment = "no_selected_layer"
    elif selected_layer_key == target_layer_key:
        target_alignment = "selected_layer_matches_target"
    elif selected_layer_key:
        target_alignment = "selected_layer_differs_from_target"
    else:
        target_alignment = "no_selected_layer"
    target_alignment_labels = {
        "selected_layer_matches_target": "Selected layer matches emphasis target",
        "selected_layer_differs_from_target": "Selected layer differs from emphasis target",
        "selected_layer_not_boundary_capable": "Selected layer is not boundary-capable",
        "no_selected_layer": "No selected layer",
    }
    controls = [
        {"id": "target_mode", "label": "Boundary target", "kind": "combo"},
        {"id": "color_rgb", "label": "RGB emphasis color", "kind": "rgb"},
        {"id": "contrast", "label": "Contrast", "kind": "slider"},
        {"id": "opacity", "label": "Opacity", "kind": "slider"},
        {"id": "gamma", "label": "Gamma", "kind": "slider"},
        {"id": "breathing_enabled", "label": "Breathing effect", "kind": "checkbox"},
        {"id": "breathing_period_s", "label": "Breathing period", "kind": "slider"},
    ]
    return {
        "schema": "rrkal_displaytools.boundary_emphasis_control.v1",
        "source": source,
        "status": "ui_ready",
        "selected_layer": selected_layer,
        "target_mode": target_mode,
        "target_layer_key": target_layer_key,
        "selected_layer_matches_target": target_alignment == "selected_layer_matches_target",
        "target_alignment": target_alignment,
        "target_alignment_label": target_alignment_labels.get(target_alignment, target_alignment),
        "target_layer_types": ["country_boundary", "territorial_sea", "exclusive_economic_zone", "maritime_boundary"],
        "color_rgb": color_rgb,
        "contrast": _float_value("contrast", 1.35),
        "opacity": _float_value("opacity", 0.42),
        "gamma": _float_value("gamma", 1.0),
        "breathing_enabled": bool(state.get("breathing_enabled", True)),
        "breathing_period_s": _float_value("breathing_period_s", 4.0),
        "hover_behavior": "Pointer hover preview is bridged through rrkal_displaytools.boundary_highlight_mask.v1.",
        "open_behavior": "Use the Layers dock button or double-click a boundary-capable layer row to open the dialog.",
        "qt_surface": "Layers dock boundary emphasis dialog",
        "row_double_click_binding": "ready",
        "row_double_click_layer_keys": ["border_layer", "territorial_sea_layer", "eez_layer", "high_seas_layer"],
        "renderer_hook_status": "wired_via_boundary_highlight_mask",
        "renderer_bridge_contract": "rrkal_displaytools.boundary_highlight_mask.v1",
        "renderer_controls_mapped": ["target_layers", "color_rgb", "contrast", "alpha", "gamma", "breathing"],
        "dialog_feedback": ["rgb_swatch", "live_numeric_readout", "renderer_bridge_summary"],
        "value_preview_fields": ["target_mode", "target_alignment", "color_rgb", "contrast", "opacity", "gamma", "breathing_period_s"],
        "pending_renderer_refinements": ["authoritative_polygon_identity", "open_line_area_inference", "full_polygon_fill_mask"],
        "control_count": len(controls),
        "controls": controls,
        "boundary": "UI profile state is mapped to the existing boundary highlight renderer bridge; governed geospatial ownership remains outside displaytools.",
    }


def layer_capability_matrix_packet(
    source: str,
    selected_layer: str | None = None,
    authoritative_identity_source_ref: str | None = None,
) -> dict[str, object]:
    layers = [layer_capability_packet(key, label) for key, label in LAYER_LABELS]
    runtime_evidence = {
        "schema": "rrkal_displaytools.layer_runtime_evidence.v1",
        "available": False,
        "ack_schema": "rrkal_displaytools.renderer_layer_runtime_ack.v1",
        "event": None,
        "updated_at_utc": None,
        "frame_index": None,
        "error": None,
        "selected_renderer_layer": None,
        "changed_layers": [],
        "changed_opacity_layers": [],
        "changed_blend_layers": [],
        "skipped_locked_layers": [],
        "counts": {
            "changed_visibility": 0,
            "changed_opacity": 0,
            "changed_blend": 0,
            "skipped_locked": 0,
        },
        "boundary": "No-GUI launch packets do not include runtime renderer ack evidence.",
    }
    for layer in layers:
        layer["runtime_evidence_available"] = False
        layer["runtime_status"] = ["no_ack"]
    counts = {
        "visibility": sum(1 for layer in layers if layer["visibility_live"]),
        "opacity": sum(1 for layer in layers if layer["opacity_live"]),
        "blend": sum(1 for layer in layers if layer["blend_live"]),
        "selected_layer_pick": sum(1 for layer in layers if layer["pick_live"]),
    }
    selected = next((layer for layer in layers if layer["key"] == selected_layer), None)
    runtime_evidence_summary = layer_runtime_evidence_summary_packet(runtime_evidence)
    runtime_badge_summary = layer_runtime_badge_summary_packet(layers, selected_layer, source)
    runtime_warning_list = layer_runtime_warning_list_packet(runtime_badge_summary, runtime_evidence_summary, source)
    renderer_target = selected.get("renderer_target") if isinstance(selected, dict) else None
    runtime_interaction_context = layer_runtime_interaction_context_packet(
        runtime_warning_list,
        selected_layer,
        str(renderer_target) if renderer_target else None,
        source,
    )
    authoritative_identity_source = layer_authoritative_identity_source_packet(authoritative_identity_source_ref, source)
    renderer_diagnostics_summary = layer_renderer_diagnostics_summary_packet(
        runtime_evidence_summary,
        runtime_warning_list,
        runtime_interaction_context,
        authoritative_identity_source,
        counts,
        selected_layer,
        source,
    )
    renderer_diagnostics_detail = layer_renderer_diagnostics_detail_packet(
        renderer_diagnostics_summary,
        runtime_evidence,
        runtime_warning_list,
        runtime_interaction_context,
        authoritative_identity_source,
        counts,
        selected_layer,
        source,
    )
    renderer_diagnostics_remediation = layer_renderer_diagnostics_remediation_packet(
        renderer_diagnostics_detail,
        renderer_diagnostics_summary,
        selected_layer,
        source,
    )
    return {
        "schema": "rrkal_displaytools.layer_capability_matrix.v1",
        "source": source,
        "layer_count": len(layers),
        "live_counts": counts,
        "runtime_evidence": runtime_evidence,
        "runtime_evidence_summary": runtime_evidence_summary,
        "runtime_badge_summary": runtime_badge_summary,
        "runtime_warning_list": runtime_warning_list,
        "runtime_interaction_context": runtime_interaction_context,
        "territory_identity_context": layer_territory_identity_context_packet(runtime_interaction_context, selected_layer, source),
        "authoritative_identity_source": authoritative_identity_source,
        "renderer_diagnostics_summary": renderer_diagnostics_summary,
        "renderer_diagnostics_detail": renderer_diagnostics_detail,
        "renderer_diagnostics_remediation": renderer_diagnostics_remediation,
        "runtime_status_legend": layer_runtime_status_legend_packet(),
        "selected_layer": selected_layer,
        "selected_layer_capabilities": selected,
        "layers": layers,
        "boundary": "Documents launch-packet layer controls and renderer live support; unsupported controls remain visible UI/profile state but are explicitly marked planned.",
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
    group_view = layer_group_view_packet(profile, matched_layers)
    collapsed_groups = set(group_view["collapsed_groups"])
    group_for_layer = {}
    for group_id, keys in group_view["available_groups"].items():
        for key in keys:
            group_for_layer[key] = group_id
    visible_matched_layers = [
        key for key in matched_layers if group_for_layer.get(key) not in collapsed_groups
    ]
    selected_layer = str(profile.get("selected_layer", ""))
    selected_layer_visible = selected_layer in visible_matched_layers
    return {
        "schema": "rrkal_displaytools.layer_filter.v1",
        "mode": "no_gui_export_status",
        "preset": preset if preset else "all",
        "available_presets": ["all", "hydrology", "maritime", "traffic", "visual_aids", "custom"],
        "query": query,
        "first_matched_layer": visible_matched_layers[0] if visible_matched_layers else None,
        "selected_layer_visible": selected_layer_visible,
        "selected_layer_reveal_available": bool(selected_layer) and not selected_layer_visible,
        "matched_layers": matched_layers,
        "matched_count": len(matched_layers),
        "visible_matched_layers": visible_matched_layers,
        "visible_matched_count": len(visible_matched_layers),
        "total_layers": len([key for key in BOOL_FLAGS if key != "demo_closed_loop"]),
        "boundary": "No-GUI launch packet preserves Qt row-filter/collapse state only; renderer layer state is unchanged.",
    }


def layer_group_view_packet(profile: dict[str, object], matched_layers: list[str] | None = None) -> dict[str, object]:
    groups = {
        "hydrology": ["lake_layer", "river_layer"],
        "maritime": ["border_layer", "territorial_sea_layer", "eez_layer", "high_seas_layer"],
        "traffic": ["aircraft_layer", "pin_layer", "vehicle_icons"],
        "visual_aids": ["show_grid", "show_stars", "terrain_contours", "scale_bar"],
    }
    payload = profile.get("layer_group_view")
    collapsed = []
    if isinstance(payload, dict):
        raw_collapsed = payload.get("collapsed_groups", [])
        if isinstance(raw_collapsed, list):
            collapsed = [str(group) for group in raw_collapsed if str(group) in groups]
    group_for_layer = {}
    for group_id, keys in groups.items():
        for key in keys:
            group_for_layer[key] = group_id
    candidates = matched_layers if matched_layers is not None else [key for key in BOOL_FLAGS if key != "demo_closed_loop"]
    visible_rows = [key for key in candidates if group_for_layer.get(key) not in set(collapsed)]
    selected_layer = str(profile.get("selected_layer", "")).strip()
    selected_group = group_for_layer.get(selected_layer) if selected_layer else None
    active_group_collapsed = selected_group in set(collapsed) if selected_group is not None else False
    return {
        "schema": "rrkal_displaytools.layer_group_view.v1",
        "mode": "no_gui_export_status",
        "available_groups": groups,
        "collapsed_groups": collapsed,
        "visible_counts_by_group": {
            group_id: sum(1 for key in keys if key in candidates and group_for_layer.get(key) not in set(collapsed))
            for group_id, keys in groups.items()
        },
        "total_counts_by_group": {group_id: len(keys) for group_id, keys in groups.items()},
        "selected_layer_group": selected_group,
        "selected_layer_hidden_by_group": active_group_collapsed,
        "active_group_collapsed": active_group_collapsed,
        "visible_row_count": len(visible_rows),
        "total_layers": len([key for key in BOOL_FLAGS if key != "demo_closed_loop"]),
        "boundary": "No-GUI launch packet preserves Qt row grouping only; renderer visibility is unchanged.",
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
                    "has_camera": isinstance(keyframe.get("camera"), dict),
                }
            )
    return {
        "schema": "rrkal_displaytools.timeline_state.v1",
        "status": "profile_keyframes_exported" if keyframes else "no_gui_export_no_runtime_keyframes",
        "implemented": ["launch_packet_status_contract", "profile_timeline_keyframe_handoff", "camera_keyframe_handoff", "camera_keyframe_interpolation"],
        "pending": [
            "visible_qt_timeline_dock",
            "keyframe_storage",
            "keyframe_restore",
            "playback_controls",
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
        "boundary": "No-GUI status contract includes renderer discrete step playback, PNG export, and discrete camera keyframes.",
    }


def timeline_runtime_state_packet(profile: dict[str, object], target_file: str = TIMELINE_STATE_PATH) -> dict[str, object]:
    profile_keyframes = profile.get("timeline_keyframes")
    keyframes = [dict(keyframe) for keyframe in profile_keyframes if isinstance(keyframe, dict)] if isinstance(profile_keyframes, list) else []
    timeline_state = timeline_state_packet(profile)
    active_step_state = timeline_active_step_state_packet(timeline_state, keyframes)
    return {
        "schema": "rrkal_displaytools.timeline_runtime_state.v1",
        "updated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "timeline_state": timeline_state,
        "playback_readiness": timeline_playback_readiness_packet(),
        "playback_plan": timeline_playback_plan_packet(keyframes),
        "segment_state": timeline_segment_state_packet(keyframes, active_step_state.get("active_index")),
        "active_step_state": active_step_state,
        "step_playback": timeline_step_playback_packet(timeline_state, keyframes, instantiated=False),
        "ocean_material_interpolation": timeline_ocean_material_interpolation_packet(timeline_state, keyframes, instantiated=False),
        "animation_export": timeline_animation_export_packet(executed=False),
        "camera_keyframe": timeline_camera_keyframe_packet(timeline_state, keyframes, instantiated=False),
        "camera_interpolation": timeline_camera_interpolation_packet(timeline_state, keyframes, instantiated=False),
        "layer_opacity_interpolation": timeline_layer_opacity_interpolation_packet(timeline_state, keyframes, instantiated=False),
        "layer_discrete_hold": timeline_layer_discrete_hold_packet(timeline_state, keyframes, instantiated=False),
        "timeline_keyframes": keyframes,
        "source": "scripts/export_launch_packet.py",
        "target_file": target_file,
        "boundary": "Save this payload to the target file before launching the renderer; discrete step playback, camera apply, material interpolation, and PNG export are supported.",
    }


def timeline_playback_readiness_packet() -> dict[str, object]:
    return {
        "schema": "rrkal_displaytools.timeline_playback_readiness.v1",
        "ui_preview_playback_available": True,
        "renderer_ack_available": True,
        "renderer_timeline_playback": True,
        "renderer_playback_mode": "discrete_keyframe_step",
        "ocean_material_interpolation": True,
        "animation_export": True,
        "animation_export_mode": "png_frame_sequence_with_optional_gif_mp4",
        "camera_keyframes": True,
        "camera_keyframe_interpolation": True,
        "layer_opacity_interpolation": True,
        "layer_discrete_hold": True,
        "pending": [
            "blend_crossfade_interpolation",
            "visibility_fade_interpolation",
        ],
        "boundary": "No-GUI handoff can export runtime state for renderer PNG frame sequence/GIF/MP4 export, camera keyframe interpolation, layer opacity interpolation, and active-keyframe layer visibility/blend hold. MP4 requires imageio[ffmpeg].",
    }


def timeline_playback_plan_packet(keyframes: list[dict[str, object]]) -> dict[str, object]:
    plan_keyframes = []
    for index, keyframe in enumerate(keyframes[:24]):
        pins = keyframe.get("pins")
        camera = keyframe.get("camera")
        boundary_emphasis = keyframe.get("boundary_emphasis_control")
        plan_keyframes.append(
            {
                "index": index,
                "id": str(keyframe.get("id", "")),
                "label": str(keyframe.get("label", "")),
                "style_profile": str(keyframe.get("style_profile", "")),
                "selected_layer": keyframe.get("selected_layer"),
                "has_ocean_material": isinstance(keyframe.get("ocean_material"), dict),
                "has_layer_stack_snapshot": isinstance(keyframe.get("layer_stack_snapshot"), dict),
                "pin_count": len(pins) if isinstance(pins, list) else 0,
                "has_boundary_highlight": isinstance(keyframe.get("boundary_highlight"), dict),
                "has_boundary_emphasis_control": isinstance(boundary_emphasis, dict),
                "has_camera": isinstance(camera, dict),
            }
        )
    return {
        "schema": "rrkal_displaytools.timeline_playback_plan.v1",
        "mode": "ordered_keyframe_plan",
        "playback_driver": "renderer_discrete_step_playback",
        "renderer_contract": "discrete_step_playback",
        "keyframe_count": len(plan_keyframes),
        "segment_count": max(0, len(plan_keyframes) - 1),
        "keyframes": plan_keyframes,
        "planned_apply_scope": [
            "style_profile",
            "ocean_material",
            "layer_stack_snapshot",
            "pins",
            "boundary_highlight",
            "boundary_emphasis_control",
            "camera",
            "layer_opacity",
            "layer_discrete_hold",
        ],
        "pending": [
            "blend_crossfade_interpolation",
            "visibility_fade_interpolation",
        ],
        "boundary": "Playback plan is exported for renderer discrete step playback, camera interpolation, ocean/material interpolation, layer opacity interpolation, and active-keyframe layer visibility/blend hold.",
    }


def timeline_segment_state_packet(
    keyframes: list[dict[str, object]],
    active_index: int | None = 0,
) -> dict[str, object]:
    keyframes = [keyframe for keyframe in keyframes if isinstance(keyframe, dict)] if isinstance(keyframes, list) else []
    segment_index = 0
    if len(keyframes) >= 2 and isinstance(active_index, int):
        segment_index = max(0, min(active_index, len(keyframes) - 2))
    active_segment = None
    if len(keyframes) >= 2:
        active_segment = {
            "from_index": segment_index,
            "to_index": segment_index + 1,
            "from_keyframe_id": str(keyframes[segment_index].get("id", "")),
            "to_keyframe_id": str(keyframes[segment_index + 1].get("id", "")),
            "interpolatable_fields": ["ocean_material", "camera", "layer_opacity"],
            "discrete_fields": [
                "style_profile",
                "layer_visibility",
                "layer_blend",
                "layer_discrete_hold",
                "pins",
                "boundary_highlight",
                "boundary_emphasis_control",
            ],
        }
    return {
        "schema": "rrkal_displaytools.timeline_segment_state.v1",
        "mode": "active_segment_preview",
        "source": "timeline_state.playback.next_index",
        "active_index": segment_index if active_segment is not None else None,
        "active_segment": active_segment,
        "segment_available": active_segment is not None,
        "segment_count": max(0, len(keyframes) - 1),
        "pending": ["blend_crossfade_interpolation", "visibility_fade_interpolation"],
        "boundary": "No-GUI segment state describes the next playback segment; camera, ocean material, and layer opacity are interpolatable fields, while layer visibility/blend are held discretely from the active keyframe.",
    }


def timeline_active_step_state_packet(
    timeline_state: dict[str, object] | None,
    keyframes: list[dict[str, object]],
) -> dict[str, object]:
    timeline_state = timeline_state if isinstance(timeline_state, dict) else {}
    playback = timeline_state.get("playback")
    playback = playback if isinstance(playback, dict) else {}
    try:
        requested_index = int(playback.get("next_index", 0))
    except (TypeError, ValueError):
        requested_index = 0
    active_index = None
    active_keyframe_id = None
    if keyframes:
        active_index = max(0, min(requested_index, len(keyframes) - 1))
        active_keyframe = keyframes[active_index]
        active_keyframe_id = str(active_keyframe.get("id", f"keyframe_{active_index + 1}"))
    return {
        "schema": "rrkal_displaytools.timeline_active_step_state.v1",
        "mode": "no_gui_active_step",
        "source": "timeline_state.playback.next_index",
        "playback_active": bool(playback.get("active")),
        "requested_index": requested_index,
        "active_index": active_index,
        "active_keyframe_id": active_keyframe_id,
        "keyframe_count": len(keyframes),
        "step_available": active_index is not None,
        "applies": ["renderer_startup_selection_hint"],
        "pending": ["blend_crossfade_interpolation", "visibility_fade_interpolation"],
        "boundary": "Active step is a discrete keyframe selection contract for renderer step playback.",
    }


def timeline_camera_payload(keyframe: dict[str, object] | None) -> dict[str, object] | None:
    if not isinstance(keyframe, dict):
        return None
    camera = keyframe.get("camera")
    if not isinstance(camera, dict):
        return None
    try:
        raw_yaw = camera.get("yaw")
        raw_pitch = camera.get("pitch")
        yaw = float(raw_yaw) if raw_yaw is not None else math.radians(float(camera.get("yaw_degrees", 0.0)))
        pitch = (
            float(raw_pitch)
            if raw_pitch is not None
            else math.radians(float(camera.get("pitch_degrees", 0.0)))
        )
        zoom = float(camera.get("zoom", 1.0))
    except (TypeError, ValueError):
        return None
    pitch_limit = math.pi / 2.0 - 0.01
    pitch = max(-pitch_limit, min(pitch_limit, pitch))
    zoom = max(0.08, min(zoom, 4.0))
    return {
        "yaw": yaw,
        "pitch": pitch,
        "zoom": zoom,
        "yaw_degrees": math.degrees(yaw),
        "pitch_degrees": math.degrees(pitch),
    }


def timeline_camera_keyframe_packet(
    timeline_state: dict[str, object] | None,
    keyframes: list[dict[str, object]],
    instantiated: bool = False,
) -> dict[str, object]:
    active_step = timeline_active_step_state_packet(timeline_state, keyframes)
    active_index = active_step.get("active_index")
    active_camera = None
    if isinstance(active_index, int) and 0 <= active_index < len(keyframes):
        active_camera = timeline_camera_payload(keyframes[active_index])
    return {
        "schema": "rrkal_displaytools.timeline_camera_keyframe.v1",
        "supported": True,
        "instantiated": bool(instantiated),
        "mode": "renderer_discrete_camera_keyframe",
        "active_index": active_index,
        "camera": active_camera,
        "applies": ["renderer_discrete_camera_apply"],
        "pending": [],
        "boundary": "Camera keyframes are applied discretely at active keyframes; smooth playback is represented by timeline_camera_interpolation.",
    }


def _lerp_camera_angle(start: float, end: float, fraction: float) -> float:
    delta = (end - start + math.pi) % (2.0 * math.pi) - math.pi
    return start + delta * fraction


def timeline_camera_interpolation_packet(
    timeline_state: dict[str, object] | None,
    keyframes: list[dict[str, object]],
    instantiated: bool = False,
    last_step_at: float | None = None,
) -> dict[str, object]:
    playback = timeline_state.get("playback") if isinstance(timeline_state, dict) else {}
    playback = playback if isinstance(playback, dict) else {}
    active_step = timeline_active_step_state_packet(timeline_state, keyframes)
    from_index = active_step.get("active_index")
    to_index = ((from_index + 1) % len(keyframes)) if isinstance(from_index, int) and len(keyframes) >= 2 else None
    try:
        interval_ms = int(playback.get("interval_ms", 1200))
    except (TypeError, ValueError):
        interval_ms = 1200
    interval_s = max(0.05, interval_ms / 1000.0)
    elapsed_s = 0.0 if last_step_at is None else max(0.0, time.time() - float(last_step_at))
    fraction = 0.0 if not instantiated else max(0.0, min(1.0, elapsed_s / interval_s))
    interpolated: dict[str, float] = {}
    if isinstance(from_index, int) and isinstance(to_index, int):
        from_camera = timeline_camera_payload(keyframes[from_index])
        to_camera = timeline_camera_payload(keyframes[to_index])
        if isinstance(from_camera, dict) and isinstance(to_camera, dict):
            yaw = _lerp_camera_angle(float(from_camera["yaw"]), float(to_camera["yaw"]), fraction)
            pitch = float(from_camera["pitch"]) + (float(to_camera["pitch"]) - float(from_camera["pitch"])) * fraction
            zoom = float(from_camera["zoom"]) + (float(to_camera["zoom"]) - float(from_camera["zoom"])) * fraction
            interpolated = {
                "yaw": yaw,
                "pitch": pitch,
                "zoom": max(0.08, min(zoom, 4.0)),
                "yaw_degrees": math.degrees(yaw),
                "pitch_degrees": math.degrees(pitch),
            }
    return {
        "schema": "rrkal_displaytools.timeline_camera_interpolation.v1",
        "supported": True,
        "instantiated": bool(instantiated),
        "mode": "linear_camera_segment",
        "playback_active": bool(playback.get("active")),
        "active": bool(playback.get("active")) and bool(interpolated),
        "from_index": from_index,
        "to_index": to_index,
        "fraction": fraction,
        "fields": ["yaw", "pitch", "zoom"],
        "interpolated": interpolated,
        "applies": ["camera_keyframe_interpolation"],
        "pending": [],
        "boundary": "Camera yaw/pitch/zoom are linearly interpolated across the active Timeline segment; yaw uses shortest-angle interpolation.",
    }


def timeline_layer_opacity_payload(keyframe: dict[str, object] | None) -> dict[str, float]:
    if not isinstance(keyframe, dict):
        return {}
    snapshot = keyframe.get("layer_stack_snapshot")
    snapshot = snapshot if isinstance(snapshot, dict) else {}
    layers = snapshot.get("layers")
    layers = layers if isinstance(layers, dict) else snapshot
    opacities: dict[str, float] = {}
    for layer_key, layer_state in layers.items():
        if not isinstance(layer_state, dict):
            continue
        raw_opacity = layer_state.get("opacity")
        if raw_opacity is None:
            continue
        try:
            opacities[str(layer_key)] = max(0.0, min(100.0, float(raw_opacity)))
        except (TypeError, ValueError):
            continue
    return opacities


def timeline_layer_opacity_interpolation_packet(
    timeline_state: dict[str, object] | None,
    keyframes: list[dict[str, object]],
    instantiated: bool = False,
    last_step_at: float | None = None,
) -> dict[str, object]:
    playback = timeline_state.get("playback") if isinstance(timeline_state, dict) else {}
    playback = playback if isinstance(playback, dict) else {}
    active_step = timeline_active_step_state_packet(timeline_state, keyframes)
    from_index = active_step.get("active_index")
    to_index = ((from_index + 1) % len(keyframes)) if isinstance(from_index, int) and len(keyframes) >= 2 else None
    try:
        interval_ms = int(playback.get("interval_ms", 1200))
    except (TypeError, ValueError):
        interval_ms = 1200
    interval_s = max(0.05, interval_ms / 1000.0)
    elapsed_s = 0.0 if last_step_at is None else max(0.0, time.time() - float(last_step_at))
    fraction = 0.0 if not instantiated else max(0.0, min(1.0, elapsed_s / interval_s))
    interpolated: dict[str, float] = {}
    if isinstance(from_index, int) and isinstance(to_index, int):
        from_opacity = timeline_layer_opacity_payload(keyframes[from_index])
        to_opacity = timeline_layer_opacity_payload(keyframes[to_index])
        for layer_key in sorted(set(from_opacity) | set(to_opacity)):
            start = from_opacity.get(layer_key)
            end = to_opacity.get(layer_key)
            if start is None and end is None:
                continue
            if start is None:
                start = end
            if end is None:
                end = start
            if start is None or end is None:
                continue
            interpolated[layer_key] = round(float(start) + (float(end) - float(start)) * fraction, 4)
    return {
        "schema": "rrkal_displaytools.timeline_layer_opacity_interpolation.v1",
        "supported": True,
        "instantiated": bool(instantiated),
        "mode": "linear_layer_opacity_segment",
        "playback_active": bool(playback.get("active")),
        "active": bool(playback.get("active")) and bool(interpolated),
        "from_index": from_index,
        "to_index": to_index,
        "fraction": fraction,
        "fields": ["layer_stack_snapshot.layers.*.opacity"],
        "interpolated_layer_opacity": interpolated,
        "layer_count": len(interpolated),
        "applies": ["layer_opacity_keyframe_interpolation"],
        "pending": ["blend_crossfade_interpolation", "visibility_fade_interpolation"],
        "boundary": "No-GUI handoff exports layer opacity interpolation; renderer owns runtime apply.",
    }


def timeline_layer_discrete_hold_payload(keyframe: dict[str, object] | None) -> dict[str, dict[str, object]]:
    if not isinstance(keyframe, dict):
        return {"visible": {}, "blend_mode": {}}
    snapshot = keyframe.get("layer_stack_snapshot")
    snapshot = snapshot if isinstance(snapshot, dict) else {}
    layers = snapshot.get("layers")
    layers = layers if isinstance(layers, dict) else snapshot
    visible: dict[str, bool] = {}
    blend_mode: dict[str, str] = {}
    for layer_key, layer_state in layers.items():
        if not isinstance(layer_state, dict):
            continue
        if isinstance(layer_state.get("visible"), bool):
            visible[str(layer_key)] = bool(layer_state["visible"])
        raw_blend = layer_state.get("blend_mode")
        if isinstance(raw_blend, str) and raw_blend:
            blend_mode[str(layer_key)] = raw_blend
    return {"visible": visible, "blend_mode": blend_mode}


def timeline_layer_discrete_hold_packet(
    timeline_state: dict[str, object] | None,
    keyframes: list[dict[str, object]],
    instantiated: bool = False,
) -> dict[str, object]:
    playback = timeline_state.get("playback") if isinstance(timeline_state, dict) else {}
    playback = playback if isinstance(playback, dict) else {}
    active_step = timeline_active_step_state_packet(timeline_state, keyframes)
    active_index = active_step.get("active_index")
    active_keyframe_id = active_step.get("active_keyframe_id")
    held = {"visible": {}, "blend_mode": {}}
    if isinstance(active_index, int) and 0 <= active_index < len(keyframes):
        held = timeline_layer_discrete_hold_payload(keyframes[active_index])
    visible = held.get("visible", {}) if isinstance(held, dict) else {}
    blend_mode = held.get("blend_mode", {}) if isinstance(held, dict) else {}
    return {
        "schema": "rrkal_displaytools.timeline_layer_discrete_hold.v1",
        "supported": True,
        "instantiated": bool(instantiated),
        "mode": "active_keyframe_layer_discrete_hold",
        "playback_active": bool(playback.get("active")),
        "active_index": active_index,
        "active_keyframe_id": active_keyframe_id,
        "fields": ["layer_stack_snapshot.layers.*.visible", "layer_stack_snapshot.layers.*.blend_mode"],
        "held_layer_visible": visible,
        "held_layer_blend_mode": blend_mode,
        "layer_count": len(set(visible) | set(blend_mode)),
        "applies": ["layer_visibility_discrete_hold", "layer_blend_mode_discrete_hold"],
        "pending": ["blend_crossfade_interpolation", "visibility_fade_interpolation"],
        "boundary": "No-GUI handoff exports active-keyframe layer visibility/blend hold; renderer owns runtime apply.",
    }


def timeline_step_playback_packet(
    timeline_state: dict[str, object] | None,
    keyframes: list[dict[str, object]],
    instantiated: bool = False,
) -> dict[str, object]:
    timeline_state = timeline_state if isinstance(timeline_state, dict) else {}
    playback = timeline_state.get("playback")
    playback = playback if isinstance(playback, dict) else {}
    active_step = timeline_active_step_state_packet(timeline_state, keyframes)
    try:
        interval_ms = int(playback.get("interval_ms", 1200))
    except (TypeError, ValueError):
        interval_ms = 1200
    return {
        "schema": "rrkal_displaytools.timeline_step_playback.v1",
        "supported": True,
        "instantiated": bool(instantiated),
        "mode": "renderer_discrete_keyframe_step",
        "playback_active": bool(playback.get("active")),
        "interval_ms": max(50, interval_ms),
        "current_index": active_step.get("active_index"),
        "keyframe_count": len(keyframes),
        "step_count": 0,
        "applies": ["renderer_discrete_keyframe_step"],
        "pending": ["blend_crossfade_interpolation", "visibility_fade_interpolation"],
        "boundary": "Renderer can advance whole-keyframe steps and apply discrete camera state; layer blend interpolation and visibility interpolation remain pending.",
    }


def timeline_ocean_material_interpolation_packet(
    timeline_state: dict[str, object] | None,
    keyframes: list[dict[str, object]],
    instantiated: bool = False,
) -> dict[str, object]:
    timeline_state = timeline_state if isinstance(timeline_state, dict) else {}
    playback = timeline_state.get("playback")
    playback = playback if isinstance(playback, dict) else {}
    active_step = timeline_active_step_state_packet(timeline_state, keyframes)
    from_index = active_step.get("active_index")
    to_index = ((from_index + 1) % len(keyframes)) if isinstance(from_index, int) and len(keyframes) >= 2 else None
    return {
        "schema": "rrkal_displaytools.timeline_ocean_material_interpolation.v1",
        "supported": True,
        "instantiated": bool(instantiated),
        "mode": "linear_ocean_material_segment",
        "playback_active": bool(playback.get("active")),
        "from_index": from_index,
        "to_index": to_index,
        "fraction": 0.0,
        "fields": ["wave_strength", "roughness", "foam"],
        "interpolated": {},
        "applies": ["ocean_material_keyframe_interpolation"],
        "pending": ["blend_crossfade_interpolation", "visibility_fade_interpolation"],
        "boundary": "Only ocean material scalar fields are interpolated here; layer opacity is handled by the layer opacity interpolation contract, while style/blend/visibility/pins/boundary remain discrete.",
    }


def timeline_animation_export_packet(executed: bool = False) -> dict[str, object]:
    return {
        "schema": "rrkal_displaytools.timeline_animation_export.v1",
        "supported": True,
        "executed": bool(executed),
        "mode": "png_frame_sequence_with_optional_gif_mp4",
        "frame_count": 0,
        "fps": 24.0,
        "manifest_file": None,
        "frames": [],
        "gif_file": None,
        "mp4_file": None,
        "encoded_animation": False,
        "encoding_format": None,
        "encoding_error": None,
        "encoded_video": False,
        "video_encoding_format": None,
        "video_encoding_error": None,
        "applies": ["timeline_png_frame_sequence", "timeline_animation_manifest", "timeline_gif_animation", "timeline_mp4_video"],
        "pending": ["blend_crossfade_interpolation", "visibility_fade_interpolation"],
        "boundary": "No-GUI launch packets expose renderer animation export capability; renderer writes frames, manifest, optional GIF, and optional MP4 with interpolated camera and layer opacity keyframes. MP4 requires imageio[ffmpeg].",
    }


def launch_packet(
    profile_path: Path,
    profile: dict[str, object],
    rrkal_data_manifest_ref: str = "",
    timeline_state_file: str = TIMELINE_STATE_PATH,
    timeline_ack_file: str = TIMELINE_ACK_PATH,
    timeline_export_options: dict[str, object] | None = None,
) -> dict[str, object]:
    export_options = timeline_export_options if isinstance(timeline_export_options, dict) else timeline_export_options_packet()
    portable_command = [
        "py",
        "-3",
        "taichi_global_bathymetry.py",
        *renderer_args(profile, rrkal_data_manifest_ref, timeline_state_file, timeline_ack_file, export_options),
    ]
    manifest_ref = rrkal_data_manifest_ref or str(profile.get("renderer", {}).get("rrkal_data_manifest_ref", "")).strip()
    profile_keyframes = profile.get("timeline_keyframes")
    timeline_keyframes = [dict(keyframe) for keyframe in profile_keyframes if isinstance(keyframe, dict)] if isinstance(profile_keyframes, list) else []
    timeline_state = timeline_state_packet(profile)
    timeline_active_step_state = timeline_active_step_state_packet(timeline_state, timeline_keyframes)
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
        "layer_group_view": layer_group_view_packet(profile),
        "layer_operator_shortcuts": layer_operator_shortcuts_packet("scripts.export_launch_packet", profile.get("selected_layer") if isinstance(profile.get("selected_layer"), str) else None),
        "layer_operator_groups": layer_operator_groups_packet(layer_operator_shortcuts_packet("scripts.export_launch_packet", profile.get("selected_layer") if isinstance(profile.get("selected_layer"), str) else None), "scripts.export_launch_packet"),
        "layer_selection_tool": layer_selection_tool_packet("scripts.export_launch_packet", profile.get("selected_layer") if isinstance(profile.get("selected_layer"), str) else None),
        "layer_research_workflow": layer_research_workflow_packet(layer_filter_packet(profile), layer_group_view_packet(profile), layer_operator_groups_packet(layer_operator_shortcuts_packet("scripts.export_launch_packet", profile.get("selected_layer") if isinstance(profile.get("selected_layer"), str) else None), "scripts.export_launch_packet"), layer_capability_matrix_packet("scripts.export_launch_packet", profile.get("selected_layer") if isinstance(profile.get("selected_layer"), str) else None, rrkal_data_manifest_ref), "scripts.export_launch_packet"),
        "boundary_emphasis_control": boundary_emphasis_control_packet(profile.get("boundary_emphasis_control") if isinstance(profile.get("boundary_emphasis_control"), dict) else None, profile.get("selected_layer") if isinstance(profile.get("selected_layer"), str) else None, "scripts.export_launch_packet"),
        "style_renderer_entries": style_renderer_entries_packet("scripts.export_launch_packet", profile.get("style_profile") if isinstance(profile.get("style_profile"), str) else None),
        "style_profile_renderer_routes": style_profile_renderer_routes_packet(style_renderer_entries_packet("scripts.export_launch_packet", profile.get("style_profile") if isinstance(profile.get("style_profile"), str) else None), "scripts.export_launch_packet"),
        "module_boundary_registry": module_boundary_registry_packet("scripts.export_launch_packet"),
        "cross_machine_clone_readiness": cross_machine_clone_readiness_packet(profile_launch_readiness_packet("scripts.export_launch_packet", style_renderer_entries_packet("scripts.export_launch_packet", profile.get("style_profile") if isinstance(profile.get("style_profile"), str) else None), layer_operator_groups_packet(layer_operator_shortcuts_packet("scripts.export_launch_packet", profile.get("selected_layer") if isinstance(profile.get("selected_layer"), str) else None), "scripts.export_launch_packet")), module_boundary_registry_packet("scripts.export_launch_packet"), "scripts.export_launch_packet"),
        "profile_launch_readiness": profile_launch_readiness_packet("scripts.export_launch_packet", style_renderer_entries_packet("scripts.export_launch_packet", profile.get("style_profile") if isinstance(profile.get("style_profile"), str) else None), layer_operator_groups_packet(layer_operator_shortcuts_packet("scripts.export_launch_packet", profile.get("selected_layer") if isinstance(profile.get("selected_layer"), str) else None), "scripts.export_launch_packet")),
        "profile_launch_readiness_ui": profile_launch_readiness_ui_packet(profile_launch_readiness_packet("scripts.export_launch_packet", style_renderer_entries_packet("scripts.export_launch_packet", profile.get("style_profile") if isinstance(profile.get("style_profile"), str) else None), layer_operator_groups_packet(layer_operator_shortcuts_packet("scripts.export_launch_packet", profile.get("selected_layer") if isinstance(profile.get("selected_layer"), str) else None), "scripts.export_launch_packet")), "scripts.export_launch_packet"),
        "profile_ui_state_replay": profile_ui_state_replay_packet("scripts.export_launch_packet"),
        "layer_visual_presets": layer_visual_presets_packet("scripts.export_launch_packet"),
        "layer_visual_preset_runtime_feedback": layer_visual_preset_runtime_feedback_packet(layer_visual_presets_packet("scripts.export_launch_packet"), None, "scripts.export_launch_packet"),
        "hydrology_lod_readiness": hydrology_lod_readiness_packet("scripts.export_launch_packet", layer_capability_matrix_packet("scripts.export_launch_packet", profile.get("selected_layer") if isinstance(profile.get("selected_layer"), str) else None, rrkal_data_manifest_ref)),
        "hydrology_lod_runtime_evidence": hydrology_lod_runtime_evidence_packet(hydrology_lod_readiness_packet("scripts.export_launch_packet", layer_capability_matrix_packet("scripts.export_launch_packet", profile.get("selected_layer") if isinstance(profile.get("selected_layer"), str) else None, rrkal_data_manifest_ref)), None, None, "scripts.export_launch_packet"),
        "ocean_material_control_port": ocean_material_control_port_packet(profile.get("ocean_material") if isinstance(profile.get("ocean_material"), dict) else None, "scripts.export_launch_packet"),
        "layer_capability_matrix": layer_capability_matrix_packet("scripts.export_launch_packet", profile.get("selected_layer") if isinstance(profile.get("selected_layer"), str) else None, rrkal_data_manifest_ref),
        "canvas_preview": canvas_preview_packet(profile),
        "cursor_geodesy_readout": cursor_geodesy_readout_packet(canvas_preview_packet(profile), "scripts.export_launch_packet"),
        "pin_overlay": pin_projection_contract_packet(),
        "boundary_highlight": boundary_highlight_packet(profile),
        "active_layer_diagnostics": active_layer_diagnostics_packet(profile, rrkal_data_manifest_ref),
        "layer_undo": layer_undo_packet(),
        "session_journal": session_journal_packet(),
        "document_undo": document_undo_packet(),
        "timeline_state": timeline_state,
        "timeline_playback_readiness": timeline_playback_readiness_packet(),
        "timeline_playback_plan": timeline_playback_plan_packet(timeline_keyframes),
        "timeline_segment_state": timeline_segment_state_packet(timeline_keyframes, timeline_active_step_state.get("active_index")),
        "timeline_active_step_state": timeline_active_step_state,
        "timeline_step_playback": timeline_step_playback_packet(timeline_state, timeline_keyframes, instantiated=False),
        "timeline_ocean_material_interpolation": timeline_ocean_material_interpolation_packet(timeline_state, timeline_keyframes, instantiated=False),
        "timeline_animation_export": timeline_animation_export_packet(executed=False),
        "timeline_export_options": export_options,
        "timeline_camera_keyframe": timeline_camera_keyframe_packet(timeline_state, timeline_keyframes, instantiated=False),
        "timeline_camera_interpolation": timeline_camera_interpolation_packet(timeline_state, timeline_keyframes, instantiated=False),
        "timeline_layer_opacity_interpolation": timeline_layer_opacity_interpolation_packet(timeline_state, timeline_keyframes, instantiated=False),
        "timeline_layer_discrete_hold": timeline_layer_discrete_hold_packet(timeline_state, timeline_keyframes, instantiated=False),
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
    parser.add_argument("--timeline-export-dir")
    parser.add_argument("--timeline-export-frames", type=int, default=24)
    parser.add_argument("--timeline-export-fps", type=float, default=24.0)
    parser.add_argument("--timeline-export-gif")
    parser.add_argument("--timeline-export-mp4")
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
    timeline_export_options = timeline_export_options_packet(
        args.timeline_export_dir,
        args.timeline_export_frames,
        args.timeline_export_fps,
        args.timeline_export_gif,
        args.timeline_export_mp4,
    )
    packet = launch_packet(
        profile_path,
        profile,
        str(args.rrkal_data_manifest_ref or "").strip(),
        timeline_state_file,
        TIMELINE_ACK_PATH,
        timeline_export_options,
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



