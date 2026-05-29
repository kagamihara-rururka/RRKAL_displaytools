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
| `layer_stack_ui` | object | optional | Qt layer stack 的 UI-only state。 |

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

## Handoff rules

- Repo-shared templates live in `profiles/` and are committed.
- User/operator saved profiles live in `state/ui_profiles/` and are ignored.
- Launch packets live in `state/showcase/` and are ignored.
- RRKAL 若未來產生 displaytools profiles，應寫入此 schema shape，而不是直接控制 renderer internals。
