import pytest

from junior_architect.backend.fake_backend import FakeBackend
from junior_architect.commands import registry
from junior_architect.geometry import Point


def test_draw_line_records_entity():
    backend = FakeBackend()
    handle = registry.dispatch("draw_line", backend, start=[0, 0], end=[10, 0])
    entity = backend.entities[0]
    assert entity.kind == "LINE"
    assert entity.handle == handle
    assert entity.data["start"] == Point(0, 0, 0)
    assert entity.data["end"] == Point(10, 0, 0)


def test_draw_circle_uses_current_layer_by_default():
    backend = FakeBackend()
    registry.dispatch("draw_circle", backend, center=[5, 5], radius=2)
    assert backend.entities[0].layer == "0"


def test_draw_rectangle_produces_closed_four_point_polyline():
    backend = FakeBackend()
    registry.dispatch("draw_rectangle", backend, corner1=[0, 0], corner2=[4, 2])
    entity = backend.entities[0]
    assert entity.kind == "LWPOLYLINE"
    assert entity.data["closed"] is True
    xs = sorted({p.x for p in entity.data["points"]})
    ys = sorted({p.y for p in entity.data["points"]})
    assert xs == [0, 4]
    assert ys == [0, 2]


def test_draw_arc_converts_degrees_to_radians():
    backend = FakeBackend()
    registry.dispatch("draw_arc", backend, center=[0, 0], radius=1, start_angle=0, end_angle=90)
    entity = backend.entities[0]
    assert entity.data["start_angle"] == pytest.approx(0)
    assert entity.data["end_angle"] == pytest.approx(1.5707963267948966)


def test_add_text_records_content_and_rotation_radians():
    backend = FakeBackend()
    registry.dispatch("add_text", backend, position=[1, 1], content="Hello", height=0.3, rotation=180)
    entity = backend.entities[0]
    assert entity.kind == "TEXT"
    assert entity.data["content"] == "Hello"
    assert entity.data["rotation"] == pytest.approx(3.141592653589793)


def test_unknown_layer_raises():
    backend = FakeBackend()
    with pytest.raises(ValueError):
        registry.dispatch("draw_line", backend, start=[0, 0], end=[1, 1], layer="DOES_NOT_EXIST")
