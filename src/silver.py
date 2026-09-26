"""Silver layer: clean the data and keep only valid orders."""

import pandas as pd


def parse_date(series):
    """Convert a pandas column to a real date type."""
    return pd.to_datetime(series, errors="coerce", format="mixed")


def build_silver(data):
    """Fix dates and text values, then remove rows without required order fields."""
    data = data.copy()
    data["order_date"] = parse_date(data["order_date"])
    data["ship_date"] = parse_date(data["ship_date"])
    data["customer_id"] = data["customer_id"].astype(str).str.strip()
    data["customer_name"] = data["customer_name"].astype(str).str.strip()
    data["order_year"] = data["order_date"].dt.year
    data["order_month"] = data["order_date"].dt.month
    data["order_day"] = data["order_date"].dt.day

    valid_mask = data["order_id"].notna() & data["order_date"].notna()
    return data[valid_mask].reset_index(drop=True)