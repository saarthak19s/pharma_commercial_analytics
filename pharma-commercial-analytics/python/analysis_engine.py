import sqlite3 as sq
import pandas as pd
import os

base = os.path.dirname(__file__)
db_path = os.path.join(base, "..", "data", "database", "pharma_commercial.db")
sql_dir = os.path.join(base, "..", "sql")
out_dir = os.path.join(base, "..", "data", "processed")
os.makedirs(out_dir, exist_ok=True)


def run_query(conn, sql_file):
    with open(os.path.join(sql_dir, sql_file)) as f:
        query = f.read()
    return pd.read_sql_query(query, conn)


conn = sq.connect(db_path)

print("running hcp segmentation...")
segmentation = run_query(conn, "hcp_segmentation.sql")
segmentation.to_csv(out_dir + "/hcp_segmentation.csv", index=False)

print("running call planning...")
call_plan = run_query(conn, "call_planning.sql")
call_plan.to_csv(out_dir + "/call_planning.csv", index=False)

print("running incentive compensation...")
incentive = run_query(conn, "incentive_compensation.sql")
incentive.to_csv(out_dir + "/incentive_compensation.csv", index=False)

print("running marketing analytics...")
marketing = run_query(conn, "marketing_analytics.sql")
marketing.to_csv(out_dir + "/marketing_analytics.csv", index=False)

conn.close()

# quick summary so I can eyeball if numbers look sane
seg_summary = segmentation.groupby("hcp_segment").agg(
    hcp_count=("hcp_id", "count"),
    total_revenue=("total_revenue", "sum")
).reset_index()

print("\nhcp segment split:")
print(seg_summary.to_string(index=False))

under_called = call_plan[call_plan["call_plan_action"].str.contains("UNDER-CALLED")]
high_value_under_called = under_called[under_called["segment"] == "Tier 1 - High Value"]
print(f"\nhigh value hcps under called: {len(high_value_under_called)}")

total_payout = incentive["incentive_payout_usd"].sum()
print(f"total incentive payout: ${total_payout:,.0f}")

top_product = marketing.groupby("product_name")["total_revenue"].sum().idxmax()
print(f"top product: {top_product}")

seg_summary.to_csv(out_dir + "/segment_summary.csv", index=False)
print(f"\nsaved processed csvs to {out_dir}")