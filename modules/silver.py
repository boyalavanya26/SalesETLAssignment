"""Silver layer: clean the data and keep only valid orders."""

import pandas as pd


def parse_date(series):
    """Convert a pandas column to a real date type."""
    return pd.to_datetime(series, errors="coerce", format="mixed")


def normalize_string_series(series):
    """Trim whitespace, remove extra spacing, and convert empty values to missing."""
    if series is None:
        return series
    return series.map(lambda value: None if pd.isna(value) else str(value).strip()).str.replace(r"\s+", " ", regex=True)


def build_silver(data):
    """Silver layer cleans and standardizes Bronze data, then drops invalid records."""
    data = data.copy()

    for column in ["order_id", "ship_mode", "customer_id", "customer_name", "segment", "country_name", "city"]:
        if column in data.columns:
            data[column] = normalize_string_series(data[column])

    if "order_id" in data.columns:
        data["order_id"] = data["order_id"].str.upper().str.replace(r"\s+", "", regex=True)
    if "customer_id" in data.columns:
        data["customer_id"] = data["customer_id"].str.upper()
    if "customer_name" in data.columns:
        data["customer_name"] = data["customer_name"].str.title()
    if "segment" in data.columns:
        data["segment"] = data["segment"].str.title()
    if "country_name" in data.columns:
        data["country_name"] = data["country_name"].str.title()
    if "city" in data.columns:
        data["city"] = data["city"].str.title()
    if "ship_mode" in data.columns:
        data["ship_mode"] = data["ship_mode"].str.title()

    data["order_date"] = parse_date(data["order_date"])
    data["ship_date"] = parse_date(data["ship_date"])
    data["order_year"] = data["order_date"].dt.year
    data["order_month"] = data["order_date"].dt.month
    data["order_day"] = data["order_date"].dt.day

    valid_mask = (
        data["order_id"].notna()
        & data["order_date"].notna()
        & data["customer_id"].notna()
        & data["customer_name"].notna()
    )
    return data[valid_mask].reset_index(drop=True)
