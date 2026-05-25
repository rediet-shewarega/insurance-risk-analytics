"""Load and standardise the ACIS insurance dataset."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATE_COLUMNS = ["TransactionMonth", "VehicleIntroDate"]

NUMERIC_COLUMNS = [
    "TotalPremium",
    "TotalClaims",
    "SumInsured",
    "CalculatedPremiumPerTerm",
    "CustomValueEstimate",
    "CapitalOutstanding",
    "RegistrationYear",
    "Cylinders",
    "Cubiccapacity",
    "Kilowatts",
    "NumberOfDoors",
    "NumberOfVehiclesInFleet",
]

CATEGORICAL_COLUMNS = [
    "IsVATRegistered",
    "Citizenship",
    "LegalType",
    "Title",
    "Language",
    "Bank",
    "AccountType",
    "MaritalStatus",
    "Gender",
    "Country",
    "Province",
    "PostalCode",
    "MainCrestaZone",
    "SubCrestaZone",
    "ItemType",
    "VehicleType",
    "Make",
    "Model",
    "Bodytype",
    "AlarmImmobiliser",
    "TrackingDevice",
    "NewVehicle",
    "WrittenOff",
    "Rebuilt",
    "Converted",
    "CrossBorder",
    "TermFrequency",
    "ExcessSelected",
    "CoverCategory",
    "CoverType",
    "CoverGroup",
    "Section",
    "Product",
    "StatutoryClass",
    "StatutoryRiskType",
]


def load_insurance_data(
    path: str | Path,
    *,
    sep: str | None = None,
    parse_dates: bool = True,
) -> pd.DataFrame:
    """Read the insurance dataset and coerce types.

    Auto-detects `,`, `|`, and `\\t` separators if `sep` is None.
    Unknown columns are passed through untouched so the loader is robust to
    minor schema changes.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    if sep is None:
        sep = _sniff_separator(path)

    df = pd.read_csv(path, sep=sep, low_memory=False)

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if parse_dates:
        for col in DATE_COLUMNS:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in CATEGORICAL_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype("category")

    return df


def _sniff_separator(path: Path) -> str:
    with path.open("r", encoding="utf-8", errors="ignore") as fh:
        header = fh.readline()
    for candidate in ("|", "\t", ","):
        if candidate in header:
            return candidate
    return ","


def add_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Append the project's core derived metrics.

    - `LossRatio` = TotalClaims / TotalPremium (NaN when premium is 0)
    - `Margin` = TotalPremium - TotalClaims
    - `HasClaim` = TotalClaims > 0
    """
    out = df.copy()
    premium = out["TotalPremium"].replace(0, pd.NA)
    out["LossRatio"] = out["TotalClaims"] / premium
    out["Margin"] = out["TotalPremium"] - out["TotalClaims"]
    out["HasClaim"] = (out["TotalClaims"] > 0).astype(int)
    return out
