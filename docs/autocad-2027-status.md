# AutoCAD 2027 Production Spec — Honest Status & Gap Analysis

This maps the current repository against `AUTOCAD_2027_PRODUCTION_PROMPT.md`. It
is a truthful status report, not a claim of completion. The spec targets a
Windows machine with AutoCAD 2027; parts of it cannot be executed or verified in
the Linux container this repo is developed in (see `environment-verification.md`).

## What the spec asks for vs. what exists today

| Spec requirement | Status | Notes |
|---|---|---|
| Text-to-CAD → validated editable drawing, native objects | **Working (DXF)** | `draw_floor_plan` + agent produce real LWPOLYLINE/ARC/MTEXT/DIMENSION objects, audited by ezdxf. Output is DXF; DWG via converter (below). |
| Native **DWG** output | **Partial** | `dwg_export.py` shells to ODA File Converter or `accoreconsole.exe`. Command construction is tested; **the conversion itself is unverified** until run on a machine with a converter. |
| Existing-DWG automation (open/inspect/modify/annotate/plot) | **Partial** | `Win32ComBackend` can open/modify via COM (Windows only, unverified here). DXF read is possible via ezdxf; a full inspection/query API is not yet built. |
| Image-to-CAD (raster/sketch → calibrated underlay + traced geometry) | **Not started** | Requires an image pipeline (edge/vector extraction, calibration). Not attempted — would be fabrication to claim otherwise. |
| Optional design-image generation → same image-to-CAD pipeline | **Not started** | Needs a configured image provider + provenance. Not attempted. |
| Validation report per drawing | **Partial** | ezdxf `audit()` is run in tests; a user-facing per-drawing validation report is not yet emitted. |
| Capability catalogue (`docs/autocad-command-catalog.md`, matrix CSV) | **Not produced** | The spec requires each row be *verified* against the installed AutoCAD/docs. That verification can't happen in this container, and an unverified catalogue marked "verified" would violate the spec. To be produced on the Windows machine. |
| Tests run against `accoreconsole.exe` / full AutoCAD | **Not done here** | No AutoCAD in this environment. `scripts/smoke_autocad.py` is ready to run there. |

## Architecture that IS in place (and tested)

- **Backend abstraction** (`AutoCADBackend`) with four implementations: `FakeBackend`
  (in-memory), `DxfBackend` (real DXF files), `Win32ComBackend` (live AutoCAD COM),
  `LoggingBackend` (trace / dry-run wrapper).
- **20+ drafting commands** exposed both as Python calls and Claude tool-use schemas.
- **Whole-building generation** in one call (`draw_floor_plan`) with shared-wall
  merging, cut openings, symbols, labels, dimensions.
- **52 passing tests**, all runnable without AutoCAD.

## Honest path to the full spec (must run on Windows + AutoCAD 2027)

1. **Gate 0 on Windows** — run `scripts/smoke_autocad.py`; record real outputs; confirm
   `accoreconsole.exe` opens a fixture DWG. Fill in `environment-verification.md`.
2. **Native DWG** — install ODA File Converter (free) or use `accoreconsole`; run the
   DWG export end-to-end; confirm the SAVEAS token/version for the installed build.
3. **Capability catalogue** — build it incrementally, marking each row `test_status`
   only after an actual automated run against `accoreconsole`/COM.
4. **Existing-DWG automation** — extend the COM/DXF backends with inspection/query,
   layouts, plotting, and a validation-report emitter.
5. **Image-to-CAD** — design the pipeline separately (calibration + tracing); keep it
   honest about confidence and never emit fake geometry as if traced.

This document should be updated with real evidence (log paths, artifacts) as each
step is actually completed on the target machine.
