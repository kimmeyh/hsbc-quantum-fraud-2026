"""Query a Dirac-3 job by id: status, metrics, results. ZERO metered seconds.

All four QciClient endpoints used here (`get_job_status`, `get_job_metrics`,
`get_job_results`, `get_job_response`) take only a job_id and perform a read.
They submit nothing, so they consume no QPU time and need no Criterion H
approval -- verified against the client signatures before writing this.

WHY THIS EXISTS. The F46 probe's first attempt died leaving no artifact, and
whether the one approved metered call had been spent was unanswerable from the
repository; only an allocation-balance query settled it. A job id turns a lost
connection from a lost call into a re-read: the device keeps the result, and
this fetches it afterwards.

That is the retrieval half of F47 (#68). The capture half -- recording the id at
submission, before waiting -- still needs doing inside the runners, and is the
part that makes this tool reliably usable rather than usable when we happen to
have an id.

Usage:
    python experiments/src/job_query.py <job_id> [<job_id> ...]
    python experiments/src/job_query.py --known      # ids already in the store
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
RESULTS = REPO / "experiments" / "results"


def _load_env() -> None:
    p = REPO / ".env"
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def _client():
    from qci_client import QciClient
    url, token = os.environ.get("QCI_API_URL"), os.environ.get("QCI_TOKEN")
    if not (url and token):
        raise SystemExit("QCI_API_URL and QCI_TOKEN must both be set (ADR-0011).")
    return QciClient(api_token=token, url=url)


def known_job_ids() -> list[str]:
    """Ids already retained in the store, so a lookup needs no copy-paste."""
    p = RESULTS / "hw_job_ids.json"
    if not p.exists():
        return []
    d = json.loads(p.read_text(encoding="utf-8"))
    ids = d.get("job_ids", d if isinstance(d, list) else [])
    return [str(i) for i in ids]


def query(client, job_id: str) -> dict:
    """Best-effort read of everything the API will say about one job.

    Each endpoint is tried independently: a job that is still queued has a
    status but no results, and that is a useful answer rather than an error.
    """
    out: dict[str, object] = {"job_id": job_id}
    for name in ("get_job_status", "get_job_metrics", "get_job_results"):
        try:
            out[name.replace("get_job_", "")] = getattr(client, name)(job_id=job_id)
        except Exception as e:                      # noqa: BLE001
            out[name.replace("get_job_", "")] = {"error": f"{type(e).__name__}: {str(e)[:200]}"}
    return out


def _summarise(rec: dict) -> str:
    st = rec.get("status")
    if isinstance(st, dict) and "error" not in st:
        for key in ("status", "job_status", "state"):
            if key in st:
                return str(st[key])
        return json.dumps(st)[:80]
    return "unreadable"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("job_ids", nargs="*", help="job ids to query")
    ap.add_argument("--known", action="store_true",
                    help="query every id retained in hw_job_ids.json")
    ap.add_argument("--json", action="store_true", help="dump the full records")
    args = ap.parse_args()

    ids = list(args.job_ids)
    if args.known:
        ids += known_job_ids()
    if not ids:
        ap.error("give at least one job id, or --known")

    _load_env()
    client = _client()

    records = []
    for jid in ids:
        rec = query(client, jid)
        records.append(rec)
        print(f"{jid}  {_summarise(rec)}")

    if args.json:
        print()
        print(json.dumps(records, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
