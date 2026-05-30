# Decoupling Runbook

## Scope

This runbook starts only after `2026-05-31T07:00:00+08:00`.

Before that gate, keep work limited to Qt UI, launch/reviewer packets, handoff docs, and smoke-gated contracts.

## Required preflight

Run from `L:\RRKAL_displaytools`:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\pre_decoupling_gate.ps1
```

The gate must report:

- `schema=rrkal_displaytools.pre_decoupling_gate.v1`
- `ready=true`
- `first_extraction_id=render_plan_compose`
- `requires_clean_worktree=true`
- `observability_baseline_schema=rrkal_displaytools.decoupling_observability_baseline.v1`
- `performance_smoke_schema=rrkal_displaytools.performance_smoke.v1`
- `decoupling_boundary_inspector_command=scripts/inspect_decoupling_boundaries.ps1`
- `render_plan_compose_work_order_command=scripts/inspect_render_plan_compose_work_order.ps1`

For a read-only boundary review before code movement, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_decoupling_boundaries.ps1
```

This must report `first_extraction_id=render_plan_compose`, `first_extraction_target=render_core/render_plan.py`, `tk_primary_ui_allowed=false`, and the RRKAL data/cache governance boundary.

For the first extraction work order, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_render_plan_compose_work_order.ps1
```

This must report the target module, source helpers, keep-contracts, smoke gates, and the non-goal that runtime compose-run merging stays disabled until zero-diff parity artifacts exist.

The pre-decoupling gate treats this work order as required-before-move evidence. If it fails, do not start extraction.

For the one-command no-GUI readiness bundle, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\export_pre_decoupling_readiness_bundle.ps1
```

This bundles the inspector index, review packet, gate contract, boundary inspection, render-plan work order and snapshot export contract without writing state.

For a compact pass/fail check before the formal gate, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_pre_decoupling_readiness.ps1
```

This must report `status=pass`, `ready_for_07_gate_review=true`, and `first_extraction_target=render_core/render_plan.py`.

## First extraction order

1. `render_plan_compose` -> `render_core/render_plan.py`
2. `ocean_material` -> `render_core/ocean_material.py`
3. `layer_runtime_bridge` -> `overlays/layer_runtime.py`
4. `style_profile_routes` -> `styles/profile_routes.py`
5. `diagnostics_packets` -> `diagnostics/packets.py`

## Boundary rules

- Do not move RRKAL provider discovery into displaytools.
- Do not move download/import/cache lifecycle into displaytools.
- Do not change the primary UI stack away from Qt.
- Keep each extraction smoke-gated, committed, pushed, and documented before starting the next extraction.

## First code-move target

Start with pure render-plan helpers only. Preserve these fields while moving code:

- `layer_render_plan_performance`
- `compose_performance_summary`
- `render_compose_parity`
- `performance_smoke_telemetry`
- `state/performance/stage_timing.jsonl`
- `decoupling_readiness`
- `decoupling_boundary_inspection`
- `render_plan_compose_work_order`
- `reviewer_packet_export`

If a move requires runtime visual validation, stop after the smoke-gated commit and ask for local Qt/Taichi visual review.
