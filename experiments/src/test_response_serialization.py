"""Device responses are saved IN FULL, and dry runs return the real type.

Sprint 22. The B4 and B5 runners saved each response with
`json.dumps(resp, default=str)`. A real solve returns a `SolutionResults`
dataclass, so `default=str` stored its printed form -- numpy truncates long
arrays when printing, and every 560- and 816-value sample was saved as its
first and last three values. The B4 rows also recorded n_samples_returned = 0,
because the runner looked for a dict. The full samples were recovered by job
id (experiments/phase2/src/recover_device_samples.py).

It reached the device unseen because `eqc_submit.offline_solver` returned a
plain dict, so every dry run exercised a shape no real run produces. Both are
pinned here.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "src"))

import eqc_submit  # noqa: E402


def _model(n):
    """A REAL eqc model, so from_cloud_response sees the attributes a real
    solve has (machine_slacks, upper_bound)."""
    from eqc_models.ml.classifierqsvm import QSVMClassifier
    m = QSVMClassifier()
    m.set_model(np.eye(n), np.zeros((n, 1)), 1.0)
    return m


def _real_shaped(n=816, ns=8):
    from eqc_models.base.results import SolutionResults

    rng = np.random.default_rng(0)
    raw = {"results": {"solutions": [list(rng.dirichlet(np.ones(n)))
                                     for _ in range(ns)],
                       "energies": list(rng.normal(size=ns)),
                       "counts": [1] * ns},
           "job_info": {"job_id": "a" * 24, "job_submission": {
               "device_config": {"dirac-3": {"num_samples": ns}}}}}
    class _Solver:
        class client:                                   # noqa: N801
            @staticmethod
            def get_job_metrics(job_id=None):
                return {}

    return SolutionResults.from_cloud_response(_model(n), raw, _Solver())


def test_a_solution_results_round_trips_every_value():
    resp = _real_shaped()
    data = json.loads(json.dumps(eqc_submit.to_jsonable(resp)))
    sols = data["solutions"]
    assert len(sols) == 8 and all(len(s) == 816 for s in sols), (
        "a full 816-value sample must survive serialization")


def test_default_str_is_the_defect_this_replaces():
    """The original call, kept as a measurement: it does not round-trip."""
    text = json.dumps(_real_shaped(), default=str)
    assert "..." in text, (
        "numpy's print truncates; if this ever stops truncating, the reason "
        "for to_jsonable should be re-checked")


def test_samples_of_reads_the_real_object():
    assert len(eqc_submit.samples_of(_real_shaped())) == 8


def test_the_offline_solver_returns_the_real_response_type():
    """Dry runs must hand the runners what a real solve hands them."""
    from eqc_models.base.results import SolutionResults

    sent: list = []
    with eqc_submit.offline_solver(sent):
        import eqc_models.ml.classifierbase as cb
        resp = cb.Dirac3CloudSolver().solve(_model(4), num_samples=3,
                                           sum_constraint=1.0,
                                           relaxation_schedule=2)
    assert isinstance(resp, SolutionResults), (
        f"offline_solver returned {type(resp).__name__}; a real solve returns "
        "SolutionResults, so the dry run would test a shape no run produces")
    assert len(eqc_submit.samples_of(resp)) == 3


def test_neither_runner_uses_default_str_on_a_response():
    for name in ("run_hardware_b4.py", "run_hardware_b5.py"):
        src = (ROOT / "experiments" / "src" / name).read_text(encoding="utf-8")
        assert "json.dumps(resp, default=str" not in src, (
            f"{name} saves a response with default=str again")
