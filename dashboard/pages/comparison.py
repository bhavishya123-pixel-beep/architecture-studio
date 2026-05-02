"""Comparison view page."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def render():
    st.title("📊 Location Comparison")
    st.caption("Compare up to 4 micro-markets side by side.")

    all_markets = [
        "Hyderabad / Kokapet", "Hyderabad / Gachibowli", "Hyderabad / Narsingi",
        "Bengaluru / Sarjapur Road", "Bengaluru / Whitefield", "Bengaluru / Electronic City",
        "Pune / Hinjawadi", "Pune / Wagholi", "Mumbai / Thane", "Noida / Sector 150",
    ]

    selected = st.multiselect("Select markets to compare (max 4)", all_markets, max_selections=4,
                               default=["Hyderabad / Kokapet", "Bengaluru / Sarjapur Road", "Pune / Hinjawadi"])

    if not selected:
        st.info("Select at least one market.")
        return

    # Demo score data
    import random
    random.seed(99)
    demo = {}
    for m in selected:
        demo[m] = {
            "Infrastructure Uplift": random.randint(55, 90),
            "Connectivity": random.randint(50, 85),
            "Affordability": random.randint(45, 85),
            "Rental Yield": random.randint(50, 80),
            "Liquidity": random.randint(55, 82),
            "Regulatory Safety": random.randint(60, 90),
            "Developer Trust": random.randint(55, 85),
            "Execution Risk": random.randint(50, 88),
            "Final Score": random.randint(60, 88),
            "Price ₹/sqft": random.randint(5000, 12000),
            "Gross Yield %": round(random.uniform(2.0, 4.5), 2),
            "YoY % Change": round(random.uniform(5.0, 18.0), 1),
        }

    # Radar chart comparison
    categories = ["Infrastructure Uplift", "Connectivity", "Affordability",
                  "Rental Yield", "Liquidity", "Regulatory Safety"]
    colors = ["#2563EB", "#16A34A", "#CA8A04", "#DC2626"]

    fig = go.Figure()
    for i, market in enumerate(selected):
        vals = [demo[market][c] for c in categories]
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor=f"rgba{tuple(int(colors[i][j:j+2],16) for j in (1,3,5))+(0.12,)}",
            line=dict(color=colors[i], width=2),
            name=market,
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        height=420, legend=dict(orientation="h", y=-0.15),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Table comparison
    st.markdown("### Side-by-Side Metrics")
    rows = ["Final Score", "Price ₹/sqft", "Gross Yield %", "YoY % Change"]
    table_data = {"Metric": rows}
    for market in selected:
        table_data[market] = [demo[market][r] for r in rows]

    df = pd.DataFrame(table_data)
    st.dataframe(df, hide_index=True, use_container_width=True)

    st.caption("⚠️ Demo data. Connect scoring engine to database for live comparisons.")


