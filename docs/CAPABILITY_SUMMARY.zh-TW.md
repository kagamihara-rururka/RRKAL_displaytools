# Capability Summary

最後更新：2026-05-29

## 目前已有功能

### Qt-first operator UI

- `rrkal_displaytools_qt_panel.py` 提供 Qt/PyQt6 圖層控制面板。
- 產品定位是科研視覺化工作台：UI 借鑑 Photoshop 的面板精神，但優先服務科研者對圖層狀態、資料來源、profile 可重現性、manifest/launch packet 可追蹤性的需求。
- 模組邊界與後續解耦順序記錄於 `docs/MODULE_BOUNDARIES.zh-TW.md`；displaytools 只負責視覺化/UI/renderer bridge，不接手 RRKAL 的資料 discovery/download/cache governance。
- 跨機器 clone / smoke / Qt 啟動步驟記錄於 `docs/QUICKSTART_CLONE.zh-TW.md`；`scripts/run_qt_panel.ps1` 是建議啟動入口，會優先使用 repo `.venv`，也支援 `-SmokeFirst` 與 `-HandoffFirst`。
- 前端方向採 Photoshop-inspired workspace：menu bar、左側 Tools dock、右側 dockable Layers/Properties/Navigator/History/Timeline panels、工具選項、Looks/模板、圖層、屬性、中央預覽、動作分區。
- 可控制 style profile、UI backend、topography source、data mode、resolution、Taichi arch。
- 可控制 lake、river、border、territorial sea、EEZ、high seas、aircraft、Pin marker、ocean material、terrain contours、scale bar、vehicle icons 等圖層。
- 支援水文、海域、交通、視覺輔助四組一鍵切換，並可對目前選取圖層執行 Solo / restore visibility。
- Layers 面板已具備 Photoshop-like layer stack 雛形：active layer selection、row search/filter、Hydro/Maritime/Traffic/Aids/All focus presets、Select first filtered layer、Reveal selected layer row、Hydro/Sea/Traffic/Aids group collapse/expand、visibility、lock、opacity、blend mode、UI-only state reset 與 layer stack undo snapshots。Visibility 已接 renderer flags，並支援 Solo selected layer / restore previous visibility snapshot，方便科研者快速隔離水文、海域、交通或輔助圖層；layer filter 與 layer group collapse 可用 layer key/name/flag、科研群組 preset 或收合群組快速定位圖層，並會寫入 profile / launch packet / provenance，但不改變 renderer layer state。Qt lock 會停用 locked layer 的 visibility checkbox，並讓 group toggle、Solo、restore、selected-layer visibility toggle 與 layer undo 跳過或還原正確 layer UI state。Qt 會寫出 `state/renderer_layer_runtime_state.json`，renderer 可用 `--layer-runtime-state-file` 讀取並即時套用 visibility 與支援圖層的 opacity 變更，也可用 `--layer-runtime-ack-file` 寫回 `state/renderer_layer_runtime_ack.json` 作為接收回執；renderer 端會把 Qt layer keys 對應到 renderer layer IDs，並跳過 runtime state 中 `locked=true` 圖層的 visibility/opacity/支援 overlay blend 變更，ack 會回報 `changed_opacity_layers`、`skipped_locked_layers`、`layer_opacity`、selected renderer target 與 alias map。Layers 面板會顯示 layer runtime bridge 的 selected layer、renderer target、visible count、last write、renderer ack、opacity changed count 與 skipped locked count，也可把目前 runtime JSON 與 layer pick JSON 顯示到中央文字區；History 面板會記錄最近 layer runtime 摘要、layer undo snapshot 與 pick 摘要變更，provenance 也會保留最近幾筆 layer runtime history、renderer ack 與 layer pick state。selected layer semantic target 已成為 renderer ack 中可追蹤的語意目標，renderer 滑鼠點擊會依目前 selected layer 限定 Pin、交通點、boundary 線段或 hydrology 線段 picking，並寫回 `state/renderer_layer_pick_state.json` 讓 Qt 面板顯示；若來源 GeoJSON 有 properties，pick state 會帶 source-property feature identity，並優先辨識 Natural Earth / Marine Regions 常見名稱、主權、ISO 與 MRGID 欄位，Qt layer pick label 也會直接顯示 feature label；後續剩下 authoritative polygon territory identity / open-line area inference。
- Layer group diagnostics 會在 Layers 狀態列、profile、launch packet、provenance 與 No-GUI export 中記錄各 group 可見/總 row 數、active layer 所屬 group，以及 active layer 是否被收合群組藏起來，避免研究者誤以為 renderer layer 已被關閉。
- Renderer layer runtime opacity 目前已落地到 hydrology/boundary/scale/contours、ADS-B aircraft overlay alpha、Pin marker overlay alpha 與 vehicle icon overlay alpha。
- Timeline playback/export 已新增 `rrkal_displaytools.timeline_layer_opacity_interpolation.v1`、`rrkal_displaytools.timeline_layer_discrete_hold.v1` 與 `rrkal_displaytools.timeline_export_options.v1`；前者在 active/next keyframe 間插值 layer opacity，後者明確持有 active-keyframe layer visibility / blend mode。Timeline export 可在 Qt Timeline dock 設定 export-on-launch、output directory、frame count、FPS、GIF fallback 與 optional MP4 video；MP4 依賴 `imageio[ffmpeg]`。True blend crossfade 與 visibility fade 仍 pending。
- Renderer layer runtime blend mode 目前已對 lake、river、borders、territorial sea、EEZ、high seas、ADS-B aircraft、Pin marker 與 vehicle icon overlay 支援 Normal、Screen、Multiply、Overlay、Soft Light。
- Renderer layer runtime visibility 目前已同步 hydrology/boundary/aircraft/pin/vehicle icons/scale/contours/grid/stars/ocean material 的對應 renderer flags；這些基礎視覺圖層可透過 runtime bridge 改變而不必重啟。
- Layer capability matrix 已建立為 `rrkal_displaytools.layer_capability_matrix.v1`，會列出每個 Qt layer 的 renderer target、visibility/opacity/blend/selected-layer pick 是否 live、live control counts 與 selected layer capabilities。Qt Properties 會直接顯示選取圖層能力、最近 renderer ack runtime status、`rrkal_displaytools.layer_runtime_evidence_summary.v1` 可讀摘要、`Runtime warnings`、`Renderer summary`、`Renderer detail`、`Renderer hints`、`Runtime context`、`Territory identity` 與 RRKAL identity source ref 狀態，Layers dock 可顯示完整 JSON，且每列已有帶色彩語意的 `Runtime` badge 顯示 `no_ack` / `ok` / `target` / `changed` / `locked` / `error`；launch packet、No-GUI export、renderer capabilities、handoff inspection 與 smoke gate 也會驗證此 contract。矩陣內含 `rrkal_displaytools.layer_runtime_evidence.v1`、`rrkal_displaytools.layer_runtime_evidence_summary.v1`、`rrkal_displaytools.layer_runtime_badge_summary.v1`、`rrkal_displaytools.layer_runtime_warning_list.v1`、`rrkal_displaytools.layer_runtime_interaction_context.v1`、`rrkal_displaytools.layer_territory_identity_context.v1`、`rrkal_displaytools.layer_authoritative_identity_source.v1`、`rrkal_displaytools.layer_renderer_diagnostics_summary.v1`、`rrkal_displaytools.layer_renderer_diagnostics_detail.v1`、`rrkal_displaytools.layer_renderer_diagnostics_remediation.v1` 與 `rrkal_displaytools.layer_runtime_status_legend.v1`，Qt runtime 會摘要 changed visibility/opacity/blend、skipped locked layers、selected renderer target、event/error/frame，並把 badge counts / selected-layer badge / noteworthy layers / researcher-facing warnings / pick context / source-property feature identity / authoritative identity pending boundary / RRKAL reference-only source handoff / renderer diagnostics summary/detail/remediation hints 寫入可複製 research provenance；No-GUI 與 static renderer capability discovery 會明確標示 runtime evidence 或 live pick context unavailable。
- Qt layer stack metadata 會在 profile / launch packet / runtime bridge 中寫入每個 layer 的 `renderer_sync` 摘要，區分 visibility / opacity / blend live 狀態；runtime bridge 另會寫出 selected renderer target 供 renderer ack/provenance 追蹤。
- `rrkal_displaytools.layer_operator_shortcuts.v1` documents Qt-first Photoshop-like layer operations: select, visibility, lock, opacity, blend, solo, restore, undo, reset and diagnostics actions. The contract is exposed through Qt launch/provenance packets, No-GUI launch packets, renderer capabilities and handoff inspection, and smoke gates verify solo/restore/undo actions plus keyboard shortcut metadata. Qt installs `Ctrl+Alt+V/L/S/R/Z/0/D` shortcuts for selected-layer visibility, lock, solo, restore, undo, reset and diagnostics.
- `rrkal_displaytools.layer_operator_groups.v1` groups those operations into Selection, Edit state, Isolation, History and Diagnostics workflows. Qt Layers dock shows the group summary; Qt launch/provenance packets, No-GUI launch packets, renderer capabilities, handoff inspection, closed-loop evidence and smoke gates all expose the same grouping contract.
- `rrkal_displaytools.layer_selection_tool.v1` unifies Qt row selection, first-filtered selection, reveal-selected-row and renderer `state/renderer_layer_pick_state.json` inspection into a smoke-gated scientific selection tool contract; brush/mask scope is explicitly excluded.
- `rrkal_displaytools.layer_research_workflow.v1` turns filter/group/selected-layer/runtime-warning/remediation state into a researcher-facing workflow contract and a Qt Layers dock status label, so dense layer stacks have a verifiable path from filtering to reproducible diagnostics.
- `rrkal_displaytools.boundary_emphasis_control.v1` adds the Qt-first territory/boundary emphasis control surface requested for country boundaries, territorial seas, EEZs and maritime boundaries. The dialog exposes RGB, contrast, opacity, gamma and breathing controls; launch packets, renderer capabilities, handoff and smoke track the UI contract, including boundary-layer row double-click entry and renderer bridge mapping through `rrkal_displaytools.boundary_highlight_mask.v1`; full polygon fill mask remains a backend refinement.
- `rrkal_displaytools.cursor_geodesy_readout.v1` exposes canvas mouse-position longitude/latitude readout for researchers. The Qt surface still gives an immediate guarded canvas preview estimate, while renderer-facing globe-disc raycast math is now smoke-gated through `cursor_geodesy.viewport_sphere_raycast` and recorded as `rrkal_displaytools.cursor_geodesy_raycast.v1`; The renderer cursor raycast state/ack contract now names `state/renderer_cursor_geodesy_state.json` and `state/renderer_cursor_geodesy_ack.json`; Taichi mouse-state writing remains the next backend integration step.
- `rrkal_displaytools.pin_projection.v1` verifies that research Pins are geodetic annotations projected every frame from the current globe camera and hidden behind the horizon when `view_z <= horizon_eps`; renderer depth/terrain refinement remains a later backend pass.
- `rrkal_displaytools.style_renderer_entries.v1` exposes scientific, nautical, parchment and tactical renderer entry contracts. Each entry records the `--style-profile <id>` CLI args, `profile.style_profile` field, portable-command support and renderer entrypoint; Qt launch/provenance packets, No-GUI launch packets, renderer capabilities, handoff inspection, closed-loop evidence and smoke gates verify parchment/tactical availability.
- `rrkal_displaytools.style_profile_renderer_routes.v1` turns those entries into explicit renderer routes with `py -3 taichi_global_bathymetry.py --style-profile <id>` portable commands, with parchment and tactical routes required by smoke and handoff inspection.
- `rrkal_displaytools.module_boundary_registry.v1` marks extraction seams for contracts, Qt UI, Taichi render core, ocean material, style profiles, overlays, RRKAL-owned data sources and diagnostics. It explicitly keeps Qt as primary UI, blocks Tk as primary UI, and keeps RRKAL data discovery/import/cache governance outside displaytools.
- `rrkal_displaytools.cross_machine_clone_readiness.v1` records the public repo URL, Windows setup doc, required first-run commands, launcher options including `-HandoffFirst`, smoke-before-push rule, Qt-first boundary and handoff inspection steps so another machine can verify clone/setup/run state through launch packets, renderer capabilities, handoff inspection and smoke gates.
- Qt Layers dock shows `Cross-machine clone readiness`, making clone/setup status visible beside profile/launch readiness instead of only inside JSON packets.
- `rrkal_displaytools.profile_launch_readiness.v1` summarizes cross-machine readiness for profile schema, built-in templates, launch packet export, portable command, renderer capability discovery, style renderer entries and layer operator workflow groups. Qt launch/provenance packets, No-GUI launch packets, renderer capabilities, handoff inspection, closed-loop evidence and smoke gates must all report readiness as `ready`.
- `rrkal_displaytools.profile_launch_readiness_ui.v1` makes that readiness visible in the Qt Layers dock as a `Profile/launch readiness` label, and the same UI surface is exposed through launch packets, renderer capabilities, handoff inspection, closed-loop evidence and smoke gates.
- `rrkal_displaytools.layer_visual_presets.v1` adds Qt Layers dock preset buttons for All context, Hydrology focus, Boundary focus and Annotation focus. Presets mutate existing layer visibility controls, reset visible layer opacity/blend to stable defaults, preserve locked layers, exclude Brush/Mask scope, and are verifiable through launch packets, renderer capabilities, handoff inspection, closed-loop evidence and smoke gates.
- `rrkal_displaytools.layer_visual_preset_runtime_feedback.v1` connects those presets to the existing renderer layer runtime ack bridge and shows a `Preset renderer ack` label in the Qt Layers dock. Launch packets, renderer capabilities, handoff inspection, closed-loop evidence and smoke gates verify the ack-file contract and reproducibility requirement.
- `rrkal_displaytools.hydrology_lod_readiness.v1` stabilizes the water/hydrology layer contract for `lake_layer` and `river_layer`, mapping them to renderer targets `lakes` and `rivers`, recording live visibility/opacity/blend/selected-layer-pick support, and marking the LOD hook boundary as `contract_ready`. Bathymetry/coastline context layers remain deferred to RRKAL-governed data/source work.
- `rrkal_displaytools.hydrology_lod_runtime_evidence.v1` connects Hydrology/LOD readiness to `state/renderer_layer_runtime_ack.json` and `state/renderer_layer_pick_state.json`, exposing runtime hydrology hits, selected-layer hydrology pick status and the Qt `Hydrology runtime evidence` label through launch packets, renderer capabilities, handoff inspection, closed-loop evidence and smoke gates.
- `rrkal_displaytools.ocean_material_control_port.v1` exposes the Qt Properties wave/roughness/foam controls, renderer flags, Taichi scalar uniforms and manual scalar sea-state port boundary. Displaytools only passes normalized scalar handoff fields; provider discovery, download, import and cache governance remain outside this repo.
- Properties 面板已接 active layer inspector，可查看目前選取圖層的 visibility、lock、opacity、blend mode、renderer target，以及最近 renderer runtime ack / layer pick 摘要，並可切換選取圖層 visibility 或重設選取圖層 UI state。
- Properties 面板已新增 `Boundary highlight` 疆域強調遮罩控制入口與 `Boundary identity` 摘要；國界、領海、EEZ、公海圖層列可雙擊打開控制對話框，設定 hover/selected 觸發、target layers、RGB 色彩、對比、半透明、gamma、feather 與呼吸特效。對話框、Properties 摘要與 `boundary_highlight.identity_status` 會明確標示 source-property feature identity 已 live，但 authoritative 疆域/EEZ identity 與 open-line area inference 仍 pending。此狀態已寫入 profile、launch packet、Canvas Preview 與 provenance；Qt 啟動 renderer 時會以 `--boundary-highlight-json` 傳入，renderer 會用 `--boundary-highlight-ack-file` 寫回 `state/renderer_boundary_highlight_ack.json`。Renderer 目前已用該 payload 控制 hover hit target layers、啟用狀態、outline/glow 顏色、contrast、gamma、alpha、feather 與 breathing speed；滑鼠移到國界/領海/EEZ/公海線段附近，或落在完整可見的閉合 ring 內，可看到線段/面域強調；閉合 ring 幾何會加上半透明 polygon fill preview，fill preview 會套用獨立的 gamma/contrast tone 控制，且 source GeoJSON properties 會進入 pick feature identity。Authoritative polygon territory identity 與開放線段面域推論仍是下一步。
- Qt profile save/load 已支援 selected layer 與 layer stack UI state，因此 active layer、lock、opacity、blend mode 可以隨本機 profile 保存與載入；既有 repo templates 仍相容。
- 左側 Tools dock 已新增科研導向 tool palette：Move、Select、Pin。Select 用於指定 active layer，並可在 Canvas Preview 以垂直 hit bands 點選目前可見圖層；Pin 用於科研標記，可保存 type、label、note、latitude、longitude，並加入 marker list。Pin list 已支援選取、欄位回填與 selected pin 狀態保存。Brush/Mask 暫不納入本輪 UI。`tool_state`、`pins` 與 `selected_pin_id` 會寫入 profile 與 launch packet。
- 支援啟動、停止、套用並重啟 renderer。
- 顯示 renderer PID、執行中狀態與 exit code。
- 中央 Canvas Preview 已可用 UI-only 方式顯示 style/topography/data mode、active tool、active layer、visible layer count、Select hit map 與 zoom；也可切到最近 `state/showcase/*.png` 的 renderer static thumbnail，thumbnail 模式下會自動輪詢並刷新最新 PNG。Qt 啟動 renderer 時會帶入 `--preview-frame-file state/renderer_preview_frame.png`，Canvas Preview 的 Live preview 模式會輪詢該 PNG，形成 file-based live renderer frame stream。Canvas preview mode、preview frame path 與 interval 會寫入 profile / launch packet / provenance；runtime PNG 只作本機狀態，不提交 Git。中央文字區也可顯示 renderer capabilities、layer manifest、launch packet 或 smoke 結果。
- Canvas Preview 已支援滑鼠位置的 UI-only 經緯度估算，使用 equirectangular canvas mapping，可一鍵填入 Pin 的 latitude/longitude，並顯示目前 selected pin 與 marker 摘要。 Renderer-facing cursor raycast helper is smoke-gated for center hit / outside-globe miss.
- 右側 `Provenance` dock 已提供科研可重現性摘要，可複製 JSON，內容包含 style/topo/data mode、active layer、active layer diagnostics、layer undo depth/capacity、session journal、document undo state、active tool、visible/locked layers、layer count 與 portable command line。
- 已新增 `pin_projection.py` 共用 hook：以 latitude/longitude 作為 geodetic surface anchor，依 renderer camera yaw/pitch/zoom 投影到 screen_x/screen_y，並以 horizon clipping 判斷背面遮蔽；renderer capabilities 會暴露此 Pin overlay contract。
- Renderer 已支援 `--pin-file`、`--pin-json`、`--pin-layer`、`--pin-size`、`--pin-horizon-eps`、`--pin-label-mode`、`--pin-label-min-priority`、`--pin-pick-radius`、`--pin-pick-state-file`、`--pin-input-ack-file`。Qt 若有 Pins，啟動 renderer 時會以 `--pin-json` 傳入，renderer 會每 frame 投影並只繪製可見 hemisphere 上的 Pin marker；`selected_pin_id` 會以 profile-aware 外圈高亮。Renderer 初始化後可寫回 `state/renderer_pin_input_ack.json`，記錄收到的 pin_count、selected_pin_id 與 selected pin 是否存在。Pin marker 已接 scientific、nautical、tactical、parchment style profiles，並具備基本 label box / leader line / collision avoidance。Qt Pin 已支援 `label_priority` 與 label visibility modes，renderer label placement 會先放 selected Pin，再依 priority 高低排序。Renderer 支援 Pin hover / click pick，點到 Pin 會更新 selected Pin highlight 與資訊面板，並可將 pick state 寫到 JSON bridge；外部 Qt control panel 會輪詢該 bridge，將 selected/cleared 事件同步回 Pin list、欄位與 provenance，並寫出 `state/qt_pin_pick_ack.json` 記錄 Qt 是否已同步該 renderer event。Pin Annotation 面板可直接顯示 renderer Pin input ack、最新 Pin pick JSON 與 Qt ack；History 面板會記錄最近 Pin pick 摘要，provenance 也會保留最新 Pin input ack、Pin pick payload、Qt ack 與最近幾筆 Pin pick history。Malformed `--pin-json` / `--pin-file` 會被 warning 後忽略，不再造成 renderer 閃退。
- Timeline dock 已可見，並支援 UI-only keyframe storage / restore / playback controls，可保存目前 style/material/layer/pin/boundary UI state 成 keyframe 清單、回套選取 keyframe，也可用 `Play UI preview` / `Next` 在 keyframes 間巡覽；keyframes 會隨 Qt profile save/load 保存，`timeline_state` 會進入 launch packet / provenance / no-GUI export，No-GUI exporter 也會摘要 profile 內的 `timeline_keyframes`。Qt 會寫出 `state/renderer_timeline_state.json`，renderer 啟動時可讀取並寫回 `state/renderer_timeline_ack.json`，確認收到 keyframe count 與 state schema。`timeline_playback_readiness` 會在 launch packet、runtime state、renderer ack 與 renderer capabilities 中明確標示 Qt preview playback、renderer ack、renderer discrete keyframe step playback、ocean/material interpolation 與 PNG/GIF/MP4 animation export 可用；`timeline_playback_plan` 會列出 ordered keyframes、segment count、可套用 scope 與 discrete step playback boundary；`timeline_segment_state` 會依 active step 暴露當前 keyframe segment 與 interpolatable/discrete fields；`timeline_active_step_state` 會暴露目前 requested/active keyframe index，作為 renderer startup step selection 的契約；`timeline_step_playback` 會回報 renderer step playback 支援、interval、current index 與 step count；`timeline_ocean_material_interpolation` 會回報 wave_strength、roughness、foam 的 active segment 線性插值；`timeline_export_options` 已進入 Qt profile / launch packet / runtime state / No-GUI export，Qt dock 可控制 export-on-launch、frames、FPS、GIF 與 MP4；`timeline_animation_export` 可透過 `--timeline-export-dir` 輸出 PNG frames 與 manifest，可透過 `--timeline-export-gif` 產生 animated GIF fallback，也可透過 `--timeline-export-mp4` 產生 MP4 video。`timeline_camera_keyframe` 已提供 camera yaw/pitch/zoom 的離散 keyframe contract，`timeline_camera_interpolation` 已提供 yaw/pitch/zoom segment interpolation, `timeline_layer_opacity_interpolation` layer opacity segment interpolation, and `timeline_layer_discrete_hold` active-keyframe visibility / blend mode hold。Renderer 啟動時可依 active step 契約套用 Timeline keyframe 的 style/material/layer/pin/boundary/camera state，playback active 時可按 interval 前進並在 segment 內平滑套用海洋材質與 camera；blend crossfade and visibility fade 仍 pending。History 面板已提供手動 document snapshot undo/redo 與 undo/redo depth 狀態列，可回復整個 Qt profile 狀態；profile apply、renderer preset、Timeline keyframe apply/clear 與 layer reset 前會做 limited automatic snapshot capture。operation-level history 與 persisted lab notebook 仍 pending。layer stack undo snapshots 已落地，Canvas Preview 的 state / static thumbnail / file-based live preview 已落地，Brush/Mask 暫不納入本輪 UI。
- 可保存、載入、重置本機 workspace layout，狀態位於 `state/ui_workspace.json`。
- Window menu 提供 workspace presets：Default、Maritime、Tactical、Parchment、Review，可切換 dock/tab 排版並套用對應顯示 preset。

## 預計實現功能

- Timeline 下一步是從 camera/ocean/layer opacity interpolation、layer visibility/blend discrete hold、PNG frame sequence export、GIF fallback 與 MP4 video export 推進到 blend crossfade 與 visibility fade；目前 Timeline dock、UI-only keyframe storage/restore/playback controls、profile save/load、No-GUI keyframe handoff、`timeline_state` status contract、active step handoff、renderer step playback、ocean/material interpolation、camera keyframe interpolation、layer visibility/blend discrete hold、discrete camera keyframe apply、PNG frame export、GIF animation export 與 MP4 video export 已建立。
- 中央 Canvas Preview 已具備 Qt state preview、最近 renderer output static thumbnail、static thumbnail auto-refresh 與 file-based live renderer frame stream；後續要升級為低延遲 IPC/GPU texture stream。
- Renderer layer runtime sync 下一步擴充 polygon fill mask 與更完整 renderer diagnostics；目前 visibility、支援圖層 opacity、lake/river/boundary/aircraft/pin/vehicle icon overlay blend、selected layer semantic target、selected-layer-scoped Pin/traffic/boundary/hydrology line picking 已可透過 `state/renderer_layer_runtime_state.json` 與 `state/renderer_layer_pick_state.json` 即時同步，Qt 與 renderer 端已有 bridge diagnostics、history、renderer ack 與 locked layer 防誤改。
- Layer capability matrix 下一步可補更細 renderer diagnostics，並等 RRKAL 提供 governed authoritative polygon identity source 後再做讀取/比對。
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
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_handoff.ps1`

這些入口給腳本查詢 renderer 能力、closed-loop status、圖層 manifest、可用 templates、profile schema、產生 launch packet，以及檢查跨機器 handoff summary。Renderer capabilities 內含 `closed_loop_status`、`preview_frame_stream`、`active_layer_diagnostics`、`timeline_handoff` 與 `ui_handoff_contracts` contract；`ui_handoff_contracts` 會列出 `layer_filter`、`layer_group_view`、`document_undo` 與 `timeline_state`，`timeline_handoff` 會列出 `timeline-state-file` / `timeline-ack-file` / `ack-timeline-state-and-exit`、`timeline-export-dir`、`timeline-export-frames`、`timeline-export-gif`、`timeline-export-mp4`、`rrkal_displaytools.renderer_timeline_ack.v1`、`rrkal_displaytools.timeline_playback_readiness.v1`、`rrkal_displaytools.timeline_playback_plan.v1`、`rrkal_displaytools.timeline_segment_state.v1`、`rrkal_displaytools.timeline_active_step_state.v1`、`rrkal_displaytools.timeline_step_playback.v1`、`rrkal_displaytools.timeline_ocean_material_interpolation.v1`、`rrkal_displaytools.timeline_animation_export.v1`、`rrkal_displaytools.timeline_camera_keyframe.v1`、`rrkal_displaytools.timeline_camera_interpolation.v1` / `rrkal_displaytools.timeline_layer_opacity_interpolation.v1` / `rrkal_displaytools.timeline_layer_discrete_hold.v1` 與 `rrkal_displaytools.timeline_first_keyframe_apply.v1`，並明確標示 blend crossfade 與 visibility fade 仍 pending。也可用 `--print-closed-loop-status` 只輸出目前 closed、partial 與 pending 的功能邊界；closed-loop status 會列出 `diagnostics_handoff_contracts`。

### Launch packets and handoff

- Qt panel 可匯出 launch packet 到 `state/showcase/`，內容包含當下的 `closed_loop_status` snapshot 與 `active_layer_diagnostics` snapshot。
- No-GUI exporter 可從 profile/template 產生 launch packet，並包含 `closed_loop_status` snapshot、`canvas_preview` contract、`active_layer_diagnostics` contract、`layer_filter` contract、`layer_group_view` contract、`layer_undo` contract、`session_journal` contract、`document_undo` contract、`timeline_state` / `timeline_active_step_state` contract、`timeline_export_options` contract、可保存為 `state/renderer_timeline_state.json` 的 `timeline_runtime_state` payload、Timeline runtime state/ack file CLI args、Timeline export CLI args、preview frame stream CLI args、`pin-layer` renderer flag 與 optional `--rrkal-data-manifest-ref` reference-only handoff。需要產生實體 runtime 檔時可加 `--timeline-state-out <path>`，portable command 會同步指向該檔案；需要匯出動畫時可加 `--timeline-export-dir`、`--timeline-export-gif` 或 `--timeline-export-mp4`。
- Launch packet 內含 profile、portable command、RRKAL/displaytools 責任邊界。
- `docs/RRKAL_HANDOFF_CONTRACT.zh-TW.md` 定義未來 RRKAL 對接方式。

### Windows workflow

- `scripts/setup_windows.ps1` 安裝依賴。
- `scripts/run_qt_panel.ps1` 啟動 Qt panel，支援 `-Profile`、`-Template`、`-SmokeFirst` 與 `-HandoffFirst`。
- `scripts/inspect_handoff.ps1` 輸出 read-only handoff inspection JSON，方便跨機器 clone 後先確認 UI/renderer contract，包含 layer capability matrix 摘要。
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
  - Launch packet `layer_capability_matrix` schema / live-count gate。
  - Launch packet `layer_runtime_evidence` / `layer_runtime_evidence_summary` / `layer_runtime_badge_summary` / `layer_runtime_warning_list` / `layer_runtime_interaction_context` / `layer_territory_identity_context` / `layer_authoritative_identity_source` / `layer_renderer_diagnostics_summary` / `layer_renderer_diagnostics_detail` / `layer_renderer_diagnostics_remediation` schema gate。
  - Launch packet / renderer / handoff `layer_runtime_status_legend` schema gate。
  - Launch packet `layer_filter` schema gate。
  - Launch packet `layer_filter.available_presets` gate。
  - Launch packet `layer_filter.first_matched_layer` / `selected_layer_reveal_available` gate。
  - Launch packet `layer_group_view` schema / hydrology group / selected-layer hidden diagnostic gate。
  - Launch packet `layer_undo` schema gate。
  - Launch packet `session_journal` schema gate。
  - Launch packet `document_undo` schema gate。
  - Launch packet `document_undo.limited_automatic_change_capture` / `auto_capture_points` gate。
  - Launch packet `timeline_state` schema / `timeline_playback_readiness` / `timeline_playback_plan` / `timeline_active_step_state` gate。
  - Launch packet `timeline_state.profile_timeline_keyframe_handoff` gate。
  - Launch packet `timeline_export_options` schema gate。
  - Launch packet `timeline_runtime_state` schema gate。
  - Launch packet Timeline runtime state/ack file gate。
  - Launch packet `--timeline-state-file` / `--timeline-ack-file` gate。
  - No-GUI `--timeline-state-out` writes runtime JSON and updates portable command gate。
  - Renderer `--ack-timeline-state-and-exit` reads Timeline runtime JSON and writes ack gate。
  - Launch packet `boundary_highlight.identity_status` schema gate。
  - Launch packet `--preview-frame-file` gate。
  - Launch packet `canvas_preview.preview_frame_path` / `preview_frame_interval_s` gate。
  - No-GUI Timeline export options portable command gate。
  - Renderer capabilities JSON 與 `preview_frame_stream` / `active_layer_diagnostics` / `layer_capability_matrix` / `timeline_handoff` / `timeline_handoff.ack_schema` / `timeline_handoff.playback_readiness` / `timeline_handoff.playback_plan_schema` / `timeline_handoff.active_step_state_schema` / `timeline_handoff.step_playback_schema` / `timeline_handoff.ocean_material_interpolation_schema` / `timeline_handoff.animation_export_schema` / `timeline_handoff.timeline-export-mp4` / `timeline_handoff.camera_keyframe_schema` / `timeline_handoff.camera_interpolation_schema` / `timeline_handoff.layer_opacity_interpolation_schema` / `timeline_handoff.layer_discrete_hold_schema` / `timeline_handoff.first_keyframe_apply_schema` / `ui_handoff_contracts` / `ui_handoff_contracts.layer_filter` / `ui_handoff_contracts.layer_group_view` / `ui_handoff_contracts.document_undo` schema gate。
  - Closed-loop status `diagnostics_handoff_contracts` gate。
  - Closed-loop status `layer_stack_undo_snapshots` gate。
  - Closed-loop status `session_journal_handoff` gate。
  - Closed-loop status `qt_timeline_panel` UI-only playback controls gate。
  - Handoff inspection `session_journal` / `timeline_state` contract gate。
  - Handoff inspection `layer_capability_matrix` / `layer_runtime_evidence_summary` / `layer_runtime_badge_summary` / `layer_runtime_warning_list` / `layer_runtime_interaction_context` / `layer_territory_identity_context` / `layer_authoritative_identity_source` / `layer_renderer_diagnostics_summary` / `layer_renderer_diagnostics_detail` / `layer_renderer_diagnostics_remediation` contract gate。
  - No-GUI template listing。
  - PowerShell script parse。

## 邊界

- displaytools 不負責 dataset discovery、download、import、install registry、cache/manifest governance。
- RRKAL / `APIkeys_collection` 仍是資料治理與 renderer bridge asset ownership 的來源。
- `state/`、generated images、runtime cache、logs、secrets 不提交 Git。

### 2026-05-30 cursor geodesy renderer bridge

- Renderer mouse press/move events now write `state/renderer_cursor_geodesy_state.json` and `state/renderer_cursor_geodesy_ack.json`.
- Qt launcher and no-GUI launch packets pass `--cursor-geodesy-state-file` and `--cursor-geodesy-ack-file`.
- Launch packets, renderer capabilities, handoff inspection, and smoke expose `renderer_mouse_state_wired` for the cursor geodesy bridge.

### 2026-05-30 Qt cursor geodesy bridge readback

- Qt Canvas Preview now reads renderer cursor geodesy state/ack files and shows hit/miss, lat/lon, event, frame, and update time.
- Research provenance records renderer cursor geodesy state and ack payloads alongside the UI cursor estimate.
- Smoke gates the Qt label, refresh hook, and provenance payload for this bridge.

### 2026-05-30 Pin cursor fill priority

- Pin "use cursor" now prefers renderer globe raycast geodesy and falls back to the Qt canvas estimate only when renderer state is unavailable.
- This makes researcher annotations use globe-aware coordinates when the renderer bridge is active.

### 2026-05-30 Pin cursor fill contract discovery

- Shared Pin projection contract now exposes `cursor_fill_priority = renderer_cursor_geodesy_state_then_ui_estimate`.
- Launch packets, renderer capabilities, Qt provenance, handoff inspection, and smoke all verify renderer-first Pin cursor placement.

### 2026-05-30 Pin cursor fill source UI status

- Tools dock now shows whether Pin cursor fill is using renderer globe raycast, outside-globe fallback, Qt canvas estimate fallback, or waiting for cursor state.
- This makes annotation coordinate provenance visible before researchers place Pins.

### 2026-05-30 Layer pick screen position diagnostics

- Renderer layer pick state now records click `screen_position`.
- Qt layer diagnostics show click position with hit/no-hit results so researchers can trace selected-layer picking behavior.

### 2026-05-30 Active layer pick position contract

- Active layer diagnostics now exposes the selected-layer pick `screen_position` contract and its source file.
- Launch packet, renderer capability discovery, and smoke all verify that layer pick screen-position provenance is available for cross-machine handoff.

### 2026-05-30 Handoff active layer pick position inspection

- Handoff inspection now reports active-layer `screen_position` diagnostics contract from launch packets and renderer capabilities.
- Cross-machine users can verify selected-layer pick provenance through `scripts/inspect_handoff.ps1` without inspecting renderer internals.

### 2026-05-30 Layer pick history provenance

- History panel now records renderer layer pick attempts with target, picker, hit/no-hit, feature, frame, and screen position.
- This preserves a short interaction trail for selected-layer picking during research inspection.

### 2026-05-30 Boundary ack history provenance

- Qt History now records renderer boundary highlight ack changes with enabled state, trigger, targets, renderer targets, live scopes, pending refinements, and update time.
- Research provenance includes `boundary_highlight_ack_history`, making boundary emphasis state changes reproducible after renderer handoff.

### 2026-05-30 Boundary ack history handoff contract

- Launch packets, renderer capabilities, and handoff inspection now expose the boundary ack history contract, source file, fields, Qt History surface, and provenance field.
- Smoke verifies that boundary emphasis ack history is discoverable across machines.

### 2026-05-30 Boundary identity status verification

- Renderer capabilities and handoff inspection now expose boundary identity applied/pending markers.
- Smoke verifies applied closed-ring/source-property identity scope and pending authoritative polygon / open-line inference scope across launch packet, capabilities, and handoff.

### 2026-05-30 Boundary identity markers in Qt

- Qt Properties and Canvas Preview now show boundary identity applied/pending marker names, making visual/source-property identity and pending authoritative polygon/open-line work visible in the UI.
- Smoke verifies the visible Boundary identity summary line.

### 2026-05-30 Boundary emphasis dialog preview

- Qt Boundary emphasis controls now include an RGB swatch and live numeric preview for target, RGB, contrast, opacity, gamma and breathing timing.
- Boundary emphasis launch/capability contracts expose dialog feedback fields so clone-after-setup checks can confirm the UI affordance exists.

### 2026-05-30 Boundary layer action badge

- Boundary-capable layer rows now expose a visible Emphasis action badge in the Qt Layers dock.
- Launch packet and renderer capabilities advertise the boundary emphasis row action so cross-machine clone checks can verify the UI affordance.

### 2026-05-30 Boundary emphasis target alignment

- Boundary emphasis UI now reports the resolved target layer and whether it matches the selected layer.
- Launch packet and renderer capabilities expose target alignment fields for handoff and clone-after-setup inspection.

### 2026-05-30 Boundary target in Canvas Preview

- Canvas Preview now reports Boundary target mode, resolved target layer and selected-layer alignment.
- Canvas preview provenance carries the same boundary emphasis target alignment fields.

### 2026-05-30 Timeline boundary emphasis state

- Timeline keyframes now preserve Boundary emphasis control state and restore it when keyframes are applied in Qt.
- Timeline launch/renderer contracts include Boundary emphasis as a discrete keyframe field for reproducible demonstrations.

### 2026-05-30 Timeline keyframe boundary target summary

- Timeline keyframe rows now include Boundary emphasis target and alignment summaries.
- Loaded profile keyframes and newly captured keyframes share the same display formatter.

### 2026-05-30 Pin cursor fill status row

- Pin Annotation now exposes a fixed Cursor Fill status row with renderer-raycast vs Qt-estimate source text.
- Cursor fill status refreshes after coordinate fill and remains mirrored in the tool palette summary.

### 2026-05-30 Pin coordinate source metadata

- Pin records now capture coordinate source metadata for manual entry, renderer globe raycast and Qt canvas estimate fallback.
- Pin list rows display the coordinate source for quick research review.

### 2026-05-30 Pin projection rule note

- Pin Annotation now visibly documents that Pins rotate with the globe and are hidden by horizon/depth occlusion when behind the globe.

### 2026-05-30 Pin/Boundary handoff inspection summary

- Handoff inspection now reports Pin coordinate-source fields, supported coordinate sources, Qt Pin affordances and projection note text.
- Handoff inspection now reports Boundary emphasis dialog feedback and target-alignment fields.
- Windows setup clone URL now uses `Kagamihara-Ruruka`.

### 2026-05-30 Profile schema Pin/Boundary/Timeline fields

- Profile schema now documents Pin coordinate source metadata, Boundary emphasis target alignment and Timeline boundary-emphasis keyframe preservation.
- Canvas Preview profile docs now include Boundary emphasis target alignment provenance fields.

### 2026-05-30 Renderer UI handoff contract list refresh

- Renderer capability discovery now lists cursor geodesy, Pin overlay, Boundary emphasis and Boundary ack history in `ui_handoff_contracts`.
- Smoke verifies the refreshed handoff contract list.

### 2026-05-30 Closed-loop Pin/Boundary UI handoff evidence

- Closed-loop status now includes `pin_boundary_ui_handoff` for Pin coordinate source/projection UI and Boundary emphasis/ack handoff evidence.
- Timeline partial status now lists Boundary emphasis keyframe preservation and Boundary target summaries.

### 2026-05-30 Boundary identity source hint contract

- Boundary identity status now carries `identity_source_hint` across renderer, Qt and launch packet contracts.
- The contract states that current emphasis identity is preview/provenance based, while authoritative polygon identity and open-line area inference remain `pending_backend_geometry_closure` backend closures.


### 2026-05-30 Boundary identity source hint summary

- Boundary identity contracts now include `identity_source_hint_summary` for compact handoff display.
- The summary keeps the UI honest that current identity is preview/source-property based and `pending_backend_geometry_closure` still blocks authoritative open-line inference.

### 2026-05-30 Qt Boundary identity source visible summary

- Properties and Canvas Preview now expose Boundary identity `source_hint=` text directly through the shared Qt identity summary helper.
- Smoke verifies that compact identity provenance is visible in Qt, not only available in JSON contracts.

### 2026-05-30 Qt Boundary identity pending warning badge

- Properties now shows a styled Boundary identity warning badge when authoritative polygon/EEZ identity or open-line inference remains pending.
- The badge keeps the scientific UI explicit that current Boundary emphasis is visual/provenance state, not authoritative identity resolution.

### 2026-05-30 Canvas Preview Boundary identity warning provenance

- Canvas Preview now shows a `Boundary warning:` line and mirrors the warning in canvas meta text.
- Research provenance now records `canvas_preview.boundary_identity_warning` so exported UI state preserves the non-authoritative identity warning.

### 2026-05-30 No-GUI launch packet Boundary identity warning

- No-GUI launch packets now expose `canvas_preview.boundary_identity_warning` by default.
- Clone/handoff users can see pending authoritative polygon/EEZ identity and open-line closure warnings without starting Qt.

### 2026-05-30 Handoff inspection Boundary identity warning

- `scripts\inspect_handoff.ps1` now reports `canvas_preview.boundary_identity_warning` and its surface description.
- Cross-machine inspection can show Boundary/EEZ identity warnings without launching Qt.

### 2026-05-30 Closed-loop Boundary identity warning handoff evidence

- Closed-loop status now lists `boundary_identity_warning_handoff` for the warning/provenance loop across Qt, Canvas Preview, launch packet, handoff inspection and smoke.
- The closed-loop note keeps authoritative polygon/EEZ identity and open-line area inference explicitly pending.

### 2026-05-30 Qt Layers workflow hint

- Layers dock now includes a visible workflow hint for selecting active research layers and opening Boundary emphasis controls.
- The hint clarifies that identity warning badges indicate preview/source-property identity, not authoritative polygon/EEZ resolution.

### 2026-05-30 Launch/Handoff Layers workflow hint

- `layer_research_workflow` now carries `workflow_hint` and `workflow_hint_surface` in Qt/no-GUI contracts.
- Handoff inspection reports the same hint, including Boundary/territorial sea/EEZ/high-seas emphasis entry points.

### 2026-05-30 Renderer capability Layers workflow hint

- Renderer capability discovery now includes the Layers workflow hint under `layer_research_workflow`.
- The hint is now aligned across Qt UI, no-GUI launch packet, handoff inspection and renderer capabilities.

### 2026-05-30 Closed-loop Layers workflow hint handoff evidence

- Closed-loop status now lists `layer_workflow_hint_handoff` for the layer workflow guidance loop.
- Evidence spans Qt UI, launch packet, handoff inspection, renderer capabilities and smoke gates.

### 2026-05-30 Profile UI state replay handoff loop

- Added `profile_ui_state_replay` across Qt UI, launch packet, renderer capabilities, handoff inspection and closed-loop status.
- The contract summarizes which UI state groups are portable through profiles and Timeline keyframes.

### 2026-05-30 Profile schema UI state replay docs

- Profile schema docs now describe `profile_ui_state_replay` and its saved state groups / replay surfaces.
- Smoke verifies the docs stay aligned with the new profile replay handoff contract.

### 2026-05-30 Profile UI replay smoke source gates

- Smoke now checks `saved_state_groups` and `replay_surfaces` across Qt, renderer capabilities, launch packet and handoff inspection.
- This keeps profile replay coverage machine-verifiable across clone-after-setup workflows.

### 2026-05-30 Qt Profile replay JSON action

- Qt Actions now includes `Profile replay`, which displays the live `profile_ui_state_replay` payload in the JSON preview pane.
- Smoke verifies the action button and handler so replay coverage remains inspectable from the UI.

### 2026-05-30 Qt Ocean material port JSON action

- Qt Actions now includes `Ocean port`, which displays the live `ocean_material_control_port` payload in the JSON preview pane.
- This keeps wave strength, roughness, foam, Taichi uniforms and scalar sea-state handoff inspectable without adding provider discovery/download/import/cache governance to displaytools.

### 2026-05-30 Qt Hydrology LOD JSON action

- Qt Actions now includes `Hydro LOD`, which displays `hydrology_lod_readiness` and `hydrology_lod_runtime_evidence` together in the JSON preview pane.
- This makes lake/river layer contracts, renderer targets, runtime ack files, pick-state files and LOD hook readiness inspectable from the primary Qt UI.

### 2026-05-30 Qt Style routes JSON action

- Qt Actions now includes `Style routes`, which displays `style_renderer_entries` and `style_profile_renderer_routes` together in the JSON preview pane.
- Parchment and tactical renderer routes are now inspectable from Qt in addition to launch packets, renderer capabilities and handoff inspection.

### 2026-05-30 Qt Module seams JSON action

- Qt Actions now includes `Module seams`, which displays the live `module_boundary_registry` payload in the JSON preview pane.
- The registry keeps future extraction boundaries explicit: contracts, Qt UI, Taichi render core, ocean material, style profiles, overlays, RRKAL-owned data sources and diagnostics.

### 2026-05-30 Qt Clone readiness JSON action

- Qt Actions now includes `Clone ready`, which displays the live `cross_machine_clone_readiness` payload in the JSON preview pane.
- Cross-machine users can inspect portable command, profile launch readiness and module boundary readiness from Qt without reading raw launch packets.

### 2026-05-30 Qt contract inspector tooltips

- The Qt Actions inspector buttons now include tooltips and accessible descriptions for Profile replay, Ocean port, Hydro LOD, Style routes, Module seams and Clone ready.
- This makes the smoke-gated JSON inspection surface easier to understand for researchers using the panel directly.

### 2026-05-30 Qt Pin pick JSON action

- Qt Actions now includes `Pin pick`, which displays the renderer Pin hover/click pick bridge JSON from the panel.
- This gives researchers a direct inspection path for Pin selection feedback while keeping Pins as globe-following geodetic anchors.

### 2026-05-30 Qt Cursor geodesy JSON action

- Qt Actions now includes `Cursor geo`, which displays `cursor_geodesy_readout`, renderer cursor state/ack file paths and the latest state/ack payloads.
- This gives researchers a direct JSON inspection path for mouse-position latitude/longitude inference and renderer raycast feedback.

### 2026-05-30 Qt Boundary JSON action

- Qt Actions now includes `Boundary JSON`, which displays Boundary highlight, Boundary emphasis controls, identity warning text, renderer ack payload and recent ack history.
- This gives researchers a direct inspection path for country/territorial sea/EEZ emphasis state and the current non-authoritative identity warning.

### 2026-05-30 Qt inspector action naming

- Qt JSON inspection buttons now use an `Inspect:` prefix, separating state/contract inspection from renderer launch, profile save/load and process control actions.
- This keeps the Actions panel more readable as more scientific inspection surfaces are added.

### 2026-05-30 Clone quickstart Inspect guidance

- The clone quickstart now tells cross-machine users which `Inspect:` buttons to open first after launching Qt.
- Smoke verifies the quickstart mentions `Inspect: Clone ready` and `Inspect: Boundary JSON` so onboarding docs stay aligned with the Qt Actions panel.

### 2026-05-30 Profile replay Inspect surface

- `profile_ui_state_replay.replay_surfaces` now includes `Qt Inspect actions` in Qt, no-GUI launch packets and renderer capability discovery.
- The profile schema and smoke gates now keep this direct Qt inspection surface aligned across clone/handoff workflows.

### 2026-05-30 Profile replay inspector action IDs

- `profile_ui_state_replay` now exposes `qt_inspector_action_ids`, `qt_inspector_action_labels` and `qt_inspector_action_count`.
- Smoke verifies Boundary, Cursor and Clone inspector entries through launch packets, renderer capabilities and schema docs.

### 2026-05-30 Profile replay inspector groups

- `profile_ui_state_replay` now exposes `qt_inspector_action_groups` and `qt_inspector_group_count`.
- Inspector groups separate replay/contracts, renderer ports and research interaction checks for Qt-first onboarding and capability discovery.

### 2026-05-30 Clone quickstart Inspect groups

- The clone quickstart now mirrors the machine-readable Inspect groups: Replay/contracts, Renderer ports and Research interaction.
- Smoke verifies quickstart group guidance so onboarding remains aligned with `profile_ui_state_replay.qt_inspector_action_groups`.

### 2026-05-30 Qt grouped Inspect tooltips

- Qt Inspect button tooltips and accessible descriptions now include their group names: Replay/contracts, Renderer ports and Research interaction.
- Smoke verifies grouped tooltip text so the UI reflects the same grouping exposed in profile replay contracts.

### 2026-05-30 Qt Actions section layout

- Qt Actions now uses section headers for Run/profile, Inspect Replay/contracts, Inspect Renderer ports, Inspect Research interaction, Renderer diagnostics and Process.
- Smoke verifies the section header marker and representative Inspect group headers.

### 2026-05-30 Qt Layer Inspect actions

- Qt Actions now includes `Inspect: Layer matrix`, `Inspect: Layer runtime` and `Inspect: Layer pick`.
- These actions expose existing layer capability matrix, layer runtime state/ack and selected-layer pick JSON from the grouped Actions panel, and are listed in profile replay inspector contracts.

### 2026-05-30 Qt Timeline Inspect action

- Qt Actions now includes `Inspect: Timeline`.
- The action writes/opens the current Timeline runtime state JSON, covering Timeline state, keyframes, playback readiness, segment state, active step, export options and interpolation contracts.

### 2026-05-30 Qt Canvas state Inspect action

- Qt Actions now labels Canvas state as `Inspect: Canvas state` inside the Research interaction section.
- The action remains backed by the existing Canvas Preview state/provenance view and is now listed in profile replay inspector contracts.

## Qt Inspect visual review

- Qt Actions now exposes `Inspect: Visual review` as a first-class section.
- `Inspect: Renderer thumbnail` provides a static renderer pixel checkpoint for clone/readback review.
- `Inspect: Live preview` provides the file-based live preview frame path for renderer pixel review.
- Launch packets and renderer capabilities advertise the `visual_review` group through `profile_ui_state_replay`.

## Qt Renderer menu Inspect alignment

- Renderer menu visual preview entries now use `Inspect: Renderer thumbnail` and `Inspect: Live preview`.
- This keeps the menu bar, Actions panel, launch packet inspector labels, and smoke gates aligned around one inspection vocabulary.

## Qt Inspect selection state

- Qt Actions now exposes `Inspect: Selection state` inside Research interaction.
- The action calls the existing layer pick state JSON path, but labels it around the researcher task: confirming active layer selection and renderer target before analysis/export.
- Launch packets and renderer capabilities advertise `selection_state` through `profile_ui_state_replay`.

## Qt active layer operation summary

- Layers dock now shows a visible `Layer operation summary` for the active research layer.
- The summary includes active layer key/label, visibility, lock, opacity, blend mode, renderer target, runtime ack and pick context.
- Qt launch/provenance packets include `active_layer_operation_summary`, so clone/review workflows can inspect the same operation state without opening multiple JSON panes first.

## Qt last layer operation feedback

- Layers dock now keeps a visible `Last layer operation` label for selected-layer visibility, lock, selected-layer reset and stack reset actions.
- Qt launch/provenance packets include `last_layer_operation`, giving clone/review workflows a compact record of the last layer operation message.
- Solo selected layer, restore pre-solo visibility and layer undo now use the same operation feedback path, so isolation/history actions leave visible researcher-facing status in the Layers dock.
- Group toggles and layer visual preset application now also update `Last layer operation`, closing feedback for high-level layer visibility workflows.

## Qt Inspect layer operation feedback

- Qt Actions now exposes `Inspect: Layer ops` inside Research interaction.
- `rrkal_displaytools.layer_operation_feedback.v1` combines active layer summary, last layer operation, operator groups and undo depth into one copyable packet.
- Qt launch/provenance packets, No-GUI launch packets and renderer capabilities advertise `layer_operation_feedback`.
- Handoff inspection now reports `layer_operation_feedback`, giving clone/review users a read-only summary before opening Qt.

## Handoff profile/visual quick review

- Handoff inspection now exposes `profile_visual_quick_review`.
- The quick review reports Qt inspector group ids, Research interaction actions, Visual review actions and a recommended cross-machine inspection sequence.
- Smoke gates that Research interaction includes `layer_ops` and Visual review includes `renderer_thumbnail` / `live_preview`.

## Visual review readiness

- Handoff inspection now exposes `rrkal_displaytools.visual_review_readiness.v1`.
- The packet reports Visual review action ids, renderer thumbnail readiness, live preview readiness and missing-frame guidance.
- Smoke gates both readiness flags and the renderer thumbnail/live preview guidance text.

## Qt visual readiness Inspect

- `rrkal_displaytools.visual_review_readiness.v1` is now emitted by no-GUI launch packets and renderer capability discovery.
- Profile UI replay advertises `Inspect: Visual readiness` in the Visual review group.
- Smoke gates the launch packet schema, renderer capability schema and Qt action id through handoff output.

## Visual review frame status

- `visual_review_readiness.frame_status_schema` now advertises `rrkal_displaytools.visual_review_frame_status.v1`.
- The packet reports renderer thumbnail and live preview frame status separately.
- Smoke gates both statuses as `inspect_action_available` and both artifact states as `runtime_dependent`.

## Visual review inspector view

- `visual_review_readiness.inspector_view_schema` now advertises `rrkal_displaytools.visual_review_inspector_view.v1`.
- The view provides a Qt-facing title, surface id, status badges, rows and hints.
- Smoke gates the title, surface, row count and copyable flag through handoff output.

## Visual readiness Qt command contract

- `visual_review_readiness.qt_command_contract_schema` now advertises `rrkal_displaytools.visual_review_qt_command_contract.v1`.
- The contract maps `visual_readiness` to `visual_review_readiness.inspector_view`.
- Smoke gates action id, payload field, `contract_ready` dispatch status and `wired_in_qt_panel` implementation status through handoff output.

## Qt Visual readiness action

- The Qt panel now includes `Inspect: Visual readiness` in the Visual review button group and Renderer menu.
- `show_visual_review_readiness()` displays the copyable `visual_review_readiness` JSON packet.
- Smoke gates the packet function, collector, button and Inspect action in `rrkal_displaytools_qt_panel.py`.

## Qt Visual readiness runtime artifacts

- `collect_visual_review_readiness()` now adds `rrkal_displaytools.visual_review_runtime_artifact_summary.v1`.
- The Qt packet marks renderer thumbnail/live preview as `frame_available` when runtime frame artifacts exist.
- Smoke gates that the Qt collector checks `latest_renderer_thumbnail_path()` and `RENDERER_PREVIEW_FRAME_PATH.exists()`.

## Qt Visual readiness visible summary

- The Layers dock now exposes a `visualReviewReadiness` label.
- `show_visual_review_readiness()` updates the label through `visual_review_readiness_summary_text()`.
- Smoke gates the label object name, summary formatter and label updater.

## Qt Visual readiness copy summary

- The Visual review group now includes `Copy visual summary`.
- `copy_visual_review_readiness_summary()` copies the compact readiness summary to the clipboard and refreshes the visible label.
- Smoke gates the copy button and copy action.

## Visual readiness copy summary contract

- `visual_review_readiness.copy_summary_contract_schema` now advertises `rrkal_displaytools.visual_review_copy_summary_contract.v1`.
- The contract defines the summary label, format, Qt label object, Qt copy action, launch packet field and handoff field.
- Smoke gates the contract schema, label object, copy action and portability flag through handoff output.

## Layer selection summary contract

- `layer_selection_tool.selection_summary_contract_schema` now advertises `rrkal_displaytools.layer_selection_summary_contract.v1`.
- The contract maps the existing `selectedLayer` label to `copy_layer_selection_summary`.
- Smoke gates launch packet, renderer capability, handoff and Qt button/action coverage.

## Boundary emphasis summary contract

- `boundary_emphasis_control.boundary_summary_contract_schema` now advertises `rrkal_displaytools.boundary_emphasis_summary_contract.v1`.
- The contract maps the existing Layers dock Boundary emphasis label to `copy_boundary_emphasis_summary`.
- Smoke gates launch packet, renderer capability, handoff and Qt button/action coverage.

## Pin overlay summary contract

- `pin_overlay.pin_summary_contract_schema` now advertises `rrkal_displaytools.pin_summary_contract.v1`.
- The contract maps the Pin list object to `copy_pin_overlay_summary`.
- Smoke gates launch packet, renderer capability, handoff and Qt button/action coverage.

## Cursor geodesy summary contract

- `cursor_geodesy_readout.cursor_summary_contract_schema` now advertises `rrkal_displaytools.cursor_geodesy_summary_contract.v1`.
- The contract maps the Cursor geo research action to `copy_cursor_geodesy_summary`.
- Smoke gates launch packet, renderer capability, handoff and Qt button/action coverage.
