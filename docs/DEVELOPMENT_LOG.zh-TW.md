# Development Log

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
