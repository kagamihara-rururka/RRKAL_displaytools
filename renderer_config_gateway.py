"""Typed renderer configuration gateway.

This module is a pre-decoupling contract for replacing scattered
``getattr(args, "...", default)`` access with one normalized configuration
object. It is intentionally standalone until the renderer monolith is split.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass, fields
from datetime import UTC, datetime
from typing import Any


SCHEMA = "rrkal_displaytools.renderer_config_gateway.v1"


@dataclass(frozen=True)
class RendererConfig:
    width: int = 1280
    height: int = 720
    topo_step: int = 48
    style_profile: str = "scientific"
    ui_backend: str = "qt"
    topo_source: str = "synthetic"
    data_mode: str = "synthetic"
    taichi_arch: str = "gpu"
    map_projection: str = "globe"
    rrkal_data_manifest_ref: str = ""
    demo_closed_loop: bool = False
    ocean_wave_strength: float = 0.22
    ocean_roughness: float = 0.28
    ocean_foam: float = 0.12


def _as_mapping(value: object | None) -> dict[str, object]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return {str(key): item for key, item in value.items()}
    try:
        return {str(key): item for key, item in vars(value).items()}
    except TypeError:
        return {}


def _coerce_int(value: object, default: int, lower: int = 1) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(lower, number)


def _coerce_float(value: object, default: float, lower: float, upper: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return max(lower, min(number, upper))


def _coerce_bool(value: object, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    if value is None:
        return default
    return bool(value)


def normalize_renderer_config(value: object | None = None) -> RendererConfig:
    payload = _as_mapping(value)
    defaults = RendererConfig()
    return RendererConfig(
        width=_coerce_int(payload.get("width"), defaults.width),
        height=_coerce_int(payload.get("height"), defaults.height),
        topo_step=_coerce_int(payload.get("topo_step"), defaults.topo_step),
        style_profile=str(payload.get("style_profile") or defaults.style_profile),
        ui_backend=str(payload.get("ui_backend") or defaults.ui_backend),
        topo_source=str(payload.get("topo_source") or defaults.topo_source),
        data_mode=str(payload.get("data_mode") or defaults.data_mode),
        taichi_arch=str(payload.get("taichi_arch") or defaults.taichi_arch),
        map_projection=str(payload.get("map_projection") or defaults.map_projection),
        rrkal_data_manifest_ref=str(payload.get("rrkal_data_manifest_ref") or defaults.rrkal_data_manifest_ref),
        demo_closed_loop=_coerce_bool(payload.get("demo_closed_loop"), defaults.demo_closed_loop),
        ocean_wave_strength=_coerce_float(payload.get("ocean_wave_strength"), defaults.ocean_wave_strength, 0.0, 1.0),
        ocean_roughness=_coerce_float(payload.get("ocean_roughness"), defaults.ocean_roughness, 0.02, 1.0),
        ocean_foam=_coerce_float(payload.get("ocean_foam"), defaults.ocean_foam, 0.0, 1.0),
    )


def renderer_config_gateway_packet(
    source: str = "renderer_config_gateway",
    value: object | None = None,
) -> dict[str, object]:
    config = normalize_renderer_config(value)
    defaults = RendererConfig()
    normalized = asdict(config)
    default_values = asdict(defaults)
    changed_defaults = [
        key for key, current in normalized.items()
        if current != default_values.get(key)
    ]
    return {
        "schema": SCHEMA,
        "source": source,
        "generated_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "status": "contract_ready",
        "config": normalized,
        "defaults": default_values,
        "field_names": [field.name for field in fields(RendererConfig)],
        "changed_defaults": changed_defaults,
        "replaces_pattern": "getattr(args, <field>, <default>)",
        "next_integration_target": "render_plan_compose / renderer argument normalization",
        "boundary": "Config normalization only; does not launch Qt, Taichi, data discovery, download, import or cache governance.",
        "portable": True,
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Print renderer config gateway JSON.")
    parser.add_argument("--sample-width", type=int, default=None)
    parser.add_argument("--sample-map-projection", default="")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    sample: dict[str, Any] = {}
    if args.sample_width is not None:
        sample["width"] = args.sample_width
    if args.sample_map_projection:
        sample["map_projection"] = args.sample_map_projection
    print(json.dumps(renderer_config_gateway_packet("renderer_config_gateway.cli", sample), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
