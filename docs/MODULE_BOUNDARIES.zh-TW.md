# RRKAL_displaytools 模組邊界

日期：2026-05-29

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
   - RRKAL handoff notes。

## 解耦原則

- Renderer modules may consume local files, URLs, or arrays only after RRKAL/provider side has decided they are valid renderer inputs.
- UI modules may display cache paths and manifest references, but must not create discovery/download policies.
- Bridge JSON should stay small, inspectable, and reproducible.
- Any future extraction should keep one shadow-mode path until smoke and one manual launch path both pass.

## 目前閉環狀態

- Layer visibility/opacity/blend/lock guard runtime bridge：closed.
- Selected-layer semantic target：closed.
- Selected-layer picking for Pin, traffic, boundary line, hydrology line：closed.
- Boundary closed-ring fill preview：partial closed loop.
- Full territory feature identity and open-line area inference：pending.
- Embedded renderer thumbnail in Qt panel：pending.
