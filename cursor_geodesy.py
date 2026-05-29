"""Cursor-to-geodesy helpers for RRKAL_displaytools renderer contracts.

The helper is intentionally dependency-free so smoke tests and renderer capability
discovery can prove the math contract without starting the Qt panel or Taichi GUI.
"""

from __future__ import annotations

import math
from typing import Any

CURSOR_GEODESY_RAYCAST_SCHEMA = "rrkal_displaytools.cursor_geodesy_raycast.v1"


def _rotate_y(vector: tuple[float, float, float], degrees: float) -> tuple[float, float, float]:
    radians = math.radians(degrees)
    cosine = math.cos(radians)
    sine = math.sin(radians)
    x, y, z = vector
    return (x * cosine + z * sine, y, -x * sine + z * cosine)


def _rotate_x(vector: tuple[float, float, float], degrees: float) -> tuple[float, float, float]:
    radians = math.radians(degrees)
    cosine = math.cos(radians)
    sine = math.sin(radians)
    x, y, z = vector
    return (x, y * cosine - z * sine, y * sine + z * cosine)


def normalize_longitude(longitude: float) -> float:
    """Normalize longitude into the [-180, 180) interval."""

    return ((float(longitude) + 180.0) % 360.0) - 180.0


def viewport_sphere_raycast(
    screen_x: float,
    screen_y: float,
    viewport_width: float,
    viewport_height: float,
    *,
    camera_yaw_deg: float = 0.0,
    camera_pitch_deg: float = 0.0,
    globe_radius_px: float | None = None,
    center_x: float | None = None,
    center_y: float | None = None,
) -> dict[str, Any]:
    """Intersect a screen-space cursor with an orthographic globe proxy.

    This is the renderer-facing contract used before full Taichi depth/ray state is
    split out: screen pixels are normalized against the visible globe disc, the
    front hemisphere is intersected, then yaw/pitch are inverted into geodetic
    latitude/longitude. Misses outside the globe return a structured no-hit result.
    """

    width = float(viewport_width)
    height = float(viewport_height)
    if width <= 0.0 or height <= 0.0:
        raise ValueError("viewport_width and viewport_height must be positive")
    cx = width * 0.5 if center_x is None else float(center_x)
    cy = height * 0.5 if center_y is None else float(center_y)
    radius = min(width, height) * 0.5 if globe_radius_px is None else float(globe_radius_px)
    if radius <= 0.0:
        raise ValueError("globe_radius_px must be positive")
    x = (float(screen_x) - cx) / radius
    y = (cy - float(screen_y)) / radius
    radius_sq = x * x + y * y
    if radius_sq > 1.0:
        return {
            "schema": CURSOR_GEODESY_RAYCAST_SCHEMA,
            "hit": False,
            "front_hemisphere": False,
            "latitude": None,
            "longitude": None,
            "normalized_xy": [x, y],
            "reason": "outside_globe_disc",
        }
    z = math.sqrt(max(0.0, 1.0 - radius_sq))
    world = _rotate_y(_rotate_x((x, y, z), -float(camera_pitch_deg)), -float(camera_yaw_deg))
    wx, wy, wz = world
    length = math.sqrt(wx * wx + wy * wy + wz * wz) or 1.0
    wx, wy, wz = wx / length, wy / length, wz / length
    latitude = math.degrees(math.asin(max(-1.0, min(1.0, wy))))
    longitude = normalize_longitude(math.degrees(math.atan2(wx, wz)))
    return {
        "schema": CURSOR_GEODESY_RAYCAST_SCHEMA,
        "hit": True,
        "front_hemisphere": True,
        "latitude": latitude,
        "longitude": longitude,
        "normalized_xy": [x, y],
        "camera_yaw_deg": float(camera_yaw_deg),
        "camera_pitch_deg": float(camera_pitch_deg),
        "method": "orthographic_globe_disc_intersection",
    }
