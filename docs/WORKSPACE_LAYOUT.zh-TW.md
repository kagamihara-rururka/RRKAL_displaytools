# Workspace Layout

最後更新：2026-05-29

## Canonical repo

`C:\Users\lyn59\Documents\Codex\RRKAL_displaytools`

這是後續 displaytools 開發與 commit 的正式位置。

## Root files

- `rrkal_displaytools_qt_panel.py`: Qt-first operator panel for layer/style/material launch control。
- `taichi_global_bathymetry.py`: 目前的 Taichi globe / bathymetry monolithic prototype。
- `requirements.txt`: prototype runtime dependency list。
- `README.md`: repo 簡介、定位與核心文件入口。
- `.gitignore`: 排除 runtime cache、logs、db、screenshots、virtual env、private config。

## Docs

- `docs/PRODUCT_POSITIONING.zh-TW.md`: RRKAL 與 displaytools 的產品/責任邊界。
- `docs/PROJECT_GTD.md`: 目前工作線、狀態、下一步與 backlog。
- `docs/AGENT_HANDOFF.zh-TW.md`: Agent 接手規則、限制與風險。
- `docs/GIT_HANDOFF.md`: Git start/end loop 與 commit/push 規則。
- `docs/WORKSPACE_LAYOUT.zh-TW.md`: 本文件。
- `docs/DEVELOPMENT_LOG.zh-TW.md`: 每輪開發紀錄。
- `docs/DOCS_INDEX.zh-TW.md`: 文件索引。

## Old scratch source

舊來源曾在：

`C:\Users\lyn59\scratch\taichi_global_bathymetry.py`

後續預設不應繼續在 scratch 開發。若使用者要求從 scratch 搬移新成果，必須明確複製、更新開發日誌、commit，避免 repo copy 與 scratch copy 漂移。

## Local-only artifacts

以下類型只留本機，不進 Git：

- Virtual environments and package caches。
- Taichi/runtime logs。
- Generated screenshots, recordings, PNG output。
- SQLite databases and local state files。
- Downloaded datasets。
- `.npy`, `.npz`, tile/cache artifacts。
- Secrets, `.env`, API keys, OAuth tokens。
