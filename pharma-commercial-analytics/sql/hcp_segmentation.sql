-- HCP Segmentation: classify doctors into Tier 1 (High), Tier 2 (Medium), Tier 3 (Low)
-- based on prescription revenue generated and patient volume.
-- This directly supports "segmentation" and "commercial analytics" use cases.

WITH hcp_revenue AS (
    SELECT
        h.hcp_id,
        h.specialty,
        h.territory,
        h.patient_volume_monthly,
        h.hospital_affiliated,
        COALESCE(SUM(p.revenue_usd), 0) AS total_revenue,
        COALESCE(SUM(p.rx_count), 0) AS total_rx
    FROM hcps h
    LEFT JOIN prescriptions p ON h.hcp_id = p.hcp_id
    GROUP BY h.hcp_id, h.specialty, h.territory, h.patient_volume_monthly, h.hospital_affiliated
),
ranked AS (
    SELECT *,
        NTILE(3) OVER (ORDER BY total_revenue DESC) AS revenue_tercile
    FROM hcp_revenue
)
SELECT
    hcp_id,
    specialty,
    territory,
    patient_volume_monthly,
    total_revenue,
    total_rx,
    CASE
        WHEN revenue_tercile = 1 THEN 'Tier 1 - High Value'
        WHEN revenue_tercile = 2 THEN 'Tier 2 - Medium Value'
        ELSE 'Tier 3 - Low Value'
    END AS hcp_segment
FROM ranked
ORDER BY total_revenue DESC;
