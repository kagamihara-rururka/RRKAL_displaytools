"""Export all display runtime boundary contracts.

The exporter is headless and imports display_runtime contract modules only.
It does not import Qt, Taichi or chart backends.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from display_runtime import (  # noqa: E402
    build_earth_canvas_runtime_contract_packet,
    build_time_series_canvas_runtime_contract_packet,
)


def main() -> None:
    contracts = [
        build_earth_canvas_runtime_contract_packet(),
        build_time_series_canvas_runtime_contract_packet(),
    ]
    packet = {
        "schema": "rrkal_displaytools.display_runtime_contracts.v1",
        "source": "scripts.export_display_runtime_contracts",
        "status": "contract_ready",
        "contract_count": len(contracts),
        "canvas_types": [contract["boundary"]["canvas_type"] for contract in contracts],
        "runtime_render_invoked": any(contract["runtime_render_invoked"] for contract in contracts),
        "imports_renderer_packages": any(contract["imports_renderer_packages"] for contract in contracts),
        "contracts": contracts,
        "boundary": "Runtime contracts define landing zones only; concrete renderer execution remains out of scope.",
    }
    print(json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
