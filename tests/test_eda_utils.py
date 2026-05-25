from src import eda_utils as eu
from src.data_loader import add_derived_metrics


def test_missing_value_report_handles_no_missing(synthetic_df):
    report = eu.missing_value_report(synthetic_df)
    assert report.empty


def test_loss_ratio_by_returns_expected_columns(synthetic_df):
    df = add_derived_metrics(synthetic_df)
    agg = eu.loss_ratio_by(df, "Province")
    assert {"loss_ratio", "claim_frequency", "policies"}.issubset(agg.columns)
    assert (agg["policies"] > 0).all()


def test_detect_outliers_iqr_flags_extremes(synthetic_df):
    flags = eu.detect_outliers_iqr(synthetic_df["TotalPremium"])
    assert flags.dtype == bool
    assert len(flags) == len(synthetic_df)
