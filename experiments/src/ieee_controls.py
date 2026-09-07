"""Section 4 item 4 controls for IEEE-CIS (F3 Task A).

The preregistration requires two filters that the Sprint 6 scaffolding did not
implement, and `ieee_baseline.py` explicitly scoped out for its own scale check:

  "Time-consistency filter (single-feature train-early/test-late AUC must exceed
   0.5) and adversarial validation (target AUC near 0.5, recursively dropping top
   adversarial features) both run INSIDE training folds only."

Both exist to catch the same failure from opposite directions. IEEE-CIS spans
roughly six months, and a feature can be predictive on early rows and useless or
inverted on late ones -- a model leaning on it scores well in cross-validation
and fails in production. The time-consistency filter finds features that do not
survive time ordering. Adversarial validation finds the complement: features
that predict WHICH PERIOD a row came from, which is drift a model will mistake
for signal.

THE TRAIN-FOLD-ONLY CONSTRAINT IS THE WHOLE POINT. A filter that inspects
validation or test rows to decide which features to keep has leaked those rows
into the model, and the leak is invisible in the resulting metric because
nothing looks wrong. Every function here takes ONLY training data, and
`test_ieee_controls.py` asserts that a call given evaluation rows fails.

Usage is inside a fold loop:

    keep = time_consistent_features(X_tr, y_tr, day_tr)
    keep = drop_adversarial_features(X_tr[keep], day_tr)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# A single feature must beat a coin flip when trained early and tested late.
# 0.5 is the preregistered floor; a feature at or below it carries no
# time-stable signal and is dropped.
TIME_CONSISTENCY_MIN_AUC = 0.5

# Adversarial validation targets AUC near 0.5: at 0.5 a classifier cannot tell
# early rows from late ones, so the feature set carries no period signal. Above
# this bound it can, and the top contributor is dropped and the check repeated.
ADVERSARIAL_MAX_AUC = 0.60
ADVERSARIAL_MAX_ROUNDS = 20


def _auc(y_true, score) -> float:
    from sklearn.metrics import roc_auc_score
    y_true = np.asarray(y_true)
    if len(np.unique(y_true)) < 2:
        return 0.5          # undefined; treat as uninformative rather than raise
    return float(roc_auc_score(y_true, score))


def time_consistent_features(X: pd.DataFrame, y, day, min_auc: float = TIME_CONSISTENCY_MIN_AUC,
                             early_frac: float = 0.5) -> list[str]:
    """Keep features whose single-feature train-early/test-late AUC exceeds
    `min_auc`. TRAINING DATA ONLY: `X`, `y` and `day` must all come from inside
    one training fold.

    Each feature is fitted on the early half of the TRAINING fold and scored on
    the late half of the SAME fold. Nothing outside the fold is touched, so this
    is a property of the training data and cannot leak evaluation rows.
    """
    from sklearn.linear_model import LogisticRegression

    day = np.asarray(day, dtype=float)
    y = np.asarray(y)
    cut = np.quantile(day, early_frac)
    early, late = day <= cut, day > cut
    if early.sum() < 50 or late.sum() < 50:
        # Too little history inside this fold to judge; keep everything rather
        # than silently dropping features on a sample that cannot support it.
        return list(X.columns)

    keep = []
    for col in X.columns:
        v = X[col].to_numpy(dtype=float)
        v = np.nan_to_num(v, nan=0.0, posinf=0.0, neginf=0.0)
        if np.std(v[early]) == 0.0:
            continue                     # constant in the early half: no signal
        try:
            m = LogisticRegression(max_iter=200).fit(v[early].reshape(-1, 1), y[early])
            auc = _auc(y[late], m.decision_function(v[late].reshape(-1, 1)))
        except Exception:                # noqa: BLE001 - a feature that cannot fit is dropped
            continue
        # A feature that INVERTS under time ordering is as dangerous as a weak
        # one; the criterion is one-sided by design and matches the prereg text.
        if auc > min_auc:
            keep.append(col)
    return keep


def adversarial_auc(X: pd.DataFrame, day, early_frac: float = 0.5, seed: int = 0) -> tuple[float, str | None]:
    """Train a classifier to tell EARLY training rows from LATE ones.

    Returns (auc, top_feature). An AUC near 0.5 means the feature set carries no
    period signal, which is what the protocol wants. Higher means the features
    encode drift, and the top contributor is the one to drop.
    """
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.model_selection import train_test_split

    day = np.asarray(day, dtype=float)
    cut = np.quantile(day, early_frac)
    is_late = (day > cut).astype(int)
    if len(np.unique(is_late)) < 2 or len(X.columns) == 0:
        return 0.5, None

    Xtr, Xte, ytr, yte = train_test_split(
        X, is_late, test_size=0.3, random_state=seed, stratify=is_late)
    clf = HistGradientBoostingClassifier(max_iter=60, random_state=seed).fit(Xtr, ytr)
    auc = _auc(yte, clf.predict_proba(Xte)[:, 1])

    # Attribution by a SINGLE-PASS ranking, not permutation importance.
    #
    # The check above is cheap: one fit, one AUC. The attribution was not:
    # permutation_importance with n_repeats=3 over ~400 columns is 1,200 model
    # scorings per round, and the loop runs up to 20 rounds per fold. That cost
    # about 3 CPU-hours for ONE smoke fold against 12 seconds of actual model
    # fitting (F3 pre-run audit finding 5).
    #
    # A per-round ranking only has to name the single feature to drop next, and
    # the AUC check re-validates after every drop -- so a cheaper ranking that
    # is occasionally wrong costs one extra round, not a wrong answer.
    top = _rank_top_feature(clf, Xte, yte, X.columns, seed)
    return auc, top


def _rank_top_feature(clf, Xte, yte, columns, seed: int) -> str | None:
    """Name the feature carrying the most period signal, cheaply.

    Single-feature AUC against the early/late label: one pass over the columns,
    no refitting. A feature that alone separates early from late rows IS the
    drift, which is the quantity the adversarial filter is chasing.
    """
    best, best_auc = None, -1.0
    y = np.asarray(yte)
    for col in columns:
        v = np.nan_to_num(np.asarray(Xte[col], dtype=float),
                          nan=0.0, posinf=0.0, neginf=0.0)
        if np.std(v) == 0.0:
            continue
        a = _auc(y, v)
        a = max(a, 1.0 - a)          # direction is irrelevant; separation is not
        if a > best_auc:
            best, best_auc = str(col), a
    return best


def drop_adversarial_features(X: pd.DataFrame, day, max_auc: float = ADVERSARIAL_MAX_AUC,
                              max_rounds: int = ADVERSARIAL_MAX_ROUNDS,
                              seed: int = 0) -> list[str]:
    """Recursively drop the top adversarial feature until early and late rows are
    no longer separable. TRAINING DATA ONLY.

    Returns the surviving column list. Stops at `max_rounds` so a pathological
    feature set cannot loop indefinitely; the round count is worth reporting
    when it hits the bound, because that itself says the data is drifting hard.
    """
    cols = list(X.columns)
    dropped, rounds, final_auc = [], 0, None
    for _ in range(max_rounds):
        if not cols:
            break
        rounds += 1
        auc, top = adversarial_auc(X[cols], day, seed=seed)
        final_auc = auc
        if auc <= max_auc or top is None:
            break
        cols.remove(top)
        dropped.append(top)
    # A loop that stops at its bound is EVIDENCE, not a nuisance: it says the
    # data carries more drift than max_rounds drops can remove. Reported rather
    # than silently absorbed, and the caller records it.
    drop_adversarial_features.last_run = {
        "rounds": rounds, "hit_round_cap": rounds >= max_rounds and
        (final_auc is not None and final_auc > max_auc),
        "final_adversarial_auc": final_auc, "dropped": dropped,
    }
    return cols


def apply_item4_controls(X_train: pd.DataFrame, y_train, day_train, seed: int = 0) -> dict:
    """Run both controls in order and report what each removed.

    Returns a record suitable for results.json: the surviving columns plus the
    counts, so a reader can see how much of the feature set each filter took
    rather than only the final number.
    """
    n_start = len(X_train.columns)
    tc = time_consistent_features(X_train, y_train, day_train)
    adv = drop_adversarial_features(X_train[tc], day_train, seed=seed)
    run_info = getattr(drop_adversarial_features, "last_run", {})
    return {
        "adversarial_rounds": run_info.get("rounds"),
        "adversarial_hit_round_cap": run_info.get("hit_round_cap"),
        "final_adversarial_auc": run_info.get("final_adversarial_auc"),
        "n_features_start": n_start,
        "n_after_time_consistency": len(tc),
        "n_after_adversarial": len(adv),
        "dropped_time_inconsistent": n_start - len(tc),
        "dropped_adversarial": len(tc) - len(adv),
        "features": adv,
        "controls": "section 4 item 4, both computed on training rows only",
    }
