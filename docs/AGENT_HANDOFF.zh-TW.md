# Agent Handoff

## Project identity

- GitHub repo: `Kagamihara-Ruruka/RRKAL_displaytools`
- GitHub URL: `https://github.com/Kagamihara-Ruruka/RRKAL_displaytools`
- Local repo: `L:\RRKAL_displaytools`
- Purpose: visualization/display tooling and renderer-facing contracts for RRKAL-related work.

## Required first reads

- `docs/WORKFLOW.zh-TW.md`
- `docs/CODEX_CLOUD_HANDOFF.zh-TW.md`
- `docs/DEVELOPMENT_LOG.zh-TW.md`
- `docs/DISPLAY_SHELL_RENDER_MATRIX.zh-TW.md` when display shell, canvas, render matrix, or runtime boundary work is involved.
- `docs/RRKAL_HANDOFF_CONTRACT.zh-TW.md` when RRKAL/displaytools responsibility boundaries are involved.

## Working agreement

- Focus on visualization work.
- Use neighboring `Kagamihara-Ruruka/APIkeys_collection` repository documentation patterns as reference for governance when available.
- Treat RRKAL / `APIkeys_collection` as owner of dataset discovery, download, import, install registry, manifest, cache governance, and renderer bridge asset registration.
- Treat this repo as owner of renderer consumption contracts, Taichi globe output, material/style controls, LOD/display diagnostics, and future visualization frontends.
- Use Qt/PyQt6 as the primary displaytools control UI direction; do not add Tk as the main UI path.
- Do not commit generated caches, logs, screenshots, databases, or virtual environments.
- After each development round, update docs/logs and commit before starting another round.
- Public repo stores handoff/decisions/logs only; raw conversation transcripts belong only in a private backup repo after secret/path screening.

## Start-of-round checklist

- Work from `L:\RRKAL_displaytools` unless explicitly using a local temporary clone for GUI/renderer validation.
- Inspect Git state before edits.
- Read `docs/WORKFLOW.zh-TW.md`, `docs/CODEX_CLOUD_HANDOFF.zh-TW.md`, `docs/DOCS_INDEX.zh-TW.md`, `docs/PROJECT_GTD.md`, and this handoff.
- Pick one small, reversible visualization slice.

## End-of-round checklist

- Run at least `scripts\smoke.ps1` before commit.
- Update `docs/DEVELOPMENT_LOG.zh-TW.md`.
- Update `docs/PROJECT_GTD.md`, `docs/WORKFLOW.zh-TW.md`, `docs/CODEX_CLOUD_HANDOFF.zh-TW.md`, or this handoff if scope/status/process changed.
- Run docs mojibake scan when zh-TW docs changed.
- Commit scoped code/docs before starting the next round.
- Push main when network/GitHub access is available.
- Confirm GitHub Actions smoke when practical.
- After every push, report in Chinese what capabilities the program currently has, then add planned/next capabilities, overall maturity estimate, and current-stage maturity estimate.
- For cross-machine reviewer handoff, call out `compose_performance_summary` when renderer performance, parity runner or compose budget work changed.
- When performance work changes, run `scripts\performance_smoke.ps1` directly or via `scripts\smoke.ps1`; inspect `state\performance\performance_smoke.json`, `state\performance\stage_timing.jsonl`, and `state\performance\render_telemetry.json`. These files are generated local state and must not be committed.

## Current source of truth

- GitHub `main` is the sync truth.
- `L:\RRKAL_displaytools` is the local cloud-drive working copy.
- `taichi_global_bathymetry.py` is still a monolithic prototype.
- `rrkal_displaytools_qt_panel.py` is the current Qt operator UI for layer/style/material launch control.
- `display_core/` now owns renderer-package-free DisplayShell / Canvas / Layer / Render Matrix contracts.
- `display_runtime/` now owns contract-only runtime landing zones, runtime request/result protocol, sample runtime requests, and no-render handoff contracts.
- Current display shell review command: `py -3 scripts\export_display_shell_render_matrix.py`
- Current display shell check command: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_display_shell_render_matrix.ps1`
- Current display runtime contracts command: `py -3 scripts\export_display_runtime_contracts.py`
- Current display runtime check command: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_display_runtime_contracts.ps1`
- Current display runtime handoff command: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_display_runtime_handoff.ps1`
- Module extraction is planned but not physically completed in this repo.
- Do not start physical module extraction before `2026-05-31T07:00:00+08:00`; after that, run `scripts\pre_decoupling_gate.ps1` and start with `render_plan_compose`.
- Current panel entry: `py -3 rrkal_displaytools_qt_panel.py`.
- Current showcase entry: `py -3 taichi_global_bathymetry.py --demo-closed-loop --style-profile tactical`.
- Optional packet output: add `--write-demo-packet state\showcase\closed_loop_demo.json`; generated `state/` artifacts remain local-only.

## Known constraints

- Before each commit, run at least a smoke test and record the result in the development log.
- Runtime data/cache artifacts are local-only.
- Keep commits intentional and scoped.
- Do not add crawler/provider/download logic here; keep those concerns in RRKAL.
- Do not import Qt, Taichi, Matplotlib, Plotly, VisPy, PyVista or VTK into `display_core/` or current `display_runtime/` skeletons before explicit adapter parity work.
- Do not move RRKAL crawler/download/import/cache performance smoke into this repo; displaytools owns renderer/config/UI telemetry only.
- Codex Cloud can work from GitHub and handoff docs, but local Qt/Taichi/GPU visual validation remains a local responsibility.
