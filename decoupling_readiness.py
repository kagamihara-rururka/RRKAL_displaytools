"""Decoupling readiness packet for RRKAL_displaytools.

This module is intentionally standalone. It records the next extraction
sequence without moving code out of the current renderer monolith yet.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime

from controlled_interception import controlled_interception_policy_packet
from performance_telemetry import contract_packet as performance_smoke_contract_packet


SCHEMA = "rrkal_displaytools.decoupling_readiness.v1"


def decoupling_readiness_packet(phase: str = "pre_07_ui_closure") -> dict[str, object]:
    """Return the renderer decoupling queue and boundary guardrails."""

    phase = phase if phase in {"pre_07_ui_closure", "post_07_decoupling"} else "pre_07_ui_closure"
    performance_contract = performance_smoke_contract_packet()
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "phase": phase,
        "operation_schedule": {
            "timezone": "Asia/Taipei",
            "ui_contract_handoff_until": "2026-05-31T07:00:00+08:00",
            "decoupling_not_before": "2026-05-31T07:00:00+08:00",
            "pre_decoupling_gate_command": "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/pre_decoupling_gate.ps1",
            "contract_only_gate_command": "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/pre_decoupling_gate.ps1 -ContractOnly",
            "note": "Before the gate, continue UI/contract/handoff closure only; after the gate, start with render_plan_compose extraction.",
        },
        "controlled_interception_policy": controlled_interception_policy_packet("decoupling_readiness"),
        "observability_baseline": {
            "schema": "rrkal_displaytools.decoupling_observability_baseline.v1",
            "status": "contract_ready",
            "performance_smoke_schema": performance_contract["schema"],
            "stage_timing_schema": performance_contract["stage_timing_schema"],
            "render_telemetry_schema": performance_contract["render_telemetry_schema"],
            "output_paths": performance_contract["output_paths"],
            "pre_move_command": "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/performance_smoke.ps1",
            "contract_only_command": "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/performance_smoke.ps1 -ContractOnly",
            "gate_reason": "Before render_plan_compose extraction, record a lightweight displaytools timing baseline so regressions can be localized by stage.",
            "boundary": "Displaytools observability only; RRKAL crawler/download/import/cache telemetry stays in RRKAL.",
        },
        "phase_policy": {
            "pre_07_ui_closure": {
                "allowed": [
                    "Qt UI affordances",
                    "renderer capability contracts",
                    "launch/reviewer packet fields",
                    "small smoke-gated handoff docs",
                ],
                "blocked": [
                    "large renderer file moves",
                    "render loop rewrites",
                    "RRKAL provider/cache governance",
                ],
            },
            "post_07_decoupling": {
                "allowed": [
                    "extract pure packet builders",
                    "extract render-plan composition",
                    "extract ocean material scalar mapping",
                    "extract style profile routing",
                ],
                "blocked": [
                    "dataset discovery/download/import",
                    "cache lifecycle ownership",
                    "unvalidated GUI framework mixing",
                ],
            },
        },
        "first_extraction_order": [
            {
                "id": "render_plan_compose",
                "target_module": "render_core/render_plan.py",
                "reason": "Needed before optimizing many layer passes into one planned render pass.",
                "keep_contracts": [
                    "layer_render_plan_performance",
                    "compose_performance_summary",
                    "render_compose_parity",
                    "performance_smoke_telemetry",
                    "stage_timing_jsonl",
                ],
                "requires_observability_baseline": True,
                "risk": "medium",
            },
            {
                "id": "ocean_material",
                "target_module": "render_core/ocean_material.py",
                "reason": "Ocean 3D scalar controls are now stable enough to separate from Qt wiring.",
                "keep_contracts": [
                    "ocean_material_control_port",
                    "timeline_ocean_material_interpolation",
                    "taichi_ocean_3d_control_panel",
                ],
                "risk": "low",
            },
            {
                "id": "layer_runtime_bridge",
                "target_module": "overlays/layer_runtime.py",
                "reason": "Layer visibility, opacity, blend and pick ack paths need one bridge before renderer batching.",
                "keep_contracts": [
                    "layer_runtime_state",
                    "layer_runtime_ack",
                    "layer_capability_matrix",
                ],
                "risk": "medium",
            },
            {
                "id": "style_profile_routes",
                "target_module": "styles/profile_routes.py",
                "reason": "Parchment and tactical renderer routes should stop living inside UI packet code.",
                "keep_contracts": [
                    "style_renderer_entries",
                    "style_profile_renderer_routes",
                    "profile_launch_readiness",
                ],
                "risk": "low",
            },
            {
                "id": "diagnostics_packets",
                "target_module": "diagnostics/packets.py",
                "reason": "Large diagnostic packet builders can move after render and UI state contracts stabilize.",
                "keep_contracts": [
                    "closed_loop_status",
                    "reviewer_packet_export",
                    "goal_closure_scorecard",
                ],
                "risk": "medium",
            },
        ],
        "rrkal_boundary": {
            "displaytools_owns": [
                "visualization contracts",
                "renderer profiles",
                "Qt control surfaces",
                "render-plan execution and diagnostics",
            ],
            "rrkal_owns": [
                "provider discovery",
                "download/import workflows",
                "asset cache governance",
                "authoritative data registry",
            ],
            "rule": "Do not move discovery/download/import/cache lifecycle into displaytools during decoupling.",
        },
        "smoke_gate_before_each_move": [
            "scripts/smoke.ps1",
            "scripts/performance_smoke.ps1",
            "git diff --check",
            "docs/DEVELOPMENT_LOG.zh-TW.md smoke result",
        ],
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Print RRKAL_displaytools decoupling readiness JSON.")
    parser.add_argument(
        "--phase",
        choices=("pre_07_ui_closure", "post_07_decoupling"),
        default="pre_07_ui_closure",
        help="Phase policy to report.",
    )
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    print(json.dumps(decoupling_readiness_packet(args.phase), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
