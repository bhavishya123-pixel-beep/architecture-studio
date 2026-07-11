"""Hatching commands."""
from ..geometry import point_from
from .registry import command


@command(
    name="add_hatch",
    description="Fill a closed boundary with a hatch pattern (e.g. for floor finishes, sections).",
    parameters={
        "boundary": {
            "type": "array",
            "items": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 3},
            "minItems": 3,
            "description": "Ordered vertices of the closed boundary to hatch",
        },
        "pattern": {"type": "string", "description": "AutoCAD hatch pattern name, defaults to 'ANSI31'"},
        "scale": {"type": "number", "description": "Hatch pattern scale, defaults to 1.0"},
        "layer": {"type": "string", "description": "Layer to draw on (defaults to current layer)"},
    },
    required=["boundary"],
)
def add_hatch(backend, boundary, pattern="ANSI31", scale=1.0, layer=None):
    return backend.add_hatch([point_from(p) for p in boundary], pattern=pattern, scale=scale, layer=layer)
