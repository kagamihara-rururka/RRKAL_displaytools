"""EarthCanvas runtime boundary contract.

This module is the future landing zone for the existing globe runtime wrapper.
It intentionally does not import Taichi, Qt or concrete renderer packages yet.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from display_core import CANVAS_EARTH, LAYER_GEO


@dataclass(frozen=True)
class EarthCanvasRuntimeBoundary:
    canvas_type: str = CANVAS_EARTH
    current_runtime_owner: str = "taichi_global_bathymetry.py::HybridRenderController"
    future_module: str = "display_runtime.earth_canvas"
    supported_layer_type: str = LAYER_GEO
    runtime_status: str = "contract_only_no_runtime_move"

    def to_packet(self) -> dict[str, Any]:
        return {
            "canvas_type": self.canvas_type,
            "current_runtime_owner": self.current_runtime_owner,
            "future_module": self.future_module,
            "supported_layer_type": self.supported_layer_type,
            "runtime_status": self.runtime_status,
        }


def build_earth_canvas_runtime_contract_packet() -> dict[str, Any]:
    boundary = EarthCanvasRuntimeBoundary()
    return {
        "schema": "rrkal_displaytools.earth_canvas_runtime_contract.v1",
        "source": "display_runtime.earth_canvas.build_earth_canvas_runtime_contract_packet",
        "status": boundary.runtime_status,
        "boundary": boundary.to_packet(),
        "runtime_render_invoked": False,
        "imports_renderer_packages": False,
        "first_safe_move": "Wrap current HybridRenderController globe runtime behind EarthCanvas after render-plan parity evidence is stronger.",
        "do_not_move_yet": [
            "Taichi kernels",
            "ndarray composition application",
            "Qt widgets",
            "RRKAL data/cache governance",
        ],
    }
