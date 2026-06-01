"""Проверки качества данных после ETL."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class QualityReport:
    passed: bool
    checks: list[dict]


def run_checks(df: pd.DataFrame, min_rows: int = 10_000) -> QualityReport:
    checks: list[dict] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"check": name, "ok": ok, "detail": detail})

    add("row_count", len(df) >= min_rows, f"строк={len(df):,}")
    add("no_null_order_id", df["order_id"].notna().all())
    add("positive_sales", (df["sales"] > 0).all(), "вся выручка > 0")
    margin = df["profit_margin"].dropna()
    p99 = margin.abs().quantile(0.99)
    add(
        "profit_margin_range",
        p99 < 5,
        f"99-й перц. |маржа|={p99:.2f}",
    )
    add(
        "valid_years",
        df["year"].between(2011, 2014).fillna(False).all(),
        f"годы={sorted(df['year'].dropna().unique().astype(int).tolist())}",
    )
    add(
        "regions_present",
        df["region"].nunique() >= 4,
        f"регионов={df['region'].nunique()}",
    )
    add(
        "order_dates_populated",
        df["order_date"].notna().mean() > 0.99,
        f"заполнено дат={df['order_date'].notna().mean():.1%}",
    )

    passed = all(c["ok"] for c in checks)
    return QualityReport(passed=passed, checks=checks)


def print_report(report: QualityReport) -> None:
    from superstore.labels import QUALITY_CHECKS_RU

    for c in report.checks:
        status = "ОК" if c["ok"] else "ОШИБКА"
        name = QUALITY_CHECKS_RU.get(c["check"], c["check"])
        detail = f" — {c['detail']}" if c.get("detail") else ""
        print(f"[{status}] {name}{detail}")
    print("\n" + ("ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ" if report.passed else "ЕСТЬ ОШИБКИ КАЧЕСТВА ДАННЫХ"))
