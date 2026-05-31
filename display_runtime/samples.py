"""Sample runtime request packets built from display_core render plans."""

from __future__ import annotations

from typing import Any

from display_core import build_sample_view_model_render_plans_packet

from .protocols import CanvasRuntimeRenderRequest


def build_sample_canvas_runtime_requests_packet() -> dict[str, Any]:
    render_plan_packet = build_sample_view_model_render_plans_packet()
    requests = []
    for plan in render_plan_packet["plans"]:
        request = CanvasRuntimeRenderRequest(
            canvas_type=plan["canvas_type"],
            view_model={
                "view_id": plan["view_id"],
                "canvas_type": plan["canvas_type"],
                "output_format": plan["output_format"],
            },
            render_plan=plan,
            runtime_options={
                "contract_only": True,
                "runtime_render_invoked": False,
            },
        )
        requests.append(request.to_packet())

    return {
        "schema": "rrkal_displaytools.sample_canvas_runtime_requests.v1",
        "source": "display_runtime.samples.build_sample_canvas_runtime_requests_packet",
        "status": "contract_ready",
        "request_schema": "rrkal_displaytools.canvas_runtime_render_request.v1",
        "render_plan_schema": render_plan_packet["schema"],
        "request_count": len(requests),
        "canvas_types": [request["canvas_type"] for request in requests],
        "requests": requests,
        "runtime_render_invoked": False,
        "boundary": "Samples bridge display_core render-plan metadata to display_runtime request packets without invoking renderer backends.",
    }
