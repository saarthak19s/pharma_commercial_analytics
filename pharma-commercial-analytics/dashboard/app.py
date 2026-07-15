"""
Pharma Commercial Analytics Dashboard
Streamlit app presenting HCP segmentation, call planning, incentive compensation,
and marketing analytics — mirrors the JD's core commercial analytics use cases.
"""
import streamlit as st
import pandas as pd
import os
import plotly.express as px

BASE = os.path.dirname(__file__)
DATA = os.path.join(BASE, "..", "data", "processed")

st.set_page_config(page_title="Pharma Commercial Analytics", layout="wide")

st.title("💊 Pharma Commercial Analytics Dashboard")
st.caption("HCP Segmentation • Call Planning • Incentive Compensation • Marketing Analytics")

segmentation = pd.read_csv(f"{DATA}/hcp_segmentation.csv")
call_plan = pd.read_csv(f"{DATA}/call_planning.csv")
incentive = pd.read_csv(f"{DATA}/incentive_compensation.csv")
marketing = pd.read_csv(f"{DATA}/marketing_analytics.csv")

tab1, tab2, tab3, tab4 = st.tabs([
    "HCP Segmentation", "Call Planning", "Incentive Compensation", "Marketing Analytics"
])

with tab1:
    st.subheader("HCP Segmentation")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total HCPs", len(segmentation))
    col2.metric("Total Revenue", f"${segmentation['total_revenue'].sum():,.0f}")
    col3.metric("Tier 1 HCPs", len(segmentation[segmentation["hcp_segment"].str.contains("Tier 1")]))

    seg_summary = segmentation.groupby("hcp_segment")["total_revenue"].sum().reset_index()
    fig = px.pie(seg_summary, names="hcp_segment", values="total_revenue",
                 title="Revenue Contribution by HCP Segment")
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.scatter(segmentation, x="patient_volume_monthly", y="total_revenue",
                       color="hcp_segment", hover_data=["hcp_id", "specialty"],
                       title="Patient Volume vs Revenue by Segment")
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(segmentation, use_container_width=True)

with tab2:
    st.subheader("Call Planning: Recommended vs Actual Visits")
    action_counts = call_plan["call_plan_action"].value_counts().reset_index()
    action_counts.columns = ["action", "count"]
    fig3 = px.bar(action_counts, x="action", y="count", title="Call Plan Action Distribution",
                  color="action")
    st.plotly_chart(fig3, use_container_width=True)

    st.warning(
        f"{len(call_plan[(call_plan['segment']=='Tier 1 - High Value') & (call_plan['call_plan_action'].str.contains('UNDER'))])} "
        "high-value HCPs are currently under-called — reallocating rep time here is the "
        "highest-ROI call-plan fix."
    )
    st.dataframe(call_plan, use_container_width=True)

with tab3:
    st.subheader("Incentive Compensation")
    col1, col2 = st.columns(2)
    col1.metric("Total Payout Projected", f"${incentive['incentive_payout_usd'].sum():,.0f}")
    col2.metric("Reps Above Target", len(incentive[incentive["attainment_pct"] >= 100]))

    fig4 = px.bar(incentive.sort_values("attainment_pct", ascending=False),
                  x="rep_name", y="attainment_pct", color="ic_tier",
                  title="Rep Attainment % vs Target")
    st.plotly_chart(fig4, use_container_width=True)
    st.dataframe(incentive, use_container_width=True)

with tab4:
    st.subheader("Marketing / Product Analytics")
    trend = marketing.groupby(["month", "product_name"])["total_revenue"].sum().reset_index()
    fig5 = px.line(trend, x="month", y="total_revenue", color="product_name",
                    title="Monthly Revenue Trend by Product")
    st.plotly_chart(fig5, use_container_width=True)

    fig6 = px.bar(marketing.groupby("therapeutic_area")["total_revenue"].sum().reset_index(),
                  x="therapeutic_area", y="total_revenue", title="Revenue by Therapeutic Area")
    st.plotly_chart(fig6, use_container_width=True)

    st.dataframe(marketing, use_container_width=True)

st.markdown("---")
st.caption("Built with Python, SQL (SQLite), Pandas, and Streamlit | Synthetic data for demonstration purposes")
