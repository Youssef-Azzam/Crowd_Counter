from __future__ import annotations

import argparse
import json
from pathlib import Path

from people_counter.config_runtime import LineConfig, load_config
from people_counter.counter import VideoCounter


def main() -> int:
    args = parse_args()
    config = load_config(args.config)

    if args.model:
        config.detector.model_path = args.model
    if args.conf_thresh is not None:
        config.detector.confidence = args.conf_thresh
    if args.detector_iou is not None:
        config.detector.iou = args.detector_iou
    if args.device:
        config.detector.device = args.device
    if args.tracker:
        config.tracker.backend = args.tracker
    if args.tracker_iou is not None:
        config.tracker.iou_threshold = args.tracker_iou
    if args.max_misses is not None:
        config.tracker.max_misses = args.max_misses
    if args.output_dir:
        config.output.directory = args.output_dir
    if args.save_video:
        config.output.save_annotated_video = True
    export = not args.no_export
    if args.line:
        config.analytics.lines = [_parse_line(value) for value in args.line]
    if args.max_frames:
        config.runtime.max_frames = args.max_frames
    if args.frame_skip:
        config.runtime.frame_skip = args.frame_skip
    if args.privacy_blur:
        config.runtime.privacy_blur = True

    counter = VideoCounter(source=_parse_source(args.source), config=config)
    result = counter.run(visualize=args.show, export=export)

    print(json.dumps(result.summary, indent=2))
    if result.output_paths:
        print("\nOutputs:")
        for name, path in result.output_paths.items():
            print(f"- {name}: {Path(path)}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Track and count people in video streams.")
    parser.add_argument("--source", required=True, help="Video path, RTSP URL, or camera index.")
    parser.add_argument("--config", default="config/default.yaml", help="YAML config path.")
    parser.add_argument("--model", help="YOLO model name or local .pt path.")
    parser.add_argument("--tracker", choices=["csrt", "bytetrack", "botsort"], help="Tracker backend.")
    parser.add_argument("--conf-thresh", type=float, help="Detection confidence threshold.")
    parser.add_argument("--detector-iou", type=float, help="YOLO NMS IoU threshold.")
    parser.add_argument("--tracker-iou", type=float, help="CSRT IoU association threshold.")
    parser.add_argument("--max-misses", type=int, help="Frames to keep a missing CSRT track.")
    parser.add_argument("--device", help="Inference device, e.g. cpu, 0, cuda:0.")
    parser.add_argument("--output-dir", help="Directory for CSV/JSON/video outputs.")
    parser.add_argument("--save-video", action="store_true", help="Save annotated MP4 output.")
    parser.add_argument("--no-export", action="store_true", help="Disable CSV/JSON export.")
    parser.add_argument("--show", action="store_true", help="Show OpenCV preview window.")
    parser.add_argument("--max-frames", type=int, help="Stop after this many source frames.")
    parser.add_argument("--frame-skip", type=int, help="Process every Nth frame.")
    parser.add_argument("--privacy-blur", action="store_true", help="Blur tracked people.")
    parser.add_argument(
        "--line",
        action="append",
        help=(
            "Counting line as name:x1,y1,x2,y2:direction. "
            "Direction is negative_to_positive or positive_to_negative."
        ),
    )
    return parser.parse_args()


def _parse_source(value: str):
    return int(value) if value.isdigit() else value


def _parse_line(value: str) -> LineConfig:
    try:
        name, coords, direction = value.split(":")
        x1, y1, x2, y2 = [int(part) for part in coords.split(",")]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "Line must look like main:100,300,900,300:negative_to_positive"
        ) from exc
    if direction not in {"negative_to_positive", "positive_to_negative"}:
        raise argparse.ArgumentTypeError(
            "Line direction must be negative_to_positive or positive_to_negative"
        )
    return LineConfig(name=name, start=(x1, y1), end=(x2, y2), in_direction=direction)


if __name__ == "__main__":
    raise SystemExit(main())
