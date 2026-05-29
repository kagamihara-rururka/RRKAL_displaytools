"""Qt operator panel for RRKAL_displaytools layer/UI launch.

This panel intentionally stays outside the renderer loop. It collects operator
choices, builds command-line flags, and starts taichi_global_bathymetry.py.
RRKAL remains responsible for data discovery, download, manifest, and cache
governance; this file is only a displaytools control surface.
"""

from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

from closed_loop_status import renderer_closed_loop_status_packet
from profile_schema import profile_payload_errors
from pin_projection import pin_projection_contract_packet


ROOT = Path(__file__).resolve().parent
PROFILE_TEMPLATE_DIR = ROOT / "profiles"
PIN_PICK_STATE_PATH = ROOT / "state" / "renderer_pin_pick_state.json"
PIN_INPUT_ACK_PATH = ROOT / "state" / "renderer_pin_input_ack.json"
PIN_PICK_ACK_PATH = ROOT / "state" / "qt_pin_pick_ack.json"
BOUNDARY_HIGHLIGHT_ACK_PATH = ROOT / "state" / "renderer_boundary_highlight_ack.json"
LAYER_RUNTIME_STATE_PATH = ROOT / "state" / "renderer_layer_runtime_state.json"
LAYER_RUNTIME_ACK_PATH = ROOT / "state" / "renderer_layer_runtime_ack.json"
LAYER_PICK_STATE_PATH = ROOT / "state" / "renderer_layer_pick_state.json"


def profile_template_packet() -> dict[str, object]:
    templates = []
    for path in sorted(PROFILE_TEMPLATE_DIR.glob("*.json")):
        item: dict[str, object] = {
            "id": path.stem,
            "path": str(path.relative_to(ROOT)),
        }
        try:
            profile = json.loads(path.read_text(encoding="utf-8-sig"))
            if isinstance(profile, dict):
                item["name"] = profile.get("name", path.stem)
                item["description"] = profile.get("description", "")
                item["schema"] = profile.get("schema", "")
        except Exception as exc:
            item["error"] = str(exc)
        templates.append(item)
    return {
        "schema": "rrkal_displaytools.profile_templates.v1",
        "templates": templates,
    }


if "--list-templates" in sys.argv[1:]:
    print(json.dumps(profile_template_packet(), ensure_ascii=False, indent=2))
    raise SystemExit(0)

try:
    from PyQt6 import QtCore, QtGui, QtWidgets
except ImportError as exc:
    raise SystemExit(
        "PyQt6 is required for the Qt control panel. Install project dependencies with: "
        "py -3 -m pip install -r requirements.txt"
    ) from exc

RENDERER = ROOT / "taichi_global_bathymetry.py"
PROFILE_DIR = ROOT / "state" / "ui_profiles"
SHOWCASE_DIR = ROOT / "state" / "showcase"
RENDERER_PREVIEW_FRAME_PATH = ROOT / "state" / "renderer_preview_frame.png"
RENDERER_PREVIEW_FRAME_INTERVAL_S = 0.75
WORKSPACE_STATE_PATH = ROOT / "state" / "ui_workspace.json"

STYLE_PROFILES = ("scientific", "nautical", "parchment", "tactical")
UI_BACKENDS = ("qt", "vispy")
TOPO_SOURCES = ("gebco", "synthetic")
DATA_MODES = ("static", "realtime", "timeseries")

BOOL_FLAGS = {
    "show_grid": "show-grid",
    "show_stars": "show-stars",
    "lake_layer": "lake-layer",
    "river_layer": "river-layer",
    "border_layer": "border-layer",
    "territorial_sea_layer": "territorial-sea-layer",
    "eez_layer": "eez-layer",
    "high_seas_layer": "high-seas-layer",
    "aircraft_layer": "aircraft-layer",
    "pin_layer": "pin-layer",
    "ocean_material": "ocean-material",
    "terrain_contours": "terrain-contours",
    "scale_bar": "scale-bar",
    "vehicle_icons": "vehicle-icons",
    "demo_closed_loop": "demo-closed-loop",
}

LAYER_LABELS = (
    ("show_grid", "經緯網格"),
    ("show_stars", "星空背景"),
    ("lake_layer", "湖泊圖層"),
    ("river_layer", "河流圖層"),
    ("border_layer", "國界圖層"),
    ("territorial_sea_layer", "領海圖層"),
    ("eez_layer", "EEZ 圖層"),
    ("high_seas_layer", "公海圖層"),
    ("aircraft_layer", "航機圖層"),
    ("pin_layer", "科研 Pin 標記"),
    ("ocean_material", "海洋材質"),
    ("terrain_contours", "地形等高線"),
    ("scale_bar", "比例尺"),
    ("vehicle_icons", "交通工具圖示"),
)

LAYER_RUNTIME_ID_ALIASES = {
    "show_grid": "grid",
    "show_stars": "stars",
    "lake_layer": "lakes",
    "river_layer": "rivers",
    "border_layer": "borders",
    "territorial_sea_layer": "territorial_sea",
    "eez_layer": "eez",
    "high_seas_layer": "high_seas",
    "aircraft_layer": "aircraft",
    "pin_layer": "pins",
    "ocean_material": "ocean_material",
    "terrain_contours": "contours",
    "scale_bar": "scale",
    "vehicle_icons": "vehicle_icons",
}

BOUNDARY_HIGHLIGHT_SCHEMA = "rrkal_displaytools.boundary_highlight_mask.v1"
BOUNDARY_IDENTITY_STATUS_SCHEMA = "rrkal_displaytools.boundary_identity_status.v1"
BOUNDARY_HIGHLIGHT_LAYER_KEYS = (
    "border_layer",
    "territorial_sea_layer",
    "eez_layer",
    "high_seas_layer",
)
BLEND_MODES = ("Normal", "Screen", "Multiply", "Overlay", "Soft Light")
TOOL_MODES = (
    ("move", "Move", "檢視 / 平移"),
    ("select", "Select", "選取圖層 / active layer target"),
    ("pin", "Pin", "科研標記 / observation marker"),
)
PIN_TYPES = ("Observation", "Sample Site", "Anomaly", "Reference", "Event")
PIN_LABEL_MODES = (
    ("auto", "Auto", "Place visible labels until collision budget is exhausted."),
    ("selected", "Selected only", "Only label the selected Pin."),
    ("priority", "Priority", "Only label selected Pin and Pins above the priority threshold."),
    ("hidden", "Hidden", "Hide all Pin labels; markers remain visible."),
)


def _coerce_int(value: object, default: int, minimum: int, maximum: int) -> int:
    if isinstance(value, bool):
        return default
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, number))


def default_boundary_identity_status() -> dict[str, object]:
    return {
        "schema": BOUNDARY_IDENTITY_STATUS_SCHEMA,
        "applied": [
            "source_property_feature_identity",
            "maritime_property_key_identity",
            "closed_ring_area_hit_test",
            "closed_ring_fill_preview",
        ],
        "pending": [
            "authoritative_polygon_territory_identity",
            "open_line_area_inference",
        ],
        "boundary": "visual/source-property preview only; not an authoritative legal boundary resolution",
    }


def default_boundary_highlight_state() -> dict[str, object]:
    return {
        "schema": BOUNDARY_HIGHLIGHT_SCHEMA,
        "enabled": True,
        "trigger": "hover",
        "target_layers": list(BOUNDARY_HIGHLIGHT_LAYER_KEYS),
        "color_rgb": [255, 190, 72],
        "contrast": 45,
        "alpha": 48,
        "gamma": 100,
        "feather": 14,
        "breathing": {
            "enabled": True,
            "speed": 42,
            "amplitude": 16,
        },
        "identity_status": default_boundary_identity_status(),
        "renderer_sync": "renderer_line_fill_identity_status_handoff",
    }


def normalized_boundary_highlight_state(payload: object) -> dict[str, object]:
    state = default_boundary_highlight_state()
    if not isinstance(payload, dict):
        return state
    state["enabled"] = bool(payload.get("enabled", state["enabled"]))
    trigger = payload.get("trigger")
    if isinstance(trigger, str) and trigger in {"hover", "selected", "hover_or_selected"}:
        state["trigger"] = trigger
    targets = payload.get("target_layers")
    if isinstance(targets, list):
        target_layers = [str(layer) for layer in targets if str(layer) in BOUNDARY_HIGHLIGHT_LAYER_KEYS]
        if target_layers:
            state["target_layers"] = target_layers
    color_rgb = payload.get("color_rgb")
    if isinstance(color_rgb, list) and len(color_rgb) >= 3:
        state["color_rgb"] = [_coerce_int(color_rgb[index], 255, 0, 255) for index in range(3)]
    state["contrast"] = _coerce_int(payload.get("contrast"), int(state["contrast"]), 0, 100)
    state["alpha"] = _coerce_int(payload.get("alpha"), int(state["alpha"]), 0, 100)
    state["gamma"] = _coerce_int(payload.get("gamma"), int(state["gamma"]), 25, 300)
    state["feather"] = _coerce_int(payload.get("feather"), int(state["feather"]), 0, 100)
    breathing = payload.get("breathing")
    if isinstance(breathing, dict):
        state["breathing"] = {
            "enabled": bool(breathing.get("enabled", True)),
            "speed": _coerce_int(breathing.get("speed"), 42, 0, 100),
            "amplitude": _coerce_int(breathing.get("amplitude"), 16, 0, 100),
        }
    renderer_sync = payload.get("renderer_sync")
    if isinstance(renderer_sync, str):
        state["renderer_sync"] = renderer_sync
    return state


class DisplayToolsQtPanel(QtWidgets.QMainWindow):
    def __init__(self, initial_profile: Path | None = None) -> None:
        super().__init__()
        self.setWindowTitle("RRKAL DisplayTools Qt 控制面板")
        self.resize(1120, 780)
        self.process: subprocess.Popen[bytes] | None = None
        self.checks: dict[str, QtWidgets.QCheckBox] = {}
        self.layer_locks: dict[str, QtWidgets.QCheckBox] = {}
        self.layer_opacity: dict[str, QtWidgets.QSlider] = {}
        self.layer_blends: dict[str, QtWidgets.QComboBox] = {}
        self.layer_rows: dict[str, QtWidgets.QWidget] = {}
        self.layer_property_labels: dict[str, QtWidgets.QLabel] = {}
        self.layer_visibility_snapshot: dict[str, bool] | None = None
        self.layer_undo_stack: list[dict[str, object]] = []
        self.layer_last_state_snapshot: dict[str, object] | None = None
        self.layer_last_state_signature: str | None = None
        self.layer_undo_restore_active = False
        self.layer_undo_tracking_enabled = False
        self.layer_undo_label: QtWidgets.QLabel | None = None
        self.layer_runtime_state_label: QtWidgets.QLabel | None = None
        self.layer_runtime_state_last_write_utc: str | None = None
        self.layer_runtime_state_write_error: str | None = None
        self.layer_runtime_history: list[str] = []
        self.layer_runtime_history_signature: str | None = None
        self.layer_runtime_ack_label: QtWidgets.QLabel | None = None
        self.layer_runtime_ack_mtime_ns: int | None = LAYER_RUNTIME_ACK_PATH.stat().st_mtime_ns if LAYER_RUNTIME_ACK_PATH.exists() else None
        self.layer_runtime_ack_payload: dict[str, object] | None = None
        self.layer_pick_state_label: QtWidgets.QLabel | None = None
        self.layer_pick_state_mtime_ns: int | None = LAYER_PICK_STATE_PATH.stat().st_mtime_ns if LAYER_PICK_STATE_PATH.exists() else None
        self.layer_pick_state_payload: dict[str, object] | None = None
        self.history_list: QtWidgets.QListWidget | None = None
        self.selected_layer_key: str | None = None
        self.boundary_highlight_state: dict[str, object] = default_boundary_highlight_state()
        self.boundary_highlight_label: QtWidgets.QLabel | None = None
        self.boundary_identity_status_label: QtWidgets.QLabel | None = None
        self.boundary_highlight_ack_label: QtWidgets.QLabel | None = None
        self.boundary_highlight_ack_mtime_ns: int | None = (
            BOUNDARY_HIGHLIGHT_ACK_PATH.stat().st_mtime_ns if BOUNDARY_HIGHLIGHT_ACK_PATH.exists() else None
        )
        self.boundary_highlight_ack_payload: dict[str, object] | None = None
        self.boundary_layer_event_targets: dict[int, str] = {}
        self.active_tool = "move"
        self.tool_buttons: dict[str, QtWidgets.QToolButton] = {}
        self.tool_target_label: QtWidgets.QLabel | None = None
        self.pin_type_combo: QtWidgets.QComboBox | None = None
        self.pin_label_edit: QtWidgets.QLineEdit | None = None
        self.pin_note_edit: QtWidgets.QLineEdit | None = None
        self.pin_lat_edit: QtWidgets.QLineEdit | None = None
        self.pin_lon_edit: QtWidgets.QLineEdit | None = None
        self.pin_priority_spin: QtWidgets.QSpinBox | None = None
        self.pin_label_mode_combo: QtWidgets.QComboBox | None = None
        self.pin_label_min_priority_spin: QtWidgets.QSpinBox | None = None
        self.pin_list: QtWidgets.QListWidget | None = None
        self.pin_input_ack_label: QtWidgets.QLabel | None = None
        self.pin_input_ack_mtime_ns: int | None = PIN_INPUT_ACK_PATH.stat().st_mtime_ns if PIN_INPUT_ACK_PATH.exists() else None
        self.pin_input_ack_payload: dict[str, object] | None = None
        self.pin_pick_state_label: QtWidgets.QLabel | None = None
        self.pin_pick_ack_label: QtWidgets.QLabel | None = None
        self.pin_pick_state_mtime_ns: int | None = PIN_PICK_STATE_PATH.stat().st_mtime_ns if PIN_PICK_STATE_PATH.exists() else None
        self.pin_pick_state_last_event: str | None = None
        self.pin_pick_state_payload: dict[str, object] | None = None
        self.pin_pick_ack_payload: dict[str, object] | None = None
        self.pin_pick_ack_write_error: str | None = None
        self.pin_pick_history: list[str] = []
        self.pin_pick_history_signature: str | None = None
        self.selected_pin_id: str | None = None
        self.research_pins: list[dict[str, object]] = []
        self.canvas_preview_label: QtWidgets.QLabel | None = None
        self.canvas_meta_label: QtWidgets.QLabel | None = None
        self.canvas_preview_mode = "state"
        self.renderer_thumbnail_path: Path | None = None
        self.renderer_thumbnail_mtime_ns: int | None = None
        self.canvas_zoom_slider: QtWidgets.QSlider | None = None
        self.cursor_latitude: float | None = None
        self.cursor_longitude: float | None = None
        self.provenance_text: QtWidgets.QPlainTextEdit | None = None
        self.docks: dict[str, QtWidgets.QDockWidget] = {}
        self.template_paths: list[Path] = []
        self._build_ui()
        self._build_menu_bar()
        self._build_tool_dock()
        self._build_auxiliary_docks()
        self.load_workspace_layout(silent=True)
        self.statusBar().showMessage("Ready")
        self.process_timer = QtCore.QTimer(self)
        self.process_timer.setInterval(1500)
        self.process_timer.timeout.connect(self.update_process_status)
        self.process_timer.start()
        self.pin_pick_state_timer = QtCore.QTimer(self)
        self.pin_pick_state_timer.setInterval(800)
        self.pin_pick_state_timer.timeout.connect(self.refresh_renderer_pin_pick_state)
        self.pin_pick_state_timer.start()
        self.pin_input_ack_timer = QtCore.QTimer(self)
        self.pin_input_ack_timer.setInterval(1000)
        self.pin_input_ack_timer.timeout.connect(self.refresh_pin_input_ack_state)
        self.pin_input_ack_timer.start()
        self.layer_runtime_ack_timer = QtCore.QTimer(self)
        self.layer_runtime_ack_timer.setInterval(1000)
        self.layer_runtime_ack_timer.timeout.connect(self.refresh_layer_runtime_ack_state)
        self.layer_runtime_ack_timer.start()
        self.layer_pick_state_timer = QtCore.QTimer(self)
        self.layer_pick_state_timer.setInterval(800)
        self.layer_pick_state_timer.timeout.connect(self.refresh_layer_pick_state)
        self.layer_pick_state_timer.start()
        self.boundary_highlight_ack_timer = QtCore.QTimer(self)
        self.boundary_highlight_ack_timer.setInterval(1000)
        self.boundary_highlight_ack_timer.timeout.connect(self.refresh_boundary_highlight_ack_state)
        self.boundary_highlight_ack_timer.start()
        self.renderer_thumbnail_timer = QtCore.QTimer(self)
        self.renderer_thumbnail_timer.setInterval(1500)
        self.renderer_thumbnail_timer.timeout.connect(self.refresh_renderer_thumbnail_if_needed)
        self.renderer_thumbnail_timer.start()
        self.apply_baseline()
        self.refresh_template_list()
        if initial_profile is not None:
            self.load_profile_path(initial_profile)
        self.refresh_command_preview()
        self.refresh_layer_stack_status()
        self.layer_undo_stack = []
        self.layer_last_state_snapshot = self.collect_layer_undo_snapshot()
        self.layer_last_state_signature = self.layer_undo_signature(self.layer_last_state_snapshot)
        self.layer_undo_tracking_enabled = True
        self.refresh_layer_undo_label()

    def _build_ui(self) -> None:
        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        main = QtWidgets.QVBoxLayout(central)
        main.setContentsMargins(18, 16, 18, 16)
        main.setSpacing(12)

        title = QtWidgets.QLabel("RRKAL_displaytools Studio")
        title.setObjectName("title")
        subtitle = QtWidgets.QLabel(
            "Research-oriented Qt workspace：借鑑 Photoshop 的面板精神，但優先服務科研者的可追蹤圖層、可重現 profile 與資料狀態檢查。"
        )
        subtitle.setWordWrap(True)
        main.addWidget(title)
        main.addWidget(subtitle)

        body = QtWidgets.QHBoxLayout()
        body.setSpacing(14)
        main.addLayout(body, stretch=1)

        left = QtWidgets.QVBoxLayout()
        right = QtWidgets.QVBoxLayout()
        body.addLayout(left, stretch=1)
        body.addLayout(right, stretch=1)

        renderer_group = self._group("工具選項 / Renderer 入口")
        renderer_form = QtWidgets.QFormLayout(renderer_group)
        self.style_combo = self._combo(STYLE_PROFILES)
        self.ui_combo = self._combo(UI_BACKENDS)
        self.topo_combo = self._combo(TOPO_SOURCES)
        self.data_combo = self._combo(DATA_MODES)
        self.width_edit = QtWidgets.QLineEdit("1280")
        self.height_edit = QtWidgets.QLineEdit("720")
        self.topo_step_edit = QtWidgets.QLineEdit("48")
        self.arch_edit = QtWidgets.QLineEdit("gpu")
        self.rrkal_manifest_ref_edit = QtWidgets.QLineEdit("")
        self.rrkal_manifest_ref_edit.setPlaceholderText("optional RRKAL manifest path/URL/reference")
        renderer_form.addRow("Style profile", self.style_combo)
        renderer_form.addRow("UI backend", self.ui_combo)
        renderer_form.addRow("Topography", self.topo_combo)
        renderer_form.addRow("Data mode", self.data_combo)
        renderer_form.addRow("Width", self.width_edit)
        renderer_form.addRow("Height", self.height_edit)
        renderer_form.addRow("Topo step", self.topo_step_edit)
        renderer_form.addRow("Taichi arch", self.arch_edit)
        renderer_form.addRow("RRKAL manifest ref", self.rrkal_manifest_ref_edit)
        left.addWidget(renderer_group)

        material_group = self._group("屬性 / 海洋材質")
        material_form = QtWidgets.QFormLayout(material_group)
        self.wave_edit = QtWidgets.QLineEdit("0.22")
        self.roughness_edit = QtWidgets.QLineEdit("0.28")
        self.foam_edit = QtWidgets.QLineEdit("0.12")
        material_form.addRow("Wave strength", self.wave_edit)
        material_form.addRow("Roughness", self.roughness_edit)
        material_form.addRow("Foam", self.foam_edit)
        layer_inspector_note = QtWidgets.QLabel("Active layer inspector：已同步 layer runtime；renderer pick state 會回寫選取結果。")
        layer_inspector_note.setWordWrap(True)
        self.layer_property_labels = {
            "name": QtWidgets.QLabel("尚未選取"),
            "visible": QtWidgets.QLabel("-"),
            "locked": QtWidgets.QLabel("-"),
            "opacity": QtWidgets.QLabel("-"),
            "blend": QtWidgets.QLabel("-"),
            "renderer_target": QtWidgets.QLabel("-"),
            "diagnostics": QtWidgets.QLabel("-"),
        }
        for property_label in self.layer_property_labels.values():
            property_label.setWordWrap(True)
        material_form.addRow("Layer inspector", layer_inspector_note)
        material_form.addRow("Active layer", self.layer_property_labels["name"])
        material_form.addRow("Visible", self.layer_property_labels["visible"])
        material_form.addRow("Locked", self.layer_property_labels["locked"])
        material_form.addRow("Opacity", self.layer_property_labels["opacity"])
        material_form.addRow("Blend mode", self.layer_property_labels["blend"])
        material_form.addRow("Renderer target", self.layer_property_labels["renderer_target"])
        material_form.addRow("Renderer diagnostics", self.layer_property_labels["diagnostics"])
        layer_property_actions = QtWidgets.QHBoxLayout()
        toggle_selected_visibility = QtWidgets.QPushButton("切換選取可見")
        reset_selected_state = QtWidgets.QPushButton("重設選取 UI 狀態")
        toggle_selected_visibility.clicked.connect(self.toggle_selected_layer_visibility)
        reset_selected_state.clicked.connect(self.reset_selected_layer_controls)
        layer_property_actions.addWidget(toggle_selected_visibility)
        layer_property_actions.addWidget(reset_selected_state)
        material_form.addRow(layer_property_actions)
        self.boundary_highlight_label = QtWidgets.QLabel(self.boundary_highlight_summary())
        self.boundary_highlight_label.setWordWrap(True)
        self.boundary_identity_status_label = QtWidgets.QLabel(self.boundary_identity_status_summary())
        self.boundary_identity_status_label.setWordWrap(True)
        boundary_highlight_button = QtWidgets.QPushButton("疆域強調遮罩設定")
        boundary_highlight_button.clicked.connect(lambda _checked=False: self.open_boundary_highlight_dialog())
        material_form.addRow("Boundary highlight", self.boundary_highlight_label)
        material_form.addRow("Boundary identity", self.boundary_identity_status_label)
        material_form.addRow(boundary_highlight_button)
        self.boundary_highlight_ack_label = QtWidgets.QLabel(
            f"Boundary ack: waiting for {BOUNDARY_HIGHLIGHT_ACK_PATH.name}"
        )
        self.boundary_highlight_ack_label.setWordWrap(True)
        material_form.addRow("Boundary renderer", self.boundary_highlight_ack_label)
        properties_dock = QtWidgets.QDockWidget("Properties", self)
        properties_dock.setObjectName("propertiesDock")
        properties_dock.setAllowedAreas(
            QtCore.Qt.DockWidgetArea.LeftDockWidgetArea
            | QtCore.Qt.DockWidgetArea.RightDockWidgetArea
        )
        properties_dock.setWidget(material_group)
        self.docks["properties"] = properties_dock
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, properties_dock)

        preset_group = self._group("預設 / Looks")
        preset_layout = QtWidgets.QGridLayout(preset_group)
        presets = (
            ("昨天風格基線", self.apply_baseline),
            ("航海/水文", self.apply_maritime),
            ("羊皮紙", self.apply_parchment),
            ("戰術", self.apply_tactical),
            ("最少圖層", self.apply_minimal),
            ("快速 synthetic", self.apply_fast_synthetic),
        )
        for index, (label, callback) in enumerate(presets):
            button = QtWidgets.QPushButton(label)
            button.clicked.connect(callback)
            preset_layout.addWidget(button, index // 2, index % 2)
        left.addWidget(preset_group)

        template_group = self._group("模板 / Profile templates")
        template_layout = QtWidgets.QGridLayout(template_group)
        self.template_combo = QtWidgets.QComboBox()
        load_template_button = QtWidgets.QPushButton("載入模板")
        rescan_template_button = QtWidgets.QPushButton("重掃模板")
        load_template_button.clicked.connect(self.load_selected_template)
        rescan_template_button.clicked.connect(self.refresh_template_list)
        template_layout.addWidget(self.template_combo, 0, 0, 1, 2)
        template_layout.addWidget(load_template_button, 1, 0)
        template_layout.addWidget(rescan_template_button, 1, 1)
        left.addWidget(template_group)
        left.addStretch(1)

        layers_group = self._group("圖層 / Layers")
        layers_layout = QtWidgets.QVBoxLayout(layers_group)
        layer_header = QtWidgets.QWidget()
        layer_header_layout = QtWidgets.QGridLayout(layer_header)
        layer_header_layout.setContentsMargins(0, 0, 0, 0)
        headers = ("Select", "Vis", "Layer", "Lock", "Opacity", "Blend")
        for column, text in enumerate(headers):
            header_label = QtWidgets.QLabel(text)
            header_label.setObjectName("layerHeader")
            layer_header_layout.addWidget(header_label, 0, column)
        layers_layout.addWidget(layer_header)
        for key, label in LAYER_LABELS:
            row = QtWidgets.QWidget()
            row.setObjectName("layerRow")
            row.setProperty("selected", False)
            row_layout = QtWidgets.QGridLayout(row)
            row_layout.setContentsMargins(4, 2, 4, 2)
            row_layout.setHorizontalSpacing(8)
            self.layer_rows[key] = row

            select_button = QtWidgets.QToolButton()
            select_button.setText("選取")
            select_button.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextOnly)
            select_button.clicked.connect(lambda _checked=False, layer_key=key: self.select_layer(layer_key))

            check = QtWidgets.QCheckBox()
            check.setToolTip(f"Renderer visibility flag: {BOOL_FLAGS[key]}")
            check.stateChanged.connect(self.refresh_command_preview)
            check.stateChanged.connect(lambda _state, self=self: self.refresh_layer_stack_status())
            self.checks[key] = check

            layer_label = QtWidgets.QLabel(label)

            lock = QtWidgets.QCheckBox()
            lock.setToolTip("Lock is honored by renderer runtime sync for visibility, opacity, and blend updates.")
            lock.stateChanged.connect(lambda _state, self=self: self.refresh_layer_stack_status())
            self.layer_locks[key] = lock

            opacity = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
            opacity.setRange(0, 100)
            opacity.setValue(100)
            opacity.setToolTip("Renderer runtime opacity sync is live for supported layers.")
            opacity.valueChanged.connect(lambda _value, self=self: self.refresh_layer_stack_status())
            self.layer_opacity[key] = opacity

            blend = QtWidgets.QComboBox()
            blend.addItems(BLEND_MODES)
            blend.setToolTip("Renderer runtime blend sync is live for hydrology, boundary, and point/icon overlays.")
            blend.currentTextChanged.connect(lambda _text, self=self: self.refresh_layer_stack_status())
            self.layer_blends[key] = blend
            if key in BOUNDARY_HIGHLIGHT_LAYER_KEYS:
                boundary_tooltip = "雙擊開啟疆域/領海/EEZ/公海強調遮罩控制。"
                row.setToolTip(boundary_tooltip)
                layer_label.setToolTip(boundary_tooltip)
                row.installEventFilter(self)
                layer_label.installEventFilter(self)
                self.boundary_layer_event_targets[id(row)] = key
                self.boundary_layer_event_targets[id(layer_label)] = key

            row_layout.addWidget(select_button, 0, 0)
            row_layout.addWidget(check, 0, 1)
            row_layout.addWidget(layer_label, 0, 2)
            row_layout.addWidget(lock, 0, 3)
            row_layout.addWidget(opacity, 0, 4)
            row_layout.addWidget(blend, 0, 5)
            layers_layout.addWidget(row)
        self.selected_layer_label = QtWidgets.QLabel("目前選取圖層：尚未選取")
        self.selected_layer_label.setObjectName("selectedLayer")
        layers_layout.addWidget(self.selected_layer_label)
        self.layer_stack_note = QtWidgets.QLabel("Lock / Opacity / Blend 已接 renderer runtime；未支援圖層會在 renderer_sync 標示。")
        self.layer_stack_note.setWordWrap(True)
        layers_layout.addWidget(self.layer_stack_note)
        self.layer_undo_label = QtWidgets.QLabel("Layer undo: 0 snapshots")
        self.layer_undo_label.setWordWrap(True)
        layers_layout.addWidget(self.layer_undo_label)
        self.layer_runtime_state_label = QtWidgets.QLabel(f"Layer runtime bridge: waiting for {LAYER_RUNTIME_STATE_PATH.name}")
        self.layer_runtime_state_label.setWordWrap(True)
        layers_layout.addWidget(self.layer_runtime_state_label)
        self.layer_runtime_ack_label = QtWidgets.QLabel(f"Renderer ack: waiting for {LAYER_RUNTIME_ACK_PATH.name}")
        self.layer_runtime_ack_label.setWordWrap(True)
        layers_layout.addWidget(self.layer_runtime_ack_label)
        self.layer_pick_state_label = QtWidgets.QLabel(f"Layer pick: waiting for {LAYER_PICK_STATE_PATH.name}")
        self.layer_pick_state_label.setWordWrap(True)
        layers_layout.addWidget(self.layer_pick_state_label)
        demo = QtWidgets.QCheckBox("閉環展示 preset（會覆蓋部分設定）")
        demo.stateChanged.connect(self.refresh_command_preview)
        self.checks["demo_closed_loop"] = demo
        layers_layout.addWidget(demo)
        layer_actions = (
            ("水文開/關", self.toggle_hydrology_layers),
            ("海域開/關", self.toggle_maritime_layers),
            ("交通開/關", self.toggle_transport_layers),
            ("輔助開/關", self.toggle_visual_aids),
            ("Solo 選取圖層", self.solo_selected_layer_visibility),
            ("還原 Solo 前可見性", self.restore_layer_visibility_snapshot),
            ("Undo 圖層狀態", self.undo_layer_stack_state),
            ("顯示 layer runtime JSON", self.show_layer_runtime_state),
            ("顯示 layer pick JSON", self.show_layer_pick_state),
            ("重設 UI 圖層狀態", self.reset_layer_stack_controls),
        )
        layer_actions_layout = QtWidgets.QGridLayout()
        for index, (label, callback) in enumerate(layer_actions):
            button = QtWidgets.QPushButton(label)
            button.clicked.connect(callback)
            layer_actions_layout.addWidget(button, index // 2, index % 2)
        layers_layout.addLayout(layer_actions_layout)
        self.select_layer("show_grid")
        layers_dock = QtWidgets.QDockWidget("Layers", self)
        layers_dock.setObjectName("layersDock")
        layers_dock.setAllowedAreas(
            QtCore.Qt.DockWidgetArea.LeftDockWidgetArea
            | QtCore.Qt.DockWidgetArea.RightDockWidgetArea
        )
        layers_dock.setWidget(layers_group)
        self.docks["layers"] = layers_dock
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, layers_dock)

        command_group = self._group("中央預覽 / Canvas, Command and JSON preview")
        command_layout = QtWidgets.QVBoxLayout(command_group)
        self.canvas_preview_label = QtWidgets.QLabel("Canvas Preview")
        self.canvas_preview_label.setObjectName("canvasPreview")
        self.canvas_preview_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.canvas_preview_label.setMinimumHeight(220)
        self.canvas_preview_label.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.canvas_preview_label.setMouseTracking(True)
        self.canvas_preview_label.installEventFilter(self)
        command_layout.addWidget(self.canvas_preview_label)
        self.canvas_meta_label = QtWidgets.QLabel("Canvas state: -")
        self.canvas_meta_label.setObjectName("canvasMeta")
        self.canvas_meta_label.setWordWrap(True)
        command_layout.addWidget(self.canvas_meta_label)
        zoom_row = QtWidgets.QHBoxLayout()
        zoom_row.addWidget(QtWidgets.QLabel("Canvas zoom"))
        self.canvas_zoom_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.canvas_zoom_slider.setRange(25, 200)
        self.canvas_zoom_slider.setValue(100)
        self.canvas_zoom_slider.valueChanged.connect(lambda _value, self=self: self.refresh_canvas_preview())
        zoom_row.addWidget(self.canvas_zoom_slider)
        command_layout.addLayout(zoom_row)
        self.command_text = QtWidgets.QPlainTextEdit()
        self.command_text.setReadOnly(True)
        self.command_text.setMinimumHeight(150)
        command_layout.addWidget(self.command_text)
        right.addWidget(command_group, stretch=1)

        actions_group = self._group("動作 / Actions")
        actions = QtWidgets.QGridLayout(actions_group)
        refresh_button = QtWidgets.QPushButton("刷新命令")
        copy_button = QtWidgets.QPushButton("複製命令")
        copy_portable_button = QtWidgets.QPushButton("複製可攜命令")
        save_button = QtWidgets.QPushButton("儲存配置")
        load_button = QtWidgets.QPushButton("載入配置")
        open_templates_button = QtWidgets.QPushButton("模板目錄")
        open_local_profiles_button = QtWidgets.QPushButton("本機配置")
        export_packet_button = QtWidgets.QPushButton("匯出啟動包")
        capabilities_button = QtWidgets.QPushButton("Renderer 能力")
        closed_loop_button = QtWidgets.QPushButton("閉環狀態")
        layer_manifest_button = QtWidgets.QPushButton("圖層 manifest")
        canvas_state_button = QtWidgets.QPushButton("Canvas state")
        thumbnail_button = QtWidgets.QPushButton("Renderer thumbnail")
        live_preview_button = QtWidgets.QPushButton("Live preview")
        smoke_button = QtWidgets.QPushButton("Smoke check")
        launch_button = QtWidgets.QPushButton("啟動地球儀")
        restart_button = QtWidgets.QPushButton("套用並重啟")
        stop_button = QtWidgets.QPushButton("停止本面板啟動的程序")
        refresh_button.clicked.connect(self.refresh_command_preview)
        copy_button.clicked.connect(self.copy_command_to_clipboard)
        copy_portable_button.clicked.connect(self.copy_portable_command_to_clipboard)
        save_button.clicked.connect(self.save_profile_dialog)
        load_button.clicked.connect(self.load_profile_dialog)
        open_templates_button.clicked.connect(self.open_template_dir)
        open_local_profiles_button.clicked.connect(self.open_local_profile_dir)
        export_packet_button.clicked.connect(self.export_launch_packet_dialog)
        capabilities_button.clicked.connect(self.show_renderer_capabilities)
        closed_loop_button.clicked.connect(self.show_closed_loop_status)
        layer_manifest_button.clicked.connect(self.show_layer_manifest)
        canvas_state_button.clicked.connect(self.show_canvas_state_preview)
        thumbnail_button.clicked.connect(self.show_latest_renderer_thumbnail)
        live_preview_button.clicked.connect(self.show_live_renderer_preview)
        smoke_button.clicked.connect(self.run_smoke_check)
        launch_button.clicked.connect(self.launch_renderer)
        restart_button.clicked.connect(self.restart_renderer)
        stop_button.clicked.connect(self.stop_renderer)
        action_buttons = (
            refresh_button,
            copy_button,
            copy_portable_button,
            save_button,
            load_button,
            open_templates_button,
            open_local_profiles_button,
            export_packet_button,
            capabilities_button,
            closed_loop_button,
            layer_manifest_button,
            canvas_state_button,
            thumbnail_button,
            live_preview_button,
            smoke_button,
            launch_button,
            restart_button,
            stop_button,
        )
        for index, button in enumerate(action_buttons):
            actions.addWidget(button, index // 4, index % 4)
        right.addWidget(actions_group)

        self.status = QtWidgets.QLabel("尚未啟動 renderer")
        main.addWidget(self.status)

        self._connect_preview_signals()
        self.setStyleSheet(
            """
            QWidget { font-family: 'Microsoft JhengHei UI', 'Segoe UI'; font-size: 10.5pt; }
            QLabel#title { font-size: 18pt; font-weight: 700; }
            QGroupBox { font-weight: 700; border: 1px solid #8aa0b6; border-radius: 8px; margin-top: 12px; padding: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 4px; }
            QPushButton { padding: 7px 10px; }
            QPlainTextEdit { font-family: Consolas, 'Cascadia Mono', monospace; }
            QLabel#navigatorPreview { background: #202832; color: #d8e6f3; border: 1px dashed #8aa0b6; }
            QLabel#layerHeader { color: #587087; font-size: 8.5pt; font-weight: 700; }
            QWidget#layerRow { border-bottom: 1px solid #d6e0ea; }
            QWidget#layerRow[selected="true"] { background: #dceeff; border: 1px solid #5b8db8; }
            QLabel#selectedLayer { color: #23435f; font-weight: 700; padding-top: 6px; }
            QLabel#toolPaletteTitle { color: #23435f; font-weight: 700; padding-top: 6px; }
            QLabel#canvasPreview {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #142331, stop:0.52 #1f4d5e, stop:1 #d7c29b);
                color: #f3f7f9;
                border: 2px solid #5b8db8;
                border-radius: 10px;
                font-size: 13pt;
                font-weight: 700;
                padding: 16px;
            }
            QLabel#canvasMeta { color: #31475a; font-weight: 600; }
            """
        )

    def _build_menu_bar(self) -> None:
        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction("Save Profile", self.save_profile_dialog)
        file_menu.addAction("Load Profile", self.load_profile_dialog)
        file_menu.addAction("Export Launch Packet", self.export_launch_packet_dialog)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        renderer_menu = self.menuBar().addMenu("Renderer")
        renderer_menu.addAction("Launch", self.launch_renderer)
        renderer_menu.addAction("Apply and Restart", self.restart_renderer)
        renderer_menu.addAction("Stop", self.stop_renderer)
        renderer_menu.addSeparator()
        renderer_menu.addAction("Capabilities JSON", self.show_renderer_capabilities)
        renderer_menu.addAction("Closed-loop Status JSON", self.show_closed_loop_status)
        renderer_menu.addAction("Layer Manifest JSON", self.show_layer_manifest)
        renderer_menu.addAction("Latest Output Thumbnail", self.show_latest_renderer_thumbnail)
        renderer_menu.addAction("Live Preview Stream", self.show_live_renderer_preview)

        window_menu = self.menuBar().addMenu("Window")
        window_menu.addAction("Open Template Folder", self.open_template_dir)
        window_menu.addAction("Open Local Profile Folder", self.open_local_profile_dir)
        window_menu.addSeparator()
        window_menu.addAction("Save Workspace Layout", self.save_workspace_layout)
        window_menu.addAction("Load Workspace Layout", self.load_workspace_layout)
        window_menu.addAction("Reset Saved Workspace Layout", self.reset_workspace_layout)
        workspace_presets = window_menu.addMenu("Workspace Presets")
        workspace_presets.addAction("Default", lambda _checked=False: self.apply_workspace_preset("default"))
        workspace_presets.addAction("Maritime", lambda _checked=False: self.apply_workspace_preset("maritime"))
        workspace_presets.addAction("Tactical", lambda _checked=False: self.apply_workspace_preset("tactical"))
        workspace_presets.addAction("Parchment", lambda _checked=False: self.apply_workspace_preset("parchment"))
        workspace_presets.addAction("Review", lambda _checked=False: self.apply_workspace_preset("review"))

        help_menu = self.menuBar().addMenu("Help")
        help_menu.addAction("Smoke Check", self.run_smoke_check)

    def _build_tool_dock(self) -> None:
        dock = QtWidgets.QDockWidget("Tools", self)
        dock.setObjectName("toolsDock")
        dock.setAllowedAreas(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea | QtCore.Qt.DockWidgetArea.RightDockWidgetArea)
        tools = QtWidgets.QWidget(dock)
        layout = QtWidgets.QVBoxLayout(tools)
        layout.setContentsMargins(8, 8, 8, 8)
        palette_title = QtWidgets.QLabel("工具箱 / Tool Palette")
        palette_title.setObjectName("toolPaletteTitle")
        layout.addWidget(palette_title)
        tool_grid = QtWidgets.QGridLayout()
        for index, (mode, label, hint) in enumerate(TOOL_MODES):
            button = QtWidgets.QToolButton()
            button.setText(label)
            button.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextOnly)
            button.setCheckable(True)
            button.setToolTip(hint)
            button.clicked.connect(lambda _checked=False, tool_mode=mode: self.set_active_tool(tool_mode))
            self.tool_buttons[mode] = button
            tool_grid.addWidget(button, index // 2, index % 2)
        layout.addLayout(tool_grid)
        self.tool_target_label = QtWidgets.QLabel("Target layer: -")
        self.tool_target_label.setWordWrap(True)
        layout.addWidget(self.tool_target_label)
        tool_note = QtWidgets.QLabel("Select 只負責選取/指定 active layer；Brush/Mask 暫不納入本輪 UI。")
        tool_note.setWordWrap(True)
        layout.addWidget(tool_note)
        pin_group = QtWidgets.QGroupBox("Pin Annotation")
        pin_form = QtWidgets.QFormLayout(pin_group)
        self.pin_type_combo = QtWidgets.QComboBox()
        self.pin_type_combo.addItems(PIN_TYPES)
        self.pin_label_edit = QtWidgets.QLineEdit("Station A")
        self.pin_note_edit = QtWidgets.QLineEdit("Geodetic marker; renderer rotates and occludes it with the globe")
        self.pin_lat_edit = QtWidgets.QLineEdit("0.0")
        self.pin_lon_edit = QtWidgets.QLineEdit("0.0")
        self.pin_priority_spin = QtWidgets.QSpinBox()
        self.pin_priority_spin.setRange(0, 100)
        self.pin_priority_spin.setValue(50)
        self.pin_priority_spin.setToolTip("Renderer label priority: selected Pin wins first, then higher priority labels are placed earlier.")
        self.pin_label_mode_combo = QtWidgets.QComboBox()
        for mode, label, hint in PIN_LABEL_MODES:
            self.pin_label_mode_combo.addItem(label, mode)
            self.pin_label_mode_combo.setItemData(self.pin_label_mode_combo.count() - 1, hint, QtCore.Qt.ItemDataRole.ToolTipRole)
        self.pin_label_mode_combo.setToolTip("Renderer Pin label visibility mode.")
        self.pin_label_min_priority_spin = QtWidgets.QSpinBox()
        self.pin_label_min_priority_spin.setRange(0, 100)
        self.pin_label_min_priority_spin.setValue(50)
        self.pin_label_min_priority_spin.setToolTip("Priority mode only: labels below this threshold are hidden unless selected.")
        self.pin_type_combo.currentTextChanged.connect(lambda _text, self=self: self.refresh_tool_target())
        self.pin_label_edit.textChanged.connect(lambda _text, self=self: self.refresh_tool_target())
        self.pin_note_edit.textChanged.connect(lambda _text, self=self: self.refresh_tool_target())
        self.pin_lat_edit.textChanged.connect(lambda _text, self=self: self.refresh_tool_target())
        self.pin_lon_edit.textChanged.connect(lambda _text, self=self: self.refresh_tool_target())
        self.pin_priority_spin.valueChanged.connect(lambda _value, self=self: self.refresh_tool_target())
        self.pin_label_mode_combo.currentIndexChanged.connect(lambda _value, self=self: self.refresh_tool_target())
        self.pin_label_min_priority_spin.valueChanged.connect(lambda _value, self=self: self.refresh_tool_target())
        pin_form.addRow("Type", self.pin_type_combo)
        pin_form.addRow("Label", self.pin_label_edit)
        pin_form.addRow("Latitude", self.pin_lat_edit)
        pin_form.addRow("Longitude", self.pin_lon_edit)
        pin_form.addRow("Label Priority", self.pin_priority_spin)
        pin_form.addRow("Label Mode", self.pin_label_mode_combo)
        pin_form.addRow("Min Label Priority", self.pin_label_min_priority_spin)
        pin_form.addRow("Note", self.pin_note_edit)
        pin_actions = QtWidgets.QHBoxLayout()
        add_pin_button = QtWidgets.QPushButton("加入 Pin")
        remove_pin_button = QtWidgets.QPushButton("移除選取 Pin")
        use_cursor_button = QtWidgets.QPushButton("用游標填入 Pin")
        show_pin_pick_button = QtWidgets.QPushButton("顯示 Pin pick JSON")
        add_pin_button.clicked.connect(self.add_pin_marker)
        remove_pin_button.clicked.connect(self.remove_selected_pin_marker)
        use_cursor_button.clicked.connect(self.fill_pin_from_cursor)
        show_pin_pick_button.clicked.connect(self.show_pin_pick_state)
        pin_actions.addWidget(add_pin_button)
        pin_actions.addWidget(remove_pin_button)
        pin_actions.addWidget(use_cursor_button)
        pin_actions.addWidget(show_pin_pick_button)
        pin_form.addRow(pin_actions)
        self.pin_list = QtWidgets.QListWidget()
        self.pin_list.setMinimumHeight(110)
        self.pin_list.currentRowChanged.connect(self.select_pin_marker)
        pin_form.addRow("Pins", self.pin_list)
        self.pin_input_ack_label = QtWidgets.QLabel(f"Renderer input ack: waiting for {PIN_INPUT_ACK_PATH.name}")
        self.pin_input_ack_label.setWordWrap(True)
        pin_form.addRow("Renderer Input", self.pin_input_ack_label)
        self.pin_pick_state_label = QtWidgets.QLabel(f"Renderer bridge: waiting for {PIN_PICK_STATE_PATH.name}")
        self.pin_pick_state_label.setWordWrap(True)
        pin_form.addRow("Renderer Pick", self.pin_pick_state_label)
        self.pin_pick_ack_label = QtWidgets.QLabel(f"Qt ack: waiting for {PIN_PICK_ACK_PATH.name}")
        self.pin_pick_ack_label.setWordWrap(True)
        pin_form.addRow("Qt Ack", self.pin_pick_ack_label)
        pin_form.addRow("Status", QtWidgets.QLabel("Manual lat/lon Pins; renderer click/hover sync uses JSON bridge."))
        layout.addWidget(pin_group)

        quick_title = QtWidgets.QLabel("快捷 / Presets")
        quick_title.setObjectName("toolPaletteTitle")
        layout.addWidget(quick_title)
        tool_actions = (
            ("Baseline", self.apply_baseline),
            ("Maritime", self.apply_maritime),
            ("Parchment", self.apply_parchment),
            ("Tactical", self.apply_tactical),
            ("Smoke", self.run_smoke_check),
            ("Caps", self.show_renderer_capabilities),
            ("Loops", self.show_closed_loop_status),
            ("Layers", self.show_layer_manifest),
        )
        for label, callback in tool_actions:
            button = QtWidgets.QToolButton()
            button.setText(label)
            button.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextOnly)
            button.clicked.connect(callback)
            layout.addWidget(button)
        self.set_active_tool("move")
        layout.addStretch(1)
        dock.setWidget(tools)
        self.docks["tools"] = dock
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, dock)

    def _build_auxiliary_docks(self) -> None:
        navigator_dock = QtWidgets.QDockWidget("Navigator", self)
        navigator_dock.setObjectName("navigatorDock")
        navigator = QtWidgets.QWidget(navigator_dock)
        navigator_layout = QtWidgets.QVBoxLayout(navigator)
        navigator_layout.setContentsMargins(10, 10, 10, 10)
        preview = QtWidgets.QLabel(
            "Navigator preview\n"
            "Live renderer pixels are available from the central Canvas Preview."
        )
        preview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        preview.setMinimumHeight(120)
        preview.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        preview.setObjectName("navigatorPreview")
        navigator_layout.addWidget(preview)
        zoom_row = QtWidgets.QHBoxLayout()
        zoom_row.addWidget(QtWidgets.QLabel("Zoom"))
        self.zoom_placeholder = QtWidgets.QLineEdit("100%")
        self.zoom_placeholder.setEnabled(False)
        zoom_row.addWidget(self.zoom_placeholder)
        navigator_layout.addLayout(zoom_row)
        navigator_dock.setWidget(navigator)
        self.docks["navigator"] = navigator_dock
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, navigator_dock)

        history_dock = QtWidgets.QDockWidget("History", self)
        history_dock.setObjectName("historyDock")
        self.history_list = QtWidgets.QListWidget()
        for item in (
            "✅ Qt Studio workspace loaded",
            "✅ Profile/template launch flow",
            "✅ Layer manifest/capabilities preview",
            "✅ Live renderer layer visibility/opacity/blend sync",
            "✅ Selected-layer renderer picking bridge",
            "✅ Layer stack undo snapshots",
            "🚧 Timeline/keyframes",
            "🚧 Global document undo stack",
        ):
            self.history_list.addItem(item)
        for item in self.layer_runtime_history:
            self.history_list.insertItem(0, item)
        for item in self.pin_pick_history:
            self.history_list.insertItem(0, item)
        history_dock.setWidget(self.history_list)
        self.docks["history"] = history_dock
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, history_dock)

        provenance_dock = QtWidgets.QDockWidget("Provenance", self)
        provenance_dock.setObjectName("provenanceDock")
        provenance = QtWidgets.QWidget(provenance_dock)
        provenance_layout = QtWidgets.QVBoxLayout(provenance)
        provenance_layout.setContentsMargins(10, 10, 10, 10)
        provenance_note = QtWidgets.QLabel("科研可重現性摘要：目前 UI 狀態、資料來源、圖層、profile 與可攜命令。")
        provenance_note.setWordWrap(True)
        provenance_layout.addWidget(provenance_note)
        self.provenance_text = QtWidgets.QPlainTextEdit()
        self.provenance_text.setReadOnly(True)
        self.provenance_text.setMinimumHeight(180)
        provenance_layout.addWidget(self.provenance_text)
        copy_provenance = QtWidgets.QPushButton("複製 provenance summary")
        copy_provenance.clicked.connect(self.copy_research_provenance)
        provenance_layout.addWidget(copy_provenance)
        provenance_dock.setWidget(provenance)
        self.docks["provenance"] = provenance_dock
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, provenance_dock)

    @QtCore.pyqtSlot()
    def save_workspace_layout(self) -> None:
        WORKSPACE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": "rrkal_displaytools.qt_workspace_layout.v1",
            "geometry": bytes(self.saveGeometry().toBase64()).decode("ascii"),
            "window_state": bytes(self.saveState().toBase64()).decode("ascii"),
        }
        WORKSPACE_STATE_PATH.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.status.setText(f"已儲存 workspace layout：{WORKSPACE_STATE_PATH}")
        self.statusBar().showMessage("Workspace layout saved", 4000)

    def load_workspace_layout(self, silent: bool = False) -> None:
        if not WORKSPACE_STATE_PATH.exists():
            if not silent:
                self.status.setText("尚未儲存 workspace layout")
            return
        try:
            payload = json.loads(WORKSPACE_STATE_PATH.read_text(encoding="utf-8"))
            geometry = QtCore.QByteArray.fromBase64(str(payload.get("geometry", "")).encode("ascii"))
            window_state = QtCore.QByteArray.fromBase64(str(payload.get("window_state", "")).encode("ascii"))
            if not geometry.isEmpty():
                self.restoreGeometry(geometry)
            if not window_state.isEmpty():
                self.restoreState(window_state)
        except Exception as exc:
            if not silent:
                self.status.setText(f"Workspace layout 載入失敗：{exc}")
            return
        if not silent:
            self.status.setText(f"已載入 workspace layout：{WORKSPACE_STATE_PATH}")
        self.statusBar().showMessage("Workspace layout loaded", 4000)

    @QtCore.pyqtSlot()
    def reset_workspace_layout(self) -> None:
        if WORKSPACE_STATE_PATH.exists():
            WORKSPACE_STATE_PATH.unlink()
        self.status.setText("已移除已儲存 workspace layout；下次啟動使用預設佈局")
        self.statusBar().showMessage("Saved workspace layout reset", 4000)

    def apply_workspace_preset(self, preset: str) -> None:
        for dock in self.docks.values():
            dock.setFloating(False)
            dock.show()
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, self.docks["tools"])
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.docks["layers"])
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.docks["properties"])
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.docks["navigator"])
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.docks["history"])
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.docks["provenance"])
        if preset == "maritime":
            self.apply_maritime()
            self.tabifyDockWidget(self.docks["layers"], self.docks["properties"])
            self.docks["layers"].raise_()
        elif preset == "tactical":
            self.apply_tactical()
            self.tabifyDockWidget(self.docks["navigator"], self.docks["history"])
            self.docks["layers"].raise_()
        elif preset == "parchment":
            self.apply_parchment()
            self.tabifyDockWidget(self.docks["properties"], self.docks["navigator"])
            self.docks["properties"].raise_()
        elif preset == "review":
            self.apply_baseline()
            self.tabifyDockWidget(self.docks["layers"], self.docks["properties"])
            self.tabifyDockWidget(self.docks["navigator"], self.docks["history"])
            self.tabifyDockWidget(self.docks["history"], self.docks["provenance"])
            self.docks["history"].raise_()
        else:
            self.apply_baseline()
            self.docks["layers"].raise_()
        self.status.setText(f"已套用 workspace preset：{preset}")
        self.statusBar().showMessage(f"Workspace preset applied: {preset}", 4000)

    def _group(self, title: str) -> QtWidgets.QGroupBox:
        return QtWidgets.QGroupBox(title)

    def _combo(self, values: tuple[str, ...]) -> QtWidgets.QComboBox:
        combo = QtWidgets.QComboBox()
        combo.addItems(values)
        return combo

    def _connect_preview_signals(self) -> None:
        for combo in (self.style_combo, self.ui_combo, self.topo_combo, self.data_combo):
            combo.currentTextChanged.connect(self.refresh_command_preview)
        for edit in (
            self.width_edit,
            self.height_edit,
            self.topo_step_edit,
            self.arch_edit,
            self.rrkal_manifest_ref_edit,
            self.wave_edit,
            self.roughness_edit,
            self.foam_edit,
        ):
            edit.textChanged.connect(self.refresh_command_preview)

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if event.type() == QtCore.QEvent.Type.MouseButtonDblClick:
            layer_key = self.boundary_layer_event_targets.get(id(watched))
            if layer_key is not None:
                self.open_boundary_highlight_dialog(layer_key)
                return True
        if watched is self.canvas_preview_label and event.type() == QtCore.QEvent.Type.MouseMove:
            position = event.position()
            width = max(1, self.canvas_preview_label.width() if self.canvas_preview_label is not None else 1)
            height = max(1, self.canvas_preview_label.height() if self.canvas_preview_label is not None else 1)
            x_ratio = min(max(position.x() / width, 0.0), 1.0)
            y_ratio = min(max(position.y() / height, 0.0), 1.0)
            self.cursor_longitude = x_ratio * 360.0 - 180.0
            self.cursor_latitude = 90.0 - y_ratio * 180.0
            self.refresh_canvas_preview()
        if watched is self.canvas_preview_label and event.type() == QtCore.QEvent.Type.MouseButtonPress:
            if self.active_tool == "select" and event.button() == QtCore.Qt.MouseButton.LeftButton:
                key = self.canvas_layer_hit_key(float(event.position().y()))
                if key is not None:
                    label = next((text for layer_key, text in LAYER_LABELS if layer_key == key), key)
                    self.select_layer(key)
                    self.status.setText(f"Canvas Select 命中圖層：{label}")
                    return True
        return super().eventFilter(watched, event)

    def build_command(self) -> list[str]:
        cmd = [
            sys.executable,
            str(RENDERER),
            "--style-profile",
            self.style_combo.currentText(),
            "--ui",
            self.ui_combo.currentText(),
            "--topo-source",
            self.topo_combo.currentText(),
            "--data-mode",
            self.data_combo.currentText(),
            "--width",
            self.width_edit.text().strip() or "1280",
            "--height",
            self.height_edit.text().strip() or "720",
            "--topo-step",
            self.topo_step_edit.text().strip() or "48",
            "--ti-arch",
            self.arch_edit.text().strip() or "gpu",
            "--ocean-wave-strength",
            self.wave_edit.text().strip() or "0.22",
            "--ocean-roughness",
            self.roughness_edit.text().strip() or "0.28",
            "--ocean-foam",
            self.foam_edit.text().strip() or "0.12",
            "--preview-frame-file",
            str(RENDERER_PREVIEW_FRAME_PATH),
            "--preview-frame-interval",
            str(RENDERER_PREVIEW_FRAME_INTERVAL_S),
        ]
        rrkal_manifest_ref = self.rrkal_manifest_ref_edit.text().strip()
        if rrkal_manifest_ref:
            cmd.extend(["--rrkal-data-manifest-ref", rrkal_manifest_ref])
        for key, flag in BOOL_FLAGS.items():
            enabled = self.checks[key].isChecked()
            cmd.append(f"--{flag}" if enabled else f"--no-{flag}")
        cmd.extend(
            [
                "--pin-label-mode",
                self.current_pin_label_mode(),
                "--pin-label-min-priority",
                str(self.pin_label_min_priority_spin.value() if self.pin_label_min_priority_spin is not None else 50),
                "--pin-pick-state-file",
                str(PIN_PICK_STATE_PATH),
                "--pin-input-ack-file",
                str(PIN_INPUT_ACK_PATH),
                "--boundary-highlight-json",
                json.dumps(self.collect_boundary_highlight_state(), ensure_ascii=False),
                "--boundary-highlight-ack-file",
                str(BOUNDARY_HIGHLIGHT_ACK_PATH),
                "--layer-runtime-state-file",
                str(LAYER_RUNTIME_STATE_PATH),
                "--layer-runtime-ack-file",
                str(LAYER_RUNTIME_ACK_PATH),
                "--layer-pick-state-file",
                str(LAYER_PICK_STATE_PATH),
            ]
        )
        pins = self.collect_research_pins()
        if pins:
            cmd.extend(
                [
                    "--pin-json",
                    json.dumps(
                        {
                            "pins": pins,
                            "selected_pin_id": self.selected_pin_id,
                            "source": "rrkal_displaytools_qt_panel",
                        },
                        ensure_ascii=False,
                    ),
                ]
            )
        return cmd

    def build_portable_command(self) -> list[str]:
        return ["py", "-3", "taichi_global_bathymetry.py", *self.build_command()[2:]]

    def collect_profile(self) -> dict[str, object]:
        return {
            "schema": "rrkal_displaytools.qt_panel_profile.v1",
            "renderer": {
                "style_profile": self.style_combo.currentText(),
                "ui_backend": self.ui_combo.currentText(),
                "topo_source": self.topo_combo.currentText(),
                "data_mode": self.data_combo.currentText(),
                "width": self.width_edit.text().strip(),
                "height": self.height_edit.text().strip(),
                "topo_step": self.topo_step_edit.text().strip(),
                "taichi_arch": self.arch_edit.text().strip(),
                "rrkal_data_manifest_ref": self.rrkal_manifest_ref_edit.text().strip(),
            },
            "ocean_material": {
                "wave_strength": self.wave_edit.text().strip(),
                "roughness": self.roughness_edit.text().strip(),
                "foam": self.foam_edit.text().strip(),
            },
            "layers": {key: check.isChecked() for key, check in self.checks.items()},
            "selected_layer": self.selected_layer_key,
            "selected_pin_id": self.selected_pin_id,
            "layer_stack_ui": self.collect_layer_stack_ui(),
            "tool_state": self.collect_tool_state(),
            "pins": self.collect_research_pins(),
            "boundary_highlight": self.collect_boundary_highlight_state(),
            "canvas_preview": self.collect_canvas_preview_state(),
        }

    def collect_launch_packet(self) -> dict[str, object]:
        return {
            "schema": "rrkal_displaytools.launch_packet.v1",
            "created_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "repo_role": "RRKAL displaytools renderer launch state",
            "rrkal_boundary": {
                "rrkal_owns": [
                    "dataset discovery",
                    "download/import/install registry",
                    "manifest/cache governance",
                ],
                "displaytools_owns": [
                    "renderer launch flags",
                    "layer/style/material operator state",
                    "visualization frontend",
                ],
            },
            "profile": self.collect_profile(),
            "rrkal_data_manifest_ref": self.rrkal_manifest_ref_edit.text().strip(),
            "rrkal_data_manifest_ref_boundary": "Reference-only handoff field; displaytools does not discover, download, validate, import, or govern this manifest.",
            "selected_layer": self.selected_layer_key,
            "active_layer_diagnostics": self.active_layer_diagnostics_packet(),
            "selected_pin_id": self.selected_pin_id,
            "layer_stack_ui": self.collect_layer_stack_ui(),
            "tool_state": self.collect_tool_state(),
            "pins": self.collect_research_pins(),
            "boundary_highlight": self.collect_boundary_highlight_state(),
            "canvas_preview": self.collect_canvas_preview_state(),
            "closed_loop_status": renderer_closed_loop_status_packet(),
            "boundary_highlight_ack_file": str(BOUNDARY_HIGHLIGHT_ACK_PATH),
            "pin_input_ack_file": str(PIN_INPUT_ACK_PATH),
            "pin_pick_state_file": str(PIN_PICK_STATE_PATH),
            "pin_pick_ack_file": str(PIN_PICK_ACK_PATH),
            "layer_runtime_state_file": str(LAYER_RUNTIME_STATE_PATH),
            "layer_runtime_ack_file": str(LAYER_RUNTIME_ACK_PATH),
            "layer_pick_state_file": str(LAYER_PICK_STATE_PATH),
            "command": self.build_command(),
            "command_line": subprocess.list2cmdline(self.build_command()),
            "portable_command": self.build_portable_command(),
            "portable_command_line": subprocess.list2cmdline(self.build_portable_command()),
        }

    def renderer_thumbnail_profile_path(self) -> str | None:
        if self.renderer_thumbnail_path is None:
            return None
        try:
            return str(self.renderer_thumbnail_path.relative_to(ROOT))
        except ValueError:
            return str(self.renderer_thumbnail_path)

    def display_renderer_preview_path(self, path: Path) -> str:
        try:
            return str(path.relative_to(ROOT))
        except ValueError:
            return str(path)

    def collect_canvas_preview_state(self) -> dict[str, object]:
        renderer_sync = {
            "state": "ui_state_preview",
            "thumbnail": "static_renderer_output_thumbnail",
            "live_file_stream": "file_based_live_renderer_frame_stream",
        }.get(self.canvas_preview_mode, "ui_state_preview")
        return {
            "schema": "rrkal_displaytools.canvas_preview.v1",
            "mode": self.canvas_preview_mode,
            "renderer_thumbnail_path": self.renderer_thumbnail_profile_path(),
            "preview_frame_path": str(RENDERER_PREVIEW_FRAME_PATH.relative_to(ROOT)),
            "preview_frame_interval_s": RENDERER_PREVIEW_FRAME_INTERVAL_S,
            "renderer_sync": renderer_sync,
        }

    def collect_layer_stack_ui(self) -> dict[str, dict[str, object]]:
        stack: dict[str, dict[str, object]] = {}
        for key, _label in LAYER_LABELS:
            stack[key] = {
                "locked": self.layer_locks[key].isChecked(),
                "opacity": self.layer_opacity[key].value(),
                "blend_mode": self.layer_blends[key].currentText(),
                "selected": key == self.selected_layer_key,
                "renderer_sync": self.layer_renderer_sync_status(key),
            }
        return stack

    def layer_renderer_sync_status(self, key: str) -> str:
        visibility_live = {
            "show_grid",
            "show_stars",
            "lake_layer",
            "river_layer",
            "border_layer",
            "territorial_sea_layer",
            "eez_layer",
            "high_seas_layer",
            "aircraft_layer",
            "pin_layer",
            "vehicle_icons",
            "ocean_material",
            "terrain_contours",
            "scale_bar",
        }
        opacity_live = {
            "lake_layer",
            "river_layer",
            "border_layer",
            "territorial_sea_layer",
            "eez_layer",
            "high_seas_layer",
            "aircraft_layer",
            "pin_layer",
            "vehicle_icons",
            "terrain_contours",
            "scale_bar",
        }
        blend_live = {
            "lake_layer",
            "river_layer",
            "border_layer",
            "territorial_sea_layer",
            "eez_layer",
            "high_seas_layer",
            "aircraft_layer",
            "pin_layer",
            "vehicle_icons",
        }
        live = []
        if key in visibility_live:
            live.append("visibility")
        if key in opacity_live:
            live.append("opacity")
        if key in blend_live:
            live.append("blend")
        if not live:
            return "planned"
        return f"live: {', '.join(live)}"

    def collect_layer_runtime_state(self) -> dict[str, object]:
        layers = self.collect_layer_stack_ui()
        for key, _label in LAYER_LABELS:
            if key in self.checks and key in layers:
                layers[key]["visible"] = self.checks[key].isChecked()
        visible_layers = [key for key, _label in LAYER_LABELS if key in self.checks and self.checks[key].isChecked()]
        locked_layers = [key for key, _label in LAYER_LABELS if key in self.layer_locks and self.layer_locks[key].isChecked()]
        selected_renderer_layer = (
            LAYER_RUNTIME_ID_ALIASES.get(self.selected_layer_key, self.selected_layer_key)
            if self.selected_layer_key
            else None
        )
        selected_layer_state = layers.get(self.selected_layer_key) if self.selected_layer_key else None
        selected_layer_label = next(
            (label for key, label in LAYER_LABELS if key == self.selected_layer_key),
            self.selected_layer_key,
        )
        return {
            "schema": "rrkal_displaytools.layer_runtime_state.v1",
            "updated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "source": "rrkal_displaytools_qt_panel",
            "selected_layer": self.selected_layer_key,
            "selected_renderer_layer": selected_renderer_layer,
            "selected_layer_semantic_target": {
                "ui_layer": self.selected_layer_key,
                "renderer_layer": selected_renderer_layer,
                "label": selected_layer_label,
                "state": selected_layer_state,
            }
            if self.selected_layer_key
            else None,
            "visible_layers": visible_layers,
            "locked_layers": locked_layers,
            "layer_visibility_snapshot_active": self.layer_visibility_snapshot is not None,
            "layer_visibility_snapshot": self.layer_visibility_snapshot,
            "layers": layers,
        }

    def write_layer_runtime_state(self) -> None:
        if not self.checks:
            return
        payload = self.collect_layer_runtime_state()
        try:
            LAYER_RUNTIME_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
            LAYER_RUNTIME_STATE_PATH.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            self.layer_runtime_state_last_write_utc = str(payload.get("updated_at_utc", ""))
            self.layer_runtime_state_write_error = None
            self.refresh_layer_runtime_state_label(payload)
            self.append_layer_runtime_history(payload)
        except OSError as exc:
            self.layer_runtime_state_write_error = str(exc)
            self.refresh_layer_runtime_state_label(payload)
            print(f"Unable to write layer runtime state: {exc}")

    def refresh_layer_runtime_state_label(self, payload: dict[str, object] | None = None) -> None:
        if self.layer_runtime_state_label is None:
            return
        if payload is None:
            payload = self.collect_layer_runtime_state()
        visible_layers = payload.get("visible_layers", [])
        visible_count = len(visible_layers) if isinstance(visible_layers, list) else "-"
        selected_layer = str(payload.get("selected_layer") or "-")
        selected_renderer_layer = str(payload.get("selected_renderer_layer") or "-")
        if self.layer_runtime_state_write_error:
            self.layer_runtime_state_label.setText(
                f"Layer runtime bridge: write failed: {self.layer_runtime_state_write_error}"
            )
            return
        last_write = self.layer_runtime_state_last_write_utc or str(payload.get("updated_at_utc", "-"))
        self.layer_runtime_state_label.setText(
            f"Layer runtime bridge: {LAYER_RUNTIME_STATE_PATH.name}; selected={selected_layer}; "
            f"renderer_target={selected_renderer_layer}; visible={visible_count}/{len(LAYER_LABELS)}; "
            f"last_write={last_write}; visibility/opacity live, overlay/split blend live, "
            "selected-layer semantic target live, lock guard live"
        )

    def append_layer_runtime_history(self, payload: dict[str, object]) -> None:
        visible_layers = payload.get("visible_layers", [])
        locked_layers = payload.get("locked_layers", [])
        visible_count = len(visible_layers) if isinstance(visible_layers, list) else 0
        locked_count = len(locked_layers) if isinstance(locked_layers, list) else 0
        signature = json.dumps(
            {
                "selected_layer": payload.get("selected_layer"),
                "visible_layers": visible_layers,
                "locked_layers": locked_layers,
                "snapshot": payload.get("layer_visibility_snapshot_active"),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        if signature == self.layer_runtime_history_signature:
            return
        self.layer_runtime_history_signature = signature
        updated_at = str(payload.get("updated_at_utc", "-"))
        selected_layer = str(payload.get("selected_layer") or "-")
        snapshot = "snapshot" if payload.get("layer_visibility_snapshot_active") else "no snapshot"
        entry = (
            f"↻ Layer runtime {updated_at}: selected={selected_layer}, "
            f"visible={visible_count}/{len(LAYER_LABELS)}, locked={locked_count}, {snapshot}"
        )
        self.layer_runtime_history.insert(0, entry)
        del self.layer_runtime_history[10:]
        if self.history_list is None:
            return
        self.history_list.insertItem(0, entry)
        while self.history_list.count() > 18:
            self.history_list.takeItem(self.history_list.count() - 1)

    def refresh_layer_runtime_ack_state(self) -> None:
        try:
            stat = LAYER_RUNTIME_ACK_PATH.stat()
        except FileNotFoundError:
            if self.layer_runtime_ack_mtime_ns is not None:
                self.layer_runtime_ack_mtime_ns = None
                if self.layer_runtime_ack_label is not None:
                    self.layer_runtime_ack_label.setText(f"Renderer ack: waiting for {LAYER_RUNTIME_ACK_PATH.name}")
            return
        except OSError as exc:
            if self.layer_runtime_ack_label is not None:
                self.layer_runtime_ack_label.setText(f"Renderer ack read failed: {exc}")
            return
        if stat.st_mtime_ns == self.layer_runtime_ack_mtime_ns:
            return
        next_mtime_ns = stat.st_mtime_ns
        try:
            payload = json.loads(LAYER_RUNTIME_ACK_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            if self.layer_runtime_ack_label is not None:
                self.layer_runtime_ack_label.setText(f"Renderer ack parse failed: {exc}")
            return
        self.layer_runtime_ack_mtime_ns = next_mtime_ns
        if isinstance(payload, dict):
            self.layer_runtime_ack_payload = payload
            self.refresh_layer_runtime_ack_label(payload)
            self.refresh_layer_properties()
            self.refresh_research_provenance()

    def refresh_layer_runtime_ack_label(self, payload: dict[str, object]) -> None:
        if self.layer_runtime_ack_label is None:
            return
        event = str(payload.get("event", "-"))
        changed_layers = payload.get("changed_layers", [])
        changed_count = len(changed_layers) if isinstance(changed_layers, list) else "-"
        changed_opacity_layers = payload.get("changed_opacity_layers", [])
        changed_opacity_count = len(changed_opacity_layers) if isinstance(changed_opacity_layers, list) else "-"
        changed_blend_layers = payload.get("changed_blend_layers", [])
        changed_blend_count = len(changed_blend_layers) if isinstance(changed_blend_layers, list) else "-"
        skipped_locked_layers = payload.get("skipped_locked_layers", [])
        skipped_count = len(skipped_locked_layers) if isinstance(skipped_locked_layers, list) else "-"
        boundary_blend = str(payload.get("boundary_aggregate_blend_mode", "-"))
        selected_renderer_layer = str(payload.get("selected_renderer_layer") or "-")
        frame_index = payload.get("frame_index", "-")
        updated_at = str(payload.get("updated_at_utc", "-"))
        error = payload.get("error")
        if error:
            self.layer_runtime_ack_label.setText(f"Renderer ack: event={event}, error={error}, updated={updated_at}")
            return
        self.layer_runtime_ack_label.setText(
            f"Renderer ack: event={event}, changed={changed_count}, opacity={changed_opacity_count}, "
            f"blend={changed_blend_count}, "
            f"target={selected_renderer_layer}, boundary_blend={boundary_blend}, "
            f"skipped_locked={skipped_count}, frame={frame_index}, updated={updated_at}"
        )

    def refresh_layer_pick_state(self) -> None:
        try:
            stat = LAYER_PICK_STATE_PATH.stat()
        except FileNotFoundError:
            if self.layer_pick_state_mtime_ns is not None:
                self.layer_pick_state_mtime_ns = None
                if self.layer_pick_state_label is not None:
                    self.layer_pick_state_label.setText(f"Layer pick: waiting for {LAYER_PICK_STATE_PATH.name}")
            return
        except OSError as exc:
            if self.layer_pick_state_label is not None:
                self.layer_pick_state_label.setText(f"Layer pick read failed: {exc}")
            return
        if stat.st_mtime_ns == self.layer_pick_state_mtime_ns:
            return
        next_mtime_ns = stat.st_mtime_ns
        try:
            payload = json.loads(LAYER_PICK_STATE_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            if self.layer_pick_state_label is not None:
                self.layer_pick_state_label.setText(f"Layer pick parse failed: {exc}")
            return
        self.layer_pick_state_mtime_ns = next_mtime_ns
        if isinstance(payload, dict):
            self.layer_pick_state_payload = payload
            self.refresh_layer_pick_state_label(payload)
            self.refresh_layer_properties()
            self.refresh_research_provenance()

    def refresh_layer_pick_state_label(self, payload: dict[str, object]) -> None:
        if self.layer_pick_state_label is None:
            return
        result = payload.get("pick_result")
        result = result if isinstance(result, dict) else {}
        event = str(result.get("event") or payload.get("event") or "-")
        target = str(payload.get("selected_renderer_layer") or result.get("renderer_layer") or "-")
        picker = str(result.get("picker") or "-")
        hit = result.get("hit")
        hit_detail = result.get("hit_detail")
        hit_detail = hit_detail if isinstance(hit_detail, dict) else {}
        feature = hit_detail.get("feature")
        feature_text = ""
        if isinstance(feature, dict):
            feature_label = str(feature.get("label") or feature.get("feature_index") or "-")
            if len(feature_label) > 72:
                feature_label = f"{feature_label[:69]}..."
            if feature_label != "-":
                feature_text = f", feature={feature_label}"
        frame_index = payload.get("frame_index", "-")
        updated_at = str(payload.get("updated_at_utc", "-"))
        self.layer_pick_state_label.setText(
            f"Layer pick: event={event}, target={target}, picker={picker}, hit={hit}{feature_text}, "
            f"frame={frame_index}, updated={updated_at}"
        )

    def refresh_pin_input_ack_state(self) -> None:
        try:
            stat = PIN_INPUT_ACK_PATH.stat()
        except FileNotFoundError:
            if self.pin_input_ack_mtime_ns is not None:
                self.pin_input_ack_mtime_ns = None
                if self.pin_input_ack_label is not None:
                    self.pin_input_ack_label.setText(f"Renderer input ack: waiting for {PIN_INPUT_ACK_PATH.name}")
            return
        except OSError as exc:
            if self.pin_input_ack_label is not None:
                self.pin_input_ack_label.setText(f"Renderer input ack read failed: {exc}")
            return
        if stat.st_mtime_ns == self.pin_input_ack_mtime_ns:
            return
        next_mtime_ns = stat.st_mtime_ns
        try:
            payload = json.loads(PIN_INPUT_ACK_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            if self.pin_input_ack_label is not None:
                self.pin_input_ack_label.setText(f"Renderer input ack parse failed: {exc}")
            return
        self.pin_input_ack_mtime_ns = next_mtime_ns
        if isinstance(payload, dict):
            self.pin_input_ack_payload = payload
            self.refresh_pin_input_ack_label(payload)
            self.refresh_research_provenance()

    def refresh_pin_input_ack_label(self, payload: dict[str, object]) -> None:
        if self.pin_input_ack_label is None:
            return
        pin_count = payload.get("pin_count", "-")
        selected_pin_id = str(payload.get("selected_pin_id") or "-")
        selected_exists = payload.get("selected_pin_exists", "-")
        updated_at = str(payload.get("updated_at_utc", "-"))
        self.pin_input_ack_label.setText(
            f"Renderer input ack: pins={pin_count}, selected={selected_pin_id}, "
            f"selected_exists={selected_exists}, updated={updated_at}"
        )

    def current_pin_label_mode(self) -> str:
        if self.pin_label_mode_combo is None:
            return "auto"
        data = self.pin_label_mode_combo.currentData()
        return data if isinstance(data, str) else "auto"

    def set_pin_label_mode(self, mode: str) -> None:
        if self.pin_label_mode_combo is None:
            return
        for index in range(self.pin_label_mode_combo.count()):
            if self.pin_label_mode_combo.itemData(index) == mode:
                self.pin_label_mode_combo.setCurrentIndex(index)
                return
        self.pin_label_mode_combo.setCurrentIndex(0)

    def collect_tool_state(self) -> dict[str, object]:
        return {
            "active_tool": self.active_tool,
            "target_layer": self.selected_layer_key,
            "pin_label_mode": self.current_pin_label_mode(),
            "pin_label_min_priority": self.pin_label_min_priority_spin.value() if self.pin_label_min_priority_spin is not None else 50,
            "pin": {
                "type": self.pin_type_combo.currentText() if self.pin_type_combo is not None else "Observation",
                "label": self.pin_label_edit.text().strip() if self.pin_label_edit is not None else "",
                "note": self.pin_note_edit.text().strip() if self.pin_note_edit is not None else "",
                "latitude": self.pin_lat_edit.text().strip() if self.pin_lat_edit is not None else "",
                "longitude": self.pin_lon_edit.text().strip() if self.pin_lon_edit is not None else "",
                "label_priority": self.pin_priority_spin.value() if self.pin_priority_spin is not None else 50,
                "placement": "manual_lat_lon",
            },
            "renderer_sync": "planned",
        }

    def collect_research_pins(self) -> list[dict[str, object]]:
        return [dict(pin) for pin in self.research_pins]

    def collect_boundary_highlight_state(self) -> dict[str, object]:
        return normalized_boundary_highlight_state(self.boundary_highlight_state)

    def boundary_highlight_summary(self) -> str:
        state = self.collect_boundary_highlight_state()
        color_rgb = state.get("color_rgb", [255, 190, 72])
        color_text = (
            f"{color_rgb[0]},{color_rgb[1]},{color_rgb[2]}"
            if isinstance(color_rgb, list) and len(color_rgb) >= 3
            else "255,190,72"
        )
        breathing = state.get("breathing", {})
        breathing_enabled = isinstance(breathing, dict) and breathing.get("enabled") is True
        target_layers = state.get("target_layers", [])
        target_count = len(target_layers) if isinstance(target_layers, list) else 0
        gamma = _coerce_int(state.get("gamma"), 100, 25, 300) / 100.0
        return (
            f"{'On' if state.get('enabled') else 'Off'}; trigger={state.get('trigger', 'hover')}; "
            f"RGB={color_text}; contrast={state.get('contrast')}%; alpha={state.get('alpha')}%; "
            f"gamma={gamma:.2f}; feather={state.get('feather')}%; "
            f"breath={'on' if breathing_enabled else 'off'}; targets={target_count}; line mask live; closed-ring fill live"
        )

    def boundary_identity_status_summary(self) -> str:
        state = self.collect_boundary_highlight_state()
        identity_status = state.get("identity_status")
        if not isinstance(identity_status, dict):
            identity_status = default_boundary_identity_status()
        applied = identity_status.get("applied", [])
        pending = identity_status.get("pending", [])
        applied_count = len(applied) if isinstance(applied, list) else "-"
        pending_count = len(pending) if isinstance(pending, list) else "-"
        boundary = str(identity_status.get("boundary", "visual/source-property preview only"))
        return f"applied={applied_count}; pending={pending_count}; {boundary}"

    def refresh_boundary_highlight_status(self) -> None:
        if self.boundary_highlight_label is not None:
            self.boundary_highlight_label.setText(self.boundary_highlight_summary())
        if self.boundary_identity_status_label is not None:
            self.boundary_identity_status_label.setText(self.boundary_identity_status_summary())

    def refresh_boundary_highlight_ack_state(self) -> None:
        try:
            stat = BOUNDARY_HIGHLIGHT_ACK_PATH.stat()
        except FileNotFoundError:
            if self.boundary_highlight_ack_mtime_ns is not None:
                self.boundary_highlight_ack_mtime_ns = None
                if self.boundary_highlight_ack_label is not None:
                    self.boundary_highlight_ack_label.setText(
                        f"Boundary ack: waiting for {BOUNDARY_HIGHLIGHT_ACK_PATH.name}"
                    )
            return
        except OSError as exc:
            if self.boundary_highlight_ack_label is not None:
                self.boundary_highlight_ack_label.setText(f"Boundary ack read failed: {exc}")
            return
        if stat.st_mtime_ns == self.boundary_highlight_ack_mtime_ns:
            return
        next_mtime_ns = stat.st_mtime_ns
        try:
            payload = json.loads(BOUNDARY_HIGHLIGHT_ACK_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            if self.boundary_highlight_ack_label is not None:
                self.boundary_highlight_ack_label.setText(f"Boundary ack parse failed: {exc}")
            return
        self.boundary_highlight_ack_mtime_ns = next_mtime_ns
        if isinstance(payload, dict):
            self.boundary_highlight_ack_payload = payload
            self.refresh_boundary_highlight_ack_label(payload)
            self.refresh_research_provenance()

    def refresh_boundary_highlight_ack_label(self, payload: dict[str, object]) -> None:
        if self.boundary_highlight_ack_label is None:
            return
        enabled = payload.get("enabled", "-")
        target_layers = payload.get("target_layers", [])
        target_count = len(target_layers) if isinstance(target_layers, list) else "-"
        renderer_layers = payload.get("renderer_target_layers", [])
        renderer_count = len(renderer_layers) if isinstance(renderer_layers, list) else "-"
        updated_at = str(payload.get("updated_at_utc", "-"))
        error = payload.get("error")
        if error:
            self.boundary_highlight_ack_label.setText(
                f"Boundary ack: error={error}, updated={updated_at}"
            )
            return
        self.boundary_highlight_ack_label.setText(
            f"Boundary ack: enabled={enabled}, targets={target_count}, renderer_targets={renderer_count}, "
            f"updated={updated_at}"
        )

    def open_boundary_highlight_dialog(self, layer_key: str | None = None) -> None:
        if not isinstance(layer_key, str) or layer_key not in BOUNDARY_HIGHLIGHT_LAYER_KEYS:
            if self.selected_layer_key in BOUNDARY_HIGHLIGHT_LAYER_KEYS:
                layer_key = self.selected_layer_key
            else:
                layer_key = "border_layer"
        self.select_layer(layer_key)
        state = self.collect_boundary_highlight_state()
        dialog = QtWidgets.QDialog(self)
        layer_label = next((label for key, label in LAYER_LABELS if key == layer_key), layer_key)
        dialog.setWindowTitle(f"疆域強調遮罩：{layer_label}")
        layout = QtWidgets.QVBoxLayout(dialog)
        note = QtWidgets.QLabel(
            "控制國界/領海/EEZ/公海 hover 強調遮罩。這是科研定位用的圖層強調狀態，"
            "已寫入 profile / launch packet / provenance。renderer 線段遮罩、閉合 ring fill、"
            "source-property feature identity 已 live；authoritative 疆域/EEZ identity 與 open-line area inference 仍為明確 pending。"
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        form = QtWidgets.QFormLayout()
        enabled = QtWidgets.QCheckBox("啟用 hover 疆域強調")
        enabled.setChecked(bool(state.get("enabled", True)))
        form.addRow("Enabled", enabled)
        trigger_combo = QtWidgets.QComboBox()
        trigger_items = (
            ("hover", "Hover"),
            ("selected", "Selected"),
            ("hover_or_selected", "Hover or selected"),
        )
        for value, label in trigger_items:
            trigger_combo.addItem(label, value)
        for index in range(trigger_combo.count()):
            if trigger_combo.itemData(index) == state.get("trigger"):
                trigger_combo.setCurrentIndex(index)
                break
        form.addRow("Trigger", trigger_combo)
        color_rgb = state.get("color_rgb", [255, 190, 72])
        if not isinstance(color_rgb, list) or len(color_rgb) < 3:
            color_rgb = [255, 190, 72]
        selected_color = [QtGui.QColor(int(color_rgb[0]), int(color_rgb[1]), int(color_rgb[2]))]
        color_button = QtWidgets.QPushButton()

        def update_color_button() -> None:
            color = selected_color[0]
            color_button.setText(f"RGB {color.red()}, {color.green()}, {color.blue()}")
            color_button.setStyleSheet(
                f"background-color: rgb({color.red()}, {color.green()}, {color.blue()}); color: #111; font-weight: 700;"
            )

        def choose_color() -> None:
            color = QtWidgets.QColorDialog.getColor(selected_color[0], dialog, "Boundary highlight RGB")
            if color.isValid():
                selected_color[0] = color
                update_color_button()

        color_button.clicked.connect(choose_color)
        update_color_button()
        form.addRow("RGB 色環", color_button)

        def slider_row(value: int, minimum: int, maximum: int, suffix: str = "%") -> tuple[QtWidgets.QWidget, QtWidgets.QSlider, QtWidgets.QLabel]:
            container = QtWidgets.QWidget()
            row = QtWidgets.QHBoxLayout(container)
            row.setContentsMargins(0, 0, 0, 0)
            slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
            slider.setRange(minimum, maximum)
            slider.setValue(value)
            label = QtWidgets.QLabel()

            def update_label(next_value: int) -> None:
                if suffix == "x":
                    label.setText(f"{next_value / 100.0:.2f}x")
                else:
                    label.setText(f"{next_value}{suffix}")

            slider.valueChanged.connect(update_label)
            update_label(value)
            row.addWidget(slider, stretch=1)
            row.addWidget(label)
            return container, slider, label

        contrast_row, contrast_slider, _contrast_label = slider_row(_coerce_int(state.get("contrast"), 45, 0, 100), 0, 100)
        alpha_row, alpha_slider, _alpha_label = slider_row(_coerce_int(state.get("alpha"), 48, 0, 100), 0, 100)
        gamma_row, gamma_slider, _gamma_label = slider_row(_coerce_int(state.get("gamma"), 100, 25, 300), 25, 300, "x")
        feather_row, feather_slider, _feather_label = slider_row(_coerce_int(state.get("feather"), 14, 0, 100), 0, 100)
        form.addRow("對比 Contrast", contrast_row)
        form.addRow("半透明 Alpha", alpha_row)
        form.addRow("Gamma", gamma_row)
        form.addRow("邊緣 Feather", feather_row)
        breathing = state.get("breathing", {})
        if not isinstance(breathing, dict):
            breathing = {}
        breath_enabled = QtWidgets.QCheckBox("呼吸特效")
        breath_enabled.setChecked(bool(breathing.get("enabled", True)))
        breath_speed_row, breath_speed_slider, _speed_label = slider_row(
            _coerce_int(breathing.get("speed"), 42, 0, 100), 0, 100
        )
        breath_amp_row, breath_amp_slider, _amp_label = slider_row(
            _coerce_int(breathing.get("amplitude"), 16, 0, 100), 0, 100
        )
        form.addRow("Breathing", breath_enabled)
        form.addRow("Breath speed", breath_speed_row)
        form.addRow("Breath amplitude", breath_amp_row)
        layout.addLayout(form)
        target_group = QtWidgets.QGroupBox("Target boundary layers")
        target_layout = QtWidgets.QGridLayout(target_group)
        current_targets = state.get("target_layers", [])
        target_checks: dict[str, QtWidgets.QCheckBox] = {}
        for index, target_key in enumerate(BOUNDARY_HIGHLIGHT_LAYER_KEYS):
            target_label = next((label for key, label in LAYER_LABELS if key == target_key), target_key)
            target_check = QtWidgets.QCheckBox(target_label)
            target_check.setChecked(isinstance(current_targets, list) and target_key in current_targets)
            target_checks[target_key] = target_check
            target_layout.addWidget(target_check, index // 2, index % 2)
        layout.addWidget(target_group)
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )

        def apply_dialog() -> None:
            color = selected_color[0]
            targets = [key for key, checkbox in target_checks.items() if checkbox.isChecked()]
            if not targets:
                targets = [layer_key]
            self.boundary_highlight_state = normalized_boundary_highlight_state(
                {
                    "schema": BOUNDARY_HIGHLIGHT_SCHEMA,
                    "enabled": enabled.isChecked(),
                    "trigger": trigger_combo.currentData(),
                    "target_layers": targets,
                    "color_rgb": [color.red(), color.green(), color.blue()],
                    "contrast": contrast_slider.value(),
                    "alpha": alpha_slider.value(),
                    "gamma": gamma_slider.value(),
                    "feather": feather_slider.value(),
                    "breathing": {
                        "enabled": breath_enabled.isChecked(),
                        "speed": breath_speed_slider.value(),
                        "amplitude": breath_amp_slider.value(),
                    },
                    "renderer_sync": "renderer_line_fill_identity_status_handoff",
                }
            )
            self.refresh_boundary_highlight_status()
            self.refresh_command_preview()
            self.refresh_canvas_preview()
            if self.history_list is not None:
                self.history_list.insertItem(0, f"Boundary highlight UI updated: {layer_key}")
            self.status.setText(f"已更新疆域強調遮罩設定：{layer_label}")
            dialog.accept()

        buttons.accepted.connect(apply_dialog)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.exec()

    def apply_profile(self, profile: dict[str, object]) -> None:
        errors = profile_payload_errors(profile)
        if errors:
            self.status.setText("配置格式錯誤")
            self.command_text.setPlainText("\n".join(errors))
            return
        renderer = profile.get("renderer", {})
        material = profile.get("ocean_material", {})
        layers = profile.get("layers", {})
        selected_layer = profile.get("selected_layer")
        selected_pin_id = profile.get("selected_pin_id")
        layer_stack = profile.get("layer_stack_ui")
        tool_state = profile.get("tool_state")
        pins = profile.get("pins")
        boundary_highlight = profile.get("boundary_highlight")
        canvas_preview = profile.get("canvas_preview")
        if isinstance(renderer, dict):
            self._set_combo(self.style_combo, str(renderer.get("style_profile", self.style_combo.currentText())))
            self._set_combo(self.ui_combo, str(renderer.get("ui_backend", self.ui_combo.currentText())))
            self._set_combo(self.topo_combo, str(renderer.get("topo_source", self.topo_combo.currentText())))
            self._set_combo(self.data_combo, str(renderer.get("data_mode", self.data_combo.currentText())))
            self.width_edit.setText(str(renderer.get("width", self.width_edit.text())))
            self.height_edit.setText(str(renderer.get("height", self.height_edit.text())))
            self.topo_step_edit.setText(str(renderer.get("topo_step", self.topo_step_edit.text())))
            self.arch_edit.setText(str(renderer.get("taichi_arch", self.arch_edit.text())))
            self.rrkal_manifest_ref_edit.setText(
                str(renderer.get("rrkal_data_manifest_ref", self.rrkal_manifest_ref_edit.text()))
            )
        if isinstance(material, dict):
            self.wave_edit.setText(str(material.get("wave_strength", self.wave_edit.text())))
            self.roughness_edit.setText(str(material.get("roughness", self.roughness_edit.text())))
            self.foam_edit.setText(str(material.get("foam", self.foam_edit.text())))
        if isinstance(layers, dict):
            for key, value in layers.items():
                if key in self.checks:
                    self.checks[key].setChecked(bool(value))
        if isinstance(layer_stack, dict):
            for key, value in layer_stack.items():
                if key not in self.layer_locks or not isinstance(value, dict):
                    continue
                self.layer_locks[key].setChecked(bool(value.get("locked", False)))
                self.layer_opacity[key].setValue(int(value.get("opacity", 100)))
                self.layer_blends[key].setCurrentText(str(value.get("blend_mode", "Normal")))
        if isinstance(selected_layer, str) and selected_layer in self.layer_rows:
            self.select_layer(selected_layer)
        elif isinstance(layer_stack, dict):
            for key, value in layer_stack.items():
                if key in self.layer_rows and isinstance(value, dict) and value.get("selected") is True:
                    self.select_layer(key)
                    break
        if isinstance(tool_state, dict):
            self.apply_tool_state(tool_state)
        if isinstance(pins, list):
            self.apply_research_pins(pins)
        if isinstance(boundary_highlight, dict):
            self.boundary_highlight_state = normalized_boundary_highlight_state(boundary_highlight)
            self.refresh_boundary_highlight_status()
        if isinstance(canvas_preview, dict):
            self.apply_canvas_preview_state(canvas_preview)
        self.selected_pin_id = selected_pin_id if isinstance(selected_pin_id, str) else None
        if self.selected_pin_id is not None and self.selected_pin_packet() is None:
            self.selected_pin_id = None
        self.refresh_pin_list()
        self.populate_selected_pin_fields()
        self.refresh_command_preview()
        self.refresh_layer_stack_status()

    def apply_canvas_preview_state(self, state: dict[str, object]) -> None:
        mode = str(state.get("mode", "state"))
        if mode == "live_file_stream":
            preview_path = RENDERER_PREVIEW_FRAME_PATH
            raw_path = state.get("renderer_thumbnail_path")
            if isinstance(raw_path, str) and raw_path.strip():
                candidate = Path(raw_path.strip())
                if not candidate.is_absolute():
                    candidate = ROOT / candidate
                preview_path = candidate
            self.canvas_preview_mode = "live_file_stream"
            self.renderer_thumbnail_path = preview_path
            self.renderer_thumbnail_mtime_ns = None
            return
        if mode == "thumbnail":
            thumbnail_path: Path | None = None
            raw_path = state.get("renderer_thumbnail_path")
            if isinstance(raw_path, str) and raw_path.strip():
                candidate = Path(raw_path.strip())
                if not candidate.is_absolute():
                    candidate = ROOT / candidate
                if candidate.exists():
                    thumbnail_path = candidate
            if thumbnail_path is None:
                thumbnail_path = self.latest_renderer_thumbnail_path()
            if thumbnail_path is not None:
                self.canvas_preview_mode = "thumbnail"
                self.renderer_thumbnail_path = thumbnail_path
                return
        self.canvas_preview_mode = "state"
        self.renderer_thumbnail_path = None

    def load_profile_path(self, path: Path) -> None:
        if not path.exists():
            self.status.setText(f"找不到配置：{path}")
            return
        profile = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(profile, dict):
            self.status.setText("配置格式錯誤：root 不是 JSON object")
            return
        self.apply_profile(profile)
        self.status.setText(f"已載入配置：{path}")

    @QtCore.pyqtSlot()
    def refresh_template_list(self) -> None:
        PROFILE_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
        self.template_paths = sorted(PROFILE_TEMPLATE_DIR.glob("*.json"))
        self.template_combo.clear()
        if not self.template_paths:
            self.template_combo.addItem("沒有內建模板")
            return
        for path in self.template_paths:
            label = path.stem.replace("_", " ")
            try:
                profile = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(profile, dict) and profile.get("name"):
                    label = str(profile["name"])
            except Exception:
                pass
            self.template_combo.addItem(label, str(path))

    @QtCore.pyqtSlot()
    def load_selected_template(self) -> None:
        if not self.template_paths:
            self.status.setText("沒有可載入的內建模板")
            return
        index = self.template_combo.currentIndex()
        if index < 0 or index >= len(self.template_paths):
            self.status.setText("模板選取無效")
            return
        path = self.template_paths[index]
        profile = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(profile, dict):
            self.status.setText("模板格式錯誤：root 不是 JSON object")
            return
        self.apply_profile(profile)
        self.status.setText(f"已載入內建模板：{path.name}")

    @QtCore.pyqtSlot()
    def refresh_command_preview(self) -> None:
        self.command_text.setPlainText(subprocess.list2cmdline(self.build_command()))
        self.refresh_canvas_preview()
        self.refresh_research_provenance()

    def refresh_layer_stack_status(self) -> None:
        if not hasattr(self, "layer_stack_note"):
            return
        self.track_layer_undo_snapshot()
        visible = sum(1 for key, _label in LAYER_LABELS if self.checks[key].isChecked())
        locked = sum(1 for key, _label in LAYER_LABELS if self.layer_locks[key].isChecked())
        for key, _label in LAYER_LABELS:
            if key in self.checks and key in self.layer_locks:
                self.checks[key].setEnabled(not self.layer_locks[key].isChecked())
        non_default = sum(
            1
            for key, _label in LAYER_LABELS
            if self.layer_opacity[key].value() != 100 or self.layer_blends[key].currentText() != "Normal"
        )
        self.layer_stack_note.setText(
            f"可見圖層 {visible}/{len(LAYER_LABELS)}；鎖定 {locked}；"
            f"非預設 opacity/blend {non_default}；"
            f"solo snapshot={'active' if self.layer_visibility_snapshot is not None else 'none'}。"
            "Visibility/Opacity/Blend 已接 renderer runtime sync。"
        )
        self.refresh_layer_undo_label()
        self.write_layer_runtime_state()
        self.refresh_layer_properties()
        self.refresh_canvas_preview()

    def collect_layer_undo_snapshot(self) -> dict[str, object]:
        return {
            "schema": "rrkal_displaytools.layer_stack_undo_snapshot.v1",
            "selected_layer": self.selected_layer_key,
            "layers": {
                key: {
                    "visible": self.checks[key].isChecked(),
                    "locked": self.layer_locks[key].isChecked(),
                    "opacity": self.layer_opacity[key].value(),
                    "blend_mode": self.layer_blends[key].currentText(),
                }
                for key, _label in LAYER_LABELS
                if key in self.checks and key in self.layer_locks
            },
        }

    def layer_undo_signature(self, snapshot: dict[str, object]) -> str:
        return json.dumps(snapshot, sort_keys=True, ensure_ascii=False)

    def track_layer_undo_snapshot(self) -> None:
        snapshot = self.collect_layer_undo_snapshot()
        signature = self.layer_undo_signature(snapshot)
        if (
            not self.layer_undo_restore_active
            and self.layer_undo_tracking_enabled
            and self.layer_last_state_snapshot is not None
            and self.layer_last_state_signature is not None
            and signature != self.layer_last_state_signature
        ):
            self.layer_undo_stack.append(self.layer_last_state_snapshot)
            while len(self.layer_undo_stack) > 24:
                self.layer_undo_stack.pop(0)
            if self.history_list is not None:
                self.history_list.insertItem(0, f"Layer undo snapshot saved: {len(self.layer_undo_stack)}")
        self.layer_last_state_snapshot = snapshot
        self.layer_last_state_signature = signature

    def refresh_layer_undo_label(self) -> None:
        if self.layer_undo_label is None:
            return
        self.layer_undo_label.setText(
            f"Layer undo: {len(self.layer_undo_stack)} snapshots; "
            "covers visibility/lock/opacity/blend/active layer"
        )

    @QtCore.pyqtSlot()
    def undo_layer_stack_state(self) -> None:
        if not self.layer_undo_stack:
            self.status.setText("沒有可回復的 layer undo snapshot")
            return
        snapshot = self.layer_undo_stack.pop()
        layers = snapshot.get("layers")
        if not isinstance(layers, dict):
            self.status.setText("Layer undo snapshot 格式不正確")
            return
        self.layer_undo_restore_active = True
        try:
            for key, value in layers.items():
                if key not in self.checks or key not in self.layer_locks or not isinstance(value, dict):
                    continue
                self.checks[key].blockSignals(True)
                self.layer_locks[key].blockSignals(True)
                self.layer_opacity[key].blockSignals(True)
                self.layer_blends[key].blockSignals(True)
                self.checks[key].setChecked(bool(value.get("visible", False)))
                self.layer_locks[key].setChecked(bool(value.get("locked", False)))
                self.layer_opacity[key].setValue(_coerce_int(value.get("opacity"), 100, 0, 100))
                blend_mode = str(value.get("blend_mode", "Normal"))
                self.layer_blends[key].setCurrentText(blend_mode if blend_mode in BLEND_MODES else "Normal")
                self.checks[key].blockSignals(False)
                self.layer_locks[key].blockSignals(False)
                self.layer_opacity[key].blockSignals(False)
                self.layer_blends[key].blockSignals(False)
            selected_layer = snapshot.get("selected_layer")
            if isinstance(selected_layer, str) and selected_layer in self.layer_rows:
                self.select_layer(selected_layer)
        finally:
            self.layer_undo_restore_active = False
        self.layer_last_state_snapshot = self.collect_layer_undo_snapshot()
        self.layer_last_state_signature = self.layer_undo_signature(self.layer_last_state_snapshot)
        self.refresh_command_preview()
        self.refresh_layer_stack_status()
        self.status.setText("已回復上一個 layer undo snapshot")

    def select_layer(self, key: str) -> None:
        if key not in self.layer_rows:
            return
        self.selected_layer_key = key
        label = next((label for layer_key, label in LAYER_LABELS if layer_key == key), key)
        self.selected_layer_label.setText(f"目前選取圖層：{label} / {key}")
        for layer_key, row in self.layer_rows.items():
            row.setProperty("selected", layer_key == key)
            row.style().unpolish(row)
            row.style().polish(row)
            row.update()
        self.refresh_layer_stack_status()
        if hasattr(self, "status"):
            self.status.setText(f"已選取圖層：{label}")
        self.refresh_tool_target()

    def solo_selected_layer_visibility(self) -> None:
        key = self.selected_layer_key
        if key not in self.checks:
            self.status.setText("尚未選取可 Solo 的圖層")
            return
        if self.layer_locks.get(key) is not None and self.layer_locks[key].isChecked():
            self.status.setText("選取圖層已鎖定，Solo 未變更 visibility")
            return
        self.layer_visibility_snapshot = {
            layer_key: self.checks[layer_key].isChecked()
            for layer_key, _label in LAYER_LABELS
            if layer_key in self.checks
        }
        for layer_key, _label in LAYER_LABELS:
            if layer_key not in self.checks:
                continue
            if layer_key != key and self.layer_locks.get(layer_key) is not None and self.layer_locks[layer_key].isChecked():
                continue
            self.checks[layer_key].blockSignals(True)
            self.checks[layer_key].setChecked(layer_key == key)
            self.checks[layer_key].blockSignals(False)
        self.refresh_command_preview()
        self.refresh_layer_stack_status()
        label = next((text for layer_key, text in LAYER_LABELS if layer_key == key), key)
        self.status.setText(f"已 Solo 選取圖層：{label}")

    def restore_layer_visibility_snapshot(self) -> None:
        if not self.layer_visibility_snapshot:
            self.status.setText("沒有可還原的 Solo 前可見性 snapshot")
            return
        skipped_locked = 0
        for layer_key, enabled in self.layer_visibility_snapshot.items():
            if layer_key not in self.checks:
                continue
            if self.layer_locks.get(layer_key) is not None and self.layer_locks[layer_key].isChecked():
                skipped_locked += 1
                continue
            self.checks[layer_key].blockSignals(True)
            self.checks[layer_key].setChecked(bool(enabled))
            self.checks[layer_key].blockSignals(False)
        self.layer_visibility_snapshot = None
        self.refresh_command_preview()
        self.refresh_layer_stack_status()
        if skipped_locked:
            self.status.setText(f"已還原 Solo 前圖層可見性；跳過 locked layers：{skipped_locked}")
        else:
            self.status.setText("已還原 Solo 前圖層可見性")

    def canvas_layer_hit_keys(self) -> list[str]:
        visible_keys = [key for key, _label in LAYER_LABELS if key in self.checks and self.checks[key].isChecked()]
        if visible_keys:
            return visible_keys
        return [key for key, _label in LAYER_LABELS if key in self.checks]

    def canvas_layer_hit_key(self, y: float) -> str | None:
        if self.canvas_preview_label is None:
            return None
        keys = self.canvas_layer_hit_keys()
        if not keys:
            return None
        height = max(1.0, float(self.canvas_preview_label.height()))
        y_ratio = min(max(y / height, 0.0), 0.999999)
        return keys[min(len(keys) - 1, int(y_ratio * len(keys)))]

    def refresh_layer_properties(self) -> None:
        if not self.layer_property_labels:
            return
        key = self.selected_layer_key
        if key not in self.checks:
            for label in self.layer_property_labels.values():
                label.setText("-")
            self.layer_property_labels["name"].setText("尚未選取")
            return
        label = next((text for layer_key, text in LAYER_LABELS if layer_key == key), key)
        self.layer_property_labels["name"].setText(f"{label} / {key}")
        self.layer_property_labels["visible"].setText("On" if self.checks[key].isChecked() else "Off")
        self.layer_property_labels["locked"].setText("Locked" if self.layer_locks[key].isChecked() else "Unlocked")
        self.layer_property_labels["opacity"].setText(f"{self.layer_opacity[key].value()}%")
        self.layer_property_labels["blend"].setText(self.layer_blends[key].currentText())
        renderer_target = LAYER_RUNTIME_ID_ALIASES.get(key, "-")
        self.layer_property_labels["renderer_target"].setText(str(renderer_target))
        self.layer_property_labels["diagnostics"].setText(self.layer_diagnostics_text(str(renderer_target)))
        self.refresh_boundary_highlight_status()

    def layer_diagnostics_text(self, renderer_target: str) -> str:
        ack = self.layer_runtime_ack_payload if isinstance(self.layer_runtime_ack_payload, dict) else {}
        ack_event = str(ack.get("event") or "waiting")
        ack_target = str(ack.get("selected_renderer_layer") or "-")
        ack_frame = ack.get("frame_index", "-")
        ack_error = ack.get("error")
        if ack_error:
            ack_text = f"ack error={ack_error}"
        elif ack_target == "-":
            ack_text = f"ack={ack_event}, target waiting"
        elif ack_target == renderer_target:
            ack_text = f"ack={ack_event}, target matched, frame={ack_frame}"
        else:
            ack_text = f"ack={ack_event}, target={ack_target}, frame={ack_frame}"

        pick_payload = self.layer_pick_state_payload if isinstance(self.layer_pick_state_payload, dict) else {}
        pick_result = pick_payload.get("pick_result")
        pick_result = pick_result if isinstance(pick_result, dict) else {}
        pick_event = str(pick_result.get("event") or pick_payload.get("event") or "waiting")
        pick_target = str(pick_payload.get("selected_renderer_layer") or pick_result.get("renderer_layer") or "-")
        hit_value = pick_result.get("hit")
        if isinstance(hit_value, bool):
            hit_text = "hit" if hit_value else "no-hit"
        else:
            hit_text = "-"
        feature_label = pick_result.get("feature_label") or pick_result.get("label") or pick_result.get("name")
        feature_text = ""
        if isinstance(feature_label, str) and feature_label.strip():
            feature = feature_label.strip()
            if len(feature) > 48:
                feature = f"{feature[:45]}..."
            feature_text = f", feature={feature}"
        if pick_target == "-":
            pick_text = f"pick={pick_event}, target waiting"
        else:
            pick_text = f"pick={pick_event}, target={pick_target}, {hit_text}{feature_text}"
        return f"{ack_text}; {pick_text}"

    def active_layer_diagnostics_packet(self) -> dict[str, object]:
        key = self.selected_layer_key
        label = next((text for layer_key, text in LAYER_LABELS if layer_key == key), key or None)
        renderer_target = LAYER_RUNTIME_ID_ALIASES.get(key, None) if key is not None else None
        diagnostics_text = (
            self.layer_diagnostics_text(str(renderer_target))
            if renderer_target is not None
            else "no active layer selected"
        )
        return {
            "schema": "rrkal_displaytools.active_layer_diagnostics.v1",
            "selected_layer": key,
            "label": label,
            "renderer_target": renderer_target,
            "diagnostics_text": diagnostics_text,
            "runtime_ack_file": str(LAYER_RUNTIME_ACK_PATH),
            "runtime_ack": self.layer_runtime_ack_payload,
            "pick_state_file": str(LAYER_PICK_STATE_PATH),
            "pick_state": self.layer_pick_state_payload,
        }

    def set_active_tool(self, mode: str) -> None:
        if mode not in self.tool_buttons:
            return
        self.active_tool = mode
        for tool_mode, button in self.tool_buttons.items():
            button.setChecked(tool_mode == mode)
        self.refresh_tool_target()
        label = next((text for tool_mode, text, _hint in TOOL_MODES if tool_mode == mode), mode)
        if hasattr(self, "status"):
            self.status.setText(f"已選取工具：{label}")
        self.refresh_canvas_preview()

    def apply_tool_state(self, state: dict[str, object]) -> None:
        active_tool = state.get("active_tool")
        if isinstance(active_tool, str) and active_tool in self.tool_buttons:
            self.set_active_tool(active_tool)
        target_layer = state.get("target_layer")
        if isinstance(target_layer, str) and target_layer in self.layer_rows:
            self.select_layer(target_layer)
        pin = state.get("pin")
        if isinstance(pin, dict):
            if self.pin_type_combo is not None and isinstance(pin.get("type"), str):
                self.pin_type_combo.setCurrentText(str(pin["type"]))
            if self.pin_label_edit is not None and isinstance(pin.get("label"), str):
                self.pin_label_edit.setText(str(pin["label"]))
            if self.pin_note_edit is not None and isinstance(pin.get("note"), str):
                self.pin_note_edit.setText(str(pin["note"]))
            if self.pin_lat_edit is not None and isinstance(pin.get("latitude"), str):
                self.pin_lat_edit.setText(str(pin["latitude"]))
            if self.pin_lon_edit is not None and isinstance(pin.get("longitude"), str):
                self.pin_lon_edit.setText(str(pin["longitude"]))
            if self.pin_priority_spin is not None and isinstance(pin.get("label_priority"), int):
                self.pin_priority_spin.setValue(max(0, min(100, int(pin["label_priority"]))))
        label_mode = state.get("pin_label_mode")
        if isinstance(label_mode, str):
            self.set_pin_label_mode(label_mode)
        label_min_priority = state.get("pin_label_min_priority")
        if self.pin_label_min_priority_spin is not None and isinstance(label_min_priority, int):
            self.pin_label_min_priority_spin.setValue(max(0, min(100, int(label_min_priority))))
        self.refresh_tool_target()

    def refresh_tool_target(self) -> None:
        if self.tool_target_label is None:
            return
        layer_label = next(
            (text for layer_key, text in LAYER_LABELS if layer_key == self.selected_layer_key),
            self.selected_layer_key or "-",
        )
        tool_label = next((text for mode, text, _hint in TOOL_MODES if mode == self.active_tool), self.active_tool)
        self.tool_target_label.setText(
            f"Active tool: {tool_label}\n"
            f"Target layer: {layer_label}\n"
            f"Pin: {self.collect_tool_state()['pin']['type']} / {self.collect_tool_state()['pin']['label']}\n"
            f"Labels: {self.current_pin_label_mode()} >= {self.pin_label_min_priority_spin.value() if self.pin_label_min_priority_spin is not None else 50}"
        )
        self.refresh_canvas_preview()

    def add_pin_marker(self) -> None:
        if self.pin_lat_edit is None or self.pin_lon_edit is None:
            return
        try:
            latitude = float(self.pin_lat_edit.text().strip())
            longitude = float(self.pin_lon_edit.text().strip())
        except ValueError:
            self.status.setText("Pin 經緯度必須是數字")
            return
        if not -90 <= latitude <= 90:
            self.status.setText("Pin latitude 必須介於 -90 到 90")
            return
        if not -180 <= longitude <= 180:
            self.status.setText("Pin longitude 必須介於 -180 到 180")
            return
        label = self.pin_label_edit.text().strip() if self.pin_label_edit is not None else ""
        pin = {
            "id": f"pin-{len(self.research_pins) + 1:03d}",
            "type": self.pin_type_combo.currentText() if self.pin_type_combo is not None else "Observation",
            "label": label or f"Pin {len(self.research_pins) + 1}",
            "note": self.pin_note_edit.text().strip() if self.pin_note_edit is not None else "",
            "latitude": latitude,
            "longitude": longitude,
            "label_priority": self.pin_priority_spin.value() if self.pin_priority_spin is not None else 50,
            "target_layer": self.selected_layer_key,
            "placement": "manual_lat_lon",
        }
        self.research_pins.append(pin)
        self.selected_pin_id = str(pin["id"])
        self.refresh_pin_list()
        self.refresh_canvas_preview()
        self.status.setText(f"已加入科研 Pin：{pin['label']}")

    def fill_pin_from_cursor(self) -> None:
        if self.cursor_latitude is None or self.cursor_longitude is None:
            self.status.setText("尚未偵測到 Canvas 游標經緯度")
            return
        if self.pin_lat_edit is not None:
            self.pin_lat_edit.setText(f"{self.cursor_latitude:.6f}")
        if self.pin_lon_edit is not None:
            self.pin_lon_edit.setText(f"{self.cursor_longitude:.6f}")
        self.status.setText(
            f"已用游標位置填入 Pin：lat={self.cursor_latitude:.6f}, lon={self.cursor_longitude:.6f}"
        )

    def remove_selected_pin_marker(self) -> None:
        if self.pin_list is None:
            return
        row = self.pin_list.currentRow()
        if row < 0 or row >= len(self.research_pins):
            self.status.setText("尚未選取要移除的 Pin")
            return
        removed = self.research_pins.pop(row)
        if self.research_pins:
            next_row = min(row, len(self.research_pins) - 1)
            self.selected_pin_id = str(self.research_pins[next_row].get("id", ""))
        else:
            self.selected_pin_id = None
        self.refresh_pin_list()
        self.refresh_canvas_preview()
        self.status.setText(f"已移除科研 Pin：{removed.get('label', removed.get('id', 'pin'))}")

    def select_pin_marker(self, row: int) -> None:
        if row < 0 or row >= len(self.research_pins):
            self.selected_pin_id = None
            self.refresh_canvas_preview()
            return
        pin = self.research_pins[row]
        self.selected_pin_id = str(pin.get("id", ""))
        self.populate_selected_pin_fields()
        self.refresh_canvas_preview()
        self.status.setText(f"已選取科研 Pin：{pin.get('label', pin.get('id', 'pin'))}")

    def selected_pin_packet(self) -> dict[str, object] | None:
        if self.selected_pin_id is None:
            return None
        for pin in self.research_pins:
            if pin.get("id") == self.selected_pin_id:
                return dict(pin)
        return None

    def pin_id_exists(self, pin_id: str) -> bool:
        return any(str(pin.get("id", "")) == pin_id for pin in self.research_pins)

    def populate_selected_pin_fields(self) -> None:
        pin = self.selected_pin_packet()
        if pin is None:
            return
        if self.pin_type_combo is not None and isinstance(pin.get("type"), str):
            self.pin_type_combo.setCurrentText(str(pin["type"]))
        if self.pin_label_edit is not None and isinstance(pin.get("label"), str):
            self.pin_label_edit.setText(str(pin["label"]))
        if self.pin_note_edit is not None and isinstance(pin.get("note"), str):
            self.pin_note_edit.setText(str(pin["note"]))
        if self.pin_lat_edit is not None and isinstance(pin.get("latitude"), (int, float)):
            self.pin_lat_edit.setText(str(pin["latitude"]))
        if self.pin_lon_edit is not None and isinstance(pin.get("longitude"), (int, float)):
            self.pin_lon_edit.setText(str(pin["longitude"]))
        if self.pin_priority_spin is not None and isinstance(pin.get("label_priority"), int):
            self.pin_priority_spin.setValue(max(0, min(100, int(pin["label_priority"]))))

    def refresh_pin_list(self) -> None:
        if self.pin_list is None:
            return
        self.pin_list.blockSignals(True)
        self.pin_list.clear()
        selected_row = -1
        for index, pin in enumerate(self.research_pins):
            selected = pin.get("id") == self.selected_pin_id
            prefix = "* " if selected else "  "
            self.pin_list.addItem(
                f"{prefix}{pin.get('id')} | P{pin.get('label_priority', 50)} | {pin.get('type')} | {pin.get('label')} "
                f"({pin.get('latitude')}, {pin.get('longitude')})"
            )
            if selected:
                selected_row = index
        self.pin_list.setCurrentRow(selected_row)
        self.pin_list.blockSignals(False)

    def apply_research_pins(self, pins: list[object]) -> None:
        self.research_pins = [dict(pin) for pin in pins if isinstance(pin, dict)]
        if self.selected_pin_id is not None and self.selected_pin_packet() is None:
            self.selected_pin_id = None
        self.refresh_pin_list()

    def refresh_renderer_pin_pick_state(self) -> None:
        try:
            stat = PIN_PICK_STATE_PATH.stat()
        except FileNotFoundError:
            if self.pin_pick_state_mtime_ns is not None:
                self.pin_pick_state_mtime_ns = None
                if self.pin_pick_state_label is not None:
                    self.pin_pick_state_label.setText(f"Renderer bridge: waiting for {PIN_PICK_STATE_PATH.name}")
            return
        except OSError as exc:
            if self.pin_pick_state_label is not None:
                self.pin_pick_state_label.setText(f"Renderer bridge read failed: {exc}")
            return
        if stat.st_mtime_ns == self.pin_pick_state_mtime_ns:
            return
        next_mtime_ns = stat.st_mtime_ns
        try:
            payload = json.loads(PIN_PICK_STATE_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            if self.pin_pick_state_label is not None:
                self.pin_pick_state_label.setText(f"Renderer bridge parse failed: {exc}")
            return
        self.pin_pick_state_mtime_ns = next_mtime_ns
        if isinstance(payload, dict):
            self.pin_pick_state_payload = payload
            self.apply_renderer_pin_pick_state(payload)

    def apply_renderer_pin_pick_state(self, payload: dict[str, object]) -> None:
        event = str(payload.get("event", "unknown"))
        selected_pin_id = payload.get("selected_pin_id")
        hover_pin = payload.get("hover_pin")
        hover_pin_id = "-"
        if isinstance(hover_pin, dict) and hover_pin.get("id") is not None:
            hover_pin_id = str(hover_pin.get("id"))
        selected_text = str(selected_pin_id) if isinstance(selected_pin_id, str) and selected_pin_id else "-"
        visible_count = payload.get("pin_visible_count", "-")
        frame_index = payload.get("frame_index", "-")
        updated_at = str(payload.get("updated_at_utc", "-"))
        if self.pin_pick_state_label is not None:
            self.pin_pick_state_label.setText(
                f"Renderer bridge: event={event}, selected={selected_text}, hover={hover_pin_id}, "
                f"visible={visible_count}, frame={frame_index}, updated={updated_at}"
            )
        self.pin_pick_state_last_event = event
        self.append_pin_pick_history(payload)
        if event == "selected":
            if isinstance(selected_pin_id, str) and self.pin_id_exists(selected_pin_id):
                self.selected_pin_id = selected_pin_id
                self.refresh_pin_list()
                self.populate_selected_pin_fields()
                self.refresh_command_preview()
                pin = self.selected_pin_packet()
                label = pin.get("label", selected_pin_id) if pin is not None else selected_pin_id
                self.status.setText(f"Renderer 已同步選取 Pin：{label}")
            else:
                self.status.setText(f"Renderer pick 的 Pin 不在目前 Qt Pin list：{selected_text}")
        elif event == "cleared":
            if self.selected_pin_id is not None:
                self.selected_pin_id = None
                self.refresh_pin_list()
                self.refresh_command_preview()
                self.status.setText("Renderer 已清除 Pin 選取")
        self.write_pin_pick_ack(payload)
        self.refresh_research_provenance()

    def write_pin_pick_ack(self, payload: dict[str, object]) -> None:
        event = str(payload.get("event", "unknown"))
        selected_pin_id = payload.get("selected_pin_id")
        ui_synced = True
        if event == "selected":
            ui_synced = isinstance(selected_pin_id, str) and self.selected_pin_id == selected_pin_id
        elif event == "cleared":
            ui_synced = self.selected_pin_id is None
        ack = {
            "schema": "rrkal_displaytools.qt_pin_pick_ack.v1",
            "updated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "event": event,
            "renderer_updated_at_utc": payload.get("updated_at_utc"),
            "renderer_frame_index": payload.get("frame_index"),
            "renderer_selected_pin_id": selected_pin_id,
            "qt_selected_pin_id": self.selected_pin_id,
            "ui_synced": ui_synced,
            "pin_count": len(self.research_pins),
            "source": "rrkal_displaytools_qt_panel",
        }
        try:
            PIN_PICK_ACK_PATH.parent.mkdir(parents=True, exist_ok=True)
            PIN_PICK_ACK_PATH.write_text(json.dumps(ack, ensure_ascii=False, indent=2), encoding="utf-8")
            self.pin_pick_ack_payload = ack
            self.pin_pick_ack_write_error = None
            if self.pin_pick_ack_label is not None:
                self.pin_pick_ack_label.setText(
                    f"Qt ack: event={event}, ui_synced={ui_synced}, selected={self.selected_pin_id or '-'}, "
                    f"updated={ack['updated_at_utc']}"
                )
        except OSError as exc:
            self.pin_pick_ack_write_error = str(exc)
            if self.pin_pick_ack_label is not None:
                self.pin_pick_ack_label.setText(f"Qt ack write failed: {exc}")

    def append_pin_pick_history(self, payload: dict[str, object]) -> None:
        event = str(payload.get("event", "unknown"))
        selected_pin_id = str(payload.get("selected_pin_id") or "-")
        hover_pin = payload.get("hover_pin")
        event_pin = payload.get("event_pin")
        hover_pin_id = str(hover_pin.get("id")) if isinstance(hover_pin, dict) and hover_pin.get("id") is not None else "-"
        event_pin_id = str(event_pin.get("id")) if isinstance(event_pin, dict) and event_pin.get("id") is not None else "-"
        signature = json.dumps(
            {
                "event": event,
                "selected": selected_pin_id,
                "hover": hover_pin_id,
                "event_pin": event_pin_id,
                "frame": payload.get("frame_index"),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        if signature == self.pin_pick_history_signature:
            return
        self.pin_pick_history_signature = signature
        updated_at = str(payload.get("updated_at_utc", "-"))
        visible_count = payload.get("pin_visible_count", "-")
        entry = (
            f"⌖ Pin pick {updated_at}: event={event}, selected={selected_pin_id}, "
            f"hover={hover_pin_id}, event_pin={event_pin_id}, visible={visible_count}"
        )
        self.pin_pick_history.insert(0, entry)
        del self.pin_pick_history[10:]
        if self.history_list is None:
            return
        self.history_list.insertItem(0, entry)
        while self.history_list.count() > 18:
            self.history_list.takeItem(self.history_list.count() - 1)

    def refresh_canvas_preview(self) -> None:
        if self.canvas_preview_label is None or self.canvas_meta_label is None:
            return
        if self.canvas_preview_mode in {"thumbnail", "live_file_stream"} and self.renderer_thumbnail_path is not None:
            if self.render_thumbnail_into_canvas(self.renderer_thumbnail_path):
                sync_note = (
                    "File-based live renderer frame stream."
                    if self.canvas_preview_mode == "live_file_stream"
                    else "Static output preview with auto-refresh."
                )
                self.canvas_meta_label.setText(
                    f"Renderer preview: {self.display_renderer_preview_path(self.renderer_thumbnail_path)}. {sync_note}"
                )
                self.refresh_research_provenance()
                return
            if self.canvas_preview_mode == "live_file_stream":
                self.canvas_preview_label.setPixmap(QtGui.QPixmap())
                self.canvas_preview_label.setText(
                    "Renderer Live Preview\n\n"
                    f"Waiting for {self.display_renderer_preview_path(self.renderer_thumbnail_path)}\n"
                    "Launch or restart renderer to start the file stream."
                )
                self.canvas_meta_label.setText(
                    f"Renderer live preview waiting for {self.display_renderer_preview_path(self.renderer_thumbnail_path)}."
                )
                self.refresh_research_provenance()
                return
            self.canvas_preview_mode = "state"
            self.renderer_thumbnail_path = None
        selected_label = next(
            (text for key, text in LAYER_LABELS if key == self.selected_layer_key),
            self.selected_layer_key or "-",
        )
        tool_label = next((text for mode, text, _hint in TOOL_MODES if mode == self.active_tool), self.active_tool)
        visible = sum(1 for key, _label in LAYER_LABELS if key in self.checks and self.checks[key].isChecked())
        pin_count = len(self.research_pins)
        zoom = self.canvas_zoom_slider.value() if self.canvas_zoom_slider is not None else 100
        selected_pin = self.selected_pin_packet()
        selected_pin_text = (
            f"{selected_pin.get('label', selected_pin.get('id'))} "
            f"@ lat={selected_pin.get('latitude')}, lon={selected_pin.get('longitude')}"
            if selected_pin is not None
            else "-"
        )
        pin_markers = ", ".join(str(pin.get("label", pin.get("id", "pin"))) for pin in self.research_pins[:3])
        if len(self.research_pins) > 3:
            pin_markers = f"{pin_markers}, +{len(self.research_pins) - 3} more"
        if not pin_markers:
            pin_markers = "-"
        cursor_text = (
            f"lat={self.cursor_latitude:.4f}, lon={self.cursor_longitude:.4f}"
            if self.cursor_latitude is not None and self.cursor_longitude is not None
            else "move mouse over canvas"
        )
        style = self.style_combo.currentText() if hasattr(self, "style_combo") else "-"
        topo = self.topo_combo.currentText() if hasattr(self, "topo_combo") else "-"
        data_mode = self.data_combo.currentText() if hasattr(self, "data_combo") else "-"
        hit_keys = self.canvas_layer_hit_keys()
        hit_labels = [next((text for layer_key, text in LAYER_LABELS if layer_key == key), key) for key in hit_keys[:5]]
        hit_map = ", ".join(hit_labels)
        if len(hit_keys) > 5:
            hit_map = f"{hit_map}, +{len(hit_keys) - 5} more"
        if not hit_map:
            hit_map = "-"
        boundary_summary = self.boundary_highlight_summary()
        self.canvas_preview_label.setPixmap(QtGui.QPixmap())
        self.canvas_preview_label.setText(
            "RRKAL Scientific Canvas Preview\n\n"
            f"Style: {style} | Topo: {topo} | Data: {data_mode}\n"
            f"Tool: {tool_label} -> Layer: {selected_label}\n"
            f"Visible layers: {visible}/{len(LAYER_LABELS)} | Pins: {pin_count} | Zoom: {zoom}%\n\n"
            f"Select hit map: {hit_map}\n"
            f"Boundary highlight: {boundary_summary}\n"
            f"Selected pin: {selected_pin_text}\n"
            f"Pin markers: {pin_markers}\n"
            f"Cursor estimate: {cursor_text}\n\n"
            "Qt state preview; renderer state sync and pick bridges are live. Use Renderer thumbnail or Live preview for renderer pixels."
        )
        self.canvas_meta_label.setText(
            f"Canvas state mirrors Qt UI only：active tool={self.active_tool}, "
            f"target layer={self.selected_layer_key or '-'}, style={style}, visible_layers={visible}, "
            f"selected_pin={self.selected_pin_id or '-'}, cursor={cursor_text}, "
            f"boundary_highlight={'on' if self.boundary_highlight_state.get('enabled') else 'off'}."
        )
        self.refresh_research_provenance()

    def latest_renderer_thumbnail_path(self) -> Path | None:
        try:
            candidates = [path for path in SHOWCASE_DIR.glob("*.png") if path.is_file()]
        except OSError:
            return None
        if not candidates:
            return None
        try:
            return max(candidates, key=lambda path: path.stat().st_mtime_ns)
        except OSError:
            return None

    def render_thumbnail_into_canvas(self, path: Path) -> bool:
        if self.canvas_preview_label is None:
            return False
        pixmap = QtGui.QPixmap(str(path))
        if pixmap.isNull():
            return False
        try:
            self.renderer_thumbnail_mtime_ns = path.stat().st_mtime_ns
        except OSError:
            self.renderer_thumbnail_mtime_ns = None
        target_size = self.canvas_preview_label.size()
        scaled = pixmap.scaled(
            target_size,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation,
        )
        self.canvas_preview_label.setPixmap(scaled)
        self.canvas_preview_label.setText("")
        return True

    @QtCore.pyqtSlot()
    def show_canvas_state_preview(self) -> None:
        self.canvas_preview_mode = "state"
        self.renderer_thumbnail_path = None
        self.renderer_thumbnail_mtime_ns = None
        self.refresh_canvas_preview()
        self.status.setText("已切回 Qt Canvas state preview")

    @QtCore.pyqtSlot()
    def show_latest_renderer_thumbnail(self) -> None:
        path = self.latest_renderer_thumbnail_path()
        if path is None:
            self.status.setText("找不到 renderer PNG；可先跑 scripts\\render_quick_smoke.ps1 或 renderer --output")
            return
        self.canvas_preview_mode = "thumbnail"
        self.renderer_thumbnail_path = path
        self.renderer_thumbnail_mtime_ns = None
        self.refresh_canvas_preview()
        self.status.setText(f"已顯示 renderer thumbnail：{path.relative_to(ROOT)}")

    @QtCore.pyqtSlot()
    def show_live_renderer_preview(self) -> None:
        self.canvas_preview_mode = "live_file_stream"
        self.renderer_thumbnail_path = RENDERER_PREVIEW_FRAME_PATH
        self.renderer_thumbnail_mtime_ns = None
        self.refresh_canvas_preview()
        self.status.setText(f"已切到 renderer live preview stream：{RENDERER_PREVIEW_FRAME_PATH.relative_to(ROOT)}")

    def refresh_renderer_thumbnail_if_needed(self) -> None:
        if self.canvas_preview_mode not in {"thumbnail", "live_file_stream"}:
            return
        path = self.renderer_thumbnail_path
        if self.canvas_preview_mode == "live_file_stream":
            path = RENDERER_PREVIEW_FRAME_PATH
        elif path is None or not path.exists():
            path = self.latest_renderer_thumbnail_path()
        if path is None:
            return
        try:
            mtime_ns = path.stat().st_mtime_ns
        except OSError:
            return
        if path == self.renderer_thumbnail_path and mtime_ns == self.renderer_thumbnail_mtime_ns:
            return
        self.renderer_thumbnail_path = path
        if self.render_thumbnail_into_canvas(path) and self.canvas_meta_label is not None:
            sync_note = (
                "File-based live renderer frame stream."
                if self.canvas_preview_mode == "live_file_stream"
                else "Static output preview with auto-refresh."
            )
            self.canvas_meta_label.setText(
                f"Renderer preview auto-refreshed: {self.display_renderer_preview_path(path)}. {sync_note}"
            )
            self.refresh_research_provenance()

    def build_research_provenance(self) -> str:
        visible_layers = [key for key, _label in LAYER_LABELS if key in self.checks and self.checks[key].isChecked()]
        locked_layers = [key for key, _label in LAYER_LABELS if key in self.layer_locks and self.layer_locks[key].isChecked()]
        packet = {
            "schema": "rrkal_displaytools.research_provenance_summary.v1",
            "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "purpose": "research visualization reproducibility summary",
            "renderer": {
                "style_profile": self.style_combo.currentText(),
                "ui_backend": self.ui_combo.currentText(),
                "topo_source": self.topo_combo.currentText(),
                "data_mode": self.data_combo.currentText(),
                "width": self.width_edit.text().strip(),
                "height": self.height_edit.text().strip(),
                "topo_step": self.topo_step_edit.text().strip(),
                "taichi_arch": self.arch_edit.text().strip(),
                "rrkal_data_manifest_ref": self.rrkal_manifest_ref_edit.text().strip(),
            },
            "active_layer": self.selected_layer_key,
            "active_layer_diagnostics": self.active_layer_diagnostics_packet(),
            "active_tool": self.active_tool,
            "cursor_lat_lon_estimate": {
                "latitude": self.cursor_latitude,
                "longitude": self.cursor_longitude,
                "method": "ui_equirectangular_canvas_estimate",
            },
            "selected_pin_id": self.selected_pin_id,
            "selected_pin": self.selected_pin_packet(),
            "pins": self.collect_research_pins(),
            "pin_input_ack_file": str(PIN_INPUT_ACK_PATH),
            "pin_input_ack": self.pin_input_ack_payload,
            "pin_pick_state_file": str(PIN_PICK_STATE_PATH),
            "pin_pick_state_last_event": self.pin_pick_state_last_event,
            "pin_pick_state": self.pin_pick_state_payload,
            "pin_pick_ack_file": str(PIN_PICK_ACK_PATH),
            "pin_pick_ack": self.pin_pick_ack_payload,
            "pin_pick_ack_write_error": self.pin_pick_ack_write_error,
            "pin_pick_history": self.pin_pick_history[:5],
            "layer_runtime_state_file": str(LAYER_RUNTIME_STATE_PATH),
            "layer_runtime_state_last_write_utc": self.layer_runtime_state_last_write_utc,
            "layer_runtime_state_write_error": self.layer_runtime_state_write_error,
            "layer_runtime_ack_file": str(LAYER_RUNTIME_ACK_PATH),
            "layer_runtime_ack": self.layer_runtime_ack_payload,
            "layer_runtime_history": self.layer_runtime_history[:5],
            "layer_pick_state_file": str(LAYER_PICK_STATE_PATH),
            "layer_pick_state": self.layer_pick_state_payload,
            "canvas_select_hit_targets": self.canvas_layer_hit_keys(),
            "canvas_preview": self.collect_canvas_preview_state(),
            "pin_overlay_boundary": "Pins are geodetic annotations; renderer sync must rotate them with the globe and apply horizon/depth occlusion.",
            "pin_projection_contract": pin_projection_contract_packet(),
            "boundary_highlight": self.collect_boundary_highlight_state(),
            "boundary_highlight_ack_file": str(BOUNDARY_HIGHLIGHT_ACK_PATH),
            "boundary_highlight_ack": self.boundary_highlight_ack_payload,
            "boundary_highlight_boundary": "Line hover mask, selected-layer line picking, and closed-ring fill preview are live; full territory feature identity and open-line area inference remain pending.",
            "visible_layers": visible_layers,
            "locked_layers": locked_layers,
            "layer_visibility_snapshot_active": self.layer_visibility_snapshot is not None,
            "layer_count": {
                "visible": len(visible_layers),
                "total": len(LAYER_LABELS),
            },
            "portable_command_line": subprocess.list2cmdline(self.build_portable_command()),
            "boundary": "UI provenance only; renderer image output and RRKAL data manifest are separate artifacts.",
            "rrkal_data_manifest_ref": self.rrkal_manifest_ref_edit.text().strip(),
            "rrkal_data_manifest_ref_boundary": "Reference-only; RRKAL owns manifest/cache governance.",
        }
        return json.dumps(packet, ensure_ascii=False, indent=2)

    def refresh_research_provenance(self) -> None:
        if self.provenance_text is None:
            return
        self.provenance_text.setPlainText(self.build_research_provenance())

    def copy_research_provenance(self) -> None:
        QtWidgets.QApplication.clipboard().setText(self.build_research_provenance())
        if hasattr(self, "status"):
            self.status.setText("已複製科研可重現性摘要")

    def show_layer_runtime_state(self) -> None:
        self.write_layer_runtime_state()
        try:
            text = LAYER_RUNTIME_STATE_PATH.read_text(encoding="utf-8")
        except OSError:
            text = json.dumps(self.collect_layer_runtime_state(), ensure_ascii=False, indent=2)
        self.command_text.setPlainText(text)
        self.status.setText(f"已顯示 layer runtime state JSON：{LAYER_RUNTIME_STATE_PATH}")

    def show_pin_pick_state(self) -> None:
        try:
            text = PIN_PICK_STATE_PATH.read_text(encoding="utf-8")
        except OSError:
            text = json.dumps(self.pin_pick_state_payload or {}, ensure_ascii=False, indent=2)
        self.command_text.setPlainText(text)
        self.status.setText(f"已顯示 Pin pick state JSON：{PIN_PICK_STATE_PATH}")

    def show_layer_pick_state(self) -> None:
        try:
            text = LAYER_PICK_STATE_PATH.read_text(encoding="utf-8")
        except OSError:
            text = json.dumps(self.layer_pick_state_payload or {}, ensure_ascii=False, indent=2)
        self.command_text.setPlainText(text)
        self.status.setText(f"已顯示 layer pick state JSON：{LAYER_PICK_STATE_PATH}")

    def toggle_selected_layer_visibility(self) -> None:
        key = self.selected_layer_key
        if key not in self.checks:
            self.status.setText("尚未選取圖層")
            return
        if self.layer_locks.get(key) is not None and self.layer_locks[key].isChecked():
            self.status.setText("選取圖層已鎖定，visibility 未變更")
            return
        self.checks[key].setChecked(not self.checks[key].isChecked())
        self.refresh_command_preview()
        self.refresh_layer_stack_status()

    def reset_selected_layer_controls(self) -> None:
        key = self.selected_layer_key
        if key not in self.layer_locks:
            self.status.setText("尚未選取圖層")
            return
        self.layer_locks[key].setChecked(False)
        self.layer_opacity[key].setValue(100)
        self.layer_blends[key].setCurrentText("Normal")
        self.refresh_layer_stack_status()
        label = next((text for layer_key, text in LAYER_LABELS if layer_key == key), key)
        self.status.setText(f"已重設選取圖層 UI 狀態：{label}")

    def reset_layer_stack_controls(self) -> None:
        for key, _label in LAYER_LABELS:
            self.layer_locks[key].blockSignals(True)
            self.layer_opacity[key].blockSignals(True)
            self.layer_blends[key].blockSignals(True)
            self.layer_locks[key].setChecked(False)
            self.layer_opacity[key].setValue(100)
            self.layer_blends[key].setCurrentText("Normal")
            self.layer_locks[key].blockSignals(False)
            self.layer_opacity[key].blockSignals(False)
            self.layer_blends[key].blockSignals(False)
        self.refresh_layer_stack_status()
        self.status.setText("已重設 UI-only layer lock/opacity/blend 狀態")

    @QtCore.pyqtSlot()
    def copy_command_to_clipboard(self) -> None:
        QtWidgets.QApplication.clipboard().setText(self.command_text.toPlainText())
        self.status.setText("已複製目前啟動命令")

    @QtCore.pyqtSlot()
    def copy_portable_command_to_clipboard(self) -> None:
        QtWidgets.QApplication.clipboard().setText(subprocess.list2cmdline(self.build_portable_command()))
        self.status.setText("已複製可攜啟動命令")

    @QtCore.pyqtSlot()
    def open_template_dir(self) -> None:
        PROFILE_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(PROFILE_TEMPLATE_DIR)))
        self.status.setText(f"已開啟模板目錄：{PROFILE_TEMPLATE_DIR}")

    @QtCore.pyqtSlot()
    def open_local_profile_dir(self) -> None:
        PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(PROFILE_DIR)))
        self.status.setText(f"已開啟本機配置目錄：{PROFILE_DIR}")

    @QtCore.pyqtSlot()
    def run_smoke_check(self) -> None:
        smoke_script = ROOT / "scripts" / "smoke.ps1"
        if sys.platform == "win32" and smoke_script.exists():
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(smoke_script),
                ],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                timeout=120,
            )
            if result.returncode != 0:
                self.status.setText("Smoke failed")
                self.command_text.setPlainText((result.stderr or result.stdout).strip())
                return
            self.status.setText("Smoke passed")
            self.command_text.setPlainText(result.stdout.strip())
            return
        python_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "py_compile",
                "rrkal_displaytools_qt_panel.py",
                "taichi_global_bathymetry.py",
            ],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            timeout=90,
        )
        if python_result.returncode != 0:
            self.status.setText("Smoke failed: Python compile")
            self.command_text.setPlainText((python_result.stderr or python_result.stdout).strip())
            return
        if sys.platform == "win32":
            ps_command = (
                "$files=Get-ChildItem scripts -Filter *.ps1;"
                "foreach($file in $files){"
                "$tokens=$null;$errors=$null;"
                "[System.Management.Automation.Language.Parser]::ParseFile($file.FullName,[ref]$tokens,[ref]$errors)>$null;"
                "if($errors -and $errors.Count -gt 0){$errors|Format-List *;exit 1}"
                "}"
            )
            ps_result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_command],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                timeout=30,
            )
            if ps_result.returncode != 0:
                self.status.setText("Smoke failed: PowerShell parse")
                self.command_text.setPlainText((ps_result.stderr or ps_result.stdout).strip())
                return
        self.status.setText("Smoke passed: Python compile and script parse")
        self.refresh_command_preview()

    @QtCore.pyqtSlot()
    def save_profile_dialog(self) -> None:
        PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        default_path = PROFILE_DIR / "panel_profile.json"
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "儲存圖層配置",
            str(default_path),
            "JSON profiles (*.json)",
        )
        if not path:
            return
        Path(path).write_text(
            json.dumps(self.collect_profile(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.status.setText(f"已儲存配置：{path}")

    @QtCore.pyqtSlot()
    def export_launch_packet_dialog(self) -> None:
        SHOWCASE_DIR.mkdir(parents=True, exist_ok=True)
        default_path = SHOWCASE_DIR / "launch_packet.json"
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "匯出啟動包",
            str(default_path),
            "JSON packets (*.json)",
        )
        if not path:
            return
        Path(path).write_text(
            json.dumps(self.collect_launch_packet(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.status.setText(f"已匯出啟動包：{path}")

    @QtCore.pyqtSlot()
    def show_renderer_capabilities(self) -> None:
        result = subprocess.run(
            [sys.executable, str(RENDERER), "--print-renderer-capabilities"],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            timeout=90,
        )
        if result.returncode != 0:
            self.status.setText("Renderer capabilities failed")
            self.command_text.setPlainText((result.stderr or result.stdout).strip())
            return
        self.command_text.setPlainText(result.stdout.strip())
        self.status.setText("已顯示 renderer capabilities JSON")

    @QtCore.pyqtSlot()
    def show_closed_loop_status(self) -> None:
        result = subprocess.run(
            [sys.executable, str(RENDERER), "--print-closed-loop-status"],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            timeout=90,
        )
        if result.returncode != 0:
            self.status.setText("Closed-loop status failed")
            self.command_text.setPlainText((result.stderr or result.stdout).strip())
            return
        self.command_text.setPlainText(result.stdout.strip())
        self.status.setText("已顯示 renderer closed-loop status JSON")

    @QtCore.pyqtSlot()
    def show_layer_manifest(self) -> None:
        result = subprocess.run(
            [sys.executable, str(RENDERER), "--print-layer-manifest"],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            timeout=90,
        )
        if result.returncode != 0:
            self.status.setText("Layer manifest failed")
            self.command_text.setPlainText((result.stderr or result.stdout).strip())
            return
        self.command_text.setPlainText(result.stdout.strip())
        self.status.setText("已顯示 renderer layer manifest JSON")

    @QtCore.pyqtSlot()
    def load_profile_dialog(self) -> None:
        PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "載入圖層配置",
            str(PROFILE_DIR),
            "JSON profiles (*.json)",
        )
        if not path:
            return
        self.load_profile_path(Path(path))

    @QtCore.pyqtSlot()
    def launch_renderer(self) -> None:
        if not RENDERER.exists():
            self.status.setText(f"找不到 renderer: {RENDERER}")
            return
        if self.process is not None and self.process.poll() is None:
            self.status.setText(f"renderer 已在執行中，PID={self.process.pid}")
            return
        kwargs: dict[str, object] = {"cwd": str(ROOT)}
        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        self.process = subprocess.Popen(self.build_command(), **kwargs)
        self.status.setText(f"已啟動 renderer，PID={self.process.pid}")

    @QtCore.pyqtSlot()
    def stop_renderer(self) -> None:
        if self.process is None or self.process.poll() is not None:
            self.status.setText("沒有由此面板啟動且仍在執行的 renderer")
            return
        self.process.terminate()
        self.status.setText(f"已要求停止 renderer，PID={self.process.pid}")

    @QtCore.pyqtSlot()
    def restart_renderer(self) -> None:
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
        self.process = None
        self.launch_renderer()

    @QtCore.pyqtSlot()
    def update_process_status(self) -> None:
        if self.process is None:
            return
        pid = self.process.pid
        exit_code = self.process.poll()
        if exit_code is None:
            self.status.setText(f"renderer 執行中，PID={pid}")
            return
        self.status.setText(f"renderer 已結束，PID={pid}，exit={exit_code}")
        self.process = None

    def _set_combo(self, combo: QtWidgets.QComboBox, value: str) -> None:
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _set_layers(self, enabled: dict[str, bool]) -> None:
        for key, check in self.checks.items():
            check.blockSignals(True)
            check.setChecked(enabled.get(key, False))
            check.blockSignals(False)
        self.refresh_command_preview()
        self.refresh_layer_stack_status()

    def _toggle_group(self, keys: tuple[str, ...]) -> None:
        target = not all(self.checks[key].isChecked() for key in keys)
        skipped_locked = 0
        for key in keys:
            if self.layer_locks.get(key) is not None and self.layer_locks[key].isChecked():
                skipped_locked += 1
                continue
            self.checks[key].setChecked(target)
        self.refresh_command_preview()
        if skipped_locked:
            self.status.setText(f"已切換未鎖定圖層；跳過 locked layers：{skipped_locked}")

    @QtCore.pyqtSlot()
    def toggle_hydrology_layers(self) -> None:
        self._toggle_group(("lake_layer", "river_layer"))

    @QtCore.pyqtSlot()
    def toggle_maritime_layers(self) -> None:
        self._toggle_group(("territorial_sea_layer", "eez_layer", "high_seas_layer"))

    @QtCore.pyqtSlot()
    def toggle_transport_layers(self) -> None:
        self._toggle_group(("aircraft_layer", "vehicle_icons"))

    @QtCore.pyqtSlot()
    def toggle_visual_aids(self) -> None:
        self._toggle_group(("show_grid", "show_stars", "terrain_contours", "scale_bar", "pin_layer"))

    @QtCore.pyqtSlot()
    def apply_baseline(self) -> None:
        self._set_combo(self.style_combo, "scientific")
        self._set_combo(self.topo_combo, "gebco")
        self._set_combo(self.data_combo, "static")
        self.topo_step_edit.setText("48")
        self.wave_edit.setText("0.22")
        self.roughness_edit.setText("0.28")
        self.foam_edit.setText("0.12")
        self._set_layers(
            {
                "show_grid": True,
                "show_stars": True,
                "lake_layer": True,
                "river_layer": True,
                "border_layer": True,
                "pin_layer": True,
                "ocean_material": True,
                "scale_bar": True,
            }
        )

    @QtCore.pyqtSlot()
    def apply_maritime(self) -> None:
        self.apply_baseline()
        self._set_combo(self.style_combo, "nautical")
        current = {key: self.checks[key].isChecked() for key in self.checks}
        current.update(
            {
                "territorial_sea_layer": True,
                "eez_layer": True,
                "high_seas_layer": True,
                "terrain_contours": True,
            }
        )
        self._set_layers(current)

    @QtCore.pyqtSlot()
    def apply_parchment(self) -> None:
        self.apply_baseline()
        self._set_combo(self.style_combo, "parchment")
        self.checks["show_stars"].setChecked(False)
        self.checks["terrain_contours"].setChecked(True)

    @QtCore.pyqtSlot()
    def apply_tactical(self) -> None:
        self.apply_maritime()
        self._set_combo(self.style_combo, "tactical")
        self.checks["aircraft_layer"].setChecked(True)
        self.checks["vehicle_icons"].setChecked(True)

    @QtCore.pyqtSlot()
    def apply_minimal(self) -> None:
        self._set_combo(self.style_combo, "scientific")
        self._set_combo(self.topo_combo, "gebco")
        self._set_layers({"ocean_material": True, "scale_bar": True})

    @QtCore.pyqtSlot()
    def apply_fast_synthetic(self) -> None:
        self.apply_baseline()
        self._set_combo(self.topo_combo, "synthetic")
        self.topo_step_edit.setText("64")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RRKAL_displaytools Qt operator panel")
    parser.add_argument("--profile", type=Path, help="Load a panel profile JSON on startup")
    parser.add_argument("--template", help="Load a built-in profile template by file stem, for example maritime_hydrology")
    parser.add_argument("--list-templates", action="store_true", help="Print built-in profile templates as JSON and exit")
    return parser


def resolve_startup_profile(profile: Path | None, template: str | None) -> Path | None:
    if profile is not None:
        return profile
    if not template:
        return None
    template_name = template[:-5] if template.endswith(".json") else template
    return PROFILE_TEMPLATE_DIR / f"{template_name}.json"


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)
    if args.list_templates:
        print(json.dumps(profile_template_packet(), ensure_ascii=False, indent=2))
        return
    app = QtWidgets.QApplication([sys.argv[0]])
    panel = DisplayToolsQtPanel(initial_profile=resolve_startup_profile(args.profile, args.template))
    panel.show()
    raise SystemExit(app.exec())


if __name__ == "__main__":
    main()
