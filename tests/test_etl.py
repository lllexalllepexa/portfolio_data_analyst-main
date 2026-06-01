"""pytest: ETL и качество данных."""
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
PARQUET = ROOT / "data" / "processed" / "orders_clean.parquet"


@pytest.fixture(scope="module")
def df() -> pd.DataFrame:
    if not PARQUET.exists():
        pytest.skip("Сначала запустите ETL")
    return pd.read_parquet(PARQUET)


def test_row_count(df: pd.DataFrame) -> None:
    assert len(df) > 50_000


def test_required_columns(df: pd.DataFrame) -> None:
    required = {
        "order_id",
        "sales",
        "profit",
        "region",
        "category",
        "order_date",
        "profit_margin",
    }
    assert required.issubset(df.columns)


def test_revenue_positive(df: pd.DataFrame) -> None:
    assert (df["sales"] > 0).all()


def test_quality_module(df: pd.DataFrame) -> None:
    from superstore.etl.data_quality import run_checks

    report = run_checks(df)
    assert report.passed
