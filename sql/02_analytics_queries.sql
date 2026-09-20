SELECT 
    CAST(DATE_TRUNC('month', oi.order_date) AS date) AS sale_month,
    p.category ,
    SUM(oi.quantity * oi.unit_price) AS Faturamento
FROM order_items AS oi
JOIN products AS P 
    ON oi.product_id = p.product_id
WHERE oi.status = 'completed'
GROUP BY 
    DATE_TRUNC('month', oi.order_date), 
    p.category
ORDER BY 
    sale_month,
    p.category;

SELECT
    p.product_name,
    SUM(oi.quantity * oi.unit_price) AS Faturamento 
FROM order_items AS oi
JOIN products AS p ON oi.product_id = p.product_id
WHERE oi.status = 'completed'
GROUP BY
    P.product_name
ORDER BY
    Faturamento DESC
LIMIT 10;

SELECT 
    c.customer_id,
    c.name,
    SUM(oi.quantity * oi.unit_price) AS Faturamento  
FROM order_items AS oi
JOIN customers AS c ON oi.customer_id = c.customer_id
WHERE oi.status = 'completed'
GROUP BY
    c.customer_id,
    c.name
ORDER BY
    Faturamento DESC
LIMIT 10;

SELECT 
    SUM(quantity * unit_price) AS Faturamento,
    COUNT(DISTINCT order_id) AS Pedidos_Total,
    ROUND(SUM(quantity * unit_price) / COUNT(DISTINCT order_id),2) AS Ticket_medio
FROM order_items
WHERE status = 'completed';

WITH orders_by_status AS (
    SELECT DISTINCT
        order_id,
        status
    FROM order_items
)
SELECT
    status,
    COUNT(*) AS total_orders,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () AS percentual
FROM orders_by_status
GROUP BY status
ORDER BY status;