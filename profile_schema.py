from __future__ import annotations

import json
import sys
from pathlib import Path


PROFILE_SCHEMA_ID = "rrkal_displaytools.qt_panel_profile.v1"

REQUIRED_PROFILE_TOP_LEVEL = {"schema", "renderer", "ocean_material", "layers"}
OPTIONAL_PROFILE_TOP_LEVEL = {"selected_layer", "layer_stack_ui", "tool_state", "pins"}
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
REQUIRED_PIN_FIELDS = {"id", "type", "label", "latitude", "longitude", "placement"}
OPTIONAL_PIN_FIELDS = {"note", "target_layer"}
REQUIRED_TOOL_STATE_FIELDS = {
    "active_tool",
    "target_layer",
}
OPTIONAL_TOOL_STATE_FIELDS = {"renderer_sync", "pin"}


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
                pin_type = pin.get("type")
                if not isinstance(pin_type, str) or pin_type not in PIN_TYPES:
                    errors.append(f"pins[{index}].type must be one of {sorted(PIN_TYPES)}")
                latitude = pin.get("latitude")
                if not isinstance(latitude, (int, float)) or isinstance(latitude, bool) or not -90 <= latitude <= 90:
                    errors.append(f"pins[{index}].latitude must be a number from -90 to 90")
                longitude = pin.get("longitude")
                if not isinstance(longitude, (int, float)) or isinstance(longitude, bool) or not -180 <= longitude <= 180:
                    errors.append(f"pins[{index}].longitude must be a number from -180 to 180")
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
        },
        "optional_pins": {
            "required_fields": sorted(REQUIRED_PIN_FIELDS),
            "optional_fields": sorted(OPTIONAL_PIN_FIELDS),
            "pin_types": sorted(PIN_TYPES),
            "coordinate_source": "manual_lat_lon now; cursor lat/lon resolver planned",
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
