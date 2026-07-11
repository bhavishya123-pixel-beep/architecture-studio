# Environment Verification (Gate 0)

**This file records the ACTUAL environment this repository was last built in.
It is deliberately honest about what is and isn't available, per the project's
no-fabrication policy: no AutoCAD test result is claimed unless AutoCAD actually ran.**

## Where this was run

A Linux cloud container (Claude Code on the web), **not** a Windows workstation
with AutoCAD 2027. Commands run and their real outputs:

```text
$ uname -a
Linux vm 6.18.5 #1 SMP PREEMPT_DYNAMIC x86_64 GNU/Linux

$ ls "/mnt/c/Program Files/Autodesk"        # AutoCAD install
no Windows C: mount

$ which acad accoreconsole
no acad/accoreconsole on PATH

$ which dotnet
no dotnet

$ which ODAFileConverter TeighaFileConverter
no ODA/Teigha converter

$ python3 --version
Python 3.11.15

$ python3 -c "import ezdxf; print(ezdxf.__version__)"
1.4.4
```

## What this means

The AutoCAD-specific gates in `AUTOCAD_2027_PRODUCTION_PROMPT.md` — inspecting
the installed `acad.exe`/`accoreconsole.exe`, running a fixture DWG through the
core console, verifying the managed .NET API, producing tested native DWG — **cannot
be completed in this container.** They require running Claude Code on the Windows
machine where AutoCAD 2027 is installed. Nothing in this repo claims otherwise.

## What HAS been verified here (and how)

| Capability | Status | Evidence |
|---|---|---|
| DXF output with native objects (LWPOLYLINE, ARC, MTEXT, DIMENSION, HATCH, INSERT) | **Verified** | `tests/test_dxf_backend.py` writes real `.dxf`, reads it back with ezdxf, asserts entity census, runs ezdxf's auditor (0 errors) |
| Text/spec → editable multi-room floor plan | **Verified** | `tests/test_floorplan.py`, `examples/apartment.dxf` (audit-clean) |
| Wall openings, door/window symbols, room labels, dimensions | **Verified** | `tests/test_wall_openings.py`, `tests/test_architecture.py` |
| Command registry → Claude tool-use schemas | **Verified** | `tests/test_registry.py` |
| DWG-export command/script construction | **Verified (construction only)** | `tests/test_dwg_export.py` — argv/script are unit-tested; the real conversion is NOT run here (no converter installed) |
| Live AutoCAD COM automation (`Win32ComBackend`) | **NOT verified here** | No Windows/AutoCAD. Run `scripts/smoke_autocad.py` on the target machine |
| Native `.dwg` file production | **NOT verified here** | Needs ODA File Converter or `accoreconsole.exe`; neither is installed in this container |

## To verify the AutoCAD paths (on the Windows/AutoCAD 2027 machine)

```bat
pip install -e ".[windows]"
python scripts\smoke_autocad.py          REM exercises every COM op, prints PASS/FAIL

REM native DWG via the free ODA File Converter (or accoreconsole):
junior-architect --backend dxf --output plan.dwg --prompt "Draft a 2-bedroom apartment, 8x10m"
```

Record the real outputs of those runs here to complete Gate 0 on Windows.
