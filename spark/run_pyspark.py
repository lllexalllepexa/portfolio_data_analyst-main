"""
Run Spark SQL aggregations locally (requires Java + pip install pyspark).

  python spark/run_pyspark.py
"""
from pathlib import Path

from pyspark.sql import SparkSession

ROOT = Path(__file__).resolve().parents[1]
PARQUET = ROOT / "data" / "processed" / "orders_clean.parquet"
SQL_FILE = Path(__file__).with_name("aggregations.sql")


def main() -> None:
    if not PARQUET.exists():
        raise SystemExit("Run ETL first: python -m superstore.etl.load_and_clean")

    spark = (
        SparkSession.builder.appName("superstore")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )
    spark.read.parquet(str(PARQUET)).createOrReplaceTempView("orders")

    sql = SQL_FILE.read_text(encoding="utf-8")
    # Execute statements separated by semicolons (skip comments-only blocks)
    for stmt in sql.split(";"):
        block = "\n".join(
            line for line in stmt.splitlines() if line.strip() and not line.strip().startswith("--")
        ).strip()
        if not block or block.upper().startswith("CREATE OR REPLACE TEMP VIEW"):
            if block:
                spark.sql(block)
            continue
        if "CREATE OR REPLACE TEMP VIEW" in stmt.upper():
            continue
        print(f"\n--- Query ---\n{block[:120]}...")
        spark.sql(block).show(20, truncate=False)

    spark.stop()


if __name__ == "__main__":
    main()
