# RRKAL Handoff Contract

最後更新：2026-05-29

## 目的

這份文件定義 RRKAL / `APIkeys_collection` 未來如何對接 `RRKAL_displaytools`，不需要讀 Qt UI 內部，也不需要把資料治理邏輯塞進 renderer。

## 責任邊界

RRKAL 負責：

- Dataset discovery。
- Download / import / install registry。
- Manifest / cache governance。
- Renderer bridge asset registration。
- Dataset version、checksum、license、source metadata。

displaytools 負責：

- Renderer launch profile。
- Layer/style/material operator state。
- Taichi globe visualization frontend。
- Launch packet / renderer capabilities / profile schema discovery。

## No-GUI discovery endpoints

### Renderer capabilities

```powershell
py -3 taichi_global_bathymetry.py --print-renderer-capabilities
```

輸出 schema：

```text
rrkal_displaytools.renderer_capabilities.v1
```

用途：

- 查 style profiles。
- 查 UI backend。
- 查 layer flags。
- 查 material controls。
- 查 RRKAL/displaytools 責任邊界。

### Profile templates

```powershell
py -3 rrkal_displaytools_qt_panel.py --list-templates
```

輸出 schema：

```text
rrkal_displaytools.profile_templates.v1
```

用途：

- 查 repo 內建 display profiles。
- 讓 RRKAL UI 或 script 顯示可用 renderer presets。
- 不需要啟動 Qt runtime。

### Profile schema

```powershell
py -3 profile_schema.py
```

輸出 schema：

```text
rrkal_displaytools.profile_schema_contract.v1
```

用途：

- 查必填 profile 欄位。
- 查必填 renderer/material/layer keys。
- 讓 RRKAL 產生 displaytools profile 時避免欄位漂移。

### Launch packet export

```powershell
py -3 scripts\export_launch_packet.py --template fast_synthetic
```

輸出 schema：

```text
rrkal_displaytools.launch_packet.v1
```

用途：

- 從 shared template 產生可攜 launch state。
- 取得 portable command。
- 作為 RRKAL renderer bridge asset 的候選 metadata。

## Local-only outputs

以下輸出只留本機，不提交 Git：

- `state/ui_profiles/`
- `state/showcase/`
- Generated PNG / screenshot / render output。
- Runtime logs / caches。

## 對接原則

- RRKAL 可以產生 profile 或 launch packet，但不要直接修改 renderer loop internals。
- displaytools 可以讀 RRKAL 產出的 manifest/cache/tile path，但不負責下載或資料授權判斷。
- Renderer bridge asset 若需要被登錄，應由 RRKAL install registry / manifest governance 擁有。
- `compose_run_parity_artifact_runner_schema` / `compose_run_parity_artifact_runner_script` 是跨機器 parity review 的手動入口；它只能產生本機 `state/compose_parity` artifacts，不應由 RRKAL 負責資料 discovery/download/cache governance。
- 若新增 layer flag 或 material control，必須同步更新 capabilities、profile schema、templates、smoke。
