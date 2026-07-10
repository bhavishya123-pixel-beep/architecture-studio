import math

import ezdxf
import pytest

from junior_architect.backend.dxf_backend import DxfBackend
from junior_architect.commands import registry
from junior_architect.geometry import Point


def _census(msp):
    counts = {}
    for e in msp:
        counts[e.dxftype()] = counts.get(e.dxftype(), 0) + 1
    return counts


def test_primitives_round_trip_through_a_real_dxf_file(tmp_path):
    path = tmp_path / "primitives.dxf"
    backend = DxfBackend(path=str(path))
    backend.create_layer("A-WALL", color=4)
    backend.add_line(Point(0, 0), Point(5, 0), layer="A-WALL")
    backend.add_polyline([Point(0, 1), Point(5, 1), Point(5, 2)], closed=True, layer="A-WALL")
    backend.add_circle(Point(7, 1), 0.5)
    backend.add_arc(Point(9, 1), 0.5, 0.0, math.pi / 2)
    backend.add_text(Point(0, 3), 0.25, "hello")
    backend.save_drawing()

    doc = ezdxf.readfile(str(path))
    msp = doc.modelspace()
    counts = _census(msp)
    assert counts["LINE"] == 1
    assert counts["LWPOLYLINE"] == 1
    assert counts["CIRCLE"] == 1
    assert counts["ARC"] == 1
    assert counts["TEXT"] == 1
    assert "A-WALL" in doc.layers
    assert doc.layers.get("A-WALL").color == 4

    line = msp.query("LINE")[0]
    assert line.dxf.layer == "A-WALL"
    assert tuple(line.dxf.end)[:2] == (5, 0)
    # Arc angles converted radians -> degrees at the ezdxf boundary.
    arc = msp.query("ARC")[0]
    assert arc.dxf.end_angle == pytest.approx(90.0)


def test_multiline_label_becomes_mtext(tmp_path):
    path = tmp_path / "label.dxf"
    backend = DxfBackend(path=str(path))
    backend.add_text(Point(2, 1.5), 0.25, "Bedroom 1\n12.0 m2")
    backend.save_drawing()
    msp = ezdxf.readfile(str(path)).modelspace()
    mtexts = msp.query("MTEXT")
    assert len(mtexts) == 1
    assert "Bedroom 1" in mtexts[0].text


def test_hatch_and_dimensions_round_trip(tmp_path):
    path = tmp_path / "hatch_dims.dxf"
    backend = DxfBackend(path=str(path))
    backend.add_hatch([Point(0, 0), Point(2, 0), Point(2, 1)], pattern="ANSI31", scale=2.0)
    backend.add_aligned_dimension(Point(0, 0), Point(5, 0), -0.8)
    backend.add_linear_dimension(Point(0, 0), Point(0, 3), Point(-0.8, 1.5))
    backend.save_drawing()
    msp = ezdxf.readfile(str(path)).modelspace()
    counts = _census(msp)
    assert counts["HATCH"] == 1
    assert counts["DIMENSION"] == 2
    hatch = msp.query("HATCH")[0]
    assert hatch.dxf.pattern_name == "ANSI31"


def test_layer_freeze_and_current_layer(tmp_path):
    backend = DxfBackend(path=str(tmp_path / "layers.dxf"))
    backend.create_layer("A-WIND", color=5)
    backend.set_current_layer("A-WIND")
    assert backend.doc.header["$CLAYER"] == "A-WIND"
    backend.set_layer_frozen("A-WIND", True)
    assert backend.doc.layers.get("A-WIND").is_frozen()
    backend.set_layer_frozen("A-WIND", False)
    assert not backend.doc.layers.get("A-WIND").is_frozen()
    with pytest.raises(ValueError, match="does not exist"):
        backend.set_current_layer("NOPE")


def test_insert_block_requires_definition(tmp_path):
    backend = DxfBackend(path=str(tmp_path / "blocks.dxf"))
    with pytest.raises(ValueError, match="not defined"):
        backend.insert_block("CHAIR", Point(0, 0))
    backend.doc.blocks.new(name="CHAIR")
    handle = backend.insert_block("CHAIR", Point(1, 1), scale=2.0, rotation=math.pi / 2)
    assert handle
    insert = backend.msp.query("INSERT")[0]
    assert insert.dxf.rotation == pytest.approx(90.0)
    assert insert.dxf.xscale == pytest.approx(2.0)


def test_full_floor_plan_writes_valid_dxf(tmp_path):
    path = tmp_path / "apartment.dxf"
    backend = DxfBackend(path=str(path))
    result = registry.dispatch(
        "draw_floor_plan",
        backend,
        rooms=[
            {"name": "Living Room", "corner": [0, 0], "width": 8, "height": 5,
             "doors": [{"wall": "south", "offset": 3.5, "width": 1.0}],
             "windows": [{"wall": "west", "offset": 1.5, "width": 1.5}]},
            {"name": "Bedroom 1", "corner": [0, 5], "width": 4, "height": 5,
             "doors": [{"wall": "south", "offset": 2.8, "width": 0.9}],
             "windows": [{"wall": "north", "offset": 1.4, "width": 1.2}]},
            {"name": "Bedroom 2", "corner": [4, 5], "width": 4, "height": 5,
             "doors": [{"wall": "south", "offset": 0.3, "width": 0.9}],
             "windows": [{"wall": "north", "offset": 1.4, "width": 1.2}]},
        ],
    )
    backend.save_drawing()
    assert result["rooms"] == 3 and result["walls_drawn"] == 6

    doc = ezdxf.readfile(str(path))
    msp = doc.modelspace()
    counts = _census(msp)
    assert counts["LWPOLYLINE"] == 12  # wall segments
    assert counts["ARC"] == 3  # door swings
    assert counts["MTEXT"] == 3  # room labels with areas
    assert counts["DIMENSION"] == 2  # overall extents
    assert counts["LINE"] == 24  # jambs, door leaves, window symbols
    for layer in ("A-WALL", "A-DOOR", "A-WIND", "A-ANNO-TEXT", "A-ANNO-DIMS"):
        assert layer in doc.layers
    # ezdxf validates the document on save; a second audit confirms integrity.
    auditor = doc.audit()
    assert not auditor.has_errors
