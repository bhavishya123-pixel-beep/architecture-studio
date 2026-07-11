import math

import pytest

from junior_architect.backend.fake_backend import FakeBackend
from junior_architect.commands import registry
from junior_architect.geometry import distance


def test_draw_wall_creates_closed_offset_polyline():
    backend = FakeBackend()
    backend.create_layer("A-WALL")
    registry.dispatch("draw_wall", backend, start=[0, 0], end=[10, 0], thickness=0.2, layer="A-WALL")
    entity = backend.entities[-1]
    assert entity.kind == "LWPOLYLINE"
    assert entity.data["closed"] is True
    ys = sorted(p.y for p in entity.data["points"])
    assert ys[0] == pytest.approx(-0.1)
    assert ys[-1] == pytest.approx(0.1)


def test_add_door_leaf_length_matches_width_and_swing_arc_spans_90_degrees():
    backend = FakeBackend()
    backend.create_layer("A-DOOR")
    registry.dispatch(
        "add_door", backend, insertion_point=[0, 0], angle=0, width=0.9, swing="left", layer="A-DOOR"
    )
    leaf = backend.entities[0]
    arc = backend.entities[1]
    assert leaf.kind == "LINE"
    assert distance(leaf.data["start"], leaf.data["end"]) == pytest.approx(0.9)
    assert arc.kind == "ARC"
    assert arc.data["radius"] == pytest.approx(0.9)
    assert (arc.data["end_angle"] - arc.data["start_angle"]) == pytest.approx(math.pi / 2)


def test_add_door_invalid_swing_raises():
    backend = FakeBackend()
    with pytest.raises(ValueError):
        registry.dispatch("add_door", backend, insertion_point=[0, 0], angle=0, swing="sideways")


def test_add_window_opening_length_matches_width():
    backend = FakeBackend()
    backend.create_layer("A-WIND")
    registry.dispatch(
        "add_window", backend, insertion_point=[0, 0], angle=0, width=1.2, layer="A-WIND"
    )
    opening = backend.entities[0]
    assert opening.kind == "LINE"
    assert distance(opening.data["start"], opening.data["end"]) == pytest.approx(1.2)
    # main opening line + 2 end ticks
    assert len([e for e in backend.entities if e.kind == "LINE"]) == 3


def test_label_room_computes_area_and_places_text_at_centroid():
    backend = FakeBackend()
    backend.create_layer("A-ANNO-TEXT")
    registry.dispatch(
        "label_room",
        backend,
        name="Bedroom",
        boundary=[[0, 0], [4, 0], [4, 3], [0, 3]],
        layer="A-ANNO-TEXT",
    )
    entity = backend.entities[-1]
    assert entity.kind == "TEXT"
    assert "Bedroom" in entity.data["content"]
    assert "12.0" in entity.data["content"]  # area = 4 * 3
    assert entity.data["position"].x == pytest.approx(2.0)
    assert entity.data["position"].y == pytest.approx(1.5)
