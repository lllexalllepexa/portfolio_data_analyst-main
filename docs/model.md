# Модель данных

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER_LINE : places
    PRODUCT  ||--o{ ORDER_LINE : contains
    ORDER    ||--|{ ORDER_LINE : has

    CUSTOMER {
        string customer_id PK
        string segment
    }
    PRODUCT {
        string product_id PK
        string category
        string sub_category
    }
    ORDER {
        string order_id PK
        date order_date
        date ship_date
    }
    ORDER_LINE {
        bigint row_id PK
        float sales
        float profit
        float discount
    }
```

## Витрина `mart_region_year`

| Поле | Тип | Смысл |
|------|-----|--------|
| region, country, year | измерения | |
| order_lines | count | число строк |
| revenue, profit | sum | метрики |
| margin | ratio | profit / revenue |

SQL: `sql/duckdb/analytics.sql`, `sql/postgres/init.sql`.
