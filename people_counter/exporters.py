from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .config_runtime import OutputConfig


class SessionExporter:
    def __init__(self, config: OutputConfig):
        self.config = config
        self.output_dir = Path(config.directory)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(
        self,
        frame_metrics: list[dict[str, Any]],
        events: list[dict[str, Any]],
        trajectories: list[dict[str, Any]],
        summary: dict[str, Any],
    ) -> dict[str, str]:
        paths: dict[str, str] = {}
        if self.config.save_frame_metrics_csv:
            paths["frame_metrics_csv"] = str(
                self._write_csv("frame_metrics.csv", frame_metrics)
            )
        if self.config.save_events_csv:
            paths["events_csv"] = str(self._write_csv("crossing_events.csv", events))
        if self.config.save_trajectories_csv:
            paths["trajectories_csv"] = str(
                self._write_csv("trajectories.csv", trajectories)
            )
        if self.config.save_summary_json:
            paths["summary_json"] = str(self._write_json("summary.json", summary))
        return paths

    def _write_csv(self, filename: str, rows: list[dict[str, Any]]) -> Path:
        path = self.output_dir / filename
        if not rows:
            path.write_text("", encoding="utf-8")
            return path

        fieldnames = sorted({key for row in rows for key in row.keys()})
        with path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return path

    def _write_json(self, filename: str, data: dict[str, Any]) -> Path:
        path = self.output_dir / filename
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return path
