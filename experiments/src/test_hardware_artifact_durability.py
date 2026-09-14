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
    """Count _write_artifact calls, split by whether `complete` is True.

    Incremental calls are counted ONLY inside a for loop. The first version
    walked the whole module, so two `complete=False` calls sitting in dead code
    or an unrelated helper would have satisfied the assertion while the fit loop
    wrote nothing. The function name promised loop scope and the implementation
    did not deliver it.
    """
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    counts = {"incremental": 0, "final": 0}

    # Line spans of every for loop, so a call can be tested for containment.
    loop_spans = [(n.lineno, n.end_lineno) for n in ast.walk(tree)
                  if isinstance(n, ast.For) and n.end_lineno]

    def in_a_loop(node: ast.AST) -> bool:
        return any(lo <= node.lineno <= hi for lo, hi in loop_spans)

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
        elif in_a_loop(node):
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


def _artifact_write_target() -> ast.expr | None:
    """The first argument of the store.atomic_write_json call, as an AST node."""
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and getattr(node.func, "attr", None) == "atomic_write_json"):
            return node.args[0] if node.args else None
    return None


@pytest.mark.skipif(not RUNNER.exists(), reason="B3 runner absent")
def test_a_dry_run_cannot_overwrite_the_evidence_file():
    """`--dry-run` must write somewhere else. Asserted against STRUCTURE.

    FOUND THE HARD WAY in Sprint 14, by running it. `--dry-run --ks 5` replaced
    the committed b3_hardware.json -- 12 real fits and 62 metered seconds of
    [HW] evidence -- with three dry-run placeholder rows, and reported success.

    THIS GUARD HAS BEEN VACUOUS TWICE, and both times a review caught it rather
    than the injection I claimed to have run.

    Version 1 asserted the substrings `if args.dry_run else OUT` and
    `store.atomic_write_json(target, out)` appear in the source. That phrase
    occurs TWICE in the runner: once in the real redirect at the write site, and
    once in a cosmetic `written = ...` line that only feeds a console message.
    The second occurrence satisfies the assertion by itself, so the redirect
    could be deleted entirely and the test stayed green.

    Version 2 called `store.atomic_write_json` directly with a hand-built
    target. That tested the JSON writer, not the runner's decision about WHERE
    to write, so a rewrite to `target = OUT if args.dry_run else OUT` still
    passed. It exercised code while asserting nothing about the thing at risk.

    WHAT IT ASSERTS NOW. The single-argument structure of the actual write call:
    it must pass a NAME, and that name must be bound to a conditional whose test
    mentions `dry_run`. A bare `OUT`, or a name bound to something that is not a
    conditional, fails. Cosmetic copies of the phrase elsewhere are irrelevant
    because nothing outside the write call is examined.

    Verified by injection, the specific one both earlier versions survived:
    rewriting the binding to `target = OUT if args.dry_run else OUT` -- which
    keeps every substring and restores the defect -- now FAILS here.
    """
    target = _artifact_write_target()
    assert target is not None, (
        "no store.atomic_write_json call found in run_hardware_b3.py; the "
        "artifact is no longer written where this guard can check it")
    assert isinstance(target, ast.Name), (
        "the artifact write passes a literal rather than a redirected variable, "
        "so a dry run writes wherever that literal points. It must pass a name "
        "bound to a dry-run conditional.")

    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    bindings = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Assign)
        and any(isinstance(x, ast.Name) and x.id == target.id for x in n.targets)
    ]
    assert bindings, f"`{target.id}` is passed to the write call but never assigned"

    conditional = [b for b in bindings
                   if isinstance(b.value, ast.IfExp)
                   and "dry_run" in ast.dump(b.value.test)]
    assert conditional, (
        f"`{target.id}` is not bound to a conditional on args.dry_run. A dry "
        "run that overwrites the evidence file destroys metered results that "
        "cost real money and cannot be re-run for free: this defect already "
        "cost 12 fits and 62 metered seconds once.")

    # The two branches must differ. `OUT if args.dry_run else OUT` is the exact
    # injection both earlier versions of this guard survived.
    for b in conditional:
        body, orelse = ast.dump(b.value.body), ast.dump(b.value.orelse)
        assert body != orelse, (
            f"`{target.id}` is bound to a conditional whose branches are "
            "IDENTICAL, so the dry-run test changes nothing. This is the "
            "injection that defeated two earlier versions of this guard.")


@pytest.mark.skipif(not RUNNER.exists(), reason="B3 runner absent")
def test_the_dry_run_artifact_has_its_own_name():
    """The companion check, and it is deliberately the weak one.

    It fails for a DIFFERENT reason than the structural test above: if someone
    removes the separate dry-run filename, this names what went missing while
    the structural test says the redirect broke. Kept only because the test
    above exists; on its own it would be the vacuous guard this file documents.
    """
    body = RUNNER.read_text(encoding="utf-8")
    assert "b3_hardware.dryrun.json" in body, (
        "run_hardware_b3.py no longer names a separate dry-run artifact path.")
