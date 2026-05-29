# RRKAL_displaytools

RRKAL display and visualization tools.

Positioning:
- `kagamihara-rururka/APIkeys_collection` / RRKAL owns dataset discovery, download, install registry, manifest, cache governance, and renderer bridge asset registration.
- `RRKAL_displaytools` owns visualization prototypes, renderer-facing contracts, Taichi globe output, style profiles, material controls, and LOD/display diagnostics.
- This repo should consume RRKAL-managed data or manifest contracts; it should not become a second crawler, downloader, API key, or dataset registry project.

Current focus:
- Qt-first operator UI for controlling renderer launch flags and layers.
- Taichi globe / bathymetry visualization prototype.
- Hydrology basic layers, LOD hook contracts, ocean material controls, style profile renderer entries, and decoupling-ready diagnostics.

Run on another Windows machine:
```powershell
git clone https://github.com/kagamihara-rururka/RRKAL_displaytools.git
cd RRKAL_displaytools
.\scripts\setup_windows.ps1
.\scripts\run_qt_panel.ps1
```

Manual equivalent:
```powershell
py -3 -m pip install -r requirements.txt
py -3 rrkal_displaytools_qt_panel.py
```

List shared templates without opening the panel:
`powershell
py -3 rrkal_displaytools_qt_panel.py --list-templates
` 

Open the panel with a shared template already loaded:
```powershell
.\scripts\run_qt_panel.ps1 -Profile .\profiles\maritime_hydrology.json
.\scripts\run_qt_panel.ps1 -Template maritime_hydrology
```

Optional quick headless render request:
```powershell
.\scripts\render_quick_smoke.ps1
```

Export a launch packet without opening Qt:
`powershell
py -3 scripts\export_launch_packet.py --template fast_synthetic
` 

Pre-commit smoke:
```powershell
.\scripts\smoke.ps1
```

Renderer capabilities JSON:
`powershell
py -3 taichi_global_bathymetry.py --print-renderer-capabilities
` 

Direct renderer launch:
```powershell
py -3 taichi_global_bathymetry.py --style-profile scientific --topo-source gebco --topo-step 48 --data-mode static
```

Governance rule:
- Development work focuses on visualization.
- Qt/PyQt6 is the primary UI direction for displaytools control surfaces; avoid adding Tk as a primary UI path.
- Documentation governance can reference the neighboring `kagamihara-rururka/APIkeys_collection` repository style.
- After each development round, update docs/logs and commit before starting the next round.

Primary files:
- `rrkal_displaytools_qt_panel.py`: Qt operator panel for layer/style/material launch control.
- `taichi_global_bathymetry.py`: current monolithic renderer prototype.
- `profiles/*.json`: repo-shared Qt panel profile templates.
- `scripts/setup_windows.ps1`: Windows dependency setup helper.
- `scripts/run_qt_panel.ps1`: Windows Qt panel launch helper.
- `scripts/render_quick_smoke.ps1`: Windows headless quick render helper.
- scripts/smoke.ps1: pre-commit smoke test helper.
- scripts/validate_profiles.py: profile template schema smoke validator.

Qt panel capabilities:
- Toggle renderer layers without memorizing CLI flags.
- Load repo-shared profile templates from `profiles/`.
- Save/load local layer profiles as JSON under `state/ui_profiles/`.
- Apply current settings by restarting the renderer from the panel.
- Export a local launch packet JSON under state/showcase/ for handoff/debugging.

Core docs:
- `docs/PRODUCT_POSITIONING.zh-TW.md`
- `docs/PROJECT_GTD.md`
- `docs/AGENT_HANDOFF.zh-TW.md`
- `docs/GIT_HANDOFF.md`
- `docs/WORKSPACE_LAYOUT.zh-TW.md`
- `docs/PROFILE_SCHEMA.zh-TW.md`
- `docs/DEVELOPMENT_LOG.zh-TW.md`

Notes:
- Runtime caches, screenshots, logs, databases, and virtual environments are intentionally excluded from Git.
- This initial import preserves the current monolithic prototype before later module extraction.






