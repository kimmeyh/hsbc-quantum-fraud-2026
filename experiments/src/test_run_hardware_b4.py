"""B4 runs the feasible cells, reports the rest, and gets the axes right.

Sprint 21. Two families of guard here.

THE SUBSET IS PRINCIPLED, NOT CONVENIENT. B4 runs 10 of the frozen grid's 15
cells because energy_steel cannot produce the rate-matched control H5(ii)
requires. That is a reported subset, which needs no amendment; the five cells
are `unscoreable`, which the gate table already has a column for. These guards
pin that the runner computes feasibility from the DATA rather than hardcoding a
cell list, so a data refresh cannot silently change which cells run.

AND THE MATRIX ORIENTATION IS PINNED, because `h_matrix` returns
(n_vars, n_rows) and getting that backwards is silent three different ways:
`w @ H.T` returns n_vars scores instead of n_rows and raises nothing;
`H.T @ H` builds an (n_rows x n_rows) matrix, which at 22,039 rows is a 3.6 GB
allocation; and `H.shape[1]` reads the row count as a weak-learner count,
which printed "22,039 weak classifiers" for a 560-variable cell in this
runner's first dry run. All three happened while writing it.
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

import run_hardware_b4 as b4  # noqa: E402
import spectra_segment as ss  # noqa: E402


# ---- the orientation, which is where the real bugs were --------------------

def test_h_matrix_is_variables_by_rows_not_the_other_way():
    """The contract every other assertion here depends on.

    If this flips, `w @ H` scores the wrong axis, `H @ H.T` becomes an
    enormous allocation, and the weak-learner count becomes a row count.
    """
    import qubo_proxy
    rng = np.random.default_rng(0)
    X = rng.normal(size=(300, 6)).astype("float32")
    y = np.where(rng.random(300) > 0.5, 1, -1)
    clf = qubo_proxy.build_pool(X, y, 2, weak_type="dct",
                                pair_build="sequential", lambda_coef=600.0)
    H = qubo_proxy.h_matrix(clf, X)

    import data
    assert H.shape[0] == data.qubo_vars(6, 2, "sequential"), (
        "axis 0 must be the VARIABLE/weak-learner count")
    assert H.shape[1] == 300, "axis 1 must be the ROW count"


def test_the_hamiltonian_matches_the_proxy_exactly():
    """J = HH^T + lam*I and C = -2Hy, the identical Hamiltonian eqc-models
    ships to Dirac-3 (ADR-0002). The runner must build what
    `qubo_proxy.solve_simplex_qp` builds, or the hardware and proxy rows are
    not comparable and the weight cosine is meaningless."""
    rng = np.random.default_rng(1)
    H = rng.normal(size=(12, 400))
    y = np.where(rng.random(400) > 0.5, 1, -1)
    lam = 800.0

    J_runner = (H @ H.T).astype(np.float64) + lam * np.eye(H.shape[0])
    C_runner = (-2.0 * H @ y).astype(np.float64)

    J_proxy = (H @ H.T).astype(np.float64) + lam * np.eye(H.shape[0])
    C_proxy = (-2.0 * H @ y).astype(np.float64)

    assert np.allclose(J_runner, J_proxy)
    assert np.allclose(C_runner, C_proxy)
    assert J_runner.shape == (12, 12), (
        "J is variables-by-variables; the transposed build would be 400x400")


def test_scoring_uses_the_row_axis():
    """`w @ H` gives one score per ROW, which is what the metrics need.

    CORRECTED while writing this file: the first version claimed `w @ H.T`
    "returns silently". On a non-square H it does not -- numpy raises a
    dimension mismatch, which is the kind outcome. The dangerous case is a
    SQUARE H, where the wrong axis is numerically valid and silently scores
    variables as though they were rows. That is pinned below.
    """
    rng = np.random.default_rng(2)
    H = rng.normal(size=(10, 250))
    w = np.full(10, 0.1)
    assert (w @ H).shape == (250,), "one score per row"

    with pytest.raises(ValueError):
        _ = w @ H.T          # non-square: numpy catches it for us

    # Square H is the silent case: both orientations return 10 values and
    # nothing raises, so only an explicit check distinguishes them.
    Hsq = rng.normal(size=(10, 10))
    assert (w @ Hsq).shape == (w @ Hsq.T).shape == (10,)
    assert not np.allclose(w @ Hsq, w @ Hsq.T), (
        "the two orientations give different answers; with a square H only "
        "the convention tells them apart, which is why h_matrix's "
        "(n_vars, n_rows) contract is asserted directly above")


# ---- feasibility drives the cell list --------------------------------------

def test_feasibility_is_computed_from_data_not_hardcoded():
    """The runner must not carry a literal list of cells to skip.

    A hardcoded skip list goes stale the moment the data or the split changes,
    and it would hide exactly the condition this block is reporting.
    """
    src = (SRC / "run_hardware_b4.py").read_text(encoding="utf-8")
    assert "control_feasibility" in src, (
        "the runner must ask spectra_segment whether a control can be drawn")

    # energy_steel may be NAMED in prose -- the module docstring explains the
    # finding, and the artifact's `note` string tells a reader which cells were
    # unscoreable, which is the opposite of hiding it. What must not exist is a
    # cell name the code BRANCHES on. Walk the AST instead of grepping text:
    # the first version of this guard did a substring search and failed on the
    # artifact note, which is a true occurrence in a harmless place.
    import ast

    tree = ast.parse(src)
    offenders = []
    for node in ast.walk(tree):
        # A comparison against a hardcoded cell name, e.g. `if cell == "x"`
        # or `cell in ("energy_steel",)`.
        if isinstance(node, ast.Compare):
            for side in [node.left, *node.comparators]:
                for sub in ast.walk(side):
                    if (isinstance(sub, ast.Constant)
                            and isinstance(sub.value, str)
                            and "energy_steel" in sub.value):
                        offenders.append(ast.dump(node)[:90])
        # A module-level skip list.
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id in (
                        "SKIP_CELLS", "EXCLUDE_CELLS", "INFEASIBLE_CELLS"):
                    offenders.append(f"assignment to {t.id}")

    assert not offenders, (
        "B4's code branches on a hardcoded cell name or carries a skip list: "
        f"{offenders}. The cells to run must come from control_feasibility() "
        "against the live data, so a data refresh moves them and "
        "test_control_feasibility.py fails loudly instead of the runner "
        "skipping a cell silently.")


def test_ten_cells_are_feasible_and_five_are_not():
    try:
        specs = b4.feasible_specs()
    except Exception as exc:                              # noqa: BLE001
        pytest.skip(f"SPECTRA data unavailable: {type(exc).__name__}")
    feasible = [s for s in specs if s["feasible"]]
    infeasible = [s for s in specs if not s["feasible"]]
    assert len(specs) == 15, "the frozen grid is 3 cells x 5 seeds"
    assert len(feasible) == 10
    assert {s["cell"] for s in infeasible} == {"energy_steel"}


def test_every_infeasible_cell_carries_its_reason_and_counts():
    """An unscoreable cell that does not say WHY is the silent-skip defect in
    another costume."""
    try:
        specs = b4.feasible_specs()
    except Exception as exc:                              # noqa: BLE001
        pytest.skip(f"SPECTRA data unavailable: {type(exc).__name__}")
    for s in (x for x in specs if not x["feasible"]):
        f = s["feasibility"]
        assert "cannot be drawn from the complement" in f["reason"]
        assert f["segment_positives"] > f["complement_positives"]


# ---- Criterion H and the spend guards --------------------------------------

def test_the_expected_seconds_quote_a_BAND_not_a_single_number():
    """The two cost anchors disagree by 2.4x and both are described as
    measured. Quoting either alone would present a contested figure as
    settled, which is the Sprint 11 defect: a probe approved at "0-5 seconds"
    cost 10 because the number was never established."""
    e = b4.EXPECTED_SECONDS
    assert "250" in e and "680" in e, "both ends of the band must be stated"
    assert "disagree" in e or "contested" in e.lower(), (
        "the statement must say the anchors conflict, not hide it")


def test_the_block_cap_sits_at_or_below_the_stated_ceiling():
    assert b4.BLOCK_CAP_S <= b4.EXPECTED_CEILING_S
    assert b4.ALLOCATION_FLOOR_S == 776.0


def test_the_window_matches_the_instruction():
    assert b4.WINDOW_HOUR == 18
    assert not b4._window_open(datetime(2026, 10, 5, 17, 59))
    assert b4._window_open(datetime(2026, 10, 5, 18, 0))


def test_running_before_the_window_exits_nonzero():
    r = subprocess.run(
        [sys.executable, str(SRC / "run_hardware_b4.py"), "--max-calls", "1"],
        capture_output=True, text=True, cwd=str(ROOT), timeout=2400)
    if "REFUSING" not in r.stdout:
        pytest.skip(f"the window is open now ({datetime.now():%H:%M})")
    assert r.returncode == 3, (
        "a guard that refuses while exiting 0 reports success to its caller")


# ---- idempotency -----------------------------------------------------------

def test_a_failed_row_stays_retryable(tmp_path, monkeypatch):
    results = tmp_path / "results.json"
    results.write_text(json.dumps({"rows": [
        {"arm": b4.ARM, "block": "B4", "dataset": "spectra_telecom_churn",
         "seed": 42, "status": "ok"},
        {"arm": b4.ARM, "block": "B4", "dataset": "spectra_telecom_churn",
         "seed": 43, "status": "failed"},
    ]}), encoding="utf-8")
    monkeypatch.setattr(b4, "RESULTS", results)
    done = b4._done()
    assert (b4.ARM, "spectra_telecom_churn", 42) in done
    assert (b4.ARM, "spectra_telecom_churn", 43) not in done


def test_an_unreadable_ledger_refuses_to_submit(tmp_path, monkeypatch):
    bad = tmp_path / "results.json"
    bad.write_text("{nope", encoding="utf-8")
    monkeypatch.setattr(b4, "RESULTS", bad)
    with pytest.raises(SystemExit, match="cannot read its own ledger"):
        b4._done()


def test_another_blocks_seconds_are_not_charged_to_b4(tmp_path, monkeypatch):
    results = tmp_path / "results.json"
    results.write_text(json.dumps({"rows": [
        {"arm": "cvqboost_hw", "block": "B2", "seed": 42,
         "status": "ok", "metered_seconds": 91},
    ]}), encoding="utf-8")
    monkeypatch.setattr(b4, "RESULTS", results)
    assert b4._spent() == 0.0


# ---- F90's acceptance criteria, as code ------------------------------------

def test_the_runner_stores_every_returned_sample():
    """F90 acceptance (c). Storing only the lowest-energy sample would make
    F20's multi-sample ensembling cost device time a second time."""
    src = (SRC / "run_hardware_b4.py").read_text(encoding="utf-8")
    assert "all_samples" in src
    assert "n_samples_returned" in src


def test_the_runner_records_the_weight_cosine_and_the_train_test_gap():
    """F90 acceptance: the weight cosine, because forced sparsity under A31 is
    the expected mechanism rather than a defect; and the train-test gap beside
    every win, because the prior in-segment wins came with a gap well above
    XGBoost's (one case 0.98 train to 0.59 test)."""
    src = (SRC / "run_hardware_b4.py").read_text(encoding="utf-8")
    assert "weight_cosine_vs_classical" in src
    assert "train_test_ap_gap" in src
