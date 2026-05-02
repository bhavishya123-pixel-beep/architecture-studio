"""Alert feed page."""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta


def render():
    st.title("🔔 Alert Feed")
    st.caption("Real-time alerts triggered by infrastructure, RERA, price, and macro changes.")

    col1, col2, col3 = st.columns(3)
    with col1:
        severity_filter = st.multiselect(
            "Severity", ["HIGH", "MEDIUM", "LOW", "INFO"],
            default=["HIGH", "MEDIUM"],
        )
    with col2:
        city_filter = st.text_input("Filter by city", "")
    with col3:
        days_back = st.slider("Last N days", 1, 30, 7)

    st.markdown("---")

    # Demo alerts
    now = datetime.utcnow()
    demo_alerts = [
        {
            "Time": (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
            "Severity": "🔴 HIGH",
            "Type": "INFRA_APPROVED",
            "City": "Hyderabad",
            "Title": "Construction started: ORR Phase 3 Extension",
            "Body": "Hyderabad ORR Phase 3 extension (12.4 km) entered construction. Expected: Q3 2026.",
            "Source": "nhai_projects",
        },
        {
            "Time": (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"),
            "Severity": "🔴 HIGH",
            "Type": "RERA_CHANGE",
            "City": "Pune",
            "Title": "RERA REVOKED: Skyline Heights Phase 2",
            "Body": "RERA P52100012345 revoked. Immediate due diligence required.",
            "Source": "rera_maharashtra",
        },
        {
            "Time": (now - timedelta(hours=12)).strftime("%Y-%m-%d %H:%M"),
            "Severity": "🟡 MEDIUM",
            "Type": "PRICE_SPIKE",
            "City": "Bengaluru",
            "Title": "Price spike: Sarjapur Road +18.3%",
            "Body": "Avg price in Sarjapur Road jumped 18.3% QoQ. Verify against absorption data.",
            "Source": "propequity_feed",
        },
        {
            "Time": (now - timedelta(hours=18)).strftime("%Y-%m-%d %H:%M"),
            "Severity": "🟡 MEDIUM",
            "Type": "MACRO_RATE_CHANGE",
            "City": "National",
            "Title": "RBI repo rate cut: 6.00%",
            "Body": "RBI cut repo rate 25 bps to 6.00%. Mortgage affordability improves.",
            "Source": "rbi_mpc",
        },
        {
            "Time": (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
            "Severity": "🟢 LOW",
            "Type": "LAUNCH_SPIKE",
            "City": "Mumbai",
            "Title": "Launch spike: Thane 2.3× QoQ",
            "Body": "New launches in Thane jumped 2.3× QoQ (1,200 → 2,760 units). Monitor supply.",
            "Source": "propequity_feed",
        },
    ]

    # Filter
    filtered = demo_alerts
    if severity_filter:
        sev_map = {"HIGH": "🔴 HIGH", "MEDIUM": "🟡 MEDIUM", "LOW": "🟢 LOW", "INFO": "ℹ️ INFO"}
        allowed = [sev_map[s] for s in severity_filter if s in sev_map]
        filtered = [a for a in filtered if a["Severity"] in allowed]
    if city_filter:
        filtered = [a for a in filtered if city_filter.lower() in a["City"].lower()]

    st.write(f"**{len(filtered)} alerts** (demo data)")

    for alert in filtered:
        sev = alert["Severity"]
        icon = "🔴" if "HIGH" in sev else "🟡" if "MEDIUM" in sev else "🟢"
        with st.expander(f"{icon} {alert['Title']} — {alert['City']} ({alert['Time']})"):
            st.write(alert["Body"])
            st.caption(f"Type: {alert['Type']} | Source: {alert['Source']}")
            col_ack, col_inv = st.columns(2)
            col_ack.button("✓ Acknowledge", key=f"ack_{alert['Time']}")
            col_inv.button("🔍 Investigate", key=f"inv_{alert['Time']}")

    st.caption("⚠️ Demo data. Connect alert evaluator + database for live feed.")
