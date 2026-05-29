# RRKAL_displaytools GTD

Last updated: 2026-05-29

## Current focus

| Area | Status | Current progress | Next step |
| --- | --- | --- | --- |
| Product positioning | MVP | Repo is positioned as RRKAL's visualization/display layer, not a duplicate data launcher. `docs/PRODUCT_POSITIONING.zh-TW.md` records the launcher-vs-renderer boundary. | Keep future code changes aligned with RRKAL-owned data governance and displaytools-owned renderer contracts. |
| Qt operator UI | MVP | Added `rrkal_displaytools_qt_panel.py`, a PyQt6 control panel for layer toggles, grouped layer quick actions, style profiles, topo source, data mode, ocean material values, renderer launch/stop/restart, startup profile loading, launch packet export, smoke check, process status polling, local/portable command copy, grouped operator actions, profile folders, local JSON layer profiles, and repo-shared profile templates. Tk is not the primary UI direction. | Wire deeper in-app layer control after the renderer loop is easier to separate. |
| Cross-machine onboarding | MVP | Added Windows helper scripts: `scripts/setup_windows.ps1`, `scripts/run_qt_panel.ps1`, and `scripts/render_quick_smoke.ps1`. | Add richer troubleshooting only after another machine reports concrete setup friction. |
| Profile templates | MVP | Added baseline scientific, maritime hydrology, parchment review, tactical ops, and fast synthetic templates under `profiles/`. | Tune the preferred visual baseline after user review, then add project-specific templates as needed. |
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
- Every development round ends with docs/log update and commit before the next round starts.
- Current user rule: before each commit, run at least a smoke test and record the result in `docs/DEVELOPMENT_LOG.zh-TW.md`.

## Backlog

- Move future development fully into `C:\Users\lyn59\Documents\Codex\RRKAL_displaytools`; avoid editing the old scratch source unless explicitly requested.
- Define the minimal renderer input contract expected from RRKAL tile/cache manifests.
- Create in-renderer layer toggles after the Qt launch panel proves the control model.
- Tune profile templates after the preferred visual baseline is confirmed.
- Separate diagnostics from render-loop code after contracts stabilize.
- Decide which local cache artifacts should later be registered by RRKAL as renderer bridge assets.

## Done

- 2026-05-29: Created and pushed the private GitHub repo `kagamihara-rururka/RRKAL_displaytools`.
- 2026-05-29: Imported the current Taichi globe prototype and minimal governance docs.
- 2026-05-29: Added RRKAL-aligned documentation governance skeleton and product positioning.
- 2026-05-29: Added `--demo-closed-loop` as the first bounded showcase path for the existing renderer stack.
- 2026-05-29: Added a PyQt6 operator panel for layer/style/material launch control.
- 2026-05-29: Added Qt panel save/load JSON profiles and apply-by-restart flow.
- 2026-05-29: Added repo-shared profile templates and Qt template loading.
- 2026-05-29: Added Qt panel command copy and profile directory shortcuts.
- 2026-05-29: Added Qt panel renderer process status polling.
- 2026-05-29: Added Windows setup and Qt panel launch scripts for another computer.
- 2026-05-29: Added Qt panel grouped layer quick actions.
- 2026-05-29: Added startup profile loading for the Qt panel and run script.
- 2026-05-29: Added Qt panel smoke-check action.
- 2026-05-29: Added Qt launch packet export for handoff/debugging.
- 2026-05-29: Added Windows quick headless render helper script.
- 2026-05-29: Added portable command copy and launch-packet portable command fields.
- 2026-05-29: Reworked Qt operator actions into a grid layout.
- 2026-05-29: Added renderer capabilities JSON CLI output.








