"""Known-answer tests for gate-scoring aggregation (Sprint 4 retro improvement 1).

Every reported number passes through score_gates.py, and it had no tests: three
separate defects were fixed there by inspection during Sprint 4. These pin the
aggregation logic against hand-computable fixtures.
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))


def _load():
    spec = importlib.util.spec_from_file_location("score_gates", SRC / "score_gates.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_gate_constants_match_the_preregistration():
    """G0's floor, the leakage tripwire, and the A5 MDE are protocol values;
    a silent edit here would rescore a gate."""
    sg = _load()
    assert sg.G0_FLOOR == 0.85, "prereg 3 floor"
    assert sg.G0_LEAK_FLAG == 0.95, "leakage tripwire"
    assert sg.MDE == 0.0268, "amendment A5 measured paired-delta MDE"
    assert sg.N_SEEDS == 10, "prereg 8.1 primary seed count"


def test_mde_is_a_single_source():
    """Sprint 4 finding: the MDE was hard-coded twice, so the report could print
    one value and adjudicate against another."""
    text = (SRC / "score_gates.py").read_text(encoding="utf-8")
    assert text.count("0.0268") <= 1, "MDE must appear once, as the MDE constant"


def test_seed_mean_t_interval_known_answer():
    """The H1b decision rule against a hand-computable case."""
    import metrics

    d = [0.10] * 10                      # zero variance -> zero-width interval at the mean
    ti = metrics.seed_mean_t_interval(d)
    assert ti["mean"] == pytest.approx(0.10)
    assert ti["ci95"][0] == pytest.approx(0.10) and ti["ci95"][1] == pytest.approx(0.10)

    d2 = [0.0, 0.2] * 5                  # mean 0.1, symmetric spread
    ti2 = metrics.seed_mean_t_interval(d2)
    assert ti2["mean"] == pytest.approx(0.10)
    assert ti2["ci95"][0] < 0.10 < ti2["ci95"][1]


def test_spearman_guard_on_degenerate_input():
    """G0b over a constant input is undefined; a nan must never read as FAIL
    against a numeric gate (Sprint 4 review finding)."""
    from scipy.stats import spearmanr

    rho = spearmanr([1.0, 1.0, 1.0, 1.0, 1.0], [0.1, 0.2, 0.3, 0.4, 0.5]).statistic
    assert not np.isfinite(rho), "constant input yields an undefined correlation"
    assert not (rho >= 0.5), "a nan comparison must not evaluate true"
    text = (SRC / "score_gates.py").read_text(encoding="utf-8")
    assert "isfinite" in text, "the scorer must guard the degenerate case"


def test_hardware_pairs_by_config_hash_not_string_surgery():
    """Sprint 4 review finding: label-to-label .replace() chains broke silently."""
    text = (SRC / "score_gates.py").read_text(encoding="utf-8")
    assert 'replace("hw_b1_dct"' not in text, "pairing must not use label string surgery"
    assert "hw_hashes" in text and "config_hash" in text


def test_report_generates_over_the_live_store():
    """End-to-end: the scorer runs on the real store and emits the sections the
    memo and paper cite. Catches keying regressions like the Sprint 4 one where
    the hardware H1b block silently produced no lines."""
    sg = _load()
    assert sg.main() == 0
    report = (SRC.parents[0] / "results" / "gate_report.md").read_text(encoding="utf-8")
    for section in ("## G0 ", "## Score health", "## Hardware rows",
                    "### H1b on hardware", "## A3 build side-by-side"):
        assert section in report, f"missing section: {section}"
    assert "minus exact proxy" in report, "H4 solver-fidelity line must be paired and emitted"
