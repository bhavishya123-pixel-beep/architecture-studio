"""Layer management commands (AutoCAD layer table operations)."""
from .registry import command


@command(
    name="create_layer",
    description=(
        "Create an AutoCAD layer if it doesn't already exist. Use standard architectural layer "
        "names where sensible, e.g. A-WALL, A-DOOR, A-WIND, A-ANNO-DIMS, A-ANNO-TEXT, A-FLOR-HATCH."
    ),
    parameters={
        "name": {"type": "string", "description": "Layer name"},
        "color": {"type": "integer", "description": "AutoCAD color index (ACI), 1-255. Defaults to 7 (white/black)."},
        "linetype": {"type": "string", "description": "Linetype name, defaults to 'Continuous'"},
    },
    required=["name"],
)
def create_layer(backend, name, color=7, linetype="Continuous"):
    backend.create_layer(name, color=color, linetype=linetype)
    return {"layer": name}


@command(
    name="set_current_layer",
    description="Set the current/active drawing layer; subsequent commands without an explicit layer draw onto it.",
    parameters={"name": {"type": "string", "description": "Layer name to make current"}},
    required=["name"],
)
def set_current_layer(backend, name):
    backend.set_current_layer(name)
    return {"current_layer": name}


@command(
    name="freeze_layer",
    description="Freeze a layer, hiding it and excluding it from regeneration.",
    parameters={"name": {"type": "string", "description": "Layer name"}},
    required=["name"],
)
def freeze_layer(backend, name):
    backend.set_layer_frozen(name, True)
    return {"layer": name, "frozen": True}


@command(
    name="thaw_layer",
    description="Thaw a previously frozen layer, making it visible again.",
    parameters={"name": {"type": "string", "description": "Layer name"}},
    required=["name"],
)
def thaw_layer(backend, name):
    backend.set_layer_frozen(name, False)
    return {"layer": name, "frozen": False}
