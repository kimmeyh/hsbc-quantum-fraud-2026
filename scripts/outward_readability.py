"""Can the recipient resolve everything in this document?

IMP-5, Sprint 18 retrospective. The QCi package went through three rounds of
revision AFTER the team lead reviewed it: two sections he wanted removed, a
pass to strip internal shorthand, and a note reconciling the ask against the
original request. The shorthand round is the one this script prevents -- it is
a mechanical check, and running it before handover costs seconds.

WHAT IT LOOKS FOR. Tokens that resolve only inside this repository:

    F87, F2b        backlog card IDs
    B1, B2, B3      internal hardware block names
    G0b             internal gate name
    H1b, H5         internal hypothesis IDs
    Sprint 18       internal sprint numbering
    prereg, MDE     unexpanded internal abbreviations

WHAT IT DELIBERATELY ALLOWS. Amendment references (A12, A31) read as citation
labels and the preregistration is public, so a reader can follow them. Anything
in a fenced code block, since code and error messages are quoted verbatim and a
variable named `B2` in a snippet is not jargon.

THIS IS A PROMPT, NOT A GATE. A hit is a question -- "would a QCi engineer know
what this means?" -- and some hits are fine in context. It exits non-zero so it
can be wired into a checklist, and `--allow` exempts a token with a reason.

Usage:
    python scripts/outward_readability.py docs/HARDWARE_PLAN_PHASE_2.md
    python scripts/outward_readability.py docs/*.md --allow B2
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# (pattern, what a recipient cannot resolve about it)
INTERNAL = (
    (r"\bF\d{1,3}\b", "backlog card ID"),
    (r"\bF\d{1,3}[a-z]\b", "backlog card ID"),
    (r"\bB[1-5]\b", "internal hardware block name"),
    (r"\bG0b?\b", "internal gate name"),
    (r"\bH[1-6][ab]?\b", "internal hypothesis ID"),
    (r"\bSprint \d+", "internal sprint number"),
    (r"\bprereg\b", "unexpanded internal abbreviation"),
    (r"\bMDE\b", "unexpanded acronym"),
    (r"\bIMP-\d+", "internal improvement ID"),
    (r"\bPR #\d+", "internal pull request"),
)

FENCE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`\n]+`")


def strip_code(text: str) -> str:
    """Blank out code spans, preserving offsets so line numbers stay true.

    Code is quoted verbatim from the library or the device, so a token inside
    it is evidence rather than jargon -- `run_hardware_f32.py:59-64` and a
    `repr()` sample both belong in the QCi feedback exactly as they are.
    """
    def blank(m: re.Match) -> str:
        return re.sub(r"[^\n]", " ", m.group(0))
    return INLINE_CODE.sub(blank, FENCE.sub(blank, text))


def scan(path: Path, allow: set[str]) -> list[tuple[int, str, str]]:
    text = strip_code(path.read_text(encoding="utf-8"))
    hits: list[tuple[int, str, str]] = []
    for pattern, why in INTERNAL:
        for m in re.finditer(pattern, text):
            token = m.group(0)
            if token in allow:
                continue
            line = text[:m.start()].count("\n") + 1
            hits.append((line, token, why))
    return sorted(set(hits))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--allow", action="append", default=[], metavar="TOKEN",
                    help="exempt a token; repeatable")
    args = ap.parse_args(argv)

    allow = set(args.allow)
    total = 0
    for raw in args.paths:
        p = Path(raw)
        if not p.is_file():
            print(f"  SKIP (not a file): {p}")
            continue
        hits = scan(p, allow)
        total += len(hits)
        if not hits:
            print(f"  CLEAN  {p}")
            continue
        print(f"  {len(hits)} hit(s)  {p}")
        for line, token, why in hits:
            print(f"      line {line:4d}  {token:12s} {why}")

    print()
    if total:
        print(f"{total} token(s) a recipient outside this repository cannot "
              "resolve.")
        print("Each is a QUESTION, not a verdict: would the reader know what "
              "this means?")
        print("If one is genuinely fine, re-run with --allow <token>.")
        return 1
    print("No unresolvable internal references found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
