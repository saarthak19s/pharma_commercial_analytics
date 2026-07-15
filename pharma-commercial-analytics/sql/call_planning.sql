-- Call Planning: recommend visit frequency per HCP segment vs actual calls made.
-- Flags under-called high-value HCPs and over-called low-value HCPs (efficiency signal).

WITH hcp_segment AS (
    SELECT
        h.hcp_id,
        h.territory,
        COALESCE(SUM(p.revenue_usd), 0) AS total_revenue,
        NTILE(3) OVER (ORDER BY COALESCE(SUM(p.revenue_usd), 0) DESC) AS tercile
    FROM hcps h
    LEFT JOIN prescriptions p ON h.hcp_id = p.hcp_id
    GROUP BY h.hcp_id, h.territory
),
call_activity AS (
    SELECT hcp_id, COUNT(*) AS actual_calls
    FROM calls
    GROUP BY hcp_id
),
target_frequency AS (
    SELECT
        hs.hcp_id,
        hs.territory,
        hs.total_revenue,
        CASE
            WHEN hs.tercile = 1 THEN 'Tier 1 - High Value'
            WHEN hs.tercile = 2 THEN 'Tier 2 - Medium Value'
            ELSE 'Tier 3 - Low Value'
        END AS segment,
        CASE
            WHEN hs.tercile = 1 THEN 12   -- monthly visits for top-tier
            WHEN hs.tercile = 2 THEN 6    -- bi-monthly
            ELSE 3                        -- quarterly
        END AS recommended_annual_calls,
        COALESCE(ca.actual_calls, 0) AS actual_calls
    FROM hcp_segment hs
    LEFT JOIN call_activity ca ON hs.hcp_id = ca.hcp_id
)
SELECT
    hcp_id,
    territory,
    segment,
    recommended_annual_calls,
    actual_calls,
    (actual_calls - recommended_annual_calls) AS call_gap,
    CASE
        WHEN actual_calls < recommended_annual_calls THEN 'UNDER-CALLED - Increase Visits'
        WHEN actual_calls > recommended_annual_calls * 1.3 THEN 'OVER-CALLED - Reallocate Time'
        ELSE 'ON TARGET'
    END AS call_plan_action
FROM target_frequency
ORDER BY segment, call_gap ASC;
