from __future__ import annotations

import json
import sys
from pathlib import Path


PROFILE_SCHEMA_ID = "rrkal_displaytools.qt_panel_profile.v1"

REQUIRED_PROFILE_TOP_LEVEL = {"schema", "renderer", "ocean_material", "layers"}
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
        "required_renderer": sorted(REQUIRED_PROFILE_RENDERER),
        "required_ocean_material": sorted(REQUIRED_PROFILE_OCEAN_MATERIAL),
        "required_layers": sorted(REQUIRED_PROFILE_LAYERS),
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
