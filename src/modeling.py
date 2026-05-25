"""Modeling utilities for severity prediction and claim-probability scoring (Task 4)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

try:
    from xgboost import XGBClassifier, XGBRegressor
    HAS_XGB = True
except ImportError:  # pragma: no cover
    HAS_XGB = False


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add vehicle age, policy-duration proxies, and a few interaction terms."""
    out = df.copy()
    if "RegistrationYear" in out.columns and "TransactionMonth" in out.columns:
        out["VehicleAge"] = out["TransactionMonth"].dt.year - out["RegistrationYear"]
        out["VehicleAge"] = out["VehicleAge"].clip(lower=0)
    if "CustomValueEstimate" in out.columns and "SumInsured" in out.columns:
        out["InsuredValueGap"] = out["SumInsured"] - out["CustomValueEstimate"]
    if "TotalPremium" in out.columns and "SumInsured" in out.columns:
        out["PremiumPerInsured"] = out["TotalPremium"] / out["SumInsured"].replace(0, np.nan)
    return out


def build_preprocessor(
    numeric: Iterable[str],
    categorical: Iterable[str],
) -> ColumnTransformer:
    """Standard imputer + scaler / one-hot encoder pipeline."""
    return ColumnTransformer(
        [
            (
                "num",
                Pipeline([
                    ("impute", SimpleImputer(strategy="median")),
                    ("scale", StandardScaler()),
                ]),
                list(numeric),
            ),
            (
                "cat",
                Pipeline([
                    ("impute", SimpleImputer(strategy="most_frequent")),
                    ("ohe", OneHotEncoder(handle_unknown="ignore", min_frequency=0.01)),
                ]),
                list(categorical),
            ),
        ],
        remainder="drop",
    )


@dataclass
class RegressionResult:
    name: str
    rmse: float
    r2: float
    model: object | None = field(default=None, repr=False)


@dataclass
class ClassificationResult:
    name: str
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float
    model: object | None = field(default=None, repr=False)


def regression_models() -> dict[str, object]:
    models = {
        "LinearRegression": LinearRegression(),
        "RandomForest": RandomForestRegressor(
            n_estimators=300, max_depth=None, n_jobs=-1, random_state=42
        ),
    }
    if HAS_XGB:
        models["XGBoost"] = XGBRegressor(
            n_estimators=600,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
            n_jobs=-1,
        )
    return models


def classification_models() -> dict[str, object]:
    models = {
        "LogisticRegression": LogisticRegression(max_iter=2000, n_jobs=-1),
        "RandomForest": RandomForestClassifier(
            n_estimators=400, max_depth=None, n_jobs=-1, random_state=42
        ),
    }
    if HAS_XGB:
        models["XGBoost"] = XGBClassifier(
            n_estimators=600,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
            n_jobs=-1,
            eval_metric="logloss",
        )
    return models


def evaluate_regressors(
    X: pd.DataFrame,
    y: pd.Series,
    preprocessor: ColumnTransformer,
    *,
    test_size: float = 0.2,
    random_state: int = 42,
) -> tuple[list[RegressionResult], dict]:
    """Train regression_models() on (X, y) and return per-model RMSE/R^2."""
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=test_size, random_state=random_state)
    results, fitted = [], {}
    for name, est in regression_models().items():
        pipe = Pipeline([("pre", preprocessor), ("model", est)])
        pipe.fit(Xtr, ytr)
        pred = pipe.predict(Xte)
        rmse = float(np.sqrt(mean_squared_error(yte, pred)))
        r2 = float(r2_score(yte, pred))
        results.append(RegressionResult(name=name, rmse=rmse, r2=r2, model=pipe))
        fitted[name] = pipe
    return results, fitted


def evaluate_classifiers(
    X: pd.DataFrame,
    y: pd.Series,
    preprocessor: ColumnTransformer,
    *,
    test_size: float = 0.2,
    random_state: int = 42,
) -> tuple[list[ClassificationResult], dict]:
    """Train classification_models() on (X, y) and return accuracy/precision/recall/F1/AUC."""
    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    results, fitted = [], {}
    for name, est in classification_models().items():
        pipe = Pipeline([("pre", preprocessor), ("model", est)])
        pipe.fit(Xtr, ytr)
        pred = pipe.predict(Xte)
        proba = pipe.predict_proba(Xte)[:, 1] if hasattr(pipe, "predict_proba") else pred
        results.append(
            ClassificationResult(
                name=name,
                accuracy=float(accuracy_score(yte, pred)),
                precision=float(precision_score(yte, pred, zero_division=0)),
                recall=float(recall_score(yte, pred, zero_division=0)),
                f1=float(f1_score(yte, pred, zero_division=0)),
                roc_auc=float(roc_auc_score(yte, proba)),
                model=pipe,
            )
        )
        fitted[name] = pipe
    return results, fitted


def expected_premium(
    p_claim: np.ndarray,
    predicted_severity: np.ndarray,
    *,
    expense_loading: float = 0.0,
    profit_margin: float = 0.0,
) -> np.ndarray:
    """Compose the risk-based premium formula.

    Premium = P(claim) * Predicted Severity + Expense Loading + Profit Margin
    """
    return p_claim * predicted_severity + expense_loading + profit_margin
