# RRKAL_displaytools GTD

## Agent Exchange 工作流規則

- 新 session / 新 thread 開始時，先快速讀 `L:\AGENT_EXCHANGE\inbox\u_owner_all-projects.md`、`L:\AGENT_EXCHANGE\inbox\*_RRKAL_displaytools.md` 與 `L:\AGENT_EXCHANGE\inbox\*_RRKAL_project.md`。
- 每個 checkpoint 結束、更新 handoff / development log 前，再快速檢查一次 displaytools / RRKAL_project 收信檔。
- 大改、資料夾搬遷、OpenSpec、跨專案整合前，也要先讀交換區。
- `L:\AGENT_EXCHANGE` 不進 GitHub；只把驗證後的決策或工程結果消化進本 repo 的 GTD / handoff / docs / OpenSpec / code。
- 若 displaytools 發現需求或風險屬於其他專案，只寫交換區信件，不直接改對方 repo。

Last updated: 2026-05-30

## Current focus

| Area | Status | Current progress | Next step |
| --- | --- | --- | --- |
| Product positioning | MVP | Repo is positioned as RRKAL's visualization/display layer, not a duplicate data launcher. `docs/PRODUCT_POSITIONING.zh-TW.md` records the launcher-vs-renderer boundary. | Keep future code changes aligned with RRKAL-owned data governance and displaytools-owned renderer contracts. |
| Qt operator UI | MVP | Added `rrkal_displaytools_qt_panel.py`, a PyQt6 control panel with Photoshop-inspired workspace naming: tool options, Looks/templates, layers, properties, central preview, and actions. It supports layer toggles, grouped layer quick actions, style profiles, topo source, data mode, ocean material values, renderer launch/stop/restart, startup profile/template loading, template listing, renderer capability/layer manifest display, launch packet export, smoke check, process status polling, local/portable command copy, profile folders, profile load validation, local JSON layer profiles, repo-shared profile templates, Replay/contracts reviewer-route inspection, capability-summary inspection, extraction dry-run inspection, Visual review workspace-map inspection, and a visible reviewer path hint. `scripts/inspect_qt_uiux_surface.ps1` gives clone-first evidence for Qt-first grouping, research actions and layer operator closure. Tk is not the primary UI direction. | Move from grouped forms toward dockable Photoshop-like panels after renderer state boundaries are stable. |
| UIUX closure status | MVP | `visual_feature_closure_matrix`, `goal_closure_scorecard`, `closed_loop_status` and `visual_review_readiness` are exposed through `scripts/inspect_uiux_closure_status.ps1`; queued/under-construction items remain visible and are not reported as done. Qt Visual review now includes `Inspect: UIUX closure` so researchers can see ready/queued items in the command review pane. | Keep this closure board current while UIUX contracts settle; after 7:00, use it to avoid regressing UI surfaces during module extraction. |
| UIUX closure readiness | MVP | `scripts/check_uiux_closure_readiness.ps1` gives a single no-GUI pass/fail check over Qt-first UI, closure board, Timeline, layer presets, shortcuts, research interaction, renderer ports, reviewer route/capability summary, Qt workspace review path, clone quickstart alignment and disabled render-plan runtime merge. `scripts/check_pre7_closure_readiness.ps1` adds the compact pre-7 closure check across reviewer route, capability summary, UIUX closure, workspace map, extraction dry-run, source map, post-07 runbook, quickstart alignment and formal gate presence; Qt Replay/contracts, inspector index and reviewer packet now expose it for panel/no-GUI review, with `Copy pre-7 closure` for checkpoint handoff. | Use `scripts/check_pre7_closure_readiness.ps1` or the Qt `Inspect: Pre-7 closure` action, then `scripts/pre_decoupling_gate.ps1` at/after 7:00 before moving render-plan code. |
| Timeline UIUX | MVP | Timeline playback readiness, renderer runtime handoff, PNG/GIF/MP4 export, camera/ocean/layer interpolation and discrete layer visibility/blend hold are exposed through `scripts/inspect_timeline_uiux.ps1`; blend crossfade and visibility fade remain visible pending items. | After decoupling, keep timeline contracts wired while extracting renderer modules; only close pending interpolation items with runtime evidence. |
| Cross-machine onboarding / CI smoke | MVP | Added Windows helper scripts: `scripts/setup_windows.ps1`, `scripts/run_qt_panel.ps1`, `scripts/render_quick_smoke.ps1`, `scripts/smoke.ps1`, `scripts/list_visual_contract_inspectors.ps1` as a no-GUI reviewer command index, `scripts/export_visual_contract_review_packet.ps1` as the one-packet cloned-machine handoff, `scripts/check_cross_machine_review_readiness.ps1` as the public clone / first-run / review readiness pass-fail gate, `scripts/inspect_reviewer_first_run_route.ps1` as the researcher first-look route, and `scripts/export_capability_summary.ps1` as the post-push current/planned capability report source including pre-7 closure readiness and render-plan compose source-map readiness. `docs/QUICKSTART_CLONE.zh-TW.md` now points cloned machines to the Qt Reviewer route, Capability summary, UIUX closure, Workspace map, Extraction dry-run, Source map and Pre-7 closure actions. The inspector index now includes layer workflow, style routes, hydrology/LOD, Ocean material and UIUX readiness contracts. | Add richer troubleshooting only after another machine reports concrete setup friction. |
| Profile templates / launch packets | MVP | Added named baseline scientific, maritime hydrology, parchment review, tactical ops, and fast synthetic templates under `profiles/`; `docs/PROFILE_SCHEMA.zh-TW.md` documents the schema; `profile_schema.py` owns validation rules; `scripts/validate_profiles.py` checks required fields in smoke. | Tune the preferred visual baseline after user review, then add project-specific templates as needed. |
| Taichi globe prototype | MVP | `taichi_global_bathymetry.py` is imported as the current monolithic source of truth for the globe/bathymetry prototype and now exposes `--print-renderer-capabilities`. A bounded `--demo-closed-loop` preset exists, but the Qt panel defaults back to scientific/non-tactical baseline control. | Use the Qt panel for near-term visual review, then continue small reversible renderer slices inside the repo copy. |
| Hydrology and LOD hook | In progress | Hydrology readiness, layer diagnostics, LOD invalidation and layer-count contracts are represented in the prototype. The Qt panel exposes lake/river/border/maritime layer switches, and `scripts/inspect_hydrology_lod.ps1` exposes no-GUI readiness/runtime evidence review for lake/river renderer targets. | After 7:00 decoupling, extract Hydrology/LOD contracts from the monolith and connect them to the render-plan compose path. |
| Layer visual presets | MVP | Qt exposes all-context, hydrology-focus, boundary-focus and annotation-focus layer presets with brush/mask scope excluded; `scripts/inspect_layer_visual_presets.ps1` gives clone-first evidence that the selection tool is retained while brush/mask tools stay out of scope. | After decoupling, wire preset evidence into extracted layer/render-plan modules and measure renderer ack parity. |
| Layer operator shortcuts | MVP | Layer actions expose select, visibility, lock, opacity, blend, Boundary emphasis, solo/restore, undo/reset and diagnostics operations; `scripts/inspect_layer_operator_shortcuts.ps1` verifies keyboard shortcuts, active quick actions and copyable provenance without opening Qt. | Keep shortcut contracts stable while moving layer/render-plan code after 7:00. |
| Ocean material and sea-state port | In progress | Ocean material controls and sea-condition diagnostics exist as contract-oriented scaffolding. The Qt panel exposes wave strength, roughness, foam, Ocean 3D safe preview, control-board audit visibility, research-oriented performance budget presets, dialog cost estimate, and `scripts/inspect_ocean_material.ps1` for no-GUI contract review. | Keep scalar controls stable until 7:00, then move render-plan merge / pass reduction into the decoupling phase. |
| Research interaction UI | MVP | Qt exposes selected-layer review, cursor geodesy, Pin pick/occlusion and Boundary emphasis state; `scripts/inspect_research_interaction.ps1` gives clone-first no-GUI review evidence for these researcher interaction contracts, including Boundary RGB, contrast, opacity, gamma and breathing controls. | After decoupling, attach the inspector evidence to extracted render-plan/layer modules and refine authoritative polygon/EEZ identity separately. |
| Style renderer entries | MVP | Scientific/nautical/tactical/parchment style renderer entries and routes are explicit through Qt, launch packets, renderer capabilities, handoff, smoke, and the no-GUI `scripts/inspect_style_renderer_routes.ps1` inspector. | After decoupling, extract the style route registry out of the monolith and tune visual defaults from reviewer feedback. |
| Module boundaries | In progress | Monolith contains diagnostics for extraction readiness and seam matrices. `decoupling_readiness.py` records the `2026-05-31T07:00:00+08:00` not-before gate, post-7 extraction order, controlled interception policy, observability baseline, boundary inspector, render-plan compose work order and snapshot command; Qt/no-GUI reviewer packets expose it; Qt Replay/contracts exposes the snapshot command; `scripts/pre_decoupling_gate.ps1` verifies the first extraction, clean worktree, UIUX readiness, boundary inspector, render-plan compose work order and performance telemetry contract before code moves, and refuses formal execution before the 7:00 not-before timestamp. The pre-decoupling snapshot now embeds UIUX readiness, boundary inspection and render-plan compose work order for one-file handoff; `scripts/export_pre_decoupling_readiness_bundle.ps1` exposes the same readiness state plus embedded UIUX readiness without writing state; `scripts/check_pre_decoupling_readiness.ps1` gives a compact pass/fail check that also verifies the UIUX readiness pre-move requirement and embedded UIUX pass result; `scripts/inspect_render_plan_extraction_dry_run.ps1` gives a no-code-move checklist for the first post-7 extraction; `scripts/inspect_render_plan_compose_source_map.ps1` maps the first extraction helper lines across `taichi_global_bathymetry.py` and `render_core/render_plan.py`; `render_core/render_plan.py` now owns alpha compose helpers, compiled plan packet builder, reused compiled plan refresh helper, runtime snapshot builder, composition step builder, compose queue classifier, compose queue packet builder, compose-run builder, compose parity contract builder, single-pass preflight contract builder, apply-path builder, execution summary builder, execution phases builder, phase timing contract builder, bottleneck recommendation builder, phase timing runtime packet builder, metadata summary builder, cache key builder, cache invalidation reasons builder, cache invalidation scope builder and batch decisions builder while monolith methods preserve runtime contracts; `docs/MODULE_BOUNDARIES.zh-TW.md` records this concrete seam and keeps overlay ndarray / Qt / IO responsibilities in the controller boundary. | Continue extracting render-plan compose helpers in small smoke-gated slices. |
| Performance smoke and telemetry | In progress | `performance_telemetry.py` and `scripts/performance_smoke.ps1` produce lightweight displaytools timing outputs under `state/performance/`: structured performance summary, stage timing JSONL, and render telemetry schema for a headless tiny scene. Launch/reviewer/handoff packets and Qt Replay/contracts now expose the contract and output paths; Qt Renderer diagnostics can copy the queued render-plan work order. | After decoupling, attach real render-plan stage timings and keep RRKAL crawler/download/import performance smoke in RRKAL. |
| Layer render-plan performance | Planned | `layer_render_plan_performance` records the precompute-layer-state-then-single-render-pass target; `scripts/inspect_layer_render_plan_performance.ps1` now exposes the compose pass budget, merge preflight, disabled runtime merge and zero-diff parity requirements for clone-first review. `scripts/inspect_render_plan_single_pass_preflight.ps1` verifies the source-visible disabled single-pass gate, parity smoke gate, measured phase timing gate and manual review gate without launching Qt/Taichi. `scripts/inspect_render_plan_metadata_summary.ps1` verifies that renderer metadata preserves the full `layer_render_plan` and exposes `layer_render_plan_summary` without launching Qt/Taichi or writing metadata. | After 7:00 decoupling, extract render-plan compose into `render_core/render_plan.py` before enabling any collapsed compose-run candidate. |
| Spatial compression roadmap | Planned | `spatial_compression_roadmap.py` records DWT, spherical harmonics and neural-field options as contract-only strategy, with Qt Replay/contracts inspect/copy actions. | After render-plan decoupling, prototype spherical-harmonics LOD and DWT residual contracts with `rrkal-visual-compressor`; keep neural fields research-only until parity evidence exists. |
| Cloud/local workflow | MVP | `docs/WORKFLOW.zh-TW.md` and `docs/CODEX_CLOUD_HANDOFF.zh-TW.md` define GitHub as sync truth, `L:\\RRKAL_displaytools` as the local cloud-drive working copy, Codex Cloud as the long-running code/docs/CI surface, and local Windows as Qt/Taichi visual validation authority. | Convert the conversation backup step into a reusable skill after the private transcript repo policy is confirmed. |

## Working rules

- Visualization-first: renderer, material, style, LOD, diagnostics, display contracts.
- Qt/PyQt6-first for displaytools control UI; do not introduce Tk as the main UI path.
- RRKAL-first data governance: dataset discovery, download, import, install registry, manifest, cache lifecycle, and asset repair belong to `APIkeys_collection`.
- Do not commit generated caches, screenshots, logs, databases, virtual environments, secrets, or heavy local data.
- Every development round ends with docs/log update, smoke test, commit, push, a Chinese summary of current program capabilities, and a second summary of planned/next capabilities.
- Current user rule: before each commit, run at least a smoke test and record the result in `docs/DEVELOPMENT_LOG.zh-TW.md`.

## Backlog

- Move future development fully into `L:\RRKAL_displaytools`; avoid editing the old scratch source unless explicitly requested.
- Define the minimal renderer input contract expected from RRKAL tile/cache manifests.
- Create in-renderer layer toggles after the Qt launch panel proves the control model.
- Tune profile templates after the preferred visual baseline is confirmed.
- Separate diagnostics from render-loop code after contracts stabilize.
- Decide which local cache artifacts should later be registered by RRKAL as renderer bridge assets.

## Done
- 2026-05-30: Documented Cloud/local development workflow and handoff entrypoint, including private transcript backup policy and maturity reporting requirements.
- 2026-05-31: Added `renderer_config_gateway.py` as a typed pre-decoupling contract for replacing scattered `getattr(args, ...)` access.
- 2026-05-31: Exposed renderer config gateway through Qt Replay/contracts, launch packets, reviewer packets and handoff inspection.
- 2026-05-31: Added no-GUI renderer config gateway inspector for cross-machine clone/reviewer use.
- 2026-05-31: Added Qt copyable layer controls guide for researcher workflow, including pin occlusion and cursor geodesy reminders.
- 2026-05-31: Added displaytools performance smoke telemetry with JSON summary, JSONL stage timing and headless tiny render telemetry.
- 2026-05-31: Exposed performance smoke telemetry through launch/reviewer/handoff packets and Qt Replay/contracts.
- 2026-05-31: Added decoupling observability baseline to readiness/gate/runbook before post-7 module extraction.
- 2026-05-31: Added pre-decoupling snapshot exporter for one-file handoff before `render_plan_compose` extraction.
- 2026-05-31: Added Qt Replay/contracts controls for inspecting and copying the pre-decoupling snapshot command.
- 2026-05-31: Added Qt Ocean 3D board audit inspect/copy actions so control-board visibility evidence is directly reviewable.
- 2026-05-31: Added Ocean 3D dialog interactive cost estimate and dialog-level safe preview action so researchers can avoid heavy scalar settings during live review.
- 2026-05-31: Added `layerNavigationHint` so layer filter/group state explains whether to reveal selected, select first, clear filters or edit the visible active layer.
- 2026-05-31: Added copyable layer navigation summary contract/action so the current hint can be handed off with state, next action, selected layer, first visible row and UI-only boundary.
- 2026-05-31: Added no-GUI Layer workflow inspector and registered it in the visual contract review packet for clone-first UIUX inspection.
- 2026-05-31: Added no-GUI decoupling boundary inspector to prove the first code-move target and RRKAL data/cache boundary before post-7 extraction.
- 2026-05-31: Added decoupling boundary inspection into the pre-decoupling snapshot for one-file post-7 handoff.
- 2026-05-31: Added no-GUI render-plan compose work order inspector and embedded it in the pre-decoupling snapshot.
- 2026-05-31: Added render-plan compose work order inspector as required-before-move evidence in the pre-decoupling gate.
- 2026-05-31: Added no-GUI pre-decoupling readiness bundle for one-command gate/boundary/work-order handoff.
- 2026-05-31: Added no-GUI pre-decoupling readiness pass/fail check for the first extraction gate.
- 2026-05-31: Added formal pre-decoupling gate time enforcement so non-contract code movement cannot start before 07:00 +08:00.
- 2026-05-31: Added no-GUI Research interaction inspector for selected layer, cursor geodesy, Pin occlusion and Boundary emphasis review.
- 2026-05-31: Added Boundary emphasis RGB/contrast/opacity/gamma/breathing fields to the no-GUI Research interaction inspector.
- 2026-05-31: Added no-GUI Qt UIUX surface inspector for Qt-first panel grouping, research actions, renderer-port actions and layer operator closure.
- 2026-05-31: Added no-GUI Layer visual presets inspector for hydrology/boundary/annotation presets, brush/mask exclusion and retained selection mode.
- 2026-05-31: Added no-GUI cross-machine review readiness check for public clone target, first-run commands, portable review packet, UIUX readiness and pre-decoupling contract availability.
- 2026-05-31: Added no-GUI reviewer first-run route for clone setup, smoke, handoff, Qt review, research interaction, Ocean 3D board and visible pending UIUX items.
- 2026-05-31: Added no-GUI capability summary export for post-push current/planned feature reporting and boundary reminders.
- 2026-05-31: Added Qt Replay/contracts buttons for reviewer first-run route and capability summary inspection.
- 2026-05-31: Added Qt Visual review UIUX closure inspection button for visible ready/queued feature status.
- 2026-05-31: Added Qt Visual review workspace map inspection button for Photoshop-like dock roles and researcher flow.
- 2026-05-31: Updated clone quickstart with the current Qt reviewer route, capability summary, UIUX closure and workspace map actions.
- 2026-05-31: Added a visible Qt reviewer path hint above Actions for cloned-machine first-look routing.
- 2026-05-31: Expanded UIUX closure readiness to include reviewer route, capability summary, Qt reviewer path and clone quickstart alignment.
- 2026-05-31: Added UIUX readiness as a required pre-move step in the formal pre-decoupling gate.
- 2026-05-31: Updated compact pre-decoupling readiness check to verify the UIUX readiness pre-move requirement.
- 2026-05-31: Embedded UIUX readiness in the pre-decoupling readiness bundle and compact readiness result.
- 2026-05-31: Embedded UIUX readiness in the pre-decoupling one-file snapshot.
- 2026-05-31: Added no-code-move render-plan extraction dry-run inspector for the first post-7 extraction.
- 2026-05-31: Added Qt Replay/contracts entry for render-plan extraction dry-run inspection.
- 2026-05-31: Updated clone quickstart with the Qt Extraction dry-run route.
- 2026-05-31: Added no-GUI Layer render-plan performance inspector for the post-decoupling single-pass optimization path and parity guard.
- 2026-05-31: Added no-GUI UIUX closure status inspector so ready, queued and excluded UI features stay reviewable.
- 2026-05-31: Added no-GUI Layer operator shortcuts inspector for keyboard shortcuts, active quick actions, operation groups and provenance review.
- 2026-05-31: Added no-GUI Timeline UIUX inspector for playback readiness, animation export, interpolation support and visible pending items.
- 2026-05-31: Added no-GUI UIUX closure readiness check for one-command pre-7 UIUX pass/fail review.
- 2026-05-31: Added Qt copyable render-plan work order summary for the post-decoupling single-pass optimization path.
- 2026-05-31: Added contract-only spatial compression roadmap and Qt inspect/copy actions for DWT, spherical harmonics and neural-field strategy boundaries.
- 2026-05-31: Added no-GUI style renderer routes inspector for parchment/tactical/scientific/nautical entrypoint review.
- 2026-05-31: Added no-GUI Hydrology/LOD inspector for lake/river target, LOD hook, runtime state/ack/pick bridge review.
- 2026-05-31: Added no-GUI Ocean material inspector for Ocean 3D control-board, safe-preview, renderer apply and sea-state scalar contract review.
- 2026-05-31: Added visual contract inspector index for cloned-machine no-GUI reviewer command discovery.
- 2026-05-31: Added visual contract review packet exporter for cloned-machine no-GUI handoff.
- 2026-05-31: Hardened pre-decoupling snapshot export against transient cloud-drive file locks during smoke.
- 2026-05-31: Added `compat/headless_import_shims.py` with a smoke-gated synthetic sys.modules interception self-test.
- 2026-05-31: Added Qt `Inspect: Interception` and `Copy interception summary` for bounded shim/hook policy review.
- 2026-05-30: Added controlled interception policy to launch/reviewer packet handoff for cross-machine review.
- 2026-05-30: Added `rrkal_displaytools.controlled_interception_policy.v1` for bounded import/output/runtime interception during smoke, handoff and module extraction.
- 2026-05-30: Suppressed transient cloud-drive retry noise in passing smoke logs while preserving final failure output.
- 2026-05-30: Added Qt `Copy decoupling summary` for handoff-friendly post-7 extraction readiness.
- 2026-05-30: Added `docs/DECOUPLING_RUNBOOK.zh-TW.md` and linked it from handoff docs for the post-7 renderer extraction phase.
- 2026-05-30: Added a clean-worktree guard to the pre-decoupling gate for post-7 renderer extraction.
- 2026-05-30: Added explicit Asia/Taipei schedule metadata to the decoupling readiness packet for the 2026-05-31 07:00 not-before gate.
- 2026-05-30: Added `scripts/pre_decoupling_gate.ps1` to check render-plan-first extraction and RRKAL boundary before the decoupling phase.
- 2026-05-30: Added `decoupling_readiness` to launch/reviewer packet handoff so Cloud/local reviewers can inspect post-7 extraction order without opening Qt.
- 2026-05-30: Added a reusable Qt `collect_decoupling_readiness()` collector for later reviewer/launch packet handoff.
- 2026-05-30: Added Qt `Inspect: Decoupling` so the post-7 renderer extraction order is visible from the control panel.
- 2026-05-30: Added bounded retry/backoff for smoke and handoff Python commands to tolerate transient cloud-drive `Errno 13` file-access denial.
- 2026-05-30: Added smoke coverage for the decoupling readiness packet and render-plan-first extraction rule.
- 2026-05-30: Added a standalone decoupling readiness packet for the pre-7:00 UI closure phase and post-7:00 renderer extraction order.
- 2026-05-30: Added Qt Ocean 3D performance budget presets and synced them into the ocean material control port while keeping true render-pass optimization queued for decoupling.
- 2026-05-30: Added smoke-gated cursor geodesy state/ack bridge contract for renderer cursor raycast runtime wiring.
- 2026-05-30: Repaired the Capability Summary Canvas Preview mojibake introduced during cursor raycast contract work.
- 2026-05-30: Added `cursor_geodesy.py` renderer-facing cursor raycast helper and smoke-gated `rrkal_displaytools.cursor_geodesy_raycast.v1` evidence.
- 2026-05-30: Aligned the Qt Boundary emphasis status label with the wired renderer bridge and added a smoke guard against stale queued wording.
- 2026-05-30: Added `-HandoffFirst` to `scripts/run_qt_panel.ps1` and smoke-gated the cross-machine handoff-first Qt launch command.
- 2026-05-30: Added smoke-gated `rrkal_displaytools.layer_selection_tool.v1` for Qt-first layer selection, filtered/revealed row selection and renderer pick-state inspection while keeping brush/mask scope excluded.
- 2026-05-30: Mapped Qt boundary emphasis Apply state into the existing boundary highlight renderer bridge and smoke-gated RGB/contrast/alpha/gamma/breathing mapping evidence.
- 2026-05-30: Added smoke-gated Pin projection evidence for globe-rotation tracking and horizon occlusion through `rrkal_displaytools.pin_projection.v1`.
- 2026-05-30: Added smoke-gated `rrkal_displaytools.cursor_geodesy_readout.v1` for guarded canvas mouse lon/lat readout; renderer globe raycast contract is now smoke-gated through `cursor_geodesy.viewport_sphere_raycast`, with Taichi mouse-state wiring still pending.
- 2026-05-30: Routed boundary-capable layer row double-clicks to the Qt boundary emphasis dialog and added smoke-gated contract evidence for the binding.
- 2026-05-30: Added `rrkal_displaytools.boundary_emphasis_control.v1` and a Qt Layers dock dialog for RGB/contrast/opacity/gamma/breathing territory emphasis controls; renderer mask hook remains queued for backend implementation.
- 2026-05-30: Added `rrkal_displaytools.layer_research_workflow.v1` and a Qt Layers dock workflow label linking filter/group/selected-layer/runtime-warning/remediation state.
- 2026-05-30: Added a Qt Layers dock cross-machine clone readiness label and smoke gates for its launch/renderer Qt surface.
- 2026-05-30: Added `rrkal_displaytools.cross_machine_clone_readiness.v1` so cross-machine clone/setup/smoke/run readiness is visible through launch packets, renderer capabilities, handoff and smoke.
- 2026-05-30: Added `rrkal_displaytools.module_boundary_registry.v1` so future decoupling boundaries are visible through launch packets, renderer capabilities, handoff and smoke.
- 2026-05-30: Added `rrkal_displaytools.style_profile_renderer_routes.v1` so parchment/tactical style renderer routes are explicit and portable through launch packets, renderer capabilities, handoff and smoke.
- 2026-05-30: Added `rrkal_displaytools.ocean_material_control_port.v1` so Qt ocean material controls and scalar sea-state handoff fields are visible through launch packets, renderer capabilities, handoff and smoke.
- 2026-05-30: Added `rrkal_displaytools.hydrology_lod_runtime_evidence.v1` so Hydrology/LOD readiness is tied to renderer ack and selected-layer pick evidence across Qt, launch packets, renderer capabilities, handoff and smoke.
- 2026-05-30: Added `rrkal_displaytools.hydrology_lod_readiness.v1` so lake/river hydrology layer targets and LOD hook evidence are visible through Qt, launch packets, renderer capabilities, handoff and smoke.
- 2026-05-30: Added `rrkal_displaytools.layer_visual_preset_runtime_feedback.v1` so layer presets expose renderer ack feedback in the Qt Layers dock and through launch packets, renderer capabilities, handoff and smoke.
- 2026-05-30: Added `rrkal_displaytools.layer_visual_presets.v1` and Qt Layers dock preset buttons for All / Hydrology / Boundary / Annotations, preserving locked layers and exposing the contract through launch packets, renderer capabilities, handoff and smoke.
- 2026-05-30: Added `rrkal_displaytools.profile_launch_readiness_ui.v1` and a Qt Layers dock readiness label so profile/launch readiness is visible in the UI and verifiable through launch packets, renderer capabilities, handoff and smoke.
- 2026-05-30: Added `rrkal_displaytools.profile_launch_readiness.v1` so cross-machine profile/launch/portable-command/renderer-discovery readiness is visible through Qt, launch packets, renderer capabilities, handoff and smoke.
- 2026-05-30: Added `rrkal_displaytools.style_renderer_entries.v1` so scientific / nautical / parchment / tactical renderer entries are discoverable through Qt, launch packets, renderer capabilities, handoff and smoke.
- 2026-05-30: Added `rrkal_displaytools.layer_operator_groups.v1` so layer operations are grouped into Selection / Edit state / Isolation / History / Diagnostics across Qt UI, launch packets, renderer capabilities, handoff and smoke.

- 2026-05-30: Added layer operator shortcuts contract and Qt keyboard shortcuts for Photoshop-like layer operations across launch packets, renderer capabilities, handoff inspection and smoke.
- 2026-05-30: Added renderer diagnostics remediation hints across Qt Properties, launch packets, renderer capabilities, handoff inspection and smoke.
- 2026-05-30: Added renderer diagnostics detail bridge breakdown across Qt Properties, launch packets, renderer capabilities, handoff inspection and smoke.
- 2026-05-29: Added renderer diagnostics summary across Qt Properties, launch packets, renderer capabilities, handoff inspection and smoke.
- 2026-05-29: Added RRKAL-governed authoritative identity source reference-only handoff for territory/EEZ identity.
- 2026-05-29: Added layer territory identity context that preserves source-property feature identity while marking authoritative polygon identity pending.
- 2026-05-29: Added layer runtime interaction context tying warnings to renderer pick target, hit status and source-property feature identity.
- 2026-05-29: Added researcher-facing layer runtime warning list across Qt Properties, provenance, launch packets, renderer capabilities, handoff inspection and smoke.
- 2026-05-29: Added copyable layer runtime badge summary provenance across Qt, launch packets, renderer capabilities, handoff inspection and smoke.
- 2026-05-29: Added layer runtime evidence summary contract for Qt Properties, launch packets, renderer capabilities, handoff inspection and smoke.
- 2026-05-29: Added runtime badge color/legend contract to the layer capability matrix and Qt Layers dock.
- 2026-05-29: Added Qt Layers runtime evidence badges for per-layer renderer ack status.
- 2026-05-29: Added layer runtime evidence schema to connect renderer ack results with the layer capability matrix.
- 2026-05-29: Added layer capability matrix to read-only handoff inspection for cross-machine clone checks.
- 2026-05-29: Added layer capability matrix contract for Qt/No-GUI/renderer capability discovery and active layer UI diagnostics.
- 2026-05-29: Added Qt/No-GUI Timeline export options controls and profile schema support for export-on-launch, GIF, and MP4.
- 2026-05-29: Added optional Timeline MP4 video export through `--timeline-export-mp4` / `TIMELINE_EXPORT_MP4`, with Qt/No-GUI/capability/smoke contracts.
- 2026-05-29: Created and pushed the GitHub repo `Kagamihara-Ruruka/RRKAL_displaytools`.
- 2026-05-29: Imported the current Taichi globe prototype and minimal governance docs.
- 2026-05-29: Added RRKAL-aligned documentation governance skeleton and product positioning.
- 2026-05-29: Added `--demo-closed-loop` as the first bounded showcase path for the existing renderer stack.
- 2026-05-29: Added a PyQt6 operator panel for layer/style/material launch control.
- 2026-05-29: Added Qt panel save/load JSON profiles and apply-by-restart flow.
- 2026-05-29: Added repo-shared profile templates and Qt template loading.
- 2026-05-29: Added profile template names/descriptions for clearer Qt selection.
- 2026-05-29: Added profile schema documentation for RRKAL/displaytools handoff.
- 2026-05-29: Added Qt panel command copy and profile directory shortcuts.
- 2026-05-29: Added Qt panel renderer process status polling.
- 2026-05-29: Added centralized Windows smoke helper script.
- 2026-05-29: Routed Qt panel smoke action through scripts/smoke.ps1 on Windows.
- 2026-05-29: Added Windows setup and Qt panel launch scripts for another computer.
- 2026-05-29: Added Qt panel grouped layer quick actions.
- 2026-05-29: Added startup profile loading for the Qt panel and run script.
- 2026-05-29: Added startup template-name loading for built-in profiles.
- 2026-05-29: Added no-GUI template listing for built-in profiles.
- 2026-05-29: Made no-GUI template listing return before PyQt6 import.
- 2026-05-29: Added profile template validation to smoke.
- 2026-05-29: Hardened smoke helper to fail on native command errors and tolerate UTF-8 BOM profile files.
- 2026-05-29: Added Qt panel profile load validation.
- 2026-05-29: Extracted shared profile schema validation module.
- 2026-05-29: Added no-GUI launch packet exporter and smoke coverage.
- 2026-05-29: Added GitHub Actions Windows smoke workflow.
- 2026-05-29: Added Windows setup document for another computer.
- 2026-05-29: Added Qt panel smoke-check action.
- 2026-05-29: Added Qt launch packet export for handoff/debugging.
- 2026-05-29: Added Windows quick headless render helper script.
- 2026-05-29: Added portable command copy and launch-packet portable command fields.
- 2026-05-29: Reworked Qt operator actions into a grid layout.
- 2026-05-29: Added renderer capabilities JSON CLI output.
- 2026-05-29: Added Qt panel renderer capabilities display action.





















- 2026-05-29: Added no-GUI profile schema contract JSON output and repaired README command fences.
- 2026-05-29: Added RRKAL handoff contract documentation for no-GUI integration endpoints.
- 2026-05-29: Added current capability summary documentation for push reports.
- 2026-05-29: Added renderer layer manifest JSON output and smoke coverage.
- 2026-05-29: Reframed Qt panel labels toward a Photoshop-inspired workspace and added layer manifest display action.
- 2026-05-29: Added Qt Studio menu bar and left tools dock toward Photoshop-like workspace structure.
- 2026-05-29: Moved layer controls into a right-side dockable Qt Layers panel.
- 2026-05-29: Moved ocean material controls into a dockable Qt Properties panel.
- 2026-05-29: Added dockable Qt Navigator and History panels with construction placeholders.
- 2026-05-29: Added local workspace layout save/load/reset for dock/window state.
- 2026-05-29: Added Timeline camera keyframe controls and renderer discrete camera apply contract.
- 2026-05-29: Added Timeline camera keyframe interpolation for renderer playback and PNG export manifests.
- 2026-05-29: Added Timeline GIF animation export fallback for dependency-light sharing.
- 2026-05-29: Added Timeline layer opacity interpolation for renderer playback and export manifests.
- 2026-05-29: Added Timeline layer visibility/blend discrete hold contract for renderer playback and export manifests.
- 2026-05-30: Wired cursor geodesy renderer state/ack bridge for mouse press/move lat-lon readout.
- 2026-05-30: Added Qt readback for renderer cursor geodesy state/ack in Canvas Preview and provenance.
- 2026-05-30: Made Pin cursor fill prefer renderer cursor geodesy state before Qt canvas estimate fallback.
- 2026-05-30: Added renderer-first Pin cursor fill priority to shared contract discovery and smoke gates.
- 2026-05-30: Added Tools dock status for Pin cursor fill source provenance.
- 2026-05-30: Added screen-position provenance to renderer layer pick state and Qt diagnostics.
- 2026-05-30: Promoted layer pick screen-position diagnostics into active-layer launch/capability contracts.
- 2026-05-30: Added active-layer screen-position diagnostics to handoff inspection and smoke gates.
- 2026-05-30: Added layer pick history entries with screen-position provenance.
- 2026-05-30: Added boundary highlight ack history to Qt History and research provenance.
- 2026-05-30: Promoted boundary highlight ack history into launch/capability/handoff contracts.
- 2026-05-30: Added smoke-gated boundary identity applied/pending markers to renderer capabilities and handoff inspection.
- 2026-05-30: Showed boundary identity applied/pending markers in Qt Properties and Canvas Preview.
- 2026-05-30: Added Boundary emphasis dialog RGB swatch/live numeric preview and smoke-gated the dialog feedback contract.
- 2026-05-30: Added visible Boundary layer Emphasis action badges and smoke-gated the layer action contract.
- 2026-05-30: Added Boundary emphasis target alignment fields and Qt status display.
- 2026-05-30: Added Boundary target alignment to Canvas Preview and canvas provenance state.
- 2026-05-30: Added Boundary emphasis control preservation to timeline keyframes and renderer timeline ack contracts.
- 2026-05-30: Added Boundary target summaries to Timeline keyframe list rows.
- 2026-05-30: Added fixed Pin cursor fill source status row in the Qt Pin panel.
- 2026-05-30: Added Pin coordinate source metadata and list-row source summaries.
- 2026-05-30: Added visible Pin projection rotation/occlusion note to the Qt Pin panel.
- 2026-05-30: Added Pin/Boundary UI affordance fields to handoff inspection and fixed the Windows setup GitHub clone URL.
- 2026-05-30: Updated profile schema docs for Pin coordinate source, Boundary emphasis alignment and Timeline keyframe preservation.
- 2026-05-30: Refreshed renderer `ui_handoff_contracts` with cursor geodesy, Pin overlay, Boundary emphasis and Boundary ack history.
- 2026-05-30: Added closed-loop evidence for Pin/Boundary UI handoff and Timeline Boundary emphasis preservation.
- 2026-05-30: Added boundary identity source hint fields across renderer, Qt, launch packets, closed-loop status and smoke gates so territory/EEZ emphasis provenance remains explicit before backend identity closure.
- 2026-05-30: Added compact Boundary identity source hint summaries so clone/handoff inspection can show preview sources and pending backend geometry closure without nested JSON expansion.
- 2026-05-30: Surfaced Boundary identity `source_hint=` in Qt Properties and Canvas Preview, with smoke coverage for visible provenance text.
- 2026-05-30: Added a Qt Properties Boundary identity warning badge for pending authoritative polygon/EEZ identity and open-line geometry closure.
- 2026-05-30: Added Boundary identity warning text to Canvas Preview, canvas meta and `canvas_preview.boundary_identity_warning` provenance.
- 2026-05-30: Added no-GUI launch packet `canvas_preview.boundary_identity_warning` and smoke coverage for cross-machine warning inspection.
- 2026-05-30: Added Boundary identity warning fields to handoff inspection output and smoke coverage.
- 2026-05-30: Added `boundary_identity_warning_handoff` closed-loop evidence while keeping authoritative polygon/EEZ and open-line backend work pending.
- 2026-05-30: Added Qt Layers dock workflow hint for row selection, Boundary emphasis entry points and non-authoritative identity warnings.
- 2026-05-30: Added launch packet and handoff inspection workflow hints for layer row selection and Boundary emphasis entry points.
- 2026-05-30: Added renderer capability discovery support for the Layers workflow hint and smoke coverage.
- 2026-05-30: Added `layer_workflow_hint_handoff` closed-loop evidence for layer workflow guidance across Qt, launch packet, handoff, capabilities and smoke.
- 2026-05-30: Added `profile_ui_state_replay_handoff` for portable profile/UI replay coverage across Qt, launch packet, capabilities, handoff and smoke.
- 2026-05-30: Documented `profile_ui_state_replay` in the profile schema and smoke-gated the docs.
- 2026-05-30: Strengthened smoke gates for `profile_ui_state_replay` saved groups and replay surfaces across Qt, capabilities, launch packet and handoff.
- 2026-05-30: Added Qt `Profile replay` action for inspecting `profile_ui_state_replay` JSON directly in the panel.
- 2026-05-30: Added Qt `Ocean port` action for inspecting the scalar ocean material / sea-state handoff JSON directly in the panel.
- 2026-05-30: Added Qt `Hydro LOD` action for inspecting Hydrology/LOD readiness and runtime evidence JSON directly in the panel.
- 2026-05-30: Added Qt `Style routes` action for inspecting parchment/tactical style renderer entries and routes JSON directly in the panel.
- 2026-05-30: Added Qt `Module seams` action for inspecting future extraction/module boundary registry JSON directly in the panel.
- 2026-05-30: Added Qt `Clone ready` action for inspecting cross-machine clone readiness JSON directly in the panel.
- 2026-05-30: Added tooltips/accessibility descriptions for Qt contract inspector buttons so researchers can understand each JSON inspection surface.
- 2026-05-30: Added Qt `Pin pick` action for inspecting renderer Pin hover/click pick bridge JSON directly in the panel.
- 2026-05-30: Added Qt `Cursor geo` action for inspecting mouse latitude/longitude readout and renderer cursor geodesy bridge JSON directly in the panel.
- 2026-05-30: Added Qt `Boundary JSON` action for inspecting Boundary emphasis, identity warning and renderer ack JSON directly in the panel.
- 2026-05-30: Added `Inspect:` prefixes to Qt JSON inspector action buttons to clarify which buttons inspect state rather than mutate renderer/profile state.
- 2026-05-30: Added clone quickstart guidance for the Qt `Inspect:` actions and smoke-gated the clone-readiness / Boundary JSON references.
- 2026-05-30: Added `Qt Inspect actions` to `profile_ui_state_replay.replay_surfaces` across Qt, launch packet, renderer capabilities, schema docs and smoke.
- 2026-05-30: Added `qt_inspector_action_ids/labels/count` to `profile_ui_state_replay` and smoke-gated Boundary/Cursor/Clone inspector entries.
- 2026-05-30: Added `qt_inspector_action_groups/group_count` to `profile_ui_state_replay` for replay/contracts, renderer ports and research interaction inspector grouping.
- 2026-05-30: Updated clone quickstart to mirror the Qt Inspect groups and smoke-gated Replay/contracts plus Research interaction guidance.
- 2026-05-30: Added Inspect group names to Qt tooltips/accessibility descriptions and smoke-gated grouped tooltip text.
- 2026-05-30: Split the Qt Actions grid into section headers for Run/profile, Inspect groups, Renderer diagnostics and Process, with smoke-gated section markers.
- 2026-05-30: Added Qt `Inspect: Layer runtime` and `Inspect: Layer pick` actions, and included them in profile replay inspector IDs/groups and clone quickstart guidance.
- 2026-05-30: Added Qt `Inspect: Layer matrix` action for direct layer capability matrix inspection and synced it to profile replay inspector contracts and quickstart.
- 2026-05-30: Added Qt `Inspect: Timeline` action for direct Timeline runtime/keyframe/export contract inspection and synced it to profile replay inspector contracts and quickstart.
- 2026-05-30: Added Qt `Inspect: Canvas state` to the Research interaction section and synced it to profile replay inspector contracts and clone quickstart guidance.


## 2026-05-30 - Qt Visual review Inspect group

Done:
- Added `Inspect: Visual review` as a separate Qt Actions section.
- Mapped renderer thumbnail and live preview actions into `profile_ui_state_replay.qt_inspector_action_groups.visual_review`.
- Kept diagnostics/remediation controls separate from visual pixel inspection.

Next:
- Continue closing UIUX loops before backend closure, especially layer selection feedback and scientific annotation review.


## 2026-05-30 - Renderer menu Inspect label alignment

Done:
- Renamed Renderer menu thumbnail/live preview entries to the same `Inspect:` labels used by the Actions panel.
- Added smoke coverage so menu labels cannot drift from visual review actions.

Next:
- Continue UIUX closure on selection/layer operation feedback for research workflows.


## 2026-05-30 - Qt Selection state Inspect action

Done:
- Added `Inspect: Selection state` to Research interaction.
- Reused the existing layer pick state handler so active layer selection has a task-oriented inspection entry without duplicating backend state.
- Added smoke/docs gates for `selection_state`.

Next:
- Continue improving layer operation feedback and research annotation review before backend closure.


## 2026-05-30 - Active layer operation summary

Done:
- Added a visible `Layer operation summary` label to the Layers dock.
- The summary reports active layer identity, visibility, lock, opacity, blend, renderer target, runtime ack and pick context.
- Added `active_layer_operation_summary` to Qt launch/provenance packets and smoke gates.

Next:
- Continue UIUX closure around layer operation feedback, especially clearer status after layer isolation/restore/undo.


## 2026-05-30 - Last layer operation feedback

Done:
- Added a visible `Last layer operation` label to the Layers dock.
- Routed selected-layer visibility, lock, selected reset and stack reset messages through the same operation status helper.
- Added `last_layer_operation` to Qt launch/provenance packets and smoke gates.

Next:
- Extend the same feedback path to solo/restore/undo/isolation actions.


## 2026-05-30 - Layer isolation/history operation feedback

Done:
- Routed Solo selected layer, restore pre-solo visibility and layer undo messages through `set_layer_operation_status()`.
- Added smoke/docs gates so isolation/history actions keep updating `Last layer operation`.

Next:
- Continue closing layer operation feedback for group toggles and preset application.


## 2026-05-30 - Layer group/preset operation feedback

Done:
- Routed layer group toggles through `set_layer_operation_status()` with changed/skipped counts.
- Routed layer visual preset application through the same operation feedback path.
- Added smoke/docs gates for group toggle and layer preset operation messages.

Next:
- Continue UIUX closure on layer operation provenance and profile replay discoverability.


## 2026-05-30 - Layer operation feedback Inspect packet

Done:
- Added `rrkal_displaytools.layer_operation_feedback.v1`.
- Added Qt `Inspect: Layer ops` for active layer operation summary, last operation, operator groups and undo depth.
- Exposed `layer_operation_feedback` in Qt launch/provenance, No-GUI launch packet and renderer capability discovery.

Next:
- Continue UIUX closure on profile replay discoverability and cross-machine review flows.


## 2026-05-30 - Handoff Layer ops review

Done:
- Added `layer_operation_feedback` to `scripts\inspect_handoff.ps1`.
- Smoke now verifies handoff launch packet and renderer capability schemas for layer operation feedback.
- Updated clone/capability docs for `-HandoffFirst` review of layer operation state.

Next:
- Continue tightening cross-machine quick review around profile replay and visual review actions.


## 2026-05-30 - Handoff profile/visual quick review

Done:
- Added `profile_visual_quick_review` to `scripts\inspect_handoff.ps1`.
- The handoff summary now reports Research interaction and Visual review action ids plus a recommended Inspect sequence.
- Smoke gates `layer_ops`, `renderer_thumbnail` and `live_preview` availability through handoff output.

Next:
- Continue closing visual review around renderer thumbnail/live preview availability and missing-frame guidance.


## 2026-05-30 - Visual review readiness handoff

Done:
- Added `visual_review_readiness` to `scripts\inspect_handoff.ps1`.
- Handoff now reports renderer thumbnail/live preview readiness and missing-frame guidance before Qt launch.
- Smoke gates readiness flags and guidance text.

Next:
- Continue moving the same review clarity into Qt-side user-facing Inspect output where useful.


## 2026-05-30 - Qt visual readiness capability

Done:
- Added `visual_review_readiness` to launch packets and renderer capability discovery.
- Added `Inspect: Visual readiness` to the profile replay Visual review group.
- Handoff and smoke now gate the launch packet schema, renderer capability schema and Qt action id.

Next:
- Continue closing Qt visual review by surfacing thumbnail/live preview frame status in the user-facing payload.


## 2026-05-30 - Visual review frame status

Done:
- Added `visual_review_frame_status` metadata to `visual_review_readiness`.
- Renderer thumbnail and live preview now report separate `inspect_action_available` / `runtime_dependent` status.
- Handoff and smoke gate both frame-status entries.

Next:
- Continue wiring UI labels so Qt can show readiness, frame status and missing-frame hints in one inspector view.


## 2026-05-30 - Visual review inspector view

Done:
- Added `visual_review_inspector_view` metadata to `visual_review_readiness`.
- The view packages title, Qt surface, status badges, rows, hints and copyable flag.
- Handoff and smoke gate the inspector view schema and key UI fields.

Next:
- Continue closing actual Qt command wiring so the `Inspect: Visual readiness` action can render this packet directly.


## 2026-05-30 - Visual readiness Qt command contract

Done:
- Added `visual_review_qt_command_contract` metadata to `visual_review_readiness`.
- The contract maps `Inspect: Visual readiness` to `visual_review_readiness.inspector_view`.
- Handoff and smoke gate the contract schema, action id, payload field and dispatch status.

Next:
- Implement actual monolith Qt dispatch for `visual_readiness`, then split toward `qt_ui/main_window.py` when the UI module boundary is ready.


## 2026-05-30 - Qt Visual readiness action

Done:
- Added `Inspect: Visual readiness` to the Qt Visual review button group and Renderer menu.
- Added `visual_review_readiness_packet`, collector and display method to `rrkal_displaytools_qt_panel.py`.
- Updated the command contract implementation status to `wired_in_qt_panel`.
- Smoke gates the Qt packet, button, collector, action and implementation status.

Next:
- Continue tightening the visual review UI by summarizing thumbnail/live preview runtime artifact state in the visible status area.


## 2026-05-30 - Qt Visual readiness runtime artifacts

Done:
- `collect_visual_review_readiness()` now adds runtime artifact status for renderer thumbnail and live preview.
- Existing frame-status rows are updated with `frame_available` / `runtime_dependent` and artifact paths when available.
- Smoke gates the Qt collector runtime artifact checks.

Next:
- Continue making the Qt visual review panel more user-facing by turning readiness JSON into a compact visible summary.


## 2026-05-30 - Qt Visual readiness visible summary

Done:
- Added the `visualReviewReadiness` label to the Layers dock.
- `Inspect: Visual readiness` now updates a compact thumbnail/live-preview status summary.
- Smoke gates the label object name, formatter and updater.

Next:
- Continue tightening visual review by adding a lightweight copy/share path for the compact summary.


## 2026-05-30 - Qt Visual readiness copy summary

Done:
- Added `Copy visual summary` to the Visual review action group.
- Added `copy_visual_review_readiness_summary()` to copy the compact status summary to the clipboard.
- Smoke gates the copy button and action.

Next:
- Continue tightening visual review by aligning the copy summary with profile/launch packet handoff labels.


## 2026-05-30 - Visual readiness copy summary contract

Done:
- Added `visual_review_copy_summary_contract` to visual readiness packets.
- Handoff now exports the copy-summary contract.
- Qt summary formatting now reads the contract label.
- Smoke gates the contract schema, label object, copy action and portability flag.

Next:
- Continue aligning profile/launch/handoff labels for layer selection and boundary emphasis controls.


## 2026-05-30 - Layer selection summary contract

Done:
- Added `layer_selection_summary_contract` to layer selection packets.
- Added `Copy selection summary` to the Qt Research interaction group.
- Handoff and smoke gate the selected-layer summary contract.

Next:
- Continue applying the same label/copy contract pattern to Boundary emphasis controls.


## 2026-05-30 - Boundary emphasis summary contract

Done:
- Added `boundary_emphasis_summary_contract` to Boundary emphasis packets.
- Added `Copy boundary summary` to the Qt Research interaction group.
- Handoff and smoke gate the Boundary emphasis summary contract.

Next:
- Continue applying the same summary/copy pattern to pin and cursor geodesy research interactions.


## 2026-05-30 - Pin overlay summary contract

Done:
- Added `pin_summary_contract` to the Pin projection contract.
- Added Pin overlay summary copy actions to Qt Pin Annotation and Research interaction surfaces.
- Handoff and smoke gate the Pin summary contract.

Next:
- Continue applying the same summary/copy pattern to cursor geodesy research interactions.


## 2026-05-30 - Cursor geodesy summary contract

Done:
- Added `cursor_summary_contract` to the Cursor geodesy readout contract.
- Added `Copy cursor summary` to the Qt Research interaction group.
- Handoff and smoke gate the Cursor geodesy summary contract.

Next:
- Continue consolidating Qt research interaction summaries into clone/handoff reviewer flows.


## 2026-05-30 - Research interaction summary bundle

Done:
- Added `research_summary_contract` to `layer_research_workflow`.
- Added `Copy research summary` to the Qt Research interaction group.
- Handoff and smoke gate the bundled reviewer summary contract.

Next:
- Continue tightening clone/handoff reviewer flow around profile and launch packet review.


## 2026-05-30 - Clone reviewer summary contract

Done:
- Added `clone_reviewer_summary_contract` to `cross_machine_clone_readiness`.
- Added `Copy clone summary` to the Qt Replay/contracts group.
- Handoff and smoke gate the clone reviewer summary contract.

Next:
- Continue tightening profile/launch packet reviewer actions and one-click export flow.


## 2026-05-30 - Launch reviewer summary contract

Done:
- Added `launch_reviewer_summary_contract` to `profile_launch_readiness`.
- Added `Copy launch summary` to the Qt Replay/contracts group.
- Handoff and smoke gate the launch reviewer summary contract.

Next:
- Continue tightening one-click reviewer packet export for clone users.


## 2026-05-30 - Reviewer packet export

Done:
- Added `reviewer_packet_export` to launch packets and renderer capabilities.
- Added Qt `Export reviewer packet` to write clone/launch/research/visual summaries plus launch packet snapshot.
- Handoff and smoke gate the reviewer packet export contract.

Next:
- Return to backend-facing renderer LOD, hydrology and ocean material closed loops.
