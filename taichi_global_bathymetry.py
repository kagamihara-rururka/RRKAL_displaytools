import argparse
import datetime
import gzip
import io
import json
import math
import os
import platform
import re
import atexit
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
from pin_projection import pin_projection_contract_packet, project_pins_to_screen
try:
    import xarray as xr
except ImportError:
    xr = None
try:
    from tqdm import tqdm
except ImportError:
    class tqdm:
        def __init__(self, *args, **kwargs):
            self.total = kwargs.get("total", None)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            self.close()
            return False

        def update(self, amount: int = 1) -> None:
            return None

        def close(self) -> None:
            return None

try:
    import datashader as ds
    import datashader.transfer_functions as tf
except ImportError as exc:
    ds = None
    tf = None
    DATASHADER_IMPORT_ERROR = exc
else:
    DATASHADER_IMPORT_ERROR = None

try:
    import taichi as ti
except ImportError as exc:
    class _MissingTaichi:
        cpu = "cpu"
        cuda = "cuda"
        vulkan = "vulkan"
        opengl = "opengl"
        metal = "metal"
        f32 = "f32"
        i32 = "i32"
        i16 = "i16"
        u8 = "u8"

        def __getattr__(self, name):
            raise RuntimeError("Taichi is required before using Taichi runtime APIs.")

        def func(self, fn):
            return fn

        def kernel(self, fn):
            return fn

        def data_oriented(self, cls):
            return cls

    ti = _MissingTaichi()
    TAICHI_IMPORT_ERROR = exc
else:
    TAICHI_IMPORT_ERROR = None

try:
    import vispy
except ImportError as exc:
    vispy = None
    VISPY_IMPORT_ERROR = exc
else:
    VISPY_IMPORT_ERROR = None

try:
    from api_launcher.renderer_contracts import (
        GEBCO_2025_OPENDAP_URL,
        GEBCO_2025_TOPOGRAPHY_CONTRACT,
        GEBCO_2025_TOPO_SOURCE,
        HYG_V38_STAR_CONTRACT,
        HYG_V38_URL,
    )
except Exception:
    GEBCO_2025_TOPO_SOURCE = "gebco_2025"
    GEBCO_2025_OPENDAP_URL = (
        "https://dap.ceda.ac.uk/thredds/dodsC/bodc/gebco/global/"
        "gebco_2025/ice_surface_elevation/netcdf/GEBCO_2025.nc"
    )
    GEBCO_2025_TOPOGRAPHY_CONTRACT = None
    HYG_V38_STAR_CONTRACT = None
    HYG_V38_URL = (
        "https://raw.githubusercontent.com/astronexus/HYG-Database/main/"
        "hyg/v3/hyg_v38.csv.gz"
    )


SCRIPT_DIR = Path(__file__).resolve().parent
CACHE_DIR = Path(os.environ.get("AIS_RENDER_CACHE_DIR", Path.home() / ".cache" / "taichi_earth"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)


STARTUP_PROGRESS = None


class StartupProgressDialog:
    def __init__(self, enabled: bool):
        self.enabled = False
        self.value = 0
        if not enabled:
            return
        try:
            from PyQt6 import QtWidgets

            self.QtWidgets = QtWidgets
            self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
            self.dialog = QtWidgets.QProgressDialog("準備資料快取...", None, 0, 100)
            self.dialog.setWindowTitle("資料載入進度")
            self.dialog.setCancelButton(None)
            self.dialog.setMinimumDuration(0)
            self.dialog.setAutoClose(False)
            self.dialog.setAutoReset(False)
            self.dialog.resize(420, 96)
            self.dialog.show()
            self.app.processEvents()
            self.enabled = True
        except Exception as exc:
            print(f"GUI startup progress unavailable: {exc}")

    def begin(self, label: str, total: int | None = None) -> None:
        if not self.enabled:
            return
        self.value = 0
        if total is None or total <= 0:
            self.dialog.setRange(0, 0)
            self.dialog.setValue(0)
        else:
            self.dialog.setRange(0, int(total))
            self.dialog.setValue(0)
        self.dialog.setLabelText(label)
        self.dialog.show()
        self.app.processEvents()

    def update(self, amount: int = 1, label: str | None = None) -> None:
        if not self.enabled:
            return
        if label:
            self.dialog.setLabelText(label)
        if self.dialog.maximum() > 0:
            self.value = min(self.dialog.maximum(), self.value + int(amount))
            self.dialog.setValue(self.value)
        self.app.processEvents()

    def set_value(self, value: int, total: int, label: str | None = None) -> None:
        if not self.enabled:
            return
        total = max(1, int(total))
        if self.dialog.maximum() != total:
            self.dialog.setRange(0, total)
        self.value = max(0, min(total, int(value)))
        if label:
            self.dialog.setLabelText(label)
        self.dialog.setValue(self.value)
        self.dialog.show()
        self.app.processEvents()

    def message(self, label: str) -> None:
        if not self.enabled:
            return
        self.dialog.setLabelText(label)
        self.dialog.show()
        self.app.processEvents()

    def done(self, label: str | None = None) -> None:
        if not self.enabled:
            return
        if label:
            self.dialog.setLabelText(label)
        if self.dialog.maximum() > 0:
            self.dialog.setValue(self.dialog.maximum())
        self.app.processEvents()

    def close(self) -> None:
        if not self.enabled:
            return
        self.dialog.close()
        self.app.processEvents()


def setup_startup_progress(enabled: bool) -> None:
    global STARTUP_PROGRESS
    STARTUP_PROGRESS = StartupProgressDialog(enabled)


def startup_progress_begin(label: str, total: int | None = None) -> None:
    if STARTUP_PROGRESS is not None:
        STARTUP_PROGRESS.begin(label, total)


def startup_progress_update(amount: int = 1, label: str | None = None) -> None:
    if STARTUP_PROGRESS is not None:
        STARTUP_PROGRESS.update(amount, label)


def startup_progress_set(value: int, total: int, label: str | None = None) -> None:
    if STARTUP_PROGRESS is not None:
        STARTUP_PROGRESS.set_value(value, total, label)


def startup_progress_message(label: str) -> None:
    if STARTUP_PROGRESS is not None:
        STARTUP_PROGRESS.message(label)


def startup_progress_done(label: str | None = None) -> None:
    if STARTUP_PROGRESS is not None:
        STARTUP_PROGRESS.done(label)


def close_startup_progress() -> None:
    global STARTUP_PROGRESS
    if STARTUP_PROGRESS is not None:
        STARTUP_PROGRESS.close()
        STARTUP_PROGRESS = None

MIN_ELEV = -11000.0
MAX_ELEV = 8848.0
PI = math.pi
INV_PI = 1.0 / math.pi
INV_TWO_PI = 1.0 / (2.0 * math.pi)

TOPO_CMAP = [
    (0.01, 0.03, 0.14),
    (0.01, 0.14, 0.36),
    (0.02, 0.39, 0.62),
    (0.20, 0.68, 0.72),
    (0.10, 0.35, 0.14),
    (0.42, 0.52, 0.22),
    (0.66, 0.54, 0.31),
    (0.55, 0.52, 0.48),
    (0.95, 0.95, 0.90),
]
SHIP_DENSITY_CMAP = ["#21d4fd", "#b8f35a", "#ffe05d", "#ff6b3d", "#ff2d55"]
SHIP_SPEED_CMAP = ["#38e8ff", "#56f57a", "#ffe05d", "#ff873d", "#ff2d55"]
AIRCRAFT_ALTITUDE_CMAP = ["#4cc9f0", "#4361ee", "#7209b7", "#f72585", "#ffd166"]
AIRCRAFT_SPEED_CMAP = ["#6ee7ff", "#80ff72", "#ffd166", "#f3722c", "#d00000"]
AIRCRAFT_DENSITY_CMAP = ["#4cc9f0", "#80ff72", "#ffd166", "#f3722c", "#d00000"]
DATASHADER_STYLE_CMAPS = {
    "scientific": {
        "ais_speed": SHIP_SPEED_CMAP,
        "ais_density": SHIP_DENSITY_CMAP,
        "aircraft_altitude": AIRCRAFT_ALTITUDE_CMAP,
        "aircraft_speed": AIRCRAFT_SPEED_CMAP,
        "aircraft_density": AIRCRAFT_DENSITY_CMAP,
    },
    "nautical": {
        "ais_speed": ["#7df9ff", "#3fe7c8", "#f7f7a1", "#ffb347", "#ff5f5f"],
        "ais_density": ["#073b4c", "#118ab2", "#06d6a0", "#ffd166", "#ef476f"],
        "aircraft_altitude": ["#80ffdb", "#64dfdf", "#48bfe3", "#5390d9", "#ffcad4"],
        "aircraft_speed": ["#80ffdb", "#72efdd", "#ffd166", "#f77f00", "#d62828"],
        "aircraft_density": ["#118ab2", "#06d6a0", "#ffd166", "#f77f00", "#ef476f"],
    },
    "tactical": {
        "ais_speed": ["#1bff5a", "#a6ff00", "#fff700", "#ff9e00", "#ff3131"],
        "ais_density": ["#073b12", "#00a843", "#70ff70", "#fff700", "#ff3131"],
        "aircraft_altitude": ["#39ff14", "#a6ff00", "#ffe600", "#ff9e00", "#ff3131"],
        "aircraft_speed": ["#39ff14", "#a6ff00", "#ffe600", "#ff9e00", "#ff3131"],
        "aircraft_density": ["#073b12", "#00a843", "#70ff70", "#fff700", "#ff3131"],
    },
    "parchment": {
        "ais_speed": ["#2f5d62", "#5e8b7e", "#c2b280", "#b86f34", "#8f2d1c"],
        "ais_density": ["#3b2f2f", "#6b4f2a", "#9f7e45", "#c9a86a", "#7f3121"],
        "aircraft_altitude": ["#4b3621", "#7f5539", "#9c6644", "#b08968", "#7f1d1d"],
        "aircraft_speed": ["#3d405b", "#6b705c", "#b7b7a4", "#cb997e", "#9d0208"],
        "aircraft_density": ["#3b2f2f", "#6b4f2a", "#9f7e45", "#c9a86a", "#7f3121"],
    },
}

LAT_ALIASES = (
    "lat",
    "latitude",
    "y",
    "position.lat",
    "position.latitude",
    "navigation.lat",
    "ais.lat",
)
LON_ALIASES = (
    "lon",
    "lng",
    "long",
    "longitude",
    "x",
    "position.lon",
    "position.lng",
    "position.longitude",
    "navigation.lon",
    "ais.lon",
)
COLUMN_ALIASES = {
    "mmsi": ("mmsi", "MMSI", "ship_mmsi", "vessel_mmsi", "id"),
    "sog": ("sog", "SOG", "speed", "speed_knots", "speed_over_ground"),
    "cog": ("cog", "COG", "course", "course_over_ground"),
    "heading": ("heading", "true_heading", "hdg", "HDG"),
    "timestamp": (
        "timestamp",
        "time",
        "datetime",
        "received_at",
        "last_seen",
        "last_position_update",
    ),
    "name": ("name", "shipname", "vessel_name", "ship_name"),
}
AIRCRAFT_COLUMN_ALIASES = {
    "icao24": ("icao24", "icao", "hex", "hexident", "aircraft_id", "id"),
    "callsign": ("callsign", "call_sign", "flight", "flight_id", "ident"),
    "altitude_m": ("altitude_m", "alt_m", "baro_altitude", "geo_altitude", "altitude", "height_m"),
    "altitude_ft": ("altitude_ft", "alt_ft", "baro_altitude_ft", "geo_altitude_ft", "height_ft"),
    "speed_kt": ("speed_kt", "speed_knots", "groundspeed", "gs", "ground_speed_kt"),
    "speed_ms": ("speed_ms", "velocity", "ground_speed_ms", "speed_mps"),
    "heading": ("heading", "track", "true_track", "course"),
    "timestamp": ("timestamp", "time", "last_seen", "last_contact", "seen", "received_at"),
}
DEFAULT_AIS_DB_TABLE = "ais_positions"
DEFAULT_AIS_DB_LIMIT = 200000
DEFAULT_AIRCRAFT_DB_TABLE = "aircraft_positions"
DEFAULT_AIRCRAFT_DB_LIMIT = 200000


def configure_stdio() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is not None and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def parse_bool(value: object, default: bool = False) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def parse_int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def parse_float_env(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def normalize_name(name: object) -> str:
    return "".join(ch for ch in str(name).lower() if ch.isalnum())


def find_column(frame: pd.DataFrame, aliases: tuple[str, ...]) -> str | None:
    normalized = {normalize_name(col): col for col in frame.columns}
    for alias in aliases:
        found = normalized.get(normalize_name(alias))
        if found is not None:
            return found
    return None


def align_to_multiple(value: int, multiple: int = 8) -> int:
    return max(multiple, value - value % multiple)


def ensure_dependencies(headless: bool) -> None:
    if TAICHI_IMPORT_ERROR is not None:
        raise SystemExit("Taichi is required. Install with: py -3.13 -m pip install taichi")
    if DATASHADER_IMPORT_ERROR is not None:
        raise SystemExit(
            "Datashader is required. Install with: py -3.13 -m pip install datashader"
        )
    if not headless and VISPY_IMPORT_ERROR is not None:
        raise SystemExit("VisPy is required. Install with: py -3.13 -m pip install vispy glfw")


def init_taichi(arch_name: str | None) -> object:
    preferred = (arch_name or os.environ.get("TAICHI_ARCH", "")).strip().lower()
    system = platform.system()
    arch_order = {
        "metal": [ti.metal, ti.cpu],
        "vulkan": [ti.vulkan, ti.cpu],
        "cuda": [ti.cuda, ti.cpu],
        "opengl": [ti.opengl, ti.cpu],
        "gpu": [ti.vulkan, ti.cuda, ti.opengl, ti.cpu],
        "cpu": [ti.cpu],
    }

    if preferred in arch_order:
        candidates = arch_order[preferred]
    elif system == "Darwin":
        candidates = [ti.metal, ti.vulkan, ti.cpu]
    elif system == "Windows":
        candidates = [ti.vulkan, ti.cuda, ti.opengl, ti.cpu]
    else:
        candidates = [ti.cuda, ti.vulkan, ti.opengl, ti.cpu]

    last_error = None
    for arch in candidates:
        try:
            ti.init(arch=arch, default_fp=ti.f32, default_ip=ti.i32)
            print(f"Taichi backend: {arch}")
            return arch
        except Exception as exc:
            last_error = exc
            print(f"Taichi backend {arch} unavailable: {exc}")

    raise RuntimeError("No usable Taichi backend was found") from last_error


def topography_cache_path(step: int) -> Path:
    if GEBCO_2025_TOPOGRAPHY_CONTRACT is not None:
        return Path(GEBCO_2025_TOPOGRAPHY_CONTRACT.cache_path(step=step))
    return CACHE_DIR / f"{GEBCO_2025_TOPO_SOURCE}_topo_cache_step{step}.npy"


def star_cache_path() -> Path:
    if HYG_V38_STAR_CONTRACT is not None:
        return Path(HYG_V38_STAR_CONTRACT.cache_path())
    return CACHE_DIR / "stars_cache.npy"


def derive_topography_cache_from_finer_step(requested_step: int, target_path: Path) -> np.ndarray | None:
    pattern = f"{GEBCO_2025_TOPO_SOURCE}_topo_cache_step*.npy"
    candidates = []
    for path in set(CACHE_DIR.glob(pattern)) | set(target_path.parent.glob(pattern)):
        match = re.search(r"_step(\d+)\.npy$", path.name)
        if not match:
            continue
        cached_step = int(match.group(1))
        if cached_step <= 0 or cached_step == requested_step:
            continue
        if requested_step % cached_step == 0:
            candidates.append((cached_step, path))

    if not candidates:
        return None

    cached_step, source_path = max(candidates, key=lambda item: item[0])
    stride = requested_step // cached_step
    print(
        f"Deriving GEBCO step={requested_step} cache from existing "
        f"step={cached_step}: {source_path}"
    )
    startup_progress_begin(f"從既有地形快取建立 step={requested_step}", None)
    source = np.load(source_path, mmap_mode="r")
    topo = np.ascontiguousarray(source[::stride, ::stride].astype(np.int16, copy=False))
    np.save(target_path, topo)
    print(f"Saved derived topography cache: {target_path}")
    startup_progress_done(f"地形 step={requested_step} 快取完成")
    return topo


def interpolate_stops(stops: list[tuple[float, tuple[float, float, float]]], count: int) -> np.ndarray:
    stops_np = [(pos, np.asarray(color, dtype=np.float32)) for pos, color in stops]
    xs = np.linspace(0.0, 1.0, count, dtype=np.float32)
    out = np.empty((count, 3), dtype=np.float32)
    for i, x in enumerate(xs):
        for j in range(len(stops_np) - 1):
            left_pos, left_color = stops_np[j]
            right_pos, right_color = stops_np[j + 1]
            if x <= right_pos or j == len(stops_np) - 2:
                t = (x - left_pos) / max(right_pos - left_pos, 1e-6)
                out[i] = left_color * (1.0 - t) + right_color * t
                break
    return np.clip(out, 0.0, 1.0)


def build_taichi_colormap() -> np.ndarray:
    ocean = interpolate_stops(
        [
            (0.0, (0.005, 0.018, 0.080)),
            (0.36, (0.010, 0.080, 0.210)),
            (0.76, (0.025, 0.190, 0.360)),
            (1.0, (0.075, 0.360, 0.520)),
        ],
        128,
    )
    land = interpolate_stops(
        [
            (0.0, (0.105, 0.360, 0.095)),
            (0.12, (0.180, 0.450, 0.130)),
            (0.34, (0.390, 0.520, 0.180)),
            (0.56, (0.670, 0.560, 0.280)),
            (0.76, (0.530, 0.390, 0.230)),
            (0.90, (0.620, 0.580, 0.520)),
            (1.0, (0.960, 0.950, 0.900)),
        ],
        128,
    )
    return np.vstack((ocean, land)).astype(np.float32)


def synthetic_topography(step: int) -> np.ndarray:
    h = max(360, 43200 // max(step, 1) + 1)
    w = max(720, 86400 // max(step, 1) + 1)
    lat = np.linspace(-90.0, 90.0, h, dtype=np.float32)
    lon = np.linspace(-180.0, 180.0, w, dtype=np.float32)
    lon_r, lat_r = np.meshgrid(np.radians(lon), np.radians(lat))

    continents = (
        3000.0 * np.sin(2.1 * lon_r) * np.cos(1.4 * lat_r)
        + 1800.0 * np.sin(3.3 * lon_r + 0.8) * np.sin(2.0 * lat_r)
        + 900.0 * np.cos(5.5 * lon_r - lat_r)
    )
    ocean_bias = -2200.0 + 1200.0 * np.cos(lat_r) ** 2
    return np.rint(continents + ocean_bias).astype(np.int16)


def load_topography(step: int, source: str, chunk_rows: int) -> np.ndarray:
    cache_path = topography_cache_path(step)
    if source == "synthetic":
        print(f"Using synthetic topography, step={step}")
        return synthetic_topography(step)

    if cache_path.exists():
        print(f"Using cached topography: {cache_path}")
        startup_progress_message(f"讀取地形快取：{cache_path.name}")
        return np.ascontiguousarray(np.load(cache_path))

    if source == "gebco":
        derived = derive_topography_cache_from_finer_step(step, cache_path)
        if derived is not None:
            return derived

    try:
        print(f"Opening GEBCO topography: {GEBCO_2025_OPENDAP_URL}")
        dataset = xr.open_dataset(GEBCO_2025_OPENDAP_URL, decode_times=False)
        elevation = dataset["elevation"][::step, ::step]
        h, w = elevation.shape
        estimated_mb = h * w * np.dtype(np.int16).itemsize / (1024 * 1024)
        print(f"Downloading topography grid {h}x{w}, about {estimated_mb:.1f} MiB")

        topo = np.empty((h, w), dtype=np.int16)
        total = (h + chunk_rows - 1) // chunk_rows
        startup_progress_begin(f"下載 GEBCO 地形快取 {h}x{w}，約 {estimated_mb:.1f} MiB", total)
        with tqdm(total=total, desc="Topography", unit="chunk") as progress:
            for row0 in range(0, h, chunk_rows):
                row1 = min(row0 + chunk_rows, h)
                block = elevation[row0:row1, :].values
                topo[row0:row1, :] = block.astype(np.int16, copy=False)
                progress.update(1)
                startup_progress_update(1, f"下載 GEBCO 地形：{row1:,}/{h:,} rows")
        np.save(cache_path, topo)
        startup_progress_done("GEBCO 地形快取完成")
        return np.ascontiguousarray(topo)
    except Exception as exc:
        print(f"GEBCO load failed, using synthetic topography: {exc}")
        topo = synthetic_topography(step)
        np.save(cache_path, topo)
        return np.ascontiguousarray(topo)


SURFACE_UNKNOWN = 0
SURFACE_OCEAN = 1
SURFACE_LAND = 2
SURFACE_INLAND_WATER = 3


def land_mask_cache_path(source: str, topo_shape: tuple[int, int], sea_level_m: float = 0.0) -> Path:
    h, w = topo_shape
    sea_tag = f"sl{int(round(float(sea_level_m)))}"
    return CACHE_DIR / f"surface_mask_v2_{source}_{h}x{w}_{sea_tag}.npy"


def natural_earth_resolution(source: str) -> str:
    source = (source or "ne50").strip().lower()
    if source in {"naturalearth", "ne", "ne50", "naturalearth50", "50m"}:
        return "50m"
    if source in {"ne10", "naturalearth10", "10m"}:
        return "10m"
    if source in {"ne110", "naturalearth110", "110m"}:
        return "110m"
    return "50m"


def natural_earth_geojson_path(source: str, layer: str = "land") -> Path:
    resolution = natural_earth_resolution(source)
    layer = (layer or "land").strip().lower()
    return CACHE_DIR / f"ne_{resolution}_{layer}.geojson"


def download_natural_earth_geojson(path: Path, source: str, layer: str = "land") -> None:
    resolution = natural_earth_resolution(source)
    layer = (layer or "land").strip().lower()
    resolutions = []
    for item in (resolution, "50m", "110m"):
        if item not in resolutions:
            resolutions.append(item)
    urls = [
        f"https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_{res}_{layer}.geojson"
        for res in resolutions
    ]
    last_error = None
    for url in urls:
        try:
            print(f"Downloading Natural Earth {layer} mask: {url}")
            startup_progress_begin(f"下載 Natural Earth {layer} 遮罩：{resolution}", None)
            text = read_url_text(url, timeout=60.0)
            path.write_text(text, encoding="utf-8")
            startup_progress_done(f"Natural Earth {layer} 遮罩下載完成")
            return
        except Exception as exc:
            last_error = exc
    raise RuntimeError(f"Natural Earth {layer} GeoJSON download failed") from last_error


def download_natural_earth_land_geojson(path: Path, source: str) -> None:
    download_natural_earth_geojson(path, source, "land")


def elevation_land_mask(topo: np.ndarray, sea_level_m: float = 0.0) -> np.ndarray:
    mask = np.full(np.asarray(topo).shape, SURFACE_OCEAN, dtype=np.uint8)
    mask[np.asarray(topo) >= float(sea_level_m)] = SURFACE_LAND
    return mask


def load_land_mask(
    topo: np.ndarray,
    source: str,
    chunk_rows: int,
    sea_level_m: float = 0.0,
) -> np.ndarray:
    source = (source or "naturalearth").strip().lower()
    if source in {"none", "off"}:
        return np.full(topo.shape, SURFACE_UNKNOWN, dtype=np.uint8)
    if source in {"elevation", "height"}:
        return elevation_land_mask(topo, sea_level_m)

    cache_path = land_mask_cache_path(source, topo.shape, sea_level_m)
    if cache_path.exists():
        print(f"Using cached surface mask: {cache_path}")
        startup_progress_message(f"讀取海陸分類快取：{cache_path.name}")
        return np.ascontiguousarray(np.load(cache_path).astype(np.uint8, copy=False))

    if source not in {"naturalearth", "ne", "ne110", "ne50", "ne10", "naturalearth110", "naturalearth50", "naturalearth10", "110m", "50m", "10m"}:
        print(f"Unknown land mask source={source}; using elevation mask")
        return elevation_land_mask(topo, sea_level_m)

    try:
        import shapely
        from shapely.geometry import shape
        from shapely.ops import unary_union
    except Exception as exc:
        print(
            "Natural Earth land mask requires shapely. "
            "Install with: python -m pip install shapely. "
            f"Using elevation mask for now: {exc}"
        )
        return elevation_land_mask(topo, sea_level_m)

    def load_natural_earth_union(layer: str):
        geojson_path = natural_earth_geojson_path(source, layer)
        if not geojson_path.exists():
            download_natural_earth_geojson(geojson_path, source, layer)
        obj = json.loads(geojson_path.read_text(encoding="utf-8"))
        polygons = [shape(feature["geometry"]) for feature in obj.get("features", []) if feature.get("geometry")]
        if not polygons:
            return None
        geom = unary_union(polygons)
        try:
            shapely.prepare(geom)
        except Exception:
            pass
        return geom

    try:
        land = load_natural_earth_union("land")
        ocean = load_natural_earth_union("ocean")
    except Exception as exc:
        print(f"Natural Earth land/ocean mask unavailable; using elevation mask: {exc}")
        return elevation_land_mask(topo, sea_level_m)

    try:
        inland_water = load_natural_earth_union("lakes")
    except Exception as exc:
        print(f"Natural Earth lakes mask unavailable; continuing without inland-water classification: {exc}")
        inland_water = None

    if land is None or ocean is None:
        print("Natural Earth land/ocean polygons incomplete; using elevation mask")
        return elevation_land_mask(topo, sea_level_m)

    def contains_xy_safe(geom, lon_grid, lat_grid):
        if geom is None:
            return np.zeros(lon_grid.shape, dtype=bool)
        try:
            return shapely.contains_xy(geom, lon_grid, lat_grid)
        except AttributeError:
            from shapely.vectorized import contains

            return contains(geom, lon_grid, lat_grid)

    h, w = topo.shape
    lons = np.linspace(-180.0, 180.0, w, dtype=np.float64)
    lats = np.linspace(-90.0, 90.0, h, dtype=np.float64)
    mask = np.full((h, w), SURFACE_UNKNOWN, dtype=np.uint8)
    rows_per_chunk = max(16, min(int(chunk_rows), 256))
    total = (h + rows_per_chunk - 1) // rows_per_chunk
    startup_progress_begin(f"建立海陸分類遮罩 {h}x{w}", total)
    with tqdm(total=total, desc="Surface mask", unit="chunk") as progress:
        for row0 in range(0, h, rows_per_chunk):
            row1 = min(h, row0 + rows_per_chunk)
            lon_grid, lat_grid = np.meshgrid(lons, lats[row0:row1])
            chunk = np.full((row1 - row0, w), SURFACE_UNKNOWN, dtype=np.uint8)
            inside_ocean = contains_xy_safe(ocean, lon_grid, lat_grid)
            inside_land = contains_xy_safe(land, lon_grid, lat_grid)
            inside_lake = contains_xy_safe(inland_water, lon_grid, lat_grid)

            chunk[inside_ocean] = SURFACE_OCEAN
            chunk[inside_land] = SURFACE_LAND
            chunk[inside_lake] = SURFACE_INLAND_WATER

            unknown = chunk == SURFACE_UNKNOWN
            if np.any(unknown):
                fallback_land = np.asarray(topo[row0:row1, :]) >= float(sea_level_m)
                chunk[unknown & fallback_land] = SURFACE_LAND
                chunk[unknown & ~fallback_land] = SURFACE_OCEAN

            mask[row0:row1, :] = chunk
            progress.update(1)
            startup_progress_update(1, f"建立海陸分類遮罩：{row1:,}/{h:,} rows")

    np.save(cache_path, mask)
    print(f"Saved surface mask: {cache_path}")
    startup_progress_done("海陸分類遮罩快取完成")
    return np.ascontiguousarray(mask)


def ice_mask_cache_path(source: str, topo_shape: tuple[int, int]) -> Path:
    h, w = topo_shape
    return CACHE_DIR / f"ice_mask_v1_{source}_{h}x{w}.npy"


def load_ice_mask(topo: np.ndarray, source: str, chunk_rows: int) -> np.ndarray:
    source = (source or "naturalearth").strip().lower()
    if source in {"none", "off"}:
        return np.zeros(topo.shape, dtype=np.uint8)

    if source not in {"naturalearth", "ne", "ne110", "ne50", "ne10", "naturalearth110", "naturalearth50", "naturalearth10", "110m", "50m", "10m"}:
        print(f"Unknown ice mask source={source}; disabling ice layer")
        return np.zeros(topo.shape, dtype=np.uint8)

    cache_path = ice_mask_cache_path(source, topo.shape)
    if cache_path.exists():
        print(f"Using cached ice mask: {cache_path}")
        startup_progress_message(f"讀取冰雪遮罩快取：{cache_path.name}")
        return np.ascontiguousarray(np.load(cache_path).astype(np.uint8, copy=False))

    try:
        import shapely
        from shapely.geometry import shape
        from shapely.ops import unary_union
    except Exception as exc:
        print(f"Natural Earth ice mask requires shapely; disabling ice layer: {exc}")
        return np.zeros(topo.shape, dtype=np.uint8)

    def load_union(layer: str):
        geojson_path = natural_earth_geojson_path(source, layer)
        if not geojson_path.exists():
            download_natural_earth_geojson(geojson_path, source, layer)
        obj = json.loads(geojson_path.read_text(encoding="utf-8"))
        polygons = [shape(feature["geometry"]) for feature in obj.get("features", []) if feature.get("geometry")]
        if not polygons:
            return None
        geom = unary_union(polygons)
        try:
            shapely.prepare(geom)
        except Exception:
            pass
        return geom

    geometries = []
    for layer in ("glaciated_areas", "antarctic_ice_shelves_polys"):
        try:
            geom = load_union(layer)
            if geom is not None:
                geometries.append(geom)
        except Exception as exc:
            print(f"Natural Earth ice layer {layer} unavailable; skipping: {exc}")

    if not geometries:
        print("No Natural Earth ice polygons available; disabling ice layer")
        return np.zeros(topo.shape, dtype=np.uint8)

    ice_geom = unary_union(geometries)
    try:
        shapely.prepare(ice_geom)
    except Exception:
        pass

    def contains_xy_safe(geom, lon_grid, lat_grid):
        try:
            return shapely.contains_xy(geom, lon_grid, lat_grid)
        except AttributeError:
            from shapely.vectorized import contains

            return contains(geom, lon_grid, lat_grid)

    h, w = topo.shape
    lons = np.linspace(-180.0, 180.0, w, dtype=np.float64)
    lats = np.linspace(-90.0, 90.0, h, dtype=np.float64)
    mask = np.zeros((h, w), dtype=np.uint8)
    rows_per_chunk = max(16, min(int(chunk_rows), 256))
    total = (h + rows_per_chunk - 1) // rows_per_chunk
    startup_progress_begin(f"建立冰雪遮罩 {h}x{w}", total)
    with tqdm(total=total, desc="Ice mask", unit="chunk") as progress:
        for row0 in range(0, h, rows_per_chunk):
            row1 = min(h, row0 + rows_per_chunk)
            lon_grid, lat_grid = np.meshgrid(lons, lats[row0:row1])
            mask[row0:row1, :] = contains_xy_safe(ice_geom, lon_grid, lat_grid).astype(np.uint8)
            progress.update(1)
            startup_progress_update(1, f"建立冰雪遮罩：{row1:,}/{h:,} rows")

    np.save(cache_path, mask)
    print(f"Saved ice mask: {cache_path}")
    startup_progress_done("冰雪遮罩快取完成")
    return np.ascontiguousarray(mask)


def forest_density_cache_path(source: str, topo_shape: tuple[int, int]) -> Path:
    h, w = topo_shape
    return CACHE_DIR / f"forest_density_v1_{source}_{h}x{w}.npy"


def load_forest_density(
    topo: np.ndarray,
    surface_mask: np.ndarray,
    source: str,
    density_file: str | None,
    chunk_rows: int,
) -> np.ndarray:
    source = (source or "heuristic").strip().lower()
    if source in {"none", "off"}:
        return np.zeros(topo.shape, dtype=np.uint8)

    if density_file:
        path = Path(density_file)
        try:
            data = np.load(path)
            data = np.asarray(data)
            if data.shape != topo.shape:
                print(f"Forest density file shape {data.shape} does not match topography {topo.shape}; using heuristic")
            else:
                if data.dtype != np.uint8:
                    finite = np.nan_to_num(data.astype(np.float32), nan=0.0)
                    if float(np.nanmax(finite)) <= 1.0:
                        finite = finite * 255.0
                    data = np.clip(finite, 0.0, 255.0).astype(np.uint8)
                print(f"Using forest density file: {path}")
                return np.ascontiguousarray(data)
        except Exception as exc:
            print(f"Forest density file unavailable; using heuristic: {exc}")

    cache_path = forest_density_cache_path(source, topo.shape)
    if cache_path.exists():
        print(f"Using cached forest density: {cache_path}")
        startup_progress_message(f"讀取森林密度快取：{cache_path.name}")
        return np.ascontiguousarray(np.load(cache_path).astype(np.uint8, copy=False))

    if source not in {"heuristic", "auto", "estimated"}:
        print(f"Unknown forest source={source}; using heuristic")

    h, w = topo.shape
    lons = np.linspace(-180.0, 180.0, w, dtype=np.float32)
    lon_rad = np.radians(lons)[None, :]
    rows_per_chunk = max(16, min(int(chunk_rows), 256))
    total = (h + rows_per_chunk - 1) // rows_per_chunk
    density = np.zeros((h, w), dtype=np.uint8)
    startup_progress_begin(f"建立森林密度快取 {h}x{w}", total)
    with tqdm(total=total, desc="Forest density", unit="chunk") as progress:
        for row0 in range(0, h, rows_per_chunk):
            row1 = min(h, row0 + rows_per_chunk)
            lats = np.linspace(-90.0, 90.0, h, dtype=np.float32)[row0:row1][:, None]
            abs_lat = np.abs(lats)
            elev = np.asarray(topo[row0:row1, :], dtype=np.float32)
            land = np.asarray(surface_mask[row0:row1, :]) == SURFACE_LAND

            tropical = np.exp(-((abs_lat - 4.0) / 28.0) ** 2)
            temperate = 0.72 * np.exp(-((abs_lat - 43.0) / 17.0) ** 2)
            boreal = 0.82 * np.exp(-((abs_lat - 58.0) / 9.0) ** 2)
            lat_potential = np.maximum.reduce([tropical, temperate, boreal])
            moisture_texture = 0.62 + 0.26 * np.sin(lon_rad * 2.1 + np.radians(lats) * 1.7)
            moisture_texture += 0.12 * np.sin(lon_rad * 5.3 - np.radians(lats) * 2.6)
            moisture_texture = np.clip(moisture_texture, 0.08, 1.0)
            elevation_factor = np.clip((4200.0 - np.maximum(elev, 0.0)) / 4200.0, 0.0, 1.0)
            cold_limit = np.clip((74.0 - abs_lat) / 12.0, 0.0, 1.0)
            dry_belt = 1.0 - 0.42 * np.exp(-((abs_lat - 25.0) / 8.5) ** 2)
            raw = lat_potential * moisture_texture * elevation_factor * cold_limit * dry_belt
            raw = np.where(land, raw, 0.0)
            density[row0:row1, :] = np.clip(raw * 255.0, 0.0, 255.0).astype(np.uint8)
            progress.update(1)
            startup_progress_update(1, f"建立森林密度快取：{row1:,}/{h:,} rows")

    np.save(cache_path, density)
    print(f"Saved forest density: {cache_path}")
    startup_progress_done("森林密度快取完成")
    return np.ascontiguousarray(density)


class DownloadProgressBar(tqdm):
    def update_to(self, blocks: int = 1, block_size: int = 1, total_size: int | None = None) -> None:
        if total_size is not None:
            self.total = total_size
            startup_progress_set(
                min(blocks * block_size, total_size),
                total_size,
                f"下載星空快取：{min(blocks * block_size, total_size) / max(total_size, 1):.0%}",
            )
        self.update(blocks * block_size - self.n)


def load_stars(mag_limit: float, enabled: bool) -> np.ndarray:
    if not enabled:
        return np.zeros((0, 4), dtype=np.float32)

    cache_path = star_cache_path()
    if cache_path.exists():
        print(f"Using cached stars: {cache_path}")
        startup_progress_message(f"讀取星空快取：{cache_path.name}")
        stars = np.load(cache_path)
    else:
        project_cache = SCRIPT_DIR / "stars_cache.npy"
        if project_cache.exists():
            print(f"Importing project star cache: {project_cache}")
            stars = np.load(project_cache)
        else:
            print("Downloading HYG star catalog v3.8")
            temp_file = CACHE_DIR / "temp_stars_cache.csv.gz"
            startup_progress_begin("下載 HYG 星空目錄", None)
            with DownloadProgressBar(
                unit="B", unit_scale=True, miniters=1, desc="Stars"
            ) as progress:
                urllib.request.urlretrieve(
                    HYG_V38_URL, filename=temp_file, reporthook=progress.update_to
                )

            startup_progress_message("解析星空目錄快取")
            df = pd.read_csv(temp_file, compression="gzip", usecols=["ra", "dec", "mag"])
            temp_file.unlink(missing_ok=True)
            df = df[df["mag"] < 6.5].dropna()
            ra_rad = (df["ra"].to_numpy(dtype=np.float32) / 24.0) * (2.0 * np.pi)
            dec_rad = (df["dec"].to_numpy(dtype=np.float32) / 180.0) * np.pi
            mag = df["mag"].to_numpy(dtype=np.float32)

            x = np.cos(dec_rad) * np.sin(ra_rad)
            y = np.sin(dec_rad)
            z = np.cos(dec_rad) * np.cos(ra_rad)
            stars = np.column_stack((x, y, z, mag)).astype(np.float32)

        np.save(cache_path, stars)
        startup_progress_done("星空快取完成")

    stars = np.asarray(stars, dtype=np.float32)
    if mag_limit < 6.5:
        stars = stars[stars[:, 3] < mag_limit]
    print(f"Loaded stars: {len(stars):,}, mag_limit={mag_limit}")
    return np.ascontiguousarray(stars)


DATA_FETCH_MAX_EVENTS = 80
DATA_FETCH_EVENTS: list[dict] = []


def record_data_fetch_event(
    kind: str,
    layer: str,
    stage: str,
    source: str = "",
    cache_path: str = "",
    message: str = "",
    bytes_read: int | None = None,
) -> None:
    event = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "kind": str(kind),
        "layer": str(layer),
        "stage": str(stage),
        "source": str(source or ""),
        "cache_path": str(cache_path or ""),
        "message": str(message or ""),
        "bytes_read": int(bytes_read) if bytes_read is not None else None,
    }
    DATA_FETCH_EVENTS.append(event)
    if len(DATA_FETCH_EVENTS) > DATA_FETCH_MAX_EVENTS:
        del DATA_FETCH_EVENTS[: len(DATA_FETCH_EVENTS) - DATA_FETCH_MAX_EVENTS]


def data_fetch_events_snapshot() -> list[dict]:
    return [dict(event) for event in DATA_FETCH_EVENTS]


def data_fetch_progress_snapshot() -> dict:
    if not DATA_FETCH_EVENTS:
        return {
            "active": False,
            "percent": 0,
            "label": "資料快取尚未開始",
            "stage": "idle",
            "kind": "",
            "layer": "",
            "events": 0,
        }
    latest = DATA_FETCH_EVENTS[-1]
    stage = str(latest.get("stage", ""))
    active = stage in {"begin", "download-needed", "file-read", "read"}
    if stage in {"done", "cache-write", "normalized"}:
        percent = 100
    elif stage in {"cache-hit", "memory-cache-hit"}:
        percent = 100
    elif stage in {"failed", "missing"}:
        percent = 0
    elif active:
        percent = 35
    else:
        percent = 10
    layer = str(latest.get("layer", ""))
    kind = str(latest.get("kind", ""))
    message = str(latest.get("message", ""))
    label = f"{kind}:{layer} | {stage}"
    if message:
        label += f" | {message}"
    return {
        "active": bool(active),
        "percent": int(max(0, min(percent, 100))),
        "label": label,
        "stage": stage,
        "kind": kind,
        "layer": layer,
        "events": len(DATA_FETCH_EVENTS),
    }


def data_fetch_status_text() -> str:
    lines = [
        "Data fetch / cache status",
        "",
        "Purpose: expose recent provider downloads, cache hits, and file reads for the future Qt progress panel.",
    ]
    progress = data_fetch_progress_snapshot()
    lines.extend(
        [
            f"- latest: {progress['label']}",
            f"- progress: {progress['percent']}%",
            f"- active: {progress['active']}",
            f"- events retained: {progress['events']}",
            "",
            "Recent events:",
        ]
    )
    if not DATA_FETCH_EVENTS:
        lines.append("- no data fetch events recorded yet")
        return "\n".join(lines)
    for event in DATA_FETCH_EVENTS[-30:]:
        size = ""
        if event.get("bytes_read") is not None:
            size = f" | {int(event['bytes_read']):,} bytes"
        lines.append(
            f"- {event['time']} | {event['kind']}:{event['layer']} | {event['stage']} | "
            f"{event.get('message', '')}{size}"
        )
        source = event.get("source") or ""
        cache_path = event.get("cache_path") or ""
        if source:
            lines.append(f"  source: {source}")
        if cache_path:
            lines.append(f"  cache: {cache_path}")
    return "\n".join(lines)


def read_url_text(url: str, timeout: float, progress_label: str | None = None) -> str:
    headers = {"User-Agent": "taichi-datashader-ais/1.0"}
    token = os.environ.get("AIS_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    if progress_label:
        record_data_fetch_event("url", progress_label, "begin", source=url, message="request started")
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            raw_size = len(raw)
            encoding = response.headers.get_content_charset() or "utf-8"
            if url.lower().endswith(".gz"):
                raw = gzip.decompress(raw)
            if progress_label:
                record_data_fetch_event("url", progress_label, "done", source=url, message="request completed", bytes_read=raw_size)
            return raw.decode(encoding, errors="replace")
    except Exception as exc:
        if progress_label:
            record_data_fetch_event("url", progress_label, "failed", source=url, message=str(exc))
        raise


def read_file_text(path: Path) -> str:
    raw = path.read_bytes()
    if path.suffix.lower() == ".gz":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", errors="replace")


def dataframe_from_geojson(obj: dict) -> pd.DataFrame:
    rows = []
    for feature in obj.get("features", []):
        props = dict(feature.get("properties") or {})
        geometry = feature.get("geometry") or {}
        coords = geometry.get("coordinates")
        if geometry.get("type") == "Point" and isinstance(coords, (list, tuple)) and len(coords) >= 2:
            props["lon"] = coords[0]
            props["lat"] = coords[1]
        rows.append(props)
    return pd.DataFrame(rows)


def dataframe_from_json(text: str) -> pd.DataFrame:
    obj = json.loads(text)
    if isinstance(obj, dict) and obj.get("type") == "FeatureCollection":
        return dataframe_from_geojson(obj)
    if isinstance(obj, dict):
        if isinstance(obj.get("states"), list):
            columns = [
                "icao24",
                "callsign",
                "origin_country",
                "time_position",
                "last_contact",
                "lon",
                "lat",
                "baro_altitude",
                "on_ground",
                "velocity",
                "true_track",
                "vertical_rate",
                "sensors",
                "geo_altitude",
                "squawk",
                "spi",
                "position_source",
            ]
            return pd.DataFrame(obj["states"], columns=columns[: len(obj["states"][0])] if obj["states"] else columns)
        for key in ("data", "ships", "vessels", "aircraft", "planes", "positions", "rows", "results"):
            value = obj.get(key)
            if isinstance(value, list):
                return pd.json_normalize(value)
        return pd.json_normalize(obj)
    if isinstance(obj, list):
        return pd.json_normalize(obj)
    return pd.DataFrame()


def dataframe_from_jsonl(text: str) -> pd.DataFrame:
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return pd.json_normalize(rows) if rows else pd.DataFrame()


def dataframe_from_nmea(text: str) -> pd.DataFrame:
    try:
        from pyais import decode
    except Exception:
        return pd.DataFrame()

    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith(("!AI", "$AI")):
            continue
        try:
            row = decode(line).asdict()
        except Exception:
            continue
        if "lat" in row and "lon" in row:
            rows.append(row)
    return pd.DataFrame(rows)


def dataframe_from_text(text: str, source_name: str) -> pd.DataFrame:
    suffix = Path(source_name.split("?", 1)[0]).suffix.lower()
    stripped = text.lstrip()

    if suffix in {".json", ".geojson"} or stripped.startswith(("{", "[")):
        try:
            return dataframe_from_json(text)
        except Exception:
            pass

    if suffix in {".jsonl", ".ndjson"}:
        try:
            return dataframe_from_jsonl(text)
        except Exception:
            pass

    if stripped.startswith(("!AI", "$AI")):
        frame = dataframe_from_nmea(text)
        if not frame.empty:
            return frame

    try:
        return pd.read_csv(io.StringIO(text))
    except Exception:
        frame = dataframe_from_nmea(text)
        if not frame.empty:
            return frame
        raise


def normalize_ais_frame(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["lon", "lat", "mmsi", "sog", "cog", "heading", "timestamp"])

    lat_col = find_column(frame, LAT_ALIASES)
    lon_col = find_column(frame, LON_ALIASES)
    if lat_col is None or lon_col is None:
        raise ValueError(
            "AIS data must contain latitude/longitude columns. "
            f"Found columns: {', '.join(map(str, frame.columns[:20]))}"
        )

    out = pd.DataFrame(
        {
            "lat": pd.to_numeric(frame[lat_col], errors="coerce"),
            "lon": pd.to_numeric(frame[lon_col], errors="coerce"),
        }
    )
    for target, aliases in COLUMN_ALIASES.items():
        col = find_column(frame, aliases)
        if col is not None:
            out[target] = frame[col]

    for numeric_col in ("sog", "cog", "heading"):
        if numeric_col in out.columns:
            out[numeric_col] = pd.to_numeric(out[numeric_col], errors="coerce")

    out = out.dropna(subset=["lat", "lon"]).copy()
    out["lon"] = ((out["lon"] + 180.0) % 360.0) - 180.0
    out = out[out["lat"].between(-90.0, 90.0) & out["lon"].between(-180.0, 180.0)]
    return out.reset_index(drop=True)


def filter_recent(frame: pd.DataFrame, max_age_minutes: float) -> pd.DataFrame:
    if max_age_minutes <= 0 or "timestamp" not in frame.columns or frame.empty:
        return frame

    timestamps = pd.to_datetime(frame["timestamp"], errors="coerce", utc=True)
    if timestamps.notna().sum() == 0:
        return frame

    cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(minutes=max_age_minutes)
    return frame[timestamps >= cutoff].reset_index(drop=True)


def normalize_aircraft_frame(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["lon", "lat", "icao24", "callsign", "altitude_m", "speed_kt", "heading", "timestamp"])

    lat_col = find_column(frame, LAT_ALIASES)
    lon_col = find_column(frame, LON_ALIASES)
    if lat_col is None or lon_col is None:
        raise ValueError(
            "ADS-B data must contain latitude/longitude columns. "
            f"Found columns: {', '.join(map(str, frame.columns[:20]))}"
        )
    out = pd.DataFrame(
        {
            "lat": pd.to_numeric(frame[lat_col], errors="coerce"),
            "lon": pd.to_numeric(frame[lon_col], errors="coerce"),
        }
    )
    for target, aliases in AIRCRAFT_COLUMN_ALIASES.items():
        col = find_column(frame, aliases)
        if col is not None:
            out[target] = frame[col]
    for numeric_col in ("altitude_m", "altitude_ft", "speed_kt", "speed_ms", "heading"):
        if numeric_col in out.columns:
            out[numeric_col] = pd.to_numeric(out[numeric_col], errors="coerce")
    if "altitude_m" not in out.columns and "altitude_ft" in out.columns:
        out["altitude_m"] = out["altitude_ft"] * 0.3048
    if "speed_kt" not in out.columns and "speed_ms" in out.columns:
        out["speed_kt"] = out["speed_ms"] * 1.943844
    if "altitude_m" not in out.columns:
        out["altitude_m"] = 0.0
    if "speed_kt" not in out.columns:
        out["speed_kt"] = np.nan
    out = out.dropna(subset=["lat", "lon"]).copy()
    out["lon"] = ((out["lon"] + 180.0) % 360.0) - 180.0
    out = out[out["lat"].between(-90.0, 90.0) & out["lon"].between(-180.0, 180.0)]
    return out.reset_index(drop=True)


class AISSource:
    def __init__(
        self,
        ais_url: str | None,
        ais_file: str | None,
        timeout: float,
        ais_db_url: str | None = None,
        ais_db_query: str | None = None,
        ais_db_table: str = DEFAULT_AIS_DB_TABLE,
        ais_db_limit: int = DEFAULT_AIS_DB_LIMIT,
    ):
        self.ais_url = ais_url
        self.ais_file = Path(ais_file) if ais_file else None
        self.ais_db_url = ais_db_url
        self.ais_db_query = ais_db_query
        self.ais_db_table = ais_db_table
        self.ais_db_limit = ais_db_limit
        self._db_engine = None
        self.timeout = timeout
        self.demo = not ais_url and not ais_file and not ais_db_url
        self.demo_start = time.time()
        self.demo_count = parse_int_env("AIS_DEMO_COUNT", 12000)
        rng = np.random.default_rng(7)
        self.demo_base = self._build_demo_shipping_lanes(rng)

    def _build_demo_shipping_lanes(self, rng: np.random.Generator) -> pd.DataFrame:
        def lonlat_to_xyz(lat_deg: np.ndarray, lon_deg: np.ndarray) -> np.ndarray:
            lat_rad = np.radians(lat_deg)
            lon_rad = np.radians(lon_deg)
            cos_lat = np.cos(lat_rad)
            return np.column_stack(
                (
                    cos_lat * np.sin(lon_rad),
                    np.sin(lat_rad),
                    cos_lat * np.cos(lon_rad),
                )
            )

        routes = np.array(
            [
                (35.0, 139.0, 34.0, -122.0, 1.2),
                (31.0, 121.0, 1.3, 104.0, 1.0),
                (1.3, 104.0, 7.0, 80.0, 0.9),
                (7.0, 80.0, 13.0, 43.0, 0.9),
                (13.0, 43.0, 31.0, 32.0, 0.8),
                (31.0, 32.0, 36.0, 14.0, 0.8),
                (36.0, 14.0, 51.0, 1.0, 0.8),
                (40.0, -74.0, 50.0, -5.0, 1.0),
                (25.0, -80.0, 9.0, -79.0, 0.7),
                (-23.0, -43.0, -34.0, 18.0, 0.7),
                (1.3, 104.0, -33.0, 151.0, 0.8),
                (35.0, -6.0, 36.0, 14.0, 0.7),
            ],
            dtype=np.float32,
        )
        weights = routes[:, 4] / routes[:, 4].sum()
        route_idx = rng.choice(len(routes), size=self.demo_count, p=weights)
        route = routes[route_idx]
        progress = rng.random(self.demo_count, dtype=np.float32)
        direction = rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=self.demo_count)

        lat0 = route[:, 0]
        lon0 = route[:, 1]
        lat1 = route[:, 2]
        lon1 = route[:, 3]

        p0 = lonlat_to_xyz(lat0, lon0)
        p1 = lonlat_to_xyz(lat1, lon1)
        dot = np.clip(np.sum(p0 * p1, axis=1), -0.999999, 0.999999)
        omega = np.arccos(dot)
        sin_omega = np.sin(omega)
        a = np.sin((1.0 - progress) * omega) / sin_omega
        b = np.sin(progress * omega) / sin_omega
        pos = p0 * a[:, None] + p1 * b[:, None]
        pos /= np.linalg.norm(pos, axis=1)[:, None]

        lat = np.degrees(np.arcsin(pos[:, 1])) + rng.normal(0.0, 0.45, self.demo_count)
        lon = np.degrees(np.arctan2(pos[:, 0], pos[:, 2])) + rng.normal(0.0, 0.7, self.demo_count)
        lon = ((lon + 180.0) % 360.0) - 180.0

        normal = np.cross(p0, p1)
        normal /= np.linalg.norm(normal, axis=1)[:, None]
        tangent = np.cross(normal, pos)
        tangent *= direction[:, None]
        lon_rad = np.radians(lon)
        lat_rad = np.radians(lat)
        east = np.column_stack((np.cos(lon_rad), np.zeros_like(lon_rad), -np.sin(lon_rad)))
        north = np.column_stack(
            (
                -np.sin(lat_rad) * np.sin(lon_rad),
                np.cos(lat_rad),
                -np.sin(lat_rad) * np.cos(lon_rad),
            )
        )
        east_component = np.sum(tangent * east, axis=1)
        north_component = np.sum(tangent * north, axis=1)
        cog = (np.degrees(np.arctan2(east_component, north_component)) + 360.0) % 360.0

        return pd.DataFrame(
            {
                "mmsi": np.arange(100000000, 100000000 + self.demo_count, dtype=np.int64),
                "lat0": np.clip(lat, -82.0, 82.0).astype(np.float32),
                "lon0": lon.astype(np.float32),
                "phase": rng.uniform(0.0, 2.0 * np.pi, self.demo_count).astype(np.float32),
                "sog": rng.gamma(3.0, 3.0, self.demo_count).clip(1.0, 28.0).astype(np.float32),
                "cog": cog.astype(np.float32),
            }
        )

    def read(self) -> pd.DataFrame:
        if self.demo:
            return self._demo_frame()
        if self.ais_db_url:
            return self._read_database()
        if self.ais_url:
            text = read_url_text(self.ais_url, self.timeout)
            return normalize_ais_frame(dataframe_from_text(text, self.ais_url))
        if self.ais_file:
            text = read_file_text(self.ais_file)
            return normalize_ais_frame(dataframe_from_text(text, str(self.ais_file)))
        return pd.DataFrame(columns=["lon", "lat"])

    def _read_database(self) -> pd.DataFrame:
        try:
            from sqlalchemy import create_engine, text
        except Exception as exc:
            raise RuntimeError(
                "SQLAlchemy is required for AIS database mode. "
                "Install with: py -3.13 -m pip install sqlalchemy psycopg[binary] pymysql"
            ) from exc

        if self._db_engine is None:
            self._db_engine = create_engine(self.ais_db_url, pool_pre_ping=True)

        query = self.ais_db_query
        if not query:
            limit = max(1, int(self.ais_db_limit))
            query = f"SELECT * FROM {self.ais_db_table} ORDER BY timestamp DESC LIMIT {limit}"

        with self._db_engine.connect() as conn:
            frame = pd.read_sql_query(text(query), conn)
        return normalize_ais_frame(frame)

    def _demo_frame(self) -> pd.DataFrame:
        elapsed = time.time() - self.demo_start
        base = self.demo_base
        cog = base["cog"].to_numpy(dtype=np.float32)
        sog = base["sog"].to_numpy(dtype=np.float32)
        lon = base["lon0"].to_numpy(dtype=np.float32) + elapsed * (sog / 900.0) * np.cos(
            np.radians(cog)
        )
        lat = base["lat0"].to_numpy(dtype=np.float32) + 4.0 * np.sin(
            base["phase"].to_numpy(dtype=np.float32) + elapsed / 180.0
        )
        lon = ((lon + 180.0) % 360.0) - 180.0
        lat = np.clip(lat, -80.0, 80.0)

        return pd.DataFrame(
            {
                "mmsi": base["mmsi"],
                "lat": lat,
                "lon": lon,
                "sog": sog,
                "cog": cog,
                "timestamp": pd.Timestamp.now(tz="UTC"),
            }
        )


class AircraftSource:
    def __init__(
        self,
        aircraft_url: str | None,
        aircraft_file: str | None,
        timeout: float,
        aircraft_db_url: str | None = None,
        aircraft_db_query: str | None = None,
        aircraft_db_table: str = DEFAULT_AIRCRAFT_DB_TABLE,
        aircraft_db_limit: int = DEFAULT_AIRCRAFT_DB_LIMIT,
    ):
        self.aircraft_url = aircraft_url
        self.aircraft_file = Path(aircraft_file) if aircraft_file else None
        self.aircraft_db_url = aircraft_db_url
        self.aircraft_db_query = aircraft_db_query
        self.aircraft_db_table = aircraft_db_table
        self.aircraft_db_limit = aircraft_db_limit
        self.timeout = timeout
        self._db_engine = None
        self.demo = not aircraft_url and not aircraft_file and not aircraft_db_url
        self.demo_start = time.time()
        self.demo_count = parse_int_env("AIRCRAFT_DEMO_COUNT", 6000)
        rng = np.random.default_rng(13)
        self.demo_base = self._build_demo_flights(rng)

    def _build_demo_flights(self, rng: np.random.Generator) -> pd.DataFrame:
        hubs = np.array(
            [
                (35.55, 139.78, 40.64, -73.78),
                (25.08, 121.23, 34.05, -118.24),
                (51.47, -0.45, 40.64, -73.78),
                (1.36, 103.99, 22.31, 113.92),
                (48.35, 11.78, 25.25, 55.36),
                (-33.94, 151.17, 1.36, 103.99),
                (37.46, 126.44, 33.94, -118.40),
                (31.14, 121.81, 55.97, 37.41),
            ],
            dtype=np.float32,
        )
        idx = rng.integers(0, len(hubs), self.demo_count)
        route = hubs[idx]
        progress = rng.random(self.demo_count, dtype=np.float32)
        lat = route[:, 0] * (1.0 - progress) + route[:, 2] * progress + rng.normal(0.0, 0.8, self.demo_count)
        lon = route[:, 1] * (1.0 - progress) + route[:, 3] * progress + rng.normal(0.0, 1.2, self.demo_count)
        lon = ((lon + 180.0) % 360.0) - 180.0
        heading = (np.degrees(np.arctan2(route[:, 3] - route[:, 1], route[:, 2] - route[:, 0])) + 360.0) % 360.0
        return pd.DataFrame(
            {
                "icao24": [f"demo{i:06x}" for i in range(self.demo_count)],
                "callsign": [f"AI{i % 9000:04d}" for i in range(self.demo_count)],
                "lat0": np.clip(lat, -82.0, 82.0).astype(np.float32),
                "lon0": lon.astype(np.float32),
                "phase": rng.uniform(0.0, 2.0 * np.pi, self.demo_count).astype(np.float32),
                "altitude_m": rng.normal(9800.0, 1800.0, self.demo_count).clip(300.0, 13000.0).astype(np.float32),
                "speed_kt": rng.normal(430.0, 80.0, self.demo_count).clip(80.0, 620.0).astype(np.float32),
                "heading": heading.astype(np.float32),
            }
        )

    def read(self) -> pd.DataFrame:
        if self.demo:
            return self._demo_frame()
        if self.aircraft_db_url:
            return self._read_database()
        if self.aircraft_url:
            text = read_url_text(self.aircraft_url, self.timeout)
            return normalize_aircraft_frame(dataframe_from_text(text, self.aircraft_url))
        if self.aircraft_file:
            text = read_file_text(self.aircraft_file)
            return normalize_aircraft_frame(dataframe_from_text(text, str(self.aircraft_file)))
        return pd.DataFrame(columns=["lon", "lat"])

    def _read_database(self) -> pd.DataFrame:
        try:
            from sqlalchemy import create_engine, text
        except Exception as exc:
            raise RuntimeError(
                "SQLAlchemy is required for ADS-B database mode. "
                "Install with: py -3.13 -m pip install sqlalchemy psycopg[binary] pymysql"
            ) from exc
        if self._db_engine is None:
            self._db_engine = create_engine(self.aircraft_db_url, pool_pre_ping=True)
        query = self.aircraft_db_query
        if not query:
            limit = max(1, int(self.aircraft_db_limit))
            query = f"SELECT * FROM {self.aircraft_db_table} ORDER BY timestamp DESC LIMIT {limit}"
        with self._db_engine.connect() as conn:
            frame = pd.read_sql_query(text(query), conn)
        return normalize_aircraft_frame(frame)

    def _demo_frame(self) -> pd.DataFrame:
        elapsed = time.time() - self.demo_start
        base = self.demo_base
        heading = base["heading"].to_numpy(dtype=np.float32)
        speed = base["speed_kt"].to_numpy(dtype=np.float32)
        lon = base["lon0"].to_numpy(dtype=np.float32) + elapsed * (speed / 24000.0) * np.sin(np.radians(heading))
        lat = base["lat0"].to_numpy(dtype=np.float32) + elapsed * (speed / 24000.0) * np.cos(np.radians(heading))
        lat += 0.4 * np.sin(base["phase"].to_numpy(dtype=np.float32) + elapsed / 120.0)
        lon = ((lon + 180.0) % 360.0) - 180.0
        lat = np.clip(lat, -82.0, 82.0)
        return pd.DataFrame(
            {
                "icao24": base["icao24"],
                "callsign": base["callsign"],
                "lat": lat,
                "lon": lon,
                "altitude_m": base["altitude_m"],
                "speed_kt": speed,
                "heading": heading,
                "timestamp": pd.Timestamp.now(tz="UTC"),
            }
        )


@ti.func
def rotate_view_to_world(v, yaw, pitch):
    cp = ti.cos(pitch)
    sp = ti.sin(pitch)
    y1 = cp * v.y - sp * v.z
    z1 = sp * v.y + cp * v.z
    x1 = v.x

    cy = ti.cos(yaw)
    sy = ti.sin(yaw)
    x2 = cy * x1 + sy * z1
    y2 = y1
    z2 = -sy * x1 + cy * z1
    return ti.Vector([x2, y2, z2])


@ti.data_oriented
class TaichiGlobeRenderer:
    def __init__(
        self,
        topo: np.ndarray,
        land_mask: np.ndarray,
        ice_mask: np.ndarray,
        forest_density: np.ndarray,
        colormap: np.ndarray,
        stars: np.ndarray,
        width: int,
        height: int,
        bump_scale: float,
        show_grid: bool,
        sea_level_m: float,
    ):
        self.width = int(width)
        self.height = int(height)
        self.topo_h = int(topo.shape[0])
        self.topo_w = int(topo.shape[1])
        self.num_stars = int(stars.shape[0])
        self.bump_scale = float(bump_scale)
        self.show_grid = bool(show_grid)
        self.sea_level_m = float(sea_level_m)

        self.topo = ti.field(dtype=ti.i16, shape=topo.shape)
        self.land_mask = ti.field(dtype=ti.u8, shape=topo.shape)
        self.ice_mask = ti.field(dtype=ti.u8, shape=topo.shape)
        self.forest_density = ti.field(dtype=ti.u8, shape=topo.shape)
        self.image = ti.Vector.field(3, dtype=ti.f32, shape=(self.width, self.height))
        self.globe_mask = ti.field(dtype=ti.u8, shape=(self.width, self.height))
        self.colormap = ti.Vector.field(3, dtype=ti.f32, shape=256)
        self.stars = ti.Vector.field(4, dtype=ti.f32, shape=max(self.num_stars, 1))
        self.topo.from_numpy(np.ascontiguousarray(topo))
        self.land_mask.from_numpy(np.ascontiguousarray(land_mask.astype(np.uint8, copy=False)))
        self.ice_mask.from_numpy(np.ascontiguousarray(ice_mask.astype(np.uint8, copy=False)))
        self.forest_density.from_numpy(np.ascontiguousarray(forest_density.astype(np.uint8, copy=False)))
        self.colormap.from_numpy(np.ascontiguousarray(colormap.astype(np.float32)))
        if self.num_stars:
            self.stars.from_numpy(np.ascontiguousarray(stars.astype(np.float32, copy=False)))

    @ti.func
    def terrain_color(self, z_val, land_mix: ti.f32, sea_level_m: ti.f32):
        ocean_norm = (z_val - MIN_ELEV) / (sea_level_m - MIN_ELEV + 1e-6) * 0.5
        land_base = ti.max(0.0, (z_val + 300.0) / (MAX_ELEV + 300.0))
        land_base = ti.pow(ti.min(1.0, land_base), 0.55)
        land_norm = 0.5 + land_base * 0.5

        ocean_norm = ti.max(0.0, ti.min(1.0, ocean_norm))
        ocean_c_idx = ocean_norm * 255.0
        ocean_idx0 = ti.cast(ti.floor(ocean_c_idx), ti.i32)
        ocean_idx1 = ti.min(255, ocean_idx0 + 1)
        ocean_frac = ocean_c_idx - ti.cast(ocean_idx0, ti.f32)
        ocean_color = self.colormap[ocean_idx0] * (1.0 - ocean_frac) + self.colormap[ocean_idx1] * ocean_frac

        land_norm = ti.max(0.0, ti.min(1.0, land_norm))
        land_c_idx = land_norm * 255.0
        land_idx0 = ti.cast(ti.floor(land_c_idx), ti.i32)
        land_idx1 = ti.min(255, land_idx0 + 1)
        land_frac = land_c_idx - ti.cast(land_idx0, ti.f32)
        land_color = self.colormap[land_idx0] * (1.0 - land_frac) + self.colormap[land_idx1] * land_frac

        mix = ti.max(0.0, ti.min(1.0, land_mix))
        return ocean_color * (1.0 - mix) + land_color * mix

    @ti.kernel
    def render(
        self,
        yaw: ti.f32,
        pitch: ti.f32,
        zoom: ti.f32,
        sun_x: ti.f32,
        sun_y: ti.f32,
        sun_z: ti.f32,
        flip_longitude: ti.i32,
        flip_latitude: ti.i32,
        sea_level_m: ti.f32,
        ice_enabled: ti.i32,
        ice_opacity: ti.f32,
        ice_specular: ti.f32,
        ice_blue: ti.f32,
        forest_enabled: ti.i32,
        forest_opacity: ti.f32,
        forest_green: ti.f32,
        canopy_shadow: ti.f32,
        ocean_enabled: ti.i32,
        ocean_wave_strength: ti.f32,
        ocean_roughness: ti.f32,
        ocean_foam: ti.f32,
        ocean_time: ti.f32,
    ):
        aspect = ti.cast(self.width, ti.f32) / ti.cast(self.height, ti.f32)
        light_dir = ti.Vector([sun_x, sun_y, sun_z])

        for i, j in self.image:
            u = (ti.cast(i, ti.f32) + 0.5) / ti.cast(self.width, ti.f32)
            v = (ti.cast(j, ti.f32) + 0.5) / ti.cast(self.height, ti.f32)
            sx = (u * 2.0 - 1.0) * zoom * aspect
            sy = (v * 2.0 - 1.0) * zoom
            r2 = sx * sx + sy * sy
            color = ti.Vector([0.004, 0.010, 0.024])
            self.globe_mask[i, j] = ti.cast(0, ti.u8)

            if r2 <= 1.0:
                self.globe_mask[i, j] = ti.cast(255, ti.u8)
                z = ti.sqrt(1.0 - r2)
                n_view = ti.Vector([sx, sy, z])
                n_world = rotate_view_to_world(n_view, yaw, pitch)
                lon = ti.atan2(n_world.x, n_world.z)
                lat = ti.asin(ti.max(-1.0, ti.min(1.0, n_world.y)))
                sample_lon = lon
                sample_lat = lat
                if flip_longitude:
                    sample_lon = -sample_lon
                if flip_latitude:
                    sample_lat = -sample_lat

                tx_f = (sample_lon * INV_TWO_PI + 0.5) * ti.cast(self.topo_w - 1, ti.f32)
                ty_f = (sample_lat * INV_PI + 0.5) * ti.cast(self.topo_h - 1, ti.f32)
                tx0 = ti.cast(ti.floor(tx_f), ti.i32)
                ty0 = ti.cast(ti.floor(ty_f), ti.i32)
                tx0 = ti.max(0, ti.min(self.topo_w - 1, tx0))
                ty0 = ti.max(0, ti.min(self.topo_h - 1, ty0))
                tx1 = ti.min(self.topo_w - 1, tx0 + 1)
                ty1 = ti.min(self.topo_h - 1, ty0 + 1)
                fx = ti.max(0.0, ti.min(1.0, tx_f - ti.cast(tx0, ti.f32)))
                fy = ti.max(0.0, ti.min(1.0, ty_f - ti.cast(ty0, ti.f32)))
                tx = tx0
                ty = ty0

                z00 = ti.cast(self.topo[ty0, tx0], ti.f32)
                z10 = ti.cast(self.topo[ty0, tx1], ti.f32)
                z01 = ti.cast(self.topo[ty1, tx0], ti.f32)
                z11 = ti.cast(self.topo[ty1, tx1], ti.f32)
                z0 = z00 * (1.0 - fx) + z10 * fx
                z1 = z01 * (1.0 - fx) + z11 * fx
                z_val = z0 * (1.0 - fy) + z1 * fy

                c00 = ti.cast(self.land_mask[ty0, tx0], ti.i32)
                c10 = ti.cast(self.land_mask[ty0, tx1], ti.i32)
                c01 = ti.cast(self.land_mask[ty1, tx0], ti.i32)
                c11 = ti.cast(self.land_mask[ty1, tx1], ti.i32)

                land00 = ti.cast(c00 == SURFACE_LAND, ti.f32)
                land10 = ti.cast(c10 == SURFACE_LAND, ti.f32)
                land01 = ti.cast(c01 == SURFACE_LAND, ti.f32)
                land11 = ti.cast(c11 == SURFACE_LAND, ti.f32)
                water00 = ti.cast(c00 == SURFACE_OCEAN, ti.f32) + ti.cast(c00 == SURFACE_INLAND_WATER, ti.f32)
                water10 = ti.cast(c10 == SURFACE_OCEAN, ti.f32) + ti.cast(c10 == SURFACE_INLAND_WATER, ti.f32)
                water01 = ti.cast(c01 == SURFACE_OCEAN, ti.f32) + ti.cast(c01 == SURFACE_INLAND_WATER, ti.f32)
                water11 = ti.cast(c11 == SURFACE_OCEAN, ti.f32) + ti.cast(c11 == SURFACE_INLAND_WATER, ti.f32)

                land0 = land00 * (1.0 - fx) + land10 * fx
                land1 = land01 * (1.0 - fx) + land11 * fx
                water0 = water00 * (1.0 - fx) + water10 * fx
                water1 = water01 * (1.0 - fx) + water11 * fx
                land_known = land0 * (1.0 - fy) + land1 * fy
                water_known = water0 * (1.0 - fy) + water1 * fy
                known_mix = ti.min(1.0, land_known + water_known)
                fallback_land = 0.0
                if z_val >= sea_level_m:
                    fallback_land = 1.0
                land_mix = land_known + (1.0 - known_mix) * fallback_land

                ice00 = ti.cast(self.ice_mask[ty0, tx0], ti.f32)
                ice10 = ti.cast(self.ice_mask[ty0, tx1], ti.f32)
                ice01 = ti.cast(self.ice_mask[ty1, tx0], ti.f32)
                ice11 = ti.cast(self.ice_mask[ty1, tx1], ti.f32)
                ice0 = ice00 * (1.0 - fx) + ice10 * fx
                ice1 = ice01 * (1.0 - fx) + ice11 * fx
                ice_mix = ti.max(0.0, ti.min(1.0, ice0 * (1.0 - fy) + ice1 * fy))

                forest00 = ti.cast(self.forest_density[ty0, tx0], ti.f32) / 255.0
                forest10 = ti.cast(self.forest_density[ty0, tx1], ti.f32) / 255.0
                forest01 = ti.cast(self.forest_density[ty1, tx0], ti.f32) / 255.0
                forest11 = ti.cast(self.forest_density[ty1, tx1], ti.f32) / 255.0
                forest0 = forest00 * (1.0 - fx) + forest10 * fx
                forest1 = forest01 * (1.0 - fx) + forest11 * fx
                forest_mix = ti.max(0.0, ti.min(1.0, forest0 * (1.0 - fy) + forest1 * fy))
                base = self.terrain_color(z_val, land_mix, sea_level_m)

                if forest_enabled != 0 and forest_mix > 0.001:
                    forest_alpha = ti.max(0.0, ti.min(1.0, forest_opacity)) * forest_mix * land_mix
                    green_boost = ti.max(0.0, ti.min(1.0, forest_green))
                    forest_color = ti.Vector([0.020 + 0.035 * green_boost, 0.155 + 0.190 * green_boost, 0.045 + 0.045 * green_boost])
                    canopy_variation = 0.82 + 0.18 * ti.sin(sample_lon * 37.0 + sample_lat * 19.0)
                    forest_color = forest_color * canopy_variation
                    base = base * (1.0 - forest_alpha) + forest_color * forest_alpha

                n_world_bump = n_world
                if ti.static(self.bump_scale > 0.0):
                    tx_next = ti.min(self.topo_w - 1, tx + 1)
                    ty_next = ti.min(self.topo_h - 1, ty + 1)
                    dz_dx = (ti.cast(self.topo[ty, tx_next], ti.f32) - z_val) * self.bump_scale
                    dz_dy = (ti.cast(self.topo[ty_next, tx], ti.f32) - z_val) * self.bump_scale
                    if flip_longitude:
                        dz_dx = -dz_dx
                    if flip_latitude:
                        dz_dy = -dz_dy

                    r_xz = ti.sqrt(n_world.x * n_world.x + n_world.z * n_world.z)
                    inv_r_xz = 1.0 / (r_xz + 1e-7)
                    cos_lon = n_world.z * inv_r_xz
                    sin_lon = n_world.x * inv_r_xz
                    tan_x = ti.Vector([cos_lon, 0.0, -sin_lon])
                    tan_y = ti.Vector([-n_world.y * sin_lon, r_xz, -n_world.y * cos_lon])
                    n_world_bump = (n_world - tan_x * dz_dx - tan_y * dz_dy).normalized()

                dot_l = n_world_bump.dot(light_dir)
                shade = ti.max(0.14, dot_l)
                twilight = 0.0
                if dot_l > -0.2 and dot_l < 0.2:
                    twilight = (0.2 - ti.abs(dot_l)) * 5.0
                rim = ti.pow(ti.max(0.0, 1.0 - z), 2.5)
                color = (
                    base * shade
                    + ti.Vector([0.80, 0.35, 0.16]) * twilight * 0.15
                    + ti.Vector([0.15, 0.24, 0.34]) * rim * ti.max(0.0, dot_l + 0.2)
                )

                if forest_enabled != 0 and forest_mix > 0.001:
                    shadow_strength = ti.max(0.0, ti.min(1.0, canopy_shadow)) * forest_mix * land_mix
                    shade_loss = shadow_strength * (0.22 + 0.42 * (1.0 - ti.max(0.0, dot_l)))
                    color = color * (1.0 - shade_loss) + ti.Vector([0.010, 0.050, 0.018]) * shadow_strength * 0.18

                ocean_mix = ti.max(0.0, ti.min(1.0, water_known * (1.0 - land_mix)))
                if ocean_enabled != 0 and ocean_mix > 0.001:
                    wave_strength = ti.max(0.0, ti.min(1.0, ocean_wave_strength))
                    roughness = ti.max(0.02, ti.min(1.0, ocean_roughness))
                    foam_strength = ti.max(0.0, ti.min(1.0, ocean_foam))
                    wave_a = ti.sin(sample_lon * 41.0 + sample_lat * 17.0 + ocean_time * (0.45 + roughness))
                    wave_b = ti.sin(sample_lon * -23.0 + sample_lat * 31.0 + ocean_time * (0.24 + roughness * 0.7))
                    wave_c = ti.sin((sample_lon + sample_lat) * 69.0 - ocean_time * (0.18 + roughness * 0.35))
                    wave = (wave_a * 0.52 + wave_b * 0.32 + wave_c * 0.16)
                    ocean_view_dir = rotate_view_to_world(ti.Vector([0.0, 0.0, 1.0]), yaw, pitch)
                    ocean_half_dir = (light_dir + ocean_view_dir).normalized()
                    wave_normal = (n_world_bump + ti.Vector([wave * 0.018 * roughness, wave_b * 0.012 * roughness, wave_c * 0.018 * roughness])).normalized()
                    spec_power = 18.0 + 72.0 * (1.0 - roughness)
                    glitter = ti.pow(ti.max(0.0, wave_normal.dot(ocean_half_dir)), spec_power) * (0.18 + 0.75 * roughness)
                    fresnel = ti.pow(ti.max(0.0, 1.0 - z), 2.0)
                    shallow = ti.max(0.0, ti.min(1.0, (z_val - MIN_ELEV) / (sea_level_m - MIN_ELEV + 1e-6)))
                    foam = ti.max(0.0, wave - 0.55) * foam_strength * (0.25 + 0.75 * shallow)
                    water_glow = ti.Vector([0.05, 0.22, 0.33]) * (0.04 + wave_strength * (0.08 + 0.08 * wave))
                    color = color + (water_glow + ti.Vector([0.58, 0.82, 1.0]) * glitter + ti.Vector([0.85, 0.95, 1.0]) * foam + ti.Vector([0.10, 0.22, 0.32]) * fresnel * 0.10) * ocean_mix

                if ice_enabled != 0 and ice_mix > 0.001:
                    ice_alpha = ti.max(0.0, ti.min(1.0, ice_opacity)) * ice_mix
                    cold = ti.max(0.0, ti.min(1.0, ice_blue))
                    ice_base = ti.Vector([0.94 - 0.10 * cold, 0.97 - 0.04 * cold, 1.0])
                    ice_shadow = ti.Vector([0.38, 0.52, 0.68])
                    ice_diffuse = ti.max(0.0, dot_l)
                    ice_color = ice_shadow * (0.32 + 0.10 * rim) + ice_base * (0.42 + 0.62 * ice_diffuse)
                    view_dir_world = rotate_view_to_world(ti.Vector([0.0, 0.0, 1.0]), yaw, pitch)
                    half_dir = (light_dir + view_dir_world).normalized()
                    specular = ti.pow(ti.max(0.0, n_world_bump.dot(half_dir)), 56.0) * ti.max(0.0, ti.min(1.0, ice_specular))
                    fresnel = ti.pow(ti.max(0.0, 1.0 - z), 2.2) * ti.max(0.0, dot_l + 0.15)
                    ice_color = ice_color + ti.Vector([0.78, 0.92, 1.0]) * (specular + fresnel * 0.16)
                    color = color * (1.0 - ice_alpha) + ice_color * ice_alpha

                if ti.static(self.show_grid):
                    lon_deg = lon * 180.0 / PI
                    lat_deg = lat * 180.0 / PI
                    rem_lon = ti.abs(lon_deg - ti.floor(lon_deg / 15.0) * 15.0)
                    rem_lat = ti.abs(lat_deg - ti.floor(lat_deg / 15.0) * 15.0)
                    dist_lon = ti.min(rem_lon, 15.0 - rem_lon)
                    dist_lat = ti.min(rem_lat, 15.0 - rem_lat)
                    line_width = 0.30 * zoom
                    if dist_lon < line_width or dist_lat < line_width:
                        intensity = 1.0 - ti.min(dist_lon, dist_lat) / line_width
                        color = color * (1.0 - 0.35 * intensity) + ti.Vector([1.0, 1.0, 1.0]) * 0.35 * intensity

            self.image[i, j] = ti.min(ti.Vector([1.0, 1.0, 1.0]), ti.max(color, 0.0))

    @ti.kernel
    def render_stars(self, yaw: ti.f32, pitch: ti.f32, zoom: ti.f32):
        aspect = ti.cast(self.width, ti.f32) / ti.cast(self.height, ti.f32)

        for idx in range(self.num_stars):
            star = self.stars[idx]
            pos_world = ti.Vector([star.x, star.y, star.z])
            mag = star.w

            cy = ti.cos(-yaw)
            sy = ti.sin(-yaw)
            x1 = cy * pos_world.x + sy * pos_world.z
            y1 = pos_world.y
            z1 = -sy * pos_world.x + cy * pos_world.z

            cp = ti.cos(-pitch)
            sp = ti.sin(-pitch)
            x2 = x1
            y2 = cp * y1 - sp * z1
            z2 = sp * y1 + cp * z1

            if z2 > 0.0:
                sx = x2 / z2
                sy_screen = y2 / z2
                r2 = sx * sx + sy_screen * sy_screen
                if r2 > 1.0:
                    u = (sx / (zoom * aspect) + 1.0) * 0.5
                    v = (sy_screen / zoom + 1.0) * 0.5
                    i = ti.cast(u * self.width, ti.i32)
                    j = ti.cast(v * self.height, ti.i32)

                    if 1 <= i < self.width - 1 and 1 <= j < self.height - 1:
                        intensity = ti.max(0.06, (6.6 - mag) / 8.0)
                        star_color = ti.Vector([1.0, 0.95, 0.86]) * intensity * 2.3
                        for di in ti.static(range(-1, 2)):
                            for dj in ti.static(range(-1, 2)):
                                dist2 = ti.cast(di * di + dj * dj, ti.f32)
                                weight = ti.max(0.0, 1.0 - dist2 * 0.48)
                                ni = i + di
                                nj = j + dj
                                self.image[ni, nj] = ti.min(
                                    ti.Vector([1.0, 1.0, 1.0]),
                                    self.image[ni, nj] + star_color * weight,
                                )

    def to_rgba_u8(self) -> np.ndarray:
        rgb = self.image.to_numpy()
        rgb = (np.clip(rgb, 0.0, 1.0) * 255.0).astype(np.uint8)
        rgb = np.flipud(np.transpose(rgb, (1, 0, 2)))
        alpha = np.full((self.height, self.width, 1), 255, dtype=np.uint8)
        return np.concatenate((rgb, alpha), axis=2)

    def mask_u8(self) -> np.ndarray:
        mask = self.globe_mask.to_numpy()
        return np.flipud(mask.T).astype(np.uint8, copy=False)


@ti.data_oriented
class TaichiProceduralCloudOverlay:
    def __init__(self, width: int, height: int):
        self.width = int(width)
        self.height = int(height)
        self.image = ti.Vector.field(4, dtype=ti.u8, shape=(self.width, self.height))

    @ti.kernel
    def render(
        self,
        yaw: ti.f32,
        pitch: ti.f32,
        zoom: ti.f32,
        sun_x: ti.f32,
        sun_y: ti.f32,
        sun_z: ti.f32,
        flip_longitude: ti.i32,
        flip_latitude: ti.i32,
        opacity: ti.f32,
        coverage: ti.f32,
        detail: ti.f32,
        cloud_time: ti.f32,
    ):
        aspect = ti.cast(self.width, ti.f32) / ti.cast(self.height, ti.f32)
        light_dir = ti.Vector([sun_x, sun_y, sun_z])
        for i, j in self.image:
            self.image[i, j] = ti.Vector([0, 0, 0, 0])
            u = (ti.cast(i, ti.f32) + 0.5) / ti.cast(self.width, ti.f32)
            v = (ti.cast(j, ti.f32) + 0.5) / ti.cast(self.height, ti.f32)
            sx = (u * 2.0 - 1.0) * zoom * aspect
            sy = (v * 2.0 - 1.0) * zoom
            r2 = sx * sx + sy * sy
            if r2 <= 1.0:
                z = ti.sqrt(1.0 - r2)
                n_view = ti.Vector([sx, sy, z])
                n_world = rotate_view_to_world(n_view, yaw, pitch)
                lon = ti.atan2(n_world.x, n_world.z)
                lat = ti.asin(ti.max(-1.0, ti.min(1.0, n_world.y)))
                if flip_longitude:
                    lon = -lon
                if flip_latitude:
                    lat = -lat

                band = ti.sin(lat * (5.0 + detail * 4.0) + ti.sin(lon * 3.0 + cloud_time * 0.08) * 0.85)
                cell = ti.sin(lon * (9.0 + detail * 8.0) + cloud_time * 0.13)
                swirl = ti.sin((lon + lat) * (13.0 + detail * 10.0) - cloud_time * 0.17)
                noise = 0.50 + 0.24 * band + 0.16 * cell + 0.10 * swirl
                threshold = ti.max(0.05, ti.min(0.95, coverage))
                density = ti.max(0.0, (noise - threshold) / ti.max(0.05, 1.0 - threshold))
                density = ti.min(1.0, density * density * 2.25)

                day = ti.max(0.0, n_world.dot(light_dir))
                limb = ti.max(0.0, ti.min(1.0, z))
                alpha = ti.max(0.0, ti.min(1.0, opacity * density * (0.25 + 0.75 * limb)))
                shade = 0.48 + 0.52 * day
                r = ti.cast(ti.min(255.0, 205.0 + 45.0 * shade), ti.u8)
                g = ti.cast(ti.min(255.0, 218.0 + 35.0 * shade), ti.u8)
                b = ti.cast(ti.min(255.0, 230.0 + 25.0 * shade), ti.u8)
                a = ti.cast(alpha * 255.0, ti.u8)
                self.image[i, j] = ti.Vector([r, g, b, a])

    def to_rgba_u8(self) -> np.ndarray:
        rgba = self.image.to_numpy().astype(np.uint8, copy=False)
        return np.flipud(np.transpose(rgba, (1, 0, 2)))


def project_ais_to_screen(
    frame: pd.DataFrame,
    yaw: float,
    pitch: float,
    zoom: float,
    width: int,
    height: int,
    flip_longitude: bool,
    flip_latitude: bool,
    horizon_eps: float,
) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["screen_x", "screen_y", "sog"])

    lat = np.radians(frame["lat"].to_numpy(dtype=np.float32))
    lon = np.radians(frame["lon"].to_numpy(dtype=np.float32))
    if flip_longitude:
        lon = -lon
    if flip_latitude:
        lat = -lat
    cos_lat = np.cos(lat)
    x = cos_lat * np.sin(lon)
    y = np.sin(lat)
    z = cos_lat * np.cos(lon)

    cy = math.cos(-yaw)
    sy = math.sin(-yaw)
    x1 = cy * x + sy * z
    y1 = y
    z1 = -sy * x + cy * z

    cp = math.cos(-pitch)
    sp = math.sin(-pitch)
    x2 = x1
    y2 = cp * y1 - sp * z1
    z2 = sp * y1 + cp * z1

    aspect = width / float(height)
    u = (x2 / (zoom * aspect) + 1.0) * 0.5
    v = (y2 / zoom + 1.0) * 0.5
    screen_x = u * width
    screen_y = v * height

    mask = (
        (z2 > horizon_eps)
        & ((x2 * x2 + y2 * y2) <= 1.0)
        & (screen_x >= 0.0)
        & (screen_x < width)
        & (screen_y >= 0.0)
        & (screen_y < height)
    )
    if not np.any(mask):
        return pd.DataFrame(columns=["screen_x", "screen_y", "sog"])

    projected = frame.loc[mask].copy()
    projected["screen_x"] = screen_x[mask].astype(np.float32)
    projected["screen_y"] = screen_y[mask].astype(np.float32)
    return projected


def project_aircraft_to_screen(
    frame: pd.DataFrame,
    yaw: float,
    pitch: float,
    zoom: float,
    width: int,
    height: int,
    flip_longitude: bool,
    flip_latitude: bool,
    horizon_eps: float,
    altitude_exaggeration: float,
) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["screen_x", "screen_y", "altitude_m", "speed_kt"])

    lat = np.radians(frame["lat"].to_numpy(dtype=np.float32))
    lon = np.radians(frame["lon"].to_numpy(dtype=np.float32))
    if flip_longitude:
        lon = -lon
    if flip_latitude:
        lat = -lat
    altitude = pd.to_numeric(frame.get("altitude_m", 0.0), errors="coerce").fillna(0.0).to_numpy(dtype=np.float32)
    radius = 1.0 + np.maximum(0.0, altitude) / 6_371_000.0 * max(0.0, float(altitude_exaggeration))
    cos_lat = np.cos(lat)
    x = radius * cos_lat * np.sin(lon)
    y = radius * np.sin(lat)
    z = radius * cos_lat * np.cos(lon)

    cy = math.cos(-yaw)
    sy = math.sin(-yaw)
    x1 = cy * x + sy * z
    y1 = y
    z1 = -sy * x + cy * z

    cp = math.cos(-pitch)
    sp = math.sin(-pitch)
    x2 = x1
    y2 = cp * y1 - sp * z1
    z2 = sp * y1 + cp * z1

    aspect = width / float(height)
    u = (x2 / (zoom * aspect) + 1.0) * 0.5
    v = (y2 / zoom + 1.0) * 0.5
    screen_x = u * width
    screen_y = v * height
    mask = (
        (z2 > horizon_eps)
        & (screen_x >= 0.0)
        & (screen_x < width)
        & (screen_y >= 0.0)
        & (screen_y < height)
    )
    if not np.any(mask):
        return pd.DataFrame(columns=["screen_x", "screen_y", "altitude_m", "speed_kt"])
    projected = frame.loc[mask].copy()
    projected["screen_x"] = screen_x[mask].astype(np.float32)
    projected["screen_y"] = screen_y[mask].astype(np.float32)
    return projected


def mask_overlay_to_globe(overlay: np.ndarray, globe_mask: np.ndarray) -> np.ndarray:
    if globe_mask.shape != overlay.shape[:2]:
        raise ValueError(f"Globe mask shape {globe_mask.shape} does not match overlay {overlay.shape}")
    masked = overlay.copy()
    masked[..., 3] = np.where(globe_mask > 0, masked[..., 3], 0).astype(np.uint8)
    return masked


def build_datashader_overlay_config(style_profile: str, layer_kind: str, color_mode: str, point_px: int) -> dict:
    cmaps = resolve_datashader_style_cmaps(style_profile)
    layer_kind = str(layer_kind or "ais")
    color_mode = str(color_mode or "density")
    if layer_kind == "aircraft":
        if color_mode == "altitude":
            cmap_key = "aircraft_altitude"
            shade_how = "linear"
            name = "aircraft_altitude"
        elif color_mode == "speed":
            cmap_key = "aircraft_speed"
            shade_how = "linear"
            name = "aircraft_speed"
        else:
            cmap_key = "aircraft_density"
            shade_how = "eq_hist"
            name = "aircraft_density"
        min_alpha = 80
        threshold = 0.42
    else:
        if color_mode == "speed":
            cmap_key = "ais_speed"
            shade_how = "linear"
            name = "ais_speed"
        else:
            cmap_key = "ais_density"
            shade_how = "eq_hist"
            name = "ais_density"
        min_alpha = 70
        threshold = 0.45
    return {
        "layer_kind": layer_kind,
        "color_mode": color_mode,
        "cmap_key": cmap_key,
        "cmap": cmaps[cmap_key],
        "how": shade_how,
        "min_alpha": min_alpha,
        "name": name,
        "dynspread_threshold": threshold,
        "dynspread_max_px": max(1, int(point_px)),
        "style_profile": resolve_style_profile(style_profile)["id"],
    }


class AISDatashaderOverlay:
    def __init__(
        self,
        width: int,
        height: int,
        color_by: str,
        point_px: int,
        speed_span: tuple[float, float],
    ):
        self.width = width
        self.height = height
        self.color_by = color_by
        self.point_px = point_px
        self.speed_span = speed_span
        self.style_profile = "scientific"
        self.canvas = ds.Canvas(
            plot_width=width,
            plot_height=height,
            x_range=(0.0, float(width)),
            y_range=(0.0, float(height)),
        )
        self.empty = np.zeros((height, width, 4), dtype=np.uint8)

    def set_style_profile(self, profile: str) -> None:
        self.style_profile = str(profile or "scientific")

    def render(self, projected: pd.DataFrame) -> np.ndarray:
        if projected.empty:
            return self.empty.copy()

        if self.color_by == "speed" and "sog" in projected.columns and projected["sog"].notna().any():
            config = build_datashader_overlay_config(self.style_profile, "ais", "speed", self.point_px)
            agg = self.canvas.points(projected, "screen_x", "screen_y", agg=ds.mean("sog"))
            overlay = tf.shade(
                agg,
                cmap=config["cmap"],
                how=config["how"],
                span=self.speed_span,
                min_alpha=config["min_alpha"],
                name=config["name"],
            )
        else:
            config = build_datashader_overlay_config(self.style_profile, "ais", "density", self.point_px)
            agg = self.canvas.points(projected, "screen_x", "screen_y", agg=ds.count())
            overlay = tf.shade(
                agg,
                cmap=config["cmap"],
                how=config["how"],
                min_alpha=config["min_alpha"],
                name=config["name"],
            )

        if self.point_px > 1:
            overlay = tf.dynspread(overlay, threshold=config["dynspread_threshold"], max_px=config["dynspread_max_px"])

        return np.asarray(overlay.to_pil().convert("RGBA"), dtype=np.uint8)


class AircraftDatashaderOverlay:
    def __init__(
        self,
        width: int,
        height: int,
        color_by: str,
        point_px: int,
        altitude_span: tuple[float, float] = (0.0, 13000.0),
        speed_span: tuple[float, float] = (80.0, 620.0),
    ):
        self.width = width
        self.height = height
        self.color_by = color_by
        self.point_px = point_px
        self.altitude_span = altitude_span
        self.speed_span = speed_span
        self.style_profile = "scientific"
        self.canvas = ds.Canvas(
            plot_width=width,
            plot_height=height,
            x_range=(0.0, float(width)),
            y_range=(0.0, float(height)),
        )
        self.empty = np.zeros((height, width, 4), dtype=np.uint8)

    def set_style_profile(self, profile: str) -> None:
        self.style_profile = str(profile or "scientific")

    def render(self, projected: pd.DataFrame) -> np.ndarray:
        if projected.empty:
            return self.empty.copy()
        if self.color_by == "altitude" and "altitude_m" in projected.columns and projected["altitude_m"].notna().any():
            config = build_datashader_overlay_config(self.style_profile, "aircraft", "altitude", self.point_px)
            agg = self.canvas.points(projected, "screen_x", "screen_y", agg=ds.mean("altitude_m"))
            overlay = tf.shade(
                agg,
                cmap=config["cmap"],
                how=config["how"],
                span=self.altitude_span,
                min_alpha=config["min_alpha"],
                name=config["name"],
            )
        elif self.color_by == "speed" and "speed_kt" in projected.columns and projected["speed_kt"].notna().any():
            config = build_datashader_overlay_config(self.style_profile, "aircraft", "speed", self.point_px)
            agg = self.canvas.points(projected, "screen_x", "screen_y", agg=ds.mean("speed_kt"))
            overlay = tf.shade(
                agg,
                cmap=config["cmap"],
                how=config["how"],
                span=self.speed_span,
                min_alpha=config["min_alpha"],
                name=config["name"],
            )
        else:
            config = build_datashader_overlay_config(self.style_profile, "aircraft", "density", self.point_px)
            agg = self.canvas.points(projected, "screen_x", "screen_y", agg=ds.count())
            overlay = tf.shade(
                agg,
                cmap=config["cmap"],
                how=config["how"],
                min_alpha=config["min_alpha"],
                name=config["name"],
            )
        if self.point_px > 1:
            overlay = tf.dynspread(overlay, threshold=config["dynspread_threshold"], max_px=config["dynspread_max_px"])
        return np.asarray(overlay.to_pil().convert("RGBA"), dtype=np.uint8)


def alpha_compose(background: np.ndarray, overlay: np.ndarray) -> np.ndarray:
    if overlay.shape != background.shape:
        raise ValueError(f"Overlay shape {overlay.shape} does not match background {background.shape}")

    out = background.copy()
    alpha = overlay[..., 3:4].astype(np.float32) / 255.0
    out[..., :3] = (
        overlay[..., :3].astype(np.float32) * alpha
        + out[..., :3].astype(np.float32) * (1.0 - alpha)
    ).astype(np.uint8)
    out[..., 3] = 255
    return out


PIN_MARKER_STYLE_PROFILES = {
    "scientific": {
        "colors": {
            "Observation": (255, 226, 112, 232),
            "Sample Site": (88, 214, 141, 232),
            "Anomaly": (255, 105, 97, 238),
            "Reference": (126, 188, 255, 232),
            "Event": (255, 168, 76, 238),
        },
        "selected_ring": (255, 255, 255, 220),
        "center": (12, 18, 24, 255),
        "label_bg": (15, 28, 42, 218),
        "label_text": (245, 250, 255, 255),
        "label_line": (255, 255, 255, 170),
    },
    "nautical": {
        "colors": {
            "Observation": (255, 238, 132, 234),
            "Sample Site": (91, 216, 205, 234),
            "Anomaly": (238, 80, 90, 240),
            "Reference": (82, 165, 232, 234),
            "Event": (255, 178, 82, 238),
        },
        "selected_ring": (237, 248, 255, 226),
        "center": (8, 32, 44, 255),
        "label_bg": (6, 44, 60, 220),
        "label_text": (235, 250, 255, 255),
        "label_line": (237, 248, 255, 176),
    },
    "tactical": {
        "colors": {
            "Observation": (160, 255, 140, 238),
            "Sample Site": (72, 255, 216, 238),
            "Anomaly": (255, 54, 66, 245),
            "Reference": (96, 176, 255, 238),
            "Event": (255, 198, 66, 242),
        },
        "selected_ring": (214, 255, 220, 235),
        "center": (0, 20, 12, 255),
        "label_bg": (0, 24, 14, 228),
        "label_text": (188, 255, 190, 255),
        "label_line": (160, 255, 140, 188),
    },
    "parchment": {
        "colors": {
            "Observation": (124, 79, 38, 230),
            "Sample Site": (77, 111, 76, 230),
            "Anomaly": (143, 49, 38, 238),
            "Reference": (80, 94, 120, 230),
            "Event": (151, 92, 34, 236),
        },
        "selected_ring": (255, 244, 202, 228),
        "center": (61, 39, 24, 255),
        "label_bg": (235, 213, 165, 222),
        "label_text": (70, 45, 25, 255),
        "label_line": (124, 79, 38, 180),
    },
}


def resolve_pin_marker_style(style_profile: str) -> dict[str, object]:
    key = str(style_profile or "scientific").strip().lower()
    if key not in PIN_MARKER_STYLE_PROFILES:
        key = "scientific"
    return PIN_MARKER_STYLE_PROFILES[key]


def pin_marker_style_packet() -> dict[str, object]:
    profiles: dict[str, object] = {}
    for profile_id, style in PIN_MARKER_STYLE_PROFILES.items():
        colors = style["colors"]
        profiles[profile_id] = {
            "pin_types": sorted(colors),
            "selected_ring": style["selected_ring"],
            "center": style["center"],
            "label_bg": style["label_bg"],
            "label_text": style["label_text"],
            "label_line": style["label_line"],
        }
    return {
        "schema": "rrkal_displaytools.pin_marker_style_profiles.v1",
        "profiles": profiles,
        "fallback": "scientific",
    }


def _extract_pin_records(payload: object) -> list[dict[str, object]]:
    if isinstance(payload, dict):
        pins = payload.get("pins", [])
    else:
        pins = payload
    if not isinstance(pins, list):
        return []
    return [dict(pin) for pin in pins if isinstance(pin, dict)]


def _extract_selected_pin_id(payload: object) -> str | None:
    if not isinstance(payload, dict):
        return None
    selected_pin_id = payload.get("selected_pin_id")
    return selected_pin_id if isinstance(selected_pin_id, str) else None


def _load_pin_json_text(text: str) -> object | None:
    try:
        return json.loads(text)
    except json.JSONDecodeError as first_error:
        try:
            return json.loads(text.encode("utf-8").decode("unicode_escape"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            print(f"Invalid --pin-json ignored: {first_error}")
            return None


def load_pin_records(pin_file: str | None, pin_json: str | None) -> tuple[list[dict[str, object]], str | None]:
    records: list[dict[str, object]] = []
    selected_pin_id: str | None = None
    if pin_file:
        try:
            payload = json.loads(Path(pin_file).read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Invalid --pin-file ignored: {exc}")
        else:
            records.extend(_extract_pin_records(payload))
            selected_pin_id = selected_pin_id or _extract_selected_pin_id(payload)
    if pin_json:
        payload = _load_pin_json_text(pin_json)
        if payload is not None:
            records.extend(_extract_pin_records(payload))
            selected_pin_id = selected_pin_id or _extract_selected_pin_id(payload)
    return records, selected_pin_id


def _pin_label_text(pin: dict[str, object]) -> str:
    text = str(pin.get("label") or pin.get("id") or "Pin").strip()
    if len(text) > 28:
        return text[:25] + "..."
    return text or "Pin"


def _pin_label_priority(pin: dict[str, object]) -> int:
    value = pin.get("label_priority", 50)
    if isinstance(value, bool):
        return 50
    try:
        return max(0, min(100, int(value)))
    except (TypeError, ValueError):
        return 50


def _boxes_intersect(a: tuple[int, int, int, int], b: tuple[int, int, int, int], pad: int = 4) -> bool:
    return not (
        a[2] + pad <= b[0]
        or b[2] + pad <= a[0]
        or a[3] + pad <= b[1]
        or b[3] + pad <= a[1]
    )


def _clamp_label_box(box: tuple[int, int, int, int], width: int, height: int) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = box
    box_w = x1 - x0
    box_h = y1 - y0
    x0 = max(0, min(width - box_w - 1, x0))
    y0 = max(0, min(height - box_h - 1, y0))
    return x0, y0, x0 + box_w, y0 + box_h


def _pin_label_candidates(
    x: int,
    y: int,
    text: str,
    marker_radius: int,
    width: int,
    height: int,
) -> list[tuple[int, int, int, int]]:
    label_w = max(42, min(220, len(text) * 7 + 14))
    label_h = 18
    gap = marker_radius + 8
    raw = [
        (x + gap, y - label_h - 4, x + gap + label_w, y - 4),
        (x + gap, y + 4, x + gap + label_w, y + 4 + label_h),
        (x - gap - label_w, y - label_h - 4, x - gap, y - 4),
        (x - gap - label_w, y + 4, x - gap, y + 4 + label_h),
    ]
    return [_clamp_label_box(box, width, height) for box in raw]


def _draw_pin_label_fallback(
    overlay: np.ndarray,
    planned: list[dict[str, object]],
    marker_style: dict[str, object],
) -> None:
    label_bg = marker_style["label_bg"]
    label_line = marker_style["label_line"]
    for item in planned:
        x = int(item["x"])
        y = int(item["y"])
        x0, y0, x1, y1 = item["box"]
        cx = max(x0, min(x1 - 1, x))
        cy = max(y0, min(y1 - 1, y))
        steps = max(abs(cx - x), abs(cy - y), 1)
        for step in range(steps + 1):
            px = int(round(x + (cx - x) * step / steps))
            py = int(round(y + (cy - y) * step / steps))
            if 0 <= py < overlay.shape[0] and 0 <= px < overlay.shape[1]:
                overlay[py, px, :3] = label_line[:3]
                overlay[py, px, 3] = max(int(overlay[py, px, 3]), int(label_line[3]))
        region = overlay[y0:y1, x0:x1]
        region[..., :3] = label_bg[:3]
        region[..., 3] = np.maximum(region[..., 3], int(label_bg[3]))


def _draw_pin_labels(
    overlay: np.ndarray,
    labels: list[dict[str, object]],
    marker_style: dict[str, object],
    width: int,
    height: int,
    label_mode: str = "auto",
    label_min_priority: int = 50,
) -> None:
    occupied: list[tuple[int, int, int, int]] = []
    planned: list[dict[str, object]] = []
    mode = str(label_mode or "auto")
    if mode not in {"auto", "selected", "priority", "hidden"}:
        mode = "auto"
    try:
        min_priority = max(0, min(100, int(label_min_priority)))
    except (TypeError, ValueError):
        min_priority = 50
    filtered: list[dict[str, object]] = []
    for label in labels:
        selected = bool(label.get("selected", False))
        priority = int(label.get("priority", 50))
        if mode == "hidden":
            continue
        if selected:
            filtered.append(label)
        elif mode == "selected":
            continue
        elif mode == "priority" and priority < min_priority:
            continue
        else:
            filtered.append(label)
    ordered_labels = sorted(
        filtered,
        key=lambda item: (
            not bool(item.get("selected", False)),
            -int(item.get("priority", 50)),
            str(item.get("text", "")),
        ),
    )
    for label in ordered_labels[:24]:
        x = int(label["x"])
        y = int(label["y"])
        text = str(label["text"])
        marker_radius = int(label["marker_radius"])
        for box in _pin_label_candidates(x, y, text, marker_radius, width, height):
            if any(_boxes_intersect(box, other) for other in occupied):
                continue
            occupied.append(box)
            planned.append({"x": x, "y": y, "text": text, "box": box})
            break
    if not planned:
        return
    try:
        from PIL import Image, ImageDraw, ImageFont

        image = Image.fromarray(overlay, mode="RGBA")
        draw = ImageDraw.Draw(image, mode="RGBA")
        font = ImageFont.load_default()
        label_bg = tuple(marker_style["label_bg"])
        label_text = tuple(marker_style["label_text"])
        label_line = tuple(marker_style["label_line"])
        for item in planned:
            x = int(item["x"])
            y = int(item["y"])
            x0, y0, x1, y1 = item["box"]
            draw.line((x, y, (x0 + x1) // 2, (y0 + y1) // 2), fill=label_line, width=1)
            draw.rectangle((x0, y0, x1, y1), fill=label_bg, outline=label_line)
            draw.text((x0 + 5, y0 + 3), str(item["text"]), fill=label_text, font=font)
        overlay[:] = np.asarray(image, dtype=np.uint8)
    except Exception:
        _draw_pin_label_fallback(overlay, planned, marker_style)


def render_pin_overlay(
    width: int,
    height: int,
    projected_pins: list[dict[str, object]],
    pin_size: int = 9,
    selected_pin_id: str | None = None,
    style_profile: str = "scientific",
    label_mode: str = "auto",
    label_min_priority: int = 50,
) -> np.ndarray:
    overlay = np.zeros((height, width, 4), dtype=np.uint8)
    radius = max(2, int(pin_size) // 2)
    marker_style = resolve_pin_marker_style(style_profile)
    marker_colors = marker_style["colors"]
    selected_ring = marker_style["selected_ring"]
    center_color = marker_style["center"]
    labels: list[dict[str, object]] = []
    for pin in projected_pins:
        if not bool(pin.get("visible", False)):
            continue
        try:
            x = int(round(float(pin["screen_x"])))
            y = int(round(float(pin["screen_y"])))
        except (KeyError, TypeError, ValueError):
            continue
        selected = selected_pin_id is not None and pin.get("id") == selected_pin_id
        color = marker_colors.get(str(pin.get("type", "Observation")), marker_colors["Observation"])
        marker_radius = radius + (2 if selected else 0)
        ring_radius = marker_radius + (3 if selected else 0)
        for dy in range(-ring_radius, ring_radius + 1):
            py = y + dy
            if py < 0 or py >= height:
                continue
            for dx in range(-ring_radius, ring_radius + 1):
                px = x + dx
                if px < 0 or px >= width:
                    continue
                dist2 = dx * dx + dy * dy
                if selected and marker_radius * marker_radius < dist2 <= ring_radius * ring_radius:
                    overlay[py, px, :3] = selected_ring[:3]
                    overlay[py, px, 3] = max(int(overlay[py, px, 3]), int(selected_ring[3]))
                elif dist2 <= marker_radius * marker_radius or dx == 0 or dy == 0:
                    alpha = color[3] if dist2 <= marker_radius * marker_radius else 190
                    overlay[py, px, :3] = color[:3]
                    overlay[py, px, 3] = max(int(overlay[py, px, 3]), alpha)
        if 0 <= x < width and 0 <= y < height:
            overlay[y, x, :3] = center_color[:3]
            overlay[y, x, 3] = center_color[3]
        labels.append(
            {
                "x": x,
                "y": y,
                "text": _pin_label_text(pin),
                "marker_radius": marker_radius,
                "priority": _pin_label_priority(pin),
                "selected": selected,
            }
        )
    _draw_pin_labels(overlay, labels, marker_style, width, height, label_mode, label_min_priority)
    return overlay


def alpha_compose_transparent(background: np.ndarray, overlay: np.ndarray) -> np.ndarray:
    if overlay.shape != background.shape:
        raise ValueError(f"Overlay shape {overlay.shape} does not match background {background.shape}")
    bg = background.astype(np.float32) / 255.0
    fg = overlay.astype(np.float32) / 255.0
    fg_a = fg[..., 3:4]
    bg_a = bg[..., 3:4]
    out_a = fg_a + bg_a * (1.0 - fg_a)
    safe_a = np.maximum(out_a, 1e-6)
    out_rgb = (fg[..., :3] * fg_a + bg[..., :3] * bg_a * (1.0 - fg_a)) / safe_a
    out = np.zeros_like(background)
    out[..., :3] = np.clip(out_rgb * 255.0, 0.0, 255.0).astype(np.uint8)
    out[..., 3:4] = np.clip(out_a * 255.0, 0.0, 255.0).astype(np.uint8)
    return out


def scale_bar_geometry(width: int, height: int, zoom: float, x: float, y: float) -> tuple[float, float, float, float]:
    km_per_px = max(0.001, 6371.0 * float(zoom) * 2.0 / max(1.0, float(min(width, height))))
    target_px = max(80.0, min(220.0, float(width) * 0.18))
    raw_km = max(1.0, target_px * km_per_px)
    magnitude = 10.0 ** math.floor(math.log10(raw_km))
    normalized = raw_km / magnitude
    if normalized >= 5.0:
        nice = 5.0 * magnitude
    elif normalized >= 2.0:
        nice = 2.0 * magnitude
    else:
        nice = magnitude
    px = max(40.0, nice / km_per_px)
    x0 = max(8.0, min(float(x), max(8.0, float(width) - px - 12.0)))
    y0 = max(24.0, min(float(y), max(24.0, float(height) - 16.0)))
    return x0, y0, x0 + px, nice


class FPSRecorder:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path or (CACHE_DIR / "fps_log.jsonl"))
        self.samples: list[dict] = []
        self.last_tick = time.time()
        atexit.register(self.close)

    def tick(self) -> None:
        now = time.time()
        delta = max(1e-6, now - self.last_tick)
        self.last_tick = now
        self.samples.append({"time": now, "fps": 1.0 / delta})
        if len(self.samples) > 6000:
            self.samples = self.samples[-3000:]

    def close(self) -> None:
        if not self.samples:
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as fh:
                for sample in self.samples:
                    fh.write(json.dumps(sample, ensure_ascii=False) + "\n")
            self.samples.clear()
        except Exception:
            return


FOREST_EVENT_CMAP = ["#fff3b0", "#ffb703", "#fb8500", "#e85d04", "#d00000"]


def normalize_forest_event_frame(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["lon", "lat", "frp", "confidence", "timestamp", "event_type"])
    lat_col = find_column(frame, LAT_ALIASES)
    lon_col = find_column(frame, LON_ALIASES)
    if lat_col is None or lon_col is None:
        raise ValueError("Forest event data must contain latitude/longitude columns.")
    out = pd.DataFrame(
        {
            "lat": pd.to_numeric(frame[lat_col], errors="coerce"),
            "lon": pd.to_numeric(frame[lon_col], errors="coerce"),
        }
    )
    frp_col = find_column(frame, ("frp", "power", "radiative_power", "brightness", "bright_ti4", "bright_ti5"))
    confidence_col = find_column(frame, ("confidence", "conf", "confidence_pct", "confidence_percent"))
    time_col = find_column(frame, ("timestamp", "time", "acq_datetime", "acq_time", "date", "acq_date"))
    type_col = find_column(frame, ("event_type", "type", "class", "source"))
    out["frp"] = pd.to_numeric(frame[frp_col], errors="coerce") if frp_col is not None else 1.0
    out["confidence"] = pd.to_numeric(frame[confidence_col], errors="coerce") if confidence_col is not None else 75.0
    if time_col is not None:
        out["timestamp"] = pd.to_datetime(frame[time_col], errors="coerce", utc=True)
    else:
        out["timestamp"] = pd.Timestamp.now(tz="UTC")
    out["event_type"] = frame[type_col].astype(str) if type_col is not None else "fire"
    out = out.dropna(subset=["lat", "lon"])
    out = out[(out["lat"].between(-90, 90)) & (out["lon"].between(-180, 180))]
    return out.reset_index(drop=True)


def dataframe_from_forest_event_text(text: str, source_name: str) -> pd.DataFrame:
    return normalize_forest_event_frame(dataframe_from_text(text, source_name))


def simulated_forest_events(count: int = 1600) -> pd.DataFrame:
    rng = np.random.default_rng(38291)
    centers = np.array(
        [
            [-4.5, -62.0],
            [-2.0, 112.0],
            [-18.0, 132.0],
            [55.0, -112.0],
            [61.0, 98.0],
            [-12.0, 24.0],
        ],
        dtype=np.float32,
    )
    choice = rng.integers(0, len(centers), size=count)
    lat = centers[choice, 0] + rng.normal(0.0, 3.2, size=count)
    lon = centers[choice, 1] + rng.normal(0.0, 5.8, size=count)
    frp = np.clip(rng.lognormal(mean=2.1, sigma=0.9, size=count), 0.5, 650.0)
    confidence = np.clip(rng.normal(78.0, 15.0, size=count), 15.0, 100.0)
    return pd.DataFrame(
        {
            "lat": lat.astype(np.float32),
            "lon": lon.astype(np.float32),
            "frp": frp.astype(np.float32),
            "confidence": confidence.astype(np.float32),
            "timestamp": pd.Timestamp.now(tz="UTC"),
            "event_type": "fire",
        }
    )


class ForestEventSource:
    def __init__(self, event_url: str | None, event_file: str | None, timeout: float, demo: bool):
        self.event_url = event_url
        self.event_file = event_file
        self.timeout = timeout
        self.demo = bool(demo)

    def read(self) -> pd.DataFrame:
        if self.event_file:
            path = Path(self.event_file)
            text = path.read_text(encoding="utf-8")
            return dataframe_from_forest_event_text(text, str(path))
        if self.event_url:
            text = read_url_text(self.event_url, self.timeout)
            return dataframe_from_forest_event_text(text, self.event_url)
        if self.demo:
            return simulated_forest_events()
        return pd.DataFrame(columns=["lon", "lat", "frp", "confidence", "timestamp", "event_type"])


class ForestEventDatashaderOverlay:
    def __init__(self, width: int, height: int, point_px: int, frp_span: tuple[float, float]):
        self.width = width
        self.height = height
        self.point_px = point_px
        self.frp_span = frp_span
        self.canvas = ds.Canvas(
            plot_width=width,
            plot_height=height,
            x_range=(0.0, float(width)),
            y_range=(0.0, float(height)),
        )
        self.empty = np.zeros((height, width, 4), dtype=np.uint8)

    def render(self, projected: pd.DataFrame) -> np.ndarray:
        if projected.empty:
            return self.empty.copy()
        if "frp" in projected.columns and projected["frp"].notna().any():
            agg = self.canvas.points(projected, "screen_x", "screen_y", agg=ds.max("frp"))
            overlay = tf.shade(
                agg,
                cmap=FOREST_EVENT_CMAP,
                how="linear",
                span=self.frp_span,
                min_alpha=90,
                name="forest_events_frp",
            )
        else:
            agg = self.canvas.points(projected, "screen_x", "screen_y", agg=ds.count())
            overlay = tf.shade(
                agg,
                cmap=FOREST_EVENT_CMAP,
                how="eq_hist",
                min_alpha=90,
                name="forest_events_density",
            )
        if self.point_px > 1:
            overlay = tf.dynspread(overlay, threshold=0.45, max_px=self.point_px)
        return np.asarray(overlay.to_pil().convert("RGBA"), dtype=np.uint8)


def load_vector_geojson_from_source(
    name: str,
    file_path: str | None = None,
    url: str | None = None,
    natural_earth_layer: str | None = None,
    natural_earth_source: str = "naturalearth",
) -> dict | None:
    try:
        if file_path:
            path = Path(file_path)
            if not path.exists():
                record_data_fetch_event("file", name, "missing", source=str(path), message="vector file not found")
                print(f"{name} vector file not found: {path}")
                return None
            record_data_fetch_event("file", name, "read", source=str(path), message="reading local vector source")
            suffix = path.suffix.lower()
            if suffix in {".json", ".geojson"}:
                return json.loads(path.read_text(encoding="utf-8"))
            if suffix in {".gpkg", ".shp", ".zip"}:
                try:
                    import geopandas as gpd
                except Exception as exc:
                    print(f"{name} vector source requires geopandas for {suffix}: {exc}")
                    return None
                frame = gpd.read_file(path)
                return json.loads(frame.to_json())
            print(f"Unsupported {name} vector file type: {path}")
            return None
        if url:
            cache_path = CACHE_DIR / f"vector_{re.sub(r'[^a-zA-Z0-9_]+', '_', name).strip('_')}.geojson"
            if cache_path.exists():
                startup_progress_message(f"讀取向量快取：{cache_path.name}")
                record_data_fetch_event("vector", name, "cache-hit", source=url, cache_path=str(cache_path), message="using cached vector geojson")
                return json.loads(cache_path.read_text(encoding="utf-8"))
            startup_progress_begin(f"下載向量圖層：{name}", None)
            text = read_url_text(url, timeout=90.0, progress_label=f"vector:{name}")
            cache_path.write_text(text, encoding="utf-8")
            record_data_fetch_event("vector", name, "cache-write", source=url, cache_path=str(cache_path), message="vector geojson cached", bytes_read=len(text.encode("utf-8", errors="replace")))
            startup_progress_done(f"{name} 向量圖層下載完成")
            return json.loads(text)
        if natural_earth_layer:
            path = natural_earth_geojson_path(natural_earth_source, natural_earth_layer)
            if not path.exists():
                record_data_fetch_event("naturalearth", name, "download-needed", source=f"{natural_earth_source}:{natural_earth_layer}", cache_path=str(path), message="Natural Earth cache missing")
                download_natural_earth_geojson(path, natural_earth_source, natural_earth_layer)
            else:
                record_data_fetch_event("naturalearth", name, "cache-hit", source=f"{natural_earth_source}:{natural_earth_layer}", cache_path=str(path), message="using Natural Earth cache")
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"{name} vector layer unavailable: {exc}")
    return None


def _append_geojson_geometry_lines(geometry: dict | None, out: list[np.ndarray]) -> None:
    if not geometry:
        return
    gtype = geometry.get("type")
    coords = geometry.get("coordinates")
    if not coords:
        return
    if gtype == "LineString":
        arr = np.asarray(coords, dtype=np.float32)
        if arr.ndim == 2 and arr.shape[0] >= 2:
            out.append(arr[:, :2])
    elif gtype == "MultiLineString":
        for line in coords:
            arr = np.asarray(line, dtype=np.float32)
            if arr.ndim == 2 and arr.shape[0] >= 2:
                out.append(arr[:, :2])
    elif gtype == "Polygon":
        for ring in coords:
            arr = np.asarray(ring, dtype=np.float32)
            if arr.ndim == 2 and arr.shape[0] >= 2:
                out.append(arr[:, :2])
    elif gtype == "MultiPolygon":
        for polygon in coords:
            for ring in polygon:
                arr = np.asarray(ring, dtype=np.float32)
                if arr.ndim == 2 and arr.shape[0] >= 2:
                    out.append(arr[:, :2])
    elif gtype == "GeometryCollection":
        for geom in geometry.get("geometries", []):
            _append_geojson_geometry_lines(geom, out)


def geojson_to_lines(obj: dict | None, decimate: int = 1) -> list[np.ndarray]:
    if not obj:
        return []
    lines: list[np.ndarray] = []
    if obj.get("type") == "FeatureCollection":
        for feature in obj.get("features", []):
            _append_geojson_geometry_lines(feature.get("geometry"), lines)
    elif obj.get("type") == "Feature":
        _append_geojson_geometry_lines(obj.get("geometry"), lines)
    else:
        _append_geojson_geometry_lines(obj, lines)
    step = max(1, int(decimate))
    if step <= 1:
        return lines
    decimated = []
    for line in lines:
        if len(line) <= 2:
            decimated.append(line)
        else:
            sampled = line[::step]
            if not np.array_equal(sampled[-1], line[-1]):
                sampled = np.vstack([sampled, line[-1]])
            decimated.append(np.ascontiguousarray(sampled))
    return decimated


class GeoVectorLineOverlay:
    def __init__(self, width: int, height: int, lines: list[np.ndarray], name: str):
        self.width = int(width)
        self.height = int(height)
        self.lines = lines
        self.name = name
        self.empty = np.zeros((height, width, 4), dtype=np.uint8)
        if not lines:
            print(f"{name} layer has no vector geometry loaded.")

    def render(
        self,
        yaw: float,
        pitch: float,
        zoom: float,
        flip_longitude: bool,
        flip_latitude: bool,
        globe_mask: np.ndarray,
        color: tuple[int, int, int],
        opacity: float,
        line_width: int,
        highlight_line_index: int | None = None,
        highlight_phase: float = 0.0,
        point_stride: int = 1,
    ) -> np.ndarray:
        if not self.lines:
            return self.empty.copy()
        if opacity <= 0.0 and highlight_line_index is None:
            return self.empty.copy()
        from PIL import Image, ImageDraw

        img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        rgba = (int(color[0]), int(color[1]), int(color[2]), int(255 * max(0.0, min(float(opacity), 1.0))))
        point_stride = max(1, int(point_stride))
        aspect = self.width / float(self.height)
        cy = math.cos(-yaw)
        sy = math.sin(-yaw)
        cp = math.cos(-pitch)
        sp = math.sin(-pitch)
        max_jump = max(self.width, self.height) * 0.35

        def draw_projected_line(line: np.ndarray, rgba_value: tuple[int, int, int, int], width_value: int) -> list[list[tuple[float, float]]]:
            segments: list[list[tuple[float, float]]] = []
            if len(line) < 2:
                return segments
            render_line = line
            if point_stride > 1 and len(render_line) > point_stride + 2:
                render_line = render_line[::point_stride]
                if not np.array_equal(render_line[-1], line[-1]):
                    render_line = np.vstack([render_line, line[-1]])
            lon = np.radians(render_line[:, 0].astype(np.float32))
            lat = np.radians(render_line[:, 1].astype(np.float32))
            if flip_longitude:
                lon = -lon
            if flip_latitude:
                lat = -lat
            cos_lat = np.cos(lat)
            x = cos_lat * np.sin(lon)
            y = np.sin(lat)
            z = cos_lat * np.cos(lon)
            x1 = cy * x + sy * z
            y1 = y
            z1 = -sy * x + cy * z
            x2 = x1
            y2 = cp * y1 - sp * z1
            z2 = sp * y1 + cp * z1
            visible = z2 > 0.006
            sx = ((x2 / (float(zoom) * aspect)) + 1.0) * 0.5 * self.width
            sy2 = (1.0 - ((y2 / float(zoom)) + 1.0) * 0.5) * self.height
            segment: list[tuple[float, float]] = []
            last_point: tuple[float, float] | None = None
            for idx in range(len(render_line)):
                if not visible[idx]:
                    if len(segment) >= 2:
                        draw.line(segment, fill=rgba_value, width=max(1, int(width_value)), joint="curve")
                        segments.append(segment)
                    segment = []
                    last_point = None
                    continue
                point = (float(sx[idx]), float(sy2[idx]))
                if last_point is not None:
                    if abs(point[0] - last_point[0]) > max_jump or abs(point[1] - last_point[1]) > max_jump:
                        if len(segment) >= 2:
                            draw.line(segment, fill=rgba_value, width=max(1, int(width_value)), joint="curve")
                            segments.append(segment)
                        segment = []
                segment.append(point)
                last_point = point
            if len(segment) >= 2:
                draw.line(segment, fill=rgba_value, width=max(1, int(width_value)), joint="curve")
                segments.append(segment)
            return segments

        for line_index, line in enumerate(self.lines):
            if len(line) < 2:
                continue
            if highlight_line_index is not None and line_index == int(highlight_line_index):
                pulse = 0.5 + 0.5 * math.sin(float(highlight_phase) * math.tau)
                glow_alpha = int(95 + 95 * pulse)
                glow_width = max(4, int(line_width) + int(7 + 5 * pulse))
                core_width = max(2, int(line_width) + 2)
                glow_rgba = (255, 255, 180, glow_alpha)
                core_rgba = (255, 255, 255, 255)
                draw_projected_line(line, glow_rgba, glow_width)
                draw_projected_line(line, core_rgba, core_width)
            else:
                draw_projected_line(line, rgba, max(1, int(line_width)))

        return mask_overlay_to_globe(np.asarray(img, dtype=np.uint8), globe_mask)

    def render_highlight(
        self,
        yaw: float,
        pitch: float,
        zoom: float,
        flip_longitude: bool,
        flip_latitude: bool,
        globe_mask: np.ndarray,
        line_index: int | None,
        highlight_phase: float = 0.0,
        line_width: int = 2,
    ) -> np.ndarray:
        if line_index is None or line_index < 0 or line_index >= len(self.lines):
            return self.empty.copy()
        return self.render(
            yaw,
            pitch,
            zoom,
            flip_longitude,
            flip_latitude,
            globe_mask,
            (0, 0, 0),
            0.0,
            max(1, int(line_width)),
            int(line_index),
            highlight_phase,
        )

    def hit_test(
        self,
        screen_x: float,
        screen_y: float,
        yaw: float,
        pitch: float,
        zoom: float,
        flip_longitude: bool,
        flip_latitude: bool,
        radius_px: float,
    ) -> dict | None:
        if not self.lines:
            return None
        aspect = self.width / float(self.height)
        cy = math.cos(-yaw)
        sy = math.sin(-yaw)
        cp = math.cos(-pitch)
        sp = math.sin(-pitch)
        best: dict | None = None
        best_d2 = float(radius_px) * float(radius_px)

        for line_index, line in enumerate(self.lines):
            if len(line) < 2:
                continue
            lon = np.radians(line[:, 0].astype(np.float32))
            lat = np.radians(line[:, 1].astype(np.float32))
            if flip_longitude:
                lon = -lon
            if flip_latitude:
                lat = -lat
            cos_lat = np.cos(lat)
            x = cos_lat * np.sin(lon)
            y = np.sin(lat)
            z = cos_lat * np.cos(lon)
            x1 = cy * x + sy * z
            y1 = y
            z1 = -sy * x + cy * z
            x2 = x1
            y2 = cp * y1 - sp * z1
            z2 = sp * y1 + cp * z1
            visible = z2 > 0.006
            if np.count_nonzero(visible) < 2:
                continue
            sx = ((x2 / (float(zoom) * aspect)) + 1.0) * 0.5 * self.width
            sy2 = (1.0 - ((y2 / float(zoom)) + 1.0) * 0.5) * self.height
            max_jump = max(self.width, self.height) * 0.35

            for idx in range(len(line) - 1):
                if not (visible[idx] and visible[idx + 1]):
                    continue
                x0 = float(sx[idx])
                y0 = float(sy2[idx])
                x1p = float(sx[idx + 1])
                y1p = float(sy2[idx + 1])
                if abs(x1p - x0) > max_jump or abs(y1p - y0) > max_jump:
                    continue
                vx = x1p - x0
                vy = y1p - y0
                seg_len2 = vx * vx + vy * vy
                if seg_len2 <= 1e-6:
                    continue
                t = max(0.0, min(1.0, ((float(screen_x) - x0) * vx + (float(screen_y) - y0) * vy) / seg_len2))
                px = x0 + vx * t
                py = y0 + vy * t
                dx = float(screen_x) - px
                dy = float(screen_y) - py
                d2 = dx * dx + dy * dy
                if d2 < best_d2:
                    best_d2 = d2
                    best = {
                        "line_index": line_index,
                        "distance_px": math.sqrt(d2),
                        "screen_x": px,
                        "screen_y": py,
                    }
        return best



BOUNDARY_SPECS = {
    "borders": {
        "name": "\u570b\u754c",
        "color": (220, 225, 235),
        "prefix": "border",
        "natural_earth_layer": "admin_0_boundary_lines_land",
        "source_note": "Natural Earth admin_0_boundary_lines_land. For strict work, pin the dataset version and dispute policy.",
    },
    "territorial_sea": {
        "name": "\u9818\u6d77",
        "color": (64, 224, 255),
        "prefix": "territorial_sea",
        "marine_regions_layer": "eez_12nm",
        "source_note": "Strict mode should use Marine Regions World 12 Nautical Miles Zone or equivalent official maritime boundary data.",
    },
    "eez": {
        "name": "\u7d93\u6fdf\u6d77\u57df EEZ",
        "color": (255, 213, 74),
        "prefix": "eez",
        "marine_regions_layer": "eez_boundaries",
        "source_note": "Strict mode should use Marine Regions World EEZ or equivalent official maritime boundary data.",
    },
    "high_seas": {
        "name": "\u516c\u6d77",
        "color": (177, 130, 255),
        "prefix": "high_seas",
        "marine_regions_layer": "high_seas",
        "source_note": "High-seas visualization should come from a maritime boundary dataset, not from guessed country buffers.",
    },
}


HYDROLOGY_SPECS = {
    "lakes": {
        "name": "\u6e56\u6cca / \u6c34\u5eab",
        "color": (74, 194, 235),
        "natural_earth_layer": "lakes",
        "source_note": "Natural Earth lakes are the basic layer; strict/local work should switch to HydroLAKES or OSM water polygons.",
        "prefix": "lake",
    },
    "rivers": {
        "name": "\u4e3b\u8981\u6cb3\u5ddd",
        "color": (92, 210, 255),
        "natural_earth_layer": "rivers_lake_centerlines",
        "source_note": "Natural Earth rivers_lake_centerlines are the basic layer; strict/local work should switch to HydroRIVERS, MERIT Hydro, or OSM waterways.",
        "prefix": "river",
    },
}


HYDROLOGY_RENDER_LOD_PROFILES = {
    "global": {
        "opacity_scale": 0.52,
        "width_scale": 0.70,
        "decimate_factor": 3.5,
        "source_hint": "coarse world overview; keep only major lakes/rivers",
    },
    "continental": {
        "opacity_scale": 0.78,
        "width_scale": 1.00,
        "decimate_factor": 2.0,
        "source_hint": "continent-scale hydrology; major rivers and lakes remain readable",
    },
    "regional": {
        "opacity_scale": 1.00,
        "width_scale": 1.35,
        "decimate_factor": 1.0,
        "source_hint": "regional hydrology; preserve source detail",
    },
    "local": {
        "opacity_scale": 1.00,
        "width_scale": 1.70,
        "decimate_factor": 1.0,
        "source_hint": "local hydrology; prefer strict HydroRIVERS/MERIT/OSM source",
    },
}


class HydrologyRenderLODProfile:
    def __init__(self, args) -> None:
        self.args = args

    def decision(self, lod: str, layer_id: str) -> dict:
        profile = HYDROLOGY_RENDER_LOD_PROFILES.get(lod, HYDROLOGY_RENDER_LOD_PROFILES["global"])
        spec = HYDROLOGY_SPECS.get(layer_id, {})
        prefix = spec.get("prefix", layer_id)
        base_decimate = max(1, int(getattr(self.args, "hydrology_decimate", 2)))
        layer_factor = 1.0
        if layer_id == "rivers" and lod in {"global", "continental"}:
            layer_factor = 1.25
        decimate = max(1, int(round(base_decimate * float(profile["decimate_factor"]) * layer_factor)))
        return {
            "lod": lod,
            "layer_id": layer_id,
            "prefix": prefix,
            "opacity_scale": float(profile["opacity_scale"]),
            "width_scale": float(profile["width_scale"]),
            "decimate": int(decimate),
            "source_hint": profile["source_hint"],
            "base_decimate": int(base_decimate),
        }

    def text(self, lod: str) -> str:
        lines = [
            "Hydrology render LOD profile",
            "",
            f"- active LOD: {lod}",
            "- purpose: centralize river/lake decimation, opacity, and line width before hydrology is split into a provider module.",
        ]
        for layer_id in HYDROLOGY_SPECS:
            decision = self.decision(lod, layer_id)
            lines.extend(
                [
                    "",
                    f"[{layer_id}]",
                    f"- decimate: {decision['decimate']} (base={decision['base_decimate']})",
                    f"- opacity scale: {decision['opacity_scale']:.2f}",
                    f"- width scale: {decision['width_scale']:.2f}",
                    f"- source hint: {decision['source_hint']}",
                ]
            )
        return "\n".join(lines)


HYDROLOGY_STRICT_SOURCE_TIERS = {
    "lakes": [
        {
            "tier": "basic",
            "source": "Natural Earth lakes",
            "use": "overview/cartographic context",
            "risk": "generalized geometry; missing small lakes/reservoirs; not suitable for strict hydrology measurement",
        },
        {
            "tier": "strict",
            "source": "HydroLAKES or official national lake/reservoir inventory",
            "use": "scientific/static lake layer",
            "risk": "requires pinned version, license, and attribute mapping",
        },
        {
            "tier": "local",
            "source": "OSM water polygons or national hydrography",
            "use": "local visual detail",
            "risk": "coverage and tagging consistency vary by region",
        },
    ],
    "rivers": [
        {
            "tier": "basic",
            "source": "Natural Earth rivers_lake_centerlines",
            "use": "overview/cartographic context",
            "risk": "only major centerlines; topology and stream order are generalized",
        },
        {
            "tier": "strict",
            "source": "HydroRIVERS or MERIT Hydro",
            "use": "scientific river network",
            "risk": "requires stream order, basin id, version, projection, and citation governance",
        },
        {
            "tier": "local",
            "source": "OSM waterways or official national hydrography",
            "use": "local operational display",
            "risk": "coverage and classification consistency vary by region",
        },
    ],
}


HYDROLOGY_STRICT_PROVIDER_PORTS = {
    "lakes": [
        {
            "id": "hydrolakes",
            "label": "HydroLAKES",
            "provider_id": "hydrology.hydrolakes",
            "file_attr": "hydrolakes_file",
            "url_attr": "hydrolakes_url",
            "tier": "strict",
            "status": "Strict lake/waterbody adapter port; expects GeoJSON/GPKG/SHP/ZIP normalized to lake boundary lines.",
        },
        {
            "id": "osm_water",
            "label": "OSM water polygons",
            "provider_id": "hydrology.osm_water",
            "file_attr": "osm_water_file",
            "url_attr": "osm_water_url",
            "tier": "local",
            "status": "Local detail port; useful for visual detail but needs tagging/coverage audit for scientific use.",
        },
    ],
    "rivers": [
        {
            "id": "hydrorivers",
            "label": "HydroRIVERS",
            "provider_id": "hydrology.hydrorivers",
            "file_attr": "hydrorivers_file",
            "url_attr": "hydrorivers_url",
            "tier": "strict",
            "status": "Strict river network adapter port; expects stream order and river id attributes when available.",
        },
        {
            "id": "merit_hydro",
            "label": "MERIT Hydro",
            "provider_id": "hydrology.merit_hydro",
            "file_attr": "merit_hydro_file",
            "url_attr": "merit_hydro_url",
            "tier": "strict",
            "status": "Strict hydrological network port; use pinned MERIT Hydro derived vector extracts.",
        },
        {
            "id": "osm_waterways",
            "label": "OSM waterways",
            "provider_id": "hydrology.osm_waterways",
            "file_attr": "osm_waterways_file",
            "url_attr": "osm_waterways_url",
            "tier": "local",
            "status": "Local detail port; good for operational display but requires regional QA.",
        },
    ],
}


def resolve_hydrology_strict_provider(args, layer_id: str) -> dict:
    metadata = {
        "source_version": str(getattr(args, "hydrology_source_version", "") or ""),
        "license": str(getattr(args, "hydrology_license", "") or ""),
        "projection": str(getattr(args, "hydrology_projection", "") or ""),
        "attribution": str(getattr(args, "hydrology_attribution", "") or ""),
        "schema_note": str(getattr(args, "hydrology_schema_note", "") or ""),
    }
    for port in HYDROLOGY_STRICT_PROVIDER_PORTS.get(layer_id, []):
        file_value = str(getattr(args, port["file_attr"], "") or "")
        url_value = str(getattr(args, port["url_attr"], "") or "")
        if file_value or url_value:
            metadata_missing = [key for key, value in metadata.items() if not value and key in {"source_version", "license", "projection", "attribution"}]
            return {
                "configured": True,
                "layer_id": layer_id,
                "provider_id": port["provider_id"],
                "label": port["label"],
                "tier": port["tier"],
                "file_path": file_value or None,
                "url": url_value or None,
                "source_url": file_value or url_value,
                "status": port["status"],
                "metadata": metadata,
                "metadata_missing": metadata_missing,
                "metadata_complete": not metadata_missing,
                "port": port,
            }
    return {
        "configured": False,
        "layer_id": layer_id,
        "provider_id": "",
        "label": "",
        "tier": "missing",
        "file_path": None,
        "url": None,
        "source_url": "",
        "status": "No strict hydrology provider configured for this layer.",
        "metadata": metadata,
        "metadata_missing": ["source"],
        "metadata_complete": False,
        "port": None,
    }


def hydrology_strict_provider_ports_text() -> str:
    lines = [
        "Hydrology strict provider ports",
        "",
        "Purpose: named strict-source ports for HydroLAKES, HydroRIVERS, MERIT Hydro, and OSM extracts before physical provider modules are split.",
    ]
    for layer_id, ports in HYDROLOGY_STRICT_PROVIDER_PORTS.items():
        lines.extend(["", f"[{layer_id}]"])
        for port in ports:
            lines.append(
                f"- {port['id']}: {port['label']} | tier={port['tier']} | file=--{port['file_attr'].replace('_', '-')} | url=--{port['url_attr'].replace('_', '-')}"
            )
            lines.append(f"  provider: {port['provider_id']}")
            lines.append(f"  status: {port['status']}")
    lines.extend(
        [
            "",
            "Shared strict metadata arguments:",
            "- --hydrology-source-version / HYDROLOGY_SOURCE_VERSION",
            "- --hydrology-license / HYDROLOGY_LICENSE",
            "- --hydrology-projection / HYDROLOGY_PROJECTION",
            "- --hydrology-attribution / HYDROLOGY_ATTRIBUTION",
            "- --hydrology-schema-note / HYDROLOGY_SCHEMA_NOTE",
        ]
    )
    return "\n".join(lines)


class HydrologyScientificStrictnessPolicy:
    def __init__(self, args) -> None:
        self.args = args

    def decision(self, lod: str, layer_id: str, provider_decision: dict) -> dict:
        provider_id = str(provider_decision.get("provider_id", ""))
        source_url = str(provider_decision.get("manifest", {}).get("source_url", ""))
        has_manual_source = provider_id.startswith("hydrology.file.") or provider_id.startswith("hydrology.url.")
        if has_manual_source:
            tier = "user-supplied"
            scientific_use = "depends-on-user-source"
            risk = "Manual hydrology source is accepted, but version/license/attribute metadata must be recorded before scientific publication."
            next_action = "Record source version, license, projection, geometry type, and hydrology attributes in provider manifest."
        elif provider_decision.get("strict_source", {}).get("configured"):
            strict_source = provider_decision["strict_source"]
            tier = strict_source.get("tier", "strict")
            if strict_source.get("metadata_complete", False):
                scientific_use = "strict-source-with-metadata"
                risk = "Strict-source port has required metadata fields; still inspect geometry/schema quality before publication."
                next_action = f"Validate {strict_source.get('label', 'strict provider')} schema attributes and geometry topology."
            else:
                scientific_use = "strict-source-port-metadata-incomplete"
                missing = ", ".join(strict_source.get("metadata_missing", []))
                risk = f"Strict-source port is configured, but metadata is incomplete: {missing}."
                next_action = "Fill source version, license, projection, and attribution before scientific publication."
        elif "naturalearth" in source_url.lower() or "naturalearth" in provider_id.lower() or provider_id.startswith("hydrology."):
            tier = "basic"
            scientific_use = "visual-context-only"
            risk = "Natural Earth hydrology is generalized cartography, not a strict hydrological network."
            if layer_id == "lakes":
                next_action = "Add HydroLAKES or official lake/reservoir adapter for strict lake/waterbody work."
            else:
                next_action = "Add HydroRIVERS or MERIT Hydro adapter for strict river network work."
        else:
            tier = "unknown"
            scientific_use = "unverified"
            risk = "Provider strictness cannot be inferred from the current source id."
            next_action = "Pin provider id, source version, license, projection, and schema."
        return {
            "lod": lod,
            "layer_id": layer_id,
            "tier": tier,
            "scientific_use": scientific_use,
            "risk": risk,
            "next_action": next_action,
            "metadata": provider_decision.get("strict_source", {}).get("metadata", {}),
            "metadata_missing": provider_decision.get("strict_source", {}).get("metadata_missing", []),
            "metadata_complete": provider_decision.get("strict_source", {}).get("metadata_complete", False),
            "source_tiers": HYDROLOGY_STRICT_SOURCE_TIERS.get(layer_id, []),
        }

    def text(self, lod: str, provider_policy) -> str:
        lines = [
            "Hydrology scientific strictness policy",
            "",
            f"- active LOD: {lod}",
            "- rule: basic Natural Earth hydrology is acceptable for visual context, not strict scientific measurement.",
        ]
        for layer_id in HYDROLOGY_SPECS:
            provider_decision = provider_policy.decision(lod, layer_id)
            decision = self.decision(lod, layer_id, provider_decision)
            lines.extend(
                [
                    "",
                    f"[{layer_id}]",
                    f"- current tier: {decision['tier']}",
                    f"- scientific use: {decision['scientific_use']}",
                    f"- risk: {decision['risk']}",
                    f"- next action: {decision['next_action']}",
                    f"- metadata complete: {decision['metadata_complete']}",
                    f"- metadata missing: {', '.join(decision['metadata_missing']) if decision['metadata_missing'] else '(none)'}",
                    "- strict source ladder:",
                ]
            )
            for tier in decision["source_tiers"]:
                lines.append(f"  - {tier['tier']}: {tier['source']} | use={tier['use']} | risk={tier['risk']}")
        return "\n".join(lines)


PROJECT_FEATURE_STATUS = [
    ("Core renderer", "done", "Taichi globe kernel plus terrain, ice, forest, ocean material hooks live in the current monolithic renderer."),
    ("Mass point rendering", "done", "AIS/ADS-B use Datashader screen-space aggregation with horizon clipping and sampling controls."),
    ("Realtime feeds", "done", "AIS feeder/WebSocket/API/file/database ports exist; ADS-B has matching ports and simulated fallback."),
    ("Qt controls", "done", "Side panel, Photoshop-like layer list, locks, groups, timeline dock, and mode switch are present."),
    ("LOD / basemap switching", "partial", "BasemapLODManager exists; high-resolution provider switching still needs separate modules."),
    ("Hydrology layers", "partial", "Natural Earth lakes/rivers and manual source hooks exist; strict HydroRIVERS/MERIT/OSM adapters are next."),
    ("Ocean conditions", "partial", "Taichi ocean material accepts normalized wave/roughness/foam; NOAA/HYCOM/Copernicus registry ports can read configured URL summaries."),
    ("Maritime jurisdictions", "partial", "Country boundaries and Marine Regions WFS/manual loaders use the vector overlay path; provider version pinning is still needed."),
    ("Projection modes", "port", "Globe works; Mercator/equirectangular/polar should become projection backends, not separate apps."),
    ("Export pipeline", "port", "Screenshot/video/export buttons are UI ports; capture implementation is staged."),
    ("Decoupling", "partial", "Module boundaries and handoff snapshot exist; physical split should wait until one runtime pass confirms contracts."),
]

FEATURE_STATUS_LABELS = {
    "done": "done",
    "partial": "partial",
    "port": "port",
    "next": "next",
}


def project_feature_status_text() -> str:
    lines = [
        "Work board until 06:00",
        "",
        "Principle: align data pipes, layers, LOD, and UI ports first; split modules after the prototype stops shifting.",
        "",
    ]
    for name, state, note in PROJECT_FEATURE_STATUS:
        label = FEATURE_STATUS_LABELS.get(state, state)
        lines.append(f"[{label}] {name}: {note}")
    lines.extend([
        "",
        "Priority:",
        "1. Protect FPS: avoid unnecessary overlay recomputation; route expensive layers through cache and LOD.",
        "2. Add real data: hydrology, EEZ/territorial sea/high seas, and ocean conditions should use replaceable providers.",
        "3. Decouple: split data_sources/vector_layers/overlays first, then render_core and projection.",
    ])
    return "\n".join(lines)


DATA_SOURCE_CATALOG = [
    ("Basemap / elevation", "GEBCO / ETOPO / Copernicus DEM / local tiled DEM", "LOD manager chooses resolution; close views should not rely on one low-resolution global grid."),
    ("Land-water mask", "Natural Earth land + ocean polygons / GSHHG / OSM coastline", "Land-water classification must not depend only on elevation 0m; below-sea-level land requires polygon correction."),
    ("Lakes / rivers", "Natural Earth / HydroRIVERS / HydroLAKES / MERIT Hydro / OSM waterway", "Natural Earth is the basic layer; regional/local LOD should switch to HydroRIVERS, MERIT, or OSM."),
    ("Borders", "Natural Earth Admin 0 / GADM / OSM boundary", "Strict work requires version/date and disputed-boundary policy."),
    ("Territorial sea / EEZ / high seas", "Marine Regions / VLIZ / Flanders Marine Institute datasets", "Use official maritime polygons rather than guessing from country boundaries."),
    ("AIS vessels", "AISStream / local feeder / MySQL table / replay file", "Realtime-only layer; static and timeseries modes should hide realtime feeds."),
    ("ADS-B aircraft", "OpenSky historical/API / ADS-B Exchange-compatible feed / local feeder / replay file", "Public realtime websocket access is often restricted; keep feeder and replay ports."),
    ("Ocean conditions", "NOAA WaveWatch III / HYCOM / Copernicus Marine / local raster or point feed", "Taichi ocean material consumes normalized wave_strength, roughness, and foam, not provider-specific fields."),
    ("Clouds / atmosphere", "NOAA GOES / Himawari / EUMETSAT / local cloud texture or volume field", "Use the Taichi procedural cloud layer now; later swap in real satellite or volume providers."),
]

DATA_PROVIDER_TIERS = [
    {"domain": "hydrology", "label": "Hydrology", "state": "partial", "active": "Natural Earth lakes/rivers_lake_centerlines", "next": "HydroRIVERS, HydroLAKES, MERIT Hydro, OSM water polygons", "module": "data_sources/hydrology_provider.py"},
    {"domain": "maritime_boundaries", "label": "Territorial sea / EEZ / high seas", "state": "partial", "active": "Marine Regions WFS port + manual GeoJSON/file URL", "next": "Marine Regions release pinning, cache manifest, feature simplification by LOD", "module": "data_sources/maritime_boundary_provider.py"},
    {"domain": "ocean_conditions", "label": "Ocean conditions", "state": "partial", "active": "manual/file/url plus NOAA WW3/HYCOM/Copernicus registry ports normalized to wave_strength/roughness/foam", "next": "provider-specific gridded extractors and release/version metadata", "module": "data_sources/ocean_condition_provider.py"},
    {"domain": "atmosphere", "label": "Clouds / atmosphere", "state": "port", "active": "Taichi procedural cloud shell basic", "next": "GOES/Himawari/EUMETSAT tile or volume provider", "module": "data_sources/atmosphere_provider.py"},
    {"domain": "basemap_lod", "label": "Basemap LOD", "state": "partial", "active": "BasemapLODManager + cached global raster", "next": "tile pyramid, per-provider resolution contract, projection-aware cache keys", "module": "projection/basemap_lod.py"},
]

LAYER_PROVIDER_REGISTRY = {
    "globe": {
        "provider": "basemap_lod.global_elevation",
        "domain": "basemap_lod",
        "mode": "static/timeseries/realtime",
        "renderer_input": "topography raster + land/water/ice/forest masks",
        "lod_policy": "BasemapLODManager chooses global/continental/regional/local context.",
    },
    "lakes": {
        "provider": "hydrology.naturalearth.lakes",
        "domain": "hydrology",
        "mode": "static/timeseries/realtime",
        "renderer_input": "normalized lon/lat line geometry",
        "lod_policy": "Natural Earth basic; swap HydroLAKES/OSM when LOD becomes regional/local.",
    },
    "rivers": {
        "provider": "hydrology.naturalearth.rivers",
        "domain": "hydrology",
        "mode": "static/timeseries/realtime",
        "renderer_input": "normalized lon/lat line geometry",
        "lod_policy": "Natural Earth basic; swap HydroRIVERS/MERIT/OSM when LOD becomes regional/local.",
    },
    "borders": {
        "provider": "naturalearth.admin0_boundaries",
        "domain": "maritime_boundaries",
        "mode": "static/timeseries/realtime",
        "renderer_input": "normalized lon/lat line geometry",
        "lod_policy": "Natural Earth basic; strict work should pin GADM/OSM or official source version.",
    },
    "territorial_sea": {
        "provider": "marine_regions.territorial_sea",
        "domain": "maritime_boundaries",
        "mode": "static/timeseries/realtime",
        "renderer_input": "normalized maritime boundary geometry",
        "lod_policy": "Marine Regions WFS/manual GeoJSON; simplify by LOD before rendering.",
    },
    "eez": {
        "provider": "marine_regions.eez",
        "domain": "maritime_boundaries",
        "mode": "static/timeseries/realtime",
        "renderer_input": "normalized maritime boundary geometry",
        "lod_policy": "Marine Regions WFS/manual GeoJSON; simplify by LOD before rendering.",
    },
    "high_seas": {
        "provider": "marine_regions.high_seas",
        "domain": "maritime_boundaries",
        "mode": "static/timeseries/realtime",
        "renderer_input": "normalized maritime boundary geometry",
        "lod_policy": "Use explicit high-seas dataset, not inferred country buffers.",
    },
    "ais": {
        "provider": "ais.realtime_or_replay",
        "domain": "realtime_feeds",
        "mode": "realtime",
        "renderer_input": "DataFrame lon/lat/sog/cog/timestamp projected to screen space",
        "lod_policy": "Datashader sampling adapts to FPS; hidden outside realtime mode.",
    },
    "aircraft": {
        "provider": "adsb.realtime_or_replay",
        "domain": "realtime_feeds",
        "mode": "realtime",
        "renderer_input": "DataFrame lon/lat/altitude/speed/timestamp projected to screen space",
        "lod_policy": "Datashader sampling adapts to FPS; hidden outside realtime mode.",
    },
    "clouds": {
        "provider": "atmosphere.procedural_clouds",
        "domain": "atmosphere",
        "mode": "realtime",
        "renderer_input": "Taichi-generated cloud shell parameters",
        "lod_policy": "Basic procedural layer now; later swap GOES/Himawari/EUMETSAT provider.",
    },
}

PROVIDER_CACHE_MANIFEST_FIELDS = [
    ("provider_id", "Stable ID, e.g. hydrology.naturalearth.rivers or marine_regions.eez."),
    ("source_url", "Original download URL, or absolute local file path."),
    ("source_version", "Dataset version/release date; if absent, record retrieved_at."),
    ("license", "License and attribution text."),
    ("projection", "Coordinate system, usually EPSG:4326."),
    ("lod", "global / continental / regional / local."),
    ("cache_path", "Normalized local cache file."),
    ("schema", "Output field contract, e.g. lon/lat/geometry/value/timestamp."),
    ("simplification", "Vector simplification, decimate, max_features, raster step, etc."),
    ("created_at", "Cache creation timestamp."),
]


def data_source_catalog_text() -> str:
    lines = ["Real data source catalog", "", "Each layer must state source, resolution, offline-cache support, and time support.", ""]
    for name, source, note in DATA_SOURCE_CATALOG:
        lines.append(f"{name}")
        lines.append(f"  source: {source}")
        lines.append(f"  policy: {note}")
        lines.append("")
    lines.extend([
        "Integration rules:",
        "1. Providers download/cache/normalize; they do not touch Qt or Taichi kernels.",
        "2. Renderers consume normalized arrays, dataframes, or raster tiles.",
        "3. UI changes parameters and source choices only; it should not parse heavy data directly.",
    ])
    return "\n".join(lines)


def provider_catalog_text() -> str:
    lines = ["Provider split status", "", "Target interface for decoupling: source, cache, normalize, render input; no direct UI coupling.", ""]
    for item in DATA_PROVIDER_TIERS:
        state = FEATURE_STATUS_LABELS.get(item["state"], item["state"])
        lines.append(f"[{state}] {item['label']} ({item['domain']})")
        lines.append(f"  active: {item['active']}")
        lines.append(f"  next: {item['next']}")
        lines.append(f"  target module: {item['module']}")
        lines.append("")
    lines.append("When split: renderer must not import Qt; Qt must not download data; providers must not know Taichi kernels.")
    return "\n".join(lines)


def layer_provider_registry_text() -> str:
    lines = [
        "Layer to provider registry",
        "",
        "This is the contract that lets UI layers, provider modules, and render inputs be split apart later.",
        "",
    ]
    for layer_id, meta in LAYER_PROVIDER_REGISTRY.items():
        lines.append(f"- {layer_id}: {meta['provider']}")
        lines.append(f"  domain: {meta['domain']}")
        lines.append(f"  mode: {meta['mode']}")
        lines.append(f"  renderer input: {meta['renderer_input']}")
        lines.append(f"  LOD policy: {meta['lod_policy']}")
    return "\n".join(lines)


def provider_cache_manifest_text() -> str:
    lines = [
        "Provider cache manifest",
        "",
        "Purpose: hydrology, maritime boundaries, ocean conditions, atmosphere, and basemap LOD should share cache metadata.",
        "",
        "Fields:",
    ]
    for name, description in PROVIDER_CACHE_MANIFEST_FIELDS:
        lines.append(f"- {name}: {description}")
    lines.extend([
        "",
        "Rules:",
        "1. Provider creates the manifest; Qt UI and Taichi renderer do not.",
        "2. Renderer consumes normalized payload only, not source_url.",
        "3. UI displays manifest summary and triggers reload only.",
        "4. Strict scientific data must keep source_version, license, and projection.",
    ])
    return "\n".join(lines)


def build_provider_cache_manifest(
    provider_id: str,
    source_url: str | None = None,
    source_version: str | None = None,
    license_text: str | None = None,
    projection: str = "EPSG:4326",
    lod: str = "global",
    cache_path: str | None = None,
    schema: dict | None = None,
    simplification: dict | None = None,
) -> dict:
    return {
        "provider_id": str(provider_id),
        "source_url": source_url or "",
        "source_version": source_version or "",
        "license": license_text or "",
        "projection": str(projection or "EPSG:4326"),
        "lod": str(lod or "global"),
        "cache_path": cache_path or "",
        "schema": schema or {},
        "simplification": simplification or {},
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


def provider_manifest_templates(lod: str = "global") -> list[dict]:
    return [
        build_provider_cache_manifest(
            f"basemap.{lod}.globe",
            source_url="gebco/natural-earth/runtime",
            source_version="runtime-selected",
            license_text="depends on selected topo/basemap provider",
            lod=lod,
            cache_path=str(CACHE_DIR / f"basemap_globe_{lod}_manifest.json"),
            schema={"raster": "topography/color/land-water mask", "fields": ["elevation_m", "land_mask"]},
            simplification={"projection": "globe", "target": "TaichiGlobeRenderer", "lod": lod},
        ),
        build_provider_cache_manifest(
            "hydrology.naturalearth.lakes",
            source_url="naturalearth:lakes",
            source_version="runtime-selected",
            license_text="Natural Earth public domain",
            lod=lod,
            cache_path=str(CACHE_DIR / "vector_lakes.geojson"),
            schema={"geometry": "LineString/MultiLineString", "fields": ["name"]},
            simplification={"decimate": "HYDROLOGY_DECIMATE"},
        ),
        build_provider_cache_manifest(
            "hydrology.naturalearth.rivers",
            source_url="naturalearth:rivers_lake_centerlines",
            source_version="runtime-selected",
            license_text="Natural Earth public domain",
            lod=lod,
            cache_path=str(CACHE_DIR / "vector_rivers.geojson"),
            schema={"geometry": "LineString/MultiLineString", "fields": ["name"]},
            simplification={"decimate": "HYDROLOGY_DECIMATE"},
        ),
        build_provider_cache_manifest(
            "marine_regions.eez",
            source_url=marine_regions_wfs_geojson_url("eez_boundaries"),
            source_version="runtime WFS",
            license_text="Marine Regions/VLIZ attribution required",
            lod=lod,
            cache_path=str(CACHE_DIR / "vector_eez.geojson"),
            schema={"geometry": "LineString/MultiLineString/Polygon boundary", "fields": ["name", "territory"]},
            simplification={"decimate": "BOUNDARY_DECIMATE", "max_features_env": "MARINE_REGIONS_MAX_FEATURES"},
        ),
        build_provider_cache_manifest(
            "ocean_conditions.normalized",
            source_url="manual/file/url/noaa/hycom/copernicus",
            source_version="runtime",
            license_text="depends on selected ocean provider",
            lod=lod,
            cache_path=str(CACHE_DIR / "ocean_conditions_cache.json"),
            schema={"fields": ["wave_strength", "roughness", "foam", "timestamp"]},
            simplification={"refresh_seconds": "OCEAN_CONDITION_REFRESH"},
        ),
        build_provider_cache_manifest(
            "ocean_conditions.provider_registry",
            source_url=",".join(OCEAN_PROVIDER_REGISTRY.keys()),
            source_version="runtime",
            license_text="depends on selected provider",
            lod=lod,
            cache_path=str(CACHE_DIR / "ocean_provider_registry_manifest.json"),
            schema={"fields": ["source", "source_attr", "wave_strength", "roughness", "foam"]},
            simplification={"adapter_contract": "OCEAN_PROVIDER_REGISTRY"},
        ),
        build_provider_cache_manifest(
            "atmosphere.procedural_clouds",
            source_url="procedural",
            source_version="basic",
            license_text="generated locally",
            lod=lod,
            cache_path="",
            schema={"fields": ["opacity", "coverage", "detail", "time"]},
            simplification={"animation_fps": "CLOUD_ANIMATION_FPS"},
        ),
        build_provider_cache_manifest(
            "ais.realtime_or_replay",
            source_url="url/file/database/simulated",
            source_version="runtime",
            license_text="depends on selected AIS provider",
            lod=lod,
            cache_path=str(CACHE_DIR / "ais_feed_cache.json"),
            schema={"fields": ["lat", "lon", "mmsi", "sog", "cog", "heading", "timestamp"]},
            simplification={"sample_ratio": "AIS_SAMPLE_RATIO", "max_age_minutes": "AIS_MAX_AGE_MINUTES"},
        ),
        build_provider_cache_manifest(
            "adsb.realtime_or_replay",
            source_url="url/file/database/simulated",
            source_version="runtime",
            license_text="depends on selected ADS-B provider",
            lod=lod,
            cache_path=str(CACHE_DIR / "aircraft_feed_cache.json"),
            schema={"fields": ["lat", "lon", "icao24", "callsign", "altitude_m", "speed_kt", "heading", "timestamp"]},
            simplification={"sample_ratio": "AIRCRAFT_SAMPLE_RATIO", "max_age_minutes": "AIRCRAFT_MAX_AGE_MINUTES"},
        ),
    ]


def provider_manifest_templates_text(lod: str = "global") -> str:
    lines = [
        "Provider manifest templates",
        "",
        f"LOD context: {lod}",
        "",
    ]
    for manifest in provider_manifest_templates(lod):
        lines.append(f"- {manifest['provider_id']}")
        lines.append(f"  source: {manifest['source_url']}")
        lines.append(f"  cache: {manifest['cache_path'] or '(none)'}")
        lines.append(f"  schema: {manifest['schema']}")
        lines.append(f"  simplification: {manifest['simplification']}")
    return "\n".join(lines)


def dedupe_provider_manifests(manifests: list[dict]) -> list[dict]:
    deduped: dict[str, dict] = {}
    for manifest in manifests:
        provider_id = str(manifest.get("provider_id", ""))
        if not provider_id:
            continue
        deduped[provider_id] = manifest
    return [deduped[key] for key in sorted(deduped)]


def provider_health_summary(lod: str = "global") -> str:
    lines = [f"Provider health summary for LOD={lod}"]
    for item in DATA_PROVIDER_TIERS:
        state = FEATURE_STATUS_LABELS.get(item["state"], item["state"])
        lines.append(f"- {item['domain']}: {state}; active={item['active']}; target={item['module']}")
    return "\n".join(lines)


def layer_provider_summary(layer_ids: list[str], mode: str, lod: str) -> str:
    lines = [f"Active layer provider summary for mode={mode}, LOD={lod}"]
    for layer_id in layer_ids:
        meta = LAYER_PROVIDER_REGISTRY.get(layer_id)
        if not meta:
            continue
        lines.append(f"- {layer_id}: {meta['provider']} -> {meta['renderer_input']}")
    if len(lines) == 1:
        lines.append("- no registered active layer providers")
    return "\n".join(lines)


PROJECTION_PIPELINE_MODES = {
    "globe": {
        "label": "3D globe",
        "camera": "yaw/pitch/zoom spherical camera",
        "overlay_space": "screen-space after horizon clipping",
        "horizon_clipping": True,
        "basemap_target": "TaichiGlobeRenderer",
        "lod_strategy": "km_per_pixel from projected globe radius",
        "shared_layers": ["basemap", "hydrology", "boundaries", "ice", "forest"],
        "mode_specific_layers": ["stars", "volumetric_clouds", "AIS/ADS-B visible hemisphere"],
    },
    "mercator": {
        "label": "Web Mercator",
        "camera": "pan/zoom planar map camera",
        "overlay_space": "projected planar coordinates then screen-space rasterization",
        "horizon_clipping": False,
        "basemap_target": "PlanarTileRenderer",
        "lod_strategy": "tile zoom / km_per_pixel from latitude",
        "shared_layers": ["basemap", "hydrology", "boundaries", "ice", "forest"],
        "mode_specific_layers": ["tile pyramid", "wraparound antimeridian handling"],
    },
    "equirectangular": {
        "label": "Equirectangular",
        "camera": "lon/lat extent camera",
        "overlay_space": "lon/lat to screen affine transform",
        "horizon_clipping": False,
        "basemap_target": "PlanarRasterRenderer",
        "lod_strategy": "extent width / screen width",
        "shared_layers": ["basemap", "hydrology", "boundaries", "ice", "forest"],
        "mode_specific_layers": ["scientific gridded rasters", "global comparison views"],
    },
}


def projection_pipeline_contract_text(projection: str = "globe", lod: str = "global") -> str:
    projection = str(projection or "globe")
    mode = PROJECTION_PIPELINE_MODES.get(projection, PROJECTION_PIPELINE_MODES["globe"])
    lines = [
        "Projection pipeline contract",
        "",
        f"- projection: {projection}",
        f"- label: {mode['label']}",
        f"- lod: {lod}",
        f"- camera: {mode['camera']}",
        f"- overlay space: {mode['overlay_space']}",
        f"- horizon clipping: {mode['horizon_clipping']}",
        f"- basemap target: {mode['basemap_target']}",
        f"- lod strategy: {mode['lod_strategy']}",
        f"- shared static layers: {', '.join(mode['shared_layers'])}",
        f"- mode-specific layers: {', '.join(mode['mode_specific_layers'])}",
        "",
        "Rule: provider data stays in source coordinates; projection adapters convert to renderer input.",
        "Rule: Datashader receives screen-space data for globe mode, and projected planar data for planar modes.",
    ]
    return "\n".join(lines)


class DatashaderSamplingPolicy:
    LOD_BUDGETS = {
        "global": 250_000,
        "continental": 500_000,
        "regional": 900_000,
        "local": 1_250_000,
    }

    def decision(self, records: int, lod: str, user_scale: float = 1.0, realtime: bool = True) -> dict:
        records = max(0, int(records))
        budget = int(self.LOD_BUDGETS.get(lod, self.LOD_BUDGETS["global"]))
        user_scale = max(0.05, float(user_scale))
        effective_budget = max(1, int(budget * user_scale))
        if not realtime:
            effective_budget = max(effective_budget, records)
        fraction = 1.0 if records <= effective_budget else effective_budget / max(1, records)
        return {
            "lod": lod,
            "records": records,
            "base_budget": budget,
            "effective_budget": effective_budget,
            "sample_fraction": max(0.001, min(1.0, fraction)),
            "strategy": "aggregate-all" if fraction >= 1.0 else "pre-sample-then-aggregate",
            "realtime": realtime,
        }

    def text(self, ais_records: int, aircraft_records: int, lod: str, ais_scale: float, aircraft_scale: float, mode: str) -> str:
        realtime = mode == "realtime"
        ais = self.decision(ais_records, lod, ais_scale, realtime)
        aircraft = self.decision(aircraft_records, lod, aircraft_scale, realtime)
        lines = [
            "Datashader sampling policy",
            "",
            f"- mode: {mode}",
            f"- lod: {lod}",
            "",
            "AIS:",
            f"- records: {ais['records']}",
            f"- effective budget: {ais['effective_budget']}",
            f"- sample fraction: {ais['sample_fraction']:.4f}",
            f"- strategy: {ais['strategy']}",
            "",
            "ADS-B:",
            f"- records: {aircraft['records']}",
            f"- effective budget: {aircraft['effective_budget']}",
            f"- sample fraction: {aircraft['sample_fraction']:.4f}",
            f"- strategy: {aircraft['strategy']}",
            "",
            "Rule: Datashader should aggregate all points when affordable; sampling is a realtime FPS valve.",
        ]
        return "\n".join(lines)



LAYER_RENDER_COSTS = {
    "globe": 10,
    "clouds": 9,
    "ice": 5,
    "forest": 5,
    "contours": 7,
    "lakes": 6,
    "rivers": 7,
    "borders": 6,
    "territorial_sea": 7,
    "eez": 7,
    "high_seas": 7,
    "ais": 8,
    "aircraft": 8,
    "vehicle_icons": 4,
    "scale": 1,
}


class LayerRenderBudgetPolicy:
    VECTOR_LAYER_IDS = {"lakes", "rivers", "borders", "territorial_sea", "eez", "high_seas"}

    def decision(
        self,
        width: int,
        height: int,
        render_ms: float | None,
        lod: str,
        target_fps: float,
        interaction_active: bool,
        layer_visible: dict | None,
    ) -> dict:
        target_ms = 1000.0 / max(1.0, float(target_fps))
        current_ms = float(render_ms or 0.0)
        visible = layer_visible or {}
        visible_cost = sum(
            LAYER_RENDER_COSTS.get(layer_id, 1)
            for layer_id, enabled in visible.items()
            if enabled
        )
        vector_cost = sum(
            LAYER_RENDER_COSTS.get(layer_id, 1)
            for layer_id in self.VECTOR_LAYER_IDS
            if visible.get(layer_id, False)
        )
        megapixels = max(1.0, (int(width) * int(height)) / 1_000_000.0)
        pressure = current_ms / max(target_ms, 1e-6) if current_ms > 0.0 else 0.0
        heavy_canvas = megapixels >= 3.0
        over_budget = current_ms > target_ms * 1.08 if current_ms > 0.0 else False
        defer_vector_overlays = bool(interaction_active and over_budget and vector_cost > 0)
        prefer_static_cache = bool(over_budget and (heavy_canvas or vector_cost >= 12))
        if defer_vector_overlays:
            vector_cache_degrees = 0.45
            vector_cache_zoom_step = 0.025
            vector_point_stride = 5
        elif interaction_active and prefer_static_cache:
            vector_cache_degrees = 0.18
            vector_cache_zoom_step = 0.014
            vector_point_stride = 4
        elif prefer_static_cache:
            vector_cache_degrees = 0.08
            vector_cache_zoom_step = 0.008
            vector_point_stride = 3 if lod in {"global", "continental"} else 2
        elif lod == "global" and heavy_canvas:
            vector_cache_degrees = 0.012
            vector_cache_zoom_step = 0.002
            vector_point_stride = 2
        else:
            vector_cache_degrees = 0.004
            vector_cache_zoom_step = 0.001
            vector_point_stride = 1
        state = "over-budget" if over_budget else "within-budget"
        if current_ms <= 0.0:
            state = "warming-up"
        return {
            "state": state,
            "target_ms": float(target_ms),
            "current_ms": float(current_ms),
            "pressure": float(pressure),
            "megapixels": float(megapixels),
            "visible_cost": int(visible_cost),
            "vector_cost": int(vector_cost),
            "heavy_canvas": bool(heavy_canvas),
            "interaction_active": bool(interaction_active),
            "defer_vector_overlays": bool(defer_vector_overlays),
            "prefer_static_cache": bool(prefer_static_cache),
            "vector_cache_degrees": float(vector_cache_degrees),
            "vector_cache_zoom_step": float(vector_cache_zoom_step),
            "vector_point_stride": int(vector_point_stride),
            "lod": str(lod),
        }

    def text(
        self,
        width: int,
        height: int,
        render_ms: float | None,
        lod: str,
        target_fps: float,
        interaction_active: bool,
        layer_visible: dict | None,
    ) -> str:
        decision = self.decision(width, height, render_ms, lod, target_fps, interaction_active, layer_visible)
        lines = [
            "Render budget policy",
            "",
            f"- state: {decision['state']}",
            f"- target: {decision['target_ms']:.2f} ms/frame",
            f"- current: {decision['current_ms']:.2f} ms/frame",
            f"- pressure: {decision['pressure']:.2f}x",
            f"- canvas: {decision['megapixels']:.2f} MP",
            f"- visible layer cost: {decision['visible_cost']}",
            f"- vector layer cost: {decision['vector_cost']}",
            f"- interaction active: {decision['interaction_active']}",
            f"- defer vector overlays while dragging: {decision['defer_vector_overlays']}",
            f"- prefer static/vector cache: {decision['prefer_static_cache']}",
            f"- vector camera quantum: {decision['vector_cache_degrees']:.3f} deg / zoom {decision['vector_cache_zoom_step']:.4f}",
            f"- vector point stride: every {decision['vector_point_stride']} point(s)",
            "",
            "Rule: while dragging and over budget, keep the last vector overlay frame and recompute it after interaction settles.",
        ]
        return "\n".join(lines)


class PointOverlayBudgetPolicy:
    def decision(
        self,
        layer: str,
        point_count: int,
        width: int,
        height: int,
        render_ms: float | None,
        lod: str,
        target_fps: float,
        interaction_active: bool,
    ) -> dict:
        target_ms = 1000.0 / max(1.0, float(target_fps))
        current_ms = float(render_ms or 0.0)
        count = max(0, int(point_count))
        megapixels = max(1.0, (int(width) * int(height)) / 1_000_000.0)
        pressure = current_ms / max(target_ms, 1e-6) if current_ms > 0.0 else 0.0
        over_budget = current_ms > target_ms * 1.08 if current_ms > 0.0 else False
        dense = count >= 75_000
        very_dense = count >= 250_000
        sample_ratio_cap = 1.0
        reason = "full-quality"
        if interaction_active and over_budget:
            if very_dense:
                sample_ratio_cap = 0.10
            elif dense:
                sample_ratio_cap = 0.18
            else:
                sample_ratio_cap = 0.35
            reason = "drag-over-budget"
        elif interaction_active and megapixels >= 3.0:
            sample_ratio_cap = 0.40 if dense else 0.65
            reason = "drag-large-canvas"
        elif over_budget and very_dense:
            sample_ratio_cap = 0.22
            reason = "steady-over-budget-very-dense"
        elif over_budget and dense:
            sample_ratio_cap = 0.35
            reason = "steady-over-budget-dense"
        elif lod == "global" and megapixels >= 4.0 and dense:
            sample_ratio_cap = 0.55
            reason = "global-large-canvas"
        return {
            "layer": str(layer),
            "point_count": int(count),
            "target_ms": float(target_ms),
            "current_ms": float(current_ms),
            "pressure": float(pressure),
            "megapixels": float(megapixels),
            "interaction_active": bool(interaction_active),
            "over_budget": bool(over_budget),
            "dense": bool(dense),
            "very_dense": bool(very_dense),
            "sample_ratio_cap": float(max(0.01, min(sample_ratio_cap, 1.0))),
            "reason": reason,
            "lod": str(lod),
        }

    def text(
        self,
        decisions: dict,
    ) -> str:
        lines = [
            "Point overlay budget policy",
            "",
            "Rule: AIS/ADS-B stay screen-space correct while interaction lowers sample ratio under pressure.",
        ]
        for layer, decision in decisions.items():
            lines.extend(
                [
                    "",
                    f"[{layer}]",
                    f"- points: {int(decision.get('point_count', 0)):,}",
                    f"- reason: {decision.get('reason', 'unknown')}",
                    f"- pressure: {float(decision.get('pressure', 0.0)):.2f}x",
                    f"- sample ratio cap: {float(decision.get('sample_ratio_cap', 1.0)):.2f}",
                    f"- interaction active: {bool(decision.get('interaction_active', False))}",
                ]
            )
        return "\n".join(lines)

class AdaptiveRenderQualityPolicy:
    def decision(self, width: int, height: int, render_ms: float | None, lod: str, target_fps: float = 30.0) -> dict:
        width = max(1, int(width))
        height = max(1, int(height))
        pixels = width * height
        target_ms = 1000.0 / max(1.0, float(target_fps))
        render_ms = None if render_ms is None else max(0.0, float(render_ms))
        pressure = 1.0 if render_ms is None else render_ms / target_ms
        if pressure <= 1.15:
            scale = 1.0
            overlay_budget = "full"
        elif pressure <= 2.0:
            scale = 0.85
            overlay_budget = "reduced overlays"
        elif pressure <= 4.0:
            scale = 0.70
            overlay_budget = "sample realtime overlays"
        else:
            scale = 0.55
            overlay_budget = "aggressive realtime sampling"
        if pixels >= 6_000_000 and scale > 0.85:
            scale = 0.85
            overlay_budget = "large-display guardrail"
        return {
            "width": width,
            "height": height,
            "pixels": pixels,
            "lod": lod,
            "render_ms": render_ms,
            "target_fps": float(target_fps),
            "target_ms": target_ms,
            "pressure": pressure,
            "suggested_render_scale": scale,
            "overlay_budget": overlay_budget,
        }

    def text(self, width: int, height: int, render_ms: float | None, lod: str, target_fps: float = 30.0) -> str:
        decision = self.decision(width, height, render_ms, lod, target_fps)
        render_ms_text = "unknown" if decision["render_ms"] is None else f"{decision['render_ms']:.2f} ms"
        lines = [
            "Adaptive render quality policy",
            "",
            f"- canvas: {decision['width']} x {decision['height']}",
            f"- pixels: {decision['pixels']:,}",
            f"- lod: {decision['lod']}",
            f"- last render: {render_ms_text}",
            f"- target fps: {decision['target_fps']:.1f}",
            f"- pressure: {decision['pressure']:.2f}x",
            f"- suggested render scale: {decision['suggested_render_scale']:.2f}",
            f"- overlay budget: {decision['overlay_budget']}",
            "",
            "Rule: this policy reports recommendations only; it does not silently degrade scientific output.",
        ]
        return "\n".join(lines)


MODULE_SPLIT_BLUEPRINT = [
    {
        "module": "render_core/taichi_globe.py",
        "move_first": ["TaichiGlobeRenderer", "TaichiProceduralCloudOverlay", "terrain/ocean/ice/forest shader constants"],
        "imports_allowed": ["numpy", "taichi", "math"],
        "imports_forbidden": ["PyQt", "vispy", "datashader", "sqlalchemy", "urllib"],
        "contract": "Consumes normalized raster/mask arrays and scalar render parameters; returns RGBA frame and globe mask.",
    },
    {
        "module": "projection/globe_projection.py",
        "move_first": ["project_ais_to_screen", "project_aircraft_to_screen", "scale_bar_geometry", "BasemapLODManager"],
        "imports_allowed": ["numpy", "math"],
        "imports_forbidden": ["PyQt", "taichi kernel state", "database clients"],
        "contract": "Owns camera, projection, horizon clipping, km/px, and projection-aware LOD decisions.",
    },
    {
        "module": "data_sources/hydrology_provider.py",
        "move_first": ["HYDROLOGY_SPECS", "HydrologyLODSourcePolicy", "hydrology manifest builders"],
        "imports_allowed": ["json", "pathlib", "urllib", "pandas optional"],
        "imports_forbidden": ["PyQt", "vispy", "taichi"],
        "contract": "Loads lakes/rivers, caches manifests, normalizes geometry to lon/lat line arrays.",
    },
    {
        "module": "data_sources/maritime_boundary_provider.py",
        "move_first": ["BOUNDARY_SPECS", "Marine Regions WFS URL helpers", "boundary manifest builders"],
        "imports_allowed": ["json", "pathlib", "urllib"],
        "imports_forbidden": ["PyQt", "vispy", "taichi"],
        "contract": "Loads borders/territorial sea/EEZ/high seas and reports version/license/projection metadata.",
    },
    {
        "module": "data_sources/ocean_condition_provider.py",
        "move_first": ["OceanConditionProvider", "normalize_ocean_condition_frame", "OCEAN_CONDITION_SCHEMA_TEXT"],
        "imports_allowed": ["json", "pathlib", "pandas", "urllib"],
        "imports_forbidden": ["PyQt", "vispy", "taichi"],
        "contract": "Normalizes ocean condition feeds into wave_strength/roughness/foam/time fields.",
    },
    {
        "module": "overlays/datashader_points.py",
        "move_first": ["AISDatashaderOverlay", "AircraftDatashaderOverlay", "ForestEventDatashaderOverlay"],
        "imports_allowed": ["numpy", "pandas", "datashader"],
        "imports_forbidden": ["PyQt", "taichi", "database clients"],
        "contract": "Consumes projected screen-space dataframes and returns transparent RGBA overlays.",
    },
    {
        "module": "contracts/project_handoff.py",
        "move_first": ["project_handoff_snapshot", "provider manifest decision helpers", "renderer_data_contract_text"],
        "imports_allowed": ["json", "datetime", "pathlib"],
        "imports_forbidden": ["PyQt", "vispy", "taichi kernels", "provider network downloads"],
        "contract": "Builds serializable handoff snapshots that describe provider decisions, render inputs, policies, and split boundaries.",
    },
    {
        "module": "contracts/provider_manifests.py",
        "move_first": ["collect_provider_manifest_bundle", "dedupe_provider_manifests", "write_provider_manifest_bundle"],
        "imports_allowed": ["json", "datetime", "pathlib"],
        "imports_forbidden": ["PyQt", "vispy", "taichi kernels", "network downloads"],
        "contract": "Collects source/cache/schema/license manifests for provider split and cache governance.",
    },
    {
        "module": "qt_ui/main_window.py",
        "move_first": ["QtHybridWindow", "layer dialogs", "timeline dock", "toolbar ports"],
        "imports_allowed": ["PyQt", "vispy"],
        "imports_forbidden": ["provider download internals", "taichi kernels"],
        "contract": "Controls state, asks controller for renders, and displays provider/runtime summaries.",
    },
]


def module_split_blueprint_text() -> str:
    lines = [
        "Module split blueprint",
        "",
        "Goal: keep the current single-file prototype usable while making the next split mechanical and low-risk.",
        "",
    ]
    for item in MODULE_SPLIT_BLUEPRINT:
        lines.append(f"- {item['module']}")
        lines.append(f"  move first: {', '.join(item['move_first'])}")
        lines.append(f"  allowed imports: {', '.join(item['imports_allowed'])}")
        lines.append(f"  forbidden imports: {', '.join(item['imports_forbidden'])}")
        lines.append(f"  contract: {item['contract']}")
        lines.append("")
    lines.extend([
        "Split order:",
        "1. Move pure data/provider constants and manifest builders first.",
        "2. Move projection helpers next because they are shared by Datashader and scale bar.",
        "3. Move Datashader overlays after projection contracts are stable.",
        "4. Move handoff/contracts helpers before splitting UI so both old and new structures can be compared.",
        "5. Move Taichi render core only after input arrays and scalar parameters are explicit.",
        "6. Move Qt last; UI should become an orchestration shell, not the owner of data logic.",
    ])
    return "\n".join(lines)


def provider_interface_spec_text() -> str:
    return "\n".join([
        "Provider interface spec",
        "",
        "Required methods for future provider classes:",
        "- provider_id() -> str",
        "- manifest(lod: str) -> dict",
        "- load(lod: str, force: bool = False) -> object",
        "- normalize(raw: object) -> object",
        "- status_text() -> str",
        "",
        "Renderer input rules:",
        "- vector providers return lon/lat line arrays or geometry records, never Qt objects.",
        "- point-feed providers return normalized pandas DataFrames before projection.",
        "- raster providers return numpy arrays plus projection metadata.",
        "- ocean providers return scalar fields wave_strength/roughness/foam/time.",
        "",
        "This keeps Taichi, Datashader, VisPy, and Qt coupled only through explicit data contracts.",
    ])


def renderer_data_contract_text() -> str:
    return "\n".join([
        "Renderer/data contract map",
        "",
        "Current prototype rule:",
        "- data providers return normalized arrays/dataframes/geometries plus a cache manifest.",
        "- projection adapters convert source coordinates to renderer coordinates.",
        "- Datashader receives projected screen-space points for globe mode.",
        "- Taichi receives dense raster/mask arrays and scalar material controls only.",
        "- Qt owns interaction state and controls; it should not own provider internals.",
        "",
        "Extraction candidates:",
        "- render_core/taichi_globe.py: TaichiGlobeRenderer, TaichiProceduralCloudOverlay, terrain/ocean/ice material kernels.",
        "- projection/globe_projection.py: project_ais_to_screen, scale_bar_geometry, BasemapLODManager.",
        "- projection/globe_projection.py: project_aircraft_to_screen shares the same visible-hemisphere clipping contract.",
        "- overlays/datashader_points.py: AISDatashaderOverlay, AircraftDatashaderOverlay, DatashaderSamplingPolicy, AdaptiveRenderQualityPolicy.",
        "- data_sources/hydrology_provider.py: HYDROLOGY_SPECS, HydrologyLODSourcePolicy, GeoJSON loading helpers.",
        "- data_sources/maritime_boundary_provider.py: BOUNDARY_SPECS, BoundaryLODSourcePolicy, Marine Regions/Natural Earth adapters.",
        "- data_sources/ocean_condition_provider.py: OCEAN_PROVIDER_REGISTRY, OceanConditionProvider, OceanMaterialPolicy, normalize_ocean_condition_frame.",
        "- contracts/project_handoff.py: project_handoff_snapshot and provider/cache manifest decision helpers.",
        "- contracts/provider_manifests.py: collect_provider_manifest_bundle, dedupe_provider_manifests, write_provider_manifest_bundle.",
        "- qt_ui/main_window.py: QtHybridWindow and layer/timeline dialogs.",
        "",
        "Do not split before these contracts stay stable for one runtime pass.",
    ])


def ui_localization_status_text() -> str:
    return "\n".join([
        "介面中文化狀態",
        "",
        "已整理區塊：",
        "- 模式切換：靜態 / 時間序列 / 即時。",
        "- 投影切換：3D 地球 / 麥卡托 / 等距圓柱 / 極區。",
        "- 風格切換：科學 / 戰術 / 航海 / 羊皮紙，未完成風格標示施工中 🚧。",
        "- 工具列：輸出截圖、輸出影片、資料來源、解耦計畫、專案狀態、資料來源總覽。",
        "- 主控面板：狀態、圖層說明、選取資訊、載具 icon、效能控制。",
        "- 狀態列：visible/rendered/render/zoom/flip lon/lat 已轉成中文概念。",
        "",
        "仍保留英文的原因：",
        "- provider id、schema、module path、CLI argument、renderer input 是工程契約，保留英文比較安全。",
        "- AIS、ADS-B、LOD、FPS、Qt、Taichi、Datashader、VisPy 是技術名詞，保留原文。",
        "",
        "後續清理規則：",
        "- 使用者可見按鈕與說明優先中文化。",
        "- contract / manifest / source id 保留英文。",
        "- 未開放功能在標題或說明中標示施工中 🚧。",
    ])



SYMBOL_EXTRACTION_MAP = [
    {
        "target": "taichi_earth/contracts/provider_manifests.py",
        "owner": "data-contracts",
        "symbols": [
            "PROVIDER_CACHE_MANIFEST_FIELDS",
            "build_provider_cache_manifest",
            "provider_manifest_templates",
            "provider_manifest_templates_text",
            "dedupe_provider_manifests",
            "collect_provider_manifest_bundle",
            "provider_manifest_bundle_text",
            "write_provider_manifest_bundle",
            "write_provider_manifest_bundle_text",
        ],
        "inputs": ["provider registry dictionaries", "cache paths", "source metadata"],
        "outputs": ["manifest dictionaries", "manifest text", "manifest json files"],
        "forbidden_dependencies": ["Qt", "VisPy", "Taichi kernels", "Datashader canvas"],
        "notes": "Keep this module pure-Python so every provider can report provenance before rendering starts.",
    },
    {
        "target": "taichi_earth/contracts/project_handoff.py",
        "owner": "architecture-contracts",
        "symbols": [
            "project_handoff_snapshot",
            "project_handoff_snapshot_text",
            "write_project_handoff_snapshot",
            "write_project_handoff_snapshot_text",
            "renderer_data_contract_text",
            "module_split_blueprint_text",
            "architecture_split_plan_text",
            "module_split_readiness_text",
            "symbol_extraction_map_text",
        ],
        "inputs": ["feature status", "provider manifests", "module boundaries", "symbol extraction map"],
        "outputs": ["human-readable handoff", "handoff json"],
        "forbidden_dependencies": ["Qt widgets", "render buffers", "network fetch at import time"],
        "notes": "This remains the documentation spine while the monolith is being split.",
    },
    {
        "target": "taichi_earth/projection/globe_projection.py",
        "owner": "projection-core",
        "symbols": [
            "project_ais_to_screen",
            "project_aircraft_to_screen",
            "rotate_view_to_world",
            "scale_bar_geometry",
            "BasemapLODManager",
            "PROJECTION_PIPELINE_MODES",
        ],
        "inputs": ["lat/lon/altitude tables", "camera yaw/pitch/roll", "viewport size", "zoom"],
        "outputs": ["screen-space point tables", "visibility masks", "scale bar geometry", "LOD decisions"],
        "forbidden_dependencies": ["Qt controls", "database connectors", "provider download code"],
        "notes": "This is the shared math layer for globe, Mercator, and future map projections.",
    },
    {
        "target": "taichi_earth/overlays/datashader_points.py",
        "owner": "screen-space-overlays",
        "symbols": [
            "AISDatashaderOverlay",
            "AircraftDatashaderOverlay",
            "DatashaderSamplingPolicy",
            "AdaptiveRenderQualityPolicy",
            "alpha_compose",
            "alpha_compose_transparent",
        ],
        "inputs": ["projected visible point tables", "sampling ratio", "viewport size", "color mode"],
        "outputs": ["RGBA overlay images", "render statistics"],
        "forbidden_dependencies": ["Taichi kernels", "Qt widgets", "raw unprojected geodetic clipping"],
        "notes": "Datashader should only see screen-space points after hemisphere and projection clipping.",
    },
    {
        "target": "taichi_earth/overlays/vector_lines.py",
        "owner": "screen-space-vector-overlays",
        "symbols": [
            "GeoVectorLineOverlay",
            "geojson_to_lines",
            "_append_geojson_geometry_lines",
            "load_geojson_lines",
            "polyline_screen_distance",
        ],
        "inputs": ["GeoJSON line/polygon boundaries", "projection callback", "viewport size"],
        "outputs": ["RGBA line overlay", "hover hit-test result"],
        "forbidden_dependencies": ["Qt layer panel state", "AIS/ADS-B tables", "Taichi renderer internals"],
        "notes": "Borders, EEZ, territorial seas, rivers, and future tactical vectors should share this path.",
    },
    {
        "target": "taichi_earth/data_sources/realtime_feeds.py",
        "owner": "realtime-feeds",
        "symbols": [
            "AISSource",
            "AircraftSource",
            "normalize_ais_frame",
            "normalize_aircraft_frame",
            "filter_recent",
            "dataframe_from_text",
            "dataframe_from_json",
        ],
        "inputs": ["WebSocket/HTTP payloads", "database rows", "CSV/JSON files"],
        "outputs": ["normalized pandas DataFrame", "source status", "refresh timing"],
        "forbidden_dependencies": ["Qt widgets", "Datashader canvas", "Taichi kernels"],
        "notes": "Feeder modules own truth ingestion; renderer modules only receive normalized frames.",
    },
    {
        "target": "taichi_earth/data_sources/hydrology_provider.py",
        "owner": "static-geodata",
        "symbols": [
            "HYDROLOGY_SPECS",
            "HydrologyLODSourcePolicy",
            "default_hydrology_url",
            "load_hydrology_lines",
            "hydrology_provider_decisions_text",
            "hydrology_layer_status_text",
        ],
        "inputs": ["LOD decision", "manual URL/file override", "cache directory"],
        "outputs": ["lake/river vector line sets", "provider decision text"],
        "forbidden_dependencies": ["Qt widget instances", "Taichi fields", "AIS/ADS-B runtime state"],
        "notes": "Hydrology has to support multi-resolution sources without changing renderer code.",
    },
    {
        "target": "taichi_earth/data_sources/maritime_boundary_provider.py",
        "owner": "legal-geodata",
        "symbols": [
            "BOUNDARY_SPECS",
            "BoundaryLODSourcePolicy",
            "marine_regions_wfs_geojson_url",
            "default_boundary_url",
            "boundary_provider_decisions_text",
            "boundary_layer_status_text",
        ],
        "inputs": ["boundary kind", "provider tier", "cache directory", "manual override"],
        "outputs": ["country borders", "territorial sea", "EEZ", "high seas boundary overlays"],
        "forbidden_dependencies": ["render loop mutation", "Qt drag/drop state", "vehicle feeds"],
        "notes": "Legal/scientific layers need provenance and source-tier reporting before visual polish.",
    },
    {
        "target": "taichi_earth/data_sources/ocean_condition_provider.py",
        "owner": "ocean-conditions",
        "symbols": [
            "OCEAN_PROVIDER_REGISTRY",
            "OCEAN_CONDITION_SCHEMA_TEXT",
            "OCEAN_CONDITION_ALIASES",
            "OceanConditionProvider",
            "OceanMaterialPolicy",
            "normalize_ocean_condition_frame",
        ],
        "inputs": ["manual state", "file/url source", "NOAA/HYCOM/Copernicus adapter payloads"],
        "outputs": ["normalized ocean condition frame", "Taichi ocean material parameters"],
        "forbidden_dependencies": ["Qt controls", "Datashader overlays", "hard-coded provider URLs in renderer"],
        "notes": "This is the bridge that lets Taichi ocean material respond to real sea-state data later.",
    },
    {
        "target": "taichi_earth/render_core/taichi_globe.py",
        "owner": "taichi-render-core",
        "symbols": [
            "TaichiGlobeRenderer",
            "TaichiProceduralCloudOverlay",
            "init_taichi",
            "make_topography_texture",
            "terrain_color",
            "color_from_norm",
        ],
        "inputs": ["topography arrays", "land/sea masks", "camera state", "ocean material params", "layer toggles"],
        "outputs": ["base globe RGBA frame", "depth/visibility support fields", "procedural cloud/ice/ocean shading"],
        "forbidden_dependencies": ["Qt widget construction", "network/database IO", "Datashader canvas creation"],
        "notes": "Taichi should own dense pixel work and procedural material simulation, not UI or provider logic.",
    },
    {
        "target": "taichi_earth/ui/qt_main_window.py",
        "owner": "desktop-ui",
        "symbols": [
            "QtHybridWindow",
            "LayerSettingsDialog",
            "show_info_dialog",
            "show_text_dialog",
            "create_mode_toolbar",
            "create_timeline_bar",
        ],
        "inputs": ["controller public methods", "status text", "layer metadata"],
        "outputs": ["Photoshop-like panels", "mode switching", "settings dialogs", "export command ports"],
        "forbidden_dependencies": ["direct provider downloads", "direct Taichi field writes", "hidden renderer state mutation"],
        "notes": "Qt should become a thin operator console over controller methods, not the data/rendering owner.",
    },
    {
        "target": "taichi_earth/controller/hybrid_controller.py",
        "owner": "orchestration",
        "symbols": [
            "HybridRenderController",
            "render_if_needed",
            "refresh_ais_if_due",
            "refresh_aircraft_if_due",
            "set_layer_order",
            "set_data_mode",
            "runtime_status_text",
        ],
        "inputs": ["UI commands", "provider frames", "camera state", "render settings"],
        "outputs": ["composited frame", "status text", "selected feature info", "dirty flags"],
        "forbidden_dependencies": ["Qt widget subclasses", "provider-specific credentials in source", "blocking downloads inside render loop"],
        "notes": "Controller remains the seam between UI, providers, projection, Datashader overlays, and Taichi core.",
    },
]


def symbol_extraction_map_text() -> str:
    lines = [
        "Symbol extraction map",
        "",
        "Purpose: split the monolith by stable symbol groups instead of moving code by visual guesswork.",
        "Rule: providers ingest data, projection clips/projects data, overlays rasterize screen-space data, Taichi renders dense globe materials, Qt only controls the system.",
    ]
    for item in SYMBOL_EXTRACTION_MAP:
        lines.append("")
        lines.append(f"[{item['target']}]")
        lines.append(f"Owner: {item['owner']}")
        lines.append("Symbols:")
        for symbol in item["symbols"]:
            lines.append(f"  - {symbol}")
        lines.append("Inputs: " + ", ".join(item["inputs"]))
        lines.append("Outputs: " + ", ".join(item["outputs"]))
        lines.append("Forbidden dependencies: " + ", ".join(item["forbidden_dependencies"]))
        lines.append("Notes: " + item["notes"])
    return "\n".join(lines)

DECOUPLING_MODULE_BOUNDARIES = [
    ("render_core", "TaichiGlobeRenderer, ocean material, ice/forest/terrain shading."),
    ("projection", "3D globe, Mercator, Polar, screen-space clipping, scale bar calculations."),
    ("data_sources", "AIS, ADS-B, forest events, ocean condition providers, database and WebSocket feeders."),
    ("vector_layers", "Borders, EEZ, rivers, lakes, HydroRIVERS/MERIT/OSM loading and LOD."),
    ("overlays", "Datashader points, vector lines, icons, hover highlight, and layer composition."),
    ("qt_ui", "QDock layer panel, timeline, mode switch, settings dialogs."),
    ("style_profiles", "Scientific, tactical, nautical, parchment palettes, symbols, line styles, and post-processing."),
]


def architecture_split_plan_text() -> str:
    lines = ["Decoupling module boundaries"]
    for name, description in DECOUPLING_MODULE_BOUNDARIES:
        lines.append(f"- {name}: {description}")
    return "\n".join(lines)


RUNTIME_CONFIGURATION_CONTRACT = {
    "render_core": [
        "width",
        "height",
        "ti_arch",
        "topo_step",
        "bump_scale",
        "sea_level_m",
        "ocean_material",
        "ocean_wave_strength",
        "ocean_roughness",
        "ocean_foam",
        "ocean_material_scale",
        "ocean_responsive",
    ],
    "projection": [
        "map_projection",
        "flip_longitude",
        "flip_latitude",
        "ais_horizon_eps",
        "aircraft_horizon_eps",
        "aircraft_altitude_exaggeration",
        "scale_bar",
        "scale_bar_x",
        "scale_bar_y",
        "flight_speed_deg",
    ],
    "data_sources": [
        "ais_url",
        "ais_file",
        "ais_db_url",
        "aircraft_url",
        "aircraft_file",
        "aircraft_db_url",
        "ocean_condition_source",
        "ocean_condition_file",
        "ocean_condition_url",
        "ocean_provider_lat",
        "ocean_provider_lon",
        "hydrology_source_mode",
    ],
    "vector_layers": [
        "lake_file",
        "lake_url",
        "river_file",
        "river_url",
        "border_file",
        "territorial_sea_file",
        "eez_file",
        "high_seas_file",
        "hydrolakes_file",
        "hydrorivers_file",
        "merit_hydro_file",
        "osm_water_file",
        "osm_waterways_file",
    ],
    "overlays": [
        "color_by",
        "point_px",
        "ais_sample_ratio",
        "aircraft_color_by",
        "aircraft_point_px",
        "aircraft_sample_ratio",
        "vehicle_icons",
        "icon_max_count",
        "icon_pick_radius",
    ],
    "style_profiles": [
        "style_profile",
    ],
    "qt_ui": [
        "ui",
        "data_mode",
        "target_fps",
        "adaptive_sampling",
        "fps_log",
    ],
}


def runtime_configuration_contract_text(args=None) -> str:
    choices = {
        "style_profile": ["scientific", "nautical", "tactical", "parchment"],
        "ocean_condition_source": ["manual", "file", "url", "noaa_ww3", "noaa", "hycom", "copernicus", "local_grid"],
        "hydrology_source_mode": ["lod", "manual", "strict"],
        "data_mode": ["static", "timeseries", "realtime"],
    }
    lines = [
        "Runtime configuration contract",
        "",
        "Purpose: keep CLI/env/Qt controls owned by the same future module that consumes the value.",
        "Rule: data provider modules may read source settings, but render_core should only receive normalized arrays and scalar material values.",
        "",
    ]
    for module, names in RUNTIME_CONFIGURATION_CONTRACT.items():
        lines.append(f"[{module}]")
        for name in names:
            if args is None:
                lines.append(f"- {name}")
            else:
                value = getattr(args, name, None)
                suffix = f" choices={choices[name]}" if name in choices else ""
                lines.append(f"- {name}: {value}{suffix}")
        lines.append("")
    return "\n".join(lines).rstrip()


PROJECT_GOAL_MILESTONES = [
    {
        "id": "hydrology_basic",
        "label": "水文圖層 basic",
        "state": "port-wired",
        "evidence": [
            "lakes/rivers vector overlays",
            "hydrology LOD source policy",
            "strict/manual/LOD source modes",
            "download/cache progress hooks",
        ],
        "remaining": [
            "runtime visual pass",
            "provider-specific schema validation",
            "higher-resolution scientific hydrology datasets",
        ],
    },
    {
        "id": "lod_hooks",
        "label": "LOD hook",
        "state": "contract-wired",
        "evidence": [
            "basemap LOD decision",
            "hydrology render LOD profile",
            "boundary/vector cache camera key",
            "adaptive render and point overlay budgets",
        ],
        "remaining": [
            "multi-basemap tile/source switching",
            "projection-specific LOD tuning",
            "runtime performance calibration",
        ],
    },
    {
        "id": "taichi_ocean_material",
        "label": "Taichi 海洋材質控制入口",
        "state": "port-wired",
        "evidence": [
            "OceanConditionProvider normalization",
            "OceanSpatialSamplingPolicy lat/lon sampling",
            "OceanMaterialPolicy scalar output",
            "Qt controls for source, refresh, and sampling point",
        ],
        "remaining": [
            "true gridded ocean adapter",
            "sea-state time interpolation",
            "runtime visual/performance pass",
        ],
    },
    {
        "id": "decoupling_preparation",
        "label": "後續解耦準備",
        "state": "contract-wired",
        "evidence": [
            "module split blueprint",
            "symbol extraction map",
            "runtime configuration contract",
            "provider manifest bundle",
            "project handoff snapshot",
        ],
        "remaining": [
            "first physical module extraction",
            "import boundary enforcement",
            "one runtime pass after split",
        ],
    },
]


def project_goal_milestones_snapshot() -> list[dict]:
    return [dict(item) for item in PROJECT_GOAL_MILESTONES]


def project_goal_milestones_text() -> str:
    lines = [
        "Project goal milestones",
        "",
        "This is a progress map, not a completion claim. Runtime verification has not been run unless explicitly requested.",
        "",
    ]
    for item in PROJECT_GOAL_MILESTONES:
        lines.append(f"[{item['id']}] {item['label']} | {item['state']}")
        lines.append("- evidence:")
        for evidence in item["evidence"]:
            lines.append(f"  - {evidence}")
        lines.append("- remaining:")
        for remaining in item["remaining"]:
            lines.append(f"  - {remaining}")
        lines.append("")
    return "\n".join(lines).rstrip()


DECOUPLING_EXTRACTION_UNITS = [
    {
        "id": "contracts_provider_manifests",
        "target": "taichi_earth/contracts/provider_manifests.py",
        "stage": "first-safe-extract",
        "move": [
            "build_provider_cache_manifest",
            "collect_provider_manifest_bundle helpers",
            "provider manifest text helpers",
        ],
        "keep_out": ["PyQt", "VisPy", "Taichi kernels", "Datashader canvas", "network fetch at import time"],
        "inputs": ["plain dict/list metadata", "cache path strings", "LOD labels"],
        "outputs": ["serializable manifest dicts", "manifest bundle JSON text"],
        "rollback": "copy pure helpers back into monolith; no renderer state should depend on module globals",
    },
    {
        "id": "style_profiles",
        "target": "taichi_earth/style_profiles.py",
        "stage": "second-safe-extract",
        "move": [
            "STYLE_PROFILE_REGISTRY",
            "STYLE_RENDERER_ENTRIES",
            "DATASHADER_STYLE_CMAPS",
            "resolve_style_renderer_entry",
            "resolve_style_overlay_intent",
            "resolve_datashader_style_cmaps",
            "apply_style_profile",
        ],
        "keep_out": ["Qt widgets", "provider IO", "database clients"],
        "inputs": ["profile id", "RGBA frame", "layer kind/base color"],
        "outputs": ["post-processed RGBA frame", "palette/tint/material intent dicts"],
        "rollback": "restore pure functions/constants only; render loop calls remain unchanged",
    },
    {
        "id": "projection_lod_pipeline",
        "target": "taichi_earth/projection/lod_pipeline.py",
        "stage": "third-safe-extract",
        "move": [
            "BasemapLODManager",
            "HydrologyRenderLODProfile",
            "LayerRenderBudgetPolicy",
            "PointOverlayBudgetPolicy",
            "LOD hook snapshot shape",
        ],
        "keep_out": ["Qt widgets", "provider download code", "Taichi fields"],
        "inputs": ["km_per_pixel", "projection", "viewport size", "last render ms", "record counts"],
        "outputs": ["LOD/provider decisions", "render budgets", "point/vector simplification hints"],
        "rollback": "keep decision classes pure and re-import from monolith if runtime pass fails",
    },
    {
        "id": "hydrology_provider",
        "target": "taichi_earth/data_sources/hydrology_provider.py",
        "stage": "after-contracts",
        "move": [
            "HYDROLOGY_SPECS",
            "HYDROLOGY_STRICT_PROVIDER_PORTS",
            "HydrologyLODSourcePolicy",
            "HydrologyScientificStrictnessPolicy",
            "resolve_hydrology_strict_provider",
        ],
        "keep_out": ["Qt widgets", "Taichi renderer internals", "AIS/ADS-B runtime state"],
        "inputs": ["args-like config", "LOD label", "layer id", "cache directory"],
        "outputs": ["GeoJSON source decision", "provider manifest", "strictness report"],
        "rollback": "do not move GeoVectorLineOverlay with provider decisions; vector rendering stays separate",
    },
    {
        "id": "ocean_condition_provider",
        "target": "taichi_earth/data_sources/ocean_condition_provider.py",
        "stage": "after-contracts",
        "move": [
            "OCEAN_PROVIDER_REGISTRY",
            "OceanConditionProvider",
            "OceanSpatialSamplingPolicy",
            "normalize_ocean_condition_frame",
            "select_ocean_condition_sample_frame",
        ],
        "keep_out": ["Taichi kernels", "Qt widgets", "VisPy scene objects"],
        "inputs": ["source config", "refresh interval", "sampling lat/lon", "raw JSON/CSV/table data"],
        "outputs": ["normalized scalar condition dict", "normalization report", "spatial sampling decision"],
        "rollback": "OceanMaterialPolicy remains in render_core side until scalar contract is verified",
    },
]


def decoupling_extraction_units_snapshot() -> list[dict]:
    return [dict(item) for item in DECOUPLING_EXTRACTION_UNITS]


def decoupling_extraction_units_text() -> str:
    lines = [
        "Decoupling extraction units",
        "",
        "Purpose: make the first physical split mechanical and reversible.",
        "Rule: extract pure contracts/providers first; move Qt and Taichi render core last.",
        "",
    ]
    for unit in DECOUPLING_EXTRACTION_UNITS:
        lines.append(f"[{unit['id']}] {unit['target']} | {unit['stage']}")
        lines.append("- move:")
        for symbol in unit["move"]:
            lines.append(f"  - {symbol}")
        lines.append(f"- inputs: {', '.join(unit['inputs'])}")
        lines.append(f"- outputs: {', '.join(unit['outputs'])}")
        lines.append(f"- keep out: {', '.join(unit['keep_out'])}")
        lines.append(f"- rollback: {unit['rollback']}")
        lines.append("")
    return "\n".join(lines).rstrip()


PROVIDER_MANIFESTS_MODULE_API = {
    "module": "taichi_earth/contracts/provider_manifests.py",
    "purpose": "Pure serialization contract for source provenance, cache identity, schema, and simplification metadata.",
    "public_api": [
        {
            "name": "build_provider_cache_manifest",
            "signature": "build_provider_cache_manifest(provider_id, source_url, source_version, license_text, lod, cache_path, schema, simplification) -> dict",
            "ownership": "contracts",
            "side_effects": "none",
        },
        {
            "name": "dedupe_provider_manifests",
            "signature": "dedupe_provider_manifests(manifests: list[dict]) -> list[dict]",
            "ownership": "contracts",
            "side_effects": "none",
        },
        {
            "name": "provider_manifest_templates_text",
            "signature": "provider_manifest_templates_text(lod: str) -> str",
            "ownership": "contracts",
            "side_effects": "none",
        },
        {
            "name": "collect_provider_manifest_bundle",
            "signature": "collect_provider_manifest_bundle(controller_like) -> dict",
            "ownership": "controller adapter",
            "side_effects": "reads current controller/provider decisions only",
        },
        {
            "name": "write_provider_manifest_bundle",
            "signature": "write_provider_manifest_bundle(bundle: dict, path: Path) -> str",
            "ownership": "controller adapter",
            "side_effects": "writes one UTF-8 JSON file when explicitly invoked",
        },
    ],
    "must_not_import": ["PyQt", "vispy", "taichi", "datashader", "sqlalchemy"],
    "allowed_imports": ["json", "datetime", "pathlib", "typing"],
    "handoff_rule": "Provider modules return manifests; UI/controller may aggregate and write them, but renderers never mutate them.",
}


def provider_manifests_module_api_snapshot() -> dict:
    return dict(PROVIDER_MANIFESTS_MODULE_API)


def provider_manifests_module_api_text() -> str:
    api = PROVIDER_MANIFESTS_MODULE_API
    lines = [
        "Provider manifests module API",
        "",
        f"- module: {api['module']}",
        f"- purpose: {api['purpose']}",
        f"- allowed imports: {', '.join(api['allowed_imports'])}",
        f"- must not import: {', '.join(api['must_not_import'])}",
        f"- handoff rule: {api['handoff_rule']}",
        "",
        "Public API:",
    ]
    for item in api["public_api"]:
        lines.append(f"- {item['name']}")
        lines.append(f"  signature: {item['signature']}")
        lines.append(f"  ownership: {item['ownership']}")
        lines.append(f"  side effects: {item['side_effects']}")
    return "\n".join(lines)


HYDROLOGY_PROVIDER_MODULE_API = {
    "module": "taichi_earth/data_sources/hydrology_provider.py",
    "purpose": "Own hydrology source selection, strict scientific provenance, provider manifests, and LOD source decisions without owning screen-space rendering.",
    "public_api": [
        {
            "name": "HydrologyLODSourcePolicy",
            "signature": "HydrologyLODSourcePolicy(args_like).decision(lod: str, layer_id: str) -> dict",
            "ownership": "data_sources",
            "side_effects": "none",
        },
        {
            "name": "HydrologyRenderLODProfile",
            "signature": "HydrologyRenderLODProfile().decision(lod: str, layer_id: str) -> dict",
            "ownership": "projection/lod_pipeline",
            "side_effects": "none",
        },
        {
            "name": "HydrologyScientificStrictnessPolicy",
            "signature": "HydrologyScientificStrictnessPolicy(args_like).decision(lod: str, layer_id: str, source_decision: dict) -> dict",
            "ownership": "data_sources",
            "side_effects": "none",
        },
        {
            "name": "resolve_hydrology_strict_provider",
            "signature": "resolve_hydrology_strict_provider(args_like, layer_id: str) -> dict",
            "ownership": "data_sources",
            "side_effects": "none",
        },
        {
            "name": "load_hydrology_geojson",
            "signature": "load_hydrology_geojson(decision: dict, cache_dir: Path, force: bool = False) -> dict",
            "ownership": "data_sources",
            "side_effects": "may read/write provider cache only when explicitly loading",
        },
        {
            "name": "hydrology_dirty_reload_contract_snapshot",
            "signature": "hydrology_dirty_reload_contract_snapshot(controller_like) -> dict",
            "ownership": "controller adapter",
            "side_effects": "reads dirty flag and cache state only",
        },
    ],
    "layers": ["lakes", "rivers"],
    "strict_provider_ports": ["hydrolakes", "hydrorivers", "merit_hydro", "osm_water", "osm_waterways"],
    "must_not_import": ["PyQt", "vispy", "taichi", "datashader", "AIS/ADS-B feed classes"],
    "allowed_imports": ["json", "pathlib", "urllib", "typing", "pandas optional"],
    "handoff_rule": "Hydrology provider returns GeoJSON/source decisions and manifests; vector_lines owns lon/lat to screen-space rendering.",
}


def hydrology_provider_module_api_snapshot() -> dict:
    return dict(HYDROLOGY_PROVIDER_MODULE_API)


def hydrology_provider_module_api_text() -> str:
    api = HYDROLOGY_PROVIDER_MODULE_API
    lines = [
        "Hydrology provider module API",
        "",
        f"- module: {api['module']}",
        f"- purpose: {api['purpose']}",
        f"- layers: {', '.join(api['layers'])}",
        f"- strict provider ports: {', '.join(api['strict_provider_ports'])}",
        f"- allowed imports: {', '.join(api['allowed_imports'])}",
        f"- must not import: {', '.join(api['must_not_import'])}",
        f"- handoff rule: {api['handoff_rule']}",
        "",
        "Public API:",
    ]
    for item in api["public_api"]:
        lines.append(f"- {item['name']}")
        lines.append(f"  signature: {item['signature']}")
        lines.append(f"  ownership: {item['ownership']}")
        lines.append(f"  side effects: {item['side_effects']}")
    return "\n".join(lines)


HYDROLOGY_DIRTY_RELOAD_CONTRACT = [
    {
        "trigger": "manual_layer_reload",
        "entry_point": "reload_hydrology_layer",
        "expected_dirty_flags": ["hydrology_dirty", "overlay_dirty"],
        "provider_scope": ["manual file/url override", "single layer source decision", "GeoJSON load boundary"],
        "cache_policy": "reload replaces the layer overlay object and keeps vector overlay cache ownership in controller adapter.",
        "controller_keeps": ["dirty flags", "GeoVectorLineOverlay construction", "render scheduling"],
    },
    {
        "trigger": "strict_provider_switch",
        "entry_point": "set_hydrology_strict_source",
        "expected_dirty_flags": ["hydrology_dirty", "overlay_dirty"],
        "provider_scope": ["strict provider port selection", "strict metadata/provenance attrs", "GeoJSON load boundary"],
        "cache_policy": "strict source switch reloads the selected layer and leaves cache eviction policy unchanged.",
        "controller_keeps": ["selected strict mode", "dirty flags", "toolbar diagnostics"],
    },
    {
        "trigger": "source_mode_change",
        "entry_point": "set_hydrology_source_mode",
        "expected_dirty_flags": ["hydrology_dirty", "overlay_dirty"],
        "provider_scope": ["lod/manual/strict source decision mode"],
        "cache_policy": "source mode changes mark hydrology overlays dirty; physical cache cleanup is not attempted.",
        "controller_keeps": ["source mode state", "dirty flags", "render scheduling"],
    },
    {
        "trigger": "render_style_control_change",
        "entry_point": "set_hydrology_opacity/set_hydrology_width",
        "expected_dirty_flags": ["hydrology_dirty", "overlay_dirty"],
        "provider_scope": ["none; render params only"],
        "cache_policy": "opacity/width changes force hydrology redraw without touching provider source caches.",
        "controller_keeps": ["render params", "dirty flags", "vector overlay cache key"],
    },
    {
        "trigger": "style_profile_change",
        "entry_point": "set_style_profile",
        "expected_dirty_flags": ["globe_dirty", "overlay_dirty"],
        "provider_scope": ["none; style intent only"],
        "cache_policy": "style_vector_cache_key must separate cached vector overlays by profile while providers remain unchanged.",
        "controller_keeps": ["style profile", "overlay renderer style propagation", "vector overlay cache key"],
    },
]


HYDROLOGY_PROVIDER_EXTRACTION_READINESS_PACKET = {
    "target_file": "taichi_earth/data_sources/hydrology_provider.py",
    "purpose": "Prepare the hydrology source/strictness split while keeping vector rendering, screen-space params, and controller dirty/cache state outside the provider module.",
    "candidate_status": "prepared-not-extracted",
    "move_symbols": [
        "HYDROLOGY_SPECS",
        "HydrologyLODSourcePolicy",
        "HydrologyScientificStrictnessPolicy",
        "resolve_hydrology_strict_provider",
        "load_hydrology_geojson",
        "hydrology_provider_module_api_snapshot",
        "hydrology_provider_module_api_text",
    ],
    "keep_in_controller_adapter": [
        "hydrology_control_snapshot",
        "hydrology_basic_readiness_matrix_snapshot",
        "hydrology_dirty_reload_contract_snapshot",
        "hydrology_dirty_reload_contract_text",
        "hydrology_provider_decisions_text",
        "hydrology_strict_provider_ports_text",
        "_load_hydrology_overlays",
        "_load_single_hydrology_overlay",
        "GeoVectorLineOverlay construction",
        "vector cache ownership and dirty flags",
    ],
    "owned_by_other_modules": [
        "HydrologyRenderLODProfile remains in projection/lod_pipeline.py",
        "build_hydrology_render_params remains in overlays/vector_lines.py",
        "style color resolution remains in style_profiles.py",
    ],
    "allowed_imports": ["json", "pathlib", "urllib", "typing", "pandas optional"],
    "forbidden_imports": ["PyQt", "vispy", "taichi", "datashader", "AIS/ADS-B feed classes", "GeoVectorLineOverlay"],
    "input_contract": [
        "args-like source settings",
        "LOD id",
        "layer id",
        "optional strict file/url overrides",
        "cache directory only at explicit load boundary",
    ],
    "output_contract": [
        "source decision dict",
        "strictness decision dict",
        "provider manifest dict",
        "loaded GeoJSON/line payload at explicit load boundary",
        "no screen-space render params",
        "no overlay object construction",
    ],
    "preconditions": [
        "Hydrology basic readiness is visible from toolbar",
        "LOD pipeline extraction readiness packet keeps HydrologyRenderLODProfile out of provider ownership",
        "Vector lines extraction readiness packet owns render params and overlay rendering",
        "pre-validation evidence plan has been reviewed",
    ],
    "rollback_steps": [
        "restore hydrology source policy and strictness policy inside the monolith",
        "keep hydrology overlay rendering and vector cache code unchanged",
        "disable only hydrology provider extraction readiness diagnostics if toolbar wiring fails",
    ],
}


def hydrology_provider_extraction_readiness_packet_snapshot() -> dict:
    packet = dict(HYDROLOGY_PROVIDER_EXTRACTION_READINESS_PACKET)
    packet["module_api"] = hydrology_provider_module_api_snapshot()
    packet["validation_evidence_plan_ids"] = [
        item["id"] for item in PRE_VALIDATION_EVIDENCE_PLAN
        if item["id"] in {
            "hydrology_basic_diagnostic_gate",
            "lod_hook_diagnostic_gate",
            "small_render_gate",
        }
    ]
    packet["runtime_verification"] = "not-run"
    return packet


def hydrology_provider_extraction_readiness_packet_text() -> str:
    packet = hydrology_provider_extraction_readiness_packet_snapshot()
    lines = [
        "Hydrology provider extraction readiness packet",
        "",
        f"- target file: {packet['target_file']}",
        f"- purpose: {packet['purpose']}",
        f"- status: {packet['candidate_status']}",
        f"- runtime verification: {packet['runtime_verification']}",
        "",
        "Move symbols:",
    ]
    for name in packet["move_symbols"]:
        lines.append(f"- {name}")
    lines.append("")
    lines.append("Keep in controller adapter:")
    for item in packet["keep_in_controller_adapter"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Owned by other modules:")
    for item in packet["owned_by_other_modules"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append(f"Allowed imports: {', '.join(packet['allowed_imports'])}")
    lines.append(f"Forbidden imports: {', '.join(packet['forbidden_imports'])}")
    lines.append("")
    lines.append("Input contract:")
    for item in packet["input_contract"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Output contract:")
    for item in packet["output_contract"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Preconditions:")
    for item in packet["preconditions"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Rollback steps:")
    for item in packet["rollback_steps"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Validation evidence gates:")
    for gate_id in packet["validation_evidence_plan_ids"]:
        lines.append(f"- {gate_id}")
    return "\n".join(lines).rstrip()


OCEAN_CONDITION_PROVIDER_MODULE_API = {
    "module": "taichi_earth/data_sources/ocean_condition_provider.py",
    "purpose": "Own ocean condition source IO, spatial sampling, normalization, and cache policy while emitting scalar sea-state fields for Taichi.",
    "public_api": [
        {
            "name": "OceanConditionProvider",
            "signature": "OceanConditionProvider(args_like).read(lod: str, force: bool = False) -> dict",
            "ownership": "data_sources",
            "side_effects": "may read file/url/cache according to refresh policy",
        },
        {
            "name": "OceanSpatialSamplingPolicy",
            "signature": "OceanSpatialSamplingPolicy(args_like).decision(source: str, source_kind: str, spatial_mode: str, lod: str) -> dict",
            "ownership": "data_sources",
            "side_effects": "none",
        },
        {
            "name": "normalize_ocean_condition_frame",
            "signature": "normalize_ocean_condition_frame(frame_like, source: str, source_kind: str, spatial_selection: dict) -> dict",
            "ownership": "data_sources",
            "side_effects": "none",
        },
        {
            "name": "select_ocean_condition_sample_frame",
            "signature": "select_ocean_condition_sample_frame(frame_like, spatial_decision: dict) -> frame_like",
            "ownership": "data_sources",
            "side_effects": "none",
        },
        {
            "name": "OceanMaterialPolicy",
            "signature": "OceanMaterialPolicy(args_like).resolve(condition_state: dict, lod: str) -> dict",
            "ownership": "render_core adapter",
            "side_effects": "none",
        },
    ],
    "provider_ports": ["manual", "file", "url", "noaa_ww3", "noaa", "hycom", "copernicus", "local_grid"],
    "renderer_scalar_fields": ["enabled", "wave_strength", "roughness", "foam", "material_scale"],
    "future_spatial_fields": ["lon", "lat", "valid_time", "grid_id", "interpolation", "confidence"],
    "must_not_import": ["PyQt", "vispy", "taichi kernels", "datashader", "AIS/ADS-B feed classes"],
    "allowed_imports": ["json", "pathlib", "urllib", "typing", "pandas optional", "numpy optional"],
    "handoff_rule": "Ocean providers normalize raw feeds before render_core; Taichi receives scalar material controls only.",
}


def ocean_condition_provider_module_api_snapshot() -> dict:
    return dict(OCEAN_CONDITION_PROVIDER_MODULE_API)


def ocean_condition_provider_module_api_text() -> str:
    api = OCEAN_CONDITION_PROVIDER_MODULE_API
    lines = [
        "Ocean condition provider module API",
        "",
        f"- module: {api['module']}",
        f"- purpose: {api['purpose']}",
        f"- provider ports: {', '.join(api['provider_ports'])}",
        f"- renderer scalar fields: {', '.join(api['renderer_scalar_fields'])}",
        f"- future spatial fields: {', '.join(api['future_spatial_fields'])}",
        f"- allowed imports: {', '.join(api['allowed_imports'])}",
        f"- must not import: {', '.join(api['must_not_import'])}",
        f"- handoff rule: {api['handoff_rule']}",
        "",
        "Public API:",
    ]
    for item in api["public_api"]:
        lines.append(f"- {item['name']}")
        lines.append(f"  signature: {item['signature']}")
        lines.append(f"  ownership: {item['ownership']}")
        lines.append(f"  side effects: {item['side_effects']}")
    return "\n".join(lines)


OCEAN_CONDITION_PROVIDER_EXTRACTION_READINESS_PACKET = {
    "target_file": "taichi_earth/data_sources/ocean_condition_provider.py",
    "purpose": "Prepare the ocean condition source/normalization split while keeping render-core ocean material policy, Taichi kernel inputs, and Qt source controls outside the provider module.",
    "candidate_status": "prepared-not-extracted",
    "move_symbols": [
        "OCEAN_PROVIDER_REGISTRY",
        "OCEAN_CONDITION_SCHEMA_TEXT",
        "OceanConditionProvider",
        "OceanSpatialSamplingPolicy",
        "normalize_ocean_condition_frame",
        "select_ocean_condition_sample_frame",
        "build_ocean_normalization_report",
        "ocean_condition_provider_module_api_snapshot",
        "ocean_condition_provider_module_api_text",
    ],
    "keep_in_controller_adapter": [
        "set_ocean_condition_source",
        "set_ocean_provider_lat",
        "set_ocean_provider_lon",
        "ocean_provider_decision_text",
        "ocean_normalization_report_text",
        "ocean_spatial_sampling_text",
        "ocean_material_control_snapshot",
        "ocean_material_taichi_port_snapshot",
        "Qt source/file/url controls",
    ],
    "owned_by_other_modules": [
        "OceanMaterialPolicy remains in render_core/ocean_material.py",
        "build_ocean_material_uniforms remains in render_core/ocean_material.py",
        "Taichi globe.render argument assembly remains in the controller/render adapter",
        "style material modifiers remain in style_profiles.py",
    ],
    "allowed_imports": ["json", "pathlib", "urllib", "typing", "pandas optional", "numpy optional"],
    "forbidden_imports": ["PyQt", "vispy", "taichi kernels", "datashader", "AIS/ADS-B feed classes", "render_core/ocean_material.py"],
    "input_contract": [
        "args-like source settings",
        "LOD id",
        "manual/file/url/provider source id",
        "optional lat/lon sampling target",
        "refresh/cache policy",
    ],
    "output_contract": [
        "provider decision dict",
        "spatial sampling decision dict",
        "normalization report dict",
        "cached scalar condition state",
        "provider manifest dict",
        "no material policy dict",
        "no Taichi kernel inputs",
    ],
    "preconditions": [
        "Ocean provider API is visible from toolbar",
        "Ocean material control and Ocean Taichi material port remain controller/render-core adapter views",
        "Render ocean extraction readiness owns scalar material policy",
        "pre-validation evidence plan has been reviewed",
    ],
    "rollback_steps": [
        "restore OceanConditionProvider and normalization helpers inside the monolith",
        "keep render-core ocean material policy and Taichi port snapshots unchanged",
        "disable only ocean provider extraction readiness diagnostics if toolbar wiring fails",
    ],
}


def ocean_condition_provider_extraction_readiness_packet_snapshot() -> dict:
    packet = dict(OCEAN_CONDITION_PROVIDER_EXTRACTION_READINESS_PACKET)
    packet["module_api"] = ocean_condition_provider_module_api_snapshot()
    packet["validation_evidence_plan_ids"] = [
        item["id"] for item in PRE_VALIDATION_EVIDENCE_PLAN
        if item["id"] in {
            "ocean_taichi_port_gate",
            "small_render_gate",
            "syntax_import_gate",
        }
    ]
    packet["runtime_verification"] = "not-run"
    return packet


def ocean_condition_provider_extraction_readiness_packet_text() -> str:
    packet = ocean_condition_provider_extraction_readiness_packet_snapshot()
    lines = [
        "Ocean condition provider extraction readiness packet",
        "",
        f"- target file: {packet['target_file']}",
        f"- purpose: {packet['purpose']}",
        f"- status: {packet['candidate_status']}",
        f"- runtime verification: {packet['runtime_verification']}",
        "",
        "Move symbols:",
    ]
    for name in packet["move_symbols"]:
        lines.append(f"- {name}")
    lines.append("")
    lines.append("Keep in controller adapter:")
    for item in packet["keep_in_controller_adapter"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Owned by other modules:")
    for item in packet["owned_by_other_modules"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append(f"Allowed imports: {', '.join(packet['allowed_imports'])}")
    lines.append(f"Forbidden imports: {', '.join(packet['forbidden_imports'])}")
    lines.append("")
    lines.append("Input contract:")
    for item in packet["input_contract"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Output contract:")
    for item in packet["output_contract"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Preconditions:")
    for item in packet["preconditions"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Rollback steps:")
    for item in packet["rollback_steps"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Validation evidence gates:")
    for gate_id in packet["validation_evidence_plan_ids"]:
        lines.append(f"- {gate_id}")
    return "\n".join(lines).rstrip()


RENDER_CORE_OCEAN_MATERIAL_MODULE_API = {
    "module": "taichi_earth/render_core/ocean_material.py",
    "purpose": "Convert normalized sea-state and style profile intent into scalar Taichi ocean material parameters without provider IO.",
    "public_api": [
        {
            "name": "OceanMaterialPolicy",
            "signature": "OceanMaterialPolicy(args_like).resolve(condition_state: dict, lod: str) -> dict",
            "ownership": "render_core adapter",
            "side_effects": "none",
        },
        {
            "name": "build_ocean_material_uniforms",
            "signature": "build_ocean_material_uniforms(material: dict) -> dict[str, float | bool]",
            "ownership": "render_core adapter",
            "side_effects": "none",
        },
        {
            "name": "ocean_material_taichi_port_snapshot",
            "signature": "ocean_material_taichi_port_snapshot(controller_like) -> dict",
            "ownership": "controller adapter",
            "side_effects": "reads cached normalized ocean conditions only",
        },
        {
            "name": "ocean_material_control_snapshot",
            "signature": "ocean_material_control_snapshot(provider_decision: dict, condition_state: dict, material: dict, style_entry: dict) -> dict",
            "ownership": "controller adapter",
            "side_effects": "none",
        },
        {
            "name": "ocean_condition_material_binding_snapshot",
            "signature": "ocean_condition_material_binding_snapshot(controller_like) -> dict",
            "ownership": "controller adapter",
            "side_effects": "reads cached normalized ocean conditions only",
        },
    ],
    "input_contract": {
        "condition_state": ["enabled", "wave_strength", "roughness", "foam", "timestamp"],
        "style_entry": ["id", "ocean_material_modifier", "post_process"],
        "lod": ["global", "regional", "local"],
    },
    "taichi_uniforms": ["ocean_enabled", "wave_strength", "roughness", "foam", "material_scale"],
    "taichi_kernel_inputs": ["ocean_enabled", "wave_strength", "roughness", "foam", "time_seconds"],
    "must_not_import": ["PyQt", "vispy", "datashader", "urllib", "database clients", "provider classes"],
    "allowed_imports": ["math", "typing", "numpy optional"],
    "handoff_rule": "Provider modules emit normalized conditions; render_core/ocean_material resolves scalar uniforms; Taichi kernels consume only those uniforms.",
}


def render_core_ocean_material_module_api_snapshot() -> dict:
    return dict(RENDER_CORE_OCEAN_MATERIAL_MODULE_API)


def render_core_ocean_material_module_api_text() -> str:
    api = RENDER_CORE_OCEAN_MATERIAL_MODULE_API
    lines = [
        "Render core ocean material module API",
        "",
        f"- module: {api['module']}",
        f"- purpose: {api['purpose']}",
        f"- Taichi uniforms: {', '.join(api['taichi_uniforms'])}",
        f"- Taichi kernel inputs: {', '.join(api['taichi_kernel_inputs'])}",
        f"- allowed imports: {', '.join(api['allowed_imports'])}",
        f"- must not import: {', '.join(api['must_not_import'])}",
        f"- handoff rule: {api['handoff_rule']}",
        "",
        "Input contract:",
    ]
    for name, values in api["input_contract"].items():
        lines.append(f"- {name}: {', '.join(values)}")
    lines.append("")
    lines.append("Public API:")
    for item in api["public_api"]:
        lines.append(f"- {item['name']}")
        lines.append(f"  signature: {item['signature']}")
        lines.append(f"  ownership: {item['ownership']}")
        lines.append(f"  side effects: {item['side_effects']}")
    return "\n".join(lines)


RENDER_CORE_OCEAN_MATERIAL_EXTRACTION_READINESS_PACKET = {
    "target_file": "taichi_earth/render_core/ocean_material.py",
    "purpose": "Prepare the ocean material scalar-policy split while keeping provider IO, Qt controls, and Taichi kernel invocation outside the pure render-core material module.",
    "candidate_status": "prepared-not-extracted",
    "move_symbols": [
        "OceanMaterialPolicy",
        "build_ocean_material_uniforms",
        "RENDER_CORE_OCEAN_MATERIAL_MODULE_API",
        "render_core_ocean_material_module_api_snapshot",
        "render_core_ocean_material_module_api_text",
    ],
    "keep_in_controller_adapter": [
        "ocean_material_control_snapshot",
        "ocean_material_taichi_port_snapshot",
        "cached ocean condition lookup",
        "ocean_condition_material_binding_snapshot",
        "ocean_condition_material_binding_text",
        "style profile lookup",
        "globe.render argument assembly",
        "Qt setter methods for material sliders and toggles",
    ],
    "allowed_imports": ["math", "typing", "numpy optional"],
    "forbidden_imports": ["PyQt", "vispy", "datashader", "urllib", "database clients", "provider classes", "Taichi renderer instance"],
    "input_contract": [
        "normalized condition_state dict",
        "LOD id",
        "style modifier values as plain dict data",
        "args-like defaults for UI-controlled scalar clamps",
    ],
    "output_contract": [
        "material policy dict",
        "scalar uniform dict",
        "no provider decisions",
        "no Taichi kernel launch",
        "no controller mutation",
    ],
    "preconditions": [
        "Ocean material control and Ocean Taichi material port are visible from toolbar",
        "pre-validation evidence plan has been reviewed",
        "ocean_material_taichi_port_runtime risk remains explicit until one render pass is allowed",
    ],
    "rollback_steps": [
        "restore OceanMaterialPolicy and build_ocean_material_uniforms inside the monolith",
        "keep controller adapter snapshots unchanged",
        "disable only render-core ocean extraction diagnostics if toolbar wiring fails",
    ],
}


def render_core_ocean_material_extraction_readiness_packet_snapshot() -> dict:
    packet = dict(RENDER_CORE_OCEAN_MATERIAL_EXTRACTION_READINESS_PACKET)
    packet["module_api"] = render_core_ocean_material_module_api_snapshot()
    packet["validation_evidence_plan_ids"] = [
        item["id"] for item in PRE_VALIDATION_EVIDENCE_PLAN
        if item["id"] in {
            "ocean_taichi_port_gate",
            "small_render_gate",
            "syntax_import_gate",
        }
    ]
    packet["runtime_verification"] = "not-run"
    return packet


def render_core_ocean_material_extraction_readiness_packet_text() -> str:
    packet = render_core_ocean_material_extraction_readiness_packet_snapshot()
    lines = [
        "Render core ocean material extraction readiness packet",
        "",
        f"- target file: {packet['target_file']}",
        f"- purpose: {packet['purpose']}",
        f"- status: {packet['candidate_status']}",
        f"- runtime verification: {packet['runtime_verification']}",
        "",
        "Move symbols:",
    ]
    for name in packet["move_symbols"]:
        lines.append(f"- {name}")
    lines.append("")
    lines.append("Keep in controller adapter:")
    for item in packet["keep_in_controller_adapter"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append(f"Allowed imports: {', '.join(packet['allowed_imports'])}")
    lines.append(f"Forbidden imports: {', '.join(packet['forbidden_imports'])}")
    lines.append("")
    lines.append("Input contract:")
    for item in packet["input_contract"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Output contract:")
    for item in packet["output_contract"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Preconditions:")
    for item in packet["preconditions"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Rollback steps:")
    for item in packet["rollback_steps"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Validation evidence gates:")
    for gate_id in packet["validation_evidence_plan_ids"]:
        lines.append(f"- {gate_id}")
    return "\n".join(lines).rstrip()


VECTOR_LINES_MODULE_API = {
    "module": "taichi_earth/overlays/vector_lines.py",
    "purpose": "Render lon/lat vector line geometries into transparent screen-space RGBA overlays, independent from data provider source decisions.",
    "public_api": [
        {
            "name": "GeoVectorLineOverlay",
            "signature": "GeoVectorLineOverlay(width: int, height: int, lines: list[np.ndarray], name: str).render(camera..., color, opacity, line_width, highlight..., point_stride=1) -> np.ndarray",
            "ownership": "overlays",
            "side_effects": "none except local image allocation",
        },
        {
            "name": "geojson_to_lines",
            "signature": "geojson_to_lines(obj: dict, decimate: int = 1) -> list[np.ndarray]",
            "ownership": "overlays adapter",
            "side_effects": "none",
        },
        {
            "name": "build_hydrology_render_params",
            "signature": "build_hydrology_render_params(args_like, layer_id: str, spec: dict, render_profile: dict, style_profile: str) -> dict",
            "ownership": "controller/style adapter",
            "side_effects": "none",
        },
        {
            "name": "build_boundary_render_params",
            "signature": "build_boundary_render_params(args_like, layer_id: str, spec: dict, style_profile: str) -> dict",
            "ownership": "controller/style adapter",
            "side_effects": "none",
        },
        {
            "name": "polyline_screen_distance",
            "signature": "polyline_screen_distance(points: list[tuple[float, float]], x: float, y: float) -> float",
            "ownership": "overlays",
            "side_effects": "none",
        },
    ],
    "input_contract": {
        "geometry": ["lon/lat line arrays", "already loaded/decoded by providers"],
        "camera": ["yaw", "pitch", "zoom", "flip_longitude", "flip_latitude"],
        "mask": ["globe_mask for visible hemisphere clipping"],
        "style": ["resolved RGB color", "opacity", "line width", "highlight phase"],
    },
    "outputs": ["RGBA overlay", "hover hit-test distance/line index", "serializable render params"],
    "must_not_import": ["PyQt", "vispy", "taichi", "datashader", "database clients", "provider source decision classes"],
    "allowed_imports": ["math", "numpy", "PIL optional", "typing"],
    "handoff_rule": "Providers load geometry; style/lod/controller resolve render params; vector_lines only projects and draws.",
}


def vector_lines_module_api_snapshot() -> dict:
    return dict(VECTOR_LINES_MODULE_API)


def vector_lines_module_api_text() -> str:
    api = VECTOR_LINES_MODULE_API
    lines = [
        "Vector lines module API",
        "",
        f"- module: {api['module']}",
        f"- purpose: {api['purpose']}",
        f"- outputs: {', '.join(api['outputs'])}",
        f"- allowed imports: {', '.join(api['allowed_imports'])}",
        f"- must not import: {', '.join(api['must_not_import'])}",
        f"- handoff rule: {api['handoff_rule']}",
        "",
        "Input contract:",
    ]
    for name, values in api["input_contract"].items():
        lines.append(f"- {name}: {', '.join(values)}")
    lines.append("")
    lines.append("Public API:")
    for item in api["public_api"]:
        lines.append(f"- {item['name']}")
        lines.append(f"  signature: {item['signature']}")
        lines.append(f"  ownership: {item['ownership']}")
        lines.append(f"  side effects: {item['side_effects']}")
    return "\n".join(lines)


LOD_PIPELINE_MODULE_API = {
    "module": "taichi_earth/projection/lod_pipeline.py",
    "purpose": "Resolve scale-dependent source, simplification, render-budget, and sampling decisions before renderers run.",
    "public_api": [
        {
            "name": "BasemapLODManager",
            "signature": "BasemapLODManager().decision(km_per_pixel: float, projection: str, topo_source: str | None, topo_step: int | None) -> dict",
            "ownership": "projection/lod_pipeline",
            "side_effects": "none",
        },
        {
            "name": "HydrologyRenderLODProfile",
            "signature": "HydrologyRenderLODProfile().decision(lod: str, layer_id: str) -> dict",
            "ownership": "projection/lod_pipeline",
            "side_effects": "none",
        },
        {
            "name": "LayerRenderBudgetPolicy",
            "signature": "LayerRenderBudgetPolicy(args_like).decision(width: int, height: int, last_render_ms: float, lod: str) -> dict",
            "ownership": "projection/lod_pipeline",
            "side_effects": "none",
        },
        {
            "name": "PointOverlayBudgetPolicy",
            "signature": "PointOverlayBudgetPolicy(args_like).decision(ais_records: int, aircraft_records: int, lod: str, last_render_ms: float) -> dict",
            "ownership": "projection/lod_pipeline",
            "side_effects": "none",
        },
        {
            "name": "lod_hook_pipeline_snapshot",
            "signature": "lod_hook_pipeline_snapshot(controller_like) -> dict",
            "ownership": "controller adapter",
            "side_effects": "reads current runtime state only",
        },
        {
            "name": "lod_layer_decision_matrix_snapshot",
            "signature": "lod_layer_decision_matrix_snapshot(controller_like) -> dict",
            "ownership": "controller adapter",
            "side_effects": "reads current runtime state only",
        },
        {
            "name": "lod_invalidation_contract_snapshot",
            "signature": "lod_invalidation_contract_snapshot(controller_like) -> dict",
            "ownership": "controller adapter",
            "side_effects": "reads dirty flag state only",
        },
    ],
    "input_contract": {
        "scale": ["km_per_pixel", "projection", "zoom", "viewport width/height"],
        "runtime_pressure": ["last_render_ms", "target_fps", "record counts", "interaction active"],
        "style": ["style_profile for resolved render params only"],
        "provider_context": ["topo_source", "topo_step", "hydrology_source_mode", "ocean_condition_source"],
    },
    "outputs": [
        "basemap LOD decision",
        "hydrology render profile",
        "LOD-to-layer decision matrix",
        "vector overlay budget",
        "point overlay sample budget",
        "ocean spatial sampling context",
    ],
    "must_not_import": ["PyQt", "vispy", "taichi", "datashader", "urllib", "database clients"],
    "allowed_imports": ["math", "typing"],
    "handoff_rule": "LOD pipeline returns decisions only; providers load data and renderers draw pixels.",
}


def lod_pipeline_module_api_snapshot() -> dict:
    return dict(LOD_PIPELINE_MODULE_API)


def lod_pipeline_module_api_text() -> str:
    api = LOD_PIPELINE_MODULE_API
    lines = [
        "LOD pipeline module API",
        "",
        f"- module: {api['module']}",
        f"- purpose: {api['purpose']}",
        f"- outputs: {', '.join(api['outputs'])}",
        f"- allowed imports: {', '.join(api['allowed_imports'])}",
        f"- must not import: {', '.join(api['must_not_import'])}",
        f"- handoff rule: {api['handoff_rule']}",
        "",
        "Input contract:",
    ]
    for name, values in api["input_contract"].items():
        lines.append(f"- {name}: {', '.join(values)}")
    lines.append("")
    lines.append("Public API:")
    for item in api["public_api"]:
        lines.append(f"- {item['name']}")
        lines.append(f"  signature: {item['signature']}")
        lines.append(f"  ownership: {item['ownership']}")
        lines.append(f"  side effects: {item['side_effects']}")
    return "\n".join(lines)


LOD_INVALIDATION_CONTRACT = [
    {
        "trigger": "lod_bucket_changed",
        "entry_point": "update_basemap_lod",
        "expected_dirty_flags": ["hydrology_dirty", "boundary_dirty", "overlay_dirty"],
        "cache_policy": "vector overlay cache may be reused by quantized view/style key, but LOD-driven cache misses must redraw hydrology and boundaries.",
        "provider_scope": ["hydrology LOD source decisions", "boundary LOD source decisions", "ocean spatial sampling decision"],
        "open_risk": "ocean material LOD resampling still depends on the globe render branch, so this contract is diagnostic until runtime validation is allowed.",
    },
    {
        "trigger": "projection_changed",
        "entry_point": "set_map_projection",
        "expected_dirty_flags": ["globe_dirty", "overlay_dirty", "hydrology_dirty", "boundary_dirty"],
        "cache_policy": "projection changes invalidate screen-space overlays and should not reuse stale projected vector buffers.",
        "provider_scope": ["basemap provider decision", "projection-aware LOD label", "all vector projection params"],
        "open_risk": "planar renderers are still port/basic and need runtime parity before physical split.",
    },
    {
        "trigger": "style_profile_changed",
        "entry_point": "set_style_profile",
        "expected_dirty_flags": ["globe_dirty", "overlay_dirty"],
        "cache_policy": "style_vector_cache_key and Datashader cmap config must separate cached overlays by profile.",
        "provider_scope": ["style renderer entry", "vector tint", "Datashader palette", "ocean material modifier"],
        "open_risk": "style-dependent vector cache behavior is contract-only until visual parity is inspected.",
    },
    {
        "trigger": "vector_overlay_deferred",
        "entry_point": "render_if_needed",
        "expected_dirty_flags": ["hydrology_dirty", "boundary_dirty"],
        "cache_policy": "when vector overlays are deferred for FPS protection, dirty flags remain true for the next non-deferred frame.",
        "provider_scope": ["hydrology overlays", "boundary overlays"],
        "open_risk": "deferred redraw behavior still needs runtime FPS/visual inspection.",
    },
]


LOD_PIPELINE_EXTRACTION_READINESS_PACKET = {
    "target_file": "taichi_earth/projection/lod_pipeline.py",
    "purpose": "Prepare the LOD hook split while keeping controller runtime state, provider IO, and renderer calls outside the projection policy module.",
    "candidate_status": "prepared-not-extracted",
    "move_symbols": [
        "BasemapLODManager",
        "HydrologyRenderLODProfile",
        "LayerRenderBudgetPolicy",
        "PointOverlayBudgetPolicy",
    ],
    "keep_in_controller_adapter": [
        "current_km_per_pixel",
        "update_basemap_lod",
        "lod_hook_pipeline_snapshot",
        "lod_layer_decision_matrix_snapshot",
        "lod_invalidation_contract_snapshot",
        "lod_invalidation_contract_text",
        "render_budget_decision",
        "point_overlay_budget_last",
        "provider decision calls",
        "dirty flags and render scheduling",
    ],
    "allowed_imports": ["math", "typing"],
    "forbidden_imports": ["PyQt", "vispy", "taichi", "datashader", "urllib", "database clients", "provider loader functions"],
    "input_contract": [
        "km_per_pixel",
        "projection",
        "viewport width/height",
        "last_render_ms",
        "target_fps",
        "record counts",
        "current basemap LOD",
        "style profile id only when resolving adapter-side render params",
    ],
    "output_contract": [
        "decision dictionaries only",
        "no provider data loading",
        "no renderer calls",
        "no controller mutation",
    ],
    "preconditions": [
        "LOD hook pipeline and LOD layer decision matrix are visible from toolbar",
        "active_goal_gate_lod_layer_count_contract risk is understood or fixed",
        "pre-validation evidence plan has been reviewed",
        "vector lines extraction readiness packet remains adapter-compatible",
    ],
    "rollback_steps": [
        "restore LOD policy classes inside the monolith",
        "keep controller snapshot methods unchanged",
        "disable only the LOD extraction readiness diagnostic if toolbar wiring fails",
    ],
}


def lod_pipeline_extraction_readiness_packet_snapshot() -> dict:
    packet = dict(LOD_PIPELINE_EXTRACTION_READINESS_PACKET)
    packet["module_api"] = lod_pipeline_module_api_snapshot()
    packet["validation_evidence_plan_ids"] = [
        item["id"] for item in PRE_VALIDATION_EVIDENCE_PLAN
        if item["id"] in {
            "lod_hook_diagnostic_gate",
            "hydrology_basic_diagnostic_gate",
            "small_render_gate",
        }
    ]
    packet["runtime_verification"] = "not-run"
    return packet


def lod_pipeline_extraction_readiness_packet_text() -> str:
    packet = lod_pipeline_extraction_readiness_packet_snapshot()
    lines = [
        "LOD pipeline extraction readiness packet",
        "",
        f"- target file: {packet['target_file']}",
        f"- purpose: {packet['purpose']}",
        f"- status: {packet['candidate_status']}",
        f"- runtime verification: {packet['runtime_verification']}",
        "",
        "Move symbols:",
    ]
    for name in packet["move_symbols"]:
        lines.append(f"- {name}")
    lines.append("")
    lines.append("Keep in controller adapter:")
    for item in packet["keep_in_controller_adapter"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append(f"Allowed imports: {', '.join(packet['allowed_imports'])}")
    lines.append(f"Forbidden imports: {', '.join(packet['forbidden_imports'])}")
    lines.append("")
    lines.append("Input contract:")
    for item in packet["input_contract"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Output contract:")
    for item in packet["output_contract"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Preconditions:")
    for item in packet["preconditions"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Rollback steps:")
    for item in packet["rollback_steps"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Validation evidence gates:")
    for gate_id in packet["validation_evidence_plan_ids"]:
        lines.append(f"- {gate_id}")
    return "\n".join(lines).rstrip()


STYLE_PROFILES_MODULE_API = {
    "module": "taichi_earth/style_profiles.py",
    "purpose": "Resolve visual style profiles into Taichi material modifiers, Datashader palettes, vector/icon tint intents, and final frame post-process.",
    "public_api": [
        {
            "name": "resolve_style_profile",
            "signature": "resolve_style_profile(profile: str) -> dict",
            "ownership": "style_profiles",
            "side_effects": "none",
        },
        {
            "name": "resolve_style_renderer_entry",
            "signature": "resolve_style_renderer_entry(profile: str) -> dict",
            "ownership": "style_profiles",
            "side_effects": "none",
        },
        {
            "name": "style_renderer_entry_matrix_snapshot",
            "signature": "style_renderer_entry_matrix_snapshot(active_profile: str = 'scientific') -> dict",
            "ownership": "style_profiles",
            "side_effects": "none",
        },
        {
            "name": "style_renderer_entry_matrix_text",
            "signature": "style_renderer_entry_matrix_text(active_profile: str = 'scientific') -> str",
            "ownership": "style_profiles",
            "side_effects": "none",
        },
        {
            "name": "resolve_style_overlay_intent",
            "signature": "resolve_style_overlay_intent(profile: str) -> dict",
            "ownership": "style_profiles",
            "side_effects": "none",
        },
        {
            "name": "resolve_datashader_style_cmaps",
            "signature": "resolve_datashader_style_cmaps(profile: str) -> dict",
            "ownership": "style_profiles",
            "side_effects": "none",
        },
        {
            "name": "resolve_style_layer_rgb",
            "signature": "resolve_style_layer_rgb(profile: str, layer_kind: str, base_color: tuple[int, int, int]) -> tuple[int, int, int]",
            "ownership": "style_profiles",
            "side_effects": "none",
        },
        {
            "name": "apply_style_profile",
            "signature": "apply_style_profile(frame: np.ndarray, profile: str) -> np.ndarray",
            "ownership": "style_profiles",
            "side_effects": "allocates output frame for non-scientific post-process",
        },
    ],
    "profiles": ["scientific", "nautical", "tactical", "parchment"],
    "input_contract": {
        "style_id": ["scientific", "nautical", "tactical", "parchment"],
        "render_targets": ["Taichi ocean material", "Datashader AIS/ADS-B palettes", "vector line tints", "final RGBA post-process"],
        "frame": ["RGBA uint8 ndarray for post-process only"],
    },
    "outputs": [
        "style renderer entry",
        "overlay intent",
        "Datashader cmap dict",
        "style-aware RGB tuple",
        "post-processed RGBA frame",
    ],
    "must_not_import": ["PyQt", "vispy", "taichi", "urllib", "database clients", "provider classes"],
    "allowed_imports": ["math", "typing", "numpy"],
    "handoff_rule": "Style profiles return pure intents and post-process frames; renderers consume those intents without owning style registry state.",
}


def style_profiles_module_api_snapshot() -> dict:
    return dict(STYLE_PROFILES_MODULE_API)


def style_profiles_module_api_text() -> str:
    api = STYLE_PROFILES_MODULE_API
    lines = [
        "Style profiles module API",
        "",
        f"- module: {api['module']}",
        f"- purpose: {api['purpose']}",
        f"- profiles: {', '.join(api['profiles'])}",
        f"- outputs: {', '.join(api['outputs'])}",
        f"- allowed imports: {', '.join(api['allowed_imports'])}",
        f"- must not import: {', '.join(api['must_not_import'])}",
        f"- handoff rule: {api['handoff_rule']}",
        "",
        "Input contract:",
    ]
    for name, values in api["input_contract"].items():
        lines.append(f"- {name}: {', '.join(values)}")
    lines.append("")
    lines.append("Public API:")
    for item in api["public_api"]:
        lines.append(f"- {item['name']}")
        lines.append(f"  signature: {item['signature']}")
        lines.append(f"  ownership: {item['ownership']}")
        lines.append(f"  side effects: {item['side_effects']}")
    return "\n".join(lines)


STYLE_PROFILES_EXTRACTION_READINESS_PACKET = {
    "target_file": "taichi_earth/style_profiles.py",
    "purpose": "Prepare the shared visual style split so renderers, vector overlays, Datashader overlays, and ocean material policies consume resolved style data rather than duplicating palette logic.",
    "candidate_status": "prepared-not-extracted",
    "move_symbols": [
        "STYLE_PROFILE_REGISTRY",
        "STYLE_PROFILE_MATERIAL_MODIFIERS",
        "DATASHADER_STYLE_CMAPS",
        "resolve_style_profile",
        "resolve_style_renderer_entry",
        "style_renderer_entry_matrix_snapshot",
        "style_renderer_entry_matrix_text",
        "resolve_style_overlay_intent",
        "resolve_datashader_style_cmaps",
        "resolve_style_layer_rgb",
        "style_profile_registry_text",
        "style_renderer_entry_text",
        "style_overlay_intent_text",
        "apply_style_profile",
        "style_profiles_module_api_snapshot",
        "style_profiles_module_api_text",
    ],
    "keep_in_controller_adapter": [
        "set_style_profile",
        "style_profile_status_text",
        "style_renderer_entry_text controller wrapper",
        "style_renderer_entry_matrix_text controller wrapper",
        "style_overlay_intent_text controller wrapper",
        "overlay renderer set_style_profile calls",
        "final frame post-process call site",
        "Qt combo-box state",
    ],
    "owned_by_other_modules": [
        "style_vector_cache_key remains in overlays/vector_lines.py unless vector cache ownership is changed",
        "build_datashader_overlay_config remains in overlays/datashader_points.py and consumes resolved cmaps",
        "build_hydrology_render_params and build_boundary_render_params remain in overlays/vector_lines.py and consume resolved RGB values",
        "OceanMaterialPolicy remains in render_core/ocean_material.py and consumes style modifier dicts",
    ],
    "allowed_imports": ["math", "typing", "numpy optional"],
    "forbidden_imports": ["PyQt", "vispy", "taichi", "datashader", "provider classes", "database clients", "network clients"],
    "input_contract": [
        "style profile id or user-provided profile string",
        "layer kind for vector color resolution",
        "base RGB tuple",
        "frame array only for explicit post-process helper",
    ],
    "output_contract": [
        "resolved style profile dict",
        "renderer entry dict",
        "overlay intent dict",
        "Datashader cmap names",
        "resolved RGB tuple",
        "post-processed frame copy when requested",
    ],
    "preconditions": [
        "Style profiles API is visible from toolbar",
        "Vector lines extraction readiness consumes style through resolved RGB/cache-key values",
        "Render ocean extraction readiness consumes style through material modifier dicts",
        "Datashader points API consumes style through resolved cmap config",
        "pre-validation evidence plan has been reviewed",
    ],
    "rollback_steps": [
        "restore style registries and helper functions inside the monolith",
        "keep controller and Qt style selection wrappers unchanged",
        "disable only style profiles extraction readiness diagnostics if toolbar wiring fails",
    ],
}


def style_profiles_extraction_readiness_packet_snapshot() -> dict:
    packet = dict(STYLE_PROFILES_EXTRACTION_READINESS_PACKET)
    packet["module_api"] = style_profiles_module_api_snapshot()
    packet["validation_evidence_plan_ids"] = [
        item["id"] for item in PRE_VALIDATION_EVIDENCE_PLAN
        if item["id"] in {
            "syntax_import_gate",
            "hydrology_basic_diagnostic_gate",
            "lod_hook_diagnostic_gate",
            "ocean_taichi_port_gate",
            "small_render_gate",
        }
    ]
    packet["runtime_verification"] = "not-run"
    return packet


def style_profiles_extraction_readiness_packet_text() -> str:
    packet = style_profiles_extraction_readiness_packet_snapshot()
    lines = [
        "Style profiles extraction readiness packet",
        "",
        f"- target file: {packet['target_file']}",
        f"- purpose: {packet['purpose']}",
        f"- status: {packet['candidate_status']}",
        f"- runtime verification: {packet['runtime_verification']}",
        "",
        "Move symbols:",
    ]
    for name in packet["move_symbols"]:
        lines.append(f"- {name}")
    lines.append("")
    lines.append("Keep in controller adapter:")
    for item in packet["keep_in_controller_adapter"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Owned by other modules:")
    for item in packet["owned_by_other_modules"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append(f"Allowed imports: {', '.join(packet['allowed_imports'])}")
    lines.append(f"Forbidden imports: {', '.join(packet['forbidden_imports'])}")
    lines.append("")
    lines.append("Input contract:")
    for item in packet["input_contract"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Output contract:")
    for item in packet["output_contract"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Preconditions:")
    for item in packet["preconditions"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Rollback steps:")
    for item in packet["rollback_steps"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Validation evidence gates:")
    for gate_id in packet["validation_evidence_plan_ids"]:
        lines.append(f"- {gate_id}")
    return "\n".join(lines).rstrip()


VECTOR_LINES_EXTRACTION_READINESS_PACKET = {
    "target_file": "taichi_earth/overlays/vector_lines.py",
    "purpose": "Prepare the shared hydrology/boundary vector rendering split while keeping provider decisions and controller cache ownership out of the overlay module.",
    "candidate_status": "prepared-not-extracted",
    "move_symbols": [
        "GeoVectorLineOverlay",
        "style_vector_cache_key",
        "build_hydrology_render_params",
        "build_boundary_render_params",
    ],
    "keep_in_controller_adapter": [
        "vector_overlay_cache dictionary and eviction order",
        "_store_vector_overlay_cache",
        "_lookup_vector_overlay_cache",
        "_render_hydrology_overlay",
        "_render_boundary_overlay",
        "dirty flags and force/defer decisions",
    ],
    "allowed_imports": ["math", "typing", "numpy", "style_profiles optional"],
    "forbidden_imports": ["PyQt", "taichi", "datashader", "network clients", "database clients", "provider loader functions"],
    "input_contract": [
        "lon/lat line arrays",
        "camera yaw/pitch/zoom",
        "viewport width/height",
        "resolved color/opacity/line_width/point_stride",
        "optional hover/highlight screen coordinate",
    ],
    "output_contract": [
        "RGBA overlay array or None when no lines should be rendered",
        "no provider decisions",
        "no controller mutation",
    ],
    "preconditions": [
        "style profile helpers are either extracted first or passed through adapter as resolved RGB/cache-key values",
        "Hydrology basic readiness and LOD layer decision matrix are visible from toolbar",
        "pre-validation evidence plan has been reviewed",
    ],
    "rollback_steps": [
        "restore GeoVectorLineOverlay and render param helpers inside the monolith",
        "keep controller cache code unchanged",
        "disable only vector lines readiness diagnostics if toolbar wiring fails",
    ],
}


def vector_lines_extraction_readiness_packet_snapshot() -> dict:
    packet = dict(VECTOR_LINES_EXTRACTION_READINESS_PACKET)
    packet["module_api"] = vector_lines_module_api_snapshot()
    packet["validation_evidence_plan_ids"] = [
        item["id"] for item in PRE_VALIDATION_EVIDENCE_PLAN
        if item["id"] in {
            "hydrology_basic_diagnostic_gate",
            "lod_hook_diagnostic_gate",
            "small_render_gate",
        }
    ]
    packet["runtime_verification"] = "not-run"
    return packet


def vector_lines_extraction_readiness_packet_text() -> str:
    packet = vector_lines_extraction_readiness_packet_snapshot()
    lines = [
        "Vector lines extraction readiness packet",
        "",
        f"- target file: {packet['target_file']}",
        f"- purpose: {packet['purpose']}",
        f"- status: {packet['candidate_status']}",
        f"- runtime verification: {packet['runtime_verification']}",
        "",
        "Move symbols:",
    ]
    for name in packet["move_symbols"]:
        lines.append(f"- {name}")
    lines.append("")
    lines.append("Keep in controller adapter:")
    for item in packet["keep_in_controller_adapter"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append(f"Allowed imports: {', '.join(packet['allowed_imports'])}")
    lines.append(f"Forbidden imports: {', '.join(packet['forbidden_imports'])}")
    lines.append("")
    lines.append("Input contract:")
    for item in packet["input_contract"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Output contract:")
    for item in packet["output_contract"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Preconditions:")
    for item in packet["preconditions"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Rollback steps:")
    for item in packet["rollback_steps"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Validation evidence gates:")
    for gate_id in packet["validation_evidence_plan_ids"]:
        lines.append(f"- {gate_id}")
    return "\n".join(lines).rstrip()


DATASHADER_POINTS_MODULE_API = {
    "module": "taichi_earth/overlays/datashader_points.py",
    "purpose": "Render projected screen-space AIS/ADS-B point tables into transparent RGBA overlays with style-aware palettes and sample-budget controls.",
    "public_api": [
        {
            "name": "AISDatashaderOverlay",
            "signature": "AISDatashaderOverlay(width, height, color_by, point_px, speed_span).render(projected: pd.DataFrame) -> np.ndarray",
            "ownership": "overlays",
            "side_effects": "allocates Datashader aggregate/image only",
        },
        {
            "name": "AircraftDatashaderOverlay",
            "signature": "AircraftDatashaderOverlay(width, height, color_by, point_px, altitude_span, speed_span).render(projected: pd.DataFrame) -> np.ndarray",
            "ownership": "overlays",
            "side_effects": "allocates Datashader aggregate/image only",
        },
        {
            "name": "DatashaderSamplingPolicy",
            "signature": "DatashaderSamplingPolicy().decision(record_count: int, lod: str, requested_ratio: float, realtime: bool) -> dict",
            "ownership": "overlays/lod adapter",
            "side_effects": "none",
        },
        {
            "name": "PointOverlayBudgetPolicy",
            "signature": "PointOverlayBudgetPolicy(args_like).decision(ais_records: int, aircraft_records: int, lod: str, last_render_ms: float) -> dict",
            "ownership": "projection/lod_pipeline",
            "side_effects": "none",
        },
        {
            "name": "build_datashader_overlay_config",
            "signature": "build_datashader_overlay_config(style_profile: str, layer_kind: str, color_mode: str, point_px: int) -> dict",
            "ownership": "overlays/style adapter",
            "side_effects": "none",
        },
        {
            "name": "mask_overlay_to_globe",
            "signature": "mask_overlay_to_globe(overlay: np.ndarray, globe_mask: np.ndarray) -> np.ndarray",
            "ownership": "overlays",
            "side_effects": "allocates masked overlay copy",
        },
    ],
    "input_contract": {
        "points": ["projected screen_x/screen_y dataframe", "already hemisphere-clipped by projection adapter"],
        "style": ["resolved Datashader cmap dict from style_profiles", "color_by mode"],
        "sampling": ["requested sample ratio", "adaptive cap", "point overlay budget"],
        "mask": ["globe_mask for final compositing guard"],
    },
    "outputs": ["transparent RGBA overlay", "visible/rendered counts", "serializable sampling decision"],
    "must_not_import": ["PyQt", "vispy", "taichi", "database clients", "raw provider socket clients"],
    "allowed_imports": ["numpy", "pandas", "datashader", "colorcet optional", "typing"],
    "handoff_rule": "Projection owns visibility clipping; Datashader receives only screen-space points and style cmaps.",
}


def datashader_points_module_api_snapshot() -> dict:
    return dict(DATASHADER_POINTS_MODULE_API)


def datashader_points_module_api_text() -> str:
    api = DATASHADER_POINTS_MODULE_API
    lines = [
        "Datashader points module API",
        "",
        f"- module: {api['module']}",
        f"- purpose: {api['purpose']}",
        f"- outputs: {', '.join(api['outputs'])}",
        f"- allowed imports: {', '.join(api['allowed_imports'])}",
        f"- must not import: {', '.join(api['must_not_import'])}",
        f"- handoff rule: {api['handoff_rule']}",
        "",
        "Input contract:",
    ]
    for name, values in api["input_contract"].items():
        lines.append(f"- {name}: {', '.join(values)}")
    lines.append("")
    lines.append("Public API:")
    for item in api["public_api"]:
        lines.append(f"- {item['name']}")
        lines.append(f"  signature: {item['signature']}")
        lines.append(f"  ownership: {item['ownership']}")
        lines.append(f"  side effects: {item['side_effects']}")
    return "\n".join(lines)


DATASHADER_POINTS_EXTRACTION_READINESS_PACKET = {
    "target_file": "taichi_earth/overlays/datashader_points.py",
    "purpose": "Prepare the AIS/ADS-B Datashader overlay split while keeping feed IO, projection clipping, controller overlay state, and Qt controls outside the point-rendering module.",
    "candidate_status": "prepared-not-extracted",
    "move_symbols": [
        "AISDatashaderOverlay",
        "AircraftDatashaderOverlay",
        "DatashaderSamplingPolicy",
        "build_datashader_overlay_config",
        "mask_overlay_to_globe",
        "datashader_points_module_api_snapshot",
        "datashader_points_module_api_text",
    ],
    "keep_in_controller_adapter": [
        "current_ais and current_aircraft tables",
        "project_ais_to_screen and project_aircraft_to_screen call sites",
        "hemisphere/horizon clipping decisions",
        "overlay_dirty flags",
        "visible/rendered count bookkeeping",
        "overlay renderer instance lifecycle",
        "Qt point/color mode controls",
    ],
    "owned_by_other_modules": [
        "style cmap resolution remains in style_profiles.py",
        "point overlay budget policy remains in projection/lod_pipeline.py",
        "AIS/ADS-B provider decisions remain in data source/provider adapters",
        "final compositing remains in the controller/render adapter",
    ],
    "allowed_imports": ["numpy", "pandas", "datashader", "colorcet optional", "typing"],
    "forbidden_imports": ["PyQt", "vispy", "taichi", "database clients", "raw provider socket clients", "controller instances"],
    "input_contract": [
        "projected screen-space point DataFrame",
        "style profile id or resolved Datashader cmap config",
        "color_by mode",
        "point spread/pixel size",
        "sampling decision",
        "optional globe mask for compositing guard",
    ],
    "output_contract": [
        "transparent RGBA overlay array",
        "serializable sampling/config decision",
        "no provider IO",
        "no projection math ownership",
        "no controller mutation",
    ],
    "preconditions": [
        "Datashader points API is visible from toolbar",
        "Style profiles extraction readiness owns cmap resolution",
        "LOD pipeline extraction readiness owns point overlay budget policy",
        "pre-validation evidence plan has been reviewed",
    ],
    "rollback_steps": [
        "restore Datashader overlay classes and config helper inside the monolith",
        "keep controller projection and overlay state code unchanged",
        "disable only Datashader points extraction readiness diagnostics if toolbar wiring fails",
    ],
}


def datashader_points_extraction_readiness_packet_snapshot() -> dict:
    packet = dict(DATASHADER_POINTS_EXTRACTION_READINESS_PACKET)
    packet["module_api"] = datashader_points_module_api_snapshot()
    packet["validation_evidence_plan_ids"] = [
        item["id"] for item in PRE_VALIDATION_EVIDENCE_PLAN
        if item["id"] in {
            "syntax_import_gate",
            "small_render_gate",
        }
    ]
    packet["runtime_verification"] = "not-run"
    return packet


def datashader_points_extraction_readiness_packet_text() -> str:
    packet = datashader_points_extraction_readiness_packet_snapshot()
    lines = [
        "Datashader points extraction readiness packet",
        "",
        f"- target file: {packet['target_file']}",
        f"- purpose: {packet['purpose']}",
        f"- status: {packet['candidate_status']}",
        f"- runtime verification: {packet['runtime_verification']}",
        "",
        "Move symbols:",
    ]
    for name in packet["move_symbols"]:
        lines.append(f"- {name}")
    lines.append("")
    lines.append("Keep in controller adapter:")
    for item in packet["keep_in_controller_adapter"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Owned by other modules:")
    for item in packet["owned_by_other_modules"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append(f"Allowed imports: {', '.join(packet['allowed_imports'])}")
    lines.append(f"Forbidden imports: {', '.join(packet['forbidden_imports'])}")
    lines.append("")
    lines.append("Input contract:")
    for item in packet["input_contract"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Output contract:")
    for item in packet["output_contract"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Preconditions:")
    for item in packet["preconditions"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Rollback steps:")
    for item in packet["rollback_steps"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Validation evidence gates:")
    for gate_id in packet["validation_evidence_plan_ids"]:
        lines.append(f"- {gate_id}")
    return "\n".join(lines).rstrip()


def module_api_registry_snapshot() -> dict:
    return {
        "contracts/provider_manifests.py": provider_manifests_module_api_snapshot(),
        "data_sources/hydrology_provider.py": hydrology_provider_module_api_snapshot(),
        "data_sources/ocean_condition_provider.py": ocean_condition_provider_module_api_snapshot(),
        "render_core/ocean_material.py": render_core_ocean_material_module_api_snapshot(),
        "overlays/vector_lines.py": vector_lines_module_api_snapshot(),
        "projection/lod_pipeline.py": lod_pipeline_module_api_snapshot(),
        "style_profiles.py": style_profiles_module_api_snapshot(),
        "overlays/datashader_points.py": datashader_points_module_api_snapshot(),
        "qt_ui/controller_facade.py": qt_controller_facade_api_snapshot(),
        "qt_ui/main_window.py": qt_main_window_module_api_snapshot(),
    }


def module_api_registry_text() -> str:
    registry = module_api_registry_snapshot()
    lines = [
        "Module API registry",
        "",
        "Purpose: one handoff index for the first extraction wave.",
        "Rule: use this registry as the checklist before physically splitting modules.",
        "",
    ]
    for module_path, api in registry.items():
        public_names = [item.get("name", "") for item in api.get("public_api", [])]
        lines.append(f"- {module_path}")
        lines.append(f"  purpose: {api.get('purpose', '')}")
        lines.append(f"  public API: {', '.join(public_names)}")
        lines.append(f"  must not import: {', '.join(api.get('must_not_import', []))}")
    return "\n".join(lines)


def pre_extraction_readiness_audit_snapshot() -> dict:
    registry = module_api_registry_snapshot()
    units = decoupling_extraction_units_snapshot()
    unit_targets = {unit.get("target", ""): unit for unit in units}
    module_checks = {}
    for module_path, api in registry.items():
        public_api = api.get("public_api", [])
        module_checks[module_path] = {
            "has_public_api": bool(public_api),
            "public_api_count": len(public_api),
            "has_allowed_imports": bool(api.get("allowed_imports")),
            "has_forbidden_imports": bool(api.get("must_not_import")),
            "has_handoff_rule": bool(api.get("handoff_rule")),
            "has_extraction_unit": any(module_path in target for target in unit_targets),
            "state": "contract-ready" if public_api and api.get("must_not_import") and api.get("handoff_rule") else "contract-incomplete",
        }
    return {
        "contract": "Pre-extraction readiness audit checks whether module API contracts are explicit enough to start a reversible physical split.",
        "runtime_verification": "not-run",
        "physical_split": "not-started",
        "first_extract_candidate": "contracts/provider_manifests.py",
        "module_checks": module_checks,
        "global_gates": {
            "module_api_registry": bool(registry),
            "extraction_units": bool(units),
            "runtime_configuration_contract": bool(RUNTIME_CONFIGURATION_CONTRACT),
            "provider_manifest_api": bool(PROVIDER_MANIFESTS_MODULE_API),
            "handoff_snapshot_contains_contracts": True,
        },
        "required_before_goal_complete": [
            "one runtime visual pass",
            "one provider/cache manifest write pass if user permits",
            "syntax/import verification if user permits",
            "at least first physical extraction or explicit decision to keep monolith",
        ],
    }


def pre_extraction_readiness_audit_text() -> str:
    audit = pre_extraction_readiness_audit_snapshot()
    lines = [
        "Pre-extraction readiness audit",
        "",
        f"- contract: {audit['contract']}",
        f"- runtime verification: {audit['runtime_verification']}",
        f"- physical split: {audit['physical_split']}",
        f"- first extract candidate: {audit['first_extract_candidate']}",
        "",
        "Global gates:",
    ]
    for name, value in audit["global_gates"].items():
        lines.append(f"- {name}: {value}")
    lines.extend(["", "Module checks:"])
    for module_path, check in audit["module_checks"].items():
        lines.append(f"- {module_path}: {check['state']}; public_api={check['public_api_count']}; extraction_unit={check['has_extraction_unit']}")
    lines.extend(["", "Required before goal complete:"])
    for item in audit["required_before_goal_complete"]:
        lines.append(f"- {item}")
    return "\n".join(lines)


FIRST_EXTRACTION_EXECUTION_PLAN = [
    {
        "step": 1,
        "name": "extract provider manifests contracts",
        "target_file": "taichi_earth/contracts/provider_manifests.py",
        "move_symbols": [
            "build_provider_cache_manifest",
            "dedupe_provider_manifests",
            "provider_manifest_templates_text",
            "provider_manifests_module_api_*",
        ],
        "update_monolith": [
            "replace local helper definitions with imports",
            "keep controller aggregation methods in monolith for this step",
        ],
        "rollback": "delete new file and restore local helper definitions from current monolith patch.",
    },
    {
        "step": 2,
        "name": "extract style profiles",
        "target_file": "taichi_earth/style_profiles.py",
        "move_symbols": [
            "STYLE_PROFILE_REGISTRY",
            "STYLE_RENDERER_ENTRIES",
            "DATASHADER_STYLE_CMAPS",
            "resolve_style_*",
            "apply_style_profile",
        ],
        "update_monolith": [
            "import style helpers before overlay classes are constructed",
            "keep Qt combo labels local until one runtime pass confirms choices",
        ],
        "rollback": "restore constants/helpers into monolith; no cache or provider state involved.",
    },
    {
        "step": 3,
        "name": "extract vector line overlays",
        "target_file": "taichi_earth/overlays/vector_lines.py",
        "move_symbols": [
            "GeoVectorLineOverlay",
            "geojson_to_lines",
            "decimate_lines",
            "polyline_screen_distance",
            "build_hydrology_render_params",
            "build_boundary_render_params",
        ],
        "update_monolith": [
            "import vector render helpers",
            "keep controller cache ownership in monolith",
        ],
        "rollback": "move pure overlay helpers back; controller state does not move in this step.",
    },
    {
        "step": 4,
        "name": "extract datashader point overlays",
        "target_file": "taichi_earth/overlays/datashader_points.py",
        "move_symbols": [
            "AISDatashaderOverlay",
            "AircraftDatashaderOverlay",
            "DatashaderSamplingPolicy",
            "build_datashader_overlay_config",
            "mask_overlay_to_globe",
        ],
        "update_monolith": [
            "import point overlay classes",
            "projection and provider refresh stay in controller",
        ],
        "rollback": "restore overlay classes into monolith; no DB/socket code should have moved.",
    },
]


def first_extraction_execution_plan_snapshot() -> list[dict]:
    return [dict(item) for item in FIRST_EXTRACTION_EXECUTION_PLAN]


def first_extraction_execution_plan_text() -> str:
    lines = [
        "First extraction execution plan",
        "",
        "Purpose: concrete, reversible order for the first physical module split.",
        "Verification commands are listed for later use only; they are not run by this automation.",
        "",
    ]
    for item in FIRST_EXTRACTION_EXECUTION_PLAN:
        lines.append(f"{item['step']}. {item['name']}")
        lines.append(f"- target file: {item['target_file']}")
        lines.append("- move symbols:")
        for symbol in item["move_symbols"]:
            lines.append(f"  - {symbol}")
        lines.append("- monolith updates:")
        for update in item["update_monolith"]:
            lines.append(f"  - {update}")
        lines.append(f"- rollback: {item['rollback']}")
        lines.append("")
    lines.extend(
        [
            "Suggested verification after user approval:",
            "- python -m py_compile taichi_global_bathymetry.py",
            "- launch one small-window Qt runtime pass",
            "- write provider manifest bundle once",
            "- inspect handoff snapshot for missing module API entries",
        ]
    )
    return "\n".join(lines).rstrip()


FIRST_EXTRACTION_READINESS_PACKET = {
    "target_file": "taichi_earth/contracts/provider_manifests.py",
    "purpose": "Prepare the lowest-risk physical split without moving code during the no-validation automation window.",
    "candidate_status": "prepared-not-extracted",
    "move_symbols": [
        "provider_manifest_templates",
        "provider_manifest_templates_text",
        "dedupe_provider_manifests",
        "collect_provider_manifest_bundle",
        "provider_manifest_bundle_text",
        "write_provider_manifest_bundle",
        "provider_manifests_module_api_snapshot",
        "provider_manifests_module_api_text",
    ],
    "keep_in_controller_adapter": [
        "controller method wrappers that read basemap_lod",
        "cache write path selection",
        "handoff snapshot aggregation",
    ],
    "allowed_imports": ["json", "pathlib", "typing"],
    "forbidden_imports": ["PyQt", "vispy", "taichi", "datashader", "network clients", "database clients"],
    "shadow_mode_steps": [
        "create provider_manifests.py with pure functions only",
        "temporarily keep monolith functions as wrappers",
        "compare handoff/provider manifest JSON after validation is allowed",
        "remove monolith implementations only after wrapper parity is proven",
    ],
    "preconditions": [
        "syntax/import smoke is explicitly allowed and passes",
        "provider manifests API is visible from toolbar",
        "pre-validation evidence plan has been reviewed",
        "known active_goal_gate_lod_layer_count_contract risk is understood or fixed",
    ],
    "rollback_steps": [
        "restore monolith provider manifest helper definitions",
        "remove imports from taichi_earth/contracts/provider_manifests.py",
        "keep generated cache JSON unless the user asks to delete artifacts",
    ],
}


def first_extraction_readiness_packet_snapshot() -> dict:
    packet = dict(FIRST_EXTRACTION_READINESS_PACKET)
    packet["module_api"] = provider_manifests_module_api_snapshot()
    packet["execution_plan"] = first_extraction_execution_plan_snapshot()
    packet["validation_evidence_plan_ids"] = [
        item["id"] for item in PRE_VALIDATION_EVIDENCE_PLAN
    ]
    packet["runtime_verification"] = "not-run"
    return packet


def first_extraction_readiness_packet_text() -> str:
    packet = first_extraction_readiness_packet_snapshot()
    lines = [
        "First extraction readiness packet",
        "",
        f"- target file: {packet['target_file']}",
        f"- purpose: {packet['purpose']}",
        f"- status: {packet['candidate_status']}",
        f"- runtime verification: {packet['runtime_verification']}",
        "",
        "Move symbols:",
    ]
    for name in packet["move_symbols"]:
        lines.append(f"- {name}")
    lines.append("")
    lines.append("Keep in controller adapter:")
    for item in packet["keep_in_controller_adapter"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append(f"Allowed imports: {', '.join(packet['allowed_imports'])}")
    lines.append(f"Forbidden imports: {', '.join(packet['forbidden_imports'])}")
    lines.append("")
    lines.append("Shadow-mode steps:")
    for item in packet["shadow_mode_steps"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Preconditions:")
    for item in packet["preconditions"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Rollback steps:")
    for item in packet["rollback_steps"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Validation evidence gates:")
    for gate_id in packet["validation_evidence_plan_ids"]:
        lines.append(f"- {gate_id}")
    return "\n".join(lines).rstrip()


def extraction_readiness_packet_index_snapshot() -> dict:
    packets = [
        {
            "id": "provider_manifests",
            "target_file": FIRST_EXTRACTION_READINESS_PACKET["target_file"],
            "status": FIRST_EXTRACTION_READINESS_PACKET["candidate_status"],
            "move_symbol_count": len(FIRST_EXTRACTION_READINESS_PACKET["move_symbols"]),
            "priority": 1,
            "depends_on": [],
            "risk_id": "first_extraction_readiness_packet_stale_contract",
        },
        {
            "id": "style_profiles",
            "target_file": STYLE_PROFILES_EXTRACTION_READINESS_PACKET["target_file"],
            "status": STYLE_PROFILES_EXTRACTION_READINESS_PACKET["candidate_status"],
            "move_symbol_count": len(STYLE_PROFILES_EXTRACTION_READINESS_PACKET["move_symbols"]),
            "priority": 2,
            "depends_on": ["provider_manifests"],
            "risk_id": "style_profiles_extraction_readiness_packet_stale_contract",
        },
        {
            "id": "lod_pipeline",
            "target_file": LOD_PIPELINE_EXTRACTION_READINESS_PACKET["target_file"],
            "status": LOD_PIPELINE_EXTRACTION_READINESS_PACKET["candidate_status"],
            "move_symbol_count": len(LOD_PIPELINE_EXTRACTION_READINESS_PACKET["move_symbols"]),
            "priority": 3,
            "depends_on": ["provider_manifests", "style_profiles"],
            "risk_id": "lod_pipeline_extraction_readiness_packet_stale_contract",
        },
        {
            "id": "hydrology_provider",
            "target_file": HYDROLOGY_PROVIDER_EXTRACTION_READINESS_PACKET["target_file"],
            "status": HYDROLOGY_PROVIDER_EXTRACTION_READINESS_PACKET["candidate_status"],
            "move_symbol_count": len(HYDROLOGY_PROVIDER_EXTRACTION_READINESS_PACKET["move_symbols"]),
            "priority": 4,
            "depends_on": ["provider_manifests", "lod_pipeline"],
            "risk_id": "hydrology_provider_extraction_readiness_packet_stale_contract",
        },
        {
            "id": "vector_lines",
            "target_file": VECTOR_LINES_EXTRACTION_READINESS_PACKET["target_file"],
            "status": VECTOR_LINES_EXTRACTION_READINESS_PACKET["candidate_status"],
            "move_symbol_count": len(VECTOR_LINES_EXTRACTION_READINESS_PACKET["move_symbols"]),
            "priority": 5,
            "depends_on": ["style_profiles", "lod_pipeline", "hydrology_provider"],
            "risk_id": "vector_lines_extraction_readiness_packet_stale_contract",
        },
        {
            "id": "datashader_points",
            "target_file": DATASHADER_POINTS_EXTRACTION_READINESS_PACKET["target_file"],
            "status": DATASHADER_POINTS_EXTRACTION_READINESS_PACKET["candidate_status"],
            "move_symbol_count": len(DATASHADER_POINTS_EXTRACTION_READINESS_PACKET["move_symbols"]),
            "priority": 6,
            "depends_on": ["style_profiles", "lod_pipeline"],
            "risk_id": "datashader_points_extraction_readiness_packet_stale_contract",
        },
        {
            "id": "render_core_ocean_material",
            "target_file": RENDER_CORE_OCEAN_MATERIAL_EXTRACTION_READINESS_PACKET["target_file"],
            "status": RENDER_CORE_OCEAN_MATERIAL_EXTRACTION_READINESS_PACKET["candidate_status"],
            "move_symbol_count": len(RENDER_CORE_OCEAN_MATERIAL_EXTRACTION_READINESS_PACKET["move_symbols"]),
            "priority": 8,
            "depends_on": ["style_profiles", "lod_pipeline", "ocean_condition_provider"],
            "risk_id": "render_core_ocean_material_extraction_readiness_packet_stale_contract",
        },
        {
            "id": "qt_controller_facade",
            "target_file": QT_CONTROLLER_FACADE_EXTRACTION_READINESS_PACKET["target_file"],
            "status": QT_CONTROLLER_FACADE_EXTRACTION_READINESS_PACKET["candidate_status"],
            "move_symbol_count": len(QT_CONTROLLER_FACADE_EXTRACTION_READINESS_PACKET["move_symbols"]),
            "priority": 9,
            "depends_on": [
                "provider_manifests",
                "style_profiles",
                "lod_pipeline",
                "hydrology_provider",
                "ocean_condition_provider",
                "datashader_points",
                "vector_lines",
                "render_core_ocean_material",
            ],
            "risk_id": "qt_controller_facade_extraction_readiness_packet_stale_contract",
        },
        {
            "id": "qt_main_window",
            "target_file": QT_MAIN_WINDOW_EXTRACTION_READINESS_PACKET["target_file"],
            "status": QT_MAIN_WINDOW_EXTRACTION_READINESS_PACKET["candidate_status"],
            "move_symbol_count": len(QT_MAIN_WINDOW_EXTRACTION_READINESS_PACKET["move_symbols"]),
            "priority": 10,
            "depends_on": ["qt_controller_facade"],
            "risk_id": "qt_main_window_extraction_readiness_packet_stale_contract",
        },
        {
            "id": "ocean_condition_provider",
            "target_file": OCEAN_CONDITION_PROVIDER_EXTRACTION_READINESS_PACKET["target_file"],
            "status": OCEAN_CONDITION_PROVIDER_EXTRACTION_READINESS_PACKET["candidate_status"],
            "move_symbol_count": len(OCEAN_CONDITION_PROVIDER_EXTRACTION_READINESS_PACKET["move_symbols"]),
            "priority": 7,
            "depends_on": ["provider_manifests", "style_profiles", "lod_pipeline"],
            "risk_id": "ocean_condition_provider_extraction_readiness_packet_stale_contract",
        },
    ]
    return {
        "contract": "Index of prepared extraction readiness packets. This is an ordering and risk map only; it does not prove extraction or runtime parity.",
        "runtime_verification": "not-run",
        "physical_split": "not-started",
        "packet_count": len(packets),
        "total_move_symbol_count": sum(item["move_symbol_count"] for item in packets),
        "packets": sorted(packets, key=lambda item: item["priority"]),
        "known_index_blockers": [
            "active_goal_gate_lod_layer_count_contract",
            "runtime_validation",
        ],
        "remaining_packet_candidates": [],
    }


def extraction_readiness_packet_index_text() -> str:
    snapshot = extraction_readiness_packet_index_snapshot()
    lines = [
        "Extraction readiness packet index",
        "",
        f"- contract: {snapshot['contract']}",
        f"- runtime verification: {snapshot['runtime_verification']}",
        f"- physical split: {snapshot['physical_split']}",
        f"- packet count: {snapshot['packet_count']}",
        f"- total move symbols: {snapshot['total_move_symbol_count']}",
        "",
        "Packets:",
    ]
    for packet in snapshot["packets"]:
        deps = ", ".join(packet["depends_on"]) or "none"
        lines.append(f"- {packet['priority']}. {packet['id']} -> {packet['target_file']}")
        lines.append(f"  status: {packet['status']}")
        lines.append(f"  move symbols: {packet['move_symbol_count']}")
        lines.append(f"  depends on: {deps}")
        lines.append(f"  risk id: {packet['risk_id']}")
    lines.append("")
    lines.append("Known index blockers:")
    for blocker in snapshot["known_index_blockers"]:
        lines.append(f"- {blocker}")
    lines.append("")
    lines.append("Remaining packet candidates:")
    for candidate in snapshot["remaining_packet_candidates"]:
        lines.append(f"- {candidate}")
    return "\n".join(lines).rstrip()


def active_goal_extraction_seam_matrix_snapshot() -> dict:
    packet_index = extraction_readiness_packet_index_snapshot()
    packet_ids = {packet["id"] for packet in packet_index["packets"]}
    seams = [
        {
            "id": "hydrology_basic_provider",
            "packet_id": "hydrology_provider",
            "target_file": HYDROLOGY_PROVIDER_EXTRACTION_READINESS_PACKET["target_file"],
            "owner": "static-geodata",
            "boundary": "Hydrology provider owns source/LOD/cache decisions and emits normalized lon/lat vector geometry only.",
            "upstream": ["provider_manifests", "lod_pipeline"],
            "downstream": ["vector_lines", "qt_controller_facade"],
            "controller_adapter_keeps": ["reload_hydrology_layer", "dirty flags", "layer visibility", "toolbar diagnostics"],
        },
        {
            "id": "lod_hook_pipeline",
            "packet_id": "lod_pipeline",
            "target_file": LOD_PIPELINE_EXTRACTION_READINESS_PACKET["target_file"],
            "owner": "projection-core",
            "boundary": "LOD pipeline owns scale/projection decisions; providers and renderers consume decisions without owning viewport math.",
            "upstream": ["provider_manifests", "style_profiles"],
            "downstream": ["hydrology_provider", "ocean_condition_provider", "datashader_points", "vector_lines"],
            "controller_adapter_keeps": ["current_km_per_pixel", "basemap_lod updates", "render dirty orchestration"],
        },
        {
            "id": "ocean_condition_provider",
            "packet_id": "ocean_condition_provider",
            "target_file": OCEAN_CONDITION_PROVIDER_EXTRACTION_READINESS_PACKET["target_file"],
            "owner": "ocean-data",
            "boundary": "Ocean provider owns IO and normalization; render_core receives scalar sea-state fields only.",
            "upstream": ["provider_manifests", "lod_pipeline"],
            "downstream": ["render_core_ocean_material", "qt_controller_facade"],
            "controller_adapter_keeps": ["source selection", "sample lat/lon", "refresh timing", "cached condition state"],
        },
        {
            "id": "ocean_material_render_core",
            "packet_id": "render_core_ocean_material",
            "target_file": RENDER_CORE_OCEAN_MATERIAL_EXTRACTION_READINESS_PACKET["target_file"],
            "owner": "render-core",
            "boundary": "Ocean material policy maps normalized sea state and style intent into scalar uniforms without provider IO.",
            "upstream": ["ocean_condition_provider", "style_profiles", "lod_pipeline"],
            "downstream": ["qt_controller_facade"],
            "controller_adapter_keeps": ["globe.render argument assembly", "Taichi renderer instance", "time_seconds"],
        },
        {
            "id": "style_renderer_entries",
            "packet_id": "style_profiles",
            "target_file": STYLE_PROFILES_EXTRACTION_READINESS_PACKET["target_file"],
            "owner": "style-contracts",
            "boundary": "Style profiles own visual intent; renderers consume resolved style data and must not call UI or providers.",
            "upstream": ["provider_manifests"],
            "downstream": ["vector_lines", "datashader_points", "render_core_ocean_material", "qt_controller_facade"],
            "controller_adapter_keeps": ["selected style profile", "overlay renderer set_style_profile calls", "final post-process call site"],
        },
        {
            "id": "qt_controller_facade",
            "packet_id": "qt_controller_facade",
            "target_file": QT_CONTROLLER_FACADE_EXTRACTION_READINESS_PACKET["target_file"],
            "owner": "ui-boundary",
            "boundary": "Qt calls declared facade methods only; provider internals, mutable caches, and renderer instances stay behind the controller.",
            "upstream": ["hydrology_provider", "lod_pipeline", "ocean_condition_provider", "render_core_ocean_material", "style_profiles"],
            "downstream": ["qt_main_window"],
            "controller_adapter_keeps": ["state mutation", "render scheduling", "diagnostic snapshots", "export methods"],
        },
    ]
    for seam in seams:
        seam["packet_prepared"] = seam["packet_id"] in packet_ids
    missing_packet_ids = sorted({seam["packet_id"] for seam in seams if not seam["packet_prepared"]})
    return {
        "contract": "Active-goal extraction seam matrix narrows the next split boundaries for hydrology basic, LOD hooks, Taichi ocean material ports, style renderer entries, and Qt handoff.",
        "runtime_verification": "not-run",
        "physical_split": "not-started",
        "seam_count": len(seams),
        "ready": not missing_packet_ids,
        "missing_packet_ids": missing_packet_ids,
        "known_blockers": list(packet_index.get("known_index_blockers", [])),
        "seams": seams,
    }


def active_goal_extraction_seam_matrix_text() -> str:
    matrix = active_goal_extraction_seam_matrix_snapshot()
    lines = [
        "Active goal extraction seam matrix",
        "",
        f"- runtime verification: {matrix['runtime_verification']}",
        f"- physical split: {matrix['physical_split']}",
        f"- seam count: {matrix['seam_count']}",
        f"- ready: {matrix['ready']}",
        f"- missing packet ids: {', '.join(matrix['missing_packet_ids']) or 'none'}",
        "",
        "Seams:",
    ]
    for seam in matrix["seams"]:
        lines.append(f"- {seam['id']} -> {seam['target_file']}")
        lines.append(f"  owner: {seam['owner']}")
        lines.append(f"  packet prepared: {seam['packet_prepared']}")
        lines.append(f"  upstream: {', '.join(seam['upstream']) or 'none'}")
        lines.append(f"  downstream: {', '.join(seam['downstream']) or 'none'}")
        lines.append(f"  boundary: {seam['boundary']}")
    lines.append("")
    lines.append("Known blockers:")
    for blocker in matrix["known_blockers"]:
        lines.append(f"- {blocker}")
    return "\n".join(lines).rstrip()


CACHE_GOVERNANCE_MATRIX = [
    {
        "id": "data_fetch_events",
        "storage": "memory",
        "owner": "contracts/project_handoff.py",
        "producer": "record_data_fetch_event",
        "cleanup_policy": "bounded-list",
        "automatic_cleanup": True,
        "evidence": "DATA_FETCH_EVENTS is truncated to DATA_FETCH_MAX_EVENTS.",
        "future_boundary": "contracts/cache_governance.py should own event retention metadata only.",
    },
    {
        "id": "vector_overlay_cache",
        "storage": "memory",
        "owner": "controller adapter",
        "producer": "_cache_vector_overlay",
        "cleanup_policy": "bounded-eviction",
        "automatic_cleanup": True,
        "evidence": "vector_overlay_cache_order evicts old keys beyond _vector_cache_limit().",
        "future_boundary": "controller keeps cache ownership until vector overlay parity is runtime-verified.",
    },
    {
        "id": "ocean_condition_cached_conditions",
        "storage": "memory",
        "owner": "data_sources/ocean_condition_provider.py",
        "producer": "OceanConditionProvider.read",
        "cleanup_policy": "refresh-window-and-source-reset",
        "automatic_cleanup": True,
        "evidence": "cached_conditions is reused inside refresh window and reset by ocean source/sample setters.",
        "future_boundary": "provider owns cache invalidation; render_core consumes copied scalar state.",
    },
    {
        "id": "topography_cache",
        "storage": "disk",
        "owner": "data_sources/basemap_provider.py",
        "producer": "load_topography",
        "cleanup_policy": "manual-only",
        "automatic_cleanup": False,
        "evidence": "topography .npy files are reused by path and not deleted by the app.",
        "future_boundary": "provider manifests should record size/source/version before adding cleanup.",
    },
    {
        "id": "surface_mask_cache",
        "storage": "disk",
        "owner": "data_sources/surface_mask_provider.py",
        "producer": "load_land_mask",
        "cleanup_policy": "manual-only",
        "automatic_cleanup": False,
        "evidence": "land/water mask .npy files are reused by source/topography/sea-level key.",
        "future_boundary": "mask provider owns cache identity; renderer receives arrays only.",
    },
    {
        "id": "ice_forest_mask_cache",
        "storage": "disk",
        "owner": "data_sources/environment_masks.py",
        "producer": "load_ice_mask/load_forest_density",
        "cleanup_policy": "manual-only",
        "automatic_cleanup": False,
        "evidence": "ice and forest masks are cached on disk with no TTL or size cap.",
        "future_boundary": "environment providers should share cache manifest fields before cleanup.",
    },
    {
        "id": "stars_cache",
        "storage": "disk",
        "owner": "data_sources/star_catalog_provider.py",
        "producer": "load_star_catalog",
        "cleanup_policy": "manual-only",
        "automatic_cleanup": False,
        "evidence": "star cache is loaded from .npy or imported from project cache and persisted.",
        "future_boundary": "star provider owns static catalog cache; render_core receives star buffers.",
    },
    {
        "id": "vector_geojson_cache",
        "storage": "disk",
        "owner": "data_sources/vector_provider.py",
        "producer": "load_vector_geojson_from_source",
        "cleanup_policy": "manual-only",
        "automatic_cleanup": False,
        "evidence": "downloaded vector GeoJSON is written under CACHE_DIR and reused by name.",
        "future_boundary": "hydrology/boundary providers own source cache; overlays own no provider files.",
    },
]


def cache_governance_matrix_snapshot() -> dict:
    items = [dict(item) for item in CACHE_GOVERNANCE_MATRIX]
    missing_contract = [
        item["id"] for item in items
        if not item.get("owner") or not item.get("cleanup_policy") or not item.get("future_boundary")
    ]
    memory_items = [item for item in items if item["storage"] == "memory"]
    disk_items = [item for item in items if item["storage"] == "disk"]
    manual_only_disk = [
        item["id"] for item in disk_items
        if item.get("cleanup_policy") == "manual-only"
    ]
    return {
        "contract": "Cache governance matrix documents memory and disk cache ownership before adding any destructive cleanup behavior.",
        "runtime_verification": "not-run",
        "destructive_cleanup": "not-implemented",
        "item_count": len(items),
        "memory_cache_count": len(memory_items),
        "disk_cache_count": len(disk_items),
        "automatic_cleanup_count": sum(1 for item in items if item.get("automatic_cleanup")),
        "manual_only_disk_cache_ids": manual_only_disk,
        "missing_contract": missing_contract,
        "ready": not missing_contract,
        "items": items,
    }


def cache_governance_matrix_text() -> str:
    matrix = cache_governance_matrix_snapshot()
    lines = [
        "Cache governance matrix",
        "",
        f"- runtime verification: {matrix['runtime_verification']}",
        f"- destructive cleanup: {matrix['destructive_cleanup']}",
        f"- item count: {matrix['item_count']}",
        f"- memory caches: {matrix['memory_cache_count']}",
        f"- disk caches: {matrix['disk_cache_count']}",
        f"- automatic cleanup policies: {matrix['automatic_cleanup_count']}",
        f"- manual-only disk caches: {', '.join(matrix['manual_only_disk_cache_ids']) or 'none'}",
        f"- ready: {matrix['ready']}",
        "",
        "Items:",
    ]
    for item in matrix["items"]:
        lines.append(
            f"- {item['id']}: storage={item['storage']}; owner={item['owner']}; "
            f"policy={item['cleanup_policy']}; automatic={item['automatic_cleanup']}"
        )
        lines.append(f"  boundary: {item['future_boundary']}")
    if matrix["missing_contract"]:
        lines.append("")
        lines.append("Missing contract:")
        for item_id in matrix["missing_contract"]:
            lines.append(f"- {item_id}")
    return "\n".join(lines).rstrip()


def active_goal_known_issue_matrix_snapshot() -> dict:
    issues = [
        {
            "id": "active_goal_gate_lod_layer_count_contract",
            "status": "open",
            "area": "LOD hook",
            "severity": "contract-drift",
            "summary": "Active goal readiness gate expects lod_layer_decision_matrix_snapshot()['layer_count'], but the matrix currently does not emit that field.",
            "impact": "LOD matrix shape check is advisory and can create a false contract blocker until the field contract is aligned.",
            "next_action": "User decision: add layer_count to lod_layer_decision_matrix_snapshot or compute the expected count inside active_goal_readiness_gate_snapshot.",
            "requires_runtime": False,
            "requires_user_decision": True,
        },
        {
            "id": "runtime_validation_not_run",
            "status": "open",
            "area": "completion gate",
            "severity": "unverified",
            "summary": "Syntax/import/runtime validation has intentionally not been run during this automation window.",
            "impact": "Completion cannot be claimed even when contracts look complete.",
            "next_action": "When user permits: run py_compile/import smoke and one small Qt render pass.",
            "requires_runtime": True,
            "requires_user_decision": True,
        },
        {
            "id": "cache_cleanup_not_implemented",
            "status": "open",
            "area": "cache governance",
            "severity": "design-gap",
            "summary": "Cache governance documents memory/disk cache ownership but does not implement destructive cleanup.",
            "impact": "Disk caches remain manual-only and should not be deleted implicitly.",
            "next_action": "Design provider-cache cleanup only after cache manifests include size/source/version policy.",
            "requires_runtime": False,
            "requires_user_decision": True,
        },
        {
            "id": "physical_split_not_started",
            "status": "open",
            "area": "decoupling preparation",
            "severity": "planned-work",
            "summary": "Extraction packets and seam matrices are prepared, but no module has been physically split out of the monolith.",
            "impact": "Current work improves handoff and contracts, not package/module structure.",
            "next_action": "After validation is allowed, start with contracts/provider_manifests.py in shadow mode.",
            "requires_runtime": True,
            "requires_user_decision": True,
        },
        {
            "id": "ocean_lod_resampling_runtime_unverified",
            "status": "open",
            "area": "Taichi ocean material",
            "severity": "runtime-risk",
            "summary": "Ocean material LOD resampling contract is documented, but behavior depends on the globe render branch.",
            "impact": "Ocean condition changes across LOD should be visually/runtime checked before extraction.",
            "next_action": "Inspect Ocean condition material binding and render one small LOD transition pass when validation is allowed.",
            "requires_runtime": True,
            "requires_user_decision": False,
        },
        {
            "id": "preview_launch_not_evidence",
            "status": "open",
            "area": "runtime preview",
            "severity": "weak-evidence",
            "summary": "The app was launched on request for visual inspection, but no runtime output or visual result was captured as evidence here.",
            "impact": "That launch should not be treated as a passing validation result.",
            "next_action": "If the preview failed or hung, inspect terminal output only if the user asks.",
            "requires_runtime": False,
            "requires_user_decision": True,
        },
    ]
    return {
        "contract": "Known issue matrix keeps no-validation risks explicit so the active goal is not mistaken for completed/validated work.",
        "runtime_verification": "not-run",
        "issue_count": len(issues),
        "open_count": sum(1 for issue in issues if issue["status"] == "open"),
        "requires_runtime_count": sum(1 for issue in issues if issue["requires_runtime"]),
        "requires_user_decision_count": sum(1 for issue in issues if issue["requires_user_decision"]),
        "issues": issues,
    }


def active_goal_known_issue_matrix_text() -> str:
    matrix = active_goal_known_issue_matrix_snapshot()
    lines = [
        "Active goal known issue matrix",
        "",
        f"- runtime verification: {matrix['runtime_verification']}",
        f"- issue count: {matrix['issue_count']}",
        f"- open: {matrix['open_count']}",
        f"- requires runtime: {matrix['requires_runtime_count']}",
        f"- requires user decision: {matrix['requires_user_decision_count']}",
        "",
        "Issues:",
    ]
    for issue in matrix["issues"]:
        lines.append(f"- {issue['id']} [{issue['severity']}] status={issue['status']}; area={issue['area']}")
        lines.append(f"  summary: {issue['summary']}")
        lines.append(f"  next: {issue['next_action']}")
    return "\n".join(lines).rstrip()


MODULE_IMPORT_BOUNDARY_MATRIX = {
    "contracts/provider_manifests.py": {
        "may_import": ["stdlib"],
        "must_not_import": ["qt_ui", "render_core", "projection", "overlays", "data_sources"],
        "rule": "Pure manifest builders are the root contract layer and must not depend on app/runtime modules.",
    },
    "style_profiles.py": {
        "may_import": ["stdlib", "numpy"],
        "must_not_import": ["qt_ui", "data_sources", "render_core/taichi_globe.py"],
        "rule": "Style returns intents and post-process frames; renderers consume style, style must not call renderers.",
    },
    "projection/lod_pipeline.py": {
        "may_import": ["stdlib", "style_profiles optional"],
        "must_not_import": ["qt_ui", "render_core", "data_sources provider IO", "overlays datashader canvas"],
        "rule": "LOD pipeline emits decisions only and must not load provider data or allocate renderer outputs.",
    },
    "data_sources/hydrology_provider.py": {
        "may_import": ["stdlib", "contracts/provider_manifests.py"],
        "must_not_import": ["qt_ui", "render_core", "overlays/vector_lines.py", "AIS/ADS-B feeds"],
        "rule": "Hydrology provider owns source/provenance decisions, not screen-space drawing.",
    },
    "data_sources/ocean_condition_provider.py": {
        "may_import": ["stdlib", "pandas optional", "contracts/provider_manifests.py"],
        "must_not_import": ["qt_ui", "render_core", "taichi", "overlays"],
        "rule": "Ocean provider normalizes source data; render_core resolves material uniforms.",
    },
    "render_core/ocean_material.py": {
        "may_import": ["stdlib", "style_profiles.py"],
        "must_not_import": ["qt_ui", "data_sources", "urllib", "database clients"],
        "rule": "Ocean material adapter consumes normalized dicts and never performs provider IO.",
    },
    "overlays/vector_lines.py": {
        "may_import": ["stdlib", "numpy", "PIL optional", "style_profiles.py"],
        "must_not_import": ["qt_ui", "render_core", "data_sources provider decisions"],
        "rule": "Vector overlays project/draw lines only; controller owns cache and provider selection.",
    },
    "overlays/datashader_points.py": {
        "may_import": ["stdlib", "numpy", "pandas", "datashader", "style_profiles.py"],
        "must_not_import": ["qt_ui", "render_core", "data_sources sockets/db clients"],
        "rule": "Datashader overlays consume projected screen-space points only.",
    },
    "qt_ui/controller_facade.py": {
        "may_import": ["controller public methods", "contracts text helpers"],
        "must_not_import": ["raw Taichi fields", "provider private loaders", "database/socket client instances"],
        "rule": "Controller facade is the only surface Qt should use for state mutation, diagnostics, exports, and render requests.",
    },
    "qt_ui/main_window.py": {
        "may_import": ["controller facade", "contracts text helpers"],
        "must_not_import": ["taichi kernels directly", "provider private loaders"],
        "rule": "Qt orchestrates controls and display; it should call controller methods rather than mutate provider internals.",
    },
}


def module_import_boundary_matrix_snapshot() -> dict:
    return {name: dict(spec) for name, spec in MODULE_IMPORT_BOUNDARY_MATRIX.items()}


def module_import_boundary_matrix_text() -> str:
    lines = [
        "Module import boundary matrix",
        "",
        "Purpose: prevent circular dependencies during the first physical split.",
        "Rule: lower-level contracts/providers/renderers should not import Qt or each other through runtime state.",
        "",
    ]
    for module_path, spec in MODULE_IMPORT_BOUNDARY_MATRIX.items():
        lines.append(f"- {module_path}")
        lines.append(f"  may import: {', '.join(spec['may_import'])}")
        lines.append(f"  must not import: {', '.join(spec['must_not_import'])}")
        lines.append(f"  rule: {spec['rule']}")
    return "\n".join(lines)


def module_contract_coverage_snapshot() -> dict:
    api_paths = set(module_api_registry_snapshot().keys())
    extraction_targets = {
        str(unit.get("target", "")).replace("taichi_earth/", "")
        for unit in decoupling_extraction_units_snapshot()
    }
    boundary_paths = set(MODULE_IMPORT_BOUNDARY_MATRIX.keys())
    all_paths = sorted(api_paths | extraction_targets | boundary_paths)
    coverage = {}
    for path in all_paths:
        coverage[path] = {
            "in_module_api_registry": path in api_paths,
            "in_extraction_units": path in extraction_targets,
            "in_import_boundary_matrix": path in boundary_paths,
            "state": "aligned" if path in api_paths and path in boundary_paths else "needs-review",
        }
    return {
        "contract": "Module contract coverage compares module API registry, extraction execution units, and import boundary matrix.",
        "coverage": coverage,
        "needs_review": [path for path, item in coverage.items() if item["state"] != "aligned"],
        "note": "Not every module must be in extraction_units yet; API registry and import boundary coverage should stay aligned.",
    }


def module_contract_coverage_text() -> str:
    snapshot = module_contract_coverage_snapshot()
    lines = [
        "Module contract coverage",
        "",
        f"- contract: {snapshot['contract']}",
        f"- needs review: {len(snapshot['needs_review'])}",
        f"- note: {snapshot['note']}",
        "",
    ]
    for path, item in snapshot["coverage"].items():
        lines.append(
            f"- {path}: {item['state']}; "
            f"api={item['in_module_api_registry']}; "
            f"extraction={item['in_extraction_units']}; "
            f"imports={item['in_import_boundary_matrix']}"
        )
    return "\n".join(lines)


VALIDATION_AND_ROLLBACK_PLAN = [
    {
        "stage": "syntax/import smoke",
        "when": "after user explicitly permits validation",
        "commands": [
            "python -m py_compile taichi_global_bathymetry.py",
        ],
        "evidence": [
            "module compiles without SyntaxError/NameError at import-time constant initialization",
        ],
        "rollback": [
            "revert the last small patch group only",
            "prefer restoring helpers/constants into monolith rather than deleting runtime code paths",
        ],
    },
    {
        "stage": "small-window runtime pass",
        "when": "after syntax/import smoke passes and user permits launch",
        "commands": [
            "python taichi_global_bathymetry.py --width 960 --height 540 --topo-step 32 --style-profile scientific",
        ],
        "evidence": [
            "Qt window opens",
            "globe, stars, water/land, AIS overlay path still render",
            "toolbar contract buttons open text dialogs without crashing",
        ],
        "rollback": [
            "disable newest toolbar entry if crash is UI-only",
            "restore previous render helper call site if crash is in overlay render path",
        ],
    },
    {
        "stage": "contract snapshot write",
        "when": "after one runtime pass and user permits writing cache artifacts",
        "commands": [
            "use toolbar: Write handoff snapshot",
            "use toolbar: Write provider manifests",
        ],
        "evidence": [
            "UTF-8 JSON files are written",
            "module_api_registry and pre_extraction_readiness_audit are present",
            "provider_manifest_bundle is serializable",
        ],
        "rollback": [
            "delete generated cache JSON only",
            "do not revert renderer/runtime code for snapshot write failures until serialization field is identified",
        ],
    },
    {
        "stage": "first physical extraction",
        "when": "after user explicitly approves actual split",
        "commands": [
            "create taichi_earth/contracts/provider_manifests.py",
            "replace monolith definitions with imports",
            "run syntax/import smoke again if user permits",
        ],
        "evidence": [
            "monolith imports provider manifest helpers from new module",
            "no Qt/Taichi/Datashader imports in contracts/provider_manifests.py",
            "handoff snapshot still includes provider manifests API",
        ],
        "rollback": [
            "remove new module import lines",
            "restore local helper definitions",
            "leave generated cache artifacts untouched unless user asks",
        ],
    },
]


def validation_and_rollback_plan_snapshot() -> list[dict]:
    return [dict(item) for item in VALIDATION_AND_ROLLBACK_PLAN]


def validation_and_rollback_plan_text() -> str:
    lines = [
        "Validation and rollback plan",
        "",
        "Purpose: define the smallest safe evidence path once validation is allowed.",
        "Current automation rule: no validation commands are run unless the user explicitly asks.",
        "",
    ]
    for item in VALIDATION_AND_ROLLBACK_PLAN:
        lines.append(f"[{item['stage']}]")
        lines.append(f"- when: {item['when']}")
        lines.append("- commands:")
        for command in item["commands"]:
            lines.append(f"  - {command}")
        lines.append("- evidence:")
        for evidence in item["evidence"]:
            lines.append(f"  - {evidence}")
        lines.append("- rollback:")
        for rollback in item["rollback"]:
            lines.append(f"  - {rollback}")
        lines.append("")
    return "\n".join(lines).rstrip()


PRE_VALIDATION_EVIDENCE_PLAN = [
    {
        "id": "syntax_import_gate",
        "scope": "whole monolith",
        "command": "python -m py_compile taichi_global_bathymetry.py",
        "evidence": [
            "no SyntaxError",
            "no import-time NameError from contract constants or toolbar/controller methods",
        ],
        "proves": "recent contract helpers and diagnostics are at least import-safe",
        "does_not_prove": "Qt buttons, render output, provider IO, or Taichi kernel behavior",
        "rollback_hint": "revert the smallest recent contract/helper block that causes import-time failure",
    },
    {
        "id": "hydrology_basic_diagnostic_gate",
        "scope": "hydrology basic",
        "command": "open Qt toolbar: Hydrology basic readiness",
        "evidence": [
            "lakes and rivers appear in layers",
            "contract_ready is true for both hydrology layers",
            "loaded_count is checked separately from contract_ready_count",
        ],
        "proves": "source/render/strictness controls are exposed and line-data loading state is visible",
        "does_not_prove": "visual correctness of simplification, color, opacity, or source scientific quality",
        "rollback_hint": "fall back from readiness matrix to hydrology_control_snapshot for the failing layer",
    },
    {
        "id": "lod_hook_diagnostic_gate",
        "scope": "LOD hook",
        "command": "open Qt toolbar: LOD hook pipeline and LOD layer decision matrix",
        "evidence": [
            "basemap LOD decision is present",
            "hydrology and boundary source/render sections are present",
            "ocean spatial sampling is present",
        ],
        "proves": "LOD decisions are inspectable before renderers run",
        "does_not_prove": "active_goal_readiness_gate LOD shape check until the layer_count contract is aligned",
        "rollback_hint": "keep lod_hook_pipeline_snapshot and disable only the newer matrix/gate field",
    },
    {
        "id": "ocean_taichi_port_gate",
        "scope": "Taichi ocean material",
        "command": "open Qt toolbar: Ocean Taichi material port",
        "evidence": [
            "kernel_argument_order lists ocean_enabled, wave_strength, roughness, foam, time_seconds",
            "kernel_inputs are scalar values or explicit render-time placeholders",
            "unwired_policy_scalars are listed separately",
        ],
        "proves": "ocean material control has a narrow scalar render-core port",
        "does_not_prove": "Taichi kernel consumes the arguments correctly or visual material output is correct",
        "rollback_hint": "keep ocean_material_control_snapshot and remove only ocean_material_taichi_port_snapshot from toolbar/handoff",
    },
    {
        "id": "small_render_gate",
        "scope": "runtime integration",
        "command": "python taichi_global_bathymetry.py --width 960 --height 540 --topo-step 32 --style-profile scientific",
        "evidence": [
            "Qt window opens",
            "one globe frame renders",
            "diagnostic toolbar entries open without crashing",
            "hydrology, boundary, Datashader, and ocean material toggles do not crash one frame",
        ],
        "proves": "recent controller/facade/diagnostic wiring survives a minimal runtime pass",
        "does_not_prove": "performance, high-zoom correctness, all providers, or all style profiles",
        "rollback_hint": "disable only the toolbar entry or render helper added in the last failing diagnostic area",
    },
]


def pre_validation_evidence_plan_snapshot() -> list[dict]:
    return [dict(item) for item in PRE_VALIDATION_EVIDENCE_PLAN]


def pre_validation_evidence_plan_text() -> str:
    lines = [
        "Pre-validation evidence plan",
        "",
        "Purpose: define the exact evidence needed once validation is allowed, without running validation now.",
        "Current automation rule: no validation commands are run unless the user explicitly asks.",
        "",
    ]
    for item in PRE_VALIDATION_EVIDENCE_PLAN:
        lines.append(f"[{item['id']}] scope={item['scope']}")
        lines.append(f"- command: {item['command']}")
        lines.append("- evidence:")
        for evidence in item["evidence"]:
            lines.append(f"  - {evidence}")
        lines.append(f"- proves: {item['proves']}")
        lines.append(f"- does not prove: {item['does_not_prove']}")
        lines.append(f"- rollback hint: {item['rollback_hint']}")
        lines.append("")
    return "\n".join(lines).rstrip()


UNVERIFIED_RISK_REGISTER = [
    {
        "id": "import_time_name_order",
        "severity": "high",
        "area": "module contract constants",
        "risk": "Some newly added contract constants and text helpers may reference globals before they are defined.",
        "first_check": "python -m py_compile taichi_global_bathymetry.py",
        "likely_fix": "replace import-time dynamic references with fixed contract literals or move the constant below the referenced registry.",
    },
    {
        "id": "toolbar_callable_binding",
        "severity": "medium",
        "area": "Qt toolbar diagnostics",
        "risk": "New toolbar entries call many controller text methods; one missing method name would crash only when the button is clicked.",
        "first_check": "open Qt, click Module API registry / Pre-extraction audit / Validation rollback plan.",
        "likely_fix": "add the missing controller wrapper or bind directly to the pure text function.",
    },
    {
        "id": "snapshot_serialization",
        "severity": "medium",
        "area": "handoff snapshot",
        "risk": "New snapshot sections include nested dicts/lists and tuples; JSON serialization should be checked before relying on generated handoff artifacts.",
        "first_check": "use toolbar: Write handoff snapshot.",
        "likely_fix": "convert tuples to lists or rely on default=str only for non-critical display fields.",
    },
    {
        "id": "datashader_config_runtime",
        "severity": "medium",
        "area": "Datashader overlay helper",
        "risk": "AIS/ADS-B overlays now route through build_datashader_overlay_config; style/color-mode branches need one runtime pass.",
        "first_check": "render with --style-profile scientific and tactical using a small viewport.",
        "likely_fix": "fall back to scientific cmap if a style/color key is missing.",
    },
    {
        "id": "vector_render_params_runtime",
        "severity": "medium",
        "area": "hydrology/boundary vector overlays",
        "risk": "Hydrology and boundary render params were extracted into helpers; opacity/width/color behavior should be visually compared once.",
        "first_check": "toggle lakes/rivers/borders/EEZ layers in Qt.",
        "likely_fix": "restore previous inline parameter expression for the failing layer only.",
    },
    {
        "id": "hydrology_basic_readiness_runtime",
        "severity": "medium",
        "area": "hydrology basic diagnostics",
        "risk": "Hydrology basic readiness matrix separates control readiness from line-data loading, but the loaded counts still need a runtime provider pass before treating lakes/rivers as visually complete.",
        "first_check": "open Qt toolbar: Hydrology basic readiness after initial providers finish loading.",
        "likely_fix": "fix the failing provider decision, loader, or render params for the layer whose readiness stays configured_waiting_for_vectors.",
    },
    {
        "id": "lod_layer_decision_matrix_runtime",
        "severity": "medium",
        "area": "LOD hook diagnostics",
        "risk": "LOD layer decision matrix reads hydrology, boundary, and ocean policy decisions together; one policy return-shape mismatch would appear only when opening the diagnostic panel.",
        "first_check": "open Qt toolbar: LOD layer decision matrix.",
        "likely_fix": "narrow the failing section to raw policy decision output or add a default for the missing key.",
    },
    {
        "id": "ocean_material_taichi_port_runtime",
        "severity": "medium",
        "area": "Taichi ocean material port",
        "risk": "Ocean Taichi material port mirrors the intended globe.render scalar argument order, but kernel/runtime behavior has not been checked after adding the diagnostic contract.",
        "first_check": "open Qt toolbar: Ocean Taichi material port, then render one globe frame.",
        "likely_fix": "align kernel_argument_order, build_ocean_material_uniforms, and the globe.render call arguments.",
    },
    {
        "id": "active_goal_readiness_gate_runtime",
        "severity": "medium",
        "area": "active goal readiness",
        "risk": "Active goal readiness gate aggregates static contract checks and known runtime blockers; it is a handoff aid, not proof that the goal is complete.",
        "first_check": "open Qt toolbar: Active goal readiness gate after syntax/runtime validation is allowed.",
        "likely_fix": "resolve any contract_blockers first, then replace runtime blocker evidence with actual validation results.",
    },
    {
        "id": "active_goal_gate_lod_layer_count_contract",
        "severity": "medium",
        "area": "active goal readiness",
        "risk": "Active goal readiness gate currently expects lod_layer_decision_matrix_snapshot to expose layer_count, but that matrix may only expose hydrology/boundary/ocean sections; the LOD matrix check should not be trusted until the field contract is aligned.",
        "first_check": "inspect Active goal readiness gate and LOD layer decision matrix together.",
        "likely_fix": "add an explicit layer_count to lod_layer_decision_matrix_snapshot or compute the count from hydrology/boundaries/ocean in active_goal_readiness_gate_snapshot.",
    },
    {
        "id": "first_extraction_readiness_packet_stale_contract",
        "severity": "medium",
        "area": "decoupling preparation",
        "risk": "First extraction readiness packet is a planned symbol/dependency contract only; the listed move symbols still need a syntax/runtime-backed parity check before any physical split.",
        "first_check": "compare First extraction readiness packet with Provider manifests API and generated provider manifest bundle after validation is allowed.",
        "likely_fix": "update move_symbols, keep_in_controller_adapter, or shadow-mode steps before creating the new module.",
    },
    {
        "id": "vector_lines_extraction_readiness_packet_stale_contract",
        "severity": "medium",
        "area": "vector overlay decoupling",
        "risk": "Vector lines extraction readiness packet is a planned rendering-boundary contract only; render helper signatures and style/cache coupling still need a runtime-backed parity check before extraction.",
        "first_check": "compare Vector lines extraction readiness with Hydrology basic readiness, LOD layer decision matrix, and one small render pass after validation is allowed.",
        "likely_fix": "move fewer symbols, keep style resolution in the controller adapter, or restore monolith render helper ownership.",
    },
    {
        "id": "lod_pipeline_extraction_readiness_packet_stale_contract",
        "severity": "medium",
        "area": "LOD pipeline decoupling",
        "risk": "LOD pipeline extraction readiness packet is a planned policy-boundary contract only; controller state and provider/render coupling still need syntax/runtime-backed parity checks before extraction.",
        "first_check": "compare LOD pipeline extraction readiness with LOD hook pipeline, LOD layer decision matrix, and one small render pass after validation is allowed.",
        "likely_fix": "move fewer policy classes, keep snapshot methods in the controller adapter, or restore monolith policy ownership.",
    },
    {
        "id": "render_core_ocean_material_extraction_readiness_packet_stale_contract",
        "severity": "medium",
        "area": "Taichi ocean material decoupling",
        "risk": "Render-core ocean material extraction readiness packet is a planned scalar-policy contract only; Taichi kernel argument parity and visual behavior still need syntax/runtime-backed checks before extraction.",
        "first_check": "compare Render ocean extraction readiness with Ocean Taichi material port and one small render pass after validation is allowed.",
        "likely_fix": "move fewer symbols, keep Taichi port assembly in the controller adapter, or restore monolith ocean material policy ownership.",
    },
    {
        "id": "hydrology_provider_extraction_readiness_packet_stale_contract",
        "severity": "medium",
        "area": "hydrology provider decoupling",
        "risk": "Hydrology provider extraction readiness packet is a planned source/strictness-boundary contract only; provider loader behavior and loaded vector counts still need syntax/runtime-backed checks before extraction.",
        "first_check": "compare Hydrology provider extraction readiness with Hydrology basic readiness and one provider-loading runtime pass after validation is allowed.",
        "likely_fix": "move fewer symbols, keep loaders in the controller adapter, or restore monolith hydrology provider ownership.",
    },
    {
        "id": "style_profiles_extraction_readiness_packet_stale_contract",
        "severity": "medium",
        "area": "style profile decoupling",
        "risk": "Style profiles extraction readiness packet is a planned cross-cutting style-boundary contract only; Datashader palettes, vector colors, ocean material modifiers, and post-process behavior still need syntax/runtime-backed parity checks before extraction.",
        "first_check": "compare Style profiles extraction readiness with Hydrology basic readiness, Ocean Taichi material port, Datashader point overlays, and one styled render pass after validation is allowed.",
        "likely_fix": "move fewer symbols, keep post-process in the controller/render adapter, or restore monolith style helper ownership.",
    },
    {
        "id": "ocean_condition_provider_extraction_readiness_packet_stale_contract",
        "severity": "medium",
        "area": "ocean condition provider decoupling",
        "risk": "Ocean condition provider extraction readiness packet is a planned source/normalization-boundary contract only; provider IO, spatial sampling, and scalar normalization still need syntax/runtime-backed checks before extraction.",
        "first_check": "compare Ocean provider extraction readiness with Ocean provider decision, Ocean normalization, Ocean spatial sampling, and Ocean Taichi material port after validation is allowed.",
        "likely_fix": "move fewer symbols, keep source IO in the controller adapter, or restore monolith ocean condition provider ownership.",
    },
    {
        "id": "extraction_readiness_packet_index_unverified",
        "severity": "medium",
        "area": "decoupling preparation",
        "risk": "Extraction readiness packet index summarizes planned packet order and risks only; dependencies and move-symbol counts still need syntax/runtime-backed parity checks before any physical split.",
        "first_check": "open Extraction readiness packet index alongside Pre-validation evidence plan and Module contract coverage after validation is allowed.",
        "likely_fix": "update packet priorities, dependencies, or remaining_packet_candidates before creating new module files.",
    },
    {
        "id": "qt_controller_facade_extraction_readiness_packet_stale_contract",
        "severity": "medium",
        "area": "Qt/controller decoupling",
        "risk": "Qt controller facade extraction readiness packet is a planned API-boundary contract only; toolbar bindings, facade coverage, and runtime UI event routing still need syntax/runtime-backed checks before extraction.",
        "first_check": "compare Qt facade extraction readiness with Qt facade coverage and Qt coupling cleanup after validation is allowed.",
        "likely_fix": "move fewer facade helpers, keep coverage in the monolith adapter, or restore monolith Qt/controller boundary ownership.",
    },
    {
        "id": "qt_main_window_extraction_readiness_packet_stale_contract",
        "severity": "medium",
        "area": "Qt UI decoupling",
        "risk": "Qt main window extraction readiness packet is a planned UI-ownership contract only; toolbar bindings, event routing, and facade-only state mutation still need syntax/runtime-backed checks before extraction.",
        "first_check": "compare Qt main window extraction readiness with Qt facade coverage, Qt coupling cleanup, and one small Qt runtime pass after validation is allowed.",
        "likely_fix": "move fewer UI builders, keep event adapters in the monolith, or restore monolith Qt main window ownership.",
    },
    {
        "id": "datashader_points_extraction_readiness_packet_stale_contract",
        "severity": "medium",
        "area": "Datashader overlay decoupling",
        "risk": "Datashader points extraction readiness packet is a planned point-overlay boundary contract only; style palette branches, sampling budgets, and AIS/ADS-B render parity still need syntax/runtime-backed checks before extraction.",
        "first_check": "compare Datashader points extraction readiness with Style profiles extraction readiness, point overlay budgets, and one small render pass after validation is allowed.",
        "likely_fix": "move fewer symbols, keep overlay config in the controller adapter, or restore monolith Datashader overlay ownership.",
    },
]


def unverified_risk_register_snapshot() -> list[dict]:
    return [dict(item) for item in UNVERIFIED_RISK_REGISTER]


def unverified_risk_register_text() -> str:
    lines = [
        "Unverified risk register",
        "",
        "Purpose: make the known no-validation risks explicit before the next runtime or syntax pass.",
        "Status: validation has not been run in this automation.",
        "",
    ]
    for item in UNVERIFIED_RISK_REGISTER:
        lines.append(f"[{item['id']}] severity={item['severity']} | area={item['area']}")
        lines.append(f"- risk: {item['risk']}")
        lines.append(f"- first check: {item['first_check']}")
        lines.append(f"- likely fix: {item['likely_fix']}")
        lines.append("")
    return "\n".join(lines).rstrip()


ACTIVE_GOAL_NEXT_ACTION_QUEUE = {
    "no_validation": [
        {
            "id": "keep_contracts_in_handoff",
            "action": "Keep new module APIs and active-goal summaries visible from toolbar/handoff.",
            "reason": "This preserves project continuity without launching or compiling.",
        },
        {
            "id": "avoid_new_provider_io",
            "action": "Do not add new network/database/provider downloads until syntax/runtime pass is allowed.",
            "reason": "Current priority is stabilizing hydrology/LOD/ocean contracts, not increasing IO surface.",
        },
        {
            "id": "prepare_first_split_only",
            "action": "If continuing without validation, only refine extraction contracts and rollback notes.",
            "reason": "Physical split without a compile/runtime pass would be hard to debug.",
        },
        {
            "id": "inspect_active_summary_before_split",
            "action": "Open Active goal readiness gate, Pre-validation evidence plan, Extraction readiness packet index, First extraction readiness packet, Hydrology provider extraction readiness, Ocean provider extraction readiness, Render ocean extraction readiness, Vector lines extraction readiness, Datashader points extraction readiness, LOD pipeline extraction readiness, Style profiles extraction readiness, Qt facade extraction readiness, Qt main window extraction readiness, Active goal summary, Hydrology basic readiness, LOD layer decision matrix, Ocean Taichi material port, Module contract coverage, and Qt facade coverage before changing module boundaries.",
            "reason": "These summaries show drift in contracts/facade declarations without running the app.",
        },
        {
            "id": "do_not_trust_lod_gate_until_count_contract_aligned",
            "action": "Treat Active goal readiness gate's LOD matrix shape check as advisory until the layer_count contract is explicitly aligned.",
            "reason": "The current gate expects a layer_count field that may not be emitted by the LOD matrix snapshot.",
        },
    ],
    "requires_user_decision": [
        {
            "id": "fix_lod_matrix_layer_count_contract",
            "action": "Choose whether to add layer_count to lod_layer_decision_matrix_snapshot or compute the count inside active_goal_readiness_gate_snapshot.",
            "reason": "This corrects the known gate/Lod matrix field-contract mismatch without hiding that it was introduced during no-validation work.",
        },
    ],
    "requires_user_approval": [
        {
            "id": "syntax_import_smoke",
            "action": "Run python -m py_compile taichi_global_bathymetry.py.",
            "reason": "This is the first hard gate for the recent contract/helper changes.",
        },
        {
            "id": "execute_pre_validation_evidence_plan",
            "action": "Run the commands listed in Pre-validation evidence plan in order, stopping at the first failed gate.",
            "reason": "This collects explicit evidence for hydrology basic, LOD hook, Ocean Taichi port, and minimal runtime integration.",
        },
        {
            "id": "small_window_runtime",
            "action": "Launch a small Qt viewport with scientific style and topo-step 32.",
            "reason": "Confirms toolbar callables, Datashader overlay config, vector params, and Taichi render path.",
        },
        {
            "id": "write_handoff_snapshot",
            "action": "Use Write handoff snapshot and Write provider manifests.",
            "reason": "Confirms snapshot serialization and provider manifest bundle output.",
        },
    ],
    "post_split": [
        {
            "id": "extract_provider_manifests",
            "action": "Extract contracts/provider_manifests.py first.",
            "reason": "It is the lowest-risk pure contract module.",
        },
        {
            "id": "extract_style_profiles",
            "action": "Extract style_profiles.py second.",
            "reason": "Style helpers are pure and now feed Taichi ocean, Datashader, vector lines, and post-process.",
        },
        {
            "id": "extract_overlay_modules",
            "action": "Extract vector_lines.py and datashader_points.py after style is stable.",
            "reason": "Their render params and palette config helpers are now explicit.",
        },
    ],
}


def active_goal_next_action_queue_snapshot() -> dict:
    return {
        group: [dict(item) for item in items]
        for group, items in ACTIVE_GOAL_NEXT_ACTION_QUEUE.items()
    }


def active_goal_next_action_queue_text() -> str:
    lines = [
        "Active goal next action queue",
        "",
        "Purpose: keep the next work ordered by validation constraints.",
        "Current rule: do not run validation unless the user explicitly asks.",
        "",
    ]
    for group, items in ACTIVE_GOAL_NEXT_ACTION_QUEUE.items():
        lines.append(f"[{group}]")
        for item in items:
            lines.append(f"- {item['id']}: {item['action']}")
            lines.append(f"  reason: {item['reason']}")
        lines.append("")
    return "\n".join(lines).rstrip()


QT_CONTROLLER_FACADE_API = {
    "module": "taichi_earth/qt_ui/controller_facade.py",
    "purpose": "Define the narrow API Qt may call after the UI is split from the monolith.",
    "read_methods": [
        "active_goal_summary_text",
        "active_goal_next_action_queue_text",
        "active_goal_known_issue_matrix_text",
        "active_goal_control_bundle_text",
        "active_goal_readiness_gate_text",
        "hydrology_control_text",
        "hydrology_basic_readiness_matrix_text",
        "hydrology_dirty_reload_contract_text",
        "cache_governance_matrix_text",
        "lod_hook_pipeline_text",
        "lod_invalidation_contract_text",
        "lod_layer_decision_matrix_text",
        "ocean_material_control_text",
        "ocean_material_taichi_port_text",
        "ocean_condition_material_binding_text",
        "module_api_registry_text",
        "pre_extraction_readiness_audit_text",
        "first_extraction_execution_plan_text",
        "first_extraction_readiness_packet_text",
        "extraction_readiness_packet_index_text",
        "active_goal_extraction_seam_matrix_text",
        "module_import_boundary_matrix_text",
        "module_contract_coverage_text",
        "validation_and_rollback_plan_text",
        "pre_validation_evidence_plan_text",
        "unverified_risk_register_text",
        "qt_controller_facade_api_text",
        "qt_controller_facade_coverage_text",
        "qt_controller_facade_extraction_readiness_packet_text",
        "qt_ui_coupling_cleanup_status_text",
        "qt_main_window_extraction_readiness_packet_text",
        "project_goal_milestones_text",
        "decoupling_extraction_units_text",
        "provider_manifests_module_api_text",
        "hydrology_provider_module_api_text",
        "hydrology_provider_extraction_readiness_packet_text",
        "ocean_condition_provider_module_api_text",
        "ocean_condition_provider_extraction_readiness_packet_text",
        "render_core_ocean_material_module_api_text",
        "render_core_ocean_material_extraction_readiness_packet_text",
        "vector_lines_module_api_text",
        "vector_lines_extraction_readiness_packet_text",
        "lod_pipeline_module_api_text",
        "lod_pipeline_extraction_readiness_packet_text",
        "style_profiles_module_api_text",
        "style_profiles_extraction_readiness_packet_text",
        "style_profile_status_text",
        "style_renderer_entry_text",
        "style_renderer_entry_matrix_text",
        "style_overlay_intent_text",
        "datashader_points_module_api_text",
        "datashader_points_extraction_readiness_packet_text",
    ],
    "export_methods": [
        "project_handoff_snapshot_text",
        "write_project_handoff_snapshot_text",
        "provider_manifest_bundle_text",
        "write_provider_manifest_bundle_text",
    ],
    "write_methods": [
        "set_style_profile",
        "set_data_mode",
        "set_map_projection",
        "set_color_mode",
        "set_point_px",
        "set_horizon_eps",
        "set_refresh_seconds",
        "set_max_age_minutes",
        "set_speed_span",
        "set_ais_sample_ratio",
        "set_aircraft_sample_ratio",
        "set_adaptive_sampling",
        "set_target_fps",
        "set_min_sample_ratio",
        "set_vehicle_icons",
        "set_icon_max_count",
        "set_icon_pick_radius",
        "set_aircraft_color_mode",
        "set_aircraft_point_px",
        "set_aircraft_max_age_minutes",
        "set_aircraft_altitude_exaggeration",
        "set_aircraft_horizon_eps",
        "set_sea_level_m",
        "set_terrain_contours",
        "set_contour_interval",
        "set_contour_line_width",
        "set_contour_opacity",
        "set_ocean_material",
        "set_ocean_wave_strength",
        "set_ocean_roughness",
        "set_ocean_foam",
        "set_ocean_animation_fps",
        "set_ocean_condition_refresh",
        "set_ocean_condition_source",
        "set_ocean_provider_lat",
        "set_ocean_provider_lon",
        "set_ice_opacity",
        "set_ice_specular",
        "set_ice_blue",
        "set_cloud_opacity",
        "set_cloud_coverage",
        "set_cloud_detail",
        "set_cloud_animation_fps",
        "reload_hydrology_layer",
        "set_hydrology_strict_source",
        "set_hydrology_strict_metadata",
        "set_hydrology_source_mode",
        "set_hydrology_opacity",
        "set_hydrology_width",
        "set_layer_visible",
        "set_layer_order",
        "set_boundary_opacity",
        "set_boundary_width",
        "set_scale_bar_position",
        "set_scale_bar_opacity",
        "set_flight_speed_deg",
        "toggle_longitude_flip",
        "toggle_latitude_flip",
    ],
    "render_methods": [
        "render_if_needed",
        "set_interaction_active",
        "rotate",
        "zoom_by",
        "reset_view",
        "set_boundary_hover",
    ],
    "must_not_expose": [
        "raw Taichi fields",
        "provider private loader functions",
        "database/socket client instances",
        "mutable overlay cache dictionaries",
        "Qt widget instances",
    ],
    "handoff_rule": "Qt owns widgets and user events; controller facade owns state mutation and render requests; providers/renderers stay behind controller methods.",
}


def qt_controller_facade_api_snapshot() -> dict:
    api = dict(QT_CONTROLLER_FACADE_API)
    for key in ("read_methods", "export_methods", "write_methods", "render_methods", "must_not_expose"):
        seen = set()
        unique = []
        for item in api.get(key, []):
            if item in seen:
                continue
            seen.add(item)
            unique.append(item)
        api[key] = unique
    return api


def qt_controller_facade_api_text() -> str:
    api = qt_controller_facade_api_snapshot()
    lines = [
        "Qt/controller facade API",
        "",
        f"- module: {api['module']}",
        f"- purpose: {api['purpose']}",
        f"- handoff rule: {api['handoff_rule']}",
        "",
        "Read methods:",
    ]
    for name in api["read_methods"]:
        lines.append(f"- {name}")
    lines.append("")
    lines.append("Export methods:")
    for name in api["export_methods"]:
        lines.append(f"- {name}")
    lines.append("")
    lines.append("Write methods:")
    for name in api["write_methods"]:
        lines.append(f"- {name}")
    lines.append("")
    lines.append("Render methods:")
    for name in api["render_methods"]:
        lines.append(f"- {name}")
    lines.append("")
    lines.append("Must not expose:")
    for name in api["must_not_expose"]:
        lines.append(f"- {name}")
    return "\n".join(lines)


def qt_controller_facade_coverage_snapshot(controller) -> dict:
    api = qt_controller_facade_api_snapshot()
    groups = {
        "read_methods": api.get("read_methods", []),
        "export_methods": api.get("export_methods", []),
        "write_methods": api.get("write_methods", []),
        "render_methods": api.get("render_methods", []),
    }
    coverage = {}
    missing = []
    for group, names in groups.items():
        coverage[group] = {}
        for name in names:
            exists = hasattr(controller, name) and callable(getattr(controller, name, None))
            coverage[group][name] = exists
            if not exists:
                missing.append(f"{group}.{name}")
    return {
        "contract": "Qt facade coverage compares declared facade methods with the active controller object.",
        "missing": missing,
        "ok": not missing,
        "coverage": coverage,
    }


def qt_controller_facade_coverage_text(controller) -> str:
    snapshot = qt_controller_facade_coverage_snapshot(controller)
    lines = [
        "Qt facade coverage",
        "",
        f"- ok: {snapshot['ok']}",
        f"- missing count: {len(snapshot['missing'])}",
        f"- contract: {snapshot['contract']}",
        "",
    ]
    if snapshot["missing"]:
        lines.append("Missing:")
        for name in snapshot["missing"]:
            lines.append(f"- {name}")
        lines.append("")
    lines.append("Coverage:")
    for group, methods in snapshot["coverage"].items():
        lines.append(f"[{group}]")
        for name, exists in methods.items():
            lines.append(f"- {name}: {exists}")
    return "\n".join(lines)


QT_UI_COUPLING_CLEANUP_STATUS = {
    "purpose": "Track UI-to-controller coupling cleanup before qt_ui/main_window.py is physically split.",
    "status": "facade-wired",
    "facade_contract_scope": [
        "write_methods includes current Qt setter/toggle calls for projection, layer, hydrology, boundary, sampling, styling, and flight controls.",
        "Taichi ocean material setters are declared as facade write methods before the Qt shell is physically split.",
    ],
    "known_direct_writes_removed": [
        "projection changes now call controller.set_map_projection",
        "data mode changes now call controller.set_data_mode",
        "hydrology source mode changes now call controller.set_hydrology_source_mode",
        "flight speed changes now call controller.set_flight_speed_deg",
    ],
    "known_static_scan": {
        "pattern": "self.controller.<name> = ...",
        "latest_result": "no matches found in current targeted scan",
        "scope": "taichi_global_bathymetry.py",
    },
    "remaining_manual_review": [
        "Qt may still read controller.args for initial widget values; this is acceptable until a read-only config facade exists.",
        "Qt still owns many widget-building details and should be extracted after provider/style/overlay contracts stabilize.",
    ],
}


def qt_ui_coupling_cleanup_status_snapshot() -> dict:
    return dict(QT_UI_COUPLING_CLEANUP_STATUS)


def qt_ui_coupling_cleanup_status_text() -> str:
    status = QT_UI_COUPLING_CLEANUP_STATUS
    lines = [
        "Qt UI coupling cleanup status",
        "",
        f"- purpose: {status['purpose']}",
        f"- status: {status['status']}",
        "",
        "Known direct writes removed:",
    ]
    for item in status["known_direct_writes_removed"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "Facade contract scope:",
        ]
    )
    for item in status["facade_contract_scope"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "Known static scan:",
            f"- pattern: {status['known_static_scan']['pattern']}",
            f"- latest result: {status['known_static_scan']['latest_result']}",
            f"- scope: {status['known_static_scan']['scope']}",
            "",
            "Remaining manual review:",
        ]
    )
    for item in status["remaining_manual_review"]:
        lines.append(f"- {item}")
    return "\n".join(lines)


QT_CONTROLLER_FACADE_EXTRACTION_READINESS_PACKET = {
    "target_file": "taichi_earth/qt_ui/controller_facade.py",
    "purpose": "Prepare the Qt/controller boundary split while keeping Qt widgets, provider clients, renderer internals, and mutable caches behind a narrow facade contract.",
    "candidate_status": "prepared-not-extracted",
    "move_symbols": [
        "QT_CONTROLLER_FACADE_API",
        "qt_controller_facade_api_snapshot",
        "qt_controller_facade_api_text",
        "qt_controller_facade_coverage_snapshot",
        "qt_controller_facade_coverage_text",
        "QT_UI_COUPLING_CLEANUP_STATUS",
        "qt_ui_coupling_cleanup_status_snapshot",
        "qt_ui_coupling_cleanup_status_text",
    ],
    "keep_in_monolith_controller_adapter": [
        "actual controller state mutation methods",
        "provider instances",
        "renderer instances",
        "mutable overlay/cache dictionaries",
        "handoff snapshot aggregation until module split is validated",
    ],
    "owned_by_qt_main_window": [
        "Qt widgets",
        "toolbar/dock construction",
        "signals and slots",
        "mouse/keyboard event routing",
        "visible text dialogs",
    ],
    "allowed_imports": ["json", "typing"],
    "forbidden_imports": ["PyQt widgets", "vispy", "taichi", "datashader", "provider clients", "renderer instances", "database clients"],
    "input_contract": [
        "controller-like object implementing declared read/export/write/render methods",
        "method names declared in QT_CONTROLLER_FACADE_API",
        "coverage inspection through hasattr/callable only",
    ],
    "output_contract": [
        "facade API snapshot",
        "facade coverage snapshot",
        "coupling cleanup status snapshot",
        "no widget ownership",
        "no provider IO",
        "no render kernel invocation",
    ],
    "preconditions": [
        "Qt facade API and Qt facade coverage are visible from toolbar",
        "Qt coupling cleanup status is visible from toolbar",
        "active goal readiness gate remains explicit about runtime validation not being run",
        "pre-validation evidence plan has been reviewed",
    ],
    "rollback_steps": [
        "restore facade constants and coverage helpers inside the monolith",
        "keep controller methods unchanged",
        "disable only Qt facade extraction readiness diagnostics if toolbar wiring fails",
    ],
}


def qt_controller_facade_extraction_readiness_packet_snapshot() -> dict:
    packet = dict(QT_CONTROLLER_FACADE_EXTRACTION_READINESS_PACKET)
    packet["module_api"] = qt_controller_facade_api_snapshot()
    packet["coupling_cleanup"] = qt_ui_coupling_cleanup_status_snapshot()
    packet["validation_evidence_plan_ids"] = [
        item["id"] for item in PRE_VALIDATION_EVIDENCE_PLAN
        if item["id"] in {
            "syntax_import_gate",
            "small_render_gate",
        }
    ]
    packet["runtime_verification"] = "not-run"
    return packet


def qt_controller_facade_extraction_readiness_packet_text() -> str:
    packet = qt_controller_facade_extraction_readiness_packet_snapshot()
    lines = [
        "Qt controller facade extraction readiness packet",
        "",
        f"- target file: {packet['target_file']}",
        f"- purpose: {packet['purpose']}",
        f"- status: {packet['candidate_status']}",
        f"- runtime verification: {packet['runtime_verification']}",
        "",
        "Move symbols:",
    ]
    for name in packet["move_symbols"]:
        lines.append(f"- {name}")
    lines.append("")
    lines.append("Keep in monolith controller adapter:")
    for item in packet["keep_in_monolith_controller_adapter"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Owned by Qt main window:")
    for item in packet["owned_by_qt_main_window"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append(f"Allowed imports: {', '.join(packet['allowed_imports'])}")
    lines.append(f"Forbidden imports: {', '.join(packet['forbidden_imports'])}")
    lines.append("")
    lines.append("Input contract:")
    for item in packet["input_contract"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Output contract:")
    for item in packet["output_contract"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Preconditions:")
    for item in packet["preconditions"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Rollback steps:")
    for item in packet["rollback_steps"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Validation evidence gates:")
    for gate_id in packet["validation_evidence_plan_ids"]:
        lines.append(f"- {gate_id}")
    return "\n".join(lines).rstrip()


QT_MAIN_WINDOW_MODULE_API = {
    "module": "taichi_earth/qt_ui/main_window.py",
    "purpose": "Own Qt widgets, docks, toolbar actions, timeline visibility, and user-event routing while delegating state mutation and rendering to the controller facade.",
    "public_api": [
        {
            "name": "QtHybridWindow",
            "signature": "QtHybridWindow(controller_facade).run() -> None",
            "ownership": "qt_ui",
            "side_effects": "creates Qt/VisPy widgets and starts Qt event loop",
        },
        {
            "name": "_build_mode_toolbar",
            "signature": "_build_mode_toolbar() -> QToolBar",
            "ownership": "qt_ui",
            "side_effects": "creates toolbar widgets and binds actions to controller facade methods",
        },
        {
            "name": "_build_layer_dock",
            "signature": "_build_layer_dock() -> QDockWidget",
            "ownership": "qt_ui",
            "side_effects": "creates Photoshop-like layer controls from controller-visible layer state",
        },
        {
            "name": "set_data_mode",
            "signature": "set_data_mode(mode: str) -> None",
            "ownership": "qt_ui event adapter",
            "side_effects": "updates UI mode widgets and calls controller.set_data_mode",
        },
        {
            "name": "on_projection_changed",
            "signature": "on_projection_changed(index: int) -> None",
            "ownership": "qt_ui event adapter",
            "side_effects": "updates projection combo state and calls controller.set_map_projection",
        },
    ],
    "input_contract": {
        "controller": ["Qt/controller facade methods only", "render_if_needed", "diagnostic text methods"],
        "events": ["mouse drag", "wheel zoom", "toolbar clicks", "dock/layer interactions", "timeline hover/playback"],
        "outputs": ["VisPy image data updates", "Qt labels/dialogs/docks"],
    },
    "must_not_import": ["provider private loaders", "database/socket clients", "raw Taichi fields", "module extraction internals"],
    "allowed_imports": ["PyQt6", "vispy", "time", "json optional", "controller facade protocol"],
    "handoff_rule": "Qt main window must route all state changes through controller facade methods and should not own provider/render-core internals.",
}


def qt_main_window_module_api_snapshot() -> dict:
    return dict(QT_MAIN_WINDOW_MODULE_API)


def qt_main_window_module_api_text() -> str:
    api = QT_MAIN_WINDOW_MODULE_API
    lines = [
        "Qt main window module API",
        "",
        f"- module: {api['module']}",
        f"- purpose: {api['purpose']}",
        f"- allowed imports: {', '.join(api['allowed_imports'])}",
        f"- must not import: {', '.join(api['must_not_import'])}",
        f"- handoff rule: {api['handoff_rule']}",
        "",
        "Input contract:",
    ]
    for name, values in api["input_contract"].items():
        lines.append(f"- {name}: {', '.join(values)}")
    lines.append("")
    lines.append("Public API:")
    for item in api["public_api"]:
        lines.append(f"- {item['name']}")
        lines.append(f"  signature: {item['signature']}")
        lines.append(f"  ownership: {item['ownership']}")
        lines.append(f"  side effects: {item['side_effects']}")
    return "\n".join(lines)


QT_MAIN_WINDOW_EXTRACTION_READINESS_PACKET = {
    "target_file": "taichi_earth/qt_ui/main_window.py",
    "purpose": "Prepare the Qt main-window split while keeping state mutation, provider access, render-core internals, and cache ownership behind the controller facade.",
    "candidate_status": "prepared-not-extracted",
    "move_symbols": [
        "QtHybridWindow",
        "mode toolbar builders",
        "layer dock builders",
        "timeline controls",
        "diagnostic toolbar bindings",
        "mouse/keyboard/wheel event adapters",
        "Qt dialog helpers",
        "Qt label/status update helpers",
    ],
    "keep_in_controller_facade": [
        "all declared QT_CONTROLLER_FACADE_API methods",
        "controller state mutation",
        "provider decisions and IO",
        "render_if_needed and render scheduling",
        "handoff/export text methods",
        "diagnostic snapshot methods",
    ],
    "must_route_through_facade": [
        "data mode changes",
        "projection changes",
        "style profile changes",
        "hydrology source/strictness controls",
        "ocean source/material controls",
        "layer visibility/order changes",
        "flight and interaction controls",
    ],
    "allowed_imports": ["PyQt6", "vispy", "time", "json optional", "controller facade protocol"],
    "forbidden_imports": ["provider private loaders", "database/socket clients", "raw Taichi fields", "mutable overlay cache dictionaries", "module extraction internals"],
    "input_contract": [
        "controller facade object",
        "Qt user events",
        "read-only labels/dialog text from facade",
        "render requests through facade methods only",
    ],
    "output_contract": [
        "Qt widgets/docks/toolbars",
        "event-to-facade method calls",
        "visible diagnostics",
        "no direct provider IO",
        "no raw renderer mutation",
        "no direct controller attribute writes",
    ],
    "preconditions": [
        "Qt facade extraction readiness is visible from toolbar",
        "Qt facade coverage has no missing methods after validation is allowed",
        "Qt coupling cleanup status remains facade-wired",
        "pre-validation evidence plan has been reviewed",
    ],
    "rollback_steps": [
        "restore QtHybridWindow and UI builders inside the monolith",
        "keep controller facade method additions unchanged",
        "disable only Qt main window extraction readiness diagnostics if toolbar wiring fails",
    ],
}


def qt_main_window_extraction_readiness_packet_snapshot() -> dict:
    packet = dict(QT_MAIN_WINDOW_EXTRACTION_READINESS_PACKET)
    packet["module_api"] = qt_main_window_module_api_snapshot()
    packet["facade_api"] = qt_controller_facade_api_snapshot()
    packet["coupling_cleanup"] = qt_ui_coupling_cleanup_status_snapshot()
    packet["validation_evidence_plan_ids"] = [
        item["id"] for item in PRE_VALIDATION_EVIDENCE_PLAN
        if item["id"] in {
            "syntax_import_gate",
            "small_render_gate",
        }
    ]
    packet["runtime_verification"] = "not-run"
    return packet


def qt_main_window_extraction_readiness_packet_text() -> str:
    packet = qt_main_window_extraction_readiness_packet_snapshot()
    lines = [
        "Qt main window extraction readiness packet",
        "",
        f"- target file: {packet['target_file']}",
        f"- purpose: {packet['purpose']}",
        f"- status: {packet['candidate_status']}",
        f"- runtime verification: {packet['runtime_verification']}",
        "",
        "Move symbols:",
    ]
    for name in packet["move_symbols"]:
        lines.append(f"- {name}")
    lines.append("")
    lines.append("Keep in controller facade:")
    for item in packet["keep_in_controller_facade"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Must route through facade:")
    for item in packet["must_route_through_facade"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append(f"Allowed imports: {', '.join(packet['allowed_imports'])}")
    lines.append(f"Forbidden imports: {', '.join(packet['forbidden_imports'])}")
    lines.append("")
    lines.append("Input contract:")
    for item in packet["input_contract"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Output contract:")
    for item in packet["output_contract"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Preconditions:")
    for item in packet["preconditions"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Rollback steps:")
    for item in packet["rollback_steps"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Validation evidence gates:")
    for gate_id in packet["validation_evidence_plan_ids"]:
        lines.append(f"- {gate_id}")
    return "\n".join(lines).rstrip()


def module_split_readiness_text() -> str:
    rows = [
        ("data_sources", "partial", "Provider decisions and manifest bundle exist; physical modules are not extracted yet."),
        ("projection", "partial", "Globe projection, aircraft/AIS screen projection, scale bar, and LOD contract are explicit."),
        ("overlays", "partial", "Datashader point overlays and vector line overlays have renderer contracts."),
        ("render_core", "partial", "Taichi renderer inputs are explicit, but kernels still live in the monolith."),
        ("contracts", "partial", "Handoff snapshot and provider manifest bundle can be written from the UI."),
        ("qt_ui", "port", "Qt still orchestrates directly from the monolith and should be split last."),
        ("style_profiles", "port", "Scientific/tactical/nautical/parchment profiles have renderer-entry contracts plus basic post-process hooks."),
    ]
    lines = [
        "Module split readiness",
        "",
        "Legend: partial = contract exists but code is not physically split; port = UI/API hook exists but implementation is basic.",
        "",
    ]
    for module, state, note in rows:
        lines.append(f"- {module}: {state}; {note}")
    lines.extend([
        "",
        "Recommended extraction order:",
        "1. contracts/provider_manifests.py",
        "2. contracts/project_handoff.py",
        "3. data_sources/* providers",
        "4. projection/globe_projection.py",
        "5. overlays/datashader_points.py and vector_lines.py",
        "6. render_core/taichi_globe.py",
        "7. qt_ui/main_window.py",
    ])
    return "\n".join(lines)


DECOUPLING_EXTRACTION_GATES = [
    {
        "module": "contracts/provider_manifests.py",
        "target_state": "pure-python manifest builders",
        "must_have": [
            "provider manifest bundle is serializable",
            "source_url/source_version/license/cache_path/schema/simplification are represented",
            "no Qt, VisPy, Datashader, Taichi, or network fetch at import time",
        ],
        "blockers": [
            "manifest builders depending on controller instance state",
            "provider download side effects inside manifest construction",
        ],
    },
    {
        "module": "data_sources/hydrology_provider.py",
        "target_state": "strict/basic hydrology provider module",
        "must_have": [
            "HYDROLOGY_SPECS and strict provider ports move together",
            "HydrologyLODSourcePolicy remains independent from Qt and renderer buffers",
            "HydrologyRenderLODProfile stays separate from source selection",
            "HydrologyScientificStrictnessPolicy reports basic/strict/local/user-supplied risk",
            "provider decisions include manifest and strict metadata audit",
        ],
        "blockers": [
            "provider code calling Qt progress widgets directly",
            "render RGBA cache state mixed into provider decision",
        ],
    },
    {
        "module": "data_sources/ocean_condition_provider.py",
        "target_state": "ocean condition normalizer and spatial sampler",
        "must_have": [
            "OCEAN_PROVIDER_REGISTRY and OCEAN_RENDER_PORT_CONTRACT move together",
            "OceanConditionProvider returns scalar wave_strength/roughness/foam",
            "OceanSpatialSamplingPolicy owns lat/lon point selection contract",
            "normalization report exposes alias matches and selected sample row",
            "OceanMaterialPolicy can move with render_core only after scalar contract stabilizes",
        ],
        "blockers": [
            "Taichi kernel state imported into ocean provider module",
            "Qt controls mutating provider internals directly instead of args/controller setters",
        ],
    },
    {
        "module": "overlays/vector_lines.py",
        "target_state": "screen-space vector renderer",
        "must_have": [
            "GeoVectorLineOverlay consumes lon/lat lines and camera/projection state",
            "overlay cache keys stay in controller, not provider modules",
            "hover hit testing remains renderer-side and returns serializable hit dicts",
        ],
        "blockers": [
            "provider source decisions hidden inside GeoVectorLineOverlay",
            "Qt layer lock/reorder state imported into overlay renderer",
        ],
    },
    {
        "module": "render_core/taichi_globe.py",
        "target_state": "dense Taichi globe renderer",
        "must_have": [
            "TaichiGlobeRenderer receives raster/mask arrays and scalar material controls only",
            "style profile modifiers are resolved before/after render without provider IO",
            "ocean material input is scalar and independent from provider source format",
            "renderer returns RGBA frame and globe mask",
        ],
        "blockers": [
            "database/network/file provider logic inside Taichi render core",
            "Qt widgets or Datashader Canvas imported into render core",
        ],
    },
    {
        "module": "qt_ui/main_window.py",
        "target_state": "thin operator console",
        "must_have": [
            "Qt calls controller methods, not provider internals",
            "data fetch progress panel reads event snapshots only",
            "layer dialogs use setter/reload methods and do not own normalized payloads",
        ],
        "blockers": [
            "Qt widgets passed into provider modules",
            "blocking downloads launched directly from render timer",
        ],
    },
]


def decoupling_extraction_gates_text() -> str:
    lines = [
        "Decoupling extraction gates",
        "",
        "Purpose: make the future file split mechanical and prevent UI/provider/renderer dependency leaks.",
    ]
    for gate in DECOUPLING_EXTRACTION_GATES:
        lines.extend(["", f"[{gate['module']}]", f"- target: {gate['target_state']}", "- must have:"])
        for item in gate["must_have"]:
            lines.append(f"  - {item}")
        lines.append("- blockers:")
        for item in gate["blockers"]:
            lines.append(f"  - {item}")
    return "\n".join(lines)


STYLE_PROFILE_REGISTRY = {
    "scientific": {
        "label": "科學",
        "status": "active",
        "renderer_mode": "physical-color",
        "post_process": "none",
        "terrain_bias": "hypsometric/bathymetric",
        "vector_tint": "neutral-white",
        "point_palette": "speed-altitude-density",
        "taichi_ocean": "realistic",
        "notes": "Default scientific visualization; preserve measured terrain/ocean semantics.",
    },
    "nautical": {
        "label": "航海 basic 🚧",
        "status": "port",
        "renderer_mode": "chart-color",
        "post_process": "blue-chart-lift",
        "terrain_bias": "subdued-land/high-contrast-bathymetry",
        "vector_tint": "chart-line-cyan",
        "point_palette": "navigation-safety",
        "taichi_ocean": "reduced-glare",
        "notes": "Future target: chart-like water emphasis, readable boundaries, vessel-first overlays.",
    },
    "tactical": {
        "label": "戰術 basic 🚧",
        "status": "port",
        "renderer_mode": "night-ops",
        "post_process": "green-phosphor",
        "terrain_bias": "low-saturation-relief",
        "vector_tint": "hud-green",
        "point_palette": "threat-density-alert",
        "taichi_ocean": "low-specular",
        "notes": "Future target: high-contrast tactical display with glowing boundaries and sparse terrain.",
    },
    "parchment": {
        "label": "羊皮紙 basic 🚧",
        "status": "port",
        "renderer_mode": "illustrated-map",
        "post_process": "sepia-paper-grain",
        "terrain_bias": "inked-relief",
        "vector_tint": "brown-ink",
        "point_palette": "muted-symbols",
        "taichi_ocean": "flat-wash",
        "notes": "Future target: medieval game-map style with paper grain, ink coastlines, and symbolic layers.",
    },
}


STYLE_PROFILE_MATERIAL_MODIFIERS = {
    "scientific": {"wave": 1.00, "roughness": 1.00, "foam": 1.00, "post_opacity": 1.00},
    "nautical": {"wave": 0.85, "roughness": 0.72, "foam": 0.82, "post_opacity": 1.00},
    "tactical": {"wave": 0.48, "roughness": 0.42, "foam": 0.38, "post_opacity": 1.00},
    "parchment": {"wave": 0.16, "roughness": 0.22, "foam": 0.00, "post_opacity": 1.00},
}


STYLE_RENDERER_PORT_CONTRACT = {
    "input": [
        "frame_rgba from Taichi globe + vector/point overlays",
        "active style_profile",
        "current LOD and map projection",
        "ocean condition material state",
    ],
    "output": [
        "post-processed frame_rgba",
        "Datashader palette intent",
        "vector/icon tint intent",
        "Taichi ocean material modifier",
    ],
    "module_target": "taichi_earth/style_profiles.py",
    "rule": "Style profiles should be resolved once per frame and then passed to render_core, vector_layers, and overlay renderers.",
}


STYLE_RENDERER_ENTRIES = {
    "scientific": {
        "entry": "style.scientific.physical",
        "post_process": "none",
        "terrain_shader": "hypsometric_bathymetric",
        "datashader_palette": "density_speed_altitude",
        "vector_tint": "neutral-white",
        "boundary_tint_rgba": (230, 235, 240, 180),
        "hydrology_tint_rgba": (90, 185, 230, 170),
        "icon_tint": "semantic",
        "ocean_material_modifier": STYLE_PROFILE_MATERIAL_MODIFIERS["scientific"],
    },
    "nautical": {
        "entry": "style.nautical.chart",
        "post_process": "blue-chart-lift",
        "terrain_shader": "subdued_land_high_contrast_bathymetry",
        "datashader_palette": "navigation_safety",
        "vector_tint": "chart-cyan",
        "boundary_tint_rgba": (110, 220, 245, 205),
        "hydrology_tint_rgba": (70, 210, 245, 210),
        "icon_tint": "marine-symbol",
        "ocean_material_modifier": STYLE_PROFILE_MATERIAL_MODIFIERS["nautical"],
    },
    "tactical": {
        "entry": "style.tactical.night_ops",
        "post_process": "green-phosphor",
        "terrain_shader": "low_saturation_relief",
        "datashader_palette": "threat_density_alert",
        "vector_tint": "hud-green",
        "boundary_tint_rgba": (95, 255, 120, 220),
        "hydrology_tint_rgba": (60, 220, 150, 185),
        "icon_tint": "iff-hud",
        "ocean_material_modifier": STYLE_PROFILE_MATERIAL_MODIFIERS["tactical"],
    },
    "parchment": {
        "entry": "style.parchment.illustrated_map",
        "post_process": "sepia-paper-grain",
        "terrain_shader": "inked_relief",
        "datashader_palette": "muted_symbols",
        "vector_tint": "brown-ink",
        "boundary_tint_rgba": (86, 55, 27, 210),
        "hydrology_tint_rgba": (57, 92, 115, 175),
        "icon_tint": "ink-symbol",
        "ocean_material_modifier": STYLE_PROFILE_MATERIAL_MODIFIERS["parchment"],
    },
}


def resolve_style_profile(profile: str) -> dict:
    key = str(profile or "scientific").strip().lower()
    if key not in STYLE_PROFILE_REGISTRY:
        key = "scientific"
    resolved = dict(STYLE_PROFILE_REGISTRY[key])
    resolved["id"] = key
    return resolved


def resolve_style_renderer_entry(profile: str) -> dict:
    profile_spec = resolve_style_profile(profile)
    entry = dict(STYLE_RENDERER_ENTRIES.get(profile_spec["id"], STYLE_RENDERER_ENTRIES["scientific"]))
    entry["id"] = profile_spec["id"]
    entry["label"] = profile_spec["label"]
    entry["status"] = profile_spec["status"]
    entry["profile"] = profile_spec
    entry["ocean_material_modifier"] = dict(entry.get("ocean_material_modifier", STYLE_PROFILE_MATERIAL_MODIFIERS["scientific"]))
    return entry


def style_renderer_entry_matrix_snapshot(active_profile: str = "scientific") -> dict:
    required_fields = [
        "id",
        "label",
        "status",
        "entry",
        "post_process",
        "terrain_shader",
        "datashader_palette",
        "vector_tint",
        "boundary_tint_rgba",
        "hydrology_tint_rgba",
        "icon_tint",
        "ocean_material_modifier",
    ]
    target_entries = ["scientific", "tactical", "parchment"]
    active_id = resolve_style_profile(active_profile)["id"]
    entries = {}
    missing_required_fields = {}
    for profile_id in STYLE_PROFILES_MODULE_API["profiles"]:
        entry = resolve_style_renderer_entry(profile_id)
        missing = [field for field in required_fields if field not in entry]
        entries[profile_id] = {
            "id": entry.get("id", profile_id),
            "label": entry.get("label", profile_id),
            "status": entry.get("status", ""),
            "entry": entry.get("entry", ""),
            "post_process": entry.get("post_process", ""),
            "terrain_shader": entry.get("terrain_shader", ""),
            "datashader_palette": entry.get("datashader_palette", ""),
            "vector_tint": entry.get("vector_tint", ""),
            "has_boundary_tint": "boundary_tint_rgba" in entry,
            "has_hydrology_tint": "hydrology_tint_rgba" in entry,
            "has_ocean_material_modifier": bool(entry.get("ocean_material_modifier", {})),
            "is_target_entry": profile_id in target_entries,
            "is_active": profile_id == active_id,
        }
        if missing:
            missing_required_fields[profile_id] = missing
    return {
        "contract": "Style renderer entry matrix keeps scientific, tactical, and parchment renderer ports visible before a physical StyleRenderer split.",
        "runtime_verification": "not-run",
        "active_profile": active_id,
        "target_entries": target_entries,
        "required_fields": required_fields,
        "entry_count": len(entries),
        "entries": entries,
        "missing_required_fields": missing_required_fields,
        "ready": not missing_required_fields and all(profile_id in entries for profile_id in target_entries),
    }


def style_renderer_entry_matrix_text(active_profile: str = "scientific") -> str:
    matrix = style_renderer_entry_matrix_snapshot(active_profile)
    lines = [
        "Style renderer entry matrix",
        "",
        f"- runtime verification: {matrix['runtime_verification']}",
        f"- active profile: {matrix['active_profile']}",
        f"- target entries: {', '.join(matrix['target_entries'])}",
        f"- entry count: {matrix['entry_count']}",
        f"- ready: {matrix['ready']}",
        f"- missing required fields: {len(matrix['missing_required_fields'])}",
        "",
        "Entries:",
    ]
    for profile_id, entry in matrix["entries"].items():
        active_marker = " active" if entry["is_active"] else ""
        target_marker = " target" if entry["is_target_entry"] else ""
        lines.append(
            f"- {profile_id}:{active_marker}{target_marker}; status={entry['status']}; "
            f"entry={entry['entry']}; post={entry['post_process']}; terrain={entry['terrain_shader']}"
        )
    if matrix["missing_required_fields"]:
        lines.append("")
        lines.append("Missing required fields:")
        for profile_id, fields in matrix["missing_required_fields"].items():
            lines.append(f"- {profile_id}: {', '.join(fields)}")
    return "\n".join(lines)


def style_renderer_entry_text(active_profile: str = "scientific") -> str:
    entry = resolve_style_renderer_entry(active_profile)
    lines = [
        "Style renderer entry",
        "",
        f"- active profile: {entry['id']} ({entry['label']})",
        f"- status: {entry['status']}",
        f"- entry: {entry['entry']}",
        f"- post process: {entry['post_process']}",
        f"- terrain shader: {entry['terrain_shader']}",
        f"- Datashader palette: {entry['datashader_palette']}",
        f"- vector tint: {entry['vector_tint']}",
        f"- icon tint: {entry['icon_tint']}",
        f"- boundary rgba: {entry['boundary_tint_rgba']}",
        f"- hydrology rgba: {entry['hydrology_tint_rgba']}",
        f"- ocean modifier: {entry['ocean_material_modifier']}",
        "",
        "Port contract:",
    ]
    for section, values in STYLE_RENDERER_PORT_CONTRACT.items():
        if isinstance(values, list):
            lines.append(f"- {section}:")
            for value in values:
                lines.append(f"  - {value}")
        else:
            lines.append(f"- {section}: {values}")
    return "\n".join(lines)


def resolve_style_overlay_intent(profile: str) -> dict:
    entry = resolve_style_renderer_entry(profile)
    palette = str(entry.get("datashader_palette", "density_speed_altitude"))
    if palette == "navigation_safety":
        datashader = {
            "ais": "speed_safe_warning_alert",
            "aircraft": "altitude_cyan_magenta",
            "density": "cyan_density",
            "background": "transparent",
        }
    elif palette == "threat_density_alert":
        datashader = {
            "ais": "green_yellow_red_alert",
            "aircraft": "iff_green_amber_red",
            "density": "phosphor_density",
            "background": "transparent",
        }
    elif palette == "muted_symbols":
        datashader = {
            "ais": "ink_blue_brown",
            "aircraft": "ink_brown_red",
            "density": "sepia_density",
            "background": "transparent",
        }
    else:
        datashader = {
            "ais": "speed_yellow_orange_red",
            "aircraft": "altitude_blue_yellow_red",
            "density": "viridis_density",
            "background": "transparent",
        }
    return {
        "profile": entry["id"],
        "entry": entry["entry"],
        "datashader_palette": datashader,
        "vector_tint": entry.get("vector_tint", "neutral-white"),
        "boundary_tint_rgba": tuple(entry.get("boundary_tint_rgba", (230, 235, 240, 180))),
        "hydrology_tint_rgba": tuple(entry.get("hydrology_tint_rgba", (90, 185, 230, 170))),
        "icon_tint": entry.get("icon_tint", "semantic"),
        "contract": "Overlay renderers should request this once per frame instead of hard-coding layer colors.",
    }


def style_overlay_intent_text(active_profile: str = "scientific") -> str:
    intent = resolve_style_overlay_intent(active_profile)
    lines = [
        "Style overlay intent",
        "",
        f"- profile: {intent['profile']}",
        f"- entry: {intent['entry']}",
        f"- vector tint: {intent['vector_tint']}",
        f"- boundary rgba: {intent['boundary_tint_rgba']}",
        f"- hydrology rgba: {intent['hydrology_tint_rgba']}",
        f"- icon tint: {intent['icon_tint']}",
        f"- contract: {intent['contract']}",
        "",
        "Datashader palettes:",
    ]
    for layer, palette in intent["datashader_palette"].items():
        lines.append(f"- {layer}: {palette}")
    lines.extend(["", "Resolved Datashader cmaps:"])
    for layer, cmap in resolve_datashader_style_cmaps(active_profile).items():
        lines.append(f"- {layer}: {cmap}")
    return "\n".join(lines)


def resolve_datashader_style_cmaps(profile: str) -> dict:
    profile_id = resolve_style_overlay_intent(profile)["profile"]
    return DATASHADER_STYLE_CMAPS.get(profile_id, DATASHADER_STYLE_CMAPS["scientific"])


def resolve_style_layer_rgb(profile: str, layer_kind: str, base_color: tuple[int, int, int]) -> tuple[int, int, int]:
    intent = resolve_style_overlay_intent(profile)
    profile_id = intent["profile"]
    if profile_id == "scientific":
        return tuple(int(max(0, min(255, c))) for c in base_color[:3])
    tint_key = "hydrology_tint_rgba" if layer_kind == "hydrology" else "boundary_tint_rgba"
    tint = tuple(int(max(0, min(255, c))) for c in intent.get(tint_key, base_color)[:3])
    base = tuple(int(max(0, min(255, c))) for c in base_color[:3])
    return tuple(int(round(base[i] * 0.25 + tint[i] * 0.75)) for i in range(3))


def style_vector_cache_key(profile: str) -> tuple:
    intent = resolve_style_overlay_intent(profile)
    return (
        intent["profile"],
        intent["vector_tint"],
        tuple(intent["boundary_tint_rgba"]),
        tuple(intent["hydrology_tint_rgba"]),
    )


def build_hydrology_render_params(args, layer_id: str, spec: dict, render_profile: dict, style_profile: str) -> dict:
    prefix = spec["prefix"]
    opacity_scale = float(render_profile.get("opacity_scale", 1.0))
    width_scale = float(render_profile.get("width_scale", 1.0))
    opacity = max(0.0, min(1.0, float(getattr(args, f"{prefix}_opacity", 0.55)) * opacity_scale))
    width = max(1, int(round(float(getattr(args, f"{prefix}_width", 1)) * width_scale)))
    return {
        "layer_id": layer_id,
        "color": resolve_style_layer_rgb(style_profile, "hydrology", spec["color"]),
        "opacity": opacity,
        "width": width,
        "decimate": int(render_profile.get("decimate", 1)),
        "opacity_scale": opacity_scale,
        "width_scale": width_scale,
        "style_profile": resolve_style_profile(style_profile)["id"],
    }


def build_boundary_render_params(args, layer_id: str, spec: dict, style_profile: str) -> dict:
    opacity_attr = {
        "borders": "border_opacity",
        "territorial_sea": "territorial_sea_opacity",
        "eez": "eez_opacity",
        "high_seas": "high_seas_opacity",
    }.get(layer_id, f"{layer_id}_opacity")
    width_attr = {
        "borders": "border_width",
        "territorial_sea": "territorial_sea_width",
        "eez": "eez_width",
        "high_seas": "high_seas_width",
    }.get(layer_id, f"{layer_id}_width")
    return {
        "layer_id": layer_id,
        "color": resolve_style_layer_rgb(style_profile, "boundary", spec["color"]),
        "opacity": max(0.0, min(1.0, float(getattr(args, opacity_attr, 0.65)))),
        "width": max(1, int(getattr(args, width_attr, 1))),
        "opacity_attr": opacity_attr,
        "width_attr": width_attr,
        "style_profile": resolve_style_profile(style_profile)["id"],
    }


def style_profile_registry_text(active_profile: str = "scientific") -> str:
    active = resolve_style_profile(active_profile)["id"]
    active_entry = resolve_style_renderer_entry(active)
    lines = [
        "Style profile renderer contract",
        "",
        "Purpose: one style profile should drive Taichi material, Datashader point palette, vector line tint, and final post-process together.",
        f"Active profile: {active}",
        f"Active renderer entry: {active_entry['entry']} / {active_entry['post_process']}",
    ]
    for profile_id, spec in STYLE_PROFILE_REGISTRY.items():
        marker = " <active>" if profile_id == active else ""
        lines.extend(
            [
                "",
                f"[{profile_id}]{marker}",
                f"- label: {spec['label']}",
                f"- status: {spec['status']}",
                f"- renderer mode: {spec['renderer_mode']}",
                f"- post-process: {spec['post_process']}",
                f"- terrain bias: {spec['terrain_bias']}",
                f"- vector tint: {spec['vector_tint']}",
                f"- point palette: {spec['point_palette']}",
                f"- Taichi ocean: {spec['taichi_ocean']}",
                f"- notes: {spec['notes']}",
            ]
        )
    return "\n".join(lines)


def apply_style_profile(frame: np.ndarray, profile: str) -> np.ndarray:
    entry = resolve_style_renderer_entry(profile)
    post_process = entry["post_process"]
    if post_process in {"none", "", None}:
        return frame
    out = frame.copy()
    rgb = out[..., :3].astype(np.float32)
    alpha = out[..., 3:4]

    if post_process == "blue-chart-lift":
        blue = np.asarray([0.70, 0.92, 1.18], dtype=np.float32)
        chart = np.asarray([12.0, 22.0, 30.0], dtype=np.float32)
        rgb = rgb * blue + chart
    elif post_process == "green-phosphor":
        lum = rgb[..., 0:1] * 0.24 + rgb[..., 1:2] * 0.66 + rgb[..., 2:3] * 0.10
        rgb = np.concatenate((lum * 0.45, lum * 0.92, lum * 0.34), axis=2)
        rgb += np.asarray([4.0, 18.0, 2.0], dtype=np.float32)
    elif post_process == "sepia-paper-grain":
        lum = rgb[..., 0:1] * 0.30 + rgb[..., 1:2] * 0.58 + rgb[..., 2:3] * 0.12
        t = np.clip(lum / 255.0, 0.0, 1.0)
        ink = np.asarray([58.0, 42.0, 24.0], dtype=np.float32)
        paper = np.asarray([226.0, 198.0, 138.0], dtype=np.float32)
        rgb = ink * (1.0 - t) + paper * t
        yy, xx = np.indices(out.shape[:2], dtype=np.float32)
        grain = ((np.sin(xx * 0.071) + np.sin(yy * 0.113) + np.sin((xx + yy) * 0.037)) * 4.0)
        cx = (xx / max(1.0, float(out.shape[1] - 1))) * 2.0 - 1.0
        cy = (yy / max(1.0, float(out.shape[0] - 1))) * 2.0 - 1.0
        vignette = np.clip(1.0 - (cx * cx + cy * cy) * 0.22, 0.62, 1.0)
        rgb = rgb * vignette[..., None] + grain[..., None]
    else:
        return frame

    out[..., :3] = np.clip(rgb, 0.0, 255.0).astype(np.uint8)
    out[..., 3:4] = alpha
    return out


MARINE_REGIONS_WFS_ENDPOINT = "https://geo.vliz.be/geoserver/MarineRegions/wfs"


def marine_regions_wfs_geojson_url(layer_name: str) -> str:
    type_name = layer_name if ":" in layer_name else f"MarineRegions:{layer_name}"
    url = (
        f"{MARINE_REGIONS_WFS_ENDPOINT}"
        f"?service=WFS&version=1.0.0&request=GetFeature"
        f"&typeName={type_name}&outputFormat=application/json&srsName=EPSG:4326"
    )
    max_features = parse_int_env("MARINE_REGIONS_MAX_FEATURES", 0)
    if max_features > 0:
        url += f"&maxFeatures={max_features}"
    return url


MARINE_REGIONS_DEFAULT_LAYERS = {
    "territorial_sea": "eez_12nm",
    "eez": "eez_boundaries",
    "high_seas": "high_seas",
}


def default_boundary_url(layer_id: str) -> str | None:
    layer_name = MARINE_REGIONS_DEFAULT_LAYERS.get(layer_id)
    if not layer_name:
        return None
    return marine_regions_wfs_geojson_url(layer_name)


def build_empty_boundary_hit() -> dict:
    return {"layer_id": None, "name": "", "distance_px": float("inf")}


def compute_sun_direction() -> tuple[float, float, float]:
    now = datetime.datetime.now(datetime.timezone.utc)
    day_of_year = now.timetuple().tm_yday
    lat_sun = math.radians(-23.44 * math.cos(2.0 * math.pi / 365.0 * (day_of_year + 10)))
    utc_hour = now.hour + now.minute / 60.0 + now.second / 3600.0
    lon_sun = math.radians((12.0 - utc_hour) * 15.0)

    sun_y = math.sin(lat_sun)
    xz_r = math.cos(lat_sun)
    sun_z = xz_r * math.cos(lon_sun)
    sun_x = xz_r * math.sin(lon_sun)
    inv_len = 1.0 / math.sqrt(sun_x * sun_x + sun_y * sun_y + sun_z * sun_z)
    return sun_x * inv_len, sun_y * inv_len, sun_z * inv_len


class BasemapLODManager:
    LEVELS = [
        ("global", "global", float("inf"), 25.0, "global raster / Natural Earth / GEBCO"),
        ("continental", "continental", 25.0, 5.0, "continental DEM and major rivers"),
        ("regional", "regional", 5.0, 0.5, "higher-resolution DEM tiles and hydrology"),
        ("local", "local", 0.5, 0.0, "local tiles / OSM or national datasets"),
    ]

    def choose(self, km_per_pixel: float) -> str:
        value = max(0.0, float(km_per_pixel))
        for lod, _label, upper, lower, _description in self.LEVELS:
            if lower <= value <= upper:
                return lod
        return "local"

    def label(self, lod: str) -> str:
        for level, label, _upper, _lower, _description in self.LEVELS:
            if level == lod:
                return label
        return str(lod)

    def description(self, lod: str) -> str:
        for level, _label, _upper, _lower, description in self.LEVELS:
            if level == lod:
                return description
        return ""

    def decision(
        self,
        km_per_pixel: float,
        projection: str = "globe",
        topo_source: str | None = None,
        topo_step: int | str | None = None,
    ) -> dict:
        lod = self.choose(km_per_pixel)
        projection = str(projection or "globe")
        topo_source = str(topo_source or "gebco")
        topo_step_label = "auto" if topo_step is None else str(topo_step)
        provider_id = f"basemap.{lod}.{projection}"
        source_url = f"{topo_source}:topography"
        renderer_input = {
            "projection": projection,
            "topo_source": topo_source,
            "topo_step": topo_step_label,
            "km_per_pixel": float(km_per_pixel),
            "target_lod": lod,
        }
        manifest = build_provider_cache_manifest(
            provider_id,
            source_url=source_url,
            source_version="runtime-selected",
            license_text="depends on selected topo/basemap provider",
            lod=lod,
            cache_path=str(CACHE_DIR / f"basemap_{projection}_{lod}_topo_step{topo_step_label}.json"),
            schema={"raster": "topography/color/land-water mask", "fields": ["elevation_m", "land_mask"]},
            simplification={
                "km_per_pixel": float(km_per_pixel),
                "projection": projection,
                "topo_step": topo_step_label,
            },
        )
        return {
            "lod": lod,
            "label": self.label(lod),
            "description": self.description(lod),
            "km_per_pixel": float(km_per_pixel),
            "projection": projection,
            "provider_id": provider_id,
            "source_url": source_url,
            "source_hint": self.description(lod),
            "target_adapter": "render_core/taichi_globe.py",
            "renderer_input": renderer_input,
            "cache_path": manifest["cache_path"],
            "manifest": manifest,
        }

    def hydrology_style(self, lod: str) -> dict:
        if lod == "global":
            return {"opacity_scale": 0.58, "width_scale": 0.75, "source_hint": "Natural Earth coarse hydrology"}
        if lod == "continental":
            return {"opacity_scale": 0.82, "width_scale": 1.00, "source_hint": "Natural Earth / HydroRIVERS trunk hydrology"}
        if lod == "regional":
            return {"opacity_scale": 1.00, "width_scale": 1.35, "source_hint": "HydroRIVERS / MERIT Hydro regional hydrology"}
        return {"opacity_scale": 1.00, "width_scale": 1.70, "source_hint": "OSM waterways / national local hydrology"}


class OceanMaterialPolicy:
    LOD_SCALE = {
        "global": {"wave": 0.55, "roughness": 0.70, "foam": 0.45},
        "continental": {"wave": 0.75, "roughness": 0.85, "foam": 0.65},
        "regional": {"wave": 1.00, "roughness": 1.00, "foam": 0.90},
        "local": {"wave": 1.20, "roughness": 1.10, "foam": 1.00},
    }

    def __init__(self, args):
        self.args = args

    def resolve(self, state: dict, lod: str) -> dict:
        scale = self.LOD_SCALE.get(lod, self.LOD_SCALE["global"])
        responsive = bool(getattr(self.args, "ocean_responsive", True))
        material_scale = max(0.0, float(getattr(self.args, "ocean_material_scale", 1.0)))
        style_profile = resolve_style_profile(getattr(self.args, "style_profile", "scientific"))["id"]
        style_modifier = STYLE_PROFILE_MATERIAL_MODIFIERS.get(style_profile, STYLE_PROFILE_MATERIAL_MODIFIERS["scientific"])
        if not responsive:
            material_scale = 0.0
        wave = _clamp01(float(state.get("wave_strength", 0.0)) * scale["wave"] * material_scale * float(style_modifier["wave"]))
        roughness = max(0.02, min(1.0, float(state.get("roughness", 0.18)) * scale["roughness"] * max(0.2, material_scale) * float(style_modifier["roughness"])))
        foam = _clamp01(float(state.get("foam", 0.0)) * scale["foam"] * material_scale * float(style_modifier["foam"]))
        return {
            "enabled": bool(state.get("enabled", False)) and responsive,
            "lod": lod,
            "style_profile": style_profile,
            "style_modifier": style_modifier,
            "wave_strength": wave,
            "roughness": roughness,
            "foam": foam,
            "material_scale": material_scale,
            "source_state": state,
        }

    def status_text(self, state: dict, lod: str) -> str:
        material = self.resolve(state, lod)
        lines = [
            "Ocean material policy",
            "",
            f"- lod: {lod}",
            f"- style profile: {material['style_profile']}",
            f"- responsive: {bool(getattr(self.args, 'ocean_responsive', True))}",
            f"- material scale: {material['material_scale']}",
            f"- renderer enabled: {material['enabled']}",
            f"- wave_strength: {material['wave_strength']:.4f}",
            f"- roughness: {material['roughness']:.4f}",
            f"- foam: {material['foam']:.4f}",
            f"- source state: {state}",
        ]
        return "\n".join(lines)


def build_ocean_material_uniforms(material: dict) -> dict:
    def number(name: str, default: float) -> float:
        try:
            return float(material.get(name, default))
        except (TypeError, ValueError):
            return float(default)

    return {
        "ocean_enabled": bool(material.get("enabled", False)),
        "wave_strength": max(0.0, min(1.0, number("wave_strength", 0.0))),
        "roughness": max(0.02, min(1.0, number("roughness", 0.18))),
        "foam": max(0.0, min(1.0, number("foam", 0.0))),
        "material_scale": max(0.0, number("material_scale", 0.0)),
    }


OCEAN_CONDITION_SCHEMA_TEXT = (
    "Ocean condition schema: JSON/CSV/JSONL may include "
    "wave_height_m, wave_period_s, wind_speed_ms, beaufort, current_speed_ms, sst_c, chlorophyll, "
    "or direct wave_strength, roughness, foam."
)

OCEAN_PROVIDER_REGISTRY = {
    "manual": {
        "label": "Manual controls",
        "kind": "manual",
        "source_attr": None,
        "provider_id": "ocean_conditions.manual",
        "status": "Manual scalar controls feed Taichi ocean material.",
        "spatial_mode": "global-scalar",
        "refresh_hint": "on UI change",
    },
    "file": {
        "label": "Local JSON/CSV/JSONL",
        "kind": "file",
        "source_attr": "ocean_condition_file",
        "provider_id": "ocean_conditions.file",
        "status": "Local file is normalized into wave_strength/roughness/foam.",
        "spatial_mode": "summary-row or nearest-point",
        "refresh_hint": "OCEAN_CONDITION_REFRESH seconds",
    },
    "url": {
        "label": "URL JSON/CSV/JSONL",
        "kind": "url",
        "source_attr": "ocean_condition_url",
        "provider_id": "ocean_conditions.url",
        "status": "Generic URL response is normalized into wave_strength/roughness/foam.",
        "spatial_mode": "summary-row or nearest-point",
        "refresh_hint": "OCEAN_CONDITION_REFRESH seconds",
    },
    "noaa_ww3": {
        "label": "NOAA WaveWatch III adapter",
        "kind": "url",
        "source_attr": "ocean_noaa_ww3_url",
        "provider_id": "ocean_conditions.noaa_ww3",
        "status": "NOAA WW3 adapter port; set OCEAN_NOAA_WW3_URL or --ocean-noaa-ww3-url.",
        "spatial_mode": "gridded forecast adapter port",
        "refresh_hint": "forecast cycle / OCEAN_CONDITION_REFRESH",
    },
    "noaa": {
        "label": "NOAA adapter alias",
        "kind": "url",
        "source_attr": "ocean_noaa_ww3_url",
        "provider_id": "ocean_conditions.noaa_ww3",
        "status": "Backward-compatible alias for noaa_ww3.",
        "spatial_mode": "gridded forecast adapter port",
        "refresh_hint": "forecast cycle / OCEAN_CONDITION_REFRESH",
    },
    "hycom": {
        "label": "HYCOM adapter",
        "kind": "url",
        "source_attr": "ocean_hycom_url",
        "provider_id": "ocean_conditions.hycom",
        "status": "HYCOM adapter port; set OCEAN_HYCOM_URL or --ocean-hycom-url.",
        "spatial_mode": "gridded current/ocean model adapter port",
        "refresh_hint": "model cycle / OCEAN_CONDITION_REFRESH",
    },
    "copernicus": {
        "label": "Copernicus Marine adapter",
        "kind": "url",
        "source_attr": "ocean_copernicus_url",
        "provider_id": "ocean_conditions.copernicus",
        "status": "Copernicus adapter port; set OCEAN_COPERNICUS_URL or --ocean-copernicus-url.",
        "spatial_mode": "gridded marine service adapter port",
        "refresh_hint": "product cycle / OCEAN_CONDITION_REFRESH",
    },
    "local_grid": {
        "label": "Local gridded ocean file",
        "kind": "file",
        "source_attr": "ocean_grid_file",
        "provider_id": "ocean_conditions.local_grid",
        "status": "Local gridded/point extract port; currently reads tabular JSON/CSV/JSONL summary rows.",
        "spatial_mode": "local gridded extract",
        "refresh_hint": "file timestamp or manual reload",
    },
}

OCEAN_RENDER_PORT_CONTRACT = {
    "normalized_fields": ["wave_strength", "roughness", "foam", "timestamp", "source"],
    "accepted_physical_fields": [
        "wave_height_m",
        "wave_period_s",
        "wind_speed_ms",
        "beaufort",
        "current_speed_ms",
        "sst_c",
        "chlorophyll",
    ],
    "renderer_fields": ["enabled", "wave_strength", "roughness", "foam"],
    "future_spatial_fields": ["lon", "lat", "valid_time", "grid_id", "confidence"],
    "taichi_owner": "OceanMaterialPolicy -> TaichiGlobeRenderer.render(... ocean fields ...)",
    "adapter_rule": "Every external ocean source must normalize to scalar material fields before the render loop.",
}


def ocean_provider_registry_text() -> str:
    lines = ["Ocean provider registry", ""]
    for source, meta in OCEAN_PROVIDER_REGISTRY.items():
        lines.append(f"- {source}: {meta['label']}")
        lines.append(f"  provider: {meta['provider_id']}")
        lines.append(f"  kind: {meta['kind']}")
        lines.append(f"  source attr: {meta['source_attr'] or '(none)'}")
        lines.append(f"  spatial mode: {meta.get('spatial_mode', 'global-scalar')}")
        lines.append(f"  refresh: {meta.get('refresh_hint', 'manual')}")
        lines.append(f"  status: {meta['status']}")
    lines.extend(["", OCEAN_CONDITION_SCHEMA_TEXT])
    return "\n".join(lines)


def ocean_render_port_contract_text() -> str:
    lines = [
        "Ocean render port contract",
        "",
        f"- Taichi owner: {OCEAN_RENDER_PORT_CONTRACT['taichi_owner']}",
        f"- adapter rule: {OCEAN_RENDER_PORT_CONTRACT['adapter_rule']}",
        "- normalized fields: " + ", ".join(OCEAN_RENDER_PORT_CONTRACT["normalized_fields"]),
        "- accepted physical fields: " + ", ".join(OCEAN_RENDER_PORT_CONTRACT["accepted_physical_fields"]),
        "- renderer fields: " + ", ".join(OCEAN_RENDER_PORT_CONTRACT["renderer_fields"]),
        "- future spatial fields: " + ", ".join(OCEAN_RENDER_PORT_CONTRACT["future_spatial_fields"]),
        "",
        "Provider ports:",
    ]
    for source, meta in OCEAN_PROVIDER_REGISTRY.items():
        lines.append(
            f"- {source}: {meta['provider_id']} | {meta.get('spatial_mode', 'global-scalar')} | {meta.get('refresh_hint', 'manual')}"
        )
    return "\n".join(lines)


class OceanSpatialSamplingPolicy:
    def __init__(self, args) -> None:
        self.args = args

    def decision(self, source: str, source_kind: str, spatial_mode: str, lod: str) -> dict:
        lat = max(-90.0, min(90.0, float(getattr(self.args, "ocean_provider_lat", 0.0))))
        lon = ((float(getattr(self.args, "ocean_provider_lon", 0.0)) + 180.0) % 360.0) - 180.0
        spatial_mode = str(spatial_mode or "global-scalar")
        if spatial_mode == "global-scalar":
            sample_mode = "global-scalar"
            adapter_expectation = "Use one normalized sea-state record for the whole globe."
        elif "gridded" in spatial_mode or "grid" in spatial_mode:
            sample_mode = "point-from-grid-port"
            adapter_expectation = "Tabular extracts use nearest lat/lon row now; future gridded adapters should extract nearest/bilinear grid cell before normalization."
        else:
            sample_mode = "point-summary"
            adapter_expectation = "If lat/lon columns exist, select nearest row to ocean_provider_lat/lon; otherwise use the latest summary row."
        return {
            "source": str(source),
            "source_kind": str(source_kind),
            "spatial_mode": spatial_mode,
            "sample_mode": sample_mode,
            "lod": str(lod),
            "lat": float(lat),
            "lon": float(lon),
            "adapter_expectation": adapter_expectation,
            "renderer_contract": "OceanConditionProvider emits scalar fields; TaichiGlobeRenderer receives wave_strength/roughness/foam only.",
            "future_fields": ["lon", "lat", "valid_time", "grid_id", "interpolation", "confidence"],
        }

    def text(self, decision: dict) -> str:
        lines = [
            "Ocean spatial sampling policy",
            "",
            f"- source: {decision.get('source', '')}",
            f"- source kind: {decision.get('source_kind', '')}",
            f"- spatial mode: {decision.get('spatial_mode', '')}",
            f"- sample mode: {decision.get('sample_mode', '')}",
            f"- LOD: {decision.get('lod', '')}",
            f"- sampling point: lat={float(decision.get('lat', 0.0)):.4f}, lon={float(decision.get('lon', 0.0)):.4f}",
            f"- adapter expectation: {decision.get('adapter_expectation', '')}",
            f"- renderer contract: {decision.get('renderer_contract', '')}",
            "- future fields: " + ", ".join(decision.get("future_fields", [])),
        ]
        return "\n".join(lines)


OCEAN_CONDITION_ALIASES = {
    "wave_height_m": ("wave_height_m", "wave_height", "significant_wave_height", "swh", "hs"),
    "wave_period_s": ("wave_period_s", "wave_period", "peak_wave_period", "tp"),
    "wind_speed_ms": ("wind_speed_ms", "wind_speed", "wind_mps", "wind_ms"),
    "beaufort": ("beaufort", "beaufort_scale", "bft"),
    "current_speed_ms": ("current_speed_ms", "current_speed", "current_mps", "current_ms"),
    "sst_c": ("sst_c", "sea_surface_temperature_c", "sst", "temperature_c"),
    "chlorophyll": ("chlorophyll", "chlorophyll_a", "chl"),
    "wave_strength": ("wave_strength", "wave_intensity"),
    "roughness": ("roughness", "ocean_roughness"),
    "foam": ("foam", "ocean_foam"),
}


OCEAN_SPATIAL_ALIASES = {
    "lat": ("lat", "latitude", "y", "point_lat", "sample_lat"),
    "lon": ("lon", "longitude", "long", "x", "point_lon", "sample_lon"),
    "time": ("time", "timestamp", "valid_time", "datetime", "forecast_time"),
}


def _clamp01(value: float) -> float:
    return max(0.0, min(float(value), 1.0))


def select_ocean_condition_sample_frame(frame: pd.DataFrame, spatial_decision: dict) -> tuple[pd.DataFrame, dict]:
    if frame.empty:
        return frame, {
            "selected": False,
            "reason": "empty-frame",
            "mode": spatial_decision.get("sample_mode", "unknown"),
        }
    lat_col = find_column(frame, OCEAN_SPATIAL_ALIASES["lat"])
    lon_col = find_column(frame, OCEAN_SPATIAL_ALIASES["lon"])
    if lat_col is None or lon_col is None:
        return frame.tail(1), {
            "selected": False,
            "reason": "no-lat-lon-columns; using latest row",
            "mode": spatial_decision.get("sample_mode", "unknown"),
            "lat_column": lat_col,
            "lon_column": lon_col,
        }
    lat_values = pd.to_numeric(frame[lat_col], errors="coerce")
    lon_values = pd.to_numeric(frame[lon_col], errors="coerce")
    valid = lat_values.notna() & lon_values.notna()
    if not valid.any():
        return frame.tail(1), {
            "selected": False,
            "reason": "lat-lon-columns-not-numeric; using latest row",
            "mode": spatial_decision.get("sample_mode", "unknown"),
            "lat_column": lat_col,
            "lon_column": lon_col,
        }
    target_lat = float(spatial_decision.get("lat", 0.0))
    target_lon = float(spatial_decision.get("lon", 0.0))
    lon_delta = ((lon_values[valid].to_numpy(dtype=np.float64) - target_lon + 180.0) % 360.0) - 180.0
    lat_delta = lat_values[valid].to_numpy(dtype=np.float64) - target_lat
    distance2 = lat_delta * lat_delta + lon_delta * lon_delta
    selected_label = frame[valid].index[int(np.argmin(distance2))]
    selected = frame.loc[[selected_label]]
    selected_lat = float(pd.to_numeric(selected.iloc[0][lat_col], errors="coerce"))
    selected_lon = float(pd.to_numeric(selected.iloc[0][lon_col], errors="coerce"))
    time_col = find_column(frame, OCEAN_SPATIAL_ALIASES["time"])
    return selected, {
        "selected": True,
        "reason": "nearest-lat-lon-row",
        "mode": spatial_decision.get("sample_mode", "unknown"),
        "lat_column": lat_col,
        "lon_column": lon_col,
        "target_lat": target_lat,
        "target_lon": target_lon,
        "selected_lat": selected_lat,
        "selected_lon": selected_lon,
        "distance_degrees": float(np.sqrt(float(np.min(distance2)))),
        "source_rows": int(len(frame)),
        "selected_index": str(selected_label),
        "time_column": time_col or "",
    }


def normalize_ocean_condition_frame(frame: pd.DataFrame) -> dict:
    if frame.empty:
        return {}
    row = frame.dropna(how="all").tail(1)
    if row.empty:
        return {}
    row = row.iloc[0]
    values = {}
    for target, aliases in OCEAN_CONDITION_ALIASES.items():
        col = find_column(frame, aliases)
        if col is None:
            continue
        value = pd.to_numeric(pd.Series([row.get(col)]), errors="coerce").iloc[0]
        if pd.notna(value):
            values[target] = float(value)

    wave_height = max(0.0, values.get("wave_height_m", 0.0))
    wave_period = max(0.0, values.get("wave_period_s", 0.0))
    wind_speed = max(0.0, values.get("wind_speed_ms", 0.0))
    beaufort = max(0.0, values.get("beaufort", 0.0))
    current_speed = max(0.0, values.get("current_speed_ms", 0.0))
    chlorophyll = max(0.0, values.get("chlorophyll", 0.0))

    if "wave_strength" not in values:
        values["wave_strength"] = _clamp01(
            0.12 + wave_height / 8.0 + wave_period / 60.0 + wind_speed / 55.0 + beaufort / 20.0 + current_speed / 3.0
        )
    else:
        values["wave_strength"] = _clamp01(values["wave_strength"])
    if "roughness" not in values:
        values["roughness"] = max(0.02, min(1.0, 0.20 + wave_height / 10.0 + wave_period / 90.0 + wind_speed / 45.0 + beaufort / 18.0))
    else:
        values["roughness"] = max(0.02, min(float(values["roughness"]), 1.0))
    if "foam" not in values:
        values["foam"] = _clamp01(wave_height / 9.0 + wind_speed / 70.0 + beaufort / 22.0 + chlorophyll / 25.0)
    else:
        values["foam"] = _clamp01(values["foam"])
    return values


def ocean_condition_alias_matches(frame: pd.DataFrame) -> dict:
    if frame.empty:
        return {}
    matches = {}
    for target, aliases in OCEAN_CONDITION_ALIASES.items():
        col = find_column(frame, aliases)
        if col is not None:
            matches[target] = col
    return matches


def build_ocean_normalization_report(
    frame: pd.DataFrame | None,
    normalized: dict,
    source: str,
    source_kind: str,
    source_value: str = "",
    mode: str = "external",
    spatial_selection: dict | None = None,
) -> dict:
    columns = list(frame.columns) if frame is not None and not frame.empty else []
    matches = ocean_condition_alias_matches(frame) if frame is not None and not frame.empty else {}
    missing = [field for field in OCEAN_CONDITION_ALIASES if field not in matches]
    return {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source": str(source),
        "source_kind": str(source_kind),
        "source_value": str(source_value or ""),
        "mode": str(mode),
        "rows": int(len(frame)) if frame is not None else 0,
        "columns": columns,
        "alias_matches": matches,
        "missing_alias_groups": missing,
        "normalized": dict(normalized or {}),
        "spatial_selection": dict(spatial_selection or {}),
        "renderer_fields": {
            key: normalized.get(key)
            for key in ("wave_strength", "roughness", "foam")
            if key in normalized
        },
        "formula_notes": [
            "wave_strength is derived from wave_height_m, wave_period_s, wind_speed_ms, beaufort, and current_speed_ms when not directly supplied.",
            "roughness is derived from wave height/period/wind/beaufort when not directly supplied.",
            "foam is derived from wave height, wind, beaufort, and chlorophyll when not directly supplied.",
            "LOD and style profile are applied later by OceanConditionProvider.sample and OceanMaterialPolicy.resolve.",
        ],
    }


def ocean_condition_normalization_report_text(report: dict) -> str:
    lines = [
        "Ocean condition normalization report",
        "",
        f"- source: {report.get('source', '')}",
        f"- source kind: {report.get('source_kind', '')}",
        f"- mode: {report.get('mode', '')}",
        f"- rows: {int(report.get('rows', 0)):,}",
        f"- columns: {', '.join(report.get('columns', [])[:24]) or '(none)'}",
        "",
        "Alias matches:",
    ]
    matches = report.get("alias_matches", {}) or {}
    if matches:
        for target, column in matches.items():
            lines.append(f"- {target}: {column}")
    else:
        lines.append("- no external aliases matched")
    lines.extend(["", "Renderer fields:"])
    renderer_fields = report.get("renderer_fields", {}) or {}
    if renderer_fields:
        for key, value in renderer_fields.items():
            try:
                lines.append(f"- {key}: {float(value):.4f}")
            except Exception:
                lines.append(f"- {key}: {value}")
    else:
        lines.append("- no renderer fields available")
    missing = report.get("missing_alias_groups", []) or []
    lines.extend(["", "Missing alias groups: " + (", ".join(missing) if missing else "(none)")])
    spatial_selection = report.get("spatial_selection", {}) or {}
    if spatial_selection:
        lines.extend(
            [
                "",
                "Spatial selection:",
                f"- selected: {spatial_selection.get('selected', False)}",
                f"- reason: {spatial_selection.get('reason', '')}",
                f"- mode: {spatial_selection.get('mode', '')}",
            ]
        )
        if spatial_selection.get("selected"):
            lines.append(
                f"- target: lat={float(spatial_selection.get('target_lat', 0.0)):.4f}, lon={float(spatial_selection.get('target_lon', 0.0)):.4f}"
            )
            lines.append(
                f"- selected: lat={float(spatial_selection.get('selected_lat', 0.0)):.4f}, lon={float(spatial_selection.get('selected_lon', 0.0)):.4f}"
            )
            lines.append(f"- distance degrees: {float(spatial_selection.get('distance_degrees', 0.0)):.4f}")
            lines.append(f"- source rows: {int(spatial_selection.get('source_rows', 0)):,}")
        else:
            lines.append("- fallback behavior: summary/latest row normalization")
    lines.extend(["", "Formula notes:"])
    for note in report.get("formula_notes", []):
        lines.append(f"- {note}")
    return "\n".join(lines)


class OceanConditionProvider:
    LOD_SCALE = {"global": 0.65, "continental": 0.82, "regional": 1.0, "local": 1.0}

    def __init__(self, args) -> None:
        self.args = args
        self.last_status = "manual ocean parameters active; no external ocean feed loaded."
        self.last_read = 0.0
        self.cached_conditions: dict = {}
        self.last_decision: dict = {}
        self.spatial_sampling_policy = OceanSpatialSamplingPolicy(args)
        self.last_spatial_sampling_decision: dict = self.spatial_sampling_policy.decision(
            "manual",
            "manual",
            "global-scalar",
            "global",
        )
        self.last_normalization_report: dict = build_ocean_normalization_report(
            None,
            {},
            source="manual",
            source_kind="manual",
            mode="not-read-yet",
            spatial_selection=self.last_spatial_sampling_decision,
        )

    def _source_meta(self, source: str | None = None) -> dict:
        source = str(source or getattr(self.args, "ocean_condition_source", "manual") or "manual")
        return OCEAN_PROVIDER_REGISTRY.get(source, OCEAN_PROVIDER_REGISTRY["manual"])

    def _source_value(self, meta: dict) -> str:
        attr = meta.get("source_attr")
        if not attr:
            return ""
        return str(getattr(self.args, attr, "") or "")

    def decision(self, lod: str) -> dict:
        source = str(getattr(self.args, "ocean_condition_source", "manual") or "manual")
        meta = self._source_meta(source)
        lod_scale = self.LOD_SCALE.get(lod, 1.0)
        source_url = self._source_value(meta) or ("manual" if meta["kind"] == "manual" else f"{source}:provider-port")
        provider_id = meta["provider_id"]
        spatial_decision = self.spatial_sampling_policy.decision(
            source,
            meta["kind"],
            meta.get("spatial_mode", "global-scalar"),
            lod,
        )
        manifest = build_provider_cache_manifest(
            provider_id,
            source_url=source_url,
            source_version="runtime",
            license_text="depends on selected ocean condition source",
            lod=lod,
            cache_path=str(CACHE_DIR / f"ocean_conditions_{source}_cache.json") if meta["kind"] in {"file", "url"} else "",
            schema={"fields": ["wave_strength", "roughness", "foam", "timestamp"]},
            simplification={
                "refresh_seconds": "OCEAN_CONDITION_REFRESH",
                "lod_scale": lod_scale,
                "spatial_mode": meta.get("spatial_mode", "global-scalar"),
                "sample_mode": spatial_decision["sample_mode"],
                "sample_lat": spatial_decision["lat"],
                "sample_lon": spatial_decision["lon"],
                "render_contract": OCEAN_RENDER_PORT_CONTRACT["renderer_fields"],
            },
        )
        decision = {
            "provider_id": provider_id,
            "source": source,
            "source_url": source_url,
            "source_kind": meta["kind"],
            "source_attr": meta.get("source_attr"),
            "lod": lod,
            "lod_scale": lod_scale,
            "target_adapter": "data_sources/ocean_condition_provider.py",
            "renderer_input": "scalar ocean material fields: wave_strength, roughness, foam",
            "provider_status": meta["status"],
            "spatial_mode": meta.get("spatial_mode", "global-scalar"),
            "spatial_sampling": spatial_decision,
            "refresh_hint": meta.get("refresh_hint", "manual"),
            "render_port_contract": OCEAN_RENDER_PORT_CONTRACT,
            "manifest": manifest,
        }
        self.last_decision = decision
        self.last_spatial_sampling_decision = spatial_decision
        return decision

    def sample(self, lod: str) -> dict:
        decision = self.decision(lod)
        source = decision["source"]
        lod_scale = float(decision["lod_scale"])
        external = self._read_if_due(source)
        if source == "manual" or not external:
            if source == "manual":
                self.last_status = "manual ocean parameters active."
            elif decision["source_kind"] in {"file", "url"}:
                if "missing" not in self.last_status and "failed" not in self.last_status:
                    self.last_status = f"{source} ocean provider has no readable data yet; manual parameters are used. {OCEAN_CONDITION_SCHEMA_TEXT}"
            wave_strength = float(getattr(self.args, "ocean_wave_strength", 0.28))
            roughness = float(getattr(self.args, "ocean_roughness", 0.48))
            foam = float(getattr(self.args, "ocean_foam", 0.16))
        else:
            wave_strength = float(external.get("wave_strength", getattr(self.args, "ocean_wave_strength", 0.28)))
            roughness = float(external.get("roughness", getattr(self.args, "ocean_roughness", 0.48)))
            foam = float(external.get("foam", getattr(self.args, "ocean_foam", 0.16)))
            self.last_status = f"{source} ocean condition data applied. {OCEAN_CONDITION_SCHEMA_TEXT}"
        state = {
            "enabled": bool(getattr(self.args, "ocean_material", True)),
            "wave_strength": _clamp01(wave_strength * lod_scale),
            "roughness": max(0.02, min(roughness, 1.0)),
            "foam": _clamp01(foam * lod_scale),
        }
        if source == "manual" or not external:
            self.last_normalization_report = build_ocean_normalization_report(
                None,
                state,
                source=source,
                source_kind=decision["source_kind"],
                source_value=decision["source_url"],
                mode="manual" if source == "manual" else "manual-fallback",
                spatial_selection=decision.get("spatial_sampling", {}),
            )
        else:
            self.last_normalization_report["renderer_fields_after_lod"] = {
                "wave_strength": state["wave_strength"],
                "roughness": state["roughness"],
                "foam": state["foam"],
                "lod_scale": lod_scale,
            }
        return state

    def _read_if_due(self, source: str) -> dict:
        meta = self._source_meta(source)
        if meta["kind"] not in {"file", "url"}:
            return {}
        now = time.time()
        refresh = max(0.0, float(getattr(self.args, "ocean_condition_refresh", 60.0)))
        if self.cached_conditions and refresh > 0 and now - self.last_read < refresh:
            record_data_fetch_event("ocean", source, "memory-cache-hit", source=self._source_value(meta), message="using cached normalized ocean conditions")
            return self.cached_conditions
        try:
            source_value = self._source_value(meta)
            if meta["kind"] == "file":
                file_path = source_value
                if not file_path:
                    self.last_status = f"ocean file source missing {meta.get('source_attr')}. {OCEAN_CONDITION_SCHEMA_TEXT}"
                    record_data_fetch_event("ocean", source, "missing", message=f"missing {meta.get('source_attr')}")
                    return {}
                record_data_fetch_event("ocean", source, "file-read", source=str(file_path), message="reading ocean condition file")
                text = read_file_text(Path(file_path))
                frame = dataframe_from_text(text, str(file_path))
            else:
                url = source_value
                if not url:
                    self.last_status = f"ocean url source missing {meta.get('source_attr')}. {OCEAN_CONDITION_SCHEMA_TEXT}"
                    record_data_fetch_event("ocean", source, "missing", message=f"missing {meta.get('source_attr')}")
                    return {}
                text = read_url_text(str(url), timeout=float(getattr(self.args, "timeout", 20.0)), progress_label=f"ocean:{source}")
                frame = dataframe_from_text(text, str(url))
            sampled_frame, spatial_selection = select_ocean_condition_sample_frame(frame, self.last_spatial_sampling_decision)
            self.cached_conditions = normalize_ocean_condition_frame(sampled_frame)
            self.last_normalization_report = build_ocean_normalization_report(
                sampled_frame,
                self.cached_conditions,
                source=source,
                source_kind=meta["kind"],
                source_value=source_value,
                mode="external",
                spatial_selection=spatial_selection,
            )
            self.last_read = now
            record_data_fetch_event("ocean", source, "normalized", source=source_value, message="ocean data normalized for Taichi material")
            self.last_status = f"{source} ocean condition data read from {meta['kind']} source. {OCEAN_CONDITION_SCHEMA_TEXT}"
        except Exception as exc:
            self.last_status = f"ocean condition read failed: {exc}"
            return {}
        return self.cached_conditions

    def status_text(self) -> str:
        return self.last_status

    def decision_text(self, lod: str) -> str:
        decision = self.decision(lod)
        manifest = decision["manifest"]
        lines = [
            f"Ocean provider decision for LOD={lod}",
            f"- provider: {decision['provider_id']}",
            f"- source: {decision['source_url']}",
            f"- source kind: {decision['source_kind']}",
            f"- source attr: {decision['source_attr'] or '(none)'}",
            f"- lod scale: {decision['lod_scale']}",
            f"- target adapter: {decision['target_adapter']}",
            f"- renderer input: {decision['renderer_input']}",
            f"- cache: {manifest['cache_path'] or '(none)'}",
            f"- schema: {manifest['schema']}",
            f"- provider status: {decision['provider_status']}",
            f"- status: {self.last_status}",
        ]
        return "\n".join(lines)

    def normalization_report_text(self) -> str:
        return ocean_condition_normalization_report_text(self.last_normalization_report)

    def spatial_sampling_text(self) -> str:
        return self.spatial_sampling_policy.text(self.last_spatial_sampling_decision)


class HydrologyLODSourcePolicy:
    PRESETS = {
        "global": {
            "natural_earth_source": "110m",
            "preferred": "Natural Earth 110m",
            "next": "global rivers and major lakes only",
        },
        "continental": {
            "natural_earth_source": "50m",
            "preferred": "Natural Earth 50m / HydroRIVERS trunk",
            "next": "continental trunk hydrology; HydroRIVERS adapter is the next strict source",
        },
        "regional": {
            "natural_earth_source": "10m",
            "preferred": "HydroRIVERS / MERIT Hydro",
            "next": "regional hydrology should switch to HydroRIVERS or MERIT Hydro",
        },
        "local": {
            "natural_earth_source": "10m",
            "preferred": "OSM waterways / national hydrology",
            "next": "local hydrology should use OSM or national datasets, not only Natural Earth",
        },
    }

    def __init__(self, args) -> None:
        self.args = args

    def recommendation(self, lod: str, layer_id: str) -> dict:
        source_mode = str(getattr(self.args, "hydrology_source_mode", "lod") or "lod")
        if source_mode == "manual":
            manual_source = str(getattr(self.args, "hydrology_source", "naturalearth") or "naturalearth")
            return {
                "mode": "manual",
                "natural_earth_source": manual_source,
                "preferred": manual_source,
                "status": f"manual hydrology source: {manual_source}",
            }
        if source_mode == "strict":
            strict_source = resolve_hydrology_strict_provider(self.args, layer_id)
            if strict_source["configured"]:
                return {
                    "mode": "strict",
                    "natural_earth_source": "strict-provider",
                    "preferred": strict_source["label"],
                    "status": f"strict hydrology source configured: {strict_source['label']}",
                    "strict_source": strict_source,
                }
            preset = self.PRESETS.get(lod, self.PRESETS["global"])
            return {
                "mode": "strict-missing",
                "natural_earth_source": preset["natural_earth_source"],
                "preferred": preset["preferred"],
                "status": f"strict hydrology requested but no named strict provider is configured for {layer_id}; falling back to {preset['preferred']}",
                "strict_source": strict_source,
            }
        preset = self.PRESETS.get(lod, self.PRESETS["global"])
        layer_name = HYDROLOGY_SPECS.get(layer_id, {}).get("name", layer_id)
        return {
            "mode": "lod",
            "natural_earth_source": preset["natural_earth_source"],
            "preferred": preset["preferred"],
            "status": f"{layer_name} LOD recommendation: {preset['preferred']}; {preset['next']}",
        }

    def decision(self, lod: str, layer_id: str) -> dict:
        spec = HYDROLOGY_SPECS[layer_id]
        prefix = spec["prefix"]
        recommendation = self.recommendation(lod, layer_id)
        registry = LAYER_PROVIDER_REGISTRY.get(layer_id, {})
        explicit_file = getattr(self.args, f"{prefix}_file", None)
        explicit_url = getattr(self.args, f"{prefix}_url", None)
        provider_id = registry.get("provider", f"hydrology.{layer_id}")
        strict_source = recommendation.get("strict_source") or resolve_hydrology_strict_provider(self.args, layer_id)
        if recommendation["mode"] == "strict" and strict_source.get("configured"):
            explicit_file = strict_source["file_path"]
            explicit_url = strict_source["url"]
            provider_id = strict_source["provider_id"]
        if explicit_file:
            provider_id = f"hydrology.file.{layer_id}"
        elif explicit_url:
            provider_id = f"hydrology.url.{layer_id}"
        if recommendation["mode"] == "strict" and strict_source.get("configured"):
            provider_id = strict_source["provider_id"]
        decision = {
            "layer_id": layer_id,
            "provider_id": provider_id,
            "source_mode": recommendation["mode"],
            "natural_earth_layer": spec["natural_earth_layer"],
            "natural_earth_source": recommendation["natural_earth_source"],
            "preferred": recommendation["preferred"],
            "status": recommendation["status"],
            "strict_source": strict_source,
            "file_path": explicit_file,
            "url": explicit_url,
            "target_adapter": registry.get("provider", f"hydrology.{layer_id}"),
            "renderer_input": registry.get("renderer_input", "normalized lon/lat line geometry"),
            "manifest": build_provider_cache_manifest(
                provider_id,
                source_url=explicit_url or explicit_file or f"naturalearth:{spec['natural_earth_layer']}:{recommendation['natural_earth_source']}",
                source_version=strict_source.get("metadata", {}).get("source_version") or "runtime-selected",
                license_text=strict_source.get("metadata", {}).get("license") or "Natural Earth public domain unless an explicit/strict source is supplied",
                lod=lod,
                cache_path=str(CACHE_DIR / f"vector_{layer_id}.geojson"),
                schema={
                    "geometry": "LineString/MultiLineString",
                    "fields": ["name"],
                    "projection": strict_source.get("metadata", {}).get("projection", ""),
                    "schema_note": strict_source.get("metadata", {}).get("schema_note", ""),
                    "attribution": strict_source.get("metadata", {}).get("attribution", ""),
                },
                simplification={
                    "decimate": "HYDROLOGY_DECIMATE",
                    "source_mode": recommendation["mode"],
                    "strict_tier": strict_source.get("tier", "not-configured"),
                    "strict_provider": strict_source.get("provider_id", ""),
                    "strict_metadata_complete": strict_source.get("metadata_complete", False),
                    "strict_metadata_missing": strict_source.get("metadata_missing", []),
                },
            ),
        }
        return decision


class BoundaryLODSourcePolicy:
    PRESETS = {
        "global": {"natural_earth_source": "110m", "decimate": 4},
        "continental": {"natural_earth_source": "50m", "decimate": 2},
        "regional": {"natural_earth_source": "10m", "decimate": 1},
        "local": {"natural_earth_source": "10m", "decimate": 1},
    }

    def __init__(self, args) -> None:
        self.args = args

    def decision(self, lod: str, layer_id: str) -> dict:
        spec = BOUNDARY_SPECS[layer_id]
        prefix = spec.get("prefix", layer_id)
        preset = self.PRESETS.get(lod, self.PRESETS["global"])
        registry = LAYER_PROVIDER_REGISTRY.get(layer_id, {})
        explicit_file = getattr(self.args, f"{prefix}_file", None)
        explicit_url = getattr(self.args, f"{prefix}_url", None)
        natural_earth_layer = spec.get("natural_earth_layer")
        natural_earth_source = preset["natural_earth_source"]
        marine_layer = spec.get("marine_regions_layer")
        default_url = marine_regions_wfs_geojson_url(marine_layer) if marine_layer else None
        provider_id = registry.get("provider", f"boundary.{layer_id}")
        if explicit_file:
            provider_id = f"boundary.file.{layer_id}"
        elif explicit_url:
            provider_id = f"boundary.url.{layer_id}"
        elif natural_earth_layer:
            provider_id = f"naturalearth.{natural_earth_layer}"
        elif marine_layer:
            provider_id = f"marine_regions.{layer_id}"
        source_url = explicit_url or explicit_file or (f"naturalearth:{natural_earth_layer}:{natural_earth_source}" if natural_earth_layer else default_url)
        status = "manual file" if explicit_file else "manual url" if explicit_url else "Natural Earth" if natural_earth_layer else "Marine Regions WFS port"
        return {
            "layer_id": layer_id,
            "provider_id": provider_id,
            "file_path": explicit_file,
            "url": explicit_url or (None if natural_earth_layer else default_url),
            "natural_earth_layer": natural_earth_layer,
            "natural_earth_source": natural_earth_source,
            "marine_regions_layer": marine_layer,
            "decimate": max(1, int(getattr(self.args, "boundary_decimate", preset["decimate"]))),
            "target_adapter": "vector_layers/boundary_provider.py",
            "renderer_input": registry.get("renderer_input", "normalized lon/lat line geometry"),
            "status": status,
            "manifest": build_provider_cache_manifest(
                provider_id,
                source_url=source_url or "manual",
                source_version="runtime-selected",
                license_text="Natural Earth public domain or Marine Regions/VLIZ attribution depending on provider",
                lod=lod,
                cache_path=str(CACHE_DIR / f"vector_boundary_{layer_id}.geojson"),
                schema={"geometry": "LineString/MultiLineString/Polygon boundary", "fields": ["name", "territory", "sovereignt"]},
                simplification={"decimate": max(1, int(getattr(self.args, "boundary_decimate", preset["decimate"])))},
            ),
        }


class HybridRenderController:
    LAYER_LABELS = {
        "globe": "Earth base",
        "lakes": "Lakes",
        "rivers": "Rivers",
        "borders": "Borders",
        "territorial_sea": "Territorial sea",
        "eez": "Exclusive economic zone",
        "high_seas": "High seas",
        "ais": "AIS vessels",
        "aircraft": "ADS-B aircraft",
        "pins": "Research pins",
        "vehicle_icons": "Vehicle icons",
        "clouds": "Satellite/cloud volume",
        "ice": "Ice and snow",
        "forest": "Forest",
        "contours": "Terrain contours",
        "scale": "Scale bar",
    }

    def __init__(self, args) -> None:
        self.args = args
        self.width = args.width
        self.height = args.height
        self.yaw = 0.0
        self.pitch = 0.0
        self.zoom = 1.0
        self.last_ais_read = 0.0
        self.frame_index = 0
        self.globe_dirty = True
        self.overlay_dirty = True
        self.current_ais = pd.DataFrame(columns=["lon", "lat"])
        self.current_projected = pd.DataFrame(columns=["screen_x", "screen_y"])
        self.current_sampled_projected = pd.DataFrame(columns=["screen_x", "screen_y"])
        self.current_aircraft = pd.DataFrame(columns=["lon", "lat"])
        self.current_aircraft_projected = pd.DataFrame(columns=["screen_x", "screen_y"])
        self.current_aircraft_sampled_projected = pd.DataFrame(columns=["screen_x", "screen_y"])
        self.selected_vehicle = None
        self.visible_count = 0
        self.rendered_count = 0
        self.total_count = 0
        self.aircraft_visible_count = 0
        self.aircraft_rendered_count = 0
        self.aircraft_total_count = 0
        self.last_aircraft_read = 0.0
        self.last_render_ms = 0.0
        self.interaction_active = False
        self.render_budget_policy = LayerRenderBudgetPolicy()
        self.flip_longitude = bool(args.flip_longitude)
        self.flip_latitude = bool(args.flip_latitude)

        topo = load_topography(args.topo_step, args.topo_source, args.topo_chunk_rows)
        land_mask = load_land_mask(topo, args.land_mask_source, args.topo_chunk_rows, args.sea_level_m)
        ice_mask = load_ice_mask(topo, args.ice_source, args.topo_chunk_rows)
        forest_density = load_forest_density(topo, land_mask, args.forest_source, args.forest_density_file, args.topo_chunk_rows)
        self.topo = topo
        self.land_mask = land_mask
        self.ice_mask = ice_mask
        self.forest_density = forest_density
        stars = load_stars(args.star_mag_limit, args.show_stars)
        self.globe = TaichiGlobeRenderer(
            topo=topo,
            land_mask=land_mask,
            ice_mask=ice_mask,
            forest_density=forest_density,
            colormap=build_taichi_colormap(),
            stars=stars,
            width=args.width,
            height=args.height,
            bump_scale=args.bump_scale,
            show_grid=args.show_grid,
            sea_level_m=args.sea_level_m,
        )
        self.ais_source = AISSource(
            ais_url=args.ais_url,
            ais_file=args.ais_file,
            timeout=args.timeout,
            ais_db_url=args.ais_db_url,
            ais_db_query=args.ais_db_query,
            ais_db_table=args.ais_db_table,
            ais_db_limit=args.ais_db_limit,
        )
        self.aircraft_source = AircraftSource(
            aircraft_url=getattr(args, "aircraft_url", None),
            aircraft_file=getattr(args, "aircraft_file", None),
            timeout=args.timeout,
            aircraft_db_url=getattr(args, "aircraft_db_url", None),
            aircraft_db_query=getattr(args, "aircraft_db_query", None),
            aircraft_db_table=getattr(args, "aircraft_db_table", DEFAULT_AIRCRAFT_DB_TABLE),
            aircraft_db_limit=getattr(args, "aircraft_db_limit", DEFAULT_AIRCRAFT_DB_LIMIT),
        )
        self.overlay_renderer = AISDatashaderOverlay(
            width=args.width,
            height=args.height,
            color_by=args.color_by,
            point_px=args.point_px,
            speed_span=(args.speed_min, args.speed_max),
        )
        self.aircraft_overlay_renderer = AircraftDatashaderOverlay(
            width=args.width,
            height=args.height,
            color_by=getattr(args, "aircraft_color_by", "altitude"),
            point_px=getattr(args, "aircraft_point_px", 2),
        )
        self.globe_rgba = np.zeros((args.height, args.width, 4), dtype=np.uint8)
        self.overlay_rgba = np.zeros_like(self.globe_rgba)
        self.aircraft_overlay_rgba = np.zeros_like(self.globe_rgba)
        self.pin_overlay_rgba = np.zeros_like(self.globe_rgba)
        self.frame_rgba = np.zeros_like(self.globe_rgba)
        self.globe_mask = np.zeros((args.height, args.width), dtype=np.uint8)
        self.pin_records, self.selected_pin_id = load_pin_records(
            getattr(args, "pin_file", None),
            getattr(args, "pin_json", None),
        )
        self.current_pin_projections: list[dict[str, object]] = []
        self.pin_visible_count = 0
        self.output_path = Path(args.output) if args.output else None
        if self.output_path:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.lod_manager = BasemapLODManager()
        self.basemap_lod = self.lod_manager.choose(self.current_km_per_pixel())
        self.hydrology_render_profile = HydrologyRenderLODProfile(args)
        self.hydrology_lod_policy = HydrologyLODSourcePolicy(args)
        self.hydrology_strictness_policy = HydrologyScientificStrictnessPolicy(args)
        self.boundary_lod_policy = BoundaryLODSourcePolicy(args)
        self.ocean_conditions = OceanConditionProvider(args)
        self.ocean_material_policy = OceanMaterialPolicy(args)
        self.hover_boundary_hit = build_empty_boundary_hit()
        self.boundary_hover_dirty = False
        self.boundary_base_dirty = False
        self.boundary_hover_phase_bucket = -1
        self.boundary_dirty = True
        self.boundary_view_key = None
        self.hydrology_dirty = True
        self.hydrology_view_key = None
        self.datashader_sampling_policy = DatashaderSamplingPolicy()
        self.point_overlay_budget_policy = PointOverlayBudgetPolicy()
        self.point_overlay_budget_last = {
            "ais": self.point_overlay_budget_policy.decision(
                "ais",
                0,
                self.width,
                self.height,
                self.last_render_ms,
                self.basemap_lod,
                getattr(self.args, "target_fps", 30.0),
                self.interaction_active,
            ),
            "aircraft": self.point_overlay_budget_policy.decision(
                "aircraft",
                0,
                self.width,
                self.height,
                self.last_render_ms,
                self.basemap_lod,
                getattr(self.args, "target_fps", 30.0),
                self.interaction_active,
            ),
        }
        self.layer_order = [
            "scale",
            "ais",
            "aircraft",
            "pins",
            "vehicle_icons",
            "clouds",
            "borders",
            "territorial_sea",
            "eez",
            "high_seas",
            "rivers",
            "lakes",
            "ice",
            "forest",
            "contours",
            "globe",
        ]
        self.layer_visible = {
            "globe": True,
            "lakes": bool(getattr(args, "lake_layer", True)),
            "rivers": bool(getattr(args, "river_layer", True)),
            "borders": bool(getattr(args, "border_layer", True)),
            "territorial_sea": bool(getattr(args, "territorial_sea_layer", False)),
            "eez": bool(getattr(args, "eez_layer", False)),
            "high_seas": bool(getattr(args, "high_seas_layer", False)),
            "ais": True,
            "aircraft": bool(getattr(args, "aircraft_layer", False)),
            "pins": bool(getattr(args, "pin_layer", True)),
            "vehicle_icons": bool(getattr(args, "vehicle_icons", False)),
            "clouds": bool(getattr(args, "cloud_layer", False)),
            "ice": bool(getattr(args, "ice_layer", True)),
            "forest": bool(getattr(args, "forest_layer", True)),
            "contours": bool(getattr(args, "terrain_contours", False)),
            "scale": bool(getattr(args, "scale_bar", True)),
        }
        self.hydrology_overlays = self._load_hydrology_overlays()
        self.boundary_overlays = self._load_boundary_overlays()
        self.lake_overlay_rgba = np.zeros_like(self.globe_rgba)
        self.river_overlay_rgba = np.zeros_like(self.globe_rgba)
        self.boundary_overlay_rgba = np.zeros_like(self.globe_rgba)
        self.vector_overlay_cache: dict[tuple, object] = {}
        self.vector_overlay_cache_order: list[tuple] = []
        self.vector_overlay_cache_hits = 0
        self.vector_overlay_cache_misses = 0
        self.vector_overlay_cache_deferred = 0

    def rotate(self, dx: float, dy: float) -> None:
        self.yaw -= dx * 0.006 * self.zoom
        self.pitch += dy * 0.006 * self.zoom
        limit = math.pi / 2.0 - 0.01
        self.pitch = max(-limit, min(limit, self.pitch))
        self.globe_dirty = True
        self.overlay_dirty = True

    def apply_zoom(self, scale: float) -> None:
        self.zoom = max(0.08, min(self.zoom * scale, 4.0))
        self.globe_dirty = True
        self.overlay_dirty = True

    def current_km_per_pixel(self) -> float:
        return max(0.001, 6371.0 * float(self.zoom) * 2.0 / max(1.0, float(min(self.width, self.height))))

    def update_basemap_lod(self) -> bool:
        old_lod = self.basemap_lod
        self.basemap_lod = self.lod_manager.choose(self.current_km_per_pixel())
        changed = self.basemap_lod != old_lod
        if changed:
            self.hydrology_dirty = True
            self.boundary_dirty = True
            self.overlay_dirty = True
        return changed

    def basemap_lod_label(self) -> str:
        decision = self.lod_manager.decision(
            self.current_km_per_pixel(),
            projection=getattr(self.args, "map_projection", "globe"),
            topo_source=getattr(self.args, "topo_source", None),
            topo_step=getattr(self.args, "topo_step", None),
        )
        return f"LOD {decision['label']} | {decision['km_per_pixel']:.3g} km/px | {decision['projection']}"

    def basemap_provider_decision_text(self) -> str:
        decision = self.lod_manager.decision(
            self.current_km_per_pixel(),
            projection=getattr(self.args, "map_projection", "globe"),
            topo_source=getattr(self.args, "topo_source", None),
            topo_step=getattr(self.args, "topo_step", None),
        )
        lines = [
            "Basemap LOD decision",
            "",
            f"- lod: {decision['lod']}",
            f"- label: {decision['label']}",
            f"- km_per_pixel: {decision['km_per_pixel']:.6g}",
            f"- projection: {decision['projection']}",
            f"- provider: {decision['provider_id']}",
            f"- source: {decision['source_url']}",
            f"- cache: {decision['cache_path']}",
            f"- target adapter: {decision['target_adapter']}",
            f"- renderer input: {decision['renderer_input']}",
            f"- manifest: {decision['manifest']}",
        ]
        return "\n".join(lines)

    def hydrology_lod_label(self) -> str:
        profile = self.hydrology_render_profile.decision(self.basemap_lod, "rivers")
        return f"{self.lod_manager.label(self.basemap_lod)}: {profile['source_hint']}"

    def hydrology_render_profile_text(self) -> str:
        return self.hydrology_render_profile.text(self.basemap_lod)

    def hydrology_strictness_report_text(self) -> str:
        return self.hydrology_strictness_policy.text(self.basemap_lod, self.hydrology_lod_policy)

    def hydrology_strict_provider_ports_text(self) -> str:
        return hydrology_strict_provider_ports_text()

    def decoupling_extraction_audit(self) -> dict:
        hydrology_audit = {}
        for layer_id in HYDROLOGY_SPECS:
            provider = self.hydrology_lod_policy.decision(self.basemap_lod, layer_id)
            render_profile = self.hydrology_render_profile.decision(self.basemap_lod, layer_id)
            strictness = self.hydrology_strictness_policy.decision(self.basemap_lod, layer_id, provider)
            hydrology_audit[layer_id] = {
                "provider_id": provider["provider_id"],
                "source_mode": provider["source_mode"],
                "has_manifest": bool(provider.get("manifest")),
                "render_decimate": render_profile["decimate"],
                "strictness_tier": strictness["tier"],
                "metadata_complete": strictness.get("metadata_complete", False),
            }
        ocean_decision = self.ocean_conditions.decision(self.basemap_lod)
        provider_bundle = self.collect_provider_manifest_bundle()
        return {
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": "contract-ready-not-physically-split",
            "gates": DECOUPLING_EXTRACTION_GATES,
            "evidence": {
                "provider_manifest_bundle": {
                    "manifest_count": provider_bundle.get("manifest_count", 0),
                    "cache_root": provider_bundle.get("cache_root", ""),
                },
                "hydrology": hydrology_audit,
                "ocean": {
                    "provider_id": ocean_decision["provider_id"],
                    "source_kind": ocean_decision["source_kind"],
                    "spatial_mode": ocean_decision.get("spatial_mode", ""),
                    "sample_mode": ocean_decision.get("spatial_sampling", {}).get("sample_mode", ""),
                    "has_render_port_contract": bool(ocean_decision.get("render_port_contract")),
                    "has_normalization_report": bool(getattr(self.ocean_conditions, "last_normalization_report", {})),
                },
                "render_core": {
                    "topography_shape": list(getattr(self.topo, "shape", [])),
                    "land_mask_shape": list(getattr(self.land_mask, "shape", [])),
                    "frame_shape": list(getattr(self.frame_rgba, "shape", [])),
                    "globe_mask_shape": list(getattr(self.globe_mask, "shape", [])),
                    "style_profile": getattr(self.args, "style_profile", "scientific"),
                },
                "qt_ui": {
                    "data_fetch_events": len(DATA_FETCH_EVENTS),
                    "layer_count": len(getattr(self, "layer_order", [])),
                    "mode": getattr(self.args, "data_mode", "realtime"),
                },
            },
            "next_safe_step": "Extract contracts/provider_manifests.py first; do not move Qt or Taichi render core until one runtime pass confirms these contracts.",
        }

    def decoupling_extraction_audit_text(self) -> str:
        return json.dumps(self.decoupling_extraction_audit(), ensure_ascii=False, indent=2, default=str)

    def runtime_configuration_contract_text(self) -> str:
        return runtime_configuration_contract_text(self.args)

    def project_goal_milestones_text(self) -> str:
        return project_goal_milestones_text()

    def decoupling_extraction_units_text(self) -> str:
        return decoupling_extraction_units_text()

    def provider_manifests_module_api_text(self) -> str:
        return provider_manifests_module_api_text()

    def hydrology_provider_module_api_text(self) -> str:
        return hydrology_provider_module_api_text()

    def hydrology_provider_extraction_readiness_packet_text(self) -> str:
        return hydrology_provider_extraction_readiness_packet_text()

    def ocean_condition_provider_module_api_text(self) -> str:
        return ocean_condition_provider_module_api_text()

    def ocean_condition_provider_extraction_readiness_packet_text(self) -> str:
        return ocean_condition_provider_extraction_readiness_packet_text()

    def render_core_ocean_material_module_api_text(self) -> str:
        return render_core_ocean_material_module_api_text()

    def render_core_ocean_material_extraction_readiness_packet_text(self) -> str:
        return render_core_ocean_material_extraction_readiness_packet_text()

    def vector_lines_module_api_text(self) -> str:
        return vector_lines_module_api_text()

    def vector_lines_extraction_readiness_packet_text(self) -> str:
        return vector_lines_extraction_readiness_packet_text()

    def lod_pipeline_module_api_text(self) -> str:
        return lod_pipeline_module_api_text()

    def lod_pipeline_extraction_readiness_packet_text(self) -> str:
        return lod_pipeline_extraction_readiness_packet_text()

    def style_profiles_module_api_text(self) -> str:
        return style_profiles_module_api_text()

    def style_profiles_extraction_readiness_packet_text(self) -> str:
        return style_profiles_extraction_readiness_packet_text()

    def datashader_points_module_api_text(self) -> str:
        return datashader_points_module_api_text()

    def datashader_points_extraction_readiness_packet_text(self) -> str:
        return datashader_points_extraction_readiness_packet_text()

    def module_api_registry_text(self) -> str:
        return module_api_registry_text()

    def pre_extraction_readiness_audit_text(self) -> str:
        return pre_extraction_readiness_audit_text()

    def first_extraction_execution_plan_text(self) -> str:
        return first_extraction_execution_plan_text()

    def first_extraction_readiness_packet_text(self) -> str:
        return first_extraction_readiness_packet_text()

    def extraction_readiness_packet_index_text(self) -> str:
        return extraction_readiness_packet_index_text()

    def active_goal_extraction_seam_matrix_text(self) -> str:
        return active_goal_extraction_seam_matrix_text()

    def module_import_boundary_matrix_text(self) -> str:
        return module_import_boundary_matrix_text()

    def module_contract_coverage_text(self) -> str:
        return module_contract_coverage_text()

    def validation_and_rollback_plan_text(self) -> str:
        return validation_and_rollback_plan_text()

    def pre_validation_evidence_plan_text(self) -> str:
        return pre_validation_evidence_plan_text()

    def unverified_risk_register_text(self) -> str:
        return unverified_risk_register_text()

    def active_goal_control_bundle_snapshot(self) -> dict:
        return {
            "contract": "Single snapshot for the active goal: hydrology basic layer, LOD hook, Taichi ocean material controls, and decoupling readiness.",
            "runtime_verification": "not-run",
            "physical_split": "not-started",
            "readiness_gate": self.active_goal_readiness_gate_snapshot(),
            "hydrology_basic": self.hydrology_control_snapshot(),
            "hydrology_basic_readiness": self.hydrology_basic_readiness_matrix_snapshot(),
            "hydrology_dirty_reload_contract": self.hydrology_dirty_reload_contract_snapshot(),
            "lod_hook": self.lod_hook_pipeline_snapshot(),
            "lod_invalidation_contract": self.lod_invalidation_contract_snapshot(),
            "lod_layer_decision_matrix": self.lod_layer_decision_matrix_snapshot(),
            "taichi_ocean_material": self.ocean_material_control_snapshot(),
            "taichi_ocean_material_port": self.ocean_material_taichi_port_snapshot(),
            "ocean_condition_material_binding": self.ocean_condition_material_binding_snapshot(),
            "style_renderer_entry_matrix": style_renderer_entry_matrix_snapshot(getattr(self.args, "style_profile", "scientific")),
            "decoupling_preparation": {
                "module_api_registry": module_api_registry_snapshot(),
                "pre_extraction_readiness_audit": pre_extraction_readiness_audit_snapshot(),
                "first_extraction_execution_plan": first_extraction_execution_plan_snapshot(),
                "first_extraction_readiness_packet": first_extraction_readiness_packet_snapshot(),
                "extraction_readiness_packet_index": extraction_readiness_packet_index_snapshot(),
                "active_goal_extraction_seam_matrix": active_goal_extraction_seam_matrix_snapshot(),
                "cache_governance_matrix": cache_governance_matrix_snapshot(),
                "module_import_boundary_matrix": module_import_boundary_matrix_snapshot(),
                "module_contract_coverage": module_contract_coverage_snapshot(),
                "qt_controller_facade_api": qt_controller_facade_api_snapshot(),
                "qt_controller_facade_coverage": qt_controller_facade_coverage_snapshot(self),
                "qt_controller_facade_extraction_readiness_packet": qt_controller_facade_extraction_readiness_packet_snapshot(),
                "qt_ui_coupling_cleanup_status": qt_ui_coupling_cleanup_status_snapshot(),
                "qt_main_window_extraction_readiness_packet": qt_main_window_extraction_readiness_packet_snapshot(),
                "validation_and_rollback_plan": validation_and_rollback_plan_snapshot(),
                "pre_validation_evidence_plan": pre_validation_evidence_plan_snapshot(),
                "hydrology_provider_extraction_readiness_packet": hydrology_provider_extraction_readiness_packet_snapshot(),
                "ocean_condition_provider_extraction_readiness_packet": ocean_condition_provider_extraction_readiness_packet_snapshot(),
                "render_core_ocean_material_extraction_readiness_packet": render_core_ocean_material_extraction_readiness_packet_snapshot(),
                "vector_lines_extraction_readiness_packet": vector_lines_extraction_readiness_packet_snapshot(),
                "lod_pipeline_extraction_readiness_packet": lod_pipeline_extraction_readiness_packet_snapshot(),
                "style_profiles_extraction_readiness_packet": style_profiles_extraction_readiness_packet_snapshot(),
                "datashader_points_extraction_readiness_packet": datashader_points_extraction_readiness_packet_snapshot(),
                "unverified_risk_register": unverified_risk_register_snapshot(),
                "active_goal_known_issue_matrix": active_goal_known_issue_matrix_snapshot(),
                "active_goal_next_action_queue": active_goal_next_action_queue_snapshot(),
            },
        }

    def active_goal_control_bundle_text(self) -> str:
        return json.dumps(self.active_goal_control_bundle_snapshot(), ensure_ascii=False, indent=2, default=str)

    def active_goal_readiness_gate_snapshot(self) -> dict:
        hydrology = self.hydrology_basic_readiness_matrix_snapshot()
        hydrology_dirty_reload = self.hydrology_dirty_reload_contract_snapshot()
        lod_matrix = self.lod_layer_decision_matrix_snapshot()
        lod_invalidation = self.lod_invalidation_contract_snapshot()
        ocean_port = self.ocean_material_taichi_port_snapshot()
        ocean_binding = self.ocean_condition_material_binding_snapshot()
        module_contract = module_contract_coverage_snapshot()
        facade_coverage = qt_controller_facade_coverage_snapshot(self)
        extraction_index = extraction_readiness_packet_index_snapshot()
        seam_matrix = active_goal_extraction_seam_matrix_snapshot()
        cache_governance = cache_governance_matrix_snapshot()
        style_entries = style_renderer_entry_matrix_snapshot(getattr(self.args, "style_profile", "scientific"))
        required_hydrology_layers = len(HYDROLOGY_SPECS)
        expected_lod_layers = len(HYDROLOGY_SPECS) + len(BOUNDARY_SPECS) + 1
        expected_ocean_inputs = len(RENDER_CORE_OCEAN_MATERIAL_MODULE_API["taichi_kernel_inputs"])
        checks = [
            {
                "id": "hydrology_basic_contract",
                "scope": "hydrology basic",
                "passed": hydrology.get("contract_ready_count", 0) == required_hydrology_layers,
                "evidence": f"{hydrology.get('contract_ready_count', 0)}/{required_hydrology_layers} layers contract-ready",
                "requires_runtime": False,
            },
            {
                "id": "hydrology_vectors_loaded",
                "scope": "hydrology basic",
                "passed": hydrology.get("loaded_count", 0) == required_hydrology_layers,
                "evidence": f"{hydrology.get('loaded_count', 0)}/{required_hydrology_layers} layers have loaded vectors",
                "requires_runtime": True,
            },
            {
                "id": "hydrology_dirty_reload_contract",
                "scope": "hydrology basic",
                "passed": bool(hydrology_dirty_reload.get("ready", False)),
                "evidence": f"{hydrology_dirty_reload.get('trigger_count', 0)} triggers; {len(hydrology_dirty_reload.get('missing_contracts', []))} missing contracts",
                "requires_runtime": False,
            },
            {
                "id": "lod_layer_matrix_shape",
                "scope": "LOD hook",
                "passed": lod_matrix.get("layer_count", 0) == expected_lod_layers,
                "evidence": f"{lod_matrix.get('layer_count', 0)}/{expected_lod_layers} LOD matrix entries",
                "requires_runtime": False,
            },
            {
                "id": "lod_invalidation_contract",
                "scope": "LOD hook",
                "passed": bool(lod_invalidation.get("ready", False)),
                "evidence": f"{lod_invalidation.get('trigger_count', 0)} triggers; {len(lod_invalidation.get('missing_contracts', []))} missing contracts",
                "requires_runtime": False,
            },
            {
                "id": "ocean_taichi_port_shape",
                "scope": "Taichi ocean material",
                "passed": len(ocean_port.get("kernel_inputs", {})) == expected_ocean_inputs,
                "evidence": f"{len(ocean_port.get('kernel_inputs', {}))}/{expected_ocean_inputs} kernel inputs declared",
                "requires_runtime": False,
            },
            {
                "id": "ocean_condition_material_binding",
                "scope": "Taichi ocean material",
                "passed": bool(ocean_binding.get("ready", False)),
                "evidence": f"{ocean_binding.get('binding_count', 0)} bindings; {len(ocean_binding.get('missing_uniforms', []))} missing uniforms; {len(ocean_binding.get('missing_kernel_inputs', []))} missing kernel inputs",
                "requires_runtime": False,
            },
            {
                "id": "style_renderer_entries_ready",
                "scope": "style profile renderer entry",
                "passed": bool(style_entries.get("ready", False)),
                "evidence": f"{style_entries.get('entry_count', 0)} entries; {len(style_entries.get('missing_required_fields', {}))} profiles missing required fields",
                "requires_runtime": False,
            },
            {
                "id": "module_contract_coverage",
                "scope": "decoupling preparation",
                "passed": not module_contract.get("needs_review", []),
                "evidence": f"{len(module_contract.get('needs_review', []))} module contract items need review",
                "requires_runtime": False,
            },
            {
                "id": "qt_facade_coverage",
                "scope": "decoupling preparation",
                "passed": bool(facade_coverage.get("ok", False)),
                "evidence": f"{len(facade_coverage.get('missing', []))} facade methods missing",
                "requires_runtime": False,
            },
            {
                "id": "extraction_packet_index_complete",
                "scope": "decoupling preparation",
                "passed": not extraction_index.get("remaining_packet_candidates", []),
                "evidence": f"{extraction_index.get('packet_count', 0)} packets prepared; {len(extraction_index.get('remaining_packet_candidates', []))} remaining candidates",
                "requires_runtime": False,
            },
            {
                "id": "active_goal_extraction_seams_ready",
                "scope": "decoupling preparation",
                "passed": bool(seam_matrix.get("ready", False)),
                "evidence": f"{seam_matrix.get('seam_count', 0)} seams; {len(seam_matrix.get('missing_packet_ids', []))} missing packet ids",
                "requires_runtime": False,
            },
            {
                "id": "cache_governance_contract_ready",
                "scope": "decoupling preparation",
                "passed": bool(cache_governance.get("ready", False)),
                "evidence": f"{cache_governance.get('item_count', 0)} cache items; {len(cache_governance.get('missing_contract', []))} missing contracts; destructive cleanup {cache_governance.get('destructive_cleanup', 'unknown')}",
                "requires_runtime": False,
            },
            {
                "id": "runtime_validation",
                "scope": "completion gate",
                "passed": False,
                "evidence": "runtime/syntax validation intentionally not run in this automation",
                "requires_runtime": True,
            },
        ]
        contract_blockers = [
            check["id"] for check in checks
            if not check["passed"] and not check["requires_runtime"]
        ]
        runtime_blockers = [
            check["id"] for check in checks
            if not check["passed"] and check["requires_runtime"]
        ]
        status = "contract-ready-unverified" if not contract_blockers else "contract-needs-review"
        return {
            "contract": "Active goal readiness gate aggregates hydrology basic, LOD hook, Taichi ocean material, and decoupling readiness without claiming runtime completion.",
            "status": status,
            "runtime_verification": "not-run",
            "contract_blockers": contract_blockers,
            "runtime_blockers": runtime_blockers,
            "hydrology_dirty_reload_contract": {
                "ready": bool(hydrology_dirty_reload.get("ready", False)),
                "trigger_count": hydrology_dirty_reload.get("trigger_count", 0),
                "missing_contracts": list(hydrology_dirty_reload.get("missing_contracts", [])),
            },
            "extraction_packet_index": {
                "packet_count": extraction_index.get("packet_count", 0),
                "remaining_packet_candidates": list(extraction_index.get("remaining_packet_candidates", [])),
            },
            "active_goal_extraction_seam_matrix": {
                "ready": bool(seam_matrix.get("ready", False)),
                "seam_count": seam_matrix.get("seam_count", 0),
                "missing_packet_ids": list(seam_matrix.get("missing_packet_ids", [])),
            },
            "lod_invalidation_contract": {
                "ready": bool(lod_invalidation.get("ready", False)),
                "trigger_count": lod_invalidation.get("trigger_count", 0),
                "missing_contracts": list(lod_invalidation.get("missing_contracts", [])),
            },
            "cache_governance_matrix": {
                "ready": bool(cache_governance.get("ready", False)),
                "item_count": cache_governance.get("item_count", 0),
                "memory_cache_count": cache_governance.get("memory_cache_count", 0),
                "disk_cache_count": cache_governance.get("disk_cache_count", 0),
                "manual_only_disk_cache_ids": list(cache_governance.get("manual_only_disk_cache_ids", [])),
            },
            "style_renderer_entry_matrix": {
                "ready": bool(style_entries.get("ready", False)),
                "entry_count": style_entries.get("entry_count", 0),
                "target_entries": list(style_entries.get("target_entries", [])),
                "missing_required_fields": dict(style_entries.get("missing_required_fields", {})),
            },
            "ocean_condition_material_binding": {
                "ready": bool(ocean_binding.get("ready", False)),
                "binding_count": ocean_binding.get("binding_count", 0),
                "missing_uniforms": list(ocean_binding.get("missing_uniforms", [])),
                "missing_kernel_inputs": list(ocean_binding.get("missing_kernel_inputs", [])),
                "policy_only_uniforms": list(ocean_binding.get("policy_only_uniforms", [])),
            },
            "checks": checks,
            "next_required_evidence": [
                "python -m py_compile taichi_global_bathymetry.py",
                "open Qt toolbar diagnostics for Hydrology basic readiness, LOD layer decision matrix, and Ocean Taichi material port",
                "render one small globe frame with hydrology, boundary, Datashader, and ocean material toggles",
            ],
        }

    def active_goal_readiness_gate_text(self) -> str:
        return json.dumps(self.active_goal_readiness_gate_snapshot(), ensure_ascii=False, indent=2, default=str)

    def active_goal_summary_snapshot(self) -> dict:
        hydrology_layers = {}
        for layer_id in HYDROLOGY_SPECS:
            overlay = self.hydrology_overlays.get(layer_id)
            decision = self.hydrology_lod_policy.decision(self.basemap_lod, layer_id)
            hydrology_layers[layer_id] = {
                "visible": bool(self.layer_visible.get(layer_id, True)),
                "line_count": int(len(getattr(overlay, "lines", []))) if overlay else 0,
                "provider": decision.get("provider_id", ""),
                "status": decision.get("status", ""),
            }
        ocean_decision = self.ocean_conditions.decision(self.basemap_lod)
        ocean_taichi_port = self.ocean_material_taichi_port_snapshot()
        ocean_binding = self.ocean_condition_material_binding_snapshot()
        lod_invalidation = self.lod_invalidation_contract_snapshot()
        hydrology_readiness = self.hydrology_basic_readiness_matrix_snapshot()
        hydrology_dirty_reload = self.hydrology_dirty_reload_contract_snapshot()
        readiness_gate = self.active_goal_readiness_gate_snapshot()
        contract_coverage = module_contract_coverage_snapshot()
        facade_coverage = qt_controller_facade_coverage_snapshot(self)
        facade_api = qt_controller_facade_api_snapshot()
        extraction_index = extraction_readiness_packet_index_snapshot()
        seam_matrix = active_goal_extraction_seam_matrix_snapshot()
        cache_governance = cache_governance_matrix_snapshot()
        known_issues = active_goal_known_issue_matrix_snapshot()
        style_entries = style_renderer_entry_matrix_snapshot(getattr(self.args, "style_profile", "scientific"))
        return {
            "runtime_verification": "not-run",
            "physical_split": "not-started",
            "active_goal_gate_status": readiness_gate.get("status", ""),
            "active_goal_contract_blocker_count": len(readiness_gate.get("contract_blockers", [])),
            "active_goal_runtime_blocker_count": len(readiness_gate.get("runtime_blockers", [])),
            "pre_validation_evidence_gate_count": len(PRE_VALIDATION_EVIDENCE_PLAN),
            "extraction_packet_count": extraction_index["packet_count"],
            "extraction_packet_move_symbol_count": extraction_index["total_move_symbol_count"],
            "extraction_packet_remaining_count": len(extraction_index.get("remaining_packet_candidates", [])),
            "active_goal_extraction_seam_ready": bool(seam_matrix.get("ready", False)),
            "active_goal_extraction_seam_count": seam_matrix.get("seam_count", 0),
            "active_goal_extraction_seam_missing_count": len(seam_matrix.get("missing_packet_ids", [])),
            "cache_governance_ready": bool(cache_governance.get("ready", False)),
            "cache_governance_item_count": cache_governance.get("item_count", 0),
            "cache_governance_memory_count": cache_governance.get("memory_cache_count", 0),
            "cache_governance_disk_count": cache_governance.get("disk_cache_count", 0),
            "cache_governance_manual_disk_count": len(cache_governance.get("manual_only_disk_cache_ids", [])),
            "active_goal_known_issue_count": known_issues.get("issue_count", 0),
            "active_goal_known_issue_open_count": known_issues.get("open_count", 0),
            "active_goal_known_issue_runtime_count": known_issues.get("requires_runtime_count", 0),
            "active_goal_known_issue_user_decision_count": known_issues.get("requires_user_decision_count", 0),
            "first_extraction_move_symbol_count": len(FIRST_EXTRACTION_READINESS_PACKET["move_symbols"]),
            "hydrology_provider_move_symbol_count": len(HYDROLOGY_PROVIDER_EXTRACTION_READINESS_PACKET["move_symbols"]),
            "ocean_condition_provider_move_symbol_count": len(OCEAN_CONDITION_PROVIDER_EXTRACTION_READINESS_PACKET["move_symbols"]),
            "render_core_ocean_material_move_symbol_count": len(RENDER_CORE_OCEAN_MATERIAL_EXTRACTION_READINESS_PACKET["move_symbols"]),
            "vector_lines_move_symbol_count": len(VECTOR_LINES_EXTRACTION_READINESS_PACKET["move_symbols"]),
            "lod_pipeline_move_symbol_count": len(LOD_PIPELINE_EXTRACTION_READINESS_PACKET["move_symbols"]),
            "style_profiles_move_symbol_count": len(STYLE_PROFILES_EXTRACTION_READINESS_PACKET["move_symbols"]),
            "datashader_points_move_symbol_count": len(DATASHADER_POINTS_EXTRACTION_READINESS_PACKET["move_symbols"]),
            "qt_controller_facade_move_symbol_count": len(QT_CONTROLLER_FACADE_EXTRACTION_READINESS_PACKET["move_symbols"]),
            "qt_main_window_move_symbol_count": len(QT_MAIN_WINDOW_EXTRACTION_READINESS_PACKET["move_symbols"]),
            "basemap_lod": self.basemap_lod,
            "lod_matrix_layer_count": len(HYDROLOGY_SPECS) + len(BOUNDARY_SPECS) + 1,
            "lod_invalidation_ready": bool(lod_invalidation.get("ready", False)),
            "lod_invalidation_trigger_count": lod_invalidation.get("trigger_count", 0),
            "lod_invalidation_missing_count": len(lod_invalidation.get("missing_contracts", [])),
            "hydrology_source_mode": getattr(self.args, "hydrology_source_mode", "lod"),
            "hydrology_basic_contract_ready_count": hydrology_readiness.get("contract_ready_count", 0),
            "hydrology_basic_loaded_count": hydrology_readiness.get("loaded_count", 0),
            "hydrology_dirty_reload_ready": bool(hydrology_dirty_reload.get("ready", False)),
            "hydrology_dirty_reload_trigger_count": hydrology_dirty_reload.get("trigger_count", 0),
            "hydrology_dirty_reload_missing_count": len(hydrology_dirty_reload.get("missing_contracts", [])),
            "hydrology_layers": hydrology_layers,
            "ocean_source": ocean_decision.get("source", ""),
            "ocean_sample_mode": ocean_decision.get("spatial_sampling", {}).get("sample_mode", ""),
            "ocean_taichi_kernel_input_count": len(ocean_taichi_port.get("kernel_inputs", {})),
            "ocean_unwired_policy_scalars": list(ocean_taichi_port.get("unwired_policy_scalars", [])),
            "ocean_material_binding_ready": bool(ocean_binding.get("ready", False)),
            "ocean_material_binding_count": ocean_binding.get("binding_count", 0),
            "ocean_material_binding_missing_uniform_count": len(ocean_binding.get("missing_uniforms", [])),
            "ocean_material_binding_missing_kernel_count": len(ocean_binding.get("missing_kernel_inputs", [])),
            "ocean_material_policy_only_uniforms": list(ocean_binding.get("policy_only_uniforms", [])),
            "style_profile": getattr(self.args, "style_profile", "scientific"),
            "style_renderer_entry_ready": bool(style_entries.get("ready", False)),
            "style_renderer_entry_count": style_entries.get("entry_count", 0),
            "style_renderer_target_entries": list(style_entries.get("target_entries", [])),
            "style_renderer_missing_required_count": len(style_entries.get("missing_required_fields", {})),
            "module_api_count": len(module_api_registry_snapshot()),
            "unverified_risk_count": len(UNVERIFIED_RISK_REGISTER),
            "module_contract_needs_review_count": len(contract_coverage.get("needs_review", [])),
            "module_contract_needs_review": list(contract_coverage.get("needs_review", []))[:8],
            "qt_facade_ok": bool(facade_coverage.get("ok", False)),
            "qt_facade_write_method_count": len(facade_api.get("write_methods", [])),
            "qt_facade_missing_count": len(facade_coverage.get("missing", [])),
            "qt_facade_missing": list(facade_coverage.get("missing", []))[:8],
            "qt_coupling_cleanup_status": QT_UI_COUPLING_CLEANUP_STATUS.get("status", ""),
            "first_extract_candidate": "contracts/provider_manifests.py",
        }

    def active_goal_summary_text(self) -> str:
        summary = self.active_goal_summary_snapshot()
        lines = [
            "Active goal summary",
            "",
            f"- runtime verification: {summary['runtime_verification']}",
            f"- physical split: {summary['physical_split']}",
            f"- active goal gate: {summary['active_goal_gate_status']}",
            f"- active goal blockers: contract={summary['active_goal_contract_blocker_count']}, runtime={summary['active_goal_runtime_blocker_count']}",
            f"- pre-validation evidence gates: {summary['pre_validation_evidence_gate_count']}",
            f"- extraction packets: {summary['extraction_packet_count']} ({summary['extraction_packet_move_symbol_count']} move symbols)",
            f"- extraction packet remaining candidates: {summary['extraction_packet_remaining_count']}",
            f"- active extraction seams: ready={summary['active_goal_extraction_seam_ready']}; count={summary['active_goal_extraction_seam_count']}; missing={summary['active_goal_extraction_seam_missing_count']}",
            f"- cache governance: ready={summary['cache_governance_ready']}; items={summary['cache_governance_item_count']}; memory={summary['cache_governance_memory_count']}; disk={summary['cache_governance_disk_count']}; manual_disk={summary['cache_governance_manual_disk_count']}",
            f"- known issues: open={summary['active_goal_known_issue_open_count']}; runtime={summary['active_goal_known_issue_runtime_count']}; user_decision={summary['active_goal_known_issue_user_decision_count']}",
            f"- first extraction move symbols: {summary['first_extraction_move_symbol_count']}",
            f"- hydrology provider move symbols: {summary['hydrology_provider_move_symbol_count']}",
            f"- ocean condition provider move symbols: {summary['ocean_condition_provider_move_symbol_count']}",
            f"- render-core ocean material move symbols: {summary['render_core_ocean_material_move_symbol_count']}",
            f"- vector lines move symbols: {summary['vector_lines_move_symbol_count']}",
            f"- LOD pipeline move symbols: {summary['lod_pipeline_move_symbol_count']}",
            f"- style profiles move symbols: {summary['style_profiles_move_symbol_count']}",
            f"- Datashader points move symbols: {summary['datashader_points_move_symbol_count']}",
            f"- Qt controller facade move symbols: {summary['qt_controller_facade_move_symbol_count']}",
            f"- Qt main window move symbols: {summary['qt_main_window_move_symbol_count']}",
            f"- basemap LOD: {summary['basemap_lod']}",
            f"- LOD matrix layer count: {summary['lod_matrix_layer_count']}",
            f"- LOD invalidation: ready={summary['lod_invalidation_ready']}; triggers={summary['lod_invalidation_trigger_count']}; missing={summary['lod_invalidation_missing_count']}",
            f"- hydrology source mode: {summary['hydrology_source_mode']}",
            f"- hydrology basic contract-ready: {summary['hydrology_basic_contract_ready_count']}",
            f"- hydrology basic loaded: {summary['hydrology_basic_loaded_count']}",
            f"- hydrology dirty/reload: ready={summary['hydrology_dirty_reload_ready']}; triggers={summary['hydrology_dirty_reload_trigger_count']}; missing={summary['hydrology_dirty_reload_missing_count']}",
            f"- ocean source: {summary['ocean_source']} ({summary['ocean_sample_mode']})",
            f"- ocean Taichi kernel inputs: {summary['ocean_taichi_kernel_input_count']}",
            f"- ocean unwired policy scalars: {', '.join(summary['ocean_unwired_policy_scalars']) or 'none'}",
            f"- ocean material binding: ready={summary['ocean_material_binding_ready']}; bindings={summary['ocean_material_binding_count']}; missing_uniforms={summary['ocean_material_binding_missing_uniform_count']}; missing_kernel={summary['ocean_material_binding_missing_kernel_count']}",
            f"- ocean policy-only uniforms: {', '.join(summary['ocean_material_policy_only_uniforms']) or 'none'}",
            f"- style profile: {summary['style_profile']}",
            f"- style renderer entries: ready={summary['style_renderer_entry_ready']}; count={summary['style_renderer_entry_count']}; missing={summary['style_renderer_missing_required_count']}; targets={', '.join(summary['style_renderer_target_entries'])}",
            f"- module API count: {summary['module_api_count']}",
            f"- unverified risks: {summary['unverified_risk_count']}",
            f"- module contract needs review: {summary['module_contract_needs_review_count']}",
            f"- Qt facade ok: {summary['qt_facade_ok']} (missing={summary['qt_facade_missing_count']})",
            f"- Qt facade write methods: {summary['qt_facade_write_method_count']}",
            f"- Qt coupling cleanup: {summary['qt_coupling_cleanup_status']}",
            f"- first extract candidate: {summary['first_extract_candidate']}",
            "",
            "Needs review:",
        ]
        if summary["module_contract_needs_review"]:
            for item in summary["module_contract_needs_review"]:
                lines.append(f"- module contract: {item}")
        else:
            lines.append("- module contract: none listed")
        if summary["qt_facade_missing"]:
            for item in summary["qt_facade_missing"]:
                lines.append(f"- Qt facade: {item}")
        else:
            lines.append("- Qt facade: none listed")
        lines.extend([
            "",
            "Hydrology layers:",
        ])
        for layer_id, layer in summary["hydrology_layers"].items():
            lines.append(
                f"- {layer_id}: visible={layer['visible']}; lines={layer['line_count']}; "
                f"provider={layer['provider']}; {layer['status']}"
            )
        return "\n".join(lines)

    def active_goal_next_action_queue_text(self) -> str:
        return active_goal_next_action_queue_text()

    def active_goal_known_issue_matrix_text(self) -> str:
        return active_goal_known_issue_matrix_text()

    def qt_controller_facade_api_text(self) -> str:
        return qt_controller_facade_api_text()

    def qt_controller_facade_coverage_text(self) -> str:
        return qt_controller_facade_coverage_text(self)

    def qt_controller_facade_extraction_readiness_packet_text(self) -> str:
        return qt_controller_facade_extraction_readiness_packet_text()

    def qt_main_window_module_api_text(self) -> str:
        return qt_main_window_module_api_text()

    def qt_main_window_extraction_readiness_packet_text(self) -> str:
        return qt_main_window_extraction_readiness_packet_text()

    def qt_ui_coupling_cleanup_status_text(self) -> str:
        return qt_ui_coupling_cleanup_status_text()

    def reset_view(self) -> None:
        self.yaw = 0.0
        self.pitch = 0.0
        self.zoom = 1.0
        self.globe_dirty = True
        self.overlay_dirty = True

    def toggle_longitude_flip(self) -> None:
        self.flip_longitude = not self.flip_longitude
        self.globe_dirty = True
        self.overlay_dirty = True

    def toggle_latitude_flip(self) -> None:
        self.flip_latitude = not self.flip_latitude
        self.globe_dirty = True
        self.overlay_dirty = True

    def set_color_mode(self, color_by: str) -> None:
        if color_by not in {"speed", "density"}:
            return
        self.args.color_by = color_by
        self.overlay_renderer.color_by = color_by
        self.overlay_dirty = True

    def set_point_px(self, point_px: int) -> None:
        self.args.point_px = max(1, int(point_px))
        self.overlay_renderer.point_px = self.args.point_px
        self.overlay_dirty = True

    def set_refresh_seconds(self, refresh: float) -> None:
        self.args.refresh = max(0.1, float(refresh))

    def set_max_age_minutes(self, max_age: float) -> None:
        self.args.max_age_minutes = max(0.0, float(max_age))
        self.overlay_dirty = True

    def set_speed_span(self, speed_min: float, speed_max: float) -> None:
        speed_min = float(speed_min)
        speed_max = max(speed_min + 0.1, float(speed_max))
        self.args.speed_min = speed_min
        self.args.speed_max = speed_max
        self.overlay_renderer.speed_span = (speed_min, speed_max)
        self.overlay_dirty = True

    def set_horizon_eps(self, value: float) -> None:
        self.args.ais_horizon_eps = max(0.0, min(float(value), 0.25))
        self.overlay_dirty = True

    def _mark_render_dirty(self, globe: bool = False, overlay: bool = True) -> None:
        if globe:
            self.globe_dirty = True
        if overlay:
            self.overlay_dirty = True

    def set_interaction_active(self, active: bool) -> None:
        self.interaction_active = bool(active)

    def fly_camera(self, yaw_delta_deg: float, pitch_delta_deg: float = 0.0, zoom_scale: float = 1.0) -> None:
        self.yaw += math.radians(float(yaw_delta_deg))
        self.pitch += math.radians(float(pitch_delta_deg))
        limit = math.pi / 2.0 - 0.01
        self.pitch = max(-limit, min(limit, self.pitch))
        self.zoom = max(0.08, min(float(self.zoom) * float(zoom_scale), 4.0))
        self._mark_render_dirty(globe=True, overlay=True)

    def set_ais_sample_ratio(self, value: float) -> None:
        self.args.ais_sample_ratio = max(0.01, min(float(value), 1.0))
        self.overlay_dirty = True

    def set_aircraft_sample_ratio(self, value: float) -> None:
        self.args.aircraft_sample_ratio = max(0.01, min(float(value), 1.0))
        self.overlay_dirty = True

    def set_adaptive_sampling(self, enabled: bool) -> None:
        self.args.adaptive_sampling = bool(enabled)
        self.overlay_dirty = True

    def set_target_fps(self, value: float) -> None:
        self.args.target_fps = max(1.0, float(value))
        self.overlay_dirty = True

    def render_budget_decision(self) -> dict:
        return self.render_budget_policy.decision(
            self.width,
            self.height,
            self.last_render_ms,
            getattr(self, "basemap_lod", "global"),
            getattr(self.args, "target_fps", 30.0),
            bool(getattr(self, "interaction_active", False)),
            getattr(self, "layer_visible", {}),
        )

    def render_budget_text(self) -> str:
        policy_text = self.render_budget_policy.text(
            self.width,
            self.height,
            self.last_render_ms,
            getattr(self, "basemap_lod", "global"),
            getattr(self.args, "target_fps", 30.0),
            bool(getattr(self, "interaction_active", False)),
            getattr(self, "layer_visible", {}),
        )
        cache_lines = [
            "",
            "Vector overlay cache",
            "",
            f"- entries: {len(self.vector_overlay_cache)} / {self._vector_cache_limit()}",
            f"- hits: {self.vector_overlay_cache_hits:,}",
            f"- misses: {self.vector_overlay_cache_misses:,}",
            f"- deferred frames: {self.vector_overlay_cache_deferred:,}",
            "- cached layers: hydrology, borders, territorial sea, EEZ, high seas",
        ]
        return policy_text + "\n" + "\n".join(cache_lines)

    def point_overlay_budget_decision(self, layer: str, point_count: int | None = None) -> dict:
        if point_count is None:
            if layer == "ais":
                point_count = len(self.current_projected)
            else:
                point_count = len(self.current_aircraft_projected)
        decision = self.point_overlay_budget_policy.decision(
            layer,
            int(point_count),
            self.width,
            self.height,
            self.last_render_ms,
            getattr(self, "basemap_lod", "global"),
            getattr(self.args, "target_fps", 30.0),
            bool(getattr(self, "interaction_active", False)),
        )
        self.point_overlay_budget_last[layer] = decision
        return decision

    def point_overlay_budget_text(self) -> str:
        return self.point_overlay_budget_policy.text(self.point_overlay_budget_last)

    def set_min_sample_ratio(self, value: float) -> None:
        self.args.min_sample_ratio = max(0.001, min(float(value), 1.0))
        self.overlay_dirty = True

    def _effective_sample_fraction(self, frame: pd.DataFrame, layer: str) -> float:
        if frame.empty:
            return 1.0
        if layer == "ais":
            ratio = float(getattr(self.args, "ais_sample_ratio", 1.0))
        else:
            ratio = float(getattr(self.args, "aircraft_sample_ratio", 1.0))
        ratio = max(0.001, min(ratio, 1.0))
        point_budget = self.point_overlay_budget_decision(layer, len(frame))
        ratio = min(ratio, float(point_budget.get("sample_ratio_cap", 1.0)))
        if bool(getattr(self.args, "adaptive_sampling", True)):
            decision = self.datashader_sampling_policy.decision(
                len(frame),
                self.basemap_lod,
                ratio,
                getattr(self.args, "data_mode", "realtime") == "realtime",
            )
            ratio = float(decision["sample_fraction"])
        ratio = max(float(getattr(self.args, "min_sample_ratio", 0.05)), ratio)
        return max(0.001, min(ratio, 1.0))

    def _sample_projected_frame(self, frame: pd.DataFrame, layer: str) -> pd.DataFrame:
        fraction = self._effective_sample_fraction(frame, layer)
        if frame.empty or fraction >= 0.999:
            return frame
        return frame.sample(frac=fraction, random_state=(self.frame_index + (17 if layer == "ais" else 31))).copy()

    def set_vehicle_icons(self, enabled: bool) -> None:
        self.args.vehicle_icons = bool(enabled)
        self.layer_visible["vehicle_icons"] = bool(enabled)
        self.overlay_dirty = True

    def set_icon_max_count(self, value: int) -> None:
        self.args.icon_max_count = max(0, int(value))
        self.overlay_dirty = True

    def set_icon_pick_radius(self, value: float) -> None:
        self.args.icon_pick_radius = max(1.0, float(value))

    def set_aircraft_color_mode(self, color_by: str) -> None:
        if color_by not in {"altitude", "speed", "density"}:
            return
        self.args.aircraft_color_by = color_by
        self.aircraft_overlay_renderer.color_by = color_by
        self.overlay_dirty = True

    def set_aircraft_point_px(self, value: int) -> None:
        self.args.aircraft_point_px = max(1, int(value))
        self.aircraft_overlay_renderer.point_px = self.args.aircraft_point_px
        self.overlay_dirty = True

    def set_aircraft_max_age_minutes(self, value: float) -> None:
        self.args.aircraft_max_age_minutes = max(0.0, float(value))
        self.overlay_dirty = True

    def set_aircraft_altitude_exaggeration(self, value: float) -> None:
        self.args.aircraft_altitude_exaggeration = max(0.0, float(value))
        self.overlay_dirty = True

    def set_aircraft_horizon_eps(self, value: float) -> None:
        self.args.aircraft_horizon_eps = max(0.0, min(float(value), 0.25))
        self.overlay_dirty = True

    def set_sea_level_m(self, value: float) -> None:
        self.args.sea_level_m = float(value)
        self.globe_dirty = True
        self.hydrology_dirty = True
        self.overlay_dirty = True

    def set_terrain_contours(self, enabled: bool) -> None:
        self.args.terrain_contours = bool(enabled)
        self.layer_visible["contours"] = bool(enabled)
        self.globe_dirty = True

    def set_contour_interval(self, value: float) -> None:
        self.args.contour_interval_m = max(1.0, float(value))
        self.globe_dirty = True

    def set_contour_line_width(self, value: float) -> None:
        self.args.contour_line_width_m = max(0.1, float(value))
        self.globe_dirty = True

    def set_contour_opacity(self, value: float) -> None:
        self.args.contour_opacity = max(0.0, min(float(value), 1.0))
        self.globe_dirty = True

    def set_ocean_material(self, enabled: bool) -> None:
        self.args.ocean_material = bool(enabled)
        self.args.ocean_responsive = bool(enabled)
        self.globe_dirty = True

    def set_ocean_wave_strength(self, value: float) -> None:
        self.args.ocean_wave_strength = max(0.0, min(float(value), 1.0))
        self.globe_dirty = True

    def set_ocean_roughness(self, value: float) -> None:
        self.args.ocean_roughness = max(0.02, min(float(value), 1.0))
        self.globe_dirty = True

    def set_ocean_foam(self, value: float) -> None:
        self.args.ocean_foam = max(0.0, min(float(value), 1.0))
        self.globe_dirty = True

    def set_ocean_animation_fps(self, value: float) -> None:
        self.args.ocean_animation_fps = max(0.0, float(value))
        self.globe_dirty = True

    def set_ocean_condition_refresh(self, value: float) -> None:
        self.args.ocean_condition_refresh = max(0.0, float(value))

    def set_ocean_provider_lat(self, value: float) -> None:
        self.args.ocean_provider_lat = max(-90.0, min(90.0, float(value)))
        self.ocean_conditions.last_read = 0.0
        self.ocean_conditions.cached_conditions = {}
        self.globe_dirty = True

    def set_ocean_provider_lon(self, value: float) -> None:
        lon = ((float(value) + 180.0) % 360.0) - 180.0
        self.args.ocean_provider_lon = lon
        self.ocean_conditions.last_read = 0.0
        self.ocean_conditions.cached_conditions = {}
        self.globe_dirty = True

    def set_ocean_condition_source(self, value: str, file_path: str | None = None, url: str | None = None) -> None:
        source = str(value or "manual")
        if source not in OCEAN_PROVIDER_REGISTRY:
            source = "manual"
        self.args.ocean_condition_source = source
        meta = OCEAN_PROVIDER_REGISTRY.get(source, OCEAN_PROVIDER_REGISTRY["manual"])
        target_attr = meta.get("source_attr")
        if file_path is not None:
            if target_attr and target_attr.endswith("_file"):
                setattr(self.args, target_attr, str(file_path).strip() or None)
            else:
                self.args.ocean_condition_file = str(file_path).strip() or None
        if url is not None:
            if target_attr and target_attr.endswith("_url"):
                setattr(self.args, target_attr, str(url).strip() or None)
            else:
                self.args.ocean_condition_url = str(url).strip() or None
        self.ocean_conditions.last_read = 0.0
        self.ocean_conditions.cached_conditions = {}
        self.globe_dirty = True

    def set_ice_opacity(self, value: float) -> None:
        self.args.ice_opacity = max(0.0, min(float(value), 1.0))
        self.globe_dirty = True

    def set_ice_specular(self, value: float) -> None:
        self.args.ice_specular = max(0.0, min(float(value), 1.0))
        self.globe_dirty = True

    def set_ice_blue(self, value: float) -> None:
        self.args.ice_blue = max(0.0, min(float(value), 1.0))
        self.globe_dirty = True

    def set_cloud_opacity(self, value: float) -> None:
        self.args.cloud_opacity = max(0.0, min(float(value), 1.0))
        self.globe_dirty = True

    def set_cloud_coverage(self, value: float) -> None:
        self.args.cloud_coverage = max(0.0, min(float(value), 1.0))
        self.globe_dirty = True

    def set_cloud_detail(self, value: float) -> None:
        self.args.cloud_detail = max(0.0, min(float(value), 1.0))
        self.globe_dirty = True

    def set_cloud_animation_fps(self, value: float) -> None:
        self.args.cloud_animation_fps = max(0.0, float(value))
        self.globe_dirty = True

    def set_map_projection(self, projection: str) -> None:
        self.args.map_projection = str(projection or "globe")
        self.globe_dirty = True
        self.overlay_dirty = True
        self.hydrology_dirty = True
        self.boundary_dirty = True

    def set_style_profile(self, profile: str) -> None:
        self.args.style_profile = resolve_style_profile(profile)["id"]
        if hasattr(self, "overlay_renderer"):
            self.overlay_renderer.set_style_profile(self.args.style_profile)
        if hasattr(self, "aircraft_overlay_renderer"):
            self.aircraft_overlay_renderer.set_style_profile(self.args.style_profile)
        self.globe_dirty = True
        self.overlay_dirty = True

    def style_profile_status_text(self) -> str:
        return style_profile_registry_text(getattr(self.args, "style_profile", "scientific"))

    def style_renderer_entry_text(self) -> str:
        return style_renderer_entry_text(getattr(self.args, "style_profile", "scientific"))

    def style_renderer_entry_matrix_text(self) -> str:
        return style_renderer_entry_matrix_text(getattr(self.args, "style_profile", "scientific"))

    def style_overlay_intent_text(self) -> str:
        return style_overlay_intent_text(getattr(self.args, "style_profile", "scientific"))

    def _load_hydrology_overlays(self) -> dict[str, GeoVectorLineOverlay]:
        overlays: dict[str, GeoVectorLineOverlay] = {}
        for layer_id, spec in HYDROLOGY_SPECS.items():
            overlays[layer_id] = self._load_single_hydrology_overlay(layer_id)
        return overlays

    def _load_single_hydrology_overlay(self, layer_id: str) -> GeoVectorLineOverlay:
        spec = HYDROLOGY_SPECS[layer_id]
        prefix = spec["prefix"]
        decision = self.hydrology_lod_policy.decision(self.basemap_lod, layer_id)
        render_profile = self.hydrology_render_profile.decision(self.basemap_lod, layer_id)
        obj = load_vector_geojson_from_source(
            layer_id,
            file_path=decision["file_path"],
            url=decision["url"],
            natural_earth_layer=decision["natural_earth_layer"],
            natural_earth_source=decision["natural_earth_source"],
        )
        lines = geojson_to_lines(obj, decimate=max(1, int(render_profile["decimate"])))
        return GeoVectorLineOverlay(self.width, self.height, lines, spec["name"])

    def _load_boundary_overlays(self) -> dict[str, GeoVectorLineOverlay]:
        overlays: dict[str, GeoVectorLineOverlay] = {}
        for layer_id, spec in BOUNDARY_SPECS.items():
            if self.layer_visible.get(layer_id, False):
                overlays[layer_id] = self._load_single_boundary_overlay(layer_id)
            else:
                overlays[layer_id] = GeoVectorLineOverlay(self.width, self.height, [], spec["name"])
        return overlays

    def _load_single_boundary_overlay(self, layer_id: str) -> GeoVectorLineOverlay:
        spec = BOUNDARY_SPECS[layer_id]
        decision = self.boundary_lod_policy.decision(self.basemap_lod, layer_id)
        obj = load_vector_geojson_from_source(
            layer_id,
            file_path=decision["file_path"],
            url=decision["url"],
            natural_earth_layer=decision["natural_earth_layer"],
            natural_earth_source=decision["natural_earth_source"],
        )
        lines = geojson_to_lines(obj, decimate=max(1, int(decision["decimate"])))
        return GeoVectorLineOverlay(self.width, self.height, lines, spec["name"])

    def _vector_cache_limit(self) -> int:
        megapixels = max(1.0, (int(self.width) * int(self.height)) / 1_000_000.0)
        if megapixels >= 6.0:
            return 2
        if megapixels >= 3.0:
            return 3
        return 5

    def _vector_point_stride(self) -> int:
        budget = self.render_budget_decision()
        return max(1, int(budget.get("vector_point_stride", 1)))

    def _vector_camera_key(self, namespace: str) -> tuple:
        budget = self.render_budget_decision()
        q_rad = max(math.radians(0.001), math.radians(float(budget.get("vector_cache_degrees", 0.004))))
        q_zoom = max(0.0005, float(budget.get("vector_cache_zoom_step", 0.001)))
        return (
            namespace,
            int(self.width),
            int(self.height),
            int(round(float(self.yaw) / q_rad)),
            int(round(float(self.pitch) / q_rad)),
            int(round(float(self.zoom) / q_zoom)),
            bool(self.flip_longitude),
            bool(self.flip_latitude),
            self.basemap_lod,
            self._vector_point_stride(),
        )

    def _cache_vector_overlay(self, cache_key: tuple, payload: object) -> None:
        self.vector_overlay_cache[cache_key] = payload
        if cache_key in self.vector_overlay_cache_order:
            self.vector_overlay_cache_order.remove(cache_key)
        self.vector_overlay_cache_order.append(cache_key)
        limit = self._vector_cache_limit()
        while len(self.vector_overlay_cache_order) > limit:
            old_key = self.vector_overlay_cache_order.pop(0)
            self.vector_overlay_cache.pop(old_key, None)

    def _lookup_vector_overlay_cache(self, cache_key: tuple) -> object | None:
        cached = self.vector_overlay_cache.get(cache_key)
        if cached is None:
            self.vector_overlay_cache_misses += 1
            return None
        self.vector_overlay_cache_hits += 1
        if cache_key in self.vector_overlay_cache_order:
            self.vector_overlay_cache_order.remove(cache_key)
        self.vector_overlay_cache_order.append(cache_key)
        return cached

    def _current_hydrology_view_key(self) -> tuple:
        layer_state = tuple(
            (
                layer_id,
                bool(self.layer_visible.get(layer_id, True)),
                id(self.hydrology_overlays.get(layer_id)),
                self.hydrology_render_profile.decision(self.basemap_lod, layer_id)["decimate"],
                round(float(self.hydrology_render_profile.decision(self.basemap_lod, layer_id)["opacity_scale"]), 3),
                round(float(self.hydrology_render_profile.decision(self.basemap_lod, layer_id)["width_scale"]), 3),
                round(float(getattr(self.args, f"{HYDROLOGY_SPECS[layer_id]['prefix']}_opacity", 0.55)), 3),
                round(float(getattr(self.args, f"{HYDROLOGY_SPECS[layer_id]['prefix']}_width", 1)), 3),
            )
            for layer_id in ("lakes", "rivers")
        )
        return self._vector_camera_key("hydrology") + (
            layer_state,
            style_vector_cache_key(getattr(self.args, "style_profile", "scientific")),
        )

    def _current_boundary_view_key(self) -> tuple:
        layer_state = tuple(
            (
                layer_id,
                bool(self.layer_visible.get(layer_id, True)),
                id(self.boundary_overlays.get(layer_id)),
                round(float(getattr(self.args, {
                    "borders": "border_opacity",
                    "territorial_sea": "territorial_sea_opacity",
                    "eez": "eez_opacity",
                    "high_seas": "high_seas_opacity",
                }.get(layer_id, f"{layer_id}_opacity"), 0.65)), 3),
                int(getattr(self.args, {
                    "borders": "border_width",
                    "territorial_sea": "territorial_sea_width",
                    "eez": "eez_width",
                    "high_seas": "high_seas_width",
                }.get(layer_id, f"{layer_id}_width"), 1)),
            )
            for layer_id in BOUNDARY_SPECS
        )
        return self._vector_camera_key("boundary") + (
            layer_state,
            style_vector_cache_key(getattr(self.args, "style_profile", "scientific")),
            self.hover_boundary_hit.get("layer_id"),
            self.hover_boundary_hit.get("line_index"),
            self.boundary_hover_phase_bucket,
        )

    def _render_hydrology_if_needed(self, force: bool = False) -> None:
        view_key = self._current_hydrology_view_key()
        if not force and not self.hydrology_dirty and self.hydrology_view_key == view_key:
            return
        cache_key = ("hydrology", view_key)
        cached = None if force else self._lookup_vector_overlay_cache(cache_key)
        if cached is not None:
            self.lake_overlay_rgba, self.river_overlay_rgba = cached
            self.hydrology_view_key = view_key
            self.hydrology_dirty = False
            return
        for layer_id, attr in (("lakes", "lake_overlay_rgba"), ("rivers", "river_overlay_rgba")):
            overlay = self.hydrology_overlays.get(layer_id)
            if overlay is None or not self.layer_visible.get(layer_id, True):
                setattr(self, attr, np.zeros_like(self.globe_rgba))
                continue
            spec = HYDROLOGY_SPECS[layer_id]
            render_profile = self.hydrology_render_profile.decision(self.basemap_lod, layer_id)
            render_params = build_hydrology_render_params(
                self.args,
                layer_id,
                spec,
                render_profile,
                getattr(self.args, "style_profile", "scientific"),
            )
            setattr(
                self,
                attr,
                overlay.render(
                    self.yaw,
                    self.pitch,
                    self.zoom,
                    self.flip_longitude,
                    self.flip_latitude,
                    self.globe_mask,
                    render_params["color"],
                    render_params["opacity"],
                    render_params["width"],
                    point_stride=self._vector_point_stride(),
                ),
            )
        self.hydrology_view_key = view_key
        self.hydrology_dirty = False
        self._cache_vector_overlay(cache_key, (self.lake_overlay_rgba, self.river_overlay_rgba))

    def _render_boundaries_if_needed(self, force: bool = False) -> None:
        view_key = self._current_boundary_view_key()
        if not force and not self.boundary_dirty and self.boundary_view_key == view_key:
            return
        cache_key = ("boundary", view_key)
        cached = None if force else self._lookup_vector_overlay_cache(cache_key)
        if cached is not None:
            self.boundary_overlay_rgba = cached
            self.boundary_view_key = view_key
            self.boundary_dirty = False
            self.boundary_hover_dirty = False
            return
        composite = np.zeros_like(self.globe_rgba)
        highlight_layer = self.hover_boundary_hit.get("layer_id")
        highlight_line_index = self.hover_boundary_hit.get("line_index")
        highlight_phase = (time.time() * 0.7) % 1.0
        for layer_id, spec in BOUNDARY_SPECS.items():
            overlay = self.boundary_overlays.get(layer_id)
            if overlay is None or not self.layer_visible.get(layer_id, True):
                continue
            render_params = build_boundary_render_params(
                self.args,
                layer_id,
                spec,
                getattr(self.args, "style_profile", "scientific"),
            )
            rendered = overlay.render(
                self.yaw,
                self.pitch,
                self.zoom,
                self.flip_longitude,
                self.flip_latitude,
                self.globe_mask,
                render_params["color"],
                render_params["opacity"],
                render_params["width"],
                int(highlight_line_index) if highlight_layer == layer_id and highlight_line_index is not None else None,
                highlight_phase,
                point_stride=self._vector_point_stride(),
            )
            composite = alpha_compose_transparent(composite, rendered)
        self.boundary_overlay_rgba = composite
        self.boundary_view_key = view_key
        self.boundary_dirty = False
        self.boundary_hover_dirty = False
        self._cache_vector_overlay(cache_key, self.boundary_overlay_rgba)

    def hydrology_layer_status_text(self, layer_id: str) -> str:
        overlay = self.hydrology_overlays.get(layer_id)
        count = len(getattr(overlay, "lines", [])) if overlay else 0
        decision = self.hydrology_lod_policy.decision(self.basemap_lod, layer_id)
        render_profile = self.hydrology_render_profile.decision(self.basemap_lod, layer_id)
        strictness = self.hydrology_strictness_policy.decision(self.basemap_lod, layer_id, decision)
        return (
            f"{layer_id}: {count:,} lines; provider={decision['provider_id']}; "
            f"source={decision['natural_earth_source']}; input={decision['renderer_input']}; "
            f"decimate={render_profile['decimate']}; strictness={strictness['tier']}; {decision['status']}"
        )

    def hydrology_provider_decisions_text(self) -> str:
        lines = [f"Hydrology provider decisions for LOD={self.basemap_lod}"]
        for layer_id in HYDROLOGY_SPECS:
            decision = self.hydrology_lod_policy.decision(self.basemap_lod, layer_id)
            render_profile = self.hydrology_render_profile.decision(self.basemap_lod, layer_id)
            strictness = self.hydrology_strictness_policy.decision(self.basemap_lod, layer_id, decision)
            manifest = decision["manifest"]
            lines.append(f"- {layer_id}: {decision['provider_id']}")
            lines.append(f"  source: {manifest['source_url']}")
            lines.append(f"  adapter target: {decision['target_adapter']}")
            lines.append(f"  renderer input: {decision['renderer_input']}")
            lines.append(f"  render decimate: {render_profile['decimate']}")
            lines.append(f"  opacity/width scale: {render_profile['opacity_scale']:.2f}/{render_profile['width_scale']:.2f}")
            lines.append(f"  strictness: {strictness['tier']} ({strictness['scientific_use']})")
            if decision.get("strict_source", {}).get("configured"):
                strict_source = decision["strict_source"]
                lines.append(f"  strict provider: {strict_source['label']} ({strict_source['provider_id']})")
                lines.append(f"  strict metadata complete: {strict_source.get('metadata_complete', False)}")
                if strict_source.get("metadata_missing"):
                    lines.append(f"  strict metadata missing: {', '.join(strict_source['metadata_missing'])}")
            lines.append(f"  strictness next: {strictness['next_action']}")
            lines.append(f"  cache: {manifest['cache_path']}")
        return "\n".join(lines)

    def hydrology_control_snapshot(self) -> dict:
        layers = {}
        for layer_id, spec in HYDROLOGY_SPECS.items():
            prefix = spec["prefix"]
            overlay = self.hydrology_overlays.get(layer_id)
            decision = self.hydrology_lod_policy.decision(self.basemap_lod, layer_id)
            render_profile = self.hydrology_render_profile.decision(self.basemap_lod, layer_id)
            strictness = self.hydrology_strictness_policy.decision(self.basemap_lod, layer_id, decision)
            render_params = build_hydrology_render_params(
                self.args,
                layer_id,
                spec,
                render_profile,
                getattr(self.args, "style_profile", "scientific"),
            )
            layers[layer_id] = {
                "visible": bool(self.layer_visible.get(layer_id, True)),
                "line_count": int(len(getattr(overlay, "lines", []))) if overlay else 0,
                "source": decision,
                "render_profile": render_profile,
                "resolved_render_params": render_params,
                "strictness": strictness,
                "ui_controls": {
                    "file_attr": f"{prefix}_file",
                    "url_attr": f"{prefix}_url",
                    "opacity_attr": f"{prefix}_opacity",
                    "width_attr": f"{prefix}_width",
                    "layer_attr": f"{prefix}_layer",
                },
            }
        return {
            "contract": "Hydrology control owns source selection and vector simplification; GeoVectorLineOverlay only receives lon/lat lines plus screen-space render parameters.",
            "source_mode": getattr(self.args, "hydrology_source_mode", "lod"),
            "basemap_lod": self.basemap_lod,
            "render_lod_profile": {
                layer_id: self.hydrology_render_profile.decision(self.basemap_lod, layer_id)
                for layer_id in HYDROLOGY_SPECS
            },
            "layers": layers,
            "dirty": bool(self.hydrology_dirty),
            "view_key": self.hydrology_view_key,
            "vector_cache": {
                "items": len(self.vector_overlay_cache),
                "limit": self._vector_cache_limit(),
                "hits": self.vector_overlay_cache_hits,
                "misses": self.vector_overlay_cache_misses,
                "deferred": self.vector_overlay_cache_deferred,
            },
            "next_module_target": "data_sources/hydrology_provider.py + overlays/vector_lines.py",
        }

    def hydrology_control_text(self) -> str:
        return json.dumps(self.hydrology_control_snapshot(), ensure_ascii=False, indent=2, default=str)

    def hydrology_basic_readiness_matrix_snapshot(self) -> dict:
        style_profile = getattr(self.args, "style_profile", "scientific")
        layers = {}
        loaded_count = 0
        contract_ready_count = 0
        for layer_id, spec in HYDROLOGY_SPECS.items():
            prefix = spec["prefix"]
            overlay = self.hydrology_overlays.get(layer_id)
            line_count = int(len(getattr(overlay, "lines", []))) if overlay else 0
            decision = self.hydrology_lod_policy.decision(self.basemap_lod, layer_id)
            render_profile = self.hydrology_render_profile.decision(self.basemap_lod, layer_id)
            strictness = self.hydrology_strictness_policy.decision(self.basemap_lod, layer_id, decision)
            render_params = build_hydrology_render_params(
                self.args,
                layer_id,
                spec,
                render_profile,
                style_profile,
            )
            data_loaded = line_count > 0
            contract_ready = bool(
                decision.get("provider_id")
                and decision.get("renderer_input")
                and render_profile
                and strictness.get("tier")
                and render_params
            )
            visible = bool(self.layer_visible.get(layer_id, getattr(self.args, f"{prefix}_layer", True)))
            if data_loaded:
                loaded_count += 1
            if contract_ready:
                contract_ready_count += 1
            layers[layer_id] = {
                "name": spec.get("name", layer_id),
                "visible": visible,
                "data_loaded": data_loaded,
                "line_count": line_count,
                "contract_ready": contract_ready,
                "readiness": (
                    "disabled"
                    if not visible else
                    "ready_with_loaded_vectors"
                    if data_loaded else
                    "configured_waiting_for_vectors"
                ),
                "provider_id": decision.get("provider_id", ""),
                "provider_status": decision.get("status", ""),
                "renderer_input": decision.get("renderer_input", ""),
                "target_adapter": decision.get("target_adapter", ""),
                "strictness_tier": strictness.get("tier", ""),
                "strictness_next_action": strictness.get("next_action", ""),
                "render_profile": render_profile,
                "resolved_render_params": render_params,
                "ui_control_attrs": {
                    "file": f"{prefix}_file",
                    "url": f"{prefix}_url",
                    "opacity": f"{prefix}_opacity",
                    "width": f"{prefix}_width",
                    "layer": f"{prefix}_layer",
                },
            }
        return {
            "contract": "Hydrology basic readiness matrix separates static control readiness from runtime vector-data loading for lakes/rivers.",
            "basemap_lod": self.basemap_lod,
            "source_mode": getattr(self.args, "hydrology_source_mode", "lod"),
            "style_profile": style_profile,
            "layer_count": len(layers),
            "contract_ready_count": contract_ready_count,
            "loaded_count": loaded_count,
            "runtime_verification": "not-run",
            "layers": layers,
            "next_module_target": "data_sources/hydrology_provider.py + overlays/vector_lines.py",
        }

    def hydrology_basic_readiness_matrix_text(self) -> str:
        return json.dumps(self.hydrology_basic_readiness_matrix_snapshot(), ensure_ascii=False, indent=2, default=str)

    def hydrology_dirty_reload_contract_snapshot(self) -> dict:
        items = []
        for item in HYDROLOGY_DIRTY_RELOAD_CONTRACT:
            expected_flags = list(item["expected_dirty_flags"])
            missing_flags = [
                flag for flag in expected_flags
                if not hasattr(self, flag)
            ]
            current_flags = {
                flag: bool(getattr(self, flag, False))
                for flag in expected_flags
                if hasattr(self, flag)
            }
            entry = dict(item)
            entry["current_flags"] = current_flags
            entry["missing_flags"] = missing_flags
            entry["contract_ready"] = not missing_flags
            items.append(entry)
        missing_contracts = [
            item["trigger"] for item in items
            if not item["contract_ready"]
        ]
        return {
            "contract": "Hydrology dirty/reload contract keeps source reload, strict provider selection, render controls, and vector cache ownership explicit before splitting hydrology provider code.",
            "runtime_verification": "not-run",
            "basemap_lod": self.basemap_lod,
            "source_mode": getattr(self.args, "hydrology_source_mode", "lod"),
            "layer_count": len(HYDROLOGY_SPECS),
            "trigger_count": len(items),
            "ready": not missing_contracts,
            "missing_contracts": missing_contracts,
            "vector_cache": {
                "items": len(self.vector_overlay_cache),
                "limit": self._vector_cache_limit(),
                "hits": self.vector_overlay_cache_hits,
                "misses": self.vector_overlay_cache_misses,
                "deferred": self.vector_overlay_cache_deferred,
            },
            "items": items,
            "next_module_target": "data_sources/hydrology_provider.py + overlays/vector_lines.py",
        }

    def hydrology_dirty_reload_contract_text(self) -> str:
        return json.dumps(self.hydrology_dirty_reload_contract_snapshot(), ensure_ascii=False, indent=2, default=str)

    def reload_hydrology_layer(self, layer_id: str, file_path: str | None = None, url: str | None = None) -> None:
        if layer_id not in HYDROLOGY_SPECS:
            return
        prefix = HYDROLOGY_SPECS[layer_id]["prefix"]
        setattr(self.args, f"{prefix}_file", (file_path or "").strip() or None)
        setattr(self.args, f"{prefix}_url", (url or "").strip() or None)
        self.hydrology_overlays[layer_id] = self._load_single_hydrology_overlay(layer_id)
        self.hydrology_dirty = True
        self.overlay_dirty = True

    def set_hydrology_strict_source(self, layer_id: str, port_id: str, file_path: str | None = None, url: str | None = None) -> None:
        if layer_id not in HYDROLOGY_SPECS:
            return
        selected = None
        for port in HYDROLOGY_STRICT_PROVIDER_PORTS.get(layer_id, []):
            setattr(self.args, port["file_attr"], None)
            setattr(self.args, port["url_attr"], None)
            if port["id"] == port_id:
                selected = port
        if selected is None:
            return
        setattr(self.args, selected["file_attr"], (file_path or "").strip() or None)
        setattr(self.args, selected["url_attr"], (url or "").strip() or None)
        self.args.hydrology_source_mode = "strict"
        self.hydrology_overlays[layer_id] = self._load_single_hydrology_overlay(layer_id)
        self.hydrology_dirty = True
        self.overlay_dirty = True

    def set_hydrology_strict_metadata(
        self,
        source_version: str = "",
        license_text: str = "",
        projection: str = "",
        attribution: str = "",
        schema_note: str = "",
    ) -> None:
        self.args.hydrology_source_version = str(source_version or "")
        self.args.hydrology_license = str(license_text or "")
        self.args.hydrology_projection = str(projection or "")
        self.args.hydrology_attribution = str(attribution or "")
        self.args.hydrology_schema_note = str(schema_note or "")
        self.hydrology_dirty = True
        self.overlay_dirty = True

    def set_hydrology_source_mode(self, mode: str) -> None:
        mode = str(mode or "lod")
        if mode not in {"lod", "manual", "strict"}:
            mode = "lod"
        self.args.hydrology_source_mode = mode
        self.hydrology_dirty = True
        self.overlay_dirty = True

    def set_hydrology_opacity(self, layer_id: str, value: float) -> None:
        if layer_id not in HYDROLOGY_SPECS:
            return
        setattr(self.args, f"{HYDROLOGY_SPECS[layer_id]['prefix']}_opacity", max(0.0, min(float(value), 1.0)))
        self.hydrology_dirty = True
        self.overlay_dirty = True

    def set_hydrology_width(self, layer_id: str, value: int) -> None:
        if layer_id not in HYDROLOGY_SPECS:
            return
        setattr(self.args, f"{HYDROLOGY_SPECS[layer_id]['prefix']}_width", max(1, int(value)))
        self.hydrology_dirty = True
        self.overlay_dirty = True

    def layer_label(self, layer_id: str) -> str:
        return self.LAYER_LABELS.get(layer_id, HYDROLOGY_SPECS.get(layer_id, {}).get("name", layer_id))

    def set_layer_visible(self, layer_id: str, visible: bool) -> None:
        self.layer_visible[layer_id] = bool(visible)
        if layer_id in HYDROLOGY_SPECS:
            setattr(self.args, f"{HYDROLOGY_SPECS[layer_id]['prefix']}_layer", bool(visible))
            self.hydrology_dirty = True
        if layer_id in BOUNDARY_SPECS:
            overlay = getattr(self, "boundary_overlays", {}).get(layer_id)
            if bool(visible) and (overlay is None or not getattr(overlay, "lines", [])):
                self.boundary_overlays[layer_id] = self._load_single_boundary_overlay(layer_id)
            self.boundary_dirty = True
        if layer_id == "scale":
            self.args.scale_bar = bool(visible)
        self.overlay_dirty = True
        self.globe_dirty = self.globe_dirty or layer_id in {"globe", "ice", "forest", "clouds", "contours"}

    def set_layer_order(self, order: list[str]) -> None:
        known = [layer for layer in order if layer in self.LAYER_LABELS]
        for layer in self.layer_order:
            if layer not in known:
                known.append(layer)
        self.layer_order = known
        self.overlay_dirty = True

    def layer_allowed_in_mode(self, layer_id: str) -> bool:
        mode = str(getattr(self.args, "data_mode", "realtime"))
        if layer_id in {"ais", "aircraft", "vehicle_icons"}:
            return mode == "realtime"
        return True

    def mode_label(self, mode: str | None = None) -> str:
        mode = str(mode or getattr(self.args, "data_mode", "realtime"))
        return {
            "static": "Static mode",
            "timeseries": "Time-series mode",
            "realtime": "Realtime mode",
        }.get(mode, mode)

    def selected_info_text(self) -> str:
        if self.selected_vehicle is None:
            return "No vehicle selected."
        row = self.selected_vehicle
        if isinstance(row, pd.Series):
            lines = ["Selected vehicle"]
            for key in ("source", "mmsi", "icao24", "name", "shipname", "callsign", "lat", "lon", "sog", "speed_kt", "altitude_m", "cog", "heading", "timestamp"):
                if key in row and pd.notna(row.get(key)):
                    lines.append(f"- {key}: {row.get(key)}")
            return "\n".join(lines)
        return str(row)

    def pick_vehicle(self, x: float, y: float) -> None:
        radius = float(getattr(self.args, "icon_pick_radius", 14.0))
        best_row = None
        best_dist2 = radius * radius
        for source_name, frame in (("AIS", self.current_projected), ("ADS-B", self.current_aircraft_projected)):
            if frame.empty:
                continue
            dx = frame["screen_x"].to_numpy(dtype=np.float32) - float(x)
            dy = frame["screen_y"].to_numpy(dtype=np.float32) - float(y)
            dist2 = dx * dx + dy * dy
            index = int(np.argmin(dist2))
            if float(dist2[index]) <= best_dist2:
                best_dist2 = float(dist2[index])
                row = frame.iloc[index].copy()
                row["source"] = source_name
                best_row = row
        self.selected_vehicle = best_row

    def hit_test_scale_bar(self, x: float, y: float) -> bool:
        if not bool(getattr(self.args, "scale_bar", True)):
            return False
        bar_x = float(getattr(self.args, "scale_bar_x", 32.0))
        bar_y = float(getattr(self.args, "scale_bar_y", max(40.0, self.height - 54.0)))
        return bar_x - 10.0 <= float(x) <= bar_x + 250.0 and bar_y - 24.0 <= float(y) <= bar_y + 28.0

    def set_scale_bar_position(self, x: float, y: float) -> None:
        self.args.scale_bar_x = max(0.0, min(float(x), max(0.0, self.width - 240.0)))
        self.args.scale_bar_y = max(24.0, min(float(y), max(24.0, self.height - 24.0)))

    def set_scale_bar_opacity(self, value: float) -> None:
        self.args.scale_bar_opacity = max(0.0, min(float(value), 1.0))

    def set_boundary_hover(self, x: float, y: float) -> None:
        best = build_empty_boundary_hit()
        for layer_id, overlay in getattr(self, "boundary_overlays", {}).items():
            if not self.layer_visible.get(layer_id, True) or overlay is None:
                continue
            hit = overlay.hit_test(
                x,
                y,
                self.yaw,
                self.pitch,
                self.zoom,
                self.flip_longitude,
                self.flip_latitude,
                radius_px=10.0,
            )
            if hit and hit["distance_px"] < best["distance_px"]:
                best = {
                    "layer_id": layer_id,
                    "name": self.layer_label(layer_id),
                    "line_index": hit.get("line_index"),
                    "distance_px": hit["distance_px"],
                }
        if best != self.hover_boundary_hit:
            self.hover_boundary_hit = best
            self.boundary_hover_dirty = True
            self.boundary_dirty = True

    def boundary_layer_status_text(self, layer_id: str) -> str:
        overlay = getattr(self, "boundary_overlays", {}).get(layer_id)
        count = len(getattr(overlay, "lines", [])) if overlay else 0
        decision = self.boundary_lod_policy.decision(self.basemap_lod, layer_id)
        manifest = decision["manifest"]
        return (
            f"{layer_id}: {count:,} lines; provider={decision['provider_id']}; "
            f"source={manifest['source_url']}; input={decision['renderer_input']}; "
            f"decimate={decision['decimate']}; {decision['status']}"
        )

    def boundary_provider_decisions_text(self) -> str:
        lines = [f"Boundary provider decisions for LOD={self.basemap_lod}"]
        for layer_id in BOUNDARY_SPECS:
            decision = self.boundary_lod_policy.decision(self.basemap_lod, layer_id)
            manifest = decision["manifest"]
            lines.append(f"- {layer_id}: {decision['provider_id']}")
            lines.append(f"  source: {manifest['source_url']}")
            lines.append(f"  adapter target: {decision['target_adapter']}")
            lines.append(f"  renderer input: {decision['renderer_input']}")
            lines.append(f"  decimate: {decision['decimate']}")
            lines.append(f"  cache: {manifest['cache_path']}")
            lines.append(f"  status: {decision['status']}")
        return "\n".join(lines)

    def set_boundary_opacity(self, layer_id: str, value: float) -> None:
        attr = {
            "borders": "border_opacity",
            "territorial_sea": "territorial_sea_opacity",
            "eez": "eez_opacity",
            "high_seas": "high_seas_opacity",
        }.get(layer_id, f"{layer_id}_opacity")
        setattr(self.args, attr, max(0.0, min(float(value), 1.0)))
        self.boundary_dirty = True
        self.overlay_dirty = True

    def set_boundary_width(self, layer_id: str, value: int) -> None:
        attr = {
            "borders": "border_width",
            "territorial_sea": "territorial_sea_width",
            "eez": "eez_width",
            "high_seas": "high_seas_width",
        }.get(layer_id, f"{layer_id}_width")
        setattr(self.args, attr, max(1, int(value)))
        self.boundary_dirty = True
        self.overlay_dirty = True

    def reload_boundary_layer(self, layer_id: str, file_path: str | None = None, url: str | None = None) -> None:
        spec = BOUNDARY_SPECS.get(layer_id)
        if not spec:
            return
        prefix = spec.get("prefix", layer_id)
        setattr(self.args, f"{prefix}_file", (file_path or "").strip() or None)
        setattr(self.args, f"{prefix}_url", (url or "").strip() or None)
        self.boundary_overlays[layer_id] = self._load_single_boundary_overlay(layer_id)
        self.boundary_dirty = True
        self.overlay_dirty = True

    def reload_topography_step(self, step: int) -> None:
        self.args.topo_step = max(1, int(step))
        self.globe_dirty = True
        self.overlay_dirty = True

    def reload_ice_source(self, source: str) -> None:
        self.args.ice_source = str(source or "auto")
        self.globe_dirty = True

    def ocean_condition_status_text(self) -> str:
        return self.ocean_conditions.status_text()

    def ocean_provider_decision_text(self) -> str:
        return self.ocean_conditions.decision_text(self.basemap_lod)

    def ocean_render_port_contract_text(self) -> str:
        return ocean_render_port_contract_text()

    def ocean_normalization_report_text(self) -> str:
        return self.ocean_conditions.normalization_report_text()

    def ocean_spatial_sampling_text(self) -> str:
        return self.ocean_conditions.spatial_sampling_text()

    def ocean_material_control_snapshot(self) -> dict:
        condition_state = dict(getattr(self.ocean_conditions, "cached_conditions", {}) or {})
        provider_decision = self.ocean_conditions.decision(self.basemap_lod)
        material = self.ocean_material_policy.resolve(condition_state, self.basemap_lod)
        uniforms = build_ocean_material_uniforms(material)
        style_profile = getattr(self.args, "style_profile", "scientific")
        return {
            "contract": "Ocean material control converts provider data into scalar Taichi render inputs only; provider IO must stay outside render_core.",
            "source": provider_decision.get("source", ""),
            "source_kind": provider_decision.get("source_kind", ""),
            "spatial_sampling": provider_decision.get("spatial_sampling", {}),
            "normalization_report": getattr(self.ocean_conditions, "last_normalization_report", {}),
            "cached_condition_state": condition_state,
            "style_renderer_entry": resolve_style_renderer_entry(style_profile),
            "taichi_scalar_inputs": {
                "enabled": bool(uniforms["ocean_enabled"]),
                **uniforms,
            },
            "style_modifier": dict(material.get("style_modifier", {})),
            "lod": self.basemap_lod,
            "next_module_target": "render_core/ocean_material.py",
        }

    def ocean_material_control_text(self) -> str:
        return json.dumps(self.ocean_material_control_snapshot(), ensure_ascii=False, indent=2, default=str)

    def ocean_material_taichi_port_snapshot(self) -> dict:
        condition_state = dict(getattr(self.ocean_conditions, "cached_conditions", {}) or {})
        material = self.ocean_material_policy.resolve(condition_state, self.basemap_lod)
        uniforms = build_ocean_material_uniforms(material)
        kernel_inputs = {
            "ocean_enabled": bool(uniforms["ocean_enabled"]),
            "wave_strength": float(uniforms["wave_strength"]),
            "roughness": float(uniforms["roughness"]),
            "foam": float(uniforms["foam"]),
            "time_seconds": "time.time() % 100000.0 at render",
        }
        wired_names = set(kernel_inputs)
        return {
            "contract": "Current Taichi ocean material render port; render_core must consume scalar inputs only, not provider decisions or Qt args.",
            "render_call": "globe.render(..., ocean_enabled, wave_strength, roughness, foam, time_seconds)",
            "kernel_argument_order": list(RENDER_CORE_OCEAN_MATERIAL_MODULE_API["taichi_kernel_inputs"]),
            "kernel_inputs": kernel_inputs,
            "resolved_uniforms": uniforms,
            "unwired_policy_scalars": [
                name for name in uniforms
                if name not in wired_names
            ],
            "cached_condition_state": condition_state,
            "policy_material": material,
            "lod": self.basemap_lod,
            "next_module_target": "render_core/ocean_material.py",
        }

    def ocean_material_taichi_port_text(self) -> str:
        return json.dumps(self.ocean_material_taichi_port_snapshot(), ensure_ascii=False, indent=2, default=str)

    def ocean_condition_material_binding_snapshot(self) -> dict:
        condition_state = dict(getattr(self.ocean_conditions, "cached_conditions", {}) or {})
        provider_decision = self.ocean_conditions.decision(self.basemap_lod)
        material = self.ocean_material_policy.resolve(condition_state, self.basemap_lod)
        uniforms = build_ocean_material_uniforms(material)
        taichi_port = self.ocean_material_taichi_port_snapshot()
        kernel_inputs = dict(taichi_port.get("kernel_inputs", {}))
        bindings = [
            {
                "source_field": "enabled",
                "material_field": "enabled",
                "uniform_field": "ocean_enabled",
                "kernel_input": "ocean_enabled",
                "kernel_required": True,
            },
            {
                "source_field": "wave_strength",
                "material_field": "wave_strength",
                "uniform_field": "wave_strength",
                "kernel_input": "wave_strength",
                "kernel_required": True,
            },
            {
                "source_field": "roughness",
                "material_field": "roughness",
                "uniform_field": "roughness",
                "kernel_input": "roughness",
                "kernel_required": True,
            },
            {
                "source_field": "foam",
                "material_field": "foam",
                "uniform_field": "foam",
                "kernel_input": "foam",
                "kernel_required": True,
            },
            {
                "source_field": "material_scale",
                "material_field": "material_scale",
                "uniform_field": "material_scale",
                "kernel_input": "",
                "kernel_required": False,
            },
        ]
        for binding in bindings:
            binding["source_declared"] = binding["source_field"] in OCEAN_CONDITION_PROVIDER_MODULE_API["renderer_scalar_fields"]
            binding["state_present"] = binding["source_field"] in condition_state
            binding["material_present"] = binding["material_field"] in material
            binding["uniform_declared"] = binding["uniform_field"] in RENDER_CORE_OCEAN_MATERIAL_MODULE_API["taichi_uniforms"]
            binding["uniform_present"] = binding["uniform_field"] in uniforms
            binding["kernel_present"] = (
                bool(binding["kernel_input"])
                and binding["kernel_input"] in kernel_inputs
            )
        missing_uniforms = [
            binding["uniform_field"] for binding in bindings
            if not binding["uniform_declared"] or not binding["uniform_present"]
        ]
        missing_kernel_inputs = [
            binding["kernel_input"] for binding in bindings
            if binding["kernel_required"] and not binding["kernel_present"]
        ]
        policy_only_uniforms = [
            binding["uniform_field"] for binding in bindings
            if not binding["kernel_required"]
        ]
        return {
            "contract": "Ocean condition material binding maps provider scalar fields to render-core material fields, scalar uniforms, and Taichi kernel inputs without exposing provider IO to render_core.",
            "runtime_verification": "not-run",
            "source": provider_decision.get("source", ""),
            "source_kind": provider_decision.get("source_kind", ""),
            "spatial_sampling": provider_decision.get("spatial_sampling", {}),
            "lod": self.basemap_lod,
            "style_profile": material.get("style_profile", ""),
            "condition_state_present_fields": sorted(condition_state.keys()),
            "binding_count": len(bindings),
            "bindings": bindings,
            "policy_only_uniforms": policy_only_uniforms,
            "missing_uniforms": missing_uniforms,
            "missing_kernel_inputs": missing_kernel_inputs,
            "ready": not missing_uniforms and not missing_kernel_inputs,
            "next_module_target": "render_core/ocean_material.py",
        }

    def ocean_condition_material_binding_text(self) -> str:
        return json.dumps(self.ocean_condition_material_binding_snapshot(), ensure_ascii=False, indent=2, default=str)

    def cache_governance_matrix_text(self) -> str:
        return cache_governance_matrix_text()

    def data_fetch_status_text(self) -> str:
        return data_fetch_status_text()

    def data_fetch_progress_snapshot(self) -> dict:
        return data_fetch_progress_snapshot()

    def lod_hook_pipeline_snapshot(self) -> dict:
        km_per_pixel = float(self.current_km_per_pixel())
        projection = getattr(self.args, "map_projection", "globe")
        basemap = self.lod_manager.decision(
            km_per_pixel,
            projection=projection,
            topo_source=getattr(self.args, "topo_source", None),
            topo_step=getattr(self.args, "topo_step", None),
        )
        hydrology = {
            layer_id: {
                "source": self.hydrology_lod_policy.decision(self.basemap_lod, layer_id),
                "render": self.hydrology_render_profile.decision(self.basemap_lod, layer_id),
            }
            for layer_id in ("lakes", "rivers")
        }
        boundaries = {
            layer_id: {
                "source": self.boundary_lod_policy.decision(self.basemap_lod, layer_id),
                "render": build_boundary_render_params(
                    self.args,
                    layer_id,
                    spec,
                    getattr(self.args, "style_profile", "scientific"),
                ),
            }
            for layer_id, spec in BOUNDARY_SPECS.items()
        }
        ocean = self.ocean_conditions.decision(self.basemap_lod)
        return {
            "contract": "LOD hook pipeline should choose data source, simplification, render budget, and material sampling before renderers run.",
            "projection": projection,
            "km_per_pixel": km_per_pixel,
            "basemap_lod": self.basemap_lod,
            "basemap": basemap,
            "hydrology": hydrology,
            "boundaries": boundaries,
            "ocean_spatial_sampling": ocean.get("spatial_sampling", {}),
            "render_budget": self.render_budget_decision(),
            "point_overlay_budget": dict(self.point_overlay_budget_last),
            "style_profile": getattr(self.args, "style_profile", "scientific"),
            "next_module_target": "projection/lod_pipeline.py",
        }

    def lod_hook_pipeline_text(self) -> str:
        return json.dumps(self.lod_hook_pipeline_snapshot(), ensure_ascii=False, indent=2, default=str)

    def lod_invalidation_contract_snapshot(self) -> dict:
        items = []
        for item in LOD_INVALIDATION_CONTRACT:
            expected_flags = list(item["expected_dirty_flags"])
            missing_flags = [
                flag for flag in expected_flags
                if not hasattr(self, flag)
            ]
            current_flags = {
                flag: bool(getattr(self, flag, False))
                for flag in expected_flags
                if hasattr(self, flag)
            }
            entry = dict(item)
            entry["current_flags"] = current_flags
            entry["missing_flags"] = missing_flags
            entry["contract_ready"] = not missing_flags
            items.append(entry)
        missing_contracts = [
            item["trigger"] for item in items
            if not item["contract_ready"]
        ]
        return {
            "contract": "LOD invalidation contract documents which controller dirty flags and cache policies must be preserved when the LOD hook is split.",
            "runtime_verification": "not-run",
            "basemap_lod": self.basemap_lod,
            "km_per_pixel": float(self.current_km_per_pixel()),
            "trigger_count": len(items),
            "ready": not missing_contracts,
            "missing_contracts": missing_contracts,
            "items": items,
            "next_module_target": "projection/lod_pipeline.py",
        }

    def lod_invalidation_contract_text(self) -> str:
        return json.dumps(self.lod_invalidation_contract_snapshot(), ensure_ascii=False, indent=2, default=str)

    def lod_layer_decision_matrix_snapshot(self) -> dict:
        style_profile = getattr(self.args, "style_profile", "scientific")
        hydrology = {}
        for layer_id, spec in HYDROLOGY_SPECS.items():
            source = self.hydrology_lod_policy.decision(self.basemap_lod, layer_id)
            render_profile = self.hydrology_render_profile.decision(self.basemap_lod, layer_id)
            strictness = self.hydrology_strictness_policy.decision(
                self.basemap_lod,
                layer_id,
                source,
            )
            hydrology[layer_id] = {
                "visible": bool(self.layer_visible.get(layer_id, getattr(self.args, f"{spec['prefix']}_layer", True))),
                "source": source,
                "render_profile": render_profile,
                "strictness": strictness,
                "resolved_render_params": build_hydrology_render_params(
                    self.args,
                    layer_id,
                    spec,
                    render_profile,
                    style_profile,
                ),
            }
        boundaries = {}
        for layer_id, spec in BOUNDARY_SPECS.items():
            boundaries[layer_id] = {
                "visible": bool(self.layer_visible.get(layer_id, getattr(self.args, f"{spec['prefix']}_layer", True))),
                "source": self.boundary_lod_policy.decision(self.basemap_lod, layer_id),
                "resolved_render_params": build_boundary_render_params(
                    self.args,
                    layer_id,
                    spec,
                    style_profile,
                ),
            }
        ocean = self.ocean_conditions.decision(self.basemap_lod)
        return {
            "contract": "Per-layer LOD matrix for split-readiness: source decision, render params, visibility, and ocean sampling at the current basemap LOD.",
            "basemap_lod": self.basemap_lod,
            "layer_count": len(hydrology) + len(boundaries) + 1,
            "style_profile": style_profile,
            "hydrology_source_mode": getattr(self.args, "hydrology_source_mode", "lod"),
            "hydrology": hydrology,
            "boundaries": boundaries,
            "ocean": {
                "source": ocean,
                "spatial_sampling": ocean.get("spatial_sampling", {}),
                "material_control": {
                    "enabled": bool(getattr(self.args, "ocean_material", True)),
                    "wave_strength": float(getattr(self.args, "ocean_wave_strength", 0.0)),
                    "roughness": float(getattr(self.args, "ocean_roughness", 0.0)),
                    "foam": float(getattr(self.args, "ocean_foam", 0.0)),
                },
            },
            "next_module_target": "projection/lod_pipeline.py",
        }

    def lod_layer_decision_matrix_text(self) -> str:
        return json.dumps(self.lod_layer_decision_matrix_snapshot(), ensure_ascii=False, indent=2, default=str)

    def render_core_input_summary_text(self) -> str:
        basemap_decision = self.lod_manager.decision(
            self.current_km_per_pixel(),
            projection=getattr(self.args, "map_projection", "globe"),
            topo_source=getattr(self.args, "topo_source", None),
            topo_step=getattr(self.args, "topo_step", None),
        )
        ocean_decision = self.ocean_conditions.decision(self.basemap_lod)
        lines = [
            "Render core input summary",
            "",
            "Taichi globe inputs:",
            f"- topo raster: {getattr(self.topo, 'shape', None)}",
            f"- land mask: {getattr(self.land_mask, 'shape', None)}",
            f"- ice mask: {getattr(self.ice_mask, 'shape', None)}",
            f"- forest density: {getattr(self.forest_density, 'shape', None)}",
            f"- basemap provider: {basemap_decision['provider_id']}",
            f"- basemap renderer input: {basemap_decision['renderer_input']}",
            "",
            "Scalar render controls:",
            f"- sea_level_m: {getattr(self.args, 'sea_level_m', 0.0)}",
            f"- ocean provider: {ocean_decision['provider_id']}",
            f"- ocean renderer input: {ocean_decision['renderer_input']}",
            f"- ocean lod scale: {ocean_decision['lod_scale']}",
            "",
            "Vector overlays:",
            f"- hydrology LOD: {self.hydrology_lod_label()}",
            f"- hydrology layers: {', '.join(HYDROLOGY_SPECS.keys())}",
            f"- boundary layers: {', '.join(BOUNDARY_SPECS.keys())}",
            f"- boundary hover: {self.hover_boundary_hit}",
            f"- AIS projected/rendered: {self.visible_count:,}/{self.rendered_count:,}",
            f"- ADS-B projected/rendered: {self.aircraft_visible_count:,}/{self.aircraft_rendered_count:,}",
        ]
        return "\n".join(lines)

    def ocean_material_policy_text(self) -> str:
        state = self.ocean_conditions.sample(self.basemap_lod)
        return self.ocean_material_policy.status_text(state, self.basemap_lod)

    def projection_pipeline_text(self) -> str:
        return projection_pipeline_contract_text(
            getattr(self.args, "map_projection", "globe"),
            self.basemap_lod,
        )

    def renderer_data_contract_text(self) -> str:
        return renderer_data_contract_text()

    def mode_layer_policy_text(self) -> str:
        mode = getattr(self.args, "data_mode", "realtime")
        try:
            mode_title = self.mode_label(mode)
        except TypeError:
            mode_title = self.mode_label()
        lines = [
            "Mode layer policy",
            "",
            f"- active mode: {mode}",
            f"- mode label: {mode_title}",
            "",
            "Layer visibility by mode:",
        ]
        for layer_id in self.layer_order:
            allowed = self.layer_allowed_in_mode(layer_id)
            visible = bool(self.layer_visible.get(layer_id, True))
            state = "shown" if allowed and visible else "hidden"
            reason = "mode policy" if not allowed else "layer visibility"
            lines.append(f"- {layer_id}: {state} ({reason})")
        lines.extend(
            [
                "",
                "Rule: static mode hides realtime AIS/ADS-B/icon layers.",
                "Rule: timeseries mode should consume replay/cache providers, not live sockets.",
                "Rule: realtime mode may consume live feeders and volatile caches.",
            ]
        )
        return "\n".join(lines)

    def datashader_sampling_policy_text(self) -> str:
        policy = DatashaderSamplingPolicy()
        ais_obj = getattr(self, "current_ais", None)
        aircraft_obj = getattr(self, "current_aircraft", None)
        ais_records = len(ais_obj) if ais_obj is not None else 0
        aircraft_records = len(aircraft_obj) if aircraft_obj is not None else 0
        return policy.text(
            ais_records,
            aircraft_records,
            self.basemap_lod,
            getattr(self.args, "ais_sample_ratio", 1.0),
            getattr(self.args, "aircraft_sample_ratio", 1.0),
            getattr(self.args, "data_mode", "realtime"),
        )

    def ais_provider_decision(self) -> dict:
        source = "simulated"
        source_url = "simulated"
        if getattr(self.args, "ais_db_url", None):
            source = "database"
            source_url = getattr(self.args, "ais_db_url")
        elif getattr(self.args, "ais_url", None):
            source = "url"
            source_url = getattr(self.args, "ais_url")
        elif getattr(self.args, "ais_file", None):
            source = "file"
            source_url = getattr(self.args, "ais_file")
        manifest = build_provider_cache_manifest(
            f"ais.{source}",
            source_url=source_url,
            source_version="runtime",
            license_text="depends on selected AIS provider",
            lod=self.basemap_lod,
            cache_path=str(CACHE_DIR / "ais_feed_cache.json"),
            schema={"fields": ["lat", "lon", "mmsi", "sog", "cog", "heading", "timestamp"]},
            simplification={
                "sample_ratio": getattr(self.args, "ais_sample_ratio", 1.0),
                "max_age_minutes": getattr(self.args, "max_age_minutes", 1440.0),
            },
        )
        return {
            "source_mode": source,
            "provider_id": manifest["provider_id"],
            "source_url": manifest["source_url"],
            "rows_current": int(len(self.current_ais)),
            "rows_visible": int(self.visible_count),
            "rows_rendered": int(self.rendered_count),
            "color_by": getattr(self.args, "color_by", "speed"),
            "manifest": manifest,
        }

    def ais_provider_decision_text(self) -> str:
        decision = self.ais_provider_decision()
        lines = [
            "AIS provider decision",
            "",
            f"- source mode: {decision['source_mode']}",
            f"- provider: {decision['provider_id']}",
            f"- source: {decision['source_url']}",
            f"- cache: {decision['manifest']['cache_path']}",
            f"- current rows: {decision['rows_current']:,}",
            f"- visible rows: {decision['rows_visible']:,}",
            f"- rendered rows: {decision['rows_rendered']:,}",
            f"- color by: {decision['color_by']}",
            f"- manifest: {decision['manifest']}",
        ]
        return "\n".join(lines)

    def aircraft_provider_decision(self) -> dict:
        source = "simulated"
        source_url = "simulated"
        if getattr(self.args, "aircraft_db_url", None):
            source = "database"
            source_url = getattr(self.args, "aircraft_db_url")
        elif getattr(self.args, "aircraft_url", None):
            source = "url"
            source_url = getattr(self.args, "aircraft_url")
        elif getattr(self.args, "aircraft_file", None):
            source = "file"
            source_url = getattr(self.args, "aircraft_file")
        manifest = build_provider_cache_manifest(
            f"adsb.{source}",
            source_url=source_url,
            source_version="runtime",
            license_text="depends on selected ADS-B provider",
            lod=self.basemap_lod,
            cache_path=str(CACHE_DIR / "aircraft_feed_cache.json"),
            schema={"fields": ["lat", "lon", "icao24", "callsign", "altitude_m", "speed_kt", "heading", "timestamp"]},
            simplification={
                "sample_ratio": getattr(self.args, "aircraft_sample_ratio", 1.0),
                "max_age_minutes": getattr(self.args, "aircraft_max_age_minutes", 60.0),
            },
        )
        return {
            "source_mode": source,
            "provider_id": manifest["provider_id"],
            "source_url": manifest["source_url"],
            "rows_current": int(len(self.current_aircraft)),
            "rows_visible": int(self.aircraft_visible_count),
            "rows_rendered": int(self.aircraft_rendered_count),
            "color_by": getattr(self.args, "aircraft_color_by", "altitude"),
            "altitude_exaggeration": getattr(self.args, "aircraft_altitude_exaggeration", 35.0),
            "manifest": manifest,
        }

    def aircraft_provider_decision_text(self) -> str:
        decision = self.aircraft_provider_decision()
        lines = [
            "ADS-B provider decision",
            "",
            f"- source mode: {decision['source_mode']}",
            f"- provider: {decision['provider_id']}",
            f"- source: {decision['source_url']}",
            f"- cache: {decision['manifest']['cache_path']}",
            f"- current rows: {decision['rows_current']:,}",
            f"- visible rows: {decision['rows_visible']:,}",
            f"- rendered rows: {decision['rows_rendered']:,}",
            f"- color by: {decision['color_by']}",
            f"- altitude exaggeration: {decision['altitude_exaggeration']}",
            f"- manifest: {decision['manifest']}",
        ]
        return "\n".join(lines)

    def adaptive_quality_policy_text(self) -> str:
        policy = AdaptiveRenderQualityPolicy()
        render_ms = getattr(self, "last_render_ms", None)
        if render_ms is None:
            render_ms = getattr(self, "render_ms", None)
        return policy.text(
            self.width,
            self.height,
            render_ms,
            self.basemap_lod,
            getattr(self.args, "target_fps", 30.0),
        )

    def collect_provider_manifest_bundle(self) -> dict:
        km_per_pixel = self.current_km_per_pixel()
        basemap = self.lod_manager.decision(
            km_per_pixel,
            projection=getattr(self.args, "map_projection", "globe"),
            topo_source=getattr(self.args, "topo_source", None),
            topo_step=getattr(self.args, "topo_step", None),
        )
        manifests = list(provider_manifest_templates(self.basemap_lod))
        manifests.append(basemap["manifest"])
        for layer_id in HYDROLOGY_SPECS:
            manifests.append(self.hydrology_lod_policy.decision(self.basemap_lod, layer_id)["manifest"])
        for layer_id in BOUNDARY_SPECS:
            manifests.append(self.boundary_lod_policy.decision(self.basemap_lod, layer_id)["manifest"])
        manifests.append(self.ocean_conditions.decision(self.basemap_lod)["manifest"])
        manifests.append(self.ais_provider_decision()["manifest"])
        manifests.append(self.aircraft_provider_decision()["manifest"])
        bundle = {
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "purpose": "provider/cache manifest bundle for data_sources split and cache governance",
            "lod": self.basemap_lod,
            "projection": getattr(self.args, "map_projection", "globe"),
            "cache_root": str(CACHE_DIR),
            "manifest_count": 0,
            "manifests": dedupe_provider_manifests(manifests),
            "rules": [
                "providers own source_url/source_version/license/projection/cache_path/schema/simplification",
                "renderers consume normalized payloads, not source URLs",
                "Qt displays manifest summaries and triggers reloads only",
                "strict scientific datasets must pin source_version and attribution before publication",
            ],
        }
        bundle["manifest_count"] = len(bundle["manifests"])
        return bundle

    def provider_manifest_bundle_text(self) -> str:
        return json.dumps(self.collect_provider_manifest_bundle(), ensure_ascii=False, indent=2, default=str)

    def write_provider_manifest_bundle(self) -> str:
        path = CACHE_DIR / "taichi_earth_provider_manifest_bundle.json"
        path.write_text(self.provider_manifest_bundle_text(), encoding="utf-8")
        return str(path)

    def write_provider_manifest_bundle_text(self) -> str:
        path = self.write_provider_manifest_bundle()
        return f"Provider manifest bundle written to:\n{path}"

    def project_handoff_snapshot(self) -> dict:
        km_per_pixel = self.current_km_per_pixel()
        basemap = self.lod_manager.decision(
            km_per_pixel,
            projection=getattr(self.args, "map_projection", "globe"),
            topo_source=getattr(self.args, "topo_source", None),
            topo_step=getattr(self.args, "topo_step", None),
        )
        ocean = self.ocean_conditions.decision(self.basemap_lod)
        sampling_policy = DatashaderSamplingPolicy()
        quality_policy = AdaptiveRenderQualityPolicy()
        hydrology = {
            layer_id: {
                "provider": self.hydrology_lod_policy.decision(self.basemap_lod, layer_id),
                "render_profile": self.hydrology_render_profile.decision(self.basemap_lod, layer_id),
                "scientific_strictness": self.hydrology_strictness_policy.decision(
                    self.basemap_lod,
                    layer_id,
                    self.hydrology_lod_policy.decision(self.basemap_lod, layer_id),
                ),
            }
            for layer_id in HYDROLOGY_SPECS
        }
        boundaries = {
            layer_id: self.boundary_lod_policy.decision(self.basemap_lod, layer_id)
            for layer_id in BOUNDARY_SPECS
        }
        layer_state = {
            layer_id: {
                "label": self.layer_label(layer_id),
                "visible": bool(self.layer_visible.get(layer_id, True)),
                "allowed_in_mode": bool(self.layer_allowed_in_mode(layer_id)),
                "provider": LAYER_PROVIDER_REGISTRY.get(layer_id, {}).get("provider", ""),
                "renderer_input": LAYER_PROVIDER_REGISTRY.get(layer_id, {}).get("renderer_input", ""),
            }
            for layer_id in self.layer_order
        }
        snapshot = {
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "purpose": "handoff snapshot before splitting taichi_global_bathymetry.py into provider/projection/overlay/render/ui modules",
            "mode": getattr(self.args, "data_mode", "realtime"),
            "projection": getattr(self.args, "map_projection", "globe"),
            "canvas": {"width": int(self.width), "height": int(self.height)},
            "camera": {
                "yaw": float(self.yaw),
                "pitch": float(self.pitch),
                "zoom": float(self.zoom),
                "km_per_pixel": float(km_per_pixel),
                "lod": self.basemap_lod,
            },
            "runtime": {
                "last_render_ms": float(self.last_render_ms),
                "fps_estimate": float(1000.0 / max(float(self.last_render_ms), 1e-6)),
                "frame_index": int(self.frame_index),
                "taichi_backend": os.environ.get("TAICHI_ARCH", "runtime-selected"),
                "data_fetch_events": data_fetch_events_snapshot(),
            },
            "render_inputs": {
                "topography_shape": list(getattr(self.topo, "shape", [])),
                "land_mask_shape": list(getattr(self.land_mask, "shape", [])),
                "ice_mask_shape": list(getattr(self.ice_mask, "shape", [])),
                "forest_density_shape": list(getattr(self.forest_density, "shape", [])),
                "sea_level_m": float(getattr(self.args, "sea_level_m", 0.0)),
                "style_profile": resolve_style_profile(getattr(self.args, "style_profile", "scientific")),
                "style_renderer_entry": resolve_style_renderer_entry(getattr(self.args, "style_profile", "scientific")),
                "style_overlay_intent": resolve_style_overlay_intent(getattr(self.args, "style_profile", "scientific")),
                "datashader_style_cmaps": resolve_datashader_style_cmaps(getattr(self.args, "style_profile", "scientific")),
            },
            "provider_decisions": {
                "basemap": basemap,
                "hydrology": hydrology,
                "hydrology_control": self.hydrology_control_snapshot(),
                "hydrology_basic_readiness": self.hydrology_basic_readiness_matrix_snapshot(),
                "boundaries": boundaries,
                "ocean": ocean,
                "ocean_normalization_report": self.ocean_conditions.last_normalization_report,
                "ocean_spatial_sampling": self.ocean_conditions.last_spatial_sampling_decision,
                "ocean_material_control": self.ocean_material_control_snapshot(),
                "ocean_material_taichi_port": self.ocean_material_taichi_port_snapshot(),
                "ais": self.ais_provider_decision(),
                "adsb": self.aircraft_provider_decision(),
            },
            "lod_hook_pipeline": self.lod_hook_pipeline_snapshot(),
            "overlay_counts": {
                "ais": {
                    "current": int(len(self.current_ais)),
                    "visible": int(self.visible_count),
                    "rendered": int(self.rendered_count),
                },
                "adsb": {
                    "current": int(len(self.current_aircraft)),
                    "visible": int(self.aircraft_visible_count),
                    "rendered": int(self.aircraft_rendered_count),
                },
                "hydrology_lines": {
                    layer_id: int(len(getattr(overlay, "lines", [])))
                    for layer_id, overlay in self.hydrology_overlays.items()
                },
                "boundary_lines": {
                    layer_id: int(len(getattr(overlay, "lines", [])))
                    for layer_id, overlay in self.boundary_overlays.items()
                },
            },
            "policies": {
                "datashader_ais": sampling_policy.decision(
                    len(self.current_ais),
                    self.basemap_lod,
                    getattr(self.args, "ais_sample_ratio", 1.0),
                    getattr(self.args, "data_mode", "realtime") == "realtime",
                ),
                "datashader_adsb": sampling_policy.decision(
                    len(self.current_aircraft),
                    self.basemap_lod,
                    getattr(self.args, "aircraft_sample_ratio", 1.0),
                    getattr(self.args, "data_mode", "realtime") == "realtime",
                ),
                "adaptive_quality": quality_policy.decision(
                    self.width,
                    self.height,
                    self.last_render_ms,
                    self.basemap_lod,
                    getattr(self.args, "target_fps", 30.0),
                ),
                "render_budget": self.render_budget_decision(),
                "point_overlay_budget": dict(self.point_overlay_budget_last),
                "vector_overlay_cache": {
                    "entries": len(self.vector_overlay_cache),
                    "limit": self._vector_cache_limit(),
                    "hits": self.vector_overlay_cache_hits,
                    "misses": self.vector_overlay_cache_misses,
                    "deferred": self.vector_overlay_cache_deferred,
                },
                "layer_state": layer_state,
            },
            "module_split": MODULE_SPLIT_BLUEPRINT,
            "symbol_extraction_map": SYMBOL_EXTRACTION_MAP,
            "module_boundaries": DECOUPLING_MODULE_BOUNDARIES,
            "runtime_configuration_contract": RUNTIME_CONFIGURATION_CONTRACT,
            "project_goal_milestones": project_goal_milestones_snapshot(),
            "decoupling_extraction_units": decoupling_extraction_units_snapshot(),
            "provider_manifests_module_api": provider_manifests_module_api_snapshot(),
            "hydrology_provider_module_api": hydrology_provider_module_api_snapshot(),
            "hydrology_provider_extraction_readiness_packet": hydrology_provider_extraction_readiness_packet_snapshot(),
            "hydrology_dirty_reload_contract": self.hydrology_dirty_reload_contract_snapshot(),
            "ocean_condition_provider_module_api": ocean_condition_provider_module_api_snapshot(),
            "ocean_condition_provider_extraction_readiness_packet": ocean_condition_provider_extraction_readiness_packet_snapshot(),
            "render_core_ocean_material_module_api": render_core_ocean_material_module_api_snapshot(),
            "render_core_ocean_material_extraction_readiness_packet": render_core_ocean_material_extraction_readiness_packet_snapshot(),
            "vector_lines_module_api": vector_lines_module_api_snapshot(),
            "vector_lines_extraction_readiness_packet": vector_lines_extraction_readiness_packet_snapshot(),
            "lod_pipeline_module_api": lod_pipeline_module_api_snapshot(),
            "lod_pipeline_extraction_readiness_packet": lod_pipeline_extraction_readiness_packet_snapshot(),
            "style_profiles_module_api": style_profiles_module_api_snapshot(),
            "style_profiles_extraction_readiness_packet": style_profiles_extraction_readiness_packet_snapshot(),
            "datashader_points_module_api": datashader_points_module_api_snapshot(),
            "datashader_points_extraction_readiness_packet": datashader_points_extraction_readiness_packet_snapshot(),
            "module_api_registry": module_api_registry_snapshot(),
            "pre_extraction_readiness_audit": pre_extraction_readiness_audit_snapshot(),
            "first_extraction_execution_plan": first_extraction_execution_plan_snapshot(),
            "first_extraction_readiness_packet": first_extraction_readiness_packet_snapshot(),
            "extraction_readiness_packet_index": extraction_readiness_packet_index_snapshot(),
            "active_goal_extraction_seam_matrix": active_goal_extraction_seam_matrix_snapshot(),
            "cache_governance_matrix": cache_governance_matrix_snapshot(),
            "module_import_boundary_matrix": module_import_boundary_matrix_snapshot(),
            "module_contract_coverage": module_contract_coverage_snapshot(),
            "validation_and_rollback_plan": validation_and_rollback_plan_snapshot(),
            "pre_validation_evidence_plan": pre_validation_evidence_plan_snapshot(),
            "unverified_risk_register": unverified_risk_register_snapshot(),
            "active_goal_readiness_gate": self.active_goal_readiness_gate_snapshot(),
            "active_goal_summary": self.active_goal_summary_snapshot(),
            "active_goal_known_issue_matrix": active_goal_known_issue_matrix_snapshot(),
            "active_goal_next_action_queue": active_goal_next_action_queue_snapshot(),
            "lod_layer_decision_matrix": self.lod_layer_decision_matrix_snapshot(),
            "lod_invalidation_contract": self.lod_invalidation_contract_snapshot(),
            "ocean_material_taichi_port": self.ocean_material_taichi_port_snapshot(),
            "qt_controller_facade_api": qt_controller_facade_api_snapshot(),
            "qt_controller_facade_coverage": qt_controller_facade_coverage_snapshot(self),
            "qt_controller_facade_extraction_readiness_packet": qt_controller_facade_extraction_readiness_packet_snapshot(),
            "qt_ui_coupling_cleanup_status": qt_ui_coupling_cleanup_status_snapshot(),
            "qt_main_window_module_api": qt_main_window_module_api_snapshot(),
            "qt_main_window_extraction_readiness_packet": qt_main_window_extraction_readiness_packet_snapshot(),
            "active_goal_control_bundle": self.active_goal_control_bundle_snapshot(),
            "extraction_gates": DECOUPLING_EXTRACTION_GATES,
            "extraction_audit": self.decoupling_extraction_audit(),
            "provider_manifest_bundle": self.collect_provider_manifest_bundle(),
            "next_split_order": [
                "data_sources constants/providers and manifest builders",
                "projection helpers and LOD decisions",
                "datashader point/vector overlays",
                "taichi render core once scalar/material inputs are final",
                "qt_ui orchestration shell last",
            ],
            "suggested_snapshot_path": str(CACHE_DIR / "taichi_earth_handoff_snapshot.json"),
        }
        return snapshot

    def project_handoff_snapshot_text(self) -> str:
        return json.dumps(self.project_handoff_snapshot(), ensure_ascii=False, indent=2, default=str)

    def write_project_handoff_snapshot(self) -> str:
        path = CACHE_DIR / "taichi_earth_handoff_snapshot.json"
        path.write_text(self.project_handoff_snapshot_text(), encoding="utf-8")
        return str(path)

    def write_project_handoff_snapshot_text(self) -> str:
        path = self.write_project_handoff_snapshot()
        return f"Project handoff snapshot written to:\n{path}"

    def set_data_mode(self, mode: str) -> None:
        mode = str(mode or "realtime")
        if mode not in {"static", "timeseries", "realtime"}:
            mode = "realtime"
        self.args.data_mode = mode
        self.overlay_dirty = True
        self.hydrology_dirty = True
        self.boundary_dirty = True
        self.selected_vehicle = None

    def set_flight_speed_deg(self, value: float) -> None:
        self.args.flight_speed_deg = max(0.05, float(value))

    def runtime_status_text(self) -> str:
        fps = 1000.0 / max(float(self.last_render_ms), 1e-6)
        budget = self.render_budget_decision()
        lines = [
            "Runtime status",
            "",
            f"- mode: {self.mode_label()}",
            f"- canvas: {self.width} x {self.height}",
            f"- render: {self.last_render_ms:.2f} ms ({fps:.2f} fps)",
            f"- LOD: {self.basemap_lod_label()}",
            f"- AIS total: {self.total_count:,}",
            f"- AIS visible: {self.visible_count:,}",
            f"- AIS rendered: {self.rendered_count:,}",
            f"- ADS-B total: {self.aircraft_total_count:,}",
            f"- ADS-B visible: {self.aircraft_visible_count:,}",
            f"- ADS-B rendered: {self.aircraft_rendered_count:,}",
            f"- sampling: AIS={getattr(self.args, 'ais_sample_ratio', 1.0):.2f}, ADS-B={getattr(self.args, 'aircraft_sample_ratio', 1.0):.2f}, adaptive={bool(getattr(self.args, 'adaptive_sampling', True))}",
            f"- point budget: AIS cap={self.point_overlay_budget_last.get('ais', {}).get('sample_ratio_cap', 1.0):.2f} reason={self.point_overlay_budget_last.get('ais', {}).get('reason', 'unknown')}",
            f"- point budget: ADS-B cap={self.point_overlay_budget_last.get('aircraft', {}).get('sample_ratio_cap', 1.0):.2f} reason={self.point_overlay_budget_last.get('aircraft', {}).get('reason', 'unknown')}",
            f"- render budget: {budget['state']} target={budget['target_ms']:.1f} ms pressure={budget['pressure']:.2f}x",
            f"- deferred vectors: {budget['defer_vector_overlays']} static-cache={budget['prefer_static_cache']}",
            f"- vector cache: hits={self.vector_overlay_cache_hits:,} misses={self.vector_overlay_cache_misses:,} deferred={self.vector_overlay_cache_deferred:,} entries={len(self.vector_overlay_cache)} stride={budget['vector_point_stride']}",
            f"- ocean: {self.ocean_conditions.status_text()}",
        ]
        return "\n".join(lines)

    def refresh_ais_if_due(self, force: bool = False) -> None:
        now = time.time()
        if not force and now - self.last_ais_read < self.args.refresh:
            return

        try:
            ais = self.ais_source.read()
            ais = filter_recent(ais, self.args.max_age_minutes)
        except Exception as exc:
            print(f"AIS read failed: {exc}")
            ais = pd.DataFrame(columns=["lon", "lat"])

        self.current_ais = ais
        self.total_count = len(ais)
        self.last_ais_read = now
        self.overlay_dirty = True

    def refresh_aircraft_if_due(self, force: bool = False) -> None:
        if not self.layer_allowed_in_mode("aircraft") or not self.layer_visible.get("aircraft", False):
            return
        now = time.time()
        refresh = max(0.1, float(getattr(self.args, "aircraft_refresh", getattr(self.args, "refresh", 2.0))))
        if not force and now - self.last_aircraft_read < refresh:
            return
        try:
            aircraft = self.aircraft_source.read()
            aircraft = filter_recent(aircraft, self.args.aircraft_max_age_minutes)
        except Exception as exc:
            print(f"ADS-B read failed: {exc}")
            aircraft = pd.DataFrame(columns=["lon", "lat"])
        self.current_aircraft = aircraft
        self.aircraft_total_count = len(aircraft)
        self.last_aircraft_read = now
        self.overlay_dirty = True

    def render_if_needed(self, force: bool = False) -> np.ndarray | None:
        start = time.time()
        self.refresh_ais_if_due(force=force)
        self.refresh_aircraft_if_due(force=force)
        self.update_basemap_lod()

        changed = force or self.globe_dirty or self.overlay_dirty
        if self.hover_boundary_hit.get("layer_id"):
            current_bucket = int((time.time() * 12.0) % 12)
            if current_bucket != self.boundary_hover_phase_bucket:
                self.boundary_hover_phase_bucket = current_bucket
                changed = True
                self.boundary_hover_dirty = True
                self.boundary_dirty = True
        if not changed:
            return None

        if force or self.globe_dirty:
            sun_x, sun_y, sun_z = compute_sun_direction()
            ocean_state = self.ocean_conditions.sample(self.basemap_lod)
            ocean_material = self.ocean_material_policy.resolve(ocean_state, self.basemap_lod)
            self.globe.render(
                self.yaw,
                self.pitch,
                self.zoom,
                sun_x,
                sun_y,
                sun_z,
                int(self.flip_longitude),
                int(self.flip_latitude),
                self.args.sea_level_m,
                int(getattr(self.args, "ice_layer", True)),
                float(getattr(self.args, "ice_opacity", 0.82)),
                float(getattr(self.args, "ice_specular", 0.35)),
                float(getattr(self.args, "ice_blue", 0.18)),
                int(getattr(self.args, "forest_layer", True)),
                float(getattr(self.args, "forest_opacity", 0.58)),
                float(getattr(self.args, "forest_green", 0.72)),
                float(getattr(self.args, "canopy_shadow", 0.45)),
                int(ocean_material["enabled"]),
                float(ocean_material["wave_strength"]),
                float(ocean_material["roughness"]),
                float(ocean_material["foam"]),
                float(time.time() % 100000.0),
            )
            if self.globe.num_stars:
                self.globe.render_stars(self.yaw, self.pitch, self.zoom)
            self.globe_rgba = self.globe.to_rgba_u8()
            self.globe_mask = self.globe.mask_u8()
            self.globe_dirty = False
            self.boundary_base_dirty = True
            self.boundary_hover_phase_bucket = -1

        if force or self.overlay_dirty or self.hydrology_dirty or self.boundary_dirty or self.boundary_hover_dirty:
            budget_decision = self.render_budget_decision()
            defer_vector_overlays = bool(budget_decision.get("defer_vector_overlays", False)) and not force
            style_profile = getattr(self.args, "style_profile", "scientific")
            self.overlay_renderer.set_style_profile(style_profile)
            self.aircraft_overlay_renderer.set_style_profile(style_profile)
            self.current_projected = project_ais_to_screen(
                self.current_ais,
                self.yaw,
                self.pitch,
                self.zoom,
                self.width,
                self.height,
                self.flip_longitude,
                self.flip_latitude,
                self.args.ais_horizon_eps,
            )
            self.visible_count = len(self.current_projected)
            self.current_sampled_projected = self._sample_projected_frame(self.current_projected, "ais")
            self.rendered_count = len(self.current_sampled_projected)
            self.overlay_rgba = mask_overlay_to_globe(
                self.overlay_renderer.render(self.current_sampled_projected),
                self.globe_mask,
            )
            if self.layer_allowed_in_mode("aircraft") and self.layer_visible.get("aircraft", False):
                self.current_aircraft_projected = project_aircraft_to_screen(
                    self.current_aircraft,
                    self.yaw,
                    self.pitch,
                    self.zoom,
                    self.width,
                    self.height,
                    self.flip_longitude,
                    self.flip_latitude,
                    self.args.aircraft_horizon_eps,
                    self.args.aircraft_altitude_exaggeration,
                )
                self.aircraft_visible_count = len(self.current_aircraft_projected)
                self.current_aircraft_sampled_projected = self._sample_projected_frame(self.current_aircraft_projected, "aircraft")
                self.aircraft_rendered_count = len(self.current_aircraft_sampled_projected)
                self.aircraft_overlay_rgba = mask_overlay_to_globe(
                    self.aircraft_overlay_renderer.render(self.current_aircraft_sampled_projected),
                    self.globe_mask,
                )
            else:
                self.current_aircraft_projected = pd.DataFrame(columns=["screen_x", "screen_y"])
                self.current_aircraft_sampled_projected = pd.DataFrame(columns=["screen_x", "screen_y"])
                self.aircraft_visible_count = 0
                self.aircraft_rendered_count = 0
                self.aircraft_overlay_rgba = np.zeros_like(self.globe_rgba)
            if self.layer_visible.get("pins", True) and self.pin_records:
                self.current_pin_projections = project_pins_to_screen(
                    self.pin_records,
                    yaw=self.yaw,
                    pitch=self.pitch,
                    zoom=self.zoom,
                    width=self.width,
                    height=self.height,
                    flip_longitude=self.flip_longitude,
                    flip_latitude=self.flip_latitude,
                    horizon_eps=float(getattr(self.args, "pin_horizon_eps", 0.006)),
                )
                self.pin_visible_count = sum(1 for pin in self.current_pin_projections if pin.get("visible") is True)
                self.pin_overlay_rgba = mask_overlay_to_globe(
                    render_pin_overlay(
                        self.width,
                        self.height,
                        self.current_pin_projections,
                        int(getattr(self.args, "pin_size", 9)),
                        self.selected_pin_id,
                        getattr(self.args, "style_profile", "scientific"),
                        getattr(self.args, "pin_label_mode", "auto"),
                        int(getattr(self.args, "pin_label_min_priority", 50)),
                    ),
                    self.globe_mask,
                )
            else:
                self.current_pin_projections = []
                self.pin_visible_count = 0
                self.pin_overlay_rgba = np.zeros_like(self.globe_rgba)
            if defer_vector_overlays:
                self.vector_overlay_cache_deferred += 1
                self.hydrology_dirty = True
                self.boundary_dirty = True
                self.boundary_hover_dirty = bool(getattr(self, "hover_boundary_hit", {}).get("layer_id"))
            else:
                self._render_hydrology_if_needed(force=force)
                self._render_boundaries_if_needed(force=force)
            self.overlay_dirty = False

        self.frame_rgba = alpha_compose(self.globe_rgba, self.lake_overlay_rgba)
        self.frame_rgba = alpha_compose(self.frame_rgba, self.river_overlay_rgba)
        self.frame_rgba = alpha_compose(self.frame_rgba, self.boundary_overlay_rgba)
        self.frame_rgba = alpha_compose(self.frame_rgba, self.overlay_rgba)
        self.frame_rgba = alpha_compose(self.frame_rgba, self.aircraft_overlay_rgba)
        self.frame_rgba = alpha_compose(self.frame_rgba, self.pin_overlay_rgba)
        self.frame_rgba = apply_style_profile(self.frame_rgba, getattr(self.args, "style_profile", "scientific"))
        self.last_render_ms = (time.time() - start) * 1000.0
        if self.output_path and (getattr(self.args, "once", False) or getattr(self.args, "headless", False)):
            from PIL import Image

            Image.fromarray(self.frame_rgba, mode="RGBA").save(self.output_path)
        self.frame_index += 1
        return self.frame_rgba

    def title(self) -> str:
        fps = 1000.0 / max(self.last_render_ms, 1e-6)
        zoom_display = 1.0 / self.zoom
        return (
            f"AIS Globe | visible {self.visible_count:,}/{self.total_count:,} | rendered {self.rendered_count:,} | "
            f"ADS-B {self.aircraft_visible_count:,}/{self.aircraft_total_count:,} rendered {self.aircraft_rendered_count:,} | "
            f"render {self.last_render_ms:.0f} ms ({fps:.1f} fps) | zoom {zoom_display:.2f}x | "
            f"flip lon={int(self.flip_longitude)} lat={int(self.flip_latitude)}"
        )


class VisPyHybridViewer:
    def __init__(self, controller: HybridRenderController, backend: str):
        vispy.use(app=backend)
        from vispy import app, scene

        self.app = app
        self.scene = scene
        self.controller = controller
        initial = controller.render_if_needed(force=True)

        self.canvas = scene.SceneCanvas(
            keys="interactive",
            size=(controller.width, controller.height),
            show=True,
            bgcolor="black",
            title=controller.title(),
        )
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = scene.cameras.PanZoomCamera(aspect=1, interactive=False)
        self.image = scene.visuals.Image(
            initial,
            interpolation="nearest",
            parent=self.view.scene,
        )
        self.hud = scene.visuals.Text(
            controller.title(),
            color=(1.0, 1.0, 1.0, 1.0),
            font_size=14,
            anchor_x="left",
            anchor_y="top",
            pos=(12, 18),
            parent=self.view.scene,
        )
        self.view.camera.set_range(x=(0, controller.width), y=(controller.height, 0), margin=0)

        self.dragging = False
        self.last_pos = None
        self.canvas.events.mouse_press.connect(self.on_mouse_press)
        self.canvas.events.mouse_release.connect(self.on_mouse_release)
        self.canvas.events.mouse_move.connect(self.on_mouse_move)
        self.canvas.events.mouse_wheel.connect(self.on_mouse_wheel)
        self.canvas.events.key_press.connect(self.on_key_press)
        self.canvas.events.key_release.connect(self.on_key_release)
        self.timer = app.Timer(interval=1.0 / 30.0, connect=self.on_timer, start=True)

    def on_timer(self, _event) -> None:
        frame = self.controller.render_if_needed(force=False)
        if frame is not None:
            self.image.set_data(frame)
            self.canvas.title = self.controller.title()
            self.hud.text = self.controller.title()
            self.canvas.update()

    def on_mouse_press(self, event) -> None:
        if event.button == 1:
            self.dragging = True
            self.last_pos = event.pos

    def on_mouse_release(self, event) -> None:
        if event.button == 1:
            self.controller.set_interaction_active(False)
            self.dragging = False
            self.last_pos = None

    def on_mouse_move(self, event) -> None:
        if not self.dragging or self.last_pos is None:
            return
        dx = event.pos[0] - self.last_pos[0]
        dy = event.pos[1] - self.last_pos[1]
        self.controller.set_interaction_active(True)
        self.controller.rotate(-dx, -dy)
        self.last_pos = event.pos

    def on_mouse_wheel(self, event) -> None:
        delta = event.delta[1]
        self.controller.apply_zoom(0.88 ** delta)

    def on_key_press(self, event) -> None:
        key = event.key.name if hasattr(event.key, "name") else str(event.key)
        if key in {"Escape", "Esc"}:
            self.canvas.close()
        elif key in {"R", "r"}:
            self.controller.reset_view()
        elif key in {"M", "m"}:
            self.controller.toggle_longitude_flip()
        elif key in {"N", "n"}:
            self.controller.toggle_latitude_flip()
        elif key in {"Up", "W", "w", "+", "="}:
            self.controller.apply_zoom(0.92)
        elif key in {"Down", "S", "s", "-", "_"}:
            self.controller.apply_zoom(1.08)

    def run(self) -> None:
        self.app.run()


class QtHybridWindow:
    def __init__(self, controller: HybridRenderController):
        vispy.use(app="pyqt6")
        from PyQt6 import QtCore, QtWidgets
        from vispy import scene

        self.QtCore = QtCore
        self.QtWidgets = QtWidgets
        self.scene = scene
        self.controller = controller
        self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        self.data_mode = str(getattr(controller.args, "data_mode", "realtime"))
        self.layer_groups_collapsed: set[str] = set()
        self.locked_layers: set[str] = set()
        self.layer_group_defs = [
            ("base", "Base map", ["globe", "ice", "forest", "contours", "lakes", "rivers"]),
            ("boundaries", "Boundaries", ["borders", "territorial_sea", "eez", "high_seas"]),
            ("realtime", "Realtime feeds", ["ais", "aircraft", "vehicle_icons", "clouds"]),
            ("ui", "UI overlays", ["scale"]),
        ]
        self.timeline_duration_seconds = 24 * 3600
        self.timeline_visible_until = 0.0
        self.timeline_playing = False
        self.timeline_speed = 1.0
        self.timeline_last_tick = time.time()
        self.dragging_scale_bar = False
        self.scale_bar_drag_offset = (0.0, 0.0)
        self.mouse_down_pos = None
        self.keys_down: set[str] = set()
        self.fps_recorder = FPSRecorder(getattr(controller.args, "fps_log", None))
        self.layer_dialogs = []

        initial = controller.render_if_needed(force=True)
        self.window = QtWidgets.QMainWindow()
        self.window.setWindowTitle("AIS Globe Control Center")
        self.window.resize(controller.width + 360, controller.height + 40)

        root = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(root)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        self.window.setCentralWidget(root)

        self.canvas = scene.SceneCanvas(
            keys="interactive",
            size=(controller.width, controller.height),
            show=False,
            bgcolor="black",
        )
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = scene.cameras.PanZoomCamera(aspect=1, interactive=False)
        self.image = scene.visuals.Image(initial, interpolation="nearest", parent=self.view.scene)
        self.hud = scene.visuals.Text(
            controller.title(),
            color=(1.0, 1.0, 1.0, 1.0),
            font_size=14,
            anchor_x="left",
            anchor_y="top",
            pos=(12, 18),
            parent=self.view.scene,
        )
        self.view.camera.set_range(x=(0, controller.width), y=(controller.height, 0), margin=0)
        self.scale_shadow = scene.visuals.Line(parent=self.view.scene)
        self.scale_line = scene.visuals.Line(parent=self.view.scene)
        self.scale_left_tick = scene.visuals.Line(parent=self.view.scene)
        self.scale_right_tick = scene.visuals.Line(parent=self.view.scene)
        self.scale_text = scene.visuals.Text(
            "",
            color=(1.0, 1.0, 1.0, 1.0),
            font_size=12,
            anchor_x="left",
            anchor_y="bottom",
            parent=self.view.scene,
        )
        self.scale_visuals = [
            self.scale_shadow,
            self.scale_line,
            self.scale_left_tick,
            self.scale_right_tick,
            self.scale_text,
        ]
        self.update_scale_bar_visuals()
        layout.addWidget(self.canvas.native, stretch=1)

        panel = self._build_panel()
        self.side_panel = panel
        self.drawer_button = QtWidgets.QToolButton()
        self.drawer_button.setText("<")
        self.drawer_button.clicked.connect(self.toggle_side_panel)
        layout.addWidget(self.drawer_button, stretch=0)
        layout.addWidget(panel, stretch=0)
        try:
            self.window.addToolBar(self._build_mode_toolbar())
            self.layer_dock = self._build_layer_dock()
            self.window.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.layer_dock)
            self.timeline_bar = self._build_timeline_bar()
            self.window.addDockWidget(QtCore.Qt.DockWidgetArea.BottomDockWidgetArea, self.timeline_bar)
            if self.data_mode != "timeseries":
                self.timeline_bar.hide()
        except Exception as exc:
            print(f"Qt dock/toolbar setup failed: {exc}")

        self.dragging = False
        self.last_pos = None
        self.canvas.events.mouse_press.connect(self.on_mouse_press)
        self.canvas.events.mouse_release.connect(self.on_mouse_release)
        self.canvas.events.mouse_move.connect(self.on_mouse_move)
        self.canvas.events.mouse_wheel.connect(self.on_mouse_wheel)
        self.canvas.events.key_press.connect(self.on_key_press)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(33)

    def _build_panel(self):
        QtCore = self.QtCore
        QtWidgets = self.QtWidgets
        panel = QtWidgets.QWidget()
        panel.setFixedWidth(390)
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self.status_label = QtWidgets.QLabel(self._status_text())
        self.status_label.setWordWrap(True)
        layout.addWidget(self._group("\u72c0\u614b", [self.status_label]))

        dock_hint = QtWidgets.QLabel("Layer panel behaves like a small Photoshop-style dock: drag to reorder, use eye/lock buttons, double-click a layer for settings.")
        dock_hint.setWordWrap(True)
        layout.addWidget(self._group("\u5716\u5c64\u8aaa\u660e", [dock_hint]))

        self.selection_label = QtWidgets.QLabel(self.controller.selected_info_text())
        self.selection_label.setWordWrap(True)
        layout.addWidget(self._group("\u9078\u53d6\u8cc7\u8a0a", [self.selection_label]))

        self.data_fetch_label = QtWidgets.QLabel("資料快取尚未開始")
        self.data_fetch_label.setWordWrap(True)
        self.data_fetch_progress = QtWidgets.QProgressBar()
        self.data_fetch_progress.setRange(0, 100)
        self.data_fetch_progress.setValue(0)
        self.data_fetch_progress.setTextVisible(True)
        layout.addWidget(self._group("資料下載 / 快取", [self.data_fetch_label, self.data_fetch_progress]))

        self.icons_checkbox = QtWidgets.QCheckBox("\u986f\u793a\u53ef\u9ede\u9078\u8f09\u5177 icon")
        self.icons_checkbox.setChecked(bool(self.controller.args.vehicle_icons))
        self.icons_checkbox.stateChanged.connect(self.on_vehicle_icons_changed)
        self.icon_max_spin = QtWidgets.QSpinBox()
        self.icon_max_spin.setRange(0, 50000)
        self.icon_max_spin.setSingleStep(100)
        self.icon_max_spin.setValue(int(self.controller.args.icon_max_count))
        self.icon_max_spin.valueChanged.connect(self.controller.set_icon_max_count)
        self.pick_radius_spin = QtWidgets.QDoubleSpinBox()
        self.pick_radius_spin.setRange(2.0, 80.0)
        self.pick_radius_spin.setSingleStep(1.0)
        self.pick_radius_spin.setValue(float(self.controller.args.icon_pick_radius))
        self.pick_radius_spin.valueChanged.connect(self.controller.set_icon_pick_radius)
        layout.addWidget(self._form_group("\u8f09\u5177 icon", [("\u555f\u7528", self.icons_checkbox), ("\u6700\u5927 icon \u6578", self.icon_max_spin), ("\u9ede\u9078\u534a\u5f91 px", self.pick_radius_spin)]))

        self.ais_sample_spin = QtWidgets.QDoubleSpinBox()
        self.ais_sample_spin.setRange(0.01, 1.0)
        self.ais_sample_spin.setSingleStep(0.05)
        self.ais_sample_spin.setDecimals(2)
        self.ais_sample_spin.setValue(float(self.controller.args.ais_sample_ratio))
        self.ais_sample_spin.valueChanged.connect(self.controller.set_ais_sample_ratio)
        self.aircraft_sample_spin = QtWidgets.QDoubleSpinBox()
        self.aircraft_sample_spin.setRange(0.01, 1.0)
        self.aircraft_sample_spin.setSingleStep(0.05)
        self.aircraft_sample_spin.setDecimals(2)
        self.aircraft_sample_spin.setValue(float(self.controller.args.aircraft_sample_ratio))
        self.aircraft_sample_spin.valueChanged.connect(self.controller.set_aircraft_sample_ratio)
        self.adaptive_sampling_checkbox = QtWidgets.QCheckBox("\u81ea\u9069\u61c9\u63a1\u6a23 / FPS \u4fdd\u8b77")
        self.adaptive_sampling_checkbox.setChecked(bool(self.controller.args.adaptive_sampling))
        self.adaptive_sampling_checkbox.stateChanged.connect(lambda state: self.controller.set_adaptive_sampling(state == self.QtCore.Qt.CheckState.Checked.value))
        self.target_fps_spin = QtWidgets.QDoubleSpinBox()
        self.target_fps_spin.setRange(1.0, 240.0)
        self.target_fps_spin.setSingleStep(1.0)
        self.target_fps_spin.setValue(float(self.controller.args.target_fps))
        self.target_fps_spin.valueChanged.connect(self.controller.set_target_fps)
        self.min_sample_spin = QtWidgets.QDoubleSpinBox()
        self.min_sample_spin.setRange(0.01, 1.0)
        self.min_sample_spin.setSingleStep(0.01)
        self.min_sample_spin.setDecimals(2)
        self.min_sample_spin.setValue(float(self.controller.args.min_sample_ratio))
        self.min_sample_spin.valueChanged.connect(self.controller.set_min_sample_ratio)
        layout.addWidget(self._form_group("\u6548\u80fd", [("AIS \u63a1\u6a23", self.ais_sample_spin), ("ADS-B \u63a1\u6a23", self.aircraft_sample_spin), ("\u81ea\u9069\u61c9", self.adaptive_sampling_checkbox), ("\u76ee\u6a19 FPS", self.target_fps_spin), ("\u6700\u5c0f\u63a1\u6a23", self.min_sample_spin)]))

        self.contours_checkbox = QtWidgets.QCheckBox("\u986f\u793a\u5730\u5f62\u7b49\u9ad8\u7dda")
        self.contours_checkbox.setChecked(bool(self.controller.args.terrain_contours))
        self.contours_checkbox.stateChanged.connect(self.on_terrain_contours_changed)
        self.contour_interval_spin = QtWidgets.QDoubleSpinBox()
        self.contour_interval_spin.setRange(50.0, 5000.0)
        self.contour_interval_spin.setSingleStep(100.0)
        self.contour_interval_spin.setValue(float(self.controller.args.contour_interval_m))
        self.contour_interval_spin.valueChanged.connect(self.controller.set_contour_interval)
        self.contour_width_spin = QtWidgets.QDoubleSpinBox()
        self.contour_width_spin.setRange(1.0, 250.0)
        self.contour_width_spin.setSingleStep(5.0)
        self.contour_width_spin.setValue(float(self.controller.args.contour_line_width_m))
        self.contour_width_spin.valueChanged.connect(self.controller.set_contour_line_width)
        self.contour_opacity_spin = QtWidgets.QDoubleSpinBox()
        self.contour_opacity_spin.setRange(0.0, 1.0)
        self.contour_opacity_spin.setSingleStep(0.05)
        self.contour_opacity_spin.setValue(float(self.controller.args.contour_opacity))
        self.contour_opacity_spin.valueChanged.connect(self.controller.set_contour_opacity)
        layout.addWidget(self._form_group("\u5730\u5f62\u7b49\u9ad8\u7dda", [("\u555f\u7528", self.contours_checkbox), ("\u9593\u8ddd m", self.contour_interval_spin), ("\u7dda\u5bec m", self.contour_width_spin), ("\u900f\u660e\u5ea6", self.contour_opacity_spin)]))

        self.legend_label = QtWidgets.QLabel("AIS \u901f\u5ea6\uff1a\u9752\u8272=\u6162\u901f\uff0c\u7da0\u8272=\u4e2d\u901f\uff0c\u9ec3/\u7d05=\u9ad8\u901f\u3002ADS-B \u9ad8\u5ea6\uff1a\u85cd\u8272=\u4f4e\u7a7a\uff0c\u7d2b\u8272=\u4e2d\u9ad8\u7a7a\uff0c\u9ec3\u8272=\u9ad8\u7a7a\u3002")
        self.legend_label.setWordWrap(True)
        self.legend_bar = QtWidgets.QLabel()
        self.legend_bar.setFixedHeight(18)
        self.legend_bar.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #38e8ff, stop:0.35 #56f57a, stop:0.65 #ffe05d, stop:0.82 #ff873d, stop:1 #ff2d55); border: 1px solid #555;")
        layout.addWidget(self._group("\u5716\u4f8b", [self.legend_bar, self.legend_label]))

        self.color_combo = QtWidgets.QComboBox()
        self.color_combo.addItem("speed", "speed")
        self.color_combo.addItem("density", "density")
        color_index = self.color_combo.findData(self.controller.args.color_by)
        if color_index >= 0:
            self.color_combo.setCurrentIndex(color_index)
        self.color_combo.currentIndexChanged.connect(self.on_color_mode)
        self.point_slider = self._slider(1, 8, self.controller.args.point_px, self.on_point_px)
        self.refresh_spin = QtWidgets.QDoubleSpinBox()
        self.refresh_spin.setRange(0.2, 60.0)
        self.refresh_spin.setSingleStep(0.5)
        self.refresh_spin.setValue(self.controller.args.refresh)
        self.refresh_spin.valueChanged.connect(self.controller.set_refresh_seconds)
        self.horizon_slider = self._slider(-50, 100, int(self.controller.args.ais_horizon_eps * 1000.0), self.on_horizon)
        layout.addWidget(self._form_group("AIS / Datashader", [("color by", self.color_combo), ("point spread", self.point_slider), ("refresh sec", self.refresh_spin), ("horizon eps", self.horizon_slider)]))

        self.aircraft_color_combo = QtWidgets.QComboBox()
        self.aircraft_color_combo.addItem("altitude", "altitude")
        self.aircraft_color_combo.addItem("speed", "speed")
        self.aircraft_color_combo.addItem("density", "density")
        aircraft_color_index = self.aircraft_color_combo.findData(self.controller.args.aircraft_color_by)
        if aircraft_color_index >= 0:
            self.aircraft_color_combo.setCurrentIndex(aircraft_color_index)
        self.aircraft_color_combo.currentIndexChanged.connect(self.on_aircraft_color_mode)
        self.aircraft_point_slider = self._slider(1, 8, self.controller.args.aircraft_point_px, self.on_aircraft_point_px)
        self.aircraft_age_spin = QtWidgets.QDoubleSpinBox()
        self.aircraft_age_spin.setRange(0.0, 1440.0)
        self.aircraft_age_spin.setSingleStep(1.0)
        self.aircraft_age_spin.setValue(self.controller.args.aircraft_max_age_minutes)
        self.aircraft_age_spin.valueChanged.connect(self.controller.set_aircraft_max_age_minutes)
        self.aircraft_altitude_scale = QtWidgets.QDoubleSpinBox()
        self.aircraft_altitude_scale.setRange(0.0, 200.0)
        self.aircraft_altitude_scale.setSingleStep(5.0)
        self.aircraft_altitude_scale.setValue(self.controller.args.aircraft_altitude_exaggeration)
        self.aircraft_altitude_scale.valueChanged.connect(self.controller.set_aircraft_altitude_exaggeration)
        self.aircraft_horizon_slider = self._slider(-50, 100, int(self.controller.args.aircraft_horizon_eps * 1000.0), self.on_aircraft_horizon)
        layout.addWidget(self._form_group("ADS-B / Datashader", [("color by", self.aircraft_color_combo), ("point spread", self.aircraft_point_slider), ("max age min", self.aircraft_age_spin), ("altitude scale", self.aircraft_altitude_scale), ("horizon eps", self.aircraft_horizon_slider)]))

        help_label = QtWidgets.QLabel("Mouse: drag to rotate/pitch, wheel to zoom. Keyboard: W/S/Q/E for altitude/zoom, A/D for yaw. Double-click layer rows for settings.")
        help_label.setWordWrap(True)
        layout.addWidget(self._group("Controls", [help_label]))

        layout.addStretch(1)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedWidth(410)
        scroll.setWidget(panel)
        return scroll

    def _layer_group_definitions(self) -> list[tuple[str, str, list[str]]]:
        return [
            ("base", "底圖 / 地形", ["globe", "forest", "ice", "contours"]),
            ("hydrology", "水文 / 河湖", ["lakes", "rivers"]),
            ("boundary", "\u908a\u754c", ["borders", "territorial_sea", "eez", "high_seas"]),
            ("realtime", "\u5373\u6642\u5716\u5c64", ["clouds", "ais", "aircraft", "vehicle_icons"]),
            ("timeseries", "\u6642\u9593\u5e8f\u5217", ["forest_events"]),
            ("ui", "介面 UI", ["scale"]),
        ]

    def _build_mode_toolbar(self):
        QtWidgets = self.QtWidgets
        toolbar = QtWidgets.QToolBar("模式 / 投影")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.mode_buttons = {}
        for label, mode in [("\u975c\u614b", "static"), ("\u6642\u9593\u5e8f\u5217", "timeseries"), ("\u5373\u6642", "realtime")]:
            button = QtWidgets.QToolButton()
            button.setText(label)
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.setChecked(mode == self.data_mode)
            button.clicked.connect(lambda _checked=False, m=mode: self.set_data_mode(m))
            self.mode_buttons[mode] = button
            toolbar.addWidget(button)
        toolbar.addSeparator()
        toolbar.addWidget(QtWidgets.QLabel("\u6295\u5f71"))
        self.projection_combo = QtWidgets.QComboBox()
        for label, value in [("3D \u5730\u7403", "globe"), ("\u9ea5\u5361\u6258 Mercator", "mercator"), ("\u7b49\u8ddd\u5713\u67f1 Equirectangular", "equirectangular"), ("\u6975\u5340 Polar", "polar")]:
            self.projection_combo.addItem(label, value)
        projection_index = self.projection_combo.findData(self.map_projection)
        if projection_index >= 0:
            self.projection_combo.setCurrentIndex(projection_index)
        self.projection_combo.currentIndexChanged.connect(self.on_projection_changed)
        toolbar.addWidget(self.projection_combo)
        toolbar.addSeparator()
        toolbar.addWidget(QtWidgets.QLabel("\u98a8\u683c"))
        self.style_combo = QtWidgets.QComboBox()
        for label, value in [("\u79d1\u5b78", "scientific"), ("\u6230\u8853 basic \U0001f6a7", "tactical"), ("\u822a\u6d77 basic \U0001f6a7", "nautical"), ("\u7f8a\u76ae\u7d19 basic \U0001f6a7", "parchment")]:
            self.style_combo.addItem(label, value)
        style_index = self.style_combo.findData(self.style_profile)
        if style_index >= 0:
            self.style_combo.setCurrentIndex(style_index)
        self.style_combo.currentIndexChanged.connect(self.on_style_profile_changed)
        toolbar.addWidget(self.style_combo)
        toolbar.addSeparator()
        self.lod_label = QtWidgets.QLabel(self.controller.basemap_lod_label())
        self.lod_label.setToolTip("\u76ee\u524d\u6bd4\u4f8b\u5c3a\u5c0d\u61c9\u7684\u5e95\u5716 LOD \u8207\u6295\u5f71\u72c0\u614b")
        toolbar.addWidget(self.lod_label)
        toolbar.addSeparator()
        for label, detail in [
            ("\u8f38\u51fa\u622a\u5716 \U0001f6a7", "\u65bd\u5de5\u4e2d\uff1a\u5c07\u76ee\u524d frame_rgba \u8f38\u51fa\u6210 PNG/TIFF\u3002"),
            ("\u8f38\u51fa\u5f71\u7247 \U0001f6a7", "\u65bd\u5de5\u4e2d\uff1a\u63a5 frame recorder \u8207\u5f71\u7247 encoder\u3002"),
            ("\u8cc7\u6599\u4f86\u6e90\u8a2d\u5b9a \U0001f6a7", "\u65bd\u5de5\u4e2d\uff1a\u96c6\u4e2d\u7ba1\u7406 provider\u3001\u5feb\u53d6\u8207\u7248\u672c\u8cc7\u8a0a\u3002"),
            ("\u5916\u639b\u6a21\u7d44 \U0001f6a7", "\u65bd\u5de5\u4e2d\uff1a\u5c07 render/data/projection/ui \u9010\u6b65\u62c6\u6a94\u3002"),
            ("\u89e3\u8026\u8a08\u756b", architecture_split_plan_text()),
            ("\u62c6\u6a94\u5c31\u7dd2\u5ea6", module_split_readiness_text()),
            ("Extraction gates", decoupling_extraction_gates_text()),
            ("Extraction audit", self.controller.decoupling_extraction_audit_text),
            ("\u5c08\u6848\u72c0\u614b / \u5f85\u8fa6", project_feature_status_text()),
            ("\u8cc7\u6599\u4f86\u6e90\u7e3d\u89bd", data_source_catalog_text()),
            ("\u4ecb\u9762\u4e2d\u6587\u5316\u72c0\u614b", ui_localization_status_text()),
            ("Provider status", provider_catalog_text()),
            ("Layer provider registry", layer_provider_registry_text()),
            ("Provider cache manifest", provider_cache_manifest_text()),
            ("Cache governance", self.controller.cache_governance_matrix_text),
            ("Provider manifest templates", lambda: provider_manifest_templates_text(self.controller.basemap_lod)),
            ("Provider manifest bundle", self.controller.provider_manifest_bundle_text),
            ("Write provider manifests", self.controller.write_provider_manifest_bundle_text),
            ("Data fetch status", self.controller.data_fetch_status_text),
            ("Basemap LOD decision", self.controller.basemap_provider_decision_text),
            ("LOD hook pipeline", self.controller.lod_hook_pipeline_text),
            ("LOD invalidation contract", self.controller.lod_invalidation_contract_text),
            ("LOD layer decision matrix", self.controller.lod_layer_decision_matrix_text),
            ("Hydrology provider decisions", self.controller.hydrology_provider_decisions_text),
            ("Hydrology control", self.controller.hydrology_control_text),
            ("Hydrology basic readiness", self.controller.hydrology_basic_readiness_matrix_text),
            ("Hydrology dirty/reload contract", self.controller.hydrology_dirty_reload_contract_text),
            ("Hydrology render profile", self.controller.hydrology_render_profile_text),
            ("Hydrology strictness", self.controller.hydrology_strictness_report_text),
            ("Hydrology strict ports", self.controller.hydrology_strict_provider_ports_text),
            ("Boundary provider decisions", self.controller.boundary_provider_decisions_text),
            ("Ocean provider decision", self.controller.ocean_provider_decision_text),
            ("Ocean provider registry", ocean_provider_registry_text),
            ("Ocean render port", self.controller.ocean_render_port_contract_text),
            ("Ocean normalization", self.controller.ocean_normalization_report_text),
            ("Ocean spatial sampling", self.controller.ocean_spatial_sampling_text),
            ("AIS provider decision", self.controller.ais_provider_decision_text),
            ("ADS-B provider decision", self.controller.aircraft_provider_decision_text),
            ("Ocean material policy", self.controller.ocean_material_policy_text),
            ("Ocean material control", self.controller.ocean_material_control_text),
            ("Ocean Taichi material port", self.controller.ocean_material_taichi_port_text),
            ("Ocean condition material binding", self.controller.ocean_condition_material_binding_text),
            ("Projection pipeline", self.controller.projection_pipeline_text),
            ("Mode layer policy", self.controller.mode_layer_policy_text),
            ("Datashader sampling policy", self.controller.datashader_sampling_policy_text),
            ("Adaptive quality policy", self.controller.adaptive_quality_policy_text),
            ("Render core input summary", self.controller.render_core_input_summary_text),
            ("Project handoff snapshot", self.controller.project_handoff_snapshot_text),
            ("Write handoff snapshot", self.controller.write_project_handoff_snapshot_text),
            ("Module split blueprint", module_split_blueprint_text()),
            ("符號抽離地圖", symbol_extraction_map_text()),
            ("Runtime config contract", self.controller.runtime_configuration_contract_text),
            ("Project milestones", self.controller.project_goal_milestones_text),
            ("Extraction units", self.controller.decoupling_extraction_units_text),
            ("Provider manifests API", self.controller.provider_manifests_module_api_text),
            ("Hydrology provider API", self.controller.hydrology_provider_module_api_text),
            ("Hydrology provider extraction readiness", self.controller.hydrology_provider_extraction_readiness_packet_text),
            ("Ocean provider API", self.controller.ocean_condition_provider_module_api_text),
            ("Ocean provider extraction readiness", self.controller.ocean_condition_provider_extraction_readiness_packet_text),
            ("Render ocean API", self.controller.render_core_ocean_material_module_api_text),
            ("Render ocean extraction readiness", self.controller.render_core_ocean_material_extraction_readiness_packet_text),
            ("Vector lines API", self.controller.vector_lines_module_api_text),
            ("Vector lines extraction readiness", self.controller.vector_lines_extraction_readiness_packet_text),
            ("LOD pipeline API", self.controller.lod_pipeline_module_api_text),
            ("LOD pipeline extraction readiness", self.controller.lod_pipeline_extraction_readiness_packet_text),
            ("Style profiles API", self.controller.style_profiles_module_api_text),
            ("Style profiles extraction readiness", self.controller.style_profiles_extraction_readiness_packet_text),
            ("Datashader points API", self.controller.datashader_points_module_api_text),
            ("Datashader points extraction readiness", self.controller.datashader_points_extraction_readiness_packet_text),
            ("Module API registry", self.controller.module_api_registry_text),
            ("Pre-extraction audit", self.controller.pre_extraction_readiness_audit_text),
            ("First extraction plan", self.controller.first_extraction_execution_plan_text),
            ("First extraction readiness packet", self.controller.first_extraction_readiness_packet_text),
            ("Extraction readiness packet index", self.controller.extraction_readiness_packet_index_text),
            ("Active goal extraction seams", self.controller.active_goal_extraction_seam_matrix_text),
            ("Import boundary matrix", self.controller.module_import_boundary_matrix_text),
            ("Module contract coverage", self.controller.module_contract_coverage_text),
            ("Validation rollback plan", self.controller.validation_and_rollback_plan_text),
            ("Pre-validation evidence plan", self.controller.pre_validation_evidence_plan_text),
            ("Unverified risks", self.controller.unverified_risk_register_text),
            ("Active goal known issues", self.controller.active_goal_known_issue_matrix_text),
            ("Active goal readiness gate", self.controller.active_goal_readiness_gate_text),
            ("Active goal summary", self.controller.active_goal_summary_text),
            ("Next action queue", self.controller.active_goal_next_action_queue_text),
            ("Qt facade API", self.controller.qt_controller_facade_api_text),
            ("Qt facade coverage", self.controller.qt_controller_facade_coverage_text),
            ("Qt facade extraction readiness", self.controller.qt_controller_facade_extraction_readiness_packet_text),
            ("Qt main window API", self.controller.qt_main_window_module_api_text),
            ("Qt main window extraction readiness", self.controller.qt_main_window_extraction_readiness_packet_text),
            ("Qt coupling cleanup", self.controller.qt_ui_coupling_cleanup_status_text),
            ("Active goal bundle", self.controller.active_goal_control_bundle_text),
            ("Provider interface spec", provider_interface_spec_text()),
            ("Renderer data contract", self.controller.renderer_data_contract_text),
            ("渲染預算", self.controller.render_budget_text),
            ("點雲預算", self.controller.point_overlay_budget_text),
            ("風格契約", self.controller.style_profile_status_text),
            ("Style renderer entry", self.controller.style_renderer_entry_text),
            ("Style renderer entry matrix", self.controller.style_renderer_entry_matrix_text),
            ("Style overlay intent", self.controller.style_overlay_intent_text),
        ]:
            action_button = QtWidgets.QToolButton()
            action_button.setText(label)
            detail_text = "Click to inspect current status." if callable(detail) else detail
            action_button.setToolTip(detail_text)
            action_button.clicked.connect(
                lambda _checked=False, title=label, detail_source=detail: self._show_construction_port(
                    title,
                    detail_source() if callable(detail_source) else detail_source,
                )
            )
            toolbar.addWidget(action_button)
        runtime_status_button = QtWidgets.QToolButton()
        runtime_status_button.setText("狀態")
        runtime_status_button.setToolTip("檢視 FPS、圖層、LOD、資料來源與渲染狀態")
        runtime_status_button.clicked.connect(lambda _checked=False: self._show_construction_port("即時狀態", self.controller.runtime_status_text()))
        toolbar.addWidget(runtime_status_button)
        return toolbar

    def _build_layer_dock(self):
        QtCore = self.QtCore
        QtWidgets = self.QtWidgets
        dock = QtWidgets.QDockWidget("圖層", self.window)
        dock.setObjectName("PhotoshopLikeLayerDock")
        dock.setAllowedAreas(QtCore.Qt.DockWidgetArea.RightDockWidgetArea | QtCore.Qt.DockWidgetArea.BottomDockWidgetArea)
        dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetClosable)
        body = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(body)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        self.layer_list = QtWidgets.QListWidget()
        self.layer_list.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        self.layer_list.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction)
        self.layer_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.layer_list.itemDoubleClicked.connect(self.open_layer_settings)
        self.layer_list.model().rowsMoved.connect(lambda *args: self.sync_layer_order_from_list())
        self.layer_list.setStyleSheet("QListWidget { background:#202124; color:#e6e6e6; border:1px solid #3a3a3a; } QListWidget::item { margin:2px; }")
        layer_help = QtWidgets.QLabel("上方代表畫面上層；拖拉可改變上下順序，雙擊圖層可開啟設定。")
        layer_help.setWordWrap(True)
        layout.addWidget(self.layer_list, stretch=1)
        layout.addWidget(layer_help)
        dock.setWidget(body)
        dock.setMinimumWidth(320)
        dock.resize(360, 420)
        self.rebuild_layer_list()
        return dock

    def _build_timeline_bar(self):
        QtCore = self.QtCore
        QtWidgets = self.QtWidgets
        dock = QtWidgets.QDockWidget("時間軸", self.window)
        dock.setObjectName("TimelineDock")
        dock.setAllowedAreas(QtCore.Qt.DockWidgetArea.BottomDockWidgetArea)
        dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetClosable)
        body = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(body)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)
        self.timeline_play_button = QtWidgets.QToolButton()
        self.timeline_play_button.setText("播放")
        self.timeline_play_button.clicked.connect(self.toggle_timeline_playback)
        self.timeline_label = QtWidgets.QLabel("00:00:00")
        self.timeline_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.timeline_slider.setRange(0, int(self.timeline_duration_seconds))
        self.timeline_slider.setValue(0)
        self.timeline_slider.valueChanged.connect(self.on_timeline_slider_changed)
        self.timeline_speed_combo = QtWidgets.QComboBox()
        for label, value in [("0.25x", 0.25), ("0.5x", 0.5), ("1x", 1.0), ("2x", 2.0), ("4x", 4.0), ("8x", 8.0)]:
            self.timeline_speed_combo.addItem(label, value)
        self.timeline_speed_combo.setCurrentIndex(2)
        self.timeline_speed_combo.currentIndexChanged.connect(self.on_timeline_speed_changed)
        self.timeline_hint = QtWidgets.QLabel("時間序列模式啟用；滑鼠移到底部時顯示。")
        layout.addWidget(self.timeline_play_button)
        layout.addWidget(self.timeline_label)
        layout.addWidget(self.timeline_slider, stretch=1)
        layout.addWidget(self.timeline_speed_combo)
        layout.addWidget(self.timeline_hint)
        dock.setWidget(body)
        dock.setMinimumHeight(82)
        return dock

    def create_layer_group_widget(self, group_id: str, title: str, visible_count: int):
        QtWidgets = self.QtWidgets
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(8, 2, 8, 2)
        arrow = QtWidgets.QToolButton()
        arrow.setText("▶" if group_id in self.layer_groups_collapsed else "▼")
        arrow.setFixedWidth(28)
        arrow.clicked.connect(lambda _checked=False, gid=group_id: self.toggle_layer_group(gid))
        label = QtWidgets.QLabel(f"{title} ({visible_count})")
        label.setStyleSheet("font-weight:600; color:#f0f0f0;")
        layout.addWidget(arrow)
        layout.addWidget(label, stretch=1)
        return widget

    def toggle_layer_group(self, group_id: str) -> None:
        if group_id in self.layer_groups_collapsed:
            self.layer_groups_collapsed.remove(group_id)
        else:
            self.layer_groups_collapsed.add(group_id)
        self.rebuild_layer_list()

    def set_data_mode(self, mode: str) -> None:
        if mode not in {"static", "timeseries", "realtime"}:
            mode = "realtime"
        self.data_mode = mode
        self.controller.set_data_mode(mode)
        for item_mode, button in getattr(self, "mode_buttons", {}).items():
            button.setChecked(item_mode == mode)
        if hasattr(self, "timeline_bar"):
            if mode == "timeseries":
                self._show_timeline_temporarily()
            else:
                self.timeline_bar.hide()
                self.timeline_playing = False
                if hasattr(self, "timeline_play_button"):
                    self.timeline_play_button.setText("播放")
        self.rebuild_layer_list()

    def _show_construction_port(self, title: str, detail: str) -> None:
        message = f"{title}\n\n{detail}\n\nStatus: port/basic implementation; more work or validation may still be required."
        self.QtWidgets.QMessageBox.information(self.window, title, message)

    def on_projection_changed(self, index: int) -> None:
        projection = self.projection_combo.itemData(index) or "globe"
        self.map_projection = str(projection)
        self.controller.set_map_projection(self.map_projection)
        if self.map_projection != "globe":
            self._show_construction_port(self.projection_combo.itemText(index), "投影模式已建立管線契約；下一步需要接 planar renderer 與 overlay projection adapter。")

    def on_style_profile_changed(self, index: int) -> None:
        profile = self.style_combo.itemData(index) or "scientific"
        self.style_profile = str(profile)
        self.controller.set_style_profile(self.style_profile)
        frame = self.controller.render_if_needed(force=True)
        if frame is not None:
            self.image.set_data(frame)
        if self.style_profile != "scientific":
            self._show_construction_port(self.style_combo.itemText(index), "目前是 basic post-process；下一步可拆成 Style Renderer，支援科學、戰術、羊皮紙等風格。")

    def _show_timeline_temporarily(self) -> None:
        if self.data_mode != "timeseries":
            return
        self.timeline_visible_until = time.time() + 1.6
        self.timeline_bar.show()

    def _update_timeline_visibility(self) -> None:
        if self.data_mode != "timeseries" or not hasattr(self, "timeline_bar"):
            return
        if self.timeline_bar.isFloating():
            return
        if time.time() > self.timeline_visible_until:
            self.timeline_bar.hide()

    def toggle_timeline_playback(self) -> None:
        self.timeline_playing = not self.timeline_playing
        self.timeline_last_tick = time.time()
        self.timeline_play_button.setText("\u66ab\u505c" if self.timeline_playing else "\u64ad\u653e")
        self._show_timeline_temporarily()

    def on_timeline_slider_changed(self, value: int) -> None:
        hours = int(value) // 3600
        minutes = (int(value) % 3600) // 60
        seconds = int(value) % 60
        self.timeline_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        self._show_timeline_temporarily()

    def on_timeline_speed_changed(self, index: int) -> None:
        self.timeline_speed = float(self.timeline_speed_combo.itemData(index) or 1.0)
        self._show_timeline_temporarily()

    def advance_timeline(self) -> None:
        if not self.timeline_playing or self.data_mode != "timeseries":
            self.timeline_last_tick = time.time()
            return
        now = time.time()
        delta = (now - self.timeline_last_tick) * self.timeline_speed
        self.timeline_last_tick = now
        next_value = int(self.timeline_slider.value() + delta)
        if next_value > self.timeline_slider.maximum():
            next_value = self.timeline_slider.maximum()
            self.timeline_playing = False
            self.timeline_play_button.setText("\u64ad\u653e")
        self.timeline_slider.setValue(next_value)

    def rebuild_layer_list(self) -> None:
        QtCore = self.QtCore
        self.updating_layers = True
        self.layer_list.clear()
        top_to_bottom = list(reversed(self.controller.layer_order))
        known_layers = set(self.controller.LAYER_LABELS)
        for group_id, title, group_layers in self.layer_group_defs:
            visible_layers = [
                layer_id
                for layer_id in top_to_bottom
                if layer_id in group_layers
                and layer_id in known_layers
                and self.controller.layer_allowed_in_mode(layer_id)
            ]
            if not visible_layers:
                continue
            group_item = self.QtWidgets.QListWidgetItem()
            group_item.setData(QtCore.Qt.ItemDataRole.UserRole, f"__group__:{group_id}")
            group_item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable)
            group_item.setSizeHint(self.QtCore.QSize(0, 30))
            self.layer_list.addItem(group_item)
            self.layer_list.setItemWidget(group_item, self.create_layer_group_widget(group_id, title, len(visible_layers)))
            if group_id in self.layer_groups_collapsed:
                continue
            for layer_id in visible_layers:
                self._add_layer_list_item(layer_id)
        self.updating_layers = False

    def _add_layer_list_item(self, layer_id: str) -> None:
        QtCore = self.QtCore
        locked = layer_id in self.locked_layers
        item = self.QtWidgets.QListWidgetItem()
        item.setData(QtCore.Qt.ItemDataRole.UserRole, layer_id)
        flags = item.flags() | QtCore.Qt.ItemFlag.ItemIsDropEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled
        if not locked:
            flags |= QtCore.Qt.ItemFlag.ItemIsDragEnabled
        item.setFlags(flags)
        item.setSizeHint(self.QtCore.QSize(0, 34))
        self.layer_list.addItem(item)
        self.layer_list.setItemWidget(item, self.create_layer_row_widget(layer_id))

    def create_layer_row_widget(self, layer_id: str):
        QtWidgets = self.QtWidgets
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(8)

        visible_btn = QtWidgets.QToolButton()
        visible_btn.setText("eye" if self.controller.layer_visible.get(layer_id, True) else "off")
        visible_btn.setToolTip("show / hide")
        visible_btn.setFixedWidth(42)
        visible_btn.setEnabled(layer_id not in self.locked_layers)
        visible_btn.clicked.connect(lambda _checked=False, lid=layer_id: self.toggle_layer_visible(lid))

        label = QtWidgets.QLabel(self.controller.layer_label(layer_id))
        label.setMinimumWidth(160)

        lock_btn = QtWidgets.QToolButton()
        lock_btn.setText("lock" if layer_id in self.locked_layers else "open")
        lock_btn.setToolTip("lock / unlock")
        lock_btn.setFixedWidth(46)
        lock_btn.clicked.connect(lambda _checked=False, lid=layer_id: self.toggle_layer_lock_by_id(lid))

        layout.addWidget(visible_btn)
        layout.addWidget(label, stretch=1)
        layout.addWidget(lock_btn)
        return widget

    def toggle_layer_visible(self, layer_id: str) -> None:
        if layer_id in self.locked_layers:
            return
        visible = not self.controller.layer_visible.get(layer_id, True)
        self.controller.set_layer_visible(layer_id, visible)
        if layer_id == "vehicle_icons":
            self.icons_checkbox.setChecked(visible)
        if layer_id == "contours":
            self.contours_checkbox.setChecked(visible)
        self.rebuild_layer_list()

    def on_layer_item_changed(self, item) -> None:
        if self.updating_layers:
            return
        layer_id = item.data(self.QtCore.Qt.ItemDataRole.UserRole)
        if layer_id in self.locked_layers:
            self.rebuild_layer_list()
            return
        visible = item.checkState() == self.QtCore.Qt.CheckState.Checked
        self.controller.set_layer_visible(layer_id, visible)
        if layer_id == "vehicle_icons":
            self.icons_checkbox.setChecked(visible)
        if layer_id == "contours":
            self.contours_checkbox.setChecked(visible)

    def sync_layer_order_from_list(self) -> None:
        if self.updating_layers:
            return
        top_to_bottom = []
        for row in range(self.layer_list.count()):
            item = self.layer_list.item(row)
            layer_id = item.data(self.QtCore.Qt.ItemDataRole.UserRole)
            if isinstance(layer_id, str) and layer_id.startswith("__group__:"):
                continue
            if layer_id in self.controller.LAYER_LABELS:
                top_to_bottom.append(layer_id)
        old_top_to_bottom = list(reversed(self.controller.layer_order))
        for locked_layer in self.locked_layers:
            if locked_layer in old_top_to_bottom and locked_layer in top_to_bottom:
                if old_top_to_bottom.index(locked_layer) != top_to_bottom.index(locked_layer):
                    self.rebuild_layer_list()
                    return
        self.controller.set_layer_order(list(reversed(top_to_bottom)))

    def toggle_layer_lock(self, item) -> None:
        layer_id = item.data(self.QtCore.Qt.ItemDataRole.UserRole)
        if isinstance(layer_id, str) and layer_id.startswith("__group__:"):
            return
        self.toggle_layer_lock_by_id(layer_id)

    def toggle_layer_lock_by_id(self, layer_id: str) -> None:
        if layer_id in self.locked_layers:
            self.locked_layers.remove(layer_id)
        else:
            self.locked_layers.add(layer_id)
        self.rebuild_layer_list()

    def toggle_side_panel(self) -> None:
        visible = not self.side_panel.isVisible()
        self.side_panel.setVisible(visible)
        self.drawer_button.setText("<" if visible else ">")

    def open_layer_settings(self, item) -> None:
        layer_id = item.data(self.QtCore.Qt.ItemDataRole.UserRole)
        if isinstance(layer_id, str) and layer_id.startswith("__group__:"):
            self.toggle_layer_group(layer_id.split(":", 1)[1])
            return
        if layer_id not in self.controller.LAYER_LABELS:
            return
        dialog = self.QtWidgets.QDialog(self.window)
        dialog.setWindowTitle(f"{self.controller.layer_label(layer_id)} Settings")
        dialog.setAttribute(self.QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)
        layout = self.QtWidgets.QVBoxLayout(dialog)
        form = self.QtWidgets.QFormLayout()
        layout.addLayout(form)

        self._add_layer_visibility_controls(form, layer_id)
        if layer_id == "globe":
            self._build_globe_settings(form)
        elif layer_id == "ice":
            self._build_ice_settings(form)
        elif layer_id == "ais":
            self._build_ais_settings(form)
        elif layer_id == "aircraft":
            self._build_aircraft_settings(form)
        elif layer_id == "vehicle_icons":
            self._build_icon_settings(form)
        elif layer_id == "contours":
            self._build_contour_settings(form)
        elif layer_id in {"lakes", "rivers"}:
            self._build_hydrology_settings(form, layer_id)
        elif layer_id == "scale":
            self._build_scale_settings(form)
        elif layer_id == "clouds":
            self._build_satellite_cloud_settings(form)
        elif layer_id in {"borders", "territorial_sea", "eez", "high_seas"}:
            self._build_boundary_settings(form, layer_id)

        close_btn = self.QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        dialog.finished.connect(lambda _code, dlg=dialog: self._forget_layer_dialog(dlg))
        self.layer_dialogs.append(dialog)
        dialog.show()

    def _forget_layer_dialog(self, dialog) -> None:
        if dialog in self.layer_dialogs:
            self.layer_dialogs.remove(dialog)

    def _add_layer_visibility_controls(self, form, layer_id: str) -> None:
        visible_box = self.QtWidgets.QCheckBox("visible")
        visible_box.setChecked(self.controller.layer_visible.get(layer_id, True))
        visible_box.setEnabled(layer_id not in self.locked_layers)
        visible_box.toggled.connect(lambda checked, lid=layer_id: self._set_layer_visible_from_dialog(lid, checked))
        lock_box = self.QtWidgets.QCheckBox("locked")
        lock_box.setChecked(layer_id in self.locked_layers)
        lock_box.toggled.connect(lambda checked, lid=layer_id: self._set_layer_locked_from_dialog(lid, checked))
        form.addRow("visibility", visible_box)
        form.addRow("lock", lock_box)

    def _set_layer_visible_from_dialog(self, layer_id: str, visible: bool) -> None:
        if layer_id in self.locked_layers:
            return
        self.controller.set_layer_visible(layer_id, visible)
        if layer_id == "vehicle_icons":
            self.icons_checkbox.setChecked(visible)
        if layer_id == "contours":
            self.contours_checkbox.setChecked(visible)
        self.update_scale_bar_visuals()
        self.rebuild_layer_list()

    def _set_layer_locked_from_dialog(self, layer_id: str, locked: bool) -> None:
        if locked:
            self.locked_layers.add(layer_id)
        else:
            self.locked_layers.discard(layer_id)
        self.rebuild_layer_list()

    def _combo(self, items: list[tuple[str, str]], current: str, callback):
        combo = self.QtWidgets.QComboBox()
        for label, value in items:
            combo.addItem(label, value)
        index = combo.findData(current)
        if index >= 0:
            combo.setCurrentIndex(index)
        combo.currentIndexChanged.connect(lambda idx: callback(combo.itemData(idx)))
        return combo

    def _double_spin(self, value: float, min_value: float, max_value: float, step: float, callback):
        spin = self.QtWidgets.QDoubleSpinBox()
        spin.setRange(min_value, max_value)
        spin.setSingleStep(step)
        spin.setDecimals(3 if step < 0.01 else 2 if step < 0.1 else 1)
        spin.setValue(float(value))
        spin.valueChanged.connect(callback)
        return spin

    def _int_spin(self, value: int, min_value: int, max_value: int, step: int, callback):
        spin = self.QtWidgets.QSpinBox()
        spin.setRange(min_value, max_value)
        spin.setSingleStep(step)
        spin.setValue(int(value))
        spin.valueChanged.connect(callback)
        return spin

    def _build_globe_settings(self, form) -> None:
        form.addRow("sea level offset m", self._double_spin(self.controller.args.sea_level_m, -500.0, 500.0, 5.0, self.controller.set_sea_level_m))
        ocean_box = self.QtWidgets.QCheckBox("enable Taichi ocean material")
        ocean_box.setChecked(bool(self.controller.args.ocean_material))
        ocean_box.toggled.connect(self.controller.set_ocean_material)
        ocean_status = self.QtWidgets.QLabel(self.controller.ocean_condition_status_text())
        ocean_status.setWordWrap(True)
        source_combo = self._combo(
            [(meta["label"], source) for source, meta in OCEAN_PROVIDER_REGISTRY.items()],
            self.controller.args.ocean_condition_source,
            lambda value: self.controller.set_ocean_condition_source(value),
        )
        selected_ocean_meta = OCEAN_PROVIDER_REGISTRY.get(self.controller.args.ocean_condition_source, OCEAN_PROVIDER_REGISTRY["manual"])
        selected_ocean_attr = selected_ocean_meta.get("source_attr")
        condition_file = self.QtWidgets.QLineEdit(
            (getattr(self.controller.args, selected_ocean_attr, None) if selected_ocean_attr and selected_ocean_attr.endswith("_file") else getattr(self.controller.args, "ocean_condition_file", None)) or ""
        )
        condition_url = self.QtWidgets.QLineEdit(
            (getattr(self.controller.args, selected_ocean_attr, None) if selected_ocean_attr and selected_ocean_attr.endswith("_url") else getattr(self.controller.args, "ocean_condition_url", None)) or ""
        )
        apply_condition_btn = self.QtWidgets.QPushButton("apply ocean source")
        apply_condition_btn.clicked.connect(lambda _checked=False, s=source_combo, f=condition_file, u=condition_url: self._apply_ocean_condition_source(s, f, u))
        schema_hint = self.QtWidgets.QLabel(OCEAN_CONDITION_SCHEMA_TEXT)
        schema_hint.setWordWrap(True)
        source_hint = self.QtWidgets.QLabel(
            f"{selected_ocean_meta.get('label', 'manual')} | "
            f"{selected_ocean_meta.get('kind', 'manual')} | "
            f"{selected_ocean_meta.get('spatial_mode', 'global-scalar')} | "
            f"refresh: {selected_ocean_meta.get('refresh_hint', 'manual')}"
        )
        source_hint.setWordWrap(True)
        spatial_hint = self.QtWidgets.QLabel(self.controller.ocean_spatial_sampling_text())
        spatial_hint.setWordWrap(True)
        form.addRow("ocean material", ocean_box)
        form.addRow("ocean status", ocean_status)
        form.addRow("ocean source", source_combo)
        form.addRow("source detail", source_hint)
        form.addRow("ocean file", condition_file)
        form.addRow("ocean URL", condition_url)
        form.addRow("apply", apply_condition_btn)
        form.addRow("schema", schema_hint)
        form.addRow("sampling policy", spatial_hint)
        form.addRow("sample latitude", self._double_spin(getattr(self.controller.args, "ocean_provider_lat", 0.0), -90.0, 90.0, 0.25, self.controller.set_ocean_provider_lat))
        form.addRow("sample longitude", self._double_spin(getattr(self.controller.args, "ocean_provider_lon", 0.0), -180.0, 180.0, 0.25, self.controller.set_ocean_provider_lon))
        form.addRow("wave strength", self._double_spin(self.controller.args.ocean_wave_strength, 0.0, 1.0, 0.05, self.controller.set_ocean_wave_strength))
        form.addRow("roughness", self._double_spin(self.controller.args.ocean_roughness, 0.02, 1.0, 0.05, self.controller.set_ocean_roughness))
        form.addRow("foam", self._double_spin(self.controller.args.ocean_foam, 0.0, 1.0, 0.05, self.controller.set_ocean_foam))
        form.addRow("ocean FPS", self._double_spin(self.controller.args.ocean_animation_fps, 0.0, 60.0, 1.0, self.controller.set_ocean_animation_fps))
        form.addRow("condition refresh sec", self._double_spin(self.controller.args.ocean_condition_refresh, 0.0, 3600.0, 5.0, self.controller.set_ocean_condition_refresh))

    def _apply_ocean_condition_source(self, source_combo, file_edit, url_edit) -> None:
        self.controller.set_ocean_condition_source(
            source_combo.currentData() or "manual",
            file_edit.text(),
            url_edit.text(),
        )
        self.image.set_data(self.controller.render_if_needed(force=True))

    def _build_ice_settings(self, form) -> None:
        source_combo = self._combo(
            [("Natural Earth", "naturalearth"), ("Natural Earth 10m", "ne10"), ("Natural Earth 50m", "ne50"), ("Natural Earth 110m", "ne110"), ("none", "none")],
            self.controller.args.ice_source,
            self._set_ice_source_from_dialog,
        )
        hint = self.QtWidgets.QLabel("Ice/snow masks are renderer inputs. Strict scientific data should later move to a provider with versioned metadata.")
        hint.setWordWrap(True)
        form.addRow("ice source", source_combo)
        form.addRow("opacity", self._double_spin(self.controller.args.ice_opacity, 0.0, 1.0, 0.05, self.controller.set_ice_opacity))
        form.addRow("specular", self._double_spin(self.controller.args.ice_specular, 0.0, 1.0, 0.05, self.controller.set_ice_specular))
        form.addRow("blue tint", self._double_spin(self.controller.args.ice_blue, 0.0, 1.0, 0.05, self.controller.set_ice_blue))
        form.addRow("note", hint)

    def _set_ice_source_from_dialog(self, source: str) -> None:
        self.window.setCursor(self.QtCore.Qt.CursorShape.WaitCursor)
        setup_startup_progress(True)
        try:
            self.controller.reload_ice_source(source)
            self.image.set_data(self.controller.render_if_needed(force=True))
        finally:
            close_startup_progress()
            self.window.unsetCursor()

    def _apply_topography_step(self, spin) -> None:
        self.window.setCursor(self.QtCore.Qt.CursorShape.WaitCursor)
        try:
            self.controller.reload_topography_step(int(spin.value()))
            self.image.set_data(self.controller.render_if_needed(force=True))
        finally:
            self.window.unsetCursor()

    def _set_highest_topography_step(self, spin) -> None:
        spin.setValue(1)
        self._apply_topography_step(spin)

    def _build_ais_settings(self, form) -> None:
        form.addRow(
            "color by",
            self._combo([("speed", "speed"), ("density", "density")], self.controller.args.color_by, self.controller.set_color_mode),
        )
        form.addRow("point spread", self._int_spin(self.controller.args.point_px, 1, 8, 1, self.controller.set_point_px))
        form.addRow("sample ratio", self._double_spin(self.controller.args.ais_sample_ratio, 0.01, 1.0, 0.05, self.controller.set_ais_sample_ratio))
        form.addRow("max age min", self._double_spin(self.controller.args.max_age_minutes, 0.0, 1440.0, 1.0, self.controller.set_max_age_minutes))

    def _build_aircraft_settings(self, form) -> None:
        form.addRow(
            "color by",
            self._combo([("altitude", "altitude"), ("speed", "speed"), ("density", "density")], self.controller.args.aircraft_color_by, self.controller.set_aircraft_color_mode),
        )
        form.addRow("point spread", self._int_spin(self.controller.args.aircraft_point_px, 1, 8, 1, self.controller.set_aircraft_point_px))
        form.addRow("sample ratio", self._double_spin(self.controller.args.aircraft_sample_ratio, 0.01, 1.0, 0.05, self.controller.set_aircraft_sample_ratio))
        form.addRow("max age min", self._double_spin(self.controller.args.aircraft_max_age_minutes, 0.0, 1440.0, 1.0, self.controller.set_aircraft_max_age_minutes))
        form.addRow("altitude scale", self._double_spin(self.controller.args.aircraft_altitude_exaggeration, 0.0, 200.0, 5.0, self.controller.set_aircraft_altitude_exaggeration))

    def _build_icon_settings(self, form) -> None:
        form.addRow("max icons", self._int_spin(self.controller.args.icon_max_count, 0, 50000, 100, self.controller.set_icon_max_count))
        form.addRow("pick radius px", self._double_spin(self.controller.args.icon_pick_radius, 2.0, 80.0, 1.0, self.controller.set_icon_pick_radius))

    def _build_satellite_cloud_settings(self, form) -> None:
        note = self.QtWidgets.QLabel("Procedural cloud basic layer: generated by Taichi from camera, lat/lon, and time. Later this can be replaced by GOES/Himawari/EUMETSAT providers.")
        note.setWordWrap(True)
        form.addRow("note", note)
        form.addRow("opacity", self._double_spin(self.controller.args.cloud_opacity, 0.0, 1.0, 0.05, self.controller.set_cloud_opacity))
        form.addRow("coverage", self._double_spin(self.controller.args.cloud_coverage, 0.05, 0.95, 0.05, self.controller.set_cloud_coverage))
        form.addRow("detail", self._double_spin(self.controller.args.cloud_detail, 0.0, 1.0, 0.05, self.controller.set_cloud_detail))
        form.addRow("animation FPS", self._double_spin(self.controller.args.cloud_animation_fps, 0.0, 60.0, 1.0, self.controller.set_cloud_animation_fps))

    def _build_contour_settings(self, form) -> None:
        form.addRow("interval m", self._double_spin(self.controller.args.contour_interval_m, 50.0, 5000.0, 100.0, self.controller.set_contour_interval))
        form.addRow("line width m", self._double_spin(self.controller.args.contour_line_width_m, 1.0, 250.0, 5.0, self.controller.set_contour_line_width))
        form.addRow("opacity", self._double_spin(self.controller.args.contour_opacity, 0.0, 1.0, 0.05, self.controller.set_contour_opacity))

    def _build_hydrology_settings(self, form, layer_id: str) -> None:
        spec = HYDROLOGY_SPECS[layer_id]
        prefix = spec["prefix"]
        provider = LAYER_PROVIDER_REGISTRY.get(layer_id, {})
        status = self.QtWidgets.QLabel(self.controller.hydrology_layer_status_text(layer_id))
        status.setWordWrap(True)
        provider_note = self.QtWidgets.QLabel(f"provider: {provider.get('provider', 'unregistered')}\ninput: {provider.get('renderer_input', 'unknown')}")
        provider_note.setWordWrap(True)
        mode_combo = self._combo(
            [("LOD automatic", "lod"), ("manual source", "manual"), ("strict source", "strict")],
            getattr(self.controller.args, "hydrology_source_mode", "lod"),
            self._set_hydrology_source_mode,
        )
        file_edit = self.QtWidgets.QLineEdit(getattr(self.controller.args, f"{prefix}_file", None) or "")
        url_edit = self.QtWidgets.QLineEdit(getattr(self.controller.args, f"{prefix}_url", None) or "")
        reload_btn = self.QtWidgets.QPushButton("load / reload data")
        reload_btn.clicked.connect(lambda _checked=False, lid=layer_id, f=file_edit, u=url_edit: self._reload_hydrology_from_dialog(lid, f, u))
        form.addRow("provider", provider_note)
        form.addRow("data status", status)
        form.addRow("source policy", mode_combo)
        form.addRow("local GeoJSON", file_edit)
        form.addRow("GeoJSON URL", url_edit)
        form.addRow("data", reload_btn)
        strict_note = self.QtWidgets.QLabel("Strict source ports feed HydroLAKES/HydroRIVERS/MERIT/OSM adapter placeholders. Fill file or URL, then click the matching apply button.")
        strict_note.setWordWrap(True)
        form.addRow("strict note", strict_note)
        for port in HYDROLOGY_STRICT_PROVIDER_PORTS.get(layer_id, []):
            strict_file_edit = self.QtWidgets.QLineEdit(getattr(self.controller.args, port["file_attr"], None) or "")
            strict_url_edit = self.QtWidgets.QLineEdit(getattr(self.controller.args, port["url_attr"], None) or "")
            strict_apply_btn = self.QtWidgets.QPushButton(f"use {port['label']}")
            strict_apply_btn.clicked.connect(
                lambda _checked=False, lid=layer_id, pid=port["id"], f=strict_file_edit, u=strict_url_edit: self._reload_hydrology_strict_from_dialog(lid, pid, f, u)
            )
            form.addRow(f"{port['label']} file", strict_file_edit)
            form.addRow(f"{port['label']} URL", strict_url_edit)
            form.addRow(f"{port['label']} apply", strict_apply_btn)
        metadata_note = self.QtWidgets.QLabel("Strict metadata is shared by strict hydrology sources and is written into provider manifests.")
        metadata_note.setWordWrap(True)
        version_edit = self.QtWidgets.QLineEdit(getattr(self.controller.args, "hydrology_source_version", "") or "")
        license_edit = self.QtWidgets.QLineEdit(getattr(self.controller.args, "hydrology_license", "") or "")
        projection_edit = self.QtWidgets.QLineEdit(getattr(self.controller.args, "hydrology_projection", "") or "")
        attribution_edit = self.QtWidgets.QLineEdit(getattr(self.controller.args, "hydrology_attribution", "") or "")
        schema_note_edit = self.QtWidgets.QLineEdit(getattr(self.controller.args, "hydrology_schema_note", "") or "")
        metadata_btn = self.QtWidgets.QPushButton("apply strict metadata")
        metadata_btn.clicked.connect(
            lambda _checked=False, v=version_edit, l=license_edit, p=projection_edit, a=attribution_edit, s=schema_note_edit: self._apply_hydrology_strict_metadata(v, l, p, a, s)
        )
        form.addRow("metadata note", metadata_note)
        form.addRow("source version", version_edit)
        form.addRow("license", license_edit)
        form.addRow("projection", projection_edit)
        form.addRow("attribution", attribution_edit)
        form.addRow("schema note", schema_note_edit)
        form.addRow("metadata", metadata_btn)
        form.addRow("opacity", self._double_spin(getattr(self.controller.args, f"{prefix}_opacity"), 0.0, 1.0, 0.05, lambda value, lid=layer_id: self.controller.set_hydrology_opacity(lid, value)))
        form.addRow("line width", self._int_spin(getattr(self.controller.args, f"{prefix}_width"), 1, 10, 1, lambda value, lid=layer_id: self.controller.set_hydrology_width(lid, value)))

    def _reload_hydrology_from_dialog(self, layer_id: str, file_edit, url_edit) -> None:
        self.window.setCursor(self.QtCore.Qt.CursorShape.WaitCursor)
        setup_startup_progress(True)
        try:
            self.controller.reload_hydrology_layer(layer_id, file_edit.text(), url_edit.text())
            self.image.set_data(self.controller.render_if_needed(force=True))
            self.rebuild_layer_list()
        finally:
            close_startup_progress()
            self.window.unsetCursor()

    def _reload_hydrology_strict_from_dialog(self, layer_id: str, port_id: str, file_edit, url_edit) -> None:
        self.window.setCursor(self.QtCore.Qt.CursorShape.WaitCursor)
        setup_startup_progress(True)
        try:
            self.controller.set_hydrology_strict_source(layer_id, port_id, file_edit.text(), url_edit.text())
            self.image.set_data(self.controller.render_if_needed(force=True))
            self.rebuild_layer_list()
        finally:
            close_startup_progress()
            self.window.unsetCursor()

    def _apply_hydrology_strict_metadata(self, version_edit, license_edit, projection_edit, attribution_edit, schema_note_edit) -> None:
        self.controller.set_hydrology_strict_metadata(
            version_edit.text(),
            license_edit.text(),
            projection_edit.text(),
            attribution_edit.text(),
            schema_note_edit.text(),
        )
        self.rebuild_layer_list()

    def _set_hydrology_source_mode(self, mode: str) -> None:
        self.controller.set_hydrology_source_mode(mode)

    def _build_boundary_settings(self, form, layer_id: str) -> None:
        opacity_attr = {"borders": "border_opacity", "territorial_sea": "territorial_sea_opacity", "eez": "eez_opacity", "high_seas": "high_seas_opacity"}[layer_id]
        width_attr = {"borders": "border_width", "territorial_sea": "territorial_sea_width", "eez": "eez_width", "high_seas": "high_seas_width"}[layer_id]
        provider = LAYER_PROVIDER_REGISTRY.get(layer_id, {})
        provider_note = self.QtWidgets.QLabel(f"provider: {provider.get('provider', 'unregistered')}\ninput: {provider.get('renderer_input', 'unknown')}")
        provider_note.setWordWrap(True)
        status = self.QtWidgets.QLabel(self.controller.boundary_layer_status_text(layer_id))
        status.setWordWrap(True)
        file_edit = self.QtWidgets.QLineEdit(getattr(self.controller.args, f"{layer_id}_file", None) or "")
        url_edit = self.QtWidgets.QLineEdit(getattr(self.controller.args, f"{layer_id}_url", None) or "")
        default_url = default_boundary_url(layer_id)
        if default_url and not url_edit.text():
            url_edit.setPlaceholderText(default_url)
        reload_btn = self.QtWidgets.QPushButton("load / reload data")
        reload_btn.clicked.connect(lambda _checked=False, lid=layer_id, f=file_edit, u=url_edit: self._reload_boundary_from_dialog(lid, f, u))
        form.addRow("provider", provider_note)
        form.addRow("data status", status)
        form.addRow("local file", file_edit)
        form.addRow("WFS / GeoJSON URL", url_edit)
        form.addRow("data", reload_btn)
        form.addRow("opacity", self._double_spin(getattr(self.controller.args, opacity_attr), 0.0, 1.0, 0.05, lambda value, lid=layer_id: self.controller.set_boundary_opacity(lid, value)))
        form.addRow("line width", self._int_spin(getattr(self.controller.args, width_attr), 1, 12, 1, lambda value, lid=layer_id: self.controller.set_boundary_width(lid, value)))

    def _reload_boundary_from_dialog(self, layer_id: str, file_edit, url_edit) -> None:
        self.window.setCursor(self.QtCore.Qt.CursorShape.WaitCursor)
        setup_startup_progress(True)
        try:
            self.controller.reload_boundary_layer(layer_id, file_edit.text(), url_edit.text())
            self.image.set_data(self.controller.render_if_needed(force=True))
            self.rebuild_layer_list()
        finally:
            close_startup_progress()
            self.window.unsetCursor()

    def _build_scale_settings(self, form) -> None:
        form.addRow("opacity", self._double_spin(self.controller.args.scale_bar_opacity, 0.0, 1.0, 0.05, self._set_scale_opacity_from_dialog))
        reset_btn = self.QtWidgets.QPushButton("reset position")
        reset_btn.clicked.connect(self._reset_scale_bar_position)
        form.addRow("position", reset_btn)

    def _set_scale_opacity_from_dialog(self, value: float) -> None:
        self.controller.set_scale_bar_opacity(value)
        self.update_scale_bar_visuals()

    def _reset_scale_bar_position(self) -> None:
        self.controller.set_scale_bar_position(28.0, self.controller.height - 34.0)
        self.update_scale_bar_visuals()

    def update_scale_bar_visuals(self) -> None:
        visible = bool(self.controller.layer_visible.get("scale", True) and self.controller.args.scale_bar)
        for visual in self.scale_visuals:
            visual.visible = visible
        if not visible:
            return

        x0, y0, x1, distance_km = scale_bar_geometry(
            self.controller.width,
            self.controller.height,
            self.controller.zoom,
            self.controller.args.scale_bar_x,
            self.controller.args.scale_bar_y,
        )
        opacity = float(self.controller.args.scale_bar_opacity)
        opacity = max(0.0, min(opacity, 1.0))
        line_pos = np.asarray([[x0, y0], [x1, y0]], dtype=np.float32)
        self.scale_shadow.set_data(pos=np.asarray([[x0, y0 + 2], [x1, y0 + 2]], dtype=np.float32), color=(0.0, 0.0, 0.0, min(0.75, opacity)))
        self.scale_line.set_data(pos=line_pos, color=(1.0, 1.0, 1.0, opacity))
        self.scale_left_tick.set_data(
            pos=np.asarray([[x0, y0 - 7], [x0, y0 + 7]], dtype=np.float32),
            color=(1.0, 1.0, 1.0, opacity),
        )
        self.scale_right_tick.set_data(
            pos=np.asarray([[x1, y0 - 7], [x1, y0 + 7]], dtype=np.float32),
            color=(1.0, 1.0, 1.0, opacity),
        )
        self.scale_text.text = f"{distance_km:g} km"
        self.scale_text.pos = (x0, y0 - 10)
        self.scale_text.color = (1.0, 1.0, 1.0, min(1.0, opacity + 0.05))

    def _group(self, title, widgets):
        box = self.QtWidgets.QGroupBox(title)
        layout = self.QtWidgets.QVBoxLayout(box)
        for widget in widgets:
            layout.addWidget(widget)
        return box

    def _form_group(self, title, rows):
        box = self.QtWidgets.QGroupBox(title)
        form = self.QtWidgets.QFormLayout(box)
        for label, widget in rows:
            form.addRow(label, widget)
        return box

    def _slider(self, min_value, max_value, value, callback):
        slider = self.QtWidgets.QSlider(self.QtCore.Qt.Orientation.Horizontal)
        slider.setRange(min_value, max_value)
        slider.setValue(value)
        slider.valueChanged.connect(callback)
        return slider

    def _status_text(self) -> str:
        return self.controller.mode_label() + " | " + self.controller.basemap_lod_label() + " | " + (
            self.controller.title()
            .replace("AIS/ADS-B Globe", "AIS/ADS-B \u5730\u7403\u5100")
            .replace("visible", "\u53ef\u898b")
            .replace("rendered", "\u5df2\u6e32\u67d3")
            .replace("render", "\u6e32\u67d3")
            .replace("fps", "FPS")
            .replace("zoom", "\u7e2e\u653e")
            .replace("flip lon", "\u7d93\u5ea6\u7ffb\u8f49")
            .replace("lat", "\u7def\u5ea6")
        )

    def update_data_fetch_visuals(self) -> None:
        if not hasattr(self, "data_fetch_label"):
            return
        snapshot = self.controller.data_fetch_progress_snapshot()
        self.data_fetch_label.setText(str(snapshot.get("label", "資料快取尚未開始")))
        self.data_fetch_progress.setValue(int(snapshot.get("percent", 0)))
        stage = str(snapshot.get("stage", "idle"))
        if stage in {"failed", "missing"}:
            self.data_fetch_progress.setFormat("資料讀取失敗 / 缺少來源")
        elif snapshot.get("active", False):
            self.data_fetch_progress.setFormat("讀取中 %p%")
        elif stage in {"cache-hit", "memory-cache-hit"}:
            self.data_fetch_progress.setFormat("使用快取 %p%")
        elif stage in {"done", "cache-write", "normalized"}:
            self.data_fetch_progress.setFormat("完成 %p%")
        else:
            self.data_fetch_progress.setFormat("%p%")

    def on_vehicle_icons_changed(self, state: int) -> None:
        enabled = state == self.QtCore.Qt.CheckState.Checked.value
        self.controller.set_vehicle_icons(enabled)
        self.rebuild_layer_list()

    def on_terrain_contours_changed(self, state: int) -> None:
        enabled = state == self.QtCore.Qt.CheckState.Checked.value
        self.controller.set_terrain_contours(enabled)
        self.rebuild_layer_list()

    def on_color_mode(self, index: int) -> None:
        value = self.color_combo.itemData(index) or "speed"
        self.controller.set_color_mode(value)
        if value == "density":
            self.legend_label.setText("AIS 密度：越暖、越亮代表同一像素內船隻越多。")
        else:
            self.legend_label.setText("AIS 速度：青色=低速，綠色=中速，黃色/紅色=高速。")

    def on_aircraft_color_mode(self, index: int) -> None:
        value = self.aircraft_color_combo.itemData(index) or "altitude"
        self.controller.set_aircraft_color_mode(value)
        if value == "altitude":
            self.legend_label.setText("ADS-B 高度：藍色=低空，紫色=中高空，黃色=高空。")
        elif value == "speed":
            self.legend_label.setText("ADS-B 速度：藍色=低速，綠色=中速，橘紅色=高速。")
        else:
            self.legend_label.setText("ADS-B 密度：越暖、越亮代表同一像素內飛機越多。")

    def on_point_px(self, value: int) -> None:
        self.controller.set_point_px(value)

    def on_aircraft_point_px(self, value: int) -> None:
        self.controller.set_aircraft_point_px(value)

    def on_horizon(self, value: int) -> None:
        self.controller.set_horizon_eps(value / 1000.0)

    def on_aircraft_horizon(self, value: int) -> None:
        self.controller.set_aircraft_horizon_eps(value / 1000.0)

    def on_flight_speed(self, value: float) -> None:
        self.controller.set_flight_speed_deg(value)

    def apply_keyboard_flight(self) -> None:
        if not self.keys_down:
            return
        speed = float(self.controller.args.flight_speed_deg)
        yaw_delta = 0.0
        zoom_scale = 1.0
        if "a" in self.keys_down:
            yaw_delta += speed
        if "d" in self.keys_down:
            yaw_delta -= speed
        if "w" in self.keys_down:
            zoom_scale *= 0.965
        if "s" in self.keys_down:
            zoom_scale *= 1.035
        if "q" in self.keys_down:
            zoom_scale *= 0.94
        if "e" in self.keys_down:
            zoom_scale *= 1.06
        if yaw_delta or zoom_scale != 1.0:
            self.controller.set_interaction_active(True)
            self.controller.fly_camera(yaw_delta, 0.0, zoom_scale)

    def on_timer(self) -> None:
        self.fps_recorder.tick()
        self.apply_keyboard_flight()
        self.controller.update_basemap_lod()
        self.advance_timeline()
        frame = self.controller.render_if_needed(force=False)
        if frame is not None:
            self.image.set_data(frame)
        title = self._status_text()
        self.hud.text = title
        if hasattr(self, "lod_label"):
            self.lod_label.setText(self.controller.basemap_lod_label())
        self.status_label.setText(title)
        self.selection_label.setText(self.controller.selected_info_text())
        self.update_data_fetch_visuals()
        self.update_scale_bar_visuals()
        self._update_timeline_visibility()
        self.window.setWindowTitle(title)
        self.canvas.update()

    def on_mouse_press(self, event) -> None:
        if event.button == 1:
            if "scale" not in self.locked_layers and self.controller.hit_test_scale_bar(float(event.pos[0]), float(event.pos[1])):
                self.dragging_scale_bar = True
                self.scale_bar_drag_offset = (
                    float(event.pos[0]) - float(self.controller.args.scale_bar_x),
                    float(event.pos[1]) - float(self.controller.args.scale_bar_y),
                )
                return
            self.dragging = False
            self.mouse_down_pos = event.pos
            self.last_pos = event.pos

    def on_mouse_release(self, event) -> None:
        if event.button == 1:
            if self.dragging_scale_bar:
                self.dragging_scale_bar = False
                self.mouse_down_pos = None
                self.last_pos = None
                return
            was_dragging = self.dragging
            if self.mouse_down_pos is not None and not self.dragging:
                self.controller.pick_vehicle(float(event.pos[0]), float(event.pos[1]))
                self.selection_label.setText(self.controller.selected_info_text())
            if was_dragging:
                self.controller.set_interaction_active(False)
            self.dragging = False
            self.mouse_down_pos = None
            self.last_pos = None

    def on_mouse_move(self, event) -> None:
        if self.data_mode == "timeseries" and float(event.pos[1]) > float(self.controller.height) - 90.0:
            self._show_timeline_temporarily()
        if self.dragging_scale_bar:
            self.controller.set_scale_bar_position(
                float(event.pos[0]) - self.scale_bar_drag_offset[0],
                float(event.pos[1]) - self.scale_bar_drag_offset[1],
            )
            self.update_scale_bar_visuals()
            return
        if self.last_pos is None:
            return
        dx = event.pos[0] - self.last_pos[0]
        dy = event.pos[1] - self.last_pos[1]
        if self.mouse_down_pos is not None:
            total_dx = event.pos[0] - self.mouse_down_pos[0]
            total_dy = event.pos[1] - self.mouse_down_pos[1]
            if total_dx * total_dx + total_dy * total_dy > 16.0:
                self.dragging = True
        if self.dragging:
            self.controller.set_interaction_active(True)
            self.controller.rotate(-dx, -dy)
        else:
            self.controller.set_boundary_hover(float(event.pos[0]), float(event.pos[1]))
        self.last_pos = event.pos

    def on_mouse_wheel(self, event) -> None:
        self.controller.apply_zoom(0.88 ** event.delta[1])

    def on_key_press(self, event) -> None:
        key = event.key.name if hasattr(event.key, "name") else str(event.key)
        key_lower = str(key).lower()
        if key_lower in {"w", "a", "s", "d", "q", "e"}:
            self.keys_down.add(key_lower)
        if key in {"R", "r"}:
            self.controller.reset_view()
        elif key in {"M", "m"}:
            self.controller.toggle_longitude_flip()
        elif key in {"N", "n"}:
            self.controller.toggle_latitude_flip()

    def on_key_release(self, event) -> None:
        key = event.key.name if hasattr(event.key, "name") else str(event.key)
        key_lower = str(key).lower()
        self.keys_down.discard(key_lower)
        if not self.keys_down:
            self.controller.set_interaction_active(False)

    def run(self) -> None:
        self.window.show()
        self.app.exec()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Taichi + Datashader + VisPy/Qt realtime AIS globe prototype")
    bool_action = argparse.BooleanOptionalAction

    parser.add_argument("--width", type=int, default=int(os.environ.get("AIS_RENDER_WIDTH", "1280")))
    parser.add_argument("--height", type=int, default=int(os.environ.get("AIS_RENDER_HEIGHT", "720")))
    parser.add_argument("--ui", choices=["qt", "vispy"], default=os.environ.get("AIS_RENDER_UI", "qt"))
    parser.add_argument("--vispy-backend", default=os.environ.get("VISPY_BACKEND", "glfw"))
    parser.add_argument("--ti-arch", default=os.environ.get("TAICHI_ARCH", "gpu"))
    parser.add_argument("--headless", action=bool_action, default=False)
    parser.add_argument("--once", action=bool_action, default=False)
    parser.add_argument("--output", default=None)
    parser.add_argument("--fps-log", default=str(CACHE_DIR / "fps_log.jsonl"))
    parser.add_argument("--demo-closed-loop", action=bool_action, default=parse_bool(os.environ.get("DEMO_CLOSED_LOOP"), False))
    parser.add_argument("--write-demo-packet", default=os.environ.get("WRITE_DEMO_PACKET"))
    parser.add_argument("--print-renderer-capabilities", action=bool_action, default=False)
    parser.add_argument("--print-layer-manifest", action=bool_action, default=False)

    parser.add_argument("--topo-step", type=int, default=int(os.environ.get("TOPO_STEP", "16")))
    parser.add_argument("--topo-source", choices=["gebco", "synthetic"], default=os.environ.get("TOPO_SOURCE", "gebco"))
    parser.add_argument("--topo-chunk-rows", type=int, default=int(os.environ.get("TOPO_CHUNK_ROWS", "256")))
    parser.add_argument("--land-mask-source", default=os.environ.get("LAND_MASK_SOURCE", "naturalearth"))
    parser.add_argument("--ice-source", default=os.environ.get("ICE_SOURCE", "auto"))
    parser.add_argument("--forest-source", default=os.environ.get("FOREST_SOURCE", "auto"))
    parser.add_argument("--forest-density-file", default=os.environ.get("FOREST_DENSITY_FILE"))
    parser.add_argument("--star-mag-limit", type=float, default=float(os.environ.get("STAR_MAG_LIMIT", "6.0")))
    parser.add_argument("--show-stars", action=bool_action, default=True)
    parser.add_argument("--show-grid", action=bool_action, default=True)
    parser.add_argument("--bump-scale", type=float, default=float(os.environ.get("BUMP_SCALE", "0.045")))
    parser.add_argument("--sea-level-m", type=float, default=float(os.environ.get("SEA_LEVEL_M", "0.0")))
    parser.add_argument("--map-projection", default=os.environ.get("MAP_PROJECTION", "globe"))
    parser.add_argument("--style-profile", choices=list(STYLE_PROFILE_REGISTRY.keys()), default=os.environ.get("STYLE_PROFILE", "scientific"))
    parser.add_argument("--flip-longitude", action=bool_action, default=parse_bool(os.environ.get("FLIP_LONGITUDE"), False))
    parser.add_argument("--flip-latitude", action=bool_action, default=parse_bool(os.environ.get("FLIP_LATITUDE"), False))

    parser.add_argument("--ais-url", default=os.environ.get("AIS_URL"))
    parser.add_argument("--ais-file", default=os.environ.get("AIS_FILE"))
    parser.add_argument("--ais-db-url", default=os.environ.get("AIS_DB_URL"))
    parser.add_argument("--ais-db-query", default=os.environ.get("AIS_DB_QUERY"))
    parser.add_argument("--ais-db-table", default=os.environ.get("AIS_DB_TABLE", "ais_positions"))
    parser.add_argument("--ais-db-limit", type=int, default=int(os.environ.get("AIS_DB_LIMIT", "25000")))
    parser.add_argument("--timeout", type=float, default=float(os.environ.get("AIS_TIMEOUT", "20.0")))
    parser.add_argument("--refresh", type=float, default=float(os.environ.get("AIS_REFRESH", "2.0")))
    parser.add_argument("--max-age-minutes", type=float, default=float(os.environ.get("AIS_MAX_AGE_MINUTES", "1440.0")))
    parser.add_argument("--color-by", choices=["speed", "density"], default=os.environ.get("AIS_COLOR_BY", "speed"))
    parser.add_argument("--point-px", type=int, default=int(os.environ.get("AIS_POINT_PX", "2")))
    parser.add_argument("--speed-min", type=float, default=float(os.environ.get("AIS_SPEED_MIN", "0.0")))
    parser.add_argument("--speed-max", type=float, default=float(os.environ.get("AIS_SPEED_MAX", "30.0")))
    parser.add_argument("--ais-horizon-eps", type=float, default=float(os.environ.get("AIS_HORIZON_EPS", "0.006")))
    parser.add_argument("--ais-sample-ratio", type=float, default=float(os.environ.get("AIS_SAMPLE_RATIO", "1.0")))

    parser.add_argument("--aircraft-url", default=os.environ.get("AIRCRAFT_URL") or os.environ.get("ADSB_URL"))
    parser.add_argument("--aircraft-file", default=os.environ.get("AIRCRAFT_FILE") or os.environ.get("ADSB_FILE"))
    parser.add_argument("--aircraft-db-url", default=os.environ.get("AIRCRAFT_DB_URL") or os.environ.get("ADSB_DB_URL"))
    parser.add_argument("--aircraft-db-query", default=os.environ.get("AIRCRAFT_DB_QUERY") or os.environ.get("ADSB_DB_QUERY"))
    parser.add_argument("--aircraft-db-table", default=os.environ.get("AIRCRAFT_DB_TABLE", DEFAULT_AIRCRAFT_DB_TABLE))
    parser.add_argument("--aircraft-db-limit", type=int, default=int(os.environ.get("AIRCRAFT_DB_LIMIT", str(DEFAULT_AIRCRAFT_DB_LIMIT))))
    parser.add_argument("--aircraft-layer", action=bool_action, default=parse_bool(os.environ.get("AIRCRAFT_LAYER"), False))
    parser.add_argument("--aircraft-refresh", type=float, default=float(os.environ.get("AIRCRAFT_REFRESH", "2.0")))
    parser.add_argument("--aircraft-color-by", choices=["altitude", "speed", "density"], default=os.environ.get("AIRCRAFT_COLOR_BY", "altitude"))
    parser.add_argument("--aircraft-point-px", type=int, default=int(os.environ.get("AIRCRAFT_POINT_PX", "2")))
    parser.add_argument("--aircraft-max-age-minutes", type=float, default=float(os.environ.get("AIRCRAFT_MAX_AGE_MINUTES", "60.0")))
    parser.add_argument("--aircraft-altitude-exaggeration", type=float, default=float(os.environ.get("AIRCRAFT_ALTITUDE_EXAGGERATION", "35.0")))
    parser.add_argument("--aircraft-horizon-eps", type=float, default=float(os.environ.get("AIRCRAFT_HORIZON_EPS", "0.006")))
    parser.add_argument("--aircraft-sample-ratio", type=float, default=float(os.environ.get("AIRCRAFT_SAMPLE_RATIO", "1.0")))
    parser.add_argument("--pin-file", default=os.environ.get("PIN_FILE"))
    parser.add_argument("--pin-json", default=os.environ.get("PIN_JSON"))
    parser.add_argument("--pin-layer", action=bool_action, default=parse_bool(os.environ.get("PIN_LAYER"), True))
    parser.add_argument("--pin-size", type=int, default=int(os.environ.get("PIN_SIZE", "9")))
    parser.add_argument("--pin-horizon-eps", type=float, default=float(os.environ.get("PIN_HORIZON_EPS", "0.006")))
    parser.add_argument("--pin-label-mode", choices=["auto", "selected", "priority", "hidden"], default=os.environ.get("PIN_LABEL_MODE", "auto"))
    parser.add_argument("--pin-label-min-priority", type=int, default=int(os.environ.get("PIN_LABEL_MIN_PRIORITY", "50")))

    parser.add_argument("--adaptive-sampling", action=bool_action, default=parse_bool(os.environ.get("ADAPTIVE_SAMPLING"), True))
    parser.add_argument("--target-fps", type=float, default=float(os.environ.get("TARGET_FPS", "30.0")))
    parser.add_argument("--min-sample-ratio", type=float, default=float(os.environ.get("MIN_SAMPLE_RATIO", "0.05")))
    parser.add_argument("--vehicle-icons", action=bool_action, default=parse_bool(os.environ.get("VEHICLE_ICONS"), False))
    parser.add_argument("--icon-max-count", type=int, default=int(os.environ.get("ICON_MAX_COUNT", "800")))
    parser.add_argument("--icon-pick-radius", type=float, default=float(os.environ.get("ICON_PICK_RADIUS", "14.0")))

    parser.add_argument("--hydrology-source-mode", choices=["lod", "manual", "strict"], default=os.environ.get("HYDROLOGY_SOURCE_MODE", "lod"))
    parser.add_argument("--hydrology-source", default=os.environ.get("HYDROLOGY_SOURCE", "naturalearth"))
    parser.add_argument("--hydrology-decimate", type=int, default=int(os.environ.get("HYDROLOGY_DECIMATE", "2")))
    parser.add_argument("--hydrolakes-file", default=os.environ.get("HYDROLAKES_FILE"))
    parser.add_argument("--hydrolakes-url", default=os.environ.get("HYDROLAKES_URL"))
    parser.add_argument("--hydrorivers-file", default=os.environ.get("HYDRORIVERS_FILE"))
    parser.add_argument("--hydrorivers-url", default=os.environ.get("HYDRORIVERS_URL"))
    parser.add_argument("--merit-hydro-file", default=os.environ.get("MERIT_HYDRO_FILE"))
    parser.add_argument("--merit-hydro-url", default=os.environ.get("MERIT_HYDRO_URL"))
    parser.add_argument("--osm-water-file", default=os.environ.get("OSM_WATER_FILE"))
    parser.add_argument("--osm-water-url", default=os.environ.get("OSM_WATER_URL"))
    parser.add_argument("--osm-waterways-file", default=os.environ.get("OSM_WATERWAYS_FILE"))
    parser.add_argument("--osm-waterways-url", default=os.environ.get("OSM_WATERWAYS_URL"))
    parser.add_argument("--hydrology-source-version", default=os.environ.get("HYDROLOGY_SOURCE_VERSION", ""))
    parser.add_argument("--hydrology-license", default=os.environ.get("HYDROLOGY_LICENSE", ""))
    parser.add_argument("--hydrology-projection", default=os.environ.get("HYDROLOGY_PROJECTION", ""))
    parser.add_argument("--hydrology-attribution", default=os.environ.get("HYDROLOGY_ATTRIBUTION", ""))
    parser.add_argument("--hydrology-schema-note", default=os.environ.get("HYDROLOGY_SCHEMA_NOTE", ""))
    parser.add_argument("--lake-file", default=os.environ.get("LAKE_FILE"))
    parser.add_argument("--lake-url", default=os.environ.get("LAKE_URL"))
    parser.add_argument("--lake-opacity", type=float, default=float(os.environ.get("LAKE_OPACITY", "0.55")))
    parser.add_argument("--lake-width", type=int, default=int(os.environ.get("LAKE_WIDTH", "1")))
    parser.add_argument("--lake-layer", action=bool_action, default=True)
    parser.add_argument("--river-file", default=os.environ.get("RIVER_FILE"))
    parser.add_argument("--river-url", default=os.environ.get("RIVER_URL"))
    parser.add_argument("--river-opacity", type=float, default=float(os.environ.get("RIVER_OPACITY", "0.48")))
    parser.add_argument("--river-width", type=int, default=int(os.environ.get("RIVER_WIDTH", "1")))
    parser.add_argument("--river-layer", action=bool_action, default=True)
    parser.add_argument("--boundary-decimate", type=int, default=int(os.environ.get("BOUNDARY_DECIMATE", "2")))
    parser.add_argument("--border-file", default=os.environ.get("BORDER_FILE"))
    parser.add_argument("--border-url", default=os.environ.get("BORDER_URL"))
    parser.add_argument("--border-layer", action=bool_action, default=parse_bool(os.environ.get("BORDER_LAYER"), True))
    parser.add_argument("--territorial-sea-file", default=os.environ.get("TERRITORIAL_SEA_FILE"))
    parser.add_argument("--territorial-sea-url", default=os.environ.get("TERRITORIAL_SEA_URL"))
    parser.add_argument("--territorial-sea-layer", action=bool_action, default=parse_bool(os.environ.get("TERRITORIAL_SEA_LAYER"), False))
    parser.add_argument("--eez-file", default=os.environ.get("EEZ_FILE"))
    parser.add_argument("--eez-url", default=os.environ.get("EEZ_URL"))
    parser.add_argument("--eez-layer", action=bool_action, default=parse_bool(os.environ.get("EEZ_LAYER"), False))
    parser.add_argument("--high-seas-file", default=os.environ.get("HIGH_SEAS_FILE"))
    parser.add_argument("--high-seas-url", default=os.environ.get("HIGH_SEAS_URL"))
    parser.add_argument("--high-seas-layer", action=bool_action, default=parse_bool(os.environ.get("HIGH_SEAS_LAYER"), False))

    parser.add_argument("--ice-opacity", type=float, default=float(os.environ.get("ICE_OPACITY", "0.82")))
    parser.add_argument("--ice-specular", type=float, default=float(os.environ.get("ICE_SPECULAR", "0.35")))
    parser.add_argument("--ice-blue", type=float, default=float(os.environ.get("ICE_BLUE", "0.18")))
    parser.add_argument("--ocean-material", action=bool_action, default=parse_bool(os.environ.get("OCEAN_MATERIAL"), True))
    parser.add_argument("--ocean-condition-source", choices=list(OCEAN_PROVIDER_REGISTRY.keys()), default=os.environ.get("OCEAN_CONDITION_SOURCE", "manual"))
    parser.add_argument("--ocean-condition-file", default=os.environ.get("OCEAN_CONDITION_FILE"))
    parser.add_argument("--ocean-condition-url", default=os.environ.get("OCEAN_CONDITION_URL"))
    parser.add_argument("--ocean-noaa-ww3-url", default=os.environ.get("OCEAN_NOAA_WW3_URL"))
    parser.add_argument("--ocean-hycom-url", default=os.environ.get("OCEAN_HYCOM_URL"))
    parser.add_argument("--ocean-copernicus-url", default=os.environ.get("OCEAN_COPERNICUS_URL"))
    parser.add_argument("--ocean-grid-file", default=os.environ.get("OCEAN_GRID_FILE"))
    parser.add_argument("--ocean-wave-strength", type=float, default=float(os.environ.get("OCEAN_WAVE_STRENGTH", "0.22")))
    parser.add_argument("--ocean-roughness", type=float, default=float(os.environ.get("OCEAN_ROUGHNESS", "0.28")))
    parser.add_argument("--ocean-foam", type=float, default=float(os.environ.get("OCEAN_FOAM", "0.12")))
    parser.add_argument("--ocean-animation-fps", type=float, default=float(os.environ.get("OCEAN_ANIMATION_FPS", "24.0")))
    parser.add_argument("--ocean-condition-refresh", type=float, default=float(os.environ.get("OCEAN_CONDITION_REFRESH", "60.0")))
    parser.add_argument("--ocean-material-scale", type=float, default=float(os.environ.get("OCEAN_MATERIAL_SCALE", "1.0")))
    parser.add_argument("--ocean-responsive", action=bool_action, default=parse_bool(os.environ.get("OCEAN_RESPONSIVE"), True))
    parser.add_argument("--ocean-provider-lat", type=float, default=float(os.environ.get("OCEAN_PROVIDER_LAT", "0.0")))
    parser.add_argument("--ocean-provider-lon", type=float, default=float(os.environ.get("OCEAN_PROVIDER_LON", "0.0")))

    parser.add_argument("--cloud-opacity", type=float, default=float(os.environ.get("CLOUD_OPACITY", "0.25")))
    parser.add_argument("--cloud-coverage", type=float, default=float(os.environ.get("CLOUD_COVERAGE", "0.45")))
    parser.add_argument("--cloud-detail", type=float, default=float(os.environ.get("CLOUD_DETAIL", "0.6")))
    parser.add_argument("--cloud-animation-fps", type=float, default=float(os.environ.get("CLOUD_ANIMATION_FPS", "12.0")))
    parser.add_argument("--terrain-contours", action=bool_action, default=parse_bool(os.environ.get("TERRAIN_CONTOURS"), False))
    parser.add_argument("--contour-interval-m", type=float, default=float(os.environ.get("CONTOUR_INTERVAL_M", "1000.0")))
    parser.add_argument("--contour-line-width-m", type=float, default=float(os.environ.get("CONTOUR_LINE_WIDTH_M", "35.0")))
    parser.add_argument("--contour-opacity", type=float, default=float(os.environ.get("CONTOUR_OPACITY", "0.42")))
    parser.add_argument("--scale-bar", action=bool_action, default=parse_bool(os.environ.get("SCALE_BAR"), True))
    parser.add_argument("--scale-bar-x", type=float, default=float(os.environ.get("SCALE_BAR_X", "28.0")))
    parser.add_argument("--scale-bar-y", type=float, default=float(os.environ.get("SCALE_BAR_Y", "686.0")))
    parser.add_argument("--scale-bar-opacity", type=float, default=float(os.environ.get("SCALE_BAR_OPACITY", "0.88")))
    parser.add_argument("--flight-speed-deg", type=float, default=float(os.environ.get("FLIGHT_SPEED_DEG", "1.2")))
    parser.add_argument("--data-mode", choices=["static", "timeseries", "realtime"], default=os.environ.get("DATA_MODE", "realtime"))

    parser.add_argument("--border-opacity", type=float, default=float(os.environ.get("BORDER_OPACITY", "0.75")))
    parser.add_argument("--border-width", type=int, default=int(os.environ.get("BORDER_WIDTH", "1")))
    parser.add_argument("--territorial-sea-opacity", type=float, default=float(os.environ.get("TERRITORIAL_SEA_OPACITY", "0.65")))
    parser.add_argument("--territorial-sea-width", type=int, default=int(os.environ.get("TERRITORIAL_SEA_WIDTH", "1")))
    parser.add_argument("--eez-opacity", type=float, default=float(os.environ.get("EEZ_OPACITY", "0.65")))
    parser.add_argument("--eez-width", type=int, default=int(os.environ.get("EEZ_WIDTH", "1")))
    parser.add_argument("--high-seas-opacity", type=float, default=float(os.environ.get("HIGH_SEAS_OPACITY", "0.55")))
    parser.add_argument("--high-seas-width", type=int, default=int(os.environ.get("HIGH_SEAS_WIDTH", "1")))
    return parser



def renderer_capabilities_packet() -> dict[str, object]:
    return {
        "schema": "rrkal_displaytools.renderer_capabilities.v1",
        "renderer": "taichi_global_bathymetry",
        "style_profiles": list(STYLE_PROFILE_REGISTRY.keys()),
        "ui_backends": ["qt", "vispy"],
        "topography_sources": ["gebco", "synthetic"],
        "data_modes": ["static", "timeseries", "realtime"],
        "layer_flags": [
            "show-grid",
            "show-stars",
            "lake-layer",
            "river-layer",
            "border-layer",
            "territorial-sea-layer",
            "eez-layer",
            "high-seas-layer",
            "aircraft-layer",
            "pin-layer",
            "ocean-material",
            "terrain-contours",
            "scale-bar",
            "vehicle-icons",
        ],
        "material_controls": [
            "ocean-wave-strength",
            "ocean-roughness",
            "ocean-foam",
            "ocean-material-scale",
            "ice-opacity",
            "ice-specular",
            "ice-blue",
            "cloud-opacity",
            "cloud-coverage",
            "cloud-detail",
        ],
        "pin_overlay": pin_projection_contract_packet(),
        "pin_selected_state": "selected_pin_id from --pin-file/--pin-json is rendered with a highlighted marker ring",
        "pin_marker_styles": pin_marker_style_packet(),
        "pin_controls": [
            "pin-file",
            "pin-json",
            "pin-layer",
            "pin-size",
            "pin-horizon-eps",
            "pin-label-mode",
            "pin-label-min-priority",
        ],
        "rrkal_boundary": {
            "displaytools_owns": [
                "renderer launch flags",
                "style and layer rendering controls",
                "Taichi visualization frontend",
            ],
            "rrkal_owns": [
                "dataset discovery/download/import",
                "install registry",
                "manifest/cache governance",
            ],
        },
    }


def renderer_layer_manifest_packet() -> dict[str, object]:
    return {
        "schema": "rrkal_displaytools.layer_manifest.v1",
        "renderer": "taichi_global_bathymetry",
        "groups": [
            {
                "id": "hydrology",
                "label": "Hydrology",
                "description": "Inland water and river display layers.",
                "layers": [
                    {"id": "lake_layer", "flag": "lake-layer", "default": True},
                    {"id": "river_layer", "flag": "river-layer", "default": True},
                ],
            },
            {
                "id": "boundaries",
                "label": "Boundaries",
                "description": "Political and maritime boundary overlays.",
                "layers": [
                    {"id": "border_layer", "flag": "border-layer", "default": True},
                    {"id": "territorial_sea_layer", "flag": "territorial-sea-layer", "default": False},
                    {"id": "eez_layer", "flag": "eez-layer", "default": False},
                    {"id": "high_seas_layer", "flag": "high-seas-layer", "default": False},
                ],
            },
            {
                "id": "transport",
                "label": "Transport",
                "description": "Traffic and vehicle overlays.",
                "layers": [
                    {"id": "aircraft_layer", "flag": "aircraft-layer", "default": False},
                    {"id": "vehicle_icons", "flag": "vehicle-icons", "default": False},
                ],
            },
            {
                "id": "visual_aids",
                "label": "Visual aids",
                "description": "Reference and orientation aids.",
                "layers": [
                    {"id": "show_grid", "flag": "show-grid", "default": True},
                    {"id": "show_stars", "flag": "show-stars", "default": True},
                    {"id": "terrain_contours", "flag": "terrain-contours", "default": False},
                    {"id": "scale_bar", "flag": "scale-bar", "default": True},
                ],
            },
            {
                "id": "material",
                "label": "Material",
                "description": "Surface material effects.",
                "layers": [
                    {"id": "ocean_material", "flag": "ocean-material", "default": True},
                ],
            },
            {
                "id": "preset",
                "label": "Preset",
                "description": "High-level launch presets.",
                "layers": [
                    {"id": "demo_closed_loop", "flag": "demo-closed-loop", "default": False},
                ],
            },
        ],
        "style_profiles": list(STYLE_PROFILE_REGISTRY.keys()),
        "material_controls": [
            {"id": "ocean_wave_strength", "flag": "ocean-wave-strength", "default": 0.22},
            {"id": "ocean_roughness", "flag": "ocean-roughness", "default": 0.28},
            {"id": "ocean_foam", "flag": "ocean-foam", "default": 0.12},
        ],
    }


def apply_closed_loop_demo_defaults(args: argparse.Namespace) -> dict[str, object]:
    """Apply a bounded showcase preset without taking over RRKAL data governance."""
    if args.style_profile not in STYLE_PROFILE_REGISTRY:
        args.style_profile = "scientific"
    args.topo_source = "synthetic"
    args.topo_step = max(int(args.topo_step), 48)
    args.data_mode = "static"
    args.hydrology_source_mode = "lod"
    args.lake_layer = True
    args.river_layer = True
    args.border_layer = True
    args.ocean_material = True
    args.ocean_condition_source = "manual"
    args.ocean_wave_strength = max(float(args.ocean_wave_strength), 0.28)
    args.ocean_roughness = max(float(args.ocean_roughness), 0.32)
    args.ocean_foam = max(float(args.ocean_foam), 0.16)
    args.ocean_responsive = True
    args.terrain_contours = True
    args.scale_bar = True
    args.show_grid = True
    args.show_stars = True
    packet = {
        "schema": "rrkal_displaytools.closed_loop_demo.v1",
        "mode": "demo_closed_loop",
        "rrkal_boundary": {
            "launcher_owns": [
                "dataset discovery",
                "download/import/install registry",
                "manifest and cache asset governance",
            ],
            "displaytools_owns": [
                "renderer consumption contract",
                "Taichi globe visualization",
                "style/material/LOD display controls",
            ],
        },
        "renderer_entry": {
            "ui": args.ui,
            "projection": args.map_projection,
            "style_profile": args.style_profile,
            "topography_source": args.topo_source,
            "topography_step": args.topo_step,
        },
        "closed_loop_layers": {
            "hydrology_source_mode": args.hydrology_source_mode,
            "lake_layer": bool(args.lake_layer),
            "river_layer": bool(args.river_layer),
            "border_layer": bool(args.border_layer),
            "ocean_material": bool(args.ocean_material),
            "terrain_contours": bool(args.terrain_contours),
            "scale_bar": bool(args.scale_bar),
            "grid": bool(args.show_grid),
            "stars": bool(args.show_stars),
        },
        "ocean_material": {
            "condition_source": args.ocean_condition_source,
            "wave_strength": float(args.ocean_wave_strength),
            "roughness": float(args.ocean_roughness),
            "foam": float(args.ocean_foam),
            "responsive": bool(args.ocean_responsive),
        },
        "launch_note": "One-command bounded showcase; uses synthetic topography and does not perform RRKAL downloads.",
    }
    if args.write_demo_packet:
        packet_path = Path(args.write_demo_packet)
        packet_path.parent.mkdir(parents=True, exist_ok=True)
        packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote closed-loop demo packet: {packet_path}")
    print(json.dumps(packet, ensure_ascii=False, indent=2))
    return packet
def main(argv: list[str] | None = None) -> None:
    configure_stdio()
    args = build_parser().parse_args(argv)
    if args.print_renderer_capabilities:
        print(json.dumps(renderer_capabilities_packet(), ensure_ascii=False, indent=2))
        return
    if args.print_layer_manifest:
        print(json.dumps(renderer_layer_manifest_packet(), ensure_ascii=False, indent=2))
        return
    if args.demo_closed_loop:
        apply_closed_loop_demo_defaults(args)
    if args.scale_bar_y == 686.0 and args.height != 720:
        args.scale_bar_y = max(34.0, float(args.height) - 34.0)
    ensure_dependencies(bool(args.headless))
    init_taichi(args.ti_arch)
    controller = HybridRenderController(args)
    if args.headless or args.once:
        controller.render_if_needed(force=True)
        return
    if args.ui == "qt":
        QtHybridWindow(controller).run()
    else:
        VisPyHybridViewer(controller, args.vispy_backend).run()


if __name__ == "__main__":
    main()

