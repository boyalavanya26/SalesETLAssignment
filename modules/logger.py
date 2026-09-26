"""Simple logging setup for the ETL project."""

import logging


def configure_logging() -> None:
    """Set up a basic logger for the pipeline."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s - %(message)s")


def get_logger(name: str = "sales_etl") -> logging.Logger:
    """Return the logger used by the ETL scripts."""
    return logging.getLogger(name)
