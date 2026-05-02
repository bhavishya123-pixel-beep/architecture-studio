"""Map view page — infrastructure + project overlay."""

import streamlit as st
import pandas as pd


def render():
    st.title("🗺️ Map View")
    st.caption("Infrastructure corridors, influence zones, and project locations.")

    try:
        import plotly.express as px
        import plotly.graph_objects as go
    except ImportError:
        st.error("Plotly required: pip install plotly")
        return

    city = st.selectbox(
        "Select City",
        ["Hyderabad", "Bengaluru", "Mumbai", "Pune", "Delhi-NCR"],
    )

    layer_opts = st.multiselect(
        "Layers",
        ["Infrastructure Projects", "RERA Projects", "Price Heatmap", "Influence Zones"],
        default=["Infrastructure Projects", "Influence Zones"],
    )

    st.markdown("---")

    # Demo coordinate data
    city_centers = {
        "Hyderabad": (17.385, 78.486),
        "Bengaluru": (12.972, 77.594),
        "Mumbai": (19.076, 72.877),
        "Pune": (18.520, 73.856),
        "Delhi-NCR": (28.704, 77.102),
    }
    center = city_centers.get(city, (20.0, 78.0))

    # Demo infra projects
    import random
    random.seed(hash(city))

    infra_points = []
    for i in range(6):
        lat = center[0] + random.uniform(-0.3, 0.3)
        lon = center[1] + random.uniform(-0.3, 0.3)
        infra_points.append({
            "name": f"Infra Project {i+1}",
            "type": random.choice(["Metro", "Highway", "Ring Road", "Expressway"]),
            "status": random.choice(["Under Construction", "Approved", "Announced"]),
            "lat": lat, "lon": lon,
        })

    df_infra = pd.DataFrame(infra_points)

    color_map = {
        "Under Construction": "#16A34A",
        "Approved": "#2563EB",
        "Announced": "#CA8A04",
    }

    fig = px.scatter_mapbox(
        df_infra,
        lat="lat", lon="lon",
        color="status",
        color_discrete_map=color_map,
        hover_name="name",
        hover_data={"type": True, "status": True, "lat": False, "lon": False},
        size_max=15,
        zoom=10,
        height=550,
        mapbox_style="open-street-map",
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(title="Status", orientation="h", y=-0.05),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Legend
    st.markdown(
        "🟢 Under Construction &nbsp;|&nbsp; 🔵 Approved &nbsp;|&nbsp; 🟡 Announced"
    )
    st.caption("⚠️ Demo coordinates. Connect PostGIS layer for real geo data.")
