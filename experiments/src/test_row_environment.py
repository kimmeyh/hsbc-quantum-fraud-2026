"""Every NEW results row records the environment that produced it (A33, F84).

WHY, stated precisely, because the justification is not the obvious one.
Sprint 17 Task H measured the suite on Windows and Linux and found ZERO
behavioral divergence. This is not a fix for a known difference.

It is provenance. Of the 168 rows written before the amendment, none records
its operating system, interpreter or BLAS. The reproducibility claim in
Appendix C rests on a lock file pinning 18 package versions and, deliberately,
no platform. So a future reader comparing a regenerated figure against a stored
one cannot tell whether a difference is a regression or a platform artifact.

That this is not hypothetical was demonstrated the same day the field was
written: the Linux venv built for Task H resolved numpy 2.5.3 against the
locked 1.26.4, and the `blas` field reports it. A row carrying that stamp makes
the drift visible; a row without it does not.

The 168 existing rows are NOT retrofitted, and these tests pin that too.
Back-filling a field that was never observed would be inventing provenance.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))
import store  # noqa: E402

RESULTS = SRC.parents[0] / "results" / "results.json"

REQUIRED_ENV_FIELDS = ("os", "os_release", "python", "threads")


def test_environment_returns_the_required_fields():
    env = store.environment()
    missing = [f for f in REQUIRED_ENV_FIELDS if f not in env]
    assert not missing, f"environment() is missing {missing}"


def test_environment_values_are_populated():
    """A field present but empty records nothing, which is the failure this
    whole amendment exists to prevent."""
    env = store.environment()
    for f in REQUIRED_ENV_FIELDS:
        assert env[f] not in (None, "", 0), f"{f} is empty: {env[f]!r}"


def test_environment_identifies_the_platform():
    env = store.environment()
    assert env["os"] in {"Windows", "Linux", "Darwin"}, env["os"]


def test_blas_is_recorded_when_numpy_is_loaded():
    """BLAS is read only when numpy is ALREADY imported, so that describing
    the environment never drags numpy into a process that does not use it."""
    import numpy  # noqa: F401
    env = store.environment()
    assert "blas" in env
    assert env["blas"], "blas present but empty"


def test_the_blas_field_is_a_blas_not_a_numpy_version():
    """The field must answer "which BLAS?", which is what A33 exists for.

    The first version called np.__config__.get_info("blas_opt"), removed in
    numpy 1.26 -- the version this repo PINS -- so the fallback was the live
    path everywhere and every row read blas: "numpy-1.26.4". The old test
    asserted only presence and truthiness, so the degraded value passed.

    OpenBLAS versus MKL is the classic cause of float-level divergence in this
    workload. Two rows both reading "numpy-<version>" cannot answer the
    question the field is named for. Found by the PR #122 review.
    """
    import numpy  # noqa: F401
    blas = store.environment()["blas"]
    assert not blas.startswith("numpy-"), (
        f"blas reports a numpy VERSION ({blas!r}), not a BLAS library")


def test_numpy_version_has_its_own_field():
    """Recorded separately rather than smuggled into `blas`."""
    import numpy
    env = store.environment()
    assert env.get("numpy") == numpy.__version__


def test_an_undeterminable_blas_says_so_rather_than_guessing():
    """"I could not check" must never render as a value that reads like an
    answer -- the conflation this repository keeps paying for."""
    import numpy
    real = numpy.__config__
    try:
        numpy.__config__ = object()          # no CONFIG, no get_info
        blas = store.environment()["blas"]
        assert "unavailable" in blas, (
            f"an undeterminable BLAS rendered as {blas!r}")
    finally:
        numpy.__config__ = real


def test_append_row_stamps_the_environment(tmp_path, monkeypatch):
    """The stamp happens in the single write path, so no caller can forget."""
    target = tmp_path / "results.json"
    target.write_text(json.dumps({"meta": {}, "rows": []}), encoding="utf-8")
    monkeypatch.setattr(store, "RESULTS", target)

    store.append_row({"arm": "test", "seed": 1, "evidence_tag": "SIM",
                      "config_hash": "abc", "metered_seconds": 0})

    rows = json.loads(target.read_text(encoding="utf-8"))["rows"]
    assert len(rows) == 1
    assert "environment" in rows[0], "append_row did not stamp the environment"
    for f in REQUIRED_ENV_FIELDS:
        assert f in rows[0]["environment"]


def test_append_row_does_not_overwrite_an_explicit_environment(tmp_path, monkeypatch):
    """A caller replaying a historical row can supply its own provenance, and
    the store must not silently relabel it with today's machine."""
    target = tmp_path / "results.json"
    target.write_text(json.dumps({"meta": {}, "rows": []}), encoding="utf-8")
    monkeypatch.setattr(store, "RESULTS", target)

    supplied = {"os": "Linux", "os_release": "x", "python": "3.12.10",
                "threads": 8}
    store.append_row({"arm": "replay", "seed": 1, "evidence_tag": "SIM",
                      "config_hash": "abc", "environment": supplied})

    rows = json.loads(target.read_text(encoding="utf-8"))["rows"]
    assert rows[0]["environment"] == supplied


def test_append_row_does_not_mutate_the_callers_dict(tmp_path, monkeypatch):
    """append_row copies before stamping. A caller that reuses a row template
    across writes must not accumulate this session's environment in it."""
    target = tmp_path / "results.json"
    target.write_text(json.dumps({"meta": {}, "rows": []}), encoding="utf-8")
    monkeypatch.setattr(store, "RESULTS", target)

    caller_row = {"arm": "test", "seed": 1, "evidence_tag": "SIM",
                  "config_hash": "abc"}
    store.append_row(caller_row)
    assert "environment" not in caller_row, (
        "append_row mutated the caller's dict")


def test_the_168_existing_rows_are_not_retrofitted():
    """Back-filling provenance that was never observed would be inventing it.

    This test is written to FAIL if someone adds `environment` to the historical
    rows, which is the opposite of how a schema test usually reads, and is
    deliberate: the amendment says the old rows stay as they are.
    """
    if not RESULTS.exists():
        pytest.skip("results.json not present")
    rows = json.loads(RESULTS.read_text(encoding="utf-8"))["rows"]
    stamped = [i for i, r in enumerate(rows) if "environment" in r]
    assert not stamped, (
        f"{len(stamped)} historical row(s) carry an environment field they "
        f"could not have observed (first at index {stamped[0]}). A33 says the "
        "existing rows are not retrofitted.")
