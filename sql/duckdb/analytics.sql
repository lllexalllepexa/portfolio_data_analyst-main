INSTALL httpfs;
LOAD httpfs;

SELECT
    region,
    category,
    COUNT(*) AS lines,
    ROUND(SUM(sales), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit,
    ROUND(AVG(discount), 4) AS avg_discount
FROM orders
WHERE year BETWEEN 2011 AND 2014
GROUP BY 1, 2
ORDER BY revenue DESC
LIMIT 20;

SELECT
    region,
    year,
    revenue,
    revenue / SUM(revenue) OVER (PARTITION BY region ORDER BY year) AS cumulative_share
FROM mart_region_year
ORDER BY region, year;
