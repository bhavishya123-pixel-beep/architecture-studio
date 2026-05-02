"""Watchlist page."""
import streamlit as st
import pandas as pd
from datetime import datetime


def render():
    st.title("⭐ Watchlist")
    st.caption("Track locations and projects for ongoing monitoring.")

    with st.form("add_watchlist"):
        col1, col2, col3 = st.columns(3)
        with col1:
            city = st.text_input("City")
            locality = st.text_input("Locality")
        with col2:
            project = st.text_input("Project (optional)")
            rera = st.text_input("RERA No. (optional)")
        with col3:
            alert_types = st.multiselect(
                "Alert Types",
                ["INFRA_ANNOUNCED", "POSSESSION_SLIP", "PRICE_SPIKE", "RERA_CHANGE"],
                default=["INFRA_ANNOUNCED", "POSSESSION_SLIP"],
            )
        add = st.form_submit_button("Add to Watchlist", type="primary")

    if add and city and locality:
        if "watchlist" not in st.session_state:
            st.session_state["watchlist"] = []
        st.session_state["watchlist"].append({
            "City": city, "Locality": locality,
            "Project": project or "-", "RERA": rera or "-",
            "Alert Types": ", ".join(alert_types),
            "Added": datetime.utcnow().strftime("%Y-%m-%d"),
            "Score": "—",
        })
        st.success(f"Added {locality}, {city} to watchlist.")

    wl = st.session_state.get("watchlist", [
        {"City": "Hyderabad", "Locality": "Kokapet", "Project": "Prestige City",
         "RERA": "P02400001234", "Alert Types": "INFRA_ANNOUNCED, POSSESSION_SLIP",
         "Added": "2025-01-15", "Score": "82/100"},
        {"City": "Bengaluru", "Locality": "Sarjapur Road", "Project": "-",
         "RERA": "-", "Alert Types": "PRICE_SPIKE, INFRA_ANNOUNCED",
         "Added": "2025-02-01", "Score": "78/100"},
    ])

    if wl:
        df = pd.DataFrame(wl)
        st.dataframe(df, hide_index=True, use_container_width=True)
        if st.button("Clear Watchlist", type="secondary"):
            st.session_state["watchlist"] = []
            st.rerun()
    else:
        st.info("Your watchlist is empty. Add locations above.")
