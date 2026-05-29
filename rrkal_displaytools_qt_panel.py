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

from profile_schema import profile_payload_errors


ROOT = Path(__file__).resolve().parent
PROFILE_TEMPLATE_DIR = ROOT / "profiles"


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
    ("ocean_material", "海洋材質"),
    ("terrain_contours", "地形等高線"),
    ("scale_bar", "比例尺"),
    ("vehicle_icons", "交通工具圖示"),
)

class DisplayToolsQtPanel(QtWidgets.QMainWindow):
    def __init__(self, initial_profile: Path | None = None) -> None:
        super().__init__()
        self.setWindowTitle("RRKAL DisplayTools Qt 控制面板")
        self.resize(1120, 780)
        self.process: subprocess.Popen[bytes] | None = None
        self.checks: dict[str, QtWidgets.QCheckBox] = {}
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
        self.apply_baseline()
        self.refresh_template_list()
        if initial_profile is not None:
            self.load_profile_path(initial_profile)
        self.refresh_command_preview()

    def _build_ui(self) -> None:
        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        main = QtWidgets.QVBoxLayout(central)
        main.setContentsMargins(18, 16, 18, 16)
        main.setSpacing(12)

        title = QtWidgets.QLabel("RRKAL_displaytools Studio")
        title.setObjectName("title")
        subtitle = QtWidgets.QLabel(
            "Photoshop-inspired Qt workspace：左側工具/預設，中間命令與資料預覽，右側圖層與屬性控制。"
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
        renderer_form.addRow("Style profile", self.style_combo)
        renderer_form.addRow("UI backend", self.ui_combo)
        renderer_form.addRow("Topography", self.topo_combo)
        renderer_form.addRow("Data mode", self.data_combo)
        renderer_form.addRow("Width", self.width_edit)
        renderer_form.addRow("Height", self.height_edit)
        renderer_form.addRow("Topo step", self.topo_step_edit)
        renderer_form.addRow("Taichi arch", self.arch_edit)
        left.addWidget(renderer_group)

        material_group = self._group("屬性 / 海洋材質")
        material_form = QtWidgets.QFormLayout(material_group)
        self.wave_edit = QtWidgets.QLineEdit("0.22")
        self.roughness_edit = QtWidgets.QLineEdit("0.28")
        self.foam_edit = QtWidgets.QLineEdit("0.12")
        material_form.addRow("Wave strength", self.wave_edit)
        material_form.addRow("Roughness", self.roughness_edit)
        material_form.addRow("Foam", self.foam_edit)
        properties_dock = QtWidgets.QDockWidget("Properties", self)
        properties_dock.setObjectName("propertiesDock")
        properties_dock.setAllowedAreas(
            QtCore.Qt.DockWidgetArea.LeftDockWidgetArea
            | QtCore.Qt.DockWidgetArea.RightDockWidgetArea
        )
        properties_dock.setWidget(material_group)
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
        layers_layout = QtWidgets.QGridLayout(layers_group)
        for index, (key, label) in enumerate(LAYER_LABELS):
            check = QtWidgets.QCheckBox(label)
            check.stateChanged.connect(self.refresh_command_preview)
            self.checks[key] = check
            layers_layout.addWidget(check, index // 2, index % 2)
        demo = QtWidgets.QCheckBox("閉環展示 preset（會覆蓋部分設定）")
        demo.stateChanged.connect(self.refresh_command_preview)
        self.checks["demo_closed_loop"] = demo
        layers_layout.addWidget(demo, 7, 0, 1, 2)
        layer_actions = (
            ("水文開/關", self.toggle_hydrology_layers),
            ("海域開/關", self.toggle_maritime_layers),
            ("交通開/關", self.toggle_transport_layers),
            ("輔助開/關", self.toggle_visual_aids),
        )
        for index, (label, callback) in enumerate(layer_actions):
            button = QtWidgets.QPushButton(label)
            button.clicked.connect(callback)
            layers_layout.addWidget(button, 8 + index // 2, index % 2)
        layers_dock = QtWidgets.QDockWidget("Layers", self)
        layers_dock.setObjectName("layersDock")
        layers_dock.setAllowedAreas(
            QtCore.Qt.DockWidgetArea.LeftDockWidgetArea
            | QtCore.Qt.DockWidgetArea.RightDockWidgetArea
        )
        layers_dock.setWidget(layers_group)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, layers_dock)

        command_group = self._group("中央預覽 / Command and JSON preview")
        command_layout = QtWidgets.QVBoxLayout(command_group)
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
        layer_manifest_button = QtWidgets.QPushButton("圖層 manifest")
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
        layer_manifest_button.clicked.connect(self.show_layer_manifest)
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
            layer_manifest_button,
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
        renderer_menu.addAction("Layer Manifest JSON", self.show_layer_manifest)

        window_menu = self.menuBar().addMenu("Window")
        window_menu.addAction("Open Template Folder", self.open_template_dir)
        window_menu.addAction("Open Local Profile Folder", self.open_local_profile_dir)
        window_menu.addSeparator()
        window_menu.addAction("Save Workspace Layout", self.save_workspace_layout)
        window_menu.addAction("Load Workspace Layout", self.load_workspace_layout)
        window_menu.addAction("Reset Saved Workspace Layout", self.reset_workspace_layout)

        help_menu = self.menuBar().addMenu("Help")
        help_menu.addAction("Smoke Check", self.run_smoke_check)

    def _build_tool_dock(self) -> None:
        dock = QtWidgets.QDockWidget("Tools", self)
        dock.setObjectName("toolsDock")
        dock.setAllowedAreas(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea | QtCore.Qt.DockWidgetArea.RightDockWidgetArea)
        tools = QtWidgets.QWidget(dock)
        layout = QtWidgets.QVBoxLayout(tools)
        layout.setContentsMargins(8, 8, 8, 8)
        tool_actions = (
            ("Baseline", self.apply_baseline),
            ("Maritime", self.apply_maritime),
            ("Parchment", self.apply_parchment),
            ("Tactical", self.apply_tactical),
            ("Smoke", self.run_smoke_check),
            ("Caps", self.show_renderer_capabilities),
            ("Layers", self.show_layer_manifest),
        )
        for label, callback in tool_actions:
            button = QtWidgets.QToolButton()
            button.setText(label)
            button.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextOnly)
            button.clicked.connect(callback)
            layout.addWidget(button)
        layout.addStretch(1)
        dock.setWidget(tools)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, dock)

    def _build_auxiliary_docks(self) -> None:
        navigator_dock = QtWidgets.QDockWidget("Navigator", self)
        navigator_dock.setObjectName("navigatorDock")
        navigator = QtWidgets.QWidget(navigator_dock)
        navigator_layout = QtWidgets.QVBoxLayout(navigator)
        navigator_layout.setContentsMargins(10, 10, 10, 10)
        preview = QtWidgets.QLabel("🚧 Navigator preview\n施工中：live renderer thumbnail")
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
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, navigator_dock)

        history_dock = QtWidgets.QDockWidget("History", self)
        history_dock.setObjectName("historyDock")
        self.history_list = QtWidgets.QListWidget()
        for item in (
            "✅ Qt Studio workspace loaded",
            "✅ Profile/template launch flow",
            "✅ Layer manifest/capabilities preview",
            "🚧 Live renderer layer sync",
            "🚧 Brush/mask tools",
            "🚧 Timeline/keyframes",
            "🚧 Undo stack",
        ):
            self.history_list.addItem(item)
        history_dock.setWidget(self.history_list)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, history_dock)

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
            self.wave_edit,
            self.roughness_edit,
            self.foam_edit,
        ):
            edit.textChanged.connect(self.refresh_command_preview)

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
        ]
        for key, flag in BOOL_FLAGS.items():
            enabled = self.checks[key].isChecked()
            cmd.append(f"--{flag}" if enabled else f"--no-{flag}")
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
            },
            "ocean_material": {
                "wave_strength": self.wave_edit.text().strip(),
                "roughness": self.roughness_edit.text().strip(),
                "foam": self.foam_edit.text().strip(),
            },
            "layers": {key: check.isChecked() for key, check in self.checks.items()},
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
            "command": self.build_command(),
            "command_line": subprocess.list2cmdline(self.build_command()),
            "portable_command": self.build_portable_command(),
            "portable_command_line": subprocess.list2cmdline(self.build_portable_command()),
        }

    def apply_profile(self, profile: dict[str, object]) -> None:
        errors = profile_payload_errors(profile)
        if errors:
            self.status.setText("配置格式錯誤")
            self.command_text.setPlainText("\n".join(errors))
            return
        renderer = profile.get("renderer", {})
        material = profile.get("ocean_material", {})
        layers = profile.get("layers", {})
        if isinstance(renderer, dict):
            self._set_combo(self.style_combo, str(renderer.get("style_profile", self.style_combo.currentText())))
            self._set_combo(self.ui_combo, str(renderer.get("ui_backend", self.ui_combo.currentText())))
            self._set_combo(self.topo_combo, str(renderer.get("topo_source", self.topo_combo.currentText())))
            self._set_combo(self.data_combo, str(renderer.get("data_mode", self.data_combo.currentText())))
            self.width_edit.setText(str(renderer.get("width", self.width_edit.text())))
            self.height_edit.setText(str(renderer.get("height", self.height_edit.text())))
            self.topo_step_edit.setText(str(renderer.get("topo_step", self.topo_step_edit.text())))
            self.arch_edit.setText(str(renderer.get("taichi_arch", self.arch_edit.text())))
        if isinstance(material, dict):
            self.wave_edit.setText(str(material.get("wave_strength", self.wave_edit.text())))
            self.roughness_edit.setText(str(material.get("roughness", self.roughness_edit.text())))
            self.foam_edit.setText(str(material.get("foam", self.foam_edit.text())))
        if isinstance(layers, dict):
            for key, value in layers.items():
                if key in self.checks:
                    self.checks[key].setChecked(bool(value))
        self.refresh_command_preview()

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

    def _toggle_group(self, keys: tuple[str, ...]) -> None:
        target = not all(self.checks[key].isChecked() for key in keys)
        for key in keys:
            self.checks[key].setChecked(target)
        self.refresh_command_preview()

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
        self._toggle_group(("show_grid", "show_stars", "terrain_contours", "scale_bar"))

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
