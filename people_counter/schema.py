from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

BBox = tuple[int, int, int, int]
Point = tuple[float, float]


@dataclass(frozen=True)
class Detection:
    bbox: BBox
    confidence: float
    class_id: int = 0
    label: str = "person"

    @property
    def centroid(self) -> Point:
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


@dataclass
class Track:
    track_id: int
    bbox: BBox
    confidence: float = 1.0
    missed: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def centroid(self) -> Point:
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


@dataclass(frozen=True)
class CrossingEvent:
    frame_index: int
    timestamp_sec: float
    track_id: int
    line_name: str
    direction: str
    centroid: Point

    def to_dict(self) -> dict[str, Any]:
        return {
            "frame_index": self.frame_index,
            "timestamp_sec": round(self.timestamp_sec, 3),
            "track_id": self.track_id,
            "line_name": self.line_name,
            "direction": self.direction,
            "centroid_x": round(self.centroid[0], 2),
            "centroid_y": round(self.centroid[1], 2),
        }


@dataclass
class FrameAnalytics:
    frame_index: int
    timestamp_sec: float
    active_tracks: int
    current_occupancy: int
    total_entered: int
    total_exited: int
    peak_occupancy: int
    fps: float
    latency_ms: float
    zone_counts: dict[str, int] = field(default_factory=dict)
    events: list[CrossingEvent] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        row: dict[str, Any] = {
            "frame_index": self.frame_index,
            "timestamp_sec": round(self.timestamp_sec, 3),
            "active_tracks": self.active_tracks,
            "current_occupancy": self.current_occupancy,
            "total_entered": self.total_entered,
            "total_exited": self.total_exited,
            "peak_occupancy": self.peak_occupancy,
            "fps": round(self.fps, 2),
            "latency_ms": round(self.latency_ms, 2),
        }
        for zone_name, count in self.zone_counts.items():
            row[f"zone_{zone_name}_count"] = count
        return row


@dataclass
class SessionResult:
    summary: dict[str, Any]
    frame_metrics: list[dict[str, Any]]
    events: list[dict[str, Any]]
    trajectories: list[dict[str, Any]]
    output_paths: dict[str, str]
