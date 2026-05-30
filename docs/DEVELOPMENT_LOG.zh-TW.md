# Development Log

## 2026-05-31 - Qt extraction dry-run entry

- Added `Inspect: Extraction dry-run` to Qt Replay/contracts.
- The Qt action displays the no-code-move render-plan extraction checklist, planned target files, required gates and stop conditions.
- Smoke now gates the button label and tooltip without launching Qt.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`).

## 2026-05-31 - Render plan extraction dry-run inspector

- Added `scripts/inspect_render_plan_extraction_dry_run.ps1` as a no-code-move checklist for the first post-7 render-plan compose extraction.
- Registered the dry-run inspector in the visual contract inspector index, review packet pre-decoupling commands and smoke gates.
- The dry run exposes planned target files, UIUX gate dependency, stop conditions and non-goals without creating modules or moving renderer code.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`).

## 2026-05-31 - Pre-decoupling snapshot includes UIUX readiness

- Updated `scripts/export_pre_decoupling_snapshot.ps1` so one-file handoff snapshots include `uiux_closure_readiness_check`.
- Smoke now gates the snapshot contract and normal snapshot output for the embedded UIUX pass result.
- This keeps snapshot, readiness bundle, compact check and formal gate aligned before post-7 extraction.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`).

## 2026-05-31 - Pre-decoupling bundle includes UIUX readiness

- Updated `scripts/export_pre_decoupling_readiness_bundle.ps1` to embed the UIUX closure readiness check result.
- Updated `scripts/check_pre_decoupling_readiness.ps1` so compact readiness also verifies the embedded UIUX result is passing.
- Smoke now gates the bundle contract, normal bundle output and compact readiness result for UIUX readiness.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; transient cloud-drive file-access backoff warnings observed, final retry passed).

## 2026-05-31 - Pre-decoupling readiness checks UIUX gate

- Updated `scripts/check_pre_decoupling_readiness.ps1` so the compact readiness check also requires `scripts/check_uiux_closure_readiness.ps1` before code movement.
- Smoke now gates the contract-only check list and normal result flag for UIUX readiness.
- This keeps the readiness bundle, compact check and formal gate aligned before the post-7 renderer extraction phase.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`).

## 2026-05-31 - Pre-decoupling gate requires UIUX readiness

- Updated `scripts/pre_decoupling_gate.ps1` so the formal post-7 gate includes `scripts/check_uiux_closure_readiness.ps1`.
- Contract-only gate output now exposes the UIUX readiness command/schema and required-before-move step.
- Full gate execution will run the UIUX readiness check before boundary/work-order inspectors can pass renderer code movement.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`).

## 2026-05-31 - UIUX readiness includes Qt reviewer path

- Expanded `scripts/check_uiux_closure_readiness.ps1` to include Reviewer route, Capability summary, Qt reviewer path hint, UIUX closure, Workspace map and clone quickstart alignment.
- Smoke now gates the new readiness checks in contract-only mode and normal pass/fail mode.
- This makes the pre-7 UIUX gate cover the latest Qt reviewer workflow before renderer decoupling starts.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; transient cloud-drive file-access backoff warning observed, final retry passed).

## 2026-05-31 - Qt reviewer path hint

- Added a visible reviewer path hint above the Qt Actions section.
- The hint points cloned-machine reviewers through `Clone ready -> Reviewer route -> Capability summary -> UIUX closure -> Workspace map` before renderer launch or visual review.
- Smoke now gates the hint text without launching Qt.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; transient cloud-drive file-access backoff warnings observed, final retry passed).

## 2026-05-31 - Clone quickstart Qt reviewer path

- Updated `docs/QUICKSTART_CLONE.zh-TW.md` with the new Qt reviewer path: Reviewer route, Capability summary, UIUX closure and Workspace map.
- Smoke now gates the quickstart document for those cross-machine Qt review actions.
- This keeps clone-after-setup guidance aligned with the current Qt UI without launching Qt.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; transient cloud-drive file-access backoff warnings observed, final retry passed).

## 2026-05-31 - Qt workspace map inspection button

- Added `Inspect: Workspace map` to the Qt Visual review section.
- The button exposes the Photoshop-like dock workflow map, panel roles, researcher flow, visible non-goals and future `qt_ui/main_window.py` split target.
- Smoke now gates the button label and tooltip without launching Qt.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`).

## 2026-05-31 - Qt UIUX closure inspection button

- Added `Inspect: UIUX closure` to the Qt Visual review section.
- The button exposes `visual_feature_closure_matrix` and `goal_closure_scorecard` in the Qt command review pane so ready/queued items stay visible to researchers.
- Smoke now gates the button label and tooltip without launching Qt.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; transient cloud-drive file-access backoff warning observed, final retry passed).

## 2026-05-31 - Qt reviewer route and capability summary buttons

- Added Replay/contracts buttons in `rrkal_displaytools_qt_panel.py` for `Inspect: Reviewer route` and `Inspect: Capability summary`.
- The buttons expose clone/setup/smoke/handoff/Qt review guidance and current/planned capability reporting directly in the Qt command review pane.
- Smoke now gates the new Qt button labels and tooltips without launching Qt.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; transient cloud-drive file-access backoff warnings observed, final retry passed).

## 2026-05-31 - Capability summary export

- Added `scripts/export_capability_summary.ps1` as a no-GUI source for post-push current/planned capability reporting.
- Registered the summary in the visual contract inspector index, cross-machine review packet and smoke gates.
- The summary separates current Qt/layer/research/Ocean/Timeline/cross-machine/pre-decoupling capabilities from planned dockable panels, render-plan compose decoupling and deferred boundary identity work.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; transient cloud-drive file-access backoff warnings observed, final retry passed).

## 2026-05-31 - Reviewer first-run route inspector

- Added `scripts/inspect_reviewer_first_run_route.ps1` as a no-GUI route for cloned-machine researcher review.
- Registered the route in the visual contract inspector index, cross-machine review packet and smoke gates.
- The route makes setup, smoke, handoff, Qt review, research interaction, Ocean 3D board and visible pending UIUX items explicit without launching Qt.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; transient cloud-drive file-access backoff warning observed, final retry passed).

## 2026-05-31 - Cross-machine review readiness check

- Added `scripts/check_cross_machine_review_readiness.ps1` as a no-GUI pass/fail gate for cloned-machine review.
- Registered the check in the visual contract inspector index, cross-machine review packet and smoke gates.
- The check verifies the public `main` clone target, first-run setup/smoke/handoff commands, portable review packet, UIUX readiness and pre-decoupling contract availability.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; transient cloud-drive file-access backoff warnings observed, final retry passed).

## 2026-05-31 - UIUX closure readiness check

- Added `scripts/check_uiux_closure_readiness.ps1` as a no-GUI pass/fail check over the UIUX inspector set.
- Registered the check in the visual contract inspector index, cross-machine review packet and smoke gates.
- The check verifies Qt-first UI, visible queued items, Timeline pending items, layer presets/shortcuts, research interaction, renderer ports and disabled render-plan runtime merge.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`).

## 2026-05-31 - Timeline UIUX inspector

- Added `scripts/inspect_timeline_uiux.ps1` as a no-GUI reviewer packet for timeline playback readiness, runtime handoff, animation export, layer opacity interpolation and layer visibility/blend discrete hold.
- Registered the inspector in the visual contract inspector index, cross-machine review packet and smoke gates.
- Smoke now verifies renderer timeline playback, GIF/MP4 export capability, layer interpolation support and visible pending items for blend crossfade / visibility fade.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; transient cloud-drive file-access backoff warning observed, final retry passed).

## 2026-05-31 - Layer operator shortcuts inspector

- Added `scripts/inspect_layer_operator_shortcuts.ps1` as a no-GUI reviewer packet for layer keyboard shortcuts, active quick actions, operation groups and copyable provenance.
- Registered the inspector in the visual contract inspector index, cross-machine review packet and smoke gates.
- Smoke now verifies `select_layer`, Boundary emphasis, visibility/undo shortcuts, quick solo action and complete operator groups.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; transient cloud-drive file-access backoff warnings observed, final retry passed).

## 2026-05-31 - UIUX closure status inspector

- Added `scripts/inspect_uiux_closure_status.ps1` as a no-GUI closure board for visual feature readiness, goal scorecard, closed-loop status and visual review readiness.
- Registered the inspector in the visual contract inspector index, cross-machine review packet and smoke gates.
- Smoke now verifies queued items remain visible, performance followup is not reported as done, and brush/mask tools stay excluded.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; transient cloud-drive file-access backoff warnings observed, final retry passed).

## 2026-05-31 - Layer render-plan performance inspector

- Added `scripts/inspect_layer_render_plan_performance.ps1` as a no-GUI reviewer packet for the post-decoupling render-plan performance path.
- Registered the inspector in the visual contract inspector index, cross-machine review packet and smoke gates.
- Smoke now verifies the precompute-then-single-render optimization target, disabled runtime merge, zero-diff parity evidence and sequential-queue failure policy.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; transient cloud-drive file-access backoff warning observed, final retry passed).

## 2026-05-31 - Layer visual presets inspector

- Added `scripts/inspect_layer_visual_presets.ps1` as a no-GUI reviewer packet for layer visual presets, runtime ack feedback, selection tool and selection affordance state.
- Registered the inspector in the visual contract inspector index, cross-machine review packet and smoke gates.
- Smoke now verifies hydrology/boundary/annotation presets, brush/mask exclusion and retained `select_layer` tool mode.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; transient cloud-drive file-access backoff warnings observed, final retry passed).

## 2026-05-31 - Qt UIUX surface inspector

- Added `scripts/inspect_qt_uiux_surface.ps1` as a no-GUI reviewer packet for Qt-first UI surface grouping, replay/contracts, renderer ports, research interaction actions, layer operator groups and clone first-run order.
- Registered the inspector in the visual contract inspector index, cross-machine review packet and smoke gates.
- Smoke now verifies the Qt-first boundary, Tk non-primary boundary, research cursor action, Ocean renderer-port action and layer operator group closure.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`).

## 2026-05-31 - Boundary emphasis inspector controls

- Expanded `scripts/inspect_research_interaction.ps1` to expose Boundary emphasis RGB, contrast, opacity, gamma, breathing and renderer-control mapping values.
- Smoke now gates the Boundary emphasis summary contract and required renderer mappings for color, contrast, alpha, gamma and breathing.
- This keeps the territory/EEZ emphasis UI reviewable without opening Qt and without claiming authoritative legal boundary identity resolution.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; transient cloud-drive file-access backoff warnings observed, final retry passed).

## 2026-05-31 - Research interaction inspector

- Added `scripts/inspect_research_interaction.ps1` as a no-GUI reviewer packet for selected layer state, cursor geodesy, Pin overlay occlusion and Boundary emphasis contracts.
- Registered the inspector in the visual contract inspector index, cross-machine review packet and smoke gates.
- Kept this as a contract/UIUX closure step only; it does not launch Qt/Taichi or change renderer runtime behavior.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; transient cloud-drive file-access backoff warnings observed, final retry passed).

## 2026-05-31 - Pre-decoupling gate time enforcement

- Added a formal `decoupling_not_before=2026-05-31T07:00:00+08:00` time gate to `scripts/pre_decoupling_gate.ps1`.
- `-ContractOnly` still reports gate metadata, but non-contract gate execution now refuses renderer code movement before the not-before timestamp.
- Smoke now gates the not-before timestamp and `time_gate_enforced=true` metadata.
- Smoke: PASS (`powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; transient cloud-drive file-access backoff warnings observed, final retry passed).

## 2026-05-31 - Pre-decoupling readiness check

- Added `scripts/check_pre_decoupling_readiness.ps1` as a compact no-GUI pass/fail check over the readiness bundle.
- The check verifies bundle readiness, first extraction target, boundary readiness, work-order readiness, required-before-move completeness and snapshot work-order inclusion.
- Registered the check in the visual inspector index, review packet, runbook and smoke gates.
- Smoke: PASS via `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; cloud-drive transient file-access retry occurred and recovered.

## 2026-05-31 - Pre-decoupling readiness bundle

- Added `scripts/export_pre_decoupling_readiness_bundle.ps1` as a single no-GUI handoff packet for the pre-7 decoupling state.
- The bundle includes the visual inspector index, visual review packet, pre-decoupling gate contract, boundary inspection, render-plan compose work order and snapshot export contract without writing state.
- Registered the bundle in the visual inspector index, review packet, runbook and smoke gates.
- Smoke: PASS via `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-31 - Render plan compose work order gate

- Added `render_plan_compose_work_order_command` and schema evidence to `scripts/pre_decoupling_gate.ps1`.
- The pre-decoupling gate now requires `scripts/inspect_render_plan_compose_work_order.ps1` before renderer code movement, alongside smoke, performance smoke and boundary inspection.
- Kept this as a pre-7 read-only gate hardening step; no renderer code was moved.
- Smoke: PASS via `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; cloud-drive transient file-access retry occurred and recovered.

## 2026-05-31 - Render plan compose work order inspector

- Added `scripts/inspect_render_plan_compose_work_order.ps1` to produce a no-GUI work order for the first post-7 extraction: `render_plan_compose -> render_core/render_plan.py`.
- The work order records source helpers, keep-contracts, required schemas, smoke gates and non-goals, including that runtime compose-run merging remains disabled until zero-diff parity artifacts exist.
- Registered the work order in the visual inspector index, review packet, pre-decoupling snapshot and runbook.
- Smoke: PASS via `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; cloud-drive transient file-access retries occurred and recovered.

## 2026-05-31 - Boundary inspection in pre-decoupling snapshot

- Added `decoupling_boundary_inspection` to `scripts/export_pre_decoupling_snapshot.ps1` output so the handoff snapshot includes the post-7 first extraction target and RRKAL data/cache boundary.
- Smoke now gates both the snapshot export contract field and the emitted boundary inspection schema/first extraction ID.
- Kept this read-only; it does not move renderer code or launch Qt/Taichi.
- Smoke: PASS via `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; cloud-drive transient file-access retries occurred and recovered.

## 2026-05-31 - No-GUI decoupling boundary inspector

- Added `scripts/inspect_decoupling_boundaries.ps1` for read-only inspection of the post-7 decoupling boundary before code movement.
- The inspector reports `render_plan_compose -> render_core/render_plan.py`, keep-contracts, module boundary registry fields, Qt-primary/Tk exclusion and the RRKAL discovery/download/import/cache ownership boundary.
- Wired the inspector into decoupling readiness, pre-decoupling gate metadata, visual contract review packet and smoke gates.
- Smoke: PASS via `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; first run hit a transient cloud-drive `-File` visibility miss for the pre-decoupling snapshot script, second full run recovered and passed.

## 2026-05-31 - No-GUI Layer workflow inspector

- Added `scripts/inspect_layer_workflow.ps1` for no-GUI inspection of layer research workflow, selection summary, operator groups and navigation copy contract.
- Registered `layer_workflow` in the visual contract inspector index and review packet first commands so cloned machines can inspect layer UIUX state without launching Qt.
- Kept the inspector contract-only/read-only; it does not launch Qt, Taichi, provider IO, dataset discovery, import or cache governance.
- Smoke: PASS via `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; cloud-drive transient file-access retries occurred and recovered.

## 2026-05-31 - Copyable layer navigation summary

- Added `rrkal_displaytools.layer_navigation_summary_contract.v1` under `layer_research_workflow.navigation_hint` across the Qt launch packet, no-GUI launch packet and renderer capability discovery.
- Added `Copy layer navigation` to the Qt Research interaction actions so researchers can copy the current navigation state, next action, selected layer, first visible layer, visible row count and filter context.
- Kept this as a UI handoff action only; it does not mutate renderer visibility, cache, import or RRKAL data governance.
- Smoke: PASS via `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; cloud-drive transient file-access retries occurred and recovered.

## 2026-05-31 - Layer navigation hint

- Added `rrkal_displaytools.layer_navigation_hint.v1` to `layer_research_workflow` across the Qt launch packet, no-GUI launch packet and renderer capability discovery.
- Added a `layerNavigationHint` label to the Qt Layers dock so researchers can see whether the active layer is hidden by filter/group state and which action to take next.
- Added the outgoing Agent Exchange rule to workflow docs: c_3 writes cross-project observations to `L:\AGENT_EXCHANGE\inbox\c_3_<target_project>.md` instead of editing another repo.
- Kept the hint UI-only; it does not mutate renderer visibility, cache, import or RRKAL data governance.
- Smoke: PASS via `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; cloud-drive transient file-access retries occurred and recovered.

## 2026-05-31 - Ocean 3D dialog cost estimate

- Added `rrkal_displaytools.taichi_ocean_3d_interactive_cost_estimate.v1` to the Ocean material control port in Qt launch packets, no-GUI launch packets and renderer capability discovery.
- Added `ocean3DDialogCostEstimate` and `ocean3DDialogSafePreviewButton` to the Taichi 3D Ocean dialog so researchers can see relative interaction cost and switch to the low-cost preset before live orbit review.
- Kept this as a UI/runtime-scalar guard only; measured render-loop telemetry and render-pass reduction remain post-decoupling work.
- Smoke: PASS via `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`; cloud-drive transient file-access retries occurred and recovered.

## 2026-05-31 - Agent Exchange workflow adoption

- Adopted `L:\AGENT_EXCHANGE` as an advisory cross-agent read-check in the displaytools workflow.
- Added session-start, checkpoint-close, and pre-large-change read points for `u_owner_all-projects.md` and `*_RRKAL_displaytools.md`.
- Kept the boundary explicit: raw exchange inbox/archive/template content is not committed to GitHub; only validated decisions or engineering outcomes enter repo docs/code.
- Smoke: PASS via `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-31 - Visual contract review packet exporter

- Added `scripts/export_visual_contract_review_packet.ps1` to emit one no-GUI JSON review packet for cloned-machine visual contract checks.
- The packet embeds the inspector index, first reviewer commands, pre-decoupling commands and the displaytools/RRKAL governance boundary.
- Smoke now verifies contract-only export, normal packet schema, key inspector IDs and required handoff commands.
- Hardened `scripts/export_pre_decoupling_snapshot.ps1` with short internal retries for transient cloud-drive file locks during Python/PowerShell JSON collection.
- Smoke: PASS (`scripts\smoke.ps1`).

## 2026-05-31 - Visual contract inspector index

- Added `scripts/list_visual_contract_inspectors.ps1` to list no-GUI reviewer commands for config gateway, style routes, Hydrology/LOD, Ocean material, performance smoke and pre-decoupling gates.
- Smoke now verifies the index schema, key inspector IDs, recommended cross-machine sequence and no-launch/no-data-governance boundary.
- This gives a cloned machine one entrypoint for deciding which displaytools contracts to inspect before visual/runtime work.
- Smoke: PASS (`scripts\smoke.ps1`).

## 2026-05-31 - No-GUI Ocean material inspector

- Added `scripts/inspect_ocean_material.ps1` for no-GUI inspection of Ocean material, Ocean 3D control panel, control-board audit, renderer apply and sea-state scalar contracts.
- Smoke now verifies the inspector contract, safe-preview action, default-visible Ocean 3D control-board status and post-decoupling render-plan follow-up marker.
- This makes the Ocean 3D control surface reviewable across machines without launching Qt while keeping provider IO/cache governance outside displaytools.
- Smoke: PASS (`scripts\smoke.ps1`).

## 2026-05-31 - No-GUI Hydrology/LOD inspector

- Added `scripts/inspect_hydrology_lod.ps1` for no-GUI inspection of Hydrology/LOD readiness and runtime evidence.
- Smoke now verifies the inspector contract, stable lake/river renderer targets, `contract_ready` LOD hook status, and runtime state/ack/pick bridge paths.
- This keeps Hydrology/LOD cross-machine review in displaytools while leaving dataset discovery/download/cache governance in RRKAL.
- Smoke: PASS (`scripts\smoke.ps1`).

## 2026-05-31 - No-GUI style renderer routes inspector

- Added `scripts/inspect_style_renderer_routes.ps1` for no-GUI inspection of scientific, nautical, parchment and tactical renderer route contracts.
- Smoke now verifies the inspector contract, launch-packet field, parchment/tactical route IDs and portable style commands.
- Updated GTD to reflect that explicit style renderer entries are already smoke-gated; the remaining work is visual tuning and post-decoupling entrypoint extraction, not first exposure.
- Smoke: PASS (`scripts\smoke.ps1`).

## 2026-05-31 - Spatial compression roadmap contract

- Added `spatial_compression_roadmap.py` as a contract-only handoff for 3D bathymetry compression strategy.
- The roadmap records DWT, spherical harmonics and neural-field options, plus explicit non-goals for dataset download, cache governance, training loops and runtime codec switching before parity evidence.
- Added Qt Replay/contracts inspect/copy actions for the roadmap.
- Smoke: PASS (`scripts\smoke.ps1`).

## 2026-05-31 - Qt render-plan work order summary

- Added `Copy render-plan work order` to the Qt Renderer diagnostics actions.
- The summary captures the queued post-decoupling path: precompute layer state, compose queue, compose runs, parity evidence, final single Taichi render pass and `runtime_merge=false`.
- Smoke: PASS (`scripts\smoke.ps1`).

## 2026-05-31 - Qt Ocean 3D board audit visibility

- Added `Inspect: Ocean 3D board` and `Copy Ocean board audit` to the Qt Renderer ports actions.
- The audit entry exposes control-board visibility, object names, dialog action, safe-preview action and the post-decoupling render-plan optimization boundary.
- Smoke: PASS (`scripts\smoke.ps1`).

## 2026-05-31 - Qt pre-decoupling snapshot entry

- Added a Qt Replay/contracts entry for the pre-decoupling snapshot command and generated output path.
- Added copy-summary support so reviewers can capture the snapshot command without hunting through scripts.
- Extended smoke coverage for the Qt snapshot buttons, handlers and schema reference.
- Smoke: PASS (`scripts\smoke.ps1`).

## 2026-05-31 - Pre-decoupling snapshot exporter

Changes:
- Added `scripts/export_pre_decoupling_snapshot.ps1` to export one no-GUI JSON handoff snapshot before post-7 module extraction.
- The snapshot includes decoupling readiness, pre-decoupling gate contract, performance smoke telemetry contract, renderer config gateway, controlled interception policy and git state.
- Added the snapshot command/output to `decoupling_readiness.operation_schedule`.
- Smoke verifies contract-only mode, normal snapshot export, required schemas and the `render_plan_compose` next action.
- Boundary: snapshot export is handoff/readiness only; it does not move renderer code, launch Qt, run live network or touch RRKAL data/cache governance.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-31 - Decoupling observability baseline gate

Changes:
- Added `observability_baseline` to `decoupling_readiness.py`, linking post-7 extraction readiness to `performance_smoke_telemetry`, stage timing JSONL and render telemetry schema.
- Updated `scripts/pre_decoupling_gate.ps1` so the gate validates performance smoke contract fields before renderer files are moved.
- Updated the decoupling runbook to list observability baseline expectations for the post-7 gate.
- Boundary: this is still pre-7 contract/gate work; no renderer modules were physically extracted.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-31 - Performance telemetry reviewer visibility

Changes:
- Added `performance_smoke_telemetry` contract packets to no-GUI launch packets, renderer capabilities, reviewer packets and handoff inspection.
- Added Qt Replay/contracts actions: `Inspect: Perf telemetry` and `Copy perf smoke summary`.
- Reviewer exports now include `performance_smoke_summary` and the performance telemetry contract field.
- Boundary: reviewer/Qt visibility only exposes the contract and output paths; heavy or full GPU profiling is still not part of regular smoke.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-31 - Displaytools performance smoke telemetry

Changes:
- Added `performance_telemetry.py` with lightweight `rrkal_displaytools.performance_smoke.v1`, `rrkal_displaytools.stage_timing.v1`, and `rrkal_displaytools.render_telemetry.v1` outputs.
- Added `scripts/performance_smoke.ps1` as the no-GUI entrypoint; normal mode writes `state/performance/performance_smoke.json`, `state/performance/stage_timing.jsonl`, and `state/performance/render_telemetry.json`.
- Added a headless 3-frame tiny render telemetry smoke that tracks frame timing, draw calls, vertices, numpy sync counts, queue depth and memory fields without GPU or live network.
- Added a synthetic threshold guard proving `performance_bucket="slow"` produces `next_action` without making the regular smoke flaky.
- Boundary: this covers displaytools renderer/config telemetry only; RRKAL crawler/download/import/cache performance smoke remains in the RRKAL repo.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit; one transient cloud-drive retry recovered).

## 2026-05-31 - Researcher layer controls guide

Changes:
- Added a Qt `Copy layer controls guide` action under Research interaction.
- The copied guide summarizes the intended research workflow: layer selection, visible/lock/solo diagnostics, Pin/cursor/boundary tools, and brush/mask exclusion.
- Smoke now verifies the button, formatter, copy action and pin occlusion wording.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-31 - Renderer config gateway no-GUI inspector

Changes:
- Added `scripts/inspect_renderer_config_gateway.ps1` for clone-side inspection of `renderer_config_gateway` without opening Qt.
- Smoke now verifies inspector contract-only mode and normal launch-packet field extraction.
- Boundary: the inspector reads launch-packet evidence only; it does not launch Qt/Taichi or touch RRKAL discovery/import/cache governance.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit; first run exposed a PowerShell `py` invocation issue, then passed after explicit invocation fix).

## 2026-05-31 - Renderer config gateway UI/reviewer hook

Changes:
- Added `renderer_config_gateway` to launch packets, renderer capabilities, no-GUI reviewer packets and handoff inspection.
- Added Qt Replay/contracts actions: `Inspect: Config gateway` and `Copy config summary`.
- Smoke gate now verifies the config gateway reviewer fields, Qt actions, no-GUI exporter contract and handoff schemas.
- Boundary: this is a typed config normalization/readout contract only; it does not launch Qt/Taichi or move post-7 renderer modules.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-31 - Renderer config gateway contract

Changes:
- Added `renderer_config_gateway.py` with `rrkal_displaytools.renderer_config_gateway.v1`.
- Introduced a typed `RendererConfig` dataclass and normalization helper as the pre-decoupling replacement path for scattered `getattr(args, ...)` access.
- Smoke now gates width/map-projection normalization, the `getattr` replacement marker and the no-launch/no-data-governance boundary.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-31 - Headless import shim contract

Changes:
- Added `compat/headless_import_shims.py` with `rrkal_displaytools.headless_import_shim.v1`.
- Implemented a synthetic `sys.modules` install/import/restore self-test that proves the interception mechanism without faking PyQt6, OpenGL, Taichi or visual runtime success.
- Smoke now gates the contract, visual-runtime guard and restoration behavior.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-31 - Qt controlled interception Inspect actions

Changes:
- Added Qt `Inspect: Interception` to show `rrkal_displaytools.controlled_interception_policy.v1` from the Replay/contracts action group.
- Added Qt `Copy interception summary` for a compact allowed/blocked/first-use handoff line.
- Smoke now gates both action labels and handlers.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Reviewer packet controlled interception handoff

Changes:
- Added `controlled_interception_policy` and `controlled_interception_summary` to Qt launch/reviewer packets and no-GUI reviewer export.
- Added a reviewer field-guide `controlled_interception` group pointing at blocked interception patterns.
- Smoke now gates launch packet and no-GUI exporter coverage for the policy.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Controlled interception policy packet

Changes:
- Added `controlled_interception.py` with `rrkal_displaytools.controlled_interception_policy.v1`.
- Captured allowed interception patterns for import shims, scoped stdout capture, runtime ack hooks and packet normalization.
- Smoke now gates the policy and its blocked patterns, including no permanent `builtins.print` patching and no fake CI visual-runtime success.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Suppress transient smoke retry noise

Changes:
- Updated `scripts/smoke.ps1` retry helper to capture native command output during retries.
- Successful retry attempts now avoid leaking transient `Errno 13 Permission denied` messages into a passing smoke log.
- Final failures still include the last captured command output for diagnosis.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Qt copy decoupling readiness summary

Changes:
- Added Qt `Copy decoupling summary` to the Replay/contracts action group.
- The copied summary includes phase, not-before time, first extraction, pre-decoupling gate command and RRKAL boundary rule.
- Smoke now gates the action label and handler.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Post-7 decoupling runbook

Changes:
- Added `docs/DECOUPLING_RUNBOOK.zh-TW.md` for the post-`2026-05-31T07:00:00+08:00` extraction phase.
- Linked the runbook from the docs index and agent handoff.
- Captured the first extraction order and boundary rules so the next agent starts with `render_plan_compose` after the pre-decoupling gate.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Pre-decoupling clean worktree guard

Changes:
- Strengthened `scripts/pre_decoupling_gate.ps1` so non-contract decoupling starts require a clean git worktree before moving renderer code.
- Added `requires_clean_worktree=true` to the gate packet and smoke-gated the requirement.
- This keeps the post-7 module extraction phase small, attributable and reversible.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Decoupling schedule gate metadata

Changes:
- Added explicit Asia/Taipei schedule metadata to `rrkal_displaytools.decoupling_readiness.v1`.
- Recorded `2026-05-31T07:00:00+08:00` as the decoupling not-before gate and linked the pre-decoupling gate command.
- Smoke now gates the schedule marker and pre-gate command so handoff agents do not start module moves before the agreed gate.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Pre-decoupling gate script

Changes:
- Added `scripts/pre_decoupling_gate.ps1` to verify the post-7 decoupling gate before moving renderer code.
- The gate checks `rrkal_displaytools.decoupling_readiness.v1`, requires `render_plan_compose` as the first extraction and preserves the RRKAL data/cache boundary.
- Smoke now runs the gate in `-ContractOnly` mode so the pre-decoupling entrypoint remains portable without recursively running smoke.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Reviewer packet decoupling readiness handoff

Changes:
- Added `decoupling_readiness` and `decoupling_readiness_summary` to Qt launch/reviewer packets and no-GUI launch/reviewer export paths.
- Added a reviewer field-guide `decoupling` group pointing at `decoupling_readiness.first_extraction_order`.
- Smoke now gates reviewer recommended fields, included summary/packet fields and no-GUI contract metadata for decoupling readiness.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Qt decoupling readiness collector

Changes:
- Added `collect_decoupling_readiness()` to the Qt panel so decoupling readiness has a reusable in-panel collector instead of a one-off action import.
- Routed `Inspect: Decoupling` through the collector, preparing the field for reviewer/launch packet handoff without moving renderer code.
- Smoke now gates the collector marker alongside the action and post-7 readiness phase.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Qt decoupling readiness Inspect action

Changes:
- Added Qt `Inspect: Decoupling` in the Replay/contracts action group.
- The action opens `rrkal_displaytools.decoupling_readiness.v1` for the post-7 decoupling phase without touching the renderer monolith.
- Smoke now gates the Qt action label, handler and post-7 readiness marker, and keeps transient retry warnings out of handoff JSON parsing.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Smoke transient file-access retry

Changes:
- Added bounded native-command retry/backoff to `scripts/smoke.ps1` for Python commands that can be hit by transient cloud-drive file-access denial.
- Routed captured smoke JSON commands through the same retry path and added matching retry behavior to `scripts/inspect_handoff.ps1`.
- This addresses intermittent `Errno 13 Permission denied` failures from the shared cloud drive without weakening final smoke failure behavior.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Smoke gate decoupling readiness

Changes:
- Added `decoupling_readiness.py --phase post_07_decoupling` to `scripts/smoke.ps1`.
- Smoke now gates the decoupling schema, post-7 phase, first extraction order, render-plan-first rule and RRKAL data/cache boundary guard.
- This keeps the seven-o'clock decoupling start aligned with a checked contract instead of relying only on prose.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Decoupling readiness packet

Changes:
- Added `decoupling_readiness.py` as a standalone packet for the pre-7:00 UI closure phase and post-7:00 decoupling phase.
- Captured the first extraction order: render-plan compose, ocean material, layer runtime bridge, style profile routes and diagnostics packets.
- Restated the RRKAL/displaytools boundary so discovery/download/import/cache governance stays outside displaytools during decoupling.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Ocean 3D performance budget controls

Changes:
- Added a visible Ocean 3D performance budget selector in the Qt Layers control board with Safe preview, Balanced research and Research detail presets.
- Synced Ocean 3D budget state into the ocean material control port, summary text, control-board strip and Taichi 3D Ocean dialog so the UI and launch packet describe the same scalar material state.
- Kept the real renderer pass reduction explicitly queued for the post-7:00 module decoupling / render-plan merge phase instead of mixing optimization into the UI control pass.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - dialogue-save transcript restore docs

Changes:
- Added `docs/DIALOGUE_SAVE_RESTORE.zh-TW.md` to document how to reconstruct the private `dialogue-save` gzip transcript chunks into the original Codex rollout JSONL.
- Linked the restore workflow from the docs index, Cloud handoff and workflow docs so Cloud/local agents can recover full context only when handoff summaries are insufficient.
- Kept raw transcript storage out of the public repo; this commit documents the process only.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Cloud/local development workflow docs

Changes:
- Added `docs/WORKFLOW.zh-TW.md` to formalize GitHub as the sync truth, `L:\RRKAL_displaytools` as the local cloud-drive working copy, Codex Cloud as the long-running code/docs/CI surface, and local Windows as the Qt/Taichi visual validation authority.
- Added `docs/CODEX_CLOUD_HANDOFF.zh-TW.md` as the first-read entrypoint for Codex Cloud, local Codex and other agents.
- Updated agent/git handoff docs, docs index and GTD to include private raw transcript backup policy, the proposed `dialogue-save` private repo layout, temporary local GUI test clones, cache reset gates and maturity estimates in push reports.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - GitHub Actions smoke UTF-8 fix

Changes:
- Fixed the repeated GitHub mobile red-X notifications by forcing the GitHub `smoke` workflow and `scripts/smoke.ps1` Python child processes to use UTF-8 stdout/stderr.
- Root cause was GitHub Windows runner using a non-UTF-8 console codec while `scripts/export_launch_packet.py` printed launch packets containing Chinese layer labels.
- Added a smoke guard so the workflow must keep `PYTHONUTF8` and `PYTHONIOENCODING` configured.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Compose parity smoke pending notification

Changes:
- Adjusted `scripts/render_compose_parity_smoke.ps1` so contract-only and missing-artifact runs report `precommit_gate_passed=true`, `visual_parity_passed=null`, `notification_level=info` and `notification_suppressed=true` instead of surfacing as failed smoke.
- Kept actual RGBA artifact diff failures as `notification_level=error` and `passed=false`, preserving the safety gate before any compose-run merge can be enabled.
- Updated launch / renderer / handoff-facing parity smoke fields and smoke checks to distinguish precommit gate health from visual parity evidence.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Goal closure scorecard

Changes:
- Added `rrkal_displaytools.goal_closure_scorecard.v1` to summarize the active objective categories: Qt-first UI, layer control, profile/launch packets, renderer capability discovery, cross-machine use, requested visualization features and queued renderer performance.
- Added Qt `Copy goal scorecard` so reviewers can copy objective-level ready/queued status without opening JSON first; the scorecard is also included in reviewer packet fields.
- Smoke now gates launch packet, renderer capability, handoff inspection and Qt source markers for the scorecard and copy summary contract.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).
## 2026-05-30 - Visual closure matrix copy summary

Changes:
- Added `rrkal_displaytools.visual_feature_closure_copy_summary_contract.v1` to the visual feature closure matrix across Qt, no-GUI launch packets, renderer capabilities and handoff inspection.
- Added Qt `Copy closure matrix` so reviewers can copy ready/queued visual feature status and the renderer-runtime-artifact boundary without opening JSON first.
- Smoke now gates the copy action, contract, reviewer field-guide group and Qt source markers.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).
## 2026-05-30 - Reviewer packet field guide copy action

Changes:
- Added `rrkal_displaytools.reviewer_packet_field_guide.v1` to reviewer packet export metadata, grouping clone/launch, layer control, ocean guard, visual review and compose performance fields.
- Added Qt `Copy reviewer fields` so cross-machine reviewers can copy the primary field, recommended review paths, grouped field guide and no-GUI export command without opening JSON first.
- Smoke now gates launch packet, renderer capability, handoff inspection and Qt source markers for the field guide.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).
## 2026-05-30 - Reviewer packet layer quick actions fields

Changes:
- Added layer quick-actions review paths to `reviewer_packet_export.recommended_review_fields` so reviewer packets point directly to active-layer Visible/Lock/Solo/Diagnostics handoff evidence.
- Added `layer_selection_tool` and `layer_selection_affordance` to reviewer packet included packet fields across Qt, no-GUI launch packets and renderer capability discovery.
- Smoke now gates launch, renderer capability and handoff inspection coverage for these reviewer packet fields.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).
## 2026-05-30 - Active layer quick actions copy summary

Changes:
- Upgraded `Copy selection summary` so the portable layer-selection handoff now includes active-layer quick actions: Visible, Lock, Solo and Diagnostics.
- Added `rrkal_displaytools.active_layer_quick_actions_summary_contract.v1` to the layer selection summary contract across Qt, no-GUI launch packets, renderer capabilities and handoff inspection.
- Smoke now gates the quick-action summary contract, source packet field and Qt summary text.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).
## 2026-05-30 - Ocean 3D guard copy summary

Changes:
- Added `Copy Ocean guard` to the Qt Renderer ports action section for copying the Ocean 3D safe-preview preset, current scalar values, action ID and render-plan optimization boundary.
- Added `rrkal_displaytools.taichi_ocean_3d_performance_guard_summary_contract.v1` to the ocean material control port across Qt, no-GUI launch packets and renderer capability discovery.
- Smoke now gates the copy action, portable summary text and launch/renderer capability summary contract.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).
## 2026-05-30 - Ocean 3D safe preview guard

Changes:
- Added Qt Layers dock `ocean3DPerformanceGuardStrip` and `Ocean safe preview` to make the Taichi Ocean 3D control board usable when the current ocean material settings feel too heavy.
- Added `rrkal_displaytools.taichi_ocean_3d_performance_guard.v1` metadata to the ocean material control port across Qt, no-GUI launch packets and renderer capability discovery.
- Smoke now gates the safe-preview action, button/object IDs and launch/renderer capability contract fields while keeping true pass reduction queued for the render-plan merge work.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).
## 2026-05-30 - Active layer quick actions row

Changes:
- Added Qt Layers dock `activeLayerQuickActions` with active-layer Visible, Lock, Solo and Diagnostics buttons directly under the active layer guide.
- Added `rrkal_displaytools.active_layer_quick_actions.v1` metadata to `layer_selection_affordance` packets for launch packet / no-GUI export / renderer capability discovery alignment.
- Smoke now gates the quick-action row, button IDs, handler feedback and renderer capability markers.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).
## 2026-05-30 - Active layer action guide strip

Changes:
- Added Qt Layers dock `activeLayerActionGuideStrip` so researchers can see the selected layer, next valid actions and the explicit Brush/Mask exclusion in one visible strip.
- Extended `layer_selection_affordance` packets with `rrkal_displaytools.active_layer_action_guide.v1`, action steps and the active guide surface for launch packet / no-GUI export / renderer capability discovery alignment.
- Smoke now gates the Qt strip, helper refresh path, Brush/Mask boundary text and renderer capability contract markers.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).
## 2026-05-30 - Reviewer packet no-GUI review fields

Changes:
- Added `no_gui_primary_summary_field=compose_performance_summary` to `reviewer_packet_export` across Qt, no-GUI launch packet export, renderer capabilities and handoff inspection.
- Added `recommended_review_fields` for compose performance, compose pass budget, parity workflow and visual closure matrix evidence.
- Smoke gates launch packet, renderer capability and handoff fields.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).
## 2026-05-30 - No-GUI reviewer packet exporter

Changes:
- Added `scripts/export_reviewer_packet.ps1` to generate `rrkal_displaytools.reviewer_packet.v1` from the no-GUI launch packet path without opening Qt.
- `reviewer_packet_export` now exposes the no-GUI script, command, contract-only smoke command and `rrkal_displaytools.no_gui_reviewer_packet_export.v1` schema across Qt, no-GUI launch packets and renderer capabilities.
- The no-GUI reviewer packet includes `compose_performance_summary`, layer render-plan performance evidence and the launch packet snapshot.
- Smoke gates source markers and runs the exporter in `-ContractOnly` mode without writing runtime artifacts.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).
## 2026-05-30 - Reviewer packet compose performance handoff note

Changes:
- Updated clone quickstart to identify `compose_performance_summary` as the first reviewer-packet field for cross-machine renderer performance review.
- Updated agent handoff rules to mention `compose_performance_summary` in push reports when compose budget, parity runner or renderer performance work changes.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).
## 2026-05-30 - Reviewer packet compose performance summary

Changes:
- Added `compose_performance_summary` to `reviewer_packet_export.included_summary_fields` across Qt, no-GUI launch packet export and renderer capabilities.
- Qt reviewer packet export now writes a combined compose budget and parity runner readiness summary, so cross-machine review can see bottleneck advice and parity runner availability in one field.
- Smoke gates launch packet, renderer capability, handoff and Qt reviewer packet source coverage.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).
## 2026-05-30 - Copyable compose budget summary

Changes:
- Added `rrkal_displaytools.layer_render_plan_compose_pass_budget_summary_contract.v1` to `layer_render_plan_performance` across launch packets, renderer capabilities and handoff inspection.
- Qt Renderer diagnostics now includes `Copy compose budget`, copying compose run counts, timing fields, slowest phase, advice, target pass model and `runtime_merge=false` as one portable line.
- Smoke gates the summary contract, Qt copy button/action and renderer markers.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).
## 2026-05-30 - Compose budget bottleneck advice

Changes:
- Added compose pass budget `bottleneck_advice_rules`, mapping `compose_overlays` to `run_parity_then_collapse_runs` while preserving safe fallback advice before runtime metadata exists.
- Qt `composePassBudgetStrip` now shows `advice=` beside compose timing and slowest-phase fields.
- Smoke gates launch packet, renderer capability, handoff, Qt and renderer source markers for the advice field/rules.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).
## 2026-05-30 - Compose budget runtime timing fields

Changes:
- Extended `rrkal_displaytools.layer_render_plan_compose_pass_budget.v1` with runtime diagnostic fields for `cache_diagnostics.phase_timing_ms.compose_overlays`, `cache_diagnostics.slowest_phase_id` and `cache_diagnostics.slow_frame_threshold_ms`.
- Qt `composePassBudgetStrip` now displays `compose_ms=` and `slowest=` from latest renderer metadata when available, while preserving safe `-` fallback before a runtime frame exists.
- Smoke gates launch packet, renderer capability, handoff and Qt source markers for the timing fields.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).
## 2026-05-30 - Compose pass budget readiness strip

Changes:
- Added `rrkal_displaytools.layer_render_plan_compose_pass_budget.v1` to `layer_render_plan_performance` across launch packets, renderer capabilities, Qt and handoff inspection.
- Added Qt `composePassBudgetStrip` in the Layers control board to show compose run count, merge-candidate count, target pass model, parity evidence dependency and `runtime_merge=false`.
- Smoke gates the compose pass budget schema, target model, required evidence, Qt strip and renderer marker.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).
## 2026-05-30 - Qt compose parity runner readiness strip

Changes:
- Added a visible Qt Layers control-board strip `composeParityRunnerReadinessStrip` for compose parity runner readiness.
- The strip shows `ready=`, runner script, runner manifest and `runtime_merge=false`, making the parity runner discoverable without copying or opening the full JSON packet first.
- Smoke gates the strip object name, readiness helper and ready text marker.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).
## 2026-05-30 - Compose parity runner venv resolver

Changes:
- Updated `scripts/render_compose_parity_artifacts.ps1` to prefer `.venv\Scripts\python.exe` before falling back to `py -3`.
- The runner manifest now records `python_command`, `python_uses_local_venv` and `python_fallback` for cross-machine diagnostics.
- Smoke now gates the local venv resolver markers, and clone quickstart documents the resolver behavior.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).
## 2026-05-30 - Cross-machine compose parity runner docs

Changes:
- Updated clone quickstart with the optional `scripts/render_compose_parity_artifacts.ps1` runner command, produced `state/compose_parity` artifacts and `-SkipDiff` mode.
- Added RRKAL handoff language that keeps compose parity artifact runner ownership inside displaytools and out of RRKAL discovery/download/cache governance.
- Corrected the agent handoff working directory to `L:\RRKAL_displaytools`.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).
## 2026-05-30 - Compose parity artifact runner

Changes:
- Added `scripts/render_compose_parity_artifacts.ps1` as a cross-machine manual runner for the compose parity loop: render synthetic/headless artifacts, then optionally call `scripts/render_compose_parity_smoke.ps1` on the generated baseline/candidate PNGs.
- `layer_render_plan_performance` now exposes `rrkal_displaytools.compose_run_parity_artifact_runner.v1`, runner script, runner command and runner manifest across Qt, launch packets, renderer capabilities and handoff inspection.
- Qt `Copy compose parity` summary now includes the single runner command in addition to separate producer/diff/precommit commands.
- Pre-commit smoke gates the runner contract and source markers only; it still uses contract-only parity smoke and does not run the heavier renderer artifact loop.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).
## 2026-05-30 - Compose parity copyable workflow summary

Changes:
- Added `rrkal_displaytools.compose_run_parity_summary_contract.v1` to `layer_render_plan_performance`.
- Qt Renderer diagnostics now includes `Copy compose parity`, which copies producer, diff, baseline/candidate artifact and precommit commands as one portable handoff line.
- Launch packets, renderer capabilities and handoff inspection now expose the compose parity summary contract and copy action.
- Smoke gates the copy button, copy handler, summary helper, contract fields and renderer contract markers.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Compose parity artifact producer

Changes:
- Added renderer CLI `--compose-parity-artifact-dir` as an opt-in artifact producer for compose-run parity review.
- Added `HybridRenderController.apply_layer_render_plan_merged_candidate_composition()` to generate a merged alpha-compose candidate frame without enabling runtime merge.
- Added `HybridRenderController.write_compose_parity_artifacts()` to write baseline sequential PNG, merged-candidate PNG and `rrkal_displaytools.compose_run_parity_artifacts.v1` metadata under `state/compose_parity`.
- Updated `rrkal_displaytools.compose_run_parity_artifact_workflow.v1` to expose producer command, renderer arg, candidate schema and artifact schema across Qt, launch packets, renderer capabilities and handoff.
- Runtime compose merging remains disabled until the manual parity smoke proves zero-diff output.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Compose parity artifact workflow contract

Changes:
- Added `rrkal_displaytools.compose_run_parity_artifact_workflow.v1` to `layer_render_plan_performance`.
- Launch packets, renderer capabilities, Qt render-plan inspector and handoff inspection now expose the parity artifact directory, baseline/candidate PNG paths, metadata path, precommit command and manual diff command.
- The workflow explicitly records the current blocker: baseline sequential renderer output is available, while the opt-in merged compose candidate path still needs to be added before runtime merging can be enabled.
- Smoke gates now verify artifact workflow schema, paths, producer status and next-step guidance.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Compose parity smoke precommit contract-only mode

Changes:
- Added `-ContractOnly` to `scripts/render_compose_parity_smoke.ps1` so pre-commit smoke is not affected by local `state/compose_parity` runtime PNG artifacts.
- `scripts/smoke.ps1` now calls the parity smoke with `-ContractOnly`, while manual parity runs still perform RGBA PNG diff when baseline/candidate artifacts are supplied.
- Launch packets, renderer capabilities and handoff inspection now expose the contract-only precommit command, making cross-machine smoke behavior stable.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Compose parity smoke PNG diff

Changes:
- Upgraded `scripts/render_compose_parity_smoke.ps1` from contract-only output to an artifact-aware RGBA PNG diff entrypoint.
- When sequential baseline and merged-candidate PNG artifacts exist, the script now checks dimensions, computes `max_abs_diff` and `changed_pixel_count`, emits pass/fail fields and exits non-zero if visual parity fails.
- `layer_render_plan_performance` now exposes compose parity smoke validation fields and pass fields through launch packets, renderer capabilities and handoff inspection.
- Pre-commit smoke now executes the parity smoke in missing-artifact contract mode, proving the entrypoint works without rendering frames or writing runtime state.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Ocean 3D control-board audit and compose parity smoke entry

Changes:
- Added `rrkal_displaytools.taichi_ocean_3d_control_board_audit.v1` so the Taichi Ocean 3D controls are explicitly tracked as default-visible control-board UI, not only a Properties dock control.
- The Qt Layers control board now labels the button as `Taichi Ocean 3D controls` and shows `board=wired_default_visible` in the Ocean 3D quick summary.
- Added `scripts/render_compose_parity_smoke.ps1` as a contract-only parity smoke entry for the next compose-run merge step.
- `layer_render_plan_performance` now exposes the parity smoke schema, script, manifest and precommit flag through launch packets, renderer capabilities and handoff inspection.
- This records the next optimization direction requested by the user: after module decoupling, precompute layer state/compose queue first, then render through one unified Taichi render/composite path instead of independent per-layer render paths.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Render-plan compose run parity contract

Changes:
- Added `HybridRenderController.layer_render_plan_compose_run_parity_contract()` to require visual parity evidence before enabling any merged compose run.
- Compiled render-plan metadata and Qt diagnostics now expose `rrkal_displaytools.layer_render_plan_compose_run_parity_contract.v1`.
- The contract records candidate run ids, strict RGBA diff tolerance, required artifacts and the recommended quick render smoke command.
- The Layers control-board render-plan strip now shows `parity=` beside compose run and merge-candidate counts.
- Smoke gates now verify parity contract schema/helper/field, Qt summary text and renderer contract markers.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Render-plan compose run grouping

Changes:
- Added `HybridRenderController.layer_render_plan_compose_runs()` to group the executable compose queue into ordered runs.
- Compose runs mark which adjacent overlay steps are merge-safe candidates and which must preserve per-layer visibility, opacity or blend semantics.
- Compiled render-plan metadata and Qt diagnostics now expose `rrkal_displaytools.layer_render_plan_compose_runs.v1`, run count and merge-candidate run count.
- The Layers control-board render-plan strip now shows `runs=` and `merge=` beside queue and skipped-step evidence.
- Smoke gates now verify compose run schema/helper/field, Qt summary text and renderer merge-safety markers.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Render-plan compose queue optimization

Changes:
- Added `HybridRenderController.layer_render_plan_compose_queue()` to turn composition steps into an executable queue before the overlay compose pass runs.
- The renderer now skips hidden, missing and transparent overlay steps before calling `apply_layer_render_plan_composition()`, while preserving the existing visual composition helper.
- Compiled render-plan metadata and Qt diagnostics now expose `rrkal_displaytools.layer_render_plan_compose_queue.v1`, queue count and skipped-step count.
- The Layers control-board render-plan strip now shows `queue=` and `skip=` beside runtime timing and bottleneck recommendation evidence.
- Smoke gates now verify compose queue schema/helper/field, skip reasons, Qt summary text and renderer source markers.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Render-plan bottleneck recommendation

Changes:
- Added `HybridRenderController.layer_render_plan_bottleneck_recommendation()` to convert measured phase timing into the next optimization target.
- Compiled render-plan metadata and Qt diagnostics now expose `rrkal_displaytools.layer_render_plan_bottleneck_recommendation.v1` and `bottleneck_recommendation`.
- Recommendations map `prepare_batches` to static batch/cache reuse, `compose_overlays` to collapsed overlay composition, `postprocess` to folded/deferred style work and `future_single_pass_candidate` to a unified Taichi composite pass prototype.
- The Layers control-board render-plan strip now shows `next_opt=` beside runtime timing and slowest phase evidence.
- Smoke gates now verify recommendation schema/helper/field, Qt summary text and renderer recommendation markers.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Render-plan phase timing runtime evidence

Changes:
- Added `HybridRenderController.layer_render_plan_phase_timing_runtime_packet()` to write measured phase timings into compiled render-plan metadata.
- `render_if_needed()` now records `prepare_batches`, `compose_overlays`, `postprocess` and `future_single_pass_candidate` phase timing evidence for each rendered frame.
- `apply_layer_render_plan_composition()` now measures composition and style postprocess timing without changing visual output.
- Qt diagnostics, launch packets and handoff inspection now expose `rrkal_displaytools.layer_render_plan_phase_timing_runtime.v1`, including `phase_timing_ms`, `slowest_phase_id`, total milliseconds and slow-frame threshold status.
- Smoke gates now verify runtime timing schema/helper/field, Qt summary text and renderer timing markers.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Render-plan phase timing probe contract

Changes:
- Added `HybridRenderController.layer_render_plan_phase_timing_contract()` so each render-plan phase has a stable probe key before the runtime timing wrapper is added.
- Compiled render-plan metadata and Qt diagnostics now expose `rrkal_displaytools.layer_render_plan_phase_timing_contract.v1` and `phase_timing_contract`.
- The contract defines millisecond timing units, per-phase `phase_ms.*` probe keys, `slow_frame_threshold_ms=33.3` and the next runtime step for writing measured `phase_timing_ms`.
- The Layers control-board render-plan strip now shows `timing=probe_contract_ready` when metadata is available.
- Smoke gates now verify timing contract schema/helper/field, Qt summary text and renderer source markers.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Render-plan execution phases

Changes:
- Added `HybridRenderController.layer_render_plan_execution_phases()` to split the current render-plan path into phase metadata.
- Compiled render-plan metadata and Qt diagnostics now expose `rrkal_displaytools.layer_render_plan_execution_phases.v1`, `execution_phases` and `execution_phase_count`.
- Phase ids are `prepare_batches`, `compose_overlays`, `postprocess` and `future_single_pass_candidate`, making the later unified Taichi render/composite pass boundary explicit.
- The Layers control-board render-plan strip now shows a compact `phases=` summary next to execution mode and single-pass candidate counts.
- Smoke gates now verify execution phase schema/helper/field, Qt summary text and renderer phase markers.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Render-plan execution summary

Changes:
- Added `HybridRenderController.layer_render_plan_execution_summary()` to summarize the current render-plan execution mode.
- Compiled render-plan metadata and Qt diagnostics now expose `rrkal_displaytools.layer_render_plan_execution_summary.v1`, including current apply helper, helper/decision counts, single-pass candidate count and blockers.
- The Layers control-board render-plan strip now shows `exec=` and `sp=` next to cache, invalidation, batch and apply-path summaries.
- Smoke gates now verify execution summary schema/helper/field, Qt summary text and renderer source markers for current mode, blockers and next refactor target.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Render-plan apply path metadata

Changes:
- Added `HybridRenderController.layer_render_plan_apply_path()` to map each composition step to its current apply helper, batch decision and single-pass candidate flag.
- Compiled render-plan metadata and Qt diagnostics now expose `rrkal_displaytools.layer_render_plan_apply_path.v1`, `apply_path` and `apply_path_count`.
- The Layers control-board render-plan strip now includes an `apply=` count next to cache, invalidation and batch decision summaries.
- Smoke gates now verify apply path schema/helper/field, Qt summary text and renderer source markers for current runtime apply helpers.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Render-plan batch decisions

Changes:
- Added `HybridRenderController.layer_render_plan_batch_decisions()` to classify batch and layer composition actions before the future single-pass renderer refactor.
- Compiled render-plan metadata and Qt diagnostics now expose `rrkal_displaytools.layer_render_plan_batch_decisions.v1`, `batch_decisions` and `batch_decision_count`.
- Batch/layer decisions include `rebuild_batch`, `reuse_batch`, `compose_dirty_overlay`, `compose_cached_overlay` and `postprocess_each_frame`.
- Smoke gates now verify batch decision schema/helper/field, Qt control-board summary text and renderer decision markers.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Render-plan invalidation scope

Changes:
- Added `HybridRenderController.layer_render_plan_cache_invalidation_scope()` to map dirty flags and cache-key decisions to batch/global/plan/reuse scopes.
- Compiled render-plan metadata and Qt diagnostics now expose `cache_invalidation_scope_schema` and `cache_invalidation_scope`.
- The Layers control-board render-plan cache strip now shows a compact `scope=` summary next to decision and reason text.
- Smoke gates now verify scope schema/helper/field plus renderer source markers for batch, global, plan and reuse scopes.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Render-plan cache invalidation reasons

Changes:
- Added `HybridRenderController.layer_render_plan_cache_invalidation_reasons()` to classify compiled render-plan cache decisions.
- Compiled plan metadata now exposes `cache_reuse_decision`, `cache_invalidation_reason_schema` and `cache_invalidation_reasons` with markers such as `dirty_flag:*`, `no_previous_compiled_plan`, `cache_key_changed` and `cache_key_match`.
- Qt render-plan cache diagnostics and the Layers control-board summary now show reuse decision and invalidation reasons alongside cache status.
- Smoke gates now verify invalidation schema/helper/fields and renderer source markers across launch packets, renderer capabilities, handoff inspection and source checks.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Compiled render-plan reuse policy

Changes:
- Exposed the renderer's compiled render-plan reuse behavior as `compiled_plan_reuse_policy`, with status values `compiled` / `reused`.
- Added `reuse_policy` and `reuse_boundary` to compiled render-plan metadata, including the existing cache-key reuse branch in `HybridRenderController.compile_layer_render_plan()`.
- Extended cache diagnostics summaries with reuse boundary evidence so the Layers control board can explain when a cached compiled plan remains valid.
- Smoke gates now verify reuse policy, status values, boundary fields and the renderer cache-key reuse guard across launch packets, renderer capabilities, handoff inspection and source checks.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Render-plan cache control-board strip

Changes:
- Added a default-visible Layers dock `renderPlanCacheDiagnosticsStrip` showing render-plan metadata/cache status, cache key availability, composition step count, visible layer count and single-pass readiness.
- Added a `renderPlanCacheDiagnosticsButton` that opens the existing render-plan performance/cache diagnostics inspector from the control board.
- Extended `rrkal_displaytools.layer_render_plan_performance.v1` with `rrkal_displaytools.layer_render_plan_cache_control_board.v1` evidence across launch packets, renderer capabilities and handoff inspection.
- Smoke gates now verify the cache diagnostics strip/button, summary formatter, metadata-missing status and control-board contract.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Ocean control board and render-plan cache diagnostics

Changes:
- Added a default-visible Layers dock Ocean 3D quick control strip that opens the same Taichi 3D Ocean Water scalar control dialog as the Properties dock.
- Extended `rrkal_displaytools.taichi_ocean_3d_control_panel.v1` with control-board object evidence so the ocean water controls are not hidden behind a tabified Properties dock.
- Completed `rrkal_displaytools.layer_render_plan_cache_diagnostics.v1` wiring in Qt, reading renderer metadata sidecar cache evidence and returning `metadata_sidecar_missing` when no runtime metadata exists.
- Smoke gates now verify the Ocean 3D control-board entry and render-plan cache diagnostics across launch packets, renderer capabilities, handoff inspection and Qt source.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Compiled render-plan cache key

Changes:
- Added `layer_render_plan_cache_key()` so compiled render plans can report whether the current plan was newly compiled or reused.
- `compile_layer_render_plan()` now emits `cache_key` and `cache_status`, while preserving the current rendering path and `runtime_optimization_applied=false`.
- Smoke gates now verify cache-key helper exposure across launch packets, renderer capabilities, handoff inspection and renderer source.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Compiled layer render-plan snapshot

Changes:
- Added `compile_layer_render_plan()` to produce `rrkal_displaytools.compiled_layer_render_plan.v1` with dirty flags, batch targets and composition steps in one reusable snapshot.
- Renderer metadata now writes the compiled plan under `layer_render_plan`, while preserving the nested runtime snapshot and `runtime_optimization_applied=false`.
- Smoke now gates the compiled plan schema/helper across launch packets, renderer capabilities, handoff inspection and renderer source wiring.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Renderer render-plan composition helper

Changes:
- Added `layer_render_plan_composition_steps()` and `apply_layer_render_plan_composition()` to centralize the existing overlay compose sequence behind a replaceable render-plan helper.
- Updated runtime snapshots to report composition helper, step count and current helper-backed compose path.
- Extended launch/capability/handoff smoke gates so the next single-pass optimization has a concrete apply boundary instead of scattered hard-coded compose calls.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Renderer layer render-plan runtime snapshot

Changes:
- Added `HybridRenderController.layer_render_plan_runtime_snapshot()` to centralize visible layers, dirty flags, batch targets and current compose order as runtime evidence.
- Wired the snapshot into renderer output metadata under `layer_render_plan` without changing current visual composition behavior.
- Extended `rrkal_displaytools.layer_render_plan_performance.v1` with the runtime snapshot schema/helper and metadata sidecar field while keeping `runtime_optimization_applied=false`.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Layer render-plan performance queue

Changes:
- Added `rrkal_displaytools.layer_render_plan_performance.v1` to record the post-decoupling performance task: precompute layer state, dirty flags and batches before one Taichi render/composite pass.
- Exposed the contract through Qt launch packets, No-GUI launch export, renderer capability discovery, handoff inspection and a Qt `Inspect: Render plan perf` action.
- Updated reviewer packet fields and visual closure matrix so renderer performance is visible as queued work, not claimed as already optimized runtime behavior.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Qt Taichi 3D Ocean control panel

Changes:
- Added an explicit `Taichi 3D Ocean controls` entry in the Qt Properties dock and Renderer ports action group.
- Added `rrkal_displaytools.taichi_ocean_3d_control_panel.v1` under `ocean_material_control_port` for launch packets, renderer capabilities and handoff inspection.
- Recorded the next performance follow-up as post-decoupling layer render-plan precompute followed by a single renderer pass, instead of treating each layer as an independent render path.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Reviewer packet visual handoff summaries

Changes:
- Expanded `reviewer_packet_export.included_summary_fields` with Hydro/LOD, Ocean material, Style routes and Module boundary summaries.
- Qt `collect_reviewer_packet()` now writes those summaries and focused packet evidence directly into `rrkal_displaytools.reviewer_packet.v1`.
- Smoke now gates the added reviewer packet summary fields for launch packets and handoff inspection.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Module boundary copyable handoff summary

Changes:
- Added `rrkal_displaytools.module_boundary_summary_contract.v1` to module boundary registry packets for Qt, launch export and renderer capability discovery.
- Added a Qt `Copy module summary` action that copies extraction order, first module, render-core target, stable contract gate, Tk-primary boundary and RRKAL governance ownership.
- Handoff inspection and smoke now gate the module boundary summary contract before future module extraction work.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Style routes copyable handoff summary

Changes:
- Added `rrkal_displaytools.style_routes_summary_contract.v1` to style profile renderer route packets for Qt, launch export and renderer capability discovery.
- Added a Qt `Copy Style routes summary` action that copies route readiness, route IDs, required parchment/tactical coverage and portable commands.
- Handoff inspection and smoke now gate the style routes summary contract while keeping RRKAL data/cache governance outside displaytools.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Ocean material copyable handoff summary

Changes:
- Added `rrkal_displaytools.ocean_material_summary_contract.v1` to Ocean material control port packets for Qt, launch export and renderer capability discovery.
- Added a Qt `Copy Ocean summary` action that copies enabled state, wave strength, roughness, foam, renderer apply status, sea-state scalar sample schema and renderer flags.
- Handoff inspection and smoke now gate the Ocean material summary contract while preserving RRKAL-owned provider/cache governance.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Hydrology LOD copyable handoff summary

Changes:
- Added `rrkal_displaytools.hydrology_lod_summary_contract.v1` to Hydrology/LOD readiness packets for Qt, launch export and renderer capability discovery.
- Added a Qt `Copy Hydro LOD summary` action that copies readiness, live layer count, renderer targets, LOD hook state, runtime evidence, ack file and pick-state file.
- Handoff inspection and smoke now gate the Hydrology/LOD summary contract and runtime summary fields.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Boundary summary identity and ack handoff

Changes:
- Added a compact Qt `boundary_highlight_ack_summary_text()` helper for the existing boundary renderer ack payload.
- `Copy boundary summary` now includes the current boundary identity warning and renderer ack summary in addition to target/tuning values.
- Smoke gates the Qt helper and copied identity/ack summary fields.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Boundary emphasis tuning summary

Changes:
- Expanded the boundary emphasis portable summary to include RGB, contrast, opacity, gamma and breathing period values.
- Added summary parameter fields to Qt, launch packet, renderer capability and handoff contracts for the boundary emphasis control surface.
- Smoke now gates the richer boundary emphasis summary format across launch packet, renderer capabilities, handoff inspection and Qt copy text.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Local style thumbnail readiness JSON

Changes:
- Added `collect_local_style_thumbnail_readiness()` for local style thumbnail slot status.
- `Inspect: Style thumbs` now includes local per-style thumbnail readiness details with path, absolute path, existence and ready/missing status.
- Style preview packets, handoff inspection and smoke now advertise `rrkal_displaytools.local_style_thumbnail_readiness.v1`.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Style thumbnail readiness copy fix

Changes:
- Removed stale undefined `packet` / `current_style` references from `copy_style_thumbnail_readiness_summary()`.
- Added smoke source gates to catch the same stale copy-handler reference pattern.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Style thumbnail readiness copy action

Changes:
- Added `Copy style thumb status` to the Qt Visual review action group.
- Added `copy_style_thumbnail_readiness_summary()` and `style_thumbnail_readiness_summary_text()` for portable ready/missing thumbnail status notes.
- Style preview packets, handoff inspection and smoke now expose the thumbnail readiness copy action and label.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Style thumbnail readiness label

Changes:
- Added `styleThumbnailReadiness` to the Qt Looks/templates section.
- The label reports ready/missing local thumbnail slots for `state/style_previews/<style>.png`.
- Added `rrkal_displaytools.style_thumbnail_readiness.v1` metadata to style preview packets, handoff inspection and smoke.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Cross-machine clone command contract

Changes:
- Added `clone_command`, `default_branch` and `repo_visibility` to `rrkal_displaytools.cross_machine_clone_readiness.v1`.
- Extended the clone reviewer summary and Qt readiness label with branch / visibility handoff details.
- Smoke now verifies clone command, public visibility and default branch across launch packet, renderer capability and handoff outputs.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Cross-machine readiness visible commands

Changes:
- Added `qt_visible_fields` to `rrkal_displaytools.cross_machine_clone_readiness.v1` for first-run smoke and handoff commands.
- The Qt Layers dock `Cross-machine clone readiness` label now displays first smoke and first handoff commands.
- `first_run_order` now includes `scripts/inspect_handoff.ps1` before the Qt panel launch.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Cross-machine first-run commands

Changes:
- Added `first_run_smoke_command` and `first_run_handoff_command` to `rrkal_displaytools.cross_machine_clone_readiness.v1`.
- Extended the clone reviewer summary format and Qt `copy_clone_reviewer_summary()` output with those first-run commands.
- Handoff inspection and smoke now verify both commands across launch packets and renderer capability discovery.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Qt Layer lock disabled controls

Changes:
- Extended `rrkal_displaytools.layer_lock_affordance.v1` with `disabled_controls_when_locked`.
- Locked Qt layer rows now disable visibility, opacity and blend controls together.
- Smoke now verifies the disabled controls contract and Qt source behavior for opacity/blend.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Qt Layer lock affordance

Changes:
- Added `rrkal_displaytools.layer_lock_affordance.v1` to Qt launch packets, no-GUI launch packets, renderer capability discovery and handoff inspection.
- Qt Layers rows now carry a `locked` property with `QWidget#layerRow[locked="true"]` styling so locked scientific layers are visually distinct.
- `refresh_layer_stack_status()` now keeps locked row styling and disabled visibility checkboxes synchronized with lock state.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Pin overlay summary occlusion vocabulary

Changes:
- Extended `copy_pin_overlay_summary()` output with the shared Pin occlusion status vocabulary and `pinOcclusionLegend` object name.
- Updated `pin_summary_contract.summary_format` so launch packets, renderer capabilities and handoff preserve those visibility semantics for research notes.
- Smoke now verifies the summary format and Qt source path for `occlusion_statuses`.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Qt Pin occlusion legend

Changes:
- Added `pinOcclusionLegend` to the Qt Pin Annotation panel, sourced from `rrkal_displaytools.pin_projection.v1`.
- The Pin projection contract now exposes the occlusion status vocabulary: `visible`, `behind_horizon`, `off_viewport`, and `invalid`.
- Handoff inspection and smoke now verify the Qt occlusion legend object and shared Pin occlusion vocabulary.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Qt Layer row hover affordance

Changes:
- Added `rrkal_displaytools.layer_hover_affordance.v1` for Qt launch packets, no-GUI launch packets, renderer capability discovery and handoff inspection.
- Qt Layers dock now exposes `layerHoverAffordance`, updated through row hover enter/leave event filters and `layer_hover_layer_key` for layer key, renderer target, visibility, lock state and renderer sync.
- Smoke now verifies the hover label, event target map, packet schema, renderer capability field and handoff output.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Style preview batch renderer script

Changes:
- Added `scripts/render_style_previews.ps1` to generate scientific, nautical, parchment and tactical thumbnail PNGs under `state/style_previews`.
- Qt Actions now includes `Copy style thumbs command`, and style preview packets expose the batch script, portable command, expected outputs and validation targets.
- Smoke verifies the batch command contract and PowerShell parser coverage without running the renderer during pre-commit validation.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Qt Style thumbnail card icons

Changes:
- Qt style cards now resolve `state/style_previews/<style>.png` locally and load existing PNGs as 96x54 card icons.
- Missing thumbnails remain visible as `thumb: missing`, so runtime artifact absence is explicit without failing pre-commit smoke.
- Smoke now verifies the icon-loading contract, Qt path resolver, `QIcon` loading and handoff metadata.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Qt Style thumbnail slots inspector

Changes:
- Added `Inspect: Style thumbs` to the Qt Actions visual review section.
- The action displays `style_template_visual_preview`, thumbnail slots, missing guidance and local renderer `--output` commands in the JSON preview pane.
- Smoke now verifies the inspector action, handler, launch packet metadata, renderer capabilities and handoff output.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Style preview thumbnail slots

Changes:
- Added thumbnail slots to `rrkal_displaytools.style_template_visual_preview.v1` for scientific, nautical, parchment and tactical cards.
- Qt style cards now display `state/style_previews/<style>.png` slot hints, and packets expose local renderer `--output` review commands tied to `rrkal_displaytools.renderer_output_artifact_contract.v1`.
- Smoke verifies thumbnail slot metadata without requiring runtime PNG generation during pre-commit validation.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Qt Layer selection affordance

Changes:
- Added `rrkal_displaytools.layer_selection_affordance.v1` for Qt launch packets, no-GUI launch packets, renderer capability discovery and handoff inspection.
- Qt Layers dock now exposes `layerSelectionAffordance`, linking selected-row highlighting, selected-layer label, `layerControlFeedbackStrip` and Reveal selected into one active-target focus contract.
- Smoke now verifies the schema, label object, selected row property, renderer capability field and handoff summary.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Qt Layer control feedback strip

Changes:
- Added `rrkal_displaytools.layer_control_feedback_strip.v1` for Qt launch packets, no-GUI launch packets, renderer capability discovery and handoff inspection.
- Qt Layers dock now exposes `layerControlFeedbackStrip`, a compact active-layer strip for selected layer, visibility, lock, opacity, blend mode and renderer sync.
- Smoke now verifies the strip schema, Qt label object, visible fields, renderer capability field and handoff summary.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Clickable Style template preview cards

Changes:
- Upgraded the Qt Looks/templates preview from a static summary into clickable `styleTemplateCard_<id>` cards for scientific, nautical, parchment and tactical profiles.
- Card clicks now call `apply_style_template_preview_card`, update `style_combo`, refresh selected-card styling and keep launch/profile routing unchanged.
- Smoke now verifies the card interaction contract across launch packet, renderer capabilities, handoff inspection and Qt source.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Style template visual preview contract

Changes:
- Added `rrkal_displaytools.style_template_visual_preview.v1` for Qt launch packets, no-GUI launch packets, renderer capability discovery and handoff inspection.
- Qt Renderer entry now exposes a `styleTemplateVisualPreview` surface for scientific, nautical, parchment and tactical preview-card intent.
- Smoke now verifies preview IDs, swatches, Qt surface and route linkage while keeping RRKAL data discovery/cache governance outside displaytools.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Renderer output artifact contract

Changes:
- Added `rrkal_displaytools.renderer_output_artifact_contract.v1` for Qt launch packets, no-GUI launch packets, renderer capability discovery and handoff inspection.
- The contract exposes the existing headless/once `--output` PNG path, `.metadata.json` sidecar schema, preview frame controls, optional `scripts/render_quick_smoke.ps1` runtime verification and RRKAL manifest reference boundary.
- Smoke now verifies the contract without making quick render smoke part of mandatory pre-commit validation.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Visual feature closure matrix

Changes:
- Added `rrkal_displaytools.visual_feature_closure_matrix.v1` for Qt, no-GUI launch packets, renderer capability discovery and handoff inspection.
- The matrix lists smoke-gated evidence for Qt UI, layer control, profile/launch, renderer capability discovery, cross-machine clone, Pin, cursor, Boundary emphasis, Hydrology/LOD, Ocean material, style profiles and module boundaries.
- Smoke now verifies the matrix across launch packets, renderer capabilities and handoff inspection without claiming fresh runtime PNG output.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Module decoupling boundary contract

Changes:
- Added `rrkal_displaytools.module_decoupling_boundary_contract.v1` under `module_boundary_registry` for Qt, no-GUI launch packets and renderer capability discovery.
- The contract records extraction order, stable contracts required before moving code, forbidden cross-imports, Qt-first/Tk-not-primary policy and RRKAL-owned data governance boundaries.
- Handoff inspection and smoke now verify the decoupling contract before future module extraction work.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Style renderer entry contracts

Changes:
- Added `rrkal_displaytools.style_renderer_entry_contract.v1` to scientific, nautical, parchment and tactical style entries in Qt, no-GUI launch packets and renderer capability discovery.
- Style routes now expose route contracts, making parchment/tactical portable commands and template support explicit in handoff inspection.
- Smoke now verifies the nested entry contract and required parchment/tactical route contracts.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Ocean material renderer apply and sea-state scalar contracts

Changes:
- Added `rrkal_displaytools.ocean_material_renderer_apply_contract.v1` to `ocean_material_control_port` for Qt, no-GUI launch packets and renderer capability discovery.
- Added `rrkal_displaytools.sea_state_scalar_sample.v1` under `sea_state_port`, defining normalized wave/roughness/foam sample fields without moving provider discovery/download/cache governance into displaytools.
- Handoff inspection and smoke now verify the renderer apply contract, timeline/source handoff and sea-state scalar sample boundary.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Hydrology LOD renderer apply contract

Changes:
- Added `rrkal_displaytools.hydrology_lod_renderer_apply_contract.v1` inside `hydrology_lod_readiness` for Qt, no-GUI launch packets and renderer capability discovery.
- The contract pins hydrology renderer apply to `state/renderer_layer_runtime_state.json`, `state/renderer_layer_runtime_ack.json`, required state/ack fields, lake/river apply targets and portable handoff semantics.
- Handoff inspection and smoke now verify the nested renderer apply contract and hydrology runtime evidence links.

Smoke:
- PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Reviewer packet export

Changes:
- Added `reviewer_packet_export` to Qt launch packets, no-GUI launch packets and renderer capabilities.
- Added Qt `Export reviewer packet`, writing `rrkal_displaytools.reviewer_packet.v1` with clone, launch, research and visual summaries plus a launch packet snapshot.
- Handoff output now exposes the reviewer packet export contract.
- Smoke gates launch packet, renderer capability, handoff and Qt source coverage.
- Updated clone quickstart, capability summary and GTD.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Launch reviewer summary contract

Changes:
- Added `launch_reviewer_summary_contract` to `profile_launch_readiness` in Qt, launch packet and renderer capability emitters.
- Added `copy_launch_reviewer_summary()` and `Copy launch summary` to the Qt Replay/contracts group.
- Handoff output now exposes the launch reviewer summary contract.
- Smoke gates launch packet, renderer capability, handoff and Qt source coverage.
- Updated clone quickstart, capability summary and GTD.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Clone reviewer summary contract

Changes:
- Added `clone_reviewer_summary_contract` to `cross_machine_clone_readiness` in Qt, launch packet and renderer capability emitters.
- Added `copy_clone_reviewer_summary()` and `Copy clone summary` to the Qt Replay/contracts group.
- Handoff output now exposes the clone reviewer summary contract.
- Smoke gates launch packet, renderer capability, handoff and Qt source coverage.
- Updated clone quickstart, capability summary and GTD.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Research interaction summary bundle

Changes:
- Added `research_summary_contract` to `layer_research_workflow` in Qt, launch packet and renderer capability emitters.
- Added `copy_research_interaction_summary()` and `Copy research summary` to the Qt Research interaction group.
- Handoff output now exposes the bundled research interaction summary contract.
- Smoke gates launch packet, renderer capability, handoff and Qt source coverage.
- Updated clone quickstart, capability summary and GTD.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Cursor geodesy summary contract

Changes:
- Added `cursor_summary_contract` to the Qt, launch packet and renderer Cursor geodesy readout emitters.
- Added `copy_cursor_geodesy_summary()` and `Copy cursor summary` to the Qt Research interaction group.
- Handoff output now exposes the Cursor geodesy summary contract.
- Smoke gates launch packet, renderer capability, handoff and Qt source coverage for the summary contract.
- Updated clone quickstart, capability summary and GTD.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Cursor geodesy state ack bridge contract

- Added smoke-gated cursor raycast state/ack file fields: `state/renderer_cursor_geodesy_state.json` and `state/renderer_cursor_geodesy_ack.json`.
- Launch packets, renderer capabilities and handoff inspection now expose the cursor raycast runtime bridge status and required state fields.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Capability summary mojibake repair

- Repaired the `Canvas Preview` capability summary line that was garbled during the cursor geodesy raycast contract update.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Cursor geodesy renderer raycast contract

- Added `cursor_geodesy.py` with a dependency-free `viewport_sphere_raycast` helper for renderer-facing cursor-to-lat/lon math.
- `cursor_geodesy_readout` now exposes `rrkal_displaytools.cursor_geodesy_raycast.v1`, raycast helper/method/inputs/outputs and smoke cases through launch packets, renderer capabilities and handoff inspection.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Boundary emphasis status label alignment

- Updated the Qt Layers dock initial Boundary emphasis label from queued renderer mask hook to renderer bridge wired.
- Smoke now guards against the stale queued label returning while `boundary_emphasis_control` is wired through `rrkal_displaytools.boundary_highlight_mask.v1`.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Handoff-first Qt launcher

- Added `-HandoffFirst` to `scripts/run_qt_panel.ps1`, allowing clone-after-setup users to run `scripts/inspect_handoff.ps1` before the Qt panel opens.
- `rrkal_displaytools.cross_machine_clone_readiness.v1`, renderer capabilities, handoff inspection and smoke now expose and verify the handoff-first launcher option and command.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Layer selection tool contract

- Added `rrkal_displaytools.layer_selection_tool.v1` so Qt row selection, filtered-layer selection, reveal-selected-row and renderer pick-state inspection have one smoke-gated selection-tool contract.
- Launch packets, renderer capabilities and handoff inspection now verify the pick-state file, selectable layer count, renderer live-control bridge and explicit brush/mask exclusion.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Boundary emphasis renderer bridge

- Mapped `Boundary emphasis controls...` Apply state into the existing `rrkal_displaytools.boundary_highlight_mask.v1` renderer bridge.
- Launch packets, renderer capabilities, handoff inspection and smoke now verify RGB/contrast/alpha/gamma/breathing mapping through the boundary highlight bridge; full polygon fill mask remains a renderer refinement.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Pin projection occlusion evidence

- Updated `rrkal_displaytools.pin_projection.v1` to reflect the current renderer path: Pins are projected every frame from geodetic anchors and composed through `pin_overlay_rgba`.
- Launch packets, renderer capabilities, handoff inspection and smoke now verify Pin rotation and horizon occlusion evidence via `view_z <= horizon_eps` and `--pin-horizon-eps`.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Cursor geodesy readout

- Added `rrkal_displaytools.cursor_geodesy_readout.v1` for canvas mouse-position lon/lat readout, with explicit `position()/pos()` Qt event guard evidence.
- Launch packets, renderer capabilities, handoff inspection and smoke now expose the cursor geodesy contract; renderer globe raycast remains queued as backend work.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Boundary emphasis row double-click

- Routed boundary-capable layer row double-clicks to `Boundary emphasis controls...` and hardened the slot for Qt `clicked(bool)` delivery.
- `rrkal_displaytools.boundary_emphasis_control.v1` now records row double-click binding evidence for boundary, territorial sea, EEZ and high-seas layers.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Boundary emphasis UI control

- Added `rrkal_displaytools.boundary_emphasis_control.v1` for country boundary, territorial sea, EEZ and maritime-boundary emphasis controls.
- Qt Layers dock now has a `Boundary emphasis controls...` dialog with RGB, contrast, opacity, gamma and breathing controls; renderer mask rasterization is explicitly marked as backend-queued.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Layer research workflow

- Added `rrkal_displaytools.layer_research_workflow.v1` to connect layer filter/group state, selected layer, runtime warnings and renderer remediation hints into a researcher-facing workflow.
- Qt Layers dock now shows `Layer research workflow`; launch packets, renderer capabilities, handoff inspection and closed-loop evidence expose the same contract.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Cross-machine readiness Qt surface

- Added a Qt Layers dock `Cross-machine clone readiness` label and exposed its `qt_surface` in `rrkal_displaytools.cross_machine_clone_readiness.v1`.
- Smoke now verifies the launch packet and renderer capability Qt surface for clone readiness.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Cross-machine clone readiness

- Added `rrkal_displaytools.cross_machine_clone_readiness.v1` to make clone/setup/smoke/run/inspect steps explicit for another Windows machine.
- Qt launch/provenance packets, No-GUI launch packets, renderer capabilities, handoff inspection and closed-loop evidence now expose the same cross-machine readiness contract while preserving the RRKAL data-governance boundary.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Module boundary registry

- Added `rrkal_displaytools.module_boundary_registry.v1` to mark future extraction boundaries for contracts, Qt UI, Taichi render core, ocean material, style profiles, overlays, RRKAL-owned data sources and diagnostics.
- Launch packets, renderer capabilities, handoff inspection and closed-loop evidence now expose the same module boundary contract, including Qt-first/Tk-not-primary and RRKAL data-governance boundaries.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Style profile renderer routes

- Added `rrkal_displaytools.style_profile_renderer_routes.v1` to make scientific, nautical, parchment and tactical renderer routes explicit, including portable commands for parchment/tactical review on another machine.
- Qt launch/provenance packets, No-GUI launch packets, renderer capabilities, handoff inspection and closed-loop evidence now expose the same style route contract.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Ocean material control port

- Added `rrkal_displaytools.ocean_material_control_port.v1` to expose Qt wave/roughness/foam controls, renderer CLI flags, Taichi uniforms and the scalar sea-state handoff boundary.
- Launch packets, renderer capabilities, handoff inspection and closed-loop evidence now verify the ocean material control port without moving data discovery/cache governance into displaytools.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Hydrology LOD runtime evidence

- Added `rrkal_displaytools.hydrology_lod_runtime_evidence.v1` to connect Hydrology/LOD readiness with renderer layer runtime ack and selected-layer pick evidence.
- Qt Layers dock now shows Hydrology runtime evidence, and launch packets, renderer capabilities, handoff inspection and closed-loop evidence expose the same contract.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Hydrology LOD readiness contract

- Added `rrkal_displaytools.hydrology_lod_readiness.v1` to lock lake/river Qt layer keys to renderer targets, live controls and LOD hook evidence.
- Qt Layers dock now shows Hydrology/LOD readiness, and launch packets, renderer capabilities, handoff inspection and closed-loop evidence expose the same contract.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Layer visual preset runtime feedback

- Added `rrkal_displaytools.layer_visual_preset_runtime_feedback.v1` to connect layer visual presets with the existing renderer layer runtime ack bridge.
- Qt Layers dock now has a preset renderer ack label, and launch packets, renderer capabilities, handoff inspection and closed-loop evidence expose the same feedback contract.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Layer visual presets panel

- Added `rrkal_displaytools.layer_visual_presets.v1` for Qt Layers dock preset buttons: All, Hydrology, Boundary and Annotations.
- Presets update layer visibility through existing Qt layer controls, preserve locked layers, and are exposed through Qt launch/provenance packets, No-GUI launch packets, renderer capability discovery, handoff inspection and closed-loop evidence.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Profile launch readiness UI surface

- Added `rrkal_displaytools.profile_launch_readiness_ui.v1` so Qt exposes profile/launch readiness as a visible Layers dock label instead of JSON-only evidence.
- Exposed the UI surface contract through Qt launch/provenance packets, No-GUI launch packets, renderer capability discovery, handoff inspection and closed-loop evidence.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Profile launch readiness contract

- Added `rrkal_displaytools.profile_launch_readiness.v1` to summarize cross-machine readiness for profile schema, built-in templates, launch packet export, portable command, renderer capability discovery, style entries and layer operator groups.
- Exposed readiness through Qt launch/provenance packets, No-GUI launch packets, renderer capability discovery, handoff inspection and closed-loop evidence.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Style renderer entries contract

- Added `rrkal_displaytools.style_renderer_entries.v1` so scientific, nautical, parchment and tactical styles have explicit renderer entry contracts.
- Exposed style entries through Qt launch/provenance packets, No-GUI launch packets, renderer capability discovery, handoff inspection and closed-loop evidence.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Layer operator workflow groups

- Added `rrkal_displaytools.layer_operator_groups.v1` to group Qt-first layer operations into Selection, Edit state, Isolation, History and Diagnostics workflows.
- Surfaced the workflow summary in the Qt Layers dock and exposed the same contract through Qt launch/provenance packets, No-GUI launch packets, renderer capability discovery, handoff inspection and closed-loop evidence.
- Smoke: PASS (`scripts/smoke.ps1`, before commit).

## 2026-05-30 - Layer operator shortcuts contract

- Added `rrkal_displaytools.layer_operator_shortcuts.v1` for Qt-first Photoshop-like layer operations: select, visibility, lock, opacity, blend, solo, restore, undo, reset and diagnostics actions.
- Installed Qt `QShortcut` bindings for selected-layer visibility/lock, solo, restore, undo, reset and diagnostics actions.
- Exposed the contract in Qt launch/provenance packets, No-GUI launch packets, renderer capability discovery, handoff inspection, closed-loop evidence and smoke gates.
- Smoke: `scripts/smoke.ps1` PASS (2026-05-30).

## 2026-05-30 - Layer renderer diagnostics remediation hints

- Added `rrkal_displaytools.layer_renderer_diagnostics_remediation.v1` with read-only next-step hints for renderer ack, layer pick state, RRKAL identity source, warning list and live-control coverage bridges.
- Surfaced remediation hints in Qt Properties, launch packet, renderer capability discovery, handoff inspection and closed-loop evidence.
- Smoke: `scripts/smoke.ps1` PASS (2026-05-30).

## 2026-05-30 - Layer renderer diagnostics detail

- Added `rrkal_displaytools.layer_renderer_diagnostics_detail.v1` to split renderer diagnostics into runtime ack, layer pick state, authoritative identity source, warning list and live-control coverage bridges.
- Surfaced the detail packet in Qt Properties, launch packet, renderer capability discovery, handoff inspection and closed-loop evidence.
- Smoke: `scripts/smoke.ps1` PASS (2026-05-30).

## 2026-05-29 - Layer renderer diagnostics summary

- Added `rrkal_displaytools.layer_renderer_diagnostics_summary.v1` to unify runtime ack availability, pick context availability, warning severity, RRKAL identity source ref status and live layer control counts.
- Surfaced the summary in Qt Properties, launch packet, renderer capability discovery, handoff inspection and closed-loop evidence.
- Smoke: `scripts/smoke.ps1` PASS (2026-05-29).

## 2026-05-29 - Layer authoritative identity source handoff

- Added `rrkal_displaytools.layer_authoritative_identity_source.v1` as a reference-only handoff for RRKAL-governed territory/EEZ polygon identity sources.
- Qt Properties now reports whether a RRKAL identity source ref is configured; launch packets, renderer capabilities and handoff inspection expose the same boundary.
- The contract explicitly keeps discovery/download/import/cache governance out of displaytools.
- Smoke: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1` PASS.

## 2026-05-29 - Layer territory identity context

- Added `rrkal_displaytools.layer_territory_identity_context.v1` to separate source-property feature identity from authoritative territory/EEZ polygon identity.
- Qt Properties now shows `Territory identity`; research provenance, launch packets, renderer capabilities and handoff inspection carry the same contract.
- The contract explicitly marks authoritative polygon identity and open-line area inference as pending while preserving runtime source-property identity evidence.
- Smoke: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1` PASS.

## 2026-05-29 - Layer runtime interaction context

- Added `rrkal_displaytools.layer_runtime_interaction_context.v1` to connect runtime warnings with selected-layer renderer pick context and source-property feature identity.
- Qt Properties now shows a `Runtime context` row; copyable research provenance carries pick target, hit status, feature label and feature identity when renderer pick evidence is available.
- No-GUI launch packets and static renderer capability discovery expose the same schema while explicitly marking live pick context unavailable.
- Smoke: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1` PASS.

## 2026-05-29 - Layer runtime warning list

- Added `rrkal_displaytools.layer_runtime_warning_list.v1` to turn Runtime badge counts into researcher-facing info/warning/error messages.
- Qt Properties now shows a `Runtime warnings` row, and copyable research provenance includes the warning list.
- Launch packets, renderer capabilities, handoff inspection, closed-loop status and smoke gates now expose the warning-list contract.
- Smoke: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1` PASS.

## 2026-05-29 - Layer runtime badge provenance

- Added `rrkal_displaytools.layer_runtime_badge_summary.v1` to summarize per-layer Runtime badge counts, selected-layer badge state and noteworthy layers.
- Qt copyable research provenance now includes the badge summary, so renderer ack evidence can be pasted into lab notes without opening the full matrix JSON.
- Launch packets, renderer capabilities, handoff inspection, closed-loop status and smoke gates now expose the badge summary contract.
- Smoke: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1` PASS.

## 2026-05-29 - Layer runtime evidence summary

- Added `rrkal_displaytools.layer_runtime_evidence_summary.v1` so Qt Properties, launch packets, renderer capabilities and handoff inspection expose a compact skip/error/count summary for layer runtime ack evidence.
- The summary reports unavailable/error/skipped_locked/changed/ok status without requiring researchers to open the full runtime JSON.
- Smoke updated to gate launch packet, renderer capability discovery and handoff inspection summary schemas.
- Smoke: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1` PASS.

## 2026-05-29 - Layer runtime badge legend

Scope:
- Added `rrkal_displaytools.layer_runtime_status_legend.v1` to the layer capability matrix.
- Qt runtime badges now use stable color semantics for `no_ack`, `ok`, `target`, `changed`, `locked`, and `error`.
- Layers dock now includes a compact runtime badge legend, and handoff/smoke verify the legend schema.

Positioning:
- This makes renderer feedback easier to read at a glance without weakening the underlying JSON contract.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Pin overlay summary contract

Changes:
- Added `pin_summary_contract` to the shared Pin projection contract.
- Added `copy_pin_overlay_summary()` and Pin summary buttons to the Qt Pin Annotation panel and Research interaction group.
- Handoff output now exposes the Pin overlay summary contract.
- Smoke gates launch packet, renderer capability, handoff and Qt source coverage for the summary contract.
- Updated clone quickstart, capability summary and GTD.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Boundary emphasis summary contract

Changes:
- Added `boundary_emphasis_summary_contract` to renderer capability, launch packet and Qt Boundary emphasis packets.
- Added `Copy boundary summary` and `copy_boundary_emphasis_summary()` to the Qt Research interaction group.
- Handoff output now exposes the Boundary emphasis summary contract.
- Smoke gates launch packet, renderer capability, handoff and Qt source coverage for the summary contract.
- Updated clone quickstart, capability summary and GTD.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Layer selection summary contract

Changes:
- Added `layer_selection_summary_contract` to renderer capability, launch packet and Qt layer selection packets.
- Added `Copy selection summary` and `copy_layer_selection_summary()` to the Qt Research interaction group.
- Handoff output now exposes the layer selection summary contract.
- Smoke gates launch packet, renderer capability, handoff and Qt source coverage for the summary contract.
- Updated clone quickstart, capability summary and GTD.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Visual readiness copy summary contract

Changes:
- Added `visual_review_copy_summary_contract` to visual readiness packets in renderer capabilities, launch packets and Qt panel packets.
- Handoff output now exposes the copy-summary contract.
- Qt summary formatting now reads the contract label so visible and copied summaries stay aligned.
- Smoke gates the contract schema, Qt label object, Qt copy action and portability flag.
- Updated clone quickstart, capability summary and GTD.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Qt Visual readiness copy summary

Changes:
- Added `Copy visual summary` to the Qt Visual review action group.
- Added `copy_visual_review_readiness_summary()` to copy the compact thumbnail/live-preview readiness summary.
- The copy action also refreshes the visible `visualReviewReadiness` label.
- Smoke gates the copy button and action.
- Updated clone quickstart, capability summary and GTD.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Qt Visual readiness visible summary

Changes:
- Added a `visualReviewReadiness` label to the Layers dock.
- Added `visual_review_readiness_summary_text()` and `update_visual_review_readiness_label()`.
- `Inspect: Visual readiness` now updates the compact visible summary and writes the full JSON packet.
- Smoke gates the label, formatter and updater.
- Updated clone quickstart, capability summary and GTD.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Qt Visual readiness runtime artifacts

Changes:
- `collect_visual_review_readiness()` now inspects current renderer thumbnail and live preview frame artifact availability.
- The Qt packet adds `runtime_artifact_summary` and updates inspector rows/status badges with artifact state and paths.
- Smoke gates the runtime artifact summary plus thumbnail/live-preview artifact checks in the Qt collector.
- Updated clone quickstart, capability summary and GTD for runtime artifact interpretation.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Qt Visual readiness action

Changes:
- Added `Inspect: Visual readiness` to the Qt Visual review button group and Renderer menu.
- Added `visual_review_readiness_packet`, `collect_visual_review_readiness()` and `show_visual_review_readiness()` to `rrkal_displaytools_qt_panel.py`.
- Updated the visual readiness command contract implementation status to `wired_in_qt_panel`.
- Updated closed-loop evidence, clone quickstart, capability summary and GTD for the wired Qt action.
- Smoke gates the Qt packet, button, collector, action and implementation status.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Visual readiness Qt command contract

Changes:
- Added `visual_review_qt_command_contract` metadata to `visual_review_readiness` packets.
- The contract maps `visual_readiness` / `Inspect: Visual readiness` to `visual_review_readiness.inspector_view`.
- Handoff output includes the command contract, and smoke gates schema, action id, payload field and dispatch status.
- Documented the current monolith boundary and future `qt_ui/main_window.py` split target.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Visual review inspector view

Changes:
- Added `visual_review_inspector_view` metadata to `visual_review_readiness` packets.
- The view now carries Qt-facing title, surface, status badges, rows, hints and copyable flag.
- Handoff output includes the inspector view, and smoke gates schema plus key UI fields.
- Updated clone quickstart, capability summary and GTD for the Visual review inspector view.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Visual review frame status

Changes:
- Added `visual_review_frame_status` metadata to `visual_review_readiness` packets.
- Renderer thumbnail and live preview now expose separate frame-status entries.
- Handoff output includes frame status, and smoke gates status plus artifact-state values.
- Updated clone quickstart, capability summary and GTD for frame-status interpretation.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Qt visual readiness capability

Changes:
- Added `visual_review_readiness` packets to `taichi_global_bathymetry.py` renderer capabilities and `scripts\export_launch_packet.py` no-GUI launch packets.
- Added `Inspect: Visual readiness` to the profile replay Visual review action group.
- Updated handoff inspection to read visual readiness from launch/capability packets instead of deriving it only from profile action ids.
- Smoke gates launch packet schema, renderer capability schema and Qt action id.
- Updated clone quickstart, capability summary and GTD for Qt visual readiness Inspect.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Visual review readiness handoff

Changes:
- Added `visual_review_readiness` to `scripts\inspect_handoff.ps1`.
- Handoff output now reports renderer thumbnail readiness, live preview readiness and missing-frame guidance.
- Smoke gates the readiness packet, both readiness flags and thumbnail/live-preview guidance text.
- Updated clone quickstart, capability summary and GTD for visual review readiness.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Qt Canvas state Inspect action

Scope:
- Renamed the Actions panel Canvas state entry to `Inspect: Canvas state` and moved it under Inspect: Research interaction.
- Added `canvas_state` to `profile_ui_state_replay.qt_inspector_action_ids` and the research interaction group across Qt, no-GUI launch packet and renderer capability discovery.
- Updated clone quickstart and profile schema docs; smoke verifies the action ID, label, tooltip and quickstart guidance.

Decision:
- Canvas Preview state/provenance is part of scientific visual inspection and should be grouped with the other research interaction Inspect actions.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Qt Timeline Inspect action

Scope:
- Added `Inspect: Timeline` to the grouped Qt Actions panel.
- The action writes the Timeline runtime state and opens the current `timeline_runtime_state` JSON in the command/JSON preview pane.
- Added `timeline` to `profile_ui_state_replay.qt_inspector_action_ids` and the replay/contracts group across Qt, no-GUI launch packet and renderer capability discovery.
- Updated clone quickstart and profile schema docs; smoke verifies the new action ID, label, tooltip and handler.

Decision:
- Timeline keyframes are part of profile/UI replay and need a direct Qt Inspect surface for cross-machine scientific review.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Qt Layer matrix Inspect action

Scope:
- Added `Inspect: Layer matrix` to the grouped Qt Actions panel.
- The action reuses the existing `show_layer_capability_matrix()` JSON view.
- Added `layer_matrix` to `profile_ui_state_replay.qt_inspector_action_ids` and the renderer ports group across Qt, no-GUI launch packet and renderer capability discovery.
- Updated clone quickstart and profile schema docs; smoke verifies the button, tooltip, action id and renderer capability label.

Decision:
- Layer capability matrix is a core layer-control closure surface and should be directly available from the grouped Actions panel.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Qt Layer Inspect actions

Scope:
- Added `Inspect: Layer runtime` and `Inspect: Layer pick` buttons to the grouped Qt Actions panel.
- The runtime action opens existing layer runtime state / renderer ack JSON; the pick action opens existing selected-layer pick JSON.
- Added `layer_runtime` and `layer_pick` to `profile_ui_state_replay.qt_inspector_action_ids` and group definitions across Qt, no-GUI launch packet and renderer capability discovery.
- Updated clone quickstart and profile schema docs; smoke verifies the new action IDs and button labels.

Decision:
- Layer control needs first-class Inspect actions because layer runtime and selected-layer pick state are central to the current scientific workflow.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Qt Actions section layout

Scope:
- Split the Qt Actions grid into section headers: Run / profile, Inspect: Replay/contracts, Inspect: Renderer ports, Inspect: Research interaction, Renderer diagnostics and Process.
- Added the `actionSectionHeader` object name and stylesheet hook for section labels.
- Smoke verifies section header presence and representative Inspect group headers.

Decision:
- The Actions panel should be readable as grouped scientific/operator controls instead of a flat button wall.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Qt grouped Inspect tooltips

Scope:
- Updated Qt `Inspect:` button tooltips and accessible descriptions to include Replay/contracts, Renderer ports or Research interaction group names.
- Smoke verifies representative grouped tooltip text for all three groups.
- Closed-loop evidence now records grouped inspector tooltips instead of ungrouped tooltip text.

Decision:
- The UI should display the same Inspect grouping that launch packets and renderer capability discovery now expose.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Clone quickstart Inspect groups

Scope:
- Updated `docs\QUICKSTART_CLONE.zh-TW.md` so the Qt `Inspect:` checklist follows the same groups as `profile_ui_state_replay.qt_inspector_action_groups`.
- The groups are Replay/contracts, Renderer ports and Research interaction.
- Smoke verifies quickstart group guidance for Replay/contracts and Research interaction.

Decision:
- Cross-machine onboarding should match the machine-readable Inspect grouping so users have a clear first-run order after opening Qt.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Profile replay inspector groups

Scope:
- Added `qt_inspector_action_groups` and `qt_inspector_group_count` to `profile_ui_state_replay` in Qt, no-GUI launch packet and renderer capability discovery.
- Groups now classify Inspect actions as `replay_contracts`, `renderer_ports` and `research_interaction`.
- Smoke verifies group fields through launch packet, renderer capabilities, source contracts and profile schema docs.

Decision:
- Inspect actions should be grouped as scientific/operator affordances, not only listed as flat button IDs.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Profile replay inspector action IDs

Scope:
- Added `qt_inspector_action_ids`, `qt_inspector_action_labels` and `qt_inspector_action_count` to `profile_ui_state_replay` in Qt, no-GUI launch packet and renderer capability discovery.
- Updated profile schema docs for the new inspector action fields.
- Smoke verifies Boundary, Cursor and Clone inspector entries across launch packet, renderer capabilities, source contracts and schema docs.

Decision:
- Qt `Inspect:` actions should be machine-readable profile replay coverage, not only human-readable button labels.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Profile replay Inspect surface

Scope:
- Added `Qt Inspect actions` to `profile_ui_state_replay.replay_surfaces` in Qt, no-GUI launch packet and renderer capability discovery.
- Updated profile schema docs to list Qt `Inspect:` actions as a replay/inspection surface.
- Smoke verifies Qt, renderer, launch packet and schema docs all include the Inspect surface.

Decision:
- The profile/UI replay contract should describe the direct Qt inspection actions that now expose portable state coverage after clone.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Clone quickstart Inspect guidance

Scope:
- Added a cross-machine Qt inspection checklist to `docs\QUICKSTART_CLONE.zh-TW.md`.
- The checklist points new clone users to `Inspect: Clone ready`, `Inspect: Profile replay`, `Inspect: Hydro LOD`, `Inspect: Ocean port`, `Inspect: Style routes`, `Inspect: Pin pick`, `Inspect: Cursor geo` and `Inspect: Boundary JSON`.
- Smoke verifies the quickstart keeps the `Inspect: Clone ready` and `Inspect: Boundary JSON` references.

Decision:
- Cross-machine users need a concrete first-run checklist after launching Qt, not only raw handoff/launch packet commands.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Qt inspector action naming

Scope:
- Added an `Inspect:` prefix to the Qt Actions JSON inspector buttons.
- The prefix now covers Profile replay, Ocean port, Hydro LOD, Style routes, Module seams, Clone ready, Pin pick, Cursor geo and Boundary JSON.
- Smoke verifies the inspector prefix and Boundary JSON prefix are present.

Decision:
- The Actions panel needs to distinguish state/contract inspection actions from mutating actions such as launch, restart, save/load and profile export.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Qt Boundary JSON action

Scope:
- Added a `Boundary JSON` action button to the Qt Actions panel.
- The action displays Boundary highlight state, Boundary emphasis control state, identity warning text, renderer ack payload and recent ack history.
- Smoke verifies the button, handler and researcher-facing tooltip.

Decision:
- Boundary/EEZ emphasis and non-authoritative identity warnings should be inspectable from Qt without opening multiple panels or raw state files.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Qt Cursor geodesy JSON action

Scope:
- Added a `Cursor geo` action button to the Qt Actions panel.
- The action displays `cursor_geodesy_readout`, renderer cursor geodesy state/ack file paths, and the latest state/ack payloads.
- Smoke verifies the button, handler and researcher-facing tooltip.

Decision:
- Mouse-position longitude/latitude inference should be directly inspectable from Qt so researchers can audit cursor-derived coordinates and renderer raycast readback without browsing state files.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Qt Pin pick JSON action

Scope:
- Added a `Pin pick` action button to the Qt Actions panel.
- The action opens the existing renderer Pin hover/click pick bridge JSON through `show_pin_pick_state()`.
- Smoke verifies the button and researcher-facing tooltip.

Decision:
- Pin selection feedback should be reachable from the primary Qt UI so researchers can inspect marker interaction state without browsing `state/` files.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Qt contract inspector tooltips

Scope:
- Added tooltips and accessible descriptions for the Qt Actions inspector buttons: `Profile replay`, `Ocean port`, `Hydro LOD`, `Style routes`, `Module seams` and `Clone ready`.
- Smoke verifies the tooltip text and accessible-description hook are present.
- Closed-loop evidence now records the tooltip surface for the contract inspectors.

Decision:
- The JSON inspection actions should be understandable to researchers from the UI itself, not only from docs or commit notes.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Qt Clone readiness JSON action

Scope:
- Added a `Clone ready` action button to the Qt Actions panel.
- The action renders `cross_machine_clone_readiness` in the command/JSON preview pane.
- Closed-loop evidence now includes the Qt action, and smoke verifies the button plus `show_cross_machine_clone_readiness` handler.

Decision:
- Cross-machine readiness should be inspectable from the primary Qt UI, not only through no-GUI launch packets or handoff scripts.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Qt Module seams JSON action

Scope:
- Added a `Module seams` action button to the Qt Actions panel.
- The action renders `module_boundary_registry` in the command/JSON preview pane.
- Closed-loop evidence now includes the Qt action, and smoke verifies the button plus `show_module_boundary_registry` handler.

Decision:
- Future module extraction boundaries should be visible from the primary Qt UI before code is split, while RRKAL-owned data discovery/import/cache governance remains outside displaytools.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Qt Style routes JSON action

Scope:
- Added a `Style routes` action button to the Qt Actions panel.
- The action renders `style_renderer_entries` and `style_profile_renderer_routes` together in the command/JSON preview pane.
- Closed-loop evidence now includes the Qt action, and smoke verifies the button plus `show_style_renderer_routes` handler.

Decision:
- Parchment and tactical renderer routes should be visible from the primary Qt UI, not only from no-GUI packets or handoff inspection.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Qt Hydrology LOD JSON action

Scope:
- Added a `Hydro LOD` action button to the Qt Actions panel.
- The action renders `hydrology_lod_readiness` and `hydrology_lod_runtime_evidence` together in the command/JSON preview pane.
- Closed-loop evidence now includes the Qt action, and smoke verifies the button plus `show_hydrology_lod_status` handler.

Decision:
- Hydrology layer contracts and LOD hook evidence should be inspectable from Qt while still keeping dataset discovery/download/import/cache governance outside displaytools.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Qt Ocean material port JSON action

Scope:
- Added an `Ocean port` action button to the Qt Actions panel.
- The action renders `collect_ocean_material_control_port()` as JSON in the command/JSON preview pane.
- Closed-loop evidence now includes the Qt action, and smoke verifies the button plus `show_ocean_material_control_port` handler.

Decision:
- Researchers should be able to inspect wave strength, roughness, foam, Taichi uniforms and scalar sea-state handoff from Qt without adding provider IO or cache governance to displaytools.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Cursor geodesy renderer state bridge

Scope:
- Wired renderer mouse press/move events to write cursor geodesy state and ack JSON files.
- Added `--cursor-geodesy-state-file` and `--cursor-geodesy-ack-file` to the renderer CLI and Qt launcher command.
- Launch packets, renderer capabilities, handoff inspection, and smoke now report `renderer_mouse_state_wired`.
- Cursor raycast state includes screen position, viewport size, hit status, lat/lon, camera yaw/pitch, frame index, and update time.

Decision:
- Mouse-move state writes are throttled to 20 Hz to avoid excessive cloud-drive churn on `L:`.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Layers runtime evidence badges

Scope:
- Added a `Runtime` badge column to the Qt Layers dock.
- Each layer row now surfaces the latest renderer ack status derived from `layer_runtime_evidence`: `no_ack`, `ok`, `target`, `changed`, `locked`, or `error`.
- Badges refresh when renderer ack changes and when layer state refreshes.

Positioning:
- This makes renderer apply feedback visible without forcing researchers to open JSON, improving the Photoshop-like layer control loop.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Layer capability runtime evidence

Scope:
- Added `rrkal_displaytools.layer_runtime_evidence.v1` under the layer capability matrix.
- Qt layer capability matrix now summarizes the latest renderer layer runtime ack: changed visibility/opacity/blend counts, skipped locked layers, selected renderer target, frame, event, and error state.
- No-GUI launch packets and renderer capability discovery explicitly report runtime evidence as unavailable instead of implying that static capability discovery saw a renderer ack.
- Smoke now gates the runtime evidence schema.

Positioning:
- This connects declared layer capabilities to the most recent renderer response, making layer controls easier to trust during scientific review.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Handoff inspection layer capabilities

Scope:
- `scripts\inspect_handoff.ps1` now reports `layer_capability_matrix` schema, launch-packet schema, live capability counts, and selected layer capabilities.
- Smoke now gates handoff inspection `layer_capability_matrix`.
- Clone quickstart now points at the current GitHub URL and tells users to expect the layer capability matrix in the read-only inspection output.

Positioning:
- This improves cross-machine confidence before opening Qt: another workstation can verify layer live capability contracts without running renderer output or touching RRKAL data governance.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Layer capability matrix UI contract

Scope:
- Added `rrkal_displaytools.layer_capability_matrix.v1` to Qt launch packets, No-GUI launch packets, renderer capabilities, active layer diagnostics, runtime state, and smoke gates.
- Qt Properties now shows the selected layer's live renderer capabilities: visibility, opacity, blend, and selected-layer picking.
- Layers dock can display the full capability matrix JSON, and the layer status line now summarizes live capability counts.

Positioning:
- This makes layer controls more honest for researchers: UI controls can remain visible, but unsupported renderer live paths are explicitly marked `planned` instead of implied.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Qt Timeline export options controls

Scope:
- Added a Qt Timeline `Renderer export` control group for export-on-launch, output directory, frame count, FPS, GIF fallback, and MP4 video.
- Added `rrkal_displaytools.timeline_export_options.v1` to Qt profiles, launch packets, runtime state, No-GUI launch packet export, profile schema, closed-loop status, and smoke gates.
- No-GUI launch packet export now accepts Timeline export flags and includes them in the portable renderer command.

Positioning:
- This keeps Timeline export operator-facing and reproducible without moving artifact/data governance into displaytools. Export paths default under `state/` and remain local runtime artifacts.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline MP4 video export

Scope:
- Added optional Timeline MP4 export through `--timeline-export-mp4` / `TIMELINE_EXPORT_MP4`.
- `rrkal_displaytools.timeline_animation_export.v1` now reports `mp4_file`, `encoded_video`, `video_encoding_format`, and `video_encoding_error`.
- Renderer, Qt runtime state, No-GUI launch packets, renderer capabilities, closed-loop status, and smoke gates now advertise `timeline_mp4_video`.
- Added `imageio[ffmpeg]` as the MP4/container writer dependency while keeping PNG frames as the canonical frame sequence.

Positioning:
- PNG remains the reproducible scientific frame sequence; GIF and MP4 are convenience containers for review and handoff. Blend crossfade and visibility fade remain pending.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline layer visibility/blend discrete hold

Scope:
- Added `rrkal_displaytools.timeline_layer_discrete_hold.v1`.
- Renderer/Qt/No-GUI Timeline handoff now exposes active-keyframe layer visibility and blend mode hold state.
- Timeline PNG/GIF export manifests now record held layer visibility and blend mode per frame.
- Renderer capabilities, closed-loop status, docs, and smoke gates now cover the layer discrete hold contract.

Positioning:
- Visibility and blend mode are categorical layer states, so this closes their honest Timeline handoff without pretending they are continuous interpolation targets. True blend crossfade and visibility fade remain pending.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline layer opacity interpolation

Scope:
- Added `rrkal_displaytools.timeline_layer_opacity_interpolation.v1`.
- Renderer playback now interpolates layer opacity between active and next Timeline keyframes.
- Timeline PNG/GIF export manifests now record interpolated layer opacity per frame.
- Qt/No-GUI launch packets, renderer ack, renderer capabilities, closed-loop status, docs, and smoke gates now expose the layer opacity interpolation contract.

Positioning:
- This closes the first layer-state interpolation path while keeping layer blend mode and visibility interpolation explicitly pending.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline PNG frame sequence export

Scope:
- Added `rrkal_displaytools.timeline_animation_export.v1`.
- Renderer now supports `--timeline-export-dir`, `--timeline-export-frames`, `--timeline-export-fps`, and `--timeline-export-manifest`.
- Export writes PNG frames plus `timeline_animation_manifest.json`, using active Timeline keyframes and ocean/material interpolation.
- Qt/No-GUI launch packets, renderer ack, renderer capabilities, closed-loop status, docs, and smoke gates now expose the export contract.

Positioning:
- This closes a first renderer animation export loop for scientific review while leaving video encoding, camera keyframes, and non-material interpolation pending.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline ocean material interpolation

Scope:
- Added `rrkal_displaytools.timeline_ocean_material_interpolation.v1`.
- Renderer now interpolates Timeline ocean material fields (`wave_strength`, `roughness`, `foam`) across the active segment while playback is active.
- Qt launch/provenance packets, No-GUI runtime state, renderer ack payloads, renderer capabilities, closed-loop status, docs, and smoke gates now expose the interpolation contract.
- Style, layers, pins, boundary, camera, and export remain discrete/pending.

Positioning:
- This turns Timeline playback from whole-keyframe stepping into a first continuous renderer behavior without overclaiming full animation export.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Renderer Timeline discrete step playback

Scope:
- Added `rrkal_displaytools.timeline_step_playback.v1`.
- Renderer now advances Timeline playback by whole keyframes when `timeline_state.playback.active` is true and the interval elapses.
- Ack/runtime/capabilities expose step playback support, current index, interval, step count, and pending interpolation/export boundaries.
- Qt and No-GUI launch packets now advertise renderer discrete step playback instead of ack-only playback.

Positioning:
- This closes renderer-side discrete keyframe playback before ocean/material interpolation, camera keyframes, and animation export.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline active segment selection

Scope:
- `timeline_segment_state` now reports the active keyframe segment derived from the current active step instead of always reporting the first segment.
- Qt, No-GUI launch/runtime state, renderer ack, smoke, and docs now use `active_segment_preview`.
- This keeps playback/export pending while making the segment handoff match the selected step.

Positioning:
- This closes the discrete active-step segment handoff needed before renderer-side step playback.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline active step renderer startup apply

Scope:
- Renderer startup Timeline apply now selects the keyframe identified by `timeline_active_step_state` instead of always selecting the first valid keyframe.
- `timeline_first_keyframe_apply` now includes the active step packet and selected active index, while keeping the existing schema for compatibility.
- Smoke now gates the nested active step packet in the renderer Timeline ack endpoint.

Positioning:
- This closes the discrete startup keyframe selection loop before adding inter-keyframe interpolation or animation export.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline active step state contract

Scope:
- Added `rrkal_displaytools.timeline_active_step_state.v1`.
- Qt launch/provenance packets, No-GUI launch packets, Timeline runtime state, renderer ack payloads, renderer capabilities, closed-loop status, docs, and smoke gates now expose requested/active keyframe index and active keyframe id.
- This does not claim renderer timeline playback yet; it gives renderer startup and future playback code a stable discrete step selection contract.

Positioning:
- This is the next reversible step after segment state, preparing renderer startup to apply the active Timeline step instead of assuming the first keyframe.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline active segment contract

Scope:
- Added `rrkal_displaytools.timeline_segment_state.v1`.
- Qt launch/provenance packets, No-GUI launch packets, Timeline runtime state, renderer ack payloads, renderer capabilities, closed-loop status, docs, and smoke gates now expose the first active segment, segment count, interpolatable fields, and discrete fields.
- Segment state does not claim renderer step playback yet; it fixes the handoff shape for the next playback loop.

Positioning:
- This prepares renderer-side Timeline step playback without mixing in animation export.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline first keyframe Pins and Boundary apply

Scope:
- Renderer startup first-keyframe apply now also applies Timeline keyframe Pins and Boundary highlight state.
- Pin input ack and Boundary highlight ack are rewritten after Timeline first-keyframe apply when those states change.
- `timeline_first_keyframe_apply.changed` now reports pins, selected pin, and boundary highlight changes.

Positioning:
- This closes the remaining first-keyframe renderer apply gap before inter-keyframe animation/export work.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Renderer startup first Timeline keyframe apply

Scope:
- Added `rrkal_displaytools.timeline_first_keyframe_apply.v1`.
- Renderer startup can apply the first Timeline keyframe's style profile, ocean material values, layer visibility/opacity/blend state, and selected layer from the runtime state.
- Renderer ack and capabilities now expose first-keyframe apply status while keeping Pins, Boundary, inter-keyframe animation, and export pending.

Positioning:
- This is the first renderer-side Timeline behavior beyond acknowledgement, without claiming full playback.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline playback plan contract

Scope:
- Added `rrkal_displaytools.timeline_playback_plan.v1`.
- Qt launch/provenance packets, No-GUI launch packets, Timeline runtime state, renderer ack payloads, renderer capabilities, closed-loop status, docs, and smoke gates now expose ordered keyframes, segment count, planned apply scope, and the ack-only renderer boundary.
- The plan does not claim renderer timeline playback; it fixes the input contract for the next interpolation work.

Positioning:
- This is the smallest reversible step from Timeline handoff toward renderer-side playback.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline playback readiness contract

Scope:
- Added `rrkal_displaytools.timeline_playback_readiness.v1`.
- Qt launch/provenance packets, No-GUI launch packets, Timeline runtime state, renderer ack payloads, renderer capabilities, closed-loop status, docs, and smoke gates now expose whether Timeline supports Qt preview playback, renderer ack, renderer playback, and animation export.
- The contract explicitly keeps renderer timeline playback/export pending instead of implying support.

Positioning:
- This improves cross-machine handoff clarity before implementing renderer-side animation playback.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Reveal selected layer row

Scope:
- Layers panel now includes `Reveal selected`.
- The action clears the row filter when it hides the active layer and expands the active layer's group when needed.
- `layer_filter.selected_layer_reveal_available` is now exposed in Qt state, No-GUI launch packets, profile schema, closed-loop status, docs, and smoke gates.

Positioning:
- This closes the common researcher workflow where a layer remains selected but its row is hidden by filter/collapse; renderer layer state remains unchanged.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Layer group active selection diagnostics

Scope:
- `layer_group_view` now records per-group visible/total row counts.
- The active layer's group and hidden-by-collapse state are exposed in Qt status, profiles, launch packets, provenance, No-GUI export, profile schema, closed-loop status, and smoke gates.
- The Layers panel now tells researchers when the selected layer still exists but is hidden by a collapsed row group.

Positioning:
- This closes a small UIUX ambiguity from the group collapse workflow without changing renderer visibility or layer runtime state.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Layer group collapse view

Scope:
- Layers panel now has group collapse/expand controls for Hydro, Sea, Traffic, and Aids row groups.
- `layer_group_view` records available groups, collapsed groups, visible row count, and the renderer-state boundary.
- `layer_filter` now reports visible matched layers after group collapse.
- Profiles, launch packets, provenance, No-GUI launch export, profile schema, renderer capabilities, closed-loop status, and smoke gates now expose `rrkal_displaytools.layer_group_view.v1`.

Positioning:
- This adds Photoshop-like layer group navigation for researchers while keeping group collapse separate from renderer visibility.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Layer filter select-first action

Scope:
- Layers filter row now includes `Select first`.
- `layer_filter` state now records `first_matched_layer` and `selected_layer_visible`.
- The filter status label reports whether the active layer is visible under the current filter.
- Smoke now gates `layer_filter.first_matched_layer`.

Positioning:
- This completes a practical filter-to-selection loop for researchers who narrow the layer list and need to immediately target the first matching layer.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Layer filter focus presets

Scope:
- Layers panel row filter now has Hydro, Maritime, Traffic, Aids, and All focus preset buttons.
- `layer_filter` state now records `preset` and `available_presets`.
- The filter aliases include hydrology, maritime boundaries, traffic, Pins, and visual aids terms.
- No-GUI launch packets, profile schema, closed-loop status, and smoke gates now expose the focus preset contract.

Positioning:
- This gives researchers one-click layer focus without changing renderer visibility, preserving the distinction between UI navigation and rendering state.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Layer row search filter

Scope:
- Layers panel now has a row search/filter box with a clear action and match count label.
- Filtering matches layer key, visible label, and renderer flag text; it hides rows only and does not change renderer layer state.
- Qt profiles, launch packets, provenance, No-GUI launch export, profile schema, renderer capabilities, and closed-loop status now expose `rrkal_displaytools.layer_filter.v1`.
- Smoke now gates launch packet `layer_filter` and renderer `ui_handoff_contracts.layer_filter`.

Positioning:
- This improves researcher control of dense layer stacks while preserving the separation between UI row filtering and renderer visibility.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Limited automatic document snapshots

Scope:
- Document snapshot undo now performs limited automatic capture before high-impact UI state changes.
- Auto capture points cover profile apply, renderer preset apply, Timeline keyframe apply/clear, and layer stack resets.
- Document history status now reports auto snapshot count.
- Launch packet `document_undo` now exposes `limited_automatic_change_capture` and `auto_capture_points`.
- Smoke now gates the limited automatic capture contract.

Positioning:
- This improves recovery for researcher-facing UI workflows without claiming complete operation-level history or a persisted lab notebook.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Document history depth label

Scope:
- History panel now shows a document history status label.
- The label reports manual snapshot mode, undo depth, redo depth, capacity, and the automatic-change-capture boundary.

Positioning:
- This makes the new document snapshot undo/redo loop visible to researchers instead of hiding state in provenance JSON only.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Manual document snapshot undo

Scope:
- History panel now provides Snapshot / Undo / Redo controls for manual document snapshots.
- Snapshots capture the Qt profile state, including renderer controls, layer UI state, tools, Pins, Boundary highlight, Canvas Preview, and Timeline keyframes.
- Launch packets and research provenance now include `document_undo`.
- No-GUI launch packet export reports the same `rrkal_displaytools.document_snapshot_undo.v1` contract.
- Renderer capabilities now list `document_undo` in `ui_handoff_contracts`.
- Smoke now gates launch packet `document_undo` and renderer capability discovery.

Positioning:
- This closes a usable manual global snapshot undo/redo loop for UIUX work while keeping automatic change capture, operation-level history, and persisted lab notebook explicitly pending.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline ack smoke endpoint

Scope:
- Renderer now supports `--ack-timeline-state-and-exit`.
- The endpoint reads `--timeline-state-file`, writes `--timeline-ack-file`, prints `rrkal_displaytools.renderer_timeline_ack.v1`, and exits before Taichi initialization.
- Renderer capabilities now list the ack endpoint control.
- Smoke now validates the no-GUI Timeline runtime JSON through the renderer ack endpoint.

Positioning:
- This closes Timeline receipt verification for smoke/cross-machine checks without starting the full renderer or claiming animation playback.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - No-GUI Timeline state file export

Scope:
- `scripts/export_launch_packet.py` now supports `--timeline-state-out`.
- When provided, the exporter writes `rrkal_displaytools.timeline_runtime_state.v1` to that path.
- The generated launch packet and portable command now point `--timeline-state-file` at the written file.
- Smoke now gates the written runtime JSON and the portable command path.

Positioning:
- This makes the cross-machine no-GUI Timeline handoff runnable without manually extracting JSON from the launch packet.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - No-GUI Timeline runtime payload

Scope:
- No-GUI launch packet export now includes `timeline_runtime_state`.
- The payload is shaped as `rrkal_displaytools.timeline_runtime_state.v1` and can be saved to `state/renderer_timeline_state.json` before launching the renderer.
- Smoke now gates the runtime payload schema and nested `timeline_state` schema.
- Capability summary now documents the cross-machine no-GUI payload path.

Positioning:
- This closes the portable launch-packet side of Timeline state handoff without adding renderer playback/export behavior.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline renderer acknowledgement handoff

Scope:
- Qt now writes `state/renderer_timeline_state.json` from the Timeline dock/profile state.
- Qt launch commands pass `--timeline-state-file` and `--timeline-ack-file`.
- Renderer reads the Timeline runtime state on startup and writes `state/renderer_timeline_ack.json`.
- The ack records received state, runtime schema, Timeline schema, keyframe count, playback mode, and pending renderer playback/export work.
- Launch packets, provenance, closed-loop status, renderer capabilities, and smoke gates now expose the Timeline state/ack contract.

Positioning:
- This closes Timeline handoff as a renderer receipt loop without claiming renderer-side animation playback, interpolation, or export.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline renderer handoff capability

Scope:
- Renderer capabilities now expose `timeline_handoff`.
- The capability lists Timeline state/keyframe input contracts, applied Qt/launch/provenance/no-GUI handoff paths, and pending renderer playback/export work.
- Smoke now gates `capabilities.timeline_handoff.schema`.
- Closed-loop status evidence now links Timeline panel status to renderer capability discovery.

Positioning:
- This makes Timeline handoff inspectable from renderer capability discovery without overclaiming renderer animation playback.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline No-GUI keyframe handoff

Scope:
- No-GUI launch packet export now summarizes profile `timeline_keyframes` into `timeline_state`.
- `timeline_state` now reports `profile_keyframes_present` and keyframe count from the source profile.
- Smoke now gates `profile_timeline_keyframe_handoff`.
- Closed-loop status now lists No-GUI profile keyframe handoff for the Timeline panel.

Positioning:
- This makes Timeline keyframes portable in launch packets even when exporting from scripts instead of opening Qt.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline UI playback controls

Scope:
- Timeline dock now has `Next`, `Play UI preview`, and `Stop`.
- UI playback loops through stored keyframes and applies them to the Qt state at a fixed interval.
- `timeline_state` now reports playback mode, active state, interval, and next keyframe index.
- Closed-loop smoke now gates `qt_timeline_panel` for UI-only playback controls.

Positioning:
- This closes Timeline playback as a Qt-side UI preview loop without claiming renderer timeline playback or animation export.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline keyframe restore

Scope:
- Timeline dock now has `Apply selected`.
- Applying a keyframe restores renderer/profile controls, ocean material controls, layer stack snapshot, Pins, and Boundary highlight state.
- Timeline keyframes now also capture `taichi_arch`.
- Closed-loop status now marks UI-only keyframe restore as applied.

Positioning:
- This closes the front-end Timeline save/restore loop while keeping playback/export as future renderer work.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline profile persistence

Scope:
- Qt profiles now save `timeline_keyframes`.
- Profile loading restores the Timeline keyframe list and status label.
- `profile_schema.py` now accepts optional `timeline_keyframes`.

Positioning:
- This makes UI-only Timeline state survive profile save/load while playback/export remain future renderer work.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline UI keyframe storage

Scope:
- Timeline dock now stores UI-only keyframes.
- Each keyframe captures style/topography/data mode, ocean material controls, selected layer, layer stack snapshot, Pins, and Boundary highlight state.
- `timeline_state` now reports keyframe count and keyframe summaries.
- Closed-loop status now marks UI-only keyframe storage as applied while playback/export remain pending.

Positioning:
- This makes Timeline useful for researcher-facing state capture without claiming renderer animation playback is complete.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline handoff discovery

Scope:
- Renderer `ui_handoff_contracts` now lists `timeline_state`.
- `scripts\inspect_handoff.ps1` now reports launch packet `timeline_state`.
- Smoke now gates the handoff inspection `timeline_state` contract.

Positioning:
- This keeps capability discovery and clone-time handoff inspection aligned with the new Timeline UI status contract.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline UI status contract

Scope:
- Added a visible Qt Timeline dock with construction markers.
- Qt launch packet and research provenance now include `timeline_state`.
- No-GUI launch packet export includes the same schema as a status contract.
- Closed-loop status now tracks `qt_timeline_panel` as partial, with keyframe storage/playback/export still pending.
- Smoke now gates launch packet `timeline_state`.

Positioning:
- This gives the Photoshop-like workspace an honest Timeline surface without claiming renderer animation playback is complete.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Clone quickstart handoff inspection

Scope:
- Rewrote `docs/QUICKSTART_CLONE.zh-TW.md` as clean zh-TW quickstart text.
- Added `scripts\inspect_handoff.ps1` as the first cross-machine contract inspection step before smoke/Qt launch.
- Clarified runtime artifacts and RRKAL/displaytools boundaries for cloned workstations.

Positioning:
- This makes the clone-to-Qt path readable and reduces startup ambiguity on another Windows machine.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Handoff inspection script

Scope:
- Added `scripts/inspect_handoff.ps1`.
- The script prints a read-only JSON summary of renderer UI handoff capabilities, closed-loop ids, partial ids, launch packet contracts, and the RRKAL/displaytools boundary.
- Smoke now gates the handoff inspection schema and `session_journal` contract.

Positioning:
- This improves cross-machine clone diagnostics without opening Qt and without adding displaytools-side dataset discovery, download, import, or cache governance.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Renderer UI handoff capability discovery

Scope:
- Renderer capabilities now expose `ui_handoff_contracts`.
- The capability lists `canvas_preview`, `active_layer_diagnostics`, `layer_undo`, `session_journal`, and `boundary_highlight.identity_status`.
- Smoke now gates `capabilities.ui_handoff_contracts.schema`.
- Closed-loop evidence now links diagnostics handoff to renderer capability discovery.

Positioning:
- This lets another machine inspect UIUX handoff support without opening Qt, while keeping data discovery/cache governance outside displaytools.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Session journal handoff contract

Scope:
- Qt launch packet and research provenance now include `session_journal`.
- No-GUI launch packet export includes the same schema with a no-runtime-history marker.
- Closed-loop status now includes `session_journal_handoff`.
- Smoke now gates launch packet `session_journal` and the closed-loop id.

Positioning:
- This makes recent layer runtime history, Pin pick history, ack presence, and layer undo depth portable without claiming to be a persisted lab notebook or global document history.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Layer undo handoff contract

Scope:
- Qt launch packet and research provenance now include `layer_undo`.
- No-GUI launch packet export includes the same schema with a no-runtime-stack marker.
- Closed-loop status now includes `layer_stack_undo_snapshots`.
- Smoke now gates launch packet `layer_undo` and the closed-loop id.
- `layer_undo` explicitly marks global document undo as pending, so the contract does not overclaim scope.

Positioning:
- This makes the local layer undo UIUX loop visible in handoff/provenance contracts without claiming full document-wide undo.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Layer stack undo snapshots

Scope:
- Layers panel now keeps a bounded layer undo stack for visibility, lock, opacity, blend mode, and active layer state.
- Added an `Undo 圖層狀態` action and a Layer undo status label.
- History now records layer undo snapshot saves and distinguishes this local layer undo from the still-pending global document undo stack.

Positioning:
- This closes a practical Photoshop-like undo loop for layer controls without pretending to implement full document-wide undo.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Diagnostics handoff closed-loop status

Scope:
- Closed-loop status now includes `diagnostics_handoff_contracts`.
- Boundary highlight partial status now lists boundary identity-status handoff as applied.
- Smoke now parses closed-loop status and fails if that closed-loop id is missing.

Positioning:
- This keeps `--print-closed-loop-status` aligned with the launch packet, capabilities, and profile schema contracts.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Boundary renderer sync wording

Scope:
- Boundary highlight default `renderer_sync` now reports `renderer_line_fill_identity_status_handoff`.
- Renderer default boundary sync text now reports acknowledged line/fill/identity-status behavior.
- Profile schema docs no longer describe Boundary highlight as only a UI/profile pending contract.

Positioning:
- This removes stale contract wording after line highlight, closed-ring fill, and identity-status handoff were closed.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Boundary identity status summary

Scope:
- Properties panel now shows a `Boundary identity` summary beside Boundary highlight controls.
- The summary reports applied/pending identity-status counts and the non-authoritative boundary note.
- Capability summary now documents the user-visible status row.

Positioning:
- This makes the boundary/EEZ identity limitation visible without requiring users to open JSON or the settings dialog.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Boundary identity status handoff

Scope:
- Qt Boundary highlight state now carries `identity_status`.
- Renderer boundary normalization and ack preserve the same identity-status contract.
- No-GUI launch packets add `boundary_highlight.identity_status` even when repo templates do not define it yet.
- Profile schema, renderer capabilities, smoke, and docs now expose the boundary identity-status schema.

Positioning:
- This makes the legal/scientific boundary of the current highlight mask portable in profile/launch packet handoff.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Boundary highlight identity status copy

Scope:
- Boundary highlight dialog now distinguishes live source-property feature identity from pending authoritative territory/EEZ identity.
- Boundary highlight history entries no longer use a construction marker for ordinary UI updates.
- Capability summary now documents the identity-status wording.

Positioning:
- This keeps the research UI honest: visual emphasis and source properties are live, but legal/authoritative area ownership inference remains pending.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Live preview status wording cleanup

Scope:
- Capability summary no longer lists embedded live preview as unfinished.
- Module boundaries now mark Qt Canvas Preview state/static thumbnail/file-based live renderer frame as closed.
- Remaining renderer preview pending item is narrowed to low-latency IPC/GPU texture streaming.

Positioning:
- This removes status drift after the file-based live preview loop was closed.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Active layer diagnostics capability

Scope:
- Renderer capabilities now expose `active_layer_diagnostics`.
- Smoke now gates `capabilities.active_layer_diagnostics.schema`.
- Capability summary now documents the contract as part of renderer capability discovery.

Positioning:
- This keeps capability discovery aligned with the Qt/provenance/no-GUI handoff contract.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Active layer diagnostics handoff

Scope:
- Qt launch packets now include `active_layer_diagnostics`.
- Research provenance now includes the same selected layer, renderer target, diagnostics text, runtime ack, and pick state snapshot.
- No-GUI launch packets now include the same contract with a no-runtime-evidence marker.
- Smoke now gates `active_layer_diagnostics.schema`.

Positioning:
- This makes active layer renderer evidence portable instead of only visible in the live Qt Properties panel.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Active layer renderer diagnostics

Scope:
- Properties active layer inspector now shows the selected layer's renderer target alias.
- The same inspector summarizes the latest renderer runtime ack target/frame and layer pick target/hit/feature.
- Ack and pick polling now refresh the active layer inspector immediately, not only the Layers dock bridge labels.

Positioning:
- This makes the Photoshop-like layer workflow more useful for researchers by keeping UI layer state, renderer target, and pick evidence in one place.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Quick render smoke verifies preview frame

Scope:
- `scripts/render_quick_smoke.ps1` now passes `--preview-frame-file`.
- The script now verifies that the preview frame PNG exists and is non-empty.
- The quick render path disables hydrology, maritime boundary, aircraft, and Pin vector layers so it stays a bounded synthetic renderer smoke.
- Clone quickstart and capability summary now document the extra quick smoke artifact.

Positioning:
- This verifies real renderer preview frame output in the optional render smoke without making the lightweight pre-commit smoke heavier.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.
- Quick render smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\render_quick_smoke.ps1`.

## 2026-05-29 - Canvas preview stream provenance

Scope:
- Qt `canvas_preview` state now records `preview_frame_path` and `preview_frame_interval_s`.
- No-GUI launch packets use the same live preview path and interval fields.
- Profile schema validation and smoke now gate those fields.

Positioning:
- This makes live preview observable in profiles, launch packets, and provenance instead of only being implicit in the command line.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Navigator live preview wording

Scope:
- Navigator dock no longer labels live renderer thumbnail as under construction.
- The dock now points users to the central Canvas Preview for live renderer pixels.

Positioning:
- This keeps the Qt UI copy aligned with the newly closed file-based live preview loop.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Launch packet preview frame handoff

Scope:
- No-GUI launch packet exporter now includes `--preview-frame-file state/renderer_preview_frame.png`.
- Default no-GUI canvas preview state now reports `renderer_sync` as `ui_state_preview`.
- Smoke now fails if the exported portable command omits `--preview-frame-file`.

Positioning:
- This closes the live preview handoff path for users who export launch packets without opening Qt.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Clone quickstart for live preview

Scope:
- README now lists Canvas Preview state / thumbnail / live preview as a Qt panel capability.
- Clone quickstart now documents how to use Live preview after launching the Qt panel.
- Quickstart now names `state/renderer_preview_frame.png` as a local runtime bridge artifact that should not be committed.

Positioning:
- This improves cross-machine usage without adding displaytools-side dataset discovery, download, import, or cache governance.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - File-based renderer live preview stream

Scope:
- Renderer now accepts `--preview-frame-file` and `--preview-frame-interval`.
- During render loops, renderer writes the current `frame_rgba` into an atomically replaced PNG for Qt preview.
- Qt launch commands pass `state/renderer_preview_frame.png`, and Canvas Preview can switch to `live_file_stream` mode with automatic polling.
- Smoke now checks that renderer capabilities expose `preview_frame_stream.schema == rrkal_displaytools.preview_frame_stream.v1`.

Positioning:
- This closes a minimal live renderer preview loop without adding another UI backend or mixing Tk.
- The future renderer preview upgrade is low-latency IPC/GPU texture streaming, not displaytools data governance.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Smoke gate for canvas preview handoff

Scope:
- `scripts/smoke.ps1` now parses the no-GUI launch packet from `fast_synthetic`.
- Smoke fails if the exported launch packet does not include `canvas_preview.schema == rrkal_displaytools.canvas_preview.v1`.

Positioning:
- This makes the Canvas Preview profile/no-GUI handoff contract verifiable in the required pre-commit smoke gate.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Canvas thumbnail auto-refresh

Scope:
- Qt thumbnail mode now polls `state/showcase/*.png` every 1.5 seconds.
- When the referenced renderer PNG changes or a newer showcase PNG appears, Canvas Preview refreshes without another manual click.
- Closed-loop status now distinguishes static thumbnail auto-refresh from the still-pending live renderer frame stream.

Positioning:
- This makes the current static renderer preview usable during iterative headless/showcase renders.
- It is not a live renderer stream; live frame streaming remains future work.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Canvas preview no-GUI handoff

Scope:
- No-GUI launch packet export now includes the `canvas_preview` contract.
- Repo-shared profile templates now carry a default `canvas_preview` state-mode block.

Positioning:
- This keeps Qt-saved profiles, built-in templates, and script-exported launch packets aligned.
- Static thumbnail references remain UI/provenance state; runtime PNG files remain ignored.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Canvas preview profile state

Scope:
- Added optional `canvas_preview` state to Qt profiles and launch packets.
- The contract records state-vs-thumbnail mode plus an optional renderer PNG reference path.
- Profile loading restores thumbnail mode when the referenced PNG exists, falls back to the latest `state/showcase/*.png`, then falls back to state preview.
- Updated profile schema validation and docs for `rrkal_displaytools.canvas_preview.v1`.

Positioning:
- This closes the static renderer thumbnail UI state loop across profile save/load and launch packet handoff.
- Live renderer frame streaming remains future work.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Maritime feature identity keys

Scope:
- Expanded GeoJSON vector feature identity extraction for Natural Earth and Marine Regions style keys.
- Pick JSON now records `identity_source`, `identity_keys`, and preview properties such as GEONAME, TERRITORY1/2, SOVEREIGN1/2, ISO codes, MRGID, and policy/type fields when present.
- Renderer capabilities and closed-loop status now mark maritime property key identity as applied source-property behavior.

Positioning:
- This improves researcher-facing boundary/EEZ inspection without pretending to resolve official disputes.
- Authoritative polygon territory identity and open-line area inference remain separate future work.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - RRKAL handoff boundary status

Scope:
- Closed-loop status now treats RRKAL manifest validation/ingest/governance as an external dependency instead of a displaytools pending item.
- Renderer output provenance still marks `--rrkal-data-manifest-ref` passthrough and image metadata sidecars as applied displaytools behavior.

Positioning:
- This keeps displaytools focused on visualization, Qt UI, renderer bridge, and provenance references.
- Dataset discovery/download/import/cache governance remains RRKAL-owned.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Qt renderer thumbnail preview

Scope:
- Added a Canvas Preview mode for the latest `state/showcase/*.png` renderer output.
- Added UI actions to switch between Qt Canvas state preview and Renderer thumbnail preview.
- Provenance and closed-loop status now distinguish static renderer output thumbnails from the still-pending live renderer frame stream.

Positioning:
- This gives researchers an embedded renderer visual check without adding a live streaming architecture yet.
- Live frame streaming remains future work.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Qt launcher smoke gate

Scope:
- `scripts/run_qt_panel.ps1` now prefers the repo `.venv` Python when available, then falls back to `py -3`.
- Added optional `-SmokeFirst` to run the project smoke check before opening the Qt panel.
- Quickstart, README, capability summary, and closed-loop evidence now point to the launcher as the cross-machine Qt entry.

Positioning:
- This improves clone-to-UI startup without adding dataset discovery, download, import, or cache governance.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Boundary closed-ring area hit

Scope:
- Added conservative screen-space interior hit testing for fully visible closed boundary rings.
- Boundary hover and selected-layer boundary picking still prefer line proximity, then fall back to closed-ring area hits.
- Renderer boundary highlight ack/capabilities and closed-loop status now mark `closed_ring_area_hit_test` as applied.

Positioning:
- This lets researchers point inside available closed rings and still trigger feature-linked highlight behavior.
- Authoritative polygon territory identity and open-line area inference remain separate future work.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Boundary highlight fill tone controls

Scope:
- Added a dedicated closed-ring polygon fill tone path for Boundary highlight.
- Fill preview now applies the same RGB, contrast, and gamma controls as the outline path, with a more restrained tone so the mask does not overpower vector lines.
- Renderer boundary highlight ack/capabilities and closed-loop status now mark `closed_ring_fill_contrast_gamma` as applied.

Positioning:
- This closes fill shader contrast/gamma for the current closed-ring fill preview.
- Authoritative polygon territory identity and open-line area inference remain separate future work.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Qt layer pick feature label

Scope:
- Qt layer pick status now reads `pick_result.hit_detail.feature` from the renderer bridge.
- When a boundary or hydrology vector hit includes source-property identity, the Layers status label shows the feature label directly.

Positioning:
- This tightens the selected-layer picking loop for researcher-facing inspection.
- Authoritative polygon territory identity and open-line area inference remain separate future work.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Vector pick source-property identity

Scope:
- GeoJSON vector loading now keeps a compact source-property identity per rendered line.
- Boundary and hydrology line hit tests now include `feature.label`, `feature_index`, geometry type, and a small properties preview when available.
- Selected-layer pick state and renderer selected-info text can now show feature identity instead of only layer/line index.

Positioning:
- This closes source-property feature identity for loaded line/ring geometry.
- Authoritative polygon territory identity and open-line area inference remain separate future work.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - RRKAL manifest reference passthrough

Scope:
- Added optional Qt `RRKAL manifest ref` input.
- Added renderer CLI `--rrkal-data-manifest-ref` / `RRKAL_DATA_MANIFEST_REF`.
- Qt launch packets, no-GUI launch packets, research provenance, renderer capabilities, and output metadata sidecars now record the reference.
- The profile schema contract documents `renderer.rrkal_data_manifest_ref` as an optional renderer field.

Positioning:
- This closes a reference-only handoff loop for future RRKAL data manifest linkage.
- Displaytools still does not discover, download, validate, import, or govern manifests.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Quick render smoke metadata check

Scope:
- `scripts/render_quick_smoke.ps1` now verifies the rendered image exists.
- The script also verifies the `.metadata.json` sidecar exists and has schema `rrkal_displaytools.renderer_output_metadata.v1`.
- Clone quickstart now documents the optional quick render smoke output pair.

Positioning:
- Renderer output provenance is now script-verifiable beyond regular compile/profile smoke.
- This does not make quick render smoke part of the mandatory pre-commit smoke because it can be heavier than syntax/profile checks.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Renderer output metadata sidecar

Scope:
- Headless/once image output now writes a `.metadata.json` sidecar next to the rendered image.
- The sidecar records style/topography/data mode, visible layers, opacity/blend state, selected-layer target, latest pick result, boundary highlight state, closed-loop status, and RRKAL/displaytools ownership boundary.

Positioning:
- This starts closing renderer output artifact provenance without taking over RRKAL data manifest governance.
- Full RRKAL data manifest linkage remains a later integration point.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - No-GUI launch packet status parity

Scope:
- `scripts/export_launch_packet.py` now includes the shared `closed_loop_status` snapshot.
- The no-GUI renderer arg builder now includes the `pin_layer` / `--pin-layer` flag, matching the Qt panel layer stack.

Positioning:
- GUI and no-GUI launch packets now expose the same closed-loop status contract.
- This improves cross-machine handoff and keeps Pin layer launch behavior consistent.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Shared closed-loop status contract

Scope:
- Added `closed_loop_status.py` as a shared contract module.
- Renderer capabilities, the standalone closed-loop endpoint, and Qt launch packets now use the same status packet source.
- Smoke now py-compiles the shared status contract.

Positioning:
- This prevents capability discovery and launch packet handoff from drifting.
- It also establishes a small contracts-style module without moving data governance into displaytools.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Closed-loop status endpoint

Scope:
- Added `--print-closed-loop-status` as a no-GUI endpoint.
- Added Qt actions/menu/quick-tool entry to display the closed-loop status JSON.
- Added the endpoint to `scripts/smoke.ps1`.

Positioning:
- Scripts and researchers can inspect current closed/partial/pending status without parsing full renderer capabilities.
- This strengthens renderer capability discovery and cross-machine checks.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Capability closed-loop status packet

Scope:
- Added `closed_loop_status` to renderer capabilities JSON.
- The packet lists closed loops, partial loops, pending gaps, and the bridge/control evidence for each category.

Positioning:
- This makes renderer capability discovery more useful for scripts and cross-machine checks.
- No runtime behavior changed.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - README current-entry refresh

Scope:
- Updated `README.md` to point at the clone quickstart and module boundary docs.
- Refreshed the current focus and Qt capability list to include runtime layer sync, selected-layer picking, layer pick JSON, and boundary closed-ring fill preview.

Positioning:
- This makes the public GitHub landing page match the current functional state.
- No runtime behavior changed.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Cross-machine clone quickstart

Scope:
- Added `docs/QUICKSTART_CLONE.zh-TW.md`.
- Documented clone, venv setup, dependency install, smoke test, Qt panel launch, bridge files, and RRKAL/displaytools responsibility boundary.

Positioning:
- This improves use from another computer through GitHub.
- Runtime state files remain local and should not be committed.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Module boundary note

Scope:
- Added `docs/MODULE_BOUNDARIES.zh-TW.md`.
- Documented displaytools ownership, RRKAL ownership, suggested split order, and bridge/governance rules.
- Marked current closed loops and remaining extraction-sensitive gaps.

Positioning:
- This gives future refactors a clear boundary without moving code yet.
- The note explicitly keeps discovery/download/import/cache governance out of displaytools.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Layer pick JSON inspector

Scope:
- Added a Layers panel action to show `renderer_layer_pick_state.json` directly in the central text area.
- The existing layer runtime JSON inspector remains available for control-state debugging.

Positioning:
- Researchers can now inspect the raw renderer pick evidence, not only the short Layer pick label.
- This improves UI observability without adding data governance responsibilities to displaytools.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Boundary closed-ring fill preview

Scope:
- Boundary highlight rendering now fills the hovered line when the source geometry is a closed lon/lat ring.
- Fill alpha follows the existing highlight alpha and breathing controls, while outline/glow remains active.
- Renderer boundary highlight ack/capabilities now distinguish closed-ring polygon fill preview from full territory feature identity and open-line area inference.

Positioning:
- This is an honest partial polygon-mask closure for datasets that already provide closed rings.
- It does not invent country/EEZ area ownership from open boundary lines.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - UI construction label cleanup

Scope:
- Updated stale Qt labels that still called lock/opacity/blend UI-only or renderer-sync pending.
- Removed Brush/Mask from the active History construction list because it is intentionally out of this UI round.
- Boundary highlight UI copy now states line mask/picking is live while polygon fill remains pending.

Positioning:
- This keeps the Photoshop-inspired UI honest for researchers using the current build.
- No renderer behavior or data governance changed in this step.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Hydrology selected-layer picking

Scope:
- Selected lake and river layers now use renderer line hit testing when clicked.
- Layer pick state can report `hydrology_line` results with layer ID, line index, distance, and screen position.
- Renderer capabilities now keep polygon fill mask as the remaining selected-layer picking gap.

Positioning:
- This gives researchers a direct inspection loop for hydrology layers without changing data/provider governance.
- Boundary polygon fill remains separate because it requires area geometry/mask behavior rather than line hit testing.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Layer pick state bridge

Scope:
- Renderer selected-layer pick results now write `state/renderer_layer_pick_state.json`.
- Qt launch commands pass `--layer-pick-state-file`, and the Layers panel reads the file to show event, target, picker, hit state, frame, and timestamp.
- Research provenance now includes the layer pick state path and latest payload.

Positioning:
- This closes the selected-layer picking feedback loop between renderer and Qt panel.
- Remaining picking work is polygon fill masks and hydrology feature picking.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Selected-layer scoped renderer picking

Scope:
- Renderer mouse clicks now route through the selected renderer layer target before falling back to legacy global picking.
- Selected Pin layers pick only Pins; selected aircraft/vehicle icon layers pick traffic points; selected boundary layers pick the matching boundary line segment.
- Non-pickable selected layers no longer accidentally select unrelated Pins or vehicles.

Positioning:
- This turns the selected-layer bridge into a renderer interaction loop useful for scientific layer/object inspection.
- Polygon fill masks and hydrology feature picking remain separate renderer work.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Selected layer semantic target bridge

Scope:
- Qt layer runtime payload now exports `selected_renderer_layer` and a `selected_layer_semantic_target` packet.
- Renderer maps the selected Qt layer key to a renderer layer ID, stores the semantic target, and reports it in `renderer_layer_runtime_ack.json`.
- Renderer capabilities now mark `selected_layer_semantic_target` as applied and keep actual renderer object picking as pending.

Positioning:
- This closes the selected-layer bridge needed before scientific object/layer picking.
- No data discovery, download, import, or cache governance was added to displaytools.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Layer renderer sync metadata

Scope:
- Replaced the Qt layer stack `renderer_sync: planned` placeholder with per-layer live support summaries.
- Launch packets, profiles, runtime bridge payloads, and provenance now distinguish visibility / opacity / blend live status.
- Boundary layers explicitly report per-boundary split blend as pending while aggregate blend remains live.

Positioning:
- This gives researchers a clearer audit trail of which layer controls are live renderer controls versus future compositor work.
- Remaining layer UX work is renderer semantic picking for the selected layer target.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Per-boundary runtime blend split

Scope:
- Preserved individual rendered boundary layer RGBA buffers in addition to the aggregate boundary overlay.
- Final frame composition now applies blend mode per boundary layer for borders, territorial sea, EEZ, and high seas.
- Renderer ack/capabilities now mark per-boundary split blend as applied and keep selected-layer semantic target as the remaining layer runtime pending item.

Positioning:
- This closes the boundary blend loop without changing provider/data governance.
- Remaining layer runtime work is selected-layer semantic/object picking rather than basic visibility/opacity/blend sync.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Boundary aggregate runtime blend

Scope:
- Added runtime blend storage for boundary layer keys.
- Boundary composition now applies the first non-Normal boundary blend mode to the aggregate boundary overlay.
- Renderer ack reports `boundary_aggregate_blend_mode`; capabilities distinguish aggregate boundary blend from pending per-boundary split blend.

Positioning:
- This closes a truthful boundary blend loop for the current aggregate renderer path.
- Remaining boundary blend work is splitting the boundary overlay so borders, territorial sea, EEZ, and high seas can each use different blend modes.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Vehicle icon overlay closure

Scope:
- Added a lightweight renderer vehicle icon overlay for AIS vessels and ADS-B aircraft.
- `vehicle_icons` now controls a real globe-masked overlay with `icon_max_count`, runtime visibility, opacity, and blend mode support.
- Renderer capabilities now include `vehicle_icons` in runtime overlay opacity/blend support and only keep boundary aggregate blend pending.

Positioning:
- This turns the vehicle icon layer from a checkbox/pick-state control into an actual visual layer.
- Remaining layer runtime work is boundary aggregate split/blend and deeper renderer-backed layer/object picking.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Visual aid runtime visibility

Scope:
- Added runtime aliases for `show_grid`, `show_stars`, and `ocean_material`.
- Renderer `set_layer_visible()` now updates `args.show_grid`, `args.show_stars`, `args.ocean_material`, and `args.terrain_contours` with globe dirty flags.
- Added `pin_layer` to the renderer layer manifest visual-aids group.

Positioning:
- This closes the basic visual-aid runtime visibility loop that Qt already exposed in the layer stack.
- Remaining visual layer work is vehicle icon rendering and boundary aggregate blend splitting.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Hydrology runtime blend mode

Scope:
- Added runtime blend support for the independent lake and river overlays.
- Lake/river blend uses the overlay alpha already produced by hydrology opacity, avoiding double opacity application.
- Renderer capabilities now separate supported overlay blend layers from pending boundary aggregate / vehicle icon blend work.

Positioning:
- This extends blend mode closure from point overlays into the hydrology overlays that are already separately composited.
- Remaining blend work is boundary aggregate splitting and vehicle icon overlay implementation.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Overlay runtime blend mode

Scope:
- Added renderer blend compositing modes for runtime overlay layers: Normal, Screen, Multiply, Overlay, and Soft Light.
- Qt `blend_mode` runtime state now applies to the ADS-B aircraft and Pin marker overlays.
- Renderer ack now reports `changed_blend_layers` and current `layer_blend_mode`; capabilities expose overlay blend support separately from vector layer pending work.

Positioning:
- This closes the first visible blend-mode loop for independent overlays without pretending aggregate vector layers are solved.
- Remaining blend work is lake/river/boundary/vector overlay composition and vehicle icon support once it has an independent renderer overlay.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Pin layer runtime visibility opacity

Scope:
- Added `pin_layer` to the Qt layer stack, command boolean flags, baseline preset, and visual-aid group toggle.
- Added `pin_layer` to the shared profile schema and repo profile templates.
- Added renderer runtime alias `pin_layer -> pins`.
- Pin marker overlay alpha now follows Qt runtime opacity before final frame composition.

Positioning:
- This makes scientific Pins controllable as a first-class live layer instead of only as a tool/annotation state.
- Remaining point/icon opacity work is vehicle icons and other independent overlays; blend mode sync remains pending.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Aircraft runtime opacity overlay

Scope:
- Added renderer runtime overlay opacity storage for overlay-only layer alpha controls.
- `aircraft_layer` opacity from Qt runtime state now scales the ADS-B overlay alpha before final frame composition.
- Renderer capabilities expose `aircraft` as a runtime overlay opacity target.

Positioning:
- This extends live opacity sync from vector/scalar layers into one real point overlay without claiming unsupported `vehicle_icons` behavior.
- Remaining point/icon opacity work is vehicle icons, Pins, other independent overlays, blend mode sync, and renderer-backed picking.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - GitHub Actions smoke workflow

Scope:
- Added `.github/workflows/smoke.yml`.
- The workflow installs `requirements.txt` on `windows-latest` and runs `scripts/smoke.ps1` on push and pull request.

Positioning:
- This extends the local pre-commit smoke rule to GitHub-side visibility.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.
## 2026-05-29 - No-GUI launch packet exporter

Scope:
- Added `scripts/export_launch_packet.py` to build launch packets from profile templates without opening Qt.
- Added exporter coverage to `scripts/smoke.ps1` using the `fast_synthetic` template.
- Updated README and GTD for the exporter.

Positioning:
- This gives RRKAL/scripts a direct way to generate displaytools launch state from shared templates.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Shared profile schema validator

Scope:
- Added `profile_schema.py` as the shared profile schema validation module.
- Updated Qt panel profile loading and `scripts/validate_profiles.py` to use the shared validator.

Positioning:
- This reduces drift between UI profile loading and smoke-time template validation.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.
## 2026-05-29 - Qt profile load validation

Scope:
- Added profile payload validation inside `rrkal_displaytools_qt_panel.py` before applying loaded profiles/templates.
- The panel now reports missing schema, renderer, material, layer keys, and non-boolean layer values instead of silently applying partial configuration.

Positioning:
- This protects operator UI state and keeps Qt profile behavior aligned with the smoke validator.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.
## 2026-05-29 - Smoke helper hardening

Scope:
- Updated `scripts/smoke.ps1` so native command failures stop the script.
- Updated `scripts/validate_profiles.py` to read UTF-8 BOM profile JSON files with `utf-8-sig`.

Positioning:
- This makes the new pre-commit smoke rule enforceable instead of only informational.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.
## 2026-05-29 - Profile template smoke validation

Scope:
- Added `scripts/validate_profiles.py` for built-in profile template validation.
- Added profile validation to `scripts/smoke.ps1`.
- Updated README and GTD to reference the validator.

Positioning:
- This protects the RRKAL/displaytools profile handoff shape as templates evolve.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.
## 2026-05-29 - No-GUI profile template listing

Scope:
- Added `--list-templates` to `rrkal_displaytools_qt_panel.py`.
- Added template listing to `scripts/smoke.ps1`.
- Updated README and GTD with the no-GUI template discovery path.

Positioning:
- This gives RRKAL and scripts a lightweight way to discover available displaytools profiles without opening the Qt panel.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.
## 2026-05-29 - Qt startup template loading

Scope:
- Added `--template` to `rrkal_displaytools_qt_panel.py` for loading a built-in profile template by file stem.
- Added `-Template` passthrough to `scripts/run_qt_panel.ps1`.
- Updated README with the shorter template startup command.

Positioning:
- This improves cross-machine startup ergonomics for shared displaytools templates.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.
## 2026-05-29 - Named profile templates

Scope:
- Added `name` and `description` metadata to built-in profile templates.
- Updated the Qt template selector to show `name` when present, falling back to filename when metadata is missing.

Positioning:
- This improves operator clarity without changing renderer behavior.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.
## 2026-05-29 - Qt smoke action uses smoke helper

Scope:
- Updated the Qt panel `Smoke check` action to call `scripts/smoke.ps1` on Windows.
- Kept the existing Python/PowerShell fallback for environments where the helper script is unavailable.

Positioning:
- This keeps panel smoke checks aligned with the pre-commit smoke path.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.
## 2026-05-29 - Centralized smoke helper

Scope:
- Added `scripts/smoke.ps1` as the pre-commit smoke helper.
- The helper compiles Python entrypoints, checks renderer capabilities output, and parses all PowerShell scripts.
- Updated README and Git handoff to point future commits at the helper.

Positioning:
- This implements the user's new rule that commits need at least smoke testing.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.
## 2026-05-29 - Qt renderer capabilities display

Scope:
- Added `Renderer 能力` to the Qt panel.
- The action runs `taichi_global_bathymetry.py --print-renderer-capabilities` and displays the JSON in the preview area.

Positioning:
- This surfaces renderer-contract discovery in the operator UI without launching the renderer.

Validation:
- Smoke passed before commit: `py -3 -m py_compile rrkal_displaytools_qt_panel.py taichi_global_bathymetry.py`.
- Smoke passed before commit: `py -3 taichi_global_bathymetry.py --print-renderer-capabilities`.
- Smoke passed before commit: PowerShell parser check for all scripts under `scripts/`.
## 2026-05-29 - Renderer capabilities JSON output

Scope:
- Added `--print-renderer-capabilities` to `taichi_global_bathymetry.py`.
- The output lists style profiles, UI backends, topography sources, data modes, layer flags, material controls, and RRKAL/displaytools responsibility boundaries.
- Updated README and GTD with the capability output entry.

Positioning:
- This gives RRKAL and other machines a lightweight renderer-contract discovery path without launching the Taichi runtime.

Validation:
- Smoke passed before commit: `py -3 -m py_compile rrkal_displaytools_qt_panel.py taichi_global_bathymetry.py`.
- Smoke passed before commit: `py -3 taichi_global_bathymetry.py --print-renderer-capabilities`.
- Smoke passed before commit: PowerShell parser check for all scripts under `scripts/`.
## 2026-05-29 - Qt operator action layout

Scope:
- Reworked the Qt panel operator actions from a single horizontal row into a 4-column grid group.
- This keeps launch/copy/profile/smoke actions usable on narrower displays.

Positioning:
- UI layout improvement only; renderer behavior is unchanged.

Validation:
- Smoke passed before commit: `py -3 -m py_compile rrkal_displaytools_qt_panel.py taichi_global_bathymetry.py`.
- Smoke passed before commit: PowerShell parser check for all scripts under `scripts/`.
## 2026-05-29 - Portable command handoff

Scope:
- Added `複製可攜命令` to the Qt panel.
- Added `portable_command` and `portable_command_line` fields to launch packets.
- Updated README and GTD for cross-machine command handoff.

Positioning:
- Portable commands use `py -3 taichi_global_bathymetry.py ...` so another Windows machine is not tied to the original Python executable path.

Validation:
- Smoke passed before commit: `py -3 -m py_compile rrkal_displaytools_qt_panel.py taichi_global_bathymetry.py`.
- Smoke passed before commit: PowerShell parser check for all scripts under `scripts/`.
## 2026-05-29 - Windows quick headless render helper

Scope:
- Added `scripts/render_quick_smoke.ps1` for a small synthetic/headless render request into `state/showcase/quick_smoke.png`.
- Updated Qt panel smoke check to parse all PowerShell scripts under `scripts/`.
- Updated README with the optional quick render command.

Positioning:
- This is a displaytools showcase helper, not a required pre-commit smoke path.
- Generated images remain local under `state/` and should not be committed.

Validation:
- Smoke passed before commit: `py -3 -m py_compile rrkal_displaytools_qt_panel.py taichi_global_bathymetry.py`.
- Smoke passed before commit: PowerShell parser check for all scripts under `scripts/`.
## 2026-05-29 - Qt launch packet export

Scope:
- Added launch-packet export to `rrkal_displaytools_qt_panel.py`.
- Exported packets include current profile state, command array, command line, timestamp, and RRKAL/displaytools boundary notes.
- Updated README and GTD for the new handoff/debugging artifact.

Positioning:
- Launch packets are local displaytools handoff artifacts under `state/showcase/`.
- They do not replace RRKAL manifest or install registry governance.

Validation:
- Smoke passed before commit: `py -3 -m py_compile rrkal_displaytools_qt_panel.py taichi_global_bathymetry.py`.
- Smoke passed before commit: PowerShell parser check for `scripts/setup_windows.ps1` and `scripts/run_qt_panel.ps1`.
## 2026-05-29 - Qt panel smoke check action

Scope:
- Added a `Smoke check` button to `rrkal_displaytools_qt_panel.py`.
- The panel smoke check runs Python compile for the Qt panel and renderer, plus PowerShell parser checks for helper scripts on Windows.
- Smoke failures are surfaced in the command preview area for quick operator inspection.

Positioning:
- This supports the new rule that commits need at least smoke testing.

Validation:
- Smoke passed before commit: `py -3 -m py_compile rrkal_displaytools_qt_panel.py taichi_global_bathymetry.py`.
- Smoke passed before commit: PowerShell parser check for `scripts/setup_windows.ps1` and `scripts/run_qt_panel.ps1`.
## 2026-05-29 - Qt panel startup profile loading

Scope:
- Added `--profile` to `rrkal_displaytools_qt_panel.py` so a JSON profile can be loaded on startup.
- Added `-Profile` passthrough to `scripts/run_qt_panel.ps1`.
- Updated README with a shared-template startup example.

Positioning:
- This improves cross-machine reproducibility of layer/UI launch state.

Validation:
- Smoke passed before commit: `py -3 -m py_compile rrkal_displaytools_qt_panel.py taichi_global_bathymetry.py`.
- Smoke passed before commit: PowerShell parser check for `scripts/setup_windows.ps1` and `scripts/run_qt_panel.ps1`.
## 2026-05-29 - Qt panel grouped layer quick actions

Scope:
- Added grouped layer toggle actions to `rrkal_displaytools_qt_panel.py`.
- Groups cover hydrology, maritime zones, transport, and visual aids.

Positioning:
- This improves operator control over existing renderer flags without changing renderer internals.

Validation:
- Smoke passed before commit: `py -3 -m py_compile rrkal_displaytools_qt_panel.py taichi_global_bathymetry.py`.
- Smoke passed before commit: PowerShell parser check for `scripts/setup_windows.ps1` and `scripts/run_qt_panel.ps1`.
## 2026-05-29 - Windows setup and launch helpers

Scope:
- Added `scripts/setup_windows.ps1` to install Python dependencies from `requirements.txt`.
- Added `scripts/run_qt_panel.ps1` to launch the Qt operator panel from the repo root.
- Updated README clone/run instructions for another Windows computer.

Positioning:
- These scripts support cross-machine displaytools onboarding only.
- They do not perform validation, dataset download, or RRKAL data governance.

Validation:
- Smoke passed before commit: `py -3 -m py_compile rrkal_displaytools_qt_panel.py taichi_global_bathymetry.py`.
- Smoke passed before commit: PowerShell parser check for `scripts/setup_windows.ps1` and `scripts/run_qt_panel.ps1`.

## 2026-05-29 - Qt panel renderer process status

Scope:
- Added a Qt timer that polls the renderer process started by `rrkal_displaytools_qt_panel.py`.
- The panel now reports running PID and exit code when the renderer closes.

Positioning:
- This improves operator feedback without changing renderer behavior or RRKAL data governance.

Validation:
- Not run; no test/validation requested.

## 2026-05-29 - Qt panel operator shortcuts

Scope:
- Added command-copy support to `rrkal_displaytools_qt_panel.py`.
- Added shortcuts to open the repo-shared `profiles/` directory and local `state/ui_profiles/` directory.

Positioning:
- This improves cross-machine launch debugging and profile handoff without changing renderer behavior.

Validation:
- Not run; no test/validation requested.

## 2026-05-29 - Repo-shared Qt profile templates

Scope:
- Added `profiles/*.json` templates for baseline scientific, maritime hydrology, parchment review, tactical ops, and fast synthetic use cases.
- Added a Qt panel template selector with load/rescan actions.
- Updated README and GTD so another computer can clone the repo and start from shared templates.

Positioning:
- Templates are displaytools launch profiles only.
- Runtime/user-saved profiles remain local under `state/ui_profiles/` and should not be committed.

Validation:
- Not run; no test/validation requested.

## 2026-05-29 - Qt panel layer profile workflow

Scope:
- Added save/load JSON profile support to `rrkal_displaytools_qt_panel.py`.
- Added `套用並重啟` so current layer/style/material settings can be applied without manually stopping and launching.
- Documented local profile storage under `state/ui_profiles/`.

Positioning:
- Profiles are local operator UI state only.
- They do not replace RRKAL manifest, cache, install registry, or dataset governance.

Validation:
- Not run; no test/validation requested.

## 2026-05-29 - Qt operator layer control panel

Scope:
- Added `rrkal_displaytools_qt_panel.py`, a PyQt6 control panel for launching the renderer with explicit layer flags.
- Exposed style profile, UI backend, topo source, data mode, resolution, Taichi arch, ocean material values, and key layer toggles.
- Added quick presets: baseline, maritime/hydrology, parchment, tactical, minimal layers, and fast synthetic.
- Updated README, GTD, handoff, and workspace docs with Qt-first clone/run instructions.
- Removed the uncommitted Tk control-panel direction before commit; displaytools UI control should stay Qt-first.

Positioning:
- This is an operator launch UI, not an RRKAL data-governance UI.
- It improves control over existing renderer flags without rewriting the monolithic render loop.

Validation:
- Not run; no test/validation requested.

## 2026-05-29 - Closed-loop showcase preset

Scope:
- Added `--demo-closed-loop` to `taichi_global_bathymetry.py`.
- The preset keeps the demo bounded: synthetic topography, static data mode, hydrology LOD path enabled, lake/river/border layers on, ocean material controls on, terrain contours/grid/stars/scale bar on.
- Added an optional `--write-demo-packet` output for a machine-readable renderer showcase packet.
- Updated GTD and handoff docs for the one-command showcase path.

Positioning:
- This is a displaytools renderer loop only.
- It does not perform RRKAL dataset discovery, download, import, install registry, or cache governance.

Validation:
- Not run; user requested progress and display, but no test/validation run was requested.

## 2026-05-29 - RRKAL-aligned documentation governance

Scope:
- Added a product positioning document that defines `RRKAL_displaytools` as RRKAL's visualization/display layer.
- Added project GTD, Git handoff, and workspace layout docs based on the governance pattern from `APIkeys_collection`.
- Updated README, docs index, and agent handoff with the launcher-vs-renderer boundary.

Positioning:
- RRKAL / `APIkeys_collection` owns dataset discovery, download, import, install registry, manifest, cache governance, and renderer bridge asset registration.
- `RRKAL_displaytools` owns renderer consumption contracts, Taichi globe output, material/style controls, LOD/display diagnostics, and visualization frontends.

Validation:
- Not run; documentation-governance-only slice.

## 2026-05-29 - Initial project repo import

Scope:
- Created `RRKAL_displaytools` as the official GitHub project repository for visualization/display work.
- Imported the current Taichi globe prototype as `taichi_global_bathymetry.py`.
- Added minimal repository docs and governance notes.

Current prototype state:
- Hydrology basic readiness contracts and diagnostics exist in the monolithic script.
- LOD hook diagnostics, invalidation contract, and layer-count gate alignment are present.
- Taichi ocean material controls and ocean condition binding diagnostics are present.
- Style renderer entries for scientific/tactical/parchment profiles are represented by contract diagnostics.
- Decoupling readiness packets, seam matrices, cache governance, and known-issue diagnostics are represented in the monolith.

Validation:
- No validation was run as part of this repository import.
- Earlier local syntax check was run before import with `py -3 -m py_compile C:\Users\lyn59\scratch\taichi_global_bathymetry.py` and returned 0.

Next round rule:
- Before any new development round, inspect current repo state.
- After each round, update this log and commit before continuing.













## 2026-05-29 - Profile schema documentation

Scope:
- Added `docs/PROFILE_SCHEMA.zh-TW.md` for Qt panel profile templates.
- Updated docs index, README, and GTD to reference the schema.

Positioning:
- This gives RRKAL a stable displaytools profile shape for future handoff without mixing dataset governance into renderer UI state.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.









## 2026-05-29 - Windows setup documentation

Scope:
- Added `docs/SETUP_WINDOWS.zh-TW.md` for clone, install, smoke, Qt panel launch, template use, quick render, and launch packet export on another Windows computer.
- Updated docs index, README, and GTD.
- Added user reporting rule: after every push, summarize current program capabilities in Chinese.

Positioning:
- This supports cross-machine usage without changing renderer behavior.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - No-GUI template listing before Qt import

Scope:
- Updated `rrkal_displaytools_qt_panel.py --list-templates` to return before importing PyQt6.
- Template listing now reads UTF-8 BOM profile files using `utf-8-sig`.

Positioning:
- This lets RRKAL/scripts discover displaytools templates without requiring the Qt runtime to initialize.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Profile schema JSON output and README repair

Scope:
- Added `profile_schema.py` JSON contract output to README usage instructions.
- Repaired malformed README PowerShell code fences.
- Documented `profile_schema.py` and no-GUI launch packet exporter as primary files.

Positioning:
- This improves RRKAL/script handoff and cross-machine copy/paste reliability.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - RRKAL handoff contract documentation

Scope:
- Added `docs/RRKAL_HANDOFF_CONTRACT.zh-TW.md`.
- Documented no-GUI endpoints for renderer capabilities, profile templates, profile schema, and launch packet export.
- Updated README and docs index.

Positioning:
- This turns the current displaytools work into an explicit future RRKAL integration surface.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Capability summary documentation

Scope:
- Added `docs/CAPABILITY_SUMMARY.zh-TW.md`.
- Updated docs index and README to reference the current capability summary.

Positioning:
- This supports the user rule that every push should include a current capability explanation.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Renderer layer manifest output

Scope:
- Added `--print-layer-manifest` to `taichi_global_bathymetry.py`.
- The manifest groups existing layer flags into hydrology, boundaries, transport, visual aids, material, and preset groups.
- Added layer manifest coverage to `scripts/smoke.ps1` and capability summary docs.

Positioning:
- This starts the renderer-side backend contract for Qt layer control without changing rendering behavior.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Photoshop-inspired Qt workspace labels

Scope:
- Reframed `rrkal_displaytools_qt_panel.py` as `RRKAL_displaytools Studio`.
- Renamed panel groups toward Photoshop-inspired workspace concepts: tool options, Looks/templates, layers, properties, central preview, and actions.
- Added a Qt action to display renderer layer manifest JSON from the backend.
- Updated capability summary and GTD.

Positioning:
- This starts aligning the Qt frontend with Photoshop's panel/workspace spirit while keeping current renderer behavior unchanged.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Qt Studio menu and tools dock

Scope:
- Added a menu bar to `rrkal_displaytools_qt_panel.py` with File, Renderer, Window, and Help menus.
- Added a left-side `Tools` dock with quick actions for baseline/maritime/parchment/tactical presets, smoke, capabilities, and layer manifest.

Positioning:
- This moves the Qt frontend closer to Photoshop's workspace structure: menu bar, tool dock, central preview, layer/properties panels.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Dockable Qt Layers panel

Scope:
- Moved the Qt layer controls into a right-side dockable `Layers` panel.
- Preserved existing layer toggles and grouped layer quick actions.

Positioning:
- This makes the frontend closer to Photoshop's dockable Layers panel model without changing renderer behavior.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Dockable Qt Properties panel

Scope:
- Moved ocean material controls into a dockable `Properties` panel.
- Kept wave strength, roughness, and foam controls unchanged.

Positioning:
- This continues the Photoshop-like workspace direction by separating Layers and Properties as dockable panels.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Qt Navigator and History placeholder docks

Scope:
- Added dockable `Navigator` and `History` panels to `rrkal_displaytools_qt_panel.py`.
- Navigator shows a construction-state live thumbnail placeholder and disabled zoom field.
- History lists completed UI flows and planned Photoshop-like features with explicit construction markers.

Positioning:
- This prioritizes UI/UIUX shape first while honestly marking unimplemented frontend features as under construction.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Qt workspace layout persistence

Scope:
- Added Window menu actions to save, load, and reset local Qt workspace layout.
- Workspace geometry and dock state are saved to `state/ui_workspace.json`.
- Updated reporting rule: every push report includes current capabilities and planned/next capabilities.

Positioning:
- This follows Photoshop's saved workspace concept while keeping layout state local-only.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Photoshop-like Qt layer stack controls

Scope:
- Reworked the Qt `Layers` panel into a layer-stack table with visibility, lock, opacity, and blend-mode columns.
- Visibility remains connected to renderer flags.
- Lock, opacity, and blend mode are explicit 🚧 UI state and are included in Qt launch packets as `layer_stack_ui` for the next renderer-sync step.

Positioning:
- This moves the Qt UI closer to Photoshop's Layers panel while keeping renderer behavior unchanged in this small slice.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Qt workspace preset menu

Scope:
- Added `Window > Workspace Presets` entries for Default, Maritime, Tactical, Parchment, and Review.
- Presets restore core docks, arrange key panels into tabs, and apply the matching display preset where appropriate.

Positioning:
- This gives the Qt frontend a Photoshop-like workspace preset flow while keeping persisted custom layouts local.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Qt active layer selection

Scope:
- Added active-layer selection controls to the Qt `Layers` stack.
- Selected rows are highlighted and the active layer is shown in the panel.
- Added a reset action for UI-only lock, opacity, and blend-mode state.
- Launch packets now include `selected_layer` and per-layer `selected` metadata for the next renderer-sync step.

Positioning:
- This gives brush, mask, selection, and Properties-panel work a concrete layer target without changing renderer behavior yet.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Qt active layer properties inspector

Scope:
- Extended the Qt `Properties` dock with an active-layer inspector.
- The inspector shows selected-layer visibility, lock, opacity, and blend mode.
- Added Properties actions to toggle selected-layer visibility and reset selected-layer UI-only state.

Positioning:
- This connects the Layers and Properties panels into one operator loop, preparing the selected-layer target for brush, mask, and renderer-sync work.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Qt layer stack profile state

Scope:
- Added optional `selected_layer` and `layer_stack_ui` contract fields to `profile_schema.py`.
- Updated Qt profile save/load so selected layer, lock, opacity, and blend-mode UI state can round-trip through local profiles.
- Rewrote `docs/PROFILE_SCHEMA.zh-TW.md` with the layer stack UI contract and handoff rules.

Positioning:
- This keeps the current work inside UIUX closure: operator UI state can now be saved, loaded, and moved across machines before renderer-side sync is implemented.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Qt tool palette UI state

Scope:
- Added a Photoshop-like tool palette to the Qt `Tools` dock: Move, Select, Brush, Mask, and Erase.
- Added UI-only tool options for brush size, hardness, tool opacity, mask mode, and selection mode.
- Bound the active tool to the selected layer target.
- Added optional `tool_state` to profile schema, profile save/load, and launch packets.

Positioning:
- This keeps development on the UIUX closure path. Brush, Mask, and Selection now have a complete Qt state loop before renderer backend sync is implemented.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Qt canvas preview and simplified select tool

Scope:
- Added a central UI-only Canvas Preview that mirrors style, topo source, data mode, active tool, active layer, visible layer count, and zoom.
- Simplified the tool palette to Move and Select only.
- Removed Brush, Mask, Erase, and their UI-only option controls from the active UI path.
- Simplified `tool_state` schema to active tool and target layer.

Positioning:
- This keeps UIUX development focused on layer selection and canvas feedback before backend renderer sync.
- The UI framing was tightened toward research workflows: panel structure borrows from Photoshop, but the primary user need is reproducible scientific visualization state.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Qt research provenance dock

Scope:
- Added a dockable `Provenance` panel for research reproducibility.
- The panel renders a copyable JSON summary with style profile, topo source, data mode, renderer dimensions, active tool, active layer, visible layers, locked layers, layer counts, and portable command line.
- Added the dock to workspace preset restoration, especially the Review workspace.

Positioning:
- This reframes the Photoshop-like UI into a scientific visualization workstation: the core value is traceable, reproducible visualization state for researchers, not generic image editing.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Qt research pin tool

Scope:
- Added a research-oriented `Pin` tool to the Qt tool palette.
- Added Pin Annotation UI fields for marker type, label, and note.
- Added optional pin metadata to `tool_state` schema, profile save/load, and launch packets.

Positioning:
- This better matches scientific workflows: researchers often need to mark observation points, sample sites, anomalies, reference locations, and events on the globe.
- Actual globe/canvas hit-testing and latitude/longitude placement remain backend work for later.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Qt pin marker list

Scope:
- Extended the Pin tool with manual latitude/longitude fields.
- Added add/remove marker list controls for research pins.
- Added optional top-level `pins` schema validation and profile/launch packet persistence.
- Documented mouse-position-to-lat/lon as the next backend boundary for globe/canvas hit-testing.

Positioning:
- This completes the UIUX-side scientific marker loop first: researchers can record observation/sample/anomaly/reference/event pins manually before renderer hit-testing is connected.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Qt cursor latitude longitude estimate

Scope:
- Added mouse tracking to the central Canvas Preview.
- Added UI-only equirectangular canvas mapping from cursor position to estimated latitude/longitude.
- Added `用游標填入 Pin` to copy the current cursor estimate into Pin latitude/longitude fields.
- Added the current cursor estimate to the research provenance summary.

Positioning:
- This gives researchers an immediate marker workflow while keeping the true renderer/globe hit-test as a later backend closure.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Qt selected pin workflow

Scope:
- Added `selected_pin_id` state for the Qt Pin list.
- Selecting a Pin now refills the Pin editor fields and updates Canvas Preview.
- Canvas Preview now shows the selected marker and a compact marker summary.
- Profile, launch packet, schema validation, and research provenance now include the selected Pin state.

Positioning:
- This closes another UIUX-side scientific annotation loop before backend renderer overlay and true globe hit-testing are connected.
- Renderer overlay follow-up must treat Pins as geodetic surface anchors that rotate with the globe and are hidden or faded by horizon/depth occlusion when they move behind the visible hemisphere.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Pin projection and occlusion hook

Scope:
- Added `pin_projection.py` as a pure Python geodetic Pin projection hook.
- The hook projects latitude/longitude anchors with camera yaw/pitch/zoom into screen coordinates.
- It classifies Pin visibility as `visible`, `behind_horizon`, `off_viewport`, or `invalid`.
- Renderer capabilities and Qt provenance now expose the Pin projection contract.

Positioning:
- This starts the renderer-facing side of scientific Pins without drawing the overlay yet.
- Pins now have a concrete math contract for rotating with the globe and hiding behind the horizon; depth/globe-mask refinement remains the next overlay step.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Renderer Pin overlay input

Scope:
- Added renderer Pin input flags: `--pin-file`, `--pin-json`, `--pin-layer`, `--pin-size`, and `--pin-horizon-eps`.
- Qt launch commands now pass current research Pins to the renderer with `--pin-json`.
- Renderer now projects Pins every overlay pass and draws visible markers after AIS/ADS-B overlays.
- Pins classified as `behind_horizon`, `off_viewport`, or `invalid` are not drawn.
- Smoke now compiles `pin_projection.py`.

Positioning:
- This moves scientific Pins from UI-only annotation into an initial renderer overlay loop.
- The current occlusion closes the visible hemisphere problem; globe-mask/depth-buffer refinement and label collision remain next.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Renderer selected Pin highlight

Scope:
- Renderer Pin loading now preserves `selected_pin_id` from `--pin-file` or `--pin-json`.
- The Pin overlay renderer now draws the selected marker with a white highlight ring.
- Renderer capabilities now document that selected Pin state is consumed by the overlay.

Positioning:
- This connects Qt Pin selection to actual renderer output, so selected scientific annotations are not just UI state.
- Remaining Pin work is label layout, pick/hover, and deeper globe-mask/depth-buffer occlusion refinement.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Style-aware Pin marker palettes

Scope:
- Added profile-aware Pin marker palettes for scientific, nautical, tactical, and parchment styles.
- Selected Pin highlight rings now follow the active style profile instead of using one fixed white ring.
- Renderer capabilities now expose the Pin marker style profile contract.

Positioning:
- This moves Pin overlay styling into the same style-profile contract as the rest of the renderer.
- Remaining Pin work is label layout, pick/hover, and deeper globe-mask/depth-buffer occlusion refinement.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Renderer Pin label layout

Scope:
- Added simple renderer-side Pin label boxes with leader lines.
- Label placement uses four candidate quadrants around each visible Pin.
- Labels skip positions that collide with previously placed labels.
- Label colors now follow the active Pin marker style profile.

Positioning:
- This makes scientific Pins readable in the renderer instead of only showing symbols.
- Remaining Pin work is label priority controls, pick/hover, and deeper globe-mask/depth-buffer occlusion refinement.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Pin label priority controls

Scope:
- Added Qt `Label Priority` control for Pin annotations.
- Saved Pins and launch packets now carry `label_priority` from 0 to 100.
- Profile schema validation accepts optional `label_priority`.
- Pin projection packets preserve `label_priority`.
- Renderer label placement now sorts selected Pin first, then higher priority labels.

Positioning:
- This lets researchers protect important stations/anomalies from being dropped by collision avoidance.
- Remaining Pin work is label visibility modes, pick/hover, and deeper globe-mask/depth-buffer occlusion refinement.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Pin label visibility modes

Scope:
- Added Qt Pin label mode controls: auto, selected only, priority, and hidden.
- Added `pin_label_min_priority` for renderer label thresholding.
- Qt launch commands now pass `--pin-label-mode` and `--pin-label-min-priority`.
- Profile schema validates label mode and threshold in `tool_state`.
- Renderer label layout filters labels before collision placement.
- Hardened Pin JSON/file loading so malformed shell-escaped Pin payloads are ignored with a warning instead of crashing the renderer.

Positioning:
- Researchers can now reduce annotation clutter without deleting Pins.
- Remaining Pin work is renderer pick/hover and deeper globe-mask/depth-buffer occlusion refinement.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Renderer Pin hover and pick

Scope:
- Added renderer-side nearest visible Pin hit testing.
- Added `--pin-pick-radius` for click/hover tolerance.
- Mouse hover now exposes Pin information in the Qt renderer selection panel.
- Mouse click now selects a Pin before falling back to AIS/ADS-B vehicle pick.
- Picked Pins update `selected_pin_id` and redraw the selected marker ring.

Positioning:
- This closes the first renderer-side interaction loop for scientific Pins.
- Remaining Pin work is sending renderer pick state back to the external Qt control panel and deeper globe-mask/depth-buffer occlusion refinement.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Renderer Pin pick state bridge

Scope:
- Added `--pin-pick-state-file` to the renderer.
- Renderer now writes selected/hover/cleared Pin pick state as JSON.
- Qt launch commands now pass `state/renderer_pin_pick_state.json` as the default bridge file.
- Launch packets include the Pin pick state file path.

Positioning:
- This creates the first bridge for syncing renderer-side Pin interaction back to the external Qt control panel.
- The next step is for the Qt control panel to watch/read this state file and update its selected Pin UI.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Qt Pin pick bridge sync

Scope:
- Added a Qt-side poller for `state/renderer_pin_pick_state.json`.
- The Pin Annotation panel now shows renderer bridge event, selected Pin, hovered Pin, visible count, frame, and update timestamp.
- Renderer `selected` events sync back into the external Qt Pin list, Pin form fields, command preview, canvas preview, and provenance.
- Renderer `cleared` events clear the Qt selected Pin without affecting saved Pin annotations.

Positioning:
- This closes the first bidirectional Pin loop: Qt sends Pins to renderer, renderer performs visible-globe hit testing, and Qt consumes renderer pick state.
- Remaining Pin work is richer bridge diagnostics/history and deeper globe-mask/depth-buffer occlusion refinement.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Canvas Select layer hit bands

Scope:
- Added UI-only Canvas Preview hit bands for the Select tool.
- When Select is active, left-clicking the Canvas Preview maps the vertical click position to the current visible layer list and updates the active layer.
- Canvas Preview now displays a compact Select hit map so researchers can see which visible layers are targetable.
- Research provenance now records the current Canvas Select hit targets.

Positioning:
- This makes layer targeting less dependent on the right-side layer stack and improves the Photoshop-like interaction loop without adding Brush/Mask tools.
- The next step is upgrading the hit target from UI-only preview bands to renderer-backed layer/object picking.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Layer solo visibility workflow

Scope:
- Added `Solo 選取圖層` in the Layers panel.
- Added `還原 Solo 前可見性` with an in-memory visibility snapshot.
- Solo updates renderer visibility flags for the selected layer while preserving the previous visible-layer state for restore.
- Research provenance now records whether a layer visibility snapshot is active.

Positioning:
- This gives researchers a fast way to isolate one hydrology, maritime, transport, or visual-aid layer without manually toggling every checkbox.
- The next step is renderer-backed live layer sync so visibility changes do not require restart.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Layer runtime state bridge

Scope:
- Added `state/renderer_layer_runtime_state.json` as a Qt-authored layer runtime bridge.
- The bridge records selected layer, visible layers, locked layers, opacity, blend mode, per-layer visibility, and Solo visibility snapshot state.
- Qt writes the bridge whenever the layer stack status refreshes.
- Launch packets and research provenance now include the layer runtime state file path.

Positioning:
- This creates the stable handoff needed for renderer-backed live layer sync without changing the renderer loop in this step.
- The next step is teaching the renderer to watch/read this bridge and apply visibility changes without restart.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Renderer layer visibility live sync

Scope:
- Qt launch commands now pass `--layer-runtime-state-file`.
- Renderer now accepts `--layer-runtime-state-file` / `LAYER_RUNTIME_STATE_FILE`.
- The render loop polls the layer runtime bridge by file mtime and applies per-layer `visible` values through the existing `set_layer_visible()` path.
- Renderer capabilities now document the layer runtime state contract and mark opacity/blend/lock as pending.

Positioning:
- This closes the first renderer-backed layer live sync loop for visibility, reducing reliance on restart for layer on/off work.
- Remaining layer sync work is opacity, blend mode, lock semantics, diagnostics, and renderer-backed picking.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Layer runtime diagnostics UI

Scope:
- Added a Layers panel runtime bridge status label.
- The label shows `renderer_layer_runtime_state.json`, selected layer, visible count, last write time, and pending opacity/blend/lock status.
- Added `顯示 layer runtime JSON` to display the current runtime bridge payload in the central text area.
- Research provenance now records the layer runtime bridge last write time and write error status.

Positioning:
- This makes renderer-backed layer visibility sync inspectable from Qt instead of requiring users to manually find files in `state/`.
- The next step is applying opacity, blend mode, and lock semantics from the same runtime bridge.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Layer lock visibility guardrails

Scope:
- Locked layers now disable their visibility checkbox in the Qt Layers panel.
- Group toggles skip locked layers.
- Solo and restore visibility skip locked layers, and Solo refuses to run when the selected layer itself is locked.
- Selected-layer visibility toggle refuses to change a locked layer.

Positioning:
- This makes lock meaningful as a UI guardrail for scientific reference layers, not just profile metadata.
- Renderer-side lock enforcement remains pending; current renderer live sync still applies visibility values from the runtime bridge.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Layer runtime history

Scope:
- Added a short layer runtime history list in the existing History panel.
- History entries are recorded only when the layer runtime summary changes, not on every UI refresh.
- Entries include update time, selected layer, visible count, locked count, and Solo snapshot state.
- Research provenance now includes the latest layer runtime history entries.

Positioning:
- This gives researchers a quick audit trail for recent layer sync changes while keeping the UI lightweight.
- The next step is persisted history or renderer-side sync acknowledgements after opacity/blend/lock are wired.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Renderer layer runtime acknowledgement

Scope:
- Qt launch commands now pass `--layer-runtime-ack-file`.
- Renderer now writes `renderer_layer_runtime_ack.json` after reading a changed layer runtime state file.
- The ack records state file mtime, state update timestamp, changed layers, renderer-visible layers, frame index, and pending opacity/blend/lock status.
- Layers panel now polls and displays renderer ack status.
- Research provenance includes the renderer layer runtime ack payload and file path.

Positioning:
- This separates "Qt wrote runtime state" from "renderer observed runtime state", improving scientific traceability for live layer sync.
- The ack currently covers visibility sync; compositor-level opacity/blend and renderer-side lock enforcement remain next.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Pin pick history

Scope:
- Added short Pin pick history entries to the existing History panel.
- Entries are recorded from renderer Pin pick bridge events and deduplicated by event, selected Pin, hover Pin, event Pin, and frame.
- Entries include event type, selected Pin, hover Pin, event Pin, visible Pin count, and update time.
- Research provenance now includes recent Pin pick history entries.

Positioning:
- This gives researchers an audit trail for recent renderer-side Pin interactions without opening `state/renderer_pin_pick_state.json` manually.
- The next Pin work is stronger diagnostics/ack and deeper globe-mask/depth-buffer occlusion refinement.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Pin pick diagnostics JSON

Scope:
- Qt now stores the latest renderer Pin pick bridge payload.
- Added `顯示 Pin pick JSON` in the Pin Annotation panel.
- The central text area can display `state/renderer_pin_pick_state.json` directly.
- Research provenance now includes the latest Pin pick payload in addition to Pin pick history.

Positioning:
- This makes Pin interaction diagnostics inspectable from the Qt UI instead of requiring manual file lookup.
- Remaining Pin work is renderer-side acknowledgement and deeper globe-mask/depth-buffer occlusion refinement.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Qt Pin pick acknowledgement

Scope:
- Added `state/qt_pin_pick_ack.json` as a Qt-authored acknowledgement for renderer Pin pick events.
- The ack records renderer event, renderer timestamp, renderer frame, renderer selected Pin, Qt selected Pin, and whether the Qt UI synced the event.
- The Pin Annotation panel now shows Qt ack status.
- Launch packets and research provenance include the Pin pick ack file and latest ack payload.

Positioning:
- This separates "renderer wrote Pin pick state" from "Qt consumed and synced Pin pick state", improving traceability for scientific annotations.
- Remaining Pin work is renderer-side acknowledgement and deeper globe-mask/depth-buffer occlusion refinement.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Renderer Pin input acknowledgement

Scope:
- Qt launch commands now pass `--pin-input-ack-file`.
- Renderer now writes `renderer_pin_input_ack.json` after loading `--pin-file` / `--pin-json`.
- The ack records pin count, a preview of Pin IDs, selected Pin ID, whether the selected Pin exists in the loaded set, and Pin layer enablement.
- The Pin Annotation panel now polls and displays renderer Pin input acknowledgement.
- Launch packets and research provenance include the Pin input ack file and latest payload.

Positioning:
- This confirms renderer receipt of Qt Pin annotations before any hover/click interaction happens.
- Remaining Pin work is finer interaction acknowledgement and deeper globe-mask/depth-buffer occlusion refinement.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Renderer layer lock enforcement

Scope:
- Renderer runtime layer sync now skips visibility changes for layers marked `locked=true` in `renderer_layer_runtime_state.json`.
- Renderer `renderer_layer_runtime_ack.json` now records `skipped_locked_layers`.
- Qt Layers panel ack status now displays the skipped locked-layer count.
- Renderer capabilities now mark `lock_guard_visibility` as applied, with opacity/blend mode still pending.

Positioning:
- This closes the lock guardrail loop across Qt layer controls, runtime bridge payload, renderer visibility application, and renderer acknowledgement.
- Remaining layer sync work is opacity, blend mode, richer diagnostics, and renderer-backed picking.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Boundary highlight mask UI contract

Scope:
- Added `boundary_highlight` state to Qt profiles, launch packets, Canvas Preview, and provenance.
- Added a Properties panel entry for boundary highlight controls.
- Boundary-capable rows (`border_layer`, `territorial_sea_layer`, `eez_layer`, `high_seas_layer`) can be double-clicked to open the control dialog.
- The dialog exposes enabled/trigger, target boundary layers, RGB color picker, contrast, alpha, gamma, feather, and breathing speed/amplitude controls.
- Updated profile schema validation and docs for `rrkal_displaytools.boundary_highlight_mask.v1`.

Positioning:
- This captures the user's territory/sea-zone emphasis behavior as a reproducible UI/profile contract before renderer polygon picking is implemented.
- Remaining work is renderer-backed hover geometry picking, outline/glow visualization, polygon fill, and shader-side contrast/gamma/breathing application.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Boundary highlight renderer acknowledgement

Scope:
- Qt launch commands now pass `--boundary-highlight-json` and `--boundary-highlight-ack-file`.
- Renderer now parses the boundary highlight payload and writes `renderer_boundary_highlight_ack.json`.
- The ack records enabled state, trigger mode, profile target layers, renderer target layers, color/contrast/alpha/gamma/feather, breathing settings, and pending overlay steps.
- The Properties panel now polls and displays the renderer boundary highlight ack.
- Merged the boundary-layer double-click handler into the active `eventFilter`, restoring the intended dialog entry path.

Positioning:
- This closes the first front-end to renderer receipt loop for territory/sea-zone emphasis.
- Remaining work is renderer-backed hover geometry picking, outline/glow visualization, polygon fill, and shader-side contrast/gamma/breathing application.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Boundary highlight hover outline preview

Scope:
- Wired `boundary_highlight.enabled`, trigger mode, and renderer target layers into renderer boundary hover hit-testing.
- Mouse move now updates Pin/boundary hover even when the user is not dragging or rotating the globe.
- Existing boundary line highlight now uses the boundary highlight RGB color, alpha, feather, and breathing speed settings.
- Renderer ack/capabilities now mark hover hit gate and outline/glow preview as applied.

Positioning:
- This turns the boundary highlight contract into a visible renderer preview while staying inside the existing globe mask/vector overlay path.
- Remaining work is feature identity, polygon fill masks, and fuller contrast/gamma shader behavior.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Boundary highlight contrast gamma preview

Scope:
- Added renderer-side color adjustment for Boundary highlight hover outline/glow.
- `boundary_highlight.contrast` now increases hover color separation around the midtone.
- `boundary_highlight.gamma` now adjusts hover color brightness before contrast is applied.
- Renderer ack/capabilities now mark hover contrast/gamma color control as applied, while polygon-fill shader contrast/gamma remains pending.

Positioning:
- This closes the current line-hover visual loop for all Boundary highlight sliders except polygon-fill behavior.
- Remaining Boundary highlight work is feature identity, polygon fill masks, and fill-shader contrast/gamma behavior.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Layer runtime opacity sync

Scope:
- Added renderer alias mapping from Qt layer keys such as `lake_layer` / `border_layer` to renderer layer IDs such as `lakes` / `borders`.
- Renderer runtime layer sync now applies supported `opacity` values from `renderer_layer_runtime_state.json`.
- Supported opacity targets currently include hydrology lines, boundary lines, scale bar, and terrain contours.
- Locked runtime layers skip both visibility and opacity changes.
- Renderer layer runtime ack now reports `changed_opacity_layers`, current `layer_opacity`, and the runtime alias map.
- Qt Layers ack label now displays opacity-change count.

Positioning:
- This closes the first live opacity loop from the Photoshop-like Qt layer stack into the renderer.
- Remaining layer stack work is blend mode sync, broader per-layer opacity support for point/icon layers, and renderer-backed picking.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline camera keyframe closed loop

Scope:
- Added Qt Timeline camera controls for yaw, pitch, and zoom.
- Timeline keyframes now store camera state and restore it in the Qt panel.
- No-GUI launch packets, runtime state, renderer ack, and renderer capabilities now expose `rrkal_displaytools.timeline_camera_keyframe.v1`.
- Renderer startup/step playback now applies discrete camera keyframes to yaw/pitch/zoom; PNG frame export records the active frame camera in the manifest.

Decision:
- Camera is intentionally discrete in this slice. Smooth camera interpolation stays pending so the current change remains small and reversible.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline camera keyframe interpolation

Scope:
- Added Timeline camera interpolation contract `rrkal_displaytools.timeline_camera_interpolation.v1`.
- Renderer playback now interpolates camera yaw, pitch, and zoom across the active Timeline segment.
- Yaw interpolation uses shortest-angle interpolation to avoid long spins across the 180 degree seam.
- Timeline PNG export now records the interpolated camera for each exported frame.
- Smoke now gates launch packet, runtime state, renderer ack, and renderer capability discovery for camera interpolation.

Decision:
- Camera interpolation is limited to yaw, pitch, and zoom. Non-material UI state interpolation remains pending.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-29 - Timeline GIF animation export fallback

Scope:
- Added `--timeline-export-gif` as a lightweight encoded animation target for Timeline exports.
- Timeline export still writes PNG frames and manifest, and now optionally writes an animated GIF using Pillow.
- Animation export packets now report `gif_file`, `encoded_animation`, `encoding_format`, and `encoding_error`.
- Renderer capabilities and smoke now gate the `timeline-export-gif` control and `timeline_gif_animation` apply scope.

Decision:
- GIF is the dependency-light fallback for sharing animations. MP4/container video encoding remains pending because `imageio` / `imageio_ffmpeg` are not installed in this workspace.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Qt cursor geodesy bridge readback

Scope:
- Added a Qt timer that reads renderer cursor geodesy state/ack files.
- Canvas Preview now surfaces renderer cursor hit/miss, lat/lon, event, frame, and update time.
- Provenance and canvas preview state now include renderer cursor geodesy state/ack payloads.
- Smoke now gates the Qt cursor geodesy bridge label, refresh hook, and provenance payload.

Decision:
- Qt readback remains file-based to match the existing renderer state bridges and keep GPU/IPC texture streaming deferred.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Pin cursor fill prefers renderer geodesy

Scope:
- Pin "use cursor" now prefers renderer cursor geodesy state from the globe raycast bridge.
- The Qt canvas equirectangular estimate remains a fallback when renderer state is unavailable or outside the globe.
- Tool state documents the fill priority as `renderer_cursor_geodesy_state_then_ui_estimate`.
- Smoke gates the renderer-first Pin cursor fill hook.

Decision:
- Pin placement should use renderer globe coordinates when available because researcher annotations need globe-aware coordinates, not only panel preview estimates.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Pin cursor fill contract discovery

Scope:
- Added Pin cursor fill priority to the shared `pin_projection` contract.
- Launch packets, renderer capabilities, Qt provenance, and handoff inspection now expose `renderer_cursor_geodesy_state_then_ui_estimate`.
- Smoke now gates launch packet, renderer capability, and handoff evidence for renderer-first Pin cursor fill.

Decision:
- Pin placement remains a visualization concern: displaytools owns the renderer-first coordinate handoff, while RRKAL still owns data discovery/import/cache governance.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Pin cursor fill source UI status

Scope:
- Tools dock now shows the active Pin cursor fill source.
- The status reports renderer globe raycast readiness, outside-globe fallback, Qt canvas estimate fallback, or waiting state.
- Renderer cursor geodesy readback refresh now updates the Tools dock status immediately.
- Smoke now gates the visible Pin cursor fill source status and helper.

Decision:
- Research users need to know whether a Pin coordinate came from renderer globe raycast or from the Qt preview estimate before placing annotations.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Layer pick screen position diagnostics

Scope:
- Renderer layer pick state now records the clicked screen position as `screen_position`.
- Qt layer pick diagnostics and active layer diagnostics now display click position beside hit/no-hit context.
- Smoke now gates renderer `last_layer_pick_screen` state and Qt screen-position diagnostics strings.

Decision:
- Layer selection needs operator-visible pick provenance so researchers can diagnose whether a miss is due to target layer, position, or renderer picker coverage.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Active layer pick position contract

Scope:
- Active layer diagnostics now exposes `layer_pick_screen_position`, `layer_pick_screen_position_field`, and `layer_pick_screen_position_source`.
- No-GUI launch packets declare that screen-position diagnostics come from `state/renderer_layer_pick_state.json`.
- Renderer capabilities now list `screen_position` as an active-layer diagnostics runtime field.
- Smoke gates launch packet and renderer capability discovery for the screen-position diagnostics contract.

Decision:
- The previous runtime JSON field is now promoted into handoff/capability contracts so cross-machine users can verify selected-layer pick provenance without reading renderer internals.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Handoff active layer pick position inspection

Scope:
- `scripts/inspect_handoff.ps1` now exposes active-layer diagnostics screen-position fields.
- Handoff JSON includes launch-packet schema, renderer capability schema, `screen_position` field name, source file, status, and renderer runtime fields.
- Smoke now gates the handoff active-layer screen-position contract.

Decision:
- Cross-machine verification should not require manual JSON spelunking in renderer state files; the handoff inspection output must summarize the selected-layer pick provenance contract directly.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Layer pick history provenance

Scope:
- History panel now records each renderer layer pick update.
- Layer pick history entries include target, picker, hit/no-hit, feature text, frame, and screen position.
- Smoke now gates the Layer pick history entry hook.

Decision:
- Researchers need a short interaction trail for selected-layer picking, not only the latest Properties label, so repeated pick attempts remain traceable.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Boundary ack history provenance

Scope:
- Qt now records renderer boundary highlight ack changes into the History panel.
- Boundary ack history entries include enabled state, trigger, target layers, renderer target count, live scope count, pending refinement count, and update time.
- Research provenance now includes `boundary_highlight_ack_history`.
- Smoke gates the boundary ack history UI hook and provenance field.

Decision:
- Boundary emphasis is a researcher-facing visual analysis tool; renderer acknowledgement history must be visible and reproducible, not only shown as the latest Properties label.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Boundary ack history handoff contract

Scope:
- Launch packets now declare the boundary ack history contract, source file, fields, Qt surface, and provenance field.
- Renderer capabilities expose the same boundary ack history contract.
- Handoff inspection now summarizes the boundary ack history contract for cross-machine verification.
- Smoke gates launch packet, renderer capability, and handoff evidence for boundary ack history.

Decision:
- Boundary emphasis state changes need the same cross-machine discoverability as other UI/runtime bridges, because the feature is used for scientific review and reproducibility.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Boundary identity status verification

Scope:
- Renderer capabilities now expose boundary identity applied/pending markers.
- Handoff inspection now reports launch-packet and renderer boundary identity applied/pending fields.
- Smoke now verifies closed-ring hit/fill applied markers and authoritative polygon / open-line pending markers across launch packet, renderer capability, and handoff inspection.

Decision:
- Boundary emphasis is not yet an authoritative legal identity resolver. The current contract now makes the applied visual/source-property identity scope and pending authoritative identity work explicit and cross-machine verifiable.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Boundary identity markers in Qt

Scope:
- Qt Boundary identity summary now lists applied and pending identity markers instead of only counts.
- Canvas Preview now shows the same Boundary identity applied/pending marker summary next to Boundary highlight status.
- Smoke gates the visible Canvas Boundary identity line and applied marker summary helper.

Decision:
- Researchers need to see whether boundary emphasis is using visual/source-property preview identity or waiting on authoritative polygon/open-line work directly in the UI, not only in JSON contracts.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Boundary emphasis dialog preview

Scope:
- Qt Boundary emphasis dialog now shows an RGB swatch and live numeric preview for target, RGB, contrast, opacity, gamma and breathing period.
- Boundary emphasis contracts now declare dialog feedback fields for RGB swatch, live numeric readout and renderer bridge summary across Qt, launch packet and renderer capabilities.
- Stale queued-mask wording was removed from the Qt dialog; the UI now states that the renderer bridge is wired through the boundary highlight mask while authoritative polygon identity remains pending.

Decision:
- Researchers need to see the visual emphasis parameters before applying them, especially when tuning EEZ/territorial boundary contrast and semi-transparent overlays.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Boundary layer action badge

Scope:
- Qt layer rows now include a visible Action column; boundary-capable rows show an Emphasis badge that opens Boundary emphasis controls by double-click.
- Layer operator shortcuts and layer selection tool contracts now expose `open_boundary_emphasis` and the Boundary row emphasis action badge surface in launch packet and renderer capabilities.

Decision:
- Boundary emphasis must be discoverable from the layer list itself, not hidden behind tooltip-only behavior, because researchers tune country/territorial sea/EEZ/high-seas overlays while scanning layers.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Boundary emphasis target alignment

Scope:
- Boundary emphasis contracts now expose target layer key, selected-layer match status and a researcher-readable target alignment label.
- Qt Boundary emphasis status label now shows target mode, resolved target layer and whether the selected layer matches that target.
- Smoke verifies target alignment preview fields in launch packet, renderer capabilities and Qt source.

Decision:
- Boundary emphasis controls should make the active target explicit so researchers know whether a tuned EEZ/territorial overlay is applied to the layer they are currently inspecting.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Boundary target in Canvas Preview

Scope:
- Canvas Preview now shows Boundary target mode, resolved target layer and target alignment label next to Boundary highlight/identity.
- Canvas preview state/provenance now carries boundary emphasis target alignment fields for handoff inspection from the UI state packet.
- Smoke verifies the visible Boundary target line and provenance alignment fields.

Decision:
- The display view should expose which boundary layer is being emphasized, so a researcher can demonstrate or review the target state without switching back to the Layers dock.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Timeline boundary emphasis state

Scope:
- Qt timeline keyframes now capture `boundary_emphasis_control` alongside `boundary_highlight`.
- Applying a Qt timeline keyframe restores boundary emphasis target/color/contrast/opacity/gamma/breathing UI state.
- Timeline playback plan and segment state now include `boundary_emphasis_control` as a discrete keyframe field in Qt, no-GUI launch packet and renderer contracts.
- Renderer timeline ack preview now reports `boundary_emphasis_control` in detected/changed scope.

Decision:
- Boundary emphasis target state must be reproducible during demonstrations; the visual highlight mask alone is not enough to explain which research layer was intended as the active target.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Timeline keyframe boundary target summary

Scope:
- Qt timeline keyframe list now shows each keyframe's Boundary emphasis target mode, resolved target layer and target alignment.
- Added a shared keyframe list formatter so loaded profile keyframes and newly captured keyframes use the same summary.
- Smoke verifies the keyframe list formatter and boundary target summary string.

Decision:
- Demonstration workflows need to inspect boundary target state before playback without opening JSON or applying each keyframe.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Pin cursor fill status row

Scope:
- Qt Pin Annotation panel now has a fixed Cursor Fill status row showing whether Pin coordinates will use renderer globe raycast, Qt canvas fallback, or are still waiting.
- The Cursor Fill status refreshes through the same helper as the tool palette and after filling Pin coordinates from the cursor.
- Smoke verifies the fixed Pin cursor fill label and form row.

Decision:
- Researchers need to know which coordinate source is being used before placing geodetic Pins, especially when renderer raycast and Qt canvas estimates can disagree.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Pin coordinate source metadata

Scope:
- Qt Pin records now store `coordinate_source` and `coordinate_source_label` for manual lat/lon, renderer globe raycast and Qt canvas estimate placements.
- Pin tool summary now shows the active coordinate source separately from the live cursor fill availability.
- Pin list rows now include a source summary so saved research markers can be audited without opening JSON.

Decision:
- Researchers need provenance for how a Pin coordinate was produced, especially when cursor raycast and fallback estimates are both available.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Pin projection rule note

Scope:
- Qt Pin Annotation panel now shows a visible Projection note explaining that renderer Pins rotate with the globe every frame.
- The same note states that back-side Pins are hidden by horizon/depth occlusion.
- Smoke verifies both the rotation and occlusion wording in the Qt panel source.

Decision:
- Pin behavior must be understandable from the UI because researchers need to trust whether a marker should remain visible while the globe rotates.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Pin/Boundary handoff inspection summary

Scope:
- `pin_projection` contract now exposes Pin coordinate source fields, supported coordinate source values, Qt UI affordances, projection note text and Pin list source summary format.
- `scripts\inspect_handoff.ps1` now reports Pin coordinate-source/projection UI affordances and Boundary emphasis dialog feedback/target-alignment fields.
- Smoke gates the new handoff inspection fields so another cloned workstation can verify the Pin/Boundary UI loops without opening Qt.
- Fixed the Windows setup clone URL to `https://github.com/Kagamihara-Ruruka/RRKAL_displaytools.git`.

Decision:
- Cross-machine users need a read-only handoff check that summarizes the recently landed Pin coordinate provenance, Pin rotation/occlusion note and Boundary emphasis target alignment before starting Qt.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Profile schema Pin/Boundary/Timeline fields

Scope:
- Profile schema docs now describe Pin coordinate source metadata in `tool_state.pin` and saved `pins` records.
- Added `boundary_emphasis_control` schema documentation, including target alignment, dialog feedback and value preview fields.
- Canvas Preview schema docs now include Boundary emphasis target alignment provenance fields.
- Timeline keyframe docs now state that keyframes preserve Pins, Boundary highlight and Boundary emphasis control as discrete replay fields.

Decision:
- Cross-machine profile users need the schema docs to match the current Qt-first UI, launch packet and renderer handoff behavior without reading source code.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Renderer UI handoff contract list refresh

Scope:
- Renderer `ui_handoff_contracts` now lists `cursor_geodesy_readout`, `pin_overlay`, `boundary_emphasis_control`, and `boundary_highlight.ack_history` in addition to the existing canvas/layer/timeline contracts.
- Smoke now gates these new renderer capability discovery entries.

Decision:
- Cross-machine capability discovery should summarize the same Pin/Boundary UI loops that handoff inspection and Qt now expose, so users can verify them from `--print-renderer-capabilities` without opening Qt.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Closed-loop Pin/Boundary UI handoff evidence

Scope:
- Closed-loop status now includes `pin_boundary_ui_handoff` as a closed evidence group for Pin coordinate source metadata, Pin cursor fill UI, Pin projection notes, Boundary emphasis feedback/target alignment and Boundary ack history handoff.
- Timeline partial status now explicitly lists Boundary emphasis keyframe preservation and Timeline keyframe Boundary target summaries.
- Smoke gates the new `pin_boundary_ui_handoff` closed-loop id.

Decision:
- Progress inspection should expose the same Pin/Boundary UI loops now covered by Qt, launch packet, renderer capabilities and handoff inspection, rather than leaving them implicit in separate contracts.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Boundary identity source hint contract

Scope:
- Boundary identity status now exposes `identity_source_hint` in renderer, Qt and no-GUI launch packet contracts.
- The hint records current preview identity sources as source properties, maritime keys and closed-ring geometry.
- Smoke now verifies the source hint and `pending_backend_geometry_closure` marker across renderer, Qt, launch packet and closed-loop status files.

Decision:
- Territory/EEZ emphasis must be honest about provenance: displaytools can visualize and preserve source-property identity, while authoritative polygon identity and open-line area inference remain RRKAL/data-backend work.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Boundary identity source hint summary

Scope:
- Added `identity_source_hint_summary` beside the structured Boundary identity hint in renderer, Qt and launch packet contracts.
- The summary states preview sources, RRKAL-governed authoritative source requirements and open-line inference pending status in one handoff-friendly field.
- Smoke now checks that the structured hint, pending marker and summary field remain present together.

Decision:
- Cross-machine inspection should make the scientific/legal provenance boundary readable without requiring users to expand nested JSON.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Qt Boundary identity source visible summary

Scope:
- Qt `Boundary identity` summary now appends `source_hint=...` from `identity_source_hint_summary`.
- The same helper feeds both the Properties dock and Canvas Preview, so researchers can see preview identity provenance without opening JSON.
- Smoke now verifies the summary field across renderer, Qt, launch packet and closed-loop status, and checks that Qt visible text includes `source_hint=`.

Decision:
- Boundary/EEZ emphasis must surface its non-authoritative provenance directly in the scientific UI, not only in handoff packets.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Qt Boundary identity pending warning badge

Scope:
- Added a styled `boundaryIdentityWarningBadge` row to the Qt Properties dock below Boundary identity.
- The warning explicitly lists pending authoritative identity items and the open-line geometry closure status.
- Smoke now verifies the Qt badge marker and pending warning text.

Decision:
- Researchers need a visible caution badge before treating Boundary/EEZ emphasis as authoritative territory identity.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Canvas Preview Boundary identity warning provenance

Scope:
- Canvas Preview text now includes a `Boundary warning:` line using the same pending identity warning helper as Properties.
- Canvas meta text now includes `boundary_warning=...` for quick UI-state inspection.
- `canvas_preview` provenance now carries `boundary_identity_warning` and its UI surface description.
- Smoke verifies the visible Canvas Preview warning line and provenance field.

Decision:
- Boundary/EEZ provenance warnings must survive beyond the Properties dock so shared research state and copied provenance remain explicit.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - No-GUI launch packet Boundary identity warning

Scope:
- No-GUI launch packet `canvas_preview` now includes `boundary_identity_warning` and `boundary_identity_warning_surface` by default.
- The warning mirrors the Qt Canvas Preview / Properties provenance language for authoritative polygon and open-line inference pending status.
- Smoke now verifies the no-GUI launch packet source contains the warning field and surface description.

Decision:
- Cross-machine users should see the Boundary identity warning from launch packet inspection even before opening Qt.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Handoff inspection Boundary identity warning

Scope:
- `scripts\inspect_handoff.ps1` now emits a `canvas_preview` summary section for renderer sync and Boundary identity warning fields.
- Handoff inspection exposes `boundary_identity_warning` and `boundary_identity_warning_surface` from the launch packet.
- Smoke verifies the handoff script contains both warning output fields.

Decision:
- Cross-machine users should see the same Boundary/EEZ non-authoritative warning through one inspection command, without opening Qt or reading raw launch packet JSON.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Closed-loop Boundary identity warning handoff evidence

Scope:
- Closed-loop status now includes `boundary_identity_warning_handoff` as a closed evidence group.
- The group covers Qt Properties badge, Canvas Preview warning, canvas provenance, no-GUI launch packet, handoff inspection and smoke gates.
- The closed-loop boundary note explicitly keeps authoritative polygon identity and open-line area inference pending.

Decision:
- Warning/provenance delivery is now its own closed loop, while backend geospatial identity closure remains separate and should not be hidden inside UI completion.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Qt Layers workflow hint

Scope:
- Added a visible `layerWorkflowHint` callout to the Qt Layers dock.
- The hint explains row selection, Boundary/territorial sea/EEZ/high-seas double-click or Emphasis action, and the meaning of identity warning badges.
- Smoke now verifies the visible workflow hint, row-selection wording and non-authoritative identity warning wording.

Decision:
- Layer control should be operable by researchers without reading implementation notes; the UI needs to explain selection and Boundary emphasis workflows directly beside the layer stack.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Launch/Handoff Layers workflow hint

Scope:
- `layer_research_workflow` now exports `workflow_hint` and `workflow_hint_surface` from both Qt and no-GUI launch packet paths.
- `scripts\inspect_handoff.ps1` now reports the workflow hint for cross-machine operators.
- Smoke verifies the launch packet and handoff script expose the Boundary emphasis workflow hint.

Decision:
- Layer workflow guidance should be available from UI and handoff contracts, because clone-after-setup users may inspect the project before launching Qt.

Validation:
- Smoke passed on rerun before commit: first run hit a transient Windows permission lock on `taichi_global_bathymetry.py`; second run passed with `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Renderer capability Layers workflow hint

Scope:
- Renderer capability discovery now exposes the same `workflow_hint` and `workflow_hint_surface` in `layer_research_workflow`.
- Smoke verifies the renderer source carries the Boundary/territorial sea/EEZ/high-seas emphasis workflow hint.
- Closed-loop evidence now includes renderer capability discovery for the Layers workflow hint.

Decision:
- The same layer-selection and Boundary emphasis guidance should be visible from Qt, launch packets, handoff inspection and renderer capability discovery.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Closed-loop Layers workflow hint handoff evidence

Scope:
- Closed-loop status now includes `layer_workflow_hint_handoff` for the UI/operator guidance loop.
- The evidence covers Qt `layerWorkflowHint`, launch packet `layer_research_workflow.workflow_hint`, handoff inspection, renderer capability discovery and smoke gates.
- The boundary note keeps renderer layer picking and backend geospatial identity refinements separate.

Decision:
- Layer operation guidance is now a verifiable cross-machine UX contract, not just an in-UI note.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Profile UI state replay handoff loop

Scope:
- Added `rrkal_displaytools.profile_ui_state_replay.v1` across Qt, no-GUI launch packet and renderer capability discovery.
- Qt Layers dock now shows a `profileUiStateReplay` label describing portable UI replay coverage for renderer config, layer stack, pins, Boundary emphasis/warnings and Timeline keyframes.
- Handoff inspection now reports saved state groups, replay surfaces and summary text.
- Closed-loop status now includes `profile_ui_state_replay_handoff`.
- Smoke verifies the Qt label, launch packet, renderer capability, handoff and closed-loop evidence.

Decision:
- Profile replay needs a visible and machine-readable coverage summary so cross-machine users can distinguish portable UI state from RRKAL data governance or authoritative geospatial identity.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Profile schema UI state replay docs

Scope:
- `docs\PROFILE_SCHEMA.zh-TW.md` now documents `profile_ui_state_replay` as a profile/launch/capability/handoff coverage summary.
- The docs list `saved_state_groups`, `replay_surfaces`, Qt surface, launch packet fields, renderer capability field and handoff field.
- Smoke now verifies the profile schema docs include `profile_ui_state_replay`, saved state groups and replay surfaces.

Decision:
- Cross-machine users need the schema docs to explain portable UI/profile replay coverage without reading Qt, renderer or launch packet source.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Profile UI replay smoke source gates

Scope:
- Smoke now verifies `saved_state_groups` and `replay_surfaces` in Qt, renderer capability, no-GUI launch packet and handoff inspection sources.
- This strengthens `profile_ui_state_replay` from a name-only gate into a coverage-content gate.

Decision:
- Profile replay handoff should remain verifiable as a concrete coverage summary, not only as a schema id.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.


## 2026-05-30 - Qt Profile replay JSON action

Scope:
- Added a `Profile replay` action button to the Qt Actions panel.
- The action renders `collect_profile_ui_state_replay()` as JSON in the command/JSON preview pane.
- Closed-loop evidence now includes the Qt action, and smoke verifies the button plus `show_profile_ui_state_replay` handler.

Decision:
- Profile replay coverage should be inspectable directly inside Qt, not only through labels, launch packet or handoff output.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Qt Visual review Inspect group

Changes:
- Added `Inspect: Visual review` as a Qt Actions section for renderer pixel review.
- Renamed renderer thumbnail/live preview controls to `Inspect: Renderer thumbnail` and `Inspect: Live preview`.
- Added `renderer_thumbnail`, `live_preview`, and `visual_review` to `profile_ui_state_replay` across Qt, launch packet export, and renderer capability discovery.
- Documented the Visual review group in profile schema, clone quickstart, capability summary, and GTD.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Renderer menu Inspect label alignment

Changes:
- Renamed Renderer menu visual preview entries to `Inspect: Renderer thumbnail` and `Inspect: Live preview`.
- Added smoke gates for Renderer menu Inspect labels.
- Documented the menu/action vocabulary alignment for clone users and capability summary.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Qt Selection state Inspect action

Changes:
- Added `Inspect: Selection state` to the Qt Research interaction actions.
- Wired it to the existing layer pick state output so active layer selection/pick history/renderer target review has a clear researcher-facing entry.
- Added `selection_state` to profile UI replay metadata across Qt, launch packet export, and renderer capability discovery.
- Updated smoke and docs for the new selection inspector.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Active layer operation summary

Changes:
- Added a visible `Layer operation summary` label to the Qt Layers dock.
- The summary reports active layer identity, visibility, lock, opacity, blend mode, renderer target, runtime ack and pick context.
- Added `active_layer_operation_summary` to Qt launch/provenance packets.
- Added smoke and docs coverage for the new layer operation summary.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Last layer operation feedback

Changes:
- Added a visible `Last layer operation` label to the Qt Layers dock.
- Added `set_layer_operation_status()` and routed selected-layer visibility, lock, selected reset and stack reset messages through it.
- Added `last_layer_operation` to Qt launch/provenance packets.
- Added smoke/docs coverage for the operation event label and packet field.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Layer isolation/history operation feedback

Changes:
- Routed Solo selected layer, restore pre-solo visibility and layer undo status messages through `set_layer_operation_status()`.
- This keeps isolation/history workflow feedback visible in the Layers dock through `Last layer operation`.
- Added smoke/docs coverage for the Solo/restore/undo feedback path.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Layer group/preset operation feedback

Changes:
- Routed layer group toggles through `set_layer_operation_status()` with changed/skipped counts.
- Routed layer visual preset application through the same `Last layer operation` feedback path.
- Added smoke/docs coverage for group toggle and layer preset operation messages.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Layer operation feedback Inspect packet

Changes:
- Added `rrkal_displaytools.layer_operation_feedback.v1` for active layer operation summary, last operation, operator groups and undo depth.
- Added Qt `Inspect: Layer ops` in Research interaction.
- Exposed `layer_operation_feedback` in Qt launch/provenance packets, No-GUI launch packets and renderer capability discovery.
- Updated smoke/docs/closed-loop evidence for the layer operation feedback packet.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Handoff Layer ops review

Changes:
- Added `layer_operation_feedback` to `scripts\inspect_handoff.ps1`.
- Handoff output now reports launch packet schema, renderer capability schema, active summary, last operation, operator group summary and undo depth.
- Smoke now gates the handoff layer operation feedback path.
- Updated clone quickstart, capability summary and GTD for `-HandoffFirst` layer ops review.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.

## 2026-05-30 - Handoff profile/visual quick review

Changes:
- Added `profile_visual_quick_review` to `scripts\inspect_handoff.ps1`.
- Handoff output now reports Qt inspector group ids, Research interaction actions, Visual review actions and a recommended Inspect sequence.
- Smoke gates `layer_ops`, `renderer_thumbnail` and `live_preview` through handoff output.
- Updated clone quickstart, capability summary and GTD for cross-machine profile/visual quick review.

Validation:
- Smoke passed before commit: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`.
