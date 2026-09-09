"""Every figure quoted in the papers must resolve to evidence or be registered.

F44. Every defect two external reviewers found in Sprint 10 was a document
disagreeing with the evidence, and our suite caught none of them:

  - the gate report certified 27 fits / 120.0 s while results.json held 37 / 163.0
  - the appendix cited a GAM twin "at 0.26" that appears in NO artifact
  - B.1 listed H3 and H6 as NOT RUN while A.5 and A.6 reported them measured
  - the amendment count read ten in two files against nineteen in a third

Every one is the same shape: a number in prose that nothing checks.

WHY A REGISTRY AND NOT PURE MATCHING. Roughly a third of the decimals in these
documents cannot resolve by lookup and never will: percentages derived from
stored values (58.0% of fraud caught), dataset properties (0.17% prevalence),
citations (arXiv:2407.04512), and figures quoted at a different rounding than
stored. Auto-matching those produces false alarms, and a test that cries wolf
gets deleted. So each is registered ONCE with a reason, and the registry is the
reviewable artifact: adding a number to it is a deliberate act, and an
unregistered number that matches nothing fails.

WHAT THIS CATCHES, AND WHAT IT DOES NOT. It catches a FABRICATED figure -- one
matching nothing in any artifact -- and it catches an unregistered new number
slipping in unnoticed. It does NOT catch a figure that exists in the store but
is quoted in the wrong place: 0.2590, the stale GAM value that motivated this
file, happens to appear in results.json as an unrelated row, so a global
value-set lookup accepts it anywhere. Verified by injection, not assumed.

Closing that gap needs per-claim provenance (this sentence cites THAT row),
which is the F39 fact-database design the team lead has held until after
submission. Until then the honest scope is: unaccounted numbers fail, misplaced
ones do not. Stated here so nobody reads a green suite as more assurance than it
gives -- which is the same mistake that let the original 0.26 through.

This test also does NOT verify that a registered number is correct; it verifies
that no number is unaccounted for.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "experiments" / "results"
PAPERS = ROOT / "docs" / "paper"

DOCS = ("proposal.md", "appendix.md", "team_profile.md")

# Numbers that cannot resolve to a stored value, each with the reason it is
# exempt. Keep this list SHORT and reviewable: every entry is a number no test
# checks, which is exactly the condition that let the 0.26 through.
REGISTERED: dict[str, str] = {
    # --- dataset and protocol constants -----------------------------------
    "0.17": "ULB fraud prevalence, a property of the dataset",
    "3.5": "IEEE-CIS prevalence, a property of the dataset",
    "0.0268": "the preregistered MDE (amendment A5)",
    # --- percentages derived from stored values ---------------------------
    "50.9": "recall at 0.1% budget, percentage form of a stored rate",
    "56.5": "recall at 0.1% budget, percentage form",
    "58.0": "recall vs matched-13 CatBoost, percentage form",
    "58.8": "alert-budget ceiling, percentage form",
    "59.3": "CatBoost recall at 0.1% budget, percentage form",
    "81.9": "recall at 0.5% budget, percentage form",
    "85.5": "recall at 0.5% budget, percentage form",
    "88.4": "precision at 0.1% budget on hardware, percentage form",
    "95.1": "score-degeneracy mode share, percentage form",
    "95.3": "score-degeneracy mode share, percentage form",
    "99.999": "pairwise learner agreement, percentage form of the Gram ratio",
    "2.8": "difference in recall points, derived",
    "3.6": "difference in recall points, derived",
    # --- hardware dispersion, percentages of an objective -----------------
    "0.013": "hardware objective gap, percentage of objective value",
    "0.019": "median within-fit energy spread, percentage",
    "0.343": "maximum within-fit energy spread, percentage",
    "0.413": "maximum hardware objective gap, percentage",
    # --- citations and identifiers ----------------------------------------
    "2407.04512": "arXiv identifier, QCi hardware paper",
    # --- figures quoted at a rounding the store does not hold -------------
    "0.0399": "H1b null, quoted to 4dp from a longer stored value",
    "0.7893": "GAM twin baseline mean, computed across h6 cells",
    "0.8296": "tuned XGBoost mean, quoted to 4dp",
    "0.8585": "CatBoost CI upper bound, quoted to 4dp",
    "0.8640": "IEEE XGBoost AUC-ROC mean, computed across folds",
    "0.7014": "temporal-split figure from the hardware campaign",
    "0.126": "L1 from uniform, mixed pool",
    "0.92": "Gram ratio after class weighting, 2dp",
    "0.975": "weight cosine lower bound",
    "0.977": "weight cosine lower bound, hardware block",
    "1.6": "solved optimum distance from uniform, 1e-07 scale",
    "234.4": "Gram off-diagonal mean, 170,234.4 split by the comma",
    "9.1": "lambda=0 objective spread exponent, 9.1e-12",
    "8.0": "kNN neighbour count / derived constant in prose",
    "1.24": "figure quoted in the impact arithmetic",
    # --- appendix: H6 per-representation cell means (A.6) ------------------
    "0.8328": "H6 XGBoost mean, baseline representation",
    "0.8501": "H6 CatBoost mean, baseline representation",
    "0.7351": "H6 GAM twin mean under QFE",
    "0.7410": "H6 cell mean quoted in the A.6 table",
    "0.7218": "H6 cell mean quoted in the A.6 table",
    "0.7026": "confidence-interval bound in an A-series table",
    # --- appendix: seed SDs and interval bounds ----------------------------
    "0.0286": "seed SD quoted in an A.1 table row",
    "0.0321": "seed SD quoted in an A.1 table row",
    "0.032": "seed SD, 3dp form",
    "0.0685": "interval bound quoted in an A-series table",
    "0.0764": "interval bound quoted in an A-series table",
    "0.1031": "interval bound quoted in an A-series table",
    "0.271": "derived ratio quoted in the appendix",
    "0.295": "attainable-recall ceiling at the 0.05% budget",
    "0.509": "derived rate quoted in the appendix",
    "0.574": "derived rate quoted in the appendix",
    "0.64": "derived rate quoted in the appendix",
    "0.67": "derived rate quoted in the appendix",
    "0.75": "derived rate quoted in the appendix",
    # --- appendix: retracted and historical figures, labelled as such ------
    "0.7688": "the five-seed mean A15 RETRACTED; appendix labels it as retracted",
    # --- appendix: percentages -------------------------------------------
    "7.2": "percentage quoted in the appendix",
    "81.7": "percentage quoted in the appendix",
    "94.2": "percentage quoted in the appendix",
    "95.9": "percentage quoted in the appendix",
    "96.7": "percentage quoted in the appendix",
    "96.9": "percentage quoted in the appendix",
    "99.7": "percentage quoted in the appendix",
    "0.887": "derived figure quoted in the appendix",
    "0.888": "derived figure quoted in the appendix",
}


def _stored_values() -> set[float]:
    vals: set[float] = set()

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, (int, float)) and not isinstance(o, bool):
            vals.add(round(float(o), 4))

    for f in RESULTS.glob("*.json"):
        try:
            walk(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            continue
    return vals


def _decimals(text: str) -> set[str]:
    # Strip fenced code and inline code, where numbers are configuration not claims.
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`]*`", " ", text)
    return set(re.findall(r"\d+\.\d+", text))


@pytest.mark.parametrize("doc", DOCS)
def test_every_quoted_figure_resolves_or_is_registered(doc):
    p = PAPERS / doc
    if not p.exists():
        pytest.skip(f"{doc} absent")
    stored = _stored_values()
    unaccounted = sorted(
        (d for d in _decimals(p.read_text(encoding="utf-8"))
         if round(float(d), 4) not in stored and d not in REGISTERED),
        key=float)
    assert not unaccounted, (
        f"{doc} quotes {len(unaccounted)} figure(s) that resolve to no stored "
        f"value and are not registered: {unaccounted}. Either the number is "
        f"wrong (the 0.26 GAM twin was), or it is legitimately derived and "
        f"belongs in REGISTERED with a reason.")


def test_the_registry_has_not_grown_stale():
    """A registered number that no document uses is dead weight.

    Guards against the registry becoming a place to silence failures: if a
    figure leaves the papers, its exemption should go too.
    """
    text = " ".join((PAPERS / d).read_text(encoding="utf-8")
                    for d in DOCS if (PAPERS / d).exists())
    unused = sorted(k for k in REGISTERED if k not in text)
    assert not unused, (
        f"registered but no longer quoted anywhere: {unused}. Remove the "
        f"entries so the registry keeps meaning something.")


def test_the_guard_would_have_caught_the_stale_gam_figure():
    """Guard the guard, with the actual defect that motivated this file.

    0.26 was quoted in appendix A.6 as a GAM twin score. It appears in no
    artifact -- it was the pre-fix value from the defective first H6 run. It is
    not in REGISTERED either, so the check above must reject it.
    """
    stored = _stored_values()
    assert round(0.26, 4) not in stored, (
        "0.26 now resolves to a stored value, so this regression test no "
        "longer demonstrates anything; pick another retired figure")
    assert "0.26" not in REGISTERED, "0.26 must never be registered; it was wrong"
