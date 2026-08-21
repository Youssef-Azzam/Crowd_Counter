from __future__ import annotations

from ultralytics import YOLO

from .config_runtime import DetectorConfig
from .schema import Detection


class Detector:
    """YOLO person detector wrapper."""

    def __init__(
        self,
        model_path: str | None = None,
        conf_thresh: float | None = None,
        config: DetectorConfig | None = None,
    ):
        self.config = config or DetectorConfig()
        if model_path is not None:
            self.config.model_path = model_path
        if conf_thresh is not None:
            self.config.confidence = conf_thresh
        self.model = YOLO(self.config.model_path)

    def detect_people(self, frame) -> list[Detection]:
        results = self.model.predict(
            frame,
            conf=self.config.confidence,
            iou=self.config.iou,
            imgsz=self.config.image_size,
            classes=self.config.classes,
            device=self.config.device,
            verbose=False,
        )[0]

        detections: list[Detection] = []
        if results.boxes is None:
            return detections

        for box in results.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            detections.append(
                Detection(
                    bbox=(x1, y1, x2, y2),
                    confidence=confidence,
                    class_id=class_id,
                    label="person",
                )
            )
        return detections
