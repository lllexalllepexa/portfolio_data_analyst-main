# Airflow DAG

Файл `superstore_etl.py`:

```
run_python_etl → [run_eda_plots, validate_data_quality] → run_stats_models
```

Инструкция по запуску: [docs/airflow.md](../docs/airflow.md).
