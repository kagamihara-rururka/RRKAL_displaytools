"""Export the DisplayShell / Canvas / Render Matrix capability packet.

This script is intentionally headless. It imports display_core contracts only
and does not import Qt, Taichi, Matplotlib, Plotly or concrete render packages.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from display_core import build_display_shell_capability_packet


def main() -> None:
    packet = build_display_shell_capability_packet()
    print(json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
