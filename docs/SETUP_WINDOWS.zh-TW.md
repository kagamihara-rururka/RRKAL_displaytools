# Windows Setup

最後更新：2026-05-29

## 目標

這份文件給另一台 Windows 電腦使用：clone `RRKAL_displaytools`、安裝依賴、跑 smoke、開 Qt panel、載入 templates。

## Clone

```powershell
git clone https://github.com/kagamihara-rururka/RRKAL_displaytools.git
cd RRKAL_displaytools
```

## Install dependencies

```powershell
.\scripts\setup_windows.ps1
```

如果系統權限不允許全域安裝：

```powershell
.\scripts\setup_windows.ps1 -UserInstall
```

## Smoke test

每次提交前至少跑：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1
```

Smoke 會做：

- Python entrypoint compile。
- Profile template validation。
- No-GUI launch packet export check。
- Renderer capabilities JSON check。
- Qt panel template listing check。
- PowerShell scripts parse check。

## Open Qt panel

```powershell
.\scripts\run_qt_panel.ps1
```

用內建模板開啟：

```powershell
.\scripts\run_qt_panel.ps1 -Template maritime_hydrology
```

可用模板先用：

```powershell
py -3 rrkal_displaytools_qt_panel.py --list-templates
```

## Quick headless render request

```powershell
.\scripts\render_quick_smoke.ps1
```

這會要求 renderer 走 synthetic/headless 快速輸出到 `state/showcase/quick_smoke.png`。`state/` 是 local-only，不要提交。

## Handoff packet

不用開 Qt 也可以從模板產生 launch packet：

```powershell
py -3 scripts\export_launch_packet.py --template fast_synthetic
```

要寫檔：

```powershell
py -3 scripts\export_launch_packet.py --template fast_synthetic --output state\showcase\fast_synthetic_launch_packet.json
```

## 邊界

- RRKAL / `APIkeys_collection` 負責 dataset discovery、download、import、install registry、manifest/cache governance。
- `RRKAL_displaytools` 負責 renderer launch/profile/layer/material/style/operator UI。
- 不要把 API key、download cache、generated image、SQLite state、`state/` 內容提交到 Git。
