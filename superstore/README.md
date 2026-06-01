# Пакет `superstore`

| Модуль | Назначение |
|--------|------------|
| `etl/load_and_clean.py` | CSV → Parquet, DuckDB |
| `etl/data_quality.py` | Проверки после загрузки |
| `analysis/eda.py` | Описательная статистика, PNG |
| `analysis/stats_models.py` | t-test, регрессия, PCA |
| `embeddings/chroma_products.py` | Поиск по каталогу (ChromaDB) |
| `loaders/load_postgres.py` | Выгрузка в Postgres |
| `labels.py` | Русские подписи для UI |

```bash
python -m superstore.etl.load_and_clean
python -m superstore.analysis.eda
pytest ../tests -q
```
