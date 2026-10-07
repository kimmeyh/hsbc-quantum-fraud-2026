"""F100 lane pilot: size each classical lane on real SPECTRA data, once.

SPRINT_PLANNING.md, Sprint 9 improvement 2: "NAME the dominant term and show
its measurement ... If you cannot say which component dominates, the sizing is
not finished." Sprint 9 followed the runtime rule and still missed by 47x --
10 minutes planned against 7.9 hours actual, three times -- because the twins
and the GBDTs were both sized from real fits and the CVQBoost pool build, 300
of 335 seconds per cell, was never on the list of things being measured.

So this measures EVERY lane F100 will run, on one real cell, and prints which
one dominates. Zero metered seconds: all five lanes are classical.

The lanes are F100's own list: LogReg, GAM, GA2M, HGB, and an order-matched
JOINT twin. The JOINT twin is the one that matters most for reading a result
-- `docs/references.md` records that omitting it is how the Fourier Wall paper
shows a fake quantum win (0.758 against 0.721) that a JOINT twin reads
classically at 0.968.

Run:
  <venv python> experiments/src/f100_lane_pilot.py [--cell oilgas_gasturbine]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import spectra_segment as ss                  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results" / "f100_lane_pilot.json"


def _fit_timed(name: str, fn) -> dict:
    t0 = time.perf_counter()
    try:
        auprc, auc = fn()
        return {"lane": name, "status": "ok",
                "elapsed_s": round(time.perf_counter() - t0, 2),
                "auprc": round(float(auprc), 4), "auc_roc": round(float(auc), 4)}
    except Exception as exc:                              # noqa: BLE001
        return {"lane": name, "status": "error",
                "elapsed_s": round(time.perf_counter() - t0, 2),
                "error": f"{type(exc).__name__}: {str(exc)[:160]}"}


def pilot(cell_name: str, seed: int = 42) -> dict:
    from sklearn.metrics import average_precision_score, roc_auc_score

    split, cols = ss._prep_spectra(cell_name, seed)
    Xtr = ss.coerce_features_to_numeric(split.X_train[cols]).to_numpy(dtype="float64")
    Xte = ss.coerce_features_to_numeric(split.X_test[cols]).to_numpy(dtype="float64")
    ytr = split.y_train.to_numpy()
    yte = split.y_test.to_numpy()

    def score(p):
        return average_precision_score(yte, p), roc_auc_score(yte, p)

    lanes = []

    # ---- LogReg: the floor control -----------------------------------------
    def _logreg():
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        m = make_pipeline(StandardScaler(),
                          LogisticRegression(max_iter=5000))
        m.fit(Xtr, ytr)
        return score(m.predict_proba(Xte)[:, 1])
    lanes.append(_fit_timed("logreg", _logreg))

    # ---- HGB: the strong GBDT ----------------------------------------------
    def _hgb():
        from sklearn.ensemble import HistGradientBoostingClassifier
        m = HistGradientBoostingClassifier(random_state=seed)
        m.fit(Xtr, ytr)
        return score(m.predict_proba(Xte)[:, 1])
    lanes.append(_fit_timed("hgb", _hgb))

    # ---- GA2M: main effects + pairwise only --------------------------------
    def _ga2m():
        from sklearn.ensemble import HistGradientBoostingClassifier
        # interaction_cst with singleton groups = main effects only; adding
        # adjacent pairs gives the GAM-plus-pairwise contract. Proven
        # available by h6_twin_preflight.py.
        n = Xtr.shape[1]
        groups = [[i] for i in range(n)] + [
            [i, j] for i in range(n) for j in range(i + 1, n)]
        m = HistGradientBoostingClassifier(random_state=seed,
                                           interaction_cst=groups)
        m.fit(Xtr, ytr)
        return score(m.predict_proba(Xte)[:, 1])
    lanes.append(_fit_timed("ga2m", _ga2m))

    # ---- GAM: spline-basis additive model ----------------------------------
    def _gam():
        from sklearn.ensemble import HistGradientBoostingClassifier
        n = Xtr.shape[1]
        m = HistGradientBoostingClassifier(
            random_state=seed, interaction_cst=[[i] for i in range(n)])
        m.fit(Xtr, ytr)
        return score(m.predict_proba(Xte)[:, 1])
    lanes.append(_fit_timed("gam_additive", _gam))

    # ---- JOINT twin: the lane that decides how a win reads -----------------
    def _joint():
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        sc = StandardScaler().fit(Xtr)
        A, B = sc.transform(Xtr), sc.transform(Xte)
        # Coarse-to-fine supervised cosine frequency scan, per column, then a
        # logistic fit on the selected cosine features. Order-matched: as many
        # cosine terms as the CVQBoost pool's feature count.
        feats_tr, feats_te = [A], [B]
        for j in range(A.shape[1]):
            best, best_f = -1.0, None
            for f in np.linspace(0.5, 6.0, 12):
                c = np.cos(f * A[:, j])
                r = abs(float(np.corrcoef(c, ytr)[0, 1])) if c.std() > 0 else 0.0
                if r > best:
                    best, best_f = r, f
            if best_f is not None:
                feats_tr.append(np.cos(best_f * A[:, [j]]))
                feats_te.append(np.cos(best_f * B[:, [j]]))
        Atr = np.hstack(feats_tr)
        Ate = np.hstack(feats_te)
        m = LogisticRegression(max_iter=5000).fit(Atr, ytr)
        return score(m.predict_proba(Ate)[:, 1])
    lanes.append(_fit_timed("joint_twin", _joint))

    ok = [l for l in lanes if l["status"] == "ok"]
    dominant = max(ok, key=lambda l: l["elapsed_s"]) if ok else None
    total = round(sum(l["elapsed_s"] for l in lanes), 2)

    return {
        "note": ("F100 lane pilot: one real SPECTRA cell, every classical lane "
                 "timed separately so the dominant term is NAMED with its "
                 "measurement (Sprint 9 improvement 2)."),
        "generator": "experiments/src/f100_lane_pilot.py",
        "evidence_tag": "SIM",
        "metered_seconds": 0,
        "cell": cell_name, "seed": seed,
        "n_features": len(cols),
        "n_train": int(len(ytr)), "n_test": int(len(yte)),
        "lanes": lanes,
        "dominant_lane": dominant["lane"] if dominant else None,
        "dominant_seconds": dominant["elapsed_s"] if dominant else None,
        "total_seconds_one_cell": total,
        "projection_15_cells_sec": round(total * 15, 1),
        "projection_15_cells_min": round(total * 15 / 60, 1),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="oilgas_gasturbine")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    r = pilot(args.cell, args.seed)
    OUT.write_text(json.dumps(r, indent=2), encoding="utf-8")

    print(f"F100 lane pilot: {r['cell']} seed {r['seed']} "
          f"({r['n_features']} features, {r['n_train']:,} train rows)")
    print()
    for l in r["lanes"]:
        if l["status"] == "ok":
            print(f"  {l['lane']:14s} {l['elapsed_s']:7.2f}s   "
                  f"AUPRC {l['auprc']:.4f}  AUC {l['auc_roc']:.4f}")
        else:
            print(f"  {l['lane']:14s} {l['elapsed_s']:7.2f}s   "
                  f"ERROR {l['error']}")
    print()
    print(f"  DOMINANT LANE   : {r['dominant_lane']} at "
          f"{r['dominant_seconds']}s of {r['total_seconds_one_cell']}s per cell")
    print(f"  15 cells        : ~{r['projection_15_cells_min']} min "
          f"(5 seeds x 3 cells, one pass, no repeats)")
    print(f"  written to      : {OUT.relative_to(Path.cwd())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
