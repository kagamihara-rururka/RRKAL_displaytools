# RRKAL_displaytools GTD

Last updated: 2026-05-29

## Current focus

| Area | Status | Current progress | Next step |
| --- | --- | --- | --- |
| Product positioning | MVP | Repo is positioned as RRKAL's visualization/display layer, not a duplicate data launcher. `docs/PRODUCT_POSITIONING.zh-TW.md` records the launcher-vs-renderer boundary. | Keep future code changes aligned with RRKAL-owned data governance and displaytools-owned renderer contracts. |
| Qt operator UI | MVP | Added `rrkal_displaytools_qt_panel.py`, a PyQt6 control panel with Photoshop-inspired workspace naming: tool options, Looks/templates, layers, properties, central preview, and actions. It supports layer toggles, grouped layer quick actions, style profiles, topo source, data mode, ocean material values, renderer launch/stop/restart, startup profile/template loading, template listing, renderer capability/layer manifest display, launch packet export, smoke check, process status polling, local/portable command copy, profile folders, profile load validation, local JSON layer profiles, and repo-shared profile templates. Tk is not the primary UI direction. | Move from grouped forms toward dockable Photoshop-like panels after renderer state boundaries are stable. |
| Cross-machine onboarding / CI smoke | MVP | Added Windows helper scripts: `scripts/setup_windows.ps1`, `scripts/run_qt_panel.ps1`, `scripts/render_quick_smoke.ps1`, and `scripts/smoke.ps1`. | Add richer troubleshooting only after another machine reports concrete setup friction. |
| Profile templates / launch packets | MVP | Added named baseline scientific, maritime hydrology, parchment review, tactical ops, and fast synthetic templates under `profiles/`; `docs/PROFILE_SCHEMA.zh-TW.md` documents the schema; `profile_schema.py` owns validation rules; `scripts/validate_profiles.py` checks required fields in smoke. | Tune the preferred visual baseline after user review, then add project-specific templates as needed. |
| Taichi globe prototype | MVP | `taichi_global_bathymetry.py` is imported as the current monolithic source of truth for the globe/bathymetry prototype and now exposes `--print-renderer-capabilities`. A bounded `--demo-closed-loop` preset exists, but the Qt panel defaults back to scientific/non-tactical baseline control. | Use the Qt panel for near-term visual review, then continue small reversible renderer slices inside the repo copy. |
| Hydrology and LOD hook | In progress | Hydrology readiness, layer diagnostics, LOD invalidation and layer-count contracts are represented in the prototype. The Qt panel exposes lake/river/border/maritime layer switches. | Converge water/hydrology layers into stable renderer-facing contract names. |
| Ocean material and sea-state port | In progress | Ocean material controls and sea-condition diagnostics exist as contract-oriented scaffolding. The Qt panel exposes wave strength, roughness, foam, and ocean material toggle. | Add a clearer Taichi material control boundary after visual review. |
| Style renderer entries | In progress | Scientific/nautical/tactical/parchment style concepts are selectable in the Qt panel and `--style-profile`. | Create explicit renderer entry points for style profiles. |
| Module boundaries | Planned | Monolith contains diagnostics for extraction readiness and seam matrices. | Mark modules before extraction: data contracts, renderer core, style profiles, ocean material, diagnostics, cache/LOD. |

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
