# Profile Schema

最後更新：2026-05-29

## 目的

`profiles/*.json` 是 `RRKAL_displaytools` 的 Qt panel 啟動配置模板。它們用來描述 renderer launch state：style、地形來源、資料模式、解析度、海洋材質參數與圖層開關。

這不是 RRKAL 的 dataset manifest、install registry、cache manifest 或授權治理資料。RRKAL 仍負責資料來源、下載、匯入、版本、cache/manifest lifecycle；displaytools profile 只負責「如何啟動視覺化」。

## Schema id

```text
rrkal_displaytools.qt_panel_profile.v1
```

## Top-level fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | optional | UI 顯示名稱。沒有時 Qt panel 會退回檔名。 |
| `description` | string | optional | 人類可讀的用途說明。 |
| `schema` | string | required | Profile schema id。 |
| `renderer` | object | required | Renderer 啟動與資料模式設定。 |
| `ocean_material` | object | required | 海洋材質控制參數。 |
| `layers` | object | required | 圖層 boolean 開關。 |

## `renderer`

| Field | Example | Description |
| --- | --- | --- |
| `style_profile` | `scientific` | 對應 renderer `--style-profile`。 |
| `ui_backend` | `qt` | 對應 renderer `--ui`。 |
| `topo_source` | `gebco` | `gebco` 或 `synthetic`。 |
| `data_mode` | `static` | `static`、`realtime` 或 `timeseries`。 |
| `width` | `1280` | 視窗/輸出寬度，保存為字串以直接映射 CLI。 |
| `height` | `720` | 視窗/輸出高度，保存為字串以直接映射 CLI。 |
| `topo_step` | `48` | 地形取樣 step。 |
| `taichi_arch` | `gpu` | Taichi backend 偏好。 |

## `ocean_material`

| Field | Example | Description |
| --- | --- | --- |
| `wave_strength` | `0.22` | 對應 `--ocean-wave-strength`。 |
| `roughness` | `0.28` | 對應 `--ocean-roughness`。 |
| `foam` | `0.12` | 對應 `--ocean-foam`。 |

## `layers`

目前 Qt panel 支援：

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

## Handoff rules

- Repo-shared templates live in `profiles/` and are committed.
- User/operator saved profiles live in `state/ui_profiles/` and are ignored.
- Launch packets live in `state/showcase/` and are ignored.
- If RRKAL later generates displaytools profiles, it should write this schema shape rather than controlling renderer internals directly.
