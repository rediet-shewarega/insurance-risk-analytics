"""Reusable EDA helpers — summaries, quality checks, and plotting."""

from __future__ import annotations

from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def missing_value_report(df: pd.DataFrame) -> pd.DataFrame:
    """Per-column missing counts and percentages, sorted descending."""
    counts = df.isna().sum()
    pct = (counts / len(df) * 100).round(2)
    report = pd.DataFrame({"missing": counts, "pct": pct, "dtype": df.dtypes.astype(str)})
    return report[report["missing"] > 0].sort_values("missing", ascending=False)


def numeric_summary(df: pd.DataFrame, cols: Iterable[str] | None = None) -> pd.DataFrame:
    """Descriptive stats with skew and kurtosis for numerical columns."""
    if cols is None:
        cols = df.select_dtypes(include=np.number).columns
    sub = df[list(cols)]
    desc = sub.describe().T
    desc["skew"] = sub.skew(numeric_only=True)
    desc["kurtosis"] = sub.kurt(numeric_only=True)
    return desc


def loss_ratio_by(df: pd.DataFrame, group: str) -> pd.DataFrame:
    """Aggregate loss ratio and exposure metrics by a categorical column."""
    g = df.groupby(group, observed=True).agg(
        policies=("TotalPremium", "size"),
        total_premium=("TotalPremium", "sum"),
        total_claims=("TotalClaims", "sum"),
        claim_count=("HasClaim", "sum"),
    )
    g["loss_ratio"] = g["total_claims"] / g["total_premium"].replace(0, np.nan)
    g["claim_frequency"] = g["claim_count"] / g["policies"]
    return g.sort_values("loss_ratio", ascending=False)


def plot_numeric_distributions(
    df: pd.DataFrame,
    cols: Iterable[str],
    *,
    bins: int = 50,
    ncols: int = 3,
    figsize: tuple[int, int] | None = None,
):
    """Grid of histograms for numerical columns."""
    cols = [c for c in cols if c in df.columns]
    nrows = int(np.ceil(len(cols) / ncols))
    figsize = figsize or (5 * ncols, 3.2 * nrows)
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    axes = np.atleast_1d(axes).ravel()
    for ax, col in zip(axes, cols):
        df[col].dropna().plot(kind="hist", bins=bins, ax=ax, edgecolor="white")
        ax.set_title(col)
        ax.set_xlabel("")
    for ax in axes[len(cols):]:
        ax.set_visible(False)
    fig.tight_layout()
    return fig


def plot_categorical_counts(
    df: pd.DataFrame,
    cols: Iterable[str],
    *,
    top_n: int = 15,
    ncols: int = 2,
):
    """Bar charts of the top categories for each categorical column."""
    cols = [c for c in cols if c in df.columns]
    nrows = int(np.ceil(len(cols) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(7 * ncols, 3.2 * nrows))
    axes = np.atleast_1d(axes).ravel()
    for ax, col in zip(axes, cols):
        counts = df[col].value_counts(dropna=False).head(top_n)
        sns.barplot(x=counts.values, y=counts.index.astype(str), ax=ax, color="#3a7ca5")
        ax.set_title(col)
        ax.set_xlabel("count")
    for ax in axes[len(cols):]:
        ax.set_visible(False)
    fig.tight_layout()
    return fig


def plot_loss_ratio_by(df: pd.DataFrame, group: str, top_n: int = 15):
    """Horizontal bar chart of loss ratio per group, weighted by exposure."""
    agg = loss_ratio_by(df, group).head(top_n)
    fig, ax = plt.subplots(figsize=(8, 0.4 * len(agg) + 1.5))
    sns.barplot(x=agg["loss_ratio"], y=agg.index.astype(str), ax=ax, color="#c44536")
    ax.axvline(
        df["TotalClaims"].sum() / df["TotalPremium"].sum(),
        color="black",
        linestyle="--",
        label="portfolio avg",
    )
    ax.set_xlabel("Loss Ratio")
    ax.set_ylabel(group)
    ax.set_title(f"Loss ratio by {group} (top {top_n})")
    ax.legend()
    fig.tight_layout()
    return fig


def plot_temporal_trends(df: pd.DataFrame):
    """Monthly claim frequency and severity over time."""
    if "TransactionMonth" not in df.columns:
        raise KeyError("TransactionMonth not in DataFrame")
    monthly = (
        df.assign(month=df["TransactionMonth"].dt.to_period("M").dt.to_timestamp())
        .groupby("month")
        .agg(
            policies=("TotalPremium", "size"),
            claims=("HasClaim", "sum"),
            severity=("TotalClaims", lambda s: s[s > 0].mean()),
        )
    )
    monthly["frequency"] = monthly["claims"] / monthly["policies"]

    fig, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(monthly.index, monthly["frequency"], color="#3a7ca5", marker="o", label="Frequency")
    ax1.set_ylabel("Claim frequency", color="#3a7ca5")
    ax2 = ax1.twinx()
    ax2.plot(monthly.index, monthly["severity"], color="#c44536", marker="s", label="Severity")
    ax2.set_ylabel("Mean claim amount (Rand)", color="#c44536")
    ax1.set_title("Monthly claim frequency vs severity")
    fig.tight_layout()
    return fig, monthly


def detect_outliers_iqr(series: pd.Series, k: float = 1.5) -> pd.Series:
    """Return a boolean mask flagging IQR outliers."""
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    return (series < q1 - k * iqr) | (series > q3 + k * iqr)
