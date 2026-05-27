"""Tiny CLI for data-pipeline stages referenced from `dvc.yaml`."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from src.data_loader import add_derived_metrics, load_insurance_data


def clean(in_path: str, out_path: str, *, claim_cap_quantile: float = 0.995) -> None:
    """Drop invalid rows and cap extreme claim amounts."""
    df = add_derived_metrics(load_insurance_data(in_path))
    df = df[(df["TotalPremium"] > 0) & (df["TotalClaims"] >= 0)].copy()
    cap = df["TotalClaims"].quantile(claim_cap_quantile)
    df.loc[df["TotalClaims"] > cap, "TotalClaims"] = cap
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"cleaned {in_path} -> {out_path} ({len(df):,} rows, cap={cap:.2f})")


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    if not argv:
        print("usage: python -m src.pipeline <stage> [args...]", file=sys.stderr)
        return 1
    stage, *rest = argv
    if stage == "clean":
        if len(rest) != 2:
            print("usage: python -m src.pipeline clean <in> <out>", file=sys.stderr)
            return 2
        clean(rest[0], rest[1])
        return 0
    print(f"unknown stage: {stage}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
