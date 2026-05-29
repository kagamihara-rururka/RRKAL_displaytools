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
| `layer_stack_ui` | object | optional | Qt layer stack 的 UI-only state。 |
| `tool_state` | object | optional | Qt tool palette 的 UI-only state。 |
| `pins` | array | optional | 科研標記清單。 |

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
- `ocean_material`
- `terrain_contours`
- `scale_bar`
- `vehicle_icons`

## `layer_stack_ui`

可選。若存在，應包含上述 layer stack key。每個 layer object 目前支援：

| Field | Type | Description |
| --- | --- | --- |
| `locked` | boolean | UI-only lock state，renderer sync 尚未接。 |
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
| `placement` | string | 目前通常是 `manual_lat_lon`，代表以手動經緯度建立；地球點擊定位後端尚未接。 |

目前 `tool_state` 不會直接改 renderer。Brush / Mask 暫不納入本輪 UI；Select 用於指定 active layer，Pin 用於先保存科研標記意圖，後續再接 canvas/globe hit-test。

## `pins`

可選。此欄位保存科研標記清單，適合記錄觀測點、採樣站、異常點、參考點與事件。若 `selected_pin_id` 存在，必須對應到此清單中的其中一個 `id`，Qt 會用它回復 Pin list 選取狀態並回填 Pin 編輯欄位。

Renderer overlay 接上後，Pin 不應是螢幕固定標籤，而應是 geodetic surface anchor：每個 frame 由 latitude/longitude 投影到球面，套用地球旋轉與 camera/view transform，再用 horizon/depth occlusion 判斷是否被地球背面或地形/海面遮蔽。

目前共用投影 hook 位於 `pin_projection.py`。它已能計算 `screen_x`、`screen_y`、`view_z`、`visible` 與 `occlusion`，先覆蓋跟隨地球旋轉與背面 horizon clipping。Renderer 已可透過 `--pin-file` 或 `--pin-json` 接收 Pins 並畫出可見 marker；若 payload 包含 `selected_pin_id`，renderer 會以高亮外圈標示該 Pin。Marker 顏色會依 `style_profile` 套用 scientific、nautical、tactical 或 parchment palette；label 目前使用簡單四象限候選位置與碰撞避讓，並支援 auto / selected / priority / hidden 顯示模式。後續再以 globe mask/depth buffer refine 地形或海面遮蔽。

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
| `placement` | string | 目前為 `manual_lat_lon`；後續會加入滑鼠位置反推經緯度的 `cursor_lat_lon` 流程。 |

## Handoff rules

- Repo-shared templates live in `profiles/` and are committed.
- User/operator saved profiles live in `state/ui_profiles/` and are ignored.
- Launch packets live in `state/showcase/` and are ignored.
- RRKAL 若未來產生 displaytools profiles，應寫入此 schema shape，而不是直接控制 renderer internals。
