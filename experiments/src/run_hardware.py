"""Metered Dirac-3 hardware runner: blocks B1 + G0b (Sprint 4 Task C / F2; #19).

CRITERION H: this script consumes metered QPU seconds. It runs ONLY on explicit
team-lead approval of docs/HARDWARE_REQUEST_B1_G0b.md (approved 2026-09-03,
"approved"), with the block, call count, expected seconds and hashes stated
immediately before launch. Every fit = one metered call.

Protocol (frozen): identical-config retry, at most 2 retries, counts recorded;
third failure = cell reported failed. No config-mutating backoff. Pool identity:
the hardware fit builds the SAME full-pair pool (A3) the proxy used; after the
fit the proxy solves the identical Hamiltonian so each [HW] row carries a
fidelity record (hardware energy vs exact proxy optimum, weight cosine).

Credentials (ADR-0011): repo-root .env with QCI_API_URL and QCI_TOKEN; loaded
into the environment at startup, never printed. Raw responses are saved under
experiments/results/pools/hw_responses/ (gitignored: may carry job/account ids).

KNOWN FAILURE MODES: free-tier rejection ("number of variables" ...) -> cell
FAILS per F18 disposition 5 (no backoff); network errors -> retry rule; the
metered-seconds key is discovered from the first response (see _metered).

Usage (WSL):
  python experiments/src/run_hardware.py plan            # prints the call plan, no calls
  python experiments/src/run_hardware.py first           # ONE call: G0b config 1, seed 42
  python experiments/src/run_hardware.py g0b             # remaining G0b calls
  python experiments/src/run_hardware.py b1              # 22 B1 calls (checkpointed)
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
import traceback
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data                      # noqa: E402
import metrics                   # noqa: E402
import qubo_proxy as qp          # noqa: E402
import store                     # noqa: E402

log = logging.getLogger("frd.hardware")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s")

REPO = Path(__file__).resolve().parents[2]
RESP_DIR = qp.RESULTS_DIR / "pools" / "hw_responses"
RANKING = qp.RESULTS_DIR / "proxy_ranking.json"
SEEDS = qp.SEEDS
PAIR_BUILD = "full"
MAX_RETRIES = 2
BLOCK_CAP_S = {"B1": 220.0, "G0b": 70.0}     # 2x the request's expected upper bound
EXPECTED_CALL_S = 6.0                        # measured 4-5 s/fit; bound the NEXT call
UNPARSEABLE_CALL_CHARGE_S = 10.0             # conservative charge when billing is unreadable
TUNING_SEED = 42

B1_VARIANTS = [
    {"label": "hw_b1_dct", "k": 13, "schedule": 2, "wt": "dct", "wp": {}, "alpha": 2.0,
     "proxy_hash": "640ed4cf9c46ea4b"},
    {"label": "hw_b1_lg", "k": 9, "schedule": 2, "wt": "lg",
     "wp": {"max_iter": 300, "class_weight": "balanced"}, "alpha": 0.5,
     "proxy_hash": "bf9e473250b773fa"},
]


def verify_proxy_hashes() -> None:
    """B1 hashes are literals; a re-run tuning study would silently make them
    stale, and config_hash is the field every reported number traces by.
    Recompute from the live ranking/results and refuse to run on a mismatch."""
    if not RANKING.exists():
        log.warning("[HW] no proxy_ranking.json; cannot verify B1 hashes")
        return
    known = {c["config_hash"] for c in json.loads(RANKING.read_text())["free_tier_ranking"]}
    if qp.RESULTS.exists():
        known |= {r.get("config_hash") for r in json.loads(qp.RESULTS.read_text())["rows"]
                  if r.get("arm") == "cvqboost_proxy"}
    missing = [v["proxy_hash"] for v in B1_VARIANTS if v["proxy_hash"] not in known]
    if missing:
        raise SystemExit(
            "FATAL: B1 proxy_hash values not found in the current ranking/results: "
            f"{missing}. The tuning study has changed; re-derive B1_VARIANTS before "
            "spending metered seconds.")
    log.info("[HW] B1 proxy hashes verified against the live ranking")


def _load_env():
    env = REPO / ".env"
    if not env.exists():
        raise SystemExit("FATAL: .env missing (QCI_API_URL, QCI_TOKEN); see ADR-0011")
    for line in env.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    # ForrierWall convention: QCI_API_KEY is accepted as the token (never printed).
    if not os.environ.get("QCI_TOKEN") and os.environ.get("QCI_API_KEY"):
        os.environ["QCI_TOKEN"] = os.environ["QCI_API_KEY"]
    for k in ("QCI_API_URL", "QCI_TOKEN"):
        if not os.environ.get(k):
            raise SystemExit(f"FATAL: {k} not set (QCI_API_KEY accepted as alias)")


def _require_wsl():
    if os.name != "posix":
        raise SystemExit("run under WSL (full-pair build needs fork)")


def _metered(resp) -> float | None:
    """Recursive search for the device-usage key in the response."""
    keys = ("device_usage_s", "device_usage", "total_device_usage_s", "runtime_s", "run_time")
    found = []

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in keys and isinstance(v, (int, float)):
                    found.append(float(v))
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(resp)
    if found:
        return max(found)
    # eqc-models returns a SolutionResults object (not a dict); its repr carries
    # the billed field 'device_usage_s': N (verified on the first G0b call).
    m = re.search(r"'device_usage_s':\s*([0-9.]+)", repr(resp))
    return float(m.group(1)) if m else None


def _wp_eff(wt, wp, y_pm1):
    wp = dict(wp)
    if wt == "xgb":
        spw = wp.pop("_spw", "one")
        ratio = float((y_pm1 == -1).sum() / max((y_pm1 == 1).sum(), 1))
        wp["scale_pos_weight"] = ratio if spw == "ratio" else 1.0
    return wp


def _cells(block: str):
    """Yield call specs. Each: dict(block, label, wt, wp, k, schedule, alpha, seed, protocol, proxy_hash)."""
    if block == "G0b":
        rank = json.loads(RANKING.read_text())
        for i, c in enumerate(rank["g0b_configs"], 1):
            p = c["params"]; wt = p["weak_type"]
            wp = {"dct": {"max_depth": p.get("dct_max_depth"),
                          "class_weight": None if p.get("dct_class_weight", "none") == "none" else "balanced",
                          "random_state": 0} if p.get("dct_max_depth") not in (None, "none") else {},
                  "lg": {"max_iter": 300,
                         "class_weight": None if p.get("lg_class_weight", "none") == "none" else "balanced"},
                  "lda": {},
                  "xgb": {"max_depth": 2, "n_estimators": 20, "learning_rate": 0.3, "n_jobs": 4,
                          "verbosity": 0, "_spw": p.get("xgb_scale_pos_weight", "one")}}[wt]
            yield dict(block="G0b", label=f"hw_g0b_{i}", wt=wt, wp=wp, k=p["k"],
                       schedule=p["schedule"], alpha=p["lambda_alpha"], seed=TUNING_SEED,
                       protocol="stratified", proxy_hash=c["config_hash"],
                       proxy_val_ap=c["val_ap"], rank=i)
    else:
        for v in B1_VARIANTS:
            for seed in SEEDS:
                yield dict(block="B1", seed=seed, protocol="stratified", **v)
            yield dict(block="B1", seed=TUNING_SEED, protocol="temporal", **v)


def _done():
    if not qp.RESULTS.exists():
        return set()
    return {(r["arm"], r.get("config"), r["seed"], r.get("protocol"))
            for r in json.loads(qp.RESULTS.read_text())["rows"]}


def _spent(block: str) -> float:
    if not qp.RESULTS.exists():
        return 0.0
    return sum(r.get("metered_seconds") or 0.0 for r in json.loads(qp.RESULTS.read_text())["rows"]
               if r["arm"] == "cvqboost_hw" and r.get("block") == block)


def _prep(spec):
    df = data.load_ulb().drop_duplicates().reset_index(drop=True)
    split = data.stratified_split(df, spec["seed"]) if spec["protocol"] == "stratified" \
        else data.temporal_split(df)
    cols = data.top_k_features(split.X_train, split.y_train, spec["k"], seed=spec["seed"])
    Xtr = split.X_train[cols].to_numpy(np.float32)
    Xva = split.X_val[cols].to_numpy(np.float32)
    Xte = split.X_test[cols].to_numpy(np.float32)
    y_pm1 = np.where(split.y_train.to_numpy() == 1, 1, -1)
    return split, cols, Xtr, Xva, Xte, y_pm1


def run_cell(spec) -> dict:
    from eqc_models.ml.classifierqboost import QBoostClassifier
    split, cols, Xtr, Xva, Xte, y_pm1 = _prep(spec)
    lam = spec["alpha"] * len(y_pm1)
    cfg = dict(lambda_coef=lam, weak_cls_schedule=spec["schedule"], weak_cls_type=spec["wt"],
               weak_cls_params=_wp_eff(spec["wt"], spec["wp"], y_pm1),
               weak_cls_strategy="multi_processing", **qp.FIXED)
    n_vars = data.qubo_vars(spec["k"], spec["schedule"], PAIR_BUILD)
    t0 = time.strftime("%Y-%m-%dT%H:%M:%S")
    retries, resp, err = 0, None, None
    while retries <= MAX_RETRIES:
        clf = QBoostClassifier(api_url=os.environ["QCI_API_URL"],
                               api_token=os.environ["QCI_TOKEN"], **cfg)
        for k, v in cfg.items():
            assert getattr(clf, k) == v, f"constructed attr mismatch: {k}"
        try:
            resp = clf.fit(Xtr, y_pm1)          # ONE metered call
            break
        except Exception as e:                  # noqa: BLE001
            err = f"{type(e).__name__}: {str(e)[:300]}"
            log.error("[HW] %s seed=%d attempt %d failed: %s", spec["label"], spec["seed"], retries + 1, err)
            msg = str(e).lower()
            if ("number of variables" in msg or "variable" in msg and "limit" in msg
                    or "free-tier" in msg or "free tier" in msg):
                retries += 1                     # record the attempt that was made
                break                            # sizing error: no retry (F18 disposition 5)
            retries += 1
            time.sleep(5)
    # temporal_split ignores the seed (Split.seed is None); recording 42 would
    # misrepresent provenance and let a second temporal seed bypass _done().
    row_seed = spec["seed"] if spec["protocol"] == "stratified" else None
    row = {"arm": "cvqboost_hw", "dataset": "ulb", "protocol": spec["protocol"], "seed": row_seed,
           "block": spec["block"], "config": spec["label"], "pool_variant": spec["wt"],
           "pair_build": PAIR_BUILD, "n_vars_expected": n_vars, "config_hash": spec["proxy_hash"],
           "hw_config": {k: (v if k != "weak_cls_params" else dict(v)) for k, v in cfg.items()},
           "features_used": cols, "evidence_tag": "HW", "retry_count": retries,
           "timestamps": {"started": t0, "finished": None}}
    if resp is None:
        row.update({"status": "failed", "error": err, "metered_seconds": None, "metrics": None})
        row["timestamps"]["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        store.append_row(row)
        return row
    RESP_DIR.mkdir(parents=True, exist_ok=True)
    (RESP_DIR / f"{spec['label']}_{spec['protocol']}_{spec['seed']}.json").write_text(
        json.dumps(resp, default=str, indent=1))
    metered = _metered(resp)
    if metered is None:
        # A vendor response we cannot bill from must NEVER count as 0.0 spend:
        # _spent() would go blind and the block cap could not fire. Charge the
        # conservative per-call estimate and flag the row for audit.
        log.error("[HW] %s seed=%d: billed seconds UNPARSEABLE; charging the "
                  "conservative estimate %.1f s and flagging the row",
                  spec["label"], spec["seed"], UNPARSEABLE_CALL_CHARGE_S)
    energies = resp.get("results", {}).get("energies", [])
    # --- fidelity: exact proxy on the identical Hamiltonian ---
    H_tr = qp.h_matrix(clf, Xtr)
    J = (H_tr @ H_tr.T).astype(np.float64) + lam * np.eye(H_tr.shape[0])
    Cv = -2.0 * H_tr @ y_pm1.astype(np.float64)
    w_hw = np.asarray(clf.params, dtype=np.float64)
    w_px = qp.solve_simplex_qp(H_tr, y_pm1, lam)
    obj = lambda w: float(w @ J @ w + Cv @ w)
    cos = float(w_hw @ w_px / (np.linalg.norm(w_hw) * np.linalg.norm(w_px) + 1e-12))
    # --- scores ---
    p_val = np.clip((clf.predict_raw(Xva) + 1.0) / 2.0, 0.0, 1.0)
    p_test = np.clip((clf.predict_raw(Xte) + 1.0) / 2.0, 0.0, 1.0)
    m = metrics.summarize(split.y_test.to_numpy(), split.y_val.to_numpy(), p_val, p_test, seed=spec["seed"])
    pred_file = store.save_predictions(spec["proxy_hash"], row_seed, spec["protocol"],
                                       split.y_val.to_numpy(), p_val,
                                       split.y_test.to_numpy(), p_test,
                                       arm="cvqboost_hw")
    s_px_val = np.clip((w_px @ qp.h_matrix(clf, Xva) + 1.0) / 2.0, 0.0, 1.0)
    row.update({
        "status": "ok" if metered is not None else "ok_unmetered",
        "predictions_file": pred_file,
        "metered_seconds": metered if metered is not None else UNPARSEABLE_CALL_CHARGE_S,
        "metered_seconds_parsed": metered is not None,
        "n_weak_classifiers": len(clf.h_list),
        "metrics": m,
        "val_auprc": float(metrics.average_precision_score(split.y_val.to_numpy(), p_val)),
        "fidelity": {"hw_min_energy": float(min(energies)) if len(energies) else None,
                     "hw_objective_recomputed": obj(w_hw), "proxy_objective": obj(w_px),
                     "weight_cosine": cos, "hw_weight_sum": float(w_hw.sum()),
                     "proxy_val_auprc_same_pool": float(metrics.average_precision_score(
                         split.y_val.to_numpy(), s_px_val))},
        "energies_n": len(energies),
    })
    row["timestamps"]["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    store.append_row(row)
    log.info("[HW] %s %s seed=%d vars=%d metered=%s test_ap=%.4f val_ap=%.4f cos(w_hw,w_px)=%.4f "
             "obj_hw=%.6g obj_px=%.6g retries=%d", spec["label"], spec["protocol"], spec["seed"],
             len(clf.h_list), metered, m["auprc"], row["val_auprc"], cos, obj(w_hw), obj(w_px), retries)
    return row


def run_block(block: str, only_first: bool = False):
    _require_wsl(); _load_env()
    if block == "B1":
        verify_proxy_hashes()
    done = _done()
    specs = list(_cells(block))
    if only_first:
        specs = specs[:1]
    for spec in specs:
        key = ("cvqboost_hw", spec["label"],
               spec["seed"] if spec["protocol"] == "stratified" else None,
               spec["protocol"])
        if key in done:
            log.info("[HW] %s exists, skipping", key); continue
        spent = _spent(block)
        projected = spent + EXPECTED_CALL_S
        if projected >= BLOCK_CAP_S[block]:
            log.error("[HW] block %s: spend %.1f s + one call (%.1f s) would reach the "
                      "%.0f s cap -- STOPPING BEFORE the call", block, spent,
                      EXPECTED_CALL_S, BLOCK_CAP_S[block])
            return
        log.info("[HW] CALL %s/%s seed=%d %s k=%d s=%d a=%.1f hash=%s (block spend so far %.1f s)",
                 block, spec["label"], spec["seed"], spec["protocol"], spec["k"], spec["schedule"],
                 spec["alpha"], spec["proxy_hash"], spent)
        try:
            run_cell(spec)
        except Exception:                        # noqa: BLE001
            # The metered call may already have been made and billed; abandoning
            # the block would waste the remaining approved calls. Record and go on.
            log.error("[HW] post-call error on %s seed=%s (call may have been billed): %s",
                      spec["label"], spec["seed"], traceback.format_exc()[-800:])
            continue
    log.info("[HW] block %s done; total metered %.1f s", block, _spent(block))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "first", "g0b", "b1"])
    args = ap.parse_args()
    if args.cmd == "plan":
        for b in ("G0b", "B1"):
            specs = list(_cells(b))
            print(f"{b}: {len(specs)} calls")
            for s in specs:
                print(f"  {s['label']} {s['protocol']} seed={s['seed']} {s['wt']} k={s['k']} s={s['schedule']} "
                      f"a={s['alpha']} vars={data.qubo_vars(s['k'], s['schedule'], PAIR_BUILD)} hash={s['proxy_hash']}")
        return 0
    if args.cmd == "first":
        run_block("G0b", only_first=True)
    elif args.cmd == "g0b":
        run_block("G0b")
    else:
        run_block("B1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
