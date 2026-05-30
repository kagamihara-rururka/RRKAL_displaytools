# 跨機器 Clone 快速啟動

最後更新：2026-05-31

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
"clone_reviewer_summary_contract_schema": "rrkal_displaytools.clone_reviewer_summary_contract.v1"
```

Qt 開啟後也可以在 Replay/contracts 使用 `Copy clone summary`，把 repo、setup doc、profile readiness、Qt-first、smoke-required 與 handoff-first 指令整理成可貼到交接紀錄的摘要。
同一區也有 `Copy launch summary`，用來複製 profile readiness、portable command、launch packet fields 與 renderer capability field。
Run/profile 區的 `Export reviewer packet` 會輸出 `state/showcase/reviewer_packet.json`，包含 clone、launch、research、visual、compose performance 摘要與 launch packet snapshot。若不開 Qt，也可執行 `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\export_reviewer_packet.ps1` 產生同路徑 reviewer packet。跨機器檢查效能優化狀態時，優先看 `compose_performance_summary`：它會合併 compose budget、slowest/advice、target pass model、parity runner readiness 與 `runtime_merge=false`。

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

可選的 compose parity artifact runner（較重，會啟動 renderer 並產生本機 artifacts）：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\render_compose_parity_artifacts.ps1
```

這會產生 `state/compose_parity/baseline_sequential_frame_rgba.png`、`state/compose_parity/merged_candidate_frame_rgba.png`、`state/compose_parity/renderer_output_metadata.json`、`state/compose_parity/render_compose_parity_smoke_manifest.json` 與 `state/compose_parity/compose_parity_artifact_runner.json`。Runner 會優先使用 `.venv\Scripts\python.exe`，找不到才 fallback 到 `py -3`。這些都是本機 runtime artifacts，不提交 Git。若只要產生 artifacts、暫不跑 RGBA diff，可加 `-SkipDiff`。

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

- Replay/contracts：先開 `Inspect: Clone ready`、`Inspect: Reviewer route`、`Inspect: Capability summary`、`Inspect: Profile replay`、`Inspect: Timeline`、`Inspect: Module seams`，確認 portable command、clone/setup/smoke/handoff/Qt review 路線、目前/預計功能、profile replay coverage、Timeline runtime/keyframes 與模組邊界。
- Renderer ports：再開 `Inspect: Hydro LOD`、`Inspect: Ocean port`、`Inspect: Style routes`、`Inspect: Layer matrix`、`Inspect: Layer runtime`，確認 hydrology/LOD、sea-state scalar port、parchment/tactical renderer routes、layer capability matrix 與 layer runtime ack。
- Research interaction：最後開 `Inspect: Layer pick`、`Inspect: Canvas state`、`Inspect: Pin pick`、`Inspect: Cursor geo`、`Inspect: Boundary JSON`，確認 selected-layer pick、Canvas Preview/provenance、Pin pick、滑鼠經緯度、Boundary/EEZ 強調與 identity warning。
- Visual review：再看 `Inspect: UIUX closure` 與 `Inspect: Workspace map`，確認 ready/queued 功能狀態、workspace dock 角色、研究者操作流與 visible non-goals。

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
- Current implementation status is `wired_in_qt_panel`; the Qt panel exposes both a Visual review button and Renderer menu action for this packet.

## Qt Visual readiness action

- `rrkal_displaytools_qt_panel.py` now exposes `Inspect: Visual readiness`.
- The action displays `visual_review_readiness` JSON in the command/provenance text panel before you inspect the renderer thumbnail or live preview.
- Use it to distinguish available Qt Inspect routes from runtime-dependent preview frame artifacts.

## Qt Visual readiness runtime artifacts

- The Qt action now adds `runtime_artifact_summary`.
- Renderer thumbnail and live preview statuses become `frame_available` when the relevant PNG/frame file exists, otherwise they stay `inspect_action_available` with `runtime_dependent` artifacts.
- This lets clone reviewers distinguish "UI route exists" from "runtime frame has not been produced yet".

## Qt Visual readiness visible summary

- The Layers dock now includes a `visualReviewReadiness` label.
- Pressing `Inspect: Visual readiness` updates the label with thumbnail/live preview status and artifact paths.
- This gives a compact visual-review state without reading the full JSON packet.

## Qt Visual readiness copy summary

- The Visual review group now includes `Copy visual summary`.
- It copies the compact thumbnail/live-preview readiness summary to the clipboard.
- Use this when recording renderer-preview state in lab notes, issues or cross-machine handoff.

## Visual readiness copy summary contract

- `visual_review_readiness.copy_summary_contract` now documents the portable summary label, format, Qt label object and copy action.
- The same contract appears in launch packets and handoff output.
- Use it to keep Qt-visible summaries, copied notes and cross-machine handoff language aligned.

## Layer selection summary contract

- `layer_selection_tool.selection_summary_contract` now documents the portable selected-layer summary.
- Qt exposes `Copy selection summary` in the Research interaction group.
- The summary keeps active layer, renderer pick bridge and brush/mask exclusion scope aligned for clone handoff.

## Boundary emphasis summary contract

- `boundary_emphasis_control.boundary_summary_contract` now documents the portable Boundary emphasis summary.
- Qt exposes `Copy boundary summary` in the Research interaction group.
- The summary keeps target mode, target layer, alignment, RGB/opacity and renderer bridge language aligned for clone handoff.

## Pin overlay summary contract

- `pin_overlay.pin_summary_contract` now documents the portable Pin overlay summary.
- Qt exposes Pin summary copy actions in the Pin Annotation panel and Research interaction group.
- The summary keeps pin count, selected pin, coordinate source, pick bridge, rotation and occlusion language aligned for clone handoff.

## Cursor geodesy summary contract

- `cursor_geodesy_readout.cursor_summary_contract` now documents the portable cursor geodesy summary.
- Qt exposes `Copy cursor summary` in the Research interaction group.
- The summary keeps source, hit state, latitude/longitude, renderer state/ack files and raycast method aligned for clone handoff.

## Research interaction summary bundle

- `layer_research_workflow.research_summary_contract` now documents the portable reviewer summary bundle.
- Qt exposes `Copy research summary` in the Research interaction group.
- The bundle combines layer selection, Pin overlay, cursor geodesy and Boundary emphasis summaries for cross-machine notes.
