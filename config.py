"""Central configuration for the ecommerce ETL pipeline."""
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
TABLES_DIR = OUTPUT_DIR / "tables"

RAW_FILE_NAME = "sales_raw.csv"
RAW_DATA_PATH = RAW_DIR / RAW_FILE_NAME
EXTERNAL_RAW_DATA_PATH = Path(r"d:\NTI - Zagazig\Project a\ecommerce-analysis\data\raw\sales_raw.csv")

PROCESSED_XLSX_PATH = PROCESSED_DIR / "sales_powerbi_ready.xlsx"
EXCEL_OUTPUT_PATH = TABLES_DIR / "sales_powerbi_ready.xlsx"
FINAL_CSV_OUTPUT_PATH = TABLES_DIR / "sales_powerbi_ready.csv"

DATE_COLUMNS = ["Order Date", "Ship Date"]
ID_COLUMNS = ["Row ID", "Order ID", "Customer ID", "Product ID"]
CURRENCY_COLUMNS = ["Sales", "Profit"]
INTEGER_COLUMNS = ["Row ID", "Quantity"]
PERCENT_COLUMNS = ["Discount", "Profit Margin"]
TEXT_COLUMNS = [
    "Order ID",
    "Ship Mode",
    "Customer ID",
    "Customer Name",
    "Segment",
    "Country/Region",
    "City",
    "State",
    "Postal Code",
    "Region",
    "Product ID",
    "Category",
    "Sub-Category",
    "Product Name",
]

REQUIRED_COLUMNS = [
    "Row ID",
    "Order ID",
    "Order Date",
    "Ship Date",
    "Ship Mode",
    "Customer ID",
    "Customer Name",
    "Segment",
    "Country/Region",
    "City",
    "State",
    "Postal Code",
    "Region",
    "Product ID",
    "Category",
    "Sub-Category",
    "Product Name",
    "Sales",
    "Quantity",
    "Discount",
    "Profit",
]

DUMMY_VALUES = {
    "",
    "-",
    "--",
    "n/a",
    "na",
    "none",
    "null",
    "unknown",
    "test",
    "dummy",
    "sample",
    "asasa",
    "asas",
    "asa",
    "sas",
}

CRITICAL_TEXT_COLUMNS = [
    "Order ID",
    "Ship Mode",
    "Customer ID",
    "Customer Name",
    "Segment",
    "Country/Region",
    "City",
    "State",
    "Region",
    "Product ID",
    "Category",
    "Sub-Category",
    "Product Name",
]

ACTIVE_CUSTOMER_WINDOW_DAYS = 90
CURRENT_PERIOD_FREQ = "M"
