"""Small geometry helpers shared by every drafting command."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence, Tuple, Union

Number = Union[int, float]


@dataclass(frozen=True)
class Point:
    x: float
    y: float
    z: float = 0.0

    def as_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)


def point_from(value: Union[Point, Sequence[Number]]) -> Point:
    """Coerce a [x, y] / [x, y, z] sequence (as passed by the chat agent) into a Point."""
    if isinstance(value, Point):
        return value
    if len(value) == 2:
        x, y = value
        return Point(float(x), float(y), 0.0)
    if len(value) == 3:
        x, y, z = value
        return Point(float(x), float(y), float(z))
    raise ValueError(f"Expected a 2 or 3 element point, got {value!r}")


def distance(a: Point, b: Point) -> float:
    return math.dist(a.as_tuple(), b.as_tuple())


def centroid(points: Sequence[Point]) -> Point:
    n = len(points)
    if n == 0:
        raise ValueError("Cannot compute centroid of zero points")
    return Point(
        sum(p.x for p in points) / n,
        sum(p.y for p in points) / n,
        sum(p.z for p in points) / n,
    )


def polygon_area(points: Sequence[Point]) -> float:
    """Shoelace formula. Assumes a planar polygon in the XY plane."""
    n = len(points)
    if n < 3:
        return 0.0
    total = 0.0
    for i in range(n):
        a, b = points[i], points[(i + 1) % n]
        total += a.x * b.y - b.x * a.y
    return abs(total) / 2.0


def offset_line_perpendicular(a: Point, b: Point, offset: float) -> Tuple[Point, Point]:
    """Shift segment a->b sideways by `offset`, perpendicular to its direction.

    Positive `offset` shifts to the left of the direction a->b; used to build
    the two parallel edges of a wall from its centerline.
    """
    dx, dy = b.x - a.x, b.y - a.y
    length = math.hypot(dx, dy)
    if length == 0:
        raise ValueError("Cannot offset a zero-length segment")
    nx, ny = -dy / length, dx / length
    ox, oy = nx * offset, ny * offset
    return Point(a.x + ox, a.y + oy, a.z), Point(b.x + ox, b.y + oy, b.z)
