"""Corridor View page."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def render():
    st.title("🛣️ Corridor Intelligence View")
    st.caption("Analyze micro-markets along major infrastructure corridors.")

    corridor = st.selectbox(
        "Select Corridor",
        [
            "Hyderabad ORR — Outer Ring Road",
            "Bengaluru Peripheral Ring Road",
            "Pune-Mumbai Expressway Belt",
            "Delhi-Meerut RRTS Corridor",
            "Mumbai Trans-Harbour Link Zone",
            "Noida Expressway — Yamuna Zone",
            "Chennai Peripheral Ring Road",
        ],
    )

    st.markdown("---")
    col_info, col_score = st.columns([2, 1])

    # Demo corridor data
    corridor_data = {
        "Hyderabad ORR — Outer Ring Road": {
            "length": 158, "status": "Operational", "type": "Ring Road",
            "zones": ["Kokapet", "Narsingi", "Gachibowli", "HITECH City", "Raidurg"],
            "scores": [88, 82, 75, 78, 80],
            "prices": [9200, 8800, 9500, 10500, 9800],
            "uplift": "High — ORR is fully operational; new junction development ongoing",
        },
        "Bengaluru Peripheral Ring Road": {
            "length": 65, "status": "Under Construction", "type": "Expressway",
            "zones": ["Sarjapur", "Hoskote", "Devanahalli", "Nelamangala", "Tumkur Road"],
            "scores": [85, 72, 68, 65, 60],
            "prices": [7200, 5800, 6200, 5400, 5100],
            "uplift": "Very High — under construction; pre-completion appreciation window open",
        },
        "Delhi-Meerut RRTS Corridor": {
            "length": 82, "status": "Under Construction", "type": "Metro Rail",
            "zones": ["Anand Vihar", "Ghaziabad", "Muradnagar", "Modinagar", "Meerut"],
            "scores": [70, 78, 72, 68, 65],
            "prices": [8500, 5200, 4800, 4200, 3800],
            "uplift": "High — RRTS will cut Delhi-Meerut time to 55 min",
        },
    }
    cd = corridor_data.get(corridor, corridor_data["Hyderabad ORR — Outer Ring Road"])

    with col_info:
        st.markdown(f"**Length:** {cd['length']} km | **Status:** {cd['status']} | **Type:** {cd['type']}")
        st.markdown(f"**Uplift Assessment:** {cd['uplift']}")

    with col_score:
        best_score = max(cd["scores"])
        st.metric("Best Zone Score", f"{best_score}/100")

    # Zone comparison
    st.subheader("Micro-market Scores Along Corridor")
    fig = go.Figure()
    colors = ["#16A34A" if s >= 75 else "#2563EB" if s >= 60 else "#CA8A04" for s in cd["scores"]]
    fig.add_trace(go.Bar(
        x=cd["zones"], y=cd["scores"],
        marker_color=colors,
        text=[f"{s}" for s in cd["scores"]],
        textposition="outside",
    ))
    fig.update_layout(
        yaxis_range=[0, 100], yaxis_title="Investment Score",
        height=280, margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="white",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Price vs score
    st.subheader("Price vs. Score Scatter (Corridor Zones)")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=cd["prices"], y=cd["scores"],
        mode="markers+text",
        text=cd["zones"],
        textposition="top center",
        marker=dict(size=14, color="#2563EB", opacity=0.8),
    ))
    fig2.update_layout(
        xaxis_title="Avg Price ₹/sqft",
        yaxis_title="Investment Score",
        height=300, margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="white",
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.caption("⚠️ Demo data. Connect live ingestion pipeline for real-time corridor intelligence.")
