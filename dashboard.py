"""Streamlit dashboard for the ecommerce analytics project."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_XLSX = PROJECT_ROOT / "data" / "processed" / "sales_powerbi_ready.xlsx"
PROCESSED_CSV = PROJECT_ROOT / "data" / "processed" / "sales_powerbi_ready.csv"
OUTPUT_XLSX = PROJECT_ROOT / "outputs" / "tables" / "sales_powerbi_ready.xlsx"
OUTPUT_CSV = PROJECT_ROOT / "outputs" / "tables" / "sales_powerbi_ready.csv"

BLUE = "#3b82f6"
GREEN = "#10b981"
RED = "#ef4444"
VIOLET = "#8b5cf6"
ORANGE = "#f59e0b"
INK = "#0f172a"
MUTED = "#64748b"
GRID = "#e8eef6"
CARD_BORDER = "#d7e0ea"
APP_BG = "#f3f6fa"


st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)


CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: "Inter", "Segoe UI", sans-serif;
    }

    .stApp {
        background: #f3f6fa;
        color: #0f172a;
    }

    .block-container {
        max-width: 1440px;
        padding-top: 0.8rem;
        padding-bottom: 2rem;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    div[data-testid="stToolbar"] {
        display: none;
    }

    .app-header {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        padding: 0.75rem 0.25rem 1rem;
        border-bottom: 1px solid #d7e0ea;
        margin: -0.2rem -2rem 1.1rem;
        padding-left: 2rem;
        background: #ffffff;
    }

    .brand-icon {
        width: 34px;
        height: 34px;
        border-radius: 9px;
        background: #2563eb;
        color: #ffffff;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 0.88rem;
    }

    .app-title {
        font-size: 1.35rem;
        line-height: 1.05;
        font-weight: 800;
        color: #0f172a;
        margin: 0;
    }

    .app-subtitle {
        font-size: 0.78rem;
        color: #334155;
        margin-top: 0.1rem;
    }

    div[data-testid="stTabs"] > div[role="tablist"] {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0;
        border: 1px solid #cfd9e5;
        border-radius: 9px;
        background: #ffffff;
        padding: 0;
        margin-bottom: 1.4rem;
    }

    div[data-testid="stTabs"] button[role="tab"] {
        justify-content: center;
        min-height: 32px;
        border-radius: 8px;
        color: #0f172a;
        font-weight: 700;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        background: #f8fafc;
        box-shadow: inset 0 0 0 1px #e2e8f0;
    }

    div[data-testid="stTabs"] button[role="tab"] p {
        font-size: 0.82rem;
        margin: 0;
    }

    div[data-testid="stTabs"] div[data-testid="stMarkdownContainer"] p {
        font-size: 0.82rem;
    }

    .kpi-card {
        background: #ffffff;
        border: 1px solid #d7e0ea;
        border-radius: 11px;
        min-height: 110px;
        padding: 1.15rem 1.25rem;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
        position: relative;
    }

    .kpi-label {
        font-size: 0.82rem;
        color: #0f2f56;
        margin-bottom: 1.65rem;
    }

    .kpi-value {
        font-size: 1.55rem;
        font-weight: 800;
        letter-spacing: 0;
        color: #020617;
        white-space: nowrap;
    }

    .kpi-hint {
        position: absolute;
        right: 1.2rem;
        top: 1rem;
        color: #86a0bf;
        font-size: 1rem;
        font-weight: 700;
    }

    .chart-card {
        background: #ffffff;
        border: 1px solid #d7e0ea;
        border-radius: 11px;
        padding: 1rem 1rem 0.55rem;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
        margin-bottom: 1.35rem;
    }

    .chart-title {
        color: #020617;
        font-size: 0.98rem;
        font-weight: 700;
        margin: 0 0 0.65rem;
    }

    .filters-box {
        background: #ffffff;
        border: 1px solid #d7e0ea;
        border-radius: 11px;
        padding: 0.85rem 1rem 0.4rem;
        margin-bottom: 1rem;
    }

    .stDataFrame {
        border: 1px solid #d7e0ea;
        border-radius: 10px;
        overflow: hidden;
    }

    @media (max-width: 900px) {
        .app-header {
            margin-left: -1rem;
            margin-right: -1rem;
            padding-left: 1rem;
        }
        div[data-testid="stTabs"] > div[role="tablist"] {
            grid-template-columns: repeat(2, 1fr);
        }
        .kpi-value {
            font-size: 1.25rem;
        }
    }
</style>
"""


@st.cache_data(show_spinner="Loading ecommerce analytics data...")
def load_data() -> pd.DataFrame:
    """Load the processed dataset from the latest available export."""
    if PROCESSED_XLSX.exists():
        df = pd.read_excel(PROCESSED_XLSX, sheet_name="Sales Data")
    elif OUTPUT_XLSX.exists():
        df = pd.read_excel(OUTPUT_XLSX, sheet_name="Sales Data")
    elif PROCESSED_CSV.exists():
        df = pd.read_csv(PROCESSED_CSV, encoding="utf-8-sig")
    elif OUTPUT_CSV.exists():
        df = pd.read_csv(OUTPUT_CSV, encoding="utf-8-sig")
    else:
        st.error("No processed dataset found. Run `python main.py` first.")
        st.stop()

    date_cols = [
        "Order Date",
        "Ship Date",
        "Order Month Date",
        "Customer First Order Date",
        "Customer Last Order Date",
    ]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    numeric_cols = [
        "Sales",
        "Profit",
        "Quantity",
        "Discount",
        "Profit Margin",
        "Days to Ship",
        "Customer Recency Days",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    bool_cols = ["Repeat Customer Flag", "New Customer Flag", "Active Customer Flag", "Is Profitable"]
    for col in bool_cols:
        if col in df.columns and df[col].dtype == object:
            df[col] = df[col].astype(str).str.lower().isin(["true", "1", "yes"])

    return df.dropna(subset=["Order Date", "Sales", "Profit"])


def format_money(value: float) -> str:
    return f"${value:,.0f}"


def format_compact_money(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.0f}k"
    return format_money(value)


def format_percent(value: float) -> str:
    return f"{value:.2%}"


def apply_theme() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_header() -> None:
    st.markdown(
        """
        <div class="app-header">
            <div class="brand-icon">BI</div>
            <div>
                <div class="app-title">E-Commerce Analytics</div>
                <div class="app-subtitle">Sales & Customer Intelligence Dashboard</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, hint: str = "") -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-hint">{hint}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chart_card(title: str, fig: go.Figure) -> None:
    with st.container(border=True):
        st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def style_figure(fig: go.Figure, height: int) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=18, r=18, t=8, b=18),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#334155", size=11),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.16,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
        ),
        hoverlabel=dict(bgcolor="#0f172a", font_color="#ffffff"),
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False, linecolor="#cbd5e1")
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, linecolor="#cbd5e1")
    return fig


def add_filters(df: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        st.title("Filters")
        min_date = df["Order Date"].min().date()
        max_date = df["Order Date"].max().date()
        selected_dates = st.date_input(
            "Order date",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        regions = _multiselect(st, df, "Region")
        categories = _multiselect(st, df, "Category")
        segments = _multiselect(st, df, "Segment")

    filtered = df.copy()
    if len(selected_dates) == 2:
        start_date = pd.to_datetime(selected_dates[0])
        end_date = pd.to_datetime(selected_dates[1])
        filtered = filtered[filtered["Order Date"].between(start_date, end_date)]
    filtered = filtered[filtered["Region"].isin(regions)] if regions else filtered.iloc[0:0]
    filtered = filtered[filtered["Category"].isin(categories)] if categories else filtered.iloc[0:0]
    filtered = filtered[filtered["Segment"].isin(segments)] if segments else filtered.iloc[0:0]
    return filtered


def _multiselect(column, df: pd.DataFrame, name: str) -> list[str]:
    values = sorted(df[name].dropna().astype(str).unique())
    return column.multiselect(name, values, default=values)


def monthly_metrics(df: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        df.groupby(pd.Grouper(key="Order Date", freq="MS"))
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
            Active_Customers=("Customer ID", "nunique"),
        )
        .reset_index()
        .rename(columns={"Order Date": "Month"})
        .sort_values("Month")
    )

    first_month = df.groupby("Customer ID")["Order Date"].min().dt.to_period("M").dt.to_timestamp()
    new_customers = first_month.value_counts().rename("New Customers")
    monthly = monthly.merge(new_customers, left_on="Month", right_index=True, how="left")
    monthly["New Customers"] = monthly["New Customers"].fillna(0).astype(int)

    customer_sets = df.groupby(pd.Grouper(key="Order Date", freq="MS"))["Customer ID"].apply(set).sort_index()
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
    monthly["Churn Rate"] = (
        monthly["Churned Customers"] / monthly["Previous Active Customers"].where(monthly["Previous Active Customers"] != 0)
    ).fillna(0)
    monthly["Retention Rate"] = (
        monthly["Retained Customers"] / monthly["Previous Active Customers"].where(monthly["Previous Active Customers"] != 0)
    ).fillna(0)
    return monthly


def render_executive(df: pd.DataFrame) -> None:
    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    orders = df["Order ID"].nunique()
    customers = df["Customer ID"].nunique()
    aov = total_sales / orders if orders else 0
    profit_margin = total_profit / total_sales if total_sales else 0
    clv = total_sales / customers if customers else 0
    monthly = monthly_metrics(df)

    row1 = st.columns(4)
    with row1[0]:
        kpi_card("Total Sales", format_money(total_sales), "$")
    with row1[1]:
        kpi_card("Total Profit", format_money(total_profit), "^")
    with row1[2]:
        kpi_card("Total Orders", f"{orders:,}", "cart")
    with row1[3]:
        kpi_card("Total Customers", f"{customers:,}", "users")

    row2 = st.columns(3)
    with row2[0]:
        kpi_card("Average Order Value", format_money(aov))
    with row2[1]:
        kpi_card("Profit Margin", format_percent(profit_margin))
    with row2[2]:
        kpi_card("Customer Lifetime Value", format_money(clv))

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=monthly["Month"],
            y=monthly["Sales"],
            mode="lines+markers",
            name="sales",
            line=dict(color=BLUE, width=3),
            marker=dict(size=6),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=monthly["Month"],
            y=monthly["Profit"],
            mode="lines+markers",
            name="profit",
            line=dict(color=GREEN, width=3),
            marker=dict(size=6),
        )
    )
    chart_card("Sales & Profit Trend", style_figure(fig, 350))

    left, right = st.columns(2)
    with left:
        fig = px.bar(monthly, x="Month", y="Orders", color_discrete_sequence=[VIOLET])
        fig.update_traces(marker_line_width=0, width=0.62)
        chart_card("Orders Trend", style_figure(fig, 265))
    with right:
        category = df.groupby("Category", as_index=False).agg(Sales=("Sales", "sum"))
        fig = px.pie(
            category,
            names="Category",
            values="Sales",
            color_discrete_sequence=[BLUE, GREEN, ORANGE, VIOLET, RED],
        )
        fig.update_traces(textinfo="label+value", texttemplate="%{label}: $%{value:,.0s}", hole=0)
        fig.update_layout(showlegend=False)
        chart_card("Top Categories by Sales", style_figure(fig, 265))


def render_customers(df: pd.DataFrame) -> None:
    monthly = monthly_metrics(df)
    latest = monthly.iloc[-1] if not monthly.empty else pd.Series(dtype=float)
    active = int(latest.get("Active_Customers", 0))
    new = int(latest.get("New Customers", 0))
    churn = float(latest.get("Churn Rate", 0))

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Active Customers (Latest)", f"{active:,}", "users")
    with c2:
        kpi_card("New Customers (Latest)", f"{new:,}", "users")
    with c3:
        kpi_card("Churn Rate (Latest)", format_percent(churn), "down")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=monthly["Month"],
            y=monthly["Active_Customers"],
            name="Active Customers",
            mode="lines",
            fill="tozeroy",
            line=dict(color=BLUE, width=2),
            fillcolor="rgba(59, 130, 246, 0.22)",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=monthly["Month"],
            y=monthly["New Customers"],
            name="New Customers",
            mode="lines",
            fill="tozeroy",
            line=dict(color=GREEN, width=2),
            fillcolor="rgba(16, 185, 129, 0.22)",
        )
    )
    chart_card("Customer Metrics Over Time", style_figure(fig, 345))

    left, right = st.columns(2)
    with left:
        fig = px.line(monthly, x="Month", y="Churn Rate", markers=True, color_discrete_sequence=[RED])
        fig.update_yaxes(tickformat=".0%")
        chart_card("Churn Rate Trend", style_figure(fig, 260))
    with right:
        fig = px.bar(monthly, x="Month", y="Retention Rate", color_discrete_sequence=[GREEN])
        fig.update_yaxes(tickformat=".0%")
        fig.update_traces(width=0.7)
        chart_card("Retention Rate Trend", style_figure(fig, 260))

    fig = go.Figure()
    fig.add_trace(go.Bar(x=monthly["Month"], y=monthly["Churned Customers"], name="Churned", marker_color=RED))
    fig.add_trace(go.Bar(x=monthly["Month"], y=monthly["Retained Customers"], name="Retained", marker_color=GREEN))
    chart_card("Churned vs Retained Customers", style_figure(fig, 300))


def render_products(df: pd.DataFrame) -> None:
    product = (
        df.groupby(["Product Name", "Category"], as_index=False)
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
        .assign(Margin=lambda x: (x["Profit"] / x["Sales"].where(x["Sales"] != 0)).fillna(0))
        .sort_values("Sales", ascending=False)
    )
    top_products = product.head(10).sort_values("Sales")

    fig = px.bar(
        top_products,
        x="Sales",
        y="Product Name",
        orientation="h",
        color_discrete_sequence=[BLUE],
    )
    fig.update_traces(width=0.58)
    chart_card("Top 10 Products by Sales", style_figure(fig, 310))

    subcategory = (
        df.groupby(["Category", "Sub-Category"], as_index=False)
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .sort_values("Sales", ascending=False)
        .head(15)
    )
    fig = go.Figure()
    fig.add_trace(go.Bar(x=subcategory["Sub-Category"], y=subcategory["Sales"], name="Sales", marker_color=BLUE))
    fig.add_trace(go.Bar(x=subcategory["Sub-Category"], y=subcategory["Profit"], name="Profit", marker_color=GREEN))
    fig.update_layout(barmode="group")
    chart_card("Category Performance", style_figure(fig, 300))

    fig = px.scatter(
        product.head(100),
        x="Sales",
        y="Margin",
        color_discrete_sequence=[VIOLET],
        hover_data=["Product Name", "Category", "Profit"],
    )
    fig.update_yaxes(tickformat=".0%")
    chart_card("Sales vs Profit Margin Analysis", style_figure(fig, 285))

    table = product.sort_values("Profit", ascending=False).head(10).copy()
    table["Sales"] = table["Sales"].map(format_money)
    table["Profit"] = table["Profit"].map(format_money)
    table["Margin"] = table["Margin"].map(format_percent)
    with st.container(border=True):
        st.markdown('<div class="chart-title">Top 10 Most Profitable Products</div>', unsafe_allow_html=True)
        st.dataframe(
            table[["Product Name", "Sales", "Profit", "Margin"]],
            use_container_width=True,
            hide_index=True,
        )


def render_segments(df: pd.DataFrame) -> None:
    total_customers = df["Customer ID"].nunique()
    active_customers = df.loc[df["Customer Status"].eq("Active"), "Customer ID"].nunique()
    high_value_customers = df.loc[df["Customer Value Segment"].eq("High Value"), "Customer ID"].nunique()
    avg_recency = df.drop_duplicates("Customer ID")["Customer Recency Days"].mean()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Total Customers", f"{total_customers:,}", "users")
    with c2:
        kpi_card("Active Customers", f"{active_customers:,}", "active")
    with c3:
        kpi_card("High Value Customers", f"{high_value_customers:,}", "value")
    with c4:
        kpi_card("Avg Recency Days", f"{avg_recency:,.0f}", "days")

    customer_level = (
        df.groupby(
            [
                "Customer ID",
                "Customer Name",
                "Segment",
                "Customer Status",
                "Customer Recency Segment",
                "Customer Frequency Segment",
                "Customer Value Segment",
                "Customer Segment Label",
            ],
            as_index=False,
        )
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"), Recency=("Customer Recency Days", "min"))
    )

    left, right = st.columns(2)
    with left:
        segment_sales = (
            customer_level.groupby("Customer Segment Label", as_index=False)
            .agg(Customers=("Customer ID", "nunique"), Sales=("Sales", "sum"))
            .sort_values("Sales", ascending=True)
            .tail(12)
        )
        fig = px.bar(
            segment_sales,
            x="Sales",
            y="Customer Segment Label",
            orientation="h",
            color="Customers",
            color_continuous_scale=[GREEN, BLUE],
        )
        fig.update_layout(coloraxis_showscale=False)
        chart_card("RFM Segment Sales", style_figure(fig, 330))
    with right:
        status = customer_level.groupby(["Segment", "Customer Status"], as_index=False).agg(Customers=("Customer ID", "nunique"))
        fig = px.bar(
            status,
            x="Segment",
            y="Customers",
            color="Customer Status",
            barmode="group",
            color_discrete_map={"Active": GREEN, "Inactive": RED},
        )
        chart_card("Customer Status by Segment", style_figure(fig, 330))

    left, right = st.columns(2)
    with left:
        region = df.groupby("Region", as_index=False).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Customers=("Customer ID", "nunique"))
        fig = px.scatter(
            region,
            x="Sales",
            y="Profit",
            size="Customers",
            color="Region",
            color_discrete_sequence=[BLUE, GREEN, ORANGE, VIOLET, RED],
            text="Region",
        )
        fig.update_traces(textposition="top center")
        chart_card("Region Sales vs Profit", style_figure(fig, 300))
    with right:
        discount = df.groupby("Discount Band", as_index=False).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        fig = go.Figure()
        fig.add_trace(go.Bar(x=discount["Discount Band"], y=discount["Sales"], name="Sales", marker_color=BLUE))
        fig.add_trace(go.Bar(x=discount["Discount Band"], y=discount["Profit"], name="Profit", marker_color=GREEN))
        fig.update_layout(barmode="group")
        chart_card("Discount Band Performance", style_figure(fig, 300))


def main() -> None:
    apply_theme()
    render_header()
    df = load_data()
    filtered = add_filters(df)

    if filtered.empty:
        st.warning("No rows match the selected filters.")
        return

    executive_tab, customers_tab, products_tab, segments_tab = st.tabs(
        ["Executive", "Customers", "Products", "Segments"]
    )
    with executive_tab:
        render_executive(filtered)
    with customers_tab:
        render_customers(filtered)
    with products_tab:
        render_products(filtered)
    with segments_tab:
        render_segments(filtered)


if __name__ == "__main__":
    main()