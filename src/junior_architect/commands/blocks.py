"""Block insertion commands."""
import math

from ..geometry import point_from
from .registry import command


@command(
    name="insert_block",
    description="Insert an existing block definition (e.g. a furniture or fixture symbol) at a point.",
    parameters={
        "name": {
            "type": "string",
            "description": "Block name, must already be defined in the drawing or a loaded block library",
        },
        "insertion_point": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 3},
        "scale": {"type": "number", "description": "Uniform scale factor, defaults to 1.0"},
        "rotation": {"type": "number", "description": "Rotation in degrees, defaults to 0"},
        "layer": {"type": "string", "description": "Layer to draw on (defaults to current layer)"},
    },
    required=["name", "insertion_point"],
)
def insert_block(backend, name, insertion_point, scale=1.0, rotation=0.0, layer=None):
    return backend.insert_block(
        name, point_from(insertion_point), scale=scale, rotation=math.radians(rotation), layer=layer
    )
