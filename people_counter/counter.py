import cv2
from .detector import Detector
from .tracker import PeopleTracker

class VideoCounter:
    def __init__(self, source, model_path, conf_thresh, iou_thresh, max_misses):
        self.cap = cv2.VideoCapture(source)
        self.detector = Detector(model_path, conf_thresh)
        self.tracker = PeopleTracker(iou_thresh, max_misses)

    def run(self, visualize=False):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            detections = self.detector.detect_people(frame)
            count = self.tracker.update(frame, detections)
            if visualize:
                cv2.putText(frame, f"Total Unique People: {count}", (10,30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                cv2.imshow("Counting", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        self.cap.release()
        cv2.destroyAllWindows()
        return self.tracker.total_count