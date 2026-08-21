from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields, is_dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class DetectorConfig:
    model_path: str = "yolo11n.pt"
    confidence: float = 0.5
    iou: float = 0.7
    image_size: int = 640
    device: str | None = None
    classes: list[int] = field(default_factory=lambda: [0])


@dataclass
class TrackerConfig:
    backend: str = "csrt"
    iou_threshold: float = 0.3
    max_misses: int = 5
    ultralytics_tracker: str = "bytetrack.yaml"
    min_box_area: int = 64


@dataclass
class LineConfig:
    name: str = "main"
    start: tuple[int, int] = (100, 300)
    end: tuple[int, int] = (900, 300)
    in_direction: str = "negative_to_positive"
    debounce_frames: int = 12


@dataclass
class ZoneConfig:
    name: str
    points: list[tuple[int, int]]
    alert_threshold: int | None = None


@dataclass
class AnalyticsConfig:
    lines: list[LineConfig] = field(default_factory=list)
    zones: list[ZoneConfig] = field(default_factory=list)
    keep_trajectory_points: int = 300
    overcrowding_threshold: int | None = None


@dataclass
class OutputConfig:
    directory: str = "outputs"
    save_frame_metrics_csv: bool = True
    save_events_csv: bool = True
    save_trajectories_csv: bool = True
    save_summary_json: bool = True
    save_annotated_video: bool = False
    annotated_video_name: str = "annotated_output.mp4"


@dataclass
class RuntimeConfig:
    frame_skip: int = 1
    max_frames: int | None = None
    display_width: int = 960
    privacy_blur: bool = False
    draw_trajectories: bool = True
    show_fps: bool = True


@dataclass
class AppConfig:
    detector: DetectorConfig = field(default_factory=DetectorConfig)
    tracker: TrackerConfig = field(default_factory=TrackerConfig)
    analytics: AnalyticsConfig = field(default_factory=AnalyticsConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)


def load_config(path: str | Path | None = None) -> AppConfig:
    config = AppConfig()
    if path is None:
        default_path = Path("config/default.yaml")
        if not default_path.exists():
            return config
        path = default_path

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    return _from_mapping(AppConfig, _deep_merge(asdict(config), data))


def save_config(config: AppConfig, path: str | Path) -> None:
    with Path(path).open("w", encoding="utf-8") as fh:
        yaml.safe_dump(asdict(config), fh, sort_keys=False)


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _from_mapping(cls: type[Any], data: dict[str, Any]) -> Any:
    if not is_dataclass(cls):
        return data

    kwargs: dict[str, Any] = {}
    for item in fields(cls):
        if item.name not in data:
            continue
        value = data[item.name]
        if item.name == "detector":
            kwargs[item.name] = _from_mapping(DetectorConfig, value)
        elif item.name == "tracker":
            kwargs[item.name] = _from_mapping(TrackerConfig, value)
        elif item.name == "analytics":
            kwargs[item.name] = _analytics_from_mapping(value)
        elif item.name == "output":
            kwargs[item.name] = _from_mapping(OutputConfig, value)
        elif item.name == "runtime":
            kwargs[item.name] = _from_mapping(RuntimeConfig, value)
        else:
            kwargs[item.name] = value
    return cls(**kwargs)


def _analytics_from_mapping(data: dict[str, Any]) -> AnalyticsConfig:
    lines = [LineConfig(**_line_points(line)) for line in data.get("lines", [])]
    zones = [ZoneConfig(**_zone_points(zone)) for zone in data.get("zones", [])]
    values = {k: v for k, v in data.items() if k not in {"lines", "zones"}}
    return AnalyticsConfig(lines=lines, zones=zones, **values)


def _line_points(data: dict[str, Any]) -> dict[str, Any]:
    fixed = dict(data)
    if "start" in fixed:
        fixed["start"] = tuple(fixed["start"])
    if "end" in fixed:
        fixed["end"] = tuple(fixed["end"])
    return fixed


def _zone_points(data: dict[str, Any]) -> dict[str, Any]:
    fixed = dict(data)
    if "points" in fixed:
        fixed["points"] = [tuple(point) for point in fixed["points"]]
    return fixed
