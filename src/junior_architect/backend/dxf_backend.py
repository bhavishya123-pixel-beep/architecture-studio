"""File-based backend: writes real DXF files via ezdxf — no AutoCAD required.

This is the fully-verifiable automation path on any platform: the agent drafts
into an in-memory DXF document, `save_drawing` writes a `.dxf` that AutoCAD
(or any CAD viewer) opens natively. Angle convention at this interface is
radians, matching :class:`AutoCADBackend`; ezdxf wants degrees, so conversion
happens here.
"""
import math
from typing import Optional, Sequence

from ..geometry import Point
from .base import AutoCADBackend

try:
    import ezdxf
    from ezdxf import zoom as ezdxf_zoom
except ImportError:  # pragma: no cover - exercised only without the dependency
    ezdxf = None
    ezdxf_zoom = None


def _require_ezdxf() -> None:
    if ezdxf is None:
        raise RuntimeError("ezdxf is required for DxfBackend. Install it with `pip install ezdxf`.")


class DxfBackend(AutoCADBackend):
    """Drafts into a DXF document; save_drawing writes it to disk."""

    def __init__(self, path: Optional[str] = None) -> None:
        _require_ezdxf()
        self.path = path
        self._new_document()

    def _new_document(self) -> None:
        # setup=True loads standard linetypes, text styles, and dim styles.
        self.doc = ezdxf.new("R2018", setup=True)
        self.msp = self.doc.modelspace()

    def _attribs(self, layer: Optional[str]) -> dict:
        return {"layer": layer} if layer else {}

    # -- document / session -------------------------------------------------
    def new_drawing(self, template: Optional[str] = None) -> None:
        # DXF templates aren't supported; always start from a clean document.
        self._new_document()

    def open_drawing(self, path: str) -> None:
        self.doc = ezdxf.readfile(path)
        self.msp = self.doc.modelspace()
        self.path = path

    def save_drawing(self, path: Optional[str] = None) -> None:
        target = path or self.path
        if not target:
            raise ValueError("No output path set; pass one to save_drawing() or the DxfBackend constructor")
        self.doc.saveas(target)
        self.path = target

    def zoom_extents(self) -> None:
        ezdxf_zoom.extents(self.msp)

    # -- layers ---------------------------------------------------------
    def create_layer(self, name: str, color: int = 7, linetype: str = "Continuous") -> None:
        if name in self.doc.layers:
            layer = self.doc.layers.get(name)
            layer.color = color
            layer.dxf.linetype = linetype
        else:
            self.doc.layers.add(name, color=color, linetype=linetype)

    def set_current_layer(self, name: str) -> None:
        if name not in self.doc.layers:
            raise ValueError(f"Layer '{name}' does not exist; create it first")
        self.doc.header["$CLAYER"] = name

    def set_layer_frozen(self, name: str, frozen: bool) -> None:
        layer = self.doc.layers.get(name)
        if frozen:
            layer.freeze()
        else:
            layer.thaw()

    # -- primitives -----------------------------------------------------
    def add_line(self, start: Point, end: Point, layer: Optional[str] = None) -> str:
        entity = self.msp.add_line(start.as_tuple(), end.as_tuple(), dxfattribs=self._attribs(layer))
        return entity.dxf.handle

    def add_polyline(self, points: Sequence[Point], closed: bool = False, layer: Optional[str] = None) -> str:
        entity = self.msp.add_lwpolyline(
            [(p.x, p.y) for p in points], close=closed, dxfattribs=self._attribs(layer)
        )
        return entity.dxf.handle

    def add_circle(self, center: Point, radius: float, layer: Optional[str] = None) -> str:
        entity = self.msp.add_circle(center.as_tuple(), radius, dxfattribs=self._attribs(layer))
        return entity.dxf.handle

    def add_arc(
        self, center: Point, radius: float, start_angle: float, end_angle: float, layer: Optional[str] = None
    ) -> str:
        entity = self.msp.add_arc(
            center.as_tuple(),
            radius,
            math.degrees(start_angle),
            math.degrees(end_angle),
            dxfattribs=self._attribs(layer),
        )
        return entity.dxf.handle

    def add_text(
        self, position: Point, height: float, content: str, layer: Optional[str] = None, rotation: float = 0.0
    ) -> str:
        # Single-line TEXT can't hold newlines; use MTEXT for multi-line labels.
        attribs = self._attribs(layer)
        if "\n" in content:
            attribs["char_height"] = height
            attribs["rotation"] = math.degrees(rotation)
            entity = self.msp.add_mtext(content, dxfattribs=attribs)
            entity.set_location(position.as_tuple())
        else:
            attribs["height"] = height
            attribs["rotation"] = math.degrees(rotation)
            entity = self.msp.add_text(content, dxfattribs=attribs)
            entity.set_placement(position.as_tuple())
        return entity.dxf.handle

    # -- dimensions -------------------------------------------------------
    # ezdxf's default "EZDXF" dimstyle multiplies displayed measurements by 100
    # (drawn-in-meters, labeled-in-cm); override so text equals drawing units.
    _DIM_OVERRIDE = {"dimlfac": 1.0}

    def add_linear_dimension(
        self, p1: Point, p2: Point, dim_line_point: Point, layer: Optional[str] = None
    ) -> str:
        dim = self.msp.add_linear_dim(
            base=dim_line_point.as_tuple(),
            p1=p1.as_tuple(),
            p2=p2.as_tuple(),
            override=dict(self._DIM_OVERRIDE),
            dxfattribs=self._attribs(layer),
        )
        dim.render()
        return dim.dimension.dxf.handle

    def add_aligned_dimension(self, p1: Point, p2: Point, offset: float, layer: Optional[str] = None) -> str:
        dim = self.msp.add_aligned_dim(
            p1=p1.as_tuple(),
            p2=p2.as_tuple(),
            distance=offset,
            override=dict(self._DIM_OVERRIDE),
            dxfattribs=self._attribs(layer),
        )
        dim.render()
        return dim.dimension.dxf.handle

    # -- hatching ---------------------------------------------------------
    def add_hatch(
        self, boundary: Sequence[Point], pattern: str = "ANSI31", scale: float = 1.0, layer: Optional[str] = None
    ) -> str:
        hatch = self.msp.add_hatch(dxfattribs=self._attribs(layer))
        hatch.set_pattern_fill(pattern, scale=scale)
        hatch.paths.add_polyline_path([(p.x, p.y) for p in boundary], is_closed=True)
        return hatch.dxf.handle

    # -- blocks -------------------------------------------------------------
    def insert_block(
        self,
        name: str,
        insertion_point: Point,
        scale: float = 1.0,
        rotation: float = 0.0,
        layer: Optional[str] = None,
    ) -> str:
        if name not in self.doc.blocks:
            raise ValueError(f"Block '{name}' is not defined in the drawing")
        attribs = self._attribs(layer)
        attribs.update(
            {"xscale": scale, "yscale": scale, "zscale": scale, "rotation": math.degrees(rotation)}
        )
        entity = self.msp.add_blockref(name, insertion_point.as_tuple(), dxfattribs=attribs)
        return entity.dxf.handle
