# Python Sales ETL

This project is a Python and PySpark ETL pipeline organized in Bronze, Silver, and Gold layers.

## Project_structure


```text
data_engineering_assignment/
├── data/sales.csv
├── output/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│       ├── sales/
│       └── customer/
├── src/
│   ├── bronze.py
│   ├── silver.py
│   ├── gold.py
│   ├── logger.py
│   └── main.py
├── tests/
├── requirements.txt
└── README.md
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

The repository includes a small input dataset for a smoke test:

```powershell
python src/main.py --input data/sales.csv --output output
```

Every layer is written as Parquet and partitioned by `order_year`, `order_month`, and `order_day`. Metadata columns are `file_path` and `execution_datetime`. Customer Gold is overwritten on each run; Sales Gold is append-oriented for incremental ingestion.

The reporting date defaults to `2018-12-30` and can be changed explicitly:

```powershell
python src/main.py --input path\to\input.csv --output output --latest-date 2018-12-30
```

## Tests

```powershell
python -m pytest
```

The tests cover customer order counts, Sales columns, and missing input paths.

## Important Windows note

Spark may need Hadoop's `winutils.exe` to write local Parquet files on Windows. If Spark reports that `HADOOP_HOME` is missing, configure Hadoop or run the project in WSL/Linux or a managed Spark environment. The transformation tests do not require local Parquet writing.

The transformation tests do not require local Parquet writing.

## CI/CD Implementation

A GitHub Actions workflow has been implemented for Continuous Integration.

Pipeline Steps:
1. Checkout source code
2. Setup Python environment
3. Install project dependencies
4. Run unit tests
5. Execute ETL pipeline

Benefits:
- Automated validation of code changes
- Early detection of failures
- Improved code quality
- Reproducible execution environment
