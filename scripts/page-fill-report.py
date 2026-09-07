"""Per-page fill report, to be run BEFORE trimming an over-limit document.

Sprint 6 retro improvement 4. Two sprints running, an over-limit document was
attacked by trimming prose, re-rendering, and repeating -- about eight cycles
each time. Both times the actual cause was structural: a table forced an early
page break, so most of a page went to waste. Trimming prose could not recover
that; moving or narrowing the table did, in one edit.

The rule this encodes: when a document is over limit, find out WHERE the space
is going before deciding what to cut. A page with real white space above the
bottom margin is a break problem, not a length problem, and prose trimming will
not fix it.

MEASURED IN POINTS, NOT CHARACTERS -- and this correction is the point.

The first version of this tool counted extracted characters per page. That
instrument produced a false positive that cost a full card (F36): it reported
appendix pages 1 and 3 as UNDERFILL at 71% and 65% of median, and a Lua filter
was built to float the tables and reclaim the supposed waste. Direct
measurement then showed every page of that document running 680 to 724 points
of a 792 point page. There was no white space anywhere. The pages were full.

Character count is the wrong instrument whenever pages differ in composition. A
table spends a lot of vertical space on few characters; prose spends little. So
a table-heavy page always "underfills" a prose-heavy page by character count,
whether or not a single point of space is actually free.

What determines whether a page is full is the vertical extent of its text
block, so that is what this measures.
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

# A page whose text block stops more than this many points above the bottom of
# the other pages' text blocks has real, reclaimable white space on it. Below
# this, the gap is ordinary line-breaking slack, not a structural break.
#
# One blank line at 10pt with normal leading is about 12pt, so 36pt is roughly
# three lines: large enough not to fire on rounding, small enough to catch a
# table that pushed a third of a page of content forward.
UNDERFILL_SLACK_PT = 36.0

# A baseline separated from the text above it by more than this is not part of
# the text block. Normal leading at 10pt is about 12pt; the folio sits far
# lower, so 30pt separates the two without any ambiguity.
FOLIO_GAP_PT = 30.0


def _is_folio(text):
    """Is this text run a page number rather than content?

    Identified by WHAT IT IS, not by where it sits. An earlier version dropped
    whatever run was lowest when it sat more than FOLIO_GAP_PT below the run
    above it, which has the right shape for a folio -- and also for a section
    heading opening at the foot of a page, a short final paragraph after a
    table, or a lone caption. Probing found a heading at -645pt silently
    dropped on a page whose body ended at -600pt, which makes the page look
    fuller than it is and HIDES reclaimable space: the same class of error as
    the character counting this module was rewritten to remove.

    A folio is a short run of digits, or roman numerals for front matter.
    A heading is neither, so it survives.
    """
    t = text.strip()
    if not t or len(t) > 6:
        return False
    return t.isdigit() or (set(t.lower()) <= set("ivxlcdm") and t.isalpha())


def text_extent(page):
    """Return (top, bottom) of the page's text block in PDF user space.

    pypdf reports each text run's position through the visitor; the lowest
    CONTENT baseline is where the text block ends, which is what decides
    whether the page had room for more.
    """
    runs = []

    def visit(text, cm, tm, font, size):
        if text.strip():
            runs.append((tm[5], text))

    page.extract_text(visitor_text=visit)
    if not runs:
        return None

    ys = sorted({y for y, _ in runs}, reverse=True)

    # Drop the page-number folio, which sits at the same depth on every page
    # well below the body. Without this the folio IS the deepest baseline
    # everywhere, so every page reports 0pt free -- including a nearly empty
    # last page, the one case that matters most.
    #
    # Both conditions are required: the run must LOOK like a page number AND
    # sit clear of the body. A body line that happens to be the number "2"
    # inside a table would satisfy the first test but not the second.
    if len(ys) >= 2 and (ys[-2] - ys[-1]) > FOLIO_GAP_PT:
        lowest = ys[-1]
        if all(_is_folio(t) for y, t in runs if y == lowest):
            ys = ys[:-1]

    return max(ys), min(ys)


def report(path: Path) -> None:
    reader = PdfReader(str(path))
    pages = list(reader.pages)
    n = len(pages)
    limit = LIMITS.get(path.name)

    extents = [text_extent(pg) for pg in pages]
    # The bottom the document actually reaches: the lowest baseline any page
    # uses. A page stopping well above it left space on the table.
    bottoms = [e[1] for e in extents if e]
    deepest = min(bottoms) if bottoms else 0.0

    status = "" if limit is None else (
        f"  [{'OK' if n <= limit else 'OVER'} {n}/{limit}]")
    print(f"\n{path.name}{status}")

    slack = []
    for i, (pg, e) in enumerate(zip(pages, extents), 1):
        if not e:
            print(f"  p{i}: (no text)")
            slack.append(0.0)
            continue
        top, bottom = e
        used = top - bottom
        free = bottom - deepest          # points of white space below the text
        slack.append(max(0.0, free))
        bar = "#" * int(40 * used / max(used, 1) * (used / (top - deepest or 1)))
        flag = ""
        # The last page is expected to end early; it is the spill.
        if i < n and free > UNDERFILL_SLACK_PT:
            flag = f"  <- UNDERFILL: {free:.0f}pt free, a break ends this page early"
        print(f"  p{i}: {used:5.0f}pt used, {free:5.0f}pt free {bar}{flag}")

    if limit and n > limit:
        spill_top, spill_bottom = extents[-1] or (0.0, 0.0)
        spill = spill_top - spill_bottom
        waste = sum(slack[:-1])
        print(f"\n  spilling {spill:.0f}pt onto page {n}")
        print(f"  reclaimable white space on earlier pages: {waste:.0f}pt")
        if waste >= spill:
            print("  => FIX THE BREAK, not the prose. There is more space wasted")
            print("     above than is spilling below; find the table or heading")
            print("     ending a page early and narrow, shorten or move it.")
        else:
            print(f"  => genuine LENGTH problem: no structural fix will recover")
            print(f"     {spill:.0f}pt from {waste:.0f}pt of slack. About "
                  f"{spill - waste:.0f}pt of content has to go.")


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
