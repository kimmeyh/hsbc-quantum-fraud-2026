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
import platform
import sys
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


def environment() -> dict:
    """The execution environment of the row about to be written (A33, F84).

    WHY THIS EXISTS. Sprint 17 Task H measured the suite on Windows and Linux
    and found ZERO behavioral divergence, so this is not a fix for a known
    difference. It is provenance: of the 168 rows written before this change,
    not one records which operating system, interpreter or BLAS produced it.
    The submission's reproducibility claim rests on a lock file that pins 18
    package versions and, deliberately, no platform -- so a future reader
    comparing a regenerated figure against a stored one has no way to tell
    whether a difference is a real regression or a platform artifact.

    "We measured no divergence today" and "a row can prove where it ran" are
    different claims, and only the second survives contact with a machine that
    is not this one.

    Kept CHEAP and DEPENDENCY-FREE: this runs on every row write. BLAS is read
    through numpy when numpy is already imported and is skipped otherwise,
    because importing numpy inside the store to describe the environment would
    be a real cost on rows that never touch it.
    """
    env = {
        "os": platform.system(),
        "os_release": platform.release(),
        "python": platform.python_version(),
        "threads": os.cpu_count(),
    }
    # BLAS only if numpy is ALREADY loaded. No import side effect.
    #
    # THE FIRST VERSION RECORDED A NUMPY VERSION IN A FIELD NAMED `blas`.
    # It called np.__config__.get_info("blas_opt"), which was removed in numpy
    # 1.26 -- the version this repository PINS -- so the try block never ran
    # and the except branch was the live path on every platform. Every row
    # said blas: "numpy-1.26.4", and the test asserted only that the key was
    # present and truthy, so the degraded value passed.
    #
    # That defeats the point of A33. The amendment exists so a reader
    # comparing a regenerated figure against a stored one can tell a platform
    # artifact from a real change, and OpenBLAS versus MKL is the classic
    # cause of float-level divergence in this workload. Two rows both reading
    # "numpy-<version>" answer "same BLAS?" with a string that cannot.
    #
    # `__config__.CONFIG` carries the real identity on 1.26 (measured here:
    # openblas64 0.3.23.dev). numpy is recorded as its own field rather than
    # smuggled into this one. Found by the PR #122 review.
    np = sys.modules.get("numpy")
    if np is not None:
        env["numpy"] = str(getattr(np, "__version__", "unknown"))
        cfg = getattr(np, "__config__", None)
        blas = None
        try:
            config = getattr(cfg, "CONFIG", None)
            if isinstance(config, dict):
                b = config.get("Build Dependencies", {}).get("blas", {})
                name, ver = b.get("name"), b.get("version")
                if name:
                    blas = f"{name}-{ver}" if ver else str(name)
            if blas is None and hasattr(cfg, "get_info"):
                info = cfg.get_info("blas_opt")
                libs = info.get("libraries") if isinstance(info, dict) else None
                if libs:
                    blas = ",".join(libs)
        except (AttributeError, TypeError, KeyError, ValueError) as exc:
            blas = f"unavailable ({exc!r})"
        # "I could not determine it" is recorded AS THAT, never as a value
        # that reads like an answer.
        env["blas"] = blas or "unavailable (numpy exposes no BLAS identity)"
    return env


def append_row(row: dict) -> None:
    """Locked read-modify-append so parallel writers cannot lose rows (ADR-0008).

    Stamps `environment` on every NEW row (A33). Does not retrofit the 168
    rows written before the amendment, and must not: back-filling a field that
    was never observed would be inventing provenance, which is worse than
    recording its absence.
    """
    row = dict(row)
    row.setdefault("environment", environment())
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


# ---------------------------------------------------------------- predictions

PRED_DIR = RESULTS_DIR / "predictions"


def prediction_path(config_hash: str, seed, protocol: str = "stratified",
                    arm: str = "") -> Path:
    """One .npz per (arm, config_hash, seed, protocol).

    ARM IS PART OF THE KEY. Hardware and its exact proxy deliberately share a
    config_hash (they solve the identical Hamiltonian over the identical pool --
    that identity is what G0b and H4 rest on), so keying by hash alone made the
    proxy backfill silently OVERWRITE the hardware predictions, and a cost table
    then reported one vector under two evidence tags. Caught by adversarial
    review, Sprint 5."""
    prefix = f"{arm}_" if arm else ""
    return PRED_DIR / f"{prefix}{config_hash}_{protocol}_{seed}.npz"


def save_predictions(config_hash: str, seed, protocol: str,
                     y_val, p_val, y_test, p_test, arm: str = "") -> str:
    """Persist per-row scores so operating points, paired bootstraps, and the
    A7 sensitivity cells can be recomputed WITHOUT refitting (amendment A7).
    Returns the stored path, recorded on the row for traceability."""
    import numpy as np

    PRED_DIR.mkdir(parents=True, exist_ok=True)
    f = prediction_path(config_hash, seed, protocol, arm)
    tmp = f.with_suffix(f".{os.getpid()}.tmp.npz")
    np.savez_compressed(tmp,
                        y_val=np.asarray(y_val), p_val=np.asarray(p_val),
                        y_test=np.asarray(y_test), p_test=np.asarray(p_test))
    os.replace(tmp, f)
    return str(f.relative_to(RESULTS_DIR.parent.parent)) if f.is_absolute() else str(f)


def load_predictions(config_hash: str, seed, protocol: str = "stratified",
                     arm: str = ""):
    """(y_val, p_val, y_test, p_test) or None when not persisted."""
    import numpy as np

    f = prediction_path(config_hash, seed, protocol, arm)
    if not f.exists():
        return None
    z = np.load(f)
    return z["y_val"], z["p_val"], z["y_test"], z["p_test"]
