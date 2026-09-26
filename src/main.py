"""Main entry point for the sales ETL pipeline."""

import argparse
from pathlib import Path

from bronze import build_bronze, read_sales
from gold import build_customer, build_sales
from logger import configure_logging, get_logger
from silver import build_silver


def write_output(data, output_folder: Path, file_name: str) -> None:
    """Save a pandas DataFrame as a CSV file in the output folder."""
    output_folder.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_folder / file_name, index=False)


def run_pipeline(input_path: Path, output_path: Path, latest_date: str = "2018-12-30") -> None:
    """Run the full ETL flow: Bronze -> Silver -> Gold."""
    logger = get_logger()

    logger.info("Reading source file: %s", input_path)
    bronze_data = build_bronze(read_sales(input_path=input_path))
    write_output(bronze_data, output_path / "bronze", "bronze.csv")

    silver_data = build_silver(bronze_data)
    write_output(silver_data, output_path / "silver", "silver.csv")

    sales_gold = build_sales(silver_data)
    customer_gold = build_customer(silver_data, latest_date)

    write_output(sales_gold, output_path / "gold" / "sales", "sales.csv")
    write_output(customer_gold, output_path / "gold" / "customer", "customer.csv")

    logger.info("ETL finished successfully. Output saved in %s", output_path)


def main() -> None:
    """Read command-line arguments and start the pipeline."""
    parser = argparse.ArgumentParser(description="Run the Bronze, Silver, and Gold sales ETL pipeline.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--latest-date", default="2018-12-30")
    args = parser.parse_args()

    configure_logging()
    run_pipeline(args.input, args.output, args.latest_date)


if __name__ == "__main__":
    main()