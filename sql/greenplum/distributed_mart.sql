CREATE TABLE IF NOT EXISTS fact_orders (
    row_id          BIGINT,
    order_id        VARCHAR(32),
    order_date      DATE,
    customer_id     VARCHAR(32),
    product_id      VARCHAR(32),
    region          VARCHAR(32),
    sales           NUMERIC(12,2),
    profit          NUMERIC(12,2),
    quantity        INT,
    discount        NUMERIC(5,4),
    year            INT
)
DISTRIBUTED BY (customer_id);

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id     VARCHAR(32),
    customer_name   VARCHAR(128),
    segment         VARCHAR(32),
    country         VARCHAR(64)
)
DISTRIBUTED BY (customer_id);

SELECT
    c.segment,
    f.year,
    COUNT(*) AS order_lines,
    SUM(f.sales) AS revenue,
    SUM(f.profit) AS profit
FROM fact_orders f
JOIN dim_customer c USING (customer_id)
GROUP BY 1, 2
ORDER BY 3 DESC;
