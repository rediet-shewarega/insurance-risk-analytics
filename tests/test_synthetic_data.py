from src import synthetic_data as sd


def test_generate_shape_and_columns():
    df = sd.generate(n_rows=500, seed=0)
    assert len(df) == 500
    expected = {
        "TransactionMonth", "Province", "Gender", "PostalCode",
        "TotalPremium", "TotalClaims", "SumInsured", "CalculatedPremiumPerTerm",
    }
    assert expected.issubset(df.columns)


def test_generate_has_claim_signal():
    df = sd.generate(n_rows=2000, seed=0)
    rate = (df["TotalClaims"] > 0).mean()
    assert 0.05 <= rate <= 0.6
