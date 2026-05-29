"""Shared geodetic Pin projection helpers.

This module is intentionally pure Python.  Qt can serialize Pin annotations,
and the renderer can later call the same math before drawing marker overlays.
"""

from __future__ import annotations

import math
from typing import Any


PIN_PROJECTION_CONTRACT_VERSION = "rrkal_displaytools.pin_projection.v1"


def _float_field(pin: dict[str, Any], field: str) -> float:
    value = pin.get(field)
    if isinstance(value, bool):
        raise ValueError(f"pin {field} must be numeric")
    return float(value)


def _pin_label_priority(pin: dict[str, Any]) -> int:
    value = pin.get("label_priority", 50)
    if isinstance(value, bool):
        return 50
    try:
        return max(0, min(100, int(value)))
    except (TypeError, ValueError):
        return 50


def lat_lon_to_world(
    latitude: float,
    longitude: float,
    *,
    flip_longitude: bool = False,
    flip_latitude: bool = False,
    radius: float = 1.0,
) -> tuple[float, float, float]:
    """Convert geodetic latitude/longitude to the renderer's unit sphere."""

    lat = math.radians(-latitude if flip_latitude else latitude)
    lon = math.radians(-longitude if flip_longitude else longitude)
    cos_lat = math.cos(lat)
    return (
        radius * cos_lat * math.sin(lon),
        radius * math.sin(lat),
        radius * cos_lat * math.cos(lon),
    )


def project_pin_to_screen(
    pin: dict[str, Any],
    *,
    yaw: float,
    pitch: float,
    zoom: float,
    width: int,
    height: int,
    flip_longitude: bool = False,
    flip_latitude: bool = False,
    horizon_eps: float = 0.006,
) -> dict[str, Any]:
    """Project one Pin from lat/lon to screen space and classify occlusion.

    The occlusion rule is intentionally conservative:
    - `behind_horizon` means the geodetic anchor is on the back hemisphere.
    - `off_viewport` means the anchor is front-facing but outside the current view.
    - `visible` means it is front-facing and inside the viewport.  A later dense
      renderer pass may still refine this with a depth buffer or terrain mask.
    """

    width = max(1, int(width))
    height = max(1, int(height))
    zoom = max(1e-6, float(zoom))
    latitude = _float_field(pin, "latitude")
    longitude = _float_field(pin, "longitude")
    if not -90.0 <= latitude <= 90.0:
        raise ValueError("pin latitude must be from -90 to 90")
    if not -180.0 <= longitude <= 180.0:
        raise ValueError("pin longitude must be from -180 to 180")

    x, y, z = lat_lon_to_world(
        latitude,
        longitude,
        flip_longitude=flip_longitude,
        flip_latitude=flip_latitude,
    )

    cy = math.cos(-yaw)
    sy = math.sin(-yaw)
    x1 = cy * x + sy * z
    y1 = y
    z1 = -sy * x + cy * z

    cp = math.cos(-pitch)
    sp = math.sin(-pitch)
    x2 = x1
    y2 = cp * y1 - sp * z1
    z2 = sp * y1 + cp * z1

    aspect = width / float(height)
    screen_x = ((x2 / (zoom * aspect) + 1.0) * 0.5) * width
    screen_y = ((y2 / zoom + 1.0) * 0.5) * height
    inside_disc = (x2 * x2 + y2 * y2) <= 1.0
    inside_viewport = 0.0 <= screen_x < width and 0.0 <= screen_y < height

    if z2 <= horizon_eps:
        occlusion = "behind_horizon"
    elif not inside_disc or not inside_viewport:
        occlusion = "off_viewport"
    else:
        occlusion = "visible"

    return {
        "schema": PIN_PROJECTION_CONTRACT_VERSION,
        "id": pin.get("id"),
        "type": pin.get("type"),
        "label": pin.get("label"),
        "label_priority": _pin_label_priority(pin),
        "latitude": latitude,
        "longitude": longitude,
        "anchor": "geodetic_surface",
        "screen_x": float(screen_x),
        "screen_y": float(screen_y),
        "view_z": float(z2),
        "visible": occlusion == "visible",
        "occlusion": occlusion,
        "occlusion_rule": "front hemisphere by view_z > horizon_eps; viewport clipping; depth-buffer refinement pending",
    }


def project_pins_to_screen(
    pins: list[dict[str, Any]],
    *,
    yaw: float,
    pitch: float,
    zoom: float,
    width: int,
    height: int,
    flip_longitude: bool = False,
    flip_latitude: bool = False,
    horizon_eps: float = 0.006,
) -> list[dict[str, Any]]:
    """Project all valid Pins and preserve invalid records as invalid packets."""

    projected: list[dict[str, Any]] = []
    for pin in pins:
        try:
            projected.append(
                project_pin_to_screen(
                    pin,
                    yaw=yaw,
                    pitch=pitch,
                    zoom=zoom,
                    width=width,
                    height=height,
                    flip_longitude=flip_longitude,
                    flip_latitude=flip_latitude,
                    horizon_eps=horizon_eps,
                )
            )
        except (AttributeError, TypeError, ValueError) as exc:
            projected.append(
                {
                    "schema": PIN_PROJECTION_CONTRACT_VERSION,
                    "id": pin.get("id") if isinstance(pin, dict) else None,
                    "visible": False,
                    "occlusion": "invalid",
                    "error": str(exc),
                }
            )
    return projected


def pin_projection_contract_packet() -> dict[str, Any]:
    return {
        "schema": PIN_PROJECTION_CONTRACT_VERSION,
        "anchor": "geodetic_surface",
        "inputs": [
            "pin.id",
            "pin.type",
            "pin.label",
            "pin.latitude",
            "pin.longitude",
            "pin.label_priority",
            "camera.yaw",
            "camera.pitch",
            "camera.zoom",
            "viewport.width",
            "viewport.height",
            "flip_longitude",
            "flip_latitude",
            "horizon_eps",
        ],
        "outputs": [
            "screen_x",
            "screen_y",
            "view_z",
            "visible",
            "occlusion",
            "label_priority",
        ],
        "rotation_rule": "recompute screen position every frame from geodetic anchor and current globe camera",
        "occlusion_rule": "hide behind-horizon anchors when view_z <= horizon_eps; clip off-viewport anchors; refine with renderer depth/globe mask when terrain/depth pass is wired",
        "renderer_overlay_status": "wired_to_pin_overlay_rgba_and_frame_composition",
        "cursor_fill_priority": "renderer_cursor_geodesy_state_then_ui_estimate",
        "cursor_fill_sources": ["renderer_cursor_geodesy_state", "qt_canvas_estimate"],
        "cursor_fill_contract": "Use renderer globe raycast coordinates for researcher Pin placement when available; fallback to Qt preview estimate only without a renderer hit.",
        "horizon_control": "--pin-horizon-eps / PIN_HORIZON_EPS",
        "current_status": "renderer overlay drawing wired; terrain/depth refinement pending",
    }
