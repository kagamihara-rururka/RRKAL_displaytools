"""Render-plan composition helpers.

This module is the first post-07 extraction seam from
``taichi_global_bathymetry.py``. It intentionally keeps the existing
sequential compose behavior and does not enable runtime compose-run merging.
"""

from __future__ import annotations

import numpy as np


def alpha_compose(background: np.ndarray, overlay: np.ndarray) -> np.ndarray:
    if overlay.shape != background.shape:
        raise ValueError(f"Overlay shape {overlay.shape} does not match background {background.shape}")

    out = background.copy()
    alpha = overlay[..., 3:4].astype(np.float32) / 255.0
    out[..., :3] = (
        overlay[..., :3].astype(np.float32) * alpha
        + out[..., :3].astype(np.float32) * (1.0 - alpha)
    ).astype(np.uint8)
    out[..., 3] = 255
    return out


def alpha_blend_compose(background: np.ndarray, overlay: np.ndarray, blend_mode: str) -> np.ndarray:
    if blend_mode == "Normal":
        return alpha_compose(background, overlay)
    if overlay.shape != background.shape:
        raise ValueError(f"Overlay shape {overlay.shape} does not match background {background.shape}")

    base_rgb = background[..., :3].astype(np.float32) / 255.0
    overlay_rgb = overlay[..., :3].astype(np.float32) / 255.0
    alpha = overlay[..., 3:4].astype(np.float32) / 255.0
    if blend_mode == "Screen":
        blended = 1.0 - (1.0 - base_rgb) * (1.0 - overlay_rgb)
    elif blend_mode == "Multiply":
        blended = base_rgb * overlay_rgb
    elif blend_mode == "Overlay":
        blended = np.where(
            base_rgb <= 0.5,
            2.0 * base_rgb * overlay_rgb,
            1.0 - 2.0 * (1.0 - base_rgb) * (1.0 - overlay_rgb),
        )
    elif blend_mode == "Soft Light":
        blended = (1.0 - 2.0 * overlay_rgb) * base_rgb * base_rgb + 2.0 * overlay_rgb * base_rgb
    else:
        return alpha_compose(background, overlay)

    out = background.copy()
    out[..., :3] = np.clip((blended * alpha + base_rgb * (1.0 - alpha)) * 255.0, 0.0, 255.0).astype(np.uint8)
    out[..., 3] = 255
    return out


def alpha_compose_transparent(background: np.ndarray, overlay: np.ndarray) -> np.ndarray:
    if overlay.shape != background.shape:
        raise ValueError(f"Overlay shape {overlay.shape} does not match background {background.shape}")
    bg = background.astype(np.float32) / 255.0
    fg = overlay.astype(np.float32) / 255.0
    fg_a = fg[..., 3:4]
    bg_a = bg[..., 3:4]
    out_a = fg_a + bg_a * (1.0 - fg_a)
    safe_a = np.maximum(out_a, 1e-6)
    out_rgb = (fg[..., :3] * fg_a + bg[..., :3] * bg_a * (1.0 - fg_a)) / safe_a
    out = np.zeros_like(background)
    out[..., :3] = np.clip(out_rgb * 255.0, 0.0, 255.0).astype(np.uint8)
    out[..., 3:4] = np.clip(out_a * 255.0, 0.0, 255.0).astype(np.uint8)
    return out
