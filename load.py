"""Data ingestion utilities with encoding fallbacks."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import EXTERNAL_RAW_DATA_PATH, RAW_DATA_PATH, REQUIRED_COLUMNS


def resolve_raw_path(raw_path: Path | None = None) -> Path:
    """Return the first available raw CSV path."""
    candidates = [raw_path, RAW_DATA_PATH, EXTERNAL_RAW_DATA_PATH]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return Path(candidate)
    raise FileNotFoundError(
        "Could not find sales_raw.csv. Place it in data/raw/ or update config.py."
    )


def load_sales_data(raw_path: Path | None = None) -> pd.DataFrame:
    """Load the sales CSV using common encodings and validate the raw schema."""
    path = resolve_raw_path(raw_path)
    encodings = ("utf-8-sig", "utf-8", "cp1252", "latin1")
    last_error: Exception | None = None

    for encoding in encodings:
        try:
            df = pd.read_csv(path, encoding=encoding)
            df.columns = df.columns.str.strip()
            _validate_raw_columns(df)
            return df
        except UnicodeDecodeError as exc:
            last_error = exc

    raise UnicodeDecodeError(
        "unknown", b"", 0, 1, f"Unable to decode {path}: {last_error}"
    )


def _validate_raw_columns(df: pd.DataFrame) -> None:
    missing = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(f"Raw dataset is missing required columns: {missing}")
