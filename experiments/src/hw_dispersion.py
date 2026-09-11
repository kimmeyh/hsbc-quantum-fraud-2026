"""Hardware solution dispersion across Dirac-3 samples (Sprint 5, review response).

QCi documents Dirac-3 as a STOCHASTIC solver, so a single returned solution is
a draw, not a deterministic answer. Every fit in this campaign requested
num_samples = 8, and the raw responses were saved, so the per-fit spread across
those draws is recoverable without spending any further metered time.

This quantifies what the stochasticity actually costs on our formulation:
the spread of returned energies within a fit, and the gap between the best draw
and the exact classical optimum.

Usage: python experiments/src/hw_dispersion.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import store

RESP_DIR = Path(__file__).resolve().parents[1] / "results" / "pools" / "hw_responses"
OUT = Path(__file__).resolve().parents[1] / "results" / "hw_dispersion.json"


def energies_from(text: str) -> list[float]:
    """Responses are saved as the repr of a SolutionResults object; pull the
    energies array out of it."""
    m = re.search(r"energies=array\(\[(.*?)\]\)", text, flags=re.S)
    if not m:
        return []
    return [float(x) for x in re.findall(r"-?\d+\.?\d*(?:e[-+]?\d+)?", m.group(1))]


def main() -> int:
    # Without this the empty-directory case reaches np.min([]) and raises a bare
    # ValueError from inside the summary, hiding the actual prerequisite. The
    # responses are now tracked (F54), so this fires only if they are deleted.
    if not RESP_DIR.exists() or not any(RESP_DIR.glob("*.json")):
        raise SystemExit(
            f"no saved responses under {RESP_DIR}. They are version-controlled "
            "because they cannot be regenerated without spending metered QPU "
            "seconds; restore them before regenerating this evidence.")

    rows = json.loads(store.RESULTS.read_text())["rows"]
    by_key = {(r.get("config"), r.get("protocol"), r["seed"]): r
              for r in rows if r["arm"] == "cvqboost_hw"}

    recs = []
    for f in sorted(RESP_DIR.glob("*.json")):
        text = f.read_text()
        e = energies_from(text)
        if len(e) < 2:
            continue
        e = np.asarray(e, dtype=float)
        best, worst = float(e.min()), float(e.max())
        spread_rel = abs(worst - best) / max(abs(best), 1e-12)
        parts = f.stem.rsplit("_", 2)
        key = (parts[0], parts[1], int(parts[2]))
        row = by_key.get(key)
        rec = {"file": f.name, "n_samples": int(len(e)),
               "best_energy": best, "worst_energy": worst,
               "spread_relative_pct": spread_rel * 100.0,
               "identical_draws": bool(np.allclose(e, e[0])),
               # Recorded per fit because the campaign is no longer homogeneous:
               # B2 ran at schedule 3 and every other block at schedule 2, and
               # pooling them would report a solver-dispersion figure that
               # describes two different device settings at once.
               "relaxation_schedule": ((row or {}).get("hw_config") or {}).get(
                   "relaxation_schedule"),
               "block": (row or {}).get("block")}
        if row and row.get("fidelity"):
            fid = row["fidelity"]
            rec["gap_to_exact_pct"] = abs(
                fid["hw_objective_recomputed"] - fid["proxy_objective"]) / max(
                abs(fid["proxy_objective"]), 1e-12) * 100.0
        recs.append(rec)

    spreads = [r["spread_relative_pct"] for r in recs]
    gaps = [r["gap_to_exact_pct"] for r in recs if "gap_to_exact_pct" in r]
    out = {
        "note": ("Dirac-3 is a stochastic solver (QCi documentation). Each fit "
                 "requested num_samples = 8; this is the spread ACROSS those draws "
                 "within each fit, recovered from saved responses at zero metered cost."),
        "num_samples_per_fit": 8,
        "n_fits": len(recs),
        "fits_where_all_draws_identical": sum(r["identical_draws"] for r in recs),
        "within_fit_energy_spread_pct": {
            "min": float(np.min(spreads)), "median": float(np.median(spreads)),
            "max": float(np.max(spreads)),
        },
        # Split by device setting. The papers quote the schedule-2 figure, which
        # covers every block except B2; reporting one pooled number across two
        # relaxation schedules would describe neither.
        "by_relaxation_schedule": {
            str(sch): {
                "n_fits": len(g),
                "fits_where_all_draws_identical": sum(r["identical_draws"] for r in g),
                "spread_pct_min": float(np.min([r["spread_relative_pct"] for r in g])),
                "spread_pct_median": float(np.median([r["spread_relative_pct"] for r in g])),
                "spread_pct_max": float(np.max([r["spread_relative_pct"] for r in g])),
                "blocks": sorted({r["block"] for r in g if r["block"]}),
            }
            for sch, g in sorted(
                {r["relaxation_schedule"]: [x for x in recs
                                            if x["relaxation_schedule"] == r["relaxation_schedule"]]
                 for r in recs if r["relaxation_schedule"] is not None}.items())
        },
        "gap_best_draw_to_exact_optimum_pct": {
            "min": float(np.min(gaps)), "median": float(np.median(gaps)),
            "max": float(np.max(gaps)),
        } if gaps else None,
        "per_fit": recs,
    }
    store.atomic_write_json(OUT, out)
    print(f"hw_dispersion.json: {len(recs)} fits, "
          f"within-fit energy spread median {np.median(spreads):.4f}%, "
          f"max {np.max(spreads):.4f}%; "
          f"identical-draw fits {out['fits_where_all_draws_identical']}/{len(recs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
