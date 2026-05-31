"""Render-plan composition helpers.

This module is the first post-07 extraction seam from
``taichi_global_bathymetry.py``. It intentionally keeps the existing
sequential compose behavior and does not enable runtime compose-run merging.
"""

from __future__ import annotations

import json

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


def build_layer_render_plan_runtime_snapshot(
    frame_index: int,
    visible_layers: list[object],
    selected_layer_semantic_target: object,
    dirty_flags: dict[str, object],
    defer_vector_overlays: object,
    composition_steps: list[dict[str, object]],
    *,
    source: str,
) -> dict[str, object]:
    return {
        "schema": "rrkal_displaytools.layer_render_plan_runtime_snapshot.v1",
        "source": source,
        "frame_index": int(frame_index),
        "status": "snapshot_only",
        "runtime_optimization_applied": False,
        "optimization_target": "precompute_layer_state_then_single_render_pass",
        "visible_layers": visible_layers,
        "visible_layer_count": len(visible_layers),
        "selected_layer_semantic_target": selected_layer_semantic_target,
        "dirty_flags": dirty_flags,
        "defer_vector_overlays": defer_vector_overlays,
        "batch_targets": [
            {"id": "globe_material", "source": "TaichiGlobe.render", "dirty_flag": "globe_dirty"},
            {"id": "hydrology_polylines", "source": "lake_overlay_rgba/river_overlay_rgba", "dirty_flag": "hydrology_dirty"},
            {"id": "boundary_and_maritime_lines", "source": "boundary_layer_rgba/boundary_overlay_rgba", "dirty_flag": "boundary_dirty"},
            {"id": "traffic_points", "source": "overlay_rgba/aircraft_overlay_rgba", "dirty_flag": "overlay_dirty"},
            {"id": "research_pins", "source": "pin_overlay_rgba", "dirty_flag": "overlay_dirty"},
            {"id": "vehicle_icons", "source": "vehicle_icon_overlay_rgba", "dirty_flag": "overlay_dirty"},
        ],
        "compose_order": ["globe_rgba", *[str(step.get("id")) for step in composition_steps]],
        "composition_step_count": len(composition_steps),
        "composition_helper": "HybridRenderController.apply_layer_render_plan_composition",
        "single_pass_target": "future_unified_taichi_render_plan",
        "current_path": "centralized_plan_helper_with_existing_overlay_composition",
    }


def build_layer_render_plan_composition_steps(
    boundary_layers_available: bool,
    boundary_layer_ids: list[str],
    boundary_aggregate_blend_mode: object,
) -> list[dict[str, object]]:
    steps: list[dict[str, object]] = [
        {"id": "lakes", "kind": "runtime_blend", "layer_id": "lakes", "overlay_attr": "lake_overlay_rgba"},
        {"id": "rivers", "kind": "runtime_blend", "layer_id": "rivers", "overlay_attr": "river_overlay_rgba"},
    ]
    if boundary_layers_available:
        for layer_id in ("borders", "territorial_sea", "eez", "high_seas"):
            if layer_id in boundary_layer_ids:
                steps.append({"id": layer_id, "kind": "runtime_blend", "layer_id": layer_id, "overlay_source": "boundary_layer_rgba"})
    else:
        steps.append(
            {
                "id": "boundary_aggregate",
                "kind": "alpha_blend",
                "overlay_attr": "boundary_overlay_rgba",
                "blend_mode": boundary_aggregate_blend_mode,
            }
        )
    steps.extend(
        [
            {"id": "ais_overlay", "kind": "alpha_compose", "overlay_attr": "overlay_rgba"},
            {"id": "aircraft", "kind": "runtime_overlay", "layer_id": "aircraft", "overlay_attr": "aircraft_overlay_rgba"},
            {"id": "vehicle_icons", "kind": "runtime_overlay", "layer_id": "vehicle_icons", "overlay_attr": "vehicle_icon_overlay_rgba"},
            {"id": "pins", "kind": "runtime_overlay", "layer_id": "pins", "overlay_attr": "pin_overlay_rgba"},
            {"id": "style_profile_postprocess", "kind": "style_profile_postprocess"},
        ]
    )
    return steps


def build_layer_render_plan_compose_queue_packet(
    input_step_count: int,
    queue: list[dict[str, object]],
    skipped_steps: list[dict[str, object]],
    compose_runs_packet: dict[str, object],
    compose_run_parity_contract: dict[str, object],
    *,
    source: str,
) -> dict[str, object]:
    return {
        "schema": "rrkal_displaytools.layer_render_plan_compose_queue.v1",
        "source": source,
        "status": "runtime_optimized",
        "optimization_applied": True,
        "optimization": "skip_hidden_missing_or_transparent_overlays_before_composition",
        "input_step_count": input_step_count,
        "executable_step_count": len(queue),
        "skipped_step_count": len(skipped_steps),
        "queue": queue,
        "skipped_steps": skipped_steps,
        "compose_runs_schema": "rrkal_displaytools.layer_render_plan_compose_runs.v1",
        "compose_runs": compose_runs_packet.get("runs", []),
        "compose_run_count": compose_runs_packet.get("run_count", 0),
        "compose_merge_candidate_run_count": compose_runs_packet.get("merge_candidate_run_count", 0),
        "compose_run_parity_contract_schema": "rrkal_displaytools.layer_render_plan_compose_run_parity_contract.v1",
        "compose_run_parity_contract": compose_run_parity_contract,
        "next_optimization_target": "collapse executable queue into fewer overlay composition passes",
    }


def build_layer_render_plan_compose_queue_entries(
    composition_steps: list[dict[str, object]],
    step_runtime_states: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    queue: list[dict[str, object]] = []
    skipped_steps: list[dict[str, object]] = []
    for index, step in enumerate(composition_steps):
        state = step_runtime_states[index] if index < len(step_runtime_states) and isinstance(step_runtime_states[index], dict) else {}
        if not isinstance(step, dict):
            skipped_steps.append({"source_order": index, "id": "unknown_step", "reason": "malformed_step"})
            continue
        step_id = str(step.get("id") or step.get("layer_id") or f"step_{index}")
        kind = str(step.get("kind") or "")
        if kind == "style_profile_postprocess":
            queued = dict(step)
            queued["source_order"] = index
            queued["queue_order"] = len(queue)
            queued["compose_queue_reason"] = "postprocess_required"
            queue.append(queued)
            continue
        if state.get("visible") is False:
            skipped_steps.append({"source_order": index, "id": step_id, "kind": kind, "reason": "hidden_layer"})
            continue
        if state.get("overlay_present") is not True:
            skipped_steps.append({"source_order": index, "id": step_id, "kind": kind, "reason": "missing_overlay"})
            continue
        if state.get("overlay_transparent") is True:
            skipped_steps.append({"source_order": index, "id": step_id, "kind": kind, "reason": "transparent_overlay"})
            continue
        queued = dict(step)
        queued["source_order"] = index
        queued["queue_order"] = len(queue)
        queued["compose_queue_reason"] = "executable_overlay"
        queue.append(queued)
    return queue, skipped_steps


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


def build_layer_render_plan_apply_path(
    composition_steps: list[dict[str, object]],
    batch_decisions: list[dict[str, object]],
) -> list[dict[str, object]]:
    decisions_by_id = {
        str(decision.get("id")): decision
        for decision in batch_decisions
        if isinstance(decision, dict) and decision.get("scope") == "layer"
    }
    helper_by_kind = {
        "runtime_blend": "HybridRenderController.compose_runtime_blend",
        "alpha_blend": "alpha_blend_compose",
        "alpha_compose": "alpha_compose",
        "runtime_overlay": "HybridRenderController.compose_runtime_overlay",
        "style_profile_postprocess": "apply_style_profile",
    }
    path: list[dict[str, object]] = []
    for index, step in enumerate(composition_steps):
        if not isinstance(step, dict):
            continue
        step_id = str(step.get("id") or step.get("layer_id") or "")
        kind = str(step.get("kind") or "")
        decision = decisions_by_id.get(step_id, {})
        path.append(
            {
                "order": index,
                "id": step_id,
                "layer_id": step.get("layer_id"),
                "kind": kind,
                "decision": decision.get("decision", "compose_cached_overlay"),
                "apply_helper": helper_by_kind.get(kind, "unknown_apply_helper"),
                "overlay_attr": step.get("overlay_attr"),
                "overlay_source": step.get("overlay_source"),
                "current_runtime_path": "HybridRenderController.apply_layer_render_plan_composition",
                "single_pass_candidate": kind in {"runtime_blend", "alpha_blend", "alpha_compose", "runtime_overlay"},
            }
        )
    return path


def build_layer_render_plan_execution_summary(
    apply_path: list[dict[str, object]],
    batch_decisions: list[dict[str, object]],
    *,
    source: str = "render_core.render_plan.build_layer_render_plan_execution_summary",
) -> dict[str, object]:
    helper_counts: dict[str, int] = {}
    decision_counts: dict[str, int] = {}
    single_pass_candidate_count = 0
    single_pass_blockers: list[str] = []
    for item in apply_path:
        if not isinstance(item, dict):
            continue
        helper = str(item.get("apply_helper") or "unknown_apply_helper")
        helper_counts[helper] = helper_counts.get(helper, 0) + 1
        decision = str(item.get("decision") or "unknown_decision")
        decision_counts[decision] = decision_counts.get(decision, 0) + 1
        if item.get("single_pass_candidate"):
            single_pass_candidate_count += 1
        else:
            single_pass_blockers.append(str(item.get("id") or "unknown_step"))
    batch_decision_counts: dict[str, int] = {}
    for item in batch_decisions:
        if not isinstance(item, dict):
            continue
        decision = str(item.get("decision") or "unknown_decision")
        batch_decision_counts[decision] = batch_decision_counts.get(decision, 0) + 1
    return {
        "schema": "rrkal_displaytools.layer_render_plan_execution_summary.v1",
        "source": source,
        "current_execution_mode": "centralized_overlay_composition",
        "current_apply_helper": "HybridRenderController.apply_layer_render_plan_composition",
        "runtime_optimization_applied": False,
        "apply_path_count": len(apply_path),
        "batch_decision_count": len(batch_decisions),
        "single_pass_candidate_count": single_pass_candidate_count,
        "single_pass_blockers": single_pass_blockers,
        "helper_counts": helper_counts,
        "decision_counts": decision_counts,
        "batch_decision_counts": batch_decision_counts,
        "next_refactor_target": "replace per-step overlay helpers with a unified Taichi render/composite pass",
    }


def build_layer_render_plan_execution_phases(
    apply_path: list[dict[str, object]],
    batch_decisions: list[dict[str, object]],
    execution_summary: dict[str, object],
) -> list[dict[str, object]]:
    def phase_decisions(items: list[dict[str, object]]) -> list[str]:
        values = sorted(
            {
                str(item.get("decision") or "unknown_decision")
                for item in items
                if isinstance(item, dict)
            }
        )
        return values or ["none"]

    batch_items = [
        item
        for item in batch_decisions
        if isinstance(item, dict) and item.get("scope") == "batch"
    ]
    layer_items = [
        item
        for item in batch_decisions
        if isinstance(item, dict) and item.get("scope") == "layer"
    ]
    single_pass_items = [
        item
        for item in apply_path
        if isinstance(item, dict) and item.get("single_pass_candidate")
    ]
    blockers_value = execution_summary.get("single_pass_blockers")
    blockers = blockers_value if isinstance(blockers_value, list) else []
    postprocess_count = sum(
        1
        for item in apply_path
        if isinstance(item, dict) and item.get("kind") == "style_profile_postprocess"
    )
    return [
        {
            "id": "prepare_batches",
            "order": 0,
            "status": "planned_runtime_metadata",
            "item_count": len(batch_items),
            "decisions": phase_decisions(batch_items),
            "current_runtime_path": "precomputed_overlay_buffers",
            "future_single_pass_role": "prepare GPU-ready batch inputs",
        },
        {
            "id": "compose_overlays",
            "order": 1,
            "status": "current_runtime_path",
            "item_count": len(layer_items),
            "decisions": phase_decisions(layer_items),
            "current_runtime_path": "HybridRenderController.apply_layer_render_plan_composition",
            "future_single_pass_role": "replace per-layer overlay composition with one Taichi composite pass",
        },
        {
            "id": "postprocess",
            "order": 2,
            "status": "current_runtime_path",
            "item_count": postprocess_count,
            "decisions": ["postprocess_each_frame"],
            "current_runtime_path": "apply_style_profile",
            "future_single_pass_role": "remain final style pass unless folded into shader",
        },
        {
            "id": "future_single_pass_candidate",
            "order": 3,
            "status": "queued_after_module_decoupling",
            "item_count": len(single_pass_items),
            "decisions": ["single_pass_candidate"],
            "current_runtime_path": "metadata_only",
            "future_single_pass_role": "candidate steps for unified Taichi render/composite pass",
            "blockers": blockers,
        },
    ]


def build_layer_render_plan_phase_timing_contract(
    execution_phases: list[dict[str, object]],
) -> dict[str, object]:
    phase_probe_points = []
    for phase in execution_phases:
        if not isinstance(phase, dict):
            continue
        phase_id = str(phase.get("id") or "unknown_phase")
        phase_probe_points.append(
            {
                "phase_id": phase_id,
                "order": phase.get("order"),
                "probe_key": f"phase_ms.{phase_id}",
                "recommended_start": f"{phase_id}.perf_counter_start",
                "recommended_end": f"{phase_id}.perf_counter_end",
                "metadata_field": f"phase_timing_ms.{phase_id}",
            }
        )
    return {
        "schema": "rrkal_displaytools.layer_render_plan_phase_timing_contract.v1",
        "source": "HybridRenderController.layer_render_plan_phase_timing_contract",
        "status": "probe_contract_ready",
        "runtime_measurements_available": False,
        "timing_unit": "milliseconds",
        "slow_frame_threshold_ms": 33.3,
        "phase_probe_count": len(phase_probe_points),
        "phase_probe_points": phase_probe_points,
        "summary_fields": ["total_ms", "phase_timing_ms", "slowest_phase_id", "frame_index"],
        "next_runtime_step": "wrap phase boundaries with perf_counter and write measured phase_timing_ms into renderer metadata",
    }


def build_layer_render_plan_bottleneck_recommendation(
    phase_timing_runtime: dict[str, object],
) -> dict[str, object]:
    timing = phase_timing_runtime if isinstance(phase_timing_runtime, dict) else {}
    slowest_phase_id = str(timing.get("slowest_phase_id") or "unavailable")
    measured = bool(timing.get("runtime_measurements_available"))
    phase_plan = {
        "prepare_batches": {
            "recommended_next_action": "reuse_static_geometry_batches",
            "target_helper": "HybridRenderController.compile_layer_render_plan",
            "optimization_boundary": "cache renderer-ready hydrology, boundary, traffic and pin batches before composition",
        },
        "compose_overlays": {
            "recommended_next_action": "collapse_overlay_composition_passes",
            "target_helper": "HybridRenderController.apply_layer_render_plan_composition",
            "optimization_boundary": "replace per-layer alpha/runtime helper sequence with fewer unified composite passes",
        },
        "postprocess": {
            "recommended_next_action": "fold_or_defer_style_profile_postprocess",
            "target_helper": "apply_style_profile",
            "optimization_boundary": "avoid repeated full-frame tone/style work when style profile is unchanged",
        },
        "future_single_pass_candidate": {
            "recommended_next_action": "prototype_single_taichi_composite_pass",
            "target_helper": "HybridRenderController.apply_layer_render_plan_composition",
            "optimization_boundary": "consume compiled layer state in one Taichi render/composite path",
        },
    }
    selected = phase_plan.get(
        slowest_phase_id,
        {
            "recommended_next_action": "collect_more_runtime_phase_timing",
            "target_helper": "HybridRenderController.layer_render_plan_phase_timing_runtime_packet",
            "optimization_boundary": "wait for measured phase_timing_ms before changing render behavior",
        },
    )
    return {
        "schema": "rrkal_displaytools.layer_render_plan_bottleneck_recommendation.v1",
        "source": "HybridRenderController.layer_render_plan_bottleneck_recommendation",
        "status": "ready" if measured else "waiting_for_runtime_metadata",
        "basis_schema": timing.get("schema", "rrkal_displaytools.layer_render_plan_phase_timing_runtime.v1"),
        "slowest_phase_id": slowest_phase_id,
        "slowest_phase_ms": timing.get("slowest_phase_ms", 0.0),
        "total_ms": timing.get("total_ms", 0.0),
        "slow_frame": bool(timing.get("slow_frame", False)),
        "recommended_next_action": selected["recommended_next_action"],
        "target_helper": selected["target_helper"],
        "optimization_boundary": selected["optimization_boundary"],
        "runtime_optimization_applied": False,
        "next_commit_scope": "implement the recommended action only after smoke-gated phase timing confirms the bottleneck",
    }


def build_layer_render_plan_phase_timing_runtime_packet(
    phase_timing_ms: dict[str, float],
    frame_index: int,
    total_ms: float,
) -> dict[str, object]:
    measured = {
        str(phase_id): round(float(elapsed_ms), 3)
        for phase_id, elapsed_ms in phase_timing_ms.items()
        if isinstance(phase_id, str)
    }
    slowest_phase_id = None
    slowest_phase_ms = 0.0
    if measured:
        slowest_phase_id = max(measured, key=lambda key: measured[key])
        slowest_phase_ms = measured.get(slowest_phase_id, 0.0)
    threshold_ms = 33.3
    packet = {
        "schema": "rrkal_displaytools.layer_render_plan_phase_timing_runtime.v1",
        "source": "HybridRenderController.layer_render_plan_phase_timing_runtime_packet",
        "status": "measured" if measured else "unavailable",
        "runtime_measurements_available": bool(measured),
        "timing_unit": "milliseconds",
        "total_ms": round(float(total_ms), 3),
        "phase_timing_ms": measured,
        "measured_phase_ids": list(measured.keys()),
        "slowest_phase_id": slowest_phase_id,
        "slowest_phase_ms": round(float(slowest_phase_ms), 3),
        "slow_frame": float(total_ms) > threshold_ms,
        "slow_frame_threshold_ms": threshold_ms,
        "frame_index": int(frame_index),
        "next_optimization_use": "identify whether prepare_batches, compose_overlays or postprocess dominates before replacing the render loop",
    }
    packet["bottleneck_recommendation_schema"] = "rrkal_displaytools.layer_render_plan_bottleneck_recommendation.v1"
    packet["bottleneck_recommendation"] = build_layer_render_plan_bottleneck_recommendation(packet)
    return packet


def _render_plan_count(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def build_layer_render_plan_metadata_summary(plan: dict[str, object]) -> dict[str, object]:
    compiled_plan = plan if isinstance(plan, dict) else {}
    runtime_snapshot = compiled_plan.get("runtime_snapshot")
    if not isinstance(runtime_snapshot, dict):
        runtime_snapshot = {}
    execution_summary = compiled_plan.get("execution_summary")
    if not isinstance(execution_summary, dict):
        execution_summary = {}
    phase_timing_runtime = compiled_plan.get("phase_timing_runtime")
    if not isinstance(phase_timing_runtime, dict):
        phase_timing_runtime = {}
    single_pass_preflight = compiled_plan.get("single_pass_preflight_contract")
    if not isinstance(single_pass_preflight, dict):
        single_pass_preflight = {}
    available = bool(compiled_plan)
    return {
        "schema": "rrkal_displaytools.layer_render_plan_metadata_summary.v1",
        "source": "render_core.render_plan.build_layer_render_plan_metadata_summary",
        "status": "ready" if available else "unavailable",
        "full_plan_field": "layer_render_plan",
        "full_plan_schema": compiled_plan.get("schema") if available else None,
        "cache_status": compiled_plan.get("cache_status", "unavailable") if available else "unavailable",
        "cache_reuse_decision": compiled_plan.get("cache_reuse_decision", "unavailable") if available else "unavailable",
        "frame_index": compiled_plan.get("frame_index"),
        "visible_layer_count": _render_plan_count(runtime_snapshot.get("visible_layer_count")),
        "composition_step_count": _render_plan_count(compiled_plan.get("composition_step_count")),
        "compose_queue_count": _render_plan_count(compiled_plan.get("compose_queue_count")),
        "compose_queue_skipped_count": _render_plan_count(compiled_plan.get("compose_queue_skipped_count")),
        "compose_run_count": _render_plan_count(compiled_plan.get("compose_run_count")),
        "compose_merge_candidate_run_count": _render_plan_count(compiled_plan.get("compose_merge_candidate_run_count")),
        "execution_phase_count": _render_plan_count(compiled_plan.get("execution_phase_count")),
        "single_pass_ready": bool(compiled_plan.get("single_pass_ready", False)) if available else False,
        "single_pass_preflight_status": single_pass_preflight.get("status", "unavailable"),
        "runtime_optimization_applied": bool(compiled_plan.get("runtime_optimization_applied", False)) if available else False,
        "current_execution_mode": execution_summary.get("current_execution_mode", "unavailable"),
        "phase_timing_status": phase_timing_runtime.get("status", "unavailable"),
        "slowest_phase_id": phase_timing_runtime.get("slowest_phase_id"),
        "slow_frame": bool(phase_timing_runtime.get("slow_frame", False)),
        "reuse_policy": compiled_plan.get("reuse_policy", "unavailable") if available else "unavailable",
        "reuse_boundary": compiled_plan.get("reuse_boundary", "unavailable") if available else "unavailable",
        "boundary": "Summary only; full layer_render_plan remains the renderer parity/debugging contract.",
    }


def build_layer_render_plan_single_pass_preflight_contract(
    compose_runs: list[dict[str, object]],
    execution_summary: dict[str, object],
    phase_timing_runtime: dict[str, object],
) -> dict[str, object]:
    merge_candidates = [
        run
        for run in compose_runs
        if isinstance(run, dict) and run.get("merge_safe") is True
    ]
    measured = bool(phase_timing_runtime.get("runtime_measurements_available")) if isinstance(phase_timing_runtime, dict) else False
    single_pass_candidate_count = _render_plan_count(execution_summary.get("single_pass_candidate_count"))
    candidate_count = len(merge_candidates) + single_pass_candidate_count
    if candidate_count <= 0:
        status = "no_candidates"
    elif measured:
        status = "ready_for_parity_smoke"
    else:
        status = "waiting_for_runtime_timing"
    return {
        "schema": "rrkal_displaytools.layer_render_plan_single_pass_preflight_contract.v1",
        "source": "render_core.render_plan.build_layer_render_plan_single_pass_preflight_contract",
        "status": status,
        "runtime_single_pass_enabled": False,
        "runtime_path_unchanged": True,
        "merge_candidate_run_count": len(merge_candidates),
        "candidate_run_ids": [str(run.get("id")) for run in merge_candidates],
        "single_pass_candidate_count": single_pass_candidate_count,
        "runtime_measurements_available": measured,
        "required_before_enable": [
            "compose_run_parity_smoke",
            "phase_timing_runtime_metadata",
            "manual_visual_review",
        ],
        "parity_gate": "zero_diff_against_sequential_compose_queue",
        "timing_gate": "measured_compose_overlays_bottleneck_before_runtime_replacement",
        "review_gate": "manual_qt_or_renderer_output_review_before_default_enable",
        "next_runtime_step": "prototype opt-in single-pass composition only after parity and timing gates pass",
    }


def build_compiled_layer_render_plan_packet(
    cache_key: str,
    invalidation_reasons: list[str],
    invalidation_scope: list[dict[str, object]],
    batch_decisions: list[dict[str, object]],
    apply_path: list[dict[str, object]],
    execution_summary: dict[str, object],
    execution_phases: list[dict[str, object]],
    phase_timing_contract: dict[str, object],
    phase_timing_runtime: dict[str, object],
    bottleneck_recommendation: dict[str, object],
    frame_index: int,
    runtime_snapshot: dict[str, object],
    composition_steps: list[dict[str, object]],
    compose_queue_packet: dict[str, object],
    *,
    source: str,
) -> dict[str, object]:
    single_pass_preflight_contract = build_layer_render_plan_single_pass_preflight_contract(
        compose_queue_packet.get("compose_runs", []),
        execution_summary,
        phase_timing_runtime,
    )
    return {
        "schema": "rrkal_displaytools.compiled_layer_render_plan.v1",
        "source": source,
        "status": "compiled_snapshot",
        "cache_status": "compiled",
        "cache_reuse_decision": "compiled",
        "cache_key": cache_key,
        "cache_invalidation_reasons": invalidation_reasons,
        "cache_invalidation_reason_schema": "rrkal_displaytools.layer_render_plan_cache_invalidation_reasons.v1",
        "cache_invalidation_scope": invalidation_scope,
        "cache_invalidation_scope_schema": "rrkal_displaytools.layer_render_plan_cache_invalidation_scope.v1",
        "batch_decisions": batch_decisions,
        "batch_decision_schema": "rrkal_displaytools.layer_render_plan_batch_decisions.v1",
        "batch_decision_count": len(batch_decisions),
        "apply_path": apply_path,
        "apply_path_schema": "rrkal_displaytools.layer_render_plan_apply_path.v1",
        "apply_path_count": len(apply_path),
        "execution_summary": execution_summary,
        "execution_summary_schema": "rrkal_displaytools.layer_render_plan_execution_summary.v1",
        "execution_phases": execution_phases,
        "execution_phases_schema": "rrkal_displaytools.layer_render_plan_execution_phases.v1",
        "execution_phase_count": len(execution_phases),
        "phase_timing_contract": phase_timing_contract,
        "phase_timing_contract_schema": "rrkal_displaytools.layer_render_plan_phase_timing_contract.v1",
        "phase_timing_runtime": phase_timing_runtime,
        "phase_timing_runtime_schema": "rrkal_displaytools.layer_render_plan_phase_timing_runtime.v1",
        "bottleneck_recommendation": bottleneck_recommendation,
        "bottleneck_recommendation_schema": "rrkal_displaytools.layer_render_plan_bottleneck_recommendation.v1",
        "single_pass_preflight_contract": single_pass_preflight_contract,
        "single_pass_preflight_contract_schema": "rrkal_displaytools.layer_render_plan_single_pass_preflight_contract.v1",
        "reuse_policy": "reuse_when_cache_key_matches_previous_compiled_plan",
        "reuse_status_values": ["compiled", "reused"],
        "runtime_optimization_applied": False,
        "optimization_target": "precompute_layer_state_then_single_render_pass",
        "frame_index": int(frame_index),
        "runtime_snapshot": runtime_snapshot,
        "dirty_flags": runtime_snapshot.get("dirty_flags", {}),
        "batch_targets": runtime_snapshot.get("batch_targets", []),
        "composition_steps": composition_steps,
        "composition_step_count": len(composition_steps),
        "compose_queue": compose_queue_packet.get("queue", []),
        "compose_queue_schema": "rrkal_displaytools.layer_render_plan_compose_queue.v1",
        "compose_queue_packet": compose_queue_packet,
        "compose_queue_count": compose_queue_packet.get("executable_step_count", 0),
        "compose_queue_skipped_count": compose_queue_packet.get("skipped_step_count", 0),
        "compose_runs": compose_queue_packet.get("compose_runs", []),
        "compose_runs_schema": "rrkal_displaytools.layer_render_plan_compose_runs.v1",
        "compose_run_count": compose_queue_packet.get("compose_run_count", 0),
        "compose_merge_candidate_run_count": compose_queue_packet.get("compose_merge_candidate_run_count", 0),
        "compose_run_parity_contract": compose_queue_packet.get("compose_run_parity_contract", {}),
        "compose_run_parity_contract_schema": "rrkal_displaytools.layer_render_plan_compose_run_parity_contract.v1",
        "compose_order": runtime_snapshot.get("compose_order", []),
        "apply_helper": "HybridRenderController.apply_layer_render_plan_composition",
        "single_pass_ready": False,
        "reuse_boundary": "valid_until_dirty_flags_or_camera_change",
    }


def build_reused_compiled_layer_render_plan_packet(
    cached_plan: dict[str, object],
    invalidation_reasons: list[str],
    invalidation_scope: list[dict[str, object]],
    batch_decisions: list[dict[str, object]],
    apply_path: list[dict[str, object]],
    execution_summary: dict[str, object],
    execution_phases: list[dict[str, object]],
    phase_timing_contract: dict[str, object],
    phase_timing_runtime: dict[str, object],
    bottleneck_recommendation: dict[str, object],
    frame_index: int,
    runtime_snapshot: dict[str, object],
    compose_queue_packet: dict[str, object],
) -> dict[str, object]:
    plan = dict(cached_plan)
    plan["cache_status"] = "reused"
    plan["cache_reuse_decision"] = "reused"
    plan["cache_invalidation_reasons"] = invalidation_reasons
    plan["cache_invalidation_scope"] = invalidation_scope
    plan["batch_decisions"] = batch_decisions
    plan["batch_decision_count"] = len(batch_decisions)
    plan["apply_path"] = apply_path
    plan["apply_path_count"] = len(apply_path)
    plan["execution_summary"] = execution_summary
    plan["execution_phases"] = execution_phases
    plan["execution_phases_schema"] = plan.get("execution_phases_schema", "rrkal_displaytools.layer_render_plan_execution_phases.v1")
    plan["execution_phase_count"] = len(execution_phases)
    plan["phase_timing_contract"] = phase_timing_contract
    plan["phase_timing_contract_schema"] = "rrkal_displaytools.layer_render_plan_phase_timing_contract.v1"
    plan["phase_timing_runtime"] = phase_timing_runtime
    plan["phase_timing_runtime_schema"] = "rrkal_displaytools.layer_render_plan_phase_timing_runtime.v1"
    plan["bottleneck_recommendation"] = bottleneck_recommendation
    plan["bottleneck_recommendation_schema"] = "rrkal_displaytools.layer_render_plan_bottleneck_recommendation.v1"
    plan["single_pass_preflight_contract"] = build_layer_render_plan_single_pass_preflight_contract(
        compose_queue_packet.get("compose_runs", []),
        execution_summary,
        phase_timing_runtime,
    )
    plan["single_pass_preflight_contract_schema"] = "rrkal_displaytools.layer_render_plan_single_pass_preflight_contract.v1"
    plan["reuse_policy"] = "reuse_when_cache_key_matches_previous_compiled_plan"
    plan["reuse_boundary"] = plan.get("reuse_boundary", "valid_until_dirty_flags_or_camera_change")
    plan["frame_index"] = int(frame_index)
    plan["runtime_snapshot"] = runtime_snapshot
    plan["dirty_flags"] = runtime_snapshot.get("dirty_flags", {})
    plan["compose_queue"] = compose_queue_packet.get("queue", [])
    plan["compose_queue_schema"] = "rrkal_displaytools.layer_render_plan_compose_queue.v1"
    plan["compose_queue_packet"] = compose_queue_packet
    plan["compose_queue_count"] = compose_queue_packet.get("executable_step_count", 0)
    plan["compose_queue_skipped_count"] = compose_queue_packet.get("skipped_step_count", 0)
    plan["compose_runs"] = compose_queue_packet.get("compose_runs", [])
    plan["compose_runs_schema"] = "rrkal_displaytools.layer_render_plan_compose_runs.v1"
    plan["compose_run_count"] = compose_queue_packet.get("compose_run_count", 0)
    plan["compose_merge_candidate_run_count"] = compose_queue_packet.get("compose_merge_candidate_run_count", 0)
    plan["compose_run_parity_contract"] = compose_queue_packet.get("compose_run_parity_contract", {})
    plan["compose_run_parity_contract_schema"] = "rrkal_displaytools.layer_render_plan_compose_run_parity_contract.v1"
    return plan


def build_layer_render_plan_cache_key(
    runtime_snapshot: dict[str, object],
    composition_steps: list[dict[str, object]],
    style_profile: object,
    boundary_layer_ids: list[str],
    layer_opacity: dict[str, object],
    layer_blend: dict[str, object],
) -> str:
    visible_layers = runtime_snapshot.get("visible_layers") if isinstance(runtime_snapshot.get("visible_layers"), list) else []
    visible_layer_ids = [str(layer_id) for layer_id in visible_layers]
    payload = {
        "style_profile": style_profile,
        "visible_layers": visible_layer_ids,
        "selected_layer_semantic_target": runtime_snapshot.get("selected_layer_semantic_target"),
        "dirty_flags": runtime_snapshot.get("dirty_flags"),
        "defer_vector_overlays": runtime_snapshot.get("defer_vector_overlays"),
        "composition_ids": [str(step.get("id")) for step in composition_steps],
        "boundary_layer_ids": sorted(str(layer_id) for layer_id in boundary_layer_ids),
        "layer_opacity": {str(layer_id): layer_opacity.get(layer_id) for layer_id in visible_layer_ids},
        "layer_blend": {str(layer_id): layer_blend.get(layer_id) for layer_id in visible_layer_ids},
    }
    return json.dumps(payload, sort_keys=True, default=str)


def build_layer_render_plan_cache_invalidation_reasons(
    runtime_snapshot: dict[str, object],
    cache_key: str,
    cached_plan: object,
    previous_key: object,
) -> list[str]:
    reasons: list[str] = []
    dirty_flags = runtime_snapshot.get("dirty_flags") if isinstance(runtime_snapshot.get("dirty_flags"), dict) else {}
    for flag, value in dirty_flags.items():
        if value is True:
            reasons.append(f"dirty_flag:{flag}")
    if not isinstance(cached_plan, dict):
        reasons.append("no_previous_compiled_plan")
    elif previous_key != cache_key:
        reasons.append("cache_key_changed")
    if not reasons:
        reasons.append("cache_key_match")
    return reasons


def build_layer_render_plan_cache_invalidation_scope(
    runtime_snapshot: dict[str, object],
    invalidation_reasons: list[str],
) -> list[dict[str, object]]:
    dirty_flags = runtime_snapshot.get("dirty_flags") if isinstance(runtime_snapshot.get("dirty_flags"), dict) else {}
    batch_targets = runtime_snapshot.get("batch_targets") if isinstance(runtime_snapshot.get("batch_targets"), list) else []
    scopes: list[dict[str, object]] = []
    for batch in batch_targets:
        if not isinstance(batch, dict):
            continue
        dirty_flag = str(batch.get("dirty_flag") or "")
        if dirty_flag and dirty_flags.get(dirty_flag) is True:
            scopes.append(
                {
                    "scope": "batch",
                    "id": str(batch.get("id") or dirty_flag),
                    "dirty_flag": dirty_flag,
                    "source": batch.get("source"),
                }
            )
    for global_flag in ("force", "changed"):
        if dirty_flags.get(global_flag) is True:
            scopes.append({"scope": "global", "id": global_flag, "dirty_flag": global_flag})
    if "cache_key_changed" in invalidation_reasons or "no_previous_compiled_plan" in invalidation_reasons:
        scopes.append({"scope": "plan", "id": "compiled_layer_render_plan", "dirty_flag": "cache_key"})
    if not scopes and "cache_key_match" in invalidation_reasons:
        scopes.append({"scope": "reuse", "id": "compiled_layer_render_plan", "dirty_flag": None})
    return scopes


def build_layer_render_plan_batch_decisions(
    runtime_snapshot: dict[str, object],
    composition_steps: list[dict[str, object]],
    invalidation_scope: list[dict[str, object]],
) -> list[dict[str, object]]:
    dirty_flags = runtime_snapshot.get("dirty_flags") if isinstance(runtime_snapshot.get("dirty_flags"), dict) else {}
    batch_targets = runtime_snapshot.get("batch_targets") if isinstance(runtime_snapshot.get("batch_targets"), list) else []
    global_dirty = bool(dirty_flags.get("force") or dirty_flags.get("changed"))
    dirty_scope_ids = {
        str(scope.get("id"))
        for scope in invalidation_scope
        if isinstance(scope, dict) and scope.get("scope") in {"batch", "global", "plan"}
    }
    decisions: list[dict[str, object]] = []
    for batch in batch_targets:
        if not isinstance(batch, dict):
            continue
        batch_id = str(batch.get("id") or "")
        dirty_flag = str(batch.get("dirty_flag") or "")
        dirty = global_dirty or bool(dirty_flag and dirty_flags.get(dirty_flag)) or batch_id in dirty_scope_ids
        decisions.append(
            {
                "scope": "batch",
                "id": batch_id,
                "dirty_flag": dirty_flag,
                "source": batch.get("source"),
                "decision": "rebuild_batch" if dirty else "reuse_batch",
                "reason": f"dirty_flag:{dirty_flag}" if dirty and dirty_flag else ("global_dirty" if dirty else "cache_key_match"),
            }
        )

    layer_dirty_map = {
        "lakes": "hydrology_dirty",
        "rivers": "hydrology_dirty",
        "borders": "boundary_dirty",
        "territorial_sea": "boundary_dirty",
        "eez": "boundary_dirty",
        "high_seas": "boundary_dirty",
        "boundary_aggregate": "boundary_dirty",
        "ais_overlay": "overlay_dirty",
        "aircraft": "overlay_dirty",
        "vehicle_icons": "overlay_dirty",
        "pins": "overlay_dirty",
        "style_profile_postprocess": "globe_dirty",
    }
    for step in composition_steps:
        if not isinstance(step, dict):
            continue
        step_id = str(step.get("id") or step.get("layer_id") or "")
        dirty_flag = layer_dirty_map.get(step_id)
        dirty = global_dirty or bool(dirty_flag and dirty_flags.get(dirty_flag))
        kind = str(step.get("kind") or "")
        if kind == "style_profile_postprocess":
            decision = "postprocess_each_frame"
        else:
            decision = "compose_dirty_overlay" if dirty else "compose_cached_overlay"
        decisions.append(
            {
                "scope": "layer",
                "id": step_id,
                "layer_id": step.get("layer_id"),
                "kind": kind,
                "dirty_flag": dirty_flag,
                "decision": decision,
                "reason": f"dirty_flag:{dirty_flag}" if dirty and dirty_flag else ("global_dirty" if dirty else "cache_key_match"),
            }
        )
    return decisions
