"""Qt operator panel for RRKAL_displaytools layer/UI launch.

This panel intentionally stays outside the renderer loop. It collects operator
choices, builds command-line flags, and starts taichi_global_bathymetry.py.
RRKAL remains responsible for data discovery, download, manifest, and cache
governance; this file is only a displaytools control surface.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

try:
    from PyQt6 import QtCore, QtGui, QtWidgets
except ImportError as exc:
    raise SystemExit(
        "PyQt6 is required for the Qt control panel. Install project dependencies with: "
        "py -3 -m pip install -r requirements.txt"
    ) from exc

ROOT = Path(__file__).resolve().parent
RENDERER = ROOT / "taichi_global_bathymetry.py"
PROFILE_DIR = ROOT / "state" / "ui_profiles"
PROFILE_TEMPLATE_DIR = ROOT / "profiles"

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
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("RRKAL DisplayTools Qt 控制面板")
        self.resize(1120, 780)
        self.process: subprocess.Popen[bytes] | None = None
        self.checks: dict[str, QtWidgets.QCheckBox] = {}
        self.template_paths: list[Path] = []
        self._build_ui()
        self.process_timer = QtCore.QTimer(self)
        self.process_timer.setInterval(1500)
        self.process_timer.timeout.connect(self.update_process_status)
        self.process_timer.start()
        self.apply_baseline()
        self.refresh_template_list()
        self.refresh_command_preview()

    def _build_ui(self) -> None:
        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        main = QtWidgets.QVBoxLayout(central)
        main.setContentsMargins(18, 16, 18, 16)
        main.setSpacing(12)

        title = QtWidgets.QLabel("RRKAL_displaytools 圖層與展示控制")
        title.setObjectName("title")
        subtitle = QtWidgets.QLabel(
            "Qt-first 控制面板：只負責啟動 renderer；RRKAL 仍負責資料下載、manifest、cache governance。"
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

        renderer_group = self._group("Renderer 入口")
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

        material_group = self._group("海洋材質")
        material_form = QtWidgets.QFormLayout(material_group)
        self.wave_edit = QtWidgets.QLineEdit("0.22")
        self.roughness_edit = QtWidgets.QLineEdit("0.28")
        self.foam_edit = QtWidgets.QLineEdit("0.12")
        material_form.addRow("Wave strength", self.wave_edit)
        material_form.addRow("Roughness", self.roughness_edit)
        material_form.addRow("Foam", self.foam_edit)
        left.addWidget(material_group)

        preset_group = self._group("快速 preset")
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

        template_group = self._group("內建 profile templates")
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

        layers_group = self._group("圖層開關")
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
        right.addWidget(layers_group)

        command_group = self._group("啟動命令預覽")
        command_layout = QtWidgets.QVBoxLayout(command_group)
        self.command_text = QtWidgets.QPlainTextEdit()
        self.command_text.setReadOnly(True)
        self.command_text.setMinimumHeight(150)
        command_layout.addWidget(self.command_text)
        right.addWidget(command_group, stretch=1)

        actions = QtWidgets.QHBoxLayout()
        refresh_button = QtWidgets.QPushButton("刷新命令")
        copy_button = QtWidgets.QPushButton("複製命令")
        save_button = QtWidgets.QPushButton("儲存配置")
        load_button = QtWidgets.QPushButton("載入配置")
        open_templates_button = QtWidgets.QPushButton("模板目錄")
        open_local_profiles_button = QtWidgets.QPushButton("本機配置")
        launch_button = QtWidgets.QPushButton("啟動地球儀")
        restart_button = QtWidgets.QPushButton("套用並重啟")
        stop_button = QtWidgets.QPushButton("停止本面板啟動的程序")
        refresh_button.clicked.connect(self.refresh_command_preview)
        copy_button.clicked.connect(self.copy_command_to_clipboard)
        save_button.clicked.connect(self.save_profile_dialog)
        load_button.clicked.connect(self.load_profile_dialog)
        open_templates_button.clicked.connect(self.open_template_dir)
        open_local_profiles_button.clicked.connect(self.open_local_profile_dir)
        launch_button.clicked.connect(self.launch_renderer)
        restart_button.clicked.connect(self.restart_renderer)
        stop_button.clicked.connect(self.stop_renderer)
        actions.addWidget(refresh_button)
        actions.addWidget(copy_button)
        actions.addWidget(save_button)
        actions.addWidget(load_button)
        actions.addWidget(open_templates_button)
        actions.addWidget(open_local_profiles_button)
        actions.addWidget(launch_button)
        actions.addWidget(restart_button)
        actions.addWidget(stop_button)
        right.addLayout(actions)

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
            """
        )

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

    def apply_profile(self, profile: dict[str, object]) -> None:
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

    @QtCore.pyqtSlot()
    def refresh_template_list(self) -> None:
        PROFILE_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
        self.template_paths = sorted(PROFILE_TEMPLATE_DIR.glob("*.json"))
        self.template_combo.clear()
        if not self.template_paths:
            self.template_combo.addItem("沒有內建模板")
            return
        for path in self.template_paths:
            self.template_combo.addItem(path.stem.replace("_", " "), str(path))

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
        profile = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(profile, dict):
            self.status.setText("配置格式錯誤：root 不是 JSON object")
            return
        self.apply_profile(profile)
        self.status.setText(f"已載入配置：{path}")

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


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    panel = DisplayToolsQtPanel()
    panel.show()
    raise SystemExit(app.exec())


if __name__ == "__main__":
    main()
