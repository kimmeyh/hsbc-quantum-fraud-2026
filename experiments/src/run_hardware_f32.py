"""F32: persist Dirac-3 predictions on the MIXED pool (block F32, metered).

Why this block exists. Every operating-point figure in the submission is
computed from the exact classical proxy and tagged [SIM], because the Sprint 4
campaign never persisted Dirac-3 solution weights (amendment A9 records how that
was discovered). The substitution is licensed by an aggregate measurement --
hardware minus proxy is -0.0010 AUPRC with the interval containing zero -- but
aggregate AP similarity does NOT establish transaction-level or top-k
equivalence, and an alert budget is a top-k decision. This block persists
weights and per-transaction scores so the operational table can carry [HW].

Why the MIXED pool rather than the frozen one. On the frozen pool the optimizer
demonstrably contributes nothing: the optimum is uniform to seven decimals and
the apparent gain is tie-breaking. Spending metered seconds there would measure
a solver with no work to do. F31 established that the mixed-family pool moves
the optimum genuinely off uniform (L1 0.127, monotone shrinkage response), so
this is the configuration where hardware-versus-proxy agreement is a meaningful
question.

SPEND: team lead pre-approved 40-50 metered device seconds on 2026-09-04,
conditional on the F31 outcome, with no further stop. This runner enforces that
envelope in code: one fit per seed, a hard block cap, and a pre-call projection
so the cap bounds the call it precedes rather than being noticed after the fact.

Usage: python experiments/src/run_hardware_f32.py [--dry-run]
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data
import mechanism_controls as mc
import metrics
import mixed_pool as mp
import qubo_proxy as qp
import store

RESP_DIR = Path(__file__).resolve().parents[1] / "results" / "pools" / "hw_responses"

BLOCK = "F32"
SEEDS = (42, 43, 44, 45, 46, 47, 48, 49, 50, 51)
BLOCK_CAP_S = 50.0          # the TOP of the approved 40-50 s envelope, not above it.
                            # A cap set above the approval could authorize spend the
                            # team lead did not grant, so the code caps at the grant.
EXPECTED_CALL_S = 6.0       # measured 4-5 s/fit; bound the NEXT call
UNPARSEABLE_CALL_CHARGE_S = 10.0   # conservative charge when billing cannot be read
# k=6, NOT mp.K_FEATURES (13). The Dirac-3 FREE TIER refuses any continuous
# degree-2 job above 100 variables, server-side, before billing: a 312-variable
# mixed pool at k=13 was rejected with "Number of variables '312' ... greater
# than the free-tier device limit '100'". Four families at k=6 give 60
# variables, which fits, and a seed-42 check confirms the optimizer still does
# real work there (L1 from uniform 0.0204, max weight 1.040x, AP +0.0036).
K_FEATURES = 6
SCHEDULE = 2


def _load_env() -> None:
    env = Path(__file__).resolve().parents[2] / ".env"
    if not env.exists():
        raise SystemExit(".env missing; ADR-0011 credentials required")
    for line in env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def _metered(resp) -> float | None:
    """Recursive search for the device-usage key; regex fallback on repr.

    A None here is NOT free: the caller charges UNPARSEABLE_CALL_CHARGE_S and
    flags the row, because a spend guard that reads unparseable billing as zero
    goes blind (Sprint 4 review finding, amendment A8).
    """
    keys = ("device_usage_s", "device_usage", "total_device_usage_s", "runtime_s")

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in keys and isinstance(v, (int, float)):
                    return float(v)
                r = walk(v)
                if r is not None:
                    return r
        elif isinstance(o, (list, tuple)):
            for v in o:
                r = walk(v)
                if r is not None:
                    return r
        return None

    got = walk(resp if isinstance(resp, (dict, list, tuple)) else getattr(resp, "__dict__", {}))
    if got is not None:
        return got
    import re
    m = re.search(r"device_usage_s['\"]?\s*[:=]\s*([0-9.]+)", repr(resp))
    return float(m.group(1)) if m else None


FREE_TIER_MAX_VARS = 100    # established empirically 2026-09-05 (amendment A12)


def check_free_tier_size(n_variables: int) -> None:
    """Refuse locally what the device would refuse anyway (Sprint 6 improvement 3).

    Dirac-3's free tier rejects any continuous degree-2 job above 100 variables,
    server-side. A 312-variable submission came back:

        Number of variables '312' in problem is greater than the free-tier
        device limit '100' for polynomial with degree '2'

    That refusal costs no metered seconds, but it costs a full pool build (about
    two minutes per seed) and it surfaces as an HTTP error mid-campaign rather
    than as a sizing decision at planning time. Compute the count and stop here.
    """
    if n_variables > FREE_TIER_MAX_VARS:
        raise SystemExit(
            f"REFUSING to submit: {n_variables} variables exceeds the free-tier "
            f"limit of {FREE_TIER_MAX_VARS} for continuous degree-2 jobs "
            f"(amendment A12). Reduce k or the family count, or move to a paid "
            f"tier. Four families at k=6 gives 60 variables and fits."
        )


def _spent() -> float:
    if not qp.RESULTS.exists():
        return 0.0
    return sum(r.get("metered_seconds") or 0.0
               for r in json.loads(qp.RESULTS.read_text())["rows"]
               if r.get("block") == BLOCK)


def run_seed(seed: int, dry_run: bool) -> dict:
    from sklearn.metrics import average_precision_score as AP

    df = data.load_ulb()
    split = data.stratified_split(df, seed)
    cols = data.top_k_features(split.X_train, split.y_train, K_FEATURES, seed=seed)
    X_tr = split.X_train[cols].to_numpy(np.float32)
    X_va = split.X_val[cols].to_numpy(np.float32)
    X_te = split.X_test[cols].to_numpy(np.float32)
    y_pm1 = np.where(split.y_train.to_numpy() == 1, 1, -1).astype(np.float64)
    y_va, y_te = split.y_val.to_numpy(), split.y_test.to_numpy()

    pool = mp.build_mixed(X_tr, X_va, X_te, y_pm1, SCHEDULE)
    H_tr, H_va, H_te = pool["H_tr"], pool["H_va"], pool["H_te"]
    n = H_tr.shape[0]
    if not dry_run:
        check_free_tier_size(n)
    lam = qp.LAMBDA_MULT * len(y_pm1)

    # exact classical solve of the identical Hamiltonian: the ADR-0002 control
    w_px = mc.solve_weighted(H_tr, y_pm1, lam, np.ones(len(y_pm1)))
    J = (H_tr @ H_tr.T).astype(np.float64) + lam * np.eye(n)
    C = (-2.0 * (H_tr @ y_pm1)).astype(np.float64)
    obj = lambda w: float(w @ J @ w + C @ w)

    if dry_run:
        return {"seed": seed, "n_variables": n, "dry_run": True,
                "proxy_objective": obj(w_px),
                "proxy_ap_test": float(AP(y_te, np.clip((w_px @ H_te + 1) / 2, 0, 1)))}

    # Use QBoostClassifier's own fit path -- the SAME metered call the frozen
    # campaign used -- but install the pre-built mixed pool instead of letting
    # it build a single-family one. Overriding the builder (rather than calling
    # the solver directly) keeps Hamiltonian construction, sum_constraint and
    # billing identical to the frozen arm, so hardware-versus-proxy remains a
    # like-for-like comparison.
    from eqc_models.ml.classifierqboost import QBoostClassifier

    families = []
    for fam in mp.FAMILIES:
        c = qp.build_pool(X_tr, y_pm1, schedule=SCHEDULE, weak_type=fam,
                          pair_build="seq")
        families.append((list(c.h_list), list(c.ind_list)))

    class _MixedQBoost(QBoostClassifier):
        def _build_weak_classifiers_sq(self, X, y):   # noqa: N802
            self.h_list, self.ind_list = [], []
            for h, ind in families:
                self.h_list.extend(h)
                self.ind_list.extend(ind)

    cfg = dict(lambda_coef=lam, weak_cls_schedule=SCHEDULE, weak_cls_type="dct",
               weak_cls_params={}, weak_cls_strategy="sequential", **qp.FIXED)
    clf = _MixedQBoost(api_url=os.environ["QCI_API_URL"],
                       api_token=os.environ["QCI_TOKEN"], **cfg)

    t0 = time.time()
    resp = clf.fit(X_tr, y_pm1)          # ONE metered call
    wall = time.time() - t0

    RESP_DIR.mkdir(parents=True, exist_ok=True)
    (RESP_DIR / f"f32_mixed_stratified_{seed}.json").write_text(
        json.dumps(resp, default=str, indent=1))

    energies = np.asarray(resp.get("results", {}).get("energies", []), dtype=float)
    w_hw = np.asarray(clf.params, dtype=np.float64)
    if w_hw.sum() > 0:
        w_hw = w_hw / w_hw.sum()

    metered = _metered(resp)
    if metered is None:
        print(f"    WARNING seed {seed}: billed seconds UNPARSEABLE; charging "
              f"the conservative estimate {UNPARSEABLE_CALL_CHARGE_S}s")

    p_val = np.clip((w_hw @ H_va + 1.0) / 2.0, 0.0, 1.0)
    p_test = np.clip((w_hw @ H_te + 1.0) / 2.0, 0.0, 1.0)

    cfg_hash = store.config_hash({"pool": "mixed", "families": list(mp.FAMILIES),
                                  "k": K_FEATURES, "schedule": SCHEDULE,
                                  "lambda_mult": qp.LAMBDA_MULT, "n_variables": n})
    pred_file = store.save_predictions(cfg_hash, seed, "stratified",
                                       y_va, p_val, y_te, p_test,
                                       arm="cvqboost_hw_mixed")

    px_test = np.clip((w_px @ H_te + 1.0) / 2.0, 0.0, 1.0)
    return {
        "seed": seed,
        "arm": "cvqboost_hw_mixed",
        "block": BLOCK,
        "config": "mixed_free_sched2",
        # cost_analysis and the store BOTH read config_hash; a row that
        # carries only "config" raises KeyError there.
        "config_hash": cfg_hash,
        "pool_variant": "mixed",
        # score_gates keys unknown arms by feature_set, and cost_analysis by
        # pair_build; a row missing either raises KeyError there rather than
        # being skipped, so the gate report cannot regenerate.
        "feature_set": "mixed_k6",
        "pair_build": "seq",
        "dataset": "ulb",
        "protocol": "stratified",
        "evidence_tag": "HW",
        "status": "ok" if metered is not None else "ok_unmetered",
        "metered_seconds": metered if metered is not None else UNPARSEABLE_CALL_CHARGE_S,
        "metered_seconds_parsed": metered is not None,
        "wall_seconds": round(wall, 1),
        "n_variables": n,
        "predictions_file": pred_file,
        "metrics": metrics.summarize(y_te, y_va, p_val, p_test, seed=seed),
        "fidelity": {
            "hw_objective_recomputed": obj(w_hw),
            "proxy_objective": obj(w_px),
            "weight_cosine": float(w_hw @ w_px /
                                   (np.linalg.norm(w_hw) * np.linalg.norm(w_px) + 1e-12)),
            "hw_ap_test": float(AP(y_te, p_test)),
            "proxy_ap_test": float(AP(y_te, px_test)),
            "hw_minus_proxy_ap": float(AP(y_te, p_test) - AP(y_te, px_test)),
            "n_solver_draws": int(len(energies)),
            "energy_spread_pct": float(abs(energies.max() - energies.min()) /
                                       max(abs(energies.min()), 1e-12) * 100.0),
        },
    }


def main() -> int:
    dry = "--dry-run" in sys.argv
    if not dry:
        _load_env()

    print(f"F32: mixed pool, {len(SEEDS)} seeds, cap {BLOCK_CAP_S}s "
          f"({'DRY RUN' if dry else 'METERED'})")
    rows = []
    for seed in SEEDS:
        # _spent() reads results.json, and append_row has ALREADY written every
        # completed fit there, so adding the in-memory rows double-counts. That
        # bug halted the first run at a reported 50.0s when 25.0s had been spent.
        # A cap that overstates spend is the safe direction, but it still loses
        # approved work, so read one source of truth.
        spent = _spent()
        if not dry and spent + EXPECTED_CALL_S >= BLOCK_CAP_S:
            print(f"  STOP before seed {seed}: spent {spent:.1f}s + expected "
                  f"{EXPECTED_CALL_S}s would reach the {BLOCK_CAP_S}s cap")
            break
        r = run_seed(seed, dry)
        rows.append(r)
        if dry:
            print(f"  seed {seed}: {r['n_variables']} vars, proxy AP "
                  f"{r['proxy_ap_test']:.4f}")
        else:
            f = r["fidelity"]
            print(f"  seed {seed}: {r['metered_seconds']:.2f}s  AP hw "
                  f"{f['hw_ap_test']:.4f} px {f['proxy_ap_test']:.4f} "
                  f"delta {f['hw_minus_proxy_ap']:+.4f}  cos {f['weight_cosine']:.4f}")
            store.append_row(r)

    if not dry and rows:
        total = sum(r["metered_seconds"] for r in rows)
        deltas = np.array([r["fidelity"]["hw_minus_proxy_ap"] for r in rows])
        print(f"\n{len(rows)} fits, {total:.1f} metered device seconds")
        print(f"hardware minus proxy AP: mean {deltas.mean():+.4f}, "
              f"range [{deltas.min():+.4f}, {deltas.max():+.4f}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
