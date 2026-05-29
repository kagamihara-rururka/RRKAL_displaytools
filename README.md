# RRKAL_displaytools

RRKAL display and visualization tools.

Positioning:
- `kagamihara-rururka/APIkeys_collection` / RRKAL owns dataset discovery, download, install registry, manifest, cache governance, and renderer bridge asset registration.
- `RRKAL_displaytools` owns visualization prototypes, renderer-facing contracts, Taichi globe output, style profiles, material controls, and LOD/display diagnostics.
- This repo should consume RRKAL-managed data or manifest contracts; it should not become a second crawler, downloader, API key, or dataset registry project.

Current focus:
- Taichi globe / bathymetry visualization prototype.
- Hydrology basic layers, LOD hook contracts, ocean material controls, style profile renderer entries, and decoupling-ready diagnostics.

Governance rule:
- Development work focuses on visualization.
- Documentation governance can reference the neighboring `kagamihara-rururka/APIkeys_collection` repository style.
- After each development round, update docs/logs and commit before starting the next round.

Primary file:
- `taichi_global_bathymetry.py`

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
