"""Guards written to catch a regression must say how they were proven to fail.

Sprint 12 improvement 2. Three guards were written that sprint and injection-
tested; ONE passed vacuously on first write. `test_the_withdrawn_claim_does_not_return`
searched for a marker phrase that the markdown wraps across a line break, so the
literal substring never matched and the assertion could not fail. It would have
shipped as a green line asserting nothing, about a claim the submission had just
withdrawn.

A guard nobody has seen fail is a guard nobody has tested.

WHAT THIS CHECKS, AND WHAT IT CANNOT. It cannot verify that an injection test was
actually run -- that happens in a terminal and leaves no artifact. What it CAN do
is require the claim to be written down: a guard whose docstring does not say how
it was proven to fail has probably not been proven to fail, because writing the
sentence is the cheapest part of doing the work.

So this is a discipline check, not a correctness check, and it is scoped
deliberately narrowly: only tests whose NAME says they exist to catch a
regression. A blanket rule across 300+ tests would be noise, and a noisy rule
gets deleted -- which is the failure mode the F44 registry docstring records.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent

# A test whose name matches one of these exists to catch something coming back.
# Naming it this way is a claim about its purpose, and this file holds it to it.
REGRESSION_NAMES = re.compile(
    r"does_not_return|does_not_regress|cannot_return|_regression|"
    r"would_fail_this_bar|detects_a_deliberately|not_computed_over|"
    r"groups_on_the_pool_not_the_device|were_built_on_the_same_rows"
)

# Phrases that count as stating how the guard was proven to fail.
EVIDENCE = re.compile(
    r"verified by injection|injection|proven to fail|"
    r"fails on the|reverting the|breaking the", re.I)


def _test_functions():
    for f in sorted(SRC.glob("test_*.py")):
        if f.name == Path(__file__).name:
            continue
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except SyntaxError:                              # noqa: PERF203
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                yield f.name, node


def test_regression_guards_record_how_they_were_proven_to_fail():
    """A guard named for catching a regression must say it was seen to fail."""
    undocumented: list[str] = []
    for fname, node in _test_functions():
        if not REGRESSION_NAMES.search(node.name):
            continue
        doc = ast.get_docstring(node) or ""
        if not EVIDENCE.search(doc):
            undocumented.append(f"{fname}::{node.name}")
    assert not undocumented, (
        "these tests are named as regression guards but their docstrings do not "
        f"say how they were proven to fail: {undocumented}. Break the thing the "
        "guard guards, confirm it goes red, restore, confirm green -- then say "
        "so in the docstring. One guard in Sprint 12 passed VACUOUSLY on first "
        "write and would have shipped as false assurance.")


def test_the_injection_standard_is_documented():
    """The rule itself must survive in the strategy doc, not only in this file.

    A test that enforces an undocumented rule teaches nobody why the rule
    exists, and the next person to hit it will delete the test rather than
    follow the practice.
    """
    doc = (SRC.parents[1] / "docs" / "TESTING_STRATEGY.md")
    if not doc.exists():
        pytest.skip("testing strategy doc absent")
    body = doc.read_text(encoding="utf-8").lower()
    assert "injection" in body, (
        "TESTING_STRATEGY.md no longer documents the injection-verification "
        "standard that this test enforces")
