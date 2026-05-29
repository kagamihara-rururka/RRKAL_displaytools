# RRKAL_displaytools 產品定位

最後更新：2026-05-29

## 一句話

`RRKAL_displaytools` 是 RRKAL 的視覺化與 renderer 消費層，負責把 RRKAL 納管後的資料、manifest、tile/cache contract 轉成可互動或可展示的畫面。

## 與 RRKAL 的分工

RRKAL / `APIkeys_collection` 的定位是 RuRuKa Asset Launcher：資料集與爬蟲資產的 discovery、下載、安裝、版本、修復、manifest、install registry、cache/tile 管理入口。

`RRKAL_displaytools` 不取代 launcher，也不負責 API key、crawler、provider catalog、下載器、安裝/解除安裝、資料修復或授權治理。這些資料主權仍留在 RRKAL。

本 repo 的任務是把「已被 RRKAL 治理或可被 RRKAL 治理的資料」轉成視覺輸出：

- Taichi globe / bathymetry renderer prototype。
- Hydrology、coastline、boundary、bathymetry 等 globe overlay 顯示契約。
- LOD hook、tile/cache readiness、renderer invalidation diagnostics。
- Ocean material、海況資料 port、style profile / parchment / tactical renderer entry。
- 未來可抽成 Taichi / Unreal / Cesium / chart frontend 的 renderer-facing boundary。

## 對接位置

目標資料流：

```text
RRKAL source / dataset registry
-> download / import / install registry
-> manifest / tile cache / renderer bridge asset
-> RRKAL_displaytools renderer contract
-> Taichi globe or other visualization frontend
```

這表示 displaytools 應優先定義「怎麼消費 RRKAL 產出的資料契約」，而不是把資料來源規則寫進 renderer。

## MVP 邊界

目前優先：

- 收斂 `taichi_global_bathymetry.py` 的 hydrology layer 與 LOD hook。
- 補 Taichi ocean material controls 與海況資料 port contract。
- 建立 `scientific`、`parchment`、`tactical` 等 style profile renderer 入口。
- 標出可解耦的模組邊界，讓 monolith 後續能拆成 renderer core、data contract、style profile、diagnostics、cache/material modules。

暫不承諾：

- 實作 RRKAL crawler、provider catalog、download plan 或 install registry。
- 大規模資料清洗或授權治理。
- 完整 Unreal shader/material 系統。
- 完整全球海洋物理模擬。
- 把所有 renderer 直接重寫成 plugin marketplace。

## 設計原則

- 資料主權在 RRKAL；renderer 只消費明確契約。
- Renderer bridge asset 也應可被 RRKAL 管理，例如 tile/cache/mesh/chart index/material preset。
- 視覺化可以快速迭代，但不能假裝資料治理已完成。
- Monolith 內新增 contract 時，要同步標記未來模組邊界。
- 每輪開發結束後更新文檔與日誌，commit 後才進入下一輪。
