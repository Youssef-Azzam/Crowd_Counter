# people_counter/tracker.py
import cv2
from .utils import iou

def make_csrt_tracker():
    """
    Return a new CSRT tracker instance. Assumes opencv-contrib-python is installed.
    """
    if hasattr(cv2, "TrackerCSRT_create"):
        return cv2.TrackerCSRT_create()
    # Some very old builds exposed it as a class instead of factory:
    if hasattr(cv2, "TrackerCSRT"):
        return cv2.TrackerCSRT()
    raise RuntimeError(
        "CSRT tracker not found. Please install opencv-contrib-python."
    )
class PeopleTracker:
    def __init__(self, iou_thresh=0.3, max_misses=5):
        self.trackers = {}   # id -> {tracker, bbox, misses}
        self.next_id   = 1
        self.total_count = 0
        self.iou_thresh = iou_thresh
        self.max_misses = max_misses

    def update(self, frame, detections):
        """Match detections to existing trackers, spawn new trackers, return total_count."""
        unmatched = set(range(len(detections)))

        # 1) Update existing trackers
        for tid in list(self.trackers.keys()):
            rec = self.trackers[tid]
            ok, bbox = rec['tracker'].update(frame)
            if not ok:
                rec['misses'] += 1
            else:
                rec['misses'] = 0
                tx, ty, tw, th = map(int, bbox)
                tracked_box = (tx, ty, tx + tw, ty + th)

                # Only attempt matching if there are unmatched detections
                if unmatched:
                    best_i, best_iou = -1, 0.0
                    for i in unmatched:
                        val = iou(tracked_box, detections[i])
                        if val > best_iou:
                            best_iou, best_i = val, i

                    if best_iou > self.iou_thresh:
                        x1, y1, x2, y2 = detections[best_i]
                        new_trk = make_csrt_tracker()
                        new_trk.init(frame, (x1, y1, x2-x1, y2-y1))
                        rec.update({
                            'tracker': new_trk,
                            'bbox': (x1, y1, x2-x1, y2-y1)
                        })
                        unmatched.remove(best_i)

            # Drop trackers that have missed too many frames
            if rec['misses'] > self.max_misses:
                del self.trackers[tid]

        # 2) Spawn new trackers for any remaining detections
        for i in unmatched:
            x1, y1, x2, y2 = detections[i]
            trk = make_csrt_tracker()
            trk.init(frame, (x1, y1, x2-x1, y2-y1))
            self.trackers[self.next_id] = {
                'tracker': trk,
                'bbox':    (x1, y1, x2-x1, y2-y1),
                'misses':  0
            }
            self.total_count += 1
            self.next_id += 1

        return self.total_count
