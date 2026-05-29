# Capability Summary

最後更新：2026-05-29

## 目前已有功能

### Qt-first operator UI

- `rrkal_displaytools_qt_panel.py` 提供 Qt/PyQt6 圖層控制面板。
- 產品定位是科研視覺化工作台：UI 借鑑 Photoshop 的面板精神，但優先服務科研者對圖層狀態、資料來源、profile 可重現性、manifest/launch packet 可追蹤性的需求。
- 前端方向採 Photoshop-inspired workspace：menu bar、左側 Tools dock、右側 dockable Layers/Properties/Navigator/History panels、工具選項、Looks/模板、圖層、屬性、中央預覽、動作分區。
- 可控制 style profile、UI backend、topography source、data mode、resolution、Taichi arch。
- 可控制 lake、river、border、territorial sea、EEZ、high seas、aircraft、ocean material、terrain contours、scale bar、vehicle icons 等圖層。
- 支援水文、海域、交通、視覺輔助四組一鍵切換，並可對目前選取圖層執行 Solo / restore visibility。
- Layers 面板已具備 Photoshop-like layer stack 雛形：active layer selection、visibility、lock、opacity、blend mode、UI-only state reset。Visibility 已接 renderer flags，並支援 Solo selected layer / restore previous visibility snapshot，方便科研者快速隔離水文、海域、交通或輔助圖層；Qt lock 會停用 locked layer 的 visibility checkbox，並讓 group toggle、Solo、restore 與 selected-layer visibility toggle 跳過 locked layers。Qt 會寫出 `state/renderer_layer_runtime_state.json`，renderer 可用 `--layer-runtime-state-file` 讀取並即時套用 visibility 變更。Layers 面板會顯示 layer runtime bridge 的 selected layer、visible count、last write 與 pending 狀態，也可把目前 runtime JSON 顯示到中央文字區。selected layer/opacity/blend 目前是 🚧 UI state，會寫入 launch packet 供後續 renderer sync。
- Properties 面板已接 active layer inspector，可查看目前選取圖層的 visibility、lock、opacity、blend mode，並可切換選取圖層 visibility 或重設選取圖層 UI state。
- Qt profile save/load 已支援 selected layer 與 layer stack UI state，因此 active layer、lock、opacity、blend mode 可以隨本機 profile 保存與載入；既有 repo templates 仍相容。
- 左側 Tools dock 已新增科研導向 tool palette：Move、Select、Pin。Select 用於指定 active layer，並可在 Canvas Preview 以垂直 hit bands 點選目前可見圖層；Pin 用於科研標記，可保存 type、label、note、latitude、longitude，並加入 marker list。Pin list 已支援選取、欄位回填與 selected pin 狀態保存。Brush/Mask 暫不納入本輪 UI。`tool_state`、`pins` 與 `selected_pin_id` 會寫入 profile 與 launch packet。
- 支援啟動、停止、套用並重啟 renderer。
- 顯示 renderer PID、執行中狀態與 exit code。
- 中央 Canvas Preview 已可用 UI-only 方式顯示 style/topography/data mode、active tool、active layer、visible layer count、Select hit map 與 zoom；也可顯示 renderer capabilities、layer manifest、launch packet 或 smoke 結果。
- Canvas Preview 已支援滑鼠位置的 UI-only 經緯度估算，使用 equirectangular canvas mapping，可一鍵填入 Pin 的 latitude/longitude，並顯示目前 selected pin 與 marker 摘要。
- 右側 `Provenance` dock 已提供科研可重現性摘要，可複製 JSON，內容包含 style/topo/data mode、active layer、active tool、visible/locked layers、layer count 與 portable command line。
- 已新增 `pin_projection.py` 共用 hook：以 latitude/longitude 作為 geodetic surface anchor，依 renderer camera yaw/pitch/zoom 投影到 screen_x/screen_y，並以 horizon clipping 判斷背面遮蔽；renderer capabilities 會暴露此 Pin overlay contract。
- Renderer 已支援 `--pin-file`、`--pin-json`、`--pin-layer`、`--pin-size`、`--pin-horizon-eps`、`--pin-label-mode`、`--pin-label-min-priority`、`--pin-pick-radius`、`--pin-pick-state-file`。Qt 若有 Pins，啟動 renderer 時會以 `--pin-json` 傳入，renderer 會每 frame 投影並只繪製可見 hemisphere 上的 Pin marker；`selected_pin_id` 會以 profile-aware 外圈高亮。Pin marker 已接 scientific、nautical、tactical、parchment style profiles，並具備基本 label box / leader line / collision avoidance。Qt Pin 已支援 `label_priority` 與 label visibility modes，renderer label placement 會先放 selected Pin，再依 priority 高低排序。Renderer 支援 Pin hover / click pick，點到 Pin 會更新 selected Pin highlight 與資訊面板，並可將 pick state 寫到 JSON bridge；外部 Qt control panel 會輪詢該 bridge，將 selected/cleared 事件同步回 Pin list、欄位與 provenance。Malformed `--pin-json` / `--pin-file` 會被 warning 後忽略，不再造成 renderer 閃退。
- 未完成的 live preview、brush/mask、timeline、undo stack 會以 🚧 施工中標示。
- 可保存、載入、重置本機 workspace layout，狀態位於 `state/ui_workspace.json`。
- Window menu 提供 workspace presets：Default、Maritime、Tactical、Parchment、Review，可切換 dock/tab 排版並套用對應顯示 preset。

## 預計實現功能

- Dockable panels 的更完整 Photoshop-like 版面：Layers / Properties / Navigator / History / Timeline。
- 中央 Canvas Preview 後續要從 UI-only 摘要升級為可嵌入或可同步的 renderer 畫面預覽。
- Renderer layer runtime sync 下一步擴充 opacity、blend mode、renderer-side lock enforcement；目前 visibility 已可透過 `state/renderer_layer_runtime_state.json` 即時同步，Qt 端已有 bridge diagnostics 與 lock 防誤改。
- Layer stack 的 selected layer、lock、opacity、blend mode 接 renderer 即時同步。
- Style / Looks panel 的縮圖化模板選擇。
- Select 工具下一步是從 UI-only Canvas Preview hit bands 升級到 renderer 實際圖層/物件 picking；Pin 下一步是把 renderer bridge 狀態做成更完整的 history/diagnostic UI，再補 globe mask / depth buffer refinement；Brush/Mask 暫不納入本輪 UI。
- Provenance 下一步要對接 renderer output artifact 與 RRKAL data manifest，但在 UIUX 閉環完成前只保留 UI provenance summary。
- Timeline / keyframe / animation controls for ocean/cloud/material parameters。
- Workspace presets 後續要補成可視化 preset manager，並支援保存多組命名工作區。

### Profiles and templates

- Repo-shared profiles 位於 `profiles/`。
- 目前內建：baseline scientific、maritime hydrology、parchment review、tactical ops、fast synthetic。
- Qt panel 可載入內建模板，也可儲存/載入本機 profile。
- 本機 profile 位於 `state/ui_profiles/`，不提交 Git。
- `profile_schema.py` 提供 shared validation rules 與 schema contract JSON。
- `scripts/validate_profiles.py` 會驗證內建模板欄位。

### No-GUI integration endpoints

- `py -3 taichi_global_bathymetry.py --print-renderer-capabilities`
- `py -3 taichi_global_bathymetry.py --print-layer-manifest`
- `py -3 rrkal_displaytools_qt_panel.py --list-templates`
- `py -3 profile_schema.py`
- `py -3 scripts\export_launch_packet.py --template fast_synthetic`

這些入口給腳本查詢 renderer 能力、圖層 manifest、可用 templates、profile schema，以及產生 launch packet。

### Launch packets and handoff

- Qt panel 可匯出 launch packet 到 `state/showcase/`。
- No-GUI exporter 可從 profile/template 產生 launch packet。
- Launch packet 內含 profile、portable command、RRKAL/displaytools 責任邊界。
- `docs/RRKAL_HANDOFF_CONTRACT.zh-TW.md` 定義未來 RRKAL 對接方式。

### Windows workflow

- `scripts/setup_windows.ps1` 安裝依賴。
- `scripts/run_qt_panel.ps1` 啟動 Qt panel，支援 `-Profile` 與 `-Template`。
- `scripts/render_quick_smoke.ps1` 要求快速 synthetic/headless render。
- `scripts/smoke.ps1` 是提交前 smoke helper。
- `docs/SETUP_WINDOWS.zh-TW.md` 提供另一台 Windows 電腦 clone/setup/smoke/run 步驟。

### CI / smoke

- GitHub Actions workflow：`.github/workflows/smoke.yml`。
- Smoke 目前檢查：
  - Python entrypoint compile。
  - Profile schema contract JSON。
  - Built-in profile validation。
  - No-GUI launch packet export。
  - Renderer capabilities JSON。
  - No-GUI template listing。
  - PowerShell script parse。

## 邊界

- displaytools 不負責 dataset discovery、download、import、install registry、cache/manifest governance。
- RRKAL / `APIkeys_collection` 仍是資料治理與 renderer bridge asset ownership 的來源。
- `state/`、generated images、runtime cache、logs、secrets 不提交 Git。




