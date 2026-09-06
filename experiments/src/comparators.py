"""Guards for reported comparisons (Sprint 7 retro improvement 1).

Three sprints running, the defects that travelled furthest were claims about
what a number MEANS rather than errors in the number itself:

- Sprint 5: the solved weight vector was reported "exactly uniform" with "L1
  0.000000" when the stored value was 8.0e-08, and the residual gain it implied
  was tie-breaking rather than optimization.
- Sprint 6: k=13 [SIM] mechanism evidence and k=6 [HW] hardware evidence were
  presented as one narrative, so a reader would conclude the mechanism had been
  confirmed on hardware. It had not.
- Sprint 7: the tuned pool (k=6) was measured against comparators at k=13, and a
  mid-run prediction compared sweep VALIDATION AP against TEST AP.

Every one was caught by reading, none by a test, and the Sprint 7 plan actually
INVITED the third by naming a k=13 figure as the acceptance criterion for a k=6
arm. ADR-0013 names this class exactly: an order-mismatched comparison is how
apparent quantum wins get manufactured.

These helpers make the mismatch fail loudly at the point a difference is
computed, rather than surviving into a document where only a careful reader
catches it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# Parameters that must match before two arms may be differenced. Feature count
# and protocol are the ones that have actually gone wrong; the rest are here
# because a silent mismatch in any of them makes a difference meaningless.
MATCH_KEYS = ("k", "protocol", "schedule", "dataset")


@dataclass(frozen=True)
class ArmSpec:
    """What a reported figure was measured on. `split` is validation or test."""

    label: str
    k: int
    protocol: str
    split: str
    schedule: int = 2
    dataset: str = "ulb"
    n_variables: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def as_match(self) -> dict:
        return {key: getattr(self, key) for key in MATCH_KEYS}


class ComparisonError(AssertionError):
    """Raised when two arms cannot legitimately be differenced."""


def assert_comparable(a: ArmSpec, b: ArmSpec) -> None:
    """Refuse a comparison whose arms differ in anything but the intervention.

    Two separate checks, because the two failures have different causes:

    1. CONFIGURATION. Differencing a k=6 arm against a k=13 comparator reports
       the feature count as if it were the treatment effect.
    2. SPLIT. Validation and test are different quantities. On this project's
       design validation runs about 0.005 below test, so comparing across them
       manufactures or hides a difference of that order -- which is a quarter of
       the minimum detectable effect.
    """
    mismatched = {
        key: (getattr(a, key), getattr(b, key))
        for key in MATCH_KEYS
        if getattr(a, key) != getattr(b, key)
    }
    if mismatched:
        detail = ", ".join(f"{k}: {v[0]!r} vs {v[1]!r}" for k, v in mismatched.items())
        raise ComparisonError(
            f"cannot difference '{a.label}' against '{b.label}': {detail}. "
            "The difference would report that mismatch as if it were the effect. "
            "Rebuild the comparator at the matched configuration, or report the "
            "two figures separately with their parameters named."
        )
    if a.split != b.split:
        raise ComparisonError(
            f"cannot difference '{a.label}' ({a.split}) against '{b.label}' "
            f"({b.split}): validation and test are different quantities. "
            "Selection uses validation; reported effects use test; never mix."
        )


def reported_difference(a: ArmSpec, a_value: float,
                        b: ArmSpec, b_value: float,
                        mde: float | None = None) -> dict:
    """Compute a difference only if the arms are comparable, and carry the
    provenance with it so a document cannot quote the number without its terms.

    When `mde` is given, the result states whether the difference clears it.
    A difference below the minimum detectable effect is reported as directional,
    never as a win -- the discipline F31 and F33 were both held to.
    """
    assert_comparable(a, b)
    diff = a_value - b_value
    out = {
        "difference": diff,
        "arm": a.label, "arm_value": a_value,
        "comparator": b.label, "comparator_value": b_value,
        "matched_on": a.as_match(),
        "split": a.split,
    }
    if mde is not None:
        out["mde"] = mde
        out["exceeds_mde"] = bool(abs(diff) > mde)
        out["reporting_guidance"] = (
            "exceeds the MDE; may be reported as a measured effect"
            if abs(diff) > mde else
            "BELOW the MDE; report as directional with the mechanism, never as a win"
        )
    return out
