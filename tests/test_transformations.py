from pathlib import Path

import pandas as pd
import pytest

from bronze import read_sales
from gold import build_customer, build_sales
from silver import build_silver


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


def test_missing_input_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        read_sales(input_path=tmp_path / "missing.csv")