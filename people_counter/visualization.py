from __future__ import annotations

import cv2
import numpy as np

from .config_runtime import AnalyticsConfig, RuntimeConfig
from .schema import FrameAnalytics, Track


def draw_overlay(
    frame,
    tracks: list[Track],
    analytics: FrameAnalytics,
    analytics_config: AnalyticsConfig,
    runtime_config: RuntimeConfig,
    trajectory_points: dict[int, list[tuple[int, int]]] | None = None,
):
    canvas = frame.copy()

    if runtime_config.privacy_blur:
        _blur_tracks(canvas, tracks)

    for zone in analytics_config.zones:
        points = np.array(zone.points, dtype=np.int32)
        cv2.polylines(canvas, [points], isClosed=True, color=(255, 180, 0), thickness=2)
        label_point = tuple(points[0])
        cv2.putText(
            canvas,
            f"{zone.name}: {analytics.zone_counts.get(zone.name, 0)}",
            label_point,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 180, 0),
            2,
        )

    for line in analytics_config.lines:
        cv2.line(canvas, line.start, line.end, (0, 200, 255), 2)
        cv2.putText(
            canvas,
            line.name,
            line.start,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 200, 255),
            2,
        )

    for track in tracks:
        x1, y1, x2, y2 = track.bbox
        cv2.rectangle(canvas, (x1, y1), (x2, y2), (40, 220, 80), 2)
        cv2.putText(
            canvas,
            f"ID {track.track_id}",
            (x1, max(20, y1 - 6)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (40, 220, 80),
            2,
        )

    if runtime_config.draw_trajectories and trajectory_points:
        for points in trajectory_points.values():
            for p1, p2 in zip(points, points[1:], strict=False):
                cv2.line(canvas, p1, p2, (255, 120, 0), 2)

    _draw_metrics(canvas, analytics, runtime_config)
    return canvas


def _blur_tracks(frame, tracks: list[Track]) -> None:
    for track in tracks:
        x1, y1, x2, y2 = track.bbox
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(frame.shape[1], x2)
        y2 = min(frame.shape[0], y2)
        roi = frame[y1:y2, x1:x2]
        if roi.size:
            frame[y1:y2, x1:x2] = cv2.GaussianBlur(roi, (31, 31), 0)


def _draw_metrics(frame, analytics: FrameAnalytics, runtime_config: RuntimeConfig) -> None:
    lines = [
        f"Occupancy: {analytics.current_occupancy}",
        f"In: {analytics.total_entered}  Out: {analytics.total_exited}",
        f"Peak: {analytics.peak_occupancy}  Active: {analytics.active_tracks}",
    ]
    if runtime_config.show_fps:
        lines.append(f"FPS: {analytics.fps:.1f}  Latency: {analytics.latency_ms:.1f} ms")

    x, y = 12, 30
    for text in lines:
        cv2.putText(
            frame,
            text,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            3,
        )
        cv2.putText(
            frame,
            text,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (20, 20, 20),
            1,
        )
        y += 28

