# Codex Cloud Handoff

最後更新：2026-05-30

## 啟動定位

這份文件是 Codex Cloud、本地 Codex 或其他 agent 接手 `RRKAL_displaytools` 時的第一入口。

## Repo 與工作區

| 項目 | 值 |
| --- | --- |
| GitHub repo | `https://github.com/Kagamihara-Ruruka/RRKAL_displaytools` |
| 本地主工作區 | `L:\RRKAL_displaytools` |
| 本地舊區 | `K:` 在本 session 視為唯讀參考，不作開發寫入。 |
| 同步真相 | GitHub `main` 最新 commit。 |
| 主要 UI 方向 | Qt / PyQt6 first，不混用 Tk 作主 UI。 |

## 接手順序

1. `git pull --ff-only origin main`
2. `git status --short --branch`
3. `git log -1 --oneline`
4. 讀 `docs/WORKFLOW.zh-TW.md`
5. 讀 `docs/AGENT_HANDOFF.zh-TW.md`
6. 讀 `docs/DEVELOPMENT_LOG.zh-TW.md` 最新段落
7. 必要時讀 `docs/RRKAL_HANDOFF_CONTRACT.zh-TW.md`
8. 開始一個小步、可回滾的閉環任務

## Cloud / local 權責分工

| 類型 | 處理位置 | 備註 |
| --- | --- | --- |
| code / docs / CI / smoke | Codex Cloud 或本地皆可 | 必須 commit/push。 |
| Qt 視窗與 Photoshop-like UI 體感 | 本地 | Cloud 不宣稱已完成視覺驗收。 |
| Taichi / Vulkan / GPU renderer | 本地 | 需要本機 GPU/視窗時，以本地結果為準。 |
| GitHub Actions failure | Cloud 優先 | 先讀 Actions log，再修 workflow/script。 |
| Raw transcript 備份 | 私有 repo `dialogue-save` | 不放公開 displaytools repo；只保存經過掃描/遮蔽的專案相關 transcript。 |

## 當前產品方向

- 這是科研視覺化工具，不是一般資料下載器。
- 主要服務研究者：圖層選取、領域/EEZ/領海強調、Pin 標記、滑鼠 lon/lat、可追溯 handoff、可複製 reviewer summary。
- `RRKAL_displaytools` 負責 renderer consumption contracts、Taichi globe visualization、Qt operator UI、style/material/LOD display controls。
- RRKAL / `APIkeys_collection` 負責 dataset discovery、download/import/install registry、manifest/cache governance。

## 已建立的閉環基礎

- Qt-first operator panel。
- Layer selection / quick actions / active-layer operation feedback。
- Ocean 3D material controls and safe preview guard。
- Profile templates / launch packet / renderer capability discovery。
- Reviewer packet / handoff inspection / clone readiness。
- Boundary emphasis control scaffold。
- Pin / cursor geodesy / occlusion vocabulary scaffold。
- Compose budget / parity runner / merge preflight gate。
- GitHub Actions smoke UTF-8 fix。

## 優先開發線

1. Qt UIUX 與圖層控制閉環。
2. Ocean 3D 控制板與效能 guard 收斂。
3. Compose parity artifacts 後再做 runtime compose pass reduction。
4. Boundary / EEZ / territorial water emphasis mask UI 與 backend identity closure。
5. Pin 與 cursor geodesy 的 renderer-backed runtime evidence。
6. 後續再做模組解耦與效能優化。

## 提交前硬性規則

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\lyn59\.codex\skills\agent-dev-safety\scripts\scan_mojibake.ps1 -Path L:\RRKAL_displaytools\docs
git diff --stat
git diff --check
git diff --cached --stat
git diff --cached --check
```

- `docs/DEVELOPMENT_LOG.zh-TW.md` 必須記錄 smoke 結果。
- 只 stage 本輪相關檔案。
- push 後確認 GitHub Actions smoke。

## Push 後回報要求

回報需包含：

- commit hash
- 本地 smoke / docs scan / diff check
- GitHub Actions smoke 狀態
- 目前已有功能
- 預計實現功能
- 整體成熟度估算
- 本階段成熟度估算

## 私有 transcript repo 命名

- 私有 repo 建議命名：dialogue-save。
- 每個對話 session 建議使用資料夾：RRKAL_displaytools/<dialogue-title-slug>__YYYY-MM-DD__<thread-short-id>/。
- metadata.json 保存原始對話框名稱、repo、branch、commit、匯出時間與 redaction 狀態。
- Cloud/local agent 預設只讀 handoff；raw transcript 只在 handoff 不足時讀取。

## 目前風險

- Cloud 看不到本地 `L:` 的未提交內容。
- Cloud 不能作為 Qt/Taichi/GPU 視覺驗收權威。
- Raw transcript 若公開可能洩漏本機路徑、帳號、token 或環境細節。
- `L:` 雲端碟適合工作副本，但高頻 GUI/renderer 測試可能需要本地暫存 clone。