"""Statistical tests for the ACIS A/B hypothesis suite (Task 3)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class TestResult:
    """Single hypothesis-test outcome."""

    hypothesis: str
    test: str
    statistic: float
    p_value: float
    group_a: str
    group_b: str
    decision: str
    effect_size: float | None = None

    def as_row(self) -> dict:
        return {
            "hypothesis": self.hypothesis,
            "test": self.test,
            "group_a": self.group_a,
            "group_b": self.group_b,
            "statistic": round(self.statistic, 4),
            "p_value": round(self.p_value, 6),
            "effect_size": None if self.effect_size is None else round(self.effect_size, 4),
            "decision": self.decision,
        }


def _decision(p: float, alpha: float) -> str:
    return "Reject H0" if p < alpha else "Fail to reject H0"


def chi_squared_frequency(
    df: pd.DataFrame,
    group_col: str,
    group_a: str,
    group_b: str,
    *,
    hypothesis: str,
    alpha: float = 0.05,
) -> TestResult:
    """Chi-squared test for claim frequency (binary HasClaim) between two groups."""
    sub = df[df[group_col].isin([group_a, group_b])]
    contingency = pd.crosstab(sub[group_col], sub["HasClaim"])
    chi2, p, _, _ = stats.chi2_contingency(contingency)
    n = contingency.values.sum()
    cramers_v = float(np.sqrt(chi2 / (n * (min(contingency.shape) - 1))))
    return TestResult(
        hypothesis=hypothesis,
        test="chi-squared",
        statistic=float(chi2),
        p_value=float(p),
        group_a=str(group_a),
        group_b=str(group_b),
        effect_size=cramers_v,
        decision=_decision(p, alpha),
    )


def t_test_numeric(
    df: pd.DataFrame,
    group_col: str,
    group_a: str,
    group_b: str,
    value_col: str,
    *,
    hypothesis: str,
    alpha: float = 0.05,
    equal_var: bool = False,
    only_claims: bool = False,
) -> TestResult:
    """Welch's t-test for a numeric KPI (severity or margin) between two groups."""
    sub = df[df[group_col].isin([group_a, group_b])]
    if only_claims:
        sub = sub[sub["HasClaim"] == 1]
    a = sub.loc[sub[group_col] == group_a, value_col].dropna()
    b = sub.loc[sub[group_col] == group_b, value_col].dropna()
    if len(a) < 2 or len(b) < 2:
        raise ValueError(f"Not enough data: |A|={len(a)}, |B|={len(b)}")
    t, p = stats.ttest_ind(a, b, equal_var=equal_var)
    pooled_sd = np.sqrt(((a.var(ddof=1) * (len(a) - 1)) + (b.var(ddof=1) * (len(b) - 1)))
                        / (len(a) + len(b) - 2))
    cohens_d = float((a.mean() - b.mean()) / pooled_sd) if pooled_sd > 0 else 0.0
    return TestResult(
        hypothesis=hypothesis,
        test=f"Welch t-test ({value_col})",
        statistic=float(t),
        p_value=float(p),
        group_a=str(group_a),
        group_b=str(group_b),
        effect_size=cohens_d,
        decision=_decision(p, alpha),
    )


def z_test_proportions(
    df: pd.DataFrame,
    group_col: str,
    group_a: str,
    group_b: str,
    *,
    hypothesis: str,
    alpha: float = 0.05,
) -> TestResult:
    """Two-proportion z-test for claim frequency."""
    sub = df[df[group_col].isin([group_a, group_b])]
    counts = sub.groupby(group_col, observed=True)["HasClaim"].agg(["sum", "size"])
    s_a, n_a = counts.loc[group_a, "sum"], counts.loc[group_a, "size"]
    s_b, n_b = counts.loc[group_b, "sum"], counts.loc[group_b, "size"]
    p_a, p_b = s_a / n_a, s_b / n_b
    p_pool = (s_a + s_b) / (n_a + n_b)
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
    z = (p_a - p_b) / se if se > 0 else 0.0
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    return TestResult(
        hypothesis=hypothesis,
        test="z-test (proportions)",
        statistic=float(z),
        p_value=float(p),
        group_a=str(group_a),
        group_b=str(group_b),
        effect_size=float(p_a - p_b),
        decision=_decision(p, alpha),
    )


def anova_across_groups(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    *,
    hypothesis: str,
    alpha: float = 0.05,
    only_claims: bool = False,
    min_size: int = 30,
) -> TestResult:
    """One-way ANOVA across all categories with at least `min_size` rows."""
    sub = df.dropna(subset=[group_col, value_col])
    if only_claims:
        sub = sub[sub["HasClaim"] == 1]
    grouped = [g[value_col].values for _, g in sub.groupby(group_col, observed=True)
               if len(g) >= min_size]
    if len(grouped) < 2:
        raise ValueError("Need >=2 groups meeting min_size for ANOVA")
    f, p = stats.f_oneway(*grouped)
    return TestResult(
        hypothesis=hypothesis,
        test=f"ANOVA ({value_col})",
        statistic=float(f),
        p_value=float(p),
        group_a="ALL",
        group_b=f"{len(grouped)} groups",
        decision=_decision(p, alpha),
    )


def results_table(results: list[TestResult]) -> pd.DataFrame:
    return pd.DataFrame([r.as_row() for r in results])
