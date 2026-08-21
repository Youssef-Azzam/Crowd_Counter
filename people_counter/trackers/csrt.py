from __future__ import annotations

import cv2

from ..config_runtime import TrackerConfig
from ..geometry import bbox_area, iou, xywh_to_xyxy, xyxy_to_xywh
from ..schema import Detection, Track


def make_csrt_tracker():
    if hasattr(cv2, "legacy") and hasattr(cv2.legacy, "TrackerCSRT_create"):
        return cv2.legacy.TrackerCSRT_create()
    if hasattr(cv2, "TrackerCSRT_create"):
        return cv2.TrackerCSRT_create()
    if hasattr(cv2, "TrackerCSRT"):
        return cv2.TrackerCSRT()
    raise RuntimeError("CSRT tracker not found. Install opencv-contrib-python.")


class CSRTTracker:
    """Simple CSRT + IoU tracker kept as an explainable baseline."""

    def __init__(
        self,
        iou_threshold: float | None = None,
        max_misses: int | None = None,
        config: TrackerConfig | None = None,
    ):
        self.config = config or TrackerConfig()
        if iou_threshold is not None:
            self.config.iou_threshold = iou_threshold
        if max_misses is not None:
            self.config.max_misses = max_misses
        self._records: dict[int, dict] = {}
        self._next_id = 1

    def update(self, frame, detections: list[Detection], frame_index: int = 0) -> list[Track]:
        detections = [
            det for det in detections if bbox_area(det.bbox) >= self.config.min_box_area
        ]
        unmatched = set(range(len(detections)))

        for track_id in list(self._records.keys()):
            record = self._records[track_id]
            ok, raw_bbox = record["tracker"].update(frame)
            if ok:
                tracked_box = xywh_to_xyxy(raw_bbox)
                record["bbox"] = tracked_box
                record["misses"] = 0
            else:
                tracked_box = record["bbox"]
                record["misses"] += 1

            best_index = None
            best_score = 0.0
            for detection_index in list(unmatched):
                score = iou(tracked_box, detections[detection_index].bbox)
                if score > best_score:
                    best_score = score
                    best_index = detection_index

            if best_index is not None and best_score >= self.config.iou_threshold:
                detection = detections[best_index]
                tracker = make_csrt_tracker()
                tracker.init(frame, xyxy_to_xywh(detection.bbox))
                record.update(
                    {
                        "tracker": tracker,
                        "bbox": detection.bbox,
                        "confidence": detection.confidence,
                        "misses": 0,
                    }
                )
                unmatched.remove(best_index)

            if record["misses"] > self.config.max_misses:
                del self._records[track_id]

        for detection_index in unmatched:
            detection = detections[detection_index]
            tracker = make_csrt_tracker()
            tracker.init(frame, xyxy_to_xywh(detection.bbox))
            self._records[self._next_id] = {
                "tracker": tracker,
                "bbox": detection.bbox,
                "confidence": detection.confidence,
                "misses": 0,
            }
            self._next_id += 1

        return [
            Track(
                track_id=track_id,
                bbox=record["bbox"],
                confidence=record.get("confidence", 1.0),
                missed=record["misses"],
                metadata={"backend": "csrt"},
            )
            for track_id, record in sorted(self._records.items())
        ]
