"""Simple logging setup for the ETL project."""

import logging
from pathlib import Path


def configure_logging() -> None:
    """Set up a basic logger for the pipeline and write to a file."""
    log_dir = Path(__file__).resolve().parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "etl.log"),
            logging.StreamHandler(),
        ],
    )


def get_logger(name: str = "sales_etl") -> logging.Logger:
    """Return the logger used by the ETL scripts."""
    return logging.getLogger(name)
