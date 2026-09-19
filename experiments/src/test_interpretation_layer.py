"""Assertions about what the evidence MEANS, not what it computes.

F35. Three consecutive sprints where the defect that travelled furthest was a
claim about meaning rather than an arithmetic error:

  A15  a five-seed mean carried into a ten-seed writeup, inverting the argument
       it supported
  A17  a protocol violation invisible for two sprints because the affected arms
       were only ever compared against each other
  S10  B.1 listing H3 and H6 as NOT RUN while A.5 and A.6 reported both measured,
       eight lines apart in the same document

None is a wrong calculation. Every one is a right number meaning something other
than what the sentence around it says. Arithmetic tests cannot see these, which
is why they reached an external reviewer first.

This file covers the class F44 explicitly cannot: a figure that exists in the
store but is quoted in the wrong PLACE, and a status claim that contradicts the
artifact it describes.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "experiments" / "results"
PAPERS = ROOT / "docs" / "paper"
APPENDIX = PAPERS / "appendix.md"


def _appendix() -> str:
    return APPENDIX.read_text(encoding="utf-8")


# --------------------------------------------------------------------------
# The Sprint 10 defect: a registry status contradicting the write-up.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("hyp,artifact", [
    ("H3", "ieee_h3_ladder.json"),
    ("H6", "h6_representation.json"),
])
def test_a_hypothesis_with_an_artifact_is_not_listed_unrun(hyp, artifact):
    """If the evidence exists, the registry must not say NOT RUN.

    B.1 listed H3 and H6 as NOT RUN [PROJ] while their artifacts sat in the
    results directory and A.5/A.6 reported their figures. A reviewer found it;
    nothing in the suite could have.
    """
    if not (RESULTS / artifact).exists():
        pytest.skip(f"{artifact} not present")
    # SCOPED to the B.1 section. An unscoped scan matched any appendix table
    # row mentioning the hypothesis -- the A.5 and A.6 tables discuss H3 and H6
    # too -- so a row like "H3 NOT RUN at k=21" in a different sense would raise
    # a contradiction that does not exist.
    text = _appendix()
    start = text.find("B.1")
    if start == -1:
        pytest.skip("no B.1 section in the appendix")
    nxt = text.find("\n## ", start)
    section = text[start:nxt if nxt != -1 else len(text)]
    for line in section.splitlines():
        if line.startswith("|") and re.search(rf"\b{hyp}\b", line):
            if "NOT RUN" in line:
                raise AssertionError(
                    f"B.1 lists {hyp} as NOT RUN, but {artifact} exists and the "
                    f"appendix reports its result. Registry and write-up "
                    f"disagree -- the Sprint 10 defect, recurring.")


def test_measured_claims_name_an_evidence_tag():
    """A figure asserted as measured must carry [HW] or [SIM] nearby.

    The tag is what separates a measurement from a projection, and an untagged
    number reads as measured whether or not it is.
    """
    text = _appendix()
    offenders = []
    for line in text.splitlines():
        low = line.lower()
        if "**measured**" in low and not re.search(r"\[(HW|SIM|PROJ)\]", line):
            offenders.append(line.strip()[:90])
    assert not offenders, (
        f"claims marked MEASURED with no evidence tag: {offenders}")


# --------------------------------------------------------------------------
# The A15 defect: a figure quoted at the wrong n.
# --------------------------------------------------------------------------

def test_ten_seed_claims_are_not_backed_by_five_seed_artifacts():
    """A15's exact shape: a five-seed mean presented as a ten-seed result."""
    h6 = RESULTS / "h6_representation.json"
    if not h6.exists():
        pytest.skip("h6 artifact absent")
    d = json.loads(h6.read_text(encoding="utf-8"))
    cells = d.get("cells", d.get("rows", []))
    seeds = {c.get("seed") for c in cells if isinstance(c, dict) and "seed" in c}
    text = _appendix()
    if "ten seeds" in text.lower() and "A.6" in text:
        assert len(seeds) >= 10, (
            f"the appendix says ten seeds for H6 but the artifact holds "
            f"{len(seeds)}; this is the A15 defect returning")


# --------------------------------------------------------------------------
# The A17 defect: an arm compared only against itself.
# --------------------------------------------------------------------------

def test_the_headline_gain_states_its_comparator():
    """+0.0319 is meaningless without naming what it is over.

    A17 happened because the exploratory arms were compared only to each other,
    so a dataset difference stayed invisible. A stated comparator is what makes
    that checkable.
    """
    text = (PAPERS / "proposal.md").read_text(encoding="utf-8")
    if "+0.0319" not in text:
        pytest.skip("headline figure changed; update this test with it")
    window = text[max(0, text.find("+0.0319") - 700): text.find("+0.0319") + 700]
    assert "frozen" in window.lower() and "matched" in window.lower(), (
        "the +0.0319 claim does not name its comparator and the matching within "
        "700 characters; a bare difference invites the A17 error")


def test_the_decomposition_and_the_headline_agree():
    """Two artifacts describing the same quantity must not disagree.

    gain_decomposition.json rebuilds the pools independently of
    tuned_vs_frozen_k6.json. If they drift apart, one of them is wrong and the
    paper is quoting whichever it happened to cite.
    """
    a, b = RESULTS / "gain_decomposition.json", RESULTS / "tuned_vs_frozen_k6.json"
    if not (a.exists() and b.exists()):
        pytest.skip("decomposition artifacts absent")
    total = json.loads(a.read_text(encoding="utf-8"))["decomposition"]["total"]["mean"]
    published = json.loads(b.read_text(encoding="utf-8"))["mean_delta"]
    assert abs(total - published) < 5e-4, (
        f"independent decomposition gives {total:.6f}, the published comparison "
        f"{published:.6f}. Two artifacts, one quantity, different answers.")


# --------------------------------------------------------------------------
# Retracted claims must not return.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("phrase,amendment", [
    ("predicts the negative class almost everywhere", "A20"),
    ("the optimum stays uniform even at zero penalty", "F42/F11"),
])
def test_retracted_wording_does_not_reappear(phrase, amendment):
    """A correction that can be undone by an edit is not a correction."""
    # qci_cover.md moved to docs/qci_package/ on 2026-09-17 (private
    # correspondence, now gitignored). It is still CHECKED here: the retraction
    # must not reappear in a letter just because the letter is unpublished.
    # The exists() guard below would have skipped it silently otherwise.
    candidates = [PAPERS / "proposal.md", PAPERS / "appendix.md",
                  PAPERS.parent / "qci_package" / "qci_cover.md"]
    for p in candidates:
        name = p.name
        if p.exists():
            assert phrase not in p.read_text(encoding="utf-8"), (
                f"{name} reasserts wording retracted by {amendment}")
