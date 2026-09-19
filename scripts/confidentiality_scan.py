"""Pre-send / pre-publication confidentiality scan (Stage 7; F19, F10).

Converted from PowerShell 2026-09-17 (F78, Sprint 16).

Scans the MARKDOWN SOURCES of an outgoing package for content that must never
leave this repository, and reports findings with file and line so a human can
adjudicate each one. Exits 1 on any HIGH finding.

  HIGH    employer references; credential values; account identifiers;
          QPU balances tied to a named account; .env content
  REVIEW  absolute local paths; personal email addresses; anything naming a
          specific machine

This is a scan, not a guarantee. The team lead walks every HIGH and REVIEW
finding before sending, per the F19 acceptance criteria.

Usage:
    python scripts/confidentiality_scan.py docs/paper/proposal.md docs/paper/appendix.md
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# RETIRED 2026-09-11 (F37): a 'Private repo URL' rule matching
# `hsbc-quantum-fraud-2026`. It was correct while the repository was private,
# because citing a URL a reader cannot open is a defect. The repository is now
# public, so the citation is REQUIRED -- Appendix C's "every figure regenerates
# from the public repository" depends on it. Leaving the rule in place blocked a
# correct document on every scan.
#
# If visibility is ever reverted, restore it here AND re-check every document
# that cites the URL:
#     ("Private repo URL", r"(?i)hsbc-quantum-fraud-2026"),

HIGH = [
    ("Employer name", r"(?i)progressive"),
    ("Employer repo/remote", r"(?i)github\.com/(?!kimmeyh)[A-Za-z0-9_.-]+"),
    ("API token value",
     r"(?i)(api[_-]?(key|token)|QCI_TOKEN|QCI_API_KEY)\s*[=:]\s*['\"]?[A-Za-z0-9._\-]{16,}"),
    ("QPU balance (account)",
     r"(?i)(balance|remaining)[^.\n]{0,40}\d{3,}\s*(QPU|second)"),
    ("dotenv content", r"(?m)^\s*(QCI_API_URL|QCI_TOKEN|QCI_API_KEY)\s*="),
]

REVIEW = [
    ("Absolute local path", r"(?i)[A-Z]:\\(Data|Users)\\"),
    ("WSL mount path", r"/mnt/[a-z]/"),
    ("Personal email",
     r"[A-Za-z0-9._%+-]+@(aol|gmail|yahoo|outlook|hotmail)\.com"),
    ("Named machine", r"(?i)\bkimme\b"),
]


def read_scannable(path: Path) -> str:
    """Decode a file, or REFUSE to certify it.

    `errors="replace"` silently mangled any non-UTF-8 file into replacement
    characters that match no rule, so the gate reported "0 HIGH, 0 REVIEW" on a
    UTF-16 file containing both an employer name and an API token. UTF-16 is
    what PowerShell's `>` redirection and Notepad's older "Unicode" option both
    produce, so it is a plausible way a cover note reaches this repository.

    That is the PowerShell single-line-file bug wearing different clothes: a
    file the scanner cannot read is reported as a file with nothing in it.
    Found by the PR #120 review.
    """
    for encoding in ("utf-8-sig", "utf-16", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except (UnicodeDecodeError, UnicodeError):
            continue
        except OSError as exc:
            raise SystemExit(
                f"UNREADABLE: {path}: {exc}\nRESULT: BLOCKED. The gate cannot "
                "certify a file it could not read.")
    raise SystemExit(
        f"UNDECODABLE: {path}\nRESULT: BLOCKED. The gate cannot certify a file "
        "it could not decode.")


def scan_file(path: Path) -> tuple[list[str], list[str]]:
    high: list[str] = []
    review: list[str] = []
    text = read_scannable(path)
    for lineno, line in enumerate(text.splitlines(), 1):
        for name, pattern in HIGH:
            if re.search(pattern, line):
                high.append(f"  HIGH   {path}:{lineno}  {name}\n"
                            f"         {line.strip()[:110]}")
        for name, pattern in REVIEW:
            if re.search(pattern, line):
                review.append(f"  REVIEW {path}:{lineno}  {name}\n"
                              f"         {line.strip()[:110]}")
    return high, review


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="+", help="markdown files to scan")
    args = ap.parse_args(argv)

    all_high: list[str] = []
    all_review: list[str] = []
    unscannable: list[str] = []
    scanned = 0

    for raw in args.paths:
        # Accept a comma-separated list too: the PowerShell version took
        # -Paths a,b and that form is in the workflow docs.
        for part in str(raw).split(","):
            part = part.strip()
            if not part:
                continue
            p = Path(part)
            # A path that cannot be scanned is a BLOCKING condition, not a
            # note. The PowerShell counted a missing file as a HIGH finding;
            # this conversion printed MISSING and continued, so a typo, a
            # renamed document or an unexpanded glob produced "Scanned 0
            # file(s)" and exit 0. A gate that skips its input has certified
            # nothing. Found by the PR #120 review.
            if not p.exists():
                unscannable.append(f"MISSING: {p}")
                continue
            if not p.is_file():
                unscannable.append(f"NOT A FILE: {p}")
                continue
            scanned += 1
            h, r = scan_file(p)
            all_high.extend(h)
            all_review.extend(r)

    for line in all_high + all_review:
        print(line)
    for line in unscannable:
        print(f"  {line}")

    print(f"\nScanned {scanned} file(s): {len(all_high)} HIGH, "
          f"{len(all_review)} REVIEW, {len(unscannable)} UNSCANNABLE")

    if all_high:
        print("RESULT: BLOCKED. Resolve every HIGH finding before this package "
              "leaves the repository.")
        return 1

    # "I could not check this" is a DISTINCT outcome from "I checked and it was
    # clean", and both of the next two blocks exist to keep them distinct. That
    # conflation is the class this repository keeps paying for.
    if unscannable:
        print(f"RESULT: BLOCKED. {len(unscannable)} path(s) could not be "
              "scanned. A gate that skips a file it was asked to check has "
              "certified nothing.")
        return 1

    if scanned == 0:
        print("RESULT: BLOCKED. No files were scanned, so nothing was "
              "certified.")
        return 1

    print("RESULT: no HIGH findings. The team lead still walks each REVIEW "
          "line before sending.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
