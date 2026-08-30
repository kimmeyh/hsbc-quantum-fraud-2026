"""Equal-budget Optuna tuning per PREREGISTRATION.md search spaces.

Budget: 100 trials per GBDT arm (25 for logistic), stratified 5-fold on TRAIN only,
optimizing average precision. Early stopping inside each fold via a 10% carve-out.
"""
from __future__ import annotations

import numpy as np
import optuna
from sklearn.model_selection import StratifiedKFold, train_test_split

N_TRIALS_GBDT = 100
N_TRIALS_LOGISTIC = 25
N_FOLDS = 5
EARLY_STOP = 50
MAX_ESTIMATORS = 2000

optuna.logging.set_verbosity(optuna.logging.WARNING)


def _spw_choices(y) -> list[float]:
    ratio = float((y == 0).sum() / max((y == 1).sum(), 1))
    return [1.0, float(np.sqrt(ratio)), ratio]


def _cv_ap(make_fit, X, y, seed: int) -> float:
    from sklearn.metrics import average_precision_score

    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
    scores = []
    for tr, va in skf.split(X, y):
        X_tr, X_va = X.iloc[tr], X.iloc[va]
        y_tr, y_va = y.iloc[tr], y.iloc[va]
        X_fit, X_es, y_fit, y_es = train_test_split(
            X_tr, y_tr, test_size=0.10, stratify=y_tr, random_state=seed
        )
        model = make_fit(X_fit, y_fit, X_es, y_es)
        scores.append(average_precision_score(y_va, model.predict_proba(X_va)[:, 1]))
    return float(np.mean(scores))


def _objective(arm: str, X, y, seed: int):
    spw = _spw_choices(y)

    def objective(trial: optuna.Trial) -> float:
        if arm == "xgboost":
            from xgboost import XGBClassifier

            params = dict(
                max_depth=trial.suggest_int("max_depth", 3, 10),
                learning_rate=trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
                subsample=trial.suggest_float("subsample", 0.6, 1.0),
                colsample_bytree=trial.suggest_float("colsample_bytree", 0.6, 1.0),
                min_child_weight=trial.suggest_int("min_child_weight", 1, 20),
                reg_alpha=trial.suggest_float("reg_alpha", 1e-3, 10, log=True),
                reg_lambda=trial.suggest_float("reg_lambda", 1e-3, 10, log=True),
                scale_pos_weight=trial.suggest_categorical("scale_pos_weight", spw),
            )

            def make_fit(X_fit, y_fit, X_es, y_es):
                m = XGBClassifier(
                    n_estimators=MAX_ESTIMATORS, early_stopping_rounds=EARLY_STOP,
                    eval_metric="aucpr", tree_method="hist", n_jobs=-1,
                    random_state=seed, **params,
                )
                m.fit(X_fit, y_fit, eval_set=[(X_es, y_es)], verbose=False)
                return m

        elif arm == "lightgbm":
            import lightgbm as lgb

            params = dict(
                num_leaves=trial.suggest_int("num_leaves", 15, 255),
                learning_rate=trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
                feature_fraction=trial.suggest_float("feature_fraction", 0.6, 1.0),
                bagging_fraction=trial.suggest_float("bagging_fraction", 0.6, 1.0),
                bagging_freq=1,
                min_child_samples=trial.suggest_int("min_child_samples", 5, 100),
                lambda_l1=trial.suggest_float("lambda_l1", 1e-3, 10, log=True),
                lambda_l2=trial.suggest_float("lambda_l2", 1e-3, 10, log=True),
                scale_pos_weight=trial.suggest_categorical("scale_pos_weight", spw),
            )

            def make_fit(X_fit, y_fit, X_es, y_es):
                m = lgb.LGBMClassifier(
                    n_estimators=MAX_ESTIMATORS, n_jobs=-1, random_state=seed,
                    verbosity=-1, **params,
                )
                m.fit(X_fit, y_fit, eval_X=X_es, eval_y=y_es, eval_metric="average_precision",
                      callbacks=[lgb.early_stopping(EARLY_STOP, verbose=False)])
                return m

        elif arm == "catboost":
            from catboost import CatBoostClassifier

            params = dict(
                depth=trial.suggest_int("depth", 4, 10),
                learning_rate=trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
                l2_leaf_reg=trial.suggest_float("l2_leaf_reg", 1, 30, log=True),
                scale_pos_weight=trial.suggest_categorical("scale_pos_weight", spw),
            )

            def make_fit(X_fit, y_fit, X_es, y_es):
                m = CatBoostClassifier(
                    iterations=MAX_ESTIMATORS, od_type="Iter", od_wait=EARLY_STOP,
                    eval_metric="PRAUC", random_seed=seed, verbose=0, **params,
                )
                m.fit(X_fit, y_fit, eval_set=(X_es, y_es))
                return m

        elif arm == "logistic":
            from sklearn.linear_model import LogisticRegression
            from sklearn.pipeline import make_pipeline
            from sklearn.preprocessing import StandardScaler

            params = dict(
                C=trial.suggest_float("C", 1e-3, 1e2, log=True),
                class_weight=trial.suggest_categorical("class_weight", [None, "balanced"]),
            )

            def make_fit(X_fit, y_fit, X_es, y_es):
                m = make_pipeline(
                    StandardScaler(),
                    LogisticRegression(max_iter=2000, random_state=seed, **params),
                )
                m.fit(X_fit, y_fit)
                return m

        else:
            raise ValueError(arm)

        return _cv_ap(make_fit, X, y, seed)

    return objective


def tune(arm: str, X_train, y_train, seed: int, n_trials: int | None = None) -> optuna.Study:
    n = n_trials or (N_TRIALS_LOGISTIC if arm == "logistic" else N_TRIALS_GBDT)
    study = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=seed),
        study_name=f"{arm}-seed{seed}",
    )
    study.optimize(_objective(arm, X_train, y_train, seed), n_trials=n, show_progress_bar=False)
    return study
