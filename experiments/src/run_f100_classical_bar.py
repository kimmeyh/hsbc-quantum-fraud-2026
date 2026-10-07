"""F100: the complete classical bar on identical SPECTRA features.

The full grid the pilot sized: five classical lanes x 3 frozen cells x 5 seeds.
LogReg, GAM, GA2M, HGB and an order-matched JOINT twin, each given the SAME
features the CVQBoost arm gets, on the same splits and seeds.

WHY THE JOINT TWIN DECIDES HOW A RESULT READS. `docs/references.md` records the
Fourier Wall paper showing a quantum win of 0.758 against 0.721 that a JOINT
twin reads classically at 0.968. A bar without the twin is how a
feature-engineering gain gets reported as a quantum gain.

THREE OUTCOMES, ALL REPORTABLE (F100's card): the gain survives the complete
bar; the gain vanishes against JOINT; or every lane gains from the phase
features, so the feature engineering is the contribution.

Sizing is measured, not assumed (`docs/F100_LANE_PILOT.md`): 3.77 s per cell,
dominated by HGB at 2.34 s. Fifteen cells is under a minute, against the ~6
hours F100's `[no-history]` card estimated. Zero metered seconds -- every lane
is classical.

Paired comparison discipline: the per-seed differences are what carry the
signal. B2's +0.0256 gain was invisible unpaired -- it sat inside a
seed-to-seed standard deviation of 0.030 and read as noise (amendment A24). So
this reports per-seed deltas and their bootstrap CI, not just arm means.

Run:
  <venv python> experiments/src/run_f100_classical_bar.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f100_lane_pilot as pilot_mod            # noqa: E402
import spectra_segment as ss                   # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "results" / "f100_classical_bar.json"
SEEDS = (42, 43, 44, 45, 46)


def _proxy_rows() -> dict:
    """The CVQBoost proxy AUPRC per (dataset, seed), for the paired delta.

    `[PROJ]`, not device. Named explicitly so no reader can mistake the
    comparison for a hardware result.
    """
    p = Path(__file__).resolve().parents[1] / "results" / "spectra_proxy_dry_run.json"
    if not p.exists():
        return {}
    rows = json.loads(p.read_text(encoding="utf-8"))
    rows = rows if isinstance(rows, list) else rows.get("rows", [])
    out = {}
    for r in rows:
        ov = r.get("overall") or {}
        if ov.get("auprc") is not None:
            out[(r["dataset"], r["seed"])] = float(ov["auprc"])
    return out


def _bootstrap_ci(deltas: list[float], n: int = 10000,
                  seed: int = 42) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    a = np.asarray(deltas, dtype="float64")
    if len(a) < 2:
        return (float("nan"), float("nan"))
    means = [float(rng.choice(a, size=len(a), replace=True).mean())
             for _ in range(n)]
    return (round(float(np.percentile(means, 2.5)), 4),
            round(float(np.percentile(means, 97.5)), 4))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="*", default=list(SEEDS))
    args = ap.parse_args()

    proxy = _proxy_rows()
    cells = []
    for cell in ss.FROZEN_CELLS:
        name = cell["dataset"].replace("spectra_", "")
        for seed in args.seeds:
            r = pilot_mod.pilot(name, seed)
            r["dataset"] = cell["dataset"]
            r["config_hash"] = cell["config_hash"]
            cells.append(r)
            ok = {l["lane"]: l.get("auprc") for l in r["lanes"]
                  if l["status"] == "ok"}
            best = max(ok, key=lambda k: ok[k]) if ok else "?"
            print(f"  {name:18s} s{seed}  best={best} "
                  f"{ok.get(best, float('nan')):.4f}", flush=True)

    # Per-lane paired deltas against the CVQBoost proxy, per cell.
    by_cell = {}
    for r in cells:
        key = r["dataset"]
        by_cell.setdefault(key, []).append(r)

    summary = {}
    for dataset, rows in by_cell.items():
        lanes = {}
        for lane in ("logreg", "gam_additive", "ga2m", "hgb", "joint_twin"):
            deltas, lane_aps = [], []
            for r in rows:
                got = {l["lane"]: l.get("auprc") for l in r["lanes"]
                       if l["status"] == "ok"}
                ap_lane = got.get(lane)
                ap_prox = proxy.get((dataset, r["seed"]))
                if ap_lane is None:
                    continue
                lane_aps.append(ap_lane)
                if ap_prox is not None:
                    deltas.append(ap_lane - ap_prox)
            if not lane_aps:
                continue
            lo, hi = _bootstrap_ci(deltas) if len(deltas) > 1 else (
                float("nan"), float("nan"))
            lanes[lane] = {
                "mean_auprc": round(float(np.mean(lane_aps)), 4),
                "sd_auprc": round(float(np.std(lane_aps, ddof=1)), 4)
                if len(lane_aps) > 1 else None,
                "n_seeds": len(lane_aps),
                "mean_delta_vs_cvqboost_proxy":
                    round(float(np.mean(deltas)), 4) if deltas else None,
                "delta_ci95": [lo, hi] if deltas else None,
                "seeds_favoring_lane":
                    int(sum(1 for d in deltas if d > 0)) if deltas else None,
                "n_paired": len(deltas),
            }
        beats = [l for l, v in lanes.items()
                 if (v["mean_delta_vs_cvqboost_proxy"] or 0) > 0]
        summary[dataset] = {"lanes": lanes, "lanes_beating_proxy": sorted(beats)}

    result = {
        "note": ("F100: the complete classical bar on identical SPECTRA "
                 "features. Five lanes x 3 frozen cells x 5 seeds. The "
                 "comparator is the CVQBoost classical PROXY, evidence tag "
                 "PROJ -- NOT a Dirac-3 result. Overall metrics, not "
                 "in-segment: H5 is F90's claim, not this card's."),
        "generator": "experiments/src/run_f100_classical_bar.py",
        "evidence_tag": "SIM",
        "metered_seconds": 0,
        "comparator": "cvqboost classical proxy [PROJ]",
        "seeds": list(args.seeds),
        "n_cells": len(cells),
        "summary": summary,
        "cells": cells,
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print()
    for dataset, s in sorted(summary.items()):
        print(f"  {dataset}")
        for lane, v in sorted(s["lanes"].items(),
                              key=lambda kv: -(kv[1]["mean_auprc"])):
            d = v["mean_delta_vs_cvqboost_proxy"]
            ci = v["delta_ci95"]
            tag = "" if d is None else (
                f"  delta {d:+.4f} CI [{ci[0]:+.4f}, {ci[1]:+.4f}]  "
                f"{v['seeds_favoring_lane']}/{v['n_paired']} seeds")
            print(f"    {lane:14s} AUPRC {v['mean_auprc']:.4f} "
                  f"(sd {v['sd_auprc']}){tag}")
        print(f"    lanes beating the proxy: "
              f"{s['lanes_beating_proxy'] or 'none'}")
        print()
    print(f"  written to {OUT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
