-- Marketing Analytics: product-level performance, month-over-month trend,
-- and territory contribution — supports commercial reporting needs.

SELECT
    pr.product_name,
    pr.therapeutic_area,
    p.month,
    SUM(p.rx_count) AS total_rx,
    SUM(p.revenue_usd) AS total_revenue,
    ROUND(SUM(p.revenue_usd) * 100.0 / SUM(SUM(p.revenue_usd)) OVER (PARTITION BY p.month), 2) AS pct_of_month_revenue
FROM prescriptions p
JOIN products pr ON p.product_id = pr.product_id
GROUP BY pr.product_name, pr.therapeutic_area, p.month
ORDER BY p.month, total_revenue DESC;
