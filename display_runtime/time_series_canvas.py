"""TimeSeriesCanvas runtime boundary contract.

This module is the future landing zone for the first non-Earth canvas runtime.
It intentionally does not import charting packages yet.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from display_core import CANVAS_TIME_SERIES, LAYER_TIME_SERIES


@dataclass(frozen=True)
class TimeSeriesCanvasRuntimeBoundary:
    canvas_type: str = CANVAS_TIME_SERIES
    current_runtime_owner: str = "contract_only_no_runtime_owner"
    future_module: str = "display_runtime.time_series_canvas"
    supported_layer_type: str = LAYER_TIME_SERIES
    runtime_status: str = "contract_only_no_chart_backend"

    def to_packet(self) -> dict[str, Any]:
        return {
            "canvas_type": self.canvas_type,
            "current_runtime_owner": self.current_runtime_owner,
            "future_module": self.future_module,
            "supported_layer_type": self.supported_layer_type,
            "runtime_status": self.runtime_status,
        }


def build_time_series_canvas_runtime_contract_packet() -> dict[str, Any]:
    boundary = TimeSeriesCanvasRuntimeBoundary()
    return {
        "schema": "rrkal_displaytools.time_series_canvas_runtime_contract.v1",
        "source": "display_runtime.time_series_canvas.build_time_series_canvas_runtime_contract_packet",
        "status": boundary.runtime_status,
        "boundary": boundary.to_packet(),
        "runtime_render_invoked": False,
        "imports_renderer_packages": False,
        "first_safe_move": "Add a minimal chart adapter after ViewModel dispatch and display shell pass/fail gates remain stable.",
        "do_not_move_yet": [
            "Matplotlib backend",
            "Plotly backend",
            "Qt chart widgets",
            "RRKAL data/cache governance",
        ],
    }
