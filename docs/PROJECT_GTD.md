# RRKAL_displaytools GTD

Last updated: 2026-05-29

## Current focus

| Area | Status | Current progress | Next step |
| --- | --- | --- | --- |
| Product positioning | MVP | Repo is positioned as RRKAL's visualization/display layer, not a duplicate data launcher. `docs/PRODUCT_POSITIONING.zh-TW.md` records the launcher-vs-renderer boundary. | Keep future code changes aligned with RRKAL-owned data governance and displaytools-owned renderer contracts. |
| Taichi globe prototype | MVP | `taichi_global_bathymetry.py` is imported as the current monolithic source of truth for the globe/bathymetry prototype. | Continue small, reversible slices inside the repo copy instead of the old scratch path. |
| Hydrology and LOD hook | In progress | Hydrology readiness, layer diagnostics, LOD invalidation and layer-count contracts are represented in the prototype. | Converge water/hydrology layers into stable renderer-facing contract names. |
| Ocean material and sea-state port | Planned | Ocean material controls and sea-condition diagnostics exist as contract-oriented scaffolding. | Add Taichi material control boundary without coupling it to RRKAL download logic. |
| Style renderer entries | Planned | Scientific/tactical/parchment style concepts are represented by diagnostics. | Create explicit renderer entry points for style profiles. |
| Module boundaries | Planned | Monolith contains diagnostics for extraction readiness and seam matrices. | Mark modules before extraction: data contracts, renderer core, style profiles, ocean material, diagnostics, cache/LOD. |

## Working rules

- Visualization-first: renderer, material, style, LOD, diagnostics, display contracts.
- RRKAL-first data governance: dataset discovery, download, import, install registry, manifest, cache lifecycle, and asset repair belong to `APIkeys_collection`.
- Do not commit generated caches, screenshots, logs, databases, virtual environments, secrets, or heavy local data.
- Every development round ends with docs/log update and commit before the next round starts.
- Do not run tests or validation unless the user explicitly asks.

## Backlog

- Move future development fully into `C:\Users\lyn59\Documents\Codex\RRKAL_displaytools`; avoid editing the old scratch source unless explicitly requested.
- Define the minimal renderer input contract expected from RRKAL tile/cache manifests.
- Create a small style profile registry for `scientific`, `parchment`, and `tactical`.
- Separate diagnostics from render-loop code after contracts stabilize.
- Decide which local cache artifacts should later be registered by RRKAL as renderer bridge assets.

## Done

- 2026-05-29: Created and pushed the private GitHub repo `kagamihara-rururka/RRKAL_displaytools`.
- 2026-05-29: Imported the current Taichi globe prototype and minimal governance docs.
- 2026-05-29: Added RRKAL-aligned documentation governance skeleton and product positioning.
