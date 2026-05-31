"""Render-core helpers extracted from the Taichi globe prototype."""

from .render_plan import (
    alpha_blend_compose,
    alpha_compose,
    alpha_compose_transparent,
    build_layer_render_plan_bottleneck_recommendation,
    build_layer_render_plan_apply_path,
    build_layer_render_plan_compose_run_parity_contract,
    build_layer_render_plan_compose_runs,
    build_layer_render_plan_execution_summary,
    build_layer_render_plan_execution_phases,
    build_layer_render_plan_phase_timing_contract,
    build_layer_render_plan_phase_timing_runtime_packet,
)

__all__ = [
    "alpha_blend_compose",
    "alpha_compose",
    "alpha_compose_transparent",
    "build_layer_render_plan_bottleneck_recommendation",
    "build_layer_render_plan_apply_path",
    "build_layer_render_plan_compose_run_parity_contract",
    "build_layer_render_plan_compose_runs",
    "build_layer_render_plan_execution_summary",
    "build_layer_render_plan_execution_phases",
    "build_layer_render_plan_phase_timing_contract",
    "build_layer_render_plan_phase_timing_runtime_packet",
]
