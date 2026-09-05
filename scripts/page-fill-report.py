"""Per-page fill report, to be run BEFORE trimming an over-limit document.

Sprint 6 retro improvement 4. Two sprints running, an over-limit document was
attacked by trimming prose, re-rendering, and repeating -- about eight cycles
each time. Both times the actual cause was structural: a table forced an early
page break, so page 1 held 2,031 characters while page 3 held 2,816, wasting
most of a page. Trimming prose could not recover that; moving or narrowing the
table did, in one edit.

The rule this encodes: when a document is over limit, find out WHERE the space
is going before deciding what to cut. A page well below the median fill is a
break problem, not a length problem, and prose trimming will not fix it.

Usage:
    python scripts/page-fill-report.py docs/paper/out/appendix.pdf
    python scripts/page-fill-report.py            # all submission PDFs
"""
from __future__ import annotations

import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = [
    ROOT / "docs" / "paper" / "out" / "proposal.pdf",
    ROOT / "docs" / "paper" / "out" / "appendix.pdf",
    ROOT / "docs" / "paper" / "out" / "team_profile.pdf",
]
LIMITS = {"proposal.pdf": 6, "appendix.pdf": 3, "team_profile.pdf": 1}

# A page holding less than this fraction of the document's median fill is
# almost certainly ended early by a table or heading, not by running out of text.
UNDERFILL_RATIO = 0.85


def report(path: Path) -> None:
    reader = PdfReader(str(path))
    fills = [len(p.extract_text() or "") for p in reader.pages]
    n = len(fills)
    limit = LIMITS.get(path.name)
    median = sorted(fills)[len(fills) // 2] if fills else 0

    status = "" if limit is None else (
        f"  [{'OK' if n <= limit else 'OVER'} {n}/{limit}]")
    print(f"\n{path.name}{status}")
    for i, f in enumerate(fills, 1):
        bar = "#" * int(40 * f / max(median, 1))
        flag = ""
        if i < n and median and f < median * UNDERFILL_RATIO:
            flag = f"  <- UNDERFILL ({f/median:.0%} of median): a break ends this page early"
        print(f"  p{i}: {f:5d} {bar}{flag}")

    if limit and n > limit:
        spill = fills[-1]
        waste = sum(max(0, int(median - f)) for f in fills[:-1])
        print(f"\n  spilling {spill} chars onto page {n}")
        print(f"  reclaimable from underfilled pages: about {waste} chars")
        if waste >= spill:
            print("  => FIX THE BREAK, not the prose. There is more space wasted")
            print("     above than is spilling below; find the table or heading")
            print("     ending a page early and narrow, shorten or move it.")
        else:
            print(f"  => genuine length problem: cut about {spill - waste} chars")


def main() -> int:
    targets = [Path(a) for a in sys.argv[1:]] or DEFAULTS
    for t in targets:
        if t.exists():
            report(t)
        else:
            print(f"missing: {t}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
