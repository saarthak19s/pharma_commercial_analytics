-- Incentive Compensation: calculate rep payout based on target attainment tiers.
-- Standard pharma IC structure: base kicker at 80%, accelerator above 100%.

SELECT
    rep_id,
    rep_name,
    territory,
    annual_target_usd,
    actual_sales_usd,
    attainment_pct,
    CASE
        WHEN attainment_pct < 80 THEN 0.0
        WHEN attainment_pct >= 80 AND attainment_pct < 100 THEN annual_target_usd * 0.05
        WHEN attainment_pct >= 100 AND attainment_pct < 120 THEN annual_target_usd * 0.10
        ELSE annual_target_usd * 0.10 + (actual_sales_usd - annual_target_usd * 1.2) * 0.15
    END AS incentive_payout_usd,
    CASE
        WHEN attainment_pct >= 120 THEN 'Accelerator Tier'
        WHEN attainment_pct >= 100 THEN 'Target Achieved'
        WHEN attainment_pct >= 80 THEN 'Threshold Met'
        ELSE 'Below Threshold - No Payout'
    END AS ic_tier
FROM reps
ORDER BY attainment_pct DESC;
