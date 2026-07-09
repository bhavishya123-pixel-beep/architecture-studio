"""A backend wrapper that logs every drafting operation, with an optional dry-run mode.

Wrap any real :class:`AutoCADBackend` (e.g. ``Win32ComBackend``) to get a
human-readable trace of exactly what the agent is doing — invaluable for
debugging the live AutoCAD/COM path, which can't be unit-tested off Windows.

In ``dry_run`` mode the wrapper logs what *would* happen and returns synthetic
handles instead of touching the wrapped backend, so you can preview an agent's
whole drafting plan against real AutoCAD without drawing anything.
"""
import logging
from typing import Optional, Sequence

from ..geometry import Point
from .base import AutoCADBackend

logger = logging.getLogger("junior_architect")


def _fmt(value) -> str:
    if isinstance(value, Point):
        return f"({value.x:g}, {value.y:g}, {value.z:g})"
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_fmt(v) for v in value) + "]"
    return repr(value)


def _fmt_kwargs(**kwargs) -> str:
    return ", ".join(f"{k}={_fmt(v)}" for k, v in kwargs.items() if v is not None)


class LoggingBackend(AutoCADBackend):
    """Delegates to a wrapped backend while logging each call.

    :param inner: the backend to wrap and delegate to.
    :param dry_run: when True, mutating operations are logged but NOT forwarded
        to ``inner``; a synthetic ``DRY-<n>`` handle is returned instead.
    """

    def __init__(self, inner: AutoCADBackend, dry_run: bool = False) -> None:
        self.inner = inner
        self.dry_run = dry_run
        self._dry_handle = 0

    def _log(self, op: str, **kwargs) -> None:
        prefix = "[dry-run] " if self.dry_run else ""
        logger.info("%s%s(%s)", prefix, op, _fmt_kwargs(**kwargs))

    def _synthetic_handle(self) -> str:
        self._dry_handle += 1
        return f"DRY-{self._dry_handle:04d}"

    # -- document / session -------------------------------------------------
    def new_drawing(self, template: Optional[str] = None) -> None:
        self._log("new_drawing", template=template)
        if not self.dry_run:
            self.inner.new_drawing(template=template)

    def open_drawing(self, path: str) -> None:
        self._log("open_drawing", path=path)
        if not self.dry_run:
            self.inner.open_drawing(path)

    def save_drawing(self, path: Optional[str] = None) -> None:
        self._log("save_drawing", path=path)
        if not self.dry_run:
            self.inner.save_drawing(path)

    def zoom_extents(self) -> None:
        self._log("zoom_extents")
        if not self.dry_run:
            self.inner.zoom_extents()

    # -- layers ---------------------------------------------------------
    def create_layer(self, name: str, color: int = 7, linetype: str = "Continuous") -> None:
        self._log("create_layer", name=name, color=color, linetype=linetype)
        if not self.dry_run:
            self.inner.create_layer(name, color=color, linetype=linetype)

    def set_current_layer(self, name: str) -> None:
        self._log("set_current_layer", name=name)
        if not self.dry_run:
            self.inner.set_current_layer(name)

    def set_layer_frozen(self, name: str, frozen: bool) -> None:
        self._log("set_layer_frozen", name=name, frozen=frozen)
        if not self.dry_run:
            self.inner.set_layer_frozen(name, frozen)

    # -- primitives -----------------------------------------------------
    def add_line(self, start: Point, end: Point, layer: Optional[str] = None) -> str:
        self._log("add_line", start=start, end=end, layer=layer)
        if self.dry_run:
            return self._synthetic_handle()
        return self.inner.add_line(start, end, layer=layer)

    def add_polyline(self, points: Sequence[Point], closed: bool = False, layer: Optional[str] = None) -> str:
        self._log("add_polyline", points=points, closed=closed, layer=layer)
        if self.dry_run:
            return self._synthetic_handle()
        return self.inner.add_polyline(points, closed=closed, layer=layer)

    def add_circle(self, center: Point, radius: float, layer: Optional[str] = None) -> str:
        self._log("add_circle", center=center, radius=radius, layer=layer)
        if self.dry_run:
            return self._synthetic_handle()
        return self.inner.add_circle(center, radius, layer=layer)

    def add_arc(
        self, center: Point, radius: float, start_angle: float, end_angle: float, layer: Optional[str] = None
    ) -> str:
        self._log("add_arc", center=center, radius=radius, start_angle=start_angle, end_angle=end_angle, layer=layer)
        if self.dry_run:
            return self._synthetic_handle()
        return self.inner.add_arc(center, radius, start_angle, end_angle, layer=layer)

    def add_text(
        self, position: Point, height: float, content: str, layer: Optional[str] = None, rotation: float = 0.0
    ) -> str:
        self._log("add_text", position=position, height=height, content=content, layer=layer, rotation=rotation)
        if self.dry_run:
            return self._synthetic_handle()
        return self.inner.add_text(position, height, content, layer=layer, rotation=rotation)

    # -- dimensions -------------------------------------------------------
    def add_linear_dimension(
        self, p1: Point, p2: Point, dim_line_point: Point, layer: Optional[str] = None
    ) -> str:
        self._log("add_linear_dimension", p1=p1, p2=p2, dim_line_point=dim_line_point, layer=layer)
        if self.dry_run:
            return self._synthetic_handle()
        return self.inner.add_linear_dimension(p1, p2, dim_line_point, layer=layer)

    def add_aligned_dimension(self, p1: Point, p2: Point, offset: float, layer: Optional[str] = None) -> str:
        self._log("add_aligned_dimension", p1=p1, p2=p2, offset=offset, layer=layer)
        if self.dry_run:
            return self._synthetic_handle()
        return self.inner.add_aligned_dimension(p1, p2, offset, layer=layer)

    # -- hatching ---------------------------------------------------------
    def add_hatch(
        self, boundary: Sequence[Point], pattern: str = "ANSI31", scale: float = 1.0, layer: Optional[str] = None
    ) -> str:
        self._log("add_hatch", boundary=boundary, pattern=pattern, scale=scale, layer=layer)
        if self.dry_run:
            return self._synthetic_handle()
        return self.inner.add_hatch(boundary, pattern=pattern, scale=scale, layer=layer)

    # -- blocks -------------------------------------------------------------
    def insert_block(
        self,
        name: str,
        insertion_point: Point,
        scale: float = 1.0,
        rotation: float = 0.0,
        layer: Optional[str] = None,
    ) -> str:
        self._log("insert_block", name=name, insertion_point=insertion_point, scale=scale, rotation=rotation, layer=layer)
        if self.dry_run:
            return self._synthetic_handle()
        return self.inner.insert_block(name, insertion_point, scale=scale, rotation=rotation, layer=layer)
