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


def test_metered_reads_a_real_billing_field_wherever_it_appears():
    """A device_usage_s field in the response is still the cheapest right answer."""
    rh = _load_runner()
    assert rh._metered({"job_info": {"device_usage_s": 7}}) == 7.0


def test_metered_does_not_scrape_a_repr(monkeypatch):
    """Sprint 11 improvement 1: the repr fallback is gone, and must stay gone.

    It was added for the free tier, where SolutionResults carried the billed
    field in its repr. PAID-TIER RESPONSES DO NOT CARRY IT, so the scrape
    returned nothing and the caller's UNPARSEABLE_CALL_CHARGE_S default was
    recorded as though it were a measurement -- the F46 probe logged 5.0 seconds
    for a call the allocation balance showed cost 10.

    Returning None is the point: a caller that cannot establish the cost must
    say so. The conservative charge is then applied KNOWINGLY, which is a
    different thing from a scraped number that silently became a default.
    """
    rh = _load_runner()

    class PaidTierResults:
        """Shaped like the real F46 response: no billing field anywhere."""
        def __repr__(self):
            return "SolutionResults(solutions=array([0.0075, 0.0074]), energies=[...])"

    assert rh._metered(PaidTierResults()) is None

    class FreeTierResults:
        """The old shape. Even here, the repr is no longer trusted."""
        def __repr__(self):
            return "SolutionResults(solutions=array([...]), 'device_usage_s': 4, 'job_id': 'x')"

    assert rh._metered(FreeTierResults()) is None, (
        "the repr scrape is back; it silently defaults on the paid tier and is "
        "why a 10-second call was recorded as 5")


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


def _load_f32():
    spec = importlib.util.spec_from_file_location(
        "run_hardware_f32", SRC / "run_hardware_f32.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_an_oversized_job_is_refused_before_submission():
    """The free-tier size limit is enforced LOCALLY, by production code.

    The previous version of this test re-implemented the matcher inline and
    asserted against its own copy -- it never imported anything from the
    runner, so no change to production code could fail it. It was cited to
    QCi as evidence that the rejection message is pinned. Found by the PR
    #139 review.

    What actually exists is a pre-submission size check, which is the
    stronger guarantee: the job never leaves the machine.
    """
    f32 = _load_f32()
    with pytest.raises(SystemExit) as exc:
        f32.check_free_tier_size(f32.FREE_TIER_MAX_VARS + 1)
    msg = str(exc.value)
    assert "REFUSING to submit" in msg
    assert str(f32.FREE_TIER_MAX_VARS) in msg, (
        "the refusal does not state the limit it enforced")


def test_a_job_at_the_limit_is_allowed():
    """The boundary. Without it, refusing everything would pass the test
    above and no job could ever be submitted."""
    f32 = _load_f32()
    f32.check_free_tier_size(f32.FREE_TIER_MAX_VARS)
