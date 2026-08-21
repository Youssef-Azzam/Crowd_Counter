from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from pathlib import Path
from time import perf_counter

import cv2

from .analytics import AnalyticsEngine
from .config_runtime import AppConfig, DetectorConfig, TrackerConfig
from .detector import Detector
from .exporters import SessionExporter
from .schema import FrameAnalytics, SessionResult, Track
from .trackers.csrt import CSRTTracker
from .trackers.ultralytics_tracker import UltralyticsTracker
from .visualization import draw_overlay

FrameCallback = Callable[[object, FrameAnalytics, list[Track]], None]


class VideoCounter:
    """End-to-end people counting pipeline."""

    def __init__(
        self,
        source,
        config: AppConfig | None = None,
        model_path: str | None = None,
        conf_thresh: float | None = None,
        iou_thresh: float | None = None,
        max_misses: int | None = None,
    ):
        self.source = source
        self.config = deepcopy(config) if config is not None else AppConfig()
        if model_path is not None:
            self.config.detector.model_path = model_path
        if conf_thresh is not None:
            self.config.detector.confidence = conf_thresh
        if iou_thresh is not None:
            self.config.tracker.iou_threshold = iou_thresh
        if max_misses is not None:
            self.config.tracker.max_misses = max_misses

        self.analytics = AnalyticsEngine(self.config.analytics)
        self.detector, self.tracker = self._build_tracking_components(
            self.config.detector, self.config.tracker
        )

    def run(
        self,
        visualize: bool = False,
        stream_callback: FrameCallback | None = None,
        export: bool = True,
    ) -> SessionResult:
        cap = cv2.VideoCapture(self.source)
        if not cap.isOpened():
            raise RuntimeError(f"Could not open video source: {self.source}")

        source_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_index = 0
        processed_frames = 0
        started_at = perf_counter()
        writer = None
        video_path = None

        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break

                frame_index += 1
                if self.config.runtime.max_frames and frame_index > self.config.runtime.max_frames:
                    break
                if frame_index % max(1, self.config.runtime.frame_skip) != 0:
                    continue

                frame_started_at = perf_counter()
                tracks = self._process_tracks(frame, frame_index)
                timestamp_sec = _timestamp_seconds(cap, frame_index, source_fps)
                latency_ms = (perf_counter() - frame_started_at) * 1000.0
                fps = 1000.0 / latency_ms if latency_ms > 0 else 0.0

                frame_result = self.analytics.update(
                    tracks=tracks,
                    frame_index=frame_index,
                    timestamp_sec=timestamp_sec,
                    fps=fps,
                    latency_ms=latency_ms,
                )
                processed_frames += 1

                trajectory_points = _trajectory_points(self.analytics.trajectories)
                annotated = draw_overlay(
                    frame,
                    tracks,
                    frame_result,
                    self.config.analytics,
                    self.config.runtime,
                    trajectory_points,
                )

                if self.config.output.save_annotated_video:
                    writer, video_path = self._write_video_frame(
                        writer, annotated, source_fps
                    )

                if stream_callback is not None:
                    stream_callback(annotated, frame_result, tracks)

                if visualize:
                    cv2.imshow("Crowd Counter", annotated)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
        finally:
            cap.release()
            if writer is not None:
                writer.release()
            if visualize:
                cv2.destroyAllWindows()

        elapsed_sec = perf_counter() - started_at
        summary = self.analytics.summary(processed_frames, elapsed_sec)
        events = [event.to_dict() for event in self.analytics.events]
        trajectories = self.analytics.trajectory_rows()

        output_paths: dict[str, str] = {}
        if export:
            output_paths = SessionExporter(self.config.output).export(
                frame_metrics=self.analytics.frame_metrics,
                events=events,
                trajectories=trajectories,
                summary=summary,
            )
        if video_path is not None:
            output_paths["annotated_video"] = str(video_path)

        return SessionResult(
            summary=summary,
            frame_metrics=self.analytics.frame_metrics,
            events=events,
            trajectories=trajectories,
            output_paths=output_paths,
        )

    def _process_tracks(self, frame, frame_index: int) -> list[Track]:
        if self.detector is None:
            return self.tracker.update(frame, [], frame_index=frame_index)

        detections = self.detector.detect_people(frame)
        return self.tracker.update(frame, detections, frame_index=frame_index)

    def _write_video_frame(self, writer, frame, source_fps: float):
        output_dir = Path(self.config.output.directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / self.config.output.annotated_video_name

        if writer is None:
            height, width = frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(str(path), fourcc, source_fps or 30.0, (width, height))
        writer.write(frame)
        return writer, path

    @staticmethod
    def _build_tracking_components(
        detector_config: DetectorConfig,
        tracker_config: TrackerConfig,
    ):
        backend = tracker_config.backend.lower()
        if backend == "csrt":
            return Detector(config=detector_config), CSRTTracker(config=tracker_config)

        if backend in {"bytetrack", "botsort", "ultralytics"}:
            if backend == "bytetrack":
                tracker_config.ultralytics_tracker = "bytetrack.yaml"
            elif backend == "botsort":
                tracker_config.ultralytics_tracker = "botsort.yaml"
            return None, UltralyticsTracker(detector_config, tracker_config)

        raise ValueError(
            f"Unsupported tracker backend '{tracker_config.backend}'. "
            "Use csrt, bytetrack, or botsort."
        )


def _timestamp_seconds(cap, frame_index: int, source_fps: float) -> float:
    timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
    if timestamp_ms and timestamp_ms > 0:
        return timestamp_ms / 1000.0
    return frame_index / (source_fps or 30.0)


def _trajectory_points(trajectories) -> dict[int, list[tuple[int, int]]]:
    points: dict[int, list[tuple[int, int]]] = {}
    for track_id, rows in trajectories.items():
        points[track_id] = [
            (int(row["centroid_x"]), int(row["centroid_y"])) for row in rows
        ]
    return points
