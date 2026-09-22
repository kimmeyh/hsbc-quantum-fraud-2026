"""The integer path must be sizeable and checkable WITHOUT a metered call.

F87, Sprint 18 Task A. This file is the sprint's premise falsifier made
executable: if the integer job cannot be built and validated locally, then the
Task B probe is a first attempt rather than a probe, and its cost is
unpredictable in a way Criterion H does not allow for.

THE num_levels RELATION IS THE THING TO GET RIGHT. The F87 card assumed
`num_levels` was a solve parameter. Reading
`Dirac3IntegerCloudSolver.solve()` shows it is not:

    num_levels = [val + 1 for val in model.upper_bound.tolist()]

So the device budget is `sum(upper_bound + 1)`, NOT the variable count. A
10-variable model at upper_bound 4 costs 50 levels. Sizing a block on the
variable count would quote the wrong number to QCi, which is the whole failure
this card exists to prevent.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))
from integer_path import (DEVICE_LEVEL_CEILING, IntegerJob,  # noqa: E402
                          size_report)


def _job(n: int = 6, ub: int = 3) -> IntegerJob:
    rng = np.random.default_rng(42)
    a = rng.normal(size=(n, n))
    return IntegerJob(linear=rng.normal(size=n),
                      quadratic=(a + a.T) / 2,
                      upper_bound=np.full(n, ub))


# ------------------------------------------------- the num_levels relation

def test_num_levels_is_upper_bound_plus_one_per_variable():
    job = _job(n=6, ub=3)
    assert job.num_levels == [4] * 6


def test_the_level_budget_is_not_the_variable_count():
    """The distinction that sizes a block. A test asserting only that the
    budget is positive would pass on the variable count and miss this."""
    job = _job(n=10, ub=4)
    assert job.n_variables == 10
    assert job.level_budget == 50, (
        "level budget must be sum(upper_bound + 1), not the variable count")


def test_the_relation_matches_what_the_library_actually_sends():
    """Pinned against eqc-models rather than restated.

    If the vendor changes the relation, this fails instead of the probe
    quoting a size the device does not agree with.
    """
    pytest.importorskip("eqc_models")
    job = _job(n=5, ub=2)
    model = job.to_model()
    library_form = [int(v) + 1 for v in model.upper_bound.tolist()]
    assert library_form == job.num_levels


# ---------------------------------------------------- local validation

def test_a_well_formed_job_validates_clean():
    assert _job().validate() == []


def test_an_asymmetric_quadratic_is_caught():
    """The device reads the matrix as a quadratic form, so an asymmetric one
    silently encodes a DIFFERENT objective -- a plausible wrong result rather
    than an error, which is this repository's recurring class."""
    job = _job(n=4)
    job.quadratic[0, 1] += 5.0
    problems = job.validate()
    assert any("not symmetric" in p for p in problems), problems


def test_a_job_over_the_device_ceiling_is_caught():
    job = _job(n=200, ub=4)          # 200 * 5 = 1000 levels
    assert job.level_budget == 1000
    assert not job.fits_device()
    assert any("exceeds the documented ceiling" in p for p in job.validate())


def test_a_job_at_exactly_the_ceiling_fits():
    """Boundary. An off-by-one here would refuse a legal block or submit an
    illegal one."""
    job = _job(n=DEVICE_LEVEL_CEILING, ub=0)   # each contributes 1 level
    assert job.level_budget == DEVICE_LEVEL_CEILING
    assert job.fits_device()


def test_a_zero_level_variable_is_caught():
    job = _job(n=4)
    job.upper_bound = np.array([1, 1, 0, 1]) - 1   # one variable at 0 levels
    assert any("below 1" in p for p in job.validate())


def test_a_non_finite_coefficient_is_caught():
    job = _job(n=4)
    job.linear[2] = np.inf
    assert any("non-finite" in p for p in job.validate())


def test_a_shape_mismatch_is_caught():
    job = _job(n=4)
    job.quadratic = np.eye(3)
    assert any("expected (4, 4)" in p for p in job.validate())


def test_an_out_of_range_relaxation_schedule_is_caught():
    job = _job()
    job.relaxation_schedule = 9
    assert any("outside the documented 1-4" in p for p in job.validate())


# ------------------------------------------------- the falsifier itself

def test_the_device_payload_builds_with_no_metered_call():
    """THE SPRINT'S PREMISE FALSIFIER.

    Everything the solver would send must be constructible locally. If this
    fails, the Task B probe measures our own code rather than the device and
    the block must be re-scoped before it runs.
    """
    pytest.importorskip("eqc_models")
    job = _job(n=8, ub=2)
    model = job.to_model()

    assert model.polynomial is not None, "no polynomial operator built"
    assert model.H is not None, "no device-form H built"
    assert job.validate() == [], "a locally checkable problem remains"


def test_the_size_report_states_what_would_be_sent():
    """The approval stop quotes size, because the seconds are unknown by
    construction. A report missing the budget cannot support that."""
    text = size_report(_job(n=7, ub=3))
    for probe in ("variables", "level budget", "num_levels",
                  "relaxation_sched", "num_samples", "fits the device"):
        assert probe in text, f"size report omits {probe!r}"


def test_the_size_report_names_its_problems():
    job = _job(n=4)
    job.quadratic[0, 1] += 5.0
    text = size_report(job)
    assert "PROBLEMS" in text and "not symmetric" in text
