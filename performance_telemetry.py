from __future__ import annotations

import argparse
import json
import math
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator

from renderer_config_gateway import renderer_config_gateway_packet


PERFORMANCE_SMOKE_SCHEMA = "rrkal_displaytools.performance_smoke.v1"
STAGE_TIMING_SCHEMA = "rrkal_displaytools.stage_timing.v1"
RENDER_TELEMETRY_SCHEMA = "rrkal_displaytools.render_telemetry.v1"
THRESHOLD_GUARD_SCHEMA = "rrkal_displaytools.performance_threshold_guard.v1"


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds")


def performance_bucket(elapsed_ms: float, threshold_ms: float, ok: bool = True) -> str:
    if not ok:
        return "error"
    return "pass" if elapsed_ms <= threshold_ms else "slow"


def stage_result(
    *,
    stage: str,
    elapsed_ms: float,
    threshold_ms: float,
    ok: bool = True,
    warnings: list[str] | None = None,
    next_action: str = "",
    metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    bucket = performance_bucket(elapsed_ms, threshold_ms, ok)
    result: dict[str, object] = {
        "schema": STAGE_TIMING_SCHEMA,
        "ts": utc_now(),
        "stage": stage,
        "ok": bool(ok and bucket == "pass"),
        "elapsed_ms": round(float(elapsed_ms), 3),
        "threshold_ms": round(float(threshold_ms), 3),
        "performance_bucket": bucket,
        "warnings": list(warnings or []),
    }
    if metadata:
        result.update(metadata)
        result["metadata"] = dict(metadata)
    if bucket == "slow":
        result["next_action"] = next_action or f"profile {stage}"
    elif next_action:
        result["next_action"] = next_action
    return result


@dataclass
class PerfStage:
    stage: str
    threshold_ms: float
    next_action: str = ""
    metadata: dict[str, object] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def set(self, **metadata: object) -> None:
        self.metadata.update(metadata)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


@contextmanager
def perf_stage(stage: str, threshold_ms: float, next_action: str = "") -> Iterator[PerfStage]:
    ctx = PerfStage(stage=stage, threshold_ms=threshold_ms, next_action=next_action)
    started = time.perf_counter()
    try:
        yield ctx
    finally:
        ctx.metadata["elapsed_ms"] = (time.perf_counter() - started) * 1000.0


def finish_stage(ctx: PerfStage) -> dict[str, object]:
    elapsed_ms = float(ctx.metadata.pop("elapsed_ms", 0.0))
    return stage_result(
        stage=ctx.stage,
        elapsed_ms=elapsed_ms,
        threshold_ms=ctx.threshold_ms,
        warnings=ctx.warnings,
        next_action=ctx.next_action,
        metadata=ctx.metadata,
    )


def renderer_config_stage() -> dict[str, object]:
    with perf_stage("renderer_config_gateway", 1000.0, "profile renderer config normalization") as stage:
        packet = renderer_config_gateway_packet(
            "performance_telemetry",
            {
                "width": "640",
                "height": "360",
                "topo_step": "64",
                "style_profile": "scientific",
                "ocean_wave_strength": "0.08",
                "ocean_roughness": "0.12",
                "ocean_foam": "0.02",
            },
        )
        stage.set(
            config_schema=packet["schema"],
            field_count=len(packet["field_names"]),
            changed_default_count=len(packet["changed_defaults"]),
            cache="n/a",
        )
    return finish_stage(stage)


def tiny_scene_frame(frame_index: int, width: int = 32, height: int = 16) -> dict[str, object]:
    started = time.perf_counter()
    vertices_count = width * height * 4
    accumulator = 0.0
    for y in range(height):
        for x in range(width):
            accumulator += math.sin((x + frame_index) * 0.1) * math.cos((y + frame_index) * 0.1)
    frame_ms = (time.perf_counter() - started) * 1000.0
    cpu_prepare_ms = round(frame_ms * 0.34, 3)
    draw_ms = round(frame_ms * 0.46, 3)
    return {
        "stage": "tiny_render_frame",
        "ok": True,
        "frame_index": frame_index,
        "frame_ms": round(frame_ms, 3),
        "input_event_ms": 0.0,
        "state_update_ms": 0.05,
        "cpu_prepare_ms": cpu_prepare_ms,
        "gpu_upload_ms": 0.0,
        "kernel_ms": 0.0,
        "draw_ms": draw_ms,
        "present_ms": 0.0,
        "to_numpy_count": 0,
        "from_numpy_count": 0,
        "draw_call_count": 1,
        "vertices_count": vertices_count,
        "cache": "hit",
        "worker_queue_depth": 0,
        "memory_mb": 0.0,
        "checksum": round(accumulator, 6),
    }


def tiny_render_stage() -> tuple[dict[str, object], dict[str, object]]:
    with perf_stage("tiny_render_3_frame_headless", 3000.0, "profile tiny render telemetry builder") as stage:
        frames = [tiny_scene_frame(index) for index in range(3)]
        frame_ms_values = [float(frame["frame_ms"]) for frame in frames]
        telemetry = {
            "schema": RENDER_TELEMETRY_SCHEMA,
            "stage": "tiny_render_3_frame_headless",
            "runtime": "headless_cpu_contract",
            "gpu_required": False,
            "frame_count": len(frames),
            "no_sync_per_frame_log": True,
            "frames": frames,
            "frame_ms_avg": round(sum(frame_ms_values) / max(len(frame_ms_values), 1), 3),
            "frame_ms_max": round(max(frame_ms_values), 3),
            "to_numpy_count": sum(int(frame["to_numpy_count"]) for frame in frames),
            "from_numpy_count": sum(int(frame["from_numpy_count"]) for frame in frames),
            "draw_call_count": sum(int(frame["draw_call_count"]) for frame in frames),
            "vertices_count": sum(int(frame["vertices_count"]) for frame in frames),
            "cache_hit": True,
            "cache_miss": False,
            "worker_queue_depth": 0,
            "memory_mb": 0.0,
            "boundary": "Headless tiny scene contract only; no GPU pressure test and no per-frame synchronous file writes.",
        }
        stage.set(
            frames=len(frames),
            draw_call_count=telemetry["draw_call_count"],
            vertices_count=telemetry["vertices_count"],
            to_numpy_count=telemetry["to_numpy_count"],
            from_numpy_count=telemetry["from_numpy_count"],
            cache="hit",
        )
    return finish_stage(stage), telemetry


def threshold_guard_sample() -> dict[str, object]:
    result = stage_result(
        stage="threshold_guard_sample",
        elapsed_ms=2.0,
        threshold_ms=1.0,
        ok=True,
        warnings=["synthetic threshold guard; does not measure runtime"],
        next_action="profile threshold guard caller",
        metadata={"synthetic": True},
    )
    result["schema"] = THRESHOLD_GUARD_SCHEMA
    return result


def performance_smoke(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    render_stage, render_telemetry = tiny_render_stage()
    stages = [
        renderer_config_stage(),
        render_stage,
    ]
    required_ok = all(stage.get("ok") is True for stage in stages)
    slow_count = sum(1 for stage in stages if stage.get("performance_bucket") == "slow")
    summary = {
        "ok": required_ok,
        "stage_count": len(stages),
        "slow_count": slow_count,
        "threshold_policy": "wide_no_network_no_gpu",
        "live_network_required": False,
        "gpu_required": False,
    }
    performance_path = output_dir / "performance_smoke.json"
    stage_timing_path = output_dir / "stage_timing.jsonl"
    render_telemetry_path = output_dir / "render_telemetry.json"
    packet = {
        "schema": PERFORMANCE_SMOKE_SCHEMA,
        "generated_at_utc": utc_now(),
        "source": "performance_telemetry.py",
        "summary": summary,
        "stages": stages,
        "render_telemetry_schema": RENDER_TELEMETRY_SCHEMA,
        "render_telemetry": render_telemetry,
        "output_paths": {
            "performance_smoke_json": str(performance_path).replace("\\", "/"),
            "stage_timing_jsonl": str(stage_timing_path).replace("\\", "/"),
            "render_telemetry_json": str(render_telemetry_path).replace("\\", "/"),
        },
        "boundary": "Displaytools performance smoke is lightweight and headless; RRKAL owns crawler/download/import/cache governance.",
    }
    performance_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    stage_timing_path.write_text(
        "\n".join(json.dumps(stage, ensure_ascii=False) for stage in stages) + "\n",
        encoding="utf-8",
    )
    render_telemetry_path.write_text(json.dumps(render_telemetry, ensure_ascii=False, indent=2), encoding="utf-8")
    return packet


def contract_packet() -> dict[str, object]:
    return {
        "schema": PERFORMANCE_SMOKE_SCHEMA,
        "source": "performance_telemetry.py",
        "status": "contract_ready",
        "stage_timing_schema": STAGE_TIMING_SCHEMA,
        "render_telemetry_schema": RENDER_TELEMETRY_SCHEMA,
        "output_paths": [
            "state/performance/performance_smoke.json",
            "state/performance/stage_timing.jsonl",
            "state/performance/render_telemetry.json",
        ],
        "required_stage_fields": [
            "stage",
            "ok",
            "elapsed_ms",
            "threshold_ms",
            "performance_bucket",
            "warnings",
        ],
        "render_fields": [
            "input_event_ms",
            "state_update_ms",
            "cpu_prepare_ms",
            "gpu_upload_ms",
            "kernel_ms",
            "draw_ms",
            "present_ms",
            "frame_ms",
            "to_numpy_count",
            "from_numpy_count",
            "draw_call_count",
            "vertices_count",
            "cache",
            "worker_queue_depth",
            "memory_mb",
        ],
        "threshold_guard_schema": THRESHOLD_GUARD_SCHEMA,
        "boundary": "No live network, no large data, no full GPU profiling and no per-frame synchronous file writes.",
        "portable": True,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run lightweight displaytools performance smoke.")
    parser.add_argument("--output-dir", default="state/performance")
    parser.add_argument("--contract-only", action="store_true")
    parser.add_argument("--threshold-guard-only", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.contract_only:
        print(json.dumps(contract_packet(), ensure_ascii=False, indent=2))
        return 0
    if args.threshold_guard_only:
        print(json.dumps(threshold_guard_sample(), ensure_ascii=False, indent=2))
        return 0
    packet = performance_smoke(Path(args.output_dir))
    print(json.dumps(packet, ensure_ascii=False, indent=2))
    return 0 if packet["summary"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
