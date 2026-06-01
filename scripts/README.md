# Скрипты

Запускать из **корня репозитория**.

| Скрипт | Назначение |
|--------|------------|
| [setup.ps1](setup.ps1) | venv + зависимости + ETL (если есть CSV) |
| [run_pipeline.ps1](run_pipeline.ps1) | ETL → quality → EDA → stats |
| [run_streamlit.ps1](run_streamlit.ps1) | Дашборд Streamlit |
| [sql_duckdb_demo.ps1](sql_duckdb_demo.ps1) | SQL через DuckDB (без Docker) |
| [run_postgres.ps1](run_postgres.ps1) | Docker Postgres + загрузка |
| [run_airflow_docker.ps1](run_airflow_docker.ps1) | Тест DAG в Docker |
| [run_airflow_test.ps1](run_airflow_test.ps1) | Airflow на Linux/WSL |

Linux/macOS: [setup.sh](setup.sh)
