# Agent Handoff

## Project identity

- GitHub repo: `kagamihara-rururka/RRKAL_displaytools`
- Local repo: `C:\Users\lyn59\Documents\Codex\RRKAL_displaytools`
- Purpose: visualization/display tooling and renderer-facing contracts for RRKAL-related work.

## Working agreement

- Focus on visualization work.
- Use neighboring `kagamihara-rururka/APIkeys_collection` repository documentation patterns as reference for governance.
- Treat RRKAL / `APIkeys_collection` as owner of dataset discovery, download, import, install registry, manifest, cache governance, and renderer bridge asset registration.
- Treat this repo as owner of renderer consumption contracts, Taichi globe output, material/style controls, LOD/display diagnostics, and future visualization frontends.
- Use Qt/PyQt6 as the primary displaytools control UI direction; do not add Tk as the main UI path.
- Do not commit generated caches, logs, screenshots, databases, or virtual environments.
- After each development round, update docs/logs and commit before starting another round.

## Start-of-round checklist

- Work from `L:\RRKAL_displaytools`.
- Inspect Git state before edits.
- Read `docs/DOCS_INDEX.zh-TW.md`, `docs/PRODUCT_POSITIONING.zh-TW.md`, `docs/PROJECT_GTD.md`, and this handoff.
- Pick one small, reversible visualization slice.

## End-of-round checklist

- Run at least a smoke test before commit.
- Update `docs/DEVELOPMENT_LOG.zh-TW.md`.
- Update `docs/PROJECT_GTD.md` or this handoff if scope/status changed.
- Commit scoped code/docs before starting the next round.
- Push main when network/GitHub access is available.
- After every push, report in Chinese what capabilities the program currently has, then add a second section summarizing planned/next capabilities.

## Current source of truth

- `taichi_global_bathymetry.py` is still a monolithic prototype.
- `rrkal_displaytools_qt_panel.py` is the current Qt operator UI for layer/style/material launch control.
- Module extraction is planned but not physically started in this repo.
- Future development should happen in the repo copy, not the old `C:\Users\lyn59\scratch` copy, unless the user explicitly asks for a scratch sync.
- Current panel entry: `py -3 rrkal_displaytools_qt_panel.py`.
- Current showcase entry: `py -3 taichi_global_bathymetry.py --demo-closed-loop --style-profile tactical`.
- Optional packet output: add `--write-demo-packet state\showcase\closed_loop_demo.json`; generated `state/` artifacts remain local-only.

## Known constraints

- Current user rule: before each commit, run at least a smoke test and record the result in the development log.
- Runtime data/cache artifacts are local-only.
- Keep commits intentional and scoped.
- Do not add crawler/provider/download logic here; keep those concerns in RRKAL.

