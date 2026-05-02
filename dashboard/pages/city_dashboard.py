"""City Dashboard page."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def render():
    st.title("🏙️ City Market Dashboard")
    st.caption("Select a city to view market intelligence, scoring, and infrastructure pipeline.")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        city = st.selectbox(
            "City",
            ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Pune",
             "Chennai", "Kolkata", "Ahmedabad", "Noida", "Gurugram"],
        )
    with col2:
        segment = st.selectbox("Segment", ["All", "affordable", "mid_income", "premium", "luxury"])
    with col3:
        period = st.selectbox("Period", ["Last Quarter", "Last 6 Months", "Last 1 Year", "Last 3 Years"])

    st.markdown("---")

    # ── Demo data ────────────────────────────────────────────────────────────
    demo_prices = {
        "Mumbai":    {"price": 18500, "yield": 2.2, "yoy": 8.5, "absorption": 62},
        "Bengaluru": {"price": 9200,  "yield": 3.1, "yoy": 12.3, "absorption": 71},
        "Hyderabad": {"price": 7800,  "yield": 3.4, "yoy": 15.2, "absorption": 78},
        "Pune":      {"price": 8500,  "yield": 2.9, "yoy": 9.8,  "absorption": 68},
        "Delhi":     {"price": 11000, "yield": 2.5, "yoy": 7.2,  "absorption": 55},
        "Chennai":   {"price": 7200,  "yield": 3.2, "yoy": 10.1, "absorption": 65},
        "Kolkata":   {"price": 5800,  "yield": 3.8, "yoy": 6.5,  "absorption": 52},
        "Ahmedabad": {"price": 5200,  "yield": 4.1, "yoy": 11.0, "absorption": 74},
        "Noida":     {"price": 7500,  "yield": 3.0, "yoy": 14.5, "absorption": 69},
        "Gurugram":  {"price": 12000, "yield": 2.4, "yoy": 10.8, "absorption": 63},
    }
    data = demo_prices.get(city, demo_prices["Mumbai"])

    # KPI cards
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Avg Price/sqft", f"₹{data['price']:,}", f"{data['yoy']:+.1f}% YoY")
    k2.metric("Gross Yield", f"{data['yield']:.1f}%", "vs benchmark 3%")
    k3.metric("Absorption Rate", f"{data['absorption']}%", "+5% QoQ")
    k4.metric("Infra Pipeline", "3 active", "2 under construction")
    k5.metric("RERA Alerts", "2 flagged", "🔴 HIGH")

    st.markdown("---")

    col_chart, col_score = st.columns([3, 2])

    with col_chart:
        st.subheader("Price Trend (₹/sqft)")
        quarters = ["Q1'23", "Q2'23", "Q3'23", "Q4'23", "Q1'24", "Q2'24", "Q3'24", "Q4'24", "Q1'25"]
        base = data["price"]
        import random; random.seed(42)
        prices_trend = [int(base * (1 - data["yoy"]/100) ** ((8 - i) / 4)) for i in range(9)]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=quarters, y=prices_trend,
            mode="lines+markers",
            line=dict(color="#2563EB", width=2.5),
            fill="tozeroy", fillcolor="rgba(37,99,235,0.08)",
            name="Avg Price",
        ))
        fig.update_layout(
            height=300, margin=dict(l=0, r=0, t=10, b=0),
            yaxis_title="₹/sqft", xaxis_title=None,
            plot_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_score:
        st.subheader("Investment Score Radar")
        categories = [
            "Infra Uplift", "Connectivity", "Affordability",
            "Yield", "Liquidity", "Reg Safety",
        ]
        # Demo scores
        score_map = {
            "Mumbai": [55, 80, 30, 45, 85, 75],
            "Bengaluru": [78, 75, 65, 70, 78, 80],
            "Hyderabad": [85, 70, 72, 75, 72, 82],
            "Pune": [72, 68, 68, 65, 70, 78],
            "Noida": [88, 72, 70, 68, 60, 65],
        }
        scores = score_map.get(city, [65, 65, 65, 65, 65, 65])
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=scores + [scores[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(37,99,235,0.15)",
            line=dict(color="#2563EB"),
            name=city,
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            height=300, margin=dict(l=20, r=20, t=10, b=10),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # Infrastructure pipeline table
    st.subheader("Infrastructure Pipeline")
    infra_data = {
        "Project": [
            f"{city} Ring Road Phase 2",
            f"{city} Metro Line 7",
            f"{city} Bypass Expressway",
        ],
        "Type": ["Ring Road", "Metro", "Expressway"],
        "Status": ["Under Construction", "Approved", "Announced"],
        "Expected Completion": ["2026-Q2", "2027-Q1", "2028-Q4"],
        "Distance to Hub (km)": [3.5, 1.2, 8.0],
        "Uplift Score": ["🟢 High", "🟢 High", "🟡 Medium"],
    }
    st.dataframe(pd.DataFrame(infra_data), use_container_width=True, hide_index=True)

    st.caption(
        "⚠️ Demo data shown. Connect live ingestion pipeline for real-time intelligence."
    )
