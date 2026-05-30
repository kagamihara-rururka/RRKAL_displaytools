# Profile Schema

最後更新：2026-05-29

## 目的

`profiles/*.json` 是 `RRKAL_displaytools` 的 Qt panel 啟動與 UI 狀態模板。它描述 renderer launch state、style、material、layers，以及可選的 layer stack UI state。

這不是 RRKAL 的 dataset manifest、install registry 或 cache manifest。RRKAL 仍負責資料治理；displaytools profile 只描述視覺化前端如何啟動與呈現。

## Schema id

```text
rrkal_displaytools.qt_panel_profile.v1
```

## Top-level fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | optional | UI 顯示名稱。 |
| `description` | string | optional | 模板用途說明。 |
| `schema` | string | required | Profile schema id。 |
| `renderer` | object | required | Renderer 啟動參數。 |
| `ocean_material` | object | required | 海洋材質參數。 |
| `layers` | object | required | Renderer layer visibility flags。 |
| `selected_layer` | string | optional | Qt layer stack 目前選取圖層。 |
| `selected_pin_id` | string | optional | Qt Pin list 目前選取的科研標記 id。 |
| `layer_filter` | object | optional | Qt Layers row search/filter 狀態，不改變 renderer layer state。 |
| `layer_group_view` | object | optional | Qt Layers row group collapse/expand 狀態，不改變 renderer layer state。 |
| `layer_stack_ui` | object | optional | Qt layer stack 的 UI-only state。 |
| `tool_state` | object | optional | Qt tool palette 的 UI-only state。 |
| `pins` | array | optional | 科研標記清單。 |
| `boundary_highlight` | object | optional | 疆域/領海/EEZ hover 強調遮罩控制。 |
| `boundary_emphasis_control` | object | optional | Layers dock Boundary emphasis dialog 的 UI profile state。 |
| `canvas_preview` | object | optional | 中央 Canvas Preview 模式、static renderer thumbnail 或 live renderer frame stream 參考。 |
| `timeline_export` | object | optional | Timeline renderer export UI 狀態，只準備 renderer flags 與本機輸出路徑。 |
| `timeline_keyframes` | array | optional | Timeline keyframe 清單，可保存 pins、boundary highlight 與 boundary emphasis control。 |

## `renderer`

| Field | Example | Description |
| --- | --- | --- |
| `style_profile` | `scientific` | 對應 renderer `--style-profile`。 |
| `ui_backend` | `qt` | 對應 renderer `--ui`。 |
| `topo_source` | `gebco` | `gebco` 或 `synthetic`。 |
| `data_mode` | `static` | `static`、`realtime` 或 `timeseries`。 |
| `width` | `1280` | CLI width，保存為字串以貼近 Qt 輸入欄。 |
| `height` | `720` | CLI height，保存為字串以貼近 Qt 輸入欄。 |
| `topo_step` | `48` | Topography sampling step。 |
| `taichi_arch` | `gpu` | Taichi backend。 |

## `ocean_material`

| Field | Example | Description |
| --- | --- | --- |
| `wave_strength` | `0.22` | 對應 `--ocean-wave-strength`。 |
| `roughness` | `0.28` | 對應 `--ocean-roughness`。 |
| `foam` | `0.12` | 對應 `--ocean-foam`。 |

## `layers`

每個欄位都是 boolean，對應 Qt panel 與 renderer flag：

- `show_grid`
- `show_stars`
- `lake_layer`
- `river_layer`
- `border_layer`
- `territorial_sea_layer`
- `eez_layer`
- `high_seas_layer`
- `aircraft_layer`
- `pin_layer`
- `ocean_material`
- `terrain_contours`
- `scale_bar`
- `vehicle_icons`
- `demo_closed_loop`

## `selected_layer`

可選。若存在，必須是 layer stack key：

- `show_grid`
- `show_stars`
- `lake_layer`
- `river_layer`
- `border_layer`
- `territorial_sea_layer`
- `eez_layer`
- `high_seas_layer`
- `aircraft_layer`
- `pin_layer`
- `ocean_material`
- `terrain_contours`
- `scale_bar`
- `vehicle_icons`

## `layer_filter`

可選。此欄位保存 Layers 面板的 row search/filter 狀態，讓 profile / launch packet / provenance 可重現研究者當時如何縮小圖層列表；它只影響 Qt row visibility，不會切換 renderer layer visibility。

| Field | Type | Description |
| --- | --- | --- |
| `schema` | string | 固定為 `rrkal_displaytools.layer_filter.v1`。 |
| `mode` | string | 目前為 `ui_row_filter` 或 no-GUI export 的 `no_gui_export_status`。 |
| `preset` | string | `all`、`hydrology`、`maritime`、`traffic`、`visual_aids` 或 `custom`。 |
| `available_presets` | array | Qt 目前提供的 focus preset 清單。 |
| `query` | string | 使用者輸入的搜尋字串。 |
| `first_matched_layer` | string or null | 目前 filter 結果中的第一個 layer key，可供 Qt `Select first` 使用。 |
| `selected_layer_visible` | boolean | 目前 active layer 是否仍在 filter 結果中可見。 |
| `selected_layer_reveal_available` | boolean | active layer 是否可用 `Reveal selected` 清除 filter 或展開 group 找回 row。 |
| `matched_layers` | array | 符合 query 的 layer key 清單。 |
| `matched_count` | integer | 符合的 row 數。 |
| `visible_matched_layers` | array | 同時符合 filter 且未被 group collapse 隱藏的 layer key 清單。 |
| `visible_matched_count` | integer | 同時符合 filter 且仍顯示的 row 數。 |
| `total_layers` | integer | 可過濾的 layer row 總數。 |
| `boundary` | string | 明確標示 filter 只影響 Qt UI row，不影響 renderer state。 |

## `layer_group_view`

可選。此欄位保存 Layers 面板的 row group collapse/expand 狀態；它只影響 Qt row visibility，不會切換 renderer layer visibility、opacity 或 blend。

| Field | Type | Description |
| --- | --- | --- |
| `schema` | string | 固定為 `rrkal_displaytools.layer_group_view.v1`。 |
| `mode` | string | 目前為 `ui_row_collapse` 或 no-GUI export 的 `no_gui_export_status`。 |
| `available_groups` | object | group id 到 layer key 清單的映射。 |
| `collapsed_groups` | array | 目前被 collapse 的 group id 清單。 |
| `visible_counts_by_group` | object | filter 與 group collapse 後，各 group 仍顯示的 row 數。 |
| `total_counts_by_group` | object | 各 group 的 row 總數。 |
| `selected_layer_group` | string or null | 目前 active layer 所屬 group，若不屬於 group 則為 null。 |
| `selected_layer_hidden_by_group` | boolean | 目前 active layer 是否因所屬 group collapse 而在 Layers row 中被藏起來。 |
| `active_group_collapsed` | boolean | `selected_layer_group` 是否目前處於 collapse 狀態。 |
| `visible_row_count` | integer | filter 與 group collapse 後仍顯示的 row 數。 |
| `total_layers` | integer | 可顯示的 layer row 總數。 |
| `boundary` | string | 明確標示 group collapse 只影響 Qt UI row，不影響 renderer state。 |

## `layer_stack_ui`

可選。若存在，應包含上述 layer stack key。每個 layer object 目前支援：

| Field | Type | Description |
| --- | --- | --- |
| `locked` | boolean | Qt 與 renderer visibility sync 的防誤改 guardrail；opacity/blend renderer sync 尚未接。 |
| `opacity` | integer 0-100 | UI-only opacity，renderer sync 尚未接。 |
| `blend_mode` | string | `Normal`、`Screen`、`Multiply`、`Overlay` 或 `Soft Light`。 |
| `selected` | boolean | 可選，記錄該 layer 是否為 active layer。 |
| `renderer_sync` | string | 可選，通常為 `planned`。 |

## `tool_state`

可選。此欄位保存左側 tool palette 的 UI-only 狀態，方便本機 profile 保存、跨機器載入與 launch packet handoff。

| Field | Type | Description |
| --- | --- | --- |
| `active_tool` | string | `move`、`select` 或 `pin`。 |
| `target_layer` | string or null | 工具目前綁定的 active layer key。 |
| `pin_label_mode` | string | 可選，`auto`、`selected`、`priority` 或 `hidden`。 |
| `pin_label_min_priority` | integer 0-100 | 可選，`priority` mode 的最低顯示門檻。 |
| `pin` | object | 可選，科研地理標記 UI state。 |
| `renderer_sync` | string | 可選，通常為 `planned`。 |

`pin` object 目前支援：

| Field | Type | Description |
| --- | --- | --- |
| `type` | string | `Observation`、`Sample Site`、`Anomaly`、`Reference` 或 `Event`。 |
| `label` | string | 標記名稱。 |
| `note` | string | 標記備註。 |
| `latitude` | string | Pin 編輯欄中的緯度文字。 |
| `longitude` | string | Pin 編輯欄中的經度文字。 |
| `label_priority` | integer 0-100 | Renderer label 排版優先度。 |
| `placement` | string | 與 `coordinate_source` 相同；目前支援 `manual_lat_lon`、`renderer_globe_raycast`、`qt_canvas_estimate`。 |
| `coordinate_source` | string | Pin 座標來源：手動輸入、renderer globe raycast 或 Qt canvas estimate fallback。 |
| `coordinate_source_label` | string | 給 UI / handoff 顯示的人類可讀座標來源。 |

目前 `tool_state` 不會直接改 renderer。Brush / Mask 暫不納入本輪 UI；Select 用於指定 active layer，Pin 用於保存科研標記意圖。Pin cursor fill 會優先使用 renderer globe raycast，沒有 renderer hit 時才 fallback 到 Qt Canvas estimate。

## `pins`

可選。此欄位保存科研標記清單，適合記錄觀測點、採樣站、異常點、參考點與事件。若 `selected_pin_id` 存在，必須對應到此清單中的其中一個 `id`，Qt 會用它回復 Pin list 選取狀態並回填 Pin 編輯欄位。

Renderer overlay 接上後，Pin 不應是螢幕固定標籤，而應是 geodetic surface anchor：每個 frame 由 latitude/longitude 投影到球面，套用地球旋轉與 camera/view transform，再用 horizon/depth occlusion 判斷是否被地球背面或地形/海面遮蔽。

目前共用投影 hook 位於 `pin_projection.py`。它已能計算 `screen_x`、`screen_y`、`view_z`、`visible` 與 `occlusion`，先覆蓋跟隨地球旋轉與背面 horizon clipping。Renderer 已可透過 `--pin-file` 或 `--pin-json` 接收 Pins 並畫出可見 marker；若 payload 包含 `selected_pin_id`，renderer 會以高亮外圈標示該 Pin。Marker 顏色會依 `style_profile` 套用 scientific、nautical、tactical 或 parchment palette；label 目前使用簡單四象限候選位置與碰撞避讓，並支援 auto / selected / priority / hidden 顯示模式。Renderer 目前也支援畫面中的 Pin hover 與 click pick；後續再以 globe mask/depth buffer refine 地形或海面遮蔽。

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Pin id，例如 `pin-001`。 |
| `type` | string | `Observation`、`Sample Site`、`Anomaly`、`Reference` 或 `Event`。 |
| `label` | string | 標記名稱。 |
| `note` | string | 可選，標記備註。 |
| `latitude` | number -90..90 | 緯度。 |
| `longitude` | number -180..180 | 經度。 |
| `label_priority` | integer 0-100 | 可選，renderer label layout 優先度；selected Pin 仍會優先於一般 Pin。 |
| `target_layer` | string or null | 可選，建立 pin 時的 active layer。 |
| `placement` | string | 與 `coordinate_source` 相同；支援 `manual_lat_lon`、`renderer_globe_raycast`、`qt_canvas_estimate`。 |
| `coordinate_source` | string | 建立此 Pin 時的座標來源。 |
| `coordinate_source_label` | string | Pin list / handoff 使用的人類可讀來源，例如 `Renderer globe raycast`。 |

## `boundary_highlight`

可選。此欄位保存國界、領海、EEZ、公海等疆域圖層的 hover/selected 強調遮罩設定，讓科研者可以把疆域、領海或經濟海域作為可重現的視覺分析狀態保存到 profile 與 launch packet。

| Field | Type | Description |
| --- | --- | --- |
| `schema` | string | 固定為 `rrkal_displaytools.boundary_highlight_mask.v1`。 |
| `enabled` | boolean | 是否啟用疆域強調遮罩。 |
| `trigger` | string | `hover`、`selected` 或 `hover_or_selected`。 |
| `target_layers` | array | 只允許 `border_layer`、`territorial_sea_layer`、`eez_layer`、`high_seas_layer`。 |
| `color_rgb` | array | 三個 0-255 integer，對應遮罩 RGB。 |
| `contrast` | integer 0-100 | 疆域強調對比度。 |
| `alpha` | integer 0-100 | 遮罩半透明程度。 |
| `gamma` | integer 25-300 | gamma bar，100 表示 1.00x。 |
| `feather` | integer 0-100 | 邊界柔化程度。 |
| `breathing` | object | 呼吸特效設定，包含 `enabled`、`speed`、`amplitude`。 |
| `identity_status` | object | 可選，固定 schema 為 `rrkal_displaytools.boundary_identity_status.v1`；記錄 source-property identity / closed-ring preview 已 live，authoritative territory/EEZ identity 與 open-line area inference 仍 pending。 |
| `renderer_sync` | string | 目前預設為 `renderer_line_fill_identity_status_handoff`，表示 renderer line/fill highlight 與 identity-status handoff 已接；authoritative polygon territory identity 仍未接。 |

目前 Qt 已提供 Properties 入口與圖層列雙擊對話框，並會把設定寫入 profile、launch packet、Canvas Preview 與 provenance。Renderer 已接 hover outline/glow、closed-ring fill preview、contrast/gamma/fill tone 與 identity-status handoff；下一步是 authoritative polygon territory identity 與 open-line area inference。

## `boundary_emphasis_control`

可選。此欄位保存 Layers dock `Boundary emphasis controls...` 對話框的 UI profile state，並映射到 `boundary_highlight` renderer bridge。圖層列的 Boundary/EEZ 類 row 會顯示 `Emphasis` action badge，雙擊可打開同一對話框。

| Field | Type | Description |
| --- | --- | --- |
| `schema` | string | 固定為 `rrkal_displaytools.boundary_emphasis_control.v1`。 |
| `target_mode` | string | `auto_selected_boundary_layer`、`country_boundary`、`territorial_sea`、`exclusive_economic_zone` 或 `maritime_boundary`。 |
| `target_layer_key` | string or null | 由 `target_mode` 解析出的 Qt layer key。 |
| `selected_layer_matches_target` | boolean | 目前 active layer 是否與 emphasis target 對齊。 |
| `target_alignment` | string | `selected_layer_matches_target`、`selected_layer_differs_from_target`、`selected_layer_not_boundary_capable` 或 `no_selected_layer`。 |
| `target_alignment_label` | string | Canvas Preview / Layers dock 顯示的人類可讀對齊狀態。 |
| `color_rgb` | array | 三個 0-255 integer。 |
| `contrast` | number | UI slider 值，預設約 `1.35`。 |
| `opacity` | number | UI slider 值，0.0 到 1.0。 |
| `gamma` | number | UI slider 值，預設 `1.0`。 |
| `breathing_enabled` | boolean | 是否啟用呼吸效果。 |
| `breathing_period_s` | number | 呼吸週期秒數。 |
| `dialog_feedback` | array | 目前包含 `rgb_swatch`、`live_numeric_readout`、`renderer_bridge_summary`。 |
| `value_preview_fields` | array | 對話框 live preview 與 handoff 應顯示的主要欄位。 |

此欄位是 displaytools UI/renderer bridge contract；authoritative polygon territory identity、EEZ identity source 與 open-line area inference 仍屬後續資料/幾何閉環。

## `canvas_preview`

可選。此欄位保存中央 Canvas Preview 的 UI 狀態，讓 profile / launch packet 可重現操作者當時是在看 Qt state preview、最近一次 renderer output static thumbnail，或 renderer 寫出的 file-based live preview frame。

| Field | Type | Description |
| --- | --- | --- |
| `schema` | string | 固定為 `rrkal_displaytools.canvas_preview.v1`。 |
| `mode` | string | `state`、`thumbnail` 或 `live_file_stream`。 |
| `renderer_thumbnail_path` | string or null | 可選的 renderer PNG 相對路徑，例如 `state/showcase/quick_smoke.png` 或 `state/renderer_preview_frame.png`。`thumbnail` 載入時若不存在，Qt 會 fallback 到最近的 `state/showcase/*.png`；`live_file_stream` 會等待 renderer 寫出 live preview frame。 |
| `preview_frame_path` | string or null | live preview renderer frame 的預設本機路徑，目前為 `state/renderer_preview_frame.png`。 |
| `preview_frame_interval_s` | number | live preview file stream 的建議寫入間隔秒數，目前 Qt 預設為 `0.75`。 |
| `boundary_emphasis_target_mode` | string | Canvas Preview 顯示的 Boundary emphasis target mode。 |
| `boundary_emphasis_target_layer` | string or null | Canvas Preview 顯示的解析後 target layer。 |
| `boundary_emphasis_target_alignment` | string | Canvas Preview provenance 中保存的 target alignment id。 |
| `boundary_emphasis_target_alignment_label` | string | Canvas Preview 顯示的人類可讀 target alignment。 |
| `renderer_sync` | string | `state` 為 UI-only preview；`thumbnail` 為 static renderer output contract；`live_file_stream` 為 file-based live renderer frame stream。 |

## `timeline_export`

可選。此欄位保存 Timeline dock 的 renderer export options，讓研究者可在 profile / launch packet 中重現「是否在下次 renderer launch 輸出動畫」與輸出格式。它只準備 renderer CLI flags；實際 PNG/GIF/MP4 寫檔由 renderer 負責，資料 discovery/download/cache governance 仍屬 RRKAL。

| Field | Type | Description |
| --- | --- | --- |
| `schema` | string | 固定為 `rrkal_displaytools.timeline_export_options.v1`。 |
| `enabled` | boolean | 是否在 renderer launch 時加入 Timeline export flags。 |
| `export_dir` | string | 匯出資料夾，預設建議位於 `state/timeline_exports`。 |
| `frame_count` | integer | 匯出 frame 數，必須大於 0。 |
| `fps` | number | 匯出 FPS，必須大於 0。 |
| `manifest_file` | string | Timeline animation manifest 路徑。 |
| `gif_enabled` | boolean | 是否同時要求 `--timeline-export-gif`。 |
| `gif_file` | string | GIF fallback 輸出路徑。 |
| `mp4_enabled` | boolean | 是否同時要求 `--timeline-export-mp4`。 |
| `mp4_file` | string | MP4 video 輸出路徑。 |
| `applies` | array | 目前包含 Qt/No-GUI export controls 與 renderer Timeline export CLI。 |
| `boundary` | string | 明確標示此欄位不負責 RRKAL data governance。 |

## `timeline_keyframes`

可選。Timeline keyframes 是 Qt-first 展示與 renderer handoff 的離散狀態序列。每個 keyframe 可包含：

| Field | Type | Description |
| --- | --- | --- |
| `schema` | string | 固定為 `rrkal_displaytools.timeline_keyframe.v1`。 |
| `id` | string | Keyframe id，例如 `kf_001`。 |
| `style_profile` | string | Keyframe 對應的 renderer style。 |
| `renderer` | object | style/topo/data/尺寸等 renderer launch state。 |
| `ocean_material` | object | wave strength、roughness、foam scalar controls。 |
| `camera` | object | yaw、pitch、zoom；renderer 可做 camera keyframe/interpolation handoff。 |
| `selected_layer` | string or null | Keyframe 當下 active layer。 |
| `layer_stack_snapshot` | object | visibility、lock、opacity、blend、selected layer snapshot。 |
| `pins` | array | Keyframe 當下 Pin 清單，含 coordinate source metadata。 |
| `boundary_highlight` | object | Keyframe 當下 renderer boundary highlight mask state。 |
| `boundary_emphasis_control` | object | Keyframe 當下 Boundary emphasis target/color/contrast/opacity/gamma/breathing UI state。 |

Timeline playback plan 目前把 style、layer visibility/blend、pins、boundary highlight、boundary emphasis control 視為 discrete keyframe fields；ocean material、camera 與 layer opacity 有獨立 interpolation/handoff contract。

## `profile_ui_state_replay`

此欄位是 profile / launch packet / renderer capability / handoff 的覆蓋摘要，用來告訴跨機器使用者哪些 UI 狀態已可透過 profile 或 Timeline keyframes 保存與復現。它不是使用者必填 profile 欄位，也不負責 RRKAL dataset discovery、download、import、cache governance 或 authoritative geospatial identity。

| Field | Type | Description |
| --- | --- | --- |
| `schema` | string | 固定為 `rrkal_displaytools.profile_ui_state_replay.v1`。 |
| `status` | string | 目前為 `ready`，表示覆蓋摘要可由 Qt、launch packet、renderer capabilities 與 handoff inspection 讀取。 |
| `saved_state_groups` | array | 已納入 portable UI/profile replay 的狀態群組，例如 `renderer_config`、`selected_layer`、`layer_stack_ui`、`pins`、`boundary_highlight`、`boundary_emphasis_control`、`canvas_preview`、`timeline_keyframes`、`timeline_export_options`。 |
| `saved_state_group_count` | integer | `saved_state_groups` 的數量。 |
| `replay_surfaces` | array | 可讀取或復現這些狀態的入口，目前包含 Qt save/load profile、Qt startup `--profile` / `--template`、Qt Inspect actions（Qt `Inspect:` buttons）、No-GUI launch packet、renderer first-keyframe apply、research provenance summary。 |
| `replay_surface_count` | integer | `replay_surfaces` 的數量。 |
| `qt_inspector_action_ids` | array | Qt `Inspect:` action IDs，例如 `profile_replay`、`timeline`、`clone_ready`、`layer_matrix`、`layer_runtime`、`layer_pick`、`canvas_state`、`cursor_geo`、`boundary_json`。 |
| `qt_inspector_action_labels` | array | Qt `Inspect:` action 顯示文字，例如 `Inspect: Profile replay`、`Inspect: Boundary JSON`。 |
| `qt_inspector_action_count` | integer | Qt `Inspect:` action 數量。 |
| `qt_inspector_action_groups` | array | Qt `Inspect:` action 分組，目前包含 `replay_contracts`、`renderer_ports`、`research_interaction`。 |
| `qt_inspector_group_count` | integer | Qt `Inspect:` action 分組數量。 |
| `qt_surface` | string | Qt 顯示入口，目前為 Layers dock `profileUiStateReplay` label。 |
| `launch_packet_fields` | array | No-GUI launch packet 中與 replay 覆蓋相關的欄位。 |
| `renderer_capability_field` | string | Renderer capability discovery 中的欄位名稱。 |
| `handoff_field` | string | `scripts\inspect_handoff.ps1` 輸出的欄位名稱。 |
| `summary_text` | string | 給 handoff / UI 顯示的簡短摘要。 |
| `boundary` | string | 明確標示此契約只描述 portable UI/profile state，不代表 RRKAL data governance 或 authoritative geospatial identity 已完成。 |

## Handoff rules

- Repo-shared templates live in `profiles/` and are committed.
- User/operator saved profiles live in `state/ui_profiles/` and are ignored.
- Launch packets live in `state/showcase/` and are ignored.
- RRKAL 若未來產生 displaytools profiles，應寫入此 schema shape，而不是直接控制 renderer internals。

## Qt Inspect visual review group

- `profile_ui_state_replay.qt_inspector_action_ids` now includes `renderer_thumbnail` and `live_preview`.
- `profile_ui_state_replay.qt_inspector_action_groups` now includes `visual_review` for renderer pixel inspection surfaces.
- `Inspect: Renderer thumbnail` opens the latest static renderer PNG when present.
- `Inspect: Live preview` switches the Canvas Preview to the file-based renderer preview frame stream.
- This group is UI replay metadata only; it does not imply data discovery, download, import, or cache governance.
