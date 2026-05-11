"""Orchestrates the ecommerce ETL pipeline."""
from __future__ import annotations

from src.clean import clean_sales_data
from src.export import export_powerbi_ready_dataset
from src.kpis import calculate_kpis
from src.load import load_sales_data
from src.transform import transform_sales_data
from src.validate import validate_powerbi_dataset


def run_pipeline() -> None:
    raw_df = load_sales_data()
    cleaned_df = clean_sales_data(raw_df)
    transformed_df = transform_sales_data(cleaned_df)
    validate_powerbi_dataset(transformed_df)
    kpi_tables = calculate_kpis(transformed_df)
    export_powerbi_ready_dataset(transformed_df, kpi_tables)

    print("ETL pipeline completed successfully.")
    print(f"Rows exported: {len(transformed_df):,}")
    print(f"Orders exported: {transformed_df['Order ID'].nunique():,}")
    print(f"Customers exported: {transformed_df['Customer ID'].nunique():,}")


if __name__ == "__main__":
    run_pipeline()
