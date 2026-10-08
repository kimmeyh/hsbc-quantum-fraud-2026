"""F124: a zero-cost proxy screen of the levers nobody has tried here.

Sprint 22 Task C (#162). Phase 2 code: it IMPORTS Phase 1 modules
(`qubo_proxy`, `spectra_segment`) and edits none. Results go to
`experiments/phase2/results/f124_lever_screen.json`. Zero metered seconds.

A SCREEN, not a test: 2 seeds, hard votes, exact proxy. It decides which
levers earn the full 5-seed proxy test that the ranked list
(`docs/phase2/SPECTRA_IMPROVEMENT_RESEARCH.md`) proposes. A lever that moves
AUPRC by less than the seed spread here is not promoted on this evidence.

Variants, each against the frozen B4 configuration (dct, default params,
schedule 3, lambda alpha 2.0):
  - weak learner type: knn, lgb, xgb (eqc_models `weak_cls_type`); the
    EvidenceBasedDB lead is KNN weak learners on a different fraud dataset
  - tree regularization against the train-test gap: max_depth 4, and
    min_samples_leaf 20
  - stronger lambda: alpha 20 (10x)

Run:  <venv python> experiments/phase2/src/lever_screen.py
      <venv python> experiments/phase2/src/lever_screen.py stack
            (soft votes on the min_leaf_20 pool: one lever or two?)
      <venv python> experiments/phase2/src/lever_screen.py confirm
            (energy_steel winners, 5 seeds, against HGB on the same splits)
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import soft_votes as sv                              # noqa: E402  (Phase 2)
import qubo_proxy as qp                              # noqa: E402  (Phase 1, read-only)
import spectra_segment as ss                         # noqa: E402  (Phase 1, read-only)

SEEDS = (42, 43)
VARIANTS = {
    "baseline_dct":    {"weak_type": "dct", "params": {}, "alpha": None},
    "dct_max_depth_4": {"weak_type": "dct", "params": {"max_depth": 4},
                        "alpha": None},
    "dct_min_leaf_20": {"weak_type": "dct", "params": {"min_samples_leaf": 20},
                        "alpha": None},
    "dct_alpha_20":    {"weak_type": "dct", "params": {}, "alpha": 20.0},
    "knn":             {"weak_type": "knn", "params": {}, "alpha": None},
    "lgb":             {"weak_type": "lgb", "params": {"verbose": -1},
                        "alpha": None},
    "xgb":             {"weak_type": "xgb", "params": {}, "alpha": None},
}


def run() -> dict:
    rows = []
    for cell in ss.FROZEN_CELLS:
        name = cell["dataset"].replace("spectra_", "")
        for seed in SEEDS:
            c, Xtr, Xte, ytr01, yte, pocket = sv._prep(name, seed)
            y_pm1 = np.where(ytr01 == 1, 1, -1)
            cfg = c["config"]
            for vname, v in VARIANTS.items():
                t0 = time.perf_counter()
                alpha = v["alpha"] or cfg["lambda_coef_alpha"]
                lam = alpha * len(y_pm1)
                row = {"dataset": cell["dataset"], "seed": seed,
                       "variant": vname}
                try:
                    clf = qp.build_pool(Xtr, y_pm1, cfg["weak_cls_schedule"],
                                        weak_type=v["weak_type"],
                                        pair_build="sequential",
                                        weak_params=v["params"],
                                        lambda_coef=lam)
                    H_tr, H_te = qp.h_matrix(clf, Xtr), qp.h_matrix(clf, Xte)
                    w = qp.solve_simplex_qp(H_tr, y_pm1, lam)
                    p_te, p_tr = sv._score(w, H_te), sv._score(w, H_tr)
                    row.update(test_auprc=sv._ap(yte, p_te),
                               train_auprc=sv._ap(ytr01, p_tr),
                               in_pocket_auprc=sv._in_pocket_ap(yte, p_te,
                                                                pocket),
                               n_learners=int(H_tr.shape[0]),
                               n_nonzero_weights=int((w > 1e-6).sum()))
                except Exception as e:                  # noqa: BLE001
                    # Recorded, never dropped: a lever that cannot be built
                    # is a finding about the lever.
                    row["error"] = f"{type(e).__name__}: {str(e)[:300]}"
                row["elapsed_s"] = round(time.perf_counter() - t0, 1)
                rows.append(row)
                print(f"  {name:18s} s{seed} {vname:16s} "
                      f"{row.get('test_auprc', float('nan')):.4f} "
                      f"{row['elapsed_s']:.0f}s {row.get('error', '')}",
                      flush=True)
    return {"rows": rows, "summary": _summarize(rows)}


def _summarize(rows):
    out = {}
    for ds in sorted({r["dataset"] for r in rows}):
        base = {r["seed"]: r for r in rows
                if r["dataset"] == ds and r["variant"] == "baseline_dct"}
        out[ds] = {}
        for vname in VARIANTS:
            sub = [r for r in rows if r["dataset"] == ds
                   and r["variant"] == vname and "test_auprc" in r]
            if not sub:
                out[ds][vname] = {"status": "failed on every seed"}
                continue
            d = [r["test_auprc"] - base[r["seed"]]["test_auprc"] for r in sub
                 if "test_auprc" in base.get(r["seed"], {})]
            out[ds][vname] = {
                "mean_test_auprc": round(float(np.mean(
                    [r["test_auprc"] for r in sub])), 4),
                "mean_delta_vs_baseline": (round(float(np.mean(d)), 4)
                                           if d else None),
                "mean_train_test_gap": round(float(np.mean(
                    [r["train_auprc"] - r["test_auprc"] for r in sub])), 4),
                "n_seeds": len(sub)}
    return out


CONFIRM_DATASET = "energy_steel"
CONFIRM_VARIANTS = ("baseline_dct", "dct_min_leaf_20", "knn", "lgb", "xgb")


def run_confirm() -> dict:
    """The screen's energy_steel winners on all 5 seeds, against HGB on the
    same splits, paired. Added after the 2-seed screen put three variants
    above HGB's 5-seed mean; 2 seeds are not enough to rank on."""
    from sklearn.ensemble import HistGradientBoostingClassifier

    cell = next(c for c in ss.FROZEN_CELLS
                if c["dataset"] == f"spectra_{CONFIRM_DATASET}")
    rows = []
    for seed in sv.SEEDS:
        c, Xtr, Xte, ytr01, yte, pocket = sv._prep(CONFIRM_DATASET, seed)
        y_pm1 = np.where(ytr01 == 1, 1, -1)
        cfg = c["config"]
        lam = cfg["lambda_coef_alpha"] * len(y_pm1)
        hgb = HistGradientBoostingClassifier(random_state=seed).fit(Xtr, ytr01)
        p_hgb = hgb.predict_proba(Xte)[:, 1]
        hgb_ap = sv._ap(yte, p_hgb)
        hgb_ip = sv._in_pocket_ap(yte, p_hgb, pocket)
        for vname in CONFIRM_VARIANTS:
            v = VARIANTS[vname]
            t0 = time.perf_counter()
            clf = qp.build_pool(Xtr, y_pm1, cfg["weak_cls_schedule"],
                                weak_type=v["weak_type"],
                                pair_build="sequential",
                                weak_params=v["params"], lambda_coef=lam)
            H_tr, H_te = qp.h_matrix(clf, Xtr), qp.h_matrix(clf, Xte)
            w = qp.solve_simplex_qp(H_tr, y_pm1, lam)
            p_te, p_tr = sv._score(w, H_te), sv._score(w, H_tr)
            row = {"dataset": cell["dataset"], "seed": seed, "variant": vname,
                   "test_auprc": sv._ap(yte, p_te),
                   "train_auprc": sv._ap(ytr01, p_tr),
                   "in_pocket_auprc": sv._in_pocket_ap(yte, p_te, pocket),
                   "hgb_test_auprc": hgb_ap, "hgb_in_pocket_auprc": hgb_ip,
                   "elapsed_s": round(time.perf_counter() - t0, 1)}
            row["delta_vs_hgb"] = row["test_auprc"] - hgb_ap
            rows.append(row)
            print(f"  s{seed} {vname:16s} {row['test_auprc']:.4f} "
                  f"hgb {hgb_ap:.4f}", flush=True)
    summary = {}
    for vname in CONFIRM_VARIANTS:
        sub = [r for r in rows if r["variant"] == vname]
        d = [r["delta_vs_hgb"] for r in sub]
        summary[vname] = {
            "mean_test_auprc": round(float(np.mean(
                [r["test_auprc"] for r in sub])), 4),
            "seed_sd": round(float(np.std([r["test_auprc"] for r in sub],
                                          ddof=1)), 4),
            "mean_train_test_gap": round(float(np.mean(
                [r["train_auprc"] - r["test_auprc"] for r in sub])), 4),
            "mean_delta_vs_hgb": round(float(np.mean(d)), 4),
            "delta_vs_hgb_ci95": sv._bootstrap_ci(d),
            "seeds_beating_hgb": int(sum(x > 0 for x in d))}
    summary["hgb_mean_test_auprc"] = round(float(np.mean(
        [r["hgb_test_auprc"] for r in rows
         if r["variant"] == "baseline_dct"])), 4)
    return {"rows": rows, "summary": summary}


def run_stack() -> dict:
    """Do Laplace soft votes and min_samples_leaf=20 stack, or are they one
    lever? Both shrink the vote of a tiny, pure leaf. energy_steel, 5 seeds:
    hard and soft votes on the min_leaf_20 pool, paired by seed."""
    rows = []
    for seed in sv.SEEDS:
        c, Xtr, Xte, ytr01, yte, pocket = sv._prep(CONFIRM_DATASET, seed)
        y_pm1 = np.where(ytr01 == 1, 1, -1)
        cfg = c["config"]
        lam = cfg["lambda_coef_alpha"] * len(y_pm1)
        clf = qp.build_pool(Xtr, y_pm1, cfg["weak_cls_schedule"],
                            weak_type="dct", pair_build="sequential",
                            weak_params={"min_samples_leaf": 20},
                            lambda_coef=lam)
        row = {"dataset": f"spectra_{CONFIRM_DATASET}", "seed": seed}
        for arm, hm in (("hard", qp.h_matrix), ("soft", sv.soft_h_matrix)):
            H_tr, H_te = hm(clf, Xtr), hm(clf, Xte)
            w = qp.solve_simplex_qp(H_tr, y_pm1, lam)
            row[f"{arm}_test_auprc"] = sv._ap(yte, sv._score(w, H_te))
            row[f"{arm}_n_nonzero_weights"] = int((w > 1e-6).sum())
        row["delta_soft_minus_hard"] = (row["soft_test_auprc"]
                                        - row["hard_test_auprc"])
        rows.append(row)
        print(f"  s{seed} min_leaf_20 hard {row['hard_test_auprc']:.4f} "
              f"soft {row['soft_test_auprc']:.4f}", flush=True)
    d = [r["delta_soft_minus_hard"] for r in rows]
    return {"rows": rows, "summary": {
        "mean_hard_auprc": round(float(np.mean(
            [r["hard_test_auprc"] for r in rows])), 4),
        "mean_soft_auprc": round(float(np.mean(
            [r["soft_test_auprc"] for r in rows])), 4),
        "mean_delta_soft_minus_hard": round(float(np.mean(d)), 4),
        "delta_ci95": sv._bootstrap_ci(d),
        "seeds_soft_better": int(sum(x > 0 for x in d))}}


OUTPUTS = {"screen": "f124_lever_screen.json",
           "confirm": "f124_lever_confirm_energy_steel.json",
           "stack": "f124_lever_stack_energy_steel.json"}


def main() -> int:
    part = sys.argv[1] if len(sys.argv) > 1 else "screen"
    if part not in OUTPUTS:
        raise SystemExit(f"unknown part {part!r}; one of {sorted(OUTPUTS)}")
    confirm = part != "screen"
    res = {"screen": run, "confirm": run_confirm, "stack": run_stack}[part]()
    out = sv.OUT_DIR / OUTPUTS[part]
    out.write_text(json.dumps({
        "generator": "experiments/phase2/src/lever_screen.py", "card": "F124",
        "sprint": 22, "phase": 2, "evidence_tag": "SIM", "metered_seconds": 0,
        "eqc_models_version": sv._eqc_version(),
        "seeds": list(sv.SEEDS if confirm else SEEDS),
        **res}, indent=2), encoding="utf-8")
    print(json.dumps(res["summary"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
