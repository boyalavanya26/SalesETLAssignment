from pathlib import Path

import pandas as pd
import pytest

from modules.bronze import read_sales
from modules.gold import build_customer, build_sales
from modules.silver import build_silver


@pytest.fixture
def sample_data():
    return pd.DataFrame(
        [
            ("o1", "2018-12-30", "2019-01-02", "Standard", "c1", "Ada Lovelace", "Consumer", "UK", "London", "f", "t"),
            ("o2", "2018-11-30", "2018-12-02", "First", "c1", "Ada Lovelace", "Consumer", "UK", "London", "f", "t"),
            ("o3", "2018-01-01", "2018-01-03", "Standard", "c1", "Ada Lovelace", "Consumer", "UK", "London", "f", "t"),
        ],
        columns=[
            "order_id", "order_date", "ship_date", "ship_mode", "customer_id", "customer_name",
            "segment", "country_name", "city", "file_path", "execution_datetime",
        ],
    )


def test_customer_metrics_and_name_split(sample_data):
    result = build_customer(build_silver(sample_data), "2018-12-30").iloc[0].to_dict()
    assert result["customer_first_name"] == "Ada"
    assert result["customer_last_name"] == "Lovelace"
    assert result["orders_last_month"] == 2
    assert result["orders_last_6_months"] == 2
    assert result["orders_last_12_months"] == 3
    assert result["orders_all_time"] == 3


def test_sales_contract(sample_data):
    assert build_sales(build_silver(sample_data)).columns.tolist() == [
        "order_id", "order_date", "shipment_date", "shipment_mode", "city",
        "file_path", "execution_datetime", "order_year", "order_month", "order_day",
    ]


def test_dirty_sales_data_is_normalized_in_silver():
    dirty_data = pd.DataFrame(
        [
            (" CA-101 ", " 2020-01-05 ", " 2020-01-08 ", " standard ", " c-001 ", "  ada lovelace  ", " consumer ", " united states ", " new york ", "raw.csv", pd.Timestamp("2020-01-09")),
            (" CA-102 ", " not-a-date ", " 2020-01-12 ", " first ", " c-002 ", "  grace hopper  ", " corporate ", " united states ", " chicago ", "raw.csv", pd.Timestamp("2020-01-09")),
            (" CA-103 ", " 2020-02-01 ", " 2020-02-04 ", "second", " c-001 ", "ADA LOVELACE", "consumer", "United States", "New York", "raw.csv", pd.Timestamp("2020-01-09")),
        ],
        columns=[
            "order_id", "order_date", "ship_date", "ship_mode", "customer_id", "customer_name",
            "segment", "country_name", "city", "file_path", "execution_datetime",
        ],
    )

    result = build_silver(dirty_data)

    assert list(result["order_id"]) == ["CA-101", "CA-103"]
    assert list(result["customer_id"]) == ["C-001", "C-001"]
    assert list(result["customer_name"]) == ["Ada Lovelace", "Ada Lovelace"]
    assert list(result["segment"]) == ["Consumer", "Consumer"]
    assert list(result["country_name"]) == ["United States", "United States"]
    assert list(result["city"]) == ["New York", "New York"]


def test_missing_input_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        read_sales(input_path=tmp_path / "missing.csv")