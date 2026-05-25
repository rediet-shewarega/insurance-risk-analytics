import pandas as pd

from src.data_loader import add_derived_metrics, load_insurance_data


def test_add_derived_metrics(synthetic_df):
    out = add_derived_metrics(synthetic_df)
    assert {"LossRatio", "Margin", "HasClaim"}.issubset(out.columns)
    assert (out["Margin"] == out["TotalPremium"] - out["TotalClaims"]).all()
    assert out["HasClaim"].isin([0, 1]).all()


def test_load_insurance_data_roundtrip(tmp_path, synthetic_df):
    path = tmp_path / "data.csv"
    synthetic_df.to_csv(path, index=False)
    loaded = load_insurance_data(path)
    assert len(loaded) == len(synthetic_df)
    assert pd.api.types.is_datetime64_any_dtype(loaded["TransactionMonth"])
    assert loaded["Province"].dtype.name == "category"
