# RRKAL_displaytools

RRKAL display and visualization tools.

Positioning:
- `kagamihara-rururka/APIkeys_collection` / RRKAL owns dataset discovery, download, install registry, manifest, cache governance, and renderer bridge asset registration.
- `RRKAL_displaytools` owns visualization prototypes, renderer-facing contracts, Taichi globe output, style profiles, material controls, and LOD/display diagnostics.
- This repo should consume RRKAL-managed data or manifest contracts; it should not become a second crawler, downloader, API key, or dataset registry project.

Current focus:
- Qt-first operator UI for controlling renderer launch flags and layers.
- Taichi globe / bathymetry visualization prototype.
- Live layer runtime bridge for visibility, opacity, blend, lock guard, selected-layer semantic target, and renderer pick state.
- Hydrology, boundary, traffic, Pin, ocean material, style profile renderer entries, and decoupling-ready diagnostics.
- Boundary highlight line mask plus closed-ring fill preview, with full territory identity kept explicit as future work.

Run on another Windows machine:
```powershell
git clone https://github.com/kagamihara-rururka/RRKAL_displaytools.git
cd RRKAL_displaytools
.\scripts\setup_windows.ps1
.\scripts\run_qt_panel.ps1
```

Detailed clone/smoke/Qt instructions:
- `docs/QUICKSTART_CLONE.zh-TW.md`

Manual equivalent:
```powershell
py -3 -m pip install -r requirements.txt
py -3 rrkal_displaytools_qt_panel.py
```

List shared templates without opening the panel:
```powershell
py -3 rrkal_displaytools_qt_panel.py --list-templates
```

Open the panel with a shared template already loaded:
```powershell
.\scripts\run_qt_panel.ps1 -Profile .\profiles\maritime_hydrology.json
.\scripts\run_qt_panel.ps1 -Template maritime_hydrology
.\scripts\run_qt_panel.ps1 -SmokeFirst
```

Optional quick headless render request:
```powershell
.\scripts\render_quick_smoke.ps1
```

Export a launch packet without opening Qt:
```powershell
py -3 scripts\export_launch_packet.py --template fast_synthetic
```

Print the profile schema contract as JSON:
```powershell
py -3 profile_schema.py
```

Renderer capabilities JSON:
```powershell
py -3 taichi_global_bathymetry.py --print-renderer-capabilities
```

GitHub Actions:
- `.github/workflows/smoke.yml` runs the Windows smoke workflow on push and pull request.

Pre-commit smoke:
```powershell
.\scripts\smoke.ps1
```

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
- `profile_schema.py`: shared profile schema validator and JSON schema-contract output.
- `scripts/setup_windows.ps1`: Windows dependency setup helper.
- `scripts/run_qt_panel.ps1`: Windows Qt panel launch helper.
- `scripts/render_quick_smoke.ps1`: Windows headless quick render helper.
- `scripts/smoke.ps1`: pre-commit smoke test helper.
- `scripts/validate_profiles.py`: profile template schema smoke validator.
- `scripts/export_launch_packet.py`: no-GUI launch packet exporter for templates/profiles.

Qt panel capabilities:
- Toggle renderer layers without memorizing CLI flags.
- Control layer lock, opacity, and blend mode through the renderer runtime bridge.
- Inspect renderer layer runtime JSON and renderer layer pick JSON from the Layers panel.
- Select Pin, traffic, boundary line, and hydrology line targets through selected-layer-aware renderer picking.
- Configure boundary highlight color, alpha, contrast, gamma, feather, breathing, and closed-ring fill preview.
- Load repo-shared profile templates from `profiles/`.
- Save/load local layer profiles as JSON under `state/ui_profiles/`.
- Apply current settings by restarting the renderer from the panel.
- Export a local launch packet JSON under `state/showcase/` for handoff/debugging.
- Copy either the local executable command or a portable `py -3 ...` command for another Windows machine.

Core docs:
- `docs/PRODUCT_POSITIONING.zh-TW.md`
- `docs/PROJECT_GTD.md`
- `docs/AGENT_HANDOFF.zh-TW.md`
- `docs/GIT_HANDOFF.md`
- `docs/WORKSPACE_LAYOUT.zh-TW.md`
- `docs/PROFILE_SCHEMA.zh-TW.md`
- `docs/SETUP_WINDOWS.zh-TW.md`
- `docs/RRKAL_HANDOFF_CONTRACT.zh-TW.md`
- `docs/CAPABILITY_SUMMARY.zh-TW.md`
- `docs/QUICKSTART_CLONE.zh-TW.md`
- `docs/MODULE_BOUNDARIES.zh-TW.md`
- `docs/DEVELOPMENT_LOG.zh-TW.md`

Notes:
- Runtime caches, screenshots, logs, databases, and virtual environments are intentionally excluded from Git.
- This initial import preserves the current monolithic prototype before later module extraction.
