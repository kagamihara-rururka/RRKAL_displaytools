# 跨機器 Clone 快速啟動

日期：2026-05-29

Repo：

`https://github.com/kagamihara-rururka/RRKAL_displaytools`

## 1. Clone

```powershell
git clone https://github.com/kagamihara-rururka/RRKAL_displaytools.git
cd RRKAL_displaytools
```

## 2. 建立 Python 環境

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 3. 先跑 smoke

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1
```

成功時應看到：

```text
RRKAL_displaytools smoke
Profile validation passed: 5 templates
Smoke passed.
```

可選的 renderer output smoke：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\render_quick_smoke.ps1
```

這會產生 `state/showcase/quick_smoke.png` 與 `state/showcase/quick_smoke.png.metadata.json`。

## 4. 開 Qt 控制面板

建議用 repo 內 launcher；它會優先使用 `.venv\Scripts\python.exe`，找不到 `.venv` 時才 fallback 到 `py -3`：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_qt_panel.ps1
```

需要先跑 smoke 再開 UI：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_qt_panel.ps1 -SmokeFirst
```

也可以直接載入 repo profile template：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_qt_panel.ps1 -Template maritime_hydrology
```

手動等價命令：

```powershell
python rrkal_displaytools_qt_panel.py
```

Qt 面板負責：

- 選 profile/template。
- 控制 layer visibility/opacity/blend/lock。
- 啟動 renderer。
- 查看 layer runtime JSON。
- 查看 renderer layer pick JSON。
- 查看 pin/boundary/layer bridge 狀態。
- 在 Canvas Preview 切換 Qt state、renderer thumbnail 或 Live preview。

## 5. Canvas Preview / Live preview

Qt 面板中央的 Canvas Preview 有三種用途：

- `Canvas state`：只顯示 Qt 操作狀態、active layer、visible layers、Pin 與游標經緯度估算。
- `Renderer thumbnail`：顯示最近的 `state/showcase/*.png`，適合 headless smoke 或輸出圖檢查。
- `Live preview`：啟動 renderer 時，Qt 會帶入 `--preview-frame-file state/renderer_preview_frame.png`；renderer 每隔一段時間把目前 frame 寫到該 PNG，Qt 會自動輪詢刷新。

使用方式：

1. 開 Qt 面板。
2. 點 `Live preview`。
3. 點 `啟動地球儀` 或 `套用並重啟`。
4. 等待 `state/renderer_preview_frame.png` 出現；這是本機 runtime 檔案，不需要提交 Git。

目前 live preview 是 file-based stream，重點是跨機器可用與容易除錯；低延遲 IPC/GPU texture stream 是後續升級項目。

## 6. Renderer bridge 檔案

常用狀態檔：

- `state/renderer_layer_runtime_state.json`
- `state/renderer_layer_runtime_ack.json`
- `state/renderer_layer_pick_state.json`
- `state/renderer_pin_pick_state.json`
- `state/renderer_boundary_highlight_ack.json`
- `state/renderer_preview_frame.png`

這些檔案是本機 runtime 狀態，不需要提交。

## 7. 權責邊界

Displaytools 只做視覺化、Qt UI、renderer runtime bridge。

不要在本 repo 加入：

- dataset discovery。
- downloader/importer。
- API key governance。
- cache governance。
- RRKAL asset registry。

這些由 RRKAL / `APIkeys_collection` 負責。
