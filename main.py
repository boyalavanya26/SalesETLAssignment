"""Main entry point for the sales ETL pipeline."""

import argparse
from pathlib import Path

from modules.bronze import build_bronze, read_sales
from modules.gold import build_customer, build_sales
from modules.logger import configure_logging, get_logger
from modules.silver import build_silver


def write_output(data, output_folder: Path, file_name: str) -> None:
    """Save a pandas DataFrame as a Parquet file in the output folder."""
    output_folder.mkdir(parents=True, exist_ok=True)
    parquet_name = file_name.replace(".csv", ".parquet")
    data.to_parquet(output_folder / parquet_name, index=False)


def run_pipeline(input_path: Path, output_path: Path, latest_date: str = "2018-12-30") -> None:
    """Run the full ETL flow: Bronze -> Silver -> Gold."""
    logger = get_logger()

    try:
        logger.info("[ETL START] Reading source file: %s", input_path)

        logger.info("[BRONZE] Starting Bronze ingestion from source data")
        bronze_data = build_bronze(read_sales(input_path=input_path))
        logger.info("[BRONZE] Bronze layer finished with %s rows", len(bronze_data))
        write_output(bronze_data, output_path / "bronze", "bronze.csv")
        logger.info("[BRONZE] Bronze output written to %s", output_path / "bronze")

        logger.info("[SILVER] Starting data cleaning and validation")
        silver_data = build_silver(bronze_data)
        logger.info("[SILVER] Silver layer finished with %s rows", len(silver_data))
        write_output(silver_data, output_path / "silver", "silver.csv")
        logger.info("[SILVER] Silver output written to %s", output_path / "silver")

        logger.info("[GOLD] Starting sales aggregation")
        sales_gold = build_sales(silver_data)
        logger.info("[GOLD] Sales aggregation finished with %s rows", len(sales_gold))
        write_output(sales_gold, output_path / "gold" / "sales", "sales.csv")
        logger.info("[GOLD] Sales gold output written to %s", output_path / "gold" / "sales")

        logger.info("[GOLD] Starting customer aggregation")
        customer_gold = build_customer(silver_data, latest_date)
        logger.info("[GOLD] Customer aggregation finished with %s rows", len(customer_gold))
        write_output(customer_gold, output_path / "gold" / "customer", "customer.csv")
        logger.info("[GOLD] Customer gold output written to %s", output_path / "gold" / "customer")

        logger.info("[ETL END] Pipeline completed successfully. Output saved in %s", output_path)
    except Exception:
        logger.exception("[ETL ERROR] Pipeline failed at a stage. Check the stack trace above.")
        raise


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
