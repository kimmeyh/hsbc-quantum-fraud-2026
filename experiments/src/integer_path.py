"""Dirac-3 INTEGER path: build, size and validate a job without submitting it.

F87, Sprint 18 Task A. Phase 1 ran only the CONTINUOUS relaxation, which is
convex -- an exact classical solve returns the global optimum in milliseconds,
so no device can beat it. That is why the Phase 1 hardware result is a fidelity
measurement rather than a performance claim. The integer solver is the
formulation where the optimizer has real work to do, and this module is the
path to it.

WHY THIS MODULE EXISTS SEPARATELY FROM THE SUBMISSION. The sprint's premise
falsifier: the metered probe must measure the DEVICE, not a bug in our own
submission code. `Dirac3IntegerCloudSolver` is a cloud solver and cannot be run
without a metered call, so everything that CAN be checked locally is checked
here first. Measured on this repository's pinned eqc-models 0.21.0:

    built locally, no device call:  the model, its polynomial operator, its
                                    QUBO form, the H tuple, and the exact
                                    num_levels list the solver would send
    requires the device:            solve() only

So the payload is fully inspectable before a second of allocation is spent.

THE num_levels RELATION, read from the library rather than assumed. The card
supposed `num_levels` was a solve parameter. It is not. `solve()` computes:

    num_levels = [val + 1 for val in model.upper_bound.tolist()]

so the DEVICE BUDGET is `sum(upper_bound + 1)`, not the variable count. A
10-variable model with upper_bound 4 costs 50 levels, not 10. That distinction
is what sizes a block against the documented 949 ceiling, and getting it wrong
would have produced a probe quoted at the wrong size.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

# QCi documents 949 as the sum-over-levels ceiling for integer-encoded jobs.
# A12 separately established a 100-variable cap on the FREE tier for
# continuous, sum-constrained runs; the two limits bind different job classes
# and only one of them is documented (see QCI_EQC_MODELS_FEEDBACK.md section 1).
DEVICE_LEVEL_CEILING = 949


@dataclass
class IntegerJob:
    """A Dirac-3 integer job, sized and validated before submission."""

    linear: np.ndarray
    quadratic: np.ndarray
    upper_bound: np.ndarray
    relaxation_schedule: int = 2
    num_samples: int = 8
    notes: list[str] = field(default_factory=list)

    @property
    def n_variables(self) -> int:
        return int(self.linear.shape[0])

    @property
    def num_levels(self) -> list[int]:
        """Exactly what Dirac3IntegerCloudSolver.solve() sends.

        Read from the library source, not inferred: `solve()` computes
        `[val + 1 for val in model.upper_bound.tolist()]`.
        """
        return [int(v) + 1 for v in self.upper_bound.tolist()]

    @property
    def level_budget(self) -> int:
        """The quantity that binds against the 949 ceiling."""
        return int(sum(self.num_levels))

    def fits_device(self) -> bool:
        return self.level_budget <= DEVICE_LEVEL_CEILING

    def validate(self) -> list[str]:
        """Every check that can be made WITHOUT a metered call.

        Returns a list of problems. Empty means the job is submittable as far
        as anything local can tell -- which is the most the falsifier allows
        us to claim.
        """
        problems: list[str] = []
        n = self.n_variables

        if self.quadratic.shape != (n, n):
            problems.append(
                f"quadratic is {self.quadratic.shape}, expected ({n}, {n})")
        if self.upper_bound.shape != (n,):
            problems.append(
                f"upper_bound is {self.upper_bound.shape}, expected ({n},)")
        if self.upper_bound.size and int(self.upper_bound.min()) < 1:
            problems.append(
                "upper_bound has a value below 1; a variable with zero levels "
                "cannot take a value")
        if not np.allclose(self.quadratic, self.quadratic.T):
            problems.append(
                "quadratic is not symmetric; the device reads it as a "
                "quadratic form and an asymmetric matrix silently encodes a "
                "different objective")
        if not np.isfinite(self.linear).all() or not np.isfinite(self.quadratic).all():
            problems.append("linear or quadratic carries a non-finite value")
        if not self.fits_device():
            problems.append(
                f"level budget {self.level_budget} exceeds the documented "
                f"ceiling {DEVICE_LEVEL_CEILING}. sum(upper_bound + 1) is what "
                "binds, NOT the variable count")
        if self.relaxation_schedule not in (1, 2, 3, 4):
            problems.append(
                f"relaxation_schedule {self.relaxation_schedule} is outside "
                "the documented 1-4")
        if self.num_samples < 1:
            problems.append("num_samples must be at least 1")
        return problems

    def to_model(self):
        """The eqc-models object the solver takes.

        Imported lazily: this module is inspected by tests that must not
        require the vendor package to be importable.
        """
        from eqc_models.base import QuadraticModel

        model = QuadraticModel(self.linear, self.quadratic)
        model.upper_bound = self.upper_bound
        return model


def size_report(job: IntegerJob) -> str:
    """One block of text stating what would be sent, for the approval stop.

    Criterion H requires a block to be quoted with its call count and expected
    seconds before it runs. For this probe the seconds are UNKNOWN by
    construction, so what can honestly be quoted is the size.
    """
    problems = job.validate()
    lines = [
        f"variables        : {job.n_variables}",
        f"level budget     : {job.level_budget} of {DEVICE_LEVEL_CEILING} "
        f"(sum of upper_bound + 1)",
        f"num_levels       : {job.num_levels[:8]}"
        + (" ..." if len(job.num_levels) > 8 else ""),
        f"relaxation_sched : {job.relaxation_schedule}",
        f"num_samples      : {job.num_samples}",
        f"fits the device  : {job.fits_device()}",
        f"local validation : {'CLEAN' if not problems else 'PROBLEMS'}",
    ]
    lines += [f"  - {p}" for p in problems]
    return "\n".join(lines)
