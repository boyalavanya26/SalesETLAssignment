"""Gold layer: create business-ready tables for sales and customers."""

import pandas as pd


def build_sales(data):
    """Create the sales table with the final output columns."""
    sales = data[[
        "order_id",
        "order_date",
        "ship_date",
        "ship_mode",
        "city",
        "file_path",
        "execution_datetime",
        "order_year",
        "order_month",
        "order_day",
    ]].copy()
    sales = sales.rename(columns={"ship_date": "shipment_date", "ship_mode": "shipment_mode"})
    return sales


def build_customer(data, latest_date: str = "2018-12-30"):
    """Create one row per customer with order-count summary metrics."""
    report_date = pd.to_datetime(latest_date)
    customer_data = data.copy()
    customer_data["customer_id"] = customer_data["customer_id"].fillna("").astype(str).str.strip().str.upper()
    customer_data["customer_name"] = customer_data["customer_name"].fillna("").astype(str).str.strip().str.title()
    customer_data["customer_name_parts"] = customer_data["customer_name"].str.split()
    customer_data["customer_first_name"] = customer_data["customer_name_parts"].map(lambda value: value[0] if value else None)
    customer_data["customer_last_name"] = customer_data["customer_name_parts"].map(lambda value: value[-1] if value else None)

    grouped = customer_data.groupby(
        ["customer_id", "customer_first_name", "customer_last_name"],
        dropna=False,
        as_index=False,
    )

    summary = grouped.agg(
        customer_segment=("segment", lambda values: values.dropna().iloc[0] if values.notna().any() else None),
        country=("country_name", lambda values: values.dropna().iloc[0] if values.notna().any() else None),
        orders_all_time=("order_id", "nunique"),
        file_path=("file_path", lambda values: values.dropna().iloc[0] if values.notna().any() else None),
        execution_datetime=("execution_datetime", lambda values: values.dropna().iloc[0] if values.notna().any() else None),
    )

    for label, months in [("orders_last_month", -1), ("orders_last_6_months", -6), ("orders_last_12_months", -12)]:
        cutoff = report_date + pd.DateOffset(months=months)
        filtered = customer_data[customer_data["order_date"] >= cutoff]
        counts = filtered.groupby(["customer_id", "customer_first_name", "customer_last_name"], dropna=False)["order_id"].nunique().rename(label)
        summary = summary.merge(counts.reset_index(), on=["customer_id", "customer_first_name", "customer_last_name"], how="left")

    summary["orders_last_month"] = summary.get("orders_last_month", 0).fillna(0)
    summary["orders_last_6_months"] = summary.get("orders_last_6_months", 0).fillna(0)
    summary["orders_last_12_months"] = summary.get("orders_last_12_months", 0).fillna(0)
    summary["order_year"] = report_date.year
    summary["order_month"] = report_date.month
    summary["order_day"] = report_date.day
    return summary[[
        "customer_id",
        "customer_first_name",
        "customer_last_name",
        "customer_segment",
        "country",
        "orders_last_month",
        "orders_last_6_months",
        "orders_last_12_months",
        "orders_all_time",
        "file_path",
        "execution_datetime",
        "order_year",
        "order_month",
        "order_day",
    ]]
