"""Correctness invariants for the IEEE runners (Sprint 8 improvement 3).

WHY THESE EXIST. The Task C smoke test PASSED on code carrying four protocol
defects: no class weighting anywhere, TransactionID and TransactionDT entering
the model as raw features, the shuffled-label control never actually run, and a
minimum detectable effect borrowed from a different experimental design. The
smoke test asserted that the pipeline COMPLETES. It asserted nothing about
whether the pipeline was doing the right thing, so it passed confidently on
code that was wrong.

All four were found only because the team lead asked for a full sweep before
re-running. Each test below asserts the invariant whose violation was one of
those four defects, so the next occurrence is caught mechanically rather than by
someone happening to look.

The rule this encodes: a test that only proves code runs will pass on code that
is wrong. Every pipeline smoke path must assert at least one CORRECTNESS
invariant.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import numpy as np
import pytest

SRC = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


# --- Defect 1: no class weighting -----------------------------------------

def test_every_classical_arm_carries_exactly_one_weighting_mechanism():
    """Section 7: weighting only, EXACTLY ONE MECHANISM PER LIBRARY.

    The first version of this runner applied no weighting at all, which makes
    the IEEE arms a different estimator from the ULB arms and any cross-dataset
    comparison false.
    """
    run_ieee = importlib.import_module("run_ieee")

    # A realistic imbalanced fold: 3.5% positives, the IEEE prevalence.
    y = np.zeros(1000, dtype=int)
    y[:35] = 1

    for arm in ("xgboost", "lightgbm"):
        kw = run_ieee._weight_kwargs(arm, y)
        assert "scale_pos_weight" in kw, (
            f"{arm} must carry scale_pos_weight; unweighted arms silently "
            f"change the estimator")
        # 965 negatives / 35 positives
        assert kw["scale_pos_weight"] == pytest.approx(965 / 35), (
            f"{arm} scale_pos_weight must be neg/pos for THIS fold")

    # CatBoost takes its single mechanism in the config, not per fold. Taking
    # both would be two mechanisms, which section 7 forbids.
    assert run_ieee._weight_kwargs("catboost", y) == {}, (
        "catboost must not also receive scale_pos_weight")
    assert run_ieee.ARMS["catboost"].get("auto_class_weights") == "Balanced", (
        "catboost's one mechanism is auto_class_weights")


def test_weighting_responds_to_the_fold_it_is_given():
    """scale_pos_weight is fold-dependent, so a constant would be a bug."""
    run_ieee = importlib.import_module("run_ieee")

    y_rare = np.zeros(1000, dtype=int)
    y_rare[:10] = 1
    y_common = np.zeros(1000, dtype=int)
    y_common[:100] = 1

    rare = run_ieee._weight_kwargs("xgboost", y_rare)["scale_pos_weight"]
    common = run_ieee._weight_kwargs("xgboost", y_common)["scale_pos_weight"]
    assert rare > common, "rarer positives must get a larger weight"


# --- Defect 2: identifier columns entering the model -----------------------

IDENTIFIER_COLUMNS = ("TransactionID", "TransactionDT")


def test_identifier_columns_never_reach_the_feature_matrix():
    """TransactionID is a row key and TransactionDT is the raw clock.

    A model given the clock can memorise WHEN fraud occurred in the training
    months, which is the leak rolling-origin evaluation exists to prevent. Both
    survived into the feature matrix until the F3 pre-run audit. The
    adversarial control happened to remove them, but it stops at a round cap,
    so that was luck rather than compliance.

    Asserted BEHAVIOURALLY on the recipe's own output, not by grepping source:
    the exclusion is a property of the recipe, so that is where it is checked.
    """
    import pandas as pd
    ieee_features = importlib.import_module("ieee_features")

    frame = pd.DataFrame({
        "TransactionID": [1, 2, 3, 4],
        "TransactionDT": [86400, 172800, 259200, 345600],
        "card1": [100, 200, 100, 300],
        "addr1": [10, 20, 10, 30],
        "D1": [1.0, 2.0, 3.0, 4.0],
        "isFraud": [0, 1, 0, 1],
    })

    recipe = ieee_features.IEEEFeaturePipeline()
    out = recipe._finalize(frame.copy())

    for col in IDENTIFIER_COLUMNS:
        assert col not in out.columns, (
            f"{col} reached the feature matrix; section 5 item 5 forbids any "
            f"identifier column entering a model raw")
    # The exclusion must be surgical, not a blanket drop.
    assert "card1" in out.columns, "real features must survive the exclusion"


# --- Defect 3: the shuffled-label control never run ------------------------

@pytest.mark.slow
def test_shuffled_label_control_is_run_and_recorded_per_fold():
    """Section 5 item 6: the control must be RUN, not declared.

    If a model scores well on shuffled labels the fold has leaked and its
    numbers are void. A control that is never executed cannot report that.

    This EXECUTES the pipeline rather than grepping the source for the key,
    because a grep passes on code that names the key and never runs the
    control. That costs about 90 seconds, hence the slow marker: `-m "not
    slow"` skips it during rapid iteration, and the full suite runs it.
    """
    run_ieee = importlib.import_module("run_ieee")
    out = run_ieee.run(smoke=True)
    control = out.get("shuffled_label_control")
    assert control, "the control's results must be written to the output record"

    # per_fold holds one row per ARM per fold; the control is one per FOLD.
    # Comparing the two lengths directly fails on correct code.
    n_folds = len({r["fold"] for r in out["per_fold"]})
    assert len(control) == n_folds, (
        "the control must be recorded for every fold")
    assert all(r["collapses_to_base_rate"] for r in control), (
        "shuffled labels should collapse to the base rate on every fold")
    assert all("shuffled_auprc" in r for r in control), (
        "the control must actually store the measured AUPRC")


def test_shuffled_control_output_key_survives_in_committed_results():
    """The committed IEEE results must carry the control, on every fold."""
    import json
    results = (SRC.parents[0] / "results" / "ieee_classical.json")
    if not results.exists():
        pytest.skip("ieee_classical.json not present")
    d = json.loads(results.read_text(encoding="utf-8"))
    control = d.get("shuffled_label_control")
    assert control, "committed results must include the shuffled-label control"
    # per_fold carries one row per ARM per fold; the control is one per fold.
    n_folds = len({r["fold"] for r in d["per_fold"]})
    assert len(control) == n_folds, (
        "the control must be recorded for EVERY fold, not just the first")
    assert all(r["collapses_to_base_rate"] for r in control), (
        "a fold whose shuffled-label model does NOT collapse to the base rate "
        "has leaked, and that fold's numbers are void")
    for row in control:
        assert "shuffled_auprc" in row, "each control row needs its AUPRC"


# --- Defect 4: an MDE borrowed from a different design ---------------------

def test_ulb_mde_is_not_reused_for_ieee():
    """The ULB MDE (0.0268) came from pilot SEED variance on a 0.17% dataset.

    IEEE-CIS is temporal FOLDS at 3.5%. Reusing the number would assert a
    detectability claim the design does not support, so the constant is named
    to make reuse visible and MDE is left None until one is computed here.
    """
    mod = importlib.import_module("run_ieee_cvqboost")
    assert hasattr(mod, "ULB_MDE_DO_NOT_REUSE"), (
        "the borrowed constant must stay explicitly named")
    assert mod.ULB_MDE_DO_NOT_REUSE == 0.0268
    assert getattr(mod, "MDE", None) is None, (
        "MDE must stay None until one is computed from THIS design")
