"""Display shell contracts for canvas/layer/renderer matrix routing."""

from .render_matrix import (
    CANVAS_EARTH,
    CANVAS_TIME_SERIES,
    LAYER_GEO,
    LAYER_TIME_SERIES,
    LayerModel,
    RendererEntry,
    ViewModel,
    build_display_shell_capability_packet,
    lookup_renderers,
    register_renderer,
)

__all__ = [
    "CANVAS_EARTH",
    "CANVAS_TIME_SERIES",
    "LAYER_GEO",
    "LAYER_TIME_SERIES",
    "LayerModel",
    "RendererEntry",
    "ViewModel",
    "build_display_shell_capability_packet",
    "lookup_renderers",
    "register_renderer",
]
