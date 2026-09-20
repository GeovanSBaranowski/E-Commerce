CREATE SCHEMA IF NOT EXISTS analytics;

CREATE OR REPLACE VIEW analytics.monthly_category_revenue AS
SELECT
    CAST(DATE_TRUNC('month', oi.order_date) AS date) AS sale_month,
    p.category,
    SUM(oi.quantity * oi.unit_price) AS faturamento
FROM order_items AS oi
JOIN products AS p
    ON oi.product_id = p.product_id
WHERE oi.status = 'completed'
GROUP BY
    DATE_TRUNC('month', oi.order_date),
    p.category
ORDER BY
    sale_month,
    p.category;