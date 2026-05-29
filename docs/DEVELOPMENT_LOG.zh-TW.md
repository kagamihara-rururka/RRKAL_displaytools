# Development Log

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
