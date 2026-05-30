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


def build_layer_render_plan_compose_runs(
    compose_queue: list[dict[str, object]],
    *,
    source: str = "render_core.render_plan.build_layer_render_plan_compose_runs",
) -> dict[str, object]:
    runs: list[dict[str, object]] = []
    current_run: dict[str, object] | None = None
    for step in compose_queue:
        if not isinstance(step, dict):
            continue
        kind = str(step.get("kind") or "unknown")
        step_id = str(step.get("id") or step.get("layer_id") or "unknown_step")
        queue_order = int(step.get("queue_order", len(runs)))
        if kind == "style_profile_postprocess":
            run_kind = "postprocess"
            merge_safe = False
            merge_reason = "full_frame_style_profile_boundary"
        elif kind == "alpha_compose":
            run_kind = "alpha_compose_overlays"
            merge_safe = True
            merge_reason = "adjacent_alpha_compose_overlays_can_be_collapsed_after_visual_parity_check"
        elif kind == "alpha_blend":
            run_kind = "alpha_blend_overlay"
            merge_safe = False
            merge_reason = "blend_mode_specific_overlay_boundary"
        elif kind in {"runtime_blend", "runtime_overlay"}:
            run_kind = "runtime_layer_overlay"
            merge_safe = False
            merge_reason = "preserve_per_layer_visibility_opacity_blend_semantics"
        else:
            run_kind = "unknown_overlay"
            merge_safe = False
            merge_reason = "unknown_runtime_semantics"
        can_extend = (
            current_run is not None
            and current_run.get("run_kind") == run_kind
            and current_run.get("merge_safe") is True
            and merge_safe
        )
        if not can_extend:
            current_run = {
                "id": f"compose_run_{len(runs)}",
                "run_kind": run_kind,
                "merge_safe": merge_safe,
                "merge_reason": merge_reason,
                "start_queue_order": queue_order,
                "end_queue_order": queue_order,
                "step_ids": [],
                "step_count": 0,
                "current_runtime_path": "sequential_compose_queue_execution",
                "next_runtime_path": "merged_overlay_pass" if merge_safe else "preserve_ordered_step_execution",
            }
            runs.append(current_run)
        current_run["end_queue_order"] = queue_order
        step_ids = current_run.get("step_ids")
        if isinstance(step_ids, list):
            step_ids.append(step_id)
        current_run["step_count"] = int(current_run.get("step_count", 0)) + 1
    return {
        "schema": "rrkal_displaytools.layer_render_plan_compose_runs.v1",
        "source": source,
        "status": "ready",
        "run_count": len(runs),
        "merge_candidate_run_count": sum(1 for run in runs if run.get("merge_safe") is True),
        "runs": runs,
        "next_optimization_target": "merge safe adjacent alpha_compose overlays after visual parity smoke is available",
    }


def build_layer_render_plan_compose_run_parity_contract(
    compose_runs: list[dict[str, object]],
    *,
    source: str = "render_core.render_plan.build_layer_render_plan_compose_run_parity_contract",
) -> dict[str, object]:
    merge_candidates = [
        run
        for run in compose_runs
        if isinstance(run, dict) and run.get("merge_safe") is True
    ]
    return {
        "schema": "rrkal_displaytools.layer_render_plan_compose_run_parity_contract.v1",
        "source": source,
        "status": "required_before_runtime_merge" if merge_candidates else "no_merge_candidates",
        "runtime_merge_enabled": False,
        "merge_candidate_run_count": len(merge_candidates),
        "candidate_run_ids": [str(run.get("id")) for run in merge_candidates],
        "compare_method": "sequential_compose_queue_vs_merged_candidate_rgba_diff",
        "required_artifacts": [
            "baseline_sequential_frame_rgba",
            "merged_candidate_frame_rgba",
            "max_abs_diff",
            "changed_pixel_count",
            "renderer_output_metadata",
        ],
        "tolerance": {
            "max_abs_diff": 0,
            "changed_pixel_count": 0,
        },
        "gate": "block_compose_run_merge_until_visual_parity_passes",
        "parity_smoke_schema": "rrkal_displaytools.render_compose_parity_smoke.v1",
        "parity_smoke_script": "scripts\\render_compose_parity_smoke.ps1",
        "parity_smoke_manifest": "state/render_compose_parity_smoke_manifest.json",
        "parity_smoke_default_mode": "contract_only_until_artifacts_then_rgba_diff",
        "parity_smoke_precommit_command": "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\\render_compose_parity_smoke.ps1 -ContractOnly",
        "parity_smoke_validates": ["png_dimensions_match", "max_abs_diff", "changed_pixel_count"],
        "parity_smoke_pass_fields": ["passed", "max_abs_diff", "changed_pixel_count", "diff_status"],
        "recommended_command": "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\\render_compose_parity_smoke.ps1",
        "next_runtime_step": "add an opt-in merged alpha compose path and compare it against the sequential compose queue before enabling it by default",
    }
