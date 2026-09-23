"""Is CI green on the commit we are about to hand over?

Sprint 18 ran red on EVERY commit, start to finish, and nobody looked. The
cause was not in the sprint's work: three tests in `test_phase3_artifacts.py`
sent a Stop hook a payload with no `branch_override`, so the hook read the
live branch name -- a name in a normal clone, EMPTY on the detached HEAD that
`actions/checkout` leaves behind. The hook's first gate is "sprint feature
branch only", so on CI it returned ALLOW before reaching any artifact check,
and those three tests failed there while passing locally on every run.

Two failures, not one, and the second is the one this script exists for:

  1. A test that could not fail locally. Local green was never evidence.
  2. A red check sat on the PR through an entire review round without being
     opened. The reviews were read; the check status was not.

WHY A SCRIPT AND NOT ONLY A HOOK. The hook fires on a close-out CLAIM, which
is once, at the end. CI goes red during execution, and the gap between cause
and discovery is where the cost is. This runs on demand in Phase 4 and as a
gate in Phase 5, and the hook calls the same code so the two cannot disagree.

FAILS CLOSED, DELIBERATELY. `gh` can be missing, unauthenticated, rate-limited
or offline, and a run can be queued rather than finished. None of those is
"green". Each returns a distinct exit code and says what could not be
determined, because the defect class this repository keeps paying for is a
check that reports success when it checked nothing.

Exit codes:
    0  every check on the commit passed
    1  at least one check FAILED
    2  could not determine (gh missing, not authenticated, no run yet, ...)
    3  checks are still running

Usage:
    python scripts/check_ci_status.py
    python scripts/check_ci_status.py --sha HEAD
    python scripts/check_ci_status.py --wait        # block until conclusive
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OK = 0
FAILED = 1
UNKNOWN = 2
PENDING = 3


class Undetermined(RuntimeError):
    """The state could not be read. NOT the same as green.

    Every path that cannot answer the question raises this rather than
    returning a default, so a caller cannot mistake silence for success.
    """


def _run(args: list[str], timeout: int = 60) -> tuple[int, str, str]:
    try:
        r = subprocess.run(args, cwd=str(ROOT), capture_output=True,
                           text=True, timeout=timeout)
    except FileNotFoundError as exc:
        raise Undetermined(f"{args[0]} is not installed: {exc}") from exc
    except subprocess.TimeoutExpired as exc:
        raise Undetermined(f"{args[0]} timed out after {timeout}s") from exc
    return r.returncode, r.stdout, r.stderr


def head_sha(ref: str = "HEAD") -> str:
    rc, out, err = _run(["git", "rev-parse", ref])
    if rc != 0 or not out.strip():
        raise Undetermined(f"cannot resolve {ref}: {err.strip() or 'no output'}")
    return out.strip()


def _require_gh() -> None:
    if shutil.which("gh") is None:
        raise Undetermined(
            "the GitHub CLI (gh) is not on PATH, so CI status cannot be read")
    rc, _out, err = _run(["gh", "auth", "status"])
    if rc != 0:
        raise Undetermined(
            f"gh is not authenticated: {err.strip()[:200] or 'auth status failed'}")


def runs_for(sha: str) -> list[dict]:
    """Workflow runs whose head commit is exactly this sha."""
    _require_gh()
    rc, out, err = _run([
        "gh", "run", "list", "--limit", "40",
        "--json", "databaseId,headSha,status,conclusion,name,url",
    ])
    if rc != 0:
        raise Undetermined(f"gh run list failed: {err.strip()[:200]}")
    try:
        allruns = json.loads(out or "[]")
    except ValueError as exc:
        raise Undetermined(f"gh returned unparseable JSON: {exc}") from exc
    return [r for r in allruns if r.get("headSha") == sha]


def evaluate(sha: str) -> tuple[int, list[str]]:
    """(exit code, human-readable lines). Never returns OK on a guess."""
    runs = runs_for(sha)
    if not runs:
        raise Undetermined(
            f"no workflow run exists for {sha[:7]}. It may not have been "
            "pushed, or CI may not have started yet. That is not a pass.")

    lines = []
    failed, pending = [], []
    for r in runs:
        name = r.get("name") or "?"
        status = r.get("status") or "?"
        concl = r.get("conclusion") or ""
        lines.append(f"  {name}: {status} {concl}".rstrip())
        if status != "completed":
            pending.append(name)
        elif concl not in ("success", "skipped", "neutral"):
            failed.append(f"{name} ({concl}) {r.get('url', '')}".strip())

    if failed:
        lines.append("")
        lines.append(f"CI is RED on {sha[:7]}:")
        lines.extend(f"  {f}" for f in failed)
        lines.append("")
        lines.append("Open the failing run BEFORE continuing. A red check that "
                     "predates this sprint's work is still a red check, and "
                     "Sprint 18 shipped an entire review round under one.")
        return FAILED, lines
    if pending:
        lines.append("")
        lines.append(f"CI is still running on {sha[:7]}: "
                     + ", ".join(pending))
        lines.append("Not a pass. Wait for it, or re-run with --wait.")
        return PENDING, lines

    lines.append("")
    lines.append(f"CI is green on {sha[:7]} ({len(runs)} run(s)).")
    return OK, lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sha", default="HEAD",
                    help="commit to check (default: HEAD)")
    ap.add_argument("--wait", action="store_true",
                    help="poll until the runs are conclusive")
    ap.add_argument("--after", type=int, default=0, metavar="SECONDS",
                    help="sleep first, so a just-created PR has time to FAIL. "
                         "A check run the instant a PR opens finds no run at "
                         "all, which is indistinguishable from a clean one.")
    ap.add_argument("--timeout", type=int, default=1800,
                    help="seconds to wait with --wait (default 1800)")
    args = ap.parse_args(argv)

    if args.after > 0:
        # Give CI time to start AND to fail. The point of this checkpoint is
        # an early red, so checking before the run exists is worse than not
        # checking: "no run yet" reads like nothing is wrong.
        print(f"waiting {args.after}s for CI to start and report ...")
        time.sleep(args.after)

    try:
        sha = head_sha(args.sha)
        deadline = time.time() + args.timeout
        while True:
            rc, lines = evaluate(sha)
            if rc != PENDING or not args.wait or time.time() > deadline:
                break
            time.sleep(30)
    except Undetermined as exc:
        print(f"CI STATUS UNDETERMINED: {exc}")
        print()
        print("This is NOT a pass. Nothing was checked, so nothing can be")
        print("concluded about whether CI is green.")
        return UNKNOWN

    print("\n".join(lines))
    return rc


if __name__ == "__main__":
    sys.exit(main())
