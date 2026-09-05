"""Regression guard for the H6 twin capability pre-flights (Sprint 6 Task C
/ F23, card #33). These are SPIKES, not the H6 arms themselves (F4, Sprint
7) -- this test only proves the three primitives keep working in CI, each
well inside the ~5-minute SPRINT_PLANNING.md pre-flight budget.
"""
from h6_twin_preflight import run_all


def test_all_three_twin_primitives_pass():
    results = run_all()
    by_family = {r["family"]: r for r in results}
    assert set(by_family) == {"GAM", "GA2M", "JOINT"}
    for family, r in by_family.items():
        assert r["status"] == "PASS", f"{family} pre-flight failed: {r}"
        assert r["elapsed_s"] < 60, f"{family} pre-flight too slow: {r['elapsed_s']}s"
