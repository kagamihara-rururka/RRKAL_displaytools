# Development Log

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







