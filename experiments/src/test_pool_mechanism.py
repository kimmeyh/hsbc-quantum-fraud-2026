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

POOLS = sorted(glob.glob(str(
    Path(__file__).resolve().parents[1] / "results" / "pools" / "h_*_free_dct_full.npz")))

# The pools are gitignored (.gitignore:9) and nothing under that directory is
# tracked, so on CI or any fresh clone POOLS is empty. An empty parametrize list
# generates ZERO cases SILENTLY -- the guards below would vanish from the run and
# the suite would stay green while the A20 mechanism claim went unchecked. That
# is exactly the "green suite read as more assurance than it gives" failure this
# sprint exists to close, so the absence is made loud instead.
pytestmark = pytest.mark.skipif(
    not POOLS,
    reason=("no pools under experiments/results/pools/ (gitignored, untracked). "
            "The A20 mechanism guard cannot run; rebuild them with the pool "
            "builder before trusting a green suite on this file."))


def _pool(path: str):
    # No allow_pickle: these artifacts hold plain numeric arrays, verified, so
    # the default (pickle disabled) both works and keeps arbitrary-code
    # deserialisation off a path that reads committed files.
    d = np.load(path)
    H = d["H_tr"].astype(float)              # (learners, rows) of +/-1 votes
    y = np.where(d["y_tr01"] == 1, 1, -1)
    return H, y


@pytest.mark.parametrize("path", POOLS, ids=lambda p: Path(p).stem)
def test_most_learners_memorise_the_training_fold(path):
    """80-84 of 91, every seed. This is the mechanism A20 records."""
    H, y = _pool(path)
    perfect = int((H == y.reshape(1, -1)).all(axis=1).sum())
    assert 75 <= perfect <= 89, (
        f"{Path(path).stem}: {perfect} of {H.shape[0]} learners reproduce the "
        f"training labels exactly. A20 records 80-84 across ten seeds; a value "
        f"outside 75-89 means the pool changed and the published mechanism "
        f"needs re-deriving, not re-asserting.")


@pytest.mark.parametrize("path", POOLS, ids=lambda p: Path(p).stem)
def test_no_learner_predicts_the_negative_class_everywhere(path):
    """The claim A20 retracts. Zero, not 'almost all'."""
    H, _ = _pool(path)
    all_negative = int((H == -1).all(axis=1).sum())
    assert all_negative == 0, (
        f"{Path(path).stem}: {all_negative} learners predict the negative class "
        f"everywhere. The pre-A20 text claimed this was the degeneracy's cause; "
        f"if it becomes true, the correction itself needs revisiting.")


@pytest.mark.parametrize("path", POOLS, ids=lambda p: Path(p).stem)
def test_the_degeneracy_itself_is_unchanged(path):
    """A20 changed the EXPLANATION, not the measurement. Guard the measurement."""
    H, _ = _pool(path)
    G = H @ H.T
    n = G.shape[0]
    off = (G.sum() - np.trace(G)) / (n * (n - 1))
    ratio = off / np.diag(G).mean()
    assert ratio > 0.999, (
        f"{Path(path).stem}: off-diagonal/diagonal Gram ratio {ratio:.6f}. The "
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
