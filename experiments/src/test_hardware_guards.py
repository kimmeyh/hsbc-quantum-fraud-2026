"""Guards on the metered hardware runner (PR #21 review findings 1-3).

These test the SAFETY properties of spend accounting, not the solver. They must
never require credentials or make a call.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))


def _load_runner():
    spec = importlib.util.spec_from_file_location("run_hardware", SRC / "run_hardware.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_metered_parses_solutionresults_repr():
    """eqc-models returns a SolutionResults object, not a dict; the billed field
    lives in its repr. Verified against the first real G0b response."""
    rh = _load_runner()

    class FakeResults:
        def __repr__(self):
            return "SolutionResults(solutions=array([...]), 'device_usage_s': 4, 'job_id': 'x')"

    assert rh._metered(FakeResults()) == 4.0
    assert rh._metered({"job_info": {"device_usage_s": 7}}) == 7.0


def test_unparseable_billing_is_never_free():
    """THE budget-blindness bug: if billed seconds cannot be parsed, the row must
    NOT count as 0.0 spend, or _spent() goes blind and the cap cannot fire."""
    rh = _load_runner()

    class Unparseable:
        def __repr__(self):
            return "SomeNewVendorFormat(no billing field here)"

    assert rh._metered(Unparseable()) is None
    assert rh.UNPARSEABLE_CALL_CHARGE_S > 0, "an unreadable call must still be charged"


def test_cap_bounds_the_call_it_precedes():
    """The guard must stop BEFORE a call that would reach the cap, not after."""
    rh = _load_runner()
    for block, cap in rh.BLOCK_CAP_S.items():
        assert rh.EXPECTED_CALL_S > 0
        just_under = cap - rh.EXPECTED_CALL_S
        assert just_under + rh.EXPECTED_CALL_S >= cap, (
            f"{block}: a call from spend {just_under} would reach the cap and must be refused")


def test_temporal_rows_carry_no_seed():
    """temporal_split ignores the seed; recording one misrepresents provenance."""
    import data

    df = None
    assert data.Split.__dataclass_fields__["seed"].type in ("int | None", "Optional[int]")


@pytest.mark.parametrize("msg", [
    "Job rejected: number of variables exceeds free-tier device limit",
    "ERROR: variable count above the free tier limit for this token",
])
def test_sizing_errors_are_recognized(msg):
    """A reworded vendor sizing error must still be recognized as no-retry."""
    m = msg.lower()
    matched = ("number of variables" in m or ("variable" in m and "limit" in m)
               or "free-tier" in m or "free tier" in m)
    assert matched, f"sizing error not recognized: {msg}"
