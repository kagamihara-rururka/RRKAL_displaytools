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
- Research interaction：最後開 `Inspect: Layer pick`、`Inspect: Canvas state`、`Inspect: Pin pick`、`Inspect: Cursor geo`、`Inspect: Boundary JSON`，確認 selected-layer pick、Canvas Preview/provenance、Pin pick、滑鼠經緯度、Boundary/EEZ 強調與 identity warning。

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

## Qt Inspect: Visual review

- After cloning on another machine, open `Inspect: Renderer thumbnail` to inspect the latest renderer PNG if the renderer has produced one.
- Open `Inspect: Live preview` to switch Canvas Preview to the file-based live preview frame.
- These actions sit under `Inspect: Visual review`, separate from renderer diagnostics, so researchers can distinguish pixel inspection from capability/remediation metadata.

## Renderer menu Inspect alignment

- The Renderer menu mirrors the Actions panel labels for visual review: `Inspect: Renderer thumbnail` and `Inspect: Live preview`.
- Use either the menu or the `Inspect: Visual review` Actions section; both call the same Qt preview handlers.

## Qt Inspect: Selection state

- Use `Inspect: Selection state` when checking which layer is currently active for research operations.
- It reuses the layer pick state output, so clone users can review active layer selection, pick history, and renderer target metadata before treating a view as reproducible.

## Active layer operation summary

- In the Layers dock, read `Layer operation summary` before treating a renderer view as reproducible.
- It summarizes the active layer's visibility, lock, opacity, blend mode, renderer target, runtime ack and pick context.
- The same text is copied into Qt launch/provenance packets as `active_layer_operation_summary`.

## Last layer operation feedback

- Read `Last layer operation` in the Layers dock after visibility, lock or reset actions.
- The same compact status is exported in Qt launch/provenance packets as `last_layer_operation`.
- Solo selected layer, restore pre-solo visibility and layer undo also update this label, making isolation/history actions reviewable after clone.
- Group toggles and layer visual presets also update the same label, so clone users can see the latest high-level layer visibility workflow.

## Qt Inspect: Layer ops

- Use `Inspect: Layer ops` to review active layer operation summary, `Last layer operation`, operator group readiness and undo depth from one JSON packet.
- The same packet is exported as `layer_operation_feedback`, so cross-machine reviewers can inspect layer-operation provenance even without reproducing every click.
- `scripts\inspect_handoff.ps1` also reports `layer_operation_feedback`, so `-HandoffFirst` users can review this loop before launching Qt.

## Handoff profile/visual quick review

- `scripts\inspect_handoff.ps1` now reports `profile_visual_quick_review`.
- Use it to confirm Research interaction actions include `layer_ops` and Visual review actions include `renderer_thumbnail` / `live_preview`.
- Recommended quick sequence: `Inspect: Profile replay`, `Inspect: Layer ops`, `Inspect: Renderer thumbnail`, `Inspect: Live preview`.

## Visual review readiness

- `scripts\inspect_handoff.ps1` now reports `visual_review_readiness`.
- Use it before launching Qt on another machine to confirm `renderer_thumbnail` and `live_preview` Inspect actions are available.
- If preview frames are missing, follow the reported guidance: inspect renderer thumbnail, inspect live preview, then retry with a known style profile before filing a renderer issue.

## Qt visual readiness Inspect

- Visual review now includes `Inspect: Visual readiness` before `Inspect: Renderer thumbnail` and `Inspect: Live preview`.
- The same `visual_review_readiness` packet is exported by no-GUI launch packets and renderer capability discovery.
- Use this first when a cloned machine opens Qt but the preview frame path is unclear.

## Visual review frame status

- `visual_review_readiness.frame_status` now reports separate status for renderer thumbnail and live preview.
- Both entries are marked `inspect_action_available` and `runtime_dependent`, meaning the UI route exists while the actual frame depends on runtime capture/cache state.
- Use this to distinguish a missing frame artifact from a missing Qt Inspect entry.

## Visual review inspector view

- `visual_review_readiness.inspector_view` now packages title, status badges, rows and hints for a single Qt Visual review inspector.
- The view is copyable, so clone reviewers can paste the readiness state into issue notes or handoff logs.
- Use it as the first user-facing summary before checking renderer thumbnail or live preview separately.

## Visual readiness Qt command contract

- `visual_review_readiness.qt_command_contract` now documents the `Inspect: Visual readiness` action contract.
- The contract points Qt to `visual_review_readiness.inspector_view` as the payload field.
- Current implementation status is `under_construction`; until direct Qt dispatch is wired, use handoff, launch packet or renderer capability output.
