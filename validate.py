"""Validation checks that protect Power BI imports from bad types and dates."""
from __future__ import annotations

import pandas as pd

from .config import DATE_COLUMNS, REQUIRED_COLUMNS


def validate_powerbi_dataset(df: pd.DataFrame) -> None:
    """Raise ValueError when the final dataset has BI-breaking issues."""
    errors: list[str] = []

    missing = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing:
        errors.append(f"Missing required columns: {missing}")

    for col in DATE_COLUMNS:
        if col in df.columns and not pd.api.types.is_datetime64_any_dtype(df[col]):
            errors.append(f"{col} must be datetime64, found {df[col].dtype}")
        elif col in df.columns and df[col].isna().any():
            errors.append(f"{col} contains {int(df[col].isna().sum())} invalid dates")

    if "Days to Ship" in df.columns and (df["Days to Ship"].dropna() < 0).any():
        count = int((df["Days to Ship"].dropna() < 0).sum())
        errors.append(f"Days to Ship contains {count} negative values")

    numeric_columns = ["Sales", "Quantity", "Discount", "Profit", "Profit Margin"]
    for col in numeric_columns:
        if col in df.columns and df[col].isna().any():
            errors.append(f"{col} contains {int(df[col].isna().sum())} null values")

    if "Quantity" in df.columns and (df["Quantity"].dropna() <= 0).any():
        errors.append("Quantity must be positive")
    if "Discount" in df.columns and (~df["Discount"].between(0, 1)).any():
        errors.append("Discount must be between 0 and 1")

    if errors:
        raise ValueError("Power BI validation failed:\n- " + "\n- ".join(errors))
