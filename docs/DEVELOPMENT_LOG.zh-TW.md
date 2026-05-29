# Development Log

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
