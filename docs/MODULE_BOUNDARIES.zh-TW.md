# RRKAL_displaytools 模組邊界

日期：2026-05-31

## 定位

`RRKAL_displaytools` 是科研視覺化與 renderer 操作工作台。

它負責：

- Qt-first 操作介面、圖層控制、profile/template、launch packet。
- Taichi/VisPy renderer 的視覺化、材質、圖層合成、選取與回寫狀態。
- `state/renderer_layer_runtime_state.json`、`state/renderer_layer_runtime_ack.json`、`state/renderer_layer_pick_state.json` 這類 renderer bridge。
- 讓科研者能檢查 layer runtime、pick evidence、boundary highlight、pin/traffic/hydrology/boundary interaction。

它不負責：

- dataset discovery。
- download/import/install registry。
- API key、provider registry、cache governance。
- RRKAL asset manifest 的來源治理。

上述資料治理仍由 RRKAL / `APIkeys_collection` 負責，displaytools 只接收已決定的 renderer input、manifest reference 或 launch state。

## 建議拆分順序

1. `ui_qt/`

   - `rrkal_displaytools_qt_panel.py` 的 Qt control panel。
   - profile/template/load/save。
   - launch packet export。
   - layer runtime/pick JSON inspector。

2. `renderer_core/`

   - Taichi globe renderer。
   - ocean material shader controls。
   - frame composition、blend mode、post-process。

3. `vector_overlays/`

   - `GeoVectorLineOverlay`。
   - hydrology/boundary line rendering。
   - closed-ring fill preview。
   - vector hit testing。

4. `interaction_bridge/`

   - layer runtime state reader/writer。
   - selected-layer semantic target。
   - selected-layer scoped picking。
   - pin/layer pick state JSON。

5. `style_profiles/`

   - scientific、nautical、parchment、tactical profile resolution。
   - renderer capability/profile template packets。

6. `contracts/`

   - capability packet schema。
   - launch packet schema。
   - profile schema。
   - closed-loop status packet。
   - RRKAL handoff notes。

## 解耦原則

- Renderer modules may consume local files, URLs, or arrays only after RRKAL/provider side has decided they are valid renderer inputs.
- UI modules may display cache paths and manifest references, but must not create discovery/download policies.
- Bridge JSON should stay small, inspectable, and reproducible.
- Any future extraction should keep one shadow-mode path until smoke and one manual launch path both pass.

## 已落地的 render-plan seam

目前實際落地的第一個 renderer seam 是 `render_core/render_plan.py`。

`render_core/render_plan.py` 負責：

- alpha compose / alpha blend / transparent compose 這類無 UI 狀態的像素合成 helper。
- render-plan 資料契約組包：runtime snapshot、composition steps、compose queue packet、compiled plan packet、reused compiled plan refresh。
- render-plan 純決策：cache key、cache invalidation reasons/scope、batch decisions、apply path、execution summary、execution phases。
- phase timing 與 bottleneck recommendation 的資料包組裝。
- compose queue classifier：只根據 controller 提供的 step runtime state 分類 queue / skipped steps。

`HybridRenderController` 仍負責：

- 收集 renderer runtime state，例如 frame index、visible layers、dirty flags、selected semantic target。
- 讀取 overlay / ndarray 物件，判斷 visibility、missing overlay、transparent overlay。
- 維持 cache-key match 判斷與 controller 生命週期狀態。
- 實際 render loop、Taichi/NumPy frame mutation、output metadata 寫檔。

後續解耦規則：

- 不要把 `np.ndarray` overlay 物件、Qt widget 或檔案寫入流程直接搬進 `render_core/render_plan.py`。
- 若要繼續拆 compose queue，先擴充 controller-to-core adapter payload，再讓 core 做純資料分類。
- 若要啟用合併渲染或 single-pass candidate，先保留 smoke-gated parity contract，不直接替換 runtime path。

## 目前閉環狀態

- Layer visibility/opacity/blend/lock guard runtime bridge：closed.
- Selected-layer semantic target：closed.
- Selected-layer picking for Pin, traffic, boundary line, hydrology line：closed.
- Boundary closed-ring fill preview：partial closed loop.
- Qt Canvas Preview state / static thumbnail / file-based live renderer frame：closed.
- Full territory feature identity and open-line area inference：pending.
- Low-latency IPC/GPU texture renderer preview：pending.
