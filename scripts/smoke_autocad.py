"""Smoke-test the live AutoCAD COM backend, one operation at a time.

Run this ON WINDOWS with AutoCAD installed (it will start AutoCAD if needed):

    pip install -e ".[windows]"
    python scripts/smoke_autocad.py

It exercises every Win32ComBackend operation in a fresh drawing and prints a
PASS/FAIL line per operation with the exact COM error on failure, then saves
the result to %TEMP%\\junior_architect_smoke.dwg. Send any FAIL output back to
get the backend fixed — this is the only part of the package that can't be
tested off Windows.
"""
import math
import os
import sys
import tempfile
import traceback

from junior_architect.backend.win32_backend import Win32ComBackend
from junior_architect.geometry import Point

results = []


def step(name, fn):
    try:
        value = fn()
        results.append((name, True, value))
        print(f"PASS  {name}" + (f"  -> {value}" if value is not None else ""))
    except Exception as exc:
        results.append((name, False, exc))
        print(f"FAIL  {name}: {exc}")
        traceback.print_exc(limit=1)


def main() -> int:
    print("Connecting to AutoCAD (this may start it)...")
    backend = Win32ComBackend(visible=True)
    print("Connected.\n")

    step("new_drawing", lambda: backend.new_drawing())
    step("create_layer A-WALL", lambda: backend.create_layer("A-WALL", color=4))
    step("create_layer A-DOOR", lambda: backend.create_layer("A-DOOR", color=2))
    step("create_layer A-ANNO-DIMS", lambda: backend.create_layer("A-ANNO-DIMS", color=1))
    step("set_current_layer", lambda: backend.set_current_layer("A-WALL"))
    step("add_line", lambda: backend.add_line(Point(0, 0), Point(5, 0)))
    step("add_polyline (closed)", lambda: backend.add_polyline(
        [Point(0, 1), Point(5, 1), Point(5, 1.2), Point(0, 1.2)], closed=True))
    step("add_circle", lambda: backend.add_circle(Point(7, 0.5), 0.5))
    step("add_arc", lambda: backend.add_arc(Point(9, 0.5), 0.5, 0.0, math.pi / 2))
    step("add_text", lambda: backend.add_text(Point(0, 2), 0.25, "junior-architect smoke test"))
    step("add_text (rotated)", lambda: backend.add_text(Point(0, 3), 0.25, "rotated", rotation=math.pi / 4))
    step("add_linear_dimension", lambda: backend.add_linear_dimension(
        Point(0, 0), Point(5, 0), Point(2.5, -0.8), layer="A-ANNO-DIMS"))
    step("add_aligned_dimension", lambda: backend.add_aligned_dimension(
        Point(0, 1), Point(5, 1), 0.8, layer="A-ANNO-DIMS"))
    step("add_hatch", lambda: backend.add_hatch(
        [Point(6, 2), Point(8, 2), Point(8, 3), Point(6, 3)], pattern="ANSI31", scale=1.0))
    step("set_layer_frozen(True)", lambda: backend.set_layer_frozen("A-DOOR", True))
    step("set_layer_frozen(False)", lambda: backend.set_layer_frozen("A-DOOR", False))
    step("zoom_extents", lambda: backend.zoom_extents())

    out = os.path.join(tempfile.gettempdir(), "junior_architect_smoke.dwg")
    step(f"save_drawing -> {out}", lambda: backend.save_drawing(out))

    failed = [name for name, ok, _ in results if not ok]
    print(f"\n{len(results) - len(failed)}/{len(results)} operations passed.")
    if failed:
        print("Failed operations:", ", ".join(failed))
        return 1
    print("Live AutoCAD COM backend fully verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
