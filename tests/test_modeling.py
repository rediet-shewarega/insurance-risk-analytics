import numpy as np

from src.data_loader import add_derived_metrics
from src.modeling import engineer_features, expected_premium


def test_engineer_features_adds_vehicle_age(synthetic_df):
    df = add_derived_metrics(synthetic_df)
    out = engineer_features(df)
    assert "VehicleAge" in out.columns
    assert (out["VehicleAge"] >= 0).all()


def test_expected_premium_formula():
    p = np.array([0.1, 0.2])
    sev = np.array([1000.0, 2000.0])
    result = expected_premium(p, sev, expense_loading=50.0, profit_margin=20.0)
    np.testing.assert_allclose(result, [0.1 * 1000 + 70, 0.2 * 2000 + 70])
