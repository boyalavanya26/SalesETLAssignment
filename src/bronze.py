"""Bronze layer: read raw CSV and prepare clean source data."""

from pathlib import Path

import pandas as pd


def read_sales(spark=None, input_path=None):
    """Read the sales CSV and add metadata about the source file."""
    if input_path is None:
        if isinstance(spark, (str, Path)):
            input_path = spark
            spark = None
        else:
            raise TypeError("Please provide an input path.")
    elif isinstance(spark, (str, Path)) and input_path is not None:
        input_path, spark = spark, input_path

    input_path = Path(input_path)
    if not input_path.exists() or (input_path.is_dir() and not any(input_path.iterdir())):
        raise FileNotFoundError(f"Input path does not exist or is empty: {input_path}")

    data = pd.read_csv(input_path)
    data["file_path"] = str(input_path)
    data["execution_datetime"] = pd.Timestamp.now()
    return data


def normalize_column_name(column_name: str) -> str:
    """Make column names clean and easy to use."""
    return str(column_name).strip().lower().replace(" ", "_")


def build_bronze(data):
    """Clean column names and create order date partition fields."""
    data = data.copy()
    data.columns = [normalize_column_name(column_name) for column_name in data.columns]
    data["order_date"] = pd.to_datetime(data["order_date"], errors="coerce", format="mixed")
    data["order_year"] = data["order_date"].dt.year
    data["order_month"] = data["order_date"].dt.month
    data["order_day"] = data["order_date"].dt.day
    return data