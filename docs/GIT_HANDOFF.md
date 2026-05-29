# Git Handoff

Last updated: 2026-05-29

## Repository

- GitHub: `https://github.com/kagamihara-rururka/RRKAL_displaytools`
- Local repo: `C:\Users\lyn59\Documents\Codex\RRKAL_displaytools`
- Governance reference: `https://github.com/kagamihara-rururka/APIkeys_collection`

## Start of a development round

Use the project repo, not the old scratch path:

```powershell
Set-Location C:\Users\lyn59\Documents\Codex\RRKAL_displaytools
git pull --ff-only origin main
git status -sb
```

Read the current docs before choosing the next slice:

```text
docs/DOCS_INDEX.zh-TW.md
docs/PRODUCT_POSITIONING.zh-TW.md
docs/PROJECT_GTD.md
docs/AGENT_HANDOFF.zh-TW.md
docs/DEVELOPMENT_LOG.zh-TW.md
```

## End of a development round

Required loop:

```powershell
git status -sb
git add <explicit files>
git commit -m "<scoped message>"
git push origin main
```

Before the commit, update:

- `docs/DEVELOPMENT_LOG.zh-TW.md`
- `docs/PROJECT_GTD.md` when priorities, status, or backlog changed
- `docs/AGENT_HANDOFF.zh-TW.md` when working rules, risks, or boundaries changed
- `docs/PRODUCT_POSITIONING.zh-TW.md` when RRKAL/displaytools responsibility changes

## Do not commit

- `.venv/`, `__pycache__/`, `.pytest_cache/`
- Runtime logs, screenshots, recordings, generated images
- SQLite databases and local state
- `.npy`, `.npz`, tile/cache dumps, downloaded datasets
- API keys, OAuth tokens, `.env`, private config

## Validation rule

Do not run tests or validation unless the user explicitly asks.

If validation is requested for the current Python prototype, prefer the smallest relevant check first:

```powershell
py -3 -m py_compile taichi_global_bathymetry.py
```
