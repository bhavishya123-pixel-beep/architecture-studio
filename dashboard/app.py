"""
India Real Estate Intelligence OS — Streamlit Dashboard
Main entry point: multi-page app.
"""

import streamlit as st

st.set_page_config(
    page_title="India RE Intelligence OS",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DISCLAIMER = (
    "⚠️ **Disclaimer:** This platform provides analytical support only. "
    "It does not constitute financial advice, legal advice, or guarantee of returns. "
    "Conduct independent due diligence before transacting."
)

def main():
    st.sidebar.title("India RE Intelligence OS")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigate",
        [
            "🏙️ City Dashboard",
            "🛣️ Corridor View",
            "📋 Project Due-Diligence",
            "🗺️ Map View",
            "🔔 Alert Feed",
            "⭐ Watchlist",
            "📊 Comparison",
            "📄 Memo Generator",
            "📈 Backtesting",
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.info(DISCLAIMER)

    if page == "🏙️ City Dashboard":
        from dashboard.pages.city_dashboard import render
        render()
    elif page == "🛣️ Corridor View":
        from dashboard.pages.corridor_view import render
        render()
    elif page == "📋 Project Due-Diligence":
        from dashboard.pages.project_dd import render
        render()
    elif page == "🗺️ Map View":
        from dashboard.pages.map_view import render
        render()
    elif page == "🔔 Alert Feed":
        from dashboard.pages.alert_feed import render
        render()
    elif page == "⭐ Watchlist":
        from dashboard.pages.watchlist import render
        render()
    elif page == "📊 Comparison":
        from dashboard.pages.comparison import render
        render()
    elif page == "📄 Memo Generator":
        from dashboard.pages.memo_generator import render
        render()
    elif page == "📈 Backtesting":
        from dashboard.pages.backtesting import render
        render()


if __name__ == "__main__":
    main()
