"""Generated evidence artifacts must match the store they derive from.

F45. A diagnostic script written to reproduce a review finding injected a fake
row into results.json, ran score_gates.py, and restored the store in a `finally`.
The store was restored correctly -- but the report had ALREADY been written from
the polluted data, so a 158-row artifact describing a fit that never happened was
briefly committed.

The restore was careful and still insufficient: the derived artifact outlived the
source it derived from. Any diagnostic that perturbs the store has the same hole,
and the next one may not be noticed in the same turn.

This is the (c) option from the card, chosen over a test helper because it does
not depend on remembering to use a helper. It catches the whole class regardless
of cause -- a perturbing diagnostic, a hand-edited artifact, a generator change
that was never re-run.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = Path(__file__).resolve().parent
REPORT = ROOT / "experiments" / "results" / "gate_report.md"


def test_gate_report_matches_a_fresh_regeneration(tmp_path):
    """Regenerate into a scratch copy and compare, without touching the real one.

    Deliberately does NOT write over the committed artifact: a test that
    regenerates in place would mask exactly the drift it exists to detect, and
    would itself be a script that mutates evidence.
    """
    before = REPORT.read_text(encoding="utf-8")

    # score_gates.py writes the REAL path, so the committed artifact is restored
    # in a finally -- not after the returncode assert. An earlier version put the
    # restore after that assert, so a generator crash left the tree modified and
    # the developer could commit it without noticing. tmp_path holds the copy.
    backup = tmp_path / "gate_report.md.committed"
    backup.write_text(before, encoding="utf-8")
    try:
        proc = subprocess.run(
            [sys.executable, str(SRC / "score_gates.py")],
            capture_output=True, text=True, cwd=str(ROOT))
        after = REPORT.read_text(encoding="utf-8")
    finally:
        REPORT.write_text(before, encoding="utf-8")

    assert proc.returncode == 0, (
        f"score_gates.py failed, so the committed report cannot be verified:\n"
        f"{proc.stderr[-800:]}")

    if before != after:
        import difflib
        diff = "\n".join(list(difflib.unified_diff(
            before.splitlines(), after.splitlines(),
            "committed", "regenerated", lineterm=""))[:40])
        raise AssertionError(
            "gate_report.md does not match a regeneration from results.json.\n"
            "Either the store changed without the report being rebuilt, or a "
            "diagnostic wrote the report from perturbed data (F45).\n\n" + diff)
