"""CVQBoost proxy tuning per PREREGISTRATION section 6 (Sprint 4 Task A / F22; A3, A6).

Runs under WSL with the A3-selected full-pair build (fork-based pool builds).
100 Optuna TPE trials, objective = validation AP on the tuning-seed (42) split;
search space: weak pool composition (type, class weighting, depth), schedule,
k, lambda alpha in {0.5, 1, 2, 4} x n_train; num_samples/relaxation_schedule
FIXED (prereg 6). (k, schedule) pairs above the 949-variable ceiling are pruned.
KNN weak learners are excluded on proxy-cost grounds (O(n^2) prediction per
learner over 170k rows) -- a reported tuning-space deviation.

KNOWN FAILURE MODES / LONG-RUN NOTES:
- 100 trials ~1-3h under WSL; the study lives in a sqlite file and RESUMES if
  killed (optuna load_if_exists). Pool H-matrices are cached on disk per
  (k, schedule, weak config) so lambda-only trials cost seconds.
- Must run under WSL (multi_processing build needs fork). Windows-run = wrong
  build, refused.

Usage (WSL):
  python experiments/src/tune_proxy.py tune [--n-trials 100] [--smoke]
  python experiments/src/tune_proxy.py refit        # tuned_free + tuned_full x 10 seeds
  python experiments/src/tune_proxy.py rank         # ranking table + G0b list
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data                      # noqa: E402
import metrics                   # noqa: E402
import qubo_proxy as qp          # noqa: E402
import store                     # noqa: E402

log = logging.getLogger("frd.tune_proxy")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s")

RESULTS_DIR = qp.RESULTS_DIR
STUDY_DB = RESULTS_DIR / "proxy_tuning.db"
RECORD = RESULTS_DIR / "proxy_tuning.json"
CACHE = RESULTS_DIR / "pools" / "tune_cache"
TUNING_SEED = 42
SEEDS = qp.SEEDS
N_TRIALS = 100
DEVICE_LIMIT = 949
FREE_TIER = 100
K_CHOICES = (5, 9, 13, 17)
LAMBDA_ALPHAS = (0.5, 1.0, 2.0, 4.0)
PAIR_BUILD = "full"              # A3 selection


def _require_wsl():
    if os.name != "posix":
        raise SystemExit("tune_proxy must run under WSL/Linux (full-pair build needs fork)")


def weak_config(trial) -> tuple[str, dict]:
    """Section-6 'weak pool composition' as a tuned choice."""
    wt = trial.suggest_categorical("weak_type", ["dct", "lg", "lda", "xgb"])
    if wt == "dct":
        cw = trial.suggest_categorical("dct_class_weight", ["none", "balanced"])
        depth = trial.suggest_int("dct_max_depth", 1, 3)
        return wt, {"max_depth": depth, "class_weight": None if cw == "none" else "balanced",
                    "random_state": 0}
    if wt == "lg":
        cw = trial.suggest_categorical("lg_class_weight", ["none", "balanced"])
        return wt, {"max_iter": 300, "class_weight": None if cw == "none" else "balanced"}
    if wt == "lda":
        return wt, {}
    spw = trial.suggest_categorical("xgb_scale_pos_weight", ["one", "ratio"])
    return wt, {"max_depth": 2, "n_estimators": 20, "learning_rate": 0.3,
                "n_jobs": 4, "verbosity": 0, "_spw": spw}


def _pool_key(k, schedule, wt, wp) -> str:
    return store.config_hash({"k": k, "schedule": schedule, "wt": wt, "wp": wp,
                              "seed": TUNING_SEED, "pair_build": PAIR_BUILD})


_prep_cache: dict = {}


def _prep(seed: int, k: int):
    key = (seed, k)
    if key not in _prep_cache:
        _prep_cache[key] = qp._prep(seed, k)
    return _prep_cache[key]


def _pool_h(seed, k, schedule, wt, wp, lam_dummy=1.0):
    """H matrices (train/val/test) for a pool; disk-cached per config.
    lambda does not affect the pool, so lambda-only trials hit the cache."""
    CACHE.mkdir(parents=True, exist_ok=True)
    key = _pool_key(k, schedule, wt, wp) + f"_s{seed}"
    f = CACHE / f"{key}.npz"
    split, cols, Xtr, Xva, Xte, y_pm1 = _prep(seed, k)
    if f.exists():
        z = np.load(f)
        return split, cols, z["H_tr"], z["H_va"], z["H_te"], y_pm1, int(z["n_pool"])
    wp_eff = dict(wp)
    if wt == "xgb":
        spw = wp_eff.pop("_spw")
        ratio = float((y_pm1 == -1).sum() / max((y_pm1 == 1).sum(), 1))
        wp_eff["scale_pos_weight"] = ratio if spw == "ratio" else 1.0
    clf = qp.build_pool(Xtr, y_pm1, schedule, wt, PAIR_BUILD, weak_params=wp_eff,
                        lambda_coef=lam_dummy)
    H_tr, H_va, H_te = (qp.h_matrix(clf, X) for X in (Xtr, Xva, Xte))
    np.savez_compressed(f, H_tr=H_tr, H_va=H_va, H_te=H_te, n_pool=len(clf.h_list))
    return split, cols, H_tr, H_va, H_te, y_pm1, len(clf.h_list)


def objective(trial):
    k = trial.suggest_categorical("k", list(K_CHOICES))
    schedule = trial.suggest_int("schedule", 1, 3)
    n_vars = data.qubo_vars(k, schedule, PAIR_BUILD)
    trial.set_user_attr("n_vars", n_vars)
    if n_vars > DEVICE_LIMIT:
        import optuna
        raise optuna.TrialPruned(f"{n_vars} vars > {DEVICE_LIMIT}")
    wt, wp = weak_config(trial)
    alpha = trial.suggest_categorical("lambda_alpha", list(LAMBDA_ALPHAS))
    t0 = time.time()
    split, cols, H_tr, H_va, H_te, y_pm1, n_pool = _pool_h(TUNING_SEED, k, schedule, wt, wp)
    lam = alpha * len(y_pm1)
    w = qp.solve_simplex_qp(H_tr, y_pm1, lam)
    s_va = w @ H_va
    val_ap = float(metrics.average_precision_score(split.y_val.to_numpy(), s_va))
    health = metrics.score_health(np.clip((s_va + 1) / 2, 0, 1))
    trial.set_user_attr("n_pool", n_pool)
    trial.set_user_attr("health_warn", health["warn"])
    trial.set_user_attr("mode_share", health["mode_share"])
    trial.set_user_attr("n_distinct", health["n_distinct"])
    trial.set_user_attr("free_tier_eligible", n_vars <= FREE_TIER)
    trial.set_user_attr("wall_s", round(time.time() - t0, 1))
    trial.set_user_attr("config_hash", store.config_hash(
        {"k": k, "schedule": schedule, "wt": wt, "wp": wp, "alpha": alpha,
         "pair_build": PAIR_BUILD, "fixed": qp.FIXED}))
    log.info("[TUNE] trial %d k=%d sched=%d %s alpha=%.1f vars=%d val_ap=%.4f "
             "health_warn=%s (%.0fs)", trial.number, k, schedule, wt, alpha, n_vars,
             val_ap, health["warn"], time.time() - t0)
    return val_ap


def _params_of(t) -> dict:
    p = dict(t.params)
    return p


def cmd_tune(args):
    _require_wsl()
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    RESULTS_DIR.mkdir(exist_ok=True)
    study = optuna.create_study(direction="maximize", study_name="cvqboost_proxy_s6",
                                storage=f"sqlite:///{STUDY_DB}", load_if_exists=True,
                                sampler=optuna.samplers.TPESampler(seed=TUNING_SEED))
    n = 2 if args.smoke else args.n_trials
    done = len([t for t in study.trials if t.state.is_finished()])
    remaining = max(0, n - done)
    log.info("[TUNE] study has %d finished trials; running %d more", done, remaining)
    if remaining:
        study.optimize(objective, n_trials=remaining, show_progress_bar=False)
    _write_record(study)


def _write_record(study):
    rows = []
    for t in study.trials:
        if t.state.name != "COMPLETE":
            continue
        rows.append({"number": t.number, "val_ap": t.value, "params": _params_of(t),
                     **{k: v for k, v in t.user_attrs.items()}})
    rows.sort(key=lambda r: -r["val_ap"])
    free = [r for r in rows if r.get("free_tier_eligible")]
    rec = {"study": "cvqboost_proxy_s6", "tuning_seed": TUNING_SEED,
           "n_complete": len(rows), "pair_build": PAIR_BUILD,
           "knn_excluded_reason": "O(n^2) prediction per learner over 170k rows; proxy cost infeasible",
           "best_overall": rows[0] if rows else None,
           "best_free_tier": free[0] if free else None,
           "trials": rows}
    store.atomic_write_json(RECORD, rec)
    log.info("[TUNE] record written: %d complete; best overall %.4f; best free-tier %s",
             len(rows), rows[0]["val_ap"] if rows else float("nan"),
             f"{free[0]['val_ap']:.4f}" if free else "none")


def _refit_one(label: str, cfg: dict, seed: int):
    p = cfg["params"]
    k, schedule, alpha = p["k"], p["schedule"], p["lambda_alpha"]
    wt = p["weak_type"]
    wp = {"dct": lambda: {"max_depth": p["dct_max_depth"],
                          "class_weight": None if p["dct_class_weight"] == "none" else "balanced",
                          "random_state": 0},
          "lg": lambda: {"max_iter": 300,
                         "class_weight": None if p["lg_class_weight"] == "none" else "balanced"},
          "lda": lambda: {},
          "xgb": lambda: {"max_depth": 2, "n_estimators": 20, "learning_rate": 0.3,
                          "n_jobs": 4, "verbosity": 0, "_spw": p["xgb_scale_pos_weight"]}}[wt]()
    t0 = time.strftime("%Y-%m-%dT%H:%M:%S")
    split, cols, H_tr, H_va, H_te, y_pm1, n_pool = _pool_h(seed, k, schedule, wt, wp)
    w = qp.solve_simplex_qp(H_tr, y_pm1, alpha * len(y_pm1))
    p_val = np.clip((w @ H_va + 1) / 2, 0, 1)
    p_test = np.clip((w @ H_te + 1) / 2, 0, 1)
    m = metrics.summarize(split.y_test.to_numpy(), split.y_val.to_numpy(), p_val, p_test, seed=seed)
    row = {"arm": "cvqboost_proxy", "dataset": "ulb", "protocol": "stratified", "seed": seed,
           "config": label, "pool_variant": wt, "pair_build": PAIR_BUILD,
           "n_weak_classifiers": int(n_pool), "tuned_params": p,
           "config_hash": cfg["config_hash"], "features_used": cols, "metrics": m,
           "val_auprc": float(metrics.average_precision_score(split.y_val.to_numpy(), p_val)),
           "evidence_tag": "SIM", "metered_seconds": 0, "retry_count": 0,
           "timestamps": {"started": t0, "finished": time.strftime("%Y-%m-%dT%H:%M:%S")}}
    store.append_row(row)
    log.info("[REFIT] %s seed=%d %s k=%d s=%d a=%.1f test_ap=%.4f val_ap=%.4f health_warn=%s",
             label, seed, wt, k, schedule, alpha, m["auprc"], row["val_auprc"],
             m["score_health"]["warn"])


def cmd_refit(args):
    _require_wsl()
    rec = json.loads(RECORD.read_text())
    done = qp._done_keys()
    labels = [("tuned_free", rec["best_free_tier"]), ("tuned_full", rec["best_overall"])]
    if (rec["best_free_tier"] and rec["best_overall"]
            and rec["best_free_tier"]["config_hash"] == rec["best_overall"]["config_hash"]):
        labels = labels[:1]   # identical config: one label, no duplicate rows
    for label, cfg in labels:
        if cfg is None:
            log.warning("[REFIT] no %s config", label); continue
        for seed in SEEDS:
            if ("cvqboost_proxy", label, cfg["params"]["weak_type"], PAIR_BUILD, seed) in done:
                continue
            _refit_one(label, cfg, seed)


def cmd_rank(args):
    rec = json.loads(RECORD.read_text())
    # The preregistered STARTING config (free, dct, full-pair; unlimited-depth
    # trees, alpha 2) is a candidate by definition: pull its tuning-seed val AP
    # from the existing results.json rows.
    start_rows = [r for r in json.loads(qp.RESULTS.read_text())["rows"]
                  if r["arm"] == "cvqboost_proxy" and r.get("config") == "free"
                  and r.get("pool_variant") == "dct" and r.get("pair_build") == PAIR_BUILD
                  and r["seed"] == TUNING_SEED]
    trials = list(rec["trials"])
    if start_rows:
        s = start_rows[0]
        h = s["metrics"].get("score_health", {})
        trials.append({"number": -1, "val_ap": s["val_auprc"],
                       "params": {"k": 13, "schedule": 2, "weak_type": "dct",
                                  "dct_max_depth": "none", "dct_class_weight": "none",
                                  "lambda_alpha": 2.0},
                       "n_vars": data.qubo_vars(13, 2, PAIR_BUILD), "n_pool": s["n_weak_classifiers"],
                       "health_warn": h.get("warn", True), "mode_share": h.get("mode_share"),
                       "n_distinct": h.get("n_distinct"), "free_tier_eligible": True,
                       "config_hash": s["config_hash"], "note": "preregistered starting config"})
    trials.sort(key=lambda r: -r["val_ap"])
    free = [r for r in trials if r.get("free_tier_eligible")]
    # one row per distinct config_hash, best value first
    seen, ranked = set(), []
    for r in free:
        if r["config_hash"] in seen:
            continue
        seen.add(r["config_hash"]); ranked.append(r)
    g0b = ranked[:3] + ranked[-2:] if len(ranked) >= 5 else ranked
    out = {"free_tier_ranking": ranked, "g0b_configs": g0b,
           "note": "G0b = top-3 + bottom-2 free-tier-eligible configs by proxy validation AP (prereg 3)"}
    store.atomic_write_json(RESULTS_DIR / "proxy_ranking.json", out)
    lines = ["| rank | val AP | k | sched | weak | alpha | vars | health warn | config_hash |",
             "|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(ranked, 1):
        p = r["params"]
        lines.append(f"| {i} | {r['val_ap']:.4f} | {p['k']} | {p['schedule']} | {p['weak_type']} "
                     f"| {p['lambda_alpha']} | {r['n_vars']} | {r['health_warn']} | {r['config_hash']} |")
    (RESULTS_DIR / "proxy_ranking.md").write_text("\n".join(lines) + "\n")
    log.info("[RANK] %d free-tier configs ranked; G0b list has %d", len(ranked), len(g0b))


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_t = sub.add_parser("tune"); p_t.add_argument("--n-trials", type=int, default=N_TRIALS)
    p_t.add_argument("--smoke", action="store_true")
    sub.add_parser("refit"); sub.add_parser("rank")
    args = ap.parse_args()
    {"tune": cmd_tune, "refit": cmd_refit, "rank": cmd_rank}[args.cmd](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
