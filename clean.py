"""Deep cleaning routines for marketplace sales data."""
from __future__ import annotations

import pandas as pd

from .config import CRITICAL_TEXT_COLUMNS, DUMMY_VALUES, REQUIRED_COLUMNS, TEXT_COLUMNS


def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean placeholders, missing values, duplicates, and base data types."""
    cleaned = df.copy()
    cleaned = cleaned[REQUIRED_COLUMNS].copy()

    cleaned.columns = cleaned.columns.str.strip()
    cleaned = _strip_text_values(cleaned)
    cleaned = _replace_dummy_customer_names(cleaned)
    cleaned = _remove_dummy_rows(cleaned)
    cleaned = _coerce_numeric_columns(cleaned)
    cleaned = _clean_postal_code(cleaned)

    cleaned = cleaned.dropna(subset=["Order ID", "Customer ID", "Product ID", "Sales", "Quantity"])
    cleaned = cleaned.drop_duplicates()
    cleaned = cleaned.drop_duplicates(subset=["Row ID"], keep="first")
    cleaned = cleaned.sort_values("Row ID").reset_index(drop=True)
    return cleaned


def _strip_text_values(df: pd.DataFrame) -> pd.DataFrame:
    text_cols = [col for col in TEXT_COLUMNS if col in df.columns]
    for col in text_cols:
        df[col] = df[col].astype("string").str.strip()
        df[col] = df[col].replace({"": pd.NA})
    return df


def _remove_dummy_rows(df: pd.DataFrame) -> pd.DataFrame:
    # Drop rows with placeholder/test text in critical fields other than
    # Customer Name. Dummy customer names are retained as Unknown Customer when
    # the rest of the order is valid, such as Row ID=2 in the raw file.
    dummy_mask = pd.Series(False, index=df.index)
    for col in [col for col in CRITICAL_TEXT_COLUMNS if col != "Customer Name"]:
        normalized = df[col].astype("string").str.strip().str.lower()
        dummy_mask = dummy_mask | normalized.isin(DUMMY_VALUES)
    return df.loc[~dummy_mask].copy()


def _replace_dummy_customer_names(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df["Customer Name"].astype("string").str.strip().str.lower()
    df.loc[normalized.isin(DUMMY_VALUES), "Customer Name"] = "Unknown Customer"
    return df


def _coerce_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    for col in ["Sales", "Discount", "Profit"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").round(4)
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").astype("Int64")
    df["Row ID"] = pd.to_numeric(df["Row ID"], errors="coerce").astype("Int64")
    return df


def _clean_postal_code(df: pd.DataFrame) -> pd.DataFrame:
    postal = df["Postal Code"].astype("string").str.strip()
    postal = postal.str.replace(r"\.0$", "", regex=True)
    df["Postal Code"] = postal.fillna("Unknown")
    return df
