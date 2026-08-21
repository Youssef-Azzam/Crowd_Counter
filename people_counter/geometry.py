from __future__ import annotations

from .schema import BBox, Point


def iou(box_a: BBox, box_b: BBox) -> float:
    x_a = max(box_a[0], box_b[0])
    y_a = max(box_a[1], box_b[1])
    x_b = min(box_a[2], box_b[2])
    y_b = min(box_a[3], box_b[3])

    intersection = max(0, x_b - x_a) * max(0, y_b - y_a)
    area_a = max(0, box_a[2] - box_a[0]) * max(0, box_a[3] - box_a[1])
    area_b = max(0, box_b[2] - box_b[0]) * max(0, box_b[3] - box_b[1])
    union = area_a + area_b - intersection
    if union <= 0:
        return 0.0
    return intersection / union


def bbox_area(box: BBox) -> int:
    return max(0, box[2] - box[0]) * max(0, box[3] - box[1])


def xyxy_to_xywh(box: BBox) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = box
    return (x1, y1, max(0, x2 - x1), max(0, y2 - y1))


def xywh_to_xyxy(box: tuple[float, float, float, float]) -> BBox:
    x, y, w, h = box
    return (int(x), int(y), int(x + w), int(y + h))


def point_side(point: Point, line_start: Point, line_end: Point) -> float:
    px, py = point
    x1, y1 = line_start
    x2, y2 = line_end
    return (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)


def point_in_polygon(point: Point, polygon: list[Point]) -> bool:
    x, y = point
    inside = False
    j = len(polygon) - 1
    for i, (xi, yi) in enumerate(polygon):
        xj, yj = polygon[j]
        intersects = (yi > y) != (yj > y)
        if intersects:
            x_intersection = (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi
            if x < x_intersection:
                inside = not inside
        j = i
    return inside
