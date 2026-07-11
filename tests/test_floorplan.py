import pytest

from junior_architect.backend.fake_backend import FakeBackend
from junior_architect.commands import registry
from junior_architect.commands.floorplan import plan_floor


def _kinds(backend):
    counts = {}
    for e in backend.entities:
        counts[e.kind] = counts.get(e.kind, 0) + 1
    return counts


# --- planner (pure) -----------------------------------------------------


def test_single_room_plans_four_walls():
    plan = plan_floor([{"name": "Studio", "corner": [0, 0], "width": 4, "height": 3}])
    assert len(plan["walls"]) == 4
    assert plan["doors"] == []
    assert plan["windows"] == []
    assert len(plan["labels"]) == 1


def test_adjacent_rooms_share_walls():
    rooms = [
        {"name": "A", "corner": [0, 0], "width": 4, "height": 3},
        {"name": "B", "corner": [4, 0], "width": 4, "height": 3},
    ]
    plan = plan_floor(rooms)
    # Naively 8 walls; merged: 1 south + 1 north (collinear touching spans merge)
    # + 3 verticals (x=0, shared x=4, x=8).
    assert len(plan["walls"]) == 5
    souths = [w for w in plan["walls"] if w["start"][1] == 0 and w["end"][1] == 0]
    assert len(souths) == 1
    assert souths[0]["start"][0] == 0 and souths[0]["end"][0] == 8


def test_door_on_shared_wall_cuts_opening_once():
    rooms = [
        {"name": "A", "corner": [0, 0], "width": 4, "height": 3,
         "doors": [{"wall": "east", "offset": 1.0, "width": 0.9}]},
        {"name": "B", "corner": [4, 0], "width": 4, "height": 3},
    ]
    plan = plan_floor(rooms)
    shared = next(w for w in plan["walls"] if w["start"] == [4, 0])
    assert shared["openings"] == [{"offset": 1.0, "width": 0.9}]
    assert len(plan["doors"]) == 1
    door = plan["doors"][0]
    assert door["insertion_point"] == [4, 1.0]
    assert door["angle"] == 90.0


def test_same_door_declared_by_both_rooms_dedupes():
    rooms = [
        {"name": "A", "corner": [0, 0], "width": 4, "height": 3,
         "doors": [{"wall": "east", "offset": 1.0, "width": 0.9}]},
        {"name": "B", "corner": [4, 0], "width": 4, "height": 3,
         "doors": [{"wall": "west", "offset": 1.0, "width": 0.9}]},
    ]
    plan = plan_floor(rooms)
    shared = next(w for w in plan["walls"] if w["start"] == [4, 0])
    assert shared["openings"] == [{"offset": 1.0, "width": 0.9}]
    assert len(plan["doors"]) == 1


def test_door_too_wide_for_wall_raises():
    with pytest.raises(ValueError, match="does not fit"):
        plan_floor([
            {"name": "A", "corner": [0, 0], "width": 3, "height": 3,
             "doors": [{"wall": "south", "offset": 2.5, "width": 1.0}]}
        ])


def test_unknown_wall_name_raises():
    with pytest.raises(ValueError, match="Unknown wall"):
        plan_floor([
            {"name": "A", "corner": [0, 0], "width": 3, "height": 3,
             "doors": [{"wall": "up", "offset": 1, "width": 0.9}]}
        ])


def test_non_positive_room_raises():
    with pytest.raises(ValueError, match="positive width and height"):
        plan_floor([{"name": "A", "corner": [0, 0], "width": 0, "height": 3}])


def test_empty_plan_raises():
    with pytest.raises(ValueError, match="at least one room"):
        plan_floor([])


# --- draw_floor_plan command (against FakeBackend) ----------------------


def test_draw_floor_plan_single_room_entity_census():
    backend = FakeBackend()
    result = registry.dispatch(
        "draw_floor_plan",
        backend,
        rooms=[
            {
                "name": "Bedroom 1",
                "corner": [0, 0],
                "width": 4,
                "height": 3,
                "doors": [{"wall": "south", "offset": 1.5, "width": 0.9}],
                "windows": [{"wall": "north", "offset": 1.4, "width": 1.2}],
            }
        ],
    )
    assert result == {"rooms": 1, "walls_drawn": 4, "doors": 1, "windows": 1, "dimensions": True}
    for layer in ("A-WALL", "A-DOOR", "A-WIND", "A-ANNO-TEXT", "A-ANNO-DIMS"):
        assert layer in backend.layers

    kinds = _kinds(backend)
    # Walls: south (2 segs) + north (2 segs) + west + east = 6 polylines.
    assert kinds["LWPOLYLINE"] == 6
    # Lines: 4 jambs + 1 door leaf + 3 window lines = 8.
    assert kinds["LINE"] == 8
    assert kinds["ARC"] == 1  # door swing
    assert kinds["TEXT"] == 1  # room label
    assert kinds["DIMENSION_ALIGNED"] == 2  # overall width + height

    label = next(e for e in backend.entities if e.kind == "TEXT")
    assert "Bedroom 1" in label.data["content"]
    assert "12.0" in label.data["content"]


def test_draw_floor_plan_two_rooms_shares_wall_and_connects_them():
    backend = FakeBackend()
    result = registry.dispatch(
        "draw_floor_plan",
        backend,
        rooms=[
            {"name": "Living", "corner": [0, 0], "width": 5, "height": 4,
             "doors": [{"wall": "east", "offset": 1.5, "width": 0.9}]},
            {"name": "Bedroom", "corner": [5, 0], "width": 4, "height": 4,
             "windows": [{"wall": "east", "offset": 1.4, "width": 1.2}]},
        ],
        dimensions=False,
    )
    assert result["walls_drawn"] == 5  # merged south, merged north, x=0, shared x=5, x=9
    assert result["doors"] == 1
    assert result["windows"] == 1
    assert result["dimensions"] is False
    kinds = _kinds(backend)
    assert kinds.get("DIMENSION_ALIGNED", 0) == 0
    # Shared wall x=5 has 2 segments; wall x=9 has 2 (window); souths+norths+x=0 are solid:
    # 2 + 2 + 1 + 1 + 1 = 7 polylines.
    assert kinds["LWPOLYLINE"] == 7
    assert kinds["TEXT"] == 2


def test_draw_floor_plan_dimensions_span_full_extents():
    backend = FakeBackend()
    registry.dispatch(
        "draw_floor_plan",
        backend,
        rooms=[
            {"name": "A", "corner": [0, 0], "width": 4, "height": 3},
            {"name": "B", "corner": [4, 0], "width": 4, "height": 5},
        ],
    )
    dims = [e for e in backend.entities if e.kind == "DIMENSION_ALIGNED"]
    assert len(dims) == 2
    spans = sorted(
        (round(abs(d.data["p2"].x - d.data["p1"].x) + abs(d.data["p2"].y - d.data["p1"].y), 6)) for d in dims
    )
    assert spans == [5.0, 8.0]  # overall height, overall width
