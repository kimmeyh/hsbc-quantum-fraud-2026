"""Render every submission PDF with its correct per-document settings.

Converted from PowerShell 2026-09-17 (F78, Sprint 16).

Sprint 5 retrospective, improvement 4. The appendix needs a 0.9in margin: at the
1in default it spills 230 characters onto a fourth page against a HARD 3-page
limit, and nothing in render_pdf.py knows that. The margin lived only in an ADR
paragraph, so any rebuild that did not read the ADR produced a silently
over-limit appendix.

THAT FAILURE REPRODUCED DURING THIS CONVERSION, which is a fair demonstration
that the script earns its place. Rendering the appendix directly at the 1in
default produced 4 pages and 6 extra words; at 0.9in it produced 3 pages and
text identical to the committed PDF.

This script is the single source of truth for how each document renders. Use it
instead of calling render_pdf.py directly.

Usage:
    python scripts/render_all.py
    python scripts/render_all.py --qci-package
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RENDER = ROOT / "scripts" / "render_pdf.py"

# (source, out, margin, landscape)
CORE = [
    ("docs/paper/proposal.md", "docs/paper/out/proposal.pdf", "1in", False),
    ("docs/paper/appendix.md", "docs/paper/out/appendix.pdf", "0.9in", False),
    ("docs/paper/team_profile.md", "docs/paper/out/team_profile.pdf", "1in", False),
]

QCI_PACKAGE = [
    ("docs/paper/proposal.md",
     "docs/qci_package/DRAFT_proposal.pdf", "1in", False),
    ("docs/paper/appendix.md",
     "docs/qci_package/DRAFT_appendix.pdf", "0.9in", False),
    # Source lives beside its outputs in docs/qci_package/, which is ignored:
    # private correspondence, not a submission document. Moved out of
    # docs/paper/out/ on 2026-09-18 so that directory holds only the three
    # PUBLISHED submission PDFs.
    ("docs/qci_package/qci_cover.md",
     "docs/qci_package/DRAFT_qci_cover.pdf", "1in", False),
    ("experiments/PREREGISTRATION.md",
     "docs/qci_package/DRAFT_preregistration.pdf", "1in", False),
    ("experiments/results/gate_report.md",
     "docs/qci_package/DRAFT_gate_report.pdf", "0.75in", True),
    ("docs/HARDWARE_REQUEST_B1_G0b.md",
     "docs/qci_package/DRAFT_hardware_plan.pdf", "1in", False),
    ("docs/QCI_EQC_MODELS_FEEDBACK.md",
     "docs/qci_package/DRAFT_eqc_models_feedback.pdf", "1in", False),
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--qci-package", action="store_true",
                    help="also render the QCi draft package")
    ap.add_argument("--paper", choices=("letter", "a4"), default="letter")
    args = ap.parse_args(argv)

    docs = CORE + (QCI_PACKAGE if args.qci_package else [])

    failures = []
    for source, out, margin, landscape in docs:
        src = ROOT / source
        if not src.exists():
            print(f"SKIP (missing source): {source}")
            continue
        cmd = [sys.executable, str(RENDER), "--source", str(src),
               "--out", str(ROOT / out), "--margin", margin,
               "--paper", args.paper]
        if landscape:
            cmd.append("--landscape")
        r = subprocess.run(cmd, capture_output=True, text=True)
        sys.stdout.write(r.stdout)
        if r.returncode != 0:
            sys.stderr.write(r.stderr)
            failures.append(source)

    if failures:
        print(f"\nFAILED: {len(failures)} document(s): {', '.join(failures)}")
        return 1
    print(f"\nRendered {len(docs)} document(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
