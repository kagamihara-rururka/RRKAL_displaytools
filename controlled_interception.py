"""Controlled interception policy for RRKAL_displaytools.

The project can use import/output/runtime interception as an engineering
tool, but only inside bounded smoke, handoff, and decoupling contexts.
Core renderer and Qt runtime paths must stay explicit and reversible.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime


SCHEMA = "rrkal_displaytools.controlled_interception_policy.v1"


def controlled_interception_policy_packet(source: str = "controlled_interception") -> dict[str, object]:
    """Return the allowed interception patterns and guardrails."""

    return {
        "schema": SCHEMA,
        "source": source,
        "generated_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "status": "policy_ready",
        "allowed_patterns": [
            {
                "id": "import_shim",
                "allowed_contexts": ["smoke", "contract_only", "handoff", "pre_decoupling_gate"],
                "purpose": "Replace optional GUI/GPU dependencies with contract-only stand-ins when verifying packets.",
                "required_guard": "must_not_claim_visual_runtime_success",
            },
            {
                "id": "scoped_stdout_capture",
                "allowed_contexts": ["subprocess_smoke", "no_gui_export", "handoff_inspection"],
                "purpose": "Capture noisy subprocess output without permanently patching builtins.print.",
                "required_guard": "must_restore_original_output_path",
            },
            {
                "id": "runtime_ack_hook",
                "allowed_contexts": ["module_extraction_smoke", "render_plan_compose_parity"],
                "purpose": "Simulate renderer ack/state files while extracting pure render-plan modules.",
                "required_guard": "must_record_hooked_runtime_state",
            },
            {
                "id": "packet_normalizer",
                "allowed_contexts": ["launch_packet", "reviewer_packet", "rrkal_manifest_reference"],
                "purpose": "Normalize unstable external fields into stable displaytools contracts.",
                "required_guard": "must_not_take_rrkal_cache_ownership",
            },
        ],
        "blocked_patterns": [
            "permanent_builtins_print_patch",
            "core_renderer_loop_import_forgery",
            "qt_event_loop_monkey_patch",
            "rrkal_provider_download_cache_governance_in_displaytools",
            "fake_visual_runtime_success_in_ci",
        ],
        "first_decoupling_use": {
            "target": "render_plan_compose",
            "allowed_hook": "runtime_ack_hook",
            "reason": "Keep smoke stable while extracting pure render-plan composition before renderer loop rewrites.",
            "must_preserve": [
                "layer_render_plan_performance",
                "compose_performance_summary",
                "render_compose_parity",
            ],
        },
        "ownership_boundary": {
            "displaytools_owns": [
                "contract-only import shims",
                "renderer packet normalization",
                "subprocess output capture for smoke/handoff",
                "runtime ack hooks for module extraction smoke",
            ],
            "rrkal_owns": [
                "provider discovery",
                "download/import workflows",
                "cache lifecycle",
                "authoritative external data normalization before manifest publication",
            ],
        },
        "operating_rule": (
            "Interception is allowed only to isolate unstable external surfaces into stable contracts; "
            "it must be scoped, visible in packets/logs, and removable after the real boundary is stable."
        ),
        "portable": True,
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Print controlled interception policy JSON.")
    parser.add_argument("--source", default="controlled_interception", help="Source label for the packet.")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    print(json.dumps(controlled_interception_policy_packet(args.source), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
