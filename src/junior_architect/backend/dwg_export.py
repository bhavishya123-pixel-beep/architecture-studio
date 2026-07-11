"""Convert DXF to native DWG using an external converter.

ezdxf writes DXF, not DWG. To produce a true `.dwg`, we shell out to one of two
externally-installed converters, preferring whichever is present:

1. **ODA File Converter** (Open Design Alliance, free) — a batch tool with a
   stable, documented CLI:
   ``ODAFileConverter <inDir> <outDir> <outVersion> <outFormat> <recurse> <audit> [filter]``
   e.g. ``ODAFileConverter in out ACAD2018 DWG 0 1 *.DXF``.
   Docs: https://ezdxf.readthedocs.io/en/stable/addons/odafc.html and
   https://www.opendesign.com/guestfiles/oda_file_converter

2. **AutoCAD Core Console** (``accoreconsole.exe``, ships with AutoCAD 2027) —
   runs headless and executes a script on a drawing:
   ``accoreconsole.exe /i <input.dxf> /s <script.scr> /l en-US``.
   The script SAVEAS's to DWG. Docs (Autodesk):
   https://static.au-uw2-prd.autodesk.com/Class_Handout_BES227196_AutoCAD_Scripting_from_the_Core_AutoCAD_Core_Console_Mike_Best.pdf

IMPORTANT: neither converter exists in the Linux CI/dev container, so the
conversion itself is only exercised on a machine that has one installed. The
command/script *construction* below is unit-tested here; the exact accoreconsole
SAVEAS token may need adjustment for a specific AutoCAD build (verify against the
installed docs, per project policy). The ODA path is the more deterministic one.
"""
import os
import shutil
import subprocess
import tempfile
from typing import Callable, List, Optional, Tuple

# Common install locations checked in addition to PATH.
_ODA_CANDIDATES = [
    r"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe",
    r"C:\Program Files\ODA\ODAFileConverter.exe",
    "/usr/bin/ODAFileConverter",
    "/opt/ODAFileConverter/ODAFileConverter",
]
_ACCORE_CANDIDATES = [
    r"C:\Program Files\Autodesk\AutoCAD 2027\accoreconsole.exe",
]


def _first_existing(names: List[str]) -> Optional[str]:
    for name in names:
        found = shutil.which(name) if os.path.basename(name) == name else (name if os.path.isfile(name) else None)
        if found:
            return found
    return None


def find_dwg_converter() -> Optional[Tuple[str, str]]:
    """Return ``(kind, path)`` for the first available converter, or None.

    kind is 'oda' or 'accoreconsole'. ODA is preferred for its deterministic CLI.
    """
    oda = _first_existing(["ODAFileConverter", "ODAFileConverter.exe", *_ODA_CANDIDATES])
    if oda:
        return ("oda", oda)
    accore = _first_existing(["accoreconsole", "accoreconsole.exe", *_ACCORE_CANDIDATES])
    if accore:
        return ("accoreconsole", accore)
    return None


def build_oda_command(exe: str, in_dir: str, out_dir: str, version: str = "ACAD2018") -> List[str]:
    """Batch-convert every *.DXF in in_dir to DWG of the given version into out_dir."""
    return [exe, in_dir, out_dir, version, "DWG", "0", "1", "*.DXF"]


def build_saveas_script(dwg_path: str, version_token: str = "2018") -> str:
    """AutoCAD script (.scr) that saves the open drawing as DWG at dwg_path.

    FILEDIA 0 suppresses the file dialog so SAVEAS reads its filename from the
    script. The drawing's folder should be in TRUSTEDPATHS for the save to
    succeed (documented accoreconsole requirement).
    """
    return "\n".join(
        [
            "FILEDIA",
            "0",
            "_.SAVEAS",
            version_token,
            dwg_path.replace("\\", "/"),
            "FILEDIA",
            "1",
            "_.QUIT",
            "Y",
            "",
        ]
    )


def convert_dxf_to_dwg(
    dxf_path: str,
    dwg_path: str,
    version: str = "ACAD2018",
    converter: Optional[Tuple[str, str]] = None,
    runner: Callable[..., "subprocess.CompletedProcess"] = subprocess.run,
) -> str:
    """Convert dxf_path to dwg_path, returning dwg_path on success.

    Raises RuntimeError if no converter is available or the output isn't produced.
    ``converter`` and ``runner`` are injectable for testing.
    """
    resolved = converter or find_dwg_converter()
    if resolved is None:
        raise RuntimeError(
            "No DWG converter found. Install the free ODA File Converter "
            "(https://www.opendesign.com/guestfiles/oda_file_converter) or run on a machine with "
            "AutoCAD's accoreconsole.exe. DXF output works everywhere; native DWG needs one of these."
        )
    kind, exe = resolved

    if kind == "oda":
        with tempfile.TemporaryDirectory() as in_dir, tempfile.TemporaryDirectory() as out_dir:
            staged = os.path.join(in_dir, "drawing.dxf")
            shutil.copyfile(dxf_path, staged)
            runner(build_oda_command(exe, in_dir, out_dir, version), check=True)
            produced = os.path.join(out_dir, "drawing.dwg")
            if not os.path.isfile(produced):
                raise RuntimeError(f"ODA File Converter did not produce a DWG in {out_dir}")
            shutil.move(produced, dwg_path)
    else:  # accoreconsole
        with tempfile.TemporaryDirectory() as work:
            script = os.path.join(work, "saveas.scr")
            with open(script, "w") as fh:
                fh.write(build_saveas_script(os.path.abspath(dwg_path)))
            runner([exe, "/i", os.path.abspath(dxf_path), "/s", script, "/l", "en-US"], check=True)
        if not os.path.isfile(dwg_path):
            raise RuntimeError(
                f"accoreconsole did not produce {dwg_path}. Ensure the output folder is in "
                "TRUSTEDPATHS and the SAVEAS version token matches your AutoCAD build."
            )
    return dwg_path
