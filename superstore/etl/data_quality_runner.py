"""CLI: python -m superstore.etl.data_quality_runner"""
from pathlib import Path

import pandas as pd

from superstore.etl.data_quality import print_report, run_checks

PARQUET = Path(__file__).resolve().parents[2] / "data" / "processed" / "orders_clean.parquet"


def main() -> None:
    if not PARQUET.exists():
        raise SystemExit(f"Missing {PARQUET}")
    df = pd.read_parquet(PARQUET)
    report = run_checks(df)
    print_report(report)
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
