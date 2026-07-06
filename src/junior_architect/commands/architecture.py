"""Composite architectural elements built on top of the drafting primitives.

These are the higher-level building blocks a junior architect reaches for
first: walls, door/window symbols, and room labels, rather than raw lines
and arcs. Door and window symbols are placed along a wall direction but do
not automatically cut the wall opening (real wall-opening booleans need
region/solid modeling beyond this first slice) — draw the wall segments
around the opening instead.
"""
import math

from ..geometry import centroid, offset_line_perpendicular, point_from, polygon_area
from .registry import command

_POINT = {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 3}


@command(
    name="draw_wall",
    description="Draw a straight wall as a closed polyline of the given thickness between two centerline points.",
    parameters={
        "start": {**_POINT, "description": "Wall centerline start point"},
        "end": {**_POINT, "description": "Wall centerline end point"},
        "thickness": {"type": "number", "description": "Wall thickness in drawing units, defaults to 0.2 (e.g. 200mm)"},
        "layer": {"type": "string", "description": "Layer to draw on, conventionally A-WALL"},
    },
    required=["start", "end"],
)
def draw_wall(backend, start, end, thickness=0.2, layer=None):
    a = point_from(start)
    b = point_from(end)
    left_a, left_b = offset_line_perpendicular(a, b, thickness / 2)
    right_a, right_b = offset_line_perpendicular(a, b, -thickness / 2)
    handle = backend.add_polyline([left_a, left_b, right_b, right_a], closed=True, layer=layer)
    return {"wall": handle}


@command(
    name="add_door",
    description=(
        "Draw a single-leaf door symbol (leaf line + quarter-circle swing arc) with its hinge at a "
        "point along a wall's direction."
    ),
    parameters={
        "insertion_point": {**_POINT, "description": "Point where the door hinge sits, on the wall centerline"},
        "angle": {"type": "number", "description": "Wall direction in degrees at the door, 0 = along +X axis"},
        "width": {"type": "number", "description": "Door leaf width (clear opening), defaults to 0.9"},
        "swing": {
            "type": "string",
            "enum": ["left", "right"],
            "description": "Which side the door swings open to, defaults to 'left'",
        },
        "layer": {"type": "string", "description": "Layer to draw on, conventionally A-DOOR"},
    },
    required=["insertion_point", "angle"],
)
def add_door(backend, insertion_point, angle, width=0.9, swing="left", layer=None):
    hinge = point_from(insertion_point)
    rad = math.radians(angle)
    leaf_end = point_from([hinge.x + width * math.cos(rad), hinge.y + width * math.sin(rad), hinge.z])
    leaf = backend.add_line(hinge, leaf_end, layer=layer)

    if swing == "left":
        arc_start, arc_end = angle, angle + 90
    elif swing == "right":
        arc_start, arc_end = angle - 90, angle
    else:
        raise ValueError("swing must be 'left' or 'right'")

    swing_arc = backend.add_arc(hinge, width, math.radians(arc_start), math.radians(arc_end), layer=layer)
    return {"leaf": leaf, "swing_arc": swing_arc}


@command(
    name="add_window",
    description=(
        "Draw a standard double-line window symbol (opening line + two end ticks) starting at a "
        "point along a wall's direction."
    ),
    parameters={
        "insertion_point": {**_POINT, "description": "Start point of the window opening, on the wall centerline"},
        "angle": {"type": "number", "description": "Wall direction in degrees, 0 = along +X axis"},
        "width": {"type": "number", "description": "Window opening width, defaults to 1.2"},
        "layer": {"type": "string", "description": "Layer to draw on, conventionally A-WIND"},
    },
    required=["insertion_point", "angle"],
)
def add_window(backend, insertion_point, angle, width=1.2, layer=None):
    p0 = point_from(insertion_point)
    rad = math.radians(angle)
    dx, dy = math.cos(rad), math.sin(rad)
    p1 = point_from([p0.x + width * dx, p0.y + width * dy, p0.z])
    main = backend.add_line(p0, p1, layer=layer)

    tick = width * 0.1
    nx, ny = -dy, dx
    tick_handles = []
    for p in (p0, p1):
        t0 = point_from([p.x + nx * tick, p.y + ny * tick, p.z])
        t1 = point_from([p.x - nx * tick, p.y - ny * tick, p.z])
        tick_handles.append(backend.add_line(t0, t1, layer=layer))

    return {"opening": main, "ticks": tick_handles}


@command(
    name="label_room",
    description="Place a room name label with its computed floor area at the centroid of its boundary.",
    parameters={
        "name": {"type": "string", "description": "Room name, e.g. 'Bedroom 1'"},
        "boundary": {
            "type": "array",
            "items": _POINT,
            "minItems": 3,
            "description": "Ordered vertices of the room's floor boundary",
        },
        "text_height": {"type": "number", "description": "Label text height, defaults to 0.25"},
        "layer": {"type": "string", "description": "Layer to draw on, conventionally A-ANNO-TEXT"},
    },
    required=["name", "boundary"],
)
def label_room(backend, name, boundary, text_height=0.25, layer=None):
    points = [point_from(p) for p in boundary]
    center = centroid(points)
    area = polygon_area(points)
    content = f"{name}\n{area:.1f} m2"
    return backend.add_text(center, text_height, content, layer=layer)
