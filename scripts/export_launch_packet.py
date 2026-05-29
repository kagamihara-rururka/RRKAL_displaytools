from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = ROOT / "profiles"
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


def resolve_profile(profile: Path | None, template: str | None) -> Path:
    if profile is not None:
        return profile
    if not template:
        raise ValueError("Either --profile or --template is required")
    template_name = template[:-5] if template.endswith(".json") else template
    return PROFILE_DIR / f"{template_name}.json"


def renderer_args(profile: dict[str, object]) -> list[str]:
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
    ]
    for key, flag in BOOL_FLAGS.items():
        args.append(f"--{flag}" if layers[key] else f"--no-{flag}")
    return args


def profile_display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def launch_packet(profile_path: Path, profile: dict[str, object]) -> dict[str, object]:
    portable_command = ["py", "-3", "taichi_global_bathymetry.py", *renderer_args(profile)]
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
        "closed_loop_status": renderer_closed_loop_status_packet(),
        "portable_command": portable_command,
        "portable_command_line": " ".join(portable_command),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export an RRKAL_displaytools launch packet")
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--template")
    parser.add_argument("--output", type=Path)
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
    packet = launch_packet(profile_path, profile)
    text = json.dumps(packet, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
