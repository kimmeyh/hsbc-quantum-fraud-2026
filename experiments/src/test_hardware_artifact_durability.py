"""A billed hardware fit must survive the process that billed it.

F65. `run_hardware_b3.py` built its block artifact once, after the loop, so a
process that died after a billed call left NO artifact even though the money was
spent. Sprint 12's first B2 fit did exactly that: a WSL teardown on parent-shell
exit, no traceback. Nothing was lost that time only because the raw response,
the predictions and a full `results.json` row had all persisted first. That was
luck, not structure.

At roughly 5 seconds per B3 fit the loss is small. At the 91 metered seconds a
B2-class fit costs, one lost fit is real money against a finite allocation, and
the allocation is a grant that cannot be topped up.

WHAT THIS CHECKS. That the artifact is written after every fit rather than once
at the end, and on the FAILURE path as well as the success path -- a fit that
errored after being billed is exactly the one whose record matters most.

It asserts on source structure rather than executing the runner, because
executing it means submitting to Dirac-3 and spending real money. That is the
weaker kind of test and it is chosen deliberately; the alternative costs metered
seconds to run a guard. The dry-run path exercises the same function without
billing, which is what a human should use to confirm behaviour.

Verified by injection: removing either mid-loop `_write_artifact` call fails
this test naming the missing path; restoring it passes.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent
RUNNER = SRC / "run_hardware_b3.py"


def _fit_loop_writes() -> dict[str, int]:
    """Count _write_artifact calls, split by whether `complete` is True."""
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    counts = {"incremental": 0, "final": 0}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = getattr(fn, "id", None) or getattr(fn, "attr", None)
        if name != "_write_artifact":
            continue
        complete = None
        for kw in node.keywords:
            if kw.arg == "complete" and isinstance(kw.value, ast.Constant):
                complete = kw.value.value
        if complete is True:
            counts["final"] += 1
        else:
            counts["incremental"] += 1
    return counts


@pytest.mark.skipif(not RUNNER.exists(), reason="B3 runner absent")
def test_the_block_artifact_is_written_after_every_fit():
    """Not once at the end. A dead process must leave a partial artifact."""
    counts = _fit_loop_writes()
    assert counts["incremental"] >= 2, (
        "run_hardware_b3.py should write its block artifact after EVERY fit -- "
        "on the success path and on the failure path -- so a process that dies "
        f"after a billed call still leaves the record. Found "
        f"{counts['incremental']} incremental write(s). A fit that was billed "
        "and then lost is unrecoverable: the allocation is a grant.")
    assert counts["final"] >= 1, (
        "the artifact must still be written once at completion with "
        "complete=True, so a reader can distinguish a finished block from an "
        "interrupted one")


@pytest.mark.skipif(not RUNNER.exists(), reason="B3 runner absent")
def test_the_artifact_records_whether_the_block_completed():
    """A partial artifact that looks complete is worse than none.

    Without this flag a reader counts rows and guesses. With it, an interrupted
    block says so, and the count can be trusted.
    """
    body = RUNNER.read_text(encoding="utf-8")
    assert '"complete": bool(complete)' in body, (
        "the block artifact must carry a `complete` field, so a partial write "
        "from an interrupted run is distinguishable from a finished block")


@pytest.mark.skipif(not RUNNER.exists(), reason="B3 runner absent")
def test_a_dry_run_cannot_overwrite_the_evidence_file():
    """`--dry-run` must write somewhere else entirely.

    FOUND THE HARD WAY in Sprint 14, by running it. `--dry-run --ks 5` replaced
    the committed b3_hardware.json -- 12 real fits and 62 metered seconds of
    [HW] evidence -- with three dry-run placeholder rows, and reported success.
    `git checkout` restored it; nothing in the runner would have stopped the
    loss.

    The defect PREDATES the F65 per-fit write, which had the same exposure at
    the end of the loop. F65 made it far easier to hit, because the artifact is
    now written after every fit and a dry run no longer has to finish to destroy
    the file.

    Sprint 8 learned this exact lesson on a different runner -- "a smoke run must
    never overwrite the evidence file" -- and the rule never travelled here. That
    is what a test is for and a note is not.

    Verified by injection: replacing the `target` expression with a bare `OUT`
    fails this test; restoring the conditional passes.
    """
    body = RUNNER.read_text(encoding="utf-8")
    assert 'if args.dry_run else OUT' in body, (
        "run_hardware_b3.py must redirect its artifact write when --dry-run is "
        "set. A dry run that overwrites the evidence file destroys metered "
        "results that cost real money and cannot be re-run for free.")
    assert 'store.atomic_write_json(target, out)' in body, (
        "the artifact write must go to the redirected `target`, not to OUT "
        "directly, or the dry-run guard above is decorative")
