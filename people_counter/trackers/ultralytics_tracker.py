from __future__ import annotations

from ultralytics import YOLO

from ..config_runtime import DetectorConfig, TrackerConfig
from ..schema import Detection, Track


class UltralyticsTracker:
    """YOLO native MOT wrapper for ByteTrack or BoT-SORT."""

    def __init__(self, detector_config: DetectorConfig, tracker_config: TrackerConfig):
        self.detector_config = detector_config
        self.tracker_config = tracker_config
        self.model = YOLO(detector_config.model_path)

    def update(self, frame, detections: list[Detection] | None = None, frame_index: int = 0) -> list[Track]:
        results = self.model.track(
            frame,
            persist=True,
            conf=self.detector_config.confidence,
            iou=self.detector_config.iou,
            imgsz=self.detector_config.image_size,
            classes=self.detector_config.classes,
            device=self.detector_config.device,
            tracker=self.tracker_config.ultralytics_tracker,
            verbose=False,
        )[0]

        tracks: list[Track] = []
        if results.boxes is None or results.boxes.id is None:
            return tracks

        for box in results.boxes:
            if box.id is None:
                continue
            track_id = int(box.id[0])
            confidence = float(box.conf[0]) if box.conf is not None else 1.0
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            tracks.append(
                Track(
                    track_id=track_id,
                    bbox=(x1, y1, x2, y2),
                    confidence=confidence,
                    metadata={"backend": self.tracker_config.backend},
                )
            )
        return tracks
