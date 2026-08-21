from people_counter.analytics import AnalyticsEngine
from people_counter.config_runtime import AnalyticsConfig, LineConfig, ZoneConfig
from people_counter.schema import Track


def test_line_crossing_counts_in_direction():
    engine = AnalyticsEngine(
        AnalyticsConfig(
            lines=[
                LineConfig(
                    name="door",
                    start=(0, 10),
                    end=(20, 10),
                    in_direction="negative_to_positive",
                    debounce_frames=1,
                )
            ]
        )
    )

    engine.update([Track(track_id=1, bbox=(0, 0, 10, 8))], 1, 0.0, 30.0, 1.0)
    result = engine.update([Track(track_id=1, bbox=(0, 12, 10, 20))], 2, 0.1, 30.0, 1.0)

    assert result.total_entered == 1
    assert result.total_exited == 0
    assert result.current_occupancy == 1
    assert result.events[0].direction == "in"


def test_line_crossing_counts_out_direction():
    engine = AnalyticsEngine(
        AnalyticsConfig(
            lines=[
                LineConfig(
                    name="door",
                    start=(0, 10),
                    end=(20, 10),
                    in_direction="negative_to_positive",
                    debounce_frames=1,
                )
            ]
        )
    )

    engine.update([Track(track_id=1, bbox=(0, 12, 10, 20))], 1, 0.0, 30.0, 1.0)
    result = engine.update([Track(track_id=1, bbox=(0, 0, 10, 8))], 2, 0.1, 30.0, 1.0)

    assert result.total_entered == 0
    assert result.total_exited == 1
    assert result.current_occupancy == 0
    assert result.events[0].direction == "out"


def test_zone_counts_active_tracks_inside_polygon():
    engine = AnalyticsEngine(
        AnalyticsConfig(
            zones=[ZoneConfig(name="queue", points=[(0, 0), (20, 0), (20, 20), (0, 20)])]
        )
    )

    result = engine.update(
        [
            Track(track_id=1, bbox=(2, 2, 6, 6)),
            Track(track_id=2, bbox=(30, 30, 40, 40)),
        ],
        1,
        0.0,
        30.0,
        1.0,
    )

    assert result.zone_counts["queue"] == 1
