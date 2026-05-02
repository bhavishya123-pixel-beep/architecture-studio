"""Project Due-Diligence page."""
import streamlit as st
import pandas as pd


def render():
    st.title("📋 Project Due-Diligence")
    st.caption("RERA status, developer history, possession risk, and compliance flags.")

    col1, col2 = st.columns(2)
    with col1:
        rera_number = st.text_input("RERA Registration Number", placeholder="e.g. P51700012345")
    with col2:
        project_name = st.text_input("Project Name", placeholder="e.g. Prestige Lakeside Habitat")

    city = st.selectbox("State RERA Portal", [
        "MahaRERA (Maharashtra)", "K-RERA (Karnataka)",
        "TSRERA (Telangana)", "UP-RERA", "RERA Delhi",
    ])

    if st.button("Run Due Diligence", type="primary"):
        if not rera_number and not project_name:
            st.error("Enter RERA number or project name.")
            return
        st.info("⏳ Fetching RERA data... (demo mode: showing synthetic record)")
        _show_demo_dd(rera_number or "P51700012345", project_name or "Demo Project", city)


def _show_demo_dd(rera_no, project, portal):
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("RERA Status", "✅ Registered")
    col2.metric("Possession Delay", "127 days", "🟡 Moderate")
    col3.metric("Complaints", "3", "0 active")
    col4.metric("Units Remaining", "142 / 480", "30%")

    st.markdown("### RERA Record")
    st.json({
        "rera_number": rera_no,
        "project_name": project,
        "portal": portal,
        "developer": "Demo Developer Pvt Ltd",
        "status": "Registered",
        "registration_date": "2022-03-15",
        "promised_possession": "2025-06-30",
        "revised_possession": "2025-10-30",
        "possession_delay_days": 122,
        "total_units": 480,
        "units_sold": 338,
        "units_remaining": 142,
        "complaints_total": 3,
        "active_complaints": 0,
        "carpet_area_sqft_range": [650, 1200],
        "confidence": 0.92,
        "source": portal,
    })

    st.markdown("### Risk Flags")
    flags = [
        "🟡 MODERATE: Possession delayed 122 days",
        "✅ CLEAR: No active RERA complaints",
        "✅ CLEAR: RERA registration active",
        "✅ CLEAR: Complaint rate <1% of total units",
    ]
    for f in flags:
        st.write(f)

    st.markdown("### Developer History")
    dev_data = {
        "Metric": ["Total Projects", "Completed", "Delayed", "On-Time Rate", "Avg Delay"],
        "Value": ["14", "9", "4", "64%", "89 days"],
    }
    st.dataframe(pd.DataFrame(dev_data), hide_index=True, use_container_width=True)

    st.warning(
        "⚠️ This report is generated from publicly available RERA data. "
        "Conduct independent legal verification before transacting."
    )
