"""In-memory AutoCAD stand-in.

Records every drafting operation instead of talking to a real AutoCAD
session, so command logic can be developed, demoed, and unit-tested on any
platform without a Windows/AutoCAD install.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from ..geometry import Point
from .base import AutoCADBackend


@dataclass
class Entity:
    kind: str
    handle: str
    layer: str
    data: Dict[str, Any] = field(default_factory=dict)


class FakeBackend(AutoCADBackend):
    def __init__(self) -> None:
        self.entities: List[Entity] = []
        self.layers: Dict[str, Dict[str, Any]] = {"0": {"color": 7, "linetype": "Continuous", "frozen": False}}
        self.current_layer = "0"
        self.drawing_path: Optional[str] = None
        self._next_handle = 1

    def _handle(self) -> str:
        h = f"E{self._next_handle:04X}"
        self._next_handle += 1
        return h

    def _resolve_layer(self, layer: Optional[str]) -> str:
        name = layer or self.current_layer
        if name not in self.layers:
            raise ValueError(f"Layer '{name}' does not exist; create it first")
        return name

    def _add(self, kind: str, layer: Optional[str], **data: Any) -> str:
        handle = self._handle()
        self.entities.append(Entity(kind, handle, self._resolve_layer(layer), data))
        return handle

    # document
    def new_drawing(self, template: Optional[str] = None) -> None:
        self.entities.clear()
        self.layers = {"0": {"color": 7, "linetype": "Continuous", "frozen": False}}
        self.current_layer = "0"
        self.drawing_path = None

    def open_drawing(self, path: str) -> None:
        self.drawing_path = path

    def save_drawing(self, path: Optional[str] = None) -> None:
        self.drawing_path = path or self.drawing_path

    def zoom_extents(self) -> None:
        pass

    # layers
    def create_layer(self, name: str, color: int = 7, linetype: str = "Continuous") -> None:
        self.layers[name] = {"color": color, "linetype": linetype, "frozen": False}

    def set_current_layer(self, name: str) -> None:
        if name not in self.layers:
            raise ValueError(f"Layer '{name}' does not exist; create it first")
        self.current_layer = name

    def set_layer_frozen(self, name: str, frozen: bool) -> None:
        if name not in self.layers:
            raise ValueError(f"Layer '{name}' does not exist; create it first")
        self.layers[name]["frozen"] = frozen

    # primitives
    def add_line(self, start: Point, end: Point, layer: Optional[str] = None) -> str:
        return self._add("LINE", layer, start=start, end=end)

    def add_polyline(self, points: Sequence[Point], closed: bool = False, layer: Optional[str] = None) -> str:
        return self._add("LWPOLYLINE", layer, points=list(points), closed=closed)

    def add_circle(self, center: Point, radius: float, layer: Optional[str] = None) -> str:
        return self._add("CIRCLE", layer, center=center, radius=radius)

    def add_arc(
        self, center: Point, radius: float, start_angle: float, end_angle: float, layer: Optional[str] = None
    ) -> str:
        return self._add("ARC", layer, center=center, radius=radius, start_angle=start_angle, end_angle=end_angle)

    def add_text(
        self, position: Point, height: float, content: str, layer: Optional[str] = None, rotation: float = 0.0
    ) -> str:
        return self._add("TEXT", layer, position=position, height=height, content=content, rotation=rotation)

    # dimensions
    def add_linear_dimension(
        self, p1: Point, p2: Point, dim_line_point: Point, layer: Optional[str] = None
    ) -> str:
        return self._add("DIMENSION_LINEAR", layer, p1=p1, p2=p2, dim_line_point=dim_line_point)

    def add_aligned_dimension(self, p1: Point, p2: Point, offset: float, layer: Optional[str] = None) -> str:
        return self._add("DIMENSION_ALIGNED", layer, p1=p1, p2=p2, offset=offset)

    # hatch
    def add_hatch(
        self, boundary: Sequence[Point], pattern: str = "ANSI31", scale: float = 1.0, layer: Optional[str] = None
    ) -> str:
        return self._add("HATCH", layer, boundary=list(boundary), pattern=pattern, scale=scale)

    # blocks
    def insert_block(
        self,
        name: str,
        insertion_point: Point,
        scale: float = 1.0,
        rotation: float = 0.0,
        layer: Optional[str] = None,
    ) -> str:
        return self._add(
            "INSERT", layer, name=name, insertion_point=insertion_point, scale=scale, rotation=rotation
        )
