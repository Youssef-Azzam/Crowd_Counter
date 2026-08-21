# Crowd Counter

A practical computer-vision people-counting project built around YOLO detection,
multi-object tracking, directional line crossing, occupancy analytics, and
exportable session reports.

This version avoids naive "number of detections" counting. Tracks are converted
into events such as IN, OUT, current occupancy, peak occupancy, trajectories,
zone counts, dwell summaries, and frame-level metrics.

## Features

- YOLO person detection through Ultralytics.
- Tracker backends:
  - `bytetrack` through Ultralytics native tracking.
  - `botsort` through Ultralytics native tracking.
  - `csrt` as an explainable OpenCV baseline.
- Directional line crossing:
  - IN count
  - OUT count
  - current occupancy
  - crossing timestamps
  - duplicate crossing debounce
- Region analytics:
  - polygonal zones
  - active people per zone
- Trajectory capture:
  - per-track centroid history
  - CSV export for later heatmaps or movement analysis
- Streamlit app:
  - upload video, webcam, or RTSP/URL input
  - model/tracker controls
  - line-crossing controls
  - live occupancy metrics
  - privacy blur option
  - downloadable outputs
- CLI:
  - reproducible command-line runs
  - CSV/JSON exports
  - optional annotated MP4
- Benchmark script for model/tracker comparisons.
- Unit tests and GitHub Actions CI.
- Docker support.

## Project Structure

```text
.
├── app.py
├── cli.py
├── config/
│   └── default.yaml
├── people_counter/
│   ├── analytics.py
│   ├── config_runtime.py
│   ├── counter.py
│   ├── detector.py
│   ├── exporters.py
│   ├── geometry.py
│   ├── schema.py
│   ├── tracker.py
│   ├── trackers/
│   │   ├── base.py
│   │   ├── csrt.py
│   │   └── ultralytics_tracker.py
│   ├── utils.py
│   └── visualization.py
├── tests/
├── tools/
│   └── benchmark.py
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
└── docker-compose.yml
```

## Installation

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

On Windows:

```bat
setup_env.bat
```

YOLO model weights are intentionally not committed. Ultralytics will download
standard model files such as `yolo11n.pt` automatically when first used, or you
can pass a local model path.

## Streamlit Usage

```bash
streamlit run app.py
```

Windows:

```bat
run.bat
```

The Streamlit app supports uploaded videos, webcam source `0`, and RTSP/URL
sources supported by OpenCV.

## CLI Usage

```bash
python cli.py --source path/to/video.mp4 --tracker bytetrack --model yolo11n.pt
```

Save an annotated MP4:

```bash
python cli.py --source path/to/video.mp4 --save-video --output-dir outputs/demo
```

Use a custom counting line:

```bash
python cli.py --source path/to/video.mp4 --tracker botsort --line main:100,300,900,300:negative_to_positive
```

Use webcam:

```bash
python cli.py --source 0 --tracker bytetrack
```

## Configuration

The default configuration lives in `config/default.yaml`.

Important fields:

- `detector.model_path`: YOLO model name or local path.
- `detector.confidence`: minimum detection confidence.
- `tracker.backend`: `csrt`, `bytetrack`, or `botsort`.
- `analytics.lines`: directional counting lines.
- `analytics.zones`: polygonal regions of interest.
- `output.directory`: output folder for CSV/JSON/video files.
- `runtime.privacy_blur`: blur tracked people in the rendered output.

## Outputs

Each run can create:

- `frame_metrics.csv`: frame index, timestamp, active tracks, occupancy, FPS, latency.
- `crossing_events.csv`: each IN/OUT event with timestamp and track ID.
- `trajectories.csv`: centroid and bbox history for each track.
- `summary.json`: session-level metrics.
- `annotated_output.mp4`: optional rendered video.

## Benchmarking

Compare model and tracker combinations:

```bash
python tools/benchmark.py --source path/to/video.mp4 --models yolo11n.pt yolo11s.pt --trackers bytetrack botsort --max-frames 300
```

The benchmark writes `outputs/benchmark.csv`.

## Testing

```bash
pip install -r requirements-dev.txt
ruff check .
pytest
```

The tests focus on deterministic logic such as IoU, polygon checks, config
loading, line crossing, and occupancy counters. They do not require downloading
YOLO weights.

## Docker

```bash
docker compose up --build
```

Then open `http://localhost:8501`.

## Notes on Counting Accuracy

For entrances and exits, directional line crossing is more meaningful than
counting newly created track IDs. A new track can be created because of
occlusion, low FPS, detection loss, or ID switching, so cumulative track IDs are
not a reliable visitor count by themselves.

For dense crowds where individual people are heavily occluded, detection-based
tracking can still fail. A true density-estimation model may be more appropriate
for extreme crowd-density estimation, but it is a separate modeling problem from
visitor counting.
