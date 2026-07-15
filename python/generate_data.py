import pandas as pd
import numpy as np
import sqlite3 as sq
from datetime import datetime, timedelta
import os

np.random.seed(42)

out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(out_dir, exist_ok=True)
os.makedirs(out_dir + "/database", exist_ok=True)

# territories and reps
territories = ["Northeast", "Southeast", "Midwest", "West", "Southwest", "Northwest"]
n_reps = 30

reps = pd.DataFrame({
    "rep_id": [f"REP{str(i).zfill(3)}" for i in range(1, n_reps + 1)],
    "rep_name": [f"Rep_{i}" for i in range(1, n_reps + 1)],
    "territory": np.random.choice(territories, n_reps),
    "tenure_years": np.round(np.random.uniform(0.5, 12, n_reps), 1),
    "annual_target_usd": np.random.choice([400000, 500000, 600000, 750000], n_reps),
})

# product portfolio
products = pd.DataFrame({
    "product_id": ["PRD001", "PRD002", "PRD003", "PRD004", "PRD005"],
    "product_name": ["CardioMax", "GlucoBalance", "OncoShield", "NeuroCalm", "RespiraClear"],
    "therapeutic_area": ["Cardiology", "Endocrinology", "Oncology", "Neurology", "Pulmonology"],
    "list_price_usd": [120, 85, 950, 60, 45],
})

# HCPs = doctors, these are basically our "customers"
n_hcps = 800
specialties = ["Cardiologist", "Endocrinologist", "Oncologist", "Neurologist", "Pulmonologist", "General Physician"]

hcps = pd.DataFrame({
    "hcp_id": [f"HCP{str(i).zfill(4)}" for i in range(1, n_hcps + 1)],
    "specialty": np.random.choice(specialties, n_hcps, p=[0.15, 0.15, 0.1, 0.15, 0.15, 0.3]),
    "territory": np.random.choice(territories, n_hcps),
    "years_in_practice": np.random.randint(1, 35, n_hcps),
    "patient_volume_monthly": np.random.randint(50, 1200, n_hcps),
    "hospital_affiliated": np.random.choice([1, 0], n_hcps, p=[0.55, 0.45]),
})

# made-up "potential" score so segmentation actually has some signal to find,
# instead of pure random data. weights are just gut-feel, not from any paper
hcps["rx_potential_score"] = (
    (hcps["patient_volume_monthly"] / hcps["patient_volume_monthly"].max()) * 50
    + hcps["hospital_affiliated"] * 15
    + (hcps["years_in_practice"] / 35) * 20
    + np.random.normal(0, 10, n_hcps)
).clip(0, 100)

# now generate rep visits / calls
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 12, 31)
n_days = (end_date - start_date).days

# assign each hcp to a rep from the same territory
hcp_rep_map = {}
for _, hcp in hcps.iterrows():
    territory_reps = reps[reps["territory"] == hcp["territory"]]["rep_id"].values
    if len(territory_reps):
        hcp_rep_map[hcp["hcp_id"]] = np.random.choice(territory_reps)
    else:
        hcp_rep_map[hcp["hcp_id"]] = reps["rep_id"].sample(1).values[0]

call_rows = []
for _, hcp in hcps.iterrows():
    # doctors with higher potential get visited more - trying to keep this realistic
    n_calls = int(np.random.poisson(2 + hcp["rx_potential_score"] / 20))
    rep_id = hcp_rep_map[hcp["hcp_id"]]
    for _ in range(n_calls):
        call_date = start_date + timedelta(days=int(np.random.uniform(0, n_days)))
        call_rows.append({
            "call_id": f"CALL{len(call_rows)+1:06d}",
            "hcp_id": hcp["hcp_id"],
            "rep_id": rep_id,
            "call_date": call_date.strftime("%Y-%m-%d"),
            "product_discussed": np.random.choice(products["product_id"]),
            "call_duration_min": np.random.randint(5, 30),
            "samples_dropped": np.random.choice([0, 1, 2, 3], p=[0.4, 0.3, 0.2, 0.1]),
        })

calls = pd.DataFrame(call_rows)

# prescriptions - this is the outcome we actually care about.
# base rx depends on potential score + how many times rep visited (more calls -> more rx, roughly)
call_counts = calls.groupby("hcp_id").size().to_dict()
rx_rows = []

for _, hcp in hcps.iterrows():
    n_calls_hcp = call_counts.get(hcp["hcp_id"], 0)
    base_rx = hcp["rx_potential_score"] * 1.5 + n_calls_hcp * 3
    for month in range(1, 13):
        monthly_rx = max(0, int(np.random.normal(base_rx / 12, base_rx / 24)))
        if monthly_rx == 0:
            continue
        product = np.random.choice(products["product_id"])
        rx_rows.append({
            "hcp_id": hcp["hcp_id"],
            "product_id": product,
            "month": f"2025-{str(month).zfill(2)}",
            "rx_count": monthly_rx,
        })

prescriptions = pd.DataFrame(rx_rows)
prescriptions = prescriptions.merge(products[["product_id", "list_price_usd"]], on="product_id")
prescriptions["revenue_usd"] = prescriptions["rx_count"] * prescriptions["list_price_usd"]

# roll up to rep level for the incentive comp calc later
rx_with_rep = prescriptions.merge(
    hcps[["hcp_id"]].assign(rep_id=hcps["hcp_id"].map(hcp_rep_map)), on="hcp_id"
)
rep_sales = rx_with_rep.groupby("rep_id")["revenue_usd"].sum().reset_index()
rep_sales.columns = ["rep_id", "actual_sales_usd"]

reps = reps.merge(rep_sales, on="rep_id", how="left")
reps["actual_sales_usd"] = reps["actual_sales_usd"].fillna(0)
reps["attainment_pct"] = np.round(reps["actual_sales_usd"] / reps["annual_target_usd"] * 100, 1)

# dump everything to csv first
reps.to_csv(out_dir + "/reps.csv", index=False)
products.to_csv(out_dir + "/products.csv", index=False)
hcps.to_csv(out_dir + "/hcps.csv", index=False)
calls.to_csv(out_dir + "/calls.csv", index=False)
prescriptions.to_csv(out_dir + "/prescriptions.csv", index=False)

# and also push into sqlite so the sql module can query it
conn = sq.connect(out_dir + "/database/pharma_commercial.db")
reps.to_sql("reps", conn, if_exists="replace", index=False)
products.to_sql("products", conn, if_exists="replace", index=False)
hcps.to_sql("hcps", conn, if_exists="replace", index=False)
calls.to_sql("calls", conn, if_exists="replace", index=False)
prescriptions.to_sql("prescriptions", conn, if_exists="replace", index=False)
conn.close()

print("reps:", len(reps))
print("products:", len(products))
print("hcps:", len(hcps))
print("calls:", len(calls))
print("prescription rows:", len(prescriptions))