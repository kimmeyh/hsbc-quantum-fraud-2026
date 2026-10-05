"""B5's runner is safe to approve BEFORE its first call, not after.

Sprint 18 IMP-3: "the runner must be IDEMPOTENT before its first approval, not
after its first over-spend." Sprint 18 spent three calls against a two-call
approval because a second invocation with a higher --max-calls restarted from
the top. The allocation has no undo, so every one of these properties is
checked without submitting anything.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pytest

SRC = Path(__file__).resolve().parent
ROOT = SRC.parents[1]
sys.path.insert(0, str(SRC))

import run_hardware_b5 as b5  # noqa: E402


# ---- the sign augmentation, which is the arm's whole reason to exist --------

def test_sign_augmentation_doubles_the_width_and_negates_the_copy():
    X = np.array([[1.0, -2.0], [3.0, 4.0]])
    A = b5.sign_augment(X)
    assert A.shape == (2, 4)
    assert np.allclose(A[:, :2], X)
    assert np.allclose(A[:, 2:], -X)


def test_a_signed_weight_is_representable_after_augmentation():
    """The point of `[X, -X]`: a NON-NEGATIVE w over the augmented space can
    express a signed w over the original one.

    Without this, Dirac-3's non-negative continuous variables cannot represent
    an anti-correlated feature at all -- which is what scored 0.18 AUC in the
    evidence inventory.
    """
    rng = np.random.default_rng(0)
    X = rng.normal(size=(50, 3))
    w_signed = np.array([1.5, -2.0, 0.5])

    # The augmented, non-negative encoding of that same hypothesis.
    w_aug = np.concatenate([np.maximum(w_signed, 0), np.maximum(-w_signed, 0)])
    assert (w_aug >= 0).all(), "the encoding must be non-negative to be legal"

    assert np.allclose(b5.sign_augment(X) @ w_aug, X @ w_signed), (
        "the augmented non-negative model must reproduce the signed model")


def test_variable_count_is_twice_the_feature_count():
    assert b5.n_variables(13) == 26
    assert b5.n_variables(b5.K_FEATURES) == 26, (
        "26 variables is what the Criterion H statement quotes")


# ---- the 12 fits the frozen grid specifies ---------------------------------

def test_there_are_exactly_twelve_cells():
    """PREREGISTRATION section 10: "B5: QSVM arms | 12 fits | ~15 [s]"."""
    assert len(list(b5.specs())) == 12


def test_ten_stratified_seeds_one_temporal_one_repeat():
    s = list(b5.specs())
    strat = [c for c in s if c["protocol"] == "stratified"]
    temporal = [c for c in s if c["protocol"] == "temporal"]
    repeat = [c for c in s if c["protocol"] == "stratified_repeat"]
    assert len(strat) == 10 and len(temporal) == 1 and len(repeat) == 1
    assert sorted(c["seed"] for c in strat) == list(range(42, 52))


def test_the_temporal_cell_records_no_seed():
    """A8, Sprint 4 review: `temporal_split` ignores the seed, so recording 42
    would misrepresent provenance AND let a second temporal row slip past the
    done-set."""
    temporal = [c for c in b5.specs() if c["protocol"] == "temporal"]
    assert temporal[0]["seed"] is None


# ---- Criterion H and the spend guards --------------------------------------

def test_the_expected_seconds_come_from_the_frozen_grid():
    """F90's card said "15-62 s" by extrapolating B3's 5.2 s/fit -- a CVQBoost
    rate at a different variable count, and the wrong anchor for a QSVM. The
    frozen grid's own figure is ~15 s for 12 fits."""
    assert "15" in b5.EXPECTED_SECONDS
    assert "frozen grid" in b5.EXPECTED_SECONDS.lower()
    assert b5.EXPECTED_CEILING_S <= b5.BLOCK_CAP_S, (
        "the conservative ceiling must sit inside the block cap")


def test_the_block_cap_and_allocation_floor_are_set():
    assert b5.BLOCK_CAP_S > 0
    assert b5.ALLOCATION_FLOOR_S == 776.0, (
        "the team lead's floor; changing it is his decision, not the runner's")


def test_the_window_closes_before_six_and_opens_after():
    """The team lead directed all Dirac-3 calls to wait until 18:00 local on
    2026-10-05."""
    assert b5.WINDOW_HOUR == 18
    assert not b5._window_open(datetime(2026, 10, 5, 15, 12))
    assert not b5._window_open(datetime(2026, 10, 5, 17, 59))
    assert b5._window_open(datetime(2026, 10, 5, 18, 0))
    assert b5._window_open(datetime(2026, 10, 5, 23, 30))


def test_running_before_the_window_refuses_with_a_nonzero_exit():
    """And it must EXIT NONZERO. A guard that refuses while reporting success
    is this repository's most-repeated defect: "could not check" reading as
    "clean"."""
    r = subprocess.run(
        [sys.executable, str(SRC / "run_hardware_b5.py"), "--max-calls", "1"],
        capture_output=True, text=True, cwd=str(ROOT), timeout=900)
    if "REFUSING" not in r.stdout:
        pytest.skip(f"the window is open now ({datetime.now():%H:%M}); this "
                    "guard only exercises the closed-window path")
    assert r.returncode != 0, (
        "refusing to run must not exit 0; a caller reading the exit code would "
        f"see success. stdout tail: {r.stdout[-200:]}")
    assert r.returncode == 3


def test_the_dry_run_spends_nothing_and_says_so():
    r = subprocess.run(
        [sys.executable, str(SRC / "run_hardware_b5.py"), "--dry-run"],
        capture_output=True, text=True, cwd=str(ROOT), timeout=1800)
    assert r.returncode == 0, r.stderr[-400:]
    assert "nothing submitted, nothing spent" in r.stdout
    assert "CALL COUNT now   : 12" in r.stdout
    assert "EXPECTED SECONDS" in r.stdout, (
        "Criterion H requires the expected seconds stated before any run")


def test_the_criterion_h_statement_names_every_required_field():
    """Block, call count, expected seconds AND provenance -- the four things
    Sprint 11 improvement 2 requires, after a probe approved at "0-5 seconds"
    cost 10 against a figure that was never established."""
    r = subprocess.run(
        [sys.executable, str(SRC / "run_hardware_b5.py"), "--dry-run"],
        capture_output=True, text=True, cwd=str(ROOT), timeout=1800)
    out = r.stdout
    for field in ("BLOCK B5", "CALL COUNT", "EXPECTED SECONDS", "provenance",
                  "variables/fit", "approved"):
        assert field in out, f"the Criterion H statement omits {field!r}"


# ---- idempotency -----------------------------------------------------------

def test_a_failed_row_does_not_count_as_done(tmp_path, monkeypatch):
    """Section 11 requires a failed cell to be retried up to twice and then
    reported failed -- never silently skipped forever, which is what happened
    before the status filter existed."""
    results = tmp_path / "results.json"
    results.write_text(json.dumps({"rows": [
        {"arm": b5.ARM, "block": "B5", "seed": 42, "protocol": "stratified",
         "status": "ok"},
        {"arm": b5.ARM, "block": "B5", "seed": 43, "protocol": "stratified",
         "status": "failed"},
    ]}), encoding="utf-8")
    monkeypatch.setattr(b5, "RESULTS", results)

    done = b5._done()
    assert (b5.ARM, 42, "stratified") in done, "the successful cell is done"
    assert (b5.ARM, 43, "stratified") not in done, (
        "a FAILED cell must remain to be retried")


def test_rows_from_other_blocks_are_not_counted_as_b5(tmp_path, monkeypatch):
    results = tmp_path / "results.json"
    results.write_text(json.dumps({"rows": [
        {"arm": "cvqboost_hw", "block": "B2", "seed": 42,
         "protocol": "stratified", "status": "ok", "metered_seconds": 91},
    ]}), encoding="utf-8")
    monkeypatch.setattr(b5, "RESULTS", results)
    assert b5._done() == set()
    assert b5._spent() == 0.0, "B2's 91 seconds are not B5's spend"


def test_an_unreadable_ledger_refuses_rather_than_assuming_nothing_is_done(
        tmp_path, monkeypatch):
    """"Refuses to submit at all if it cannot read its own ledger" (IMP-3).

    Returning an empty done-set on a parse error is the dangerous failure: the
    runner would re-pay for every completed cell.
    """
    bad = tmp_path / "results.json"
    bad.write_text("{not json", encoding="utf-8")
    monkeypatch.setattr(b5, "RESULTS", bad)
    with pytest.raises(SystemExit, match="cannot read its own ledger"):
        b5._done()
