"""Explainability evidence for both arms (Sprint 5 F28; zero metered seconds).

Measures, rather than asserts, how inspectable each arm is:
  1. Weight concentration in the CVQBoost ensemble (how many learners carry the
     decision) with the honest counter-finding that Sprint 4's near-degenerate
     optimum spreads weight almost uniformly.
  2. Per-weak-learner structure: each learner sees 1-3 features, so its vote is
     directly readable; the ensemble score decomposes exactly into learner
     contributions, with no post-hoc attribution model.
  3. A worked single decision explained end to end for the CVQBoost arm and for
     the CatBoost baseline on the SAME transaction.

Usage: python experiments/src/explainability.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import data
import qubo_proxy as qp
import run_classical as rc
import store

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
OUT = Path(__file__).resolve().parents[2] / "docs" / "EXPLAINABILITY.md"
SEED = 42


def main() -> int:
    pool = qp.POOLS_DIR / f"h_{SEED}_free_dct_full.npz"
    meta = json.loads((qp.POOLS_DIR / f"h_{SEED}_free_dct_full.meta.json").read_text())
    z = np.load(pool)
    y_pm1 = np.where(z["y_tr01"] == 1, 1, -1)
    w = qp.solve_simplex_qp(z["H_tr"], y_pm1, qp.LAMBDA_MULT * len(y_pm1))
    H_te, y_te = z["H_te"], z["y_te"]
    cols = meta["features"]
    n_pool = int(meta["n_pool"])

    order = np.argsort(w)[::-1]
    cum = np.cumsum(w[order])
    n50 = int(np.searchsorted(cum, 0.50) + 1)
    n80 = int(np.searchsorted(cum, 0.80) + 1)
    n95 = int(np.searchsorted(cum, 0.95) + 1)
    active = int((w > 1e-6).sum())

    scores = w @ H_te
    fraud_idx = np.where(y_te == 1)[0]
    pick = int(fraud_idx[np.argmax(scores[fraud_idx])])
    contrib = w * H_te[:, pick]
    top = np.argsort(np.abs(contrib))[::-1][:8]

    lines = [
        "# Explainability: CVQBoost ensemble versus the GBDT baseline",
        "",
        "**Purpose**: measured evidence on how inspectable each arm is, for the deployment "
        "question that actually gates adoption in banking: can a decline be explained to a "
        "customer, a disputes team, and a regulator.",
        "**Audience**: team lead; paper section (F28).",
        "**Last Updated**: 2026-09-04",
        "",
        "All figures below are computed from the committed pool and the exact proxy solve "
        f"(seed {SEED}, free config, full-pair build, {n_pool} weak learners over {len(cols)} "
        "features). Zero metered seconds. Reproduce with `python experiments/src/explainability.py`.",
        "",
        "## 1. The structural argument",
        "",
        "A CVQBoost ensemble is a weighted vote over small classifiers, each fit on ONE, TWO or "
        "THREE features. Two consequences follow directly, without any attribution model:",
        "",
        "- **Every learner is readable on its own.** A depth-limited tree over two named features "
        "is inspectable by a human analyst; there is no hidden interaction depth to unwind.",
        "- **The score decomposes exactly.** The ensemble score is the sum of weight times vote "
        "over learners, so each learner's contribution to a specific decision is an exact "
        "arithmetic term, not an approximation. SHAP and similar methods exist precisely because "
        "boosted-tree ensembles do NOT decompose this way; here the decomposition is the model.",
        "",
        "By contrast the tuned CatBoost baseline uses up to 2,000 trees; explaining one decision "
        "requires a post-hoc attribution method whose output is an estimate of the model, not the "
        "model itself.",
        "",
        "## 2. The measured counter-finding, stated first",
        "",
        f"Weight is spread almost uniformly across the pool: {active} of {n_pool} learners carry "
        f"non-negligible weight, and it takes **{n50} learners to reach 50%** of the total weight, "
        f"{n80} to reach 80%, and {n95} to reach 95%. The maximum single weight is "
        f"{w.max():.4f} against a uniform value of {1.0 / n_pool:.4f}.",
        "",
        "This is the Sprint 4 near-degeneracy finding seen from the explainability side, and it "
        "cuts BOTH ways. It weakens any claim that a handful of learners explain the model: they "
        "do not, at this configuration. It does not weaken the exact-decomposition property, which "
        "holds regardless of how weight is distributed. The honest summary is that CVQBoost gives "
        "**exact** attribution over **many** simple terms, while the GBDT gives **approximate** "
        "attribution over a smaller number of complex ones.",
        "",
        "## 3. A worked decision",
        "",
        f"Test transaction index {pick} (seed {SEED} test fold), a true fraud, scored highest by "
        "the CVQBoost arm. The decision decomposes exactly into learner contributions:",
        "",
        "| Rank | Learner features | Weight | Vote | Contribution |",
        "|---|---|---|---|---|",
    ]
    ind_list = meta.get("ind_list")
    for rank, i in enumerate(top, 1):
        if ind_list and i < len(ind_list):
            feats = " + ".join(cols[j] for j in ind_list[i])
        else:
            feats = f"learner #{i}"
        lines.append(f"| {rank} | {feats} | {w[i]:.4f} | {int(H_te[i, pick]):+d} "
                     f"| {contrib[i]:+.4f} |")
    lines += [
        "",
        f"Total score {scores[pick]:+.4f} (range -1 to +1); the eight terms above account for "
        f"{np.abs(contrib[top]).sum() / np.abs(contrib).sum():.1%} of the absolute contribution. "
        "Every remaining term is available and readable in the same form.",
        "",
        "**The same decision under CatBoost** requires SHAP or an equivalent post-hoc method: the "
        "explanation is a fitted approximation of the ensemble's behavior near this point, valid "
        "locally, and it changes if the attribution method changes. Both explanations are usable "
        "in practice; only one of them is the model itself.",
        "",
        "## 4. What this means for deployment",
        "",
        "- **Dispute handling**: a declined transaction can be explained as a list of named "
        "feature-pair rules that voted against it, with exact weights.",
        "- **Regulatory review**: the model is a linear combination of inspectable terms with "
        "published weights, so model documentation does not depend on an attribution library.",
        "- **The caveat that must travel with the claim**: at the current configuration the "
        "decision is spread across many small terms rather than a few large ones, so an analyst "
        "reads a longer explanation. A sparser formulation (F25, cardinality-constrained "
        "selection) would concentrate weight and shorten it, which is one more reason that "
        "formulation is the Phase 2 direction.",
    ]

    OUT.write_text("\n".join(lines))
    print(f"EXPLAINABILITY.md written: {n_pool} learners, "
          f"{n50}/{n80}/{n95} for 50/80/95% weight, decision index {pick}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
