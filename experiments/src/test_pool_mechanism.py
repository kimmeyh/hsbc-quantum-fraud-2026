"""The pool-degeneracy mechanism must match what the saved pools show.

A20 corrects a mechanism the submission asserted for three sprints: that at
0.17% prevalence the frozen pool's trees predict the negative class almost
everywhere, so the pool carries no diversity. The saved pools disprove it. The
degeneracy is real; its cause is in-sample memorisation.

No test we had written could have caught this, because every test checked
arithmetic and none checked what a number MEANT. These assert the mechanism
itself against the committed pools, so the corrected claim cannot silently drift
back and a future pool change that breaks the explanation fails here first.

Found by an external adversarial review, not by us (GPT-6 Astra, 2026-09-08).
"""
from __future__ import annotations

import glob
from pathlib import Path

import numpy as np
import pytest

RESULTS = Path(__file__).resolve().parents[1] / "results"
POOLS = sorted(glob.glob(str(RESULTS / "pools" / "h_*_free_dct_full.npz")))
FIXTURE = RESULTS / "pool_mechanism_fixture.npz"

# F67. The pools are gitignored, so on a fresh clone POOLS is empty and this
# file was the suite's ONLY skip -- the A20 mechanism guard silently did not run
# for any reader who cloned the repository, while the claim it guards is
# published in appendix A.4.
#
# A committed FIXTURE closes that. It holds the int8 sign matrix and labels the
# three per-pool tests actually read, 0.83 MB for all ten pools against 2.38 MB
# for the pools themselves, and it is lossless here because every H_tr holds
# only -1 and +1 (asserted when the fixture is built, not assumed).
#
# Real pools are still PREFERRED when present: they are the genuine artifact and
# carry full precision. The fixture is the fallback, so a fresh clone runs the
# same assertions instead of skipping them.
#
# It is NOT evidence and must not be read as such -- no val/test splits, no
# feature names, no float precision. It is the input a guard needs to detect
# drift. Rebuild with experiments/src/build_pool_fixture.py.
if POOLS:
    CASES = POOLS
    SOURCE = "pools"
elif FIXTURE.exists():
    CASES = sorted({k.split("_")[1] for k in np.load(FIXTURE).files})
    SOURCE = "fixture"
else:
    CASES = []
    SOURCE = "none"

pytestmark = pytest.mark.skipif(
    not CASES,
    reason=("neither the pools under experiments/results/pools/ nor the "
            "committed fixture is present. The A20 mechanism guard cannot run; "
            "rebuild with scripts/wsl_build_pools.sh or "
            "experiments/src/build_pool_fixture.py."))


def _pool(case: str):
    """Return (H, y) for one case, from real pools or the committed fixture.

    No allow_pickle: these artifacts hold plain numeric arrays, verified, so the
    default (pickle disabled) both works and keeps arbitrary-code
    deserialisation off a path that reads committed files.
    """
    if SOURCE == "pools":
        d = np.load(case)
        H = d["H_tr"].astype(float)          # (learners, rows) of +/-1 votes
        y = np.where(d["y_tr01"] == 1, 1, -1)
        return H, y
    d = np.load(FIXTURE)
    return d[f"H_{case}"].astype(float), d[f"y_{case}"].astype(int)


def _case_id(case: str) -> str:
    return Path(case).stem if SOURCE == "pools" else f"seed_{case}"


@pytest.mark.parametrize("path", CASES, ids=_case_id)
def test_most_learners_memorise_the_training_fold(path):
    """80-84 of 91, every seed. This is the mechanism A20 records."""
    H, y = _pool(path)
    perfect = int((H == y.reshape(1, -1)).all(axis=1).sum())
    assert 75 <= perfect <= 89, (
        f"{_case_id(path)}: {perfect} of {H.shape[0]} learners reproduce the "
        f"training labels exactly. A20 records 80-84 across ten seeds; a value "
        f"outside 75-89 means the pool changed and the published mechanism "
        f"needs re-deriving, not re-asserting.")


@pytest.mark.parametrize("path", CASES, ids=_case_id)
def test_no_learner_predicts_the_negative_class_everywhere(path):
    """The claim A20 retracts. Zero, not 'almost all'."""
    H, _ = _pool(path)
    all_negative = int((H == -1).all(axis=1).sum())
    assert all_negative == 0, (
        f"{_case_id(path)}: {all_negative} learners predict the negative class "
        f"everywhere. The pre-A20 text claimed this was the degeneracy's cause; "
        f"if it becomes true, the correction itself needs revisiting.")


@pytest.mark.parametrize("path", CASES, ids=_case_id)
def test_the_degeneracy_itself_is_unchanged(path):
    """A20 changed the EXPLANATION, not the measurement. Guard the measurement."""
    H, _ = _pool(path)
    G = H @ H.T
    n = G.shape[0]
    off = (G.sum() - np.trace(G)) / (n * (n - 1))
    ratio = off / np.diag(G).mean()
    assert ratio > 0.999, (
        f"{_case_id(path)}: off-diagonal/diagonal Gram ratio {ratio:.6f}. The "
        f"published figure is 170,234.4 against 170,235; if the pool stops being "
        f"degenerate, several reported conclusions change.")


def test_the_documents_do_not_reassert_the_retracted_mechanism():
    """Guard the papers, not just the data.

    The specific wording A20 retracts must not reappear in a document. The
    preregistration is FROZEN and keeps its original text by design -- A20 is
    the mechanism that corrects it -- so it is excluded here.
    """
    root = Path(__file__).resolve().parents[2]
    retracted = "predicts the negative class almost everywhere"
    offenders = []
    for name in ("proposal.md", "appendix.md", "qci_cover.md", "team_profile.md"):
        p = root / "docs" / "paper" / name
        if p.exists() and retracted in p.read_text(encoding="utf-8"):
            offenders.append(name)
    assert not offenders, (
        f"{offenders} still assert the mechanism A20 retracts. The saved pools "
        f"show zero learners predicting the negative class everywhere.")


def test_the_frozen_arm_is_actually_unbounded():
    """The other half of A20: 'depth-limited' was false for the frozen arm.

    Guards the claim at its source rather than in prose -- the frozen config
    passes no weak_cls_params, so sklearn's default max_depth=None applies.
    """
    import inspect

    import qubo_proxy
    src = inspect.getsource(qubo_proxy.build_pool)
    assert "weak_cls_params=dict(weak_params or {})" in src, (
        "build_pool no longer passes an empty weak_cls_params by default. If the "
        "frozen arm now sets max_depth, A20's 'unbounded' statement is stale and "
        "the papers need updating with it.")
