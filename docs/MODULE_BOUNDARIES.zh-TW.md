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

目前實際落地的第一個 renderer seam 是 `render_core/render_plan.py`，並新增 `render_core/render_plan_performance.py` 收斂 clone-first performance handoff contract。

`render_core/render_plan.py` 負責：

- alpha compose / alpha blend / transparent compose 這類無 UI 狀態的像素合成 helper。
- render-plan 資料契約組包：runtime snapshot、composition steps、compose queue packet、compiled plan packet、reused compiled plan refresh。
- runtime snapshot builder ownership 已指向 `render_core.render_plan.build_layer_render_plan_runtime_snapshot`；controller wrapper 只保留為 visible layers / dirty flags / selected target 的 runtime fact collector。
- composition step builder ownership 已指向 `render_core.render_plan.build_layer_render_plan_composition_steps`；controller wrapper 只保留為 boundary scalar input collector。
- composition apply input selector 已指向 `render_core.render_plan.select_layer_render_plan_composition_input`；core 只決定 `compose_queue` 優先、`composition_steps` fallback，實際 ndarray compose 仍由 controller 執行。
- compile path 會先建立 composition steps，再把同一份 steps 傳入 runtime snapshot，避免在同一次 plan compilation 中重算 step list。
- render-plan 純決策：cache key、cache invalidation reasons/scope、batch decisions、apply path、execution summary、execution phases。
- cache key / invalidation / batch / apply / execution / phase contract / bottleneck 這些純決策已不再保留 controller wrapper；controller 只收集 style、boundary、opacity、blend、cached-plan 這些 scalar inputs 後直接呼叫 core helper。
- phase timing runtime packet 與 bottleneck recommendation 的資料包組裝；runtime path 只收集 scalar timing values 後直接呼叫 core helper。
- output metadata 的 `layer_render_plan_summary` 摘要契約組包；實際 metadata 寫檔仍留在 controller。
- single-pass preflight contract 組包；在 parity smoke、實測 phase timing、人工視覺審查通過前，不啟用 runtime single-pass。
- adapter boundary contract 組包；先明確 controller-to-core payload 與 forbidden responsibilities，再移動 overlay runtime state。
- adapter payload summary 組包；只輸出可序列化摘要，不持有 overlay ndarray。
- adapter payload 組包；`HybridRenderController.compile_layer_render_plan` 先建立 normalized controller-to-core payload，再交給 compiled/reused plan packet builder。
- adapter payload completeness contract；payload 轉成 primary implementation 前必須先通過 required-fields gate。
- from-payload compiled/reused builder wrapper；controller 開始以 normalized payload 作為主要 contract，舊長參數 builder 暫留相容。
- compose queue classifier：只根據 controller 提供的 step runtime state 分類 queue / skipped steps。
- step runtime state packet builder：controller 提供 visible / overlay_present / overlay_transparent 這些 scalar facts，core 統一產生 queue classifier 的 state packet。
- compose queue packet-from-states orchestrator：capability / launch packet / handoff helper ownership 已指向 `render_core.render_plan.build_layer_render_plan_compose_queue_packet_from_states`；controller wrapper 只保留為 overlay lookup / visibility / transparency runtime fact collector。
- compose runs / parity contract helper ownership：殘留的 controller wrapper 已移除，capability / launch packet / handoff helper 名稱直接指向 `render_core.render_plan`。
- `layer_render_plan_performance_packet` 由 `render_core/render_plan_performance.py` 單一提供；renderer monolith、Qt panel、no-GUI launch exporter 只 import，不再維護本地鏡像。

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
