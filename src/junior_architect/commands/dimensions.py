"""Dimensioning commands."""
from ..geometry import point_from
from .registry import command

_POINT = {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 3}


@command(
    name="add_linear_dimension",
    description="Place a linear dimension between two points, with the dimension line/text offset to a third point.",
    parameters={
        "p1": {**_POINT, "description": "First measured point"},
        "p2": {**_POINT, "description": "Second measured point"},
        "dim_line_point": {**_POINT, "description": "Point the dimension line/text is offset to"},
        "layer": {
            "type": "string",
            "description": "Layer to draw on (defaults to current layer, typically A-ANNO-DIMS)",
        },
    },
    required=["p1", "p2", "dim_line_point"],
)
def add_linear_dimension(backend, p1, p2, dim_line_point, layer=None):
    return backend.add_linear_dimension(point_from(p1), point_from(p2), point_from(dim_line_point), layer=layer)


@command(
    name="add_aligned_dimension",
    description="Place a dimension aligned to the line between two points, offset perpendicular by a distance.",
    parameters={
        "p1": {**_POINT, "description": "First measured point"},
        "p2": {**_POINT, "description": "Second measured point"},
        "offset": {
            "type": "number",
            "description": "Perpendicular offset of the dimension line from the measured points",
        },
        "layer": {"type": "string", "description": "Layer to draw on (defaults to current layer)"},
    },
    required=["p1", "p2", "offset"],
)
def add_aligned_dimension(backend, p1, p2, offset, layer=None):
    return backend.add_aligned_dimension(point_from(p1), point_from(p2), offset, layer=layer)
