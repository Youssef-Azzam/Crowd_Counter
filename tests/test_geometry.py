from people_counter.geometry import iou, point_in_polygon, point_side


def test_iou_for_overlapping_boxes():
    assert round(iou((0, 0, 10, 10), (5, 5, 15, 15)), 4) == 0.1429


def test_iou_for_non_overlapping_boxes():
    assert iou((0, 0, 10, 10), (20, 20, 30, 30)) == 0.0


def test_point_side_changes_across_horizontal_line():
    assert point_side((5, 10), (0, 5), (10, 5)) > 0
    assert point_side((5, 0), (0, 5), (10, 5)) < 0


def test_point_in_polygon():
    polygon = [(0, 0), (10, 0), (10, 10), (0, 10)]
    assert point_in_polygon((5, 5), polygon)
    assert not point_in_polygon((15, 5), polygon)
