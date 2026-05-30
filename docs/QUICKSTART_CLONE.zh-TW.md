# 跨機器 Clone 快速啟動

最後更新：2026-05-29

Repo:

```text
https://github.com/Kagamihara-Ruruka/RRKAL_displaytools
```

## 1. Clone

```powershell
git clone https://github.com/Kagamihara-Ruruka/RRKAL_displaytools.git
cd RRKAL_displaytools
```

## 2. 建立 Python 環境

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 3. 先檢查 handoff contract

這一步不會打開 Qt，也不會下載或治理資料；它只輸出目前 renderer/UI handoff 的 JSON 摘要，方便先確認 clone 下來的 repo 是否具備必要 contract。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_handoff.ps1
```

應該能看到：

```text
"schema": "rrkal_displaytools.handoff_inspection.v1"
"session_journal": "rrkal_displaytools.session_journal.v1"
"layer_capability_matrix": "rrkal_displaytools.layer_capability_matrix.v1"
```

## 4. 跑提交級 smoke

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1
```

預期摘要：

```text
RRKAL_displaytools smoke
Profile validation passed: 5 templates
Smoke passed.
```

可選的 renderer output smoke：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\render_quick_smoke.ps1
```

這會產生 `state/showcase/quick_smoke.png`、`state/showcase/quick_smoke.png.metadata.json` 與 `state/showcase/quick_smoke_preview_frame.png`，用來確認 renderer output 與 live preview frame 寫檔。這些都是本機 runtime artifacts，不提交 Git。

## 5. 啟動 Qt 控制面板

建議使用 repo 內 launcher。它會優先使用 `.venv\Scripts\python.exe`，找不到 `.venv` 時 fallback 到 `py -3`。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_qt_panel.ps1
```

啟動前先跑 smoke：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_qt_panel.ps1 -SmokeFirst
```

Run handoff inspection before opening Qt on a newly cloned machine:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_qt_panel.ps1 -HandoffFirst
```

載入 repo 內建 template：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_qt_panel.ps1 -Template maritime_hydrology
```

備用入口：

```powershell
python rrkal_displaytools_qt_panel.py
```

Qt 面板目前可做：

- 載入 profile/template。
- 控制 layer visibility、opacity、blend、lock。
- 啟動/停止 renderer。
- 查看 layer runtime JSON。
- 查看 renderer layer pick JSON。
- 查看 Pin、boundary、layer bridge 狀態。
- 在 Canvas Preview 中切換 Qt state、renderer thumbnail 與 Live preview。

跨機器 clone 後建議先按 Actions 裡的 `Inspect:` 檢查入口：

- Replay/contracts：先開 `Inspect: Clone ready`、`Inspect: Profile replay`、`Inspect: Timeline`、`Inspect: Module seams`，確認 portable command、profile replay coverage、Timeline runtime/keyframes 與模組邊界。
- Renderer ports：再開 `Inspect: Hydro LOD`、`Inspect: Ocean port`、`Inspect: Style routes`、`Inspect: Layer matrix`、`Inspect: Layer runtime`，確認 hydrology/LOD、sea-state scalar port、parchment/tactical renderer routes、layer capability matrix 與 layer runtime ack。
- Research interaction：最後開 `Inspect: Layer pick`、`Inspect: Pin pick`、`Inspect: Cursor geo`、`Inspect: Boundary JSON`，確認 selected-layer pick、Pin pick、滑鼠經緯度、Boundary/EEZ 強調與 identity warning。

## 6. Canvas Preview / Live preview

Qt 面板中央有 Canvas Preview。

- `Canvas state`：顯示 Qt 狀態、active layer、visible layers、Pin 摘要與估算經緯度。
- `Renderer thumbnail`：顯示最近的 `state/showcase/*.png`。
- `Live preview`：Qt 啟動 renderer 時會帶入 `--preview-frame-file state/renderer_preview_frame.png`，renderer 會定期輸出目前 frame PNG，Qt 會輪詢刷新。

建議流程：

1. 啟動 Qt 面板。
2. 切到 `Live preview`。
3. 按 `啟動 renderer` 或 `套用並重啟`。
4. 確認 `state/renderer_preview_frame.png` 有更新。

目前 live preview 是 file-based stream；未來才升級為低延遲 IPC/GPU texture stream。

## 7. Renderer bridge runtime artifacts

常見本機 runtime 檔：

- `state/renderer_layer_runtime_state.json`
- `state/renderer_layer_runtime_ack.json`
- `state/renderer_layer_pick_state.json`
- `state/renderer_pin_pick_state.json`
- `state/renderer_boundary_highlight_ack.json`
- `state/renderer_preview_frame.png`

這些檔案是本機橋接狀態，不提交 Git。

## 8. 邊界

Displaytools 只負責 Qt UI、renderer runtime bridge、visualization launch/profile/provenance。

Displaytools 不負責：

- dataset discovery
- downloader/importer
- API key governance
- cache governance
- RRKAL asset registry

以上仍由 RRKAL / `APIkeys_collection` 負責。
