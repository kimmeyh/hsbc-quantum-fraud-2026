"""job_query.py must stay a READ-ONLY tool.

The tool exists so a lost connection becomes a re-read instead of a lost metered
call. That value depends on it never submitting anything: a "retrieval" helper
that could bill would be worse than no helper, because it would be used freely.

These tests are offline. They assert the shape of the tool, not the API's
behaviour, so they run in CI without credentials.
"""
from __future__ import annotations

import inspect
from pathlib import Path

import job_query


def test_only_read_endpoints_are_called():
    """No submit/solve/fit call may appear in the module."""
    # Strip docstrings before scanning: prose legitimately contains words like
    # "resolve", and a guard that fails on its own documentation gets deleted.
    import ast
    tree = ast.parse(inspect.getsource(job_query))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)):
            d = ast.get_docstring(node, clean=False)
            if d and node.body and isinstance(node.body[0], ast.Expr):
                node.body[0].value = ast.Constant(value="")
    src = ast.unparse(tree)
    for forbidden in ("submit_job", "process_job", ".fit(", ".solve("):
        assert forbidden not in src, (
            f"job_query calls {forbidden!r}. This tool must never submit work: "
            f"it exists to retrieve results already paid for.")


def test_queries_exactly_the_documented_read_endpoints():
    src = inspect.getsource(job_query.query)
    for expected in ("get_job_status", "get_job_metrics", "get_job_results"):
        assert expected in src, f"{expected} no longer queried"


def test_a_failing_endpoint_does_not_abort_the_others():
    """A queued job has a status but no results; that is an answer, not an error."""
    class Stub:
        def get_job_status(self, *, job_id):
            return {"status": "RUNNING"}

        def get_job_metrics(self, *, job_id):
            raise RuntimeError("not ready")

        def get_job_results(self, *, job_id):
            raise RuntimeError("not ready")

    rec = job_query.query(Stub(), "abc123")
    assert rec["status"] == {"status": "RUNNING"}
    assert "error" in rec["metrics"], "a failed endpoint must be recorded, not raised"
    assert "error" in rec["results"]


def test_known_job_ids_reads_the_retained_store():
    """--known must find the ids the campaign already retained."""
    ids = job_query.known_job_ids()
    store = Path(__file__).resolve().parents[1] / "results" / "hw_job_ids.json"
    if store.exists():
        assert len(ids) >= 27, (
            f"only {len(ids)} job ids found; the campaign retained 27 and they are "
            f"what makes past results re-readable")
        assert all(isinstance(i, str) and i for i in ids)
