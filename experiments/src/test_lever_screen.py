"""F124's lever screen compares each lever against the FROZEN B4 configuration.

Sprint 22 Task C. A screen whose baseline drifted from the frozen config would
rank levers against the wrong reference, and the drift would look exactly like
a lever effect. These guards pin the variant table and the summary arithmetic
on synthetic rows: zero metered, no dataset, nothing written to an evidence
directory (IMP-3).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "src"))
sys.path.insert(0, str(ROOT / "experiments" / "phase2" / "src"))

import lever_screen as ls        # noqa: E402
import spectra_segment as ss     # noqa: E402


def test_the_baseline_is_the_frozen_b4_configuration():
    base = ls.VARIANTS["baseline_dct"]
    for cell in ss.FROZEN_CELLS:
        cfg = cell["config"]
        assert base["weak_type"] == "dct"
        assert base["params"] == cfg["weak_cls_params"], (
            f"baseline params {base['params']} differ from the frozen "
            f"{cfg['weak_cls_params']} on {cell['dataset']}")
        assert base["alpha"] is None, (
            "a baseline alpha would override the frozen lambda_coef_alpha")


def test_every_variant_differs_from_the_baseline_in_one_named_way():
    base = ls.VARIANTS["baseline_dct"]
    for name, v in ls.VARIANTS.items():
        if name == "baseline_dct":
            continue
        changed = [k for k in ("weak_type", "params", "alpha")
                   if v[k] != base[k]]
        assert changed, f"{name} is identical to the baseline"


def _row(ds, seed, variant, test, train=1.0):
    return {"dataset": ds, "seed": seed, "variant": variant,
            "test_auprc": test, "train_auprc": train}


def test_the_delta_is_paired_by_seed():
    rows = [_row("d", 42, "baseline_dct", 0.80), _row("d", 43, "baseline_dct", 0.60),
            _row("d", 42, "knn", 0.82), _row("d", 43, "knn", 0.61)]
    s = ls._summarize(rows)["d"]["knn"]
    assert s["mean_delta_vs_baseline"] == pytest.approx(0.015)
    assert s["mean_train_test_gap"] == pytest.approx(1.0 - 0.715)


def test_a_variant_that_failed_everywhere_is_reported_not_dropped():
    rows = [_row("d", 42, "baseline_dct", 0.80),
            {"dataset": "d", "seed": 42, "variant": "xgb", "error": "boom"}]
    s = ls._summarize(rows)["d"]
    assert s["xgb"] == {"status": "failed on every seed"}


def test_unknown_part_is_refused(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["lever_screen.py", "nonsense"])
    with pytest.raises(SystemExit, match="unknown part"):
        ls.main()
