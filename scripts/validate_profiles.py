from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = ROOT / "profiles"

REQUIRED_TOP_LEVEL = {"schema", "renderer", "ocean_material", "layers"}
REQUIRED_RENDERER = {
    "style_profile",
    "ui_backend",
    "topo_source",
    "data_mode",
    "width",
    "height",
    "topo_step",
    "taichi_arch",
}
REQUIRED_OCEAN_MATERIAL = {"wave_strength", "roughness", "foam"}
REQUIRED_LAYERS = {
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


def missing_keys(payload: dict[str, object], required: set[str]) -> list[str]:
    return sorted(key for key in required if key not in payload)


def validate_profile(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return [f"{path.name}: invalid JSON: {exc}"]
    if not isinstance(payload, dict):
        return [f"{path.name}: root must be an object"]
    for key in missing_keys(payload, REQUIRED_TOP_LEVEL):
        errors.append(f"{path.name}: missing top-level key {key}")
    if payload.get("schema") != "rrkal_displaytools.qt_panel_profile.v1":
        errors.append(f"{path.name}: unexpected schema {payload.get('schema')!r}")
    renderer = payload.get("renderer")
    if not isinstance(renderer, dict):
        errors.append(f"{path.name}: renderer must be an object")
    else:
        for key in missing_keys(renderer, REQUIRED_RENDERER):
            errors.append(f"{path.name}: missing renderer key {key}")
    material = payload.get("ocean_material")
    if not isinstance(material, dict):
        errors.append(f"{path.name}: ocean_material must be an object")
    else:
        for key in missing_keys(material, REQUIRED_OCEAN_MATERIAL):
            errors.append(f"{path.name}: missing ocean_material key {key}")
    layers = payload.get("layers")
    if not isinstance(layers, dict):
        errors.append(f"{path.name}: layers must be an object")
    else:
        for key in missing_keys(layers, REQUIRED_LAYERS):
            errors.append(f"{path.name}: missing layer key {key}")
        for key, value in layers.items():
            if not isinstance(value, bool):
                errors.append(f"{path.name}: layer {key} must be boolean")
    return errors


def main() -> int:
    profile_paths = sorted(PROFILE_DIR.glob("*.json"))
    if not profile_paths:
        print("No profile templates found.", file=sys.stderr)
        return 1
    errors: list[str] = []
    for path in profile_paths:
        errors.extend(validate_profile(path))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Profile validation passed: {len(profile_paths)} templates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
