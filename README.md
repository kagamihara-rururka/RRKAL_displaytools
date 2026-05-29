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
py -3 -m pip install -r requirements.txt
py -3 rrkal_displaytools_qt_panel.py
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

Core docs:
- `docs/PRODUCT_POSITIONING.zh-TW.md`
- `docs/PROJECT_GTD.md`
- `docs/AGENT_HANDOFF.zh-TW.md`
- `docs/GIT_HANDOFF.md`
- `docs/WORKSPACE_LAYOUT.zh-TW.md`
- `docs/DEVELOPMENT_LOG.zh-TW.md`

Notes:
- Runtime caches, screenshots, logs, databases, and virtual environments are intentionally excluded from Git.
- This initial import preserves the current monolithic prototype before later module extraction.
