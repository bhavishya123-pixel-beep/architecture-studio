"""Common interface every AutoCAD automation backend must implement.

A backend translates primitive drafting operations into calls against a
real (COM-driven) or simulated AutoCAD drawing database. Angles at this
layer are always radians, matching AutoCAD's own COM API convention; the
degrees-for-humans conversion happens one layer up, in the command
modules that face the chat agent.
"""
from abc import ABC, abstractmethod
from typing import Optional, Sequence

from ..geometry import Point


class AutoCADBackend(ABC):
    # -- document / session -------------------------------------------------
    @abstractmethod
    def new_drawing(self, template: Optional[str] = None) -> None: ...

    @abstractmethod
    def open_drawing(self, path: str) -> None: ...

    @abstractmethod
    def save_drawing(self, path: Optional[str] = None) -> None: ...

    @abstractmethod
    def zoom_extents(self) -> None: ...

    # -- layers ---------------------------------------------------------
    @abstractmethod
    def create_layer(self, name: str, color: int = 7, linetype: str = "Continuous") -> None: ...

    @abstractmethod
    def set_current_layer(self, name: str) -> None: ...

    @abstractmethod
    def set_layer_frozen(self, name: str, frozen: bool) -> None: ...

    # -- primitives -----------------------------------------------------
    @abstractmethod
    def add_line(self, start: Point, end: Point, layer: Optional[str] = None) -> str: ...

    @abstractmethod
    def add_polyline(self, points: Sequence[Point], closed: bool = False, layer: Optional[str] = None) -> str: ...

    @abstractmethod
    def add_circle(self, center: Point, radius: float, layer: Optional[str] = None) -> str: ...

    @abstractmethod
    def add_arc(
        self, center: Point, radius: float, start_angle: float, end_angle: float, layer: Optional[str] = None
    ) -> str: ...

    @abstractmethod
    def add_text(
        self, position: Point, height: float, content: str, layer: Optional[str] = None, rotation: float = 0.0
    ) -> str: ...

    # -- dimensions -------------------------------------------------------
    @abstractmethod
    def add_linear_dimension(
        self, p1: Point, p2: Point, dim_line_point: Point, layer: Optional[str] = None
    ) -> str: ...

    @abstractmethod
    def add_aligned_dimension(self, p1: Point, p2: Point, offset: float, layer: Optional[str] = None) -> str: ...

    # -- hatching ---------------------------------------------------------
    @abstractmethod
    def add_hatch(
        self, boundary: Sequence[Point], pattern: str = "ANSI31", scale: float = 1.0, layer: Optional[str] = None
    ) -> str: ...

    # -- blocks -------------------------------------------------------------
    @abstractmethod
    def insert_block(
        self,
        name: str,
        insertion_point: Point,
        scale: float = 1.0,
        rotation: float = 0.0,
        layer: Optional[str] = None,
    ) -> str: ...
