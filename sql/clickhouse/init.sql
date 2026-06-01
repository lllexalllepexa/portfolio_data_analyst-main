-- ClickHouse: columnar OLAP (run after loading CSV via clickhouse-client or Python)

CREATE DATABASE IF NOT EXISTS superstore;

CREATE TABLE IF NOT EXISTS superstore.orders
(
    row_id UInt64,
    order_id String,
    order_date Date,
    ship_date Date,
    customer_id String,
    product_id String,
    product_name String,
    category LowCardinality(String),
    sub_category LowCardinality(String),
    region LowCardinality(String),
    country LowCardinality(String),
    segment LowCardinality(String),
    sales Float64,
    profit Float64,
    quantity UInt32,
    discount Float64,
    year UInt16
)
ENGINE = MergeTree()
ORDER BY (region, order_date, row_id);

-- Materialized-style rollup for dashboards
CREATE VIEW IF NOT EXISTS superstore.mart_daily AS
SELECT
    toStartOfMonth(order_date) AS month,
    region,
    sum(sales) AS revenue,
    sum(profit) AS profit,
    uniqExact(customer_id) AS customers
FROM superstore.orders
GROUP BY month, region;
