"""Exports final data and KPI tables with Power BI-friendly formatting."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .config import EXCEL_OUTPUT_PATH, FINAL_CSV_OUTPUT_PATH, PROCESSED_XLSX_PATH, TABLES_DIR


CURRENCY_COLUMNS = {
    "Sales",
    "Profit",
    "AOV",
    "Average Order Value",
    "Customer Lifetime Value",
    "Total Sales",
    "Total Profit",
    "Value",
}
PERCENT_COLUMNS = {"Discount", "Profit Margin", "Churn Rate", "Retention Rate"}
INTEGER_COLUMNS = {
    "Row ID",
    "Quantity",
    "Orders",
    "Customers",
    "Total Orders",
    "Total Customers",
    "Active_Customers",
    "Previous Active Customers",
    "New Customers",
    "Repeat Customers",
    "Churned Customers",
    "Retained Customers",
    "Customer Recency Days",
}


def export_powerbi_ready_dataset(df: pd.DataFrame, kpi_tables: dict[str, pd.DataFrame]) -> None:
    """Write final CSV and fully formatted xlsxwriter Excel workbooks."""
    _ensure_output_dirs()
    export_df = _prepare_for_export(df)

    export_df.to_csv(FINAL_CSV_OUTPUT_PATH, index=False, encoding="utf-8-sig", date_format="%Y-%m-%d")
    _write_excel_workbook(EXCEL_OUTPUT_PATH, export_df, kpi_tables)
    _write_excel_workbook(PROCESSED_XLSX_PATH, export_df, kpi_tables)


def _write_excel_workbook(
    output_path: Path,
    export_df: pd.DataFrame,
    kpi_tables: dict[str, pd.DataFrame],
) -> None:
    try:
        with pd.ExcelWriter(
            output_path,
            engine="xlsxwriter",
            date_format="yyyy-mm-dd",
            datetime_format="yyyy-mm-dd",
        ) as writer:
            export_df.to_excel(writer, sheet_name="Sales Data", index=False)
            _format_xlsxwriter_sheet(writer, "Sales Data", export_df)

            for sheet_name, table_df in kpi_tables.items():
                safe_name = sheet_name[:31]
                export_table = _prepare_for_export(table_df)
                export_table.to_excel(writer, sheet_name=safe_name, index=False)
                _format_xlsxwriter_sheet(writer, safe_name, export_table)
    except PermissionError as exc:
        raise PermissionError(
            f"Could not write {output_path}. Close the workbook in Excel/Power BI and run the pipeline again."
        ) from exc


def _ensure_output_dirs() -> None:
    for path in [PROCESSED_XLSX_PATH.parent, TABLES_DIR, EXCEL_OUTPUT_PATH.parent]:
        Path(path).mkdir(parents=True, exist_ok=True)


def _prepare_for_export(df: pd.DataFrame) -> pd.DataFrame:
    export_df = df.copy()
    date_cols = export_df.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns
    for col in date_cols:
        export_df[col] = pd.to_datetime(export_df[col]).dt.date
    return export_df


def _format_xlsxwriter_sheet(
    writer: pd.ExcelWriter,
    sheet_name: str,
    df: pd.DataFrame,
) -> None:
    """Apply table styling, freeze panes, filters, data formats, and content auto-fit."""
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]

    header_format = workbook.add_format(
        {
            "bold": True,
            "font_color": "white",
            "bg_color": "#1F4E78",
            "border": 1,
            "align": "center",
            "valign": "vcenter",
        }
    )
    currency_format = workbook.add_format({"num_format": "#,##0.00", "valign": "top"})
    percent_format = workbook.add_format({"num_format": "0.00%", "valign": "top"})
    integer_format = workbook.add_format({"num_format": "0", "valign": "top"})
    date_format = workbook.add_format({"num_format": "yyyy-mm-dd", "valign": "top"})
    text_format = workbook.add_format({"valign": "top"})

    worksheet.freeze_panes(1, 0)
    worksheet.set_row(0, 22, header_format)

    if not df.empty and len(df.columns) > 0:
        worksheet.add_table(
            0,
            0,
            len(df),
            len(df.columns) - 1,
            {
                "name": _excel_table_name(sheet_name),
                "style": "Table Style Medium 2",
                "columns": [{"header": str(column)} for column in df.columns],
            },
        )
    elif len(df.columns) > 0:
        worksheet.autofilter(0, 0, 0, len(df.columns) - 1)

    for col_idx, column_name in enumerate(df.columns):
        column_format = _get_column_format(column_name, date_format, currency_format, percent_format, integer_format, text_format)
        width = _calculate_autofit_width(df[column_name], column_name)
        worksheet.set_column(col_idx, col_idx, width, column_format)


def _get_column_format(
    column_name: str,
    date_format: Any,
    currency_format: Any,
    percent_format: Any,
    integer_format: Any,
    text_format: Any,
) -> Any:
    if "Date" in column_name or column_name == "Order Month Date":
        return date_format
    if column_name in PERCENT_COLUMNS:
        return percent_format
    if column_name in CURRENCY_COLUMNS:
        return currency_format
    if column_name in INTEGER_COLUMNS or column_name.endswith("Count"):
        return integer_format
    return text_format


def _calculate_autofit_width(series: pd.Series, column_name: str) -> float:
    """Estimate Excel column width from header and visible cell content."""
    header_length = len(str(column_name))
    if series.empty:
        return min(max(header_length + 2, 12), 60)

    content_lengths = series.map(_display_length)
    max_content_length = int(content_lengths.max()) if not content_lengths.empty else 0

    # A small padding keeps filtered table headers and numbers from feeling cramped.
    width = max(header_length, max_content_length) + 2
    return min(max(width, 12), 60)


def _display_length(value: object) -> int:
    if pd.isna(value):
        return 0
    if hasattr(value, "strftime"):
        return len(value.strftime("%Y-%m-%d"))
    if isinstance(value, float):
        return len(f"{value:,.2f}")
    return len(str(value))


def _excel_table_name(sheet_name: str) -> str:
    safe_name = "".join(ch for ch in sheet_name.title() if ch.isalnum())
    return f"tbl_{safe_name[:20] or 'Sheet'}"
