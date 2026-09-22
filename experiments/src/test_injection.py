"""The injection helper must catch the injections that fooled Sprint 17.

F89 acceptance. Six injections returned GREEN in Sprint 17, every one a defect
in the verification rather than in the thing verified. This file replays the
two that a helper CAN catch mechanically, and pins the guarantees that make
the other four harder to repeat.

The distinction matters and is not a dodge:

  MECHANICAL (cases 3 and 6) -- a partial replace, and an injection whose
  mutation never reached what the assertion reads. `Mutation.apply()` makes
  both impossible.

  TEST DESIGN (cases 1, 2, 4, 5) -- dead code, a test passing for a second
  wrong reason, an assertion on a fallback value, a mutation aimed at a
  function the test does not call. No helper can detect those from the
  outside; `assert_can_fail` addresses them by refusing to accept a green
  result as evidence.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "src"))
from injection import (InjectionError, Mutation, assert_can_fail,  # noqa: E402
                       injected, run_pytest)


@pytest.fixture()
def sample(tmp_path: Path) -> Path:
    p = tmp_path / "sample.txt"
    p.write_text("alpha 0.7671 beta\nmid 0.7671 line\ntail 0.7671 end\n",
                 encoding="utf-8")
    return p


# ------------------------------------------------- case 3: partial replace

def test_every_occurrence_is_replaced_not_just_the_first(sample):
    """SPRINT 17 CASE 3. The gate report's 0.7671 appears three times.
    `replace(..., 1)` left two behind and the assertion still found it, so the
    injection reported a passing guard while proving nothing."""
    m = Mutation(sample, "0.7671", "REDACTED")
    with injected(m):
        text = sample.read_text(encoding="utf-8")
        assert "0.7671" not in text, "an occurrence survived the injection"
        assert text.count("REDACTED") == 3


def test_a_surviving_occurrence_is_an_error_not_a_pass(sample, monkeypatch):
    """If a replace could leave the target reachable, that must raise rather
    than hand back a result the caller will read as success."""
    real = Path.write_text

    def partial(self, data, *a, **kw):           # emulate replace(..., 1)
        if self == sample:
            data = sample.read_text(encoding="utf-8").replace("0.7671", "X", 1)
        return real(self, data, *a, **kw)

    monkeypatch.setattr(Path, "write_text", partial)
    with pytest.raises(InjectionError, match="SURVIVE"):
        Mutation(sample, "0.7671", "X").apply()


def test_a_missing_target_aborts(sample):
    """SPRINT 17, TWICE: an injection whose target had moved printed
    '77 passed' while injecting nothing."""
    with pytest.raises(InjectionError, match="target not found"):
        Mutation(sample, "not-present-anywhere", "X").apply()


def test_an_unexpected_occurrence_count_aborts(sample):
    """Guards against aiming at the wrong thing: if the caller expects one
    occurrence and the file has three, the injection is not what they think."""
    with pytest.raises(InjectionError, match="expected 1 occurrence"):
        Mutation(sample, "0.7671", "X", expect_occurrences=1).apply()


def test_a_no_op_mutation_aborts(sample):
    with pytest.raises(InjectionError, match="changed nothing"):
        Mutation(sample, "0.7671", "0.7671").apply()


# --------------------------------------------------------- restoration

def test_the_file_is_restored_after_the_block(sample):
    before = sample.read_text(encoding="utf-8")
    with injected(Mutation(sample, "0.7671", "X")):
        assert sample.read_text(encoding="utf-8") != before
    assert sample.read_text(encoding="utf-8") == before


def test_the_file_is_restored_even_when_the_body_raises(sample):
    """A test that dies mid-injection must not leave the repository broken.
    Sprint 17's amendment-token test had exactly this exposure."""
    before = sample.read_text(encoding="utf-8")
    with pytest.raises(ValueError):
        with injected(Mutation(sample, "0.7671", "X")):
            raise ValueError("boom")
    assert sample.read_text(encoding="utf-8") == before


def test_multiple_mutations_all_restore(tmp_path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("aaa\n", encoding="utf-8")
    b.write_text("bbb\n", encoding="utf-8")
    with injected(Mutation(a, "aaa", "xxx"), Mutation(b, "bbb", "yyy")):
        assert a.read_text(encoding="utf-8") == "xxx\n"
        assert b.read_text(encoding="utf-8") == "yyy\n"
    assert a.read_text(encoding="utf-8") == "aaa\n"
    assert b.read_text(encoding="utf-8") == "bbb\n"


# ------------------------------------------- case 6: the three-leg check

def test_a_vacuous_guard_is_reported_as_such(sample):
    """SPRINT 17 CASES 1, 2, 4 AND 5 in one shape: the suite stays green with
    the thing it guards broken."""
    with pytest.raises(AssertionError, match="VACUOUS GUARD"):
        assert_can_fail([Mutation(sample, "0.7671", "X")],
                        run=lambda: True, label="always green")


def test_an_already_failing_guard_aborts(sample):
    """SPRINT 17 CASE 6: the hook exited at an early gate, so every case read
    as ALLOW. A guard that is already red proves nothing by going red."""
    with pytest.raises(InjectionError, match="ALREADY FAILING"):
        assert_can_fail([Mutation(sample, "0.7671", "X")],
                        run=lambda: False, label="already red")


def test_a_real_guard_passes_all_three_legs(sample):
    """Green -> red under mutation -> green again."""
    def run() -> bool:
        return "0.7671" in sample.read_text(encoding="utf-8")

    assert_can_fail([Mutation(sample, "0.7671", "X")], run=run, label="real")
    assert run(), "the guard did not return to green"


def test_a_guard_that_stays_red_after_restoration_aborts(tmp_path):
    """Catches a helper that restores the bytes but leaves other state
    broken -- reported rather than silently passing."""
    p = tmp_path / "s.txt"
    p.write_text("value\n", encoding="utf-8")
    calls = {"n": 0}

    def run() -> bool:
        calls["n"] += 1
        return calls["n"] == 1          # green once, then red forever

    with pytest.raises(InjectionError, match="did not return to GREEN"):
        assert_can_fail([Mutation(p, "value", "X")], run=run)


# ------------------------------------------------------------- run_pytest

def test_run_pytest_reports_pass_and_fail(tmp_path):
    ok = tmp_path / "test_ok.py"
    bad = tmp_path / "test_bad.py"
    ok.write_text("def test_a():\n    assert True\n", encoding="utf-8")
    bad.write_text("def test_b():\n    assert False\n", encoding="utf-8")
    assert run_pytest(str(ok), root=tmp_path) is True
    assert run_pytest(str(bad), root=tmp_path) is False


# ---------------------------------------- the helper against a REAL guard

def test_the_helper_proves_a_real_repository_guard_can_fail():
    """End-to-end on live files, not a tmp_path fixture.

    `test_the_blas_field_is_a_blas_not_a_numpy_version` exists because Sprint
    17 shipped a field named `blas` that held a numpy version, and the test
    guarding it asserted only presence and truthiness -- it passed on the
    degraded value. This proves the REPLACEMENT guard is not vacuous, using
    the helper rather than a hand-rolled harness.
    """
    store = ROOT / "experiments" / "src" / "store.py"
    target = "experiments/src/test_row_environment.py"
    node = f"{target}::test_the_blas_field_is_a_blas_not_a_numpy_version"

    if not store.exists():
        pytest.skip("store.py not present")

    assert_can_fail(
        [Mutation(store,
                  'env["blas"] = blas or "unavailable (numpy exposes no BLAS identity)"',
                  'env["blas"] = "numpy-" + str(env["numpy"])',
                  expect_occurrences=1)],
        run=lambda: run_pytest(node, root=ROOT),
        label="blas field reports a real BLAS")
