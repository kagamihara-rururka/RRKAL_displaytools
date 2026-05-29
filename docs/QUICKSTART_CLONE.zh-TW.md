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

## 5. Renderer bridge 檔案

常用狀態檔：

- `state/renderer_layer_runtime_state.json`
- `state/renderer_layer_runtime_ack.json`
- `state/renderer_layer_pick_state.json`
- `state/renderer_pin_pick_state.json`
- `state/renderer_boundary_highlight_ack.json`

這些檔案是本機 runtime 狀態，不需要提交。

## 6. 權責邊界

Displaytools 只做視覺化、Qt UI、renderer runtime bridge。

不要在本 repo 加入：

- dataset discovery。
- downloader/importer。
- API key governance。
- cache governance。
- RRKAL asset registry。

這些由 RRKAL / `APIkeys_collection` 負責。
