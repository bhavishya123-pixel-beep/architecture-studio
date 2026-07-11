"""Document/session-level commands: new/open/save drawings, view control."""
from .registry import command


@command(
    name="new_drawing",
    description="Start a new drawing, optionally from a template.",
    parameters={"template": {"type": "string", "description": "Path to a .dwt template file (optional)"}},
    required=[],
)
def new_drawing(backend, template=None):
    backend.new_drawing(template=template)
    return {"status": "new drawing started"}


@command(
    name="open_drawing",
    description="Open an existing drawing file.",
    parameters={"path": {"type": "string", "description": "Path to a .dwg/.dxf file"}},
    required=["path"],
)
def open_drawing(backend, path):
    backend.open_drawing(path)
    return {"opened": path}


@command(
    name="save_drawing",
    description="Save the current drawing, optionally to a new path.",
    parameters={"path": {"type": "string", "description": "Destination path; defaults to the drawing's current path"}},
    required=[],
)
def save_drawing(backend, path=None):
    backend.save_drawing(path)
    return {"saved": path}


@command(
    name="zoom_extents",
    description="Zoom the current view to fit all drawing content.",
    parameters={},
    required=[],
)
def zoom_extents(backend):
    backend.zoom_extents()
    return {"status": "zoomed to extents"}
