"""KPI calculations for ecommerce marketplace analysis."""
from __future__ import annotations

import pandas as pd


def calculate_kpis(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Return KPI tables ready to export to Excel and Power BI."""
    return {
        "Executive KPIs": _executive_kpis(df),
        "Monthly KPIs": _monthly_kpis(df),
        "Category Performance": _category_performance(df),
        "Product Performance": _product_performance(df),
        "Region Performance": _region_performance(df),
        "Customer Segments": _customer_segments(df),
    }


def _executive_kpis(df: pd.DataFrame) -> pd.DataFrame:
    order_count = df["Order ID"].nunique()
    customer_count = df["Customer ID"].nunique()
    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    average_order_value = round(total_sales / order_count, 4) if order_count else 0
    profit_margin = round(total_profit / total_sales, 4) if total_sales else 0
    return pd.DataFrame(
        [
            {"Metric": "Total Sales", "Value": total_sales},
            {"Metric": "Total Profit", "Value": total_profit},
            {"Metric": "Total Orders", "Value": order_count},
            {"Metric": "Total Customers", "Value": customer_count},
            {"Metric": "Average Order Value", "Value": average_order_value},
            {"Metric": "Profit Margin", "Value": profit_margin},
            {"Metric": "Customer Lifetime Value", "Value": total_sales / customer_count if customer_count else 0},
        ]
    )


def _monthly_kpis(df: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        df.groupby("Order Month Date")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
            Active_Customers=("Customer ID", "nunique"),
        )
        .reset_index()
        .sort_values("Order Month Date")
    )

    first_purchase_month = df.groupby("Customer ID")["Order Month Date"].min()
    new_customers = first_purchase_month.value_counts().rename("New Customers")
    repeat_customers = (
        df.loc[df["Repeat Customer Flag"]]
        .groupby("Order Month Date")["Customer ID"]
        .nunique()
        .rename("Repeat Customers")
    )

    monthly = monthly.merge(new_customers, left_on="Order Month Date", right_index=True, how="left")
    monthly = monthly.merge(repeat_customers, left_on="Order Month Date", right_index=True, how="left")
    monthly[["New Customers", "Repeat Customers"]] = monthly[["New Customers", "Repeat Customers"]].fillna(0).astype(int)

    monthly["AOV"] = (monthly["Sales"] / monthly["Orders"].where(monthly["Orders"] != 0)).fillna(0).round(4)
    monthly["Profit Margin"] = (monthly["Profit"] / monthly["Sales"].where(monthly["Sales"] != 0)).fillna(0).round(4)

    customer_sets = df.groupby("Order Month Date")["Customer ID"].apply(set).sort_index()
    previous_sets = customer_sets.shift(1)
    churned_counts = []
    retained_counts = []
    for current, previous in zip(customer_sets, previous_sets):
        if not isinstance(previous, set):
            churned_counts.append(0)
            retained_counts.append(0)
            continue
        churned_counts.append(len(previous - current))
        retained_counts.append(len(previous & current))

    monthly["Churned Customers"] = churned_counts
    monthly["Retained Customers"] = retained_counts
    monthly["Previous Active Customers"] = monthly["Active_Customers"].shift(1).fillna(0)
    monthly["Churn Rate"] = monthly.apply(
        lambda row: row["Churned Customers"] / row["Previous Active Customers"]
        if row["Previous Active Customers"]
        else 0,
        axis=1,
    )
    monthly["Retention Rate"] = monthly.apply(
        lambda row: row["Retained Customers"] / row["Previous Active Customers"]
        if row["Previous Active Customers"]
        else 0,
        axis=1,
    )
    return monthly


def _category_performance(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["Category", "Sub-Category"])
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"), Quantity=("Quantity", "sum"))
        .assign(**{"Profit Margin": lambda x: (x["Profit"] / x["Sales"].where(x["Sales"] != 0)).fillna(0).round(4)})
        .reset_index()
        .sort_values("Sales", ascending=False)
    )


def _product_performance(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["Product ID", "Product Name", "Category", "Sub-Category"])
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"), Quantity=("Quantity", "sum"))
        .assign(**{"Profit Margin": lambda x: (x["Profit"] / x["Sales"].where(x["Sales"] != 0)).fillna(0).round(4)})
        .reset_index()
        .sort_values("Sales", ascending=False)
        .head(100)
    )


def _region_performance(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["Region", "State", "City"])
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"), Customers=("Customer ID", "nunique"))
        .assign(**{"Profit Margin": lambda x: (x["Profit"] / x["Sales"].where(x["Sales"] != 0)).fillna(0).round(4)})
        .reset_index()
        .sort_values("Sales", ascending=False)
    )


def _customer_segments(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(
            [
                "Segment",
                "Customer Status",
                "Customer Recency Segment",
                "Customer Frequency Segment",
                "Customer Value Segment",
            ]
        )
        .agg(Customers=("Customer ID", "nunique"), Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
        .assign(AOV=lambda x: (x["Sales"] / x["Orders"].where(x["Orders"] != 0)).fillna(0).round(4))
        .reset_index()
        .sort_values("Sales", ascending=False)
    )
