import pytest

from junior_architect.backend.fake_backend import FakeBackend
from junior_architect.commands import registry


def _wall_backend():
    backend = FakeBackend()
    backend.create_layer("A-WALL")
    return backend


def test_single_opening_splits_wall_into_two_segments_with_jambs():
    backend = _wall_backend()
    result = registry.dispatch(
        "draw_wall_with_openings",
        backend,
        start=[0, 0],
        end=[5, 0],
        openings=[{"offset": 1.5, "width": 0.9}],
        thickness=0.2,
        layer="A-WALL",
    )
    polylines = [e for e in backend.entities if e.kind == "LWPOLYLINE"]
    lines = [e for e in backend.entities if e.kind == "LINE"]
    assert len(polylines) == 2
    assert len(lines) == 2  # one jamb per opening edge
    assert len(result["segments"]) == 2
    assert len(result["jambs"]) == 2

    # Segment extents along X: [0, 1.5] and [2.4, 5]
    extents = sorted((min(p.x for p in e.data["points"]), max(p.x for p in e.data["points"])) for e in polylines)
    assert extents[0] == (pytest.approx(0.0), pytest.approx(1.5))
    assert extents[1] == (pytest.approx(2.4), pytest.approx(5.0))

    # Jambs sit at the opening edges and span the wall thickness
    jamb_xs = sorted(e.data["start"].x for e in lines)
    assert jamb_xs == [pytest.approx(1.5), pytest.approx(2.4)]
    for e in lines:
        ys = sorted([e.data["start"].y, e.data["end"].y])
        assert ys[0] == pytest.approx(-0.1)
        assert ys[1] == pytest.approx(0.1)


def test_opening_flush_with_wall_start_yields_single_segment():
    backend = _wall_backend()
    result = registry.dispatch(
        "draw_wall_with_openings",
        backend,
        start=[0, 0],
        end=[4, 0],
        openings=[{"offset": 0, "width": 1.0}],
        layer="A-WALL",
    )
    assert len(result["segments"]) == 1
    assert len(result["jambs"]) == 2


def test_full_width_opening_yields_no_segments():
    backend = _wall_backend()
    result = registry.dispatch(
        "draw_wall_with_openings",
        backend,
        start=[0, 0],
        end=[2, 0],
        openings=[{"offset": 0, "width": 2.0}],
        layer="A-WALL",
    )
    assert result["segments"] == []
    assert len(result["jambs"]) == 2


def test_multiple_openings_are_sorted_before_cutting():
    backend = _wall_backend()
    result = registry.dispatch(
        "draw_wall_with_openings",
        backend,
        start=[0, 0],
        end=[10, 0],
        openings=[{"offset": 6, "width": 1.2}, {"offset": 1, "width": 0.9}],
        layer="A-WALL",
    )
    assert len(result["segments"]) == 3
    assert len(result["jambs"]) == 4


def test_openings_work_on_non_axis_aligned_walls():
    backend = _wall_backend()
    # 45-degree wall of length 10
    import math

    end = [10 * math.cos(math.radians(45)), 10 * math.sin(math.radians(45))]
    result = registry.dispatch(
        "draw_wall_with_openings",
        backend,
        start=[0, 0],
        end=end,
        openings=[{"offset": 4, "width": 1}],
        thickness=0.2,
        layer="A-WALL",
    )
    assert len(result["segments"]) == 2
    # Jamb length equals the wall thickness
    jamb = next(e for e in backend.entities if e.kind == "LINE")
    from junior_architect.geometry import distance

    assert distance(jamb.data["start"], jamb.data["end"]) == pytest.approx(0.2)


def test_overlapping_openings_raise():
    backend = _wall_backend()
    with pytest.raises(ValueError, match="overlaps"):
        registry.dispatch(
            "draw_wall_with_openings",
            backend,
            start=[0, 0],
            end=[5, 0],
            openings=[{"offset": 1, "width": 1.0}, {"offset": 1.5, "width": 1.0}],
        )


def test_opening_outside_wall_raises():
    backend = _wall_backend()
    with pytest.raises(ValueError, match="does not fit"):
        registry.dispatch(
            "draw_wall_with_openings",
            backend,
            start=[0, 0],
            end=[3, 0],
            openings=[{"offset": 2.5, "width": 1.0}],
        )


def test_zero_length_wall_raises():
    backend = _wall_backend()
    with pytest.raises(ValueError, match="zero-length"):
        registry.dispatch(
            "draw_wall_with_openings",
            backend,
            start=[1, 1],
            end=[1, 1],
            openings=[],
        )


def test_no_openings_draws_one_full_segment():
    backend = _wall_backend()
    result = registry.dispatch(
        "draw_wall_with_openings",
        backend,
        start=[0, 0],
        end=[5, 0],
        openings=[],
        layer="A-WALL",
    )
    assert len(result["segments"]) == 1
    assert result["jambs"] == []
