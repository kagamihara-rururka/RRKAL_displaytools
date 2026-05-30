# Documentation Index

## Core docs

- `PRODUCT_POSITIONING.zh-TW.md`: RRKAL / displaytools responsibility boundary and renderer-layer positioning.
- `PROJECT_GTD.md`: active work lines, current status, backlog, and next development slices.
- `DEVELOPMENT_LOG.zh-TW.md`: chronological development log and commit handoff notes.
- `WORKFLOW.zh-TW.md`: standard local/cloud development loop, testing split, conversation backup policy, and push report template.
- `CODEX_CLOUD_HANDOFF.zh-TW.md`: first-read entrypoint for Codex Cloud, local Codex, and other agents taking over from GitHub.
- `AGENT_HANDOFF.zh-TW.md`: current agent-facing working rules, scope, and known risks.
- `GIT_HANDOFF.md`: git start/end loop, commit/push rules, and do-not-commit list.
- `WORKSPACE_LAYOUT.zh-TW.md`: canonical workspace, root files, docs map, and local-only artifact policy.
- `PROFILE_SCHEMA.zh-TW.md`: Qt panel profile template schema and RRKAL/displaytools handoff rules.
- `SETUP_WINDOWS.zh-TW.md`: clone/setup/smoke/Qt panel steps for another Windows computer.
- `RRKAL_HANDOFF_CONTRACT.zh-TW.md`: no-GUI RRKAL/displaytools integration contract.
- `CAPABILITY_SUMMARY.zh-TW.md`: current program capability summary for push reports and GitHub review.

## Positioning

`RRKAL_displaytools` is the visualization/display layer for RRKAL-related renderer work. `APIkeys_collection` / RRKAL remains responsible for dataset discovery, download, import, install registry, manifest, cache governance, and renderer bridge asset ownership.

## Project rule

Every development round must end with:
- code/doc updates staged intentionally,
- development log updated,
- commit created before the next round begins.

## Reference

- Documentation governance reference: Kagamihara-Ruruka/APIkeys_collection.
- Product boundary reference: `APIkeys_collection/docs/PRODUCT_POSITIONING.zh-TW.md`, especially the renderer bridge and tile/cache asset sections.
