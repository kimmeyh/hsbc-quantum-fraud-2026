"""Wait for the team lead's Dirac-3 window, then run B5, then B4.

Sprint 21. The team lead approved both blocks on 2026-10-05 ("both qci runs
are approved - no need to ask again this sprint") and on 2026-10-06 set the
window to 07:30 Eastern and chose option 1: fix the runners, then run B5 and B4.

B4 starts ONLY if B5 exits 0. B5 is the cheap block (12 fits, ~15 s) and lands
a fresh per-fit measurement on the same submission path B4 uses, so a B5
failure is exactly the signal that B4 should not spend ~250-680 s.

This script submits nothing itself. Every guard lives in the runners and is
re-checked there: the window, the test-process refusal, the allocation floor,
the block cap, idempotency against results.json, and the ledger written before
each call.

Run:
  <venv python> scripts/run_b5_then_b4.py
"""
from __future__ import annotations

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "experiments" / "src"
LOG = ROOT / "experiments" / "results" / "call_logs" / "b5_then_b4_launcher.log"
WINDOW_START = datetime(2026, 10, 6, 7, 30)


def say(msg: str) -> None:
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S}  {msg}"
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_block(script: str) -> int:
    say(f"START {script}")
    with LOG.open("a", encoding="utf-8") as f:
        r = subprocess.run([sys.executable, str(SRC / script)],
                           cwd=str(ROOT), stdout=f, stderr=subprocess.STDOUT)
    say(f"END {script} exit={r.returncode}")
    return r.returncode


def main() -> int:
    say(f"launcher armed; window opens {WINDOW_START:%Y-%m-%d %H:%M} local")
    while datetime.now() < WINDOW_START:
        time.sleep(30)
    say("window open")

    rc5 = run_block("run_hardware_b5.py")
    if rc5 != 0:
        say(f"B5 exited {rc5}; B4 NOT started. B4 runs only on a clean B5.")
        return rc5

    rc4 = run_block("run_hardware_b4.py")
    say(f"launcher done: B5 exit 0, B4 exit {rc4}")
    return rc4


if __name__ == "__main__":
    raise SystemExit(main())
