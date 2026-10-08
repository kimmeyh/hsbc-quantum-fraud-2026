"""One metered eqc-models fit, and its zero-spend twin. Shared by B4 and B5.

WHY THIS FILE EXISTS (Sprint 21). The first B4 and B5 runners hand-built the
job body sent to QCi, with field names that were invented rather than read
from anywhere. QCi rejected the one that reached it: "400 Bad Request: Must
specify one and only one job under the job_submission.problem_config field".
Every block that has ever run on Dirac-3 in this repository -- B1, G0b, B2, B3
-- submitted through `eqc_models` instead, and `run_hardware_b3._submit_via_eqc`
says why in its docstring: "Hand-constructing a job body here would be a
reimplementation that can drift, which is exactly what [ADR-0002] rejects."

So the library builds and submits the request. This module only wraps it in
the ledger discipline the earlier runners established, and provides an
offline stand-in for the one network object, so a dry run exercises every
line a real run executes except the HTTP call.

The earlier dry run stopped BEFORE the request was built, which is why it
never caught the fabricated body. A dry run that skips the part the vendor
reads is not a dry run of the submission.
"""
from __future__ import annotations

import time
from contextlib import contextmanager

import numpy as np

import metered_call as mc
from run_hardware_b3 import _find_job_id      # reused, not rewritten

def to_jsonable(obj):
    """A device response as JSON-safe data, IN FULL.

    WHY (Sprint 22). The B4 and B5 runners saved responses with
    `json.dumps(resp, default=str)`. A real solve returns a `SolutionResults`
    dataclass, not a dict, so `default=str` stored its PRINTED form -- and
    numpy truncates long arrays when printing. Every 560- and 816-value B4
    sample was saved as its first and last three values. The full samples
    were recovered by job id (experiments/phase2/src/recover_device_samples.py).
    """
    import dataclasses

    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: to_jsonable(getattr(obj, f.name))
                for f in dataclasses.fields(obj)}
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.floating, np.integer, np.bool_)):
        return obj.item()
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(v) for v in obj]
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    return f"<unserializable {type(obj).__name__}>"


def samples_of(resp) -> list:
    """Every returned sample, from a SolutionResults or a cloud-shaped dict."""
    sols = getattr(resp, "solutions", None)
    if sols is None and isinstance(resp, dict):
        sols = (resp.get("results") or {}).get("solutions")
    return [] if sols is None else [list(map(float, s)) for s in np.asarray(sols)]


MAX_RETRIES = 2                 # PREREGISTRATION section 11: at most twice
UNPARSEABLE_CALL_CHARGE_S = 10.0  # run_hardware.py's conservative charge


def _balance_or_none(client):
    try:
        return mc.balance(client)
    except Exception:                                  # noqa: BLE001
        return None


def metered_fit(make_clf, X, y, make_record, client) -> dict:
    """Fit through eqc-models with the B3 ledger discipline, retrying at most
    twice with identical config (section 11).

    Intent is on disk BEFORE each call; cost is the allocation balance before
    minus after, never a vendor field we would have to parse. An unreadable
    balance is charged the conservative estimate and flagged, never counted
    as zero -- a blind spend counter is how a block cap fails to fire (A8).

    Returns {"clf", "resp", "attempts", "metered_seconds", "parsed", "error",
    "job_id"}; "clf" and "resp" are None if every attempt failed.
    """
    attempts, spent, parsed, err = 0, 0.0, True, None
    while attempts <= MAX_RETRIES:
        clf = make_clf()
        rec = make_record(attempts)
        rec.submitted_utc = mc._utc()
        rec.balance_before = _balance_or_none(client)
        log = mc.UnbufferedLog(
            mc.LOG_DIR / f"{rec.label}_{time.strftime('%Y%m%dT%H%M%S')}.log")
        log.write(f"INTENT {rec.label} vars={rec.n_variables} "
                  f"samples={rec.n_samples} expected={rec.expected_seconds} "
                  f"balance={rec.balance_before} attempt={attempts + 1}")
        mc.append_ledger(rec)

        resp = None
        try:
            resp = clf.fit(X, y)                 # ONE metered call
            rec.job_id = _find_job_id(resp)
            rec.status = "ok"
            log.write(f"OK job_id={rec.job_id}")
        except Exception as e:                   # noqa: BLE001
            rec.status = "failed"
            rec.error = f"{type(e).__name__}: {str(e)[:400]}"
            err = rec.error
            log.write(f"FAILED {rec.error}")
        finally:
            rec.balance_after = _balance_or_none(client)
            if rec.balance_before is not None and rec.balance_after is not None:
                rec.measured_seconds = float(rec.balance_before - rec.balance_after)
                rec.cost_source = "allocation balance before minus after"
            else:
                rec.measured_seconds = UNPARSEABLE_CALL_CHARGE_S
                rec.cost_source = ("estimated: balance unreadable, conservative "
                                   "charge applied")
                parsed = False
            spent += rec.measured_seconds
            rec.finished_utc = mc._utc()
            log.write(f"BALANCE after={rec.balance_after} "
                      f"cost={rec.measured_seconds}")
            mc.append_ledger(rec)

        attempts += 1
        if resp is not None:
            return {"clf": clf, "resp": resp, "attempts": attempts,
                    "metered_seconds": spent, "parsed": parsed,
                    "error": None, "job_id": rec.job_id}
        low = (err or "").lower()
        if "variable" in low and "limit" in low:
            break                                 # sizing refusal: no retry
        time.sleep(5)

    return {"clf": None, "resp": None, "attempts": attempts,
            "metered_seconds": spent, "parsed": parsed, "error": err,
            "job_id": None}


@contextmanager
def offline_solver(record: list):
    """Replace the ONE network object with a local stand-in.

    Everything else runs for real: the library builds the weak-learner pool,
    the Hamiltonian, the sum constraint and the solver arguments exactly as it
    would for Dirac-3, and hands them to `solver.solve(model, ...)`. This
    stand-in validates what it was handed, records it, and returns a response
    in the cloud schema, so `fit`, `predict_raw` and the scoring after them all
    execute. Nothing leaves the machine.

    `record` receives one dict per solve: the variable count, the solver
    arguments and the Hamiltonian's dynamic range in dB -- which is what the
    Criterion H statement quotes, measured rather than assumed.
    """
    import eqc_models.ml.classifierbase as cb

    real = cb.Dirac3CloudSolver

    class _OfflineClient:
        """from_cloud_response asks the client for job metrics (a network
        read). An empty answer takes the library's own KeyError path: no
        timing, everything else intact."""
        def get_job_metrics(self, job_id=None):
            return {}

    class OfflineSolver:
        client = _OfflineClient()

        def connect(self, *args, **kwargs):
            pass

        def solve(self, model, **kw):
            C = np.asarray(model._C, dtype=np.float64).reshape(-1)
            J = np.asarray(model._J, dtype=np.float64)
            n = C.shape[0]
            assert J.shape == (n, n), f"J is {J.shape}, C has {n}"
            assert np.isfinite(J).all() and np.isfinite(C).all(), \
                "non-finite Hamiltonian"
            try:
                dr = float(model.get_dynamic_range())
            except Exception:                    # noqa: BLE001
                dr = None
            ns = int(kw.get("num_samples", 1))
            record.append({
                "n_variables": n,
                "num_samples": ns,
                "relaxation_schedule": kw.get("relaxation_schedule"),
                "sum_constraint": kw.get("sum_constraint"),
                "dynamic_range_db": dr,
            })
            rng = np.random.default_rng(0)
            s = float(kw.get("sum_constraint", 1.0))
            sols = [list(rng.dirichlet(np.ones(n)) * s) for _ in range(ns)]
            # Return what the REAL solver returns: a SolutionResults built by
            # the same from_cloud_response call Dirac3CloudSolver.makeResults
            # uses. The first version returned a plain dict, so every dry run
            # exercised a response shape a real run never produces -- which
            # is how the truncated-sample bug reached the device unseen.
            # No fallback to the dict: a dry run that cannot build the real
            # type must fail, not quietly diverge from a real run again.
            from eqc_models.base.results import SolutionResults
            raw = {"results": {"energies": [0.0] * ns, "solutions": sols,
                               "counts": [1] * ns},
                   "job_info": {"job_id": "0" * 24, "job_submission": {
                       "device_config": {"dirac-3": {
                           "num_samples": ns,
                           "relaxation_schedule": kw.get("relaxation_schedule"),
                           "sum_constraint": s}}}}}
            return SolutionResults.from_cloud_response(model, raw, self)

    cb.Dirac3CloudSolver = OfflineSolver
    try:
        yield
    finally:
        cb.Dirac3CloudSolver = real
