"""Build the committed fixture the A20 mechanism guard runs against (F67).

WHY A FIXTURE AND NOT THE POOLS. `test_pool_mechanism.py` was the suite's only
skip, because the pool `.npz` files are gitignored, so on a fresh clone it
silently did not run. The claim it guards -- 80 to 84 of the 91 learners
reproduce the training fold exactly, and zero predict the negative class
everywhere (A20) -- is published in appendix A.4 and was TRUE but UNGUARDED for
any reader who cloned the repository.

Appendix C promises that every figure REGENERATES from this repository rather
than shipping pre-computed, so committing the full pools would sit awkwardly
with the claim the repository makes about itself. A fixture is different in
kind: it is not evidence, it is the input a guard needs to detect drift.

WHAT IT COSTS, measured rather than guessed:

    full pools, as-is           2.38 MB
    H_tr + y_tr01 compressed    1.42 MB
    int8 signs compressed       0.83 MB   <- this file

The three per-pool tests read `H_tr` and `y_tr01` and nothing else, and they
only ever compare SIGNS. Every H_tr holds exactly {-1.0, +1.0} on all ten
pools -- asserted below, not assumed -- so int8 is LOSSLESS for this purpose.
The fixture reproduces the same assertions as the full pools.

WHAT THIS FIXTURE IS NOT. It is not a substitute for the pools in any analysis.
It carries no validation or test split, no feature names, and no float
precision. Rebuild the real pools with `scripts/wsl_build_pools.sh` for
anything except this guard.

Regenerate:  python experiments/src/build_pool_fixture.py
"""
from __future__ import annotations

import glob
from pathlib import Path

import numpy as np

RESULTS = Path(__file__).resolve().parents[1] / "results"
POOLS = sorted(glob.glob(str(RESULTS / "pools" / "h_*_free_dct_full.npz")))
OUT = RESULTS / "pool_mechanism_fixture.npz"


def main() -> int:
    if not POOLS:
        print("no pools on disk; nothing to build. Run scripts/wsl_build_pools.sh first.")
        return 1

    payload: dict[str, np.ndarray] = {}
    for path in POOLS:
        seed = Path(path).stem.split("_")[1]
        d = np.load(path)
        H = d["H_tr"]

        # Assert the lossless precondition rather than trusting it. If a future
        # pool ever carries anything but +/-1 votes, this fixture would quietly
        # misrepresent it and the guard would assert against a distortion.
        uniq = set(np.unique(H).tolist())
        if not uniq <= {-1.0, 1.0}:
            raise SystemExit(
                f"{path}: H_tr holds {sorted(uniq)[:6]}, not only -1 and +1. "
                "int8 is no longer lossless; rebuild this fixture differently "
                "rather than shipping a distorted one.")

        payload[f"H_{seed}"] = H.astype(np.int8)
        payload[f"y_{seed}"] = np.where(d["y_tr01"] == 1, 1, -1).astype(np.int8)

    np.savez_compressed(OUT, **payload)
    size = OUT.stat().st_size
    print(f"wrote {OUT.name}: {len(POOLS)} pools, {size/1e6:.2f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
