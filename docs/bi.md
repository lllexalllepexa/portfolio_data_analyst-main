# Внешние BI-системы

Данные после ETL: `data/processed/orders_clean.parquet` или таблица `orders` в PostgreSQL.

## Superset

1. `docker compose up -d postgres`
2. `python -m superstore.etl.load_and_clean --postgres postgresql://analyst:analyst@localhost:5432/superstore`
3. Dataset: `mart_region_year` или `orders`.

## Yandex DataLens

Загрузка Parquet/CSV или подключение к ClickHouse/Postgres из `docker-compose.yml`.

## Power BI

Источник Parquet или PostgreSQL. Примеры мер:

```
Total Revenue = SUM(orders[sales])
Margin % = DIVIDE(SUM(orders[profit]), SUM(orders[sales]))
```

## Streamlit в репозитории

```powershell
.\scripts\run_streamlit.ps1
```

Статические скрины — в [otchet.md](otchet.md).
