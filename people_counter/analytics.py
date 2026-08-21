from __future__ import annotations

from collections import defaultdict, deque
from statistics import mean
from typing import Deque

from .config_runtime import AnalyticsConfig, LineConfig
from .geometry import point_in_polygon, point_side
from .schema import CrossingEvent, FrameAnalytics, Point, Track


class AnalyticsEngine:
    """Converts tracks into people-flow analytics."""

    def __init__(self, config: AnalyticsConfig):
        self.config = config
        self.total_entered = 0
        self.total_exited = 0
        self.peak_occupancy = 0
        self.events: list[CrossingEvent] = []
        self.frame_metrics: list[dict] = []
        self.trajectories: dict[int, Deque[dict]] = defaultdict(
            lambda: deque(maxlen=max(1, self.config.keep_trajectory_points))
        )
        self._last_side: dict[tuple[int, str], float] = {}
        self._last_crossing_frame: dict[tuple[int, str], int] = {}
        self._first_seen: dict[int, float] = {}
        self._last_seen: dict[int, float] = {}

    def update(
        self,
        tracks: list[Track],
        frame_index: int,
        timestamp_sec: float,
        fps: float,
        latency_ms: float,
    ) -> FrameAnalytics:
        active_track_ids = {track.track_id for track in tracks}
        zone_counts = self._zone_counts(tracks)
        events = self._line_events(tracks, frame_index, timestamp_sec)

        for event in events:
            if event.direction == "in":
                self.total_entered += 1
            elif event.direction == "out":
                self.total_exited += 1
            self.events.append(event)

        for track in tracks:
            self._first_seen.setdefault(track.track_id, timestamp_sec)
            self._last_seen[track.track_id] = timestamp_sec
            cx, cy = track.centroid
            self.trajectories[track.track_id].append(
                {
                    "frame_index": frame_index,
                    "timestamp_sec": round(timestamp_sec, 3),
                    "track_id": track.track_id,
                    "centroid_x": round(cx, 2),
                    "centroid_y": round(cy, 2),
                    "bbox_x1": track.bbox[0],
                    "bbox_y1": track.bbox[1],
                    "bbox_x2": track.bbox[2],
                    "bbox_y2": track.bbox[3],
                    "confidence": round(track.confidence, 4),
                }
            )

        current_occupancy = self.current_occupancy(len(active_track_ids))
        self.peak_occupancy = max(self.peak_occupancy, current_occupancy)

        frame_result = FrameAnalytics(
            frame_index=frame_index,
            timestamp_sec=timestamp_sec,
            active_tracks=len(active_track_ids),
            current_occupancy=current_occupancy,
            total_entered=self.total_entered,
            total_exited=self.total_exited,
            peak_occupancy=self.peak_occupancy,
            fps=fps,
            latency_ms=latency_ms,
            zone_counts=zone_counts,
            events=events,
        )
        self.frame_metrics.append(frame_result.to_dict())
        return frame_result

    def current_occupancy(self, active_tracks: int) -> int:
        if self.config.lines:
            return max(0, self.total_entered - self.total_exited)
        return active_tracks

    def trajectory_rows(self) -> list[dict]:
        rows: list[dict] = []
        for track_id in sorted(self.trajectories):
            rows.extend(self.trajectories[track_id])
        return rows

    def summary(self, total_frames: int, elapsed_sec: float) -> dict:
        dwell_times = [
            max(0.0, self._last_seen[track_id] - first_seen)
            for track_id, first_seen in self._first_seen.items()
            if track_id in self._last_seen
        ]
        current_occupancy = self.current_occupancy(len(self._last_seen))
        return {
            "total_frames": total_frames,
            "elapsed_sec": round(elapsed_sec, 3),
            "average_fps": round(total_frames / elapsed_sec, 2) if elapsed_sec > 0 else 0.0,
            "total_entered": self.total_entered,
            "total_exited": self.total_exited,
            "current_occupancy": current_occupancy,
            "peak_occupancy": self.peak_occupancy,
            "unique_track_ids_seen": len(self._first_seen),
            "average_scene_dwell_sec": round(mean(dwell_times), 3) if dwell_times else 0.0,
            "longest_scene_dwell_sec": round(max(dwell_times), 3) if dwell_times else 0.0,
            "crossing_events": len(self.events),
        }

    def _line_events(
        self,
        tracks: list[Track],
        frame_index: int,
        timestamp_sec: float,
    ) -> list[CrossingEvent]:
        events: list[CrossingEvent] = []
        for track in tracks:
            for line in self.config.lines:
                key = (track.track_id, line.name)
                current_side = point_side(track.centroid, line.start, line.end)
                previous_side = self._last_side.get(key)

                if previous_side is not None:
                    transition = _transition(previous_side, current_side)
                    if transition is not None and self._passes_debounce(key, line, frame_index):
                        direction = "in" if transition == line.in_direction else "out"
                        self._last_crossing_frame[key] = frame_index
                        events.append(
                            CrossingEvent(
                                frame_index=frame_index,
                                timestamp_sec=timestamp_sec,
                                track_id=track.track_id,
                                line_name=line.name,
                                direction=direction,
                                centroid=track.centroid,
                            )
                        )

                if abs(current_side) > 1e-6:
                    self._last_side[key] = current_side
        return events

    def _passes_debounce(
        self,
        key: tuple[int, str],
        line: LineConfig,
        frame_index: int,
    ) -> bool:
        previous_frame = self._last_crossing_frame.get(key)
        if previous_frame is None:
            return True
        return frame_index - previous_frame >= line.debounce_frames

    def _zone_counts(self, tracks: list[Track]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for zone in self.config.zones:
            polygon: list[Point] = [(float(x), float(y)) for x, y in zone.points]
            counts[zone.name] = sum(
                1 for track in tracks if point_in_polygon(track.centroid, polygon)
            )
        return counts


def _transition(previous_side: float, current_side: float) -> str | None:
    if abs(previous_side) <= 1e-6 or abs(current_side) <= 1e-6:
        return None
    if previous_side < 0 < current_side:
        return "negative_to_positive"
    if previous_side > 0 > current_side:
        return "positive_to_negative"
    return None
