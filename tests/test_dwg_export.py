"""Tests for the DWG-export path.

The converters (ODA File Converter / accoreconsole) are not installed in the
Linux dev/CI container, so we can't exercise a real conversion here. What we CAN
test honestly: converter discovery, the exact command/script we construct, and
that a missing converter fails loudly rather than silently producing nothing.
"""
import os

import pytest

from junior_architect.backend import dwg_export
from junior_architect.backend.dxf_backend import DxfBackend
from junior_architect.geometry import Point


def test_build_oda_command_matches_documented_cli():
    cmd = dwg_export.build_oda_command("ODAFileConverter", "/in", "/out", "ACAD2018")
    # ODAFileConverter <inDir> <outDir> <version> <format> <recurse> <audit> <filter>
    assert cmd == ["ODAFileConverter", "/in", "/out", "ACAD2018", "DWG", "0", "1", "*.DXF"]


def test_build_saveas_script_saves_to_dwg_path():
    script = dwg_export.build_saveas_script("C:/tmp/out.dwg", version_token="2018")
    lines = script.splitlines()
    assert lines[0] == "FILEDIA" and lines[1] == "0"  # suppress dialog
    assert "_.SAVEAS" in lines
    assert "2018" in lines
    assert "C:/tmp/out.dwg" in lines
    assert "_.QUIT" in lines


def test_convert_raises_clearly_when_no_converter(tmp_path, monkeypatch):
    monkeypatch.setattr(dwg_export, "find_dwg_converter", lambda: None)
    with pytest.raises(RuntimeError, match="No DWG converter found"):
        dwg_export.convert_dxf_to_dwg(str(tmp_path / "a.dxf"), str(tmp_path / "a.dwg"))


def test_convert_oda_invokes_runner_and_moves_output(tmp_path):
    dxf = tmp_path / "src.dxf"
    dxf.write_text("dummy")
    dwg = tmp_path / "dest.dwg"
    calls = {}

    def fake_runner(cmd, check=False):
        # ODA writes <out_dir>/drawing.dwg; simulate that.
        out_dir = cmd[2]
        with open(os.path.join(out_dir, "drawing.dwg"), "w") as fh:
            fh.write("DWG")
        calls["cmd"] = cmd
        return None

    result = dwg_export.convert_dxf_to_dwg(
        str(dxf), str(dwg), converter=("oda", "ODAFileConverter"), runner=fake_runner
    )
    assert result == str(dwg)
    assert dwg.read_text() == "DWG"
    assert calls["cmd"][0] == "ODAFileConverter" and calls["cmd"][4] == "DWG"


def test_convert_oda_raises_if_no_output_produced(tmp_path):
    dxf = tmp_path / "src.dxf"
    dxf.write_text("dummy")

    def noop_runner(cmd, check=False):
        return None  # produces nothing

    with pytest.raises(RuntimeError, match="did not produce a DWG"):
        dwg_export.convert_dxf_to_dwg(
            str(dxf), str(tmp_path / "dest.dwg"), converter=("oda", "ODAFileConverter"), runner=noop_runner
        )


def test_convert_accoreconsole_builds_expected_argv(tmp_path):
    dxf = tmp_path / "src.dxf"
    dxf.write_text("dummy")
    dwg = tmp_path / "dest.dwg"
    seen = {}

    def fake_runner(cmd, check=False):
        seen["cmd"] = cmd
        # accoreconsole would save the dwg itself; simulate it.
        with open(dwg, "w") as fh:
            fh.write("DWG")
        return None

    dwg_export.convert_dxf_to_dwg(
        str(dxf), str(dwg), converter=("accoreconsole", "accoreconsole.exe"), runner=fake_runner
    )
    cmd = seen["cmd"]
    assert cmd[0] == "accoreconsole.exe"
    assert cmd[1] == "/i" and cmd[3] == "/s"
    assert cmd[4].endswith(".scr")
    assert dwg.read_text() == "DWG"


def test_dxf_backend_dwg_target_without_converter_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(dwg_export, "find_dwg_converter", lambda: None)
    backend = DxfBackend()
    backend.create_layer("A-WALL", color=4)
    backend.add_line(Point(0, 0), Point(5, 0), layer="A-WALL")
    with pytest.raises(RuntimeError, match="No DWG converter found"):
        backend.save_drawing(str(tmp_path / "out.dwg"))
    # DXF still works as the universal fallback.
    backend.save_drawing(str(tmp_path / "out.dxf"))
    assert (tmp_path / "out.dxf").is_file()
