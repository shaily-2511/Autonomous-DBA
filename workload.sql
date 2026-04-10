-- Run these slow queries multiple times to generate statistics
-- Query 1: Slow date range query (no index on order_date)
SELECT customer_id, COUNT(*) as order_count, SUM(total_amount) as total_revenue
FROM orders
WHERE order_date >= '2025-01-01' AND order_date < '2026-01-01'
GROUP BY customer_id
HAVING SUM(total_amount) > 10000
ORDER BY total_revenue DESC;

-- Query 2: Slow join query (no indexes on foreign keys)
SELECT
    c.customer_segment,
    p.category,
    COUNT(DISTINCT o.order_id) as order_count,
    SUM(oi.line_total) as total_sales
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_date >= NOW() - INTERVAL '90 days'
GROUP BY c.customer_segment, p.category
ORDER BY total_sales DESC;

-- Run each query 5-10 times to accumulate statistics


