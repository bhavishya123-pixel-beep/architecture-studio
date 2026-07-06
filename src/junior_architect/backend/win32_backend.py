"""Real AutoCAD backend, driven live over COM/ActiveX Automation.

Only usable on Windows with a licensed AutoCAD install already running (or
launchable). The `win32com`/`pythoncom` imports are deferred so the rest of
this package stays importable — and testable via FakeBackend — on any
platform.
"""
from typing import Optional, Sequence

from ..geometry import Point
from .base import AutoCADBackend

try:
    import pythoncom
    import win32com.client
except ImportError:  # pragma: no cover - exercised only on Windows with pywin32
    win32com = None
    pythoncom = None


def _require_win32() -> None:
    if win32com is None:
        raise RuntimeError(
            "pywin32 is required for Win32ComBackend. Install it with "
            "`pip install junior-architect[windows]` on a Windows machine "
            "with AutoCAD installed."
        )


def _doubles(values: Sequence[float]):
    """Pack floats into the VARIANT double array AutoCAD's COM API expects."""
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, list(values))


def _point3d(p: Point):
    return _doubles(p.as_tuple())


class Win32ComBackend(AutoCADBackend):
    """Drives a live AutoCAD session via its ActiveX Automation COM API."""

    def __init__(self, visible: bool = True) -> None:
        _require_win32()
        self.app = win32com.client.Dispatch("AutoCAD.Application")
        self.app.Visible = visible
        if self.app.Documents.Count == 0:
            self.app.Documents.Add()
        self.doc = self.app.ActiveDocument
        self.model = self.doc.ModelSpace

    def _layer(self, name: Optional[str]):
        return name or self.doc.ActiveLayer.Name

    def _set_layer(self, entity, layer: Optional[str]) -> None:
        entity.Layer = self._layer(layer)

    # -- document / session -------------------------------------------------
    def new_drawing(self, template: Optional[str] = None) -> None:
        if template:
            self.doc = self.app.Documents.Add(template)
        else:
            self.doc = self.app.Documents.Add()
        self.model = self.doc.ModelSpace

    def open_drawing(self, path: str) -> None:
        self.doc = self.app.Documents.Open(path)
        self.model = self.doc.ModelSpace

    def save_drawing(self, path: Optional[str] = None) -> None:
        if path:
            self.doc.SaveAs(path)
        else:
            self.doc.Save()

    def zoom_extents(self) -> None:
        self.app.ZoomExtents()

    # -- layers ---------------------------------------------------------
    def create_layer(self, name: str, color: int = 7, linetype: str = "Continuous") -> None:
        layer = self.doc.Layers.Add(name)
        layer.color = color
        try:
            layer.Linetype = linetype
        except Exception:
            # Linetype must be loaded into the drawing first; fall back silently
            # to whatever the layer already has rather than failing the whole call.
            pass

    def set_current_layer(self, name: str) -> None:
        self.doc.ActiveLayer = self.doc.Layers.Item(name)

    def set_layer_frozen(self, name: str, frozen: bool) -> None:
        self.doc.Layers.Item(name).Freeze = frozen

    # -- primitives -----------------------------------------------------
    def add_line(self, start: Point, end: Point, layer: Optional[str] = None) -> str:
        line = self.model.AddLine(_point3d(start), _point3d(end))
        self._set_layer(line, layer)
        return line.Handle

    def add_polyline(self, points: Sequence[Point], closed: bool = False, layer: Optional[str] = None) -> str:
        flat = []
        for p in points:
            flat.extend([p.x, p.y])
        pl = self.model.AddLightWeightPolyline(_doubles(flat))
        pl.Closed = closed
        self._set_layer(pl, layer)
        return pl.Handle

    def add_circle(self, center: Point, radius: float, layer: Optional[str] = None) -> str:
        circle = self.model.AddCircle(_point3d(center), radius)
        self._set_layer(circle, layer)
        return circle.Handle

    def add_arc(
        self, center: Point, radius: float, start_angle: float, end_angle: float, layer: Optional[str] = None
    ) -> str:
        arc = self.model.AddArc(_point3d(center), radius, start_angle, end_angle)
        self._set_layer(arc, layer)
        return arc.Handle

    def add_text(
        self, position: Point, height: float, content: str, layer: Optional[str] = None, rotation: float = 0.0
    ) -> str:
        text = self.model.AddText(content, _point3d(position), height)
        text.Rotation = rotation
        self._set_layer(text, layer)
        return text.Handle

    # -- dimensions -------------------------------------------------------
    def add_linear_dimension(
        self, p1: Point, p2: Point, dim_line_point: Point, layer: Optional[str] = None
    ) -> str:
        dim = self.model.AddDimAligned(_point3d(p1), _point3d(p2), _point3d(dim_line_point))
        self._set_layer(dim, layer)
        return dim.Handle

    def add_aligned_dimension(self, p1: Point, p2: Point, offset: float, layer: Optional[str] = None) -> str:
        from ..geometry import offset_line_perpendicular

        _, mid = offset_line_perpendicular(p1, p2, offset)
        dim = self.model.AddDimAligned(_point3d(p1), _point3d(p2), _point3d(mid))
        self._set_layer(dim, layer)
        return dim.Handle

    # -- hatching ---------------------------------------------------------
    def add_hatch(
        self, boundary: Sequence[Point], pattern: str = "ANSI31", scale: float = 1.0, layer: Optional[str] = None
    ) -> str:
        hatch = self.model.AddHatch(0, pattern, True)  # 0 = acHatchPatternTypePredefined
        loop = [self.model.AddLightWeightPolyline(_doubles([c for p in boundary for c in (p.x, p.y)]))]
        loop[0].Closed = True
        loop_array = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, loop)
        hatch.AppendOuterLoop(loop_array)
        hatch.PatternScale = scale
        hatch.Evaluate()
        self._set_layer(hatch, layer)
        return hatch.Handle

    # -- blocks -------------------------------------------------------------
    def insert_block(
        self,
        name: str,
        insertion_point: Point,
        scale: float = 1.0,
        rotation: float = 0.0,
        layer: Optional[str] = None,
    ) -> str:
        insert = self.model.InsertBlock(_point3d(insertion_point), name, scale, scale, scale, rotation)
        self._set_layer(insert, layer)
        return insert.Handle
