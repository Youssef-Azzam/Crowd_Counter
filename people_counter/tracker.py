from __future__ import annotations

from .trackers.csrt import CSRTTracker, make_csrt_tracker


class PeopleTracker(CSRTTracker):
    """Backward-compatible alias for the original CSRT people tracker."""


__all__ = ["CSRTTracker", "PeopleTracker", "make_csrt_tracker"]
