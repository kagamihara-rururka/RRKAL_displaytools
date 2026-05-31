# Display Shell / Canvas / Render Matrix Roadmap

## 定位

`RRKAL_displaytools` 不應被鎖死為單一地球或球體 renderer。地球仍是目前最重要的 runtime canvas，但專案邊界應逐步整理為：

```text
DisplayShell
  -> Canvas System
  -> Layer System
  -> Render Matrix
  -> Renderer Adapter
```

## 第一階段範圍

- 保留現有 Earth / globe renderer 為主要 runtime。
- 先建立 `display_core` 合約，不急著支援所有圖表。
- 第一個非地球證明目標是最小 `TimeSeriesCanvas` contract。
- Render Matrix 使用 decorator registry 思路，避免 layer/canvas/backend 增加後出現大量 `if / elif`。

## 邊界

- `display_core` 不 import Matplotlib、Plotly、Graphviz、PyVista、Qt 或 Taichi。
- Layer 是語意模型，不是 Plotly trace、Matplotlib artist 或 Taichi buffer。
- Renderer adapter 才擁有具體繪圖套件與輸出格式。
- EarthCanvas 抽出前，現有 monolith globe path 不被替換。

## 第一批 contract

- `LayerModel`
- `ViewModel`
- `CanvasDescriptor`
- `build_canvas_registry_packet`
- `build_sample_view_models_packet`
- `RendererEntry`
- `register_renderer`
- `lookup_renderers`
- `build_display_shell_capability_packet`

## 目前 canvas registry

- `EarthCanvas`: 現有 globe runtime 的未來邊界，座標模型是 globe / latitude / longitude / altitude。
- `TimeSeriesCanvas`: 第一個非地球 contract，座標模型是 time x numeric y，目前不啟用 runtime renderer。

## 最小 ViewModel samples

- `rrkal_displaytools_earth_view_sample`: `earth` canvas，包含 terrain 與 research annotation layer。
- `rrkal_displaytools_time_series_view_sample`: `time_series` canvas，包含 numeric series 與 event marker layer。
- 兩者都使用同一個公式：`ViewModel = Canvas + Layer Stack + Renderer Hint + Output Format`。

## 後續執行順序

1. 先穩住目前 render-plan composition seams。
2. 把現有 globe renderer 邊界標成 `EarthCanvas`。
3. 新增最小 `TimeSeriesCanvas`，只證明 canvas switch contract，不追求完整金融/科學繪圖能力。
4. 再把 renderer adapters 分批註冊進 Render Matrix。
