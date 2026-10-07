"""Validate the Dirac-3 emulator (F17) against B4's real device results.

Sprint 22 Task D. For each of B4's 10 cells, ONE real QBoostClassifier fit is
run with the emulator swapped in for the cloud solver (`emulated_solver`), so
the library builds the pool and the Hamiltonian exactly as it did for the
device. The same Hamiltonian is then re-solved in exact mode and in emulate
mode at several iteration budgets, with no rebuild.

Compared against what the DEVICE did on that cell (results.json, block B4):
  - weight cosine against the exact solve: device 0.83-0.90
  - within-fit energy spread across the 8 samples: device responses stored in
    experiments/results/pools/hw_responses/

The iteration budget is the emulator's one free knob. The budget that best
matches the device's cosine is reported as CALIBRATED, not predicted.

Zero metered seconds. Output: experiments/phase2/results/f17_emulator_validation.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments" / "src"))
sys.path.insert(0, str(ROOT / "experiments" / "phase2" / "src"))
import metrics                                    # noqa: E402  (Phase 1, read-only)
import qubo_proxy as qp                           # noqa: E402  (Phase 1, read-only)
import spectra_segment as ss                      # noqa: E402  (Phase 1, read-only)
import dirac3_emulator as em                      # noqa: E402

BUDGETS = (25, 100, 400)
OUT = ROOT / "experiments" / "phase2" / "results" / "f17_emulator_validation.json"


def _cos(a, b):
    d = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(a @ b / d) if d else None


def _rel_spread(energies):
    e = np.asarray(energies, dtype=np.float64)
    return float((e.max() - e.min()) / abs(e.min())) if e.size and e.min() else None


def main() -> int:
    from eqc_models.ml.classifierqboost import QBoostClassifier

    rows = json.loads((ROOT / "experiments" / "results" / "results.json")
                      .read_text(encoding="utf-8"))["rows"]
    b4 = sorted([r for r in rows if r.get("block") == "B4"],
                key=lambda r: (r["dataset"], r["seed"]))
    out_rows = []
    for r in b4:
        t0 = time.perf_counter()
        name, seed = r["dataset"].replace("spectra_", ""), r["seed"]
        cell = ss.frozen_cell_by_name(name)
        split, cols = ss._prep_spectra(name, seed)
        Xtr = ss.coerce_features_to_numeric(split.X_train[cols]).to_numpy("float32")
        Xte = ss.coerce_features_to_numeric(split.X_test[cols]).to_numpy("float32")
        y01 = split.y_train.to_numpy()
        y_pm1 = np.where(y01 == 1, 1, -1)
        yte = split.y_test.to_numpy()
        c = cell["config"]
        lam = c["lambda_coef_alpha"] * len(y_pm1)
        clf = QBoostClassifier(lambda_coef=lam,
                               weak_cls_schedule=c["weak_cls_schedule"],
                               weak_cls_type="dct",
                               weak_cls_params=dict(c["weak_cls_params"]),
                               weak_cls_strategy=c["weak_cls_strategy"],
                               relaxation_schedule=c["relaxation_schedule"],
                               num_samples=c["num_samples"])
        with em.emulated_solver("exact"):
            clf.fit(Xtr, y_pm1)                     # builds pool + J, C
        H_tr = qp.h_matrix(clf, Xtr)
        H_te = qp.h_matrix(clf, Xte)
        w_exact = qp.solve_simplex_qp(H_tr, y_pm1, lam)
        ap_exact = float(metrics.average_precision_score(
            yte, np.clip((w_exact @ H_te + 1) / 2, 0, 1)))

        # Full samples recovered by job id; the Phase 1 response files hold
        # only numpy's truncated print (recover_device_samples.py).
        dev = json.loads((ROOT / "experiments" / "phase2" / "results"
                          / "device_samples" / f"b4_{name}_stratified_{seed}.json")
                         .read_text(encoding="utf-8"))
        row = {"dataset": r["dataset"], "seed": seed,
               "n_vars": int(H_tr.shape[0]),
               "exact_test_auprc": ap_exact,
               "device": {"weight_cosine": r.get("weight_cosine_vs_classical"),
                          "test_auprc": r["metrics"]["auprc"],
                          "energy_rel_spread": _rel_spread(dev.get("energies", [])),
                          "metered_seconds": r.get("metered_seconds")},
               "emulated": {}}
        for iters in BUDGETS:
            emu = em.Dirac3Emulator("emulate", iters=iters, seed=seed)
            res = emu.solve(clf, num_samples=c["num_samples"],
                            relaxation_schedule=c["relaxation_schedule"])
            sols = [np.asarray(s) for s in res["results"]["solutions"]]
            best = sols[int(np.argmin(res["results"]["energies"]))]
            row["emulated"][str(iters)] = {
                "weight_cosine": _cos(best, w_exact),
                "test_auprc": float(metrics.average_precision_score(
                    yte, np.clip((best @ H_te + 1) / 2, 0, 1))),
                "energy_rel_spread": _rel_spread(res["results"]["energies"]),
                "cost_estimate_s": res["emulated"]["cost_estimate_s"]}
        row["elapsed_s"] = round(time.perf_counter() - t0, 1)
        out_rows.append(row)
        print(f"  {name:18s} s{seed} device cos {row['device']['weight_cosine']:.3f} | "
              + " ".join(f"{k}:{v['weight_cosine']:.3f}"
                         for k, v in row["emulated"].items()), flush=True)

    dev_cos = np.array([r["device"]["weight_cosine"] for r in out_rows])
    summary = {}
    for k in map(str, BUDGETS):
        emu_cos = np.array([r["emulated"][k]["weight_cosine"] for r in out_rows])
        summary[k] = {"mean_abs_cosine_gap_vs_device":
                      round(float(np.mean(np.abs(emu_cos - dev_cos))), 4),
                      "mean_cosine": round(float(emu_cos.mean()), 4)}
    best_budget = min(summary, key=lambda k: summary[k]["mean_abs_cosine_gap_vs_device"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "generator": "experiments/phase2/src/validate_emulator.py",
        "card": "F17", "sprint": 22, "phase": 2, "evidence_tag": "SIM",
        "metered_seconds": 0,
        "device_mean_cosine": round(float(dev_cos.mean()), 4),
        "summary_by_iteration_budget": summary,
        "calibrated_budget": best_budget,
        "rows": out_rows}, indent=2), encoding="utf-8")
    print(json.dumps({"device_mean_cosine": round(float(dev_cos.mean()), 4),
                      "by_budget": summary, "calibrated": best_budget}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
