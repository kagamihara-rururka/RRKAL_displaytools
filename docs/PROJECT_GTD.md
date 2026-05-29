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
