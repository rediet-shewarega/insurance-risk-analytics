from src.data_loader import add_derived_metrics
from src.hypothesis_tests import (
    chi_squared_frequency,
    results_table,
    t_test_numeric,
    z_test_proportions,
)


def test_chi_squared_runs(synthetic_df):
    df = add_derived_metrics(synthetic_df)
    res = chi_squared_frequency(
        df, "Province", "Gauteng", "Western Cape",
        hypothesis="test",
    )
    assert 0.0 <= res.p_value <= 1.0
    assert res.test == "chi-squared"
    assert res.decision in {"Reject H0", "Fail to reject H0"}


def test_t_test_runs(synthetic_df):
    df = add_derived_metrics(synthetic_df)
    res = t_test_numeric(
        df, "Gender", "Male", "Female", "Margin",
        hypothesis="test",
    )
    assert 0.0 <= res.p_value <= 1.0


def test_z_test_proportions(synthetic_df):
    df = add_derived_metrics(synthetic_df)
    res = z_test_proportions(
        df, "Gender", "Male", "Female",
        hypothesis="test",
    )
    assert 0.0 <= res.p_value <= 1.0
    assert res.test == "z-test (proportions)"


def test_results_table(synthetic_df):
    df = add_derived_metrics(synthetic_df)
    res = chi_squared_frequency(
        df, "Province", "Gauteng", "Western Cape", hypothesis="h"
    )
    table = results_table([res])
    assert {"hypothesis", "p_value", "decision"}.issubset(table.columns)
