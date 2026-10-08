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

B2 (added at Sprint 22 Manual Validation, team lead decision D8): the 11
B2 responses carry the same truncated print. The B2 rows in results.json hold
no job id, but each stored response's printed form does. `--block B2` reads
the job id out of each `pools/hw_responses/hw_b2_full_*.json` (a read of the
file; the file is not changed) and recovers it the same way.

Usage: recover_device_samples.py            (B4 and B5, from results.json)
       recover_device_samples.py --block B2 (B2, job ids from the responses)

Output: experiments/phase2/results/device_samples/<label>.json
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments" / "src"))
import metered_call as mc                     # noqa: E402  (Phase 1, read-only)

OUT = ROOT / "experiments" / "phase2" / "results" / "device_samples"
HW_RESPONSES = ROOT / "experiments" / "results" / "pools" / "hw_responses"
B2_VARS = 833
_JOB_ID = re.compile(r"job_id': '([0-9a-f]{24})'")


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


def b45_targets(rows) -> list[dict]:
    """B4/B5: every row of the block that carries a job id."""
    return [{"label": (f"{r['block'].lower()}_"
                       f"{r['dataset'].replace('spectra_', '')}"
                       f"_{r.get('protocol')}_{r['seed']}"),
             "block": r["block"], "dataset": r["dataset"], "seed": r["seed"],
             "protocol": r["protocol"], "job_id": r["job_id"],
             "n_expected": r.get("n_vars_expected") or r.get("n_variables")}
            for r in rows if r.get("block") in ("B4", "B5") and r.get("job_id")]


def b2_targets() -> list[dict]:
    """B2: one target per stored response file. The file name gives the
    protocol and seed (the temporal row's seed is None in results.json, its
    file says 42), and the printed response gives the job id. Exactly one id
    per file, or the run refuses: a guessed id would fetch another job."""
    out = []
    for f in sorted(HW_RESPONSES.glob("hw_b2_full_*.json")):
        protocol, seed = f.stem.removeprefix("hw_b2_full_").rsplit("_", 1)
        ids = sorted(set(_JOB_ID.findall(f.read_text(encoding="utf-8"))))
        if len(ids) != 1:
            raise SystemExit(f"REFUSING: {f.name} holds {len(ids)} job ids")
        out.append({"label": f"b2_ulb_{protocol}_{seed}", "block": "B2",
                    "dataset": "ulb", "seed": int(seed), "protocol": protocol,
                    "job_id": ids[0], "n_expected": B2_VARS})
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    block = argv[1] if argv[:1] == ["--block"] and len(argv) > 1 else None
    if argv and block != "B2":
        print("usage: recover_device_samples.py [--block B2]")
        return 3
    if "PYTEST_CURRENT_TEST" in os.environ or "pytest" in sys.modules:
        print("REFUSING: network fetch from a test process.")
        return 5
    _load_env()
    import requests
    from qci_client import QciClient
    client = QciClient(api_token=os.environ["QCI_TOKEN"],
                       url=os.environ["QCI_API_URL"])
    rows = json.loads((ROOT / "experiments" / "results" / "results.json")
                      .read_text(encoding="utf-8"))["rows"]
    targets = b2_targets() if block == "B2" else b45_targets(rows)
    bal_before = mc.balance(client)
    OUT.mkdir(parents=True, exist_ok=True)
    report = []
    for r in targets:
        label = r["label"]
        try:
            res = client.get_job_results(job_id=r["job_id"])
        except requests.HTTPError as exc:
            # No file is written: an absent sample is recorded as absent,
            # never reconstructed. B2's 11 jobs all returned 404 on
            # 2026-10-07 (job not found), so B2 is not recoverable.
            report.append((label, 0, None, False))
            print(f"  {label:40s} NOT RECOVERED: {str(exc)[-60:]}", flush=True)
            continue
        sols = _find(res, "solutions")
        energies = _find(res, "energies")
        n_expected = r["n_expected"]
        ok = (isinstance(sols, list) and sols
              and all(len(s) == n_expected for s in sols))
        (OUT / f"{label}.json").write_text(json.dumps({
            "block": r["block"], "dataset": r["dataset"], "seed": r["seed"],
            "protocol": r["protocol"], "job_id": r["job_id"],
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
