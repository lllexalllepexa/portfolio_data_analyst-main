# Запуск проекта

Клонирование:

```powershell
git clone https://github.com/lllexalllepexa/portfolio_data_analyst.git
cd portfolio_data_analyst
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Файл данных: `data/raw/global_superstore.csv` ([как получить](../data/raw/README.md)).

---

## Минимум

```powershell
python -m superstore.etl.load_and_clean
.\scripts\run_streamlit.ps1
```

Откроется дашборд в браузере.

---

## Полный Python-пайплайн

```powershell
.\scripts\run_pipeline.ps1
pytest tests/ -q
```

---

## SQL

**Без Docker** (DuckDB, создаётся при ETL):

```powershell
.\scripts\sql_duckdb_demo.ps1
```

Файлы запросов: [sql/duckdb/](../sql/duckdb/analytics.sql)

**С Docker** (PostgreSQL):

```powershell
.\scripts\run_postgres.ps1
```

Если Docker не запускается — [sql_postgres.md](sql_postgres.md).

---

## R

```r
install.packages(c("dplyr", "ggplot2", "readr", "arrow"))
```

```powershell
Rscript r/analysis.R
```

График: `docs/images/margin_by_category_r.png`

---

## Spark

Нужны Java 17+ и PySpark:

```powershell
pip install pyspark
python spark/run_pyspark.py
```

SQL: [spark/aggregations.sql](../spark/aggregations.sql)

---

## Airflow

Только через Docker на Windows:

```powershell
.\scripts\run_airflow_docker.ps1
```

Код DAG: [dags/superstore_etl.py](../dags/superstore_etl.py) · [airflow.md](airflow.md)

---

## Что смотреть на GitHub без запуска

- [otchet.md](otchet.md) — цифры и картинки  
- [model.md](model.md) — ERD  
- [bi.md](bi.md) — Superset, DataLens, Power BI
