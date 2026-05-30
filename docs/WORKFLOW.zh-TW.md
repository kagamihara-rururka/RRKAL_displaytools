# RRKAL_displaytools 開發工作流

## Agent Exchange read-check

`L:\AGENT_EXCHANGE` is a local/cloud cross-agent forum, not a product repository, release artifact, or source of truth. Do not copy inbox, archive, template, or raw exchange content into this repo.

At session start, checkpoint close, and before large refactors, folder moves, OpenSpec work, or cross-project integration, quickly check:

- `L:\AGENT_EXCHANGE\inbox\u_owner_all-projects.md`
- `L:\AGENT_EXCHANGE\inbox\*_RRKAL_displaytools.md`

Only validated decisions or engineering outcomes should be converted into this repo's GTD, handoff, docs, OpenSpec, code, smoke logs, commits, or CI notes.

最後更新：2026-05-30

## 核心原則

| 面向 | 規則 |
| --- | --- |
| 工程真相 | GitHub `Kagamihara-Ruruka/RRKAL_displaytools` 是唯一同步真相。 |
| 本地工作區 | `L:\RRKAL_displaytools` 保留為本地雲端碟工作副本。 |
| 雲端開發 | Codex Cloud 可作為長時間主力開發 session，但必須從 GitHub 最新 commit 與 handoff 文件啟動。 |
| 本地驗收 | Qt / Taichi / Vulkan / GPU 視覺驗收仍以本地 Windows 環境為準。 |
| 對話保存 | 公開 repo 只保存 handoff / decisions / development log；完整 raw transcript 只能進私有備份 repo。 |
| 文件地位 | Handoff、workflow、decision、development log 是一等公民，不是附屬筆記。 |
| RRKAL 邊界 | displaytools 不做 discovery/download/import/cache governance；這些仍由 RRKAL / APIkeys_collection 擁有。 |

## 標準開發循環

| 階段 | 動作 | 證據 |
| --- | --- | --- |
| 1. 開工 | 從 GitHub latest commit 開始，確認 `git status --short --branch` 與 `git log -1 --oneline`。 | 終端輸出。 |
| 2. 讀接力文件 | 先讀 `docs/CODEX_CLOUD_HANDOFF.zh-TW.md`、`docs/AGENT_HANDOFF.zh-TW.md`、`docs/WORKFLOW.zh-TW.md`。 | agent 已掌握規則。 |
| 3. 只在必要時讀 raw transcript | Handoff 不足時，才從私有備份 repo 讀最近 raw transcript。讀完只抽取決策，不把 raw transcript 帶進公開 repo。 | 決策整理進 handoff / decisions。 |
| 4. 小步開發 | 一次只做一個可回滾閉環，優先 Qt-first UI / 圖層控制 / renderer contract / handoff evidence。 | scoped diff。 |
| 5. 文件更新 | 必更 `docs/DEVELOPMENT_LOG.zh-TW.md`；流程、規則或接力資訊變更時更新 handoff / workflow / decisions。 | 文件 diff。 |
| 6. 本地驗證 | 提交前至少跑 `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1`。 | smoke PASS。 |
| 7. 文件編碼掃描 | 變更 zh-TW docs 時跑 mojibake scan。 | scan PASS。 |
| 8. commit / push | 只 stage 本輪相關檔案，commit 後 push main。 | commit hash。 |
| 9. CI 確認 | 等 GitHub Actions `smoke` 結果。 | CI PASS / failure log。 |
| 10. 回報 | 中文回報 commit、smoke/CI、已有功能、預計功能、整體成熟度與本階段成熟度。 | 對話回報。 |

## Codex Cloud 與本地分工

| 工作 | Codex Cloud | 本地 Codex / 本機 |
| --- | --- | --- |
| code/docs/CI 修正 | 主要執行 | 可執行 |
| smoke / no-GUI packet / handoff inspection | 可執行 | 可執行 |
| Qt 視窗互動檢查 | 不作為權威 | 權威 |
| Taichi/Vulkan/GPU 視覺驗收 | 不作為權威 | 權威 |
| 雲端碟 `L:` 操作 | 看不到或不依賴 | 權威工作副本 |
| raw transcript 備份 | 可產生摘要，不應進公開 repo | 可產生摘要，不應進公開 repo |

## GUI / renderer 測試暫存策略

需要測試 GUI、Taichi 或渲染時：

1. 保留 `L:\RRKAL_displaytools` 作為工作副本。
2. 若雲端碟延遲或檔案監控造成卡頓，clone 到本地暫存區，例如 `C:\RRKAL_tmp\RRKAL_displaytools_<timestamp>`。
3. 在本地暫存區跑 GUI / renderer / quick smoke。
4. 測試結果回寫到 repo docs 或 issue/handoff，不提交暫存 artifacts。
5. 測完刪除暫存 clone 與 runtime outputs。

暫存區只用於驗收，不是新的工程真相。

## 對話備份政策

| 類型 | 位置 | 規則 |
| --- | --- | --- |
| Handoff 摘要 | 公開 repo `docs/` | 可提交，內容要可接手、精簡、無 secret。 |
| Decisions | 公開 repo `docs/` | 記錄已定案流程、邊界、架構方向。 |
| Development log | 公開 repo `docs/` | 每輪提交前更新 smoke 結果與改動摘要。 |
| Raw transcript | 私有 repo `dialogue-save` | 只在需要完整追溯時按專案/日期/thread 保存；上傳前掃 token、私密帳號、本機敏感路徑。不要整包上傳所有本機對話快取。 |
| 本地對話快取 | 本機 Codex app | 可作短期快取；約兩週或大階段結束後清理。 |


建議私有 repo 結構：

```text
dialogue-save/
  RRKAL_displaytools/
    <dialogue-title-slug>__2026-05-30__<thread-short-id>/
      metadata.json
      thread-summary.md
      transcript-redacted.md
      artifacts-manifest.json
```


資料夾命名規則：

- 來源：使用 Codex 對話框名稱。
- 格式：`<dialogue-title-slug>__YYYY-MM-DD__<thread-short-id>`。
- Slug：建議 ASCII 小寫、空白改 `-`、移除不適合檔名的符號。
- 原始名稱：保存在 `metadata.json` 的 `original_dialogue_title`，避免 slug 後遺失中文語意。
- 同名處理：用日期與 thread short id 防止覆蓋。
命名建議使用 `dialogue-save` 或 `dialogue_save`。GitHub repo 名稱不要使用空白；若保留拼字 `dioalauge` 是刻意命名，建議仍使用 `dioalauge-save`。
建議後續 skill 化為 `conversation-handoff-backup`：

- 產生本輪摘要。
- 更新公開 handoff / decisions。
- 若使用者允許，將 raw transcript 放入私有 repo。`n- 若需要恢復完整對話，依 `docs/DIALOGUE_SAVE_RESTORE.zh-TW.md` 從私有 repo 分片還原。
- 對 raw transcript 做 secret/path/token 掃描。
- 提交前仍跑 smoke 與 docs encoding scan。

## 大階段 cache reset gate

平時不要每小步清 cache。每完成一個大環節或準備 release/pre-milestone 時，才做一次從 0 開始的流程驗證：

- 清理本地 runtime cache / state artifacts。
- 重新 clone 或用乾淨暫存工作區。
- 跑 setup / smoke / no-GUI handoff。
- 本地跑 Qt / quick render / 必要視覺驗收。
- 把結果寫進 development log 或 release note。

## Push 後回報模板

每次 push 後，中文回報至少包含：

- Commit: `<hash> <message>`
- 本地 smoke: PASS / FAIL
- GitHub Actions smoke: PASS / FAIL / in progress
- 已有功能
- 預計實現功能
- 整體成熟度估算：`0-100%`，附主要理由
- 本階段成熟度估算：`0-100%`，附主要缺口
- 下一步建議：最多三項