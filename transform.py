"""Feature engineering for Power BI-ready ecommerce analytics."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .config import ACTIVE_CUSTOMER_WINDOW_DAYS, DATE_COLUMNS


def transform_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """Add date, shipping, profitability, and customer segmentation features."""
    transformed = df.copy()
    transformed = _parse_dates(transformed)
    transformed = _add_order_features(transformed)
    transformed = _add_customer_features(transformed)
    transformed = _optimize_powerbi_types(transformed)
    return transformed.sort_values(["Order Date", "Order ID", "Row ID"]).reset_index(drop=True)


def _parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    for col in DATE_COLUMNS:
        df[col] = df[col].apply(_parse_mixed_date)
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def _parse_mixed_date(value: object) -> pd.Timestamp | pd.NaT: # type: ignore
    if pd.isna(value):
        return pd.NaT

    text = str(value).strip()
    if not text:
        return pd.NaT

    # The source file mixes slash dates with values like 2020-08-11.
    # In this dataset, hyphenated dates are exported as YYYY-DD-MM.
    formats = (
        "%Y-%d-%m",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d-%m-%Y",
        "%m-%d-%Y",
    )
    for fmt in formats:
        parsed = pd.to_datetime(text, format=fmt, errors="coerce")
        if pd.notna(parsed):
            return parsed.normalize()
    return pd.to_datetime(text, errors="coerce", dayfirst=True)


def _add_order_features(df: pd.DataFrame) -> pd.DataFrame:
    df["Days to Ship"] = (df["Ship Date"] - df["Order Date"]).dt.days.astype("Int64")
    df["Profit Margin"] = np.where(df["Sales"] != 0, df["Profit"] / df["Sales"], 0).round(4)
    df["Order Year"] = df["Order Date"].dt.year.astype("Int64")
    df["Order Quarter"] = df["Order Date"].dt.to_period("Q").astype("string")
    df["Order Month"] = df["Order Date"].dt.to_period("M").astype("string")
    df["Order Month Date"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
    df["Is Profitable"] = df["Profit"] > 0
    df["Discount Band"] = pd.cut(
        df["Discount"],
        bins=[-0.001, 0, 0.2, 0.5, 1],
        labels=["No Discount", "Low", "Medium", "High"],
    ).astype("string")
    return df


def _add_customer_features(df: pd.DataFrame) -> pd.DataFrame:
    max_order_date = df["Order Date"].max()
    customer_orders = df.groupby("Customer ID")["Order ID"].nunique()
    first_order = df.groupby("Customer ID")["Order Date"].min()
    last_order = df.groupby("Customer ID")["Order Date"].max()
    monetary = df.groupby("Customer ID")["Sales"].sum()
    recency_days = (max_order_date - last_order).dt.days

    df["Customer Order Count"] = df["Customer ID"].map(customer_orders).astype("Int64")
    df["Customer First Order Date"] = df["Customer ID"].map(first_order)
    df["Customer Last Order Date"] = df["Customer ID"].map(last_order)
    df["Customer Recency Days"] = df["Customer ID"].map(recency_days).astype("Int64")
    df["Repeat Customer Flag"] = df["Customer Order Count"] > 1
    df["New Customer Flag"] = df["Order Date"].dt.to_period("M") == df[
        "Customer First Order Date"
    ].dt.to_period("M")
    df["Active Customer Flag"] = df["Customer Last Order Date"] >= (
        max_order_date - pd.Timedelta(days=ACTIVE_CUSTOMER_WINDOW_DAYS)
    )
    df["Customer Status"] = np.where(df["Active Customer Flag"], "Active", "Inactive")

    frequency = df["Customer ID"].map(customer_orders).astype(float)
    value = df["Customer ID"].map(monetary).astype(float)
    recency = df["Customer Recency Days"].astype(float)
    df["Customer Recency Segment"] = _safe_quantile_label(
        recency, ["Recent", "Warm", "Lapsed"]
    )
    df["Customer Frequency Segment"] = _safe_quantile_label(
        frequency, ["Low Frequency", "Medium Frequency", "High Frequency"]
    )
    df["Customer Value Segment"] = _safe_quantile_label(
        value, ["Low Value", "Medium Value", "High Value"]
    )
    df["Customer Segment Label"] = (
        df["Customer Recency Segment"]
        + " / "
        + df["Customer Frequency Segment"]
        + " / "
        + df["Customer Value Segment"]
    )
    return df


def _safe_quantile_label(series: pd.Series, labels: list[str]) -> pd.Series:
    ranked = series.rank(method="first")
    try:
        return pd.qcut(ranked, q=len(labels), labels=labels).astype("string")
    except ValueError:
        return pd.Series(labels[0], index=series.index, dtype="string")


def _optimize_powerbi_types(df: pd.DataFrame) -> pd.DataFrame:
    for col in ["Sales", "Discount", "Profit", "Profit Margin"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").round(4)
    for col in ["Row ID", "Quantity", "Days to Ship", "Order Year", "Customer Order Count", "Customer Recency Days"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    for col in DATE_COLUMNS + ["Order Month Date", "Customer First Order Date", "Customer Last Order Date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df
