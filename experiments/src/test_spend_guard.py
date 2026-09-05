"""Property tests for the metered spend guard (F34).

Three defects landed on this path in a single sprint, and none was caught by a
test:

- the block cap was set to 60 s when the team lead approved 40-50 s, so the code
  could have authorized spend that was never granted;
- the pre-call projection added `_spent()` (which reads results.json) to the
  in-memory rows that `append_row` had ALREADY written there, double-counting
  every fit; the block halted at a reported 50.0 s when 25.0 s had been spent,
  losing four approved seeds;
- `_metered` returned the FIRST device-usage value found depth-first rather than
  the conservative maximum, so a response nesting a per-sample runtime beside a
  larger total could under-charge the guard.

The guard is the only thing standing between a stated approval and an overrun,
so it gets tests that assert its PROPERTIES rather than its current output. Each
test below fails on the specific defect named in its docstring.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_hardware_f32 as f32

APPROVAL_S = 50.0   # top of the team lead's 40-50 s envelope, 2026-09-04


def test_cap_never_exceeds_the_stated_approval():
    """Defect 1: a cap above the approval lets the code authorize spend the
    team lead did not grant. The cap belongs AT the grant, never above it."""
    assert f32.BLOCK_CAP_S <= APPROVAL_S, (
        f"cap {f32.BLOCK_CAP_S}s exceeds the {APPROVAL_S}s approval; a guard "
        "cannot authorize more than was granted"
    )


def test_spend_comes_from_exactly_one_source():
    """Defect 2: double-counting. `_spent()` must read results.json and nothing
    else, so no caller can add already-persisted rows to it a second time."""
    import inspect
    src = inspect.getsource(f32._spent)
    assert "RESULTS" in src or "results" in src.lower()

    main_src = inspect.getsource(f32.main)
    # the fix: `spent = _spent()`, never `_spent() + sum(... for r in rows)`
    assert "_spent() +" not in main_src, (
        "spend is being summed from two sources; append_row has already written "
        "completed fits to results.json, so adding in-memory rows double-counts"
    )


def test_unparseable_billing_is_charged_not_ignored():
    """A response the client cannot bill from must NEVER count as zero spend:
    the guard would go blind and the cap could not fire (amendment A8)."""
    assert f32._metered(object()) is None, "unbillable must return None, not 0.0"
    assert f32.UNPARSEABLE_CALL_CHARGE_S > 0, "the conservative charge must be positive"
    assert f32.UNPARSEABLE_CALL_CHARGE_S >= f32.EXPECTED_CALL_S, (
        "charging LESS than an expected call for an unbillable one is not "
        "conservative"
    )


def test_billing_takes_the_maximum_of_all_usage_keys():
    """Defect 3: first-found billing. A response can nest more than one usage
    key, and the conservative reading is the largest."""
    assert f32._metered({"a": {"device_usage_s": 4}, "b": {"run_time": [9, 9]}}) == 9.0
    assert f32._metered({"a": {"device_usage_s": 12}, "b": {"run_time": [3]}}) == 12.0
    # a list-valued key must bill at its own max, not be skipped
    assert f32._metered({"results": {"run_time": [1, 7, 2]}}) == 7.0


def test_cap_bounds_the_call_it_precedes():
    """The projection must be checked BEFORE the call, using the expected cost
    of that call. Checking after it is a report, not a guard."""
    import inspect
    src = inspect.getsource(f32.main)
    assert "spent + EXPECTED_CALL_S >= BLOCK_CAP_S" in src, (
        "the pre-call projection is missing; the cap would only be noticed after "
        "the spend it was meant to prevent"
    )
    assert "spent >= BLOCK_CAP_S" in src, (
        "a hard stop on recorded spend is missing; the projection alone cannot "
        "bound a call that bills far above the expected rate"
    )


def test_a_failed_call_still_records_its_spend():
    """The device may bill before a failure. A run that dies without appending a
    row makes those seconds invisible to `_spent()`, and the next run re-spends
    against a cap that silently reset."""
    import inspect
    src = inspect.getsource(f32.run_seed)
    assert "except Exception" in src, "the metered call is unguarded"
    assert "store.append_row" in src and '"failed"' in src, (
        "a failed metered call must still record a charged row"
    )


def test_free_tier_sizing_refuses_before_the_device_has_to():
    """Local arithmetic, zero cost. Discovering a sizing error from an HTTP 400
    mid-campaign wastes a pool build and surfaces as an error rather than a
    decision (amendment A12)."""
    with pytest.raises(SystemExit):
        f32.check_free_tier_size(f32.FREE_TIER_MAX_VARS + 1)
    f32.check_free_tier_size(f32.FREE_TIER_MAX_VARS)      # at the limit: allowed


def test_recorded_spend_matches_the_saved_responses():
    """End-to-end reconciliation: what results.json claims was billed must equal
    what the saved device responses say. A divergence means the store and the
    vendor disagree about spend, which is the condition the guard exists to
    prevent."""
    import re
    results = Path(__file__).resolve().parents[1] / "results" / "results.json"
    resp_dir = Path(__file__).resolve().parents[1] / "results" / "pools" / "hw_responses"
    if not results.exists() or not resp_dir.exists():
        pytest.skip("no metered campaign in this checkout")

    rows = [r for r in json.loads(results.read_text())["rows"]
            if r.get("block") == "F32"]
    if not rows:
        pytest.skip("no F32 block recorded")

    recorded = sum(r.get("metered_seconds") or 0.0 for r in rows)
    from_responses = 0.0
    for f in resp_dir.glob("f32_*.json"):
        vals = [float(x) for x in
                re.findall(r"'device_usage_s':\s*([0-9.]+)", f.read_text())]
        from_responses += max(vals) if vals else 0.0

    assert recorded == pytest.approx(from_responses, abs=0.01), (
        f"results.json records {recorded}s but the saved responses total "
        f"{from_responses}s"
    )
    assert recorded <= APPROVAL_S, (
        f"{recorded}s exceeds the {APPROVAL_S}s approval"
    )
