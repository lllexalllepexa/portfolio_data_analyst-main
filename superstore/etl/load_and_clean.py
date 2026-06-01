"""
ETL: CSV -> cleaned Parquet + DuckDB + optional PostgreSQL.
Run: python -m superstore.etl.load_and_clean
"""
from __future__ import annotations

import argparse
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "global_superstore.csv"
OUT_PARQUET = ROOT / "data" / "processed" / "orders_clean.parquet"
DUCKDB_PATH = ROOT / "data" / "processed" / "superstore.duckdb"

RENAME = {
    "Customer ID": "customer_id",
    "Customer Name": "customer_name",
    "Order Date": "order_date",
    "Order ID": "order_id",
    "Order Priority": "order_priority",
    "Product ID": "product_id",
    "Product Name": "product_name",
    "Row ID": "row_id",
    "Ship Date": "ship_date",
    "Ship Mode": "ship_mode",
    "Shipping Cost": "shipping_cost",
    "Sub-Category": "sub_category",
    "ji_lu-shu": "record_count",
    "Market2": "market_group",
}


def resolve_raw() -> Path:
    if RAW.exists():
        return RAW
    raise FileNotFoundError(f"Положите CSV сюда: {RAW}")


def repair_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    В этом CSV даты часто битые (Excel: '00:00.0').
    Восстанавливаем order_date из year + weeknum и order_id (CA-2011-…).
    """
    year = pd.to_numeric(df.get("year"), errors="coerce")
    from_id = df["order_id"].str.extract(r"-(\d{4})-", expand=False)
    year = year.fillna(pd.to_numeric(from_id, errors="coerce"))

    week = pd.to_numeric(df.get("weeknum"), errors="coerce").fillna(26).clip(1, 52)
    order_date = pd.to_datetime(year.astype("Int64").astype(str) + "-01-01", errors="coerce")
    order_date = order_date + pd.to_timedelta((week - 1) * 7, unit="D")

    ship_lag = {
        "same day": 0,
        "first class": 1,
        "second class": 3,
        "standard class": 5,
    }
    mode = df.get("ship_mode", pd.Series("", index=df.index)).astype(str).str.lower()
    lag = mode.map(ship_lag).fillna(3).astype(int)

    df["order_date"] = order_date
    df["ship_date"] = order_date + pd.to_timedelta(lag, unit="D")
    df["delivery_days"] = lag
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=RENAME)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    numeric = ["sales", "profit", "quantity", "discount", "shipping_cost", "year", "weeknum"]
    for col in numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = repair_dates(df)
    df = df.dropna(subset=["order_id", "sales"])
    df = df[df["sales"] > 0]
    df["profit_margin"] = df["profit"] / df["sales"]
    return df


def load_duckdb(df: pd.DataFrame, db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    try:
        con.execute("CREATE OR REPLACE TABLE orders AS SELECT * FROM df")
        con.execute(
            """
            CREATE OR REPLACE VIEW mart_region_year AS
            SELECT
                region,
                country,
                CAST(year AS INTEGER) AS year,
                COUNT(*) AS order_lines,
                SUM(sales) AS revenue,
                SUM(profit) AS profit,
                AVG(profit_margin) AS avg_margin
            FROM orders
            GROUP BY 1, 2, 3
            """
        )
    finally:
        con.close()


def load_postgres(df: pd.DataFrame, url: str) -> None:
    from sqlalchemy import create_engine

    engine = create_engine(url)
    df.to_sql("orders", engine, if_exists="replace", index=False, method="multi", chunksize=5000)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--postgres", default=None, help="postgresql://analyst:analyst@localhost:5432/superstore")
    args = parser.parse_args()

    raw_path = resolve_raw()
    print(f"Чтение: {raw_path}")
    df = pd.read_csv(raw_path, encoding="utf-8", low_memory=False)
    print(f"Строк в сырье: {len(df):,}")

    clean_df = clean(df)
    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    clean_df.to_parquet(OUT_PARQUET, index=False)
    print(f"Сохранено: {OUT_PARQUET} ({len(clean_df):,} строк)")

    try:
        load_duckdb(clean_df, DUCKDB_PATH)
        print(f"База DuckDB: {DUCKDB_PATH}")
    except Exception as exc:
        print(
            f"Предупреждение: DuckDB не обновлён ({exc}). "
            "Закройте Streamlit/Jupyter и повторите ETL. Parquet сохранён."
        )

    from superstore.etl.data_quality import print_report, run_checks

    report = run_checks(clean_df)
    print_report(report)
    if not report.passed:
        raise SystemExit("Проверки качества данных не пройдены")

    if args.postgres:
        load_postgres(clean_df, args.postgres)
        print("Загружено в PostgreSQL, таблица orders")


if __name__ == "__main__":
    main()
