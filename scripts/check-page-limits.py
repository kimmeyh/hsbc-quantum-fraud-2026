"""Authoritative page-count check against the submission limits.

Word's ComputeStatistics reflows a PDF when it opens it, and reported 4 pages
for an appendix that is actually 6. Page limits are a hard rejection criterion
(requirements-matrix B1 and B4), so the count must be read from the PDF itself.

Usage: python scripts/check-page-limits.py
"""
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
LIMITS = {
    "docs/paper/out/proposal.pdf": (6, "concept proposal"),
    "docs/paper/out/appendix.pdf": (3, "appendix"),
    "docs/paper/out/team_profile.pdf": (1, "team profile"),
}

fail = 0
for rel, (limit, label) in LIMITS.items():
    f = ROOT / rel
    if not f.exists():
        print(f"MISSING  {rel}")
        fail += 1
        continue
    n = len(PdfReader(str(f)).pages)
    ok = n <= limit
    print(f"{'OK  ' if ok else 'OVER'}  {label}: {n} of {limit} page(s)")
    fail += (not ok)

print("")
print("RESULT:", "within limits" if not fail else f"{fail} document(s) OVER LIMIT")
sys.exit(1 if fail else 0)
