# Git Handoff

Last updated: 2026-05-30

## Repository

- GitHub: `https://github.com/Kagamihara-Ruruka/RRKAL_displaytools`
- Local repo: `L:\RRKAL_displaytools`
- Governance reference: `https://github.com/Kagamihara-Ruruka/APIkeys_collection`

## Start of a development round

Use the project repo and GitHub latest `main`:

```powershell
Set-Location L:\RRKAL_displaytools
git pull --ff-only origin main
git status -sb
git log -1 --oneline
```

Read the current docs before choosing the next slice:

```text
docs/WORKFLOW.zh-TW.md
docs/CODEX_CLOUD_HANDOFF.zh-TW.md
docs/DOCS_INDEX.zh-TW.md
docs/PRODUCT_POSITIONING.zh-TW.md
docs/PROJECT_GTD.md
docs/AGENT_HANDOFF.zh-TW.md
docs/DEVELOPMENT_LOG.zh-TW.md
```

## End of a development round

Required loop:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\lyn59\.codex\skills\agent-dev-safety\scripts\scan_mojibake.ps1 -Path L:\RRKAL_displaytools\docs
git diff --stat
git diff --check
git add <explicit files>
git diff --cached --stat
git diff --cached --check
git commit -m "<scoped message>"
git push origin main
```

Before the commit, update:

- `docs/DEVELOPMENT_LOG.zh-TW.md`
- `docs/PROJECT_GTD.md` when priorities, status, or backlog changed
- `docs/AGENT_HANDOFF.zh-TW.md` when working rules, risks, or boundaries changed
- `docs/WORKFLOW.zh-TW.md` when development process changed
- `docs/CODEX_CLOUD_HANDOFF.zh-TW.md` when Cloud/local handoff rules changed
- `docs/PRODUCT_POSITIONING.zh-TW.md` when RRKAL/displaytools responsibility changes

## Do not commit

- `.venv/`, `__pycache__/`, `.pytest_cache/`
- Runtime logs, screenshots, recordings, generated images
- SQLite databases and local state
- `.npy`, `.npz`, tile/cache dumps, downloaded datasets
- API keys, OAuth tokens, `.env`, private config
- Raw conversation transcripts; these belong only in a private backup repo after screening

## Smoke test rule

Before each commit, run at least a smoke test and record the result in `docs/DEVELOPMENT_LOG.zh-TW.md`.

For Python/UI/script-only changes, prefer:

```powershell
.\scripts\smoke.ps1
```

The smoke helper compiles Python entrypoints, checks renderer capabilities output, verifies handoff/launch contracts, and parses PowerShell helper scripts without executing setup/install work.