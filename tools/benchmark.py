from __future__ import annotations

import argparse
import csv
from pathlib import Path

from people_counter.config_runtime import load_config
from people_counter.counter import VideoCounter


def main() -> int:
    args = parse_args()
    rows = []

    for model in args.models:
        for tracker in args.trackers:
            config = load_config(args.config)
            config.detector.model_path = model
            config.tracker.backend = tracker
            config.runtime.max_frames = args.max_frames
            config.output.save_annotated_video = False

            result = VideoCounter(source=_parse_source(args.source), config=config).run(
                visualize=False,
                export=False,
            )
            rows.append(
                {
                    "model": model,
                    "tracker": tracker,
                    **result.summary,
                }
            )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=sorted({k for row in rows for k in row}))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote benchmark results to {output_path}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark model/tracker combinations.")
    parser.add_argument("--source", required=True)
    parser.add_argument("--config", default="config/default.yaml")
    parser.add_argument("--models", nargs="+", default=["yolo11n.pt", "yolo11s.pt"])
    parser.add_argument("--trackers", nargs="+", default=["bytetrack", "botsort"])
    parser.add_argument("--max-frames", type=int, default=300)
    parser.add_argument("--output", default="outputs/benchmark.csv")
    return parser.parse_args()


def _parse_source(value: str):
    return int(value) if value.isdigit() else value


if __name__ == "__main__":
    raise SystemExit(main())
