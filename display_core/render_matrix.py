"""Minimal DisplayShell / Canvas / Layer / RenderMatrix contracts.

This module is intentionally renderer-package free. It establishes the
contract that displaytools is a display shell with canvas backends, not only
an Earth/globe renderer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

CANVAS_EARTH = "earth"
CANVAS_TIME_SERIES = "time_series"

LAYER_GEO = "geo_layer"
LAYER_TIME_SERIES = "time_series_layer"


@dataclass(frozen=True)
class CanvasDescriptor:
    canvas_type: str
    label: str
    coordinate_model: str
    interaction_model: str
    supported_layer_types: tuple[str, ...]
    runtime_status: str

    def to_packet(self) -> dict[str, Any]:
        return {
            "canvas_type": self.canvas_type,
            "label": self.label,
            "coordinate_model": self.coordinate_model,
            "interaction_model": self.interaction_model,
            "supported_layer_types": list(self.supported_layer_types),
            "runtime_status": self.runtime_status,
        }


@dataclass(frozen=True)
class LayerModel:
    id: str
    type: str
    semantic_type: str
    data_ref: str
    name: str = ""
    visible: bool = True
    order: int = 0
    style: dict[str, Any] = field(default_factory=dict)
    interaction: dict[str, Any] = field(default_factory=dict)
    renderer_hint: str = ""
    export_policy: str = "default"

    def to_packet(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name or self.id,
            "type": self.type,
            "semantic_type": self.semantic_type,
            "data_ref": self.data_ref,
            "visible": bool(self.visible),
            "order": int(self.order),
            "style": dict(self.style),
            "interaction": dict(self.interaction),
            "renderer_hint": self.renderer_hint,
            "export_policy": self.export_policy,
        }


@dataclass(frozen=True)
class ViewModel:
    view_id: str
    canvas_type: str
    layers: tuple[LayerModel, ...]
    renderer_hint: str = ""
    output_format: str = "interactive"

    def to_packet(self) -> dict[str, Any]:
        return {
            "view_id": self.view_id,
            "canvas_type": self.canvas_type,
            "layers": [layer.to_packet() for layer in sorted(self.layers, key=lambda item: item.order)],
            "renderer_hint": self.renderer_hint,
            "output_format": self.output_format,
        }


@dataclass(frozen=True)
class RendererEntry:
    layer_type: str
    canvas_type: str | None
    output_format: str | None
    backend: str | None
    priority: int
    renderer: Any

    def matches(
        self,
        *,
        layer_type: str,
        canvas_type: str | None = None,
        output_format: str | None = None,
        backend: str | None = None,
    ) -> bool:
        return (
            self.layer_type == layer_type
            and (self.canvas_type is None or self.canvas_type == canvas_type)
            and (self.output_format is None or self.output_format == output_format)
            and (self.backend is None or self.backend == backend)
        )

    def to_packet(self) -> dict[str, Any]:
        renderer_name = getattr(self.renderer, "__name__", self.renderer.__class__.__name__)
        return {
            "layer_type": self.layer_type,
            "canvas_type": self.canvas_type,
            "output_format": self.output_format,
            "backend": self.backend,
            "priority": int(self.priority),
            "renderer": renderer_name,
        }


_RENDERERS: list[RendererEntry] = []

_CANVASES: tuple[CanvasDescriptor, ...] = (
    CanvasDescriptor(
        canvas_type=CANVAS_EARTH,
        label="EarthCanvas",
        coordinate_model="globe_lat_lon_altitude",
        interaction_model="camera_orbit_pick_pin_layer_select",
        supported_layer_types=(LAYER_GEO,),
        runtime_status="existing_globe_runtime_primary",
    ),
    CanvasDescriptor(
        canvas_type=CANVAS_TIME_SERIES,
        label="TimeSeriesCanvas",
        coordinate_model="time_x_numeric_y",
        interaction_model="zoom_pan_crosshair_range_select",
        supported_layer_types=(LAYER_TIME_SERIES,),
        runtime_status="phase1_contract_only",
    ),
)


def build_canvas_registry_packet() -> dict[str, Any]:
    return {
        "schema": "rrkal_displaytools.canvas_registry.v1",
        "source": "display_core.render_matrix.build_canvas_registry_packet",
        "status": "phase1_contract_ready",
        "runtime_canvas_switching_enabled": False,
        "canvas_count": len(_CANVASES),
        "canvases": [canvas.to_packet() for canvas in _CANVASES],
        "earth_canvas_boundary": "Existing globe renderer remains primary runtime until extracted behind EarthCanvas.",
        "time_series_canvas_boundary": "TimeSeriesCanvas is contract-only until a minimal renderer adapter is added.",
    }


def build_sample_view_models_packet() -> dict[str, Any]:
    earth_view = ViewModel(
        view_id="rrkal_displaytools_earth_view_sample",
        canvas_type=CANVAS_EARTH,
        renderer_hint="displaytools",
        output_format="interactive",
        layers=(
            LayerModel(
                id="terrain",
                name="Terrain",
                type=LAYER_GEO,
                semantic_type="terrain_dem",
                data_ref="dataset.dem",
                order=10,
                renderer_hint="displaytools",
            ),
            LayerModel(
                id="annotations",
                name="Research annotations",
                type=LAYER_GEO,
                semantic_type="geo_annotation",
                data_ref="dataset.annotations",
                order=20,
                renderer_hint="displaytools",
            ),
        ),
    )
    time_series_view = ViewModel(
        view_id="rrkal_displaytools_time_series_view_sample",
        canvas_type=CANVAS_TIME_SERIES,
        renderer_hint="contract_only",
        output_format="html",
        layers=(
            LayerModel(
                id="series",
                name="Series",
                type=LAYER_TIME_SERIES,
                semantic_type="numeric_series",
                data_ref="dataset.series",
                order=10,
                renderer_hint="future_timeseries_adapter",
            ),
            LayerModel(
                id="events",
                name="Event markers",
                type=LAYER_TIME_SERIES,
                semantic_type="event_marker",
                data_ref="dataset.events",
                order=20,
                renderer_hint="future_timeseries_adapter",
            ),
        ),
    )
    samples = (earth_view, time_series_view)
    return {
        "schema": "rrkal_displaytools.sample_view_models.v1",
        "source": "display_core.render_matrix.build_sample_view_models_packet",
        "status": "phase1_contract_ready",
        "sample_count": len(samples),
        "samples": [sample.to_packet() for sample in samples],
        "canvas_types": [sample.canvas_type for sample in samples],
        "proves": "EarthCanvas and TimeSeriesCanvas share ViewModel = Canvas + Layer Stack + Renderer Hint + Output Format.",
        "runtime_canvas_switching_enabled": False,
    }


def register_renderer(
    *,
    layer_type: str,
    canvas_type: str | None = None,
    output_format: str | None = None,
    backend: str | None = None,
    priority: int = 100,
) -> Callable[[Any], Any]:
    def decorator(renderer: Any) -> Any:
        _RENDERERS.append(
            RendererEntry(
                layer_type=layer_type,
                canvas_type=canvas_type,
                output_format=output_format,
                backend=backend,
                priority=int(priority),
                renderer=renderer,
            )
        )
        _RENDERERS.sort(key=lambda entry: entry.priority)
        return renderer

    return decorator


def lookup_renderers(
    *,
    layer_type: str,
    canvas_type: str | None = None,
    output_format: str | None = None,
    backend: str | None = None,
) -> list[RendererEntry]:
    return [
        entry
        for entry in _RENDERERS
        if entry.matches(
            layer_type=layer_type,
            canvas_type=canvas_type,
            output_format=output_format,
            backend=backend,
        )
    ]


def build_display_shell_capability_packet() -> dict[str, Any]:
    canvas_registry = build_canvas_registry_packet()
    sample_view_models = build_sample_view_models_packet()
    return {
        "schema": "rrkal_displaytools.display_shell_render_matrix.v1",
        "source": "display_core.render_matrix.build_display_shell_capability_packet",
        "status": "phase1_contract_ready",
        "positioning": "DisplayShell + Canvas System + Layer System + Render Matrix",
        "earth_renderer_status": "existing_renderer_remains_primary_runtime",
        "runtime_canvas_switching_enabled": False,
        "canvas_registry_schema": canvas_registry["schema"],
        "canvas_registry": canvas_registry,
        "sample_view_models_schema": sample_view_models["schema"],
        "sample_view_models": sample_view_models,
        "phase1_goal": "extract EarthCanvas boundary and add minimal TimeSeriesCanvas contract before supporting broad chart families",
        "core_imports_renderer_packages": False,
        "canvas_types": [CANVAS_EARTH, CANVAS_TIME_SERIES],
        "layer_types": [LAYER_GEO, LAYER_TIME_SERIES],
        "view_formula": "ViewModel = Canvas + Layer Stack + Renderer Hint + Output Format",
        "render_matrix_dispatch": "decorator_registry_no_if_elif_explosion",
        "registered_renderer_count": len(_RENDERERS),
        "registered_renderers": [entry.to_packet() for entry in _RENDERERS],
        "boundary": "display_core defines contracts only; renderer adapters own concrete plotting/globe packages.",
    }
