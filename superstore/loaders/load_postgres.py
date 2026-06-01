"""
Загрузка Parquet в PostgreSQL.

Сначала поднимите Postgres:
  docker compose up -d postgres
  (Docker Desktop должен быть запущен: docker info)

Затем:
  python -m superstore.loaders.load_postgres
"""
from __future__ import annotations

import socket
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[2]
PARQUET = ROOT / "data" / "processed" / "orders_clean.parquet"
URL = "postgresql+psycopg2://analyst:analyst@127.0.0.1:5432/superstore"


def _port_open(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def main(url: str = URL) -> None:
    if not PARQUET.exists():
        raise SystemExit(
            f"Нет {PARQUET}. Сначала: python -m superstore.etl.load_and_clean"
        )

    if not _port_open("127.0.0.1", 5432):
        print(
            "PostgreSQL на порту 5432 недоступен.\n"
            "1. Запустите Docker Desktop (иконка в трее → Engine running).\n"
            "2. docker compose up -d postgres\n"
            "3. Подождите ~10 сек и повторите эту команду.\n"
            "\n"
            "Без Docker используйте SQL через DuckDB:\n"
            "  .\\scripts\\sql_duckdb_demo.ps1\n"
            "  или: docs/sql_postgres.md",
            file=sys.stderr,
        )
        raise SystemExit(1)

    df = pd.read_parquet(PARQUET)
    engine = create_engine(
        url,
        connect_args={"connect_timeout": 10, "options": "-c client_encoding=UTF8"},
    )

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        print(
            "Не удалось подключиться к PostgreSQL.\n"
            f"URL: {url}\n"
            f"Ошибка: {exc}\n\n"
            "Проверьте: docker compose ps\n"
            "Логи: docker compose logs postgres",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc

    df.to_sql("orders", engine, if_exists="replace", index=False, chunksize=5000)
    with engine.connect() as conn:
        n = conn.execute(text("SELECT COUNT(*) FROM orders")).scalar()
    print(f"PostgreSQL: в таблице orders — {n:,} строк")


if __name__ == "__main__":
    main()
