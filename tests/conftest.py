"""Shared pytest fixtures."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture
def synthetic_df() -> pd.DataFrame:
    """Small synthetic dataset shaped like the real ACIS data."""
    rng = np.random.default_rng(0)
    n = 400
    province = rng.choice(["Gauteng", "Western Cape", "KwaZulu-Natal"], n, p=[0.5, 0.3, 0.2])
    gender = rng.choice(["Male", "Female"], n)
    has_claim = rng.binomial(1, 0.15, n)
    severity = np.where(has_claim, rng.gamma(2.0, 4000, n), 0.0)
    premium = rng.gamma(3.0, 800, n) + 200
    df = pd.DataFrame(
        {
            "TransactionMonth": pd.to_datetime(
                rng.choice(pd.date_range("2014-02-01", "2015-08-01", freq="MS"), n)
            ),
            "Province": pd.Categorical(province),
            "Gender": pd.Categorical(gender),
            "PostalCode": pd.Categorical(rng.integers(1000, 1010, n).astype(str)),
            "RegistrationYear": rng.integers(2000, 2015, n),
            "SumInsured": rng.gamma(3.0, 50000, n),
            "CustomValueEstimate": rng.gamma(3.0, 45000, n),
            "TotalPremium": premium,
            "TotalClaims": severity,
        }
    )
    return df
