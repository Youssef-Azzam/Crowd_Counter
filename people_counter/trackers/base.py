from __future__ import annotations

from typing import Protocol

from ..schema import Detection, Track


class MultiObjectTracker(Protocol):
    def update(self, frame, detections: list[Detection], frame_index: int = 0) -> list[Track]:
        """Return active tracks for the current frame."""
