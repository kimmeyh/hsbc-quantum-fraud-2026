"""Shared results-store helpers (ADR-0008; amendment A4; PR #13 review findings).

One config-hash implementation and one atomic-append path for every writer
(run_classical, qubo_proxy, future hardware runner). Fixes from the Sprint 3
PR review: unique per-process temp names (two writers previously shared
results.tmp -- os.replace collision under parallel tracks) and a portable
lock file so concurrent read-modify-append cannot lose rows.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
RESULTS = RESULTS_DIR / "results.json"


def config_hash(payload: dict) -> str:
    """THE config hash: sha256 of the sorted-key JSON, 16 hex chars."""
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[:16]


def atomic_write_json(path: Path, obj) -> None:
    """Write via a per-process temp file + os.replace (never a shared temp name)."""
    tmp = path.with_suffix(f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(obj, indent=1))
    os.replace(tmp, path)


class _Lock:
    """Portable lock file (O_CREAT|O_EXCL), Windows + WSL. Blocks up to 30 s;
    a stale lock older than 60 s is broken (crashed holder)."""

    def __init__(self, path: Path):
        self.path = path.with_suffix(".lock")

    def __enter__(self):
        deadline = time.time() + 30
        while True:
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                return self
            except FileExistsError:
                try:
                    if time.time() - self.path.stat().st_mtime > 60:
                        self.path.unlink(missing_ok=True)
                        continue
                except OSError:
                    pass
                if time.time() > deadline:
                    raise TimeoutError(f"results-store lock held too long: {self.path}")
                time.sleep(0.2)

    def __exit__(self, *exc):
        try:
            self.path.unlink()
        except OSError:
            pass


def append_row(row: dict) -> None:
    """Locked read-modify-append so parallel writers cannot lose rows (ADR-0008)."""
    with _Lock(RESULTS):
        store = (json.loads(RESULTS.read_text())
                 if RESULTS.exists() else {"meta": {}, "rows": []})
        store["rows"].append(row)
        atomic_write_json(RESULTS, store)


def update_meta(**kv) -> None:
    with _Lock(RESULTS):
        store = (json.loads(RESULTS.read_text())
                 if RESULTS.exists() else {"meta": {}, "rows": []})
        store["meta"].update(kv)
        atomic_write_json(RESULTS, store)
