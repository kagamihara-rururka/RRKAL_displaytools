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
TIMELINE_STATE_PATH = "state/renderer_timeline_state.json"
TIMELINE_ACK_PATH = "state/renderer_timeline_ack.json"
TIMELINE_EXPORT_DIR = "state/timeline_exports"
TIMELINE_EXPORT_MANIFEST = "timeline_animation_manifest.json"
TIMELINE_EXPORT_GIF = "timeline_animation.gif"
TIMELINE_EXPORT_MP4 = "timeline_animation.mp4"
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
    selected_label = next((label for key, label in LAYER_LABELS if key == selected_layer), selected_layer)
    return {
        "schema": "rrkal_displaytools.active_layer_diagnostics.v1",
        "selected_layer": selected_layer,
        "renderer_target": renderer_target,
        "capabilities": layer_capability_packet(selected_layer, selected_label) if selected_layer else None,
        "layer_capability_matrix_schema": "rrkal_displaytools.layer_capability_matrix.v1",
        "layer_runtime_evidence_schema": "rrkal_displaytools.layer_runtime_evidence.v1",
        "layer_runtime_evidence_summary_schema": "rrkal_displaytools.layer_runtime_evidence_summary.v1",
        "layer_runtime_badge_summary_schema": "rrkal_displaytools.layer_runtime_badge_summary.v1",
        "layer_runtime_warning_list_schema": "rrkal_displaytools.layer_runtime_warning_list.v1",
        "runtime_evidence_summary": layer_runtime_evidence_summary_packet(None),
        "runtime_badge_summary": layer_capability_matrix_packet("scripts.export_launch_packet", selected_layer).get("runtime_badge_summary"),
        "runtime_warning_list": layer_capability_matrix_packet("scripts.export_launch_packet", selected_layer).get("runtime_warning_list"),
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


def layer_capability_matrix_packet(source: str, selected_layer: str | None = None) -> dict[str, object]:
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
    return {
        "schema": "rrkal_displaytools.layer_capability_matrix.v1",
        "source": source,
        "layer_count": len(layers),
        "live_counts": counts,
        "runtime_evidence": runtime_evidence,
        "runtime_evidence_summary": runtime_evidence_summary,
        "runtime_badge_summary": runtime_badge_summary,
        "runtime_warning_list": layer_runtime_warning_list_packet(runtime_badge_summary, runtime_evidence_summary, source),
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
            "discrete_fields": ["style_profile", "layer_visibility", "layer_blend", "layer_discrete_hold", "pins", "boundary_highlight"],
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
        "layer_capability_matrix": layer_capability_matrix_packet("scripts.export_launch_packet", profile.get("selected_layer") if isinstance(profile.get("selected_layer"), str) else None),
        "canvas_preview": canvas_preview_packet(profile),
        "boundary_highlight": boundary_highlight_packet(profile),
        "active_layer_diagnostics": active_layer_diagnostics_packet(profile),
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
