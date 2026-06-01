-- PostgreSQL DWH schema (star-ish) for Global Superstore

CREATE TABLE IF NOT EXISTS orders (
    row_id              BIGINT PRIMARY KEY,
    order_id            TEXT NOT NULL,
    order_date          DATE,
    ship_date           DATE,
    customer_id         TEXT,
    customer_name       TEXT,
    product_id          TEXT,
    product_name        TEXT,
    category            TEXT,
    sub_category        TEXT,
    region              TEXT,
    country             TEXT,
    state               TEXT,
    city                TEXT,
    segment             TEXT,
    market              TEXT,
    market_group        TEXT,
    sales               NUMERIC(12, 2),
    profit              NUMERIC(12, 2),
    quantity            INTEGER,
    discount            NUMERIC(5, 4),
    shipping_cost       NUMERIC(10, 2),
    profit_margin       NUMERIC(8, 4),
    delivery_days       INTEGER,
    year                INTEGER
);

CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders (order_date);
CREATE INDEX IF NOT EXISTS idx_orders_region ON orders (region);

CREATE OR REPLACE VIEW mart_region_year AS
SELECT
    region,
    country,
    year,
    COUNT(*)                    AS order_lines,
    SUM(sales)                  AS revenue,
    SUM(profit)                 AS profit,
    SUM(profit) / NULLIF(SUM(sales), 0) AS margin
FROM orders
GROUP BY 1, 2, 3;
