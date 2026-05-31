"""Renderer-package-free runtime adapter protocols."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True)
class CanvasRuntimeRenderRequest:
    canvas_type: str
    view_model: dict[str, Any]
    render_plan: dict[str, Any]
    runtime_options: dict[str, Any] = field(default_factory=dict)

    def to_packet(self) -> dict[str, Any]:
        return {
            "canvas_type": self.canvas_type,
            "view_model": dict(self.view_model),
            "render_plan": dict(self.render_plan),
            "runtime_options": dict(self.runtime_options),
        }


@dataclass(frozen=True)
class CanvasRuntimeRenderResult:
    canvas_type: str
    adapter: str
    status: str
    artifacts: dict[str, Any] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    runtime_render_invoked: bool = False

    def to_packet(self) -> dict[str, Any]:
        return {
            "schema": "rrkal_displaytools.canvas_runtime_render_result.v1",
            "canvas_type": self.canvas_type,
            "adapter": self.adapter,
            "status": self.status,
            "artifacts": dict(self.artifacts),
            "diagnostics": dict(self.diagnostics),
            "runtime_render_invoked": bool(self.runtime_render_invoked),
        }


@runtime_checkable
class CanvasRuntimeAdapter(Protocol):
    def runtime_contract_packet(self) -> dict[str, Any]:
        ...

    def render(self, request: CanvasRuntimeRenderRequest) -> CanvasRuntimeRenderResult:
        ...


def build_contract_only_runtime_result(canvas_type: str, reason: str, adapter: str = "contract_only") -> dict[str, Any]:
    result = CanvasRuntimeRenderResult(
        canvas_type=canvas_type,
        adapter=adapter,
        status=reason,
        diagnostics={"reason": reason},
        runtime_render_invoked=False,
    )
    return result.to_packet()


def build_canvas_runtime_protocol_packet() -> dict[str, Any]:
    return {
        "schema": "rrkal_displaytools.canvas_runtime_protocol.v1",
        "source": "display_runtime.protocols.build_canvas_runtime_protocol_packet",
        "status": "contract_ready",
        "request_schema": "rrkal_displaytools.canvas_runtime_render_request.v1",
        "result_schema": "rrkal_displaytools.canvas_runtime_render_result.v1",
        "adapter_protocol": "CanvasRuntimeAdapter",
        "required_methods": ["runtime_contract_packet", "render"],
        "runtime_render_invoked": False,
        "imports_renderer_packages": False,
        "boundary": "Protocol definitions are renderer-package-free; concrete runtime adapters implement them later.",
    }
