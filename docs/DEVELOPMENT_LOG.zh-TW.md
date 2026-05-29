# Development Log

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
