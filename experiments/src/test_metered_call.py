"""A metered call must always leave a recoverable handle. Verified by crashing it.

F47. The F46 probe spent an approved call and left no job id, so its runtime is
unrecoverable and "was the call spent?" could only be answered from the
allocation balance. These tests use a fake client to force every failure mode
and assert the handle survives each one.

ZERO metered seconds: no real client, no submission.
"""
from __future__ import annotations

import json

import pytest

import metered_call as mc


class FakeClient:
    """Drives every branch without touching the network."""

    def __init__(self, *, fail_at=None, balances=(3000, 2990)):
        self.fail_at = fail_at
        self._balances = list(balances)
        self.submitted = False

    def get_allocations(self):
        b = self._balances[0] if len(self._balances) == 1 else self._balances.pop(0)
        return {"allocations": {"dirac": {"seconds": b, "metered": True, "paid": True}}}

    def submit_job(self, *, job_body):
        if self.fail_at == "submit":
            raise RuntimeError("Number of variables '312' is greater than the free-tier device limit '100'")
        self.submitted = True
        return {"job_id": "6a9a049408442f441bbb6d1f"}

    def get_job_status(self, *, job_id):
        if self.fail_at == "wait":
            raise ConnectionError("connection reset")
        return {"status": "COMPLETED"}

    def get_job_results(self, *, job_id):
        return {"results": {"solutions": [[0.1, 0.9]]}}

    def get_job_metrics(self, *, job_id):
        return {"job_metrics": {"time_ns": {"device": {"dirac-3_normalized_qudit": {
            "samples": {"runtime": [int(0.49e9)] * 8, "preprocessing_time": int(0.15e9),
                        "start": 0, "end": int(4.8e9)}}}}}}


@pytest.fixture(autouse=True)
def isolate(tmp_path, monkeypatch):
    """Never touch the committed ledger or logs."""
    monkeypatch.setattr(mc, "LEDGER", tmp_path / "ledger.json")
    monkeypatch.setattr(mc, "LOG_DIR", tmp_path / "logs")
    return tmp_path


def _record(label="t"):
    return mc.CallRecord(label=label, degree=2, n_variables=105, n_samples=8,
                         expected_seconds="0-5s")


def test_the_job_id_is_on_disk_before_the_wait_begins(isolate):
    """The guarantee that matters: a kill during the wait still leaves a handle."""
    c = FakeClient()
    rec = _record()
    mc.run_metered(c, {"body": 1}, rec, poll_s=0)
    led = json.loads(mc.LEDGER.read_text(encoding="utf-8"))
    assert led["calls"][-1]["job_id"] == "6a9a049408442f441bbb6d1f"


def test_a_connection_loss_during_the_wait_keeps_the_handle(isolate):
    """The F46 failure mode, forced. The id must survive."""
    c = FakeClient(fail_at="wait")
    rec = _record("lost")
    with pytest.raises(ConnectionError):
        mc.run_metered(c, {"body": 1}, rec, poll_s=0)
    led = json.loads(mc.LEDGER.read_text(encoding="utf-8"))
    row = [r for r in led["calls"] if r["label"] == "lost"][-1]
    assert row["job_id"], "the job id was lost -- this is exactly F46's failure"
    assert row["status"] == "failed"
    assert row["measured_seconds"] == 10.0, "cost must still be measured from the balance"


def test_intent_is_recorded_before_any_spend(isolate):
    """A refused submission must still appear, so the attempt is visible."""
    c = FakeClient(fail_at="submit")
    rec = _record("refused")
    with pytest.raises(RuntimeError):
        mc.run_metered(c, {"body": 1}, rec, poll_s=0)
    led = json.loads(mc.LEDGER.read_text(encoding="utf-8"))
    row = [r for r in led["calls"] if r["label"] == "refused"][-1]
    assert row["status"] == "refused", "a sizing refusal should be labelled as such"
    assert row["balance_before"] == 3000


def test_cost_comes_from_the_balance_not_the_response(isolate):
    """The repr scrape produced 5.0 for a call that cost 10. Balance is truth."""
    c = FakeClient(balances=(3000, 2990))
    rec = _record()
    mc.run_metered(c, {"body": 1}, rec, poll_s=0)
    assert rec.measured_seconds == 10.0


def test_a_metrics_disagreement_is_recorded_not_silently_preferred(isolate):
    """The fake bills 4s by runtime but 10s by balance; the gap must be noted."""
    c = FakeClient(balances=(3000, 2990))
    rec = _record()
    mc.run_metered(c, {"body": 1}, rec, poll_s=0)
    assert any("differs from balance" in n for n in rec.notes), (
        "a disagreement between the derived and measured cost must be recorded")


def test_the_log_is_written_line_by_line(isolate):
    c = FakeClient()
    rec = _record()
    log = mc.UnbufferedLog(isolate / "logs" / "x.log")
    mc.run_metered(c, {"body": 1}, rec, poll_s=0, log=log)
    text = log.path.read_text(encoding="utf-8")
    assert "INTENT" in text and "SUBMITTED" in text and "DONE" in text
    assert "job_id=" in text


def test_object_id_decomposition_matches_the_real_campaign():
    """The parts we CAN read: constant random field, increasing counter."""
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "results" / "hw_job_ids.json"
    if not p.exists():
        pytest.skip("campaign ids absent")
    ids = sorted(json.loads(p.read_text(encoding="utf-8"))["job_ids"])
    parts = [mc.split_object_id(i) for i in ids]
    assert len({p["random_field"] for p in parts}) == 1, (
        "the random field is not constant within this campaign, so it cannot be "
        "carried across a block")
    counters = [p["counter"] for p in parts]
    assert counters == sorted(counters), "counters must increase"
    assert counters != list(range(counters[0], counters[0] + len(counters))), (
        "counters are contiguous here; the non-contiguity this code warns about "
        "no longer holds and the docstring needs revisiting")


def test_timestamps_vary_across_a_block_so_ids_are_not_enumerable():
    """Why exact reconstruction is impossible. This killed the first design."""
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "results" / "hw_job_ids.json"
    if not p.exists():
        pytest.skip("campaign ids absent")
    ids = sorted(json.loads(p.read_text(encoding="utf-8"))["job_ids"])
    epochs = {mc.split_object_id(i)["epoch"] for i in ids}
    assert len(epochs) > 1, (
        "all jobs share a timestamp, so a fixed-head reconstruction would work "
        "after all; revisit candidate_ids_at")


def test_candidates_cover_a_known_id_when_the_timestamp_is_known():
    """The forensic case: log kept the second, lost the id."""
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "results" / "hw_job_ids.json"
    if not p.exists():
        pytest.skip("campaign ids absent")
    ids = sorted(json.loads(p.read_text(encoding="utf-8"))["job_ids"])
    target = ids[5]
    parts = mc.split_object_id(target)
    cands = mc.candidate_ids_at(parts["random_field"], parts["counter"],
                                parts["epoch"], n_calls=1)
    assert target in cands


def test_split_rejects_a_non_object_id():
    with pytest.raises(ValueError):
        mc.split_object_id("nope")
