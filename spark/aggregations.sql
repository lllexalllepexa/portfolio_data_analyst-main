-- Spark SQL: cluster-scale aggregations (submit via spark-sql or PySpark)

CREATE OR REPLACE TEMP VIEW orders
USING parquet
OPTIONS (path 'data/processed/orders_clean.parquet');

-- Regional YoY growth
WITH yearly AS (
    SELECT
        region,
        CAST(year AS INT) AS yr,
        SUM(sales) AS revenue
    FROM orders
    GROUP BY region, year
),
growth AS (
    SELECT
        region,
        yr,
        revenue,
        LAG(revenue) OVER (PARTITION BY region ORDER BY yr) AS prev_revenue
    FROM yearly
)
SELECT
    region,
    yr,
    ROUND(revenue, 2) AS revenue,
    ROUND(100.0 * (revenue - prev_revenue) / NULLIF(prev_revenue, 0), 2) AS yoy_pct
FROM growth
WHERE prev_revenue IS NOT NULL
ORDER BY region, yr;

-- Top sub-categories by profit per region (rank)
SELECT region, sub_category, profit, rnk
FROM (
    SELECT
        region,
        sub_category,
        SUM(profit) AS profit,
        RANK() OVER (PARTITION BY region ORDER BY SUM(profit) DESC) AS rnk
    FROM orders
    GROUP BY region, sub_category
) t
WHERE rnk <= 5;
