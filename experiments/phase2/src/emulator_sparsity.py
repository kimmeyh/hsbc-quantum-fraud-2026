"""F17's own acceptance test: does the emulator reproduce the device's SPARSITY?

Sprint 22 Task D, added at Manual Validation preparation. The F17 card's
build acceptance is "reproduces the B2 sparsity pattern on the frozen pools":
exact zeros, with nonzero weights from 0.0007 to 0.0029, all below the
resolvable step. That test cannot run as written:

  - the 833-variable B2 pools were never stored (experiments/results/pools/
    holds only the 377-variable deep and the mid pools), and
  - the stored B2 device responses carry the same truncated print as B4's
    (Sprint 22 sample-storage defect), so B2's samples are not on disk.

The SAME mechanism is testable on B4, where every device sample was
recovered in full (experiments/phase2/results/device_samples/). Per cell,
this compares three weight vectors' sparsity statistics:

  device    the lowest-energy recovered sample (on the device's own pool)
  exact     the proxy optimum on a rebuilt pool
  emulated  the emulator's lowest-energy sample at the calibrated budget (25)

The rebuilt pool is not the device's pool (random tree tie-breaks), so the
comparison is of distributions -- zero fraction, nonzero range -- never of
weights index by index.

Zero metered seconds. Output: experiments/phase2/results/f17_emulator_sparsity.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments" / "src"))
sys.path.insert(0, str(ROOT / "experiments" / "phase2" / "src"))
import qubo_proxy as qp                           # noqa: E402  (Phase 1, read-only)
import spectra_segment as ss                      # noqa: E402  (Phase 1, read-only)
import dirac3_emulator as em                      # noqa: E402

BUDGET = 25
OUT = ROOT / "experiments" / "phase2" / "results" / "f17_emulator_sparsity.json"


def sparsity(w) -> dict:
    """Zero fraction and nonzero range. A weight is ZERO only if exactly 0.0:
    the device returns exact zeros, and a tolerance would blur the pattern
    this test exists to compare."""
    w = np.asarray(w, dtype=np.float64)
    nz = w[w != 0.0]
    return {"n": int(w.size), "zero_fraction": round(float((w == 0.0).mean()), 4),
            "nonzero_min": float(nz.min()) if nz.size else None,
            "nonzero_max": float(nz.max()) if nz.size else None,
            "nonzero_median": float(np.median(nz)) if nz.size else None}


def main() -> int:
    from eqc_models.ml.classifierqboost import QBoostClassifier

    rows = json.loads((ROOT / "experiments" / "results" / "results.json")
                      .read_text(encoding="utf-8"))["rows"]
    b4 = sorted([r for r in rows if r.get("block") == "B4"],
                key=lambda r: (r["dataset"], r["seed"]))
    out_rows = []
    for r in b4:
        name, seed = r["dataset"].replace("spectra_", ""), r["seed"]
        c = ss.frozen_cell_by_name(name)["config"]
        split, cols = ss._prep_spectra(name, seed)
        Xtr = ss.coerce_features_to_numeric(split.X_train[cols]).to_numpy("float32")
        y_pm1 = np.where(split.y_train.to_numpy() == 1, 1, -1)
        lam = c["lambda_coef_alpha"] * len(y_pm1)
        clf = QBoostClassifier(lambda_coef=lam,
                               weak_cls_schedule=c["weak_cls_schedule"],
                               weak_cls_type="dct",
                               weak_cls_params=dict(c["weak_cls_params"]),
                               weak_cls_strategy=c["weak_cls_strategy"],
                               relaxation_schedule=c["relaxation_schedule"],
                               num_samples=c["num_samples"])
        with em.emulated_solver("exact"):
            clf.fit(Xtr, y_pm1)
        w_exact = qp.solve_simplex_qp(qp.h_matrix(clf, Xtr), y_pm1, lam)
        res = em.Dirac3Emulator("emulate", iters=BUDGET, seed=seed).solve(
            clf, num_samples=c["num_samples"],
            relaxation_schedule=c["relaxation_schedule"])
        emu = res["results"]["solutions"][int(np.argmin(res["results"]["energies"]))]
        dev = json.loads((ROOT / "experiments" / "phase2" / "results"
                          / "device_samples" / f"b4_{name}_stratified_{seed}.json")
                         .read_text(encoding="utf-8"))
        dev_best = dev["solutions"][int(np.argmin(dev["energies"]))]
        row = {"dataset": r["dataset"], "seed": seed,
               "device": sparsity(dev_best), "exact": sparsity(w_exact),
               "emulated": sparsity(emu)}
        out_rows.append(row)
        print(f"  {name:18s} s{seed} zero fraction: device "
              f"{row['device']['zero_fraction']:.3f} exact "
              f"{row['exact']['zero_fraction']:.3f} emulated "
              f"{row['emulated']['zero_fraction']:.3f}", flush=True)

    def mean(arm, key):
        v = [r[arm][key] for r in out_rows if r[arm][key] is not None]
        return round(float(np.mean(v)), 5) if v else None

    summary = {arm: {k: mean(arm, k) for k in
                     ("zero_fraction", "nonzero_min", "nonzero_max",
                      "nonzero_median")}
               for arm in ("device", "exact", "emulated")}
    OUT.write_text(json.dumps({
        "generator": "experiments/phase2/src/emulator_sparsity.py",
        "card": "F17", "sprint": 22, "phase": 2, "evidence_tag": "SIM",
        "metered_seconds": 0, "budget": BUDGET, "summary": summary,
        "rows": out_rows}, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
