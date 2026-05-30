"""Contract-only import shims for headless smoke and handoff checks.

This module demonstrates controlled ``sys.modules`` interception without
claiming that GUI or GPU runtime paths are actually available. Real optional
dependency shims must remain scoped to smoke, handoff, or pre-decoupling
contexts and must be removed after the probe finishes.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib
import json
import sys
import types
from collections.abc import Iterator
from datetime import UTC, datetime


SCHEMA = "rrkal_displaytools.headless_import_shim.v1"
PROBE_MODULE = "rrkal_displaytools_contract_only_probe_module"
DEFAULT_OPTIONAL_TARGETS = [
    "PyQt6",
    "PyQt6.QtCore",
    "PyQt6.QtGui",
    "PyQt6.QtWidgets",
    "vispy",
]


def _new_contract_only_module(name: str) -> types.ModuleType:
    module = types.ModuleType(name)
    module.__dict__.update(
        {
            "__all__": [],
            "__rrkal_displaytools_contract_only_shim__": True,
            "__rrkal_displaytools_runtime_available__": False,
            "__doc__": (
                "Contract-only shim installed by RRKAL_displaytools. "
                "This module proves import boundary behavior only; it is not a GUI/GPU runtime."
            ),
        }
    )
    return module


@contextlib.contextmanager
def headless_import_shim_context(module_names: list[str]) -> Iterator[dict[str, object]]:
    """Temporarily install contract-only modules and restore prior state."""

    prior: dict[str, types.ModuleType | None] = {name: sys.modules.get(name) for name in module_names}
    missing_before = [name for name, module in prior.items() if module is None]
    installed: list[str] = []
    preserved_existing: list[str] = []
    try:
        for name in module_names:
            if sys.modules.get(name) is None:
                sys.modules[name] = _new_contract_only_module(name)
                installed.append(name)
            else:
                preserved_existing.append(name)
        yield {
            "schema": SCHEMA,
            "mode": "active_context",
            "installed": installed,
            "preserved_existing": preserved_existing,
            "missing_before": missing_before,
        }
    finally:
        for name, module in prior.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module


def headless_import_shim_contract_packet(source: str = "compat.headless_import_shims") -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "source": source,
        "generated_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "status": "contract_only_ready",
        "real_dependency_targets": DEFAULT_OPTIONAL_TARGETS,
        "safe_self_test_target": PROBE_MODULE,
        "allowed_contexts": ["smoke", "contract_only", "handoff", "pre_decoupling_gate"],
        "blocked_runtime_claims": [
            "qt_event_loop_available",
            "opengl_context_available",
            "taichi_gpu_runtime_available",
            "visual_render_success",
        ],
        "restore_required": True,
        "boundary": (
            "Import shims can prove contract import paths only. They must not be used to claim "
            "real Qt, OpenGL, Taichi, or visual renderer runtime success."
        ),
        "portable": True,
    }


def run_self_test() -> dict[str, object]:
    before_present = PROBE_MODULE in sys.modules
    with headless_import_shim_context([PROBE_MODULE]) as context_packet:
        imported = importlib.import_module(PROBE_MODULE)
        import_probe_ok = bool(getattr(imported, "__rrkal_displaytools_contract_only_shim__", False))
        runtime_available = bool(getattr(imported, "__rrkal_displaytools_runtime_available__", True))
    after_present = PROBE_MODULE in sys.modules
    return {
        **headless_import_shim_contract_packet("compat.headless_import_shims.self_test"),
        "mode": "self_test",
        "before_present": before_present,
        "context": context_packet,
        "import_probe_ok": import_probe_ok,
        "runtime_available": runtime_available,
        "after_present": after_present,
        "restored": before_present == after_present,
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Print headless import shim contract JSON.")
    parser.add_argument("--contract-only", action="store_true", help="Print the shim contract without installing modules.")
    parser.add_argument("--self-test", action="store_true", help="Run a synthetic sys.modules install/import/restore probe.")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    packet = run_self_test() if args.self_test else headless_import_shim_contract_packet()
    print(json.dumps(packet, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
