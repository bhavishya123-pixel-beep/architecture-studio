"""Whole floor plans from a single declarative spec — one tool call per building.

The planner is pure Python: it turns a list of axis-aligned rooms into a set of
unique wall lines (shared walls between adjacent rooms are merged and drawn
once, with openings from either room cut into the shared wall), plus the door/
window symbols, room labels, and overall dimensions. `draw_floor_plan` then
executes that plan against any backend using the existing composite commands.
"""
from typing import Dict, List, Sequence, Tuple

from ..geometry import point_from
from . import architecture
from .registry import command

_EPS = 1e-9

WALL_NAMES = ("south", "north", "west", "east")

STANDARD_LAYERS = [
    ("A-WALL", 4),
    ("A-DOOR", 2),
    ("A-WIND", 5),
    ("A-ANNO-TEXT", 7),
    ("A-ANNO-DIMS", 1),
]


def _room_rect(room: Dict) -> Tuple[float, float, float, float]:
    cx, cy = float(room["corner"][0]), float(room["corner"][1])
    w, h = float(room["width"]), float(room["height"])
    if w <= 0 or h <= 0:
        raise ValueError(f"Room '{room.get('name', '?')}' must have positive width and height")
    return cx, cy, w, h


def _wall_geometry(room: Dict, wall: str):
    """Return (key, lo, hi) for a named wall of a room.

    key identifies the infinite wall line: ("H", y) for horizontal walls or
    ("V", x) for vertical ones. lo..hi is the wall's extent along that line
    (x for horizontal, y for vertical). Offsets in the spec are measured from
    the lo end: the west end of south/north walls, the south end of west/east.
    """
    cx, cy, w, h = _room_rect(room)
    if wall == "south":
        return ("H", cy), cx, cx + w
    if wall == "north":
        return ("H", cy + h), cx, cx + w
    if wall == "west":
        return ("V", cx), cy, cy + h
    if wall == "east":
        return ("V", cx + w), cy, cy + h
    raise ValueError(f"Unknown wall '{wall}', expected one of {WALL_NAMES}")


def _line_key(key) -> Tuple[str, float]:
    orientation, coord = key
    return (orientation, round(coord, 6))


def _merge_intervals(intervals: Sequence[Tuple[float, float]]) -> List[Tuple[float, float]]:
    merged: List[Tuple[float, float]] = []
    for lo, hi in sorted(intervals):
        if merged and lo <= merged[-1][1] + _EPS:
            merged[-1] = (merged[-1][0], max(merged[-1][1], hi))
        else:
            merged.append((lo, hi))
    return merged


def plan_floor(rooms: Sequence[Dict]) -> Dict:
    """Turn a room spec into a drawing plan: unique walls, symbols, labels.

    Walls shared between adjacent rooms collapse into a single wall carrying
    the openings declared by either room; identical door/window declarations
    from both sides dedupe to one symbol.
    """
    if not rooms:
        raise ValueError("A floor plan needs at least one room")

    lines: Dict[Tuple[str, float], Dict] = {}
    doors: Dict[tuple, Dict] = {}
    windows: Dict[tuple, Dict] = {}
    labels: List[Dict] = []

    for room in rooms:
        cx, cy, w, h = _room_rect(room)
        for wall in WALL_NAMES:
            key, lo, hi = _wall_geometry(room, wall)
            lines.setdefault(_line_key(key), {"intervals": [], "openings": []})["intervals"].append((lo, hi))

        for kind, items in (("door", room.get("doors", [])), ("window", room.get("windows", []))):
            for item in items:
                key, lo, hi = _wall_geometry(room, item["wall"])
                offset, width = float(item["offset"]), float(item["width"])
                if width <= 0:
                    raise ValueError(f"{kind} width must be positive, got {width}")
                if offset < -_EPS or offset + width > (hi - lo) + _EPS:
                    raise ValueError(
                        f"{kind} at offset {offset:g} (width {width:g}) does not fit the "
                        f"{item['wall']} wall of room '{room.get('name', '?')}' (length {hi - lo:g})"
                    )
                o0, o1 = lo + offset, lo + offset + width
                lines[_line_key(key)]["openings"].append((o0, o1))

                orientation, coord = _line_key(key)
                if orientation == "H":
                    insertion, angle = [o0, coord], 0.0
                else:
                    insertion, angle = [coord, o0], 90.0
                symbol_key = (round(insertion[0], 6), round(insertion[1], 6), angle, round(width, 6))
                if kind == "door":
                    doors.setdefault(
                        symbol_key,
                        {
                            "insertion_point": insertion,
                            "angle": angle,
                            "width": width,
                            "swing": item.get("swing", "left"),
                        },
                    )
                else:
                    windows.setdefault(
                        symbol_key, {"insertion_point": insertion, "angle": angle, "width": width}
                    )

        labels.append(
            {
                "name": room["name"],
                "boundary": [[cx, cy], [cx + w, cy], [cx + w, cy + h], [cx, cy + h]],
            }
        )

    walls: List[Dict] = []
    for (orientation, coord), data in sorted(lines.items()):
        merged_openings = _merge_intervals(data["openings"])
        for lo, hi in _merge_intervals(data["intervals"]):
            local = [
                {"offset": round(max(o0 - lo, 0.0), 9), "width": round(o1 - o0, 9)}
                for o0, o1 in merged_openings
                if o0 >= lo - _EPS and o1 <= hi + _EPS
            ]
            if orientation == "H":
                start, end = [lo, coord], [hi, coord]
            else:
                start, end = [coord, lo], [coord, hi]
            walls.append({"start": start, "end": end, "openings": local})

    return {"walls": walls, "doors": list(doors.values()), "windows": list(windows.values()), "labels": labels}


_OPENING_COMMON = {
    "wall": {
        "type": "string",
        "enum": list(WALL_NAMES),
        "description": "Which wall of the room the opening is in",
    },
    "offset": {
        "type": "number",
        "description": (
            "Distance from the wall's low end to the opening's near edge: the west end for "
            "south/north walls, the south end for west/east walls"
        ),
    },
    "width": {"type": "number", "description": "Clear width of the opening"},
}

_ROOM_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Room name, e.g. 'Bedroom 1'"},
        "corner": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 2,
            "maxItems": 2,
            "description": "South-west (bottom-left) corner [x, y]",
        },
        "width": {"type": "number", "description": "Room extent along X"},
        "height": {"type": "number", "description": "Room extent along Y"},
        "doors": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    **_OPENING_COMMON,
                    "swing": {"type": "string", "enum": ["left", "right"], "description": "Door swing side"},
                },
                "required": ["wall", "offset", "width"],
            },
            "description": "Doors in this room's walls",
        },
        "windows": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": dict(_OPENING_COMMON),
                "required": ["wall", "offset", "width"],
            },
            "description": "Windows in this room's walls",
        },
    },
    "required": ["name", "corner", "width", "height"],
}


@command(
    name="draw_floor_plan",
    description=(
        "Draft a complete floor plan in one call from a list of axis-aligned rooms. Draws every "
        "wall once (walls shared between adjacent rooms are merged, with openings from either "
        "room cut into them), cuts door/window openings with jambs, places door and window "
        "symbols in the openings, labels each room with its name and area, and optionally adds "
        "overall dimensions. Prefer this over drawing walls one by one when the user asks for a "
        "whole room layout, apartment, house, or office plan. Rooms adjacent to each other "
        "should share wall coordinates exactly (e.g. a room from x=0 to 4 next to one from x=4 to 8)."
    ),
    parameters={
        "rooms": {"type": "array", "items": _ROOM_SCHEMA, "minItems": 1, "description": "The rooms of the plan"},
        "wall_thickness": {"type": "number", "description": "Wall thickness in drawing units, defaults to 0.2"},
        "dimensions": {
            "type": "boolean",
            "description": "Add overall width/height dimensions outside the plan, defaults to true",
        },
        "text_height": {"type": "number", "description": "Room label text height, defaults to 0.25"},
    },
    required=["rooms"],
)
def draw_floor_plan(backend, rooms, wall_thickness=0.2, dimensions=True, text_height=0.25):
    plan = plan_floor(rooms)

    for name, color in STANDARD_LAYERS:
        backend.create_layer(name, color=color)

    for wall in plan["walls"]:
        architecture.draw_wall_with_openings(
            backend, wall["start"], wall["end"], wall["openings"], thickness=wall_thickness, layer="A-WALL"
        )
    for door in plan["doors"]:
        architecture.add_door(
            backend,
            door["insertion_point"],
            door["angle"],
            width=door["width"],
            swing=door["swing"],
            layer="A-DOOR",
        )
    for window in plan["windows"]:
        architecture.add_window(
            backend, window["insertion_point"], window["angle"], width=window["width"], layer="A-WIND"
        )
    for label in plan["labels"]:
        architecture.label_room(backend, label["name"], label["boundary"], text_height=text_height, layer="A-ANNO-TEXT")

    if dimensions:
        rects = [_room_rect(r) for r in rooms]
        min_x = min(cx for cx, _, _, _ in rects)
        max_x = max(cx + w for cx, _, w, _ in rects)
        min_y = min(cy for _, cy, _, _ in rects)
        max_y = max(cy + h for _, cy, _, h in rects)
        # Negative/positive offsets push both dimension lines outside the plan.
        backend.add_aligned_dimension(point_from([min_x, min_y]), point_from([max_x, min_y]), -0.8, layer="A-ANNO-DIMS")
        backend.add_aligned_dimension(point_from([min_x, min_y]), point_from([min_x, max_y]), 0.8, layer="A-ANNO-DIMS")

    backend.zoom_extents()

    return {
        "rooms": len(rooms),
        "walls_drawn": len(plan["walls"]),
        "doors": len(plan["doors"]),
        "windows": len(plan["windows"]),
        "dimensions": bool(dimensions),
    }
