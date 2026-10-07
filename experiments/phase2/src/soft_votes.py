"""F20: soft votes and multi-sample ensembling on the classical proxy.

Sprint 22 Task E (#164). Phase 2 code (`docs/PHASE_SEPARATION.md`): it IMPORTS
Phase 1 modules (`qubo_proxy`, `spectra_segment`, `metrics`) and edits none.
Results go to `experiments/phase2/results/`. Zero metered seconds.

PART 1, SOFT VOTES. CVQBoost's weak learners vote hard: +1 or -1. A learner
that is 51% sure and one that is 99% sure cast the same vote, and the device
never sees the difference. Here each vote becomes the learner's confidence,
2 * P(fraud) - 1, from the SAME learner on the SAME feature subset the hard
vote uses (`eqc_models._compute_h_matrix` calls
`h_list[i].predict(X[:, ind_list[i]])`; the soft vote calls
`h_list[i].clf.predict_proba` on the identical slice). Same pool, same
Hamiltonian shape (J = HH^T + lambda I, C = -2Hy), same simplex solve -- only
the vote values change. Both arms are solved by the exact proxy, so the
comparison isolates the vote.

The soft vote reaches the library's internal `WeakClassifier.clf`; the
installed `eqc_models` version is recorded with every result.

PART 2, MULTI-SAMPLE ENSEMBLING. Each B4 device fit returned 8 samples and
kept only the lowest-energy one. Averaging the predictions of the top-k costs
no device time. Valid ONLY if a rebuilt weak-learner pool is the pool the
device solved; the decision trees break ties randomly, so this is checked
first, per cell, by rescoring the device's best sample and comparing with the
stored device AUPRC. A cell that does not reproduce is reported as not
evaluable, never scored on a different pool.

Run:
  <venv python> experiments/phase2/src/soft_votes.py soft
  <venv python> experiments/phase2/src/soft_votes.py ensemble
  <venv python> experiments/phase2/src/soft_votes.py ensemble-emulated
  <venv python> experiments/phase2/src/soft_votes.py classical   (after soft)
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from importlib import metadata
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments" / "src"))
import metrics                                      # noqa: E402  (Phase 1, read-only)
import qubo_proxy as qp                             # noqa: E402  (Phase 1, read-only)
import spectra_segment as ss                        # noqa: E402  (Phase 1, read-only)

OUT_DIR = ROOT / "experiments" / "phase2" / "results"
SEEDS = (42, 43, 44, 45, 46)


def _eqc_version() -> str:
    for name in ("eqc-models", "eqc_models"):
        try:
            return metadata.version(name)
        except metadata.PackageNotFoundError:
            continue
    return "unknown"


def _laplace_p1(model, Xs: np.ndarray) -> np.ndarray:
    """P(class 1) from leaf COUNTS with Laplace smoothing: (n1 + 1) / (n + 2).

    WHY NOT predict_proba (found 2026-10-06, Sprint 22). The frozen pool uses
    unlimited-depth trees (`weak_cls_params={}`); measured on a synthetic pool,
    trees grow 17 deep with a MEDIAN LEAF OF ONE TRAINING ROW, every leaf is
    pure, and predict_proba returns exactly 0 or 1 -- 0% of "soft" votes fall
    strictly inside (-1, 1). The card's soft vote is then the hard vote under
    another name. The information the hard vote discards is HOW MANY rows
    decided the leaf: a one-row leaf scores 2/3, a 300-row leaf ~0.997.

    sklearn >= 1.4 stores leaf class FRACTIONS in tree_.value (1.9.0 here),
    so counts are fraction x weighted node size; an older count-valued tree is
    detected by its rows not summing to 1.
    """
    t = model.tree_
    leaf = model.apply(Xs)
    v = t.value[leaf, 0, :]
    n = t.weighted_n_node_samples[leaf]
    sums = v.sum(axis=1)
    counts = np.where(np.isclose(sums, 1.0)[:, None], v * n[:, None], v)
    classes = list(model.classes_)
    n1 = counts[:, classes.index(1)] if 1 in classes else np.zeros(len(Xs))
    return (n1 + 1.0) / (counts.sum(axis=1) + 2.0)


def soft_h_matrix(clf, X: np.ndarray, mode: str = "laplace") -> np.ndarray:
    """(n_learners, n_rows) confidences in [-1, 1]: 2 * P(class 1) - 1.

    WeakClassifier.train fits on y mapped to {0, 1}, so class 1 is fraud.
    mode "laplace" (default) smooths the leaf counts of decision-tree
    learners; mode "proba" is raw predict_proba, kept so the degeneracy above
    stays measurable.
    """
    rows = []
    for h, ind in zip(clf.h_list, clf.ind_list):
        model = h.clf
        Xs = X[:, ind]
        if mode == "laplace" and hasattr(model, "tree_"):
            p1 = _laplace_p1(model, Xs)
        else:
            proba = model.predict_proba(Xs)
            classes = list(model.classes_)
            p1 = (proba[:, classes.index(1)] if 1 in classes
                  else np.zeros(len(Xs)))
        rows.append(2.0 * p1 - 1.0)
    return np.asarray(rows, dtype=np.float64)


def _prep(name: str, seed: int):
    cell = ss.frozen_cell_by_name(name)
    split, cols = ss._prep_spectra(name, seed)

    def X(df):
        return ss.coerce_features_to_numeric(df[cols]).to_numpy(dtype="float32")

    return (cell, X(split.X_train), X(split.X_test), split.y_train.to_numpy(),
            split.y_test.to_numpy(),
            split.X_test[ss.SEGMENT_FLAG].to_numpy().astype(bool))


def _score(w, H):
    return np.clip((w @ H + 1.0) / 2.0, 0.0, 1.0)


def _ap(y, p):
    return float(metrics.average_precision_score(y, p))


def _in_pocket_ap(y, p, pocket):
    yp = y[pocket]
    return _ap(yp, p[pocket]) if yp.sum() >= 50 else None


def run_soft(heartbeat: Path) -> dict:
    rows = []
    for cell in ss.FROZEN_CELLS:
        name = cell["dataset"].replace("spectra_", "")
        for seed in SEEDS:
            t0 = time.perf_counter()
            c, Xtr, Xte, ytr01, yte, pocket = _prep(name, seed)
            y_pm1 = np.where(ytr01 == 1, 1, -1)
            lam = c["config"]["lambda_coef_alpha"] * len(y_pm1)
            clf = qp.build_pool(Xtr, y_pm1, c["config"]["weak_cls_schedule"],
                                weak_type="dct", pair_build="sequential",
                                lambda_coef=lam)
            Hh_tr, Hh_te = qp.h_matrix(clf, Xtr), qp.h_matrix(clf, Xte)
            Hs_tr, Hs_te = soft_h_matrix(clf, Xtr), soft_h_matrix(clf, Xte)
            w_h = qp.solve_simplex_qp(Hh_tr, y_pm1, lam)
            w_s = qp.solve_simplex_qp(Hs_tr, y_pm1, lam)
            ph_te, ps_te = _score(w_h, Hh_te), _score(w_s, Hs_te)
            ph_tr, ps_tr = _score(w_h, Hh_tr), _score(w_s, Hs_tr)
            row = {
                "dataset": cell["dataset"], "seed": seed,
                "n_learners": int(Hh_tr.shape[0]),
                "hard": {"test_auprc": _ap(yte, ph_te),
                         "train_auprc": _ap(ytr01, ph_tr),
                         "in_pocket_auprc": _in_pocket_ap(yte, ph_te, pocket)},
                "soft": {"test_auprc": _ap(yte, ps_te),
                         "train_auprc": _ap(ytr01, ps_tr),
                         "in_pocket_auprc": _in_pocket_ap(yte, ps_te, pocket)},
                "elapsed_s": round(time.perf_counter() - t0, 1),
            }
            row["delta_test_auprc"] = (row["soft"]["test_auprc"]
                                       - row["hard"]["test_auprc"])
            rows.append(row)
            heartbeat.write_text(
                f"{time.strftime('%H:%M:%S')} {name} seed {seed} done "
                f"({len(rows)}/15) delta {row['delta_test_auprc']:+.4f}\n",
                encoding="utf-8")
    return {"rows": rows, "summary": _summarize(rows)}


def _bootstrap_ci(d, n=10000, seed=42):
    d = np.asarray(d, dtype=np.float64)
    rng = np.random.default_rng(seed)
    means = [rng.choice(d, len(d), replace=True).mean() for _ in range(n)]
    return [round(float(np.percentile(means, 2.5)), 4),
            round(float(np.percentile(means, 97.5)), 4)]


def _summarize(rows):
    out = {}
    for ds in sorted({r["dataset"] for r in rows}):
        d = [r["delta_test_auprc"] for r in rows if r["dataset"] == ds]
        hard = [r["hard"]["test_auprc"] for r in rows if r["dataset"] == ds]
        out[ds] = {"n_seeds": len(d),
                   "mean_hard_auprc": round(float(np.mean(hard)), 4),
                   "mean_delta_soft_minus_hard": round(float(np.mean(d)), 4),
                   "delta_ci95": _bootstrap_ci(d),
                   "seeds_soft_better": int(sum(x > 0 for x in d)),
                   "seed_sd_hard": round(float(np.std(hard, ddof=1)), 4)}
    return out


def run_ensemble() -> dict:
    """Top-k ensembling over B4's stored device samples, reproducibility first."""
    b4 = [r for r in json.loads((ROOT / "experiments" / "results" /
                                 "results.json").read_text(encoding="utf-8")
                                )["rows"] if r.get("block") == "B4"]
    # The FULL samples, recovered by job id (recover_device_samples.py). The
    # Phase 1 files in pools/hw_responses hold only numpy's truncated print
    # of each sample (first and last three values), so they cannot be scored.
    samples_dir = ROOT / "experiments" / "phase2" / "results" / "device_samples"
    rows = []
    for r in sorted(b4, key=lambda r: (r["dataset"], r["seed"])):
        name, seed = r["dataset"].replace("spectra_", ""), r["seed"]
        rec = json.loads((samples_dir / f"b4_{name}_stratified_{seed}.json")
                         .read_text(encoding="utf-8"))
        sols = [np.asarray(s, dtype=np.float64) for s in rec["solutions"]]
        energies = list(rec["energies"])
        c, Xtr, Xte, ytr01, yte, pocket = _prep(name, seed)
        y_pm1 = np.where(ytr01 == 1, 1, -1)
        lam = c["config"]["lambda_coef_alpha"] * len(y_pm1)
        clf = qp.build_pool(Xtr, y_pm1, c["config"]["weak_cls_schedule"],
                            weak_type="dct", pair_build="sequential",
                            lambda_coef=lam)
        H_te = qp.h_matrix(clf, Xte)
        order = np.argsort(energies)
        best = sols[order[0]]
        rescored = _ap(yte, _score(best, H_te))
        stored = r["metrics"]["auprc"]
        reproduces = abs(rescored - stored) < 1e-6
        row = {"dataset": r["dataset"], "seed": seed,
               "n_samples": len(sols), "stored_device_auprc": stored,
               "rescored_best_auprc": rescored, "pool_reproduces": reproduces}
        if reproduces:
            for k in (1, 2, 4, len(sols)):
                p = np.mean([_score(sols[i], H_te) for i in order[:k]], axis=0)
                row[f"top{k}_auprc"] = _ap(yte, p)
        rows.append(row)
    n_rep = sum(r["pool_reproduces"] for r in rows)
    return {"rows": rows, "cells_reproducing": n_rep, "cells_total": len(rows)}


def run_ensemble_emulated() -> dict:
    """Top-k ensembling on EMULATED samples, which share the pool they score.

    The device-sample version is not evaluable: a rebuilt pool misses the
    device's stored AUPRC by 0.0001-0.003 on all 10 B4 cells (random tie
    breaks in the trees), so device weights cannot be scored on it. The
    emulator (F17) returns 8 samples ON the pool it built, so averaging them
    is a valid within-pool test of the ensembling idea. Calibrated budget 25
    (experiments/phase2/results/f17_emulator_validation.json).
    """
    from eqc_models.ml.classifierqboost import QBoostClassifier
    import dirac3_emulator as em

    b4 = [r for r in json.loads((ROOT / "experiments" / "results" /
                                 "results.json").read_text(encoding="utf-8")
                                )["rows"] if r.get("block") == "B4"]
    rows = []
    for r in sorted(b4, key=lambda r: (r["dataset"], r["seed"])):
        name, seed = r["dataset"].replace("spectra_", ""), r["seed"]
        c, Xtr, Xte, ytr01, yte, pocket = _prep(name, seed)
        y_pm1 = np.where(ytr01 == 1, 1, -1)
        cfg = c["config"]
        clf = QBoostClassifier(
            lambda_coef=cfg["lambda_coef_alpha"] * len(y_pm1),
            weak_cls_schedule=cfg["weak_cls_schedule"], weak_cls_type="dct",
            weak_cls_params=dict(cfg["weak_cls_params"]),
            weak_cls_strategy=cfg["weak_cls_strategy"],
            relaxation_schedule=cfg["relaxation_schedule"],
            num_samples=cfg["num_samples"])
        with em.emulated_solver("emulate", iters=25, seed=seed):
            resp = clf.fit(Xtr, y_pm1)
        sols = [np.asarray(s) for s in resp["results"]["solutions"]]
        order = np.argsort(resp["results"]["energies"])
        H_te = qp.h_matrix(clf, Xte)
        row = {"dataset": r["dataset"], "seed": seed, "n_samples": len(sols)}
        for k in (1, 2, 4, len(sols)):
            p = np.mean([_score(sols[i], H_te) for i in order[:k]], axis=0)
            row[f"top{k}_auprc"] = _ap(yte, p)
        row["delta_top8_minus_top1"] = row[f"top{len(sols)}_auprc"] - row["top1_auprc"]
        rows.append(row)
        print(f"  {name:18s} s{seed} top1 {row['top1_auprc']:.4f} "
              f"top8 {row[f'top{len(sols)}_auprc']:.4f}", flush=True)
    d = [r["delta_top8_minus_top1"] for r in rows]
    return {"rows": rows, "basis": "emulated samples, calibrated budget 25",
            "mean_delta_top8_minus_top1": round(float(np.mean(d)), 5),
            "delta_ci95": _bootstrap_ci(d),
            "cells_top8_better": int(sum(x > 0 for x in d))}


def run_classical() -> dict:
    """Soft-vote CVQBoost against HGB and GA2M on the SAME splits, paired.

    The classical lanes are configured as f100_lane_pilot.py configures them
    (default HGB, random_state=seed; GA2M = HGB with main-effect and pairwise
    interaction constraints). Soft-vote AUPRC is read from
    f20_soft_votes.json, so this part must run after `soft`.
    """
    from sklearn.ensemble import HistGradientBoostingClassifier

    soft = json.loads((OUT_DIR / "f20_soft_votes.json").read_text(
        encoding="utf-8"))["rows"]
    rows = []
    for r in soft:
        name, seed = r["dataset"].replace("spectra_", ""), r["seed"]
        _, Xtr, Xte, ytr01, yte, pocket = _prep(name, seed)
        n = Xtr.shape[1]
        lanes = {"hgb": HistGradientBoostingClassifier(random_state=seed),
                 "ga2m": HistGradientBoostingClassifier(
                     random_state=seed,
                     interaction_cst=[[i] for i in range(n)] + [
                         [i, j] for i in range(n) for j in range(i + 1, n)])}
        row = {"dataset": r["dataset"], "seed": seed,
               "soft_test_auprc": r["soft"]["test_auprc"]}
        for lane, m in lanes.items():
            p = m.fit(Xtr, ytr01).predict_proba(Xte)[:, 1]
            row[f"{lane}_test_auprc"] = _ap(yte, p)
            row[f"delta_soft_minus_{lane}"] = (r["soft"]["test_auprc"]
                                               - row[f"{lane}_test_auprc"])
        rows.append(row)
        print(f"  {name:18s} s{seed} soft {row['soft_test_auprc']:.4f} "
              f"hgb {row['hgb_test_auprc']:.4f}", flush=True)
    summary = {}
    for ds in sorted({r["dataset"] for r in rows}):
        sub = [r for r in rows if r["dataset"] == ds]
        summary[ds] = {}
        for lane in ("hgb", "ga2m"):
            d = [r[f"delta_soft_minus_{lane}"] for r in sub]
            summary[ds][lane] = {
                "mean_lane_auprc": round(float(np.mean(
                    [r[f"{lane}_test_auprc"] for r in sub])), 4),
                "mean_delta_soft_minus_lane": round(float(np.mean(d)), 4),
                "delta_ci95": _bootstrap_ci(d),
                "seeds_soft_better": int(sum(x > 0 for x in d))}
    return {"rows": rows, "summary": summary}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("part", choices=("soft", "ensemble", "ensemble-emulated",
                                     "classical"))
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    common = {"generator": "experiments/phase2/src/soft_votes.py",
              "card": "F20", "sprint": 22, "phase": 2,
              "evidence_tag": "SIM", "metered_seconds": 0,
              "eqc_models_version": _eqc_version()}
    if args.part == "soft":
        # Heartbeat outside the evidence directories: a progress file is not
        # evidence, and IMP-3's guard counts every non-ignored file there.
        import tempfile
        res = run_soft(Path(tempfile.gettempdir()) / "f20_soft_votes.heartbeat.txt")
        out = OUT_DIR / "f20_soft_votes.json"
    elif args.part == "ensemble":
        res = run_ensemble()
        out = OUT_DIR / "f20_multisample_ensemble.json"
    elif args.part == "classical":
        res = run_classical()
        out = OUT_DIR / "f20_soft_vs_classical.json"
    else:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        res = run_ensemble_emulated()
        out = OUT_DIR / "f20_multisample_ensemble_emulated.json"
    out.write_text(json.dumps({**common, **res}, indent=2), encoding="utf-8")
    print(json.dumps(res.get("summary") or {k: v for k, v in res.items()
                                             if k != "rows"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
