"""Primitive 2D drafting commands: lines, polylines, rectangles, circles, arcs, text.

Angles in this module's schemas are degrees (natural for a chat agent to
reason and talk about); they're converted to radians at the backend boundary
to match AutoCAD's own COM convention.
"""
import math

from ..geometry import point_from
from .registry import command

_POINT = {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 3}


def _pt(desc):
    return {**_POINT, "description": desc}


@command(
    name="draw_line",
    description="Draw a straight LINE entity between two points.",
    parameters={
        "start": _pt("Start point [x, y] or [x, y, z]"),
        "end": _pt("End point [x, y] or [x, y, z]"),
        "layer": {"type": "string", "description": "Layer to draw on (defaults to current layer)"},
    },
    required=["start", "end"],
)
def draw_line(backend, start, end, layer=None):
    return backend.add_line(point_from(start), point_from(end), layer=layer)


@command(
    name="draw_polyline",
    description="Draw a lightweight polyline (LWPOLYLINE) through a sequence of points.",
    parameters={
        "points": {
            "type": "array",
            "items": _POINT,
            "minItems": 2,
            "description": "Vertices in order",
        },
        "closed": {"type": "boolean", "description": "Whether to close the polyline back to its first vertex"},
        "layer": {"type": "string", "description": "Layer to draw on (defaults to current layer)"},
    },
    required=["points"],
)
def draw_polyline(backend, points, closed=False, layer=None):
    return backend.add_polyline([point_from(p) for p in points], closed=closed, layer=layer)


@command(
    name="draw_rectangle",
    description="Draw a closed rectangular polyline given two opposite corners.",
    parameters={
        "corner1": _pt("First corner [x, y]"),
        "corner2": _pt("Opposite corner [x, y]"),
        "layer": {"type": "string", "description": "Layer to draw on (defaults to current layer)"},
    },
    required=["corner1", "corner2"],
)
def draw_rectangle(backend, corner1, corner2, layer=None):
    a = point_from(corner1)
    c = point_from(corner2)
    points = [a, point_from([c.x, a.y, a.z]), c, point_from([a.x, c.y, a.z])]
    return backend.add_polyline(points, closed=True, layer=layer)


@command(
    name="draw_circle",
    description="Draw a CIRCLE entity.",
    parameters={
        "center": _pt("Center point [x, y]"),
        "radius": {"type": "number", "description": "Radius in drawing units"},
        "layer": {"type": "string", "description": "Layer to draw on (defaults to current layer)"},
    },
    required=["center", "radius"],
)
def draw_circle(backend, center, radius, layer=None):
    return backend.add_circle(point_from(center), radius, layer=layer)


@command(
    name="draw_arc",
    description="Draw an ARC entity, sweeping counter-clockwise from start_angle to end_angle.",
    parameters={
        "center": _pt("Center point [x, y]"),
        "radius": {"type": "number", "description": "Radius in drawing units"},
        "start_angle": {
            "type": "number",
            "description": "Start angle in degrees, measured counter-clockwise from the positive X axis",
        },
        "end_angle": {"type": "number", "description": "End angle in degrees"},
        "layer": {"type": "string", "description": "Layer to draw on (defaults to current layer)"},
    },
    required=["center", "radius", "start_angle", "end_angle"],
)
def draw_arc(backend, center, radius, start_angle, end_angle, layer=None):
    return backend.add_arc(
        point_from(center), radius, math.radians(start_angle), math.radians(end_angle), layer=layer
    )


@command(
    name="add_text",
    description="Place a single-line TEXT entity.",
    parameters={
        "position": _pt("Insertion point [x, y]"),
        "content": {"type": "string", "description": "Text string"},
        "height": {"type": "number", "description": "Text height in drawing units"},
        "rotation": {"type": "number", "description": "Rotation in degrees, defaults to 0"},
        "layer": {"type": "string", "description": "Layer to draw on (defaults to current layer)"},
    },
    required=["position", "content", "height"],
)
def add_text(backend, position, content, height, rotation=0.0, layer=None):
    return backend.add_text(point_from(position), height, content, layer=layer, rotation=math.radians(rotation))
