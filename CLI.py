'''import sys
from people_counter.counter import VideoCounter

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python cli.py <video_path_or_cam> [model_path]")
        sys.exit(1)
    src = sys.argv[1]
    model = sys.argv[2] if len(sys.argv)>2 else 'yolo11l.pt'
    vc = VideoCounter(
        source=int(src) if src.isdigit() else src,
        model_path=model,
        conf_thresh=0.5,
        iou_thresh=0.3,
        max_misses=5
    )
    total = vc.run(visualize=True)
    print(f"Final total unique people counted: {total}")'''

import cv2
print("cv2 version:", cv2.__version__)
print("Has CSRT factory?:", hasattr(cv2, "TrackerCSRT_create"))

