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
    python scripts/render_all.py                 # the three submission PDFs
    python scripts/render_all.py --qci-package   # the QCi package ONLY

The bare form now REFUSES, because all three submission PDFs are tracked and
are the bytes filed on 2026-09-12. That refusal is the correct outcome, not a
breakage: nothing should rebuild a submitted artifact in place.
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
    # THREE OUTPUT NAMES ARE THE ONES QCi SEES (F85, folded into F86). They
    # carry spaces on purpose: this package is read by a person, not a build.
    # Every consumer must quote them.
    #
    # The SOURCES are deliberately NOT renamed. `experiments/results/gate_report.md`
    # is referenced by score_gates.py and several tests; renaming it would touch
    # the evidence pipeline for a presentational reason.
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
     "docs/qci_package/Phase 1 - Results Against Preregistered Criteria.pdf", "0.75in", True),
    # HARDWARE_REQUEST_B1_G0b.md is NOT the source here. That document is the
    # Phase 1 request for blocks B1 and G0b, executed 2026-09-03, and it is a
    # dated record of what was approved. QCi needs the PHASE 2 plan, which is
    # a different document. The Phase 1 request stays in the repository
    # unchanged as the historical record.
    ("docs/HARDWARE_PLAN_PHASE_2.md",
     "docs/qci_package/Phase 1 - Hardware Plan for Phase 2.pdf", "1in", False),
    ("docs/QCI_EQC_MODELS_FEEDBACK.md",
     "docs/qci_package/Phase 1 - eqc_models Feedback.pdf", "1in", False),
]


def is_tracked(rel: str) -> bool:
    """True if git tracks this path. Tracked PDFs under docs/paper/out/ are
    the SUBMITTED artifacts."""
    r = subprocess.run(["git", "ls-files", "--error-unmatch", rel],
                       cwd=ROOT, capture_output=True, text=True)
    return r.returncode == 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--qci-package", action="store_true",
                    help="render the QCi package ONLY (does not touch the "
                         "submitted PDFs)")
    ap.add_argument("--paper", choices=("letter", "a4"), default="letter")
    args = ap.parse_args(argv)

    # `--qci-package` renders the QCi package ONLY. It used to mean "CORE AND
    # the package", which made rebuilding the submitted PDFs an unavoidable
    # side effect of producing QCi's copies. Sprint 17 Task C hit exactly that:
    # a run intended to prove an unrelated guard overwrote all three filed
    # artifacts, twice.
    docs = QCI_PACKAGE if args.qci_package else CORE

    # REFUSE TO REBUILD A SUBMITTED ARTIFACT (Sprint 16 IMP-1, and again in
    # Sprint 17 Task C). A PDF carries a per-build /ID trailer, so a rebuild is
    # never byte-identical even when the content is: the file stops being the
    # one that was filed on 2026-09-12. In Sprint 16 that cost an Acronis
    # restore.
    #
    # THERE IS NO OVERRIDE FLAG, deliberately. The first version of this guard
    # had one, and the very next command in the same session passed it -- not
    # to rebuild a submission, but because the flag was the quickest way to get
    # an unrelated test to run. An escape hatch that is easier to reach than
    # the correct path is not a guard.
    #
    # To inspect what a source renders to, point --out at a scratch path via
    # render_pdf.py directly. To genuinely re-issue a submitted document, do it
    # deliberately: delete the tracked PDF in its own commit, with the reason in
    # the sprint record, and render it fresh.
    blocked = [out for _s, out, _m, _l in docs
               if out.endswith(".pdf") and is_tracked(out)]
    if blocked:
        print("REFUSING to rebuild submitted artifact(s):")
        for b in blocked:
            print(f"  {b}")
        print("\nThese PDFs are tracked in git and are the bytes filed on "
              "2026-09-12. A rebuild changes the /ID trailer, so the file is "
              "no longer the submitted one even if the text is identical.\n\n"
              "There is no override flag. To inspect a render, use "
              "render_pdf.py with --out pointing at a scratch path.")
        return 1

    failures = []
    missing = []
    for source, out, margin, landscape in docs:
        src = ROOT / source
        if not src.exists():
            # A MISSING SOURCE IS A FAILURE, not a note. This previously
            # printed SKIP and continued, so a renamed or moved document
            # produced "Rendered N document(s)" and exit 0 with that document
            # absent from the package. Same class as the confidentiality
            # scanner's missing-file bypass fixed in Sprint 16: a step that
            # skips its input has produced nothing and said it succeeded.
            missing.append(source)
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

    if missing:
        print(f"\nMISSING SOURCE: {len(missing)} document(s): "
              f"{', '.join(missing)}")
    if failures:
        print(f"\nFAILED: {len(failures)} document(s): {', '.join(failures)}")
    if missing or failures:
        return 1
    print(f"\nRendered {len(docs)} document(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
