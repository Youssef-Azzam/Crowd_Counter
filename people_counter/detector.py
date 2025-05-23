from ultralytics import YOLO

class Detector:
    def __init__(self, model_path: str, conf_thresh: float = 0.5):
        self.model = YOLO(model_path)
        self.conf_thresh = conf_thresh

    def detect_people(self, frame):
        """Return list of (x1,y1,x2,y2) for each person detected above confidence threshold."""
        results = self.model(frame)[0].boxes
        detections = []
        for det in results:
            if int(det.cls[0]) == 0 and float(det.conf[0]) >= self.conf_thresh:
                x1, y1, x2, y2 = map(int, det.xyxy[0])
                detections.append((x1, y1, x2, y2))
        return detections