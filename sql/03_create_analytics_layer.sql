CREATE SCHEMA IF NOT EXISTS analytics;

CREATE OR REPLACE VIEW analytics.monthly_category_revenue AS
SELECT
    CAST(DATE_TRUNC('month', oi.order_date) AS date) AS sale_month,
    p.category,
    SUM(oi.quantity * oi.unit_price) AS revenue
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

CREATE OR REPLACE VIEW analytics.product_sales AS
    SELECT 
    p.product_id,
    p.product_name,
    p.category,
    SUM(oi.quantity) AS total_units_sold,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    SUM(oi.quantity * oi.unit_price) AS revenue
FROM products AS p
JOIN order_items AS oi 
    ON oi.product_id = p.product_id
WHERE oi.status = 'completed'
GROUP BY
    p.product_id,
    p.product_name,
    p.category;

CREATE OR REPLACE VIEW analytics.customer_sales AS
SELECT 
    c.customer_id,
    c.name,
    c.city,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS revenue
FROM customers AS c
LEFT JOIN order_items AS oi
    ON c.customer_id = oi.customer_id
    AND oi.status = 'completed'
GROUP BY
    c.customer_id,
    c.name,
    c.city;