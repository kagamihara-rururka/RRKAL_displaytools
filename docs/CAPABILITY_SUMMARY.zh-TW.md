# Capability Summary

最後更新：2026-05-29

## 目前已有功能

### Qt-first operator UI

- `rrkal_displaytools_qt_panel.py` 提供 Qt/PyQt6 圖層控制面板。
- 產品定位是科研視覺化工作台：UI 借鑑 Photoshop 的面板精神，但優先服務科研者對圖層狀態、資料來源、profile 可重現性、manifest/launch packet 可追蹤性的需求。
- 模組邊界與後續解耦順序記錄於 `docs/MODULE_BOUNDARIES.zh-TW.md`；displaytools 只負責視覺化/UI/renderer bridge，不接手 RRKAL 的資料 discovery/download/cache governance。
- 跨機器 clone / smoke / Qt 啟動步驟記錄於 `docs/QUICKSTART_CLONE.zh-TW.md`；`scripts/run_qt_panel.ps1` 是建議啟動入口，會優先使用 repo `.venv`，也支援 `-SmokeFirst`。
- 前端方向採 Photoshop-inspired workspace：menu bar、左側 Tools dock、右側 dockable Layers/Properties/Navigator/History panels、工具選項、Looks/模板、圖層、屬性、中央預覽、動作分區。
- 可控制 style profile、UI backend、topography source、data mode、resolution、Taichi arch。
- 可控制 lake、river、border、territorial sea、EEZ、high seas、aircraft、Pin marker、ocean material、terrain contours、scale bar、vehicle icons 等圖層。
- 支援水文、海域、交通、視覺輔助四組一鍵切換，並可對目前選取圖層執行 Solo / restore visibility。
- Layers 面板已具備 Photoshop-like layer stack 雛形：active layer selection、visibility、lock、opacity、blend mode、UI-only state reset 與 layer stack undo snapshots。Visibility 已接 renderer flags，並支援 Solo selected layer / restore previous visibility snapshot，方便科研者快速隔離水文、海域、交通或輔助圖層；Qt lock 會停用 locked layer 的 visibility checkbox，並讓 group toggle、Solo、restore、selected-layer visibility toggle 與 layer undo 跳過或還原正確 layer UI state。Qt 會寫出 `state/renderer_layer_runtime_state.json`，renderer 可用 `--layer-runtime-state-file` 讀取並即時套用 visibility 與支援圖層的 opacity 變更，也可用 `--layer-runtime-ack-file` 寫回 `state/renderer_layer_runtime_ack.json` 作為接收回執；renderer 端會把 Qt layer keys 對應到 renderer layer IDs，並跳過 runtime state 中 `locked=true` 圖層的 visibility/opacity/支援 overlay blend 變更，ack 會回報 `changed_opacity_layers`、`skipped_locked_layers`、`layer_opacity`、selected renderer target 與 alias map。Layers 面板會顯示 layer runtime bridge 的 selected layer、renderer target、visible count、last write、renderer ack、opacity changed count 與 skipped locked count，也可把目前 runtime JSON 與 layer pick JSON 顯示到中央文字區；History 面板會記錄最近 layer runtime 摘要、layer undo snapshot 與 pick 摘要變更，provenance 也會保留最近幾筆 layer runtime history、renderer ack 與 layer pick state。selected layer semantic target 已成為 renderer ack 中可追蹤的語意目標，renderer 滑鼠點擊會依目前 selected layer 限定 Pin、交通點、boundary 線段或 hydrology 線段 picking，並寫回 `state/renderer_layer_pick_state.json` 讓 Qt 面板顯示；若來源 GeoJSON 有 properties，pick state 會帶 source-property feature identity，並優先辨識 Natural Earth / Marine Regions 常見名稱、主權、ISO 與 MRGID 欄位，Qt layer pick label 也會直接顯示 feature label；後續剩下 authoritative polygon territory identity / open-line area inference。
- Renderer layer runtime opacity 目前已落地到 hydrology/boundary/scale/contours、ADS-B aircraft overlay alpha、Pin marker overlay alpha 與 vehicle icon overlay alpha。
- Renderer layer runtime blend mode 目前已對 lake、river、borders、territorial sea、EEZ、high seas、ADS-B aircraft、Pin marker 與 vehicle icon overlay 支援 Normal、Screen、Multiply、Overlay、Soft Light。
- Renderer layer runtime visibility 目前已同步 hydrology/boundary/aircraft/pin/vehicle icons/scale/contours/grid/stars/ocean material 的對應 renderer flags；這些基礎視覺圖層可透過 runtime bridge 改變而不必重啟。
- Qt layer stack metadata 會在 profile / launch packet / runtime bridge 中寫入每個 layer 的 `renderer_sync` 摘要，區分 visibility / opacity / blend live 狀態；runtime bridge 另會寫出 selected renderer target 供 renderer ack/provenance 追蹤。
- Properties 面板已接 active layer inspector，可查看目前選取圖層的 visibility、lock、opacity、blend mode、renderer target，以及最近 renderer runtime ack / layer pick 摘要，並可切換選取圖層 visibility 或重設選取圖層 UI state。
- Properties 面板已新增 `Boundary highlight` 疆域強調遮罩控制入口與 `Boundary identity` 摘要；國界、領海、EEZ、公海圖層列可雙擊打開控制對話框，設定 hover/selected 觸發、target layers、RGB 色彩、對比、半透明、gamma、feather 與呼吸特效。對話框、Properties 摘要與 `boundary_highlight.identity_status` 會明確標示 source-property feature identity 已 live，但 authoritative 疆域/EEZ identity 與 open-line area inference 仍 pending。此狀態已寫入 profile、launch packet、Canvas Preview 與 provenance；Qt 啟動 renderer 時會以 `--boundary-highlight-json` 傳入，renderer 會用 `--boundary-highlight-ack-file` 寫回 `state/renderer_boundary_highlight_ack.json`。Renderer 目前已用該 payload 控制 hover hit target layers、啟用狀態、outline/glow 顏色、contrast、gamma、alpha、feather 與 breathing speed；滑鼠移到國界/領海/EEZ/公海線段附近，或落在完整可見的閉合 ring 內，可看到線段/面域強調；閉合 ring 幾何會加上半透明 polygon fill preview，fill preview 會套用獨立的 gamma/contrast tone 控制，且 source GeoJSON properties 會進入 pick feature identity。Authoritative polygon territory identity 與開放線段面域推論仍是下一步。
- Qt profile save/load 已支援 selected layer 與 layer stack UI state，因此 active layer、lock、opacity、blend mode 可以隨本機 profile 保存與載入；既有 repo templates 仍相容。
- 左側 Tools dock 已新增科研導向 tool palette：Move、Select、Pin。Select 用於指定 active layer，並可在 Canvas Preview 以垂直 hit bands 點選目前可見圖層；Pin 用於科研標記，可保存 type、label、note、latitude、longitude，並加入 marker list。Pin list 已支援選取、欄位回填與 selected pin 狀態保存。Brush/Mask 暫不納入本輪 UI。`tool_state`、`pins` 與 `selected_pin_id` 會寫入 profile 與 launch packet。
- 支援啟動、停止、套用並重啟 renderer。
- 顯示 renderer PID、執行中狀態與 exit code。
- 中央 Canvas Preview 已可用 UI-only 方式顯示 style/topography/data mode、active tool、active layer、visible layer count、Select hit map 與 zoom；也可切到最近 `state/showcase/*.png` 的 renderer static thumbnail，thumbnail 模式下會自動輪詢並刷新最新 PNG。Qt 啟動 renderer 時會帶入 `--preview-frame-file state/renderer_preview_frame.png`，Canvas Preview 的 Live preview 模式會輪詢該 PNG，形成 file-based live renderer frame stream。Canvas preview mode、preview frame path 與 interval 會寫入 profile / launch packet / provenance；runtime PNG 只作本機狀態，不提交 Git。中央文字區也可顯示 renderer capabilities、layer manifest、launch packet 或 smoke 結果。
- Canvas Preview 已支援滑鼠位置的 UI-only 經緯度估算，使用 equirectangular canvas mapping，可一鍵填入 Pin 的 latitude/longitude，並顯示目前 selected pin 與 marker 摘要。
- 右側 `Provenance` dock 已提供科研可重現性摘要，可複製 JSON，內容包含 style/topo/data mode、active layer、active layer diagnostics、active tool、visible/locked layers、layer count 與 portable command line。
- 已新增 `pin_projection.py` 共用 hook：以 latitude/longitude 作為 geodetic surface anchor，依 renderer camera yaw/pitch/zoom 投影到 screen_x/screen_y，並以 horizon clipping 判斷背面遮蔽；renderer capabilities 會暴露此 Pin overlay contract。
- Renderer 已支援 `--pin-file`、`--pin-json`、`--pin-layer`、`--pin-size`、`--pin-horizon-eps`、`--pin-label-mode`、`--pin-label-min-priority`、`--pin-pick-radius`、`--pin-pick-state-file`、`--pin-input-ack-file`。Qt 若有 Pins，啟動 renderer 時會以 `--pin-json` 傳入，renderer 會每 frame 投影並只繪製可見 hemisphere 上的 Pin marker；`selected_pin_id` 會以 profile-aware 外圈高亮。Renderer 初始化後可寫回 `state/renderer_pin_input_ack.json`，記錄收到的 pin_count、selected_pin_id 與 selected pin 是否存在。Pin marker 已接 scientific、nautical、tactical、parchment style profiles，並具備基本 label box / leader line / collision avoidance。Qt Pin 已支援 `label_priority` 與 label visibility modes，renderer label placement 會先放 selected Pin，再依 priority 高低排序。Renderer 支援 Pin hover / click pick，點到 Pin 會更新 selected Pin highlight 與資訊面板，並可將 pick state 寫到 JSON bridge；外部 Qt control panel 會輪詢該 bridge，將 selected/cleared 事件同步回 Pin list、欄位與 provenance，並寫出 `state/qt_pin_pick_ack.json` 記錄 Qt 是否已同步該 renderer event。Pin Annotation 面板可直接顯示 renderer Pin input ack、最新 Pin pick JSON 與 Qt ack；History 面板會記錄最近 Pin pick 摘要，provenance 也會保留最新 Pin input ack、Pin pick payload、Qt ack 與最近幾筆 Pin pick history。Malformed `--pin-json` / `--pin-file` 會被 warning 後忽略，不再造成 renderer 閃退。
- 未完成的 timeline 與全域 document undo stack 會以 🚧 施工中標示；layer stack undo snapshots 已落地，Canvas Preview 的 state / static thumbnail / file-based live preview 已落地，Brush/Mask 暫不納入本輪 UI。
- 可保存、載入、重置本機 workspace layout，狀態位於 `state/ui_workspace.json`。
- Window menu 提供 workspace presets：Default、Maritime、Tactical、Parchment、Review，可切換 dock/tab 排版並套用對應顯示 preset。

## 預計實現功能

- Dockable panels 的更完整 Photoshop-like 版面：Layers / Properties / Navigator / History / Timeline。
- 中央 Canvas Preview 已具備 Qt state preview、最近 renderer output static thumbnail、static thumbnail auto-refresh 與 file-based live renderer frame stream；後續要升級為低延遲 IPC/GPU texture stream。
- Renderer layer runtime sync 下一步擴充 polygon fill mask 與更完整 renderer diagnostics；目前 visibility、支援圖層 opacity、lake/river/boundary/aircraft/pin/vehicle icon overlay blend、selected layer semantic target、selected-layer-scoped Pin/traffic/boundary/hydrology line picking 已可透過 `state/renderer_layer_runtime_state.json` 與 `state/renderer_layer_pick_state.json` 即時同步，Qt 與 renderer 端已有 bridge diagnostics、history、renderer ack 與 locked layer 防誤改。
- Point/icon opacity/blend 下一步處理其他新增獨立 overlay，前提是 renderer 有可單獨合成的 frame overlay。
- Layer stack 下一步是 selected layer 的 authoritative polygon territory identity、開放線段面域推論與更完整 renderer diagnostics。
- Style / Looks panel 的縮圖化模板選擇。
- Select 工具已接 renderer selected-layer object picking bridge；Canvas Preview 本身仍保留 Qt-side hit bands，也可嵌入最近 renderer PNG thumbnail 或 file-based live renderer frame stream。Pin 下一步是補更細的 renderer interaction ack 與 globe mask / depth buffer refinement；Brush/Mask 暫不納入本輪 UI。
- Boundary highlight 下一步是從目前 line hover outline/glow、source-property feature identity、閉合 ring area hit、閉合 ring polygon preview 與 fill gamma/contrast tone 控制，升級到 authoritative 疆域/領海/EEZ identity 與開放線段面域推論。
- Renderer headless/once output 會在 image output 旁寫出 `.metadata.json` sidecar，記錄 renderer state、layer state、selected-layer pick、boundary highlight、closed-loop status、RRKAL data manifest reference 與 RRKAL/displaytools 邊界。`--rrkal-data-manifest-ref` / Qt `RRKAL manifest ref` 只做 reference passthrough；manifest validation/ingest/governance 會在 closed-loop status 中列為 RRKAL external dependency，不列為 displaytools pending。
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
- `py -3 taichi_global_bathymetry.py --print-closed-loop-status`
- `py -3 taichi_global_bathymetry.py --print-layer-manifest`
- `py -3 rrkal_displaytools_qt_panel.py --list-templates`
- `py -3 profile_schema.py`
- `py -3 scripts\export_launch_packet.py --template fast_synthetic`

這些入口給腳本查詢 renderer 能力、closed-loop status、圖層 manifest、可用 templates、profile schema，以及產生 launch packet。Renderer capabilities 內含 `closed_loop_status`、`preview_frame_stream` 與 `active_layer_diagnostics` contract，也可用 `--print-closed-loop-status` 只輸出目前 closed、partial 與 pending 的功能邊界；closed-loop status 會列出 `diagnostics_handoff_contracts`。

### Launch packets and handoff

- Qt panel 可匯出 launch packet 到 `state/showcase/`，內容包含當下的 `closed_loop_status` snapshot 與 `active_layer_diagnostics` snapshot。
- No-GUI exporter 可從 profile/template 產生 launch packet，並包含 `closed_loop_status` snapshot、`canvas_preview` contract、`active_layer_diagnostics` contract、preview frame stream CLI args、`pin-layer` renderer flag 與 optional `--rrkal-data-manifest-ref` reference-only handoff。
- Launch packet 內含 profile、portable command、RRKAL/displaytools 責任邊界。
- `docs/RRKAL_HANDOFF_CONTRACT.zh-TW.md` 定義未來 RRKAL 對接方式。

### Windows workflow

- `scripts/setup_windows.ps1` 安裝依賴。
- `scripts/run_qt_panel.ps1` 啟動 Qt panel，支援 `-Profile` 與 `-Template`。
- `scripts/render_quick_smoke.ps1` 要求快速 synthetic/headless render，並驗證 preview frame PNG 寫檔。
- `scripts/smoke.ps1` 是提交前 smoke helper。
- `docs/SETUP_WINDOWS.zh-TW.md` 提供另一台 Windows 電腦 clone/setup/smoke/run 步驟。

### CI / smoke

- GitHub Actions workflow：`.github/workflows/smoke.yml`。
- Smoke 目前檢查：
  - Python entrypoint compile。
  - Profile schema contract JSON。
  - Built-in profile validation。
  - No-GUI launch packet export。
  - Launch packet `canvas_preview` schema gate。
  - Launch packet `active_layer_diagnostics` schema gate。
  - Launch packet `boundary_highlight.identity_status` schema gate。
  - Launch packet `--preview-frame-file` gate。
  - Launch packet `canvas_preview.preview_frame_path` / `preview_frame_interval_s` gate。
  - Renderer capabilities JSON 與 `preview_frame_stream` / `active_layer_diagnostics` schema gate。
  - Closed-loop status `diagnostics_handoff_contracts` gate。
  - No-GUI template listing。
  - PowerShell script parse。

## 邊界

- displaytools 不負責 dataset discovery、download、import、install registry、cache/manifest governance。
- RRKAL / `APIkeys_collection` 仍是資料治理與 renderer bridge asset ownership 的來源。
- `state/`、generated images、runtime cache、logs、secrets 不提交 Git。




