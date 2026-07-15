# Pharma Commercial Analytics Engine

An end-to-end commercial analytics system for pharmaceutical sales operations — built with **Python, SQL, Pandas, and Streamlit**. Simulates and analyzes HCP (doctor) engagement, sales rep performance, and product/marketing trends to support data-driven commercial decisions in the healthcare/pharma sector.

## Overview

Pharma commercial teams need to decide **which doctors to prioritize, how often to visit them, how to pay reps fairly, and which products are performing**. This project builds a synthetic but realistic dataset (30 reps, 800 HCPs, 5 products, 3,400+ field calls, ~8,900 monthly prescription records across 2025) and a full analytics pipeline to answer exactly those questions.

## Features

| Module | Description |
|---|---|
| **HCP Segmentation** | Ranks 800 HCPs into Tier 1/2/3 value segments using SQL window functions (NTILE) on prescription revenue |
| **Call Planning** | Compares recommended vs. actual rep visit frequency per HCP segment; flags under-called high-value doctors |
| **Incentive Compensation** | Tiered payout engine (threshold → target → accelerator) calculating rep bonuses from target attainment |
| **Marketing Analytics** | Month-over-month product revenue trends and therapeutic-area contribution analysis |
| **Interactive Dashboard** | Streamlit app with Plotly visuals across all four modules |

## Tech Stack

- **Python**: Pandas, NumPy for data generation and orchestration
- **SQL (SQLite)**: All business logic (segmentation, call planning, IC, marketing analytics) written as pure SQL queries
- **Streamlit + Plotly**: Interactive dashboard

## Project Structure

```
pharma-commercial-analytics/
├── data/
│   ├── raw/                 # generated source data (via generate_data.py)
│   ├── processed/           # SQL query outputs (segmentation, call plan, IC, marketing)
│   └── database/
│       └── pharma_commercial.db
├── sql/
│   ├── hcp_segmentation.sql
│   ├── call_planning.sql
│   ├── incentive_compensation.sql
│   └── marketing_analytics.sql
├── python/
│   ├── generate_data.py     # synthetic data generator
│   └── analysis_engine.py   # runs SQL modules, prints key insights
├── dashboard/
│   └── app.py                # Streamlit dashboard
├── requirements.txt
└── README.md
```

## How to Run

```bash
pip install -r requirements.txt

# 1. Generate the dataset
python python/generate_data.py

# 2. Run the SQL analytics engine
python python/analysis_engine.py

# 3. Launch the dashboard
streamlit run dashboard/app.py
```

## Key Insights (from generated data)

- **Tier 1 HCPs** (267 doctors, top third by revenue) generate **~57% of total prescription revenue** ($8.6M of $14.5M) — validating a value-based segmentation approach.
- **265 high-value HCPs are currently under-called** relative to recommended visit frequency — the single highest-ROI fix in the call plan.
- Projected total incentive payout across 30 reps: **~$684K**, with a clear tiered structure rewarding over-attainment.
- **OncoShield** is the top revenue-generating product, consistent with oncology's higher list price.

## Note on Data

All data in this project is **synthetically generated** (see `generate_data.py`) to mirror realistic pharma commercial patterns (rep-territory structures, HCP prescribing behavior, call-Rx correlation). No real patient, HCP, or company data is used.
