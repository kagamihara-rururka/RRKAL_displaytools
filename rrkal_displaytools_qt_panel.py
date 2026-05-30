"""Qt operator panel for RRKAL_displaytools layer/UI launch.

This panel intentionally stays outside the renderer loop. It collects operator
choices, builds command-line flags, and starts taichi_global_bathymetry.py.
RRKAL remains responsible for data discovery, download, manifest, and cache
governance; this file is only a displaytools control surface.
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
import subprocess
import sys
from pathlib import Path

from closed_loop_status import renderer_closed_loop_status_packet
from profile_schema import profile_payload_errors
from pin_projection import pin_projection_contract_packet


ROOT = Path(__file__).resolve().parent
PROFILE_TEMPLATE_DIR = ROOT / "profiles"
PIN_PICK_STATE_PATH = ROOT / "state" / "renderer_pin_pick_state.json"
PIN_INPUT_ACK_PATH = ROOT / "state" / "renderer_pin_input_ack.json"
PIN_PICK_ACK_PATH = ROOT / "state" / "qt_pin_pick_ack.json"
BOUNDARY_HIGHLIGHT_ACK_PATH = ROOT / "state" / "renderer_boundary_highlight_ack.json"
LAYER_RUNTIME_STATE_PATH = ROOT / "state" / "renderer_layer_runtime_state.json"
LAYER_RUNTIME_ACK_PATH = ROOT / "state" / "renderer_layer_runtime_ack.json"
LAYER_PICK_STATE_PATH = ROOT / "state" / "renderer_layer_pick_state.json"
CURSOR_GEODESY_STATE_PATH = ROOT / "state" / "renderer_cursor_geodesy_state.json"
CURSOR_GEODESY_ACK_PATH = ROOT / "state" / "renderer_cursor_geodesy_ack.json"
TIMELINE_STATE_PATH = ROOT / "state" / "renderer_timeline_state.json"
TIMELINE_ACK_PATH = ROOT / "state" / "renderer_timeline_ack.json"
TIMELINE_EXPORT_DIR = ROOT / "state" / "timeline_exports"
TIMELINE_EXPORT_MANIFEST_PATH = TIMELINE_EXPORT_DIR / "timeline_animation_manifest.json"
TIMELINE_EXPORT_GIF_PATH = TIMELINE_EXPORT_DIR / "timeline_animation.gif"
TIMELINE_EXPORT_MP4_PATH = TIMELINE_EXPORT_DIR / "timeline_animation.mp4"


def profile_template_packet() -> dict[str, object]:
    templates = []
    for path in sorted(PROFILE_TEMPLATE_DIR.glob("*.json")):
        item: dict[str, object] = {
            "id": path.stem,
            "path": str(path.relative_to(ROOT)),
        }
        try:
            profile = json.loads(path.read_text(encoding="utf-8-sig"))
            if isinstance(profile, dict):
                item["name"] = profile.get("name", path.stem)
                item["description"] = profile.get("description", "")
                item["schema"] = profile.get("schema", "")
        except Exception as exc:
            item["error"] = str(exc)
        templates.append(item)
    return {
        "schema": "rrkal_displaytools.profile_templates.v1",
        "templates": templates,
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
                "renderer_entry_contract": {
                    "schema": "rrkal_displaytools.style_renderer_entry_contract.v1",
                    "style_profile": style_id,
                    "portable_command": ["py", "-3", "taichi_global_bathymetry.py", "--style-profile", style_id],
                    "profile_field": "renderer.style_profile",
                    "qt_surface": "Looks/templates style profile selector",
                    "template_supported": True,
                    "smoke_gate": "style_renderer_entry_contract",
                    "portable": True,
                },
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
        "renderer_entry_contract_schema": "rrkal_displaytools.style_renderer_entry_contract.v1",
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
    portable_route_commands = {
        str(route["id"]): " ".join(str(part) for part in route.get("portable_command", []))
        for route in routes
        if isinstance(route, dict)
    }
    summary_parameter_fields = [
        "status",
        "route_count",
        "route_ids",
        "required_routes",
        "missing_routes",
        "portable_route_commands",
    ]
    route_contracts = [
        {
            "schema": "rrkal_displaytools.style_renderer_entry_contract.v1",
            "style_profile": route["id"],
            "portable_command": route["portable_command"],
            "renderer_entrypoint": route["renderer_entrypoint"],
            "template_supported": route["template_supported"],
            "status": "ready",
        }
        for route in routes
    ]
    return {
        "schema": "rrkal_displaytools.style_profile_renderer_routes.v1",
        "source": source,
        "route_count": len(routes),
        "route_ids": route_ids,
        "routes": routes,
        "renderer_entry_contract_schema": "rrkal_displaytools.style_renderer_entry_contract.v1",
        "route_contracts": route_contracts,
        "required_route_contract_ids": required_routes,
        "required_routes": required_routes,
        "missing_routes": missing_routes,
        "portable_route_commands": portable_route_commands,
        "style_routes_summary_contract_schema": "rrkal_displaytools.style_routes_summary_contract.v1",
        "style_routes_summary_contract": {
            "schema": "rrkal_displaytools.style_routes_summary_contract.v1",
            "summary_format": "Style routes: status={status}; routes={route_count}; ids={route_ids}; required={required_routes}; missing={missing_routes}; parchment={parchment_command}; tactical={tactical_command}; boundary=RRKAL-owned data/cache",
            "summary_parameter_fields": summary_parameter_fields,
            "qt_copy_action": "copy_style_routes_summary",
            "portable": True,
        },
        "summary_parameter_fields": summary_parameter_fields,
        "status": "ready" if not missing_routes else "partial",
        "qt_surface": "Looks/templates style profile selector",
        "launch_packet_fields": ["style_profile_renderer_routes", "style_renderer_entries", "portable_command"],
        "renderer_capability_field": "style_profile_renderer_routes",
        "boundary": "Style profile routes are renderer launch affordances only; data discovery/cache governance stays RRKAL-owned.",
    }


def style_template_visual_preview_packet(
    style_entries: dict[str, object] | None,
    source: str,
) -> dict[str, object]:
    style_entries = style_entries if isinstance(style_entries, dict) else style_renderer_entries_packet(source)
    raw_entries = style_entries.get("entries") if isinstance(style_entries.get("entries"), list) else []
    swatches = {
        "scientific": ["#06204f", "#17a2b8", "#f5f7fa"],
        "nautical": ["#073b4c", "#06d6a0", "#ffd166"],
        "parchment": ["#3b2f2f", "#c2b280", "#8f2d1c"],
        "tactical": ["#073b12", "#39ff14", "#ff3131"],
    }
    preview_cards = []
    for entry in raw_entries:
        if not isinstance(entry, dict):
            continue
        style_id = str(entry.get("id", ""))
        if style_id not in swatches:
            continue
        thumbnail_path = f"state/style_previews/{style_id}.png"
        preview_cards.append(
            {
                "id": style_id,
                "label": str(entry.get("label", style_id.title())),
                "swatches": swatches[style_id],
                "thumbnail_path": thumbnail_path,
                "thumbnail_slot": True,
                "thumbnail_status": "slot_ready_runtime_artifact_optional",
                "thumbnail_source_contract": "rrkal_displaytools.renderer_output_artifact_contract.v1",
                "thumbnail_review_command": ["py", "-3", "taichi_global_bathymetry.py", "--style-profile", style_id, "--output", thumbnail_path],
                "inspect_action_id": "style_thumbnail_slots",
                "qt_card_icon_supported": True,
                "qt_card_icon_missing_label": "thumb: missing",
                "qt_surface": "Looks/templates visual preview cards",
                "selection_control": "style_combo",
                "renderer_route_field": "style_profile_renderer_routes.routes",
                "portable_command": ["py", "-3", "taichi_global_bathymetry.py", "--style-profile", style_id],
                "template_supported": bool(entry.get("template_supported", True)),
                "preview_state": "contract_preview",
                "renderer_apply_boundary": "Preview cards expose visual intent; renderer style application still follows style_profile_renderer_routes.",
            }
        )
    preview_ids = [str(card["id"]) for card in preview_cards]
    required_preview_ids = ["scientific", "nautical", "parchment", "tactical"]
    missing_preview_ids = [style_id for style_id in required_preview_ids if style_id not in preview_ids]
    return {
        "schema": "rrkal_displaytools.style_template_visual_preview.v1",
        "source": source,
        "status": "ready" if not missing_preview_ids else "partial",
        "qt_surface": "Looks/templates visual preview cards",
        "selection_control": "style_combo",
        "preview_count": len(preview_cards),
        "preview_ids": preview_ids,
        "preview_cards": preview_cards,
        "required_preview_ids": required_preview_ids,
        "missing_preview_ids": missing_preview_ids,
        "thumbnail_slots_enabled": True,
        "thumbnail_slot_count": len(preview_cards),
        "thumbnail_artifact_dir": "state/style_previews",
        "thumbnail_source_contract": "rrkal_displaytools.renderer_output_artifact_contract.v1",
        "thumbnail_optional_runtime_artifact": True,
        "thumbnail_missing_guidance": "Run the thumbnail_review_command for a style profile to populate its local PNG slot; thumbnail PNGs are runtime artifacts, not required for pre-commit smoke.",
        "thumbnail_batch_script": "scripts/render_style_previews.ps1",
        "thumbnail_batch_command": ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts/render_style_previews.ps1"],
        "thumbnail_batch_outputs": [f"state/style_previews/{style_id}.png" for style_id in required_preview_ids],
        "thumbnail_batch_validates": ["png_nonempty", "metadata_sidecar_schema", "style_profile_loop"],
        "qt_inspector_action_id": "style_thumbnail_slots",
        "qt_inspector_action_label": "Inspect: Style thumbs",
        "qt_inspector_handler": "show_style_thumbnail_slots",
        "qt_inspector_surface": "Actions / Inspect: Visual review",
        "thumbnail_icon_loading": "qt_loads_existing_png_as_card_icon",
        "qt_icon_loader": "refresh_style_template_preview_cards",
        "thumbnail_icon_size": [96, 54],
        "thumbnail_missing_card_text": "thumb: missing",
        "thumbnail_readiness_schema": "rrkal_displaytools.style_thumbnail_readiness.v1",
        "thumbnail_readiness_label_object": "styleThumbnailReadiness",
        "thumbnail_readiness_fields": ["ready_count", "missing_count", "missing_ids", "thumbnail_batch_command"],
        "thumbnail_readiness_summary_format": "Style thumbnails: ready={ready_count}/{required_count}; missing={missing_ids}; action={thumbnail_batch_script}",
        "thumbnail_readiness_copy_action": "copy_style_thumbnail_readiness_summary",
        "thumbnail_readiness_copy_label": "Copy style thumb status",
        "local_thumbnail_readiness_schema": "rrkal_displaytools.local_style_thumbnail_readiness.v1",
        "local_thumbnail_readiness_qt_action": "show_style_thumbnail_slots",
        "local_thumbnail_readiness_fields": ["slots", "ready_count", "missing_count", "missing_ids", "summary_text"],
        "qt_interaction": "clickable_preview_cards_select_style_profile",
        "card_click_action": "apply_style_template_preview_card",
        "qt_card_object_prefix": "styleTemplateCard_",
        "interaction_state": "implemented_in_qt",
        "launch_packet_fields": ["style_template_visual_preview", "style_renderer_entries", "style_profile_renderer_routes"],
        "renderer_capability_field": "style_template_visual_preview",
        "handoff_field": "style_template_visual_preview",
        "smoke_gate": "style_template_visual_preview",
        "boundary": "Style template preview is Qt/UIUX metadata only; RRKAL data discovery, downloads, imports and cache governance stay outside displaytools.",
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
        "launch_reviewer_summary_contract_schema": "rrkal_displaytools.launch_reviewer_summary_contract.v1",
        "launch_reviewer_summary_contract": {
            "label": "Launch reviewer",
            "summary_format": "Launch reviewer: readiness={readiness}; checks={ready_check_count}/{check_count}; command={portable_command_line}; fields={launch_packet_fields}; renderer={renderer_capability_field}",
            "qt_inspector_group": "replay_contracts",
            "qt_copy_action": "copy_launch_reviewer_summary",
            "component_contract_fields": [
                "profile_launch_readiness",
                "portable_command",
                "style_renderer_entries",
                "layer_operator_groups",
            ],
            "launch_packet_field": "profile_launch_readiness.launch_reviewer_summary_contract",
            "handoff_field": "profile_launch_readiness.launch_reviewer_summary_contract",
            "portable": True,
        },
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


def reviewer_packet_export_packet(source: str) -> dict[str, object]:
    return {
        "schema": "rrkal_displaytools.reviewer_packet_export.v1",
        "source": source,
        "status": "ready",
        "reviewer_packet_schema": "rrkal_displaytools.reviewer_packet.v1",
        "qt_action": "export_reviewer_packet_dialog",
        "qt_action_label": "Export reviewer packet",
        "default_output": "state/showcase/reviewer_packet.json",
        "included_summary_fields": [
            "clone_reviewer_summary",
            "launch_reviewer_summary",
            "research_interaction_summary",
            "visual_review_summary",
            "hydrology_lod_summary",
            "ocean_material_summary",
            "style_routes_summary",
            "module_boundary_summary",
        ],
        "included_packet_fields": [
            "launch_packet_snapshot",
            "cross_machine_clone_readiness",
            "profile_launch_readiness",
            "profile_ui_state_replay",
            "hydrology_lod_readiness",
            "hydrology_lod_runtime_evidence",
            "ocean_material_control_port",
            "style_profile_renderer_routes",
            "module_boundary_registry",
            "layer_render_plan_performance",
            "reviewer_packet_export",
        ],
        "launch_packet_field": "reviewer_packet_export",
        "renderer_capability_field": "reviewer_packet_export",
        "handoff_field": "reviewer_packet_export",
        "portable": True,
    }


def profile_ui_state_replay_packet(source: str) -> dict[str, object]:
    saved_groups = [
        "renderer_config",
        "selected_layer",
        "layer_stack_ui",
        "layer_operation_feedback",
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
        ("launch_summary", "Copy launch summary"),
        ("timeline", "Inspect: Timeline"),
        ("ocean_port", "Inspect: Ocean port"),
        ("hydro_lod", "Inspect: Hydro LOD"),
        ("style_routes", "Inspect: Style routes"),
        ("module_seams", "Inspect: Module seams"),
        ("clone_ready", "Inspect: Clone ready"),
        ("clone_summary", "Copy clone summary"),
        ("layer_matrix", "Inspect: Layer matrix"),
        ("layer_runtime", "Inspect: Layer runtime"),
        ("layer_pick", "Inspect: Layer pick"),
        ("selection_state", "Inspect: Selection state"),
        ("layer_ops", "Inspect: Layer ops"),
        ("canvas_state", "Inspect: Canvas state"),
        ("pin_pick", "Inspect: Pin pick"),
        ("cursor_geo", "Inspect: Cursor geo"),
        ("boundary_json", "Inspect: Boundary JSON"),
        ("research_summary", "Copy research summary"),
        ("visual_readiness", "Inspect: Visual readiness"),
        ("renderer_thumbnail", "Inspect: Renderer thumbnail"),
        ("live_preview", "Inspect: Live preview"),
    ]
    qt_inspector_groups = [
        {"id": "replay_contracts", "label": "Replay/contracts", "action_ids": ["profile_replay", "launch_summary", "timeline", "clone_ready", "clone_summary", "module_seams"]},
        {"id": "renderer_ports", "label": "Renderer ports", "action_ids": ["hydro_lod", "ocean_port", "style_routes", "layer_matrix", "layer_runtime"]},
        {"id": "research_interaction", "label": "Research interaction", "action_ids": ["layer_pick", "selection_state", "layer_ops", "canvas_state", "pin_pick", "cursor_geo", "boundary_json", "research_summary"]},
        {"id": "visual_review", "label": "Visual review", "action_ids": ["visual_readiness", "renderer_thumbnail", "live_preview"]},
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


def visual_review_readiness_packet(source: str) -> dict[str, object]:
    visual_actions = ["visual_readiness", "renderer_thumbnail", "live_preview"]
    return {
        "schema": "rrkal_displaytools.visual_review_readiness.v1",
        "source": source,
        "status": "ready",
        "visual_review_actions": visual_actions,
        "qt_inspector_action_id": "visual_readiness",
        "qt_inspector_action_label": "Inspect: Visual readiness",
        "renderer_thumbnail_ready": True,
        "live_preview_ready": True,
        "frame_status_schema": "rrkal_displaytools.visual_review_frame_status.v1",
        "frame_status": {
            "renderer_thumbnail": {
                "status": "inspect_action_available",
                "artifact_state": "runtime_dependent",
                "inspect_action_id": "renderer_thumbnail",
                "missing_frame_hint": "Use Inspect: Renderer thumbnail to check whether a cached preview frame exists.",
            },
            "live_preview": {
                "status": "inspect_action_available",
                "artifact_state": "runtime_dependent",
                "inspect_action_id": "live_preview",
                "missing_frame_hint": "Use Inspect: Live preview to check whether the renderer frame-capture route is active.",
            },
        },
        "inspector_view_schema": "rrkal_displaytools.visual_review_inspector_view.v1",
        "inspector_view": {
            "title": "Visual readiness",
            "surface": "Qt Visual review inspector",
            "status_badges": ["renderer_thumbnail: inspect_action_available", "live_preview: inspect_action_available"],
            "rows": [
                {
                    "label": "Renderer thumbnail",
                    "action_id": "renderer_thumbnail",
                    "status": "inspect_action_available",
                    "artifact_state": "runtime_dependent",
                    "hint": "Cached preview frame is checked by Inspect: Renderer thumbnail.",
                },
                {
                    "label": "Live preview",
                    "action_id": "live_preview",
                    "status": "inspect_action_available",
                    "artifact_state": "runtime_dependent",
                    "hint": "Renderer frame-capture routing is checked by Inspect: Live preview.",
                },
            ],
            "copyable": True,
        },
        "qt_command_contract_schema": "rrkal_displaytools.visual_review_qt_command_contract.v1",
        "qt_command_contract": {
            "action_id": "visual_readiness",
            "menu_label": "Inspect: Visual readiness",
            "payload_field": "visual_review_readiness.inspector_view",
            "dispatch_status": "contract_ready",
            "implementation_status": "wired_in_qt_panel",
            "module_boundary": "rrkal_displaytools_qt_panel.py owns current Qt dispatch; future split target is qt_ui/main_window.py.",
            "fallback_user_message": "Visual readiness metadata remains available through handoff, launch packet and renderer capabilities for non-Qt review.",
        },
        "copy_summary_contract_schema": "rrkal_displaytools.visual_review_copy_summary_contract.v1",
        "copy_summary_contract": {
            "label": "Visual readiness",
            "summary_format": "Visual readiness: thumbnail={renderer_thumbnail_status} ({renderer_thumbnail_artifact_path}); live={live_preview_status} ({live_preview_artifact_path})",
            "qt_label_object": "visualReviewReadiness",
            "qt_copy_action": "copy_visual_review_readiness_summary",
            "launch_packet_field": "visual_review_readiness.copy_summary_contract",
            "handoff_field": "visual_review_readiness.copy_summary_contract",
            "portable": True,
        },
        "recommended_sequence": ["Inspect: Visual readiness", "Inspect: Renderer thumbnail", "Inspect: Live preview"],
        "missing_frame_guidance": [
            "Run Inspect: Renderer thumbnail to confirm cached preview-frame availability.",
            "Run Inspect: Live preview to confirm renderer frame-capture routing.",
            "If both views are unavailable, launch Qt with a known style profile before filing a renderer issue.",
        ],
        "summary_text": "Visual review readiness confirms the Qt Inspect path for renderer thumbnail and live preview before deeper renderer debugging.",
        "boundary": "Readiness metadata only; it does not render a new frame, download data, or mutate renderer/cache state.",
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
    summary_parameter_fields = [
        "readiness",
        "live_hydrology_layer_count",
        "hydrology_layer_count",
        "stable_renderer_targets",
        "lod_hook_status",
        "runtime_state_file",
        "ack_file",
        "pick_state_file",
    ]
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
        "hydrology_lod_summary_contract_schema": "rrkal_displaytools.hydrology_lod_summary_contract.v1",
        "hydrology_lod_summary_contract": {
            "schema": "rrkal_displaytools.hydrology_lod_summary_contract.v1",
            "summary_format": "Hydrology/LOD: readiness={readiness}; live={live_hydrology_layer_count}/{hydrology_layer_count}; targets={stable_renderer_targets}; lod={lod_hook_status}; runtime={runtime_status}; hits={hydrology_runtime_hit_count}; pick={pick_matches_hydrology}; state={runtime_state_file}; ack={ack_file}; pick_state={pick_state_file}",
            "summary_parameter_fields": summary_parameter_fields,
            "qt_copy_action": "copy_hydrology_lod_summary",
            "portable": True,
        },
        "renderer_apply_contract_schema": "rrkal_displaytools.hydrology_lod_renderer_apply_contract.v1",
        "renderer_apply_contract": {
            "schema": "rrkal_displaytools.hydrology_lod_renderer_apply_contract.v1",
            "status": "runtime_bridge_ready" if live_layer_count == len(hydrology_layers) else "partial",
            "runtime_state_schema": "rrkal_displaytools.layer_runtime_state.v1",
            "runtime_ack_schema": "rrkal_displaytools.renderer_layer_runtime_ack.v1",
            "runtime_state_file": "state/renderer_layer_runtime_state.json",
            "runtime_ack_file": "state/renderer_layer_runtime_ack.json",
            "qt_layer_keys": list(hydrology_keys),
            "renderer_targets": ["lakes", "rivers"],
            "apply_targets": hydrology_layers,
            "required_state_fields": [
                "layers.<key>.visible",
                "layers.<key>.opacity",
                "layers.<key>.blend_mode",
                "selected_layer",
            ],
            "required_ack_fields": [
                "changed_layers",
                "changed_opacity_layers",
                "changed_blend_layers",
                "selected_renderer_layer",
                "skipped_locked_layers",
            ],
            "lod_source_modes": ["lod", "static"],
            "renderer_entry_points": ["load_layer_runtime_state", "apply_layer_runtime_state"],
            "qt_surface": "Inspect: Hydro LOD",
            "smoke_gate": "hydrology_lod_renderer_apply_contract",
            "portable": True,
            "boundary": "Renderer apply consumes existing hydrology layer runtime state and ack files only; authoritative hydrology datasets and cache governance remain RRKAL-owned.",
        },
        "deferred_context_layers": ["bathymetry_layer", "coastline_layer"],
        "summary_parameter_fields": summary_parameter_fields,
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
    apply_contract = readiness.get("renderer_apply_contract") if isinstance(readiness.get("renderer_apply_contract"), dict) else {}
    return {
        "schema": "rrkal_displaytools.hydrology_lod_runtime_evidence.v1",
        "source": source,
        "readiness_schema": readiness.get("schema"),
        "readiness": readiness.get("readiness", "unknown"),
        "renderer_apply_contract_schema": apply_contract.get("schema", "rrkal_displaytools.hydrology_lod_renderer_apply_contract.v1"),
        "renderer_apply_contract_status": apply_contract.get("status", "unknown"),
        "runtime_state_file": apply_contract.get("runtime_state_file", "state/renderer_layer_runtime_state.json"),
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
        "summary_runtime_fields": ["status", "runtime_ack_available", "pick_state_available", "hydrology_runtime_hit_count", "pick_matches_hydrology"],
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
    renderer_flags = ["--ocean-wave-strength", "--ocean-roughness", "--ocean-foam"]
    taichi_uniforms = ["ocean_enabled", "wave_strength", "roughness", "foam", "time_seconds"]
    summary_parameter_fields = [
        "enabled",
        "wave_strength",
        "roughness",
        "foam",
        "renderer_apply_status",
        "sea_state_status",
        "sea_state_scalar_sample_schema",
        "renderer_flags",
    ]
    return {
        "schema": "rrkal_displaytools.ocean_material_control_port.v1",
        "source": source,
        "enabled": bool(material.get("enabled", True)),
        "material_controls": controls,
        "renderer_flags": renderer_flags,
        "taichi_uniforms": taichi_uniforms,
        "ocean_material_summary_contract_schema": "rrkal_displaytools.ocean_material_summary_contract.v1",
        "ocean_material_summary_contract": {
            "schema": "rrkal_displaytools.ocean_material_summary_contract.v1",
            "summary_format": "Ocean material: enabled={enabled}; wave={wave_strength}; roughness={roughness}; foam={foam}; apply={renderer_apply_status}; sea_state={sea_state_status}; sample={sea_state_scalar_sample_schema}; flags={renderer_flags}; governance=RRKAL-owned provider/cache",
            "summary_parameter_fields": summary_parameter_fields,
            "qt_copy_action": "copy_ocean_material_summary",
            "portable": True,
        },
        "summary_parameter_fields": summary_parameter_fields,
        "qt_control_panel_schema": "rrkal_displaytools.taichi_ocean_3d_control_panel.v1",
        "qt_control_panel": {
            "schema": "rrkal_displaytools.taichi_ocean_3d_control_panel.v1",
            "surface": "Properties dock + Layers dock quick strip + Taichi 3D Ocean controls dialog",
            "dock_object": "propertiesDock",
            "label_object": "taichiOcean3DControlPanel",
            "button_object": "taichiOcean3DControlButton",
            "control_board_surface": "Layers dock quick strip",
            "control_board_label_object": "ocean3DControlBoardStrip",
            "control_board_button_object": "ocean3DControlBoardButton",
            "control_board_default_visible": True,
            "control_board_status": "wired_default_visible",
            "control_board_audit_schema": "rrkal_displaytools.taichi_ocean_3d_control_board_audit.v1",
            "control_board_audit_field": "control_board_audit",
            "qt_dialog_action": "open_taichi_ocean_3d_controls",
            "button_label": "Taichi 3D Ocean controls",
            "fields": ["wave_strength", "roughness", "foam"],
            "writes_profile_field": "profile.ocean_material",
            "writes_renderer_flags": renderer_flags,
            "render_pipeline_followup": "post_decoupling_precompute_layer_render_plan_then_single_render_pass",
            "performance_note": "Ocean scalars are UI/apply controls here; layer batching and render-plan precompute are scheduled after module decoupling.",
        },
        "control_board_audit_schema": "rrkal_displaytools.taichi_ocean_3d_control_board_audit.v1",
        "control_board_audit": {
            "schema": "rrkal_displaytools.taichi_ocean_3d_control_board_audit.v1",
            "status": "wired_default_visible",
            "default_visible": True,
            "primary_surface": "Layers dock quick strip",
            "secondary_surfaces": ["Properties dock", "Renderer ports action group"],
            "label_object": "ocean3DControlBoardStrip",
            "button_object": "ocean3DControlBoardButton",
            "dialog_action": "open_taichi_ocean_3d_controls",
            "performance_followup": "post_decoupling_precompute_layer_render_plan_then_single_render_pass",
            "user_issue": "Ocean 3D controls must be visible from the control board, not only the Properties dock.",
        },
        "renderer_apply_contract_schema": "rrkal_displaytools.ocean_material_renderer_apply_contract.v1",
        "renderer_apply_contract": {
            "schema": "rrkal_displaytools.ocean_material_renderer_apply_contract.v1",
            "status": "startup_cli_and_timeline_ready",
            "input_sources": [
                "profile.ocean_material",
                "sea_state_port.scalar_sample_contract",
                "timeline_ocean_material_interpolation",
            ],
            "renderer_flags": renderer_flags,
            "taichi_uniforms": taichi_uniforms,
            "applied_fields": list(controls),
            "runtime_paths": [
                "launch_packet.portable_command",
                "timeline_ocean_material_interpolation.interpolated",
            ],
            "ack_contracts": [
                "launch_packet.ocean_material_control_port",
                "renderer_timeline_ack.timeline_ocean_material_interpolation",
            ],
            "pending": ["live_sea_state_stream_file", "provider_grid_sampling"],
            "portable": True,
            "boundary": "Renderer applies normalized scalar material fields from profile/launch/timeline contracts; provider IO and cache governance stay outside displaytools.",
        },
        "sea_state_port": {
            "status": "manual_scalar_port_ready",
            "normalized_fields": ["wave_strength", "roughness", "foam", "timestamp"],
            "provider_ports": ["manual", "file", "url", "noaa_ww3", "hycom", "copernicus", "local_grid"],
            "renderer_consumes": ["wave_strength", "roughness", "foam"],
            "scalar_sample_contract_schema": "rrkal_displaytools.sea_state_scalar_sample.v1",
            "scalar_sample_contract": {
                "schema": "rrkal_displaytools.sea_state_scalar_sample.v1",
                "status": "normalized_scalar_contract_ready",
                "required_fields": ["wave_strength", "roughness", "foam", "timestamp"],
                "optional_fields": ["source_id", "valid_time_utc", "confidence", "provider_ref", "grid_cell"],
                "value_ranges": {
                    "wave_strength": [0.0, 1.0],
                    "roughness": [0.02, 1.0],
                    "foam": [0.0, 1.0],
                },
                "displaytools_role": "consume_normalized_scalars_only",
                "rrkal_role": "provider discovery, download/import and cache governance",
                "portable": True,
            },
        },
        "qt_surface": "Properties dock ocean material controls + Layers dock Ocean 3D quick controls + Taichi 3D Ocean controls dialog",
        "launch_packet_fields": ["ocean_material_control_port", "profile.ocean_material", "command"],
        "renderer_capability_field": "ocean_material_control_port",
        "boundary": "Displaytools passes scalar ocean material controls and sea-state handoff fields only; RRKAL/provider modules own discovery, download, import and cache governance.",
    }


def visual_feature_closure_matrix_packet(source: str) -> dict[str, object]:
    features = [
        {"id": "qt_first_ui", "status": "ready", "evidence_fields": ["profile_launch_readiness_ui", "profile_ui_state_replay"]},
        {"id": "layer_control", "status": "ready", "evidence_fields": ["layer_operator_groups", "layer_selection_tool", "layer_capability_matrix"]},
        {"id": "profile_launch", "status": "ready", "evidence_fields": ["profile_launch_readiness", "reviewer_packet_export"]},
        {"id": "renderer_capability_discovery", "status": "ready", "evidence_fields": ["renderer_capabilities", "style_renderer_entries"]},
        {"id": "cross_machine_clone", "status": "ready", "evidence_fields": ["cross_machine_clone_readiness", "module_boundary_registry"]},
        {"id": "pin_overlay", "status": "ready", "evidence_fields": ["pin_overlay", "cursor_geodesy_readout"]},
        {"id": "cursor_geodesy", "status": "ready", "evidence_fields": ["cursor_geodesy_readout", "renderer_cursor_geodesy_ack_file"]},
        {"id": "boundary_emphasis", "status": "ready", "evidence_fields": ["boundary_emphasis_control", "boundary_highlight"]},
        {"id": "hydrology_lod", "status": "ready", "evidence_fields": ["hydrology_lod_readiness", "hydrology_lod_runtime_evidence"]},
        {"id": "ocean_material", "status": "ready", "evidence_fields": ["ocean_material_control_port", "timeline_ocean_material_interpolation"]},
        {"id": "style_profiles", "status": "ready", "evidence_fields": ["style_renderer_entries", "style_profile_renderer_routes"]},
        {"id": "module_boundaries", "status": "ready", "evidence_fields": ["module_boundary_registry.decoupling_boundary_contract"]},
        {"id": "renderer_performance", "status": "queued", "evidence_fields": ["layer_render_plan_performance"]},
    ]
    feature_ids = [feature["id"] for feature in features]
    ready_feature_count = sum(1 for feature in features if feature.get("status") == "ready")
    return {
        "schema": "rrkal_displaytools.visual_feature_closure_matrix.v1",
        "source": source,
        "status": "ready_with_queued_performance_followup",
        "feature_count": len(features),
        "ready_feature_count": ready_feature_count,
        "feature_ids": feature_ids,
        "features": features,
        "required_feature_ids": feature_ids,
        "launch_packet_fields": ["visual_feature_closure_matrix", "visual_review_readiness", "closed_loop_status"],
        "renderer_capability_field": "visual_feature_closure_matrix",
        "handoff_field": "visual_feature_closure_matrix",
        "smoke_gate": "visual_feature_closure_matrix",
        "boundary": "Closure matrix summarizes smoke-gated contract evidence; runtime artifacts still require renderer execution before claiming fresh visual output.",
    }


def renderer_output_artifact_contract_packet(source: str) -> dict[str, object]:
    return {
        "schema": "rrkal_displaytools.renderer_output_artifact_contract.v1",
        "source": source,
        "status": "contract_ready",
        "image_output_control": "--output",
        "headless_controls": ["--headless", "--once"],
        "preview_frame_controls": ["--preview-frame-file", "--preview-frame-interval"],
        "quick_render_smoke_script": "scripts/render_quick_smoke.ps1",
        "quick_render_smoke_outputs": [
            "state/showcase/quick_smoke.png",
            "state/showcase/quick_smoke.png.metadata.json",
            "state/showcase/quick_smoke_preview_frame.png",
        ],
        "quick_render_smoke_validates": [
            "output_png_exists",
            "preview_frame_png_nonempty",
            "metadata_sidecar_schema",
        ],
        "metadata_sidecar_schema": "rrkal_displaytools.renderer_output_metadata.v1",
        "metadata_sidecar_suffix": ".metadata.json",
        "metadata_fields": [
            "style_profile",
            "topography_source",
            "data_mode",
            "visible_layers",
            "layer_visible",
            "layer_opacity",
            "layer_blend_mode",
            "layer_render_plan",
            "selected_layer_semantic_target",
            "last_layer_pick_result",
            "boundary_highlight",
            "closed_loop_status",
            "rrkal_data_manifest_ref",
            "rrkal_boundary",
        ],
        "rrkal_data_manifest_ref_field": "rrkal_data_manifest_ref",
        "rrkal_data_manifest_ref_boundary": "reference_only; displaytools records the value, RRKAL owns manifest validation/ingest/cache governance",
        "runtime_artifact_scope": "runtime_local_state_not_committed",
        "launch_packet_fields": ["renderer_output_artifact_contract", "visual_review_readiness", "canvas_preview"],
        "renderer_capability_field": "renderer_output_artifact_contract",
        "handoff_field": "renderer_output_artifact_contract",
        "smoke_gate": "renderer_output_artifact_contract",
        "boundary": "Pre-commit smoke verifies the contract only; optional render_quick_smoke.ps1 verifies actual PNG/metadata artifacts when renderer runtime is needed.",
    }


def layer_render_plan_cache_diagnostics_packet(
    metadata_payload: dict[str, object] | None,
    source: str,
) -> dict[str, object]:
    metadata = metadata_payload if isinstance(metadata_payload, dict) else {}
    plan = metadata.get("layer_render_plan") if isinstance(metadata.get("layer_render_plan"), dict) else {}
    runtime_snapshot = plan.get("runtime_snapshot") if isinstance(plan.get("runtime_snapshot"), dict) else {}
    available = bool(plan)
    return {
        "schema": "rrkal_displaytools.layer_render_plan_cache_diagnostics.v1",
        "source": source,
        "status": "available" if available else "unavailable",
        "metadata_sidecar_schema": metadata.get("schema"),
        "metadata_sidecar_field": "layer_render_plan",
        "compiled_plan_schema": plan.get("schema") if available else "rrkal_displaytools.compiled_layer_render_plan.v1",
        "runtime_snapshot_schema": runtime_snapshot.get("schema") if runtime_snapshot else "rrkal_displaytools.layer_render_plan_runtime_snapshot.v1",
        "cache_status": plan.get("cache_status", "unavailable"),
        "cache_reuse_decision": plan.get("cache_reuse_decision", plan.get("cache_status", "unavailable")),
        "cache_invalidation_reason_schema": plan.get("cache_invalidation_reason_schema", "rrkal_displaytools.layer_render_plan_cache_invalidation_reasons.v1"),
        "cache_invalidation_reasons": plan.get("cache_invalidation_reasons") if isinstance(plan.get("cache_invalidation_reasons"), list) else (["metadata_sidecar_missing"] if not available else []),
        "cache_invalidation_scope_schema": plan.get("cache_invalidation_scope_schema", "rrkal_displaytools.layer_render_plan_cache_invalidation_scope.v1"),
        "cache_invalidation_scope": plan.get("cache_invalidation_scope") if isinstance(plan.get("cache_invalidation_scope"), list) else ([] if available else [{"scope": "metadata", "id": "metadata_sidecar_missing", "dirty_flag": None}]),
        "batch_decision_schema": plan.get("batch_decision_schema", "rrkal_displaytools.layer_render_plan_batch_decisions.v1"),
        "batch_decisions": plan.get("batch_decisions") if isinstance(plan.get("batch_decisions"), list) else [],
        "batch_decision_count": plan.get("batch_decision_count", 0),
        "apply_path_schema": plan.get("apply_path_schema", "rrkal_displaytools.layer_render_plan_apply_path.v1"),
        "apply_path": plan.get("apply_path") if isinstance(plan.get("apply_path"), list) else [],
        "apply_path_count": plan.get("apply_path_count", 0),
        "execution_summary_schema": plan.get("execution_summary_schema", "rrkal_displaytools.layer_render_plan_execution_summary.v1"),
        "execution_summary": plan.get("execution_summary") if isinstance(plan.get("execution_summary"), dict) else {},
        "execution_phases_schema": plan.get("execution_phases_schema", "rrkal_displaytools.layer_render_plan_execution_phases.v1"),
        "execution_phases": plan.get("execution_phases") if isinstance(plan.get("execution_phases"), list) else [],
        "execution_phase_count": plan.get("execution_phase_count", 0),
        "phase_timing_contract_schema": plan.get("phase_timing_contract_schema", "rrkal_displaytools.layer_render_plan_phase_timing_contract.v1"),
        "phase_timing_contract": plan.get("phase_timing_contract") if isinstance(plan.get("phase_timing_contract"), dict) else {},
        "phase_timing_runtime_schema": plan.get("phase_timing_runtime_schema", "rrkal_displaytools.layer_render_plan_phase_timing_runtime.v1"),
        "phase_timing_runtime": plan.get("phase_timing_runtime") if isinstance(plan.get("phase_timing_runtime"), dict) else {},
        "bottleneck_recommendation_schema": plan.get("bottleneck_recommendation_schema", "rrkal_displaytools.layer_render_plan_bottleneck_recommendation.v1"),
        "bottleneck_recommendation": plan.get("bottleneck_recommendation") if isinstance(plan.get("bottleneck_recommendation"), dict) else {},
        "compose_queue_schema": plan.get("compose_queue_schema", "rrkal_displaytools.layer_render_plan_compose_queue.v1"),
        "compose_queue_count": plan.get("compose_queue_count", 0),
        "compose_queue_skipped_count": plan.get("compose_queue_skipped_count", 0),
        "compose_queue_packet": plan.get("compose_queue_packet") if isinstance(plan.get("compose_queue_packet"), dict) else {},
        "compose_runs_schema": plan.get("compose_runs_schema", "rrkal_displaytools.layer_render_plan_compose_runs.v1"),
        "compose_runs": plan.get("compose_runs") if isinstance(plan.get("compose_runs"), list) else [],
        "compose_run_count": plan.get("compose_run_count", 0),
        "compose_merge_candidate_run_count": plan.get("compose_merge_candidate_run_count", 0),
        "compose_run_parity_contract_schema": plan.get("compose_run_parity_contract_schema", "rrkal_displaytools.layer_render_plan_compose_run_parity_contract.v1"),
        "compose_run_parity_contract": plan.get("compose_run_parity_contract") if isinstance(plan.get("compose_run_parity_contract"), dict) else {},
        "cache_key_available": bool(plan.get("cache_key")),
        "reuse_policy": plan.get("reuse_policy", "reuse_when_cache_key_matches_previous_compiled_plan") if available else "unavailable",
        "reuse_boundary": plan.get("reuse_boundary", "valid_until_dirty_flags_or_camera_change") if available else "unavailable",
        "cache_status_values": ["compiled", "reused", "unavailable"],
        "composition_step_count": plan.get("composition_step_count", runtime_snapshot.get("composition_step_count")),
        "visible_layer_count": runtime_snapshot.get("visible_layer_count"),
        "dirty_flags": plan.get("dirty_flags") if isinstance(plan.get("dirty_flags"), dict) else runtime_snapshot.get("dirty_flags", {}),
        "single_pass_ready": bool(plan.get("single_pass_ready", False)),
        "runtime_optimization_applied": bool(plan.get("runtime_optimization_applied", False)),
        "qt_inspector_action": "show_layer_render_plan_performance",
        "boundary": "Diagnostics reads renderer metadata sidecar cache evidence; unavailable means no runtime frame metadata has been produced yet.",
    }


def layer_render_plan_performance_packet(
    source: str,
    layer_capability_matrix: dict[str, object] | None = None,
    module_boundaries: dict[str, object] | None = None,
) -> dict[str, object]:
    matrix = layer_capability_matrix if isinstance(layer_capability_matrix, dict) else {}
    modules = module_boundaries if isinstance(module_boundaries, dict) else {}
    live_counts = matrix.get("live_counts") if isinstance(matrix.get("live_counts"), dict) else {}
    stage_order = [
        "collect_qt_layer_state",
        "resolve_renderer_targets_and_aliases",
        "compile_visibility_opacity_blend_pick_state",
        "freeze_static_geometry_batches",
        "apply_dirty_flags",
        "submit_single_taichi_render_pass",
    ]
    return {
        "schema": "rrkal_displaytools.layer_render_plan_performance.v1",
        "source": source,
        "status": "queued_after_module_decoupling",
        "post_decoupling_priority": 1,
        "optimization_target": "precompute_layer_state_then_single_render_pass",
        "current_runtime_claim": "contract_and_schedule_only",
        "runtime_optimization_applied": False,
        "runtime_snapshot_schema": "rrkal_displaytools.layer_render_plan_runtime_snapshot.v1",
        "runtime_snapshot_helper": "HybridRenderController.layer_render_plan_runtime_snapshot",
        "composition_steps_helper": "HybridRenderController.layer_render_plan_composition_steps",
        "composition_apply_helper": "HybridRenderController.apply_layer_render_plan_composition",
        "compiled_plan_schema": "rrkal_displaytools.compiled_layer_render_plan.v1",
        "compiled_plan_helper": "HybridRenderController.compile_layer_render_plan",
        "compiled_plan_cache_key_helper": "HybridRenderController.layer_render_plan_cache_key",
        "compiled_plan_cache_status_field": "cache_status",
        "compiled_plan_invalidation_reason_schema": "rrkal_displaytools.layer_render_plan_cache_invalidation_reasons.v1",
        "compiled_plan_invalidation_helper": "HybridRenderController.layer_render_plan_cache_invalidation_reasons",
        "compiled_plan_invalidation_reasons_field": "cache_invalidation_reasons",
        "compiled_plan_invalidation_scope_schema": "rrkal_displaytools.layer_render_plan_cache_invalidation_scope.v1",
        "compiled_plan_invalidation_scope_helper": "HybridRenderController.layer_render_plan_cache_invalidation_scope",
        "compiled_plan_invalidation_scope_field": "cache_invalidation_scope",
        "compiled_plan_batch_decision_schema": "rrkal_displaytools.layer_render_plan_batch_decisions.v1",
        "compiled_plan_batch_decision_helper": "HybridRenderController.layer_render_plan_batch_decisions",
        "compiled_plan_batch_decision_field": "batch_decisions",
        "compiled_plan_apply_path_schema": "rrkal_displaytools.layer_render_plan_apply_path.v1",
        "compiled_plan_apply_path_helper": "HybridRenderController.layer_render_plan_apply_path",
        "compiled_plan_apply_path_field": "apply_path",
        "compiled_plan_execution_summary_schema": "rrkal_displaytools.layer_render_plan_execution_summary.v1",
        "compiled_plan_execution_summary_helper": "HybridRenderController.layer_render_plan_execution_summary",
        "compiled_plan_execution_summary_field": "execution_summary",
        "compiled_plan_execution_phases_schema": "rrkal_displaytools.layer_render_plan_execution_phases.v1",
        "compiled_plan_execution_phases_helper": "HybridRenderController.layer_render_plan_execution_phases",
        "compiled_plan_execution_phases_field": "execution_phases",
        "compiled_plan_phase_timing_contract_schema": "rrkal_displaytools.layer_render_plan_phase_timing_contract.v1",
        "compiled_plan_phase_timing_contract_helper": "HybridRenderController.layer_render_plan_phase_timing_contract",
        "compiled_plan_phase_timing_contract_field": "phase_timing_contract",
        "compiled_plan_phase_timing_runtime_schema": "rrkal_displaytools.layer_render_plan_phase_timing_runtime.v1",
        "compiled_plan_phase_timing_runtime_helper": "HybridRenderController.layer_render_plan_phase_timing_runtime_packet",
        "compiled_plan_phase_timing_runtime_field": "phase_timing_runtime",
        "compiled_plan_bottleneck_recommendation_schema": "rrkal_displaytools.layer_render_plan_bottleneck_recommendation.v1",
        "compiled_plan_bottleneck_recommendation_helper": "HybridRenderController.layer_render_plan_bottleneck_recommendation",
        "compiled_plan_bottleneck_recommendation_field": "bottleneck_recommendation",
        "compiled_plan_compose_queue_schema": "rrkal_displaytools.layer_render_plan_compose_queue.v1",
        "compiled_plan_compose_queue_helper": "HybridRenderController.layer_render_plan_compose_queue",
        "compiled_plan_compose_queue_field": "compose_queue",
        "compiled_plan_compose_queue_skip_reasons": ["hidden_layer", "missing_overlay", "transparent_overlay"],
        "compiled_plan_compose_runs_schema": "rrkal_displaytools.layer_render_plan_compose_runs.v1",
        "compiled_plan_compose_runs_helper": "HybridRenderController.layer_render_plan_compose_runs",
            "compiled_plan_compose_runs_field": "compose_runs",
            "compiled_plan_compose_run_parity_contract_schema": "rrkal_displaytools.layer_render_plan_compose_run_parity_contract.v1",
            "compiled_plan_compose_run_parity_contract_helper": "HybridRenderController.layer_render_plan_compose_run_parity_contract",
            "compiled_plan_compose_run_parity_contract_field": "compose_run_parity_contract",
            "compose_run_parity_smoke_schema": "rrkal_displaytools.render_compose_parity_smoke.v1",
            "compose_run_parity_smoke_script": "scripts\\render_compose_parity_smoke.ps1",
            "compose_run_parity_smoke_manifest": "state/render_compose_parity_smoke_manifest.json",
            "compose_run_parity_smoke_precommit_required": False,
            "compose_run_parity_smoke_precommit_command": "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\\render_compose_parity_smoke.ps1 -ContractOnly",
            "compose_run_parity_smoke_validates": ["png_dimensions_match", "max_abs_diff", "changed_pixel_count"],
            "compose_run_parity_smoke_pass_fields": ["passed", "max_abs_diff", "changed_pixel_count", "diff_status"],
            "compose_run_parity_artifact_workflow_schema": "rrkal_displaytools.compose_run_parity_artifact_workflow.v1",
            "compose_run_parity_artifact_workflow": {
                "schema": "rrkal_displaytools.compose_run_parity_artifact_workflow.v1",
                "status": "producer_ready_runtime_merge_disabled",
                "renderer_arg": "--compose-parity-artifact-dir",
                "artifact_dir": "state/compose_parity",
                "baseline_artifact": "state/compose_parity/baseline_sequential_frame_rgba.png",
                "candidate_artifact": "state/compose_parity/merged_candidate_frame_rgba.png",
                "metadata_artifact": "state/compose_parity/renderer_output_metadata.json",
                "diff_script": "scripts\\render_compose_parity_smoke.ps1",
                "precommit_command": "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\\render_compose_parity_smoke.ps1 -ContractOnly",
                "manual_diff_command": "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\\render_compose_parity_smoke.ps1",
                "producer_command": "py -3 taichi_global_bathymetry.py --once --output state/compose_parity/renderer_frame.png --compose-parity-artifact-dir state/compose_parity",
                "producer_status": "baseline_and_candidate_artifact_producer_available_runtime_merge_disabled",
                "candidate_schema": "rrkal_displaytools.compose_run_parity_candidate.v1",
                "artifacts_schema": "rrkal_displaytools.compose_run_parity_artifacts.v1",
                "next_step": "Run the manual diff command on generated artifacts and require zero-diff evidence before enabling runtime merge.",
                "boundary": "Workflow metadata only; runtime artifacts stay under state/ and are not committed.",
            },
            "phase_timing_unit": "milliseconds",
            "compiled_plan_reuse_decision_field": "cache_reuse_decision",
            "compiled_plan_reuse_policy": "reuse_when_cache_key_matches_previous_compiled_plan",
        "compiled_plan_reuse_status_values": ["compiled", "reused"],
        "compiled_plan_reuse_boundary_field": "reuse_boundary",
        "compiled_plan_reuse_boundary": "valid_until_dirty_flags_or_camera_change",
        "compiled_plan_reuse_runtime_fields": ["cache_key", "cache_status", "reuse_policy", "reuse_boundary", "frame_index", "dirty_flags"],
        "cache_diagnostics_schema": "rrkal_displaytools.layer_render_plan_cache_diagnostics.v1",
        "cache_diagnostics_qt_action": "show_layer_render_plan_performance",
        "cache_diagnostics_metadata_source": "renderer_output_metadata.layer_render_plan",
        "cache_diagnostics_control_board_schema": "rrkal_displaytools.layer_render_plan_cache_control_board.v1",
        "cache_diagnostics_control_board_label_object": "renderPlanCacheDiagnosticsStrip",
        "cache_diagnostics_control_board_button_object": "renderPlanCacheDiagnosticsButton",
        "cache_diagnostics_control_board_default_visible": True,
        "metadata_sidecar_field": "layer_render_plan",
        "runtime_snapshot_wired": True,
        "deferred_until": "module_decoupling_boundary_contract_is_stable",
        "module_boundary_schema": modules.get("schema"),
        "stage_order": stage_order,
        "precompute_inputs": [
            "profile.layers",
            "layer_stack_ui",
            "layer_capability_matrix",
            "boundary_highlight",
            "pins",
            "ocean_material_control_port",
            "timeline_state",
        ],
        "dirty_flags": [
            "camera",
            "style_profile",
            "ocean_material",
            "layer_visibility",
            "layer_opacity",
            "layer_blend",
            "timeline_step",
            "data_manifest_ref",
        ],
        "batching_targets": [
            "hydrology_polylines",
            "boundary_and_maritime_lines",
            "pin_markers",
            "traffic_points",
            "scale_grid_contours",
        ],
        "single_pass_outputs": ["globe_frame", "overlay_composite", "metadata_sidecar"],
        "known_risk": "Independent layer render paths can make Taichi interaction feel sluggish when overlays grow.",
        "performance_strategy": "Compile renderer-ready layer state once per dirty change, then let Taichi consume a unified render plan in one render/composite path.",
        "live_control_counts": live_counts,
        "requires_modules": [
            "contracts/launch_packets.py",
            "render_core/taichi_globe.py",
            "overlays/vector_layers.py",
            "diagnostics/handoff.py",
        ],
        "launch_packet_fields": ["layer_render_plan_performance", "layer_capability_matrix", "module_boundary_registry"],
        "renderer_capability_field": "layer_render_plan_performance",
        "handoff_field": "layer_render_plan_performance",
        "smoke_gate": "layer_render_plan_performance",
        "boundary": "This records the next renderer performance closure after module decoupling; it does not claim a measured FPS or rewritten Taichi render loop yet.",
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
    extraction_order = [
        "contracts/launch_packets.py",
        "qt_ui/main_window.py",
        "render_core/taichi_globe.py",
        "render_core/ocean_material.py",
        "style_profiles.py",
        "overlays/vector_layers.py",
        "diagnostics/handoff.py",
    ]
    stable_contracts_before_move = [
        "launch_packet",
        "renderer_capabilities",
        "handoff_inspection",
        "smoke_gates",
    ]
    displaytools_owns = [
        "renderer launch/profile contracts",
        "Qt-first operator UI",
        "Taichi visualization/render apply paths",
        "visual diagnostics and handoff summaries",
    ]
    rrkal_owns = [
        "dataset discovery",
        "provider download/import",
        "manifest/cache governance",
        "authoritative source registry",
    ]
    summary_parameter_fields = [
        "module_count",
        "target_modules",
        "extraction_order",
        "stable_contracts_before_move",
        "tk_primary_ui_allowed",
        "rrkal_owns",
    ]
    return {
        "schema": "rrkal_displaytools.module_boundary_registry.v1",
        "source": source,
        "module_count": len(boundaries),
        "target_modules": [boundary["module"] for boundary in boundaries],
        "boundaries": boundaries,
        "qt_first": True,
        "tk_primary_ui_allowed": False,
        "decoupling_boundary_contract_schema": "rrkal_displaytools.module_decoupling_boundary_contract.v1",
        "decoupling_boundary_contract": {
            "schema": "rrkal_displaytools.module_decoupling_boundary_contract.v1",
            "status": "ready",
            "extraction_order": extraction_order,
            "stable_contracts_before_move": stable_contracts_before_move,
            "forbidden_cross_imports": [
                {"module": "contracts/launch_packets.py", "must_not_import": ["PyQt6", "taichi", "datashader", "data_sources/*"]},
                {"module": "qt_ui/main_window.py", "must_not_import": ["data_sources/*", "downloaders/*", "cache_governance/*"]},
                {"module": "render_core/*", "must_not_import": ["PyQt6 widgets", "RRKAL provider discovery"]},
                {"module": "data_sources/*", "must_not_live_in_repo": True},
            ],
            "displaytools_owns": displaytools_owns,
            "rrkal_owns": rrkal_owns,
            "qt_first": True,
            "tk_primary_ui_allowed": False,
            "smoke_gate": "module_decoupling_boundary_contract",
            "portable": True,
        },
        "module_boundary_summary_contract_schema": "rrkal_displaytools.module_boundary_summary_contract.v1",
        "module_boundary_summary_contract": {
            "schema": "rrkal_displaytools.module_boundary_summary_contract.v1",
            "summary_format": "Module seams: modules={module_count}; first={first_extraction}; render={render_core}; tk_primary={tk_primary_ui_allowed}; stable={stable_contracts_before_move}; rrkal={rrkal_owns}; boundary=RRKAL-owned data/cache",
            "summary_parameter_fields": summary_parameter_fields,
            "qt_copy_action": "copy_module_boundary_summary",
            "portable": True,
        },
        "summary_parameter_fields": summary_parameter_fields,
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
    clone_command = "git clone https://github.com/Kagamihara-Ruruka/RRKAL_displaytools.git"
    default_branch = "main"
    repo_visibility = "public"
    required_commands = [
        "scripts/setup_windows.ps1",
        "scripts/smoke.ps1",
        "scripts/run_qt_panel.ps1",
        "scripts/inspect_handoff.ps1",
    ]
    launcher_options = ["-SmokeFirst", "-HandoffFirst", "-Template", "-Profile"]
    handoff_first_command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_qt_panel.ps1 -HandoffFirst"
    first_run_smoke_command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/smoke.ps1"
    first_run_handoff_command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/inspect_handoff.ps1"
    first_run_order = [
        clone_command,
        "cd RRKAL_displaytools",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup_windows.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/smoke.ps1",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/inspect_handoff.ps1",
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
        "clone_command": clone_command,
        "default_branch": default_branch,
        "repo_visibility": repo_visibility,
        "setup_doc": "docs/SETUP_WINDOWS.zh-TW.md",
        "qt_surface": "Layers dock cross-machine readiness label",
        "qt_visible_fields": ["status", "required_command_count", "setup_doc", "default_branch", "repo_visibility", "first_run_smoke_command", "first_run_handoff_command"],
        "required_commands": required_commands,
        "launcher_options": launcher_options,
        "handoff_first_command": handoff_first_command,
        "first_run_smoke_command": first_run_smoke_command,
        "first_run_handoff_command": first_run_handoff_command,
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
        "clone_reviewer_summary_contract_schema": "rrkal_displaytools.clone_reviewer_summary_contract.v1",
        "clone_reviewer_summary_contract": {
            "label": "Clone reviewer",
            "summary_format": "Clone reviewer: status={status}; repo={repo_url}; clone={clone_command}; branch={default_branch}; visibility={repo_visibility}; setup={setup_doc}; profile={profile_launch_readiness}; qt_first={qt_first}; smoke_required={smoke_required_before_push}; first_smoke={first_run_smoke_command}; first_handoff={first_run_handoff_command}; handoff_first={handoff_first_command}",
            "qt_inspector_group": "replay_contracts",
            "qt_copy_action": "copy_clone_reviewer_summary",
            "component_contract_fields": [
                "cross_machine_clone_readiness",
                "profile_launch_readiness",
                "profile_ui_state_replay",
                "module_boundary_registry",
            ],
            "launch_packet_field": "cross_machine_clone_readiness.clone_reviewer_summary_contract",
            "handoff_field": "cross_machine_clone_readiness.clone_reviewer_summary_contract",
            "portable": True,
        },
        "boundary": "Cross-machine readiness covers clone/setup/smoke/run handoff only; data discovery, download, import and cache governance remain RRKAL-owned.",
    }


if "--list-templates" in sys.argv[1:]:
    print(json.dumps(profile_template_packet(), ensure_ascii=False, indent=2))
    raise SystemExit(0)

try:
    from PyQt6 import QtCore, QtGui, QtWidgets
except ImportError as exc:
    raise SystemExit(
        "PyQt6 is required for the Qt control panel. Install project dependencies with: "
        "py -3 -m pip install -r requirements.txt"
    ) from exc

RENDERER = ROOT / "taichi_global_bathymetry.py"
PROFILE_DIR = ROOT / "state" / "ui_profiles"
SHOWCASE_DIR = ROOT / "state" / "showcase"
RENDERER_PREVIEW_FRAME_PATH = ROOT / "state" / "renderer_preview_frame.png"
RENDERER_PREVIEW_FRAME_INTERVAL_S = 0.75
WORKSPACE_STATE_PATH = ROOT / "state" / "ui_workspace.json"

STYLE_PROFILES = ("scientific", "nautical", "parchment", "tactical")
UI_BACKENDS = ("qt", "vispy")
TOPO_SOURCES = ("gebco", "synthetic")
DATA_MODES = ("static", "realtime", "timeseries")

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


def layer_runtime_badge_style(status_id: str) -> str:
    _label, foreground, background = LAYER_RUNTIME_BADGE_STYLES.get(status_id, LAYER_RUNTIME_BADGE_STYLES["no_ack"])
    return (
        f"QLabel#layerRuntimeBadge {{ color: {foreground}; background: {background}; "
        "border: 1px solid rgba(20, 30, 40, 0.18); border-radius: 7px; "
        "padding: 2px 6px; font-weight: 600; }}"
    )


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


def layer_runtime_evidence_packet(payload: dict[str, object] | None) -> dict[str, object]:
    if not isinstance(payload, dict):
        return {
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
            "boundary": "No renderer ack has been observed yet; capability matrix is static only.",
        }
    changed_layers = [str(layer) for layer in payload.get("changed_layers", []) if layer is not None] if isinstance(payload.get("changed_layers"), list) else []
    changed_opacity_layers = [str(layer) for layer in payload.get("changed_opacity_layers", []) if layer is not None] if isinstance(payload.get("changed_opacity_layers"), list) else []
    changed_blend_layers = [str(layer) for layer in payload.get("changed_blend_layers", []) if layer is not None] if isinstance(payload.get("changed_blend_layers"), list) else []
    skipped_locked_layers = [str(layer) for layer in payload.get("skipped_locked_layers", []) if layer is not None] if isinstance(payload.get("skipped_locked_layers"), list) else []
    return {
        "schema": "rrkal_displaytools.layer_runtime_evidence.v1",
        "available": True,
        "ack_schema": str(payload.get("schema") or "rrkal_displaytools.renderer_layer_runtime_ack.v1"),
        "event": payload.get("event"),
        "updated_at_utc": payload.get("updated_at_utc"),
        "frame_index": payload.get("frame_index"),
        "error": payload.get("error"),
        "selected_renderer_layer": payload.get("selected_renderer_layer"),
        "changed_layers": changed_layers,
        "changed_opacity_layers": changed_opacity_layers,
        "changed_blend_layers": changed_blend_layers,
        "skipped_locked_layers": skipped_locked_layers,
        "counts": {
            "changed_visibility": len(changed_layers),
            "changed_opacity": len(changed_opacity_layers),
            "changed_blend": len(changed_blend_layers),
            "skipped_locked": len(skipped_locked_layers),
        },
        "boundary": "Renderer ack evidence for the most recent layer runtime bridge apply.",
    }


def layer_runtime_evidence_summary_packet(evidence: dict[str, object] | None) -> dict[str, object]:
    evidence = evidence if isinstance(evidence, dict) else layer_runtime_evidence_packet(None)
    counts = evidence.get("counts")
    counts = counts if isinstance(counts, dict) else {}
    changed_visibility = int(counts.get("changed_visibility", 0) or 0)
    changed_opacity = int(counts.get("changed_opacity", 0) or 0)
    changed_blend = int(counts.get("changed_blend", 0) or 0)
    skipped_locked = int(counts.get("skipped_locked", 0) or 0)
    if evidence.get("available") is not True:
        status = "unavailable"
        text = "No renderer ack observed yet."
    elif evidence.get("error"):
        status = "error"
        text = f"Renderer ack error: {evidence.get('error')}"
    elif skipped_locked > 0:
        status = "skipped_locked"
        text = f"Renderer skipped {skipped_locked} locked layer updates."
    elif changed_visibility or changed_opacity or changed_blend:
        status = "changed"
        text = (
            f"Renderer applied changes: visibility={changed_visibility}, "
            f"opacity={changed_opacity}, blend={changed_blend}."
        )
    else:
        status = "ok"
        text = "Renderer ack observed; no recent layer mutations."
    return {
        "schema": "rrkal_displaytools.layer_runtime_evidence_summary.v1",
        "available": bool(evidence.get("available")),
        "status": status,
        "text": text,
        "counts": {
            "changed_visibility": changed_visibility,
            "changed_opacity": changed_opacity,
            "changed_blend": changed_blend,
            "skipped_locked": skipped_locked,
        },
        "selected_renderer_layer": evidence.get("selected_renderer_layer"),
        "event": evidence.get("event"),
        "error": evidence.get("error"),
        "frame_index": evidence.get("frame_index"),
        "updated_at_utc": evidence.get("updated_at_utc"),
        "boundary": "Human-readable summary of the most recent renderer layer runtime ack evidence.",
    }


def layer_runtime_badge_summary_packet(
    layers: list[dict[str, object]],
    selected_layer: str | None,
    source: str,
) -> dict[str, object]:
    status_counts = {status_id: 0 for status_id in LAYER_RUNTIME_BADGE_STYLES}
    layers_with_runtime_notes: list[dict[str, object]] = []
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
            layers_with_runtime_notes.append(
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
        "noted_layers": layers_with_runtime_notes,
        "noted_layer_count": len(layers_with_runtime_notes),
        "copyable_provenance": True,
        "boundary": "Copyable research provenance summary of Qt layer Runtime badges; badges summarize renderer ack evidence and do not mutate renderer state.",
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
    pick_state: dict[str, object] | None,
    source: str,
) -> dict[str, object]:
    warning_list = warning_list if isinstance(warning_list, dict) else {}
    pick_state = pick_state if isinstance(pick_state, dict) else {}
    pick_result = pick_state.get("pick_result")
    pick_result = pick_result if isinstance(pick_result, dict) else {}
    pick_event = str(pick_result.get("event") or pick_state.get("event") or "waiting")
    pick_renderer_layer = pick_state.get("selected_renderer_layer") or pick_result.get("renderer_layer")
    hit_value = pick_result.get("hit")
    feature_identity = pick_result.get("feature_identity")
    feature_identity = feature_identity if isinstance(feature_identity, dict) else {}
    feature_properties = pick_result.get("feature_properties") or pick_result.get("properties")
    feature_properties = feature_properties if isinstance(feature_properties, dict) else {}
    feature_label = pick_result.get("feature_label") or pick_result.get("label") or pick_result.get("name")
    if not feature_identity:
        for key in ("name", "NAME", "NAME_EN", "SOVEREIGNT", "ADMIN", "ISO_A3", "MRGID", "GEONAME"):
            value = feature_properties.get(key) or pick_result.get(key)
            if value not in (None, ""):
                feature_identity[key.lower()] = value
    pick_available = bool(pick_state)
    target_matches = bool(renderer_target and pick_renderer_layer == renderer_target)
    if not pick_available:
        summary_text = f"No renderer pick context yet; warning severity={warning_list.get('severity', 'unknown')}."
    else:
        hit_text = "hit" if hit_value is True else "no-hit" if hit_value is False else "unknown-hit"
        feature_text = f", feature={feature_label}" if isinstance(feature_label, str) and feature_label.strip() else ""
        summary_text = f"pick={pick_event}, target={pick_renderer_layer or '-'}, {hit_text}{feature_text}."
    return {
        "schema": "rrkal_displaytools.layer_runtime_interaction_context.v1",
        "source": source,
        "selected_layer": selected_layer,
        "renderer_target": renderer_target,
        "warning_severity": warning_list.get("severity"),
        "warning_count": warning_list.get("warning_count"),
        "pick_context_available": pick_available,
        "pick_event": pick_event,
        "pick_renderer_layer": pick_renderer_layer,
        "pick_target_matches_selected_layer": target_matches,
        "pick_hit": hit_value,
        "feature_label": feature_label,
        "feature_identity": feature_identity,
        "summary_text": summary_text,
        "copyable_provenance": True,
        "boundary": "Connects runtime warnings with selected-layer renderer picking and source-property feature identity when renderer pick evidence is available.",
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



def layer_operation_feedback_packet(
    source: str,
    selected_layer: str | None = None,
    active_summary: str | None = None,
    last_operation: str | None = None,
    operator_groups: dict[str, object] | None = None,
    undo_state: dict[str, object] | None = None,
) -> dict[str, object]:
    operator_groups = operator_groups if isinstance(operator_groups, dict) else {}
    undo_state = undo_state if isinstance(undo_state, dict) else {}
    active_summary_text = active_summary or "Layer operation summary unavailable in static export."
    last_operation_text = last_operation or "Last layer operation: unavailable in static export"
    return {
        "schema": "rrkal_displaytools.layer_operation_feedback.v1",
        "source": source,
        "selected_layer": selected_layer,
        "active_layer_operation_summary": active_summary_text,
        "last_layer_operation": last_operation_text,
        "operator_group_summary": operator_groups.get("summary_text"),
        "operator_group_count": int(operator_groups.get("group_count") or 0),
        "operator_group_complete_count": int(operator_groups.get("complete_group_count") or 0),
        "undo_depth": int(undo_state.get("depth") or 0),
        "qt_surface": "Layers dock Layer operation summary / Last layer operation labels",
        "profile_state_fields": ["selected_layer", "layer_stack_ui"],
        "launch_packet_fields": [
            "layer_operation_feedback",
            "active_layer_operation_summary",
            "last_layer_operation",
            "layer_operator_groups",
            "layer_undo",
        ],
        "renderer_capability_field": "layer_operation_feedback",
        "profile_ui_state_replay_action_id": "layer_ops",
        "summary_text": "Active layer operation summary and last operation status are reviewable without reconstructing the Qt UI.",
        "copyable_provenance": True,
        "boundary": "Qt layer operation feedback/replay metadata only; renderer state and RRKAL data governance are not mutated.",
    }


def layer_control_feedback_strip_packet(
    source: str,
    selected_layer: str | None = None,
    layer_stack: dict[str, dict[str, object]] | None = None,
    active_summary: str | None = None,
    last_operation: str | None = None,
) -> dict[str, object]:
    layer_stack = layer_stack if isinstance(layer_stack, dict) else {}
    selected_state = layer_stack.get(selected_layer) if isinstance(selected_layer, str) else None
    selected_state = selected_state if isinstance(selected_state, dict) else {}
    visible = selected_state.get("visible")
    locked = selected_state.get("locked")
    opacity = selected_state.get("opacity")
    blend_mode = selected_state.get("blend_mode") or "unknown"
    renderer_sync = selected_state.get("renderer_sync") or "unknown"
    visible_text = "on" if visible is True else "off" if visible is False else "unknown"
    locked_text = "locked" if locked is True else "editable" if locked is False else "unknown"
    opacity_text = f"{opacity}%" if isinstance(opacity, int) else "unknown"
    summary_text = (
        f"Layer control strip: selected={selected_layer or 'none'}; "
        f"visible={visible_text}; lock={locked_text}; opacity={opacity_text}; "
        f"blend={blend_mode}; renderer={renderer_sync}"
    )
    return {
        "schema": "rrkal_displaytools.layer_control_feedback_strip.v1",
        "source": source,
        "status": "ready" if selected_layer else "no_selection",
        "selected_layer": selected_layer,
        "selected_layer_state_available": bool(selected_state),
        "visible": visible,
        "locked": locked,
        "opacity": opacity,
        "blend_mode": blend_mode,
        "renderer_sync": renderer_sync,
        "active_layer_operation_summary": active_summary,
        "last_layer_operation": last_operation,
        "summary_text": summary_text,
        "qt_surface": "Layers dock layerControlFeedbackStrip label",
        "qt_label_object": "layerControlFeedbackStrip",
        "visible_fields": ["selected_layer", "visible", "locked", "opacity", "blend_mode", "renderer_sync"],
        "launch_packet_fields": ["layer_control_feedback_strip", "layer_stack_ui", "layer_operation_feedback"],
        "renderer_capability_field": "layer_control_feedback_strip",
        "handoff_field": "layer_control_feedback_strip",
        "smoke_gate": "layer_control_feedback_strip",
        "boundary": "Qt layer control feedback only; renderer runtime state and RRKAL data governance are not mutated by this strip.",
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
        "selection_summary_contract_schema": "rrkal_displaytools.layer_selection_summary_contract.v1",
        "selection_summary_contract": {
            "label": "Layer selection",
            "summary_format": "Layer selection: selected={selected_layer} ({selected_layer_label}); pick_state={pick_state_file}; brush_mask={brush_mask_scope}",
            "qt_label_object": "selectedLayer",
            "qt_copy_action": "copy_layer_selection_summary",
            "launch_packet_field": "layer_selection_tool.selection_summary_contract",
            "handoff_field": "layer_selection_tool.selection_summary_contract",
            "portable": True,
        },
        "copyable_provenance": True,
        "boundary": "Selection tool state bridges Qt active-layer UX and renderer pick context only; brush/mask editing and RRKAL data governance stay out of scope.",
    }


def layer_selection_affordance_packet(
    source: str,
    selected_layer: str | None = None,
    layer_stack: dict[str, dict[str, object]] | None = None,
) -> dict[str, object]:
    layer_stack = layer_stack if isinstance(layer_stack, dict) else {}
    selected_state = layer_stack.get(selected_layer) if isinstance(selected_layer, str) else None
    selected_state = selected_state if isinstance(selected_state, dict) else {}
    visible = selected_state.get("visible")
    locked = selected_state.get("locked")
    renderer_sync = selected_state.get("renderer_sync") or "unknown"
    summary_text = (
        f"Selection affordance: active={selected_layer or 'none'}; "
        f"row_highlight=selected property; visible={visible}; locked={locked}; renderer={renderer_sync}"
    )
    return {
        "schema": "rrkal_displaytools.layer_selection_affordance.v1",
        "source": source,
        "status": "ready",
        "selected_layer": selected_layer,
        "selected_layer_state_available": bool(selected_state),
        "qt_surface": "Layers dock selected row highlight / layerSelectionAffordance label",
        "qt_label_object": "layerSelectionAffordance",
        "row_object_name": "layerRow",
        "selected_row_property": "selected",
        "selected_row_stylesheet_selector": 'QWidget#layerRow[selected="true"]',
        "focus_aids": [
            "selected row highlight",
            "selectedLayer label",
            "layerControlFeedbackStrip",
            "Reveal selected action",
        ],
        "visible": visible,
        "locked": locked,
        "renderer_sync": renderer_sync,
        "summary_text": summary_text,
        "launch_packet_fields": ["layer_selection_affordance", "layer_selection_tool", "layer_control_feedback_strip", "layer_stack_ui"],
        "renderer_capability_field": "layer_selection_affordance",
        "handoff_field": "layer_selection_affordance",
        "smoke_gate": "layer_selection_affordance",
        "boundary": "Qt selection affordance only; it clarifies active layer targeting without mutating renderer state or RRKAL data governance.",
    }


def layer_hover_affordance_packet(
    source: str,
    hovered_layer: str | None = None,
    layer_stack: dict[str, dict[str, object]] | None = None,
) -> dict[str, object]:
    layer_stack = layer_stack if isinstance(layer_stack, dict) else {}
    hovered_state = layer_stack.get(hovered_layer) if isinstance(hovered_layer, str) else None
    hovered_state = hovered_state if isinstance(hovered_state, dict) else {}
    renderer_target = globals().get("LAYER_RUNTIME_ID_ALIASES", {}).get(hovered_layer, hovered_layer) if hovered_layer else None
    visible = hovered_state.get("visible")
    locked = hovered_state.get("locked")
    renderer_sync = hovered_state.get("renderer_sync") or "unknown"
    summary_text = (
        f"Layer hover: target={hovered_layer or 'none'}; renderer={renderer_target or 'none'}; "
        f"visible={visible}; locked={locked}; sync={renderer_sync}"
    )
    return {
        "schema": "rrkal_displaytools.layer_hover_affordance.v1",
        "source": source,
        "status": "ready",
        "hovered_layer": hovered_layer,
        "hovered_layer_state_available": bool(hovered_state),
        "renderer_target": renderer_target,
        "visible": visible,
        "locked": locked,
        "renderer_sync": renderer_sync,
        "summary_text": summary_text,
        "qt_surface": "Layers dock layerHoverAffordance label / row hover event filter",
        "qt_label_object": "layerHoverAffordance",
        "row_object_name": "layerRow",
        "event_filter": "layer_hover_event_targets",
        "hover_events": ["QEvent.Enter", "QEvent.Leave"],
        "launch_packet_fields": ["layer_hover_affordance", "layer_stack_ui", "layer_selection_affordance"],
        "renderer_capability_field": "layer_hover_affordance",
        "handoff_field": "layer_hover_affordance",
        "smoke_gate": "layer_hover_affordance",
        "boundary": "Qt hover feedback only; it does not change selected layer, renderer state, or RRKAL data governance.",
    }


def layer_lock_affordance_packet(
    source: str,
    layer_stack: dict[str, dict[str, object]] | None = None,
) -> dict[str, object]:
    layer_stack = layer_stack if isinstance(layer_stack, dict) else {}
    locked_layers = [
        key
        for key, state in layer_stack.items()
        if isinstance(key, str) and isinstance(state, dict) and state.get("locked") is True
    ]
    summary_text = (
        f"Layer locks: locked={len(locked_layers)}; row_property=locked; "
        "visibility_control=disabled_when_locked"
    )
    return {
        "schema": "rrkal_displaytools.layer_lock_affordance.v1",
        "source": source,
        "status": "ready",
        "locked_layer_count": len(locked_layers),
        "locked_layers": locked_layers,
        "summary_text": summary_text,
        "qt_surface": "Layers dock locked row tint / disabled visibility checkbox",
        "row_object_name": "layerRow",
        "locked_row_property": "locked",
        "locked_row_stylesheet_selector": 'QWidget#layerRow[locked="true"]',
        "visibility_control_disabled_when_locked": True,
        "disabled_controls_when_locked": ["visibility_checkbox", "opacity_slider", "blend_combo"],
        "qt_checkbox_tooltip": "Lock is honored by renderer runtime sync for visibility, opacity, and blend updates.",
        "launch_packet_fields": ["layer_lock_affordance", "layer_stack_ui", "layer_control_feedback_strip"],
        "renderer_capability_field": "layer_lock_affordance",
        "handoff_field": "layer_lock_affordance",
        "smoke_gate": "layer_lock_affordance",
        "boundary": "Qt lock affordance only; it visualizes lock state and disabled visibility controls without mutating RRKAL data governance.",
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
        "research_summary_contract_schema": "rrkal_displaytools.research_interaction_summary_contract.v1",
        "research_summary_contract": {
            "label": "Research interaction",
            "summary_format": "Research interaction: {layer_selection} | {pin_overlay} | {cursor_geodesy} | {boundary_emphasis}",
            "qt_inspector_group": "research_interaction",
            "qt_copy_action": "copy_research_interaction_summary",
            "component_contract_fields": [
                "layer_selection_tool.selection_summary_contract",
                "pin_overlay.pin_summary_contract",
                "cursor_geodesy_readout.cursor_summary_contract",
                "boundary_emphasis_control.boundary_summary_contract",
            ],
            "launch_packet_field": "layer_research_workflow.research_summary_contract",
            "handoff_field": "layer_research_workflow.research_summary_contract",
            "portable": True,
        },
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
    summary_parameter_fields = ["color_rgb", "contrast", "opacity", "gamma", "breathing_enabled", "breathing_period_s"]
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
        "row_double_click_layer_keys": list(BOUNDARY_EMPHASIS_TARGET_BY_LAYER.keys()),
        "renderer_hook_status": "wired_via_boundary_highlight_mask",
        "renderer_bridge_contract": BOUNDARY_HIGHLIGHT_SCHEMA,
        "boundary_summary_contract_schema": "rrkal_displaytools.boundary_emphasis_summary_contract.v1",
        "boundary_summary_contract": {
            "label": "Boundary emphasis",
            "summary_format": "Boundary emphasis: target={target_mode}->{target_layer_key}; align={target_alignment_label}; color={color_rgb}; contrast={contrast}; opacity={opacity}; gamma={gamma}; breathing={breathing_enabled}@{breathing_period_s}s; bridge={renderer_bridge_contract}",
            "summary_parameter_fields": summary_parameter_fields,
            "qt_label_object": "boundary_emphasis_label",
            "qt_copy_action": "copy_boundary_emphasis_summary",
            "launch_packet_field": "boundary_emphasis_control.boundary_summary_contract",
            "handoff_field": "boundary_emphasis_control.boundary_summary_contract",
            "portable": True,
        },
        "summary_parameter_fields": summary_parameter_fields,
        "renderer_controls_mapped": ["target_layers", "color_rgb", "contrast", "alpha", "gamma", "breathing"],
        "dialog_feedback": ["rgb_swatch", "live_numeric_readout", "renderer_bridge_summary"],
        "value_preview_fields": ["target_mode", "target_alignment", "color_rgb", "contrast", "opacity", "gamma", "breathing_period_s"],
        "pending_renderer_refinements": ["authoritative_polygon_identity", "open_line_area_inference", "full_polygon_fill_mask"],
        "control_count": len(controls),
        "controls": controls,
        "boundary": "UI profile state is mapped to the existing boundary highlight renderer bridge; governed geospatial ownership remains outside displaytools.",
    }


def cursor_geodesy_readout_packet(
    latitude: float | None,
    longitude: float | None,
    source: str,
) -> dict[str, object]:
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
        "cursor_summary_contract_schema": "rrkal_displaytools.cursor_geodesy_summary_contract.v1",
        "cursor_summary_contract": {
            "label": "Cursor geodesy",
            "summary_format": "Cursor geodesy: source={source}; state={hit_state}; lat={latitude}; lon={longitude}; state_file={renderer_raycast_state_file}; ack_file={renderer_raycast_ack_file}; method={renderer_raycast_method}",
            "qt_label_object": "canvasMeta",
            "qt_copy_action": "copy_cursor_geodesy_summary",
            "launch_packet_field": "cursor_geodesy_readout.cursor_summary_contract",
            "handoff_field": "cursor_geodesy_readout.cursor_summary_contract",
            "portable": True,
        },
        "researcher_note": "Canvas preview gives immediate lon/lat feedback; renderer mouse events now write a smoke-gated state/ack bridge for Taichi globe raycast results.",
    }


def layer_capability_matrix_packet(
    source: str,
    selected_layer: str | None = None,
    runtime_ack: dict[str, object] | None = None,
    pick_state: dict[str, object] | None = None,
    authoritative_identity_source_ref: str | None = None,
) -> dict[str, object]:
    runtime_evidence = layer_runtime_evidence_packet(runtime_ack)
    layers = [layer_capability_packet(key, label) for key, label in LAYER_LABELS]
    for layer in layers:
        renderer_target = str(layer.get("renderer_target") or "")
        runtime_status = []
        if runtime_evidence["available"] is False:
            runtime_status.append("no_ack")
        elif runtime_evidence.get("error"):
            runtime_status.append("ack_error")
        else:
            if renderer_target in runtime_evidence["changed_layers"]:
                runtime_status.append("visibility_changed")
            if renderer_target in runtime_evidence["changed_opacity_layers"]:
                runtime_status.append("opacity_changed")
            if renderer_target in runtime_evidence["changed_blend_layers"]:
                runtime_status.append("blend_changed")
            if renderer_target in runtime_evidence["skipped_locked_layers"]:
                runtime_status.append("skipped_locked")
            if runtime_evidence.get("selected_renderer_layer") == renderer_target:
                runtime_status.append("selected_target")
            if not runtime_status:
                runtime_status.append("no_recent_change")
        layer["runtime_evidence_available"] = bool(runtime_evidence["available"])
        layer["runtime_status"] = runtime_status
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
        pick_state,
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
        "boundary": "Documents Qt layer controls and renderer live support; unsupported controls remain visible UI state but are explicitly marked planned.",
    }

BOUNDARY_HIGHLIGHT_SCHEMA = "rrkal_displaytools.boundary_highlight_mask.v1"
BOUNDARY_IDENTITY_STATUS_SCHEMA = "rrkal_displaytools.boundary_identity_status.v1"
BOUNDARY_HIGHLIGHT_LAYER_KEYS = (
    "border_layer",
    "territorial_sea_layer",
    "eez_layer",
    "high_seas_layer",
)
BOUNDARY_EMPHASIS_TARGET_BY_LAYER = {
    "border_layer": "country_boundary",
    "territorial_sea_layer": "territorial_sea",
    "eez_layer": "exclusive_economic_zone",
    "high_seas_layer": "maritime_boundary",
}
BOUNDARY_EMPHASIS_LAYER_BY_TARGET = {value: key for key, value in BOUNDARY_EMPHASIS_TARGET_BY_LAYER.items()}
BLEND_MODES = ("Normal", "Screen", "Multiply", "Overlay", "Soft Light")
TOOL_MODES = (
    ("move", "Move", "檢視 / 平移"),
    ("select", "Select", "選取圖層 / active layer target"),
    ("pin", "Pin", "科研標記 / observation marker"),
)
PIN_TYPES = ("Observation", "Sample Site", "Anomaly", "Reference", "Event")
PIN_LABEL_MODES = (
    ("auto", "Auto", "Place visible labels until collision budget is exhausted."),
    ("selected", "Selected only", "Only label the selected Pin."),
    ("priority", "Priority", "Only label selected Pin and Pins above the priority threshold."),
    ("hidden", "Hidden", "Hide all Pin labels; markers remain visible."),
)


def _coerce_int(value: object, default: int, minimum: int, maximum: int) -> int:
    if isinstance(value, bool):
        return default
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, number))


def default_boundary_identity_status() -> dict[str, object]:
    return {
        "schema": BOUNDARY_IDENTITY_STATUS_SCHEMA,
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


def default_boundary_highlight_state() -> dict[str, object]:
    return {
        "schema": BOUNDARY_HIGHLIGHT_SCHEMA,
        "enabled": True,
        "trigger": "hover",
        "target_layers": list(BOUNDARY_HIGHLIGHT_LAYER_KEYS),
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
        "identity_status": default_boundary_identity_status(),
        "renderer_sync": "renderer_line_fill_identity_status_handoff",
    }


def normalized_boundary_highlight_state(payload: object) -> dict[str, object]:
    state = default_boundary_highlight_state()
    if not isinstance(payload, dict):
        return state
    state["enabled"] = bool(payload.get("enabled", state["enabled"]))
    trigger = payload.get("trigger")
    if isinstance(trigger, str) and trigger in {"hover", "selected", "hover_or_selected"}:
        state["trigger"] = trigger
    targets = payload.get("target_layers")
    if isinstance(targets, list):
        target_layers = [str(layer) for layer in targets if str(layer) in BOUNDARY_HIGHLIGHT_LAYER_KEYS]
        if target_layers:
            state["target_layers"] = target_layers
    color_rgb = payload.get("color_rgb")
    if isinstance(color_rgb, list) and len(color_rgb) >= 3:
        state["color_rgb"] = [_coerce_int(color_rgb[index], 255, 0, 255) for index in range(3)]
    state["contrast"] = _coerce_int(payload.get("contrast"), int(state["contrast"]), 0, 100)
    state["alpha"] = _coerce_int(payload.get("alpha"), int(state["alpha"]), 0, 100)
    state["gamma"] = _coerce_int(payload.get("gamma"), int(state["gamma"]), 25, 300)
    state["feather"] = _coerce_int(payload.get("feather"), int(state["feather"]), 0, 100)
    breathing = payload.get("breathing")
    if isinstance(breathing, dict):
        state["breathing"] = {
            "enabled": bool(breathing.get("enabled", True)),
            "speed": _coerce_int(breathing.get("speed"), 42, 0, 100),
            "amplitude": _coerce_int(breathing.get("amplitude"), 16, 0, 100),
        }
    renderer_sync = payload.get("renderer_sync")
    if isinstance(renderer_sync, str):
        state["renderer_sync"] = renderer_sync
    return state


class DisplayToolsQtPanel(QtWidgets.QMainWindow):
    def __init__(self, initial_profile: Path | None = None) -> None:
        super().__init__()
        self.setWindowTitle("RRKAL DisplayTools Qt 控制面板")
        self.resize(1120, 780)
        self.process: subprocess.Popen[bytes] | None = None
        self.checks: dict[str, QtWidgets.QCheckBox] = {}
        self.layer_locks: dict[str, QtWidgets.QCheckBox] = {}
        self.layer_opacity: dict[str, QtWidgets.QSlider] = {}
        self.layer_blends: dict[str, QtWidgets.QComboBox] = {}
        self.layer_rows: dict[str, QtWidgets.QWidget] = {}
        self.layer_hover_event_targets: dict[int, str] = {}
        self.layer_hover_layer_key: str | None = None
        self.layer_property_labels: dict[str, QtWidgets.QLabel] = {}
        self.layer_operator_shortcut_handles: list[QtGui.QShortcut] = []
        self.layer_visibility_snapshot: dict[str, bool] | None = None
        self.layer_undo_stack: list[dict[str, object]] = []
        self.layer_last_state_snapshot: dict[str, object] | None = None
        self.layer_last_state_signature: str | None = None
        self.layer_undo_restore_active = False
        self.layer_undo_tracking_enabled = False
        self.layer_undo_label: QtWidgets.QLabel | None = None
        self.layer_runtime_state_label: QtWidgets.QLabel | None = None
        self.layer_runtime_state_last_write_utc: str | None = None
        self.layer_runtime_state_write_error: str | None = None
        self.layer_runtime_history: list[str] = []
        self.layer_runtime_history_signature: str | None = None
        self.layer_runtime_ack_label: QtWidgets.QLabel | None = None
        self.layer_runtime_ack_mtime_ns: int | None = LAYER_RUNTIME_ACK_PATH.stat().st_mtime_ns if LAYER_RUNTIME_ACK_PATH.exists() else None
        self.layer_runtime_ack_payload: dict[str, object] | None = None
        self.layer_runtime_badges: dict[str, QtWidgets.QLabel] = {}
        self.layer_pick_state_label: QtWidgets.QLabel | None = None
        self.layer_pick_state_mtime_ns: int | None = LAYER_PICK_STATE_PATH.stat().st_mtime_ns if LAYER_PICK_STATE_PATH.exists() else None
        self.layer_pick_state_payload: dict[str, object] | None = None
        self.layer_filter_edit: QtWidgets.QLineEdit | None = None
        self.layer_filter_status_label: QtWidgets.QLabel | None = None
        self.layer_filter_text = ""
        self.layer_filter_preset = "all"
        self.layer_visual_preset = "custom"
        self.layer_group_collapsed: set[str] = set()
        self.layer_group_status_label: QtWidgets.QLabel | None = None
        self.history_list: QtWidgets.QListWidget | None = None
        self.document_undo_label: QtWidgets.QLabel | None = None
        self.document_undo_stack: list[dict[str, object]] = []
        self.document_redo_stack: list[dict[str, object]] = []
        self.document_undo_capacity = 12
        self.document_undo_tracking_enabled = False
        self.document_auto_snapshot_count = 0
        self.timeline_state_label: QtWidgets.QLabel | None = None
        self.timeline_keyframe_list: QtWidgets.QListWidget | None = None
        self.timeline_keyframes: list[dict[str, object]] = []
        self.timeline_playback_timer: QtCore.QTimer | None = None
        self.timeline_playback_active = False
        self.timeline_playback_index = 0
        self.timeline_playback_interval_ms = 1200
        self.timeline_camera_yaw_spin: QtWidgets.QDoubleSpinBox | None = None
        self.timeline_camera_pitch_spin: QtWidgets.QDoubleSpinBox | None = None
        self.timeline_camera_zoom_spin: QtWidgets.QDoubleSpinBox | None = None
        self.timeline_export_enabled_check: QtWidgets.QCheckBox | None = None
        self.timeline_export_dir_edit: QtWidgets.QLineEdit | None = None
        self.timeline_export_frames_spin: QtWidgets.QSpinBox | None = None
        self.timeline_export_fps_spin: QtWidgets.QDoubleSpinBox | None = None
        self.timeline_export_gif_check: QtWidgets.QCheckBox | None = None
        self.timeline_export_mp4_check: QtWidgets.QCheckBox | None = None
        self.timeline_ack_label: QtWidgets.QLabel | None = None
        self.timeline_ack_mtime_ns: int | None = TIMELINE_ACK_PATH.stat().st_mtime_ns if TIMELINE_ACK_PATH.exists() else None
        self.timeline_ack_payload: dict[str, object] | None = None
        self.timeline_state_last_write_utc: str | None = None
        self.timeline_state_write_error: str | None = None
        self.selected_layer_key: str | None = None
        self.boundary_highlight_state: dict[str, object] = default_boundary_highlight_state()
        self.boundary_highlight_label: QtWidgets.QLabel | None = None
        self.boundary_identity_status_label: QtWidgets.QLabel | None = None
        self.boundary_identity_warning_label: QtWidgets.QLabel | None = None
        self.boundary_highlight_ack_label: QtWidgets.QLabel | None = None
        self.boundary_highlight_ack_mtime_ns: int | None = (
            BOUNDARY_HIGHLIGHT_ACK_PATH.stat().st_mtime_ns if BOUNDARY_HIGHLIGHT_ACK_PATH.exists() else None
        )
        self.boundary_highlight_ack_payload: dict[str, object] | None = None
        self.boundary_highlight_ack_history: list[str] = []
        self.boundary_highlight_ack_history_signature: str | None = None
        self.boundary_layer_event_targets: dict[int, str] = {}
        self.active_tool = "move"
        self.tool_buttons: dict[str, QtWidgets.QToolButton] = {}
        self.tool_target_label: QtWidgets.QLabel | None = None
        self.pin_type_combo: QtWidgets.QComboBox | None = None
        self.pin_label_edit: QtWidgets.QLineEdit | None = None
        self.pin_note_edit: QtWidgets.QLineEdit | None = None
        self.pin_lat_edit: QtWidgets.QLineEdit | None = None
        self.pin_lon_edit: QtWidgets.QLineEdit | None = None
        self.pin_priority_spin: QtWidgets.QSpinBox | None = None
        self.pin_label_mode_combo: QtWidgets.QComboBox | None = None
        self.pin_label_min_priority_spin: QtWidgets.QSpinBox | None = None
        self.pin_list: QtWidgets.QListWidget | None = None
        self.pin_cursor_fill_label: QtWidgets.QLabel | None = None
        self.pin_input_ack_label: QtWidgets.QLabel | None = None
        self.pin_input_ack_mtime_ns: int | None = PIN_INPUT_ACK_PATH.stat().st_mtime_ns if PIN_INPUT_ACK_PATH.exists() else None
        self.pin_input_ack_payload: dict[str, object] | None = None
        self.pin_pick_state_label: QtWidgets.QLabel | None = None
        self.pin_pick_ack_label: QtWidgets.QLabel | None = None
        self.pin_pick_state_mtime_ns: int | None = PIN_PICK_STATE_PATH.stat().st_mtime_ns if PIN_PICK_STATE_PATH.exists() else None
        self.pin_pick_state_last_event: str | None = None
        self.pin_pick_state_payload: dict[str, object] | None = None
        self.pin_pick_ack_payload: dict[str, object] | None = None
        self.pin_pick_ack_write_error: str | None = None
        self.pin_pick_history: list[str] = []
        self.pin_pick_history_signature: str | None = None
        self.selected_pin_id: str | None = None
        self.pin_coordinate_source = "manual_lat_lon"
        self.research_pins: list[dict[str, object]] = []
        self.canvas_preview_label: QtWidgets.QLabel | None = None
        self.canvas_meta_label: QtWidgets.QLabel | None = None
        self.cursor_geodesy_bridge_label: QtWidgets.QLabel | None = None
        self.canvas_preview_mode = "state"
        self.renderer_thumbnail_path: Path | None = None
        self.renderer_thumbnail_mtime_ns: int | None = None
        self.canvas_zoom_slider: QtWidgets.QSlider | None = None
        self.cursor_latitude: float | None = None
        self.cursor_longitude: float | None = None
        self.cursor_geodesy_state_mtime_ns: int | None = CURSOR_GEODESY_STATE_PATH.stat().st_mtime_ns if CURSOR_GEODESY_STATE_PATH.exists() else None
        self.cursor_geodesy_ack_mtime_ns: int | None = CURSOR_GEODESY_ACK_PATH.stat().st_mtime_ns if CURSOR_GEODESY_ACK_PATH.exists() else None
        self.cursor_geodesy_state_payload: dict[str, object] | None = None
        self.cursor_geodesy_ack_payload: dict[str, object] | None = None
        self.provenance_text: QtWidgets.QPlainTextEdit | None = None
        self.docks: dict[str, QtWidgets.QDockWidget] = {}
        self.template_paths: list[Path] = []
        self._build_ui()
        self._build_menu_bar()
        self._build_tool_dock()
        self._build_auxiliary_docks()
        self.install_layer_operator_shortcuts()
        self.load_workspace_layout(silent=True)
        self.statusBar().showMessage("Ready")
        self.process_timer = QtCore.QTimer(self)
        self.process_timer.setInterval(1500)
        self.process_timer.timeout.connect(self.update_process_status)
        self.process_timer.start()
        self.pin_pick_state_timer = QtCore.QTimer(self)
        self.pin_pick_state_timer.setInterval(800)
        self.pin_pick_state_timer.timeout.connect(self.refresh_renderer_pin_pick_state)
        self.pin_pick_state_timer.start()
        self.pin_input_ack_timer = QtCore.QTimer(self)
        self.pin_input_ack_timer.setInterval(1000)
        self.pin_input_ack_timer.timeout.connect(self.refresh_pin_input_ack_state)
        self.pin_input_ack_timer.start()
        self.layer_runtime_ack_timer = QtCore.QTimer(self)
        self.layer_runtime_ack_timer.setInterval(1000)
        self.layer_runtime_ack_timer.timeout.connect(self.refresh_layer_runtime_ack_state)
        self.layer_runtime_ack_timer.start()
        self.layer_pick_state_timer = QtCore.QTimer(self)
        self.layer_pick_state_timer.setInterval(800)
        self.layer_pick_state_timer.timeout.connect(self.refresh_layer_pick_state)
        self.layer_pick_state_timer.start()
        self.boundary_highlight_ack_timer = QtCore.QTimer(self)
        self.boundary_highlight_ack_timer.setInterval(1000)
        self.boundary_highlight_ack_timer.timeout.connect(self.refresh_boundary_highlight_ack_state)
        self.boundary_highlight_ack_timer.start()
        self.renderer_thumbnail_timer = QtCore.QTimer(self)
        self.renderer_thumbnail_timer.setInterval(1500)
        self.renderer_thumbnail_timer.timeout.connect(self.refresh_renderer_thumbnail_if_needed)
        self.renderer_thumbnail_timer.start()
        self.timeline_playback_timer = QtCore.QTimer(self)
        self.timeline_playback_timer.setInterval(self.timeline_playback_interval_ms)
        self.timeline_playback_timer.timeout.connect(self.advance_timeline_playback)
        self.timeline_ack_timer = QtCore.QTimer(self)
        self.timeline_ack_timer.setInterval(1000)
        self.timeline_ack_timer.timeout.connect(self.refresh_timeline_ack_state)
        self.timeline_ack_timer.start()
        self.cursor_geodesy_bridge_timer = QtCore.QTimer(self)
        self.cursor_geodesy_bridge_timer.setInterval(800)
        self.cursor_geodesy_bridge_timer.timeout.connect(self.refresh_cursor_geodesy_bridge_state)
        self.cursor_geodesy_bridge_timer.start()
        self.apply_baseline()
        self.refresh_template_list()
        if initial_profile is not None:
            self.load_profile_path(initial_profile)
        self.refresh_command_preview()
        self.refresh_layer_stack_status()
        self.layer_undo_stack = []
        self.layer_last_state_snapshot = self.collect_layer_undo_snapshot()
        self.layer_last_state_signature = self.layer_undo_signature(self.layer_last_state_snapshot)
        self.layer_undo_tracking_enabled = True
        self.refresh_layer_undo_label()
        self.refresh_timeline_state_label()
        self.document_undo_tracking_enabled = True
        self.capture_document_snapshot("Initial workspace", clear_redo=False)

    def install_layer_operator_shortcuts(self) -> None:
        shortcut_specs = (
            ("Ctrl+Alt+V", self.toggle_selected_layer_visibility),
            ("Ctrl+Alt+L", self.toggle_selected_layer_lock),
            ("Ctrl+Alt+S", self.solo_selected_layer_visibility),
            ("Ctrl+Alt+R", self.restore_layer_visibility_snapshot),
            ("Ctrl+Alt+Z", self.undo_layer_stack_state),
            ("Ctrl+Alt+0", self.reset_layer_stack_controls),
            ("Ctrl+Alt+D", self.show_layer_capability_matrix),
        )
        self.layer_operator_shortcut_handles.clear()
        for sequence, callback in shortcut_specs:
            shortcut = QtGui.QShortcut(QtGui.QKeySequence(sequence), self)
            shortcut.setContext(QtCore.Qt.ShortcutContext.ApplicationShortcut)
            shortcut.activated.connect(callback)
            self.layer_operator_shortcut_handles.append(shortcut)

    def _build_ui(self) -> None:
        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        main = QtWidgets.QVBoxLayout(central)
        main.setContentsMargins(18, 16, 18, 16)
        main.setSpacing(12)

        title = QtWidgets.QLabel("RRKAL_displaytools Studio")
        title.setObjectName("title")
        subtitle = QtWidgets.QLabel(
            "Research-oriented Qt workspace：借鑑 Photoshop 的面板精神，但優先服務科研者的可追蹤圖層、可重現 profile 與資料狀態檢查。"
        )
        subtitle.setWordWrap(True)
        main.addWidget(title)
        main.addWidget(subtitle)

        body = QtWidgets.QHBoxLayout()
        body.setSpacing(14)
        main.addLayout(body, stretch=1)

        left = QtWidgets.QVBoxLayout()
        right = QtWidgets.QVBoxLayout()
        body.addLayout(left, stretch=1)
        body.addLayout(right, stretch=1)

        renderer_group = self._group("工具選項 / Renderer 入口")
        renderer_form = QtWidgets.QFormLayout(renderer_group)
        self.style_combo = self._combo(STYLE_PROFILES)
        self.ui_combo = self._combo(UI_BACKENDS)
        self.topo_combo = self._combo(TOPO_SOURCES)
        self.data_combo = self._combo(DATA_MODES)
        self.width_edit = QtWidgets.QLineEdit("1280")
        self.height_edit = QtWidgets.QLineEdit("720")
        self.topo_step_edit = QtWidgets.QLineEdit("48")
        self.arch_edit = QtWidgets.QLineEdit("gpu")
        self.rrkal_manifest_ref_edit = QtWidgets.QLineEdit("")
        self.rrkal_manifest_ref_edit.setPlaceholderText("optional RRKAL manifest path/URL/reference")
        renderer_form.addRow("Style profile", self.style_combo)
        self.style_template_preview_label = QtWidgets.QLabel("Style previews: Scientific / Nautical / Parchment / Tactical")
        self.style_template_preview_label.setObjectName("styleTemplateVisualPreview")
        self.style_template_preview_label.setWordWrap(True)
        self.style_template_preview_label.setStyleSheet(
            "QLabel#styleTemplateVisualPreview { background:#181b1f; color:#e9edf1; border:1px solid #3a4652; border-radius:6px; padding:6px; }"
        )
        renderer_form.addRow("Template preview", self.style_template_preview_label)
        self.style_template_preview_cards = self._create_style_template_preview_cards()
        renderer_form.addRow("Template cards", self.style_template_preview_cards)
        self.style_thumbnail_readiness_label = QtWidgets.QLabel("Style thumbnails: ready=unknown; missing=unknown")
        self.style_thumbnail_readiness_label.setObjectName("styleThumbnailReadiness")
        self.style_thumbnail_readiness_label.setWordWrap(True)
        self.style_thumbnail_readiness_label.setStyleSheet(
            "QLabel#styleThumbnailReadiness { background:#fff7e6; color:#5a3b12; border:1px solid #d6a94f; border-radius:6px; padding:6px; font-weight:600; }"
        )
        renderer_form.addRow("Thumb readiness", self.style_thumbnail_readiness_label)
        self.style_combo.currentTextChanged.connect(lambda _text: self.refresh_style_template_preview_cards())
        self.refresh_style_template_preview_cards()
        renderer_form.addRow("UI backend", self.ui_combo)
        renderer_form.addRow("Topography", self.topo_combo)
        renderer_form.addRow("Data mode", self.data_combo)
        renderer_form.addRow("Width", self.width_edit)
        renderer_form.addRow("Height", self.height_edit)
        renderer_form.addRow("Topo step", self.topo_step_edit)
        renderer_form.addRow("Taichi arch", self.arch_edit)
        renderer_form.addRow("RRKAL manifest ref", self.rrkal_manifest_ref_edit)
        left.addWidget(renderer_group)

        material_group = self._group("屬性 / 海洋材質")
        material_form = QtWidgets.QFormLayout(material_group)
        self.wave_edit = QtWidgets.QLineEdit("0.22")
        self.roughness_edit = QtWidgets.QLineEdit("0.28")
        self.foam_edit = QtWidgets.QLineEdit("0.12")
        material_form.addRow("Wave strength", self.wave_edit)
        material_form.addRow("Roughness", self.roughness_edit)
        material_form.addRow("Foam", self.foam_edit)
        self.ocean_3d_control_label = QtWidgets.QLabel("Taichi 3D Ocean: initializing")
        self.ocean_3d_control_label.setObjectName("taichiOcean3DControlPanel")
        self.ocean_3d_control_label.setWordWrap(True)
        self.ocean_3d_control_label.setStyleSheet(
            "QLabel#taichiOcean3DControlPanel { color:#12384f; background:#e7f5ff; "
            "border:1px solid #79abc7; border-radius:8px; padding:6px 8px; font-weight:600; }"
        )
        ocean_3d_control_button = QtWidgets.QPushButton("Taichi 3D Ocean controls")
        ocean_3d_control_button.setObjectName("taichiOcean3DControlButton")
        ocean_3d_control_button.setToolTip(
            "Open the Taichi 3D Ocean Water scalar control window for wave, roughness and foam."
        )
        ocean_3d_control_button.clicked.connect(self.open_taichi_ocean_3d_controls)
        for ocean_edit in (self.wave_edit, self.roughness_edit, self.foam_edit):
            ocean_edit.textChanged.connect(self.refresh_ocean_3d_control_summary)
        self.refresh_ocean_3d_control_summary()
        material_form.addRow("Taichi ocean", self.ocean_3d_control_label)
        material_form.addRow(ocean_3d_control_button)
        layer_inspector_note = QtWidgets.QLabel("Active layer inspector：已同步 layer runtime；renderer pick state 會回寫選取結果。")
        layer_inspector_note.setWordWrap(True)
        self.layer_property_labels = {
            "name": QtWidgets.QLabel("尚未選取"),
            "visible": QtWidgets.QLabel("-"),
            "locked": QtWidgets.QLabel("-"),
            "opacity": QtWidgets.QLabel("-"),
            "blend": QtWidgets.QLabel("-"),
            "capabilities": QtWidgets.QLabel("-"),
            "runtime_summary": QtWidgets.QLabel("-"),
            "runtime_warnings": QtWidgets.QLabel("-"),
            "renderer_diagnostics_summary": QtWidgets.QLabel("-"),
            "renderer_diagnostics_detail": QtWidgets.QLabel("-"),
            "renderer_diagnostics_remediation": QtWidgets.QLabel("-"),
            "runtime_context": QtWidgets.QLabel("-"),
            "territory_identity": QtWidgets.QLabel("-"),
            "identity_source": QtWidgets.QLabel("-"),
            "renderer_target": QtWidgets.QLabel("-"),
            "diagnostics": QtWidgets.QLabel("-"),
        }
        for property_label in self.layer_property_labels.values():
            property_label.setWordWrap(True)
        material_form.addRow("Layer inspector", layer_inspector_note)
        material_form.addRow("Active layer", self.layer_property_labels["name"])
        material_form.addRow("Visible", self.layer_property_labels["visible"])
        material_form.addRow("Locked", self.layer_property_labels["locked"])
        material_form.addRow("Opacity", self.layer_property_labels["opacity"])
        material_form.addRow("Blend mode", self.layer_property_labels["blend"])
        material_form.addRow("Layer capabilities", self.layer_property_labels["capabilities"])
        material_form.addRow("Runtime summary", self.layer_property_labels["runtime_summary"])
        material_form.addRow("Runtime warnings", self.layer_property_labels["runtime_warnings"])
        material_form.addRow("Renderer summary", self.layer_property_labels["renderer_diagnostics_summary"])
        material_form.addRow("Renderer detail", self.layer_property_labels["renderer_diagnostics_detail"])
        material_form.addRow("Renderer hints", self.layer_property_labels["renderer_diagnostics_remediation"])
        material_form.addRow("Runtime context", self.layer_property_labels["runtime_context"])
        material_form.addRow("Territory identity", self.layer_property_labels["territory_identity"])
        material_form.addRow("Identity source", self.layer_property_labels["identity_source"])
        material_form.addRow("Renderer target", self.layer_property_labels["renderer_target"])
        material_form.addRow("Renderer diagnostics", self.layer_property_labels["diagnostics"])
        layer_property_actions = QtWidgets.QHBoxLayout()
        toggle_selected_visibility = QtWidgets.QPushButton("切換選取可見")
        reset_selected_state = QtWidgets.QPushButton("重設選取 UI 狀態")
        toggle_selected_visibility.clicked.connect(self.toggle_selected_layer_visibility)
        reset_selected_state.clicked.connect(self.reset_selected_layer_controls)
        layer_property_actions.addWidget(toggle_selected_visibility)
        layer_property_actions.addWidget(reset_selected_state)
        material_form.addRow(layer_property_actions)
        self.boundary_highlight_label = QtWidgets.QLabel(self.boundary_highlight_summary())
        self.boundary_highlight_label.setWordWrap(True)
        self.boundary_identity_status_label = QtWidgets.QLabel(self.boundary_identity_status_summary())
        self.boundary_identity_status_label.setWordWrap(True)
        self.boundary_identity_warning_label = QtWidgets.QLabel(self.boundary_identity_warning_text())
        self.boundary_identity_warning_label.setObjectName("boundaryIdentityWarningBadge")
        self.boundary_identity_warning_label.setWordWrap(True)
        self.boundary_identity_warning_label.setStyleSheet(
            "QLabel#boundaryIdentityWarningBadge { color: #7a4a00; background: #fff1c7; "
            "border: 1px solid #d09a2d; border-radius: 8px; padding: 6px 8px; font-weight: 600; }"
        )
        boundary_highlight_button = QtWidgets.QPushButton("疆域強調遮罩設定")
        boundary_highlight_button.clicked.connect(lambda _checked=False: self.open_boundary_highlight_dialog())
        material_form.addRow("Boundary highlight", self.boundary_highlight_label)
        material_form.addRow("Boundary identity", self.boundary_identity_status_label)
        material_form.addRow("Identity warning", self.boundary_identity_warning_label)
        material_form.addRow(boundary_highlight_button)
        self.boundary_highlight_ack_label = QtWidgets.QLabel(
            f"Boundary ack: waiting for {BOUNDARY_HIGHLIGHT_ACK_PATH.name}"
        )
        self.boundary_highlight_ack_label.setWordWrap(True)
        material_form.addRow("Boundary renderer", self.boundary_highlight_ack_label)
        properties_dock = QtWidgets.QDockWidget("Properties", self)
        properties_dock.setObjectName("propertiesDock")
        properties_dock.setAllowedAreas(
            QtCore.Qt.DockWidgetArea.LeftDockWidgetArea
            | QtCore.Qt.DockWidgetArea.RightDockWidgetArea
        )
        properties_dock.setWidget(material_group)
        self.docks["properties"] = properties_dock
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, properties_dock)

        preset_group = self._group("預設 / Looks")
        preset_layout = QtWidgets.QGridLayout(preset_group)
        presets = (
            ("昨天風格基線", self.apply_baseline),
            ("航海/水文", self.apply_maritime),
            ("羊皮紙", self.apply_parchment),
            ("戰術", self.apply_tactical),
            ("最少圖層", self.apply_minimal),
            ("快速 synthetic", self.apply_fast_synthetic),
        )
        for index, (label, callback) in enumerate(presets):
            button = QtWidgets.QPushButton(label)
            button.clicked.connect(callback)
            preset_layout.addWidget(button, index // 2, index % 2)
        left.addWidget(preset_group)

        template_group = self._group("模板 / Profile templates")
        template_layout = QtWidgets.QGridLayout(template_group)
        self.template_combo = QtWidgets.QComboBox()
        load_template_button = QtWidgets.QPushButton("載入模板")
        rescan_template_button = QtWidgets.QPushButton("重掃模板")
        load_template_button.clicked.connect(self.load_selected_template)
        rescan_template_button.clicked.connect(self.refresh_template_list)
        template_layout.addWidget(self.template_combo, 0, 0, 1, 2)
        template_layout.addWidget(load_template_button, 1, 0)
        template_layout.addWidget(rescan_template_button, 1, 1)
        left.addWidget(template_group)
        left.addStretch(1)

        layers_group = self._group("圖層 / Layers")
        layers_layout = QtWidgets.QVBoxLayout(layers_group)
        layer_filter_row = QtWidgets.QHBoxLayout()
        layer_filter_row.addWidget(QtWidgets.QLabel("Filter"))
        self.layer_filter_edit = QtWidgets.QLineEdit()
        self.layer_filter_edit.setPlaceholderText("Search layer key/name, e.g. hydro, eez, pin")
        self.layer_filter_edit.textChanged.connect(self.set_layer_filter_text)
        clear_layer_filter = QtWidgets.QPushButton("Clear")
        clear_layer_filter.clicked.connect(lambda _checked=False: self.apply_layer_filter_preset("all"))
        layer_filter_row.addWidget(self.layer_filter_edit)
        layer_filter_row.addWidget(clear_layer_filter)
        layers_layout.addLayout(layer_filter_row)
        layer_focus_row = QtWidgets.QHBoxLayout()
        select_first_match = QtWidgets.QPushButton("Select first")
        select_first_match.clicked.connect(self.select_first_filtered_layer)
        reveal_selected_layer = QtWidgets.QPushButton("Reveal selected")
        reveal_selected_layer.clicked.connect(self.reveal_selected_layer_row)
        layer_focus_row.addWidget(select_first_match)
        layer_focus_row.addWidget(reveal_selected_layer)
        for preset_id, label in (
            ("hydrology", "Hydro"),
            ("maritime", "Maritime"),
            ("traffic", "Traffic"),
            ("visual_aids", "Aids"),
            ("all", "All"),
        ):
            button = QtWidgets.QPushButton(label)
            button.clicked.connect(lambda _checked=False, preset=preset_id: self.apply_layer_filter_preset(preset))
            layer_focus_row.addWidget(button)
        layers_layout.addLayout(layer_focus_row)
        layer_group_row = QtWidgets.QHBoxLayout()
        for group_id, label in (
            ("hydrology", "Hydro"),
            ("maritime", "Sea"),
            ("traffic", "Traffic"),
            ("visual_aids", "Aids"),
        ):
            button = QtWidgets.QPushButton(f"Toggle {label}")
            button.clicked.connect(lambda _checked=False, gid=group_id: self.toggle_layer_group_collapsed(gid))
            layer_group_row.addWidget(button)
        expand_all_groups = QtWidgets.QPushButton("Expand groups")
        expand_all_groups.clicked.connect(self.expand_all_layer_groups)
        layer_group_row.addWidget(expand_all_groups)
        layers_layout.addLayout(layer_group_row)
        self.layer_group_status_label = QtWidgets.QLabel("Layer groups: all expanded")
        self.layer_group_status_label.setWordWrap(True)
        layers_layout.addWidget(self.layer_group_status_label)
        self.layer_filter_status_label = QtWidgets.QLabel("Layer filter: all layers")
        self.layer_filter_status_label.setWordWrap(True)
        layers_layout.addWidget(self.layer_filter_status_label)
        layer_header = QtWidgets.QWidget()
        layer_header_layout = QtWidgets.QGridLayout(layer_header)
        layer_header_layout.setContentsMargins(0, 0, 0, 0)
        headers = ("Select", "Vis", "Layer", "Lock", "Opacity", "Blend", "Runtime", "Action")
        for column, text in enumerate(headers):
            header_label = QtWidgets.QLabel(text)
            header_label.setObjectName("layerHeader")
            layer_header_layout.addWidget(header_label, 0, column)
        layers_layout.addWidget(layer_header)
        for key, label in LAYER_LABELS:
            row = QtWidgets.QWidget()
            row.setObjectName("layerRow")
            row.setProperty("selected", False)
            row.setProperty("locked", False)
            row.setMouseTracking(True)
            row.installEventFilter(self)
            row_layout = QtWidgets.QGridLayout(row)
            row_layout.setContentsMargins(4, 2, 4, 2)
            row_layout.setHorizontalSpacing(8)
            self.layer_rows[key] = row
            self.layer_hover_event_targets[id(row)] = key

            select_button = QtWidgets.QToolButton()
            select_button.setText("選取")
            select_button.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextOnly)
            select_button.clicked.connect(lambda _checked=False, layer_key=key: self.select_layer(layer_key))

            check = QtWidgets.QCheckBox()
            check.setToolTip(f"Renderer visibility flag: {BOOL_FLAGS[key]}")
            check.stateChanged.connect(self.refresh_command_preview)
            check.stateChanged.connect(lambda _state, self=self: self.refresh_layer_stack_status())
            self.checks[key] = check

            layer_label = QtWidgets.QLabel(label)
            layer_label.setMouseTracking(True)
            layer_label.installEventFilter(self)
            self.layer_hover_event_targets[id(layer_label)] = key

            lock = QtWidgets.QCheckBox()
            lock.setToolTip("Lock is honored by renderer runtime sync for visibility, opacity, and blend updates.")
            lock.stateChanged.connect(lambda _state, self=self: self.refresh_layer_stack_status())
            self.layer_locks[key] = lock

            opacity = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
            opacity.setRange(0, 100)
            opacity.setValue(100)
            opacity.setToolTip("Renderer runtime opacity sync is live for supported layers.")
            opacity.valueChanged.connect(lambda _value, self=self: self.refresh_layer_stack_status())
            self.layer_opacity[key] = opacity

            blend = QtWidgets.QComboBox()
            blend.addItems(BLEND_MODES)
            blend.setToolTip("Renderer runtime blend sync is live for hydrology, boundary, and point/icon overlays.")
            blend.currentTextChanged.connect(lambda _text, self=self: self.refresh_layer_stack_status())
            self.layer_blends[key] = blend
            runtime_badge = QtWidgets.QLabel("no_ack")
            runtime_badge.setObjectName("layerRuntimeBadge")
            runtime_badge.setStyleSheet(layer_runtime_badge_style("no_ack"))
            runtime_badge.setToolTip("Last renderer layer runtime ack status for this layer.")
            self.layer_runtime_badges[key] = runtime_badge
            action_badge = QtWidgets.QLabel("Emphasis" if key in BOUNDARY_HIGHLIGHT_LAYER_KEYS else "-")
            action_badge.setObjectName("layerActionBadge")
            action_badge.setMouseTracking(True)
            action_badge.installEventFilter(self)
            self.layer_hover_event_targets[id(action_badge)] = key
            if key in BOUNDARY_HIGHLIGHT_LAYER_KEYS:
                boundary_tooltip = "雙擊開啟疆域/領海/EEZ/公海強調遮罩控制。"
                row.setToolTip(boundary_tooltip)
                layer_label.setToolTip(boundary_tooltip)
                action_badge.setToolTip(boundary_tooltip)
                row.installEventFilter(self)
                layer_label.installEventFilter(self)
                action_badge.installEventFilter(self)
                self.boundary_layer_event_targets[id(row)] = key
                self.boundary_layer_event_targets[id(layer_label)] = key
                self.boundary_layer_event_targets[id(action_badge)] = key

            row_layout.addWidget(select_button, 0, 0)
            row_layout.addWidget(check, 0, 1)
            row_layout.addWidget(layer_label, 0, 2)
            row_layout.addWidget(lock, 0, 3)
            row_layout.addWidget(opacity, 0, 4)
            row_layout.addWidget(blend, 0, 5)
            row_layout.addWidget(runtime_badge, 0, 6)
            row_layout.addWidget(action_badge, 0, 7)
            layers_layout.addWidget(row)
        self.selected_layer_label = QtWidgets.QLabel("目前選取圖層：尚未選取")
        self.selected_layer_label.setObjectName("selectedLayer")
        layers_layout.addWidget(self.selected_layer_label)
        self.layer_selection_affordance_label = QtWidgets.QLabel(
            "Selection affordance: active=none; row_highlight=selected property; renderer=unknown"
        )
        self.layer_selection_affordance_label.setObjectName("layerSelectionAffordance")
        self.layer_selection_affordance_label.setWordWrap(True)
        layers_layout.addWidget(self.layer_selection_affordance_label)
        self.layer_hover_affordance_label = QtWidgets.QLabel("Layer hover: target=none; renderer=none")
        self.layer_hover_affordance_label.setObjectName("layerHoverAffordance")
        self.layer_hover_affordance_label.setWordWrap(True)
        layers_layout.addWidget(self.layer_hover_affordance_label)
        self.layer_stack_note = QtWidgets.QLabel("Lock / Opacity / Blend 已接 renderer runtime；未支援圖層會在 renderer_sync 標示。")
        self.layer_stack_note.setWordWrap(True)
        layers_layout.addWidget(self.layer_stack_note)
        self.layer_operator_groups_label = QtWidgets.QLabel(
            "Layer workflow: Selection / Edit state / Isolation / History / Diagnostics"
        )
        self.layer_operator_groups_label.setWordWrap(True)
        layers_layout.addWidget(self.layer_operator_groups_label)
        self.layer_research_workflow_label = QtWidgets.QLabel("Layer research workflow: pending")
        self.layer_research_workflow_label.setWordWrap(True)
        layers_layout.addWidget(self.layer_research_workflow_label)
        self.layer_control_feedback_strip_label = QtWidgets.QLabel(
            "Layer control strip: selected=none; visible=unknown; lock=unknown; opacity=unknown; blend=unknown; renderer=unknown"
        )
        self.layer_control_feedback_strip_label.setObjectName("layerControlFeedbackStrip")
        self.layer_control_feedback_strip_label.setWordWrap(True)
        layers_layout.addWidget(self.layer_control_feedback_strip_label)
        self.ocean_3d_control_board_label = QtWidgets.QLabel("Ocean 3D quick controls: initializing")
        self.ocean_3d_control_board_label.setObjectName("ocean3DControlBoardStrip")
        self.ocean_3d_control_board_label.setWordWrap(True)
        self.ocean_3d_control_board_label.setStyleSheet(
            "QLabel#ocean3DControlBoardStrip { color:#12384f; background:#e7f5ff; "
            "border:1px solid #79abc7; border-radius:8px; padding:6px 8px; font-weight:600; }"
        )
        layers_layout.addWidget(self.ocean_3d_control_board_label)
        ocean_3d_control_board_button = QtWidgets.QPushButton("Taichi Ocean 3D controls")
        ocean_3d_control_board_button.setObjectName("ocean3DControlBoardButton")
        ocean_3d_control_board_button.setToolTip(
            "Open the same Taichi 3D Ocean Water scalar control window from the default-visible Layers control board."
        )
        ocean_3d_control_board_button.clicked.connect(self.open_taichi_ocean_3d_controls)
        layers_layout.addWidget(ocean_3d_control_board_button)
        self.refresh_ocean_3d_control_summary()
        self.render_plan_cache_label = QtWidgets.QLabel("Render plan cache: waiting for renderer metadata")
        self.render_plan_cache_label.setObjectName("renderPlanCacheDiagnosticsStrip")
        self.render_plan_cache_label.setWordWrap(True)
        self.render_plan_cache_label.setStyleSheet(
            "QLabel#renderPlanCacheDiagnosticsStrip { color:#2b3416; background:#f1f8df; "
            "border:1px solid #a8bd65; border-radius:8px; padding:6px 8px; font-weight:600; }"
        )
        layers_layout.addWidget(self.render_plan_cache_label)
        render_plan_cache_button = QtWidgets.QPushButton("Render plan diagnostics")
        render_plan_cache_button.setObjectName("renderPlanCacheDiagnosticsButton")
        render_plan_cache_button.setToolTip(
            "Inspect layer render-plan cache metadata and the queued single-pass optimization contract."
        )
        render_plan_cache_button.clicked.connect(self.show_layer_render_plan_performance)
        layers_layout.addWidget(render_plan_cache_button)
        self.refresh_layer_render_plan_cache_diagnostics_strip()
        self.boundary_emphasis_button = QtWidgets.QPushButton("Boundary emphasis controls...")
        self.boundary_emphasis_button.clicked.connect(self.open_boundary_emphasis_dialog)
        layers_layout.addWidget(self.boundary_emphasis_button)
        self.boundary_emphasis_label = QtWidgets.QLabel("Boundary emphasis: UI ready, renderer bridge wired")
        self.boundary_emphasis_label.setWordWrap(True)
        layers_layout.addWidget(self.boundary_emphasis_label)
        self.profile_launch_readiness_label = QtWidgets.QLabel("Profile/launch readiness: pending")
        self.profile_launch_readiness_label.setWordWrap(True)
        layers_layout.addWidget(self.profile_launch_readiness_label)
        self.profile_ui_state_replay_label = QtWidgets.QLabel(
            "Profile UI replay: layers, pins, Boundary emphasis/warnings and Timeline keyframes are portable profile state"
        )
        self.profile_ui_state_replay_label.setObjectName("profileUiStateReplay")
        self.profile_ui_state_replay_label.setWordWrap(True)
        layers_layout.addWidget(self.profile_ui_state_replay_label)
        self.visual_review_readiness_label = QtWidgets.QLabel(
            "Visual readiness: press Inspect: Visual readiness to summarize thumbnail/live preview artifacts."
        )
        self.visual_review_readiness_label.setObjectName("visualReviewReadiness")
        self.visual_review_readiness_label.setWordWrap(True)
        layers_layout.addWidget(self.visual_review_readiness_label)
        self.layer_operation_summary_label = QtWidgets.QLabel(
            "Layer operation summary: no active layer selected; use Select or click a layer row."
        )
        self.layer_operation_summary_label.setObjectName("layerOperationSummary")
        self.layer_operation_summary_label.setWordWrap(True)
        layers_layout.addWidget(self.layer_operation_summary_label)
        self.layer_operation_event_label = QtWidgets.QLabel("Last layer operation: none yet")
        self.layer_operation_event_label.setObjectName("layerOperationEvent")
        self.layer_operation_event_label.setWordWrap(True)
        layers_layout.addWidget(self.layer_operation_event_label)
        self.cross_machine_readiness_label = QtWidgets.QLabel("Cross-machine clone readiness: pending")
        self.cross_machine_readiness_label.setWordWrap(True)
        layers_layout.addWidget(self.cross_machine_readiness_label)
        self.layer_visual_presets_label = QtWidgets.QLabel("Layer presets: custom")
        self.layer_visual_presets_label.setWordWrap(True)
        layers_layout.addWidget(self.layer_visual_presets_label)
        self.layer_visual_preset_runtime_feedback_label = QtWidgets.QLabel("Preset renderer ack: waiting")
        self.layer_visual_preset_runtime_feedback_label.setWordWrap(True)
        layers_layout.addWidget(self.layer_visual_preset_runtime_feedback_label)
        self.hydrology_lod_readiness_label = QtWidgets.QLabel("Hydrology/LOD readiness: pending")
        self.hydrology_lod_readiness_label.setWordWrap(True)
        layers_layout.addWidget(self.hydrology_lod_readiness_label)
        self.hydrology_lod_runtime_evidence_label = QtWidgets.QLabel("Hydrology runtime evidence: waiting")
        self.hydrology_lod_runtime_evidence_label.setWordWrap(True)
        layers_layout.addWidget(self.hydrology_lod_runtime_evidence_label)
        preset_buttons = QtWidgets.QHBoxLayout()
        for preset_id, label in (
            ("all_context", "All"),
            ("hydrology_focus", "Hydrology"),
            ("boundary_focus", "Boundary"),
            ("annotation_focus", "Annotations"),
        ):
            button = QtWidgets.QPushButton(label)
            button.setToolTip(f"Apply layer visibility preset: {preset_id}")
            button.clicked.connect(lambda _checked=False, preset_id=preset_id: self.apply_layer_visual_preset(preset_id))
            preset_buttons.addWidget(button)
        layers_layout.addLayout(preset_buttons)
        self.layer_runtime_legend_label = QtWidgets.QLabel(
            "Runtime badge: no_ack=等待 ack, ok=無近期變更, target=目前 renderer target, changed=renderer 已套用, locked=locked skip, error=ack error"
        )
        self.layer_runtime_legend_label.setWordWrap(True)
        layers_layout.addWidget(self.layer_runtime_legend_label)
        self.layer_undo_label = QtWidgets.QLabel("Layer undo: 0 snapshots")
        self.layer_undo_label.setWordWrap(True)
        layers_layout.addWidget(self.layer_undo_label)
        self.layer_runtime_state_label = QtWidgets.QLabel(f"Layer runtime bridge: waiting for {LAYER_RUNTIME_STATE_PATH.name}")
        self.layer_runtime_state_label.setWordWrap(True)
        layers_layout.addWidget(self.layer_runtime_state_label)
        self.layer_runtime_ack_label = QtWidgets.QLabel(f"Renderer ack: waiting for {LAYER_RUNTIME_ACK_PATH.name}")
        self.layer_runtime_ack_label.setWordWrap(True)
        layers_layout.addWidget(self.layer_runtime_ack_label)
        self.layer_pick_state_label = QtWidgets.QLabel(f"Layer pick: waiting for {LAYER_PICK_STATE_PATH.name}")
        self.layer_pick_state_label.setWordWrap(True)
        layers_layout.addWidget(self.layer_pick_state_label)
        self.layer_workflow_hint_label = QtWidgets.QLabel(
            "Layer workflow: click a row to select the active research layer; double-click Boundary/領海/EEZ/公海 rows "
            "or use Emphasis to open mask controls; identity warning badges mean preview/source-property identity only, "
            "not authoritative polygon/EEZ resolution."
        )
        self.layer_workflow_hint_label.setObjectName("layerWorkflowHint")
        self.layer_workflow_hint_label.setWordWrap(True)
        layers_layout.addWidget(self.layer_workflow_hint_label)
        demo = QtWidgets.QCheckBox("閉環展示 preset（會覆蓋部分設定）")
        demo.stateChanged.connect(self.refresh_command_preview)
        self.checks["demo_closed_loop"] = demo
        layers_layout.addWidget(demo)
        layer_actions = (
            ("水文開/關", self.toggle_hydrology_layers),
            ("海域開/關", self.toggle_maritime_layers),
            ("交通開/關", self.toggle_transport_layers),
            ("輔助開/關", self.toggle_visual_aids),
            ("Solo 選取圖層", self.solo_selected_layer_visibility),
            ("還原 Solo 前可見性", self.restore_layer_visibility_snapshot),
            ("Undo 圖層狀態", self.undo_layer_stack_state),
            ("顯示 layer capabilities", self.show_layer_capability_matrix),
            ("顯示 layer runtime JSON", self.show_layer_runtime_state),
            ("顯示 layer pick JSON", self.show_layer_pick_state),
            ("重設 UI 圖層狀態", self.reset_layer_stack_controls),
        )
        layer_actions_layout = QtWidgets.QGridLayout()
        for index, (label, callback) in enumerate(layer_actions):
            button = QtWidgets.QPushButton(label)
            button.clicked.connect(callback)
            layer_actions_layout.addWidget(button, index // 2, index % 2)
        layers_layout.addLayout(layer_actions_layout)
        self.select_layer("show_grid")
        self.refresh_layer_filter()
        layers_dock = QtWidgets.QDockWidget("Layers", self)
        layers_dock.setObjectName("layersDock")
        layers_dock.setAllowedAreas(
            QtCore.Qt.DockWidgetArea.LeftDockWidgetArea
            | QtCore.Qt.DockWidgetArea.RightDockWidgetArea
        )
        layers_dock.setWidget(layers_group)
        self.docks["layers"] = layers_dock
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, layers_dock)

        command_group = self._group("中央預覽 / Canvas, Command and JSON preview")
        command_layout = QtWidgets.QVBoxLayout(command_group)
        self.canvas_preview_label = QtWidgets.QLabel("Canvas Preview")
        self.canvas_preview_label.setObjectName("canvasPreview")
        self.canvas_preview_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.canvas_preview_label.setMinimumHeight(220)
        self.canvas_preview_label.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.canvas_preview_label.setMouseTracking(True)
        self.canvas_preview_label.installEventFilter(self)
        command_layout.addWidget(self.canvas_preview_label)
        self.canvas_meta_label = QtWidgets.QLabel("Canvas state: -")
        self.canvas_meta_label.setObjectName("canvasMeta")
        self.canvas_meta_label.setWordWrap(True)
        command_layout.addWidget(self.canvas_meta_label)
        self.cursor_geodesy_bridge_label = QtWidgets.QLabel("Renderer cursor geodesy: waiting for state/ack")
        self.cursor_geodesy_bridge_label.setObjectName("canvasMeta")
        self.cursor_geodesy_bridge_label.setWordWrap(True)
        command_layout.addWidget(self.cursor_geodesy_bridge_label)
        zoom_row = QtWidgets.QHBoxLayout()
        zoom_row.addWidget(QtWidgets.QLabel("Canvas zoom"))
        self.canvas_zoom_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.canvas_zoom_slider.setRange(25, 200)
        self.canvas_zoom_slider.setValue(100)
        self.canvas_zoom_slider.valueChanged.connect(lambda _value, self=self: self.refresh_canvas_preview())
        zoom_row.addWidget(self.canvas_zoom_slider)
        command_layout.addLayout(zoom_row)
        self.command_text = QtWidgets.QPlainTextEdit()
        self.command_text.setReadOnly(True)
        self.command_text.setMinimumHeight(150)
        command_layout.addWidget(self.command_text)
        right.addWidget(command_group, stretch=1)

        actions_group = self._group("動作 / Actions")
        actions = QtWidgets.QGridLayout(actions_group)
        refresh_button = QtWidgets.QPushButton("刷新命令")
        copy_button = QtWidgets.QPushButton("複製命令")
        copy_portable_button = QtWidgets.QPushButton("複製可攜命令")
        save_button = QtWidgets.QPushButton("儲存配置")
        load_button = QtWidgets.QPushButton("載入配置")
        open_templates_button = QtWidgets.QPushButton("模板目錄")
        open_local_profiles_button = QtWidgets.QPushButton("本機配置")
        export_packet_button = QtWidgets.QPushButton("匯出啟動包")
        export_reviewer_packet_button = QtWidgets.QPushButton("Export reviewer packet")
        profile_replay_button = QtWidgets.QPushButton("Inspect: Profile replay")
        copy_launch_summary_button = QtWidgets.QPushButton("Copy launch summary")
        timeline_button = QtWidgets.QPushButton("Inspect: Timeline")
        ocean_port_button = QtWidgets.QPushButton("Inspect: Ocean port")
        ocean_3d_controls_action_button = QtWidgets.QPushButton("Open: Ocean 3D controls")
        copy_ocean_summary_button = QtWidgets.QPushButton("Copy Ocean summary")
        hydro_lod_button = QtWidgets.QPushButton("Inspect: Hydro LOD")
        copy_hydro_lod_summary_button = QtWidgets.QPushButton("Copy Hydro LOD summary")
        style_routes_button = QtWidgets.QPushButton("Inspect: Style routes")
        copy_style_routes_summary_button = QtWidgets.QPushButton("Copy Style routes summary")
        style_thumbnails_button = QtWidgets.QPushButton("Inspect: Style thumbs")
        module_seams_button = QtWidgets.QPushButton("Inspect: Module seams")
        copy_module_summary_button = QtWidgets.QPushButton("Copy module summary")
        clone_ready_button = QtWidgets.QPushButton("Inspect: Clone ready")
        copy_clone_summary_button = QtWidgets.QPushButton("Copy clone summary")
        layer_matrix_button = QtWidgets.QPushButton("Inspect: Layer matrix")
        layer_runtime_button = QtWidgets.QPushButton("Inspect: Layer runtime")
        layer_pick_button = QtWidgets.QPushButton("Inspect: Layer pick")
        selection_state_button = QtWidgets.QPushButton("Inspect: Selection state")
        copy_selection_summary_button = QtWidgets.QPushButton("Copy selection summary")
        layer_ops_button = QtWidgets.QPushButton("Inspect: Layer ops")
        pin_pick_button = QtWidgets.QPushButton("Inspect: Pin pick")
        copy_pin_summary_action_button = QtWidgets.QPushButton("Copy pin summary")
        cursor_geo_button = QtWidgets.QPushButton("Inspect: Cursor geo")
        copy_cursor_summary_button = QtWidgets.QPushButton("Copy cursor summary")
        boundary_state_button = QtWidgets.QPushButton("Inspect: Boundary JSON")
        copy_boundary_summary_button = QtWidgets.QPushButton("Copy boundary summary")
        copy_research_summary_button = QtWidgets.QPushButton("Copy research summary")
        capabilities_button = QtWidgets.QPushButton("Renderer 能力")
        closed_loop_button = QtWidgets.QPushButton("閉環狀態")
        layer_manifest_button = QtWidgets.QPushButton("圖層 manifest")
        canvas_state_button = QtWidgets.QPushButton("Inspect: Canvas state")
        visual_readiness_button = QtWidgets.QPushButton("Inspect: Visual readiness")
        copy_visual_summary_button = QtWidgets.QPushButton("Copy visual summary")
        copy_style_thumbs_command_button = QtWidgets.QPushButton("Copy style thumbs command")
        copy_style_thumb_status_button = QtWidgets.QPushButton("Copy style thumb status")
        thumbnail_button = QtWidgets.QPushButton("Inspect: Renderer thumbnail")
        live_preview_button = QtWidgets.QPushButton("Inspect: Live preview")
        render_plan_perf_button = QtWidgets.QPushButton("Inspect: Render plan perf")
        smoke_button = QtWidgets.QPushButton("Smoke check")
        launch_button = QtWidgets.QPushButton("啟動地球儀")
        restart_button = QtWidgets.QPushButton("套用並重啟")
        stop_button = QtWidgets.QPushButton("停止本面板啟動的程序")
        for button, tooltip in (
            (profile_replay_button, "Replay/contracts: inspect portable UI/profile replay coverage JSON."),
            (copy_launch_summary_button, "Replay/contracts: copy profile, portable command and launch packet reviewer summary."),
            (timeline_button, "Replay/contracts: inspect Timeline keyframes, runtime state and export options JSON."),
            (ocean_port_button, "Renderer ports: inspect scalar ocean material and sea-state handoff JSON."),
            (ocean_3d_controls_action_button, "Renderer ports: open Taichi 3D Ocean Water scalar controls from the Qt control board."),
            (copy_ocean_summary_button, "Renderer ports: copy Ocean material controls, apply status, sea-state scalar sample and RRKAL governance summary."),
            (hydro_lod_button, "Renderer ports: inspect hydrology layer and LOD hook readiness JSON."),
            (copy_hydro_lod_summary_button, "Renderer ports: copy Hydrology/LOD readiness, runtime evidence and state/ack/pick file summary."),
            (style_routes_button, "Renderer ports: inspect parchment and tactical style renderer route JSON."),
            (copy_style_routes_summary_button, "Renderer ports: copy scientific/nautical/parchment/tactical route readiness and portable command summary."),
            (style_thumbnails_button, "Visual review: inspect style template thumbnail slots and local renderer --output commands."),
            (layer_matrix_button, "Renderer ports: inspect layer capability matrix JSON."),
            (layer_runtime_button, "Renderer ports: inspect layer runtime state and renderer ack JSON."),
            (export_reviewer_packet_button, "Run/profile: export one JSON reviewer packet with clone, launch, research and visual summaries."),
            (module_seams_button, "Replay/contracts: inspect future module extraction seam registry JSON."),
            (copy_module_summary_button, "Replay/contracts: copy module extraction order, stable contracts, Tk boundary and RRKAL governance summary."),
            (clone_ready_button, "Replay/contracts: inspect cross-machine clone readiness JSON."),
            (copy_clone_summary_button, "Replay/contracts: copy clone/setup/profile launch reviewer summary for cross-machine handoff."),
            (layer_pick_button, "Research interaction: inspect selected-layer renderer pick JSON."),
            (selection_state_button, "Selection state: inspect active Qt layer selection, pick history and renderer target JSON."),
            (copy_selection_summary_button, "Selection state: copy active layer, pick bridge and brush/mask scope summary."),
            (layer_ops_button, "Layer ops: inspect active layer operation summary, last operation and replay metadata JSON."),
            (canvas_state_button, "Research interaction: inspect Qt Canvas state, preview metadata and provenance summary."),
            (pin_pick_button, "Research interaction: inspect renderer Pin hover/click pick bridge JSON."),
            (copy_pin_summary_action_button, "Pin overlay: copy pin count, selected pin, source and projection/occlusion summary."),
            (cursor_geo_button, "Research interaction: inspect mouse cursor latitude/longitude geodesy bridge JSON."),
            (copy_cursor_summary_button, "Cursor geodesy: copy source, hit state, latitude/longitude and renderer state/ack bridge summary."),
            (boundary_state_button, "Research interaction: inspect Boundary emphasis, identity warning and renderer ack JSON."),
            (copy_boundary_summary_button, "Boundary emphasis: copy target, tuning values, identity warning and renderer ack summary."),
            (copy_research_summary_button, "Research interaction: copy selection, pin, cursor and boundary summaries as one portable handoff note."),
            (visual_readiness_button, "Visual review: inspect thumbnail/live preview readiness, frame status and missing-frame hints JSON."),
            (copy_visual_summary_button, "Visual review: copy compact thumbnail/live preview readiness summary to clipboard."),
            (copy_style_thumbs_command_button, "Visual review: copy portable command for generating scientific/nautical/parchment/tactical style thumbnails."),
            (copy_style_thumb_status_button, "Visual review: copy local style thumbnail ready/missing status summary."),
            (thumbnail_button, "Visual review: inspect latest renderer thumbnail PNG."),
            (live_preview_button, "Visual review: inspect file-based live renderer preview frame."),
            (render_plan_perf_button, "Renderer diagnostics: inspect queued layer render-plan precompute and single-pass performance contract."),
        ):
            button.setToolTip(tooltip)
            button.setAccessibleDescription(tooltip)
        refresh_button.clicked.connect(self.refresh_command_preview)
        copy_button.clicked.connect(self.copy_command_to_clipboard)
        copy_portable_button.clicked.connect(self.copy_portable_command_to_clipboard)
        save_button.clicked.connect(self.save_profile_dialog)
        load_button.clicked.connect(self.load_profile_dialog)
        open_templates_button.clicked.connect(self.open_template_dir)
        open_local_profiles_button.clicked.connect(self.open_local_profile_dir)
        export_packet_button.clicked.connect(self.export_launch_packet_dialog)
        export_reviewer_packet_button.clicked.connect(self.export_reviewer_packet_dialog)
        profile_replay_button.clicked.connect(self.show_profile_ui_state_replay)
        copy_launch_summary_button.clicked.connect(self.copy_launch_reviewer_summary)
        timeline_button.clicked.connect(self.show_timeline_runtime_state)
        ocean_port_button.clicked.connect(self.show_ocean_material_control_port)
        ocean_3d_controls_action_button.clicked.connect(self.open_taichi_ocean_3d_controls)
        copy_ocean_summary_button.clicked.connect(self.copy_ocean_material_summary)
        hydro_lod_button.clicked.connect(self.show_hydrology_lod_status)
        copy_hydro_lod_summary_button.clicked.connect(self.copy_hydrology_lod_summary)
        style_routes_button.clicked.connect(self.show_style_renderer_routes)
        copy_style_routes_summary_button.clicked.connect(self.copy_style_routes_summary)
        style_thumbnails_button.clicked.connect(self.show_style_thumbnail_slots)
        module_seams_button.clicked.connect(self.show_module_boundary_registry)
        copy_module_summary_button.clicked.connect(self.copy_module_boundary_summary)
        clone_ready_button.clicked.connect(self.show_cross_machine_clone_readiness)
        copy_clone_summary_button.clicked.connect(self.copy_clone_reviewer_summary)
        layer_matrix_button.clicked.connect(self.show_layer_capability_matrix)
        layer_runtime_button.clicked.connect(self.show_layer_runtime_state)
        layer_pick_button.clicked.connect(self.show_layer_pick_state)
        selection_state_button.clicked.connect(self.show_layer_pick_state)
        copy_selection_summary_button.clicked.connect(self.copy_layer_selection_summary)
        layer_ops_button.clicked.connect(self.show_layer_operation_feedback)
        pin_pick_button.clicked.connect(self.show_pin_pick_state)
        copy_pin_summary_action_button.clicked.connect(self.copy_pin_overlay_summary)
        cursor_geo_button.clicked.connect(self.show_cursor_geodesy_state)
        copy_cursor_summary_button.clicked.connect(self.copy_cursor_geodesy_summary)
        boundary_state_button.clicked.connect(self.show_boundary_state)
        copy_boundary_summary_button.clicked.connect(self.copy_boundary_emphasis_summary)
        copy_research_summary_button.clicked.connect(self.copy_research_interaction_summary)
        capabilities_button.clicked.connect(self.show_renderer_capabilities)
        closed_loop_button.clicked.connect(self.show_closed_loop_status)
        layer_manifest_button.clicked.connect(self.show_layer_manifest)
        canvas_state_button.clicked.connect(self.show_canvas_state_preview)
        visual_readiness_button.clicked.connect(self.show_visual_review_readiness)
        copy_visual_summary_button.clicked.connect(self.copy_visual_review_readiness_summary)
        copy_style_thumbs_command_button.clicked.connect(self.copy_style_thumbnail_batch_command)
        copy_style_thumb_status_button.clicked.connect(self.copy_style_thumbnail_readiness_summary)
        thumbnail_button.clicked.connect(self.show_latest_renderer_thumbnail)
        live_preview_button.clicked.connect(self.show_live_renderer_preview)
        render_plan_perf_button.clicked.connect(self.show_layer_render_plan_performance)
        smoke_button.clicked.connect(self.run_smoke_check)
        launch_button.clicked.connect(self.launch_renderer)
        restart_button.clicked.connect(self.restart_renderer)
        stop_button.clicked.connect(self.stop_renderer)
        action_sections = (
            ("Run / profile", (refresh_button, copy_button, copy_portable_button, save_button, load_button, open_templates_button, open_local_profiles_button, export_packet_button, export_reviewer_packet_button)),
            ("Inspect: Replay/contracts", (profile_replay_button, copy_launch_summary_button, timeline_button, module_seams_button, copy_module_summary_button, clone_ready_button, copy_clone_summary_button)),
            ("Inspect: Renderer ports", (hydro_lod_button, copy_hydro_lod_summary_button, ocean_port_button, ocean_3d_controls_action_button, copy_ocean_summary_button, style_routes_button, copy_style_routes_summary_button, layer_matrix_button, layer_runtime_button)),
            ("Inspect: Research interaction", (layer_pick_button, selection_state_button, copy_selection_summary_button, layer_ops_button, canvas_state_button, pin_pick_button, copy_pin_summary_action_button, cursor_geo_button, copy_cursor_summary_button, boundary_state_button, copy_boundary_summary_button, copy_research_summary_button)),
            ("Inspect: Visual review", (visual_readiness_button, copy_visual_summary_button, style_thumbnails_button, copy_style_thumbs_command_button, copy_style_thumb_status_button, thumbnail_button, live_preview_button)),
            ("Renderer diagnostics", (capabilities_button, closed_loop_button, layer_manifest_button, render_plan_perf_button, smoke_button)),
            ("Process", (launch_button, restart_button, stop_button)),
        )
        row = 0
        for section_title, section_buttons in action_sections:
            section_label = QtWidgets.QLabel(section_title)
            section_label.setObjectName("actionSectionHeader")
            actions.addWidget(section_label, row, 0, 1, 4)
            row += 1
            for index, button in enumerate(section_buttons):
                actions.addWidget(button, row + index // 4, index % 4)
            row += (len(section_buttons) + 3) // 4
        right.addWidget(actions_group)

        self.status = QtWidgets.QLabel("尚未啟動 renderer")
        main.addWidget(self.status)

        self._connect_preview_signals()
        self.setStyleSheet(
            """
            QWidget { font-family: 'Microsoft JhengHei UI', 'Segoe UI'; font-size: 10.5pt; }
            QLabel#title { font-size: 18pt; font-weight: 700; }
            QGroupBox { font-weight: 700; border: 1px solid #8aa0b6; border-radius: 8px; margin-top: 12px; padding: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 4px; }
            QPushButton { padding: 7px 10px; }
            QLabel#actionSectionHeader { color: #38516a; font-weight: 700; padding-top: 6px; }
            QPlainTextEdit { font-family: Consolas, 'Cascadia Mono', monospace; }
            QLabel#navigatorPreview { background: #202832; color: #d8e6f3; border: 1px dashed #8aa0b6; }
            QLabel#layerHeader { color: #587087; font-size: 8.5pt; font-weight: 700; }
            QLabel#layerWorkflowHint { color: #405466; background: #eef5f8; border: 1px solid #b7c9d6; border-radius: 8px; padding: 6px 8px; }
            QLabel#profileUiStateReplay { color: #2f4f42; background: #edf7f1; border: 1px solid #9fc7ad; border-radius: 8px; padding: 6px 8px; }
            QLabel#visualReviewReadiness { color: #5b3d18; background: #fff5dd; border: 1px solid #d8b165; border-radius: 8px; padding: 6px 8px; }
            QLabel#layerControlFeedbackStrip { color: #18384a; background: #e8f3ff; border: 1px solid #8fb7d8; border-radius: 8px; padding: 6px 8px; font-weight: 600; }
            QLabel#layerSelectionAffordance { color: #2f4167; background: #edf1ff; border: 1px solid #98a8d8; border-radius: 8px; padding: 6px 8px; font-weight: 600; }
            QLabel#layerHoverAffordance { color: #3d4a24; background: #f4f8e8; border: 1px solid #b5c77f; border-radius: 8px; padding: 6px 8px; font-weight: 600; }
            QLabel#pinOcclusionLegend { color: #4d2f16; background: #fff3dc; border: 1px solid #d7a45d; border-radius: 8px; padding: 6px 8px; font-weight: 600; }
            QWidget#layerRow { border-bottom: 1px solid #d6e0ea; }
            QWidget#layerRow[locked="true"] { background: #f6edf9; border-left: 4px solid #7b4a9e; color: #5a3b68; }
            QWidget#layerRow[selected="true"] { background: #dceeff; border: 1px solid #5b8db8; }
            QLabel#selectedLayer { color: #23435f; font-weight: 700; padding-top: 6px; }
            QLabel#toolPaletteTitle { color: #23435f; font-weight: 700; padding-top: 6px; }
            QLabel#canvasPreview {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #142331, stop:0.52 #1f4d5e, stop:1 #d7c29b);
                color: #f3f7f9;
                border: 2px solid #5b8db8;
                border-radius: 10px;
                font-size: 13pt;
                font-weight: 700;
                padding: 16px;
            }
            QLabel#canvasMeta { color: #31475a; font-weight: 600; }
            """
        )

    def _build_menu_bar(self) -> None:
        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction("Save Profile", self.save_profile_dialog)
        file_menu.addAction("Load Profile", self.load_profile_dialog)
        file_menu.addAction("Export Launch Packet", self.export_launch_packet_dialog)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        renderer_menu = self.menuBar().addMenu("Renderer")
        renderer_menu.addAction("Launch", self.launch_renderer)
        renderer_menu.addAction("Apply and Restart", self.restart_renderer)
        renderer_menu.addAction("Stop", self.stop_renderer)
        renderer_menu.addSeparator()
        renderer_menu.addAction("Capabilities JSON", self.show_renderer_capabilities)
        renderer_menu.addAction("Closed-loop Status JSON", self.show_closed_loop_status)
        renderer_menu.addAction("Layer Manifest JSON", self.show_layer_manifest)
        renderer_menu.addAction("Inspect: Visual readiness", self.show_visual_review_readiness)
        renderer_menu.addAction("Inspect: Renderer thumbnail", self.show_latest_renderer_thumbnail)
        renderer_menu.addAction("Inspect: Live preview", self.show_live_renderer_preview)

        window_menu = self.menuBar().addMenu("Window")
        window_menu.addAction("Open Template Folder", self.open_template_dir)
        window_menu.addAction("Open Local Profile Folder", self.open_local_profile_dir)
        window_menu.addSeparator()
        window_menu.addAction("Save Workspace Layout", self.save_workspace_layout)
        window_menu.addAction("Load Workspace Layout", self.load_workspace_layout)
        window_menu.addAction("Reset Saved Workspace Layout", self.reset_workspace_layout)
        workspace_presets = window_menu.addMenu("Workspace Presets")
        workspace_presets.addAction("Default", lambda _checked=False: self.apply_workspace_preset("default"))
        workspace_presets.addAction("Maritime", lambda _checked=False: self.apply_workspace_preset("maritime"))
        workspace_presets.addAction("Tactical", lambda _checked=False: self.apply_workspace_preset("tactical"))
        workspace_presets.addAction("Parchment", lambda _checked=False: self.apply_workspace_preset("parchment"))
        workspace_presets.addAction("Review", lambda _checked=False: self.apply_workspace_preset("review"))

        help_menu = self.menuBar().addMenu("Help")
        help_menu.addAction("Smoke Check", self.run_smoke_check)

    def _build_tool_dock(self) -> None:
        dock = QtWidgets.QDockWidget("Tools", self)
        dock.setObjectName("toolsDock")
        dock.setAllowedAreas(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea | QtCore.Qt.DockWidgetArea.RightDockWidgetArea)
        tools = QtWidgets.QWidget(dock)
        layout = QtWidgets.QVBoxLayout(tools)
        layout.setContentsMargins(8, 8, 8, 8)
        palette_title = QtWidgets.QLabel("工具箱 / Tool Palette")
        palette_title.setObjectName("toolPaletteTitle")
        layout.addWidget(palette_title)
        tool_grid = QtWidgets.QGridLayout()
        for index, (mode, label, hint) in enumerate(TOOL_MODES):
            button = QtWidgets.QToolButton()
            button.setText(label)
            button.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextOnly)
            button.setCheckable(True)
            button.setToolTip(hint)
            button.clicked.connect(lambda _checked=False, tool_mode=mode: self.set_active_tool(tool_mode))
            self.tool_buttons[mode] = button
            tool_grid.addWidget(button, index // 2, index % 2)
        layout.addLayout(tool_grid)
        self.tool_target_label = QtWidgets.QLabel("Target layer: -")
        self.tool_target_label.setWordWrap(True)
        layout.addWidget(self.tool_target_label)
        tool_note = QtWidgets.QLabel("Select 只負責選取/指定 active layer；Brush/Mask 暫不納入本輪 UI。")
        tool_note.setWordWrap(True)
        layout.addWidget(tool_note)
        pin_group = QtWidgets.QGroupBox("Pin Annotation")
        pin_form = QtWidgets.QFormLayout(pin_group)
        self.pin_type_combo = QtWidgets.QComboBox()
        self.pin_type_combo.addItems(PIN_TYPES)
        self.pin_label_edit = QtWidgets.QLineEdit("Station A")
        self.pin_note_edit = QtWidgets.QLineEdit("Geodetic marker; renderer rotates and occludes it with the globe")
        self.pin_lat_edit = QtWidgets.QLineEdit("0.0")
        self.pin_lon_edit = QtWidgets.QLineEdit("0.0")
        self.pin_priority_spin = QtWidgets.QSpinBox()
        self.pin_priority_spin.setRange(0, 100)
        self.pin_priority_spin.setValue(50)
        self.pin_priority_spin.setToolTip("Renderer label priority: selected Pin wins first, then higher priority labels are placed earlier.")
        self.pin_label_mode_combo = QtWidgets.QComboBox()
        for mode, label, hint in PIN_LABEL_MODES:
            self.pin_label_mode_combo.addItem(label, mode)
            self.pin_label_mode_combo.setItemData(self.pin_label_mode_combo.count() - 1, hint, QtCore.Qt.ItemDataRole.ToolTipRole)
        self.pin_label_mode_combo.setToolTip("Renderer Pin label visibility mode.")
        self.pin_label_min_priority_spin = QtWidgets.QSpinBox()
        self.pin_label_min_priority_spin.setRange(0, 100)
        self.pin_label_min_priority_spin.setValue(50)
        self.pin_label_min_priority_spin.setToolTip("Priority mode only: labels below this threshold are hidden unless selected.")
        self.pin_type_combo.currentTextChanged.connect(lambda _text, self=self: self.refresh_tool_target())
        self.pin_label_edit.textChanged.connect(lambda _text, self=self: self.refresh_tool_target())
        self.pin_note_edit.textChanged.connect(lambda _text, self=self: self.refresh_tool_target())
        self.pin_lat_edit.textChanged.connect(lambda _text, self=self: self.refresh_tool_target())
        self.pin_lon_edit.textChanged.connect(lambda _text, self=self: self.refresh_tool_target())
        self.pin_lat_edit.textChanged.connect(lambda _text, self=self: self.mark_pin_coordinate_manual())
        self.pin_lon_edit.textChanged.connect(lambda _text, self=self: self.mark_pin_coordinate_manual())
        self.pin_priority_spin.valueChanged.connect(lambda _value, self=self: self.refresh_tool_target())
        self.pin_label_mode_combo.currentIndexChanged.connect(lambda _value, self=self: self.refresh_tool_target())
        self.pin_label_min_priority_spin.valueChanged.connect(lambda _value, self=self: self.refresh_tool_target())
        pin_form.addRow("Type", self.pin_type_combo)
        pin_form.addRow("Label", self.pin_label_edit)
        pin_form.addRow("Latitude", self.pin_lat_edit)
        pin_form.addRow("Longitude", self.pin_lon_edit)
        pin_form.addRow("Label Priority", self.pin_priority_spin)
        pin_form.addRow("Label Mode", self.pin_label_mode_combo)
        pin_form.addRow("Min Label Priority", self.pin_label_min_priority_spin)
        pin_form.addRow("Note", self.pin_note_edit)
        self.pin_cursor_fill_label = QtWidgets.QLabel(f"Pin cursor fill: {self.pin_cursor_fill_source_text()}")
        self.pin_cursor_fill_label.setWordWrap(True)
        pin_form.addRow("Cursor Fill", self.pin_cursor_fill_label)
        pin_contract = pin_projection_contract_packet()
        pin_projection_note = QtWidgets.QLabel(str(pin_contract.get("qt_projection_note", "")))
        pin_projection_note.setObjectName("pinProjectionNote")
        pin_projection_note.setWordWrap(True)
        pin_form.addRow("Projection", pin_projection_note)
        pin_occlusion_legend = QtWidgets.QLabel(str(pin_contract.get("qt_occlusion_legend_text", "")))
        pin_occlusion_legend.setObjectName("pinOcclusionLegend")
        pin_occlusion_legend.setWordWrap(True)
        pin_form.addRow("Occlusion", pin_occlusion_legend)
        pin_actions = QtWidgets.QHBoxLayout()
        add_pin_button = QtWidgets.QPushButton("加入 Pin")
        remove_pin_button = QtWidgets.QPushButton("移除選取 Pin")
        use_cursor_button = QtWidgets.QPushButton("用游標填入 Pin")
        show_pin_pick_button = QtWidgets.QPushButton("顯示 Pin pick JSON")
        copy_pin_summary_button = QtWidgets.QPushButton("複製 Pin 摘要")
        add_pin_button.clicked.connect(self.add_pin_marker)
        remove_pin_button.clicked.connect(self.remove_selected_pin_marker)
        use_cursor_button.clicked.connect(self.fill_pin_from_cursor)
        show_pin_pick_button.clicked.connect(self.show_pin_pick_state)
        copy_pin_summary_button.clicked.connect(self.copy_pin_overlay_summary)
        pin_actions.addWidget(add_pin_button)
        pin_actions.addWidget(remove_pin_button)
        pin_actions.addWidget(use_cursor_button)
        pin_actions.addWidget(show_pin_pick_button)
        pin_actions.addWidget(copy_pin_summary_button)
        pin_form.addRow(pin_actions)
        self.pin_list = QtWidgets.QListWidget()
        self.pin_list.setObjectName("pinList")
        self.pin_list.setMinimumHeight(110)
        self.pin_list.currentRowChanged.connect(self.select_pin_marker)
        pin_form.addRow("Pins", self.pin_list)
        self.pin_input_ack_label = QtWidgets.QLabel(f"Renderer input ack: waiting for {PIN_INPUT_ACK_PATH.name}")
        self.pin_input_ack_label.setWordWrap(True)
        pin_form.addRow("Renderer Input", self.pin_input_ack_label)
        self.pin_pick_state_label = QtWidgets.QLabel(f"Renderer bridge: waiting for {PIN_PICK_STATE_PATH.name}")
        self.pin_pick_state_label.setWordWrap(True)
        pin_form.addRow("Renderer Pick", self.pin_pick_state_label)
        self.pin_pick_ack_label = QtWidgets.QLabel(f"Qt ack: waiting for {PIN_PICK_ACK_PATH.name}")
        self.pin_pick_ack_label.setWordWrap(True)
        pin_form.addRow("Qt Ack", self.pin_pick_ack_label)
        pin_form.addRow("Status", QtWidgets.QLabel("Manual lat/lon Pins; renderer click/hover sync uses JSON bridge."))
        layout.addWidget(pin_group)

        quick_title = QtWidgets.QLabel("快捷 / Presets")
        quick_title.setObjectName("toolPaletteTitle")
        layout.addWidget(quick_title)
        tool_actions = (
            ("Baseline", self.apply_baseline),
            ("Maritime", self.apply_maritime),
            ("Parchment", self.apply_parchment),
            ("Tactical", self.apply_tactical),
            ("Smoke", self.run_smoke_check),
            ("Caps", self.show_renderer_capabilities),
            ("Loops", self.show_closed_loop_status),
            ("Layers", self.show_layer_manifest),
        )
        for label, callback in tool_actions:
            button = QtWidgets.QToolButton()
            button.setText(label)
            button.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextOnly)
            button.clicked.connect(callback)
            layout.addWidget(button)
        self.set_active_tool("move")
        layout.addStretch(1)
        dock.setWidget(tools)
        self.docks["tools"] = dock
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, dock)

    def _build_auxiliary_docks(self) -> None:
        navigator_dock = QtWidgets.QDockWidget("Navigator", self)
        navigator_dock.setObjectName("navigatorDock")
        navigator = QtWidgets.QWidget(navigator_dock)
        navigator_layout = QtWidgets.QVBoxLayout(navigator)
        navigator_layout.setContentsMargins(10, 10, 10, 10)
        preview = QtWidgets.QLabel(
            "Navigator preview\n"
            "Live renderer pixels are available from the central Canvas Preview."
        )
        preview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        preview.setMinimumHeight(120)
        preview.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        preview.setObjectName("navigatorPreview")
        navigator_layout.addWidget(preview)
        zoom_row = QtWidgets.QHBoxLayout()
        zoom_row.addWidget(QtWidgets.QLabel("Zoom"))
        self.zoom_placeholder = QtWidgets.QLineEdit("100%")
        self.zoom_placeholder.setEnabled(False)
        zoom_row.addWidget(self.zoom_placeholder)
        navigator_layout.addLayout(zoom_row)
        navigator_dock.setWidget(navigator)
        self.docks["navigator"] = navigator_dock
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, navigator_dock)

        history_dock = QtWidgets.QDockWidget("History", self)
        history_dock.setObjectName("historyDock")
        history_panel = QtWidgets.QWidget(history_dock)
        history_layout = QtWidgets.QVBoxLayout(history_panel)
        history_layout.setContentsMargins(8, 8, 8, 8)
        self.document_undo_label = QtWidgets.QLabel("Document history: manual snapshot; undo=0 redo=0")
        self.document_undo_label.setWordWrap(True)
        history_layout.addWidget(self.document_undo_label)
        self.history_list = QtWidgets.QListWidget()
        for item in (
            "✅ Qt Studio workspace loaded",
            "✅ Profile/template launch flow",
            "✅ Layer manifest/capabilities preview",
            "✅ Live renderer layer visibility/opacity/blend sync",
            "✅ Selected-layer renderer picking bridge",
            "✅ Layer stack undo snapshots",
            "🚧 Timeline/keyframes",
            "✅ Manual document snapshot undo/redo",
        ):
            self.history_list.addItem(item)
        for item in self.layer_runtime_history:
            self.history_list.insertItem(0, item)
        for item in self.pin_pick_history:
            self.history_list.insertItem(0, item)
        history_layout.addWidget(self.history_list)
        document_history_actions = QtWidgets.QHBoxLayout()
        snapshot_button = QtWidgets.QPushButton("Snapshot")
        snapshot_button.clicked.connect(lambda: self.capture_document_snapshot("Manual snapshot"))
        undo_document_button = QtWidgets.QPushButton("Undo")
        undo_document_button.clicked.connect(self.undo_document_snapshot)
        redo_document_button = QtWidgets.QPushButton("Redo")
        redo_document_button.clicked.connect(self.redo_document_snapshot)
        document_history_actions.addWidget(snapshot_button)
        document_history_actions.addWidget(undo_document_button)
        document_history_actions.addWidget(redo_document_button)
        history_layout.addLayout(document_history_actions)
        history_dock.setWidget(history_panel)
        self.docks["history"] = history_dock
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, history_dock)

        timeline_dock = QtWidgets.QDockWidget("Timeline", self)
        timeline_dock.setObjectName("timelineDock")
        timeline = QtWidgets.QWidget(timeline_dock)
        timeline_layout = QtWidgets.QVBoxLayout(timeline)
        timeline_layout.setContentsMargins(10, 10, 10, 10)
        timeline_note = QtWidgets.QLabel(
            "Timeline/keyframes：Qt storage、renderer step playback、ocean/camera/layer interpolation、PNG/GIF/MP4 export 已接上；blend/visibility fade 仍待做。"
        )
        timeline_note.setWordWrap(True)
        timeline_layout.addWidget(timeline_note)
        playhead = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        playhead.setRange(0, 100)
        playhead.setValue(0)
        playhead.setEnabled(False)
        timeline_layout.addWidget(playhead)
        camera_group = QtWidgets.QGroupBox("Camera keyframe")
        camera_form = QtWidgets.QFormLayout(camera_group)
        self.timeline_camera_yaw_spin = QtWidgets.QDoubleSpinBox()
        self.timeline_camera_yaw_spin.setRange(-360.0, 360.0)
        self.timeline_camera_yaw_spin.setDecimals(2)
        self.timeline_camera_yaw_spin.setSingleStep(5.0)
        self.timeline_camera_yaw_spin.setSuffix(" deg")
        self.timeline_camera_yaw_spin.setToolTip("Renderer yaw; saved into Timeline keyframes and applied by the Taichi renderer.")
        self.timeline_camera_pitch_spin = QtWidgets.QDoubleSpinBox()
        self.timeline_camera_pitch_spin.setRange(-89.0, 89.0)
        self.timeline_camera_pitch_spin.setDecimals(2)
        self.timeline_camera_pitch_spin.setSingleStep(5.0)
        self.timeline_camera_pitch_spin.setSuffix(" deg")
        self.timeline_camera_pitch_spin.setToolTip("Renderer pitch, clamped to avoid flipping the globe camera.")
        self.timeline_camera_zoom_spin = QtWidgets.QDoubleSpinBox()
        self.timeline_camera_zoom_spin.setRange(0.08, 4.0)
        self.timeline_camera_zoom_spin.setDecimals(3)
        self.timeline_camera_zoom_spin.setSingleStep(0.05)
        self.timeline_camera_zoom_spin.setValue(1.0)
        self.timeline_camera_zoom_spin.setToolTip("Renderer zoom scale; smaller values zoom in, larger values zoom out.")
        for spin in (
            self.timeline_camera_yaw_spin,
            self.timeline_camera_pitch_spin,
            self.timeline_camera_zoom_spin,
        ):
            spin.valueChanged.connect(lambda _value, self=self: self.refresh_timeline_state_label())
        camera_form.addRow("Yaw", self.timeline_camera_yaw_spin)
        camera_form.addRow("Pitch", self.timeline_camera_pitch_spin)
        camera_form.addRow("Zoom", self.timeline_camera_zoom_spin)
        timeline_layout.addWidget(camera_group)
        export_group = QtWidgets.QGroupBox("Renderer export")
        export_form = QtWidgets.QFormLayout(export_group)
        self.timeline_export_enabled_check = QtWidgets.QCheckBox("Export on renderer launch")
        self.timeline_export_enabled_check.setToolTip(
            "When enabled, the next renderer launch writes Timeline PNG frames and optional GIF/MP4 into the selected state path."
        )
        self.timeline_export_dir_edit = QtWidgets.QLineEdit(str(TIMELINE_EXPORT_DIR))
        self.timeline_export_dir_edit.setToolTip("Renderer export directory; kept under state/ by default and not committed.")
        self.timeline_export_frames_spin = QtWidgets.QSpinBox()
        self.timeline_export_frames_spin.setRange(1, 9999)
        self.timeline_export_frames_spin.setValue(24)
        self.timeline_export_fps_spin = QtWidgets.QDoubleSpinBox()
        self.timeline_export_fps_spin.setRange(1.0, 240.0)
        self.timeline_export_fps_spin.setDecimals(2)
        self.timeline_export_fps_spin.setValue(24.0)
        self.timeline_export_gif_check = QtWidgets.QCheckBox("GIF fallback")
        self.timeline_export_gif_check.setChecked(True)
        self.timeline_export_mp4_check = QtWidgets.QCheckBox("MP4 video")
        self.timeline_export_mp4_check.setChecked(False)
        for widget in (
            self.timeline_export_enabled_check,
            self.timeline_export_dir_edit,
            self.timeline_export_frames_spin,
            self.timeline_export_fps_spin,
            self.timeline_export_gif_check,
            self.timeline_export_mp4_check,
        ):
            if isinstance(widget, QtWidgets.QLineEdit):
                widget.textChanged.connect(lambda _value, self=self: self.refresh_timeline_state_label())
            elif isinstance(widget, QtWidgets.QAbstractSpinBox):
                widget.valueChanged.connect(lambda _value, self=self: self.refresh_timeline_state_label())
            else:
                widget.stateChanged.connect(lambda _value, self=self: self.refresh_timeline_state_label())
        export_form.addRow(self.timeline_export_enabled_check)
        export_form.addRow("Directory", self.timeline_export_dir_edit)
        export_form.addRow("Frames", self.timeline_export_frames_spin)
        export_form.addRow("FPS", self.timeline_export_fps_spin)
        export_form.addRow("Containers", self.timeline_export_gif_check)
        export_form.addRow("", self.timeline_export_mp4_check)
        timeline_layout.addWidget(export_group)
        self.timeline_state_label = QtWidgets.QLabel(
            "Timeline status: construction; planned targets include ocean/material and camera states."
        )
        self.timeline_state_label.setWordWrap(True)
        timeline_layout.addWidget(self.timeline_state_label)
        self.timeline_ack_label = QtWidgets.QLabel(f"Timeline renderer ack: waiting for {TIMELINE_ACK_PATH.name}")
        self.timeline_ack_label.setWordWrap(True)
        timeline_layout.addWidget(self.timeline_ack_label)
        self.timeline_keyframe_list = QtWidgets.QListWidget()
        self.timeline_keyframe_list.setMinimumHeight(90)
        timeline_layout.addWidget(self.timeline_keyframe_list)
        timeline_actions = QtWidgets.QHBoxLayout()
        add_keyframe = QtWidgets.QPushButton("Add keyframe")
        add_keyframe.clicked.connect(self.add_timeline_keyframe)
        apply_keyframe = QtWidgets.QPushButton("Apply selected")
        apply_keyframe.clicked.connect(self.apply_selected_timeline_keyframe)
        step_keyframe = QtWidgets.QPushButton("Next")
        step_keyframe.clicked.connect(self.step_timeline_keyframe)
        play_keyframes = QtWidgets.QPushButton("Play UI preview")
        play_keyframes.clicked.connect(self.play_timeline_keyframes)
        stop_keyframes = QtWidgets.QPushButton("Stop")
        stop_keyframes.clicked.connect(self.stop_timeline_keyframes)
        clear_keyframes = QtWidgets.QPushButton("Clear")
        clear_keyframes.clicked.connect(self.clear_timeline_keyframes)
        timeline_actions.addWidget(add_keyframe)
        timeline_actions.addWidget(apply_keyframe)
        timeline_actions.addWidget(step_keyframe)
        timeline_actions.addWidget(play_keyframes)
        timeline_actions.addWidget(stop_keyframes)
        timeline_actions.addWidget(clear_keyframes)
        timeline_layout.addLayout(timeline_actions)
        timeline_dock.setWidget(timeline)
        self.docks["timeline"] = timeline_dock
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, timeline_dock)

        provenance_dock = QtWidgets.QDockWidget("Provenance", self)
        provenance_dock.setObjectName("provenanceDock")
        provenance = QtWidgets.QWidget(provenance_dock)
        provenance_layout = QtWidgets.QVBoxLayout(provenance)
        provenance_layout.setContentsMargins(10, 10, 10, 10)
        provenance_note = QtWidgets.QLabel("科研可重現性摘要：目前 UI 狀態、資料來源、圖層、profile 與可攜命令。")
        provenance_note.setWordWrap(True)
        provenance_layout.addWidget(provenance_note)
        self.provenance_text = QtWidgets.QPlainTextEdit()
        self.provenance_text.setReadOnly(True)
        self.provenance_text.setMinimumHeight(180)
        provenance_layout.addWidget(self.provenance_text)
        copy_provenance = QtWidgets.QPushButton("複製 provenance summary")
        copy_provenance.clicked.connect(self.copy_research_provenance)
        provenance_layout.addWidget(copy_provenance)
        provenance_dock.setWidget(provenance)
        self.docks["provenance"] = provenance_dock
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, provenance_dock)

    @QtCore.pyqtSlot()
    def save_workspace_layout(self) -> None:
        WORKSPACE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": "rrkal_displaytools.qt_workspace_layout.v1",
            "geometry": bytes(self.saveGeometry().toBase64()).decode("ascii"),
            "window_state": bytes(self.saveState().toBase64()).decode("ascii"),
        }
        WORKSPACE_STATE_PATH.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.status.setText(f"已儲存 workspace layout：{WORKSPACE_STATE_PATH}")
        self.statusBar().showMessage("Workspace layout saved", 4000)

    def load_workspace_layout(self, silent: bool = False) -> None:
        if not WORKSPACE_STATE_PATH.exists():
            if not silent:
                self.status.setText("尚未儲存 workspace layout")
            return
        try:
            payload = json.loads(WORKSPACE_STATE_PATH.read_text(encoding="utf-8"))
            geometry = QtCore.QByteArray.fromBase64(str(payload.get("geometry", "")).encode("ascii"))
            window_state = QtCore.QByteArray.fromBase64(str(payload.get("window_state", "")).encode("ascii"))
            if not geometry.isEmpty():
                self.restoreGeometry(geometry)
            if not window_state.isEmpty():
                self.restoreState(window_state)
        except Exception as exc:
            if not silent:
                self.status.setText(f"Workspace layout 載入失敗：{exc}")
            return
        if not silent:
            self.status.setText(f"已載入 workspace layout：{WORKSPACE_STATE_PATH}")
        self.statusBar().showMessage("Workspace layout loaded", 4000)

    @QtCore.pyqtSlot()
    def reset_workspace_layout(self) -> None:
        if WORKSPACE_STATE_PATH.exists():
            WORKSPACE_STATE_PATH.unlink()
        self.status.setText("已移除已儲存 workspace layout；下次啟動使用預設佈局")
        self.statusBar().showMessage("Saved workspace layout reset", 4000)

    def apply_workspace_preset(self, preset: str) -> None:
        for dock in self.docks.values():
            dock.setFloating(False)
            dock.show()
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, self.docks["tools"])
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.docks["layers"])
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.docks["properties"])
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.docks["navigator"])
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.docks["history"])
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.docks["timeline"])
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.docks["provenance"])
        if preset == "maritime":
            self.apply_maritime()
            self.tabifyDockWidget(self.docks["layers"], self.docks["properties"])
            self.docks["layers"].raise_()
        elif preset == "tactical":
            self.apply_tactical()
            self.tabifyDockWidget(self.docks["navigator"], self.docks["history"])
            self.tabifyDockWidget(self.docks["history"], self.docks["timeline"])
            self.docks["layers"].raise_()
        elif preset == "parchment":
            self.apply_parchment()
            self.tabifyDockWidget(self.docks["properties"], self.docks["navigator"])
            self.docks["properties"].raise_()
        elif preset == "review":
            self.apply_baseline()
            self.tabifyDockWidget(self.docks["layers"], self.docks["properties"])
            self.tabifyDockWidget(self.docks["navigator"], self.docks["history"])
            self.tabifyDockWidget(self.docks["history"], self.docks["timeline"])
            self.tabifyDockWidget(self.docks["history"], self.docks["provenance"])
            self.docks["history"].raise_()
        else:
            self.apply_baseline()
            self.docks["layers"].raise_()
        self.status.setText(f"已套用 workspace preset：{preset}")
        self.statusBar().showMessage(f"Workspace preset applied: {preset}", 4000)

    def _group(self, title: str) -> QtWidgets.QGroupBox:
        return QtWidgets.QGroupBox(title)

    def _combo(self, values: tuple[str, ...]) -> QtWidgets.QComboBox:
        combo = QtWidgets.QComboBox()
        combo.addItems(values)
        return combo

    def _connect_preview_signals(self) -> None:
        for combo in (self.style_combo, self.ui_combo, self.topo_combo, self.data_combo):
            combo.currentTextChanged.connect(self.refresh_command_preview)
        for edit in (
            self.width_edit,
            self.height_edit,
            self.topo_step_edit,
            self.arch_edit,
            self.rrkal_manifest_ref_edit,
            self.wave_edit,
            self.roughness_edit,
            self.foam_edit,
        ):
            edit.textChanged.connect(self.refresh_command_preview)

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if event.type() in (QtCore.QEvent.Type.Enter, QtCore.QEvent.Type.Leave):
            layer_key = self.layer_hover_event_targets.get(id(watched))
            if layer_key is not None:
                if event.type() == QtCore.QEvent.Type.Enter:
                    self.set_layer_hover_affordance(layer_key)
                else:
                    self.clear_layer_hover_affordance(layer_key)
                return super().eventFilter(watched, event)
        if event.type() == QtCore.QEvent.Type.MouseButtonDblClick:
            layer_key = self.boundary_layer_event_targets.get(id(watched))
            if layer_key is not None:
                self.open_boundary_emphasis_dialog(layer_key)
                return True
        if watched is self.canvas_preview_label and event.type() == QtCore.QEvent.Type.MouseMove:
            position = self.qt_event_position(event)
            if position is None:
                return super().eventFilter(watched, event)
            width = max(1, self.canvas_preview_label.width() if self.canvas_preview_label is not None else 1)
            height = max(1, self.canvas_preview_label.height() if self.canvas_preview_label is not None else 1)
            x_ratio = min(max(position.x() / width, 0.0), 1.0)
            y_ratio = min(max(position.y() / height, 0.0), 1.0)
            self.cursor_longitude = x_ratio * 360.0 - 180.0
            self.cursor_latitude = 90.0 - y_ratio * 180.0
            self.refresh_canvas_preview()
        if watched is self.canvas_preview_label and event.type() == QtCore.QEvent.Type.MouseButtonPress:
            if self.active_tool == "select" and event.button() == QtCore.Qt.MouseButton.LeftButton:
                position = self.qt_event_position(event)
                if position is None:
                    return super().eventFilter(watched, event)
                key = self.canvas_layer_hit_key(float(position.y()))
                if key is not None:
                    label = next((text for layer_key, text in LAYER_LABELS if layer_key == key), key)
                    self.select_layer(key)
                    self.status.setText(f"Canvas Select 命中圖層：{label}")
                    return True
        return super().eventFilter(watched, event)

    def qt_event_position(self, event: QtCore.QEvent) -> object | None:
        position_getter = getattr(event, "position", None)
        if callable(position_getter):
            try:
                return position_getter()
            except RuntimeError:
                return None
        pos_getter = getattr(event, "pos", None)
        if callable(pos_getter):
            try:
                return pos_getter()
            except RuntimeError:
                return None
        return None

    def build_command(self) -> list[str]:
        self.write_timeline_runtime_state()
        cmd = [
            sys.executable,
            str(RENDERER),
            "--style-profile",
            self.style_combo.currentText(),
            "--ui",
            self.ui_combo.currentText(),
            "--topo-source",
            self.topo_combo.currentText(),
            "--data-mode",
            self.data_combo.currentText(),
            "--width",
            self.width_edit.text().strip() or "1280",
            "--height",
            self.height_edit.text().strip() or "720",
            "--topo-step",
            self.topo_step_edit.text().strip() or "48",
            "--ti-arch",
            self.arch_edit.text().strip() or "gpu",
            "--ocean-wave-strength",
            self.wave_edit.text().strip() or "0.22",
            "--ocean-roughness",
            self.roughness_edit.text().strip() or "0.28",
            "--ocean-foam",
            self.foam_edit.text().strip() or "0.12",
            "--preview-frame-file",
            str(RENDERER_PREVIEW_FRAME_PATH),
            "--preview-frame-interval",
            str(RENDERER_PREVIEW_FRAME_INTERVAL_S),
        ]
        rrkal_manifest_ref = self.rrkal_manifest_ref_edit.text().strip()
        if rrkal_manifest_ref:
            cmd.extend(["--rrkal-data-manifest-ref", rrkal_manifest_ref])
        for key, flag in BOOL_FLAGS.items():
            enabled = self.checks[key].isChecked()
            cmd.append(f"--{flag}" if enabled else f"--no-{flag}")
        cmd.extend(
            [
                "--pin-label-mode",
                self.current_pin_label_mode(),
                "--pin-label-min-priority",
                str(self.pin_label_min_priority_spin.value() if self.pin_label_min_priority_spin is not None else 50),
                "--pin-pick-state-file",
                str(PIN_PICK_STATE_PATH),
                "--pin-input-ack-file",
                str(PIN_INPUT_ACK_PATH),
                "--boundary-highlight-json",
                json.dumps(self.collect_boundary_highlight_state(), ensure_ascii=False),
                "--boundary-highlight-ack-file",
                str(BOUNDARY_HIGHLIGHT_ACK_PATH),
                "--layer-runtime-state-file",
                str(LAYER_RUNTIME_STATE_PATH),
                "--layer-runtime-ack-file",
                str(LAYER_RUNTIME_ACK_PATH),
                "--layer-pick-state-file",
                str(LAYER_PICK_STATE_PATH),
                "--cursor-geodesy-state-file",
                str(CURSOR_GEODESY_STATE_PATH),
                "--cursor-geodesy-ack-file",
                str(CURSOR_GEODESY_ACK_PATH),
                "--timeline-state-file",
                str(TIMELINE_STATE_PATH),
                "--timeline-ack-file",
                str(TIMELINE_ACK_PATH),
            ]
        )
        timeline_export = self.collect_timeline_export_options()
        if timeline_export.get("enabled") is True:
            cmd.extend(
                [
                    "--timeline-export-dir",
                    str(timeline_export["export_dir"]),
                    "--timeline-export-frames",
                    str(timeline_export["frame_count"]),
                    "--timeline-export-fps",
                    str(timeline_export["fps"]),
                    "--timeline-export-manifest",
                    str(timeline_export["manifest_file"]),
                ]
            )
            if timeline_export.get("gif_enabled") is True:
                cmd.extend(["--timeline-export-gif", str(timeline_export["gif_file"])])
            if timeline_export.get("mp4_enabled") is True:
                cmd.extend(["--timeline-export-mp4", str(timeline_export["mp4_file"])])
        pins = self.collect_research_pins()
        if pins:
            cmd.extend(
                [
                    "--pin-json",
                    json.dumps(
                        {
                            "pins": pins,
                            "selected_pin_id": self.selected_pin_id,
                            "source": "rrkal_displaytools_qt_panel",
                        },
                        ensure_ascii=False,
                    ),
                ]
            )
        return cmd

    def build_portable_command(self) -> list[str]:
        return ["py", "-3", "taichi_global_bathymetry.py", *self.build_command()[2:]]

    def collect_profile(self) -> dict[str, object]:
        return {
            "schema": "rrkal_displaytools.qt_panel_profile.v1",
            "renderer": {
                "style_profile": self.style_combo.currentText(),
                "ui_backend": self.ui_combo.currentText(),
                "topo_source": self.topo_combo.currentText(),
                "data_mode": self.data_combo.currentText(),
                "width": self.width_edit.text().strip(),
                "height": self.height_edit.text().strip(),
                "topo_step": self.topo_step_edit.text().strip(),
                "taichi_arch": self.arch_edit.text().strip(),
                "rrkal_data_manifest_ref": self.rrkal_manifest_ref_edit.text().strip(),
            },
            "ocean_material": {
                "wave_strength": self.wave_edit.text().strip(),
                "roughness": self.roughness_edit.text().strip(),
                "foam": self.foam_edit.text().strip(),
            },
            "layers": {key: check.isChecked() for key, check in self.checks.items()},
            "layer_filter": self.collect_layer_filter_state(),
            "layer_group_view": self.collect_layer_group_view_state(),
            "selected_layer": self.selected_layer_key,
            "selected_pin_id": self.selected_pin_id,
            "layer_stack_ui": self.collect_layer_stack_ui(),
            "tool_state": self.collect_tool_state(),
            "pins": self.collect_research_pins(),
            "boundary_highlight": self.collect_boundary_highlight_state(),
            "canvas_preview": self.collect_canvas_preview_state(),
            "timeline_export": self.collect_timeline_export_options(),
            "timeline_keyframes": self.timeline_keyframes,
        }

    def collect_ocean_material_control_port(self) -> dict[str, object]:
        return ocean_material_control_port_packet(
            {
                "wave_strength": self.wave_edit.text().strip(),
                "roughness": self.roughness_edit.text().strip(),
                "foam": self.foam_edit.text().strip(),
            },
            "rrkal_displaytools_qt_panel",
        )

    def ocean_3d_control_summary_text(self) -> str:
        packet = self.collect_ocean_material_control_port()
        controls = packet.get("material_controls") if isinstance(packet.get("material_controls"), dict) else {}
        panel = packet.get("qt_control_panel") if isinstance(packet.get("qt_control_panel"), dict) else {}
        return (
            "Taichi 3D Ocean: "
            f"wave={controls.get('wave_strength')}; "
            f"roughness={controls.get('roughness')}; "
            f"foam={controls.get('foam')}; "
            f"board={panel.get('control_board_status', 'wired_default_visible')}; "
            f"dialog={panel.get('qt_dialog_action', 'open_taichi_ocean_3d_controls')}; "
            f"followup={panel.get('render_pipeline_followup', 'post_decoupling_precompute_layer_render_plan_then_single_render_pass')}"
        )

    def refresh_ocean_3d_control_summary(self) -> None:
        summary = self.ocean_3d_control_summary_text()
        if hasattr(self, "ocean_3d_control_label"):
            self.ocean_3d_control_label.setText(summary)
        if hasattr(self, "ocean_3d_control_board_label"):
            self.ocean_3d_control_board_label.setText(f"Ocean 3D quick controls: {summary}")

    def open_taichi_ocean_3d_controls(self) -> None:
        def bounded(value: object, default: float, lower: float, upper: float) -> float:
            try:
                number = float(value)
            except (TypeError, ValueError):
                number = default
            return max(lower, min(number, upper))

        def scalar_text(value: float) -> str:
            text = f"{value:.3f}".rstrip("0").rstrip(".")
            return text or "0"

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Taichi 3D Ocean Water")
        layout = QtWidgets.QVBoxLayout(dialog)
        intro = QtWidgets.QLabel(
            "Taichi 3D Ocean Water controls write scalar ocean material values into the Qt profile, launch packet and renderer CLI flags."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)
        summary = QtWidgets.QLabel(self.ocean_3d_control_summary_text())
        summary.setObjectName("taichiOcean3DControlDialogSummary")
        summary.setWordWrap(True)
        layout.addWidget(summary)
        form = QtWidgets.QFormLayout()
        wave_spin = QtWidgets.QDoubleSpinBox()
        wave_spin.setRange(0.0, 1.0)
        wave_spin.setDecimals(3)
        wave_spin.setSingleStep(0.01)
        wave_spin.setValue(bounded(self.wave_edit.text(), 0.22, 0.0, 1.0))
        roughness_spin = QtWidgets.QDoubleSpinBox()
        roughness_spin.setRange(0.02, 1.0)
        roughness_spin.setDecimals(3)
        roughness_spin.setSingleStep(0.01)
        roughness_spin.setValue(bounded(self.roughness_edit.text(), 0.28, 0.02, 1.0))
        foam_spin = QtWidgets.QDoubleSpinBox()
        foam_spin.setRange(0.0, 1.0)
        foam_spin.setDecimals(3)
        foam_spin.setSingleStep(0.01)
        foam_spin.setValue(bounded(self.foam_edit.text(), 0.12, 0.0, 1.0))
        form.addRow("Wave strength", wave_spin)
        form.addRow("Roughness", roughness_spin)
        form.addRow("Foam", foam_spin)
        layout.addLayout(form)
        performance_note = QtWidgets.QLabel(
            "Performance queue: after module decoupling, precompute a layer render plan and feed one combined render pass instead of independent layer renders."
        )
        performance_note.setWordWrap(True)
        layout.addWidget(performance_note)
        button_row = QtWidgets.QHBoxLayout()
        apply_button = QtWidgets.QPushButton("Apply to Qt profile")
        close_button = QtWidgets.QPushButton("Close")
        button_row.addStretch(1)
        button_row.addWidget(apply_button)
        button_row.addWidget(close_button)
        layout.addLayout(button_row)

        def apply_values() -> None:
            self.wave_edit.setText(scalar_text(wave_spin.value()))
            self.roughness_edit.setText(scalar_text(roughness_spin.value()))
            self.foam_edit.setText(scalar_text(foam_spin.value()))
            self.refresh_command_preview()
            self.refresh_canvas_preview()
            self.refresh_ocean_3d_control_summary()
            summary.setText(self.ocean_3d_control_summary_text())
            self.status.setText("Applied Taichi 3D Ocean Water controls")

        apply_button.clicked.connect(apply_values)
        close_button.clicked.connect(dialog.accept)
        dialog.exec()

    def ocean_material_summary_text(self, packet: dict[str, object] | None = None) -> str:
        packet = packet if isinstance(packet, dict) else self.collect_ocean_material_control_port()
        controls = packet.get("material_controls") if isinstance(packet.get("material_controls"), dict) else {}
        apply_contract = packet.get("renderer_apply_contract") if isinstance(packet.get("renderer_apply_contract"), dict) else {}
        sea_state = packet.get("sea_state_port") if isinstance(packet.get("sea_state_port"), dict) else {}
        scalar_sample = (
            sea_state.get("scalar_sample_contract")
            if isinstance(sea_state.get("scalar_sample_contract"), dict)
            else {}
        )
        flags = packet.get("renderer_flags")
        flags_text = ",".join(str(flag) for flag in flags) if isinstance(flags, list) else str(flags or "-")
        return (
            "Ocean material: "
            f"enabled={packet.get('enabled', True)}; "
            f"wave={controls.get('wave_strength')}; "
            f"roughness={controls.get('roughness')}; "
            f"foam={controls.get('foam')}; "
            f"apply={apply_contract.get('status', 'unknown')}; "
            f"sea_state={sea_state.get('status', 'unknown')}; "
            f"sample={scalar_sample.get('schema', 'rrkal_displaytools.sea_state_scalar_sample.v1')}; "
            f"flags={flags_text}; "
            "governance=RRKAL-owned provider/cache"
        )

    def collect_module_boundary_registry(self) -> dict[str, object]:
        return module_boundary_registry_packet("rrkal_displaytools_qt_panel")

    def module_boundary_summary_text(self, registry: dict[str, object] | None = None) -> str:
        registry = registry if isinstance(registry, dict) else self.collect_module_boundary_registry()
        contract = registry.get("decoupling_boundary_contract") if isinstance(registry.get("decoupling_boundary_contract"), dict) else {}
        extraction_order = contract.get("extraction_order") if isinstance(contract.get("extraction_order"), list) else []
        stable_contracts = contract.get("stable_contracts_before_move") if isinstance(contract.get("stable_contracts_before_move"), list) else []
        rrkal_owns = contract.get("rrkal_owns") if isinstance(contract.get("rrkal_owns"), list) else []
        first_extraction = str(extraction_order[0]) if extraction_order else "-"
        render_core = next((str(item) for item in extraction_order if str(item).startswith("render_core/")), "-")
        return (
            "Module seams: "
            f"modules={registry.get('module_count', 0)}; "
            f"first={first_extraction}; "
            f"render={render_core}; "
            f"tk_primary={registry.get('tk_primary_ui_allowed', False)}; "
            f"stable={','.join(str(item) for item in stable_contracts) or '-'}; "
            f"rrkal={','.join(str(item) for item in rrkal_owns) or '-'}; "
            "boundary=RRKAL-owned data/cache"
        )

    def collect_visual_feature_closure_matrix(self) -> dict[str, object]:
        return visual_feature_closure_matrix_packet("rrkal_displaytools_qt_panel")

    def collect_renderer_output_artifact_contract(self) -> dict[str, object]:
        return renderer_output_artifact_contract_packet("rrkal_displaytools_qt_panel")

    def latest_renderer_metadata_path(self) -> Path | None:
        candidates: list[Path] = []
        if self.renderer_thumbnail_path is not None:
            candidates.append(self.renderer_thumbnail_path)
        latest_thumbnail = self.latest_renderer_thumbnail_path()
        if latest_thumbnail is not None:
            candidates.append(latest_thumbnail)
        candidates.append(ROOT / "state" / "showcase" / "quick_smoke.png")
        candidates.append(RENDERER_PREVIEW_FRAME_PATH)

        seen: set[str] = set()
        for image_path in candidates:
            path = Path(image_path)
            key = str(path)
            if key in seen:
                continue
            seen.add(key)
            metadata_path = path.with_suffix(path.suffix + ".metadata.json")
            if metadata_path.exists():
                return metadata_path
        return None

    def display_renderer_metadata_path(self, path: Path | None) -> str | None:
        if path is None:
            return None
        try:
            return str(path.relative_to(ROOT))
        except ValueError:
            return str(path)

    def load_latest_renderer_metadata_payload(self) -> tuple[dict[str, object] | None, Path | None, str | None]:
        metadata_path = self.latest_renderer_metadata_path()
        if metadata_path is None:
            return None, None, "metadata_sidecar_missing"
        try:
            payload = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return None, metadata_path, str(exc)
        if not isinstance(payload, dict):
            return None, metadata_path, "metadata_payload_not_object"
        return payload, metadata_path, None

    def collect_layer_render_plan_cache_diagnostics(self) -> dict[str, object]:
        payload, metadata_path, read_error = self.load_latest_renderer_metadata_payload()
        diagnostics = layer_render_plan_cache_diagnostics_packet(
            payload,
            "rrkal_displaytools_qt_panel",
        )
        diagnostics["metadata_path"] = self.display_renderer_metadata_path(metadata_path)
        diagnostics["metadata_read_error"] = read_error
        return diagnostics

    def layer_render_plan_cache_summary_text(self, diagnostics: dict[str, object] | None = None) -> str:
        diagnostics = diagnostics if isinstance(diagnostics, dict) else self.collect_layer_render_plan_cache_diagnostics()
        metadata_path = diagnostics.get("metadata_path") or "-"
        read_error = diagnostics.get("metadata_read_error") or "-"
        key_state = "yes" if diagnostics.get("cache_key_available") else "no"
        reasons = diagnostics.get("cache_invalidation_reasons")
        reason_text = ",".join(str(reason) for reason in reasons[:3]) if isinstance(reasons, list) else "-"
        scopes = diagnostics.get("cache_invalidation_scope")
        if isinstance(scopes, list):
            scope_text = ",".join(str(scope.get("id", "-")) for scope in scopes[:3] if isinstance(scope, dict))
        else:
            scope_text = "-"
        batch_decision_count = diagnostics.get("batch_decision_count", 0)
        batch_decisions = diagnostics.get("batch_decisions")
        if isinstance(batch_decisions, list):
            batch_text = ",".join(str(item.get("decision", "-")) for item in batch_decisions[:3] if isinstance(item, dict))
        else:
            batch_text = "-"
        apply_path_count = diagnostics.get("apply_path_count", 0)
        execution_summary = diagnostics.get("execution_summary") if isinstance(diagnostics.get("execution_summary"), dict) else {}
        execution_phase_count = diagnostics.get("execution_phase_count", 0)
        phases = diagnostics.get("execution_phases")
        if isinstance(phases, list):
            phase_text = ",".join(str(item.get("id", "-")) for item in phases[:3] if isinstance(item, dict))
        else:
            phase_text = "-"
        phase_timing = diagnostics.get("phase_timing_contract") if isinstance(diagnostics.get("phase_timing_contract"), dict) else {}
        timing_status = phase_timing.get("status", "unavailable")
        timing_runtime = diagnostics.get("phase_timing_runtime") if isinstance(diagnostics.get("phase_timing_runtime"), dict) else {}
        runtime_timing_status = timing_runtime.get("status", "unavailable")
        slowest_phase = timing_runtime.get("slowest_phase_id", "-")
        total_ms = timing_runtime.get("total_ms", "-")
        bottleneck = diagnostics.get("bottleneck_recommendation") if isinstance(diagnostics.get("bottleneck_recommendation"), dict) else {}
        next_opt = bottleneck.get("recommended_next_action", "unavailable")
        compose_queue_count = diagnostics.get("compose_queue_count", 0)
        compose_queue_skipped_count = diagnostics.get("compose_queue_skipped_count", 0)
        compose_run_count = diagnostics.get("compose_run_count", 0)
        compose_merge_candidate_run_count = diagnostics.get("compose_merge_candidate_run_count", 0)
        parity = diagnostics.get("compose_run_parity_contract") if isinstance(diagnostics.get("compose_run_parity_contract"), dict) else {}
        parity_status = parity.get("status", "unavailable")
        parity_smoke = parity.get("parity_smoke_script", "scripts\\render_compose_parity_smoke.ps1")
        return (
            "Render plan cache: "
            f"status={diagnostics.get('status', 'unavailable')}; "
            f"cache={diagnostics.get('cache_status', 'unavailable')}; "
            f"decision={diagnostics.get('cache_reuse_decision', 'unavailable')}; "
            f"reasons={reason_text}; "
            f"scope={scope_text}; "
            f"batches={batch_decision_count}:{batch_text}; "
            f"apply={apply_path_count}; "
            f"exec={execution_summary.get('current_execution_mode', 'unavailable')}; "
            f"sp={execution_summary.get('single_pass_candidate_count', 0)}; "
            f"phases={execution_phase_count}:{phase_text}; "
            f"timing={timing_status}; "
            f"runtime_timing={runtime_timing_status}; "
            f"slowest={slowest_phase}; "
            f"total_ms={total_ms}; "
            f"next_opt={next_opt}; "
            f"queue={compose_queue_count}; "
            f"skip={compose_queue_skipped_count}; "
            f"runs={compose_run_count}; "
            f"merge={compose_merge_candidate_run_count}; "
            f"parity={parity_status}; "
            f"parity_smoke={parity_smoke}; "
            f"key={key_state}; "
            f"reuse={diagnostics.get('reuse_boundary', 'unavailable')}; "
            f"steps={diagnostics.get('composition_step_count', '-')}; "
            f"visible={diagnostics.get('visible_layer_count', '-')}; "
            f"single_pass={diagnostics.get('single_pass_ready', False)}; "
            f"metadata={metadata_path}; "
            f"read_error={read_error}"
        )

    def refresh_layer_render_plan_cache_diagnostics_strip(self) -> None:
        if hasattr(self, "render_plan_cache_label"):
            self.render_plan_cache_label.setText(self.layer_render_plan_cache_summary_text())

    def collect_layer_render_plan_performance(self) -> dict[str, object]:
        packet = layer_render_plan_performance_packet(
            "rrkal_displaytools_qt_panel",
            self.collect_layer_capability_matrix(),
            self.collect_module_boundary_registry(),
        )
        packet["cache_diagnostics"] = self.collect_layer_render_plan_cache_diagnostics()
        return packet

    def collect_cross_machine_clone_readiness(self) -> dict[str, object]:
        return cross_machine_clone_readiness_packet(
            self.collect_profile_launch_readiness(),
            self.collect_module_boundary_registry(),
            "rrkal_displaytools_qt_panel",
        )

    def clone_reviewer_summary_text(self) -> str:
        packet = self.collect_cross_machine_clone_readiness()
        contract = packet.get("clone_reviewer_summary_contract", {})
        label = "Clone reviewer"
        if isinstance(contract, dict):
            label = str(contract.get("label") or label)
        return (
            f"{label}: "
            f"status={packet.get('status')}; "
            f"repo={packet.get('repo_url')}; "
            f"clone={packet.get('clone_command')}; "
            f"branch={packet.get('default_branch')}; "
            f"visibility={packet.get('repo_visibility')}; "
            f"setup={packet.get('setup_doc')}; "
            f"profile={packet.get('profile_launch_readiness')}; "
            f"qt_first={packet.get('qt_first')}; "
            f"smoke_required={packet.get('smoke_required_before_push')}; "
            f"first_smoke={packet.get('first_run_smoke_command')}; "
            f"first_handoff={packet.get('first_run_handoff_command')}; "
            f"handoff_first={packet.get('handoff_first_command')}"
        )

    def collect_reviewer_packet_export(self) -> dict[str, object]:
        return reviewer_packet_export_packet("rrkal_displaytools_qt_panel")

    def collect_reviewer_packet(self) -> dict[str, object]:
        return {
            "schema": "rrkal_displaytools.reviewer_packet.v1",
            "created_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "source": "rrkal_displaytools_qt_panel",
            "reviewer_packet_export": self.collect_reviewer_packet_export(),
            "clone_reviewer_summary": self.clone_reviewer_summary_text(),
            "launch_reviewer_summary": self.launch_reviewer_summary_text(),
            "research_interaction_summary": self.research_interaction_summary_text(),
            "visual_review_summary": self.visual_review_readiness_summary_text(),
            "hydrology_lod_summary": self.hydrology_lod_summary_text(),
            "ocean_material_summary": self.ocean_material_summary_text(),
            "style_routes_summary": self.style_routes_summary_text(),
            "module_boundary_summary": self.module_boundary_summary_text(),
            "cross_machine_clone_readiness": self.collect_cross_machine_clone_readiness(),
            "profile_launch_readiness": self.collect_profile_launch_readiness(),
            "profile_ui_state_replay": self.collect_profile_ui_state_replay(),
            "hydrology_lod_readiness": self.collect_hydrology_lod_readiness(),
            "hydrology_lod_runtime_evidence": self.collect_hydrology_lod_runtime_evidence(),
            "ocean_material_control_port": self.collect_ocean_material_control_port(),
            "style_profile_renderer_routes": self.collect_style_profile_renderer_routes(),
            "module_boundary_registry": self.collect_module_boundary_registry(),
            "visual_feature_closure_matrix": self.collect_visual_feature_closure_matrix(),
            "renderer_output_artifact_contract": self.collect_renderer_output_artifact_contract(),
            "layer_render_plan_performance": self.collect_layer_render_plan_performance(),
            "launch_packet_snapshot": self.collect_launch_packet(),
        }

    def collect_launch_packet(self) -> dict[str, object]:
        return {
            "schema": "rrkal_displaytools.launch_packet.v1",
            "created_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
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
            "profile": self.collect_profile(),
            "rrkal_data_manifest_ref": self.rrkal_manifest_ref_edit.text().strip(),
            "rrkal_data_manifest_ref_boundary": "Reference-only handoff field; displaytools does not discover, download, validate, import, or govern this manifest.",
            "selected_layer": self.selected_layer_key,
            "active_layer_operation_summary": self.active_layer_operation_summary_text(),
            "last_layer_operation": self.layer_operation_event_text(),
            "visual_review_readiness": self.collect_visual_review_readiness(),
            "visual_feature_closure_matrix": self.collect_visual_feature_closure_matrix(),
            "renderer_output_artifact_contract": self.collect_renderer_output_artifact_contract(),
            "layer_render_plan_performance": self.collect_layer_render_plan_performance(),
            "layer_operation_feedback": self.collect_layer_operation_feedback(),
            "layer_control_feedback_strip": self.collect_layer_control_feedback_strip(),
            "layer_filter": self.collect_layer_filter_state(),
            "layer_group_view": self.collect_layer_group_view_state(),
            "layer_operator_shortcuts": self.collect_layer_operator_shortcuts(),
            "layer_operator_groups": self.collect_layer_operator_groups(),
            "layer_selection_tool": self.collect_layer_selection_tool(),
            "layer_selection_affordance": self.collect_layer_selection_affordance(),
            "layer_hover_affordance": self.collect_layer_hover_affordance(),
            "layer_lock_affordance": self.collect_layer_lock_affordance(),
            "layer_research_workflow": self.collect_layer_research_workflow(),
            "boundary_emphasis_control": self.collect_boundary_emphasis_control(),
            "cursor_geodesy_readout": self.collect_cursor_geodesy_readout(),
            "cursor_geodesy_state_file": str(CURSOR_GEODESY_STATE_PATH),
            "cursor_geodesy_ack_file": str(CURSOR_GEODESY_ACK_PATH),
            "style_renderer_entries": self.collect_style_renderer_entries(),
            "style_profile_renderer_routes": self.collect_style_profile_renderer_routes(),
            "style_template_visual_preview": self.collect_style_template_visual_preview(),
            "module_boundary_registry": self.collect_module_boundary_registry(),
            "cross_machine_clone_readiness": self.collect_cross_machine_clone_readiness(),
            "profile_launch_readiness": self.collect_profile_launch_readiness(),
            "profile_launch_readiness_ui": self.collect_profile_launch_readiness_ui(),
            "reviewer_packet_export": self.collect_reviewer_packet_export(),
            "layer_visual_presets": self.collect_layer_visual_presets(),
            "layer_visual_preset_runtime_feedback": self.collect_layer_visual_preset_runtime_feedback(),
            "hydrology_lod_readiness": self.collect_hydrology_lod_readiness(),
            "hydrology_lod_runtime_evidence": self.collect_hydrology_lod_runtime_evidence(),
            "ocean_material_control_port": self.collect_ocean_material_control_port(),
            "layer_capability_matrix": self.collect_layer_capability_matrix(),
            "layer_runtime_evidence_summary": self.collect_layer_capability_matrix().get("runtime_evidence_summary"),
            "active_layer_diagnostics": self.active_layer_diagnostics_packet(),
            "layer_undo": self.collect_layer_undo_state(),
            "session_journal": self.collect_session_journal(),
            "document_undo": self.collect_document_undo_state(),
            "timeline_state": self.collect_timeline_state(),
            "timeline_playback_readiness": self.collect_timeline_playback_readiness(),
            "timeline_playback_plan": self.collect_timeline_playback_plan(),
            "timeline_segment_state": self.collect_timeline_segment_state(),
            "timeline_active_step_state": self.collect_timeline_active_step_state(),
            "timeline_step_playback": self.collect_timeline_step_playback_state(),
            "timeline_ocean_material_interpolation": self.collect_timeline_ocean_material_interpolation_state(),
            "timeline_animation_export": self.collect_timeline_animation_export_state(),
            "timeline_export_options": self.collect_timeline_export_options(),
            "timeline_camera_keyframe": self.collect_timeline_camera_keyframe_state(),
            "timeline_camera_interpolation": self.collect_timeline_camera_interpolation_state(),
            "timeline_layer_opacity_interpolation": self.collect_timeline_layer_opacity_interpolation_state(),
            "timeline_layer_discrete_hold": self.collect_timeline_layer_discrete_hold_state(),
            "timeline_runtime_state_file": str(TIMELINE_STATE_PATH),
            "timeline_ack_file": str(TIMELINE_ACK_PATH),
            "timeline_ack": self.timeline_ack_payload,
            "selected_pin_id": self.selected_pin_id,
            "layer_stack_ui": self.collect_layer_stack_ui(),
            "tool_state": self.collect_tool_state(),
            "pins": self.collect_research_pins(),
            "boundary_highlight": self.collect_boundary_highlight_state(),
            "canvas_preview": self.collect_canvas_preview_state(),
            "closed_loop_status": renderer_closed_loop_status_packet(),
            "boundary_highlight_ack_file": str(BOUNDARY_HIGHLIGHT_ACK_PATH),
            "pin_input_ack_file": str(PIN_INPUT_ACK_PATH),
            "pin_pick_state_file": str(PIN_PICK_STATE_PATH),
            "pin_pick_ack_file": str(PIN_PICK_ACK_PATH),
            "layer_runtime_state_file": str(LAYER_RUNTIME_STATE_PATH),
            "layer_runtime_ack_file": str(LAYER_RUNTIME_ACK_PATH),
            "layer_pick_state_file": str(LAYER_PICK_STATE_PATH),
            "command": self.build_command(),
            "command_line": subprocess.list2cmdline(self.build_command()),
            "portable_command": self.build_portable_command(),
            "portable_command_line": subprocess.list2cmdline(self.build_portable_command()),
        }

    def renderer_thumbnail_profile_path(self) -> str | None:
        if self.renderer_thumbnail_path is None:
            return None
        try:
            return str(self.renderer_thumbnail_path.relative_to(ROOT))
        except ValueError:
            return str(self.renderer_thumbnail_path)

    def display_renderer_preview_path(self, path: Path) -> str:
        try:
            return str(path.relative_to(ROOT))
        except ValueError:
            return str(path)

    def collect_canvas_preview_state(self) -> dict[str, object]:
        renderer_sync = {
            "state": "ui_state_preview",
            "thumbnail": "static_renderer_output_thumbnail",
            "live_file_stream": "file_based_live_renderer_frame_stream",
        }.get(self.canvas_preview_mode, "ui_state_preview")
        boundary_emphasis = self.collect_boundary_emphasis_control()
        boundary_identity_warning = self.boundary_identity_warning_text()
        return {
            "schema": "rrkal_displaytools.canvas_preview.v1",
            "mode": self.canvas_preview_mode,
            "renderer_thumbnail_path": self.renderer_thumbnail_profile_path(),
            "preview_frame_path": str(RENDERER_PREVIEW_FRAME_PATH.relative_to(ROOT)),
            "preview_frame_interval_s": RENDERER_PREVIEW_FRAME_INTERVAL_S,
            "cursor_latitude": self.cursor_latitude,
            "cursor_longitude": self.cursor_longitude,
            "cursor_units": "degrees",
            "renderer_cursor_geodesy_state_file": str(CURSOR_GEODESY_STATE_PATH),
            "renderer_cursor_geodesy_ack_file": str(CURSOR_GEODESY_ACK_PATH),
            "renderer_cursor_geodesy_state": self.cursor_geodesy_state_payload,
            "renderer_cursor_geodesy_ack": self.cursor_geodesy_ack_payload,
            "boundary_emphasis_target_mode": boundary_emphasis.get("target_mode"),
            "boundary_emphasis_target_layer": boundary_emphasis.get("target_layer_key"),
            "boundary_emphasis_target_alignment": boundary_emphasis.get("target_alignment"),
            "boundary_emphasis_target_alignment_label": boundary_emphasis.get("target_alignment_label"),
            "boundary_identity_warning": boundary_identity_warning,
            "boundary_identity_warning_surface": "Properties dock Identity warning / Canvas Preview / research provenance",
            "renderer_sync": renderer_sync,
        }

    def collect_layer_stack_ui(self) -> dict[str, dict[str, object]]:
        stack: dict[str, dict[str, object]] = {}
        for key, _label in LAYER_LABELS:
            stack[key] = {
                "locked": self.layer_locks[key].isChecked(),
                "opacity": self.layer_opacity[key].value(),
                "blend_mode": self.layer_blends[key].currentText(),
                "selected": key == self.selected_layer_key,
                "renderer_sync": self.layer_renderer_sync_status(key),
            }
        return stack

    def layer_renderer_sync_status(self, key: str) -> str:
        return str(layer_capability_packet(key).get("renderer_sync", "planned"))

    def collect_layer_operator_shortcuts(self) -> dict[str, object]:
        return layer_operator_shortcuts_packet(
            "rrkal_displaytools_qt_panel",
            self.selected_layer_key,
            self.layer_visibility_snapshot is not None,
            len(self.layer_undo_stack),
        )

    def collect_style_renderer_entries(self) -> dict[str, object]:
        style_combo = getattr(self, "style_combo", None)
        selected_style = style_combo.currentText() if style_combo is not None else None
        return style_renderer_entries_packet("rrkal_displaytools_qt_panel", selected_style)

    def collect_style_profile_renderer_routes(self) -> dict[str, object]:
        return style_profile_renderer_routes_packet(
            self.collect_style_renderer_entries(),
            "rrkal_displaytools_qt_panel",
        )

    def style_routes_summary_text(self, routes_packet: dict[str, object] | None = None) -> str:
        routes_packet = routes_packet if isinstance(routes_packet, dict) else self.collect_style_profile_renderer_routes()
        route_ids = routes_packet.get("route_ids") if isinstance(routes_packet.get("route_ids"), list) else []
        required_routes = routes_packet.get("required_routes") if isinstance(routes_packet.get("required_routes"), list) else []
        missing_routes = routes_packet.get("missing_routes") if isinstance(routes_packet.get("missing_routes"), list) else []
        commands = routes_packet.get("portable_route_commands") if isinstance(routes_packet.get("portable_route_commands"), dict) else {}
        return (
            "Style routes: "
            f"status={routes_packet.get('status', 'unknown')}; "
            f"routes={routes_packet.get('route_count', 0)}; "
            f"ids={','.join(str(route_id) for route_id in route_ids) or '-'}; "
            f"required={','.join(str(route_id) for route_id in required_routes) or '-'}; "
            f"missing={','.join(str(route_id) for route_id in missing_routes) or '-'}; "
            f"parchment={commands.get('parchment', '-')}; "
            f"tactical={commands.get('tactical', '-')}; "
            "boundary=RRKAL-owned data/cache"
        )

    def collect_style_template_visual_preview(self) -> dict[str, object]:
        return style_template_visual_preview_packet(
            self.collect_style_renderer_entries(),
            "rrkal_displaytools_qt_panel",
        )

    def _create_style_template_preview_cards(self) -> QtWidgets.QWidget:
        grid_widget = QtWidgets.QWidget()
        grid_widget.setObjectName("styleTemplatePreviewCardGrid")
        grid = QtWidgets.QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(6)
        self.style_template_preview_buttons: dict[str, QtWidgets.QPushButton] = {}
        cards = self.collect_style_template_visual_preview().get("preview_cards", [])
        if not isinstance(cards, list):
            cards = []
        for index, card in enumerate(cards):
            if not isinstance(card, dict):
                continue
            style_id = str(card.get("id", ""))
            label = str(card.get("label", style_id.title()))
            swatches = card.get("swatches") if isinstance(card.get("swatches"), list) else []
            thumbnail_path = str(card.get("thumbnail_path", f"state/style_previews/{style_id}.png"))
            button = QtWidgets.QPushButton(f"{label}\n{'  '.join(str(color) for color in swatches)}\nthumb: missing {thumbnail_path}")
            button.setObjectName(f"styleTemplateCard_{style_id}")
            button.setCheckable(True)
            button.setMinimumHeight(72)
            button.setToolTip(f"Apply {label} style template to the renderer launch profile. Thumbnail slot: {thumbnail_path}")
            button.clicked.connect(lambda _checked=False, value=style_id: self.apply_style_template_preview_card(value))
            grid.addWidget(button, index // 2, index % 2)
            self.style_template_preview_buttons[style_id] = button
        return grid_widget

    def local_style_thumbnail_path(self, thumbnail_path: str) -> Path:
        path = Path(thumbnail_path)
        return path if path.is_absolute() else ROOT / path

    def _style_template_preview_card_stylesheet(self, swatches: list[object], selected: bool) -> str:
        colors = [str(color) for color in swatches]
        first = colors[0] if len(colors) > 0 else "#1b1f24"
        second = colors[1] if len(colors) > 1 else "#2f3a44"
        third = colors[2] if len(colors) > 2 else "#e9edf1"
        border = "#f5d061" if selected else "#3a4652"
        return (
            "QPushButton {"
            f"background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {first}, stop:0.58 {second}, stop:1 {third});"
            f"border:2px solid {border}; border-radius:8px; padding:6px; color:#f4f7fb; font-weight:600;"
            "}"
            "QPushButton:checked { color:#ffffff; }"
        )

    def refresh_style_template_preview_cards(self) -> None:
        packet = self.collect_style_template_visual_preview()
        current_style = self.style_combo.currentText() if hasattr(self, "style_combo") else ""
        cards = packet.get("preview_cards", [])
        card_by_id = {str(card.get("id")): card for card in cards if isinstance(card, dict)} if isinstance(cards, list) else {}
        ready_count = 0
        missing_ids: list[str] = []
        for style_id, button in getattr(self, "style_template_preview_buttons", {}).items():
            card = card_by_id.get(style_id, {})
            label = str(card.get("label", style_id.title())) if isinstance(card, dict) else style_id.title()
            swatches = card.get("swatches") if isinstance(card.get("swatches"), list) else []
            thumbnail_path = str(card.get("thumbnail_path", f"state/style_previews/{style_id}.png")) if isinstance(card, dict) else f"state/style_previews/{style_id}.png"
            thumbnail_file = self.local_style_thumbnail_path(thumbnail_path)
            thumbnail_exists = thumbnail_file.exists()
            if thumbnail_exists:
                ready_count += 1
            else:
                missing_ids.append(style_id)
            button.setText(
                f"{label}\n{'  '.join(str(color) for color in swatches)}\nthumb: {'ready' if thumbnail_exists else 'missing'} {thumbnail_path}"
            )
            if thumbnail_exists:
                button.setIcon(QtGui.QIcon(str(thumbnail_file)))
                button.setIconSize(QtCore.QSize(96, 54))
            else:
                button.setIcon(QtGui.QIcon())
            selected = style_id == current_style
            button.setChecked(selected)
            button.setStyleSheet(self._style_template_preview_card_stylesheet(swatches, selected))
        readiness_label = getattr(self, "style_thumbnail_readiness_label", None)
        if readiness_label is not None:
            missing_text = ", ".join(missing_ids) if missing_ids else "none"
            readiness_label.setText(
                self.style_thumbnail_readiness_summary_text(ready_count, len(card_by_id), missing_ids)
            )

    def style_thumbnail_readiness_summary_text(
        self,
        ready_count: int | None = None,
        required_count: int | None = None,
        missing_ids: list[str] | None = None,
    ) -> str:
        packet = self.collect_style_template_visual_preview()
        cards = packet.get("preview_cards", [])
        if ready_count is None or required_count is None or missing_ids is None:
            ready_count = 0
            missing_ids = []
            if isinstance(cards, list):
                for card in cards:
                    if not isinstance(card, dict):
                        continue
                    style_id = str(card.get("id", ""))
                    thumbnail_path = str(card.get("thumbnail_path", f"state/style_previews/{style_id}.png"))
                    if self.local_style_thumbnail_path(thumbnail_path).exists():
                        ready_count += 1
                    else:
                        missing_ids.append(style_id)
                required_count = len(cards)
            else:
                required_count = 0
        missing_text = ", ".join(missing_ids) if missing_ids else "none"
        return (
            f"Style thumbnails: ready={ready_count}/{required_count}; "
            f"missing={missing_text}; action=Copy style thumbs command"
        )

    def collect_local_style_thumbnail_readiness(self) -> dict[str, object]:
        packet = self.collect_style_template_visual_preview()
        cards = packet.get("preview_cards", [])
        slots: list[dict[str, object]] = []
        ready_count = 0
        missing_ids: list[str] = []
        if isinstance(cards, list):
            for card in cards:
                if not isinstance(card, dict):
                    continue
                style_id = str(card.get("id", ""))
                thumbnail_path = str(card.get("thumbnail_path", f"state/style_previews/{style_id}.png"))
                absolute_path = self.local_style_thumbnail_path(thumbnail_path)
                exists = absolute_path.exists()
                if exists:
                    ready_count += 1
                else:
                    missing_ids.append(style_id)
                slots.append(
                    {
                        "id": style_id,
                        "thumbnail_path": thumbnail_path,
                        "absolute_path": str(absolute_path),
                        "exists": exists,
                        "status": "ready" if exists else "missing",
                    }
                )
        summary_text = self.style_thumbnail_readiness_summary_text(ready_count, len(slots), missing_ids)
        return {
            "schema": "rrkal_displaytools.local_style_thumbnail_readiness.v1",
            "source": "rrkal_displaytools_qt_panel",
            "status": "ready" if not missing_ids else "missing_runtime_artifacts",
            "artifact_dir": packet.get("thumbnail_artifact_dir"),
            "slots": slots,
            "ready_count": ready_count,
            "missing_count": len(missing_ids),
            "missing_ids": missing_ids,
            "summary_text": summary_text,
            "boundary": "Local thumbnail readiness only checks optional runtime PNG artifacts; it does not render thumbnails or manage RRKAL data caches.",
        }

    def copy_style_thumbnail_readiness_summary(self) -> None:
        summary = self.style_thumbnail_readiness_summary_text()
        QtWidgets.QApplication.clipboard().setText(summary)
        self.status.setText("已複製 style thumbnail readiness 摘要")

    def apply_style_template_preview_card(self, style_id: str) -> None:
        self._set_combo(self.style_combo, style_id)
        self.refresh_style_template_preview_cards()
        self.status.setText(f"已套用 style template preview card: {style_id}")

    def collect_profile_launch_readiness(self) -> dict[str, object]:
        return profile_launch_readiness_packet(
            "rrkal_displaytools_qt_panel",
            self.collect_style_renderer_entries(),
            self.collect_layer_operator_groups(),
        )

    def launch_reviewer_summary_text(self) -> str:
        packet = self.collect_profile_launch_readiness()
        contract = packet.get("launch_reviewer_summary_contract", {})
        label = "Launch reviewer"
        if isinstance(contract, dict):
            label = str(contract.get("label") or label)
        fields = packet.get("launch_packet_fields", [])
        field_text = ",".join(str(item) for item in fields) if isinstance(fields, list) else str(fields)
        return (
            f"{label}: "
            f"readiness={packet.get('readiness')}; "
            f"checks={packet.get('ready_check_count')}/{packet.get('check_count')}; "
            f"command={subprocess.list2cmdline(self.build_portable_command())}; "
            f"fields={field_text}; "
            f"renderer={packet.get('renderer_capability_field')}"
        )

    def collect_profile_launch_readiness_ui(self) -> dict[str, object]:
        return profile_launch_readiness_ui_packet(
            self.collect_profile_launch_readiness(),
            "rrkal_displaytools_qt_panel",
        )

    def collect_profile_ui_state_replay(self) -> dict[str, object]:
        return profile_ui_state_replay_packet("rrkal_displaytools_qt_panel")

    def collect_visual_review_readiness(self) -> dict[str, object]:
        packet = visual_review_readiness_packet("rrkal_displaytools_qt_panel")
        frame_status = packet.get("frame_status", {})
        inspector_view = packet.get("inspector_view", {})
        thumbnail_path = self.latest_renderer_thumbnail_path()
        live_preview_exists = RENDERER_PREVIEW_FRAME_PATH.exists()

        def display_path(path: Path | None) -> str | None:
            if path is None:
                return None
            try:
                return str(path.relative_to(ROOT))
            except ValueError:
                return str(path)

        thumbnail_status = frame_status.get("renderer_thumbnail", {})
        if isinstance(thumbnail_status, dict):
            thumbnail_status["status"] = "frame_available" if thumbnail_path else "inspect_action_available"
            thumbnail_status["artifact_state"] = "available" if thumbnail_path else "runtime_dependent"
            thumbnail_status["artifact_path"] = display_path(thumbnail_path)

        live_status = frame_status.get("live_preview", {})
        if isinstance(live_status, dict):
            live_status["status"] = "frame_available" if live_preview_exists else "inspect_action_available"
            live_status["artifact_state"] = "available" if live_preview_exists else "runtime_dependent"
            live_status["artifact_path"] = display_path(RENDERER_PREVIEW_FRAME_PATH) if live_preview_exists else None

        if isinstance(inspector_view, dict):
            inspector_view["status_badges"] = [
                f"renderer_thumbnail: {thumbnail_status.get('status', 'unknown')}",
                f"live_preview: {live_status.get('status', 'unknown')}",
            ]
            rows = inspector_view.get("rows", [])
            if isinstance(rows, list):
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    if row.get("action_id") == "renderer_thumbnail":
                        row["status"] = thumbnail_status.get("status", row.get("status"))
                        row["artifact_state"] = thumbnail_status.get("artifact_state", row.get("artifact_state"))
                        row["artifact_path"] = thumbnail_status.get("artifact_path")
                    if row.get("action_id") == "live_preview":
                        row["status"] = live_status.get("status", row.get("status"))
                        row["artifact_state"] = live_status.get("artifact_state", row.get("artifact_state"))
                        row["artifact_path"] = live_status.get("artifact_path")

        packet["runtime_artifact_summary_schema"] = "rrkal_displaytools.visual_review_runtime_artifact_summary.v1"
        packet["runtime_artifact_summary"] = {
            "renderer_thumbnail_status": thumbnail_status.get("status", "unknown"),
            "renderer_thumbnail_artifact_path": thumbnail_status.get("artifact_path"),
            "live_preview_status": live_status.get("status", "unknown"),
            "live_preview_artifact_path": live_status.get("artifact_path"),
            "ui_status_surface": "Qt command/provenance text panel",
        }
        return packet

    def visual_review_readiness_summary_text(self, packet: dict[str, object] | None = None) -> str:
        packet = packet or self.collect_visual_review_readiness()
        summary = packet.get("runtime_artifact_summary", {})
        contract = packet.get("copy_summary_contract", {})
        if not isinstance(summary, dict):
            return "Visual readiness: runtime artifact summary unavailable."
        label = "Visual readiness"
        if isinstance(contract, dict):
            label = str(contract.get("label") or label)
        thumbnail_status = summary.get("renderer_thumbnail_status", "unknown")
        thumbnail_path = summary.get("renderer_thumbnail_artifact_path") or "no frame yet"
        live_status = summary.get("live_preview_status", "unknown")
        live_path = summary.get("live_preview_artifact_path") or "no frame yet"
        return (
            f"{label}: "
            f"thumbnail={thumbnail_status} ({thumbnail_path}); "
            f"live={live_status} ({live_path})"
        )

    def update_visual_review_readiness_label(self, packet: dict[str, object] | None = None) -> None:
        if hasattr(self, "visual_review_readiness_label"):
            self.visual_review_readiness_label.setText(self.visual_review_readiness_summary_text(packet))

    def collect_layer_operation_feedback(self) -> dict[str, object]:
        return layer_operation_feedback_packet(
            "rrkal_displaytools_qt_panel",
            self.selected_layer_key,
            self.active_layer_operation_summary_text(),
            self.layer_operation_event_text(),
            self.collect_layer_operator_groups(),
            self.collect_layer_undo_state(),
        )

    def collect_layer_control_feedback_strip(self) -> dict[str, object]:
        return layer_control_feedback_strip_packet(
            "rrkal_displaytools_qt_panel",
            self.selected_layer_key,
            self.collect_layer_stack_ui(),
            self.active_layer_operation_summary_text(),
            self.layer_operation_event_text(),
        )

    def refresh_layer_control_feedback_strip(self) -> None:
        label = getattr(self, "layer_control_feedback_strip_label", None)
        if label is not None:
            label.setText(str(self.collect_layer_control_feedback_strip().get("summary_text")))

    def collect_layer_visual_presets(self) -> dict[str, object]:
        return layer_visual_presets_packet(
            "rrkal_displaytools_qt_panel",
            getattr(self, "layer_visual_preset", "custom"),
        )

    def collect_layer_visual_preset_runtime_feedback(self) -> dict[str, object]:
        runtime_ack = self.layer_runtime_ack_payload if isinstance(self.layer_runtime_ack_payload, dict) else None
        return layer_visual_preset_runtime_feedback_packet(
            self.collect_layer_visual_presets(),
            runtime_ack,
            "rrkal_displaytools_qt_panel",
        )

    def collect_hydrology_lod_readiness(self) -> dict[str, object]:
        return hydrology_lod_readiness_packet(
            "rrkal_displaytools_qt_panel",
            self.collect_layer_capability_matrix(),
        )

    def collect_hydrology_lod_runtime_evidence(self) -> dict[str, object]:
        runtime_ack = self.layer_runtime_ack_payload if isinstance(self.layer_runtime_ack_payload, dict) else None
        pick_state = self.layer_pick_state_payload if isinstance(self.layer_pick_state_payload, dict) else None
        return hydrology_lod_runtime_evidence_packet(
            self.collect_hydrology_lod_readiness(),
            runtime_ack,
            pick_state,
            "rrkal_displaytools_qt_panel",
        )

    def hydrology_lod_summary_text(
        self,
        readiness: dict[str, object] | None = None,
        evidence: dict[str, object] | None = None,
    ) -> str:
        readiness = readiness if isinstance(readiness, dict) else self.collect_hydrology_lod_readiness()
        evidence = evidence if isinstance(evidence, dict) else self.collect_hydrology_lod_runtime_evidence()
        targets = readiness.get("stable_renderer_targets", [])
        targets_text = ",".join(str(target) for target in targets) if isinstance(targets, list) else str(targets)
        return (
            "Hydrology/LOD: "
            f"readiness={readiness.get('readiness', 'unknown')}; "
            f"live={readiness.get('live_hydrology_layer_count', 0)}/{readiness.get('hydrology_layer_count', 0)}; "
            f"targets={targets_text or '-'}; "
            f"lod={readiness.get('lod_hook_status', 'unknown')}; "
            f"runtime={evidence.get('status', 'waiting_for_runtime_evidence')}; "
            f"hits={evidence.get('hydrology_runtime_hit_count', 0)}; "
            f"pick={evidence.get('pick_matches_hydrology', False)}; "
            f"state={evidence.get('runtime_state_file', 'state/renderer_layer_runtime_state.json')}; "
            f"ack={evidence.get('ack_file', 'state/renderer_layer_runtime_ack.json')}; "
            f"pick_state={evidence.get('pick_state_file', 'state/renderer_layer_pick_state.json')}; "
            "governance=RRKAL-owned data/cache"
        )

    def collect_layer_operator_groups(self) -> dict[str, object]:
        return layer_operator_groups_packet(
            self.collect_layer_operator_shortcuts(),
            "rrkal_displaytools_qt_panel",
        )

    def collect_layer_selection_tool(self) -> dict[str, object]:
        return layer_selection_tool_packet(
            "rrkal_displaytools_qt_panel",
            self.selected_layer_key,
        )

    def collect_layer_selection_affordance(self) -> dict[str, object]:
        return layer_selection_affordance_packet(
            "rrkal_displaytools_qt_panel",
            self.selected_layer_key,
            self.collect_layer_stack_ui(),
        )

    def refresh_layer_selection_affordance(self) -> None:
        label = getattr(self, "layer_selection_affordance_label", None)
        if label is not None:
            label.setText(str(self.collect_layer_selection_affordance().get("summary_text")))

    def collect_layer_hover_affordance(self, hovered_layer: str | None = None) -> dict[str, object]:
        if hovered_layer is None:
            hovered_layer = self.layer_hover_layer_key
        return layer_hover_affordance_packet(
            "rrkal_displaytools_qt_panel",
            hovered_layer,
            self.collect_layer_stack_ui(),
        )

    def set_layer_hover_affordance(self, layer_key: str) -> None:
        self.layer_hover_layer_key = layer_key
        label = getattr(self, "layer_hover_affordance_label", None)
        if label is not None:
            label.setText(str(self.collect_layer_hover_affordance(layer_key).get("summary_text")))

    def clear_layer_hover_affordance(self, layer_key: str | None = None) -> None:
        if layer_key is not None and self.layer_hover_layer_key != layer_key:
            return
        self.layer_hover_layer_key = None
        label = getattr(self, "layer_hover_affordance_label", None)
        if label is not None:
            label.setText(str(self.collect_layer_hover_affordance(None).get("summary_text")))

    def collect_layer_lock_affordance(self) -> dict[str, object]:
        return layer_lock_affordance_packet(
            "rrkal_displaytools_qt_panel",
            self.collect_layer_stack_ui(),
        )

    def layer_selection_summary_text(self, packet: dict[str, object] | None = None) -> str:
        packet = packet or self.collect_layer_selection_tool()
        contract = packet.get("selection_summary_contract", {})
        label = "Layer selection"
        if isinstance(contract, dict):
            label = str(contract.get("label") or label)
        selected_layer = self.selected_layer_key or "none"
        selected_label = next(
            (text for key, text in LAYER_LABELS if key == self.selected_layer_key),
            selected_layer,
        )
        pick_bridge = packet.get("renderer_pick_bridge", {})
        pick_state_file = "state/renderer_layer_pick_state.json"
        if isinstance(pick_bridge, dict):
            pick_state_file = str(pick_bridge.get("pick_state_file") or pick_state_file)
        brush_mask_scope = str(packet.get("brush_mask_scope") or "excluded")
        return f"{label}: selected={selected_layer} ({selected_label}); pick_state={pick_state_file}; brush_mask={brush_mask_scope}"

    def collect_layer_research_workflow(self) -> dict[str, object]:
        return layer_research_workflow_packet(
            self.collect_layer_filter_state(),
            self.collect_layer_group_view_state(),
            self.collect_layer_operator_groups(),
            self.collect_layer_capability_matrix(),
            "rrkal_displaytools_qt_panel",
        )

    def collect_boundary_emphasis_control(self) -> dict[str, object]:
        state = getattr(self, "boundary_emphasis_state", None)
        return boundary_emphasis_control_packet(
            state if isinstance(state, dict) else None,
            self.selected_layer_key,
            "rrkal_displaytools_qt_panel",
        )

    def boundary_emphasis_summary_text(self, packet: dict[str, object] | None = None) -> str:
        packet = packet or self.collect_boundary_emphasis_control()
        contract = packet.get("boundary_summary_contract", {})
        label = "Boundary emphasis"
        if isinstance(contract, dict):
            label = str(contract.get("label") or label)
        return (
            f"{label}: "
            f"target={packet.get('target_mode')}->{packet.get('target_layer_key') or '-'}; "
            f"align={packet.get('target_alignment_label')}; "
            f"color={packet.get('color_rgb')}; "
            f"contrast={packet.get('contrast')}; "
            f"opacity={packet.get('opacity')}; "
            f"gamma={packet.get('gamma')}; "
            f"breathing={packet.get('breathing_enabled')}@{packet.get('breathing_period_s')}s; "
            f"bridge={packet.get('renderer_bridge_contract')}; "
            f"identity_warning={self.boundary_identity_warning_text()}; "
            f"renderer_ack={self.boundary_highlight_ack_summary_text()}"
        )

    def collect_cursor_geodesy_readout(self) -> dict[str, object]:
        return cursor_geodesy_readout_packet(
            self.cursor_latitude,
            self.cursor_longitude,
            "rrkal_displaytools_qt_panel",
        )

    def cursor_geodesy_summary_text(self) -> str:
        packet = self.collect_cursor_geodesy_readout()
        contract = packet.get("cursor_summary_contract", {})
        label = "Cursor geodesy"
        if isinstance(contract, dict):
            label = str(contract.get("label") or label)
        state = self.cursor_geodesy_state_payload if isinstance(self.cursor_geodesy_state_payload, dict) else {}
        ack = self.cursor_geodesy_ack_payload if isinstance(self.cursor_geodesy_ack_payload, dict) else {}
        hit = state.get("hit", ack.get("hit"))
        latitude = state.get("latitude", ack.get("latitude", packet.get("latitude")))
        longitude = state.get("longitude", ack.get("longitude", packet.get("longitude")))
        if hit is True and isinstance(latitude, (int, float)) and isinstance(longitude, (int, float)):
            hit_state = "hit"
            position = f"lat={float(latitude):.4f}; lon={float(longitude):.4f}"
        elif hit is False:
            hit_state = "outside_globe"
            position = "lat=-; lon=-"
        elif packet.get("last_known_position_available") and isinstance(latitude, (int, float)) and isinstance(longitude, (int, float)):
            hit_state = "preview_estimate"
            position = f"lat={float(latitude):.4f}; lon={float(longitude):.4f}"
        else:
            hit_state = "pending"
            position = "lat=-; lon=-"
        return (
            f"{label}: source={packet.get('source')}; "
            f"state={hit_state}; "
            f"{position}; "
            f"state_file={packet.get('renderer_raycast_state_file')}; "
            f"ack_file={packet.get('renderer_raycast_ack_file')}; "
            f"method={packet.get('renderer_raycast_method')}"
        )

    def research_interaction_summary_text(self) -> str:
        contract = self.collect_layer_research_workflow().get("research_summary_contract", {})
        label = "Research interaction"
        if isinstance(contract, dict):
            label = str(contract.get("label") or label)
        parts = [
            self.layer_selection_summary_text(),
            self.pin_overlay_summary_text(),
            self.cursor_geodesy_summary_text(),
            self.boundary_emphasis_summary_text(),
        ]
        return f"{label}: " + " | ".join(parts)

    def open_boundary_emphasis_dialog(self, layer_key: str | bool | None = None) -> None:
        if isinstance(layer_key, bool):
            layer_key = None
        if isinstance(layer_key, str) and layer_key in BOUNDARY_EMPHASIS_TARGET_BY_LAYER:
            self.select_layer(layer_key)
            state = getattr(self, "boundary_emphasis_state", None)
            self.boundary_emphasis_state = dict(state) if isinstance(state, dict) else {}
            self.boundary_emphasis_state["target_mode"] = BOUNDARY_EMPHASIS_TARGET_BY_LAYER[layer_key]
        packet = self.collect_boundary_emphasis_control()
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Boundary emphasis controls")
        layout = QtWidgets.QVBoxLayout(dialog)
        note = QtWidgets.QLabel(
            "Controls the UI profile for country/territory/territorial sea/EEZ emphasis. "
            "Renderer mask bridge is wired through the boundary highlight mask; authoritative polygon identity remains pending."
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        form = QtWidgets.QFormLayout()
        target_combo = QtWidgets.QComboBox()
        target_combo.addItems(
            [
                "auto_selected_boundary_layer",
                "country_boundary",
                "territorial_sea",
                "exclusive_economic_zone",
                "maritime_boundary",
            ]
        )
        current_target = str(packet.get("target_mode") or "auto_selected_boundary_layer")
        index = target_combo.findText(current_target)
        if index >= 0:
            target_combo.setCurrentIndex(index)
        form.addRow("Target", target_combo)
        rgb_widgets: list[QtWidgets.QSpinBox] = []
        rgb_layout = QtWidgets.QHBoxLayout()
        for label, value in zip(("R", "G", "B"), packet.get("color_rgb", [80, 180, 255])):
            spin = QtWidgets.QSpinBox()
            spin.setRange(0, 255)
            spin.setPrefix(f"{label} ")
            spin.setValue(int(value))
            rgb_widgets.append(spin)
            rgb_layout.addWidget(spin)
        form.addRow("RGB", rgb_layout)
        horizontal = getattr(QtCore.Qt, "Horizontal", None)
        if horizontal is None:
            horizontal = QtCore.Qt.Orientation.Horizontal

        def _slider(value: float, scale: int, minimum: int, maximum: int) -> QtWidgets.QSlider:
            slider = QtWidgets.QSlider(horizontal)
            slider.setRange(minimum, maximum)
            slider.setValue(int(round(value * scale)))
            return slider

        contrast_slider = _slider(float(packet.get("contrast", 1.35)), 100, 50, 300)
        opacity_slider = _slider(float(packet.get("opacity", 0.42)), 100, 0, 100)
        gamma_slider = _slider(float(packet.get("gamma", 1.0)), 100, 25, 250)
        breathing_checkbox = QtWidgets.QCheckBox("Enable breathing highlight")
        breathing_checkbox.setChecked(bool(packet.get("breathing_enabled", True)))
        breathing_period_slider = _slider(float(packet.get("breathing_period_s", 4.0)), 10, 10, 120)
        form.addRow("Contrast", contrast_slider)
        form.addRow("Opacity", opacity_slider)
        form.addRow("Gamma", gamma_slider)
        form.addRow("Breathing", breathing_checkbox)
        form.addRow("Breathing period", breathing_period_slider)
        layout.addLayout(form)
        color_swatch = QtWidgets.QLabel("Boundary emphasis RGB swatch")
        color_swatch.setObjectName("boundaryEmphasisSwatch")
        color_swatch.setMinimumHeight(28)
        color_swatch.setWordWrap(True)
        layout.addWidget(color_swatch)
        preview_label = QtWidgets.QLabel()
        preview_label.setObjectName("boundaryEmphasisPreview")
        preview_label.setWordWrap(True)
        layout.addWidget(preview_label)

        def _refresh_preview(*_args: object) -> None:
            preview_color = [spin.value() for spin in rgb_widgets]
            contrast = contrast_slider.value() / 100.0
            opacity = opacity_slider.value() / 100.0
            gamma = gamma_slider.value() / 100.0
            breathing_period_s = breathing_period_slider.value() / 10.0
            breathing_state = "on" if breathing_checkbox.isChecked() else "off"
            color_swatch.setStyleSheet(
                "QLabel#boundaryEmphasisSwatch { "
                f"background: rgb({preview_color[0]}, {preview_color[1]}, {preview_color[2]}); "
                "border: 1px solid #536270; border-radius: 6px; color: #101820; padding: 6px; "
                "}"
            )
            preview_label.setText(
                "Boundary emphasis preview: "
                f"target={target_combo.currentText()}; RGB={preview_color}; "
                f"contrast={contrast:.2f}; opacity={opacity:.2f}; gamma={gamma:.2f}; "
                f"breathing={breathing_state}/{breathing_period_s:.1f}s; "
                f"bridge={packet.get('renderer_bridge_contract')}"
            )

        for spin in rgb_widgets:
            spin.valueChanged.connect(_refresh_preview)
        target_combo.currentTextChanged.connect(_refresh_preview)
        contrast_slider.valueChanged.connect(_refresh_preview)
        opacity_slider.valueChanged.connect(_refresh_preview)
        gamma_slider.valueChanged.connect(_refresh_preview)
        breathing_checkbox.toggled.connect(_refresh_preview)
        breathing_period_slider.valueChanged.connect(_refresh_preview)
        _refresh_preview()
        buttons = QtWidgets.QHBoxLayout()
        apply_button = QtWidgets.QPushButton("Apply UI state")
        close_button = QtWidgets.QPushButton("Close")
        buttons.addWidget(apply_button)
        buttons.addWidget(close_button)
        layout.addLayout(buttons)

        def _apply_state() -> None:
            target_mode = target_combo.currentText()
            color_rgb = [spin.value() for spin in rgb_widgets]
            contrast = contrast_slider.value() / 100.0
            opacity = opacity_slider.value() / 100.0
            gamma = gamma_slider.value() / 100.0
            breathing_enabled = breathing_checkbox.isChecked()
            breathing_period_s = breathing_period_slider.value() / 10.0
            self.boundary_emphasis_state = {
                "target_mode": target_mode,
                "color_rgb": color_rgb,
                "contrast": contrast,
                "opacity": opacity,
                "gamma": gamma,
                "breathing_enabled": breathing_enabled,
                "breathing_period_s": breathing_period_s,
            }
            target_layer = BOUNDARY_EMPHASIS_LAYER_BY_TARGET.get(target_mode)
            selected_layer_key = getattr(self, "selected_layer_key", None)
            if target_layer is None and selected_layer_key in BOUNDARY_EMPHASIS_TARGET_BY_LAYER:
                target_layer = selected_layer_key
            target_layers = [target_layer] if isinstance(target_layer, str) else list(BOUNDARY_HIGHLIGHT_LAYER_KEYS)
            self.boundary_highlight_state = normalized_boundary_highlight_state(
                {
                    "schema": BOUNDARY_HIGHLIGHT_SCHEMA,
                    "enabled": True,
                    "trigger": "hover",
                    "target_layers": target_layers,
                    "color_rgb": color_rgb,
                    "contrast": max(0, min(100, int(round(contrast * 50.0)))),
                    "alpha": max(0, min(100, int(round(opacity * 100.0)))),
                    "gamma": max(25, min(300, int(round(gamma * 100.0)))),
                    "feather": 14,
                    "breathing": {
                        "enabled": breathing_enabled,
                        "speed": max(0, min(100, int(round(100.0 / max(1.0, breathing_period_s))))),
                        "amplitude": 16,
                    },
                }
            )
            self.refresh_boundary_highlight_status()
            self.refresh_command_preview()
            self.refresh_canvas_preview()
            updated = self.collect_boundary_emphasis_control()
            if hasattr(self, "boundary_emphasis_label"):
                self.boundary_emphasis_label.setText(
                    f"Boundary emphasis: {updated.get('status', 'unknown')} "
                    f"target={updated.get('target_mode')}->{updated.get('target_layer_key') or '-'} "
                    f"align={updated.get('target_alignment_label')} color={updated.get('color_rgb')} "
                    f"opacity={updated.get('opacity')} bridge={updated.get('renderer_bridge_contract')}"
                )
        apply_button.clicked.connect(_apply_state)
        close_button.clicked.connect(dialog.accept)
        if hasattr(dialog, "exec"):
            dialog.exec()
        else:
            dialog.exec_()

    def collect_layer_capability_matrix(self) -> dict[str, object]:
        runtime_ack = self.layer_runtime_ack_payload if isinstance(self.layer_runtime_ack_payload, dict) else None
        pick_state = self.layer_pick_state_payload if isinstance(self.layer_pick_state_payload, dict) else None
        identity_source_ref = self.rrkal_manifest_ref_edit.text().strip()
        return layer_capability_matrix_packet(
            "rrkal_displaytools_qt_panel",
            self.selected_layer_key,
            runtime_ack,
            pick_state,
            identity_source_ref,
        )

    def collect_layer_runtime_state(self) -> dict[str, object]:
        layers = self.collect_layer_stack_ui()
        for key, _label in LAYER_LABELS:
            if key in self.checks and key in layers:
                layers[key]["visible"] = self.checks[key].isChecked()
        visible_layers = [key for key, _label in LAYER_LABELS if key in self.checks and self.checks[key].isChecked()]
        locked_layers = [key for key, _label in LAYER_LABELS if key in self.layer_locks and self.layer_locks[key].isChecked()]
        selected_renderer_layer = (
            LAYER_RUNTIME_ID_ALIASES.get(self.selected_layer_key, self.selected_layer_key)
            if self.selected_layer_key
            else None
        )
        selected_layer_state = layers.get(self.selected_layer_key) if self.selected_layer_key else None
        selected_layer_label = next(
            (label for key, label in LAYER_LABELS if key == self.selected_layer_key),
            self.selected_layer_key,
        )
        return {
            "schema": "rrkal_displaytools.layer_runtime_state.v1",
            "updated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "source": "rrkal_displaytools_qt_panel",
            "selected_layer": self.selected_layer_key,
            "selected_renderer_layer": selected_renderer_layer,
            "selected_layer_semantic_target": {
                "ui_layer": self.selected_layer_key,
                "renderer_layer": selected_renderer_layer,
                "label": selected_layer_label,
                "state": selected_layer_state,
            }
            if self.selected_layer_key
            else None,
            "visible_layers": visible_layers,
            "locked_layers": locked_layers,
            "layer_visibility_snapshot_active": self.layer_visibility_snapshot is not None,
            "layer_visibility_snapshot": self.layer_visibility_snapshot,
            "layer_capability_matrix": self.collect_layer_capability_matrix(),
            "layers": layers,
        }

    def write_layer_runtime_state(self) -> None:
        if not self.checks:
            return
        payload = self.collect_layer_runtime_state()
        try:
            LAYER_RUNTIME_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
            LAYER_RUNTIME_STATE_PATH.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            self.layer_runtime_state_last_write_utc = str(payload.get("updated_at_utc", ""))
            self.layer_runtime_state_write_error = None
            self.refresh_layer_runtime_state_label(payload)
            self.append_layer_runtime_history(payload)
        except OSError as exc:
            self.layer_runtime_state_write_error = str(exc)
            self.refresh_layer_runtime_state_label(payload)
            print(f"Unable to write layer runtime state: {exc}")

    def refresh_layer_runtime_state_label(self, payload: dict[str, object] | None = None) -> None:
        if self.layer_runtime_state_label is None:
            return
        if payload is None:
            payload = self.collect_layer_runtime_state()
        visible_layers = payload.get("visible_layers", [])
        visible_count = len(visible_layers) if isinstance(visible_layers, list) else "-"
        selected_layer = str(payload.get("selected_layer") or "-")
        selected_renderer_layer = str(payload.get("selected_renderer_layer") or "-")
        if self.layer_runtime_state_write_error:
            self.layer_runtime_state_label.setText(
                f"Layer runtime bridge: write failed: {self.layer_runtime_state_write_error}"
            )
            return
        last_write = self.layer_runtime_state_last_write_utc or str(payload.get("updated_at_utc", "-"))
        self.layer_runtime_state_label.setText(
            f"Layer runtime bridge: {LAYER_RUNTIME_STATE_PATH.name}; selected={selected_layer}; "
            f"renderer_target={selected_renderer_layer}; visible={visible_count}/{len(LAYER_LABELS)}; "
            f"last_write={last_write}; visibility/opacity live, overlay/split blend live, "
            "selected-layer semantic target live, lock guard live"
        )

    def append_layer_runtime_history(self, payload: dict[str, object]) -> None:
        visible_layers = payload.get("visible_layers", [])
        locked_layers = payload.get("locked_layers", [])
        visible_count = len(visible_layers) if isinstance(visible_layers, list) else 0
        locked_count = len(locked_layers) if isinstance(locked_layers, list) else 0
        signature = json.dumps(
            {
                "selected_layer": payload.get("selected_layer"),
                "visible_layers": visible_layers,
                "locked_layers": locked_layers,
                "snapshot": payload.get("layer_visibility_snapshot_active"),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        if signature == self.layer_runtime_history_signature:
            return
        self.layer_runtime_history_signature = signature
        updated_at = str(payload.get("updated_at_utc", "-"))
        selected_layer = str(payload.get("selected_layer") or "-")
        snapshot = "snapshot" if payload.get("layer_visibility_snapshot_active") else "no snapshot"
        entry = (
            f"↻ Layer runtime {updated_at}: selected={selected_layer}, "
            f"visible={visible_count}/{len(LAYER_LABELS)}, locked={locked_count}, {snapshot}"
        )
        self.layer_runtime_history.insert(0, entry)
        del self.layer_runtime_history[10:]
        if self.history_list is None:
            return
        self.history_list.insertItem(0, entry)
        while self.history_list.count() > 18:
            self.history_list.takeItem(self.history_list.count() - 1)

    def refresh_layer_runtime_ack_state(self) -> None:
        try:
            stat = LAYER_RUNTIME_ACK_PATH.stat()
        except FileNotFoundError:
            if self.layer_runtime_ack_mtime_ns is not None:
                self.layer_runtime_ack_mtime_ns = None
                self.layer_runtime_ack_payload = None
                self.update_layer_runtime_badges()
                self.refresh_layer_properties()
                if self.layer_runtime_ack_label is not None:
                    self.layer_runtime_ack_label.setText(f"Renderer ack: waiting for {LAYER_RUNTIME_ACK_PATH.name}")
            return
        except OSError as exc:
            if self.layer_runtime_ack_label is not None:
                self.layer_runtime_ack_label.setText(f"Renderer ack read failed: {exc}")
            return
        if stat.st_mtime_ns == self.layer_runtime_ack_mtime_ns:
            return
        next_mtime_ns = stat.st_mtime_ns
        try:
            payload = json.loads(LAYER_RUNTIME_ACK_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            if self.layer_runtime_ack_label is not None:
                self.layer_runtime_ack_label.setText(f"Renderer ack parse failed: {exc}")
            return
        self.layer_runtime_ack_mtime_ns = next_mtime_ns
        if isinstance(payload, dict):
            self.layer_runtime_ack_payload = payload
            self.refresh_layer_runtime_ack_label(payload)
            self.update_layer_runtime_badges()
            self.refresh_layer_properties()
            self.refresh_research_provenance()

    def refresh_layer_runtime_ack_label(self, payload: dict[str, object]) -> None:
        if self.layer_runtime_ack_label is None:
            return
        event = str(payload.get("event", "-"))
        changed_layers = payload.get("changed_layers", [])
        changed_count = len(changed_layers) if isinstance(changed_layers, list) else "-"
        changed_opacity_layers = payload.get("changed_opacity_layers", [])
        changed_opacity_count = len(changed_opacity_layers) if isinstance(changed_opacity_layers, list) else "-"
        changed_blend_layers = payload.get("changed_blend_layers", [])
        changed_blend_count = len(changed_blend_layers) if isinstance(changed_blend_layers, list) else "-"
        skipped_locked_layers = payload.get("skipped_locked_layers", [])
        skipped_count = len(skipped_locked_layers) if isinstance(skipped_locked_layers, list) else "-"
        boundary_blend = str(payload.get("boundary_aggregate_blend_mode", "-"))
        selected_renderer_layer = str(payload.get("selected_renderer_layer") or "-")
        frame_index = payload.get("frame_index", "-")
        updated_at = str(payload.get("updated_at_utc", "-"))
        error = payload.get("error")
        if error:
            self.layer_runtime_ack_label.setText(f"Renderer ack: event={event}, error={error}, updated={updated_at}")
            return
        self.layer_runtime_ack_label.setText(
            f"Renderer ack: event={event}, changed={changed_count}, opacity={changed_opacity_count}, "
            f"blend={changed_blend_count}, "
            f"target={selected_renderer_layer}, boundary_blend={boundary_blend}, "
            f"skipped_locked={skipped_count}, frame={frame_index}, updated={updated_at}"
        )

    def update_layer_runtime_badges(self) -> None:
        if not self.layer_runtime_badges:
            return
        matrix = self.collect_layer_capability_matrix()
        layers = matrix.get("layers", [])
        if not isinstance(layers, list):
            return
        for layer in layers:
            if not isinstance(layer, dict):
                continue
            key = str(layer.get("key", ""))
            badge = self.layer_runtime_badges.get(key)
            if badge is None:
                continue
            runtime_status = layer.get("runtime_status")
            statuses = [str(item) for item in runtime_status] if isinstance(runtime_status, list) else ["no_ack"]
            if "ack_error" in statuses:
                text = "error"
            elif "skipped_locked" in statuses:
                text = "locked"
            elif any(status.endswith("_changed") for status in statuses):
                text = "changed"
            elif "selected_target" in statuses:
                text = "target"
            elif "no_recent_change" in statuses:
                text = "ok"
            else:
                text = "no_ack"
            badge.setText(text)
            badge.setStyleSheet(layer_runtime_badge_style(text))
            badge.setToolTip(", ".join(statuses))

    def refresh_layer_pick_state(self) -> None:
        try:
            stat = LAYER_PICK_STATE_PATH.stat()
        except FileNotFoundError:
            if self.layer_pick_state_mtime_ns is not None:
                self.layer_pick_state_mtime_ns = None
                if self.layer_pick_state_label is not None:
                    self.layer_pick_state_label.setText(f"Layer pick: waiting for {LAYER_PICK_STATE_PATH.name}")
            return
        except OSError as exc:
            if self.layer_pick_state_label is not None:
                self.layer_pick_state_label.setText(f"Layer pick read failed: {exc}")
            return
        if stat.st_mtime_ns == self.layer_pick_state_mtime_ns:
            return
        next_mtime_ns = stat.st_mtime_ns
        try:
            payload = json.loads(LAYER_PICK_STATE_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            if self.layer_pick_state_label is not None:
                self.layer_pick_state_label.setText(f"Layer pick parse failed: {exc}")
            return
        self.layer_pick_state_mtime_ns = next_mtime_ns
        if isinstance(payload, dict):
            self.layer_pick_state_payload = payload
            self.refresh_layer_pick_state_label(payload)
            self.refresh_layer_properties()
            self.refresh_research_provenance()

    def refresh_layer_pick_state_label(self, payload: dict[str, object]) -> None:
        if self.layer_pick_state_label is None:
            return
        result = payload.get("pick_result")
        result = result if isinstance(result, dict) else {}
        event = str(result.get("event") or payload.get("event") or "-")
        target = str(payload.get("selected_renderer_layer") or result.get("renderer_layer") or "-")
        picker = str(result.get("picker") or "-")
        hit = result.get("hit")
        hit_detail = result.get("hit_detail")
        hit_detail = hit_detail if isinstance(hit_detail, dict) else {}
        feature = hit_detail.get("feature")
        feature_text = ""
        if isinstance(feature, dict):
            feature_label = str(feature.get("label") or feature.get("feature_index") or "-")
            if len(feature_label) > 72:
                feature_label = f"{feature_label[:69]}..."
            if feature_label != "-":
                feature_text = f", feature={feature_label}"
        frame_index = payload.get("frame_index", "-")
        screen_position = payload.get("screen_position")
        screen_position = screen_position if isinstance(screen_position, dict) else {}
        screen_x = screen_position.get("screen_x")
        screen_y = screen_position.get("screen_y")
        screen_text = (
            f", pos=({float(screen_x):.1f},{float(screen_y):.1f})"
            if isinstance(screen_x, (int, float)) and isinstance(screen_y, (int, float))
            else ""
        )
        updated_at = str(payload.get("updated_at_utc", "-"))
        self.layer_pick_state_label.setText(
            f"Layer pick: event={event}, target={target}, picker={picker}, hit={hit}{feature_text}, "
            f"frame={frame_index}{screen_text}, updated={updated_at}"
        )
        if self.history_list is not None:
            self.history_list.insertItem(
                0,
                f"Layer pick history {updated_at}: target={target}, picker={picker}, hit={hit}{feature_text}, "
                f"frame={frame_index}{screen_text}",
            )
            while self.history_list.count() > 18:
                self.history_list.takeItem(self.history_list.count() - 1)

    def refresh_pin_input_ack_state(self) -> None:
        try:
            stat = PIN_INPUT_ACK_PATH.stat()
        except FileNotFoundError:
            if self.pin_input_ack_mtime_ns is not None:
                self.pin_input_ack_mtime_ns = None
                if self.pin_input_ack_label is not None:
                    self.pin_input_ack_label.setText(f"Renderer input ack: waiting for {PIN_INPUT_ACK_PATH.name}")
            return
        except OSError as exc:
            if self.pin_input_ack_label is not None:
                self.pin_input_ack_label.setText(f"Renderer input ack read failed: {exc}")
            return
        if stat.st_mtime_ns == self.pin_input_ack_mtime_ns:
            return
        next_mtime_ns = stat.st_mtime_ns
        try:
            payload = json.loads(PIN_INPUT_ACK_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            if self.pin_input_ack_label is not None:
                self.pin_input_ack_label.setText(f"Renderer input ack parse failed: {exc}")
            return
        self.pin_input_ack_mtime_ns = next_mtime_ns
        if isinstance(payload, dict):
            self.pin_input_ack_payload = payload
            self.refresh_pin_input_ack_label(payload)
            self.refresh_research_provenance()

    def refresh_pin_input_ack_label(self, payload: dict[str, object]) -> None:
        if self.pin_input_ack_label is None:
            return
        pin_count = payload.get("pin_count", "-")
        selected_pin_id = str(payload.get("selected_pin_id") or "-")
        selected_exists = payload.get("selected_pin_exists", "-")
        updated_at = str(payload.get("updated_at_utc", "-"))
        self.pin_input_ack_label.setText(
            f"Renderer input ack: pins={pin_count}, selected={selected_pin_id}, "
            f"selected_exists={selected_exists}, updated={updated_at}"
        )

    def cursor_geodesy_bridge_text(self) -> str:
        state = self.cursor_geodesy_state_payload if isinstance(self.cursor_geodesy_state_payload, dict) else {}
        ack = self.cursor_geodesy_ack_payload if isinstance(self.cursor_geodesy_ack_payload, dict) else {}
        error = ack.get("error")
        if error:
            return f"Renderer cursor geodesy: ack error={error}"
        if not state and not ack:
            return f"Renderer cursor geodesy: waiting for {CURSOR_GEODESY_STATE_PATH.name}"
        event = str(ack.get("event") or state.get("event") or "-")
        frame = ack.get("frame_index", state.get("frame_index", "-"))
        updated = str(ack.get("updated_at_utc") or state.get("updated_at_utc") or "-")
        hit = state.get("hit", ack.get("hit"))
        latitude = state.get("latitude", ack.get("latitude"))
        longitude = state.get("longitude", ack.get("longitude"))
        if hit is True and isinstance(latitude, (int, float)) and isinstance(longitude, (int, float)):
            return f"Renderer cursor geodesy: hit lat={float(latitude):.4f}, lon={float(longitude):.4f}, event={event}, frame={frame}, updated={updated}"
        if hit is False:
            return f"Renderer cursor geodesy: outside globe, event={event}, frame={frame}, updated={updated}"
        return f"Renderer cursor geodesy: state pending, event={event}, frame={frame}, updated={updated}"

    def refresh_cursor_geodesy_bridge_label(self) -> None:
        if self.cursor_geodesy_bridge_label is not None:
            self.cursor_geodesy_bridge_label.setText(self.cursor_geodesy_bridge_text())

    def refresh_cursor_geodesy_bridge_state(self) -> None:
        changed = False
        for path, mtime_attr, payload_attr in (
            (CURSOR_GEODESY_STATE_PATH, "cursor_geodesy_state_mtime_ns", "cursor_geodesy_state_payload"),
            (CURSOR_GEODESY_ACK_PATH, "cursor_geodesy_ack_mtime_ns", "cursor_geodesy_ack_payload"),
        ):
            try:
                stat = path.stat()
            except FileNotFoundError:
                if getattr(self, mtime_attr) is not None:
                    setattr(self, mtime_attr, None)
                    setattr(self, payload_attr, None)
                    changed = True
                continue
            except OSError as exc:
                if self.cursor_geodesy_bridge_label is not None:
                    self.cursor_geodesy_bridge_label.setText(f"Renderer cursor geodesy read failed: {exc}")
                return
            if stat.st_mtime_ns == getattr(self, mtime_attr):
                continue
            next_mtime_ns = stat.st_mtime_ns
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                if self.cursor_geodesy_bridge_label is not None:
                    self.cursor_geodesy_bridge_label.setText(f"Renderer cursor geodesy parse failed: {exc}")
                return
            setattr(self, mtime_attr, next_mtime_ns)
            if isinstance(payload, dict):
                setattr(self, payload_attr, payload)
                changed = True
        if changed:
            self.refresh_cursor_geodesy_bridge_label()
            self.refresh_tool_target()

    def current_pin_label_mode(self) -> str:
        if self.pin_label_mode_combo is None:
            return "auto"
        data = self.pin_label_mode_combo.currentData()
        return data if isinstance(data, str) else "auto"

    def set_pin_label_mode(self, mode: str) -> None:
        if self.pin_label_mode_combo is None:
            return
        for index in range(self.pin_label_mode_combo.count()):
            if self.pin_label_mode_combo.itemData(index) == mode:
                self.pin_label_mode_combo.setCurrentIndex(index)
                return
        self.pin_label_mode_combo.setCurrentIndex(0)

    def collect_tool_state(self) -> dict[str, object]:
        return {
            "active_tool": self.active_tool,
            "target_layer": self.selected_layer_key,
            "pin_label_mode": self.current_pin_label_mode(),
            "pin_label_min_priority": self.pin_label_min_priority_spin.value() if self.pin_label_min_priority_spin is not None else 50,
            "pin": {
                "type": self.pin_type_combo.currentText() if self.pin_type_combo is not None else "Observation",
                "label": self.pin_label_edit.text().strip() if self.pin_label_edit is not None else "",
                "note": self.pin_note_edit.text().strip() if self.pin_note_edit is not None else "",
                "latitude": self.pin_lat_edit.text().strip() if self.pin_lat_edit is not None else "",
                "longitude": self.pin_lon_edit.text().strip() if self.pin_lon_edit is not None else "",
                "label_priority": self.pin_priority_spin.value() if self.pin_priority_spin is not None else 50,
                "placement": self.pin_coordinate_source,
                "coordinate_source": self.pin_coordinate_source,
                "coordinate_source_label": self.pin_coordinate_source_label(),
            },
            "renderer_sync": "planned",
            "cursor_fill_priority": "renderer_cursor_geodesy_state_then_ui_estimate",
        }

    def collect_research_pins(self) -> list[dict[str, object]]:
        return [dict(pin) for pin in self.research_pins]

    def pin_overlay_summary_text(self) -> str:
        projection_contract = pin_projection_contract_packet()
        contract = projection_contract.get("pin_summary_contract", {})
        label = "Pin overlay"
        if isinstance(contract, dict):
            label = str(contract.get("label") or label)
        occlusion_statuses = projection_contract.get("occlusion_status_values", [])
        if isinstance(occlusion_statuses, list):
            occlusion_status_text = ",".join(str(value) for value in occlusion_statuses)
        else:
            occlusion_status_text = "unknown"
        legend_object = str(projection_contract.get("qt_occlusion_legend_object") or "pinOcclusionLegend")
        selected = self.selected_pin_packet()
        selected_id = self.selected_pin_id or "none"
        source_key = None
        if isinstance(selected, dict):
            source_key = str(selected.get("coordinate_source") or selected.get("placement") or "manual_lat_lon")
        coordinate_source_label = self.pin_coordinate_source_label(source_key)
        return (
            f"{label}: pins={len(self.research_pins)}; "
            f"selected={selected_id}; "
            f"source={coordinate_source_label}; "
            f"pick_state=state/{PIN_PICK_STATE_PATH.name}; "
            "rotation=per_frame; "
            f"occlusion=horizon_depth; occlusion_statuses={occlusion_status_text}; "
            f"legend={legend_object}"
        )

    def collect_boundary_highlight_state(self) -> dict[str, object]:
        return normalized_boundary_highlight_state(self.boundary_highlight_state)

    def boundary_highlight_summary(self) -> str:
        state = self.collect_boundary_highlight_state()
        color_rgb = state.get("color_rgb", [255, 190, 72])
        color_text = (
            f"{color_rgb[0]},{color_rgb[1]},{color_rgb[2]}"
            if isinstance(color_rgb, list) and len(color_rgb) >= 3
            else "255,190,72"
        )
        breathing = state.get("breathing", {})
        breathing_enabled = isinstance(breathing, dict) and breathing.get("enabled") is True
        target_layers = state.get("target_layers", [])
        target_count = len(target_layers) if isinstance(target_layers, list) else 0
        gamma = _coerce_int(state.get("gamma"), 100, 25, 300) / 100.0
        return (
            f"{'On' if state.get('enabled') else 'Off'}; trigger={state.get('trigger', 'hover')}; "
            f"RGB={color_text}; contrast={state.get('contrast')}%; alpha={state.get('alpha')}%; "
            f"gamma={gamma:.2f}; feather={state.get('feather')}%; "
            f"breath={'on' if breathing_enabled else 'off'}; targets={target_count}; line mask live; closed-ring fill live"
        )

    def boundary_identity_status_summary(self) -> str:
        state = self.collect_boundary_highlight_state()
        identity_status = state.get("identity_status")
        if not isinstance(identity_status, dict):
            identity_status = default_boundary_identity_status()
        applied = identity_status.get("applied", [])
        pending = identity_status.get("pending", [])
        applied_items = [str(item) for item in applied] if isinstance(applied, list) else []
        pending_items = [str(item) for item in pending] if isinstance(pending, list) else []
        applied_count = len(applied_items)
        pending_count = len(pending_items)
        applied_text = ", ".join(applied_items[:3]) or "-"
        pending_text = ", ".join(pending_items[:3]) or "-"
        if len(applied_items) > 3:
            applied_text = f"{applied_text}, +{len(applied_items) - 3}"
        if len(pending_items) > 3:
            pending_text = f"{pending_text}, +{len(pending_items) - 3}"
        boundary = str(identity_status.get("boundary", "visual/source-property preview only"))
        source_summary = str(identity_status.get("identity_source_hint_summary", "")).strip()
        if source_summary:
            return (
                f"applied={applied_count} [{applied_text}]; pending={pending_count} [{pending_text}]; "
                f"{boundary}; source_hint={source_summary}"
            )
        return f"applied={applied_count} [{applied_text}]; pending={pending_count} [{pending_text}]; {boundary}"

    def boundary_identity_warning_text(self) -> str:
        state = self.collect_boundary_highlight_state()
        identity_status = state.get("identity_status")
        if not isinstance(identity_status, dict):
            identity_status = default_boundary_identity_status()
        pending = identity_status.get("pending", [])
        pending_items = [str(item) for item in pending] if isinstance(pending, list) else []
        identity_hint = identity_status.get("identity_source_hint")
        identity_hint = identity_hint if isinstance(identity_hint, dict) else {}
        open_line_status = str(
            identity_hint.get("open_line_area_inference_status", "pending_backend_geometry_closure")
        )
        if pending_items:
            pending_text = ", ".join(pending_items[:3])
            if len(pending_items) > 3:
                pending_text = f"{pending_text}, +{len(pending_items) - 3}"
            return (
                f"Pending authoritative identity: {pending_text}; open_line={open_line_status}; "
                "use RRKAL-governed polygon/EEZ source before authoritative boundary claims."
            )
        return "Boundary identity source reports no pending authoritative identity items."

    def boundary_highlight_ack_summary_text(self, payload: dict[str, object] | None = None) -> str:
        payload = payload if isinstance(payload, dict) else self.boundary_highlight_ack_payload
        if not isinstance(payload, dict):
            return f"waiting_for_renderer_ack:{BOUNDARY_HIGHLIGHT_ACK_PATH.name}"
        updated_at = str(payload.get("updated_at_utc", "-"))
        error = payload.get("error")
        if error:
            return f"error={error}; updated={updated_at}"
        target_layers = payload.get("target_layers", [])
        renderer_layers = payload.get("renderer_target_layers", [])
        applies = payload.get("applies", [])
        pending = payload.get("pending", [])
        target_count = len(target_layers) if isinstance(target_layers, list) else "-"
        renderer_count = len(renderer_layers) if isinstance(renderer_layers, list) else "-"
        applies_count = len(applies) if isinstance(applies, list) else "-"
        pending_count = len(pending) if isinstance(pending, list) else "-"
        return (
            f"enabled={payload.get('enabled', '-')}; targets={target_count}; "
            f"renderer_targets={renderer_count}; live_scopes={applies_count}; "
            f"pending={pending_count}; updated={updated_at}"
        )

    def refresh_boundary_highlight_status(self) -> None:
        if self.boundary_highlight_label is not None:
            self.boundary_highlight_label.setText(self.boundary_highlight_summary())
        if self.boundary_identity_status_label is not None:
            self.boundary_identity_status_label.setText(self.boundary_identity_status_summary())
        if self.boundary_identity_warning_label is not None:
            self.boundary_identity_warning_label.setText(self.boundary_identity_warning_text())

    def refresh_boundary_highlight_ack_state(self) -> None:
        try:
            stat = BOUNDARY_HIGHLIGHT_ACK_PATH.stat()
        except FileNotFoundError:
            if self.boundary_highlight_ack_mtime_ns is not None:
                self.boundary_highlight_ack_mtime_ns = None
                if self.boundary_highlight_ack_label is not None:
                    self.boundary_highlight_ack_label.setText(
                        f"Boundary ack: waiting for {BOUNDARY_HIGHLIGHT_ACK_PATH.name}"
                    )
            return
        except OSError as exc:
            if self.boundary_highlight_ack_label is not None:
                self.boundary_highlight_ack_label.setText(f"Boundary ack read failed: {exc}")
            return
        if stat.st_mtime_ns == self.boundary_highlight_ack_mtime_ns:
            return
        next_mtime_ns = stat.st_mtime_ns
        try:
            payload = json.loads(BOUNDARY_HIGHLIGHT_ACK_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            if self.boundary_highlight_ack_label is not None:
                self.boundary_highlight_ack_label.setText(f"Boundary ack parse failed: {exc}")
            return
        self.boundary_highlight_ack_mtime_ns = next_mtime_ns
        if isinstance(payload, dict):
            self.boundary_highlight_ack_payload = payload
            self.refresh_boundary_highlight_ack_label(payload)
            self.refresh_research_provenance()

    def refresh_boundary_highlight_ack_label(self, payload: dict[str, object]) -> None:
        enabled = payload.get("enabled", "-")
        target_layers = payload.get("target_layers", [])
        target_count = len(target_layers) if isinstance(target_layers, list) else "-"
        renderer_layers = payload.get("renderer_target_layers", [])
        renderer_count = len(renderer_layers) if isinstance(renderer_layers, list) else "-"
        applies = payload.get("applies", [])
        applies_count = len(applies) if isinstance(applies, list) else "-"
        pending = payload.get("pending", [])
        pending_count = len(pending) if isinstance(pending, list) else "-"
        updated_at = str(payload.get("updated_at_utc", "-"))
        error = payload.get("error")
        if error:
            text = f"Boundary ack: error={error}, updated={updated_at}"
            if self.boundary_highlight_ack_label is not None:
                self.boundary_highlight_ack_label.setText(text)
            self.append_boundary_highlight_ack_history(payload)
            return
        text = (
            f"Boundary ack: enabled={enabled}, targets={target_count}, renderer_targets={renderer_count}, "
            f"live_scopes={applies_count}, pending={pending_count}, updated={updated_at}"
        )
        if self.boundary_highlight_ack_label is not None:
            self.boundary_highlight_ack_label.setText(text)
        self.append_boundary_highlight_ack_history(payload)

    def append_boundary_highlight_ack_history(self, payload: dict[str, object]) -> None:
        target_layers = payload.get("target_layers", [])
        target_layers = target_layers if isinstance(target_layers, list) else []
        renderer_layers = payload.get("renderer_target_layers", [])
        renderer_layers = renderer_layers if isinstance(renderer_layers, list) else []
        applies = payload.get("applies", [])
        applies = applies if isinstance(applies, list) else []
        pending = payload.get("pending", [])
        pending = pending if isinstance(pending, list) else []
        signature = json.dumps(
            {
                "enabled": payload.get("enabled"),
                "trigger": payload.get("trigger"),
                "target_layers": target_layers,
                "renderer_target_layers": renderer_layers,
                "applies": applies,
                "pending": pending,
                "error": payload.get("error"),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        if signature == self.boundary_highlight_ack_history_signature:
            return
        self.boundary_highlight_ack_history_signature = signature
        updated_at = str(payload.get("updated_at_utc", "-"))
        target_text = ",".join(str(layer) for layer in target_layers[:3]) or "-"
        if len(target_layers) > 3:
            target_text = f"{target_text},+{len(target_layers) - 3}"
        entry = (
            f"Boundary ack history {updated_at}: enabled={payload.get('enabled')}, trigger={payload.get('trigger')}, "
            f"targets={target_text}, renderer_targets={len(renderer_layers)}, live_scopes={len(applies)}, pending={len(pending)}"
        )
        self.boundary_highlight_ack_history.insert(0, entry)
        del self.boundary_highlight_ack_history[10:]
        if self.history_list is None:
            return
        self.history_list.insertItem(0, entry)
        while self.history_list.count() > 18:
            self.history_list.takeItem(self.history_list.count() - 1)

    def open_boundary_highlight_dialog(self, layer_key: str | None = None) -> None:
        if not isinstance(layer_key, str) or layer_key not in BOUNDARY_HIGHLIGHT_LAYER_KEYS:
            if self.selected_layer_key in BOUNDARY_HIGHLIGHT_LAYER_KEYS:
                layer_key = self.selected_layer_key
            else:
                layer_key = "border_layer"
        self.select_layer(layer_key)
        state = self.collect_boundary_highlight_state()
        dialog = QtWidgets.QDialog(self)
        layer_label = next((label for key, label in LAYER_LABELS if key == layer_key), layer_key)
        dialog.setWindowTitle(f"疆域強調遮罩：{layer_label}")
        layout = QtWidgets.QVBoxLayout(dialog)
        note = QtWidgets.QLabel(
            "控制國界/領海/EEZ/公海 hover 強調遮罩。這是科研定位用的圖層強調狀態，"
            "已寫入 profile / launch packet / provenance。renderer 線段遮罩、閉合 ring fill、"
            "source-property feature identity 已 live；authoritative 疆域/EEZ identity 與 open-line area inference 仍為明確 pending。"
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        form = QtWidgets.QFormLayout()
        enabled = QtWidgets.QCheckBox("啟用 hover 疆域強調")
        enabled.setChecked(bool(state.get("enabled", True)))
        form.addRow("Enabled", enabled)
        trigger_combo = QtWidgets.QComboBox()
        trigger_items = (
            ("hover", "Hover"),
            ("selected", "Selected"),
            ("hover_or_selected", "Hover or selected"),
        )
        for value, label in trigger_items:
            trigger_combo.addItem(label, value)
        for index in range(trigger_combo.count()):
            if trigger_combo.itemData(index) == state.get("trigger"):
                trigger_combo.setCurrentIndex(index)
                break
        form.addRow("Trigger", trigger_combo)
        color_rgb = state.get("color_rgb", [255, 190, 72])
        if not isinstance(color_rgb, list) or len(color_rgb) < 3:
            color_rgb = [255, 190, 72]
        selected_color = [QtGui.QColor(int(color_rgb[0]), int(color_rgb[1]), int(color_rgb[2]))]
        color_button = QtWidgets.QPushButton()

        def update_color_button() -> None:
            color = selected_color[0]
            color_button.setText(f"RGB {color.red()}, {color.green()}, {color.blue()}")
            color_button.setStyleSheet(
                f"background-color: rgb({color.red()}, {color.green()}, {color.blue()}); color: #111; font-weight: 700;"
            )

        def choose_color() -> None:
            color = QtWidgets.QColorDialog.getColor(selected_color[0], dialog, "Boundary highlight RGB")
            if color.isValid():
                selected_color[0] = color
                update_color_button()

        color_button.clicked.connect(choose_color)
        update_color_button()
        form.addRow("RGB 色環", color_button)

        def slider_row(value: int, minimum: int, maximum: int, suffix: str = "%") -> tuple[QtWidgets.QWidget, QtWidgets.QSlider, QtWidgets.QLabel]:
            container = QtWidgets.QWidget()
            row = QtWidgets.QHBoxLayout(container)
            row.setContentsMargins(0, 0, 0, 0)
            slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
            slider.setRange(minimum, maximum)
            slider.setValue(value)
            label = QtWidgets.QLabel()

            def update_label(next_value: int) -> None:
                if suffix == "x":
                    label.setText(f"{next_value / 100.0:.2f}x")
                else:
                    label.setText(f"{next_value}{suffix}")

            slider.valueChanged.connect(update_label)
            update_label(value)
            row.addWidget(slider, stretch=1)
            row.addWidget(label)
            return container, slider, label

        contrast_row, contrast_slider, _contrast_label = slider_row(_coerce_int(state.get("contrast"), 45, 0, 100), 0, 100)
        alpha_row, alpha_slider, _alpha_label = slider_row(_coerce_int(state.get("alpha"), 48, 0, 100), 0, 100)
        gamma_row, gamma_slider, _gamma_label = slider_row(_coerce_int(state.get("gamma"), 100, 25, 300), 25, 300, "x")
        feather_row, feather_slider, _feather_label = slider_row(_coerce_int(state.get("feather"), 14, 0, 100), 0, 100)
        form.addRow("對比 Contrast", contrast_row)
        form.addRow("半透明 Alpha", alpha_row)
        form.addRow("Gamma", gamma_row)
        form.addRow("邊緣 Feather", feather_row)
        breathing = state.get("breathing", {})
        if not isinstance(breathing, dict):
            breathing = {}
        breath_enabled = QtWidgets.QCheckBox("呼吸特效")
        breath_enabled.setChecked(bool(breathing.get("enabled", True)))
        breath_speed_row, breath_speed_slider, _speed_label = slider_row(
            _coerce_int(breathing.get("speed"), 42, 0, 100), 0, 100
        )
        breath_amp_row, breath_amp_slider, _amp_label = slider_row(
            _coerce_int(breathing.get("amplitude"), 16, 0, 100), 0, 100
        )
        form.addRow("Breathing", breath_enabled)
        form.addRow("Breath speed", breath_speed_row)
        form.addRow("Breath amplitude", breath_amp_row)
        layout.addLayout(form)
        target_group = QtWidgets.QGroupBox("Target boundary layers")
        target_layout = QtWidgets.QGridLayout(target_group)
        current_targets = state.get("target_layers", [])
        target_checks: dict[str, QtWidgets.QCheckBox] = {}
        for index, target_key in enumerate(BOUNDARY_HIGHLIGHT_LAYER_KEYS):
            target_label = next((label for key, label in LAYER_LABELS if key == target_key), target_key)
            target_check = QtWidgets.QCheckBox(target_label)
            target_check.setChecked(isinstance(current_targets, list) and target_key in current_targets)
            target_checks[target_key] = target_check
            target_layout.addWidget(target_check, index // 2, index % 2)
        layout.addWidget(target_group)
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )

        def apply_dialog() -> None:
            color = selected_color[0]
            targets = [key for key, checkbox in target_checks.items() if checkbox.isChecked()]
            if not targets:
                targets = [layer_key]
            self.boundary_highlight_state = normalized_boundary_highlight_state(
                {
                    "schema": BOUNDARY_HIGHLIGHT_SCHEMA,
                    "enabled": enabled.isChecked(),
                    "trigger": trigger_combo.currentData(),
                    "target_layers": targets,
                    "color_rgb": [color.red(), color.green(), color.blue()],
                    "contrast": contrast_slider.value(),
                    "alpha": alpha_slider.value(),
                    "gamma": gamma_slider.value(),
                    "feather": feather_slider.value(),
                    "breathing": {
                        "enabled": breath_enabled.isChecked(),
                        "speed": breath_speed_slider.value(),
                        "amplitude": breath_amp_slider.value(),
                    },
                    "renderer_sync": "renderer_line_fill_identity_status_handoff",
                }
            )
            self.refresh_boundary_highlight_status()
            self.refresh_command_preview()
            self.refresh_canvas_preview()
            if self.history_list is not None:
                self.history_list.insertItem(0, f"Boundary highlight UI updated: {layer_key}")
            self.status.setText(f"已更新疆域強調遮罩設定：{layer_label}")
            dialog.accept()

        buttons.accepted.connect(apply_dialog)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.exec()

    def apply_profile(self, profile: dict[str, object]) -> None:
        self.auto_capture_document_snapshot("Before profile apply")
        errors = profile_payload_errors(profile)
        if errors:
            self.status.setText("配置格式錯誤")
            self.command_text.setPlainText("\n".join(errors))
            return
        renderer = profile.get("renderer", {})
        material = profile.get("ocean_material", {})
        layers = profile.get("layers", {})
        layer_filter = profile.get("layer_filter")
        layer_group_view = profile.get("layer_group_view")
        selected_layer = profile.get("selected_layer")
        selected_pin_id = profile.get("selected_pin_id")
        layer_stack = profile.get("layer_stack_ui")
        tool_state = profile.get("tool_state")
        pins = profile.get("pins")
        boundary_highlight = profile.get("boundary_highlight")
        canvas_preview = profile.get("canvas_preview")
        timeline_export = profile.get("timeline_export")
        timeline_keyframes = profile.get("timeline_keyframes")
        if isinstance(renderer, dict):
            self._set_combo(self.style_combo, str(renderer.get("style_profile", self.style_combo.currentText())))
            self._set_combo(self.ui_combo, str(renderer.get("ui_backend", self.ui_combo.currentText())))
            self._set_combo(self.topo_combo, str(renderer.get("topo_source", self.topo_combo.currentText())))
            self._set_combo(self.data_combo, str(renderer.get("data_mode", self.data_combo.currentText())))
            self.width_edit.setText(str(renderer.get("width", self.width_edit.text())))
            self.height_edit.setText(str(renderer.get("height", self.height_edit.text())))
            self.topo_step_edit.setText(str(renderer.get("topo_step", self.topo_step_edit.text())))
            self.arch_edit.setText(str(renderer.get("taichi_arch", self.arch_edit.text())))
            self.rrkal_manifest_ref_edit.setText(
                str(renderer.get("rrkal_data_manifest_ref", self.rrkal_manifest_ref_edit.text()))
            )
        if isinstance(material, dict):
            self.wave_edit.setText(str(material.get("wave_strength", self.wave_edit.text())))
            self.roughness_edit.setText(str(material.get("roughness", self.roughness_edit.text())))
            self.foam_edit.setText(str(material.get("foam", self.foam_edit.text())))
        if isinstance(layers, dict):
            for key, value in layers.items():
                if key in self.checks:
                    self.checks[key].setChecked(bool(value))
        if isinstance(layer_stack, dict):
            for key, value in layer_stack.items():
                if key not in self.layer_locks or not isinstance(value, dict):
                    continue
                self.layer_locks[key].setChecked(bool(value.get("locked", False)))
                self.layer_opacity[key].setValue(int(value.get("opacity", 100)))
                self.layer_blends[key].setCurrentText(str(value.get("blend_mode", "Normal")))
        if isinstance(layer_filter, dict):
            self.apply_layer_filter_state(layer_filter)
        if isinstance(layer_group_view, dict):
            self.apply_layer_group_view_state(layer_group_view)
        if isinstance(selected_layer, str) and selected_layer in self.layer_rows:
            self.select_layer(selected_layer)
        elif isinstance(layer_stack, dict):
            for key, value in layer_stack.items():
                if key in self.layer_rows and isinstance(value, dict) and value.get("selected") is True:
                    self.select_layer(key)
                    break
        if isinstance(tool_state, dict):
            self.apply_tool_state(tool_state)
        if isinstance(pins, list):
            self.apply_research_pins(pins)
        if isinstance(boundary_highlight, dict):
            self.boundary_highlight_state = normalized_boundary_highlight_state(boundary_highlight)
            self.refresh_boundary_highlight_status()
        if isinstance(canvas_preview, dict):
            self.apply_canvas_preview_state(canvas_preview)
        if isinstance(timeline_export, dict):
            self.apply_timeline_export_options(timeline_export)
        if isinstance(timeline_keyframes, list):
            self.apply_timeline_keyframes(timeline_keyframes)
        self.selected_pin_id = selected_pin_id if isinstance(selected_pin_id, str) else None
        if self.selected_pin_id is not None and self.selected_pin_packet() is None:
            self.selected_pin_id = None
        self.refresh_pin_list()
        self.populate_selected_pin_fields()
        self.refresh_command_preview()
        self.refresh_layer_stack_status()

    def apply_canvas_preview_state(self, state: dict[str, object]) -> None:
        mode = str(state.get("mode", "state"))
        if mode == "live_file_stream":
            preview_path = RENDERER_PREVIEW_FRAME_PATH
            raw_path = state.get("renderer_thumbnail_path")
            if isinstance(raw_path, str) and raw_path.strip():
                candidate = Path(raw_path.strip())
                if not candidate.is_absolute():
                    candidate = ROOT / candidate
                preview_path = candidate
            self.canvas_preview_mode = "live_file_stream"
            self.renderer_thumbnail_path = preview_path
            self.renderer_thumbnail_mtime_ns = None
            return
        if mode == "thumbnail":
            thumbnail_path: Path | None = None
            raw_path = state.get("renderer_thumbnail_path")
            if isinstance(raw_path, str) and raw_path.strip():
                candidate = Path(raw_path.strip())
                if not candidate.is_absolute():
                    candidate = ROOT / candidate
                if candidate.exists():
                    thumbnail_path = candidate
            if thumbnail_path is None:
                thumbnail_path = self.latest_renderer_thumbnail_path()
            if thumbnail_path is not None:
                self.canvas_preview_mode = "thumbnail"
                self.renderer_thumbnail_path = thumbnail_path
                return
        self.canvas_preview_mode = "state"
        self.renderer_thumbnail_path = None

    def load_profile_path(self, path: Path) -> None:
        if not path.exists():
            self.status.setText(f"找不到配置：{path}")
            return
        profile = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(profile, dict):
            self.status.setText("配置格式錯誤：root 不是 JSON object")
            return
        self.apply_profile(profile)
        self.status.setText(f"已載入配置：{path}")

    @QtCore.pyqtSlot()
    def refresh_template_list(self) -> None:
        PROFILE_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
        self.template_paths = sorted(PROFILE_TEMPLATE_DIR.glob("*.json"))
        self.template_combo.clear()
        if not self.template_paths:
            self.template_combo.addItem("沒有內建模板")
            return
        for path in self.template_paths:
            label = path.stem.replace("_", " ")
            try:
                profile = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(profile, dict) and profile.get("name"):
                    label = str(profile["name"])
            except Exception:
                pass
            self.template_combo.addItem(label, str(path))

    @QtCore.pyqtSlot()
    def load_selected_template(self) -> None:
        if not self.template_paths:
            self.status.setText("沒有可載入的內建模板")
            return
        index = self.template_combo.currentIndex()
        if index < 0 or index >= len(self.template_paths):
            self.status.setText("模板選取無效")
            return
        path = self.template_paths[index]
        profile = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(profile, dict):
            self.status.setText("模板格式錯誤：root 不是 JSON object")
            return
        self.apply_profile(profile)
        self.status.setText(f"已載入內建模板：{path.name}")

    @QtCore.pyqtSlot()
    def refresh_command_preview(self) -> None:
        self.command_text.setPlainText(subprocess.list2cmdline(self.build_command()))
        self.refresh_canvas_preview()
        self.refresh_research_provenance()

    def refresh_layer_stack_status(self) -> None:
        if not hasattr(self, "layer_stack_note"):
            return
        self.track_layer_undo_snapshot()
        visible = sum(1 for key, _label in LAYER_LABELS if self.checks[key].isChecked())
        locked = sum(1 for key, _label in LAYER_LABELS if self.layer_locks[key].isChecked())
        for key, _label in LAYER_LABELS:
            if key in self.checks and key in self.layer_locks:
                is_locked = self.layer_locks[key].isChecked()
                self.checks[key].setEnabled(not is_locked)
                self.layer_opacity[key].setEnabled(not is_locked)
                self.layer_blends[key].setEnabled(not is_locked)
                row = self.layer_rows.get(key)
                if row is not None:
                    row.setProperty("locked", is_locked)
                    row.style().unpolish(row)
                    row.style().polish(row)
                    row.update()
        non_default = sum(
            1
            for key, _label in LAYER_LABELS
            if self.layer_opacity[key].value() != 100 or self.layer_blends[key].currentText() != "Normal"
        )
        capabilities = self.collect_layer_capability_matrix()
        live_counts = capabilities.get("live_counts", {})
        operator_groups = self.collect_layer_operator_groups()
        if hasattr(self, "layer_operator_groups_label"):
            self.layer_operator_groups_label.setText(
                "Layer workflow: "
                f"{operator_groups.get('summary_text', 'Selection / Edit state / Isolation / History / Diagnostics')} "
                f"({operator_groups.get('complete_group_count', 0)}/{operator_groups.get('group_count', 0)} groups complete)"
            )
        research_workflow = self.collect_layer_research_workflow()
        if hasattr(self, "layer_research_workflow_label"):
            self.layer_research_workflow_label.setText(
                f"Layer research workflow: {research_workflow.get('status', 'unknown')} "
                f"(selected={research_workflow.get('selected_layer') or '-'}, "
                f"warnings={research_workflow.get('runtime_warning_count', 0)}, "
                f"hints={research_workflow.get('remediation_hint_count', 0)})"
            )
        boundary_emphasis = self.collect_boundary_emphasis_control()
        if hasattr(self, "boundary_emphasis_label"):
            self.boundary_emphasis_label.setText(
                f"Boundary emphasis: {boundary_emphasis.get('status', 'unknown')} "
                f"target={boundary_emphasis.get('target_mode')}->{boundary_emphasis.get('target_layer_key') or '-'} "
                f"align={boundary_emphasis.get('target_alignment_label')} "
                f"hook={boundary_emphasis.get('renderer_hook_status')}"
            )
        readiness_ui = self.collect_profile_launch_readiness_ui()
        if hasattr(self, "profile_launch_readiness_label"):
            self.profile_launch_readiness_label.setText(
                f"{readiness_ui.get('label_prefix', 'Profile/launch readiness')}: "
                f"{readiness_ui.get('readiness', 'unknown')} "
                f"({readiness_ui.get('ready_check_count', 0)}/{readiness_ui.get('check_count', 0)} checks)"
            )
        clone_readiness = self.collect_cross_machine_clone_readiness()
        if hasattr(self, "cross_machine_readiness_label"):
            self.cross_machine_readiness_label.setText(
                f"Cross-machine clone readiness: {clone_readiness.get('status', 'unknown')} "
                f"({len(clone_readiness.get('required_commands', []))} commands, setup={clone_readiness.get('setup_doc', '-')}; "
                f"branch={clone_readiness.get('default_branch', '-')}; visibility={clone_readiness.get('repo_visibility', '-')}; "
                f"first smoke={clone_readiness.get('first_run_smoke_command', '-')}; "
                f"first handoff={clone_readiness.get('first_run_handoff_command', '-')})"
            )
        visual_presets = self.collect_layer_visual_presets()
        if hasattr(self, "layer_visual_presets_label"):
            self.layer_visual_presets_label.setText(
                f"Layer presets: {visual_presets.get('selected_preset', 'custom')} "
                f"({visual_presets.get('preset_count', 0)} available, locked layers preserved)"
            )
        preset_feedback = self.collect_layer_visual_preset_runtime_feedback()
        if hasattr(self, "layer_visual_preset_runtime_feedback_label"):
            self.layer_visual_preset_runtime_feedback_label.setText(
                f"Preset renderer ack: {preset_feedback.get('status', 'waiting_for_renderer_ack')} "
                f"(changed={preset_feedback.get('changed_layer_count', 0)}, locked={preset_feedback.get('skipped_locked_count', 0)})"
            )
        hydrology_lod = self.collect_hydrology_lod_readiness()
        if hasattr(self, "hydrology_lod_readiness_label"):
            self.hydrology_lod_readiness_label.setText(
                f"Hydrology/LOD readiness: {hydrology_lod.get('readiness', 'unknown')} "
                f"({hydrology_lod.get('live_hydrology_layer_count', 0)}/{hydrology_lod.get('hydrology_layer_count', 0)} live layers, "
                f"LOD={hydrology_lod.get('lod_hook_status', 'unknown')})"
            )
        hydrology_evidence = self.collect_hydrology_lod_runtime_evidence()
        if hasattr(self, "hydrology_lod_runtime_evidence_label"):
            self.hydrology_lod_runtime_evidence_label.setText(
                f"Hydrology runtime evidence: {hydrology_evidence.get('status', 'waiting_for_runtime_evidence')} "
                f"(hits={hydrology_evidence.get('hydrology_runtime_hit_count', 0)}, pick={hydrology_evidence.get('pick_matches_hydrology', False)})"
            )
        self.layer_stack_note.setText(
            f"可見圖層 {visible}/{len(LAYER_LABELS)}；鎖定 {locked}；"
            f"非預設 opacity/blend {non_default}；"
            f"solo snapshot={'active' if self.layer_visibility_snapshot is not None else 'none'}。"
            f"Live controls: vis={live_counts.get('visibility', 0)}, opacity={live_counts.get('opacity', 0)}, "
            f"blend={live_counts.get('blend', 0)}, pick={live_counts.get('selected_layer_pick', 0)}。"
        )
        self.refresh_layer_undo_label()
        self.write_layer_runtime_state()
        self.refresh_layer_properties()
        self.update_layer_runtime_badges()
        self.refresh_canvas_preview()

    def layer_filter_matches(self, key: str, label: str) -> bool:
        query = self.layer_filter_text.strip().lower()
        if not query:
            return True
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
        haystack = f"{key} {label} {BOOL_FLAGS.get(key, '')} {aliases.get(key, '')}".lower()
        return all(part in haystack for part in query.split())

    def layer_filter_preset_query(self, preset: str) -> str:
        return {
            "all": "",
            "hydrology": "hydro",
            "maritime": "maritime",
            "traffic": "traffic",
            "visual_aids": "aids",
        }.get(preset, self.layer_filter_text)

    def layer_group_definitions(self) -> dict[str, list[str]]:
        return {
            "hydrology": ["lake_layer", "river_layer"],
            "maritime": ["border_layer", "territorial_sea_layer", "eez_layer", "high_seas_layer"],
            "traffic": ["aircraft_layer", "pin_layer", "vehicle_icons"],
            "visual_aids": ["show_grid", "show_stars", "terrain_contours", "scale_bar"],
        }

    def layer_group_for_key(self, key: str) -> str | None:
        for group_id, keys in self.layer_group_definitions().items():
            if key in keys:
                return group_id
        return None

    def layer_group_allows_row(self, key: str) -> bool:
        group_id = self.layer_group_for_key(key)
        return group_id is None or group_id not in self.layer_group_collapsed

    def collect_layer_filter_state(self) -> dict[str, object]:
        matched = [key for key, label in LAYER_LABELS if self.layer_filter_matches(key, label)]
        visible_matches = [key for key in matched if self.layer_group_allows_row(key)]
        selected_layer_visible = self.selected_layer_key in visible_matches if self.selected_layer_key is not None else False
        return {
            "schema": "rrkal_displaytools.layer_filter.v1",
            "mode": "ui_row_filter",
            "preset": self.layer_filter_preset,
            "available_presets": ["all", "hydrology", "maritime", "traffic", "visual_aids", "custom"],
            "query": self.layer_filter_text,
            "first_matched_layer": visible_matches[0] if visible_matches else None,
            "selected_layer_visible": selected_layer_visible,
            "selected_layer_reveal_available": self.selected_layer_key is not None and not selected_layer_visible,
            "matched_layers": matched,
            "matched_count": len(matched),
            "visible_matched_layers": visible_matches,
            "visible_matched_count": len(visible_matches),
            "total_layers": len(LAYER_LABELS),
            "boundary": "Qt Layers row filter/collapse only; renderer layer state is not changed by hiding rows.",
        }

    def collect_layer_group_view_state(self) -> dict[str, object]:
        groups = self.layer_group_definitions()
        labels = dict(LAYER_LABELS)
        visible_rows = [
            key for key, label in LAYER_LABELS
            if self.layer_filter_matches(key, label) and self.layer_group_allows_row(key)
        ]
        selected_group = (
            self.layer_group_for_key(self.selected_layer_key)
            if self.selected_layer_key is not None
            else None
        )
        active_group_collapsed = selected_group in self.layer_group_collapsed if selected_group is not None else False
        return {
            "schema": "rrkal_displaytools.layer_group_view.v1",
            "mode": "ui_row_collapse",
            "available_groups": groups,
            "collapsed_groups": sorted(self.layer_group_collapsed),
            "visible_counts_by_group": {
                group_id: sum(
                    1
                    for key in keys
                    if self.layer_filter_matches(key, labels.get(key, key)) and self.layer_group_allows_row(key)
                )
                for group_id, keys in groups.items()
            },
            "total_counts_by_group": {group_id: len(keys) for group_id, keys in groups.items()},
            "selected_layer_group": selected_group,
            "selected_layer_hidden_by_group": active_group_collapsed,
            "active_group_collapsed": active_group_collapsed,
            "visible_row_count": len(visible_rows),
            "total_layers": len(LAYER_LABELS),
            "boundary": "Qt row grouping only; collapsed groups do not change renderer visibility or runtime state.",
        }

    def apply_layer_filter_state(self, state: dict[str, object]) -> None:
        query = state.get("query", "")
        preset = state.get("preset", "custom")
        self.layer_filter_preset = preset if isinstance(preset, str) else "custom"
        self.layer_filter_text = str(query) if isinstance(query, str) else ""
        if self.layer_filter_edit is not None:
            self.layer_filter_edit.blockSignals(True)
            self.layer_filter_edit.setText(self.layer_filter_text)
            self.layer_filter_edit.blockSignals(False)
        self.refresh_layer_filter()

    def apply_layer_group_view_state(self, state: dict[str, object]) -> None:
        groups = self.layer_group_definitions()
        raw_collapsed = state.get("collapsed_groups", [])
        if isinstance(raw_collapsed, list):
            self.layer_group_collapsed = {str(group) for group in raw_collapsed if str(group) in groups}
        self.refresh_layer_filter()

    @QtCore.pyqtSlot(str)
    def set_layer_filter_text(self, text: str) -> None:
        self.layer_filter_text = text.strip()
        self.layer_filter_preset = "custom" if self.layer_filter_text else "all"
        self.refresh_layer_filter()
        self.refresh_research_provenance()

    def apply_layer_filter_preset(self, preset: str) -> None:
        self.layer_filter_preset = preset if preset in {"all", "hydrology", "maritime", "traffic", "visual_aids"} else "custom"
        self.layer_filter_text = self.layer_filter_preset_query(self.layer_filter_preset)
        if self.layer_filter_edit is not None:
            self.layer_filter_edit.blockSignals(True)
            self.layer_filter_edit.setText(self.layer_filter_text)
            self.layer_filter_edit.blockSignals(False)
        self.refresh_layer_filter()
        self.refresh_research_provenance()

    @QtCore.pyqtSlot()
    def expand_all_layer_groups(self) -> None:
        self.layer_group_collapsed.clear()
        self.refresh_layer_filter()
        self.refresh_research_provenance()

    def toggle_layer_group_collapsed(self, group_id: str) -> None:
        if group_id not in self.layer_group_definitions():
            return
        if group_id in self.layer_group_collapsed:
            self.layer_group_collapsed.remove(group_id)
        else:
            self.layer_group_collapsed.add(group_id)
        self.refresh_layer_filter()
        self.refresh_research_provenance()

    @QtCore.pyqtSlot()
    def select_first_filtered_layer(self) -> None:
        for key, label in LAYER_LABELS:
            if self.layer_filter_matches(key, label) and self.layer_group_allows_row(key):
                self.select_layer(key)
                self.status.setText(f"已選取目前 filter 第一個圖層：{key}")
                return
        self.status.setText("目前 layer filter 沒有符合圖層")

    @QtCore.pyqtSlot()
    def reveal_selected_layer_row(self) -> None:
        if self.selected_layer_key is None or self.selected_layer_key not in self.layer_rows:
            self.status.setText("目前沒有可 reveal 的 active layer")
            return
        labels = dict(LAYER_LABELS)
        selected_label = labels.get(self.selected_layer_key, self.selected_layer_key)
        changed = False
        if not self.layer_filter_matches(self.selected_layer_key, selected_label):
            self.layer_filter_text = ""
            self.layer_filter_preset = "all"
            if self.layer_filter_edit is not None:
                self.layer_filter_edit.blockSignals(True)
                self.layer_filter_edit.setText("")
                self.layer_filter_edit.blockSignals(False)
            changed = True
        selected_group = self.layer_group_for_key(self.selected_layer_key)
        if selected_group is not None and selected_group in self.layer_group_collapsed:
            self.layer_group_collapsed.remove(selected_group)
            changed = True
        self.refresh_layer_filter()
        self.refresh_research_provenance()
        if changed:
            self.status.setText(f"已 reveal active layer row：{self.selected_layer_key}；renderer state unchanged")
        else:
            self.status.setText(f"Active layer row 已可見：{self.selected_layer_key}")

    def refresh_layer_filter(self) -> None:
        matched_count = 0
        for key, label in LAYER_LABELS:
            row = self.layer_rows.get(key)
            if row is None:
                continue
            matched = self.layer_filter_matches(key, label) and self.layer_group_allows_row(key)
            row.setVisible(matched)
            if matched:
                matched_count += 1
        if self.layer_group_status_label is not None:
            collapsed = ", ".join(sorted(self.layer_group_collapsed)) or "none"
            group_state = self.collect_layer_group_view_state()
            selected_group = group_state.get("selected_layer_group") or "none"
            active_group_state = "collapsed" if group_state.get("active_group_collapsed") else "available"
            self.layer_group_status_label.setText(
                f"Layer groups: collapsed={collapsed}; visible_rows={matched_count}/{len(LAYER_LABELS)}; "
                f"selected_group={selected_group} ({active_group_state})"
            )
        if self.layer_filter_status_label is not None:
            query = self.layer_filter_text or "all"
            selected_state = "visible" if self.collect_layer_filter_state().get("selected_layer_visible") else "hidden"
            self.layer_filter_status_label.setText(
                f"Layer filter: preset={self.layer_filter_preset}, query={query}; "
                f"matched={matched_count}/{len(LAYER_LABELS)}; selected={selected_state}; renderer state unchanged"
            )

    def collect_layer_undo_snapshot(self) -> dict[str, object]:
        return {
            "schema": "rrkal_displaytools.layer_stack_undo_snapshot.v1",
            "selected_layer": self.selected_layer_key,
            "layers": {
                key: {
                    "visible": self.checks[key].isChecked(),
                    "locked": self.layer_locks[key].isChecked(),
                    "opacity": self.layer_opacity[key].value(),
                    "blend_mode": self.layer_blends[key].currentText(),
                }
                for key, _label in LAYER_LABELS
                if key in self.checks and key in self.layer_locks
            },
        }

    def layer_undo_signature(self, snapshot: dict[str, object]) -> str:
        return json.dumps(snapshot, sort_keys=True, ensure_ascii=False)

    def track_layer_undo_snapshot(self) -> None:
        snapshot = self.collect_layer_undo_snapshot()
        signature = self.layer_undo_signature(snapshot)
        if (
            not self.layer_undo_restore_active
            and self.layer_undo_tracking_enabled
            and self.layer_last_state_snapshot is not None
            and self.layer_last_state_signature is not None
            and signature != self.layer_last_state_signature
        ):
            self.layer_undo_stack.append(self.layer_last_state_snapshot)
            while len(self.layer_undo_stack) > 24:
                self.layer_undo_stack.pop(0)
            if self.history_list is not None:
                self.history_list.insertItem(0, f"Layer undo snapshot saved: {len(self.layer_undo_stack)}")
        self.layer_last_state_snapshot = snapshot
        self.layer_last_state_signature = signature

    def refresh_layer_undo_label(self) -> None:
        if self.layer_undo_label is None:
            return
        self.layer_undo_label.setText(
            f"Layer undo: {len(self.layer_undo_stack)} snapshots; "
            "covers visibility/lock/opacity/blend/active layer"
        )

    def collect_layer_undo_state(self) -> dict[str, object]:
        return {
            "schema": "rrkal_displaytools.layer_stack_undo.v1",
            "depth": len(self.layer_undo_stack),
            "capacity": 24,
            "tracking_enabled": self.layer_undo_tracking_enabled,
            "covers": ["visibility", "lock", "opacity", "blend_mode", "active_layer"],
            "source": "qt_panel_runtime",
            "global_document_undo": "manual_document_snapshot_undo",
        }

    def collect_session_journal(self) -> dict[str, object]:
        return {
            "schema": "rrkal_displaytools.session_journal.v1",
            "mode": "qt_runtime_recent_events",
            "history_limit": 5,
            "layer_runtime_history": self.layer_runtime_history[:5],
            "pin_pick_history": self.pin_pick_history[:5],
            "layer_undo_depth": len(self.layer_undo_stack),
            "latest_ack_presence": {
                "layer_runtime_ack": self.layer_runtime_ack_payload is not None,
                "pin_input_ack": self.pin_input_ack_payload is not None,
                "pin_pick_ack": self.pin_pick_ack_payload is not None,
                "boundary_highlight_ack": self.boundary_highlight_ack_payload is not None,
            },
            "boundary": "Recent UI/runtime bridge journal only; not a persisted lab notebook or global document history.",
        }

    def collect_document_snapshot(self) -> dict[str, object]:
        return {
            "schema": "rrkal_displaytools.document_snapshot.v1",
            "captured_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "profile": self.collect_profile(),
            "boundary": "Manual UI profile snapshot; not an automatic operation-level history or persisted lab notebook.",
        }

    def document_snapshot_signature(self, snapshot: dict[str, object]) -> str:
        comparable = dict(snapshot)
        comparable.pop("captured_at_utc", None)
        return json.dumps(comparable, ensure_ascii=False, sort_keys=True)

    def collect_document_undo_state(self) -> dict[str, object]:
        return {
            "schema": "rrkal_displaytools.document_snapshot_undo.v1",
            "mode": "manual_snapshot",
            "undo_depth": len(self.document_undo_stack),
            "redo_depth": len(self.document_redo_stack),
            "capacity": self.document_undo_capacity,
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
            "auto_snapshot_count": self.document_auto_snapshot_count,
            "boundary": "Undo/redo restores saved Qt profile state snapshots only; it is not a full operation log.",
        }

    def refresh_document_undo_label(self) -> None:
        if self.document_undo_label is None:
            return
        self.document_undo_label.setText(
            f"Document history: manual snapshot; undo_depth={len(self.document_undo_stack)}, "
            f"redo_depth={len(self.document_redo_stack)}, auto={self.document_auto_snapshot_count}, "
            f"capacity={self.document_undo_capacity}; operation-level history pending"
        )

    def capture_document_snapshot(
        self,
        label: str = "Manual snapshot",
        clear_redo: bool = True,
        source: str = "manual",
    ) -> None:
        if not self.document_undo_tracking_enabled:
            return
        snapshot = self.collect_document_snapshot()
        signature = self.document_snapshot_signature(snapshot)
        if self.document_undo_stack and self.document_snapshot_signature(self.document_undo_stack[-1]) == signature:
            self.status.setText("Document snapshot unchanged; not captured")
            return
        self.document_undo_stack.append(snapshot)
        while len(self.document_undo_stack) > self.document_undo_capacity:
            self.document_undo_stack.pop(0)
        if clear_redo:
            self.document_redo_stack.clear()
        if self.history_list is not None:
            marker = "auto" if source == "auto" else "manual"
            self.history_list.insertItem(0, f"Document snapshot captured ({marker}): {label}")
        if source == "auto":
            self.document_auto_snapshot_count += 1
        self.refresh_document_undo_label()
        self.refresh_research_provenance()
        self.status.setText(f"已保存 document snapshot：{label}")

    def auto_capture_document_snapshot(self, label: str) -> None:
        if not label or not self.document_undo_tracking_enabled or not self.document_undo_stack:
            return
        self.capture_document_snapshot(label, source="auto")

    def apply_document_snapshot(self, snapshot: dict[str, object]) -> None:
        profile = snapshot.get("profile")
        if not isinstance(profile, dict):
            self.status.setText("Document snapshot 格式錯誤")
            return
        self.document_undo_tracking_enabled = False
        try:
            self.apply_profile(profile)
        finally:
            self.document_undo_tracking_enabled = True
        self.refresh_research_provenance()

    @QtCore.pyqtSlot()
    def undo_document_snapshot(self) -> None:
        if len(self.document_undo_stack) < 2:
            self.status.setText("Document snapshot undo stack 不足")
            return
        current = self.document_undo_stack.pop()
        self.document_redo_stack.append(current)
        target = self.document_undo_stack[-1]
        self.apply_document_snapshot(target)
        self.refresh_document_undo_label()
        if self.history_list is not None:
            self.history_list.insertItem(0, "Document snapshot undo")
        self.status.setText("已回復上一個 document snapshot")

    @QtCore.pyqtSlot()
    def redo_document_snapshot(self) -> None:
        if not self.document_redo_stack:
            self.status.setText("Document snapshot redo stack 為空")
            return
        snapshot = self.document_redo_stack.pop()
        self.document_undo_stack.append(snapshot)
        self.apply_document_snapshot(snapshot)
        self.refresh_document_undo_label()
        if self.history_list is not None:
            self.history_list.insertItem(0, "Document snapshot redo")
        self.status.setText("已重做 document snapshot")

    def collect_timeline_state(self) -> dict[str, object]:
        keyframes = [
            {
                "id": str(keyframe.get("id", "")),
                "label": str(keyframe.get("label", "")),
                "style_profile": str(keyframe.get("style_profile", "")),
                "selected_layer": keyframe.get("selected_layer"),
                "has_camera": isinstance(keyframe.get("camera"), dict),
            }
            for keyframe in self.timeline_keyframes[:12]
        ]
        return {
            "schema": "rrkal_displaytools.timeline_state.v1",
            "status": "ui_keyframe_playback" if self.timeline_playback_active else "ui_keyframe_storage",
            "implemented": [
                "visible_qt_timeline_dock",
                "ui_keyframe_storage",
                "ui_keyframe_restore",
                "ui_keyframe_playback_controls",
                "launch_packet_status_contract",
                "renderer_timeline_ack_handoff",
                "renderer_discrete_step_playback",
                "renderer_ocean_material_interpolation",
                "renderer_animation_export",
                "renderer_mp4_video_export",
                "camera_keyframe_storage",
                "renderer_discrete_camera_keyframe_apply",
                "renderer_camera_keyframe_interpolation",
                "renderer_layer_opacity_interpolation",
                "renderer_layer_visibility_blend_discrete_hold",
            ],
            "pending": [
                "blend_crossfade_interpolation",
                "visibility_fade_interpolation",
            ],
            "playhead": 0,
            "keyframe_count": len(self.timeline_keyframes),
            "keyframes": keyframes,
            "playback": {
                "mode": "ui_preview_timer",
                "active": self.timeline_playback_active,
                "interval_ms": self.timeline_playback_interval_ms,
                "next_index": self.timeline_playback_index,
            },
            "boundary": "UIUX keyframe storage/restore/playback plus renderer discrete step playback, ocean material interpolation, layer opacity interpolation, PNG/GIF/MP4 export, and discrete camera keyframes are available. MP4 requires imageio[ffmpeg].",
        }

    def collect_timeline_playback_readiness(self) -> dict[str, object]:
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
            "ready_handoff_files": {
                "timeline_runtime_state_file": str(TIMELINE_STATE_PATH),
                "timeline_ack_file": str(TIMELINE_ACK_PATH),
            },
            "pending": [
                "blend_crossfade_interpolation",
                "visibility_fade_interpolation",
            ],
            "boundary": "Renderer can interpolate camera keyframes, layer opacity, and ocean material, hold active-keyframe layer visibility/blend states, and export PNG frame sequences with optional GIF/MP4 animation. MP4 requires imageio[ffmpeg].",
        }

    def collect_timeline_camera_state(self) -> dict[str, object]:
        yaw_degrees = self.timeline_camera_yaw_spin.value() if self.timeline_camera_yaw_spin is not None else 0.0
        pitch_degrees = self.timeline_camera_pitch_spin.value() if self.timeline_camera_pitch_spin is not None else 0.0
        zoom = self.timeline_camera_zoom_spin.value() if self.timeline_camera_zoom_spin is not None else 1.0
        return {
            "schema": "rrkal_displaytools.timeline_camera_keyframe.v1",
            "source": "qt_timeline_camera_controls",
            "yaw_degrees": float(yaw_degrees),
            "pitch_degrees": float(pitch_degrees),
            "yaw": float(math.radians(yaw_degrees)),
            "pitch": float(math.radians(pitch_degrees)),
            "zoom": float(max(0.08, min(zoom, 4.0))),
        }

    def apply_timeline_camera_state(self, camera: object) -> None:
        if not isinstance(camera, dict):
            return
        try:
            raw_yaw_degrees = camera.get("yaw_degrees")
            raw_pitch_degrees = camera.get("pitch_degrees")
            yaw_degrees = (
                float(raw_yaw_degrees)
                if raw_yaw_degrees is not None
                else math.degrees(float(camera.get("yaw", 0.0)))
            )
            pitch_degrees = (
                float(raw_pitch_degrees)
                if raw_pitch_degrees is not None
                else math.degrees(float(camera.get("pitch", 0.0)))
            )
            zoom = float(camera.get("zoom", 1.0))
        except (TypeError, ValueError):
            return
        if self.timeline_camera_yaw_spin is not None:
            self.timeline_camera_yaw_spin.setValue(max(-360.0, min(360.0, yaw_degrees)))
        if self.timeline_camera_pitch_spin is not None:
            self.timeline_camera_pitch_spin.setValue(max(-89.0, min(89.0, pitch_degrees)))
        if self.timeline_camera_zoom_spin is not None:
            self.timeline_camera_zoom_spin.setValue(max(0.08, min(4.0, zoom)))

    def collect_timeline_camera_keyframe_state(self) -> dict[str, object]:
        active_step = self.collect_timeline_active_step_state()
        active_index = active_step.get("active_index")
        active_camera = None
        if isinstance(active_index, int) and 0 <= active_index < len(self.timeline_keyframes):
            camera = self.timeline_keyframes[active_index].get("camera")
            active_camera = camera if isinstance(camera, dict) else None
        return {
            "schema": "rrkal_displaytools.timeline_camera_keyframe.v1",
            "supported": True,
            "instantiated": False,
            "mode": "qt_handoff_contract",
            "active_index": active_index,
            "active_camera": active_camera,
            "current_camera_controls": self.collect_timeline_camera_state(),
            "applies": ["qt_camera_keyframe_capture", "renderer_discrete_camera_apply"],
            "pending": [],
            "boundary": "Camera keyframes are captured and applied discretely; smooth playback is represented by timeline_camera_interpolation.",
        }

    def collect_timeline_camera_interpolation_state(self) -> dict[str, object]:
        active_step = self.collect_timeline_active_step_state()
        active_index = active_step.get("active_index")
        next_index = None
        if isinstance(active_index, int) and len(self.timeline_keyframes) >= 2:
            next_index = (active_index + 1) % len(self.timeline_keyframes)
        return {
            "schema": "rrkal_displaytools.timeline_camera_interpolation.v1",
            "supported": True,
            "instantiated": False,
            "mode": "linear_camera_segment",
            "playback_active": bool(self.timeline_playback_active),
            "from_index": active_index,
            "to_index": next_index,
            "fraction": 0.0,
            "fields": ["yaw", "pitch", "zoom"],
            "interpolated": {},
            "applies": ["camera_keyframe_interpolation"],
            "pending": [],
            "boundary": "Qt exports the camera interpolation contract; renderer owns runtime interpolation.",
        }

    def collect_timeline_layer_opacity_interpolation_state(self) -> dict[str, object]:
        active_step = self.collect_timeline_active_step_state()
        active_index = active_step.get("active_index")
        next_index = None
        if isinstance(active_index, int) and len(self.timeline_keyframes) >= 2:
            next_index = (active_index + 1) % len(self.timeline_keyframes)
        return {
            "schema": "rrkal_displaytools.timeline_layer_opacity_interpolation.v1",
            "supported": True,
            "instantiated": False,
            "mode": "linear_layer_opacity_segment",
            "playback_active": bool(self.timeline_playback_active),
            "from_index": active_index,
            "to_index": next_index,
            "fraction": 0.0,
            "fields": ["layer_stack_snapshot.layers.*.opacity"],
            "interpolated_layer_opacity": {},
            "layer_count": 0,
            "applies": ["layer_opacity_keyframe_interpolation"],
            "pending": ["blend_crossfade_interpolation", "visibility_fade_interpolation"],
            "boundary": "Qt exports the layer opacity interpolation contract; renderer owns runtime interpolation.",
        }

    def collect_timeline_layer_discrete_hold_state(self) -> dict[str, object]:
        active_step = self.collect_timeline_active_step_state()
        active_index = active_step.get("active_index")
        held_visible: dict[str, bool] = {}
        held_blend: dict[str, str] = {}
        if isinstance(active_index, int) and 0 <= active_index < len(self.timeline_keyframes):
            snapshot = self.timeline_keyframes[active_index].get("layer_stack_snapshot")
            snapshot = snapshot if isinstance(snapshot, dict) else {}
            layers = snapshot.get("layers")
            layers = layers if isinstance(layers, dict) else snapshot
            for layer_key, layer_state in layers.items():
                if not isinstance(layer_state, dict):
                    continue
                if isinstance(layer_state.get("visible"), bool):
                    held_visible[str(layer_key)] = bool(layer_state["visible"])
                raw_blend = layer_state.get("blend_mode")
                if isinstance(raw_blend, str) and raw_blend:
                    held_blend[str(layer_key)] = raw_blend
        return {
            "schema": "rrkal_displaytools.timeline_layer_discrete_hold.v1",
            "supported": True,
            "instantiated": False,
            "mode": "active_keyframe_layer_discrete_hold",
            "playback_active": bool(self.timeline_playback_active),
            "active_index": active_index,
            "active_keyframe_id": active_step.get("active_keyframe_id"),
            "fields": ["layer_stack_snapshot.layers.*.visible", "layer_stack_snapshot.layers.*.blend_mode"],
            "held_layer_visible": held_visible,
            "held_layer_blend_mode": held_blend,
            "layer_count": len(set(held_visible) | set(held_blend)),
            "applies": ["layer_visibility_discrete_hold", "layer_blend_mode_discrete_hold"],
            "pending": ["blend_crossfade_interpolation", "visibility_fade_interpolation"],
            "boundary": "Qt exports the active-keyframe layer visibility/blend hold contract; renderer owns runtime apply.",
        }

    def collect_timeline_playback_plan(self) -> dict[str, object]:
        keyframes = []
        for index, keyframe in enumerate(self.timeline_keyframes[:24]):
            if not isinstance(keyframe, dict):
                continue
            pins = keyframe.get("pins")
            material = keyframe.get("ocean_material")
            layer_stack = keyframe.get("layer_stack_snapshot")
            boundary_highlight = keyframe.get("boundary_highlight")
            boundary_emphasis = keyframe.get("boundary_emphasis_control")
            camera = keyframe.get("camera")
            keyframes.append(
                {
                    "index": index,
                    "id": str(keyframe.get("id", "")),
                    "label": str(keyframe.get("label", "")),
                    "style_profile": str(keyframe.get("style_profile", "")),
                    "selected_layer": keyframe.get("selected_layer"),
                    "has_ocean_material": isinstance(material, dict),
                    "has_layer_stack_snapshot": isinstance(layer_stack, dict),
                    "pin_count": len(pins) if isinstance(pins, list) else 0,
                    "has_boundary_highlight": isinstance(boundary_highlight, dict),
                    "has_boundary_emphasis_control": isinstance(boundary_emphasis, dict),
                    "has_camera": isinstance(camera, dict),
                }
            )
        return {
            "schema": "rrkal_displaytools.timeline_playback_plan.v1",
            "mode": "ordered_keyframe_plan",
            "playback_driver": "qt_preview_timer",
            "renderer_contract": "discrete_step_playback",
            "keyframe_count": len(keyframes),
            "segment_count": max(0, len(keyframes) - 1),
            "keyframes": keyframes,
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
            "boundary": "Playback plan drives renderer discrete keyframe steps, camera interpolation, ocean/material interpolation, layer opacity interpolation, and active-keyframe layer visibility/blend hold.",
        }

    def collect_timeline_segment_state(self) -> dict[str, object]:
        segment_index = 0
        if len(self.timeline_keyframes) >= 2:
            segment_index = max(0, min(int(self.timeline_playback_index), len(self.timeline_keyframes) - 2))
        first = self.timeline_keyframes[segment_index] if len(self.timeline_keyframes) >= 2 else None
        second = self.timeline_keyframes[segment_index + 1] if len(self.timeline_keyframes) >= 2 else None
        active_segment = None
        if isinstance(first, dict) and isinstance(second, dict):
            active_segment = {
                "from_index": segment_index,
                "to_index": segment_index + 1,
                "from_keyframe_id": str(first.get("id", "")),
                "to_keyframe_id": str(second.get("id", "")),
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
            "segment_count": max(0, len(self.timeline_keyframes) - 1),
            "pending": ["blend_crossfade_interpolation", "visibility_fade_interpolation"],
            "boundary": "Segment state describes the next playback segment; camera, ocean material, and layer opacity are interpolatable fields, while layer visibility/blend are held discretely from the active keyframe.",
        }

    def collect_timeline_active_step_state(self) -> dict[str, object]:
        keyframe_count = len(self.timeline_keyframes)
        requested_index = int(self.timeline_playback_index)
        active_index = None
        active_keyframe_id = None
        if keyframe_count > 0:
            active_index = max(0, min(requested_index, keyframe_count - 1))
            active_keyframe = self.timeline_keyframes[active_index]
            active_keyframe_id = str(active_keyframe.get("id", f"keyframe_{active_index + 1}"))
        return {
            "schema": "rrkal_displaytools.timeline_active_step_state.v1",
            "mode": "qt_preview_active_step",
            "source": "timeline_state.playback.next_index",
            "playback_active": bool(self.timeline_playback_active),
            "requested_index": requested_index,
            "active_index": active_index,
            "active_keyframe_id": active_keyframe_id,
            "keyframe_count": keyframe_count,
            "step_available": active_index is not None,
            "applies": ["qt_preview_step_selection", "renderer_startup_selection_hint"],
            "pending": ["blend_crossfade_interpolation", "visibility_fade_interpolation"],
            "boundary": "Active step is a discrete keyframe selection contract for renderer step playback.",
        }

    def collect_timeline_step_playback_state(self) -> dict[str, object]:
        active_step = self.collect_timeline_active_step_state()
        return {
            "schema": "rrkal_displaytools.timeline_step_playback.v1",
            "supported": True,
            "instantiated": False,
            "mode": "qt_handoff_contract",
            "playback_active": bool(self.timeline_playback_active),
            "interval_ms": int(self.timeline_playback_interval_ms),
            "current_index": active_step.get("active_index"),
            "keyframe_count": len(self.timeline_keyframes),
            "step_count": 0,
            "applies": ["renderer_discrete_keyframe_step"],
            "pending": ["blend_crossfade_interpolation", "visibility_fade_interpolation"],
            "boundary": "Qt exports the step playback contract; renderer owns runtime stepping.",
        }

    def collect_timeline_ocean_material_interpolation_state(self) -> dict[str, object]:
        active_step = self.collect_timeline_active_step_state()
        return {
            "schema": "rrkal_displaytools.timeline_ocean_material_interpolation.v1",
            "supported": True,
            "instantiated": False,
            "mode": "qt_handoff_contract",
            "playback_active": bool(self.timeline_playback_active),
            "active_index": active_step.get("active_index"),
            "fields": ["wave_strength", "roughness", "foam"],
            "fraction": 0.0,
            "applies": ["ocean_material_keyframe_interpolation"],
            "pending": ["blend_crossfade_interpolation", "visibility_fade_interpolation"],
            "boundary": "Qt exports the interpolation contract; renderer owns runtime interpolation.",
        }

    def collect_timeline_export_options(self) -> dict[str, object]:
        export_dir_text = self.timeline_export_dir_edit.text().strip() if self.timeline_export_dir_edit is not None else ""
        export_dir = Path(export_dir_text) if export_dir_text else TIMELINE_EXPORT_DIR
        frames = self.timeline_export_frames_spin.value() if self.timeline_export_frames_spin is not None else 24
        fps = self.timeline_export_fps_spin.value() if self.timeline_export_fps_spin is not None else 24.0
        gif_enabled = self.timeline_export_gif_check.isChecked() if self.timeline_export_gif_check is not None else True
        mp4_enabled = self.timeline_export_mp4_check.isChecked() if self.timeline_export_mp4_check is not None else False
        return {
            "schema": "rrkal_displaytools.timeline_export_options.v1",
            "enabled": bool(self.timeline_export_enabled_check.isChecked()) if self.timeline_export_enabled_check is not None else False,
            "export_dir": str(export_dir),
            "frame_count": int(frames),
            "fps": float(fps),
            "manifest_file": str(export_dir / TIMELINE_EXPORT_MANIFEST_PATH.name),
            "gif_enabled": bool(gif_enabled),
            "gif_file": str(export_dir / TIMELINE_EXPORT_GIF_PATH.name),
            "mp4_enabled": bool(mp4_enabled),
            "mp4_file": str(export_dir / TIMELINE_EXPORT_MP4_PATH.name),
            "applies": ["qt_timeline_export_controls", "renderer_timeline_export_cli"],
            "boundary": "Qt only prepares renderer Timeline export flags and suggested state paths; renderer writes PNG/GIF/MP4 artifacts, and RRKAL remains responsible for data governance.",
        }

    def apply_timeline_export_options(self, state: dict[str, object]) -> None:
        if self.timeline_export_enabled_check is not None:
            self.timeline_export_enabled_check.setChecked(bool(state.get("enabled", False)))
        if self.timeline_export_dir_edit is not None:
            export_dir = state.get("export_dir")
            if isinstance(export_dir, str) and export_dir.strip():
                self.timeline_export_dir_edit.setText(export_dir)
        if self.timeline_export_frames_spin is not None:
            try:
                self.timeline_export_frames_spin.setValue(max(1, int(state.get("frame_count", 24))))
            except (TypeError, ValueError):
                pass
        if self.timeline_export_fps_spin is not None:
            try:
                self.timeline_export_fps_spin.setValue(max(1.0, float(state.get("fps", 24.0))))
            except (TypeError, ValueError):
                pass
        if self.timeline_export_gif_check is not None:
            self.timeline_export_gif_check.setChecked(bool(state.get("gif_enabled", True)))
        if self.timeline_export_mp4_check is not None:
            self.timeline_export_mp4_check.setChecked(bool(state.get("mp4_enabled", False)))
        self.refresh_timeline_state_label()

    def collect_timeline_animation_export_state(self) -> dict[str, object]:
        return {
            "schema": "rrkal_displaytools.timeline_animation_export.v1",
            "supported": True,
            "executed": False,
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
            "boundary": "Qt exposes renderer animation export capability; renderer writes frames, manifest, optional GIF, and optional MP4 with interpolated camera and layer opacity keyframes. MP4 requires imageio[ffmpeg].",
        }

    def collect_timeline_runtime_state(self) -> dict[str, object]:
        return {
            "schema": "rrkal_displaytools.timeline_runtime_state.v1",
            "updated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "timeline_state": self.collect_timeline_state(),
            "playback_readiness": self.collect_timeline_playback_readiness(),
            "playback_plan": self.collect_timeline_playback_plan(),
            "segment_state": self.collect_timeline_segment_state(),
            "active_step_state": self.collect_timeline_active_step_state(),
            "step_playback": self.collect_timeline_step_playback_state(),
            "ocean_material_interpolation": self.collect_timeline_ocean_material_interpolation_state(),
            "animation_export": self.collect_timeline_animation_export_state(),
            "export_options": self.collect_timeline_export_options(),
            "camera_keyframe": self.collect_timeline_camera_keyframe_state(),
            "camera_interpolation": self.collect_timeline_camera_interpolation_state(),
            "layer_opacity_interpolation": self.collect_timeline_layer_opacity_interpolation_state(),
            "layer_discrete_hold": self.collect_timeline_layer_discrete_hold_state(),
            "timeline_keyframes": [dict(keyframe) for keyframe in self.timeline_keyframes],
            "source": "rrkal_displaytools_qt_panel",
            "boundary": "Renderer receives Timeline keyframes for discrete step playback, camera apply, material interpolation, layer opacity interpolation, and optional PNG/GIF/MP4 export.",
        }

    def write_timeline_runtime_state(self) -> None:
        payload = self.collect_timeline_runtime_state()
        try:
            TIMELINE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
            TIMELINE_STATE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError as exc:
            self.timeline_state_write_error = str(exc)
            return
        self.timeline_state_last_write_utc = str(payload.get("updated_at_utc", ""))
        self.timeline_state_write_error = None

    def refresh_timeline_ack_state(self) -> None:
        try:
            stat = TIMELINE_ACK_PATH.stat()
        except FileNotFoundError:
            if self.timeline_ack_mtime_ns is not None:
                self.timeline_ack_mtime_ns = None
                if self.timeline_ack_label is not None:
                    self.timeline_ack_label.setText(f"Timeline renderer ack: waiting for {TIMELINE_ACK_PATH.name}")
            return
        except OSError as exc:
            if self.timeline_ack_label is not None:
                self.timeline_ack_label.setText(f"Timeline renderer ack read failed: {exc}")
            return
        if stat.st_mtime_ns == self.timeline_ack_mtime_ns:
            return
        next_mtime_ns = stat.st_mtime_ns
        try:
            payload = json.loads(TIMELINE_ACK_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            if self.timeline_ack_label is not None:
                self.timeline_ack_label.setText(f"Timeline renderer ack parse failed: {exc}")
            return
        self.timeline_ack_mtime_ns = next_mtime_ns
        if isinstance(payload, dict):
            self.timeline_ack_payload = payload
            self.refresh_timeline_ack_label(payload)
            self.refresh_research_provenance()

    def refresh_timeline_ack_label(self, payload: dict[str, object]) -> None:
        if self.timeline_ack_label is None:
            return
        received = payload.get("received", "-")
        keyframe_count = payload.get("keyframe_count", "-")
        updated_at = str(payload.get("updated_at_utc", "-"))
        error = payload.get("error")
        if error:
            self.timeline_ack_label.setText(f"Timeline renderer ack: error={error}, updated={updated_at}")
            return
        self.timeline_ack_label.setText(
            f"Timeline renderer ack: received={received}, keyframes={keyframe_count}, updated={updated_at}"
        )

    def collect_timeline_keyframe(self) -> dict[str, object]:
        index = len(self.timeline_keyframes) + 1
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return {
            "schema": "rrkal_displaytools.timeline_keyframe.v1",
            "id": f"kf_{index:03d}",
            "label": f"Keyframe {index}",
            "created_at_utc": timestamp,
            "style_profile": self.style_combo.currentText(),
            "renderer": {
                "style_profile": self.style_combo.currentText(),
                "ui_backend": self.ui_combo.currentText(),
                "topo_source": self.topo_combo.currentText(),
                "data_mode": self.data_combo.currentText(),
                "width": self.width_edit.text().strip(),
                "height": self.height_edit.text().strip(),
                "topo_step": self.topo_step_edit.text().strip(),
                "taichi_arch": self.arch_edit.text().strip(),
            },
            "ocean_material": {
                "wave_strength": self.wave_edit.text().strip(),
                "roughness": self.roughness_edit.text().strip(),
                "foam": self.foam_edit.text().strip(),
            },
            "camera": self.collect_timeline_camera_state(),
            "selected_layer": self.selected_layer_key,
            "layer_stack_snapshot": self.collect_layer_undo_snapshot(),
            "pins": self.collect_research_pins(),
            "boundary_highlight": self.collect_boundary_highlight_state(),
            "boundary_emphasis_control": self.collect_boundary_emphasis_control(),
        }

    def refresh_timeline_state_label(self) -> None:
        if self.timeline_state_label is None:
            return
        playback = "playing" if self.timeline_playback_active else "idle"
        camera = self.collect_timeline_camera_state()
        export_options = self.collect_timeline_export_options()
        export_state = "enabled" if export_options.get("enabled") is True else "disabled"
        self.timeline_state_label.setText(
            f"Timeline status: {len(self.timeline_keyframes)} UI keyframes stored; "
            f"UI playback={playback}; camera yaw={camera['yaw_degrees']:.1f}, pitch={camera['pitch_degrees']:.1f}, zoom={camera['zoom']:.2f}; "
            f"export={export_state}, frames={export_options['frame_count']}, fps={export_options['fps']:.1f}; "
            f"renderer ack via {TIMELINE_ACK_PATH.name}."
        )
        self.write_timeline_runtime_state()

    def timeline_keyframe_list_text(self, keyframe: dict[str, object]) -> str:
        camera = keyframe.get("camera")
        camera_label = f" · camera={float(camera.get('zoom', 1.0)):.2f}z" if isinstance(camera, dict) else ""
        boundary_emphasis = keyframe.get("boundary_emphasis_control")
        boundary_label = " · boundary=-"
        if isinstance(boundary_emphasis, dict):
            target_mode = boundary_emphasis.get("target_mode", "auto_selected_boundary_layer")
            target_layer = boundary_emphasis.get("target_layer_key") or "-"
            target_alignment = boundary_emphasis.get("target_alignment", "unknown")
            boundary_label = f" · boundary={target_mode}->{target_layer}; {target_alignment}"
        return (
            f"{keyframe.get('id', '-')} · {keyframe.get('style_profile', '-')} · "
            f"layer={keyframe.get('selected_layer') or '-'}{camera_label}{boundary_label}"
        )

    def apply_timeline_keyframes(self, keyframes: list[object]) -> None:
        self.timeline_keyframes = [dict(keyframe) for keyframe in keyframes if isinstance(keyframe, dict)]
        if self.timeline_keyframe_list is not None:
            self.timeline_keyframe_list.clear()
            for keyframe in self.timeline_keyframes:
                self.timeline_keyframe_list.addItem(self.timeline_keyframe_list_text(keyframe))
        self.refresh_timeline_state_label()

    @QtCore.pyqtSlot()
    def add_timeline_keyframe(self) -> None:
        keyframe = self.collect_timeline_keyframe()
        self.timeline_keyframes.append(keyframe)
        if self.timeline_keyframe_list is not None:
            self.timeline_keyframe_list.addItem(self.timeline_keyframe_list_text(keyframe))
        self.refresh_timeline_state_label()
        self.refresh_research_provenance()
        if self.history_list is not None:
            self.history_list.insertItem(0, f"Timeline keyframe stored: {keyframe['id']}")
        self.status.setText(f"已保存 Timeline keyframe：{keyframe['id']}")

    @QtCore.pyqtSlot()
    def apply_selected_timeline_keyframe(self) -> None:
        if self.timeline_keyframe_list is None:
            return
        row = self.timeline_keyframe_list.currentRow()
        if row < 0 or row >= len(self.timeline_keyframes):
            self.status.setText("尚未選取 Timeline keyframe")
            return
        keyframe = self.timeline_keyframes[row]
        self.auto_capture_document_snapshot(f"Before Timeline keyframe {keyframe.get('id', '-')}")
        renderer = keyframe.get("renderer")
        if isinstance(renderer, dict):
            self._set_combo(self.style_combo, str(renderer.get("style_profile", self.style_combo.currentText())))
            self._set_combo(self.ui_combo, str(renderer.get("ui_backend", self.ui_combo.currentText())))
            self._set_combo(self.topo_combo, str(renderer.get("topo_source", self.topo_combo.currentText())))
            self._set_combo(self.data_combo, str(renderer.get("data_mode", self.data_combo.currentText())))
            self.width_edit.setText(str(renderer.get("width", self.width_edit.text())))
            self.height_edit.setText(str(renderer.get("height", self.height_edit.text())))
            self.topo_step_edit.setText(str(renderer.get("topo_step", self.topo_step_edit.text())))
            self.arch_edit.setText(str(renderer.get("taichi_arch", self.arch_edit.text())))
        material = keyframe.get("ocean_material")
        if isinstance(material, dict):
            self.wave_edit.setText(str(material.get("wave_strength", self.wave_edit.text())))
            self.roughness_edit.setText(str(material.get("roughness", self.roughness_edit.text())))
            self.foam_edit.setText(str(material.get("foam", self.foam_edit.text())))
        self.apply_timeline_camera_state(keyframe.get("camera"))
        snapshot = keyframe.get("layer_stack_snapshot")
        if isinstance(snapshot, dict):
            layers = snapshot.get("layers")
            if isinstance(layers, dict):
                for key, value in layers.items():
                    if key not in self.checks or not isinstance(value, dict):
                        continue
                    self.checks[key].setChecked(bool(value.get("visible", self.checks[key].isChecked())))
                    self.layer_locks[key].setChecked(bool(value.get("locked", self.layer_locks[key].isChecked())))
                    self.layer_opacity[key].setValue(int(value.get("opacity", self.layer_opacity[key].value())))
                    self.layer_blends[key].setCurrentText(str(value.get("blend_mode", self.layer_blends[key].currentText())))
            selected_layer = snapshot.get("selected_layer")
            if isinstance(selected_layer, str) and selected_layer in self.layer_rows:
                self.select_layer(selected_layer)
        pins = keyframe.get("pins")
        if isinstance(pins, list):
            self.apply_research_pins(pins)
        boundary_highlight = keyframe.get("boundary_highlight")
        if isinstance(boundary_highlight, dict):
            self.boundary_highlight_state = normalized_boundary_highlight_state(boundary_highlight)
            self.refresh_boundary_highlight_status()
        boundary_emphasis = keyframe.get("boundary_emphasis_control")
        if isinstance(boundary_emphasis, dict):
            self.boundary_emphasis_state = {
                "target_mode": boundary_emphasis.get("target_mode", "auto_selected_boundary_layer"),
                "color_rgb": boundary_emphasis.get("color_rgb", [80, 180, 255]),
                "contrast": boundary_emphasis.get("contrast", 1.35),
                "opacity": boundary_emphasis.get("opacity", 0.42),
                "gamma": boundary_emphasis.get("gamma", 1.0),
                "breathing_enabled": boundary_emphasis.get("breathing_enabled", True),
                "breathing_period_s": boundary_emphasis.get("breathing_period_s", 4.0),
            }
        self.refresh_command_preview()
        self.refresh_layer_stack_status()
        self.refresh_canvas_preview()
        self.refresh_research_provenance()
        if self.history_list is not None:
            self.history_list.insertItem(0, f"Timeline keyframe applied: {keyframe.get('id', '-')}")
        self.status.setText(f"已套用 Timeline keyframe：{keyframe.get('id', '-')}")

    @QtCore.pyqtSlot()
    def step_timeline_keyframe(self) -> None:
        if not self.timeline_keyframes:
            self.status.setText("Timeline 沒有 keyframes")
            return
        if self.timeline_keyframe_list is None:
            return
        row = self.timeline_keyframe_list.currentRow()
        next_row = 0 if row < 0 else (row + 1) % len(self.timeline_keyframes)
        self.timeline_keyframe_list.setCurrentRow(next_row)
        self.apply_selected_timeline_keyframe()
        self.timeline_playback_index = (next_row + 1) % len(self.timeline_keyframes)
        self.refresh_timeline_state_label()

    @QtCore.pyqtSlot()
    def play_timeline_keyframes(self) -> None:
        if not self.timeline_keyframes:
            self.status.setText("Timeline 沒有 keyframes 可播放")
            return
        self.timeline_playback_active = True
        if self.timeline_playback_timer is not None:
            self.timeline_playback_timer.start()
        self.advance_timeline_playback()
        self.refresh_timeline_state_label()
        self.status.setText("Timeline UI preview playback started")

    @QtCore.pyqtSlot()
    def stop_timeline_keyframes(self) -> None:
        self.timeline_playback_active = False
        if self.timeline_playback_timer is not None:
            self.timeline_playback_timer.stop()
        self.refresh_timeline_state_label()
        self.refresh_research_provenance()
        self.status.setText("Timeline UI preview playback stopped")

    @QtCore.pyqtSlot()
    def advance_timeline_playback(self) -> None:
        if not self.timeline_keyframes:
            self.stop_timeline_keyframes()
            return
        if self.timeline_keyframe_list is None:
            return
        row = self.timeline_playback_index % len(self.timeline_keyframes)
        self.timeline_keyframe_list.setCurrentRow(row)
        self.apply_selected_timeline_keyframe()
        self.timeline_playback_index = (row + 1) % len(self.timeline_keyframes)
        self.refresh_timeline_state_label()

    @QtCore.pyqtSlot()
    def clear_timeline_keyframes(self) -> None:
        self.auto_capture_document_snapshot("Before clearing Timeline keyframes")
        self.stop_timeline_keyframes()
        self.timeline_keyframes.clear()
        if self.timeline_keyframe_list is not None:
            self.timeline_keyframe_list.clear()
        self.refresh_timeline_state_label()
        self.refresh_research_provenance()
        self.status.setText("已清除 Timeline UI keyframes")

    @QtCore.pyqtSlot()
    def undo_layer_stack_state(self) -> None:
        if not self.layer_undo_stack:
            self.set_layer_operation_status("沒有可回復的 layer undo snapshot")
            return
        snapshot = self.layer_undo_stack.pop()
        layers = snapshot.get("layers")
        if not isinstance(layers, dict):
            self.set_layer_operation_status("Layer undo snapshot 格式不正確")
            return
        self.layer_undo_restore_active = True
        try:
            for key, value in layers.items():
                if key not in self.checks or key not in self.layer_locks or not isinstance(value, dict):
                    continue
                self.checks[key].blockSignals(True)
                self.layer_locks[key].blockSignals(True)
                self.layer_opacity[key].blockSignals(True)
                self.layer_blends[key].blockSignals(True)
                self.checks[key].setChecked(bool(value.get("visible", False)))
                self.layer_locks[key].setChecked(bool(value.get("locked", False)))
                self.layer_opacity[key].setValue(_coerce_int(value.get("opacity"), 100, 0, 100))
                blend_mode = str(value.get("blend_mode", "Normal"))
                self.layer_blends[key].setCurrentText(blend_mode if blend_mode in BLEND_MODES else "Normal")
                self.checks[key].blockSignals(False)
                self.layer_locks[key].blockSignals(False)
                self.layer_opacity[key].blockSignals(False)
                self.layer_blends[key].blockSignals(False)
            selected_layer = snapshot.get("selected_layer")
            if isinstance(selected_layer, str) and selected_layer in self.layer_rows:
                self.select_layer(selected_layer)
        finally:
            self.layer_undo_restore_active = False
        self.layer_last_state_snapshot = self.collect_layer_undo_snapshot()
        self.layer_last_state_signature = self.layer_undo_signature(self.layer_last_state_snapshot)
        self.refresh_command_preview()
        self.refresh_layer_stack_status()
        self.set_layer_operation_status("已回復上一個 layer undo snapshot")

    def select_layer(self, key: str) -> None:
        if key not in self.layer_rows:
            return
        self.selected_layer_key = key
        label = next((label for layer_key, label in LAYER_LABELS if layer_key == key), key)
        self.selected_layer_label.setText(f"目前選取圖層：{label} / {key}")
        for layer_key, row in self.layer_rows.items():
            row.setProperty("selected", layer_key == key)
            row.style().unpolish(row)
            row.style().polish(row)
            row.update()
        self.refresh_layer_filter()
        self.refresh_layer_stack_status()
        if hasattr(self, "status"):
            self.status.setText(f"已選取圖層：{label}")
        self.refresh_tool_target()

    def solo_selected_layer_visibility(self) -> None:
        key = self.selected_layer_key
        if key not in self.checks:
            self.set_layer_operation_status("尚未選取可 Solo 的圖層")
            return
        if self.layer_locks.get(key) is not None and self.layer_locks[key].isChecked():
            self.set_layer_operation_status("選取圖層已鎖定，Solo 未變更 visibility")
            return
        self.layer_visibility_snapshot = {
            layer_key: self.checks[layer_key].isChecked()
            for layer_key, _label in LAYER_LABELS
            if layer_key in self.checks
        }
        for layer_key, _label in LAYER_LABELS:
            if layer_key not in self.checks:
                continue
            if layer_key != key and self.layer_locks.get(layer_key) is not None and self.layer_locks[layer_key].isChecked():
                continue
            self.checks[layer_key].blockSignals(True)
            self.checks[layer_key].setChecked(layer_key == key)
            self.checks[layer_key].blockSignals(False)
        self.refresh_command_preview()
        self.refresh_layer_stack_status()
        label = next((text for layer_key, text in LAYER_LABELS if layer_key == key), key)
        self.set_layer_operation_status(f"已 Solo 選取圖層：{label}")

    def restore_layer_visibility_snapshot(self) -> None:
        if not self.layer_visibility_snapshot:
            self.set_layer_operation_status("沒有可還原的 Solo 前可見性 snapshot")
            return
        skipped_locked = 0
        for layer_key, enabled in self.layer_visibility_snapshot.items():
            if layer_key not in self.checks:
                continue
            if self.layer_locks.get(layer_key) is not None and self.layer_locks[layer_key].isChecked():
                skipped_locked += 1
                continue
            self.checks[layer_key].blockSignals(True)
            self.checks[layer_key].setChecked(bool(enabled))
            self.checks[layer_key].blockSignals(False)
        self.layer_visibility_snapshot = None
        self.refresh_command_preview()
        self.refresh_layer_stack_status()
        if skipped_locked:
            self.set_layer_operation_status(f"已還原 Solo 前圖層可見性；跳過 locked layers：{skipped_locked}")
        else:
            self.set_layer_operation_status("已還原 Solo 前圖層可見性")

    def canvas_layer_hit_keys(self) -> list[str]:
        visible_keys = [key for key, _label in LAYER_LABELS if key in self.checks and self.checks[key].isChecked()]
        if visible_keys:
            return visible_keys
        return [key for key, _label in LAYER_LABELS if key in self.checks]

    def canvas_layer_hit_key(self, y: float) -> str | None:
        if self.canvas_preview_label is None:
            return None
        keys = self.canvas_layer_hit_keys()
        if not keys:
            return None
        height = max(1.0, float(self.canvas_preview_label.height()))
        y_ratio = min(max(y / height, 0.0), 0.999999)
        return keys[min(len(keys) - 1, int(y_ratio * len(keys)))]

    def refresh_layer_properties(self) -> None:
        if not self.layer_property_labels:
            return
        key = self.selected_layer_key
        if key not in self.checks:
            for label in self.layer_property_labels.values():
                label.setText("-")
            self.layer_property_labels["name"].setText("尚未選取")
            self.refresh_layer_selection_affordance()
            self.refresh_layer_control_feedback_strip()
            return
        label = next((text for layer_key, text in LAYER_LABELS if layer_key == key), key)
        self.layer_property_labels["name"].setText(f"{label} / {key}")
        self.layer_property_labels["visible"].setText("On" if self.checks[key].isChecked() else "Off")
        self.layer_property_labels["locked"].setText("Locked" if self.layer_locks[key].isChecked() else "Unlocked")
        self.layer_property_labels["opacity"].setText(f"{self.layer_opacity[key].value()}%")
        self.layer_property_labels["blend"].setText(self.layer_blends[key].currentText())
        matrix = self.collect_layer_capability_matrix()
        capabilities = matrix.get("selected_layer_capabilities")
        capabilities = capabilities if isinstance(capabilities, dict) else layer_capability_packet(key, label)
        live_text = ", ".join(capabilities.get("live_controls", [])) or "planned"
        runtime_text = ", ".join(capabilities.get("runtime_status", [])) or "no_ack"
        self.layer_property_labels["capabilities"].setText(f"{live_text}; runtime={runtime_text}")
        runtime_summary = matrix.get("runtime_evidence_summary") if isinstance(matrix, dict) else None
        self.layer_property_labels["runtime_summary"].setText(
            str(runtime_summary.get("text", "-")) if isinstance(runtime_summary, dict) else "-"
        )
        runtime_warning_list = matrix.get("runtime_warning_list") if isinstance(matrix, dict) else None
        self.layer_property_labels["runtime_warnings"].setText(
            str(runtime_warning_list.get("summary_text", "-")) if isinstance(runtime_warning_list, dict) else "-"
        )
        renderer_diagnostics_summary = matrix.get("renderer_diagnostics_summary") if isinstance(matrix, dict) else None
        self.layer_property_labels["renderer_diagnostics_summary"].setText(
            str(renderer_diagnostics_summary.get("summary_text", "-")) if isinstance(renderer_diagnostics_summary, dict) else "-"
        )
        renderer_diagnostics_detail = matrix.get("renderer_diagnostics_detail") if isinstance(matrix, dict) else None
        self.layer_property_labels["renderer_diagnostics_detail"].setText(
            str(renderer_diagnostics_detail.get("summary_text", "-")) if isinstance(renderer_diagnostics_detail, dict) else "-"
        )
        renderer_diagnostics_remediation = matrix.get("renderer_diagnostics_remediation") if isinstance(matrix, dict) else None
        self.layer_property_labels["renderer_diagnostics_remediation"].setText(
            str(renderer_diagnostics_remediation.get("summary_text", "-")) if isinstance(renderer_diagnostics_remediation, dict) else "-"
        )
        runtime_context = matrix.get("runtime_interaction_context") if isinstance(matrix, dict) else None
        self.layer_property_labels["runtime_context"].setText(
            str(runtime_context.get("summary_text", "-")) if isinstance(runtime_context, dict) else "-"
        )
        territory_identity = matrix.get("territory_identity_context") if isinstance(matrix, dict) else None
        self.layer_property_labels["territory_identity"].setText(
            str(territory_identity.get("summary_text", "-")) if isinstance(territory_identity, dict) else "-"
        )
        identity_source = matrix.get("authoritative_identity_source") if isinstance(matrix, dict) else None
        if isinstance(identity_source, dict):
            source_text = "configured" if identity_source.get("source_ref_configured") else "not configured"
            self.layer_property_labels["identity_source"].setText(f"RRKAL identity source: {source_text}")
        else:
            self.layer_property_labels["identity_source"].setText("-")
        renderer_target = LAYER_RUNTIME_ID_ALIASES.get(key, "-")
        self.layer_property_labels["renderer_target"].setText(str(renderer_target))
        self.layer_property_labels["diagnostics"].setText(self.layer_diagnostics_text(str(renderer_target)))
        summary_label = getattr(self, "layer_operation_summary_label", None)
        if summary_label is not None:
            summary_label.setText(self.active_layer_operation_summary_text())
        self.refresh_layer_selection_affordance()
        self.refresh_layer_control_feedback_strip()
        self.refresh_boundary_highlight_status()

    def layer_operation_event_text(self) -> str:
        event_label = getattr(self, "layer_operation_event_label", None)
        if event_label is None:
            return "Last layer operation: none yet"
        return event_label.text()

    def set_layer_operation_status(self, message: str) -> None:
        self.status.setText(message)
        event_label = getattr(self, "layer_operation_event_label", None)
        if event_label is not None:
            event_label.setText(f"Last layer operation: {message}")

    def active_layer_operation_summary_text(self) -> str:
        key = self.selected_layer_key
        if not key:
            return "Layer operation summary: no active layer selected; use Select or click a layer row."
        label = next((text for layer_key, text in LAYER_LABELS if layer_key == key), key)
        checks = getattr(self, "checks", {})
        layer_locks = getattr(self, "layer_locks", {})
        layer_opacity = getattr(self, "layer_opacity", {})
        layer_blends = getattr(self, "layer_blends", {})
        visible_widget = checks.get(key)
        lock_widget = layer_locks.get(key)
        opacity_widget = layer_opacity.get(key)
        blend_widget = layer_blends.get(key)
        visible_text = "on" if visible_widget is not None and visible_widget.isChecked() else "off"
        lock_text = "locked" if lock_widget is not None and lock_widget.isChecked() else "unlocked"
        opacity_text = f"{opacity_widget.value()}%" if opacity_widget is not None else "-"
        blend_text = blend_widget.currentText() if blend_widget is not None else "-"
        renderer_target = LAYER_RUNTIME_ID_ALIASES.get(key)
        target_text = renderer_target or "not live"
        diagnostics_text = (
            self.layer_diagnostics_text(str(renderer_target))
            if renderer_target is not None
            else "no renderer target bridge"
        )
        return (
            "Layer operation summary: "
            f"{label} ({key}); visible={visible_text}; lock={lock_text}; "
            f"opacity={opacity_text}; blend={blend_text}; renderer target={target_text}; "
            f"{diagnostics_text}"
        )

    def layer_diagnostics_text(self, renderer_target: str) -> str:
        ack = self.layer_runtime_ack_payload if isinstance(self.layer_runtime_ack_payload, dict) else {}
        ack_event = str(ack.get("event") or "waiting")
        ack_target = str(ack.get("selected_renderer_layer") or "-")
        ack_frame = ack.get("frame_index", "-")
        ack_error = ack.get("error")
        if ack_error:
            ack_text = f"ack error={ack_error}"
        elif ack_target == "-":
            ack_text = f"ack={ack_event}, target waiting"
        elif ack_target == renderer_target:
            ack_text = f"ack={ack_event}, target matched, frame={ack_frame}"
        else:
            ack_text = f"ack={ack_event}, target={ack_target}, frame={ack_frame}"

        pick_payload = self.layer_pick_state_payload if isinstance(self.layer_pick_state_payload, dict) else {}
        pick_result = pick_payload.get("pick_result")
        pick_result = pick_result if isinstance(pick_result, dict) else {}
        pick_event = str(pick_result.get("event") or pick_payload.get("event") or "waiting")
        pick_target = str(pick_payload.get("selected_renderer_layer") or pick_result.get("renderer_layer") or "-")
        screen_position = pick_payload.get("screen_position")
        screen_position = screen_position if isinstance(screen_position, dict) else {}
        screen_x = screen_position.get("screen_x")
        screen_y = screen_position.get("screen_y")
        screen_text = (
            f", pos=({float(screen_x):.1f},{float(screen_y):.1f})"
            if isinstance(screen_x, (int, float)) and isinstance(screen_y, (int, float))
            else ""
        )
        hit_value = pick_result.get("hit")
        if isinstance(hit_value, bool):
            hit_text = "hit" if hit_value else "no-hit"
        else:
            hit_text = "-"
        feature_label = pick_result.get("feature_label") or pick_result.get("label") or pick_result.get("name")
        feature_text = ""
        if isinstance(feature_label, str) and feature_label.strip():
            feature = feature_label.strip()
            if len(feature) > 48:
                feature = f"{feature[:45]}..."
            feature_text = f", feature={feature}"
        if pick_target == "-":
            pick_text = f"pick={pick_event}, target waiting"
        else:
            pick_text = f"pick={pick_event}, target={pick_target}, {hit_text}{feature_text}{screen_text}"
        return f"{ack_text}; {pick_text}"

    def active_layer_diagnostics_packet(self) -> dict[str, object]:
        key = self.selected_layer_key
        label = next((text for layer_key, text in LAYER_LABELS if layer_key == key), key or None)
        renderer_target = LAYER_RUNTIME_ID_ALIASES.get(key, None) if key is not None else None
        diagnostics_text = (
            self.layer_diagnostics_text(str(renderer_target))
            if renderer_target is not None
            else "no active layer selected"
        )
        pick_payload = self.layer_pick_state_payload if isinstance(self.layer_pick_state_payload, dict) else {}
        screen_position = pick_payload.get("screen_position")
        screen_position = screen_position if isinstance(screen_position, dict) else None
        return {
            "schema": "rrkal_displaytools.active_layer_diagnostics.v1",
            "selected_layer": key,
            "label": label,
            "renderer_target": renderer_target,
            "layer_pick_screen_position": screen_position,
            "layer_pick_screen_position_field": "screen_position",
            "layer_pick_screen_position_source": "state/renderer_layer_pick_state.json",
            "capabilities": self.collect_layer_capability_matrix().get("selected_layer_capabilities") if key is not None else None,
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
            "runtime_evidence_summary": self.collect_layer_capability_matrix().get("runtime_evidence_summary"),
            "runtime_badge_summary": self.collect_layer_capability_matrix().get("runtime_badge_summary"),
            "runtime_warning_list": self.collect_layer_capability_matrix().get("runtime_warning_list"),
            "runtime_interaction_context": self.collect_layer_capability_matrix().get("runtime_interaction_context"),
            "territory_identity_context": self.collect_layer_capability_matrix().get("territory_identity_context"),
            "authoritative_identity_source": self.collect_layer_capability_matrix().get("authoritative_identity_source"),
            "renderer_diagnostics_summary": self.collect_layer_capability_matrix().get("renderer_diagnostics_summary"),
            "renderer_diagnostics_detail": self.collect_layer_capability_matrix().get("renderer_diagnostics_detail"),
            "renderer_diagnostics_remediation": self.collect_layer_capability_matrix().get("renderer_diagnostics_remediation"),
            "diagnostics_text": diagnostics_text,
            "runtime_ack_file": str(LAYER_RUNTIME_ACK_PATH),
            "runtime_ack": self.layer_runtime_ack_payload,
            "pick_state_file": str(LAYER_PICK_STATE_PATH),
            "pick_state": self.layer_pick_state_payload,
        }

    def set_active_tool(self, mode: str) -> None:
        if mode not in self.tool_buttons:
            return
        self.active_tool = mode
        for tool_mode, button in self.tool_buttons.items():
            button.setChecked(tool_mode == mode)
        self.refresh_tool_target()
        label = next((text for tool_mode, text, _hint in TOOL_MODES if tool_mode == mode), mode)
        if hasattr(self, "status"):
            self.status.setText(f"已選取工具：{label}")
        self.refresh_canvas_preview()

    def apply_tool_state(self, state: dict[str, object]) -> None:
        active_tool = state.get("active_tool")
        if isinstance(active_tool, str) and active_tool in self.tool_buttons:
            self.set_active_tool(active_tool)
        target_layer = state.get("target_layer")
        if isinstance(target_layer, str) and target_layer in self.layer_rows:
            self.select_layer(target_layer)
        pin = state.get("pin")
        if isinstance(pin, dict):
            if self.pin_type_combo is not None and isinstance(pin.get("type"), str):
                self.pin_type_combo.setCurrentText(str(pin["type"]))
            if self.pin_label_edit is not None and isinstance(pin.get("label"), str):
                self.pin_label_edit.setText(str(pin["label"]))
            if self.pin_note_edit is not None and isinstance(pin.get("note"), str):
                self.pin_note_edit.setText(str(pin["note"]))
            if self.pin_lat_edit is not None and isinstance(pin.get("latitude"), str):
                self.pin_lat_edit.setText(str(pin["latitude"]))
            if self.pin_lon_edit is not None and isinstance(pin.get("longitude"), str):
                self.pin_lon_edit.setText(str(pin["longitude"]))
            if self.pin_priority_spin is not None and isinstance(pin.get("label_priority"), int):
                self.pin_priority_spin.setValue(max(0, min(100, int(pin["label_priority"]))))
        label_mode = state.get("pin_label_mode")
        if isinstance(label_mode, str):
            self.set_pin_label_mode(label_mode)
        label_min_priority = state.get("pin_label_min_priority")
        if self.pin_label_min_priority_spin is not None and isinstance(label_min_priority, int):
            self.pin_label_min_priority_spin.setValue(max(0, min(100, int(label_min_priority))))
        self.refresh_tool_target()

    def refresh_tool_target(self) -> None:
        if self.tool_target_label is None:
            return
        layer_label = next(
            (text for layer_key, text in LAYER_LABELS if layer_key == self.selected_layer_key),
            self.selected_layer_key or "-",
        )
        tool_label = next((text for mode, text, _hint in TOOL_MODES if mode == self.active_tool), self.active_tool)
        cursor_fill_text = self.pin_cursor_fill_source_text()
        self.tool_target_label.setText(
            f"Active tool: {tool_label}\n"
            f"Target layer: {layer_label}\n"
            f"Pin: {self.collect_tool_state()['pin']['type']} / {self.collect_tool_state()['pin']['label']}\n"
            f"Pin coordinate source: {self.pin_coordinate_source_label()}\n"
            f"Labels: {self.current_pin_label_mode()} >= {self.pin_label_min_priority_spin.value() if self.pin_label_min_priority_spin is not None else 50}\n"
            f"Pin cursor fill: {cursor_fill_text}"
        )
        if self.pin_cursor_fill_label is not None:
            self.pin_cursor_fill_label.setText(f"Pin cursor fill: {cursor_fill_text}")
        self.refresh_canvas_preview()

    def add_pin_marker(self) -> None:
        if self.pin_lat_edit is None or self.pin_lon_edit is None:
            return
        try:
            latitude = float(self.pin_lat_edit.text().strip())
            longitude = float(self.pin_lon_edit.text().strip())
        except ValueError:
            self.status.setText("Pin 經緯度必須是數字")
            return
        if not -90 <= latitude <= 90:
            self.status.setText("Pin latitude 必須介於 -90 到 90")
            return
        if not -180 <= longitude <= 180:
            self.status.setText("Pin longitude 必須介於 -180 到 180")
            return
        label = self.pin_label_edit.text().strip() if self.pin_label_edit is not None else ""
        pin = {
            "id": f"pin-{len(self.research_pins) + 1:03d}",
            "type": self.pin_type_combo.currentText() if self.pin_type_combo is not None else "Observation",
            "label": label or f"Pin {len(self.research_pins) + 1}",
            "note": self.pin_note_edit.text().strip() if self.pin_note_edit is not None else "",
            "latitude": latitude,
            "longitude": longitude,
            "label_priority": self.pin_priority_spin.value() if self.pin_priority_spin is not None else 50,
            "target_layer": self.selected_layer_key,
            "placement": self.pin_coordinate_source,
            "coordinate_source": self.pin_coordinate_source,
            "coordinate_source_label": self.pin_coordinate_source_label(),
        }
        self.research_pins.append(pin)
        self.selected_pin_id = str(pin["id"])
        self.refresh_pin_list()
        self.refresh_canvas_preview()
        self.status.setText(f"已加入科研 Pin：{pin['label']}")

    def renderer_cursor_geodesy_lat_lon(self) -> tuple[float, float] | None:
        state = self.cursor_geodesy_state_payload if isinstance(self.cursor_geodesy_state_payload, dict) else {}
        if state.get("hit") is not True:
            return None
        latitude = state.get("latitude")
        longitude = state.get("longitude")
        if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            return None
        return float(latitude), float(longitude)

    def pin_cursor_fill_source_text(self) -> str:
        renderer_lat_lon = self.renderer_cursor_geodesy_lat_lon()
        if renderer_lat_lon is not None:
            latitude, longitude = renderer_lat_lon
            return f"renderer globe raycast ready (lat={latitude:.4f}, lon={longitude:.4f})"
        state = self.cursor_geodesy_state_payload if isinstance(self.cursor_geodesy_state_payload, dict) else {}
        if state.get("hit") is False:
            return "renderer outside globe; fallback uses Qt canvas estimate"
        if self.cursor_latitude is not None and self.cursor_longitude is not None:
            return f"Qt canvas estimate fallback (lat={self.cursor_latitude:.4f}, lon={self.cursor_longitude:.4f})"
        return "waiting for renderer or Qt cursor"

    def pin_coordinate_source_label(self, source: str | None = None) -> str:
        source_key = source or self.pin_coordinate_source
        return {
            "manual_lat_lon": "Manual lat/lon",
            "renderer_globe_raycast": "Renderer globe raycast",
            "qt_canvas_estimate": "Qt canvas estimate",
        }.get(source_key, str(source_key))

    def mark_pin_coordinate_manual(self) -> None:
        self.pin_coordinate_source = "manual_lat_lon"

    def fill_pin_from_cursor(self) -> None:
        renderer_lat_lon = self.renderer_cursor_geodesy_lat_lon()
        if renderer_lat_lon is not None:
            latitude, longitude = renderer_lat_lon
            source = "renderer globe raycast"
            source_key = "renderer_globe_raycast"
        elif self.cursor_latitude is not None and self.cursor_longitude is not None:
            latitude, longitude = self.cursor_latitude, self.cursor_longitude
            source = "Qt canvas estimate"
            source_key = "qt_canvas_estimate"
        else:
            self.status.setText("尚未偵測到 Canvas 游標經緯度")
            return
        if self.pin_lat_edit is not None:
            self.pin_lat_edit.setText(f"{latitude:.6f}")
        if self.pin_lon_edit is not None:
            self.pin_lon_edit.setText(f"{longitude:.6f}")
        self.pin_coordinate_source = source_key
        self.refresh_tool_target()
        self.status.setText(
            f"已用游標位置填入 Pin：lat={latitude:.6f}, lon={longitude:.6f} ({source})"
        )

    def remove_selected_pin_marker(self) -> None:
        if self.pin_list is None:
            return
        row = self.pin_list.currentRow()
        if row < 0 or row >= len(self.research_pins):
            self.status.setText("尚未選取要移除的 Pin")
            return
        removed = self.research_pins.pop(row)
        if self.research_pins:
            next_row = min(row, len(self.research_pins) - 1)
            self.selected_pin_id = str(self.research_pins[next_row].get("id", ""))
        else:
            self.selected_pin_id = None
        self.refresh_pin_list()
        self.refresh_canvas_preview()
        self.status.setText(f"已移除科研 Pin：{removed.get('label', removed.get('id', 'pin'))}")

    def select_pin_marker(self, row: int) -> None:
        if row < 0 or row >= len(self.research_pins):
            self.selected_pin_id = None
            self.refresh_canvas_preview()
            return
        pin = self.research_pins[row]
        self.selected_pin_id = str(pin.get("id", ""))
        self.populate_selected_pin_fields()
        self.refresh_canvas_preview()
        self.status.setText(f"已選取科研 Pin：{pin.get('label', pin.get('id', 'pin'))}")

    def selected_pin_packet(self) -> dict[str, object] | None:
        if self.selected_pin_id is None:
            return None
        for pin in self.research_pins:
            if pin.get("id") == self.selected_pin_id:
                return dict(pin)
        return None

    def pin_id_exists(self, pin_id: str) -> bool:
        return any(str(pin.get("id", "")) == pin_id for pin in self.research_pins)

    def populate_selected_pin_fields(self) -> None:
        pin = self.selected_pin_packet()
        if pin is None:
            return
        if self.pin_type_combo is not None and isinstance(pin.get("type"), str):
            self.pin_type_combo.setCurrentText(str(pin["type"]))
        if self.pin_label_edit is not None and isinstance(pin.get("label"), str):
            self.pin_label_edit.setText(str(pin["label"]))
        if self.pin_note_edit is not None and isinstance(pin.get("note"), str):
            self.pin_note_edit.setText(str(pin["note"]))
        if self.pin_lat_edit is not None and isinstance(pin.get("latitude"), (int, float)):
            self.pin_lat_edit.setText(str(pin["latitude"]))
        if self.pin_lon_edit is not None and isinstance(pin.get("longitude"), (int, float)):
            self.pin_lon_edit.setText(str(pin["longitude"]))
        if self.pin_priority_spin is not None and isinstance(pin.get("label_priority"), int):
            self.pin_priority_spin.setValue(max(0, min(100, int(pin["label_priority"]))))
        source = pin.get("coordinate_source") or pin.get("placement")
        if isinstance(source, str):
            self.pin_coordinate_source = source
            self.refresh_tool_target()

    def refresh_pin_list(self) -> None:
        if self.pin_list is None:
            return
        self.pin_list.blockSignals(True)
        self.pin_list.clear()
        selected_row = -1
        for index, pin in enumerate(self.research_pins):
            selected = pin.get("id") == self.selected_pin_id
            prefix = "* " if selected else "  "
            source_label = self.pin_coordinate_source_label(str(pin.get("coordinate_source") or pin.get("placement") or "manual_lat_lon"))
            self.pin_list.addItem(
                f"{prefix}{pin.get('id')} | P{pin.get('label_priority', 50)} | {pin.get('type')} | {pin.get('label')} "
                f"({pin.get('latitude')}, {pin.get('longitude')}) | source={source_label}"
            )
            if selected:
                selected_row = index
        self.pin_list.setCurrentRow(selected_row)
        self.pin_list.blockSignals(False)

    def apply_research_pins(self, pins: list[object]) -> None:
        self.research_pins = [dict(pin) for pin in pins if isinstance(pin, dict)]
        if self.selected_pin_id is not None and self.selected_pin_packet() is None:
            self.selected_pin_id = None
        self.refresh_pin_list()

    def refresh_renderer_pin_pick_state(self) -> None:
        try:
            stat = PIN_PICK_STATE_PATH.stat()
        except FileNotFoundError:
            if self.pin_pick_state_mtime_ns is not None:
                self.pin_pick_state_mtime_ns = None
                if self.pin_pick_state_label is not None:
                    self.pin_pick_state_label.setText(f"Renderer bridge: waiting for {PIN_PICK_STATE_PATH.name}")
            return
        except OSError as exc:
            if self.pin_pick_state_label is not None:
                self.pin_pick_state_label.setText(f"Renderer bridge read failed: {exc}")
            return
        if stat.st_mtime_ns == self.pin_pick_state_mtime_ns:
            return
        next_mtime_ns = stat.st_mtime_ns
        try:
            payload = json.loads(PIN_PICK_STATE_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            if self.pin_pick_state_label is not None:
                self.pin_pick_state_label.setText(f"Renderer bridge parse failed: {exc}")
            return
        self.pin_pick_state_mtime_ns = next_mtime_ns
        if isinstance(payload, dict):
            self.pin_pick_state_payload = payload
            self.apply_renderer_pin_pick_state(payload)

    def apply_renderer_pin_pick_state(self, payload: dict[str, object]) -> None:
        event = str(payload.get("event", "unknown"))
        selected_pin_id = payload.get("selected_pin_id")
        hover_pin = payload.get("hover_pin")
        hover_pin_id = "-"
        if isinstance(hover_pin, dict) and hover_pin.get("id") is not None:
            hover_pin_id = str(hover_pin.get("id"))
        selected_text = str(selected_pin_id) if isinstance(selected_pin_id, str) and selected_pin_id else "-"
        visible_count = payload.get("pin_visible_count", "-")
        frame_index = payload.get("frame_index", "-")
        updated_at = str(payload.get("updated_at_utc", "-"))
        if self.pin_pick_state_label is not None:
            self.pin_pick_state_label.setText(
                f"Renderer bridge: event={event}, selected={selected_text}, hover={hover_pin_id}, "
                f"visible={visible_count}, frame={frame_index}, updated={updated_at}"
            )
        self.pin_pick_state_last_event = event
        self.append_pin_pick_history(payload)
        if event == "selected":
            if isinstance(selected_pin_id, str) and self.pin_id_exists(selected_pin_id):
                self.selected_pin_id = selected_pin_id
                self.refresh_pin_list()
                self.populate_selected_pin_fields()
                self.refresh_command_preview()
                pin = self.selected_pin_packet()
                label = pin.get("label", selected_pin_id) if pin is not None else selected_pin_id
                self.status.setText(f"Renderer 已同步選取 Pin：{label}")
            else:
                self.status.setText(f"Renderer pick 的 Pin 不在目前 Qt Pin list：{selected_text}")
        elif event == "cleared":
            if self.selected_pin_id is not None:
                self.selected_pin_id = None
                self.refresh_pin_list()
                self.refresh_command_preview()
                self.status.setText("Renderer 已清除 Pin 選取")
        self.write_pin_pick_ack(payload)
        self.refresh_research_provenance()

    def write_pin_pick_ack(self, payload: dict[str, object]) -> None:
        event = str(payload.get("event", "unknown"))
        selected_pin_id = payload.get("selected_pin_id")
        ui_synced = True
        if event == "selected":
            ui_synced = isinstance(selected_pin_id, str) and self.selected_pin_id == selected_pin_id
        elif event == "cleared":
            ui_synced = self.selected_pin_id is None
        ack = {
            "schema": "rrkal_displaytools.qt_pin_pick_ack.v1",
            "updated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "event": event,
            "renderer_updated_at_utc": payload.get("updated_at_utc"),
            "renderer_frame_index": payload.get("frame_index"),
            "renderer_selected_pin_id": selected_pin_id,
            "qt_selected_pin_id": self.selected_pin_id,
            "ui_synced": ui_synced,
            "pin_count": len(self.research_pins),
            "source": "rrkal_displaytools_qt_panel",
        }
        try:
            PIN_PICK_ACK_PATH.parent.mkdir(parents=True, exist_ok=True)
            PIN_PICK_ACK_PATH.write_text(json.dumps(ack, ensure_ascii=False, indent=2), encoding="utf-8")
            self.pin_pick_ack_payload = ack
            self.pin_pick_ack_write_error = None
            if self.pin_pick_ack_label is not None:
                self.pin_pick_ack_label.setText(
                    f"Qt ack: event={event}, ui_synced={ui_synced}, selected={self.selected_pin_id or '-'}, "
                    f"updated={ack['updated_at_utc']}"
                )
        except OSError as exc:
            self.pin_pick_ack_write_error = str(exc)
            if self.pin_pick_ack_label is not None:
                self.pin_pick_ack_label.setText(f"Qt ack write failed: {exc}")

    def append_pin_pick_history(self, payload: dict[str, object]) -> None:
        event = str(payload.get("event", "unknown"))
        selected_pin_id = str(payload.get("selected_pin_id") or "-")
        hover_pin = payload.get("hover_pin")
        event_pin = payload.get("event_pin")
        hover_pin_id = str(hover_pin.get("id")) if isinstance(hover_pin, dict) and hover_pin.get("id") is not None else "-"
        event_pin_id = str(event_pin.get("id")) if isinstance(event_pin, dict) and event_pin.get("id") is not None else "-"
        signature = json.dumps(
            {
                "event": event,
                "selected": selected_pin_id,
                "hover": hover_pin_id,
                "event_pin": event_pin_id,
                "frame": payload.get("frame_index"),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        if signature == self.pin_pick_history_signature:
            return
        self.pin_pick_history_signature = signature
        updated_at = str(payload.get("updated_at_utc", "-"))
        visible_count = payload.get("pin_visible_count", "-")
        entry = (
            f"⌖ Pin pick {updated_at}: event={event}, selected={selected_pin_id}, "
            f"hover={hover_pin_id}, event_pin={event_pin_id}, visible={visible_count}"
        )
        self.pin_pick_history.insert(0, entry)
        del self.pin_pick_history[10:]
        if self.history_list is None:
            return
        self.history_list.insertItem(0, entry)
        while self.history_list.count() > 18:
            self.history_list.takeItem(self.history_list.count() - 1)

    def refresh_canvas_preview(self) -> None:
        if self.canvas_preview_label is None or self.canvas_meta_label is None:
            return
        if self.canvas_preview_mode in {"thumbnail", "live_file_stream"} and self.renderer_thumbnail_path is not None:
            if self.render_thumbnail_into_canvas(self.renderer_thumbnail_path):
                sync_note = (
                    "File-based live renderer frame stream."
                    if self.canvas_preview_mode == "live_file_stream"
                    else "Static output preview with auto-refresh."
                )
                self.canvas_meta_label.setText(
                    f"Renderer preview: {self.display_renderer_preview_path(self.renderer_thumbnail_path)}. {sync_note}"
                )
                self.refresh_research_provenance()
                return
            if self.canvas_preview_mode == "live_file_stream":
                self.canvas_preview_label.setPixmap(QtGui.QPixmap())
                self.canvas_preview_label.setText(
                    "Renderer Live Preview\n\n"
                    f"Waiting for {self.display_renderer_preview_path(self.renderer_thumbnail_path)}\n"
                    "Launch or restart renderer to start the file stream."
                )
                self.canvas_meta_label.setText(
                    f"Renderer live preview waiting for {self.display_renderer_preview_path(self.renderer_thumbnail_path)}."
                )
                self.refresh_research_provenance()
                return
            self.canvas_preview_mode = "state"
            self.renderer_thumbnail_path = None
        selected_label = next(
            (text for key, text in LAYER_LABELS if key == self.selected_layer_key),
            self.selected_layer_key or "-",
        )
        tool_label = next((text for mode, text, _hint in TOOL_MODES if mode == self.active_tool), self.active_tool)
        visible = sum(1 for key, _label in LAYER_LABELS if key in self.checks and self.checks[key].isChecked())
        pin_count = len(self.research_pins)
        zoom = self.canvas_zoom_slider.value() if self.canvas_zoom_slider is not None else 100
        selected_pin = self.selected_pin_packet()
        selected_pin_text = (
            f"{selected_pin.get('label', selected_pin.get('id'))} "
            f"@ lat={selected_pin.get('latitude')}, lon={selected_pin.get('longitude')}"
            if selected_pin is not None
            else "-"
        )
        pin_markers = ", ".join(str(pin.get("label", pin.get("id", "pin"))) for pin in self.research_pins[:3])
        if len(self.research_pins) > 3:
            pin_markers = f"{pin_markers}, +{len(self.research_pins) - 3} more"
        if not pin_markers:
            pin_markers = "-"
        cursor_text = (
            f"lat={self.cursor_latitude:.4f}, lon={self.cursor_longitude:.4f}"
            if self.cursor_latitude is not None and self.cursor_longitude is not None
            else "move mouse over canvas"
        )
        renderer_cursor_text = self.cursor_geodesy_bridge_text()
        style = self.style_combo.currentText() if hasattr(self, "style_combo") else "-"
        topo = self.topo_combo.currentText() if hasattr(self, "topo_combo") else "-"
        data_mode = self.data_combo.currentText() if hasattr(self, "data_combo") else "-"
        hit_keys = self.canvas_layer_hit_keys()
        hit_labels = [next((text for layer_key, text in LAYER_LABELS if layer_key == key), key) for key in hit_keys[:5]]
        hit_map = ", ".join(hit_labels)
        if len(hit_keys) > 5:
            hit_map = f"{hit_map}, +{len(hit_keys) - 5} more"
        if not hit_map:
            hit_map = "-"
        boundary_summary = self.boundary_highlight_summary()
        boundary_identity_summary = self.boundary_identity_status_summary()
        boundary_identity_warning = self.boundary_identity_warning_text()
        boundary_emphasis = self.collect_boundary_emphasis_control()
        boundary_target_text = (
            f"{boundary_emphasis.get('target_mode')}->{boundary_emphasis.get('target_layer_key') or '-'}; "
            f"{boundary_emphasis.get('target_alignment_label')}"
        )
        self.canvas_preview_label.setPixmap(QtGui.QPixmap())
        self.canvas_preview_label.setText(
            "RRKAL Scientific Canvas Preview\n\n"
            f"Style: {style} | Topo: {topo} | Data: {data_mode}\n"
            f"Tool: {tool_label} -> Layer: {selected_label}\n"
            f"Visible layers: {visible}/{len(LAYER_LABELS)} | Pins: {pin_count} | Zoom: {zoom}%\n\n"
            f"Select hit map: {hit_map}\n"
            f"Boundary highlight: {boundary_summary}\n"
            f"Boundary identity: {boundary_identity_summary}\n"
            f"Boundary warning: {boundary_identity_warning}\n"
            f"Boundary target: {boundary_target_text}\n"
            f"Selected pin: {selected_pin_text}\n"
            f"Pin markers: {pin_markers}\n"
            f"Cursor estimate: {cursor_text}\n\n"
            f"{renderer_cursor_text}\n\n"
            "Qt state preview; renderer state sync and pick bridges are live. Use Renderer thumbnail or Live preview for renderer pixels."
        )
        self.canvas_meta_label.setText(
            f"Canvas state mirrors Qt UI only：active tool={self.active_tool}, "
            f"target layer={self.selected_layer_key or '-'}, style={style}, visible_layers={visible}, "
            f"selected_pin={self.selected_pin_id or '-'}, cursor={cursor_text}, "
            f"renderer_cursor_bridge={renderer_cursor_text}, "
            f"boundary_target={boundary_target_text}, "
            f"boundary_warning={boundary_identity_warning}, "
            f"boundary_highlight={'on' if self.boundary_highlight_state.get('enabled') else 'off'}."
        )
        self.refresh_research_provenance()

    def latest_renderer_thumbnail_path(self) -> Path | None:
        try:
            candidates = [path for path in SHOWCASE_DIR.glob("*.png") if path.is_file()]
        except OSError:
            return None
        if not candidates:
            return None
        try:
            return max(candidates, key=lambda path: path.stat().st_mtime_ns)
        except OSError:
            return None

    def render_thumbnail_into_canvas(self, path: Path) -> bool:
        if self.canvas_preview_label is None:
            return False
        pixmap = QtGui.QPixmap(str(path))
        if pixmap.isNull():
            return False
        try:
            self.renderer_thumbnail_mtime_ns = path.stat().st_mtime_ns
        except OSError:
            self.renderer_thumbnail_mtime_ns = None
        target_size = self.canvas_preview_label.size()
        scaled = pixmap.scaled(
            target_size,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation,
        )
        self.canvas_preview_label.setPixmap(scaled)
        self.canvas_preview_label.setText("")
        return True

    @QtCore.pyqtSlot()
    def show_canvas_state_preview(self) -> None:
        self.canvas_preview_mode = "state"
        self.renderer_thumbnail_path = None
        self.renderer_thumbnail_mtime_ns = None
        self.refresh_canvas_preview()
        self.status.setText("已切回 Qt Canvas state preview")

    @QtCore.pyqtSlot()
    def show_latest_renderer_thumbnail(self) -> None:
        path = self.latest_renderer_thumbnail_path()
        if path is None:
            self.status.setText("找不到 renderer PNG；可先跑 scripts\\render_quick_smoke.ps1 或 renderer --output")
            return
        self.canvas_preview_mode = "thumbnail"
        self.renderer_thumbnail_path = path
        self.renderer_thumbnail_mtime_ns = None
        self.refresh_canvas_preview()
        self.status.setText(f"已顯示 renderer thumbnail：{path.relative_to(ROOT)}")

    @QtCore.pyqtSlot()
    def show_live_renderer_preview(self) -> None:
        self.canvas_preview_mode = "live_file_stream"
        self.renderer_thumbnail_path = RENDERER_PREVIEW_FRAME_PATH
        self.renderer_thumbnail_mtime_ns = None
        self.refresh_canvas_preview()
        self.status.setText(f"已切到 renderer live preview stream：{RENDERER_PREVIEW_FRAME_PATH.relative_to(ROOT)}")

    def refresh_renderer_thumbnail_if_needed(self) -> None:
        if self.canvas_preview_mode not in {"thumbnail", "live_file_stream"}:
            return
        path = self.renderer_thumbnail_path
        if self.canvas_preview_mode == "live_file_stream":
            path = RENDERER_PREVIEW_FRAME_PATH
        elif path is None or not path.exists():
            path = self.latest_renderer_thumbnail_path()
        if path is None:
            return
        try:
            mtime_ns = path.stat().st_mtime_ns
        except OSError:
            return
        if path == self.renderer_thumbnail_path and mtime_ns == self.renderer_thumbnail_mtime_ns:
            return
        self.renderer_thumbnail_path = path
        if self.render_thumbnail_into_canvas(path) and self.canvas_meta_label is not None:
            sync_note = (
                "File-based live renderer frame stream."
                if self.canvas_preview_mode == "live_file_stream"
                else "Static output preview with auto-refresh."
            )
            self.canvas_meta_label.setText(
                f"Renderer preview auto-refreshed: {self.display_renderer_preview_path(path)}. {sync_note}"
            )
            self.refresh_research_provenance()

    def build_research_provenance(self) -> str:
        visible_layers = [key for key, _label in LAYER_LABELS if key in self.checks and self.checks[key].isChecked()]
        locked_layers = [key for key, _label in LAYER_LABELS if key in self.layer_locks and self.layer_locks[key].isChecked()]
        packet = {
            "schema": "rrkal_displaytools.research_provenance_summary.v1",
            "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "purpose": "research visualization reproducibility summary",
            "renderer": {
                "style_profile": self.style_combo.currentText(),
                "ui_backend": self.ui_combo.currentText(),
                "topo_source": self.topo_combo.currentText(),
                "data_mode": self.data_combo.currentText(),
                "width": self.width_edit.text().strip(),
                "height": self.height_edit.text().strip(),
                "topo_step": self.topo_step_edit.text().strip(),
                "taichi_arch": self.arch_edit.text().strip(),
                "rrkal_data_manifest_ref": self.rrkal_manifest_ref_edit.text().strip(),
            },
            "active_layer": self.selected_layer_key,
            "active_layer_operation_summary": self.active_layer_operation_summary_text(),
            "last_layer_operation": self.layer_operation_event_text(),
            "layer_operation_feedback": self.collect_layer_operation_feedback(),
            "layer_filter": self.collect_layer_filter_state(),
            "layer_group_view": self.collect_layer_group_view_state(),
            "layer_operator_shortcuts": self.collect_layer_operator_shortcuts(),
            "layer_operator_groups": self.collect_layer_operator_groups(),
            "layer_selection_tool": self.collect_layer_selection_tool(),
            "layer_research_workflow": self.collect_layer_research_workflow(),
            "boundary_emphasis_control": self.collect_boundary_emphasis_control(),
            "cursor_geodesy_readout": self.collect_cursor_geodesy_readout(),
            "cursor_geodesy_state_file": str(CURSOR_GEODESY_STATE_PATH),
            "cursor_geodesy_ack_file": str(CURSOR_GEODESY_ACK_PATH),
            "cursor_geodesy_state": self.cursor_geodesy_state_payload,
            "cursor_geodesy_ack": self.cursor_geodesy_ack_payload,
            "style_renderer_entries": self.collect_style_renderer_entries(),
            "style_profile_renderer_routes": self.collect_style_profile_renderer_routes(),
            "module_boundary_registry": self.collect_module_boundary_registry(),
            "cross_machine_clone_readiness": self.collect_cross_machine_clone_readiness(),
            "profile_launch_readiness": self.collect_profile_launch_readiness(),
            "profile_launch_readiness_ui": self.collect_profile_launch_readiness_ui(),
            "profile_ui_state_replay": self.collect_profile_ui_state_replay(),
            "layer_visual_presets": self.collect_layer_visual_presets(),
            "layer_visual_preset_runtime_feedback": self.collect_layer_visual_preset_runtime_feedback(),
            "hydrology_lod_readiness": self.collect_hydrology_lod_readiness(),
            "hydrology_lod_runtime_evidence": self.collect_hydrology_lod_runtime_evidence(),
            "ocean_material_control_port": self.collect_ocean_material_control_port(),
            "layer_capability_matrix": self.collect_layer_capability_matrix(),
            "layer_runtime_evidence_summary": self.collect_layer_capability_matrix().get("runtime_evidence_summary"),
            "layer_runtime_badge_summary": self.collect_layer_capability_matrix().get("runtime_badge_summary"),
            "layer_runtime_warning_list": self.collect_layer_capability_matrix().get("runtime_warning_list"),
            "layer_runtime_interaction_context": self.collect_layer_capability_matrix().get("runtime_interaction_context"),
            "layer_territory_identity_context": self.collect_layer_capability_matrix().get("territory_identity_context"),
            "layer_authoritative_identity_source": self.collect_layer_capability_matrix().get("authoritative_identity_source"),
            "layer_renderer_diagnostics_summary": self.collect_layer_capability_matrix().get("renderer_diagnostics_summary"),
            "layer_renderer_diagnostics_detail": self.collect_layer_capability_matrix().get("renderer_diagnostics_detail"),
            "layer_renderer_diagnostics_remediation": self.collect_layer_capability_matrix().get("renderer_diagnostics_remediation"),
            "active_layer_diagnostics": self.active_layer_diagnostics_packet(),
            "layer_undo": self.collect_layer_undo_state(),
            "session_journal": self.collect_session_journal(),
            "document_undo": self.collect_document_undo_state(),
            "timeline_state": self.collect_timeline_state(),
            "timeline_playback_readiness": self.collect_timeline_playback_readiness(),
            "timeline_playback_plan": self.collect_timeline_playback_plan(),
            "timeline_segment_state": self.collect_timeline_segment_state(),
            "timeline_active_step_state": self.collect_timeline_active_step_state(),
            "timeline_step_playback": self.collect_timeline_step_playback_state(),
            "timeline_ocean_material_interpolation": self.collect_timeline_ocean_material_interpolation_state(),
            "timeline_animation_export": self.collect_timeline_animation_export_state(),
            "timeline_camera_keyframe": self.collect_timeline_camera_keyframe_state(),
            "timeline_camera_interpolation": self.collect_timeline_camera_interpolation_state(),
            "timeline_layer_opacity_interpolation": self.collect_timeline_layer_opacity_interpolation_state(),
            "timeline_layer_discrete_hold": self.collect_timeline_layer_discrete_hold_state(),
            "timeline_runtime_state_file": str(TIMELINE_STATE_PATH),
            "timeline_state_last_write_utc": self.timeline_state_last_write_utc,
            "timeline_state_write_error": self.timeline_state_write_error,
            "timeline_ack_file": str(TIMELINE_ACK_PATH),
            "timeline_ack": self.timeline_ack_payload,
            "active_tool": self.active_tool,
            "cursor_lat_lon_estimate": {
                "latitude": self.cursor_latitude,
                "longitude": self.cursor_longitude,
                "method": "ui_equirectangular_canvas_estimate",
            },
            "selected_pin_id": self.selected_pin_id,
            "selected_pin": self.selected_pin_packet(),
            "pins": self.collect_research_pins(),
            "pin_input_ack_file": str(PIN_INPUT_ACK_PATH),
            "pin_input_ack": self.pin_input_ack_payload,
            "pin_pick_state_file": str(PIN_PICK_STATE_PATH),
            "pin_pick_state_last_event": self.pin_pick_state_last_event,
            "pin_pick_state": self.pin_pick_state_payload,
            "pin_pick_ack_file": str(PIN_PICK_ACK_PATH),
            "pin_pick_ack": self.pin_pick_ack_payload,
            "pin_pick_ack_write_error": self.pin_pick_ack_write_error,
            "pin_pick_history": self.pin_pick_history[:5],
            "layer_runtime_state_file": str(LAYER_RUNTIME_STATE_PATH),
            "layer_runtime_state_last_write_utc": self.layer_runtime_state_last_write_utc,
            "layer_runtime_state_write_error": self.layer_runtime_state_write_error,
            "layer_runtime_ack_file": str(LAYER_RUNTIME_ACK_PATH),
            "layer_runtime_ack": self.layer_runtime_ack_payload,
            "layer_runtime_history": self.layer_runtime_history[:5],
            "layer_pick_state_file": str(LAYER_PICK_STATE_PATH),
            "layer_pick_state": self.layer_pick_state_payload,
            "canvas_select_hit_targets": self.canvas_layer_hit_keys(),
            "canvas_preview": self.collect_canvas_preview_state(),
            "pin_overlay_boundary": "Pins are geodetic annotations; renderer sync must rotate them with the globe and apply horizon/depth occlusion.",
            "pin_projection_contract": pin_projection_contract_packet(),
            "boundary_highlight": self.collect_boundary_highlight_state(),
            "boundary_highlight_ack_file": str(BOUNDARY_HIGHLIGHT_ACK_PATH),
            "boundary_highlight_ack": self.boundary_highlight_ack_payload,
            "boundary_highlight_ack_history": self.boundary_highlight_ack_history[:5],
            "boundary_highlight_boundary": "Line hover mask, selected-layer line picking, and closed-ring fill preview are live; full territory feature identity and open-line area inference remain pending.",
            "visible_layers": visible_layers,
            "locked_layers": locked_layers,
            "layer_visibility_snapshot_active": self.layer_visibility_snapshot is not None,
            "layer_count": {
                "visible": len(visible_layers),
                "total": len(LAYER_LABELS),
            },
            "portable_command_line": subprocess.list2cmdline(self.build_portable_command()),
            "boundary": "UI provenance only; renderer image output and RRKAL data manifest are separate artifacts.",
            "rrkal_data_manifest_ref": self.rrkal_manifest_ref_edit.text().strip(),
            "rrkal_data_manifest_ref_boundary": "Reference-only; RRKAL owns manifest/cache governance.",
        }
        return json.dumps(packet, ensure_ascii=False, indent=2)

    def refresh_research_provenance(self) -> None:
        if self.provenance_text is None:
            return
        self.provenance_text.setPlainText(self.build_research_provenance())

    def copy_research_provenance(self) -> None:
        QtWidgets.QApplication.clipboard().setText(self.build_research_provenance())
        if hasattr(self, "status"):
            self.status.setText("已複製科研可重現性摘要")


    def show_layer_operation_feedback(self) -> None:
        self.command_text.setPlainText(
            json.dumps(self.collect_layer_operation_feedback(), ensure_ascii=False, indent=2)
        )
        self.status.setText("Shown layer operation feedback JSON")

    def show_visual_review_readiness(self) -> None:
        packet = self.collect_visual_review_readiness()
        self.command_text.setPlainText(
            json.dumps(packet, ensure_ascii=False, indent=2)
        )
        self.update_visual_review_readiness_label(packet)
        self.status.setText(self.visual_review_readiness_summary_text(packet))

    def copy_visual_review_readiness_summary(self) -> None:
        packet = self.collect_visual_review_readiness()
        summary = self.visual_review_readiness_summary_text(packet)
        QtWidgets.QApplication.clipboard().setText(summary)
        self.update_visual_review_readiness_label(packet)
        self.status.setText("已複製 visual readiness 摘要")

    def show_layer_runtime_state(self) -> None:
        self.write_layer_runtime_state()
        try:
            text = LAYER_RUNTIME_STATE_PATH.read_text(encoding="utf-8")
        except OSError:
            text = json.dumps(self.collect_layer_runtime_state(), ensure_ascii=False, indent=2)
        self.command_text.setPlainText(text)
        self.status.setText(f"已顯示 layer runtime state JSON：{LAYER_RUNTIME_STATE_PATH}")

    def apply_layer_visual_preset(self, preset_id: str) -> None:
        presets_packet = self.collect_layer_visual_presets()
        presets = {
            str(preset.get("id")): preset
            for preset in presets_packet.get("presets", [])
            if isinstance(preset, dict) and preset.get("id")
        }
        preset = presets.get(str(preset_id))
        if not preset:
            self.status.setText(f"Unknown layer preset: {preset_id}")
            return
        known_keys = {key for key, _label in LAYER_LABELS}
        raw_visible_keys = preset.get("visible_layer_keys")
        raw_visible_keys = raw_visible_keys if isinstance(raw_visible_keys, list) else []
        if "__all__" in raw_visible_keys:
            visible_keys = set(known_keys)
        else:
            visible_keys = {str(key) for key in raw_visible_keys if str(key) in known_keys}
            if not visible_keys:
                visible_keys = set(known_keys)
        skipped_locked: list[str] = []
        for key, _label in LAYER_LABELS:
            if key not in self.checks:
                continue
            locked = bool(self.layer_locks.get(key).isChecked()) if key in self.layer_locks else False
            if locked:
                skipped_locked.append(key)
                continue
            self.checks[key].setChecked(key in visible_keys)
            if key in visible_keys and key in self.layer_opacity:
                self.layer_opacity[key].setValue(100)
            if key in visible_keys and key in self.layer_blends:
                self.layer_blends[key].setCurrentText("Normal")
        self.layer_visual_preset = str(preset_id)
        self.refresh_command_preview()
        self.refresh_layer_stack_status()
        label = str(preset.get("label", preset_id))
        if skipped_locked:
            self.set_layer_operation_status(f"Applied layer preset: {label}; skipped locked layers: {len(skipped_locked)}")
        else:
            self.set_layer_operation_status(f"Applied layer preset: {label}")

    def show_layer_capability_matrix(self) -> None:
        self.command_text.setPlainText(
            json.dumps(self.collect_layer_capability_matrix(), ensure_ascii=False, indent=2)
        )
        self.status.setText("已顯示 layer capability matrix JSON")

    def show_layer_render_plan_performance(self) -> None:
        performance = self.collect_layer_render_plan_performance()
        diagnostics = performance.get("cache_diagnostics") if isinstance(performance.get("cache_diagnostics"), dict) else {}
        if hasattr(self, "render_plan_cache_label"):
            self.render_plan_cache_label.setText(self.layer_render_plan_cache_summary_text(diagnostics))
        self.command_text.setPlainText(
            json.dumps(
                {
                    "layer_render_plan_performance": performance,
                    "layer_render_plan_cache_diagnostics": diagnostics,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        self.status.setText("Displayed layer render-plan performance and cache diagnostics")

    def show_profile_ui_state_replay(self) -> None:
        self.command_text.setPlainText(
            json.dumps(self.collect_profile_ui_state_replay(), ensure_ascii=False, indent=2)
        )
        self.status.setText("已顯示 profile UI replay coverage JSON")

    def show_timeline_runtime_state(self) -> None:
        self.write_timeline_runtime_state()
        self.command_text.setPlainText(
            json.dumps(self.collect_timeline_runtime_state(), ensure_ascii=False, indent=2)
        )
        self.status.setText("已顯示 timeline runtime state JSON")

    def show_ocean_material_control_port(self) -> None:
        self.command_text.setPlainText(
            json.dumps(self.collect_ocean_material_control_port(), ensure_ascii=False, indent=2)
        )
        self.status.setText("已顯示 ocean material / sea-state port JSON")

    def copy_ocean_material_summary(self) -> None:
        summary = self.ocean_material_summary_text()
        QtWidgets.QApplication.clipboard().setText(summary)
        self.status.setText("已複製 ocean material / sea-state 摘要")

    def show_hydrology_lod_status(self) -> None:
        self.command_text.setPlainText(
            json.dumps(
                {
                    "hydrology_lod_readiness": self.collect_hydrology_lod_readiness(),
                    "hydrology_lod_runtime_evidence": self.collect_hydrology_lod_runtime_evidence(),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        self.status.setText("已顯示 hydrology / LOD hook JSON")

    def copy_hydrology_lod_summary(self) -> None:
        readiness = self.collect_hydrology_lod_readiness()
        evidence = self.collect_hydrology_lod_runtime_evidence()
        summary = self.hydrology_lod_summary_text(readiness, evidence)
        QtWidgets.QApplication.clipboard().setText(summary)
        if hasattr(self, "hydrology_lod_readiness_label"):
            self.hydrology_lod_readiness_label.setText(summary)
        self.status.setText("已複製 hydrology / LOD 摘要")

    def show_style_renderer_routes(self) -> None:
        self.command_text.setPlainText(
            json.dumps(
                {
                    "style_renderer_entries": self.collect_style_renderer_entries(),
                    "style_profile_renderer_routes": self.collect_style_profile_renderer_routes(),
                    "style_template_visual_preview": self.collect_style_template_visual_preview(),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        self.status.setText("已顯示 style profile renderer routes JSON")

    def copy_style_routes_summary(self) -> None:
        summary = self.style_routes_summary_text()
        QtWidgets.QApplication.clipboard().setText(summary)
        self.status.setText("已複製 style routes 摘要")

    def show_style_thumbnail_slots(self) -> None:
        packet = self.collect_style_template_visual_preview()
        self.command_text.setPlainText(
            json.dumps(
                {
                    "style_template_visual_preview": packet,
                    "thumbnail_slots": packet.get("preview_cards", []),
                    "local_thumbnail_readiness": self.collect_local_style_thumbnail_readiness(),
                    "thumbnail_batch_command": packet.get("thumbnail_batch_command"),
                    "thumbnail_missing_guidance": packet.get("thumbnail_missing_guidance"),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        self.status.setText("已顯示 style thumbnail slots JSON")

    def copy_style_thumbnail_batch_command(self) -> None:
        command = self.collect_style_template_visual_preview().get("thumbnail_batch_command", [])
        command_line = subprocess.list2cmdline([str(part) for part in command]) if isinstance(command, list) else str(command)
        QtWidgets.QApplication.clipboard().setText(command_line)
        self.status.setText("已複製 style thumbnail batch command")

    def show_module_boundary_registry(self) -> None:
        self.command_text.setPlainText(
            json.dumps(self.collect_module_boundary_registry(), ensure_ascii=False, indent=2)
        )
        self.status.setText("已顯示 module boundary registry JSON")

    def copy_module_boundary_summary(self) -> None:
        summary = self.module_boundary_summary_text()
        QtWidgets.QApplication.clipboard().setText(summary)
        self.status.setText("已複製 module boundary 摘要")

    def show_cross_machine_clone_readiness(self) -> None:
        self.command_text.setPlainText(
            json.dumps(self.collect_cross_machine_clone_readiness(), ensure_ascii=False, indent=2)
        )
        self.status.setText("已顯示 cross-machine clone readiness JSON")

    def copy_clone_reviewer_summary(self) -> None:
        summary = self.clone_reviewer_summary_text()
        QtWidgets.QApplication.clipboard().setText(summary)
        self.status.setText("已複製 clone reviewer 摘要")

    def copy_launch_reviewer_summary(self) -> None:
        summary = self.launch_reviewer_summary_text()
        QtWidgets.QApplication.clipboard().setText(summary)
        self.status.setText("已複製 launch reviewer 摘要")

    def show_cursor_geodesy_state(self) -> None:
        self.command_text.setPlainText(
            json.dumps(
                {
                    "cursor_geodesy_readout": self.collect_cursor_geodesy_readout(),
                    "cursor_geodesy_state_file": str(CURSOR_GEODESY_STATE_PATH),
                    "cursor_geodesy_ack_file": str(CURSOR_GEODESY_ACK_PATH),
                    "cursor_geodesy_state": self.cursor_geodesy_state_payload,
                    "cursor_geodesy_ack": self.cursor_geodesy_ack_payload,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        self.status.setText("已顯示 cursor geodesy bridge JSON")

    def copy_cursor_geodesy_summary(self) -> None:
        summary = self.cursor_geodesy_summary_text()
        QtWidgets.QApplication.clipboard().setText(summary)
        self.status.setText("已複製 cursor geodesy 摘要")

    def copy_research_interaction_summary(self) -> None:
        summary = self.research_interaction_summary_text()
        QtWidgets.QApplication.clipboard().setText(summary)
        self.status.setText("已複製 research interaction 摘要")

    def show_boundary_state(self) -> None:
        self.command_text.setPlainText(
            json.dumps(
                {
                    "boundary_highlight": self.collect_boundary_highlight_state(),
                    "boundary_emphasis_control": self.collect_boundary_emphasis_control(),
                    "boundary_identity_warning": self.boundary_identity_warning_text(),
                    "boundary_highlight_ack_file": str(BOUNDARY_HIGHLIGHT_ACK_PATH),
                    "boundary_highlight_ack": self.boundary_highlight_ack_payload,
                    "boundary_highlight_ack_history": self.boundary_highlight_ack_history[:5],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        self.status.setText("已顯示 boundary emphasis / identity JSON")

    def copy_boundary_emphasis_summary(self) -> None:
        packet = self.collect_boundary_emphasis_control()
        summary = self.boundary_emphasis_summary_text(packet)
        QtWidgets.QApplication.clipboard().setText(summary)
        if hasattr(self, "boundary_emphasis_label"):
            self.boundary_emphasis_label.setText(summary)
        self.status.setText("已複製 boundary emphasis 摘要")

    def show_pin_pick_state(self) -> None:
        try:
            text = PIN_PICK_STATE_PATH.read_text(encoding="utf-8")
        except OSError:
            text = json.dumps(self.pin_pick_state_payload or {}, ensure_ascii=False, indent=2)
        self.command_text.setPlainText(text)
        self.status.setText(f"已顯示 Pin pick state JSON：{PIN_PICK_STATE_PATH}")

    def copy_pin_overlay_summary(self) -> None:
        summary = self.pin_overlay_summary_text()
        QtWidgets.QApplication.clipboard().setText(summary)
        self.status.setText("已複製 Pin overlay 摘要")

    def show_layer_pick_state(self) -> None:
        try:
            text = LAYER_PICK_STATE_PATH.read_text(encoding="utf-8")
        except OSError:
            text = json.dumps(self.layer_pick_state_payload or {}, ensure_ascii=False, indent=2)
        self.command_text.setPlainText(text)
        self.status.setText(f"已顯示 layer pick state JSON：{LAYER_PICK_STATE_PATH}")

    def copy_layer_selection_summary(self) -> None:
        summary = self.layer_selection_summary_text()
        QtWidgets.QApplication.clipboard().setText(summary)
        self.status.setText("已複製 layer selection 摘要")

    def toggle_selected_layer_visibility(self) -> None:
        key = self.selected_layer_key
        if key not in self.checks:
            self.set_layer_operation_status("尚未選取圖層")
            return
        if self.layer_locks.get(key) is not None and self.layer_locks[key].isChecked():
            self.set_layer_operation_status("選取圖層已鎖定，visibility 未變更")
            return
        self.checks[key].setChecked(not self.checks[key].isChecked())
        self.refresh_command_preview()
        self.refresh_layer_stack_status()
        label = next((text for layer_key, text in LAYER_LABELS if layer_key == key), key)
        state = "visible" if self.checks[key].isChecked() else "hidden"
        self.set_layer_operation_status(f"Selected layer visibility: {label} -> {state}")

    def toggle_selected_layer_lock(self) -> None:
        key = self.selected_layer_key
        if key not in self.layer_locks:
            self.set_layer_operation_status("No selected layer")
            return
        self.layer_locks[key].setChecked(not self.layer_locks[key].isChecked())
        label = next((text for layer_key, text in LAYER_LABELS if layer_key == key), key)
        state = "locked" if self.layer_locks[key].isChecked() else "unlocked"
        self.set_layer_operation_status(f"Selected layer lock: {label} -> {state}")
        self.refresh_layer_stack_status()

    def reset_selected_layer_controls(self) -> None:
        key = self.selected_layer_key
        if key not in self.layer_locks:
            self.set_layer_operation_status("尚未選取圖層")
            return
        self.auto_capture_document_snapshot("Before selected layer reset")
        self.layer_locks[key].setChecked(False)
        self.layer_opacity[key].setValue(100)
        self.layer_blends[key].setCurrentText("Normal")
        self.refresh_layer_stack_status()
        label = next((text for layer_key, text in LAYER_LABELS if layer_key == key), key)
        self.set_layer_operation_status(f"已重設選取圖層 UI 狀態：{label}")

    def reset_layer_stack_controls(self) -> None:
        self.auto_capture_document_snapshot("Before layer stack reset")
        for key, _label in LAYER_LABELS:
            self.layer_locks[key].blockSignals(True)
            self.layer_opacity[key].blockSignals(True)
            self.layer_blends[key].blockSignals(True)
            self.layer_locks[key].setChecked(False)
            self.layer_opacity[key].setValue(100)
            self.layer_blends[key].setCurrentText("Normal")
            self.layer_locks[key].blockSignals(False)
            self.layer_opacity[key].blockSignals(False)
            self.layer_blends[key].blockSignals(False)
        self.refresh_layer_stack_status()
        self.set_layer_operation_status("已重設 UI-only layer lock/opacity/blend 狀態")

    @QtCore.pyqtSlot()
    def copy_command_to_clipboard(self) -> None:
        QtWidgets.QApplication.clipboard().setText(self.command_text.toPlainText())
        self.status.setText("已複製目前啟動命令")

    @QtCore.pyqtSlot()
    def copy_portable_command_to_clipboard(self) -> None:
        QtWidgets.QApplication.clipboard().setText(subprocess.list2cmdline(self.build_portable_command()))
        self.status.setText("已複製可攜啟動命令")

    @QtCore.pyqtSlot()
    def open_template_dir(self) -> None:
        PROFILE_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(PROFILE_TEMPLATE_DIR)))
        self.status.setText(f"已開啟模板目錄：{PROFILE_TEMPLATE_DIR}")

    @QtCore.pyqtSlot()
    def open_local_profile_dir(self) -> None:
        PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(PROFILE_DIR)))
        self.status.setText(f"已開啟本機配置目錄：{PROFILE_DIR}")

    @QtCore.pyqtSlot()
    def run_smoke_check(self) -> None:
        smoke_script = ROOT / "scripts" / "smoke.ps1"
        if sys.platform == "win32" and smoke_script.exists():
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(smoke_script),
                ],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                timeout=120,
            )
            if result.returncode != 0:
                self.status.setText("Smoke failed")
                self.command_text.setPlainText((result.stderr or result.stdout).strip())
                return
            self.status.setText("Smoke passed")
            self.command_text.setPlainText(result.stdout.strip())
            return
        python_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "py_compile",
                "rrkal_displaytools_qt_panel.py",
                "taichi_global_bathymetry.py",
            ],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            timeout=90,
        )
        if python_result.returncode != 0:
            self.status.setText("Smoke failed: Python compile")
            self.command_text.setPlainText((python_result.stderr or python_result.stdout).strip())
            return
        if sys.platform == "win32":
            ps_command = (
                "$files=Get-ChildItem scripts -Filter *.ps1;"
                "foreach($file in $files){"
                "$tokens=$null;$errors=$null;"
                "[System.Management.Automation.Language.Parser]::ParseFile($file.FullName,[ref]$tokens,[ref]$errors)>$null;"
                "if($errors -and $errors.Count -gt 0){$errors|Format-List *;exit 1}"
                "}"
            )
            ps_result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_command],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                timeout=30,
            )
            if ps_result.returncode != 0:
                self.status.setText("Smoke failed: PowerShell parse")
                self.command_text.setPlainText((ps_result.stderr or ps_result.stdout).strip())
                return
        self.status.setText("Smoke passed: Python compile and script parse")
        self.refresh_command_preview()

    @QtCore.pyqtSlot()
    def save_profile_dialog(self) -> None:
        PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        default_path = PROFILE_DIR / "panel_profile.json"
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "儲存圖層配置",
            str(default_path),
            "JSON profiles (*.json)",
        )
        if not path:
            return
        Path(path).write_text(
            json.dumps(self.collect_profile(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.status.setText(f"已儲存配置：{path}")

    @QtCore.pyqtSlot()
    def export_launch_packet_dialog(self) -> None:
        SHOWCASE_DIR.mkdir(parents=True, exist_ok=True)
        default_path = SHOWCASE_DIR / "launch_packet.json"
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "匯出啟動包",
            str(default_path),
            "JSON packets (*.json)",
        )
        if not path:
            return
        Path(path).write_text(
            json.dumps(self.collect_launch_packet(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.status.setText(f"已匯出啟動包：{path}")

    @QtCore.pyqtSlot()
    def export_reviewer_packet_dialog(self) -> None:
        SHOWCASE_DIR.mkdir(parents=True, exist_ok=True)
        default_path = SHOWCASE_DIR / "reviewer_packet.json"
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "匯出 reviewer packet",
            str(default_path),
            "JSON packets (*.json)",
        )
        if not path:
            return
        Path(path).write_text(
            json.dumps(self.collect_reviewer_packet(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.status.setText(f"已匯出 reviewer packet：{path}")

    @QtCore.pyqtSlot()
    def show_renderer_capabilities(self) -> None:
        result = subprocess.run(
            [sys.executable, str(RENDERER), "--print-renderer-capabilities"],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            timeout=90,
        )
        if result.returncode != 0:
            self.status.setText("Renderer capabilities failed")
            self.command_text.setPlainText((result.stderr or result.stdout).strip())
            return
        self.command_text.setPlainText(result.stdout.strip())
        self.status.setText("已顯示 renderer capabilities JSON")

    @QtCore.pyqtSlot()
    def show_closed_loop_status(self) -> None:
        result = subprocess.run(
            [sys.executable, str(RENDERER), "--print-closed-loop-status"],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            timeout=90,
        )
        if result.returncode != 0:
            self.status.setText("Closed-loop status failed")
            self.command_text.setPlainText((result.stderr or result.stdout).strip())
            return
        self.command_text.setPlainText(result.stdout.strip())
        self.status.setText("已顯示 renderer closed-loop status JSON")

    @QtCore.pyqtSlot()
    def show_layer_manifest(self) -> None:
        result = subprocess.run(
            [sys.executable, str(RENDERER), "--print-layer-manifest"],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            timeout=90,
        )
        if result.returncode != 0:
            self.status.setText("Layer manifest failed")
            self.command_text.setPlainText((result.stderr or result.stdout).strip())
            return
        self.command_text.setPlainText(result.stdout.strip())
        self.status.setText("已顯示 renderer layer manifest JSON")

    @QtCore.pyqtSlot()
    def load_profile_dialog(self) -> None:
        PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "載入圖層配置",
            str(PROFILE_DIR),
            "JSON profiles (*.json)",
        )
        if not path:
            return
        self.load_profile_path(Path(path))

    @QtCore.pyqtSlot()
    def launch_renderer(self) -> None:
        if not RENDERER.exists():
            self.status.setText(f"找不到 renderer: {RENDERER}")
            return
        if self.process is not None and self.process.poll() is None:
            self.status.setText(f"renderer 已在執行中，PID={self.process.pid}")
            return
        kwargs: dict[str, object] = {"cwd": str(ROOT)}
        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        self.process = subprocess.Popen(self.build_command(), **kwargs)
        self.status.setText(f"已啟動 renderer，PID={self.process.pid}")

    @QtCore.pyqtSlot()
    def stop_renderer(self) -> None:
        if self.process is None or self.process.poll() is not None:
            self.status.setText("沒有由此面板啟動且仍在執行的 renderer")
            return
        self.process.terminate()
        self.status.setText(f"已要求停止 renderer，PID={self.process.pid}")

    @QtCore.pyqtSlot()
    def restart_renderer(self) -> None:
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
        self.process = None
        self.launch_renderer()

    @QtCore.pyqtSlot()
    def update_process_status(self) -> None:
        if self.process is None:
            return
        pid = self.process.pid
        exit_code = self.process.poll()
        if exit_code is None:
            self.status.setText(f"renderer 執行中，PID={pid}")
            return
        self.status.setText(f"renderer 已結束，PID={pid}，exit={exit_code}")
        self.process = None

    def _set_combo(self, combo: QtWidgets.QComboBox, value: str) -> None:
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _set_layers(self, enabled: dict[str, bool]) -> None:
        for key, check in self.checks.items():
            check.blockSignals(True)
            check.setChecked(enabled.get(key, False))
            check.blockSignals(False)
        self.refresh_command_preview()
        self.refresh_layer_stack_status()

    def _toggle_group(self, keys: tuple[str, ...]) -> None:
        target = not all(self.checks[key].isChecked() for key in keys)
        skipped_locked = 0
        for key in keys:
            if self.layer_locks.get(key) is not None and self.layer_locks[key].isChecked():
                skipped_locked += 1
                continue
            self.checks[key].setChecked(target)
        self.refresh_command_preview()
        self.refresh_layer_stack_status()
        state = "visible" if target else "hidden"
        if skipped_locked:
            self.set_layer_operation_status(
                f"Layer group toggle: {len(keys) - skipped_locked}/{len(keys)} layer(s) -> {state}; skipped locked={skipped_locked}"
            )
        else:
            self.set_layer_operation_status(f"Layer group toggle: {len(keys)}/{len(keys)} layer(s) -> {state}")

    @QtCore.pyqtSlot()
    def toggle_hydrology_layers(self) -> None:
        self._toggle_group(("lake_layer", "river_layer"))

    @QtCore.pyqtSlot()
    def toggle_maritime_layers(self) -> None:
        self._toggle_group(("territorial_sea_layer", "eez_layer", "high_seas_layer"))

    @QtCore.pyqtSlot()
    def toggle_transport_layers(self) -> None:
        self._toggle_group(("aircraft_layer", "vehicle_icons"))

    @QtCore.pyqtSlot()
    def toggle_visual_aids(self) -> None:
        self._toggle_group(("show_grid", "show_stars", "terrain_contours", "scale_bar", "pin_layer"))

    @QtCore.pyqtSlot()
    def apply_baseline(self, snapshot_label: str | bool = "Before Baseline preset") -> None:
        if isinstance(snapshot_label, bool):
            snapshot_label = "Before Baseline preset"
        self.auto_capture_document_snapshot(snapshot_label)
        self._set_combo(self.style_combo, "scientific")
        self._set_combo(self.topo_combo, "gebco")
        self._set_combo(self.data_combo, "static")
        self.topo_step_edit.setText("48")
        self.wave_edit.setText("0.22")
        self.roughness_edit.setText("0.28")
        self.foam_edit.setText("0.12")
        self._set_layers(
            {
                "show_grid": True,
                "show_stars": True,
                "lake_layer": True,
                "river_layer": True,
                "border_layer": True,
                "pin_layer": True,
                "ocean_material": True,
                "scale_bar": True,
            }
        )

    @QtCore.pyqtSlot()
    def apply_maritime(self) -> None:
        self.auto_capture_document_snapshot("Before Maritime preset")
        self.apply_baseline(snapshot_label="")
        self._set_combo(self.style_combo, "nautical")
        current = {key: self.checks[key].isChecked() for key in self.checks}
        current.update(
            {
                "territorial_sea_layer": True,
                "eez_layer": True,
                "high_seas_layer": True,
                "terrain_contours": True,
            }
        )
        self._set_layers(current)

    @QtCore.pyqtSlot()
    def apply_parchment(self) -> None:
        self.auto_capture_document_snapshot("Before Parchment preset")
        self.apply_baseline(snapshot_label="")
        self._set_combo(self.style_combo, "parchment")
        self.checks["show_stars"].setChecked(False)
        self.checks["terrain_contours"].setChecked(True)

    @QtCore.pyqtSlot()
    def apply_tactical(self) -> None:
        self.auto_capture_document_snapshot("Before Tactical preset")
        self.apply_maritime()
        self._set_combo(self.style_combo, "tactical")
        self.checks["aircraft_layer"].setChecked(True)
        self.checks["vehicle_icons"].setChecked(True)

    @QtCore.pyqtSlot()
    def apply_minimal(self) -> None:
        self._set_combo(self.style_combo, "scientific")
        self._set_combo(self.topo_combo, "gebco")
        self._set_layers({"ocean_material": True, "scale_bar": True})

    @QtCore.pyqtSlot()
    def apply_fast_synthetic(self) -> None:
        self.auto_capture_document_snapshot("Before Fast synthetic preset")
        self.apply_baseline(snapshot_label="")
        self._set_combo(self.topo_combo, "synthetic")
        self.topo_step_edit.setText("64")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RRKAL_displaytools Qt operator panel")
    parser.add_argument("--profile", type=Path, help="Load a panel profile JSON on startup")
    parser.add_argument("--template", help="Load a built-in profile template by file stem, for example maritime_hydrology")
    parser.add_argument("--list-templates", action="store_true", help="Print built-in profile templates as JSON and exit")
    return parser


def resolve_startup_profile(profile: Path | None, template: str | None) -> Path | None:
    if profile is not None:
        return profile
    if not template:
        return None
    template_name = template[:-5] if template.endswith(".json") else template
    return PROFILE_TEMPLATE_DIR / f"{template_name}.json"


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    if args.list_templates:
        print(json.dumps(profile_template_packet(), ensure_ascii=False, indent=2))
        return
    app = QtWidgets.QApplication([sys.argv[0]])
    panel = DisplayToolsQtPanel(initial_profile=resolve_startup_profile(args.profile, args.template))
    panel.show()
    raise SystemExit(app.exec())


if __name__ == "__main__":
    main()
