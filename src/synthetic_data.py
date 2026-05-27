"""Generate synthetic ACIS-shaped data for smoke tests and notebook demos.

NOT a substitute for the real ACIS dataset — this only mimics the schema so the
notebooks, pipelines, and CI can run end-to-end. All distributions are toy
defaults chosen to make tests interesting (e.g. modest province-level risk
differences), not to reflect reality.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PROVINCES = [
    "Gauteng",
    "Western Cape",
    "KwaZulu-Natal",
    "Eastern Cape",
    "Free State",
    "Mpumalanga",
    "Limpopo",
    "North West",
    "Northern Cape",
]
VEHICLE_TYPES = ["Passenger Vehicle", "Light Commercial", "Heavy Commercial", "Motorcycle"]
MAKES = ["Toyota", "Volkswagen", "Ford", "Nissan", "BMW", "Mercedes", "Hyundai", "Kia", "Mazda"]
COVER_TYPES = ["Comprehensive", "Third Party", "Third Party Fire & Theft"]
TERMS = ["Monthly", "Annual", "Quarterly"]


def generate(n_rows: int = 20_000, seed: int = 42) -> pd.DataFrame:
    """Return a synthetic DataFrame with ACIS-style columns and modest signal."""
    rng = np.random.default_rng(seed)

    province = rng.choice(PROVINCES, n_rows, p=_softmax(rng.normal(size=len(PROVINCES))))
    gender = rng.choice(["Male", "Female"], n_rows, p=[0.58, 0.42])
    marital = rng.choice(["Single", "Married", "Divorced", "Widowed"], n_rows,
                         p=[0.45, 0.45, 0.07, 0.03])
    vehicle_type = rng.choice(VEHICLE_TYPES, n_rows, p=[0.78, 0.15, 0.05, 0.02])
    make = rng.choice(MAKES, n_rows)
    cover = rng.choice(COVER_TYPES, n_rows, p=[0.7, 0.2, 0.1])
    term = rng.choice(TERMS, n_rows, p=[0.7, 0.2, 0.1])
    postal = rng.integers(1000, 1050, n_rows).astype(str)

    months = pd.date_range("2014-02-01", "2015-08-01", freq="MS")
    tx_month = rng.choice(months, n_rows)
    reg_year = rng.integers(1998, 2015, n_rows)
    kw = rng.gamma(3, 30, n_rows).round(1)
    cubic = (kw * rng.uniform(12, 30, n_rows)).round(0)
    cyl = rng.choice([3, 4, 6, 8], n_rows, p=[0.05, 0.7, 0.2, 0.05])
    doors = rng.choice([2, 4, 5], n_rows, p=[0.1, 0.5, 0.4])

    sum_insured = rng.gamma(3, 90_000, n_rows).round(0)
    custom_value = (sum_insured * rng.normal(0.95, 0.1, n_rows)).clip(min=0).round(0)
    premium = (rng.gamma(3, 600, n_rows) + 200).round(2)

    # Per-row claim probability has small dependencies on province / vehicle age.
    province_lift = pd.Series(
        rng.uniform(0.8, 1.4, len(PROVINCES)), index=PROVINCES
    )[province].to_numpy()
    vehicle_age = np.clip(pd.to_datetime(tx_month).year.to_numpy() - reg_year, 0, None)
    age_lift = 1 + vehicle_age * 0.015
    base_p = 0.12
    p_claim = np.clip(base_p * province_lift * age_lift, 0.01, 0.7)
    has_claim = rng.binomial(1, p_claim, n_rows)
    severity = np.where(
        has_claim == 1,
        rng.gamma(2.0, 6_000, n_rows) * (1 + vehicle_age * 0.02),
        0.0,
    ).round(2)

    df = pd.DataFrame(
        {
            "UnderwrittenCoverID": np.arange(1, n_rows + 1),
            "PolicyID": rng.integers(100_000, 999_999, n_rows),
            "TransactionMonth": tx_month,
            "IsVATRegistered": rng.choice([True, False], n_rows, p=[0.2, 0.8]),
            "Citizenship": "South Africa",
            "LegalType": rng.choice(["Individual", "Close Corporation", "Pty Ltd"], n_rows,
                                    p=[0.85, 0.1, 0.05]),
            "Title": rng.choice(["Mr", "Mrs", "Ms", "Dr"], n_rows, p=[0.5, 0.3, 0.18, 0.02]),
            "Language": "English",
            "Bank": rng.choice(["FNB", "Standard Bank", "ABSA", "Nedbank", "Capitec"], n_rows),
            "AccountType": rng.choice(["Current", "Savings"], n_rows, p=[0.85, 0.15]),
            "MaritalStatus": marital,
            "Gender": gender,
            "Country": "South Africa",
            "Province": province,
            "PostalCode": postal,
            "MainCrestaZone": rng.choice(["Zone " + s for s in "ABCDEF"], n_rows),
            "SubCrestaZone": rng.choice([f"{a}{b}" for a in "ABCDEF" for b in "12345"], n_rows),
            "ItemType": "Vehicle",
            "Mmcode": rng.integers(10_000, 99_999, n_rows),
            "VehicleType": vehicle_type,
            "RegistrationYear": reg_year,
            "Make": make,
            "Model": [f"Model-{rng.integers(1, 50)}" for _ in range(n_rows)],
            "Cylinders": cyl,
            "Cubiccapacity": cubic,
            "Kilowatts": kw,
            "Bodytype": rng.choice(["Sedan", "Hatchback", "SUV", "Bakkie", "Coupe"], n_rows),
            "NumberOfDoors": doors,
            "VehicleIntroDate": pd.to_datetime(
                pd.DataFrame({"year": reg_year, "month": 1, "day": 1})
            ),
            "CustomValueEstimate": custom_value,
            "AlarmImmobiliser": rng.choice(["Yes", "No"], n_rows, p=[0.8, 0.2]),
            "TrackingDevice": rng.choice(["Yes", "No"], n_rows, p=[0.4, 0.6]),
            "CapitalOutstanding": (sum_insured * rng.uniform(0, 0.7, n_rows)).round(0),
            "NewVehicle": rng.choice(["Yes", "No"], n_rows, p=[0.15, 0.85]),
            "WrittenOff": rng.choice([True, False], n_rows, p=[0.02, 0.98]),
            "Rebuilt": rng.choice([True, False], n_rows, p=[0.03, 0.97]),
            "Converted": rng.choice([True, False], n_rows, p=[0.01, 0.99]),
            "CrossBorder": rng.choice([True, False], n_rows, p=[0.05, 0.95]),
            "NumberOfVehiclesInFleet": rng.choice([1, 2, 3, 5], n_rows, p=[0.85, 0.1, 0.03, 0.02]),
            "SumInsured": sum_insured,
            "TermFrequency": term,
            "CalculatedPremiumPerTerm": premium,
            "ExcessSelected": rng.choice([500, 1000, 2500, 5000], n_rows, p=[0.4, 0.3, 0.2, 0.1]),
            "CoverCategory": rng.choice(["Mobility", "Cover", "Optional"], n_rows, p=[0.5, 0.3, 0.2]),
            "CoverType": cover,
            "CoverGroup": rng.choice(["Group A", "Group B", "Group C"], n_rows, p=[0.5, 0.3, 0.2]),
            "Section": rng.choice(["Motor", "Other"], n_rows, p=[0.95, 0.05]),
            "Product": rng.choice(["Mobility Metered", "Standard Auto"], n_rows, p=[0.3, 0.7]),
            "StatutoryClass": "Commercial",
            "StatutoryRiskType": "IFRS Constant",
            "TotalPremium": premium,
            "TotalClaims": severity,
        }
    )
    # Sprinkle some missing values so quality checks have work to do.
    for col, frac in [("CustomValueEstimate", 0.04), ("Bank", 0.02), ("Bodytype", 0.01)]:
        idx = rng.choice(n_rows, int(n_rows * frac), replace=False)
        df.loc[idx, col] = np.nan
    return df


def _softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - x.max())
    return e / e.sum()


def main(out: str = "data/insurance_data_synth.csv", n_rows: int = 20_000) -> None:
    df = generate(n_rows=n_rows)
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"wrote {len(df):,} rows to {path}")


if __name__ == "__main__":
    main()
