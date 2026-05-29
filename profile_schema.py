from __future__ import annotations

import json
import sys
from pathlib import Path


PROFILE_SCHEMA_ID = "rrkal_displaytools.qt_panel_profile.v1"
BOUNDARY_HIGHLIGHT_SCHEMA_ID = "rrkal_displaytools.boundary_highlight_mask.v1"
CANVAS_PREVIEW_SCHEMA_ID = "rrkal_displaytools.canvas_preview.v1"

REQUIRED_PROFILE_TOP_LEVEL = {"schema", "renderer", "ocean_material", "layers"}
OPTIONAL_PROFILE_TOP_LEVEL = {
    "selected_layer",
    "selected_pin_id",
    "layer_stack_ui",
    "tool_state",
    "pins",
    "boundary_highlight",
    "canvas_preview",
}
REQUIRED_PROFILE_RENDERER = {
    "style_profile",
    "ui_backend",
    "topo_source",
    "data_mode",
    "width",
    "height",
    "topo_step",
    "taichi_arch",
}
OPTIONAL_PROFILE_RENDERER = {"rrkal_data_manifest_ref"}
REQUIRED_PROFILE_OCEAN_MATERIAL = {"wave_strength", "roughness", "foam"}
REQUIRED_PROFILE_LAYERS = {
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
    "ocean_material",
    "terrain_contours",
    "scale_bar",
    "vehicle_icons",
    "demo_closed_loop",
}
REQUIRED_LAYER_STACK_KEYS = REQUIRED_PROFILE_LAYERS - {"demo_closed_loop"}
REQUIRED_LAYER_STACK_UI_FIELDS = {"locked", "opacity", "blend_mode"}
OPTIONAL_LAYER_STACK_UI_FIELDS = {"selected", "renderer_sync"}
BLEND_MODES = {"Normal", "Screen", "Multiply", "Overlay", "Soft Light"}
TOOL_MODES = {"move", "select", "pin"}
PIN_TYPES = {"Observation", "Sample Site", "Anomaly", "Reference", "Event"}
PIN_LABEL_MODES = {"auto", "selected", "priority", "hidden"}
CANVAS_PREVIEW_MODES = {"state", "thumbnail"}
BOUNDARY_HIGHLIGHT_LAYER_KEYS = {"border_layer", "territorial_sea_layer", "eez_layer", "high_seas_layer"}
BOUNDARY_HIGHLIGHT_TRIGGERS = {"hover", "selected", "hover_or_selected"}
REQUIRED_BOUNDARY_HIGHLIGHT_FIELDS = {
    "schema",
    "enabled",
    "trigger",
    "target_layers",
    "color_rgb",
    "contrast",
    "alpha",
    "gamma",
    "feather",
    "breathing",
    "renderer_sync",
}
REQUIRED_BOUNDARY_BREATHING_FIELDS = {"enabled", "speed", "amplitude"}
REQUIRED_PIN_FIELDS = {"id", "type", "label", "latitude", "longitude", "placement"}
OPTIONAL_PIN_FIELDS = {"note", "target_layer", "label_priority"}
REQUIRED_TOOL_STATE_FIELDS = {
    "active_tool",
    "target_layer",
}
OPTIONAL_TOOL_STATE_FIELDS = {"renderer_sync", "pin", "pin_label_mode", "pin_label_min_priority"}


def profile_payload_errors(profile: dict[str, object]) -> list[str]:
    errors: list[str] = []
    for key in sorted(REQUIRED_PROFILE_TOP_LEVEL - set(profile)):
        errors.append(f"missing top-level key: {key}")
    if profile.get("schema") != PROFILE_SCHEMA_ID:
        errors.append(f"unexpected schema: {profile.get('schema')!r}")
    renderer = profile.get("renderer")
    if not isinstance(renderer, dict):
        errors.append("renderer must be an object")
    else:
        for key in sorted(REQUIRED_PROFILE_RENDERER - set(renderer)):
            errors.append(f"missing renderer key: {key}")
    material = profile.get("ocean_material")
    if not isinstance(material, dict):
        errors.append("ocean_material must be an object")
    else:
        for key in sorted(REQUIRED_PROFILE_OCEAN_MATERIAL - set(material)):
            errors.append(f"missing ocean_material key: {key}")
    layers = profile.get("layers")
    if not isinstance(layers, dict):
        errors.append("layers must be an object")
    else:
        for key in sorted(REQUIRED_PROFILE_LAYERS - set(layers)):
            errors.append(f"missing layer key: {key}")
        for key, value in layers.items():
            if not isinstance(value, bool):
                errors.append(f"layer {key} must be boolean")
    selected_layer = profile.get("selected_layer")
    if selected_layer is not None:
        if not isinstance(selected_layer, str):
            errors.append("selected_layer must be a string")
        elif selected_layer not in REQUIRED_LAYER_STACK_KEYS:
            errors.append(f"selected_layer is not a known layer stack key: {selected_layer}")
    selected_pin_id = profile.get("selected_pin_id")
    if selected_pin_id is not None and not isinstance(selected_pin_id, str):
        errors.append("selected_pin_id must be a string or null")
    layer_stack = profile.get("layer_stack_ui")
    if layer_stack is not None:
        if not isinstance(layer_stack, dict):
            errors.append("layer_stack_ui must be an object")
        else:
            for key in sorted(REQUIRED_LAYER_STACK_KEYS - set(layer_stack)):
                errors.append(f"missing layer_stack_ui key: {key}")
            for key, value in layer_stack.items():
                if key not in REQUIRED_LAYER_STACK_KEYS:
                    errors.append(f"unknown layer_stack_ui key: {key}")
                    continue
                if not isinstance(value, dict):
                    errors.append(f"layer_stack_ui {key} must be an object")
                    continue
                allowed_fields = REQUIRED_LAYER_STACK_UI_FIELDS | OPTIONAL_LAYER_STACK_UI_FIELDS
                for field in sorted(REQUIRED_LAYER_STACK_UI_FIELDS - set(value)):
                    errors.append(f"missing layer_stack_ui {key} field: {field}")
                for field in sorted(set(value) - allowed_fields):
                    errors.append(f"unknown layer_stack_ui {key} field: {field}")
                locked = value.get("locked")
                if not isinstance(locked, bool):
                    errors.append(f"layer_stack_ui {key}.locked must be boolean")
                opacity = value.get("opacity")
                if not isinstance(opacity, int) or isinstance(opacity, bool) or not 0 <= opacity <= 100:
                    errors.append(f"layer_stack_ui {key}.opacity must be an integer from 0 to 100")
                blend_mode = value.get("blend_mode")
                if not isinstance(blend_mode, str) or blend_mode not in BLEND_MODES:
                    errors.append(f"layer_stack_ui {key}.blend_mode must be one of {sorted(BLEND_MODES)}")
                if "selected" in value and not isinstance(value["selected"], bool):
                    errors.append(f"layer_stack_ui {key}.selected must be boolean")
                if "renderer_sync" in value and not isinstance(value["renderer_sync"], str):
                    errors.append(f"layer_stack_ui {key}.renderer_sync must be a string")
    tool_state = profile.get("tool_state")
    if tool_state is not None:
        if not isinstance(tool_state, dict):
            errors.append("tool_state must be an object")
        else:
            allowed_fields = REQUIRED_TOOL_STATE_FIELDS | OPTIONAL_TOOL_STATE_FIELDS
            for field in sorted(REQUIRED_TOOL_STATE_FIELDS - set(tool_state)):
                errors.append(f"missing tool_state field: {field}")
            for field in sorted(set(tool_state) - allowed_fields):
                errors.append(f"unknown tool_state field: {field}")
            active_tool = tool_state.get("active_tool")
            if not isinstance(active_tool, str) or active_tool not in TOOL_MODES:
                errors.append(f"tool_state.active_tool must be one of {sorted(TOOL_MODES)}")
            target_layer = tool_state.get("target_layer")
            if target_layer is not None:
                if not isinstance(target_layer, str):
                    errors.append("tool_state.target_layer must be a string or null")
                elif target_layer not in REQUIRED_LAYER_STACK_KEYS:
                    errors.append(f"tool_state.target_layer is not a known layer stack key: {target_layer}")
            pin_label_mode = tool_state.get("pin_label_mode")
            if pin_label_mode is not None:
                if not isinstance(pin_label_mode, str) or pin_label_mode not in PIN_LABEL_MODES:
                    errors.append(f"tool_state.pin_label_mode must be one of {sorted(PIN_LABEL_MODES)}")
            pin_label_min_priority = tool_state.get("pin_label_min_priority")
            if pin_label_min_priority is not None:
                if (
                    not isinstance(pin_label_min_priority, int)
                    or isinstance(pin_label_min_priority, bool)
                    or not 0 <= pin_label_min_priority <= 100
                ):
                    errors.append("tool_state.pin_label_min_priority must be an integer from 0 to 100")
            pin = tool_state.get("pin")
            if pin is not None:
                if not isinstance(pin, dict):
                    errors.append("tool_state.pin must be an object")
                else:
                    pin_type = pin.get("type")
                    if not isinstance(pin_type, str) or pin_type not in PIN_TYPES:
                        errors.append(f"tool_state.pin.type must be one of {sorted(PIN_TYPES)}")
                    for field in ("label", "note", "placement"):
                        if field in pin and not isinstance(pin[field], str):
                            errors.append(f"tool_state.pin.{field} must be a string")
                    for field in ("latitude", "longitude"):
                        if field in pin and not isinstance(pin[field], str):
                            errors.append(f"tool_state.pin.{field} must be a string")
                    if "label_priority" in pin:
                        priority = pin["label_priority"]
                        if not isinstance(priority, int) or isinstance(priority, bool) or not 0 <= priority <= 100:
                            errors.append("tool_state.pin.label_priority must be an integer from 0 to 100")
            if "renderer_sync" in tool_state and not isinstance(tool_state["renderer_sync"], str):
                errors.append("tool_state.renderer_sync must be a string")
    pins = profile.get("pins")
    if pins is not None:
        if not isinstance(pins, list):
            errors.append("pins must be a list")
        else:
            allowed_fields = REQUIRED_PIN_FIELDS | OPTIONAL_PIN_FIELDS
            for index, pin in enumerate(pins):
                if not isinstance(pin, dict):
                    errors.append(f"pins[{index}] must be an object")
                    continue
                for field in sorted(REQUIRED_PIN_FIELDS - set(pin)):
                    errors.append(f"missing pins[{index}] field: {field}")
                for field in sorted(set(pin) - allowed_fields):
                    errors.append(f"unknown pins[{index}] field: {field}")
                for field in ("id", "label", "placement"):
                    if not isinstance(pin.get(field), str):
                        errors.append(f"pins[{index}].{field} must be a string")
                if "note" in pin and not isinstance(pin["note"], str):
                    errors.append(f"pins[{index}].note must be a string")
                if "target_layer" in pin and pin["target_layer"] is not None:
                    if not isinstance(pin["target_layer"], str):
                        errors.append(f"pins[{index}].target_layer must be a string or null")
                    elif pin["target_layer"] not in REQUIRED_LAYER_STACK_KEYS:
                        errors.append(f"pins[{index}].target_layer is not a known layer stack key")
                if "label_priority" in pin:
                    priority = pin["label_priority"]
                    if not isinstance(priority, int) or isinstance(priority, bool) or not 0 <= priority <= 100:
                        errors.append(f"pins[{index}].label_priority must be an integer from 0 to 100")
                pin_type = pin.get("type")
                if not isinstance(pin_type, str) or pin_type not in PIN_TYPES:
                    errors.append(f"pins[{index}].type must be one of {sorted(PIN_TYPES)}")
                latitude = pin.get("latitude")
                if not isinstance(latitude, (int, float)) or isinstance(latitude, bool) or not -90 <= latitude <= 90:
                    errors.append(f"pins[{index}].latitude must be a number from -90 to 90")
                longitude = pin.get("longitude")
                if not isinstance(longitude, (int, float)) or isinstance(longitude, bool) or not -180 <= longitude <= 180:
                    errors.append(f"pins[{index}].longitude must be a number from -180 to 180")
            if isinstance(selected_pin_id, str):
                pin_ids = {pin.get("id") for pin in pins if isinstance(pin, dict)}
                if selected_pin_id not in pin_ids:
                    errors.append("selected_pin_id must match an id in pins")
    canvas_preview = profile.get("canvas_preview")
    if canvas_preview is not None:
        if not isinstance(canvas_preview, dict):
            errors.append("canvas_preview must be an object")
        else:
            allowed_fields = {"schema", "mode", "renderer_thumbnail_path", "renderer_sync"}
            for field in sorted(set(canvas_preview) - allowed_fields):
                errors.append(f"unknown canvas_preview field: {field}")
            if canvas_preview.get("schema") != CANVAS_PREVIEW_SCHEMA_ID:
                errors.append(f"canvas_preview.schema must be {CANVAS_PREVIEW_SCHEMA_ID}")
            mode = canvas_preview.get("mode")
            if not isinstance(mode, str) or mode not in CANVAS_PREVIEW_MODES:
                errors.append(f"canvas_preview.mode must be one of {sorted(CANVAS_PREVIEW_MODES)}")
            thumbnail_path = canvas_preview.get("renderer_thumbnail_path")
            if thumbnail_path is not None and not isinstance(thumbnail_path, str):
                errors.append("canvas_preview.renderer_thumbnail_path must be a string or null")
            renderer_sync = canvas_preview.get("renderer_sync")
            if renderer_sync is not None and not isinstance(renderer_sync, str):
                errors.append("canvas_preview.renderer_sync must be a string")
    boundary_highlight = profile.get("boundary_highlight")
    if boundary_highlight is not None:
        if not isinstance(boundary_highlight, dict):
            errors.append("boundary_highlight must be an object")
        else:
            for field in sorted(REQUIRED_BOUNDARY_HIGHLIGHT_FIELDS - set(boundary_highlight)):
                errors.append(f"missing boundary_highlight field: {field}")
            schema = boundary_highlight.get("schema")
            if schema != BOUNDARY_HIGHLIGHT_SCHEMA_ID:
                errors.append(f"boundary_highlight.schema must be {BOUNDARY_HIGHLIGHT_SCHEMA_ID!r}")
            if not isinstance(boundary_highlight.get("enabled"), bool):
                errors.append("boundary_highlight.enabled must be boolean")
            trigger = boundary_highlight.get("trigger")
            if not isinstance(trigger, str) or trigger not in BOUNDARY_HIGHLIGHT_TRIGGERS:
                errors.append(f"boundary_highlight.trigger must be one of {sorted(BOUNDARY_HIGHLIGHT_TRIGGERS)}")
            target_layers = boundary_highlight.get("target_layers")
            if not isinstance(target_layers, list) or not target_layers:
                errors.append("boundary_highlight.target_layers must be a non-empty list")
            elif any(not isinstance(layer, str) or layer not in BOUNDARY_HIGHLIGHT_LAYER_KEYS for layer in target_layers):
                errors.append("boundary_highlight.target_layers must contain only boundary layer keys")
            color_rgb = boundary_highlight.get("color_rgb")
            if (
                not isinstance(color_rgb, list)
                or len(color_rgb) != 3
                or any(not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 255 for value in color_rgb)
            ):
                errors.append("boundary_highlight.color_rgb must be three integers from 0 to 255")
            for field in ("contrast", "alpha", "feather"):
                value = boundary_highlight.get(field)
                if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 100:
                    errors.append(f"boundary_highlight.{field} must be an integer from 0 to 100")
            gamma = boundary_highlight.get("gamma")
            if not isinstance(gamma, int) or isinstance(gamma, bool) or not 25 <= gamma <= 300:
                errors.append("boundary_highlight.gamma must be an integer from 25 to 300")
            breathing = boundary_highlight.get("breathing")
            if not isinstance(breathing, dict):
                errors.append("boundary_highlight.breathing must be an object")
            else:
                for field in sorted(REQUIRED_BOUNDARY_BREATHING_FIELDS - set(breathing)):
                    errors.append(f"missing boundary_highlight.breathing field: {field}")
                if not isinstance(breathing.get("enabled"), bool):
                    errors.append("boundary_highlight.breathing.enabled must be boolean")
                for field in ("speed", "amplitude"):
                    value = breathing.get(field)
                    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 100:
                        errors.append(f"boundary_highlight.breathing.{field} must be an integer from 0 to 100")
            if not isinstance(boundary_highlight.get("renderer_sync"), str):
                errors.append("boundary_highlight.renderer_sync must be a string")
    return errors


def load_profile_payload(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("root must be an object")
    return payload


def profile_schema_packet() -> dict[str, object]:
    return {
        "schema": "rrkal_displaytools.profile_schema_contract.v1",
        "profile_schema_id": PROFILE_SCHEMA_ID,
        "required_top_level": sorted(REQUIRED_PROFILE_TOP_LEVEL),
        "optional_top_level": sorted(OPTIONAL_PROFILE_TOP_LEVEL),
        "required_renderer": sorted(REQUIRED_PROFILE_RENDERER),
        "optional_renderer": sorted(OPTIONAL_PROFILE_RENDERER),
        "required_ocean_material": sorted(REQUIRED_PROFILE_OCEAN_MATERIAL),
        "required_layers": sorted(REQUIRED_PROFILE_LAYERS),
        "optional_layer_stack_ui": {
            "keys": sorted(REQUIRED_LAYER_STACK_KEYS),
            "required_fields": sorted(REQUIRED_LAYER_STACK_UI_FIELDS),
            "optional_fields": sorted(OPTIONAL_LAYER_STACK_UI_FIELDS),
            "blend_modes": sorted(BLEND_MODES),
        },
        "optional_tool_state": {
            "required_fields": sorted(REQUIRED_TOOL_STATE_FIELDS),
            "optional_fields": sorted(OPTIONAL_TOOL_STATE_FIELDS),
            "tool_modes": sorted(TOOL_MODES),
            "pin_types": sorted(PIN_TYPES),
            "pin_label_modes": sorted(PIN_LABEL_MODES),
        },
        "optional_boundary_highlight": {
            "schema": BOUNDARY_HIGHLIGHT_SCHEMA_ID,
            "target_layers": sorted(BOUNDARY_HIGHLIGHT_LAYER_KEYS),
            "triggers": sorted(BOUNDARY_HIGHLIGHT_TRIGGERS),
            "required_fields": sorted(REQUIRED_BOUNDARY_HIGHLIGHT_FIELDS),
            "breathing_required_fields": sorted(REQUIRED_BOUNDARY_BREATHING_FIELDS),
            "status": "Qt UI/profile/launch packet state; renderer hover polygon mask pending",
        },
        "optional_pins": {
            "required_fields": sorted(REQUIRED_PIN_FIELDS),
            "optional_fields": sorted(OPTIONAL_PIN_FIELDS),
            "pin_types": sorted(PIN_TYPES),
            "coordinate_source": "manual_lat_lon and cursor estimate now; renderer geodetic anchor with globe rotation and horizon/depth occlusion planned",
        },
        "local_only_paths": [
            "state/ui_profiles/",
            "state/showcase/",
        ],
        "repo_shared_paths": [
            "profiles/",
            "docs/PROFILE_SCHEMA.zh-TW.md",
        ],
    }


def main() -> int:
    print(json.dumps(profile_schema_packet(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
