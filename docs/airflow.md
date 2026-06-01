# Airflow

DAG: [`dags/superstore_etl.py`](../dags/superstore_etl.py) — ETL → проверки → EDA → статистика.

## Windows

CLI `airflow` в обычном venv **не стартует** (модуль `fcntl` только в Linux). Варианты:

1. **Docker** — `.\scripts\run_airflow_docker.ps1` (нужен запущенный Docker Desktop, `docker info` без ошибок).
2. **WSL2** — команды ниже из каталога проекта в Ubuntu.

## Linux / WSL

```bash
export AIRFLOW_HOME=./.airflow
export AIRFLOW_PROJECT_ROOT=$PWD
export PYTHONPATH=.
pip install apache-airflow pandas pyarrow duckdb scipy scikit-learn
airflow db migrate
airflow dags test superstore_etl 2024-01-01
```

## Без запуска

На GitHub достаточно просмотра кода DAG и [otchet.md](otchet.md).
