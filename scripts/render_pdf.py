"""Render a Markdown source to submission-grade PDF (ADR-0012 toolchain).

Converted from PowerShell 2026-09-17 (F78, Sprint 16).

Markdown -> PDF via pandoc + xelatex. Page size is set through the LaTeX
geometry package, so the document is laid out at that size from the start.

HISTORY, so this is not reintroduced: an earlier version routed through Word
(pandoc -> docx -> Word SaveAs) and set PageSetup.PaperSize AFTER opening the
document. Word did not reflow, so it emitted 11x17 TABLOID pages while reporting
plausible page counts. Page size and page count are both submission requirements
(requirements-matrix B1), so this script verifies BOTH after rendering and fails
loudly on either.

CROSS-OS NOTES (the reason this conversion is not mechanical):

  - xelatex discovery differs per platform. PATH is tried first on both; the
    fallback candidates are MiKTeX locations on Windows and TeX Live locations
    on Linux. If neither finds it, the script says which locations it checked
    rather than "not found".
  - The PowerShell version narrowed PATH to the TeX bin plus system32 while
    invoking pandoc, to keep a stray toolchain off the path. The Python version
    passes the engine by absolute path instead, which achieves the same thing
    without mutating the environment.
  - The original shelled out to `.venv/Scripts/python.exe` to verify the PDF.
    That is one of the 21 hardcoded interpreter paths F78 removes; verification
    now happens in-process.

Usage:
    python scripts/render_pdf.py --source docs/paper/proposal.md \\
        --out docs/paper/out/proposal.pdf [--paper letter|a4] [--margin 1in]
        [--lua-filter f.lua ...] [--landscape]
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (width, height) in points -> human name.
PAGE_SIZES = {
    (612, 792): "US Letter",
    (595, 842): "A4",
    (792, 1224): "TABLOID 11x17",
    (792, 612): "US Letter landscape",
    (842, 595): "A4 landscape",
}

WINDOWS_XELATEX = [
    r"%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64\xelatex.exe",
    r"%ProgramFiles%\MiKTeX\miktex\bin\x64\xelatex.exe",
    r"C:\miktex\miktex\bin\x64\xelatex.exe",
]
POSIX_XELATEX = [
    "/usr/bin/xelatex",
    "/usr/local/bin/xelatex",
    "/usr/local/texlive/2025/bin/x86_64-linux/xelatex",
    "/usr/local/texlive/2024/bin/x86_64-linux/xelatex",
]


def find_xelatex() -> tuple[str | None, list[str]]:
    found = shutil.which("xelatex")
    if found:
        return found, []
    candidates = WINDOWS_XELATEX if os.name == "nt" else POSIX_XELATEX
    expanded = [os.path.expandvars(c) for c in candidates]
    for c in expanded:
        if Path(c).exists():
            return c, expanded
    return None, expanded


def verify(out: Path, expected: str) -> tuple[int, str]:
    """Page count and page size, read from the produced PDF.

    In-process rather than through a second interpreter: the original shelled
    out to a hardcoded .venv path, which is exactly what F78 removes.
    """
    from pypdf import PdfReader

    reader = PdfReader(str(out))
    box = reader.pages[0].mediabox
    w, h = round(float(box.width)), round(float(box.height))
    name = PAGE_SIZES.get((w, h), f"OTHER {w}x{h}pt")
    if name != expected:
        raise SystemExit(
            f"WRONG PAGE SIZE: produced {name}, expected {expected}, for {out}")
    return len(reader.pages), name


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--paper", choices=("letter", "a4"), default="letter")
    ap.add_argument("--margin", default="1in")
    ap.add_argument("--lua-filter", action="append", default=[])
    ap.add_argument("--landscape", action="store_true")
    args = ap.parse_args(argv)

    src = Path(args.source).resolve()
    if not src.exists():
        raise SystemExit(f"source not found: {src}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    # A PDF open in a viewer cannot be overwritten on Windows, and the failure
    # is otherwise reported as a pandoc error with no useful cause.
    if out.exists():
        try:
            with out.open("r+b"):
                pass
        except OSError:
            raise SystemExit(
                f"Output PDF is LOCKED by another process: {out}. Close it "
                "(a PDF viewer is the usual cause) and re-run.")

    xelatex, checked = find_xelatex()
    if not xelatex:
        raise SystemExit(
            "xelatex not found. Install MiKTeX (Windows) or TeX Live (Linux), "
            "or add its bin directory to PATH.\nChecked PATH and:\n  "
            + "\n  ".join(checked))

    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise SystemExit("pandoc not found on PATH.")

    filters = []
    for f in args.lua_filter:
        fp = Path(f) if Path(f).is_absolute() else ROOT / f
        if not fp.exists():
            raise SystemExit(f"Lua filter not found: {f}")
        filters.append(f"--lua-filter={fp}")

    geom = "a4paper" if args.paper == "a4" else "letterpaper"
    cmd = [pandoc, str(src), "-o", str(out), f"--pdf-engine={xelatex}",
           *filters]
    if args.landscape:
        cmd += ["-V", "geometry:landscape"]
    cmd += ["-V", f"geometry:{geom}", "-V", f"geometry:margin={args.margin}",
            "-V", "fontsize=10pt"]

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-2000:] + "\n")
        raise SystemExit(f"pandoc/xelatex failed on {args.source}")

    expected = "A4" if args.paper == "a4" else "US Letter"
    if args.landscape:
        expected += " landscape"

    pages, size = verify(out, expected)
    print(f"PDF written: {out} ({pages} pages, {size})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
