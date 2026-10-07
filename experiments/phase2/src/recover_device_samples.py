"""Recover B4/B5's full device samples by job id. A READ: zero metered seconds.

WHY. The B4 and B5 runners (Sprint 21) saved each device response with
`json.dumps(resp, default=str)`. The library's response is a `SolutionResults`
object, not a dict, so `default=str` stored its PRINTED form -- and numpy
truncates long arrays when printing. Each 560- or 816-value sample was saved as
its first three and last three values. F90's acceptance ("every returned
sample stored") was therefore not met, though every scored metric was computed
from the in-memory fit and is unaffected.

The device keeps the result, and every job id was retained. This fetches each
job's results with `QciClient.get_job_results` -- one of the three read-only
endpoints `experiments/src/job_query.py` already uses for the same purpose --
and stores them as real JSON lists in the Phase 2 store. Sprint 21's files in
`experiments/results/pools/hw_responses/` are Phase 1 evidence and are left
exactly as they are (`docs/PHASE_SEPARATION.md`).

The allocation balance is read before and after; the run fails if it moved.

Output: experiments/phase2/results/device_samples/<label>.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments" / "src"))
import metered_call as mc                     # noqa: E402  (Phase 1, read-only)

OUT = ROOT / "experiments" / "phase2" / "results" / "device_samples"


def _load_env() -> None:
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def _find(obj, key):
    """First value under `key` anywhere in a nested dict/list."""
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            found = _find(v, key)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = _find(v, key)
            if found is not None:
                return found
    return None


def main() -> int:
    if "PYTEST_CURRENT_TEST" in os.environ or "pytest" in sys.modules:
        print("REFUSING: network fetch from a test process.")
        return 5
    _load_env()
    from qci_client import QciClient
    client = QciClient(api_token=os.environ["QCI_TOKEN"],
                       url=os.environ["QCI_API_URL"])
    rows = json.loads((ROOT / "experiments" / "results" / "results.json")
                      .read_text(encoding="utf-8"))["rows"]
    targets = [r for r in rows if r.get("block") in ("B4", "B5")
               and r.get("job_id")]
    bal_before = mc.balance(client)
    OUT.mkdir(parents=True, exist_ok=True)
    report = []
    for r in targets:
        label = (f"{r['block'].lower()}_{r['dataset'].replace('spectra_', '')}"
                 f"_{r.get('protocol')}_{r['seed']}")
        res = client.get_job_results(job_id=r["job_id"])
        sols = _find(res, "solutions")
        energies = _find(res, "energies")
        n_expected = r.get("n_vars_expected") or r.get("n_variables")
        ok = (isinstance(sols, list) and sols
              and all(len(s) == n_expected for s in sols))
        (OUT / f"{label}.json").write_text(json.dumps({
            "block": r["block"], "dataset": r["dataset"], "seed": r["seed"],
            "protocol": r.get("protocol"), "job_id": r["job_id"],
            "n_vars_expected": n_expected,
            "solutions": sols, "energies": energies,
            "source": "QciClient.get_job_results (read)"}, indent=1),
            encoding="utf-8")
        report.append((label, len(sols) if isinstance(sols, list) else 0,
                       len(sols[0]) if ok else None, ok))
        print(f"  {label:40s} samples={report[-1][1]} width={report[-1][2]} "
              f"{'OK' if ok else 'INCOMPLETE'}", flush=True)
    bal_after = mc.balance(client)
    print(f"\n  balance before {bal_before} s, after {bal_after} s")
    if bal_before != bal_after:
        print("  FAIL: the balance moved during a read-only recovery")
        return 2
    bad = [x for x in report if not x[3]]
    print(f"  {len(report) - len(bad)} of {len(report)} recovered complete")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
