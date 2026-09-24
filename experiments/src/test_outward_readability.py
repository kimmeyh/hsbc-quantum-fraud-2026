"""The outward-readability check must actually catch internal shorthand.

IMP-5, Sprint 18 retrospective. The QCi package needed a revision round purely
to strip tokens a vendor reader cannot resolve -- "B2" in a table whose job is
to say where a number came from, citing a source outside the reader's reach.
That round happened AFTER the team lead reviewed the documents. This check
makes it mechanical and runnable before handover.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "outward_readability.py"
QCI = [ROOT / "docs" / "QCI_EQC_MODELS_FEEDBACK.md",
       ROOT / "docs" / "HARDWARE_PLAN_PHASE_2.md",
       ROOT / "docs" / "qci_package" / "Phase 1 - QCi memo.txt"]

sys.path.insert(0, str(ROOT / "scripts"))


def _run(*args: str):
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          cwd=str(ROOT), capture_output=True, text=True)


def test_the_qci_package_is_clean():
    """The live check. These three documents are what QCi receives."""
    present = [p for p in QCI if p.exists()]
    if not present:
        pytest.skip("QCi package not present")
    r = _run(*[str(p) for p in present])
    assert r.returncode == 0, (
        f"internal shorthand in the QCi package:\n{r.stdout}")


def test_it_catches_a_block_name(tmp_path):
    """GUARD THE GUARD. A clean result above means nothing if the scanner is
    blind -- every assertion in this file would pass on a scanner that found
    nothing."""
    p = tmp_path / "d.md"
    p.write_text("Costs are 82 s per fit, from B2.\n", encoding="utf-8")
    r = _run(str(p))
    assert r.returncode == 1
    assert "B2" in r.stdout


def test_it_catches_a_card_id_and_a_sprint_number(tmp_path):
    p = tmp_path / "d.md"
    p.write_text("F87 delivered this in Sprint 18.\n", encoding="utf-8")
    r = _run(str(p))
    assert r.returncode == 1
    assert "F87" in r.stdout and "Sprint 18" in r.stdout


def test_code_spans_are_exempt(tmp_path):
    """A token inside code is quoted verbatim from the library or the device,
    so it is evidence rather than jargon. The QCi feedback cites
    `run_hardware_f32.py:59-64` and a repr() sample, both correctly."""
    p = tmp_path / "d.md"
    p.write_text("See `B2` and:\n\n```\nblock = B2\n```\n", encoding="utf-8")
    r = _run(str(p))
    assert r.returncode == 0, r.stdout


def test_amendment_references_are_allowed(tmp_path):
    """A12 and A31 read as citation labels, and the preregistration is public,
    so a reader can follow them. Flagging these would train the operator to
    ignore the output."""
    p = tmp_path / "d.md"
    p.write_text("We withdrew it as a dated amendment (A31).\n", encoding="utf-8")
    assert _run(str(p)).returncode == 0


def test_allow_exempts_a_token(tmp_path):
    p = tmp_path / "d.md"
    p.write_text("Costs from B2.\n", encoding="utf-8")
    assert _run(str(p)).returncode == 1
    assert _run(str(p), "--allow", "B2").returncode == 0


def test_a_hit_is_framed_as_a_question_not_a_verdict(tmp_path):
    """Some hits are fine in context. A check that reads as a failure gets
    argued with; one that reads as a question gets answered."""
    p = tmp_path / "d.md"
    p.write_text("From B2.\n", encoding="utf-8")
    out = _run(str(p)).stdout
    assert "QUESTION, not a verdict" in out
    assert "--allow" in out


def test_checking_nothing_is_not_a_pass():
    """A typo in a path used to print "No unresolvable internal references
    found" and exit 0 -- a clean bill of health from a check that never
    opened a file. This script gates a handover to an external vendor.

    Found by the PR #139 review.
    """
    import outward_readability as orx
    rc = orx.main(["docs/THIS_FILE_DOES_NOT_EXIST.md"])
    assert rc != 0, "a run that scanned nothing reported success"


def test_one_missing_path_among_real_ones_is_still_flagged():
    """Partial coverage is the subtler case: the documents that WERE scanned
    are clean, so the exit code would otherwise say everything is fine."""
    import outward_readability as orx
    rc = orx.main(["docs/HARDWARE_PLAN_PHASE_2.md",
                   "docs/THIS_FILE_DOES_NOT_EXIST.md"])
    assert rc != 0, "a partially-skipped run reported success"


def test_a_clean_run_over_real_documents_still_passes():
    """The companion. Without it, returning non-zero unconditionally would
    satisfy both tests above and the check would be useless."""
    import outward_readability as orx
    assert orx.main(["docs/HARDWARE_PLAN_PHASE_2.md",
                     "docs/QCI_EQC_MODELS_FEEDBACK.md"]) == 0
