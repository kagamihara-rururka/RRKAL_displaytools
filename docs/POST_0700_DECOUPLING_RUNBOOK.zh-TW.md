# 07:00 後解耦 Runbook

最後更新：2026-05-31

本文件只定義 `RRKAL_displaytools` 在 `2026-05-31T07:00:00+08:00` 後的第一個小型解耦切片。它不是 RRKAL 資料治理文件，也不包含 dataset discovery、download、import、cache lifecycle 或 asset repair。

## 目標

第一個 code-move 目標是 `render_plan_compose`。

預計新增/調整：

- `render_core/render_plan.py`
- `render_core/__init__.py`
- 最小必要 import seam
- smoke-gated handoff / GTD / development log

## 進入條件

在移動任何 renderer code 前，依序確認：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_pre7_closure_readiness.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\pre_decoupling_gate.ps1
```

若任一指令失敗，停止 code move，只修該 gate 或更新 handoff。

## 第一切片範圍

允許：

- 只抽離 render-plan compose 的純資料規劃/合併邏輯。
- 保留既有 renderer runtime 行為。
- 保留 `runtime_merge=false`，不得在同一切片啟用 collapsed compose-run。
- 增加薄 import seam，但不重寫 layer/hydrology/ocean pipeline。
- 用 smoke 證明 import 與 contract 不破。

不允許：

- 不搬動 Taichi kernel、GPU material shader、Ocean 3D runtime merge。
- 不改 RRKAL 資料 discovery/download/import/cache governance。
- 不新增 Tk path。
- 不在同一切片做效能優化或多 pass 合併。
- 不把 `L:\AGENT_EXCHANGE` 內容提交到 GitHub。

## 建議執行順序

1. 讀交換區 displaytools / RRKAL_project inbox，回覆相關 `Status: new`。
2. 確認 git working tree clean。
3. 跑 `scripts\smoke.ps1`。
4. 跑 `scripts\check_pre7_closure_readiness.ps1`。
5. 跑 `scripts\pre_decoupling_gate.ps1`。
6. 建立 `render_core` 模組。
7. 只搬第一批 render-plan compose helper。
8. 更新 smoke、GTD、development log。
9. 跑 smoke。
10. commit / push，並回報已有功能與預計功能。

## 停止條件

- working tree 不乾淨且有非本切片變更。
- smoke 或 formal gate 失敗。
- 出現需要 RRKAL_project 補資料/manifest/tile/cache contract 的需求。
- 需要改 `rrkal-visual-compressor` 輸出格式。
- 抽離時碰到 Taichi runtime side effect 或 GUI startup side effect。

跨專案需求只寫入 `L:\AGENT_EXCHANGE`，不要直接改對方 repo。
