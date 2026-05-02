"""Investment Memo Generator page."""

import asyncio
import streamlit as st


def render():
    st.title("📄 Investment Memo Generator")
    st.caption(
        "Generate a structured investment memo with evidence-backed analysis. "
        "LLM narrative requires ANTHROPIC_API_KEY to be set."
    )

    with st.form("memo_form"):
        col1, col2 = st.columns(2)
        with col1:
            city = st.text_input("City *", value="Hyderabad")
            state = st.text_input("State *", value="Telangana")
            locality = st.text_input("Locality / Micro-market *", value="Kokapet")
        with col2:
            project_name = st.text_input("Project Name (optional)", value="")
            holding_years = st.slider("Holding Period (years)", 1, 15, 5)
            use_llm = st.checkbox("Enable LLM narrative generation", value=False)

        submit = st.form_submit_button("Generate Memo", type="primary")

    if submit:
        if not city or not state or not locality:
            st.error("City, State, and Locality are required.")
            return

        with st.spinner("Running analysis pipeline..."):
            result = _run_memo(city, state, locality, project_name, holding_years, use_llm)

        if "error" in result:
            st.error(f"Analysis failed: {result['error']}")
            return

        memo = result.get("memo", {})
        _render_memo(memo, result)


def _run_memo(city, state, locality, project_name, holding_years, use_llm) -> dict:
    import asyncio
    from agents.orchestrator.orchestrator_agent import OrchestratorAgent
    from config.settings import get_settings
    settings = get_settings()

    llm_client = None
    if use_llm and settings.anthropic_api_key:
        try:
            import anthropic
            llm_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        except ImportError:
            pass

    agent = OrchestratorAgent(llm_client=llm_client)

    try:
        loop = asyncio.new_event_loop()
        output = loop.run_until_complete(
            agent.run(
                city=city, state=state, locality=locality,
                project_name=project_name or None,
                holding_years=holding_years,
            )
        )
        loop.close()
        if not output.success:
            return {"error": output.error}
        return {
            "memo": output.result,
            "processing_ms": output.processing_time_ms,
            "llm_used": output.llm_used,
        }
    except Exception as e:
        return {"error": str(e)}


def _render_memo(memo: dict, meta: dict):
    score_card = memo.get("score_card", {})
    final_score = score_card.get("final_score")
    confidence = score_card.get("final_confidence")
    completeness = score_card.get("data_completeness_pct", 0)
    risk_flag = score_card.get("human_review_required", False)

    # Header
    st.markdown("---")
    st.markdown(f"## Investment Memo: {memo.get('locality')}, {memo.get('city')}")
    if memo.get("project_name"):
        st.markdown(f"**Project:** {memo['project_name']}")
    if memo.get("developer"):
        st.markdown(f"**Developer:** {memo['developer']}")

    # Score banner
    col1, col2, col3, col4 = st.columns(4)
    score_color = "🟢" if (final_score or 0) > 65 else "🟡" if (final_score or 0) > 45 else "🔴"
    col1.metric("Investment Score", f"{score_color} {final_score}/100" if final_score else "N/A")
    col2.metric("Confidence", f"{(confidence or 0)*100:.0f}%" if confidence else "N/A")
    col3.metric("Data Completeness", f"{completeness:.0f}%")
    col4.metric("Human Review", "⚠️ Required" if risk_flag else "✅ Not required")

    if risk_flag:
        st.warning(
            "⚠️ This location requires human review before acting. "
            "Data completeness or risk flags triggered automatic review requirement."
        )

    st.markdown("---")

    # Memo sections
    sections = [
        ("📌 Summary", "summary"),
        ("💡 Investment Thesis", "thesis"),
        ("📍 Location Facts", "location_facts"),
        ("🏗️ Infrastructure Tailwinds", "infrastructure_tailwinds"),
        ("📊 Market Evidence", "market_evidence"),
        ("💰 Valuation Context", "valuation_context"),
        ("⚖️ Legal & RERA Status", "legal_rera_status"),
        ("⚠️ Risks", "risks"),
        ("👁️ Watch Conditions", "watch_conditions"),
    ]

    for label, key in sections:
        content = memo.get(key, "")
        if content:
            with st.expander(label, expanded=(key in ("summary", "thesis"))):
                st.write(content)

    # Scenarios
    scenarios = memo.get("scenarios", [])
    if scenarios:
        st.markdown("### Return Scenarios")
        cols = st.columns(len(scenarios))
        for i, sc in enumerate(scenarios):
            with cols[i]:
                label = sc.get("label", "").upper()
                icon = {"BEAR": "🐻", "BASE": "📊", "BULL": "🐂"}.get(label, "")
                st.markdown(f"**{icon} {label}**")
                st.metric("CAGR", f"{sc.get('cagr_pct', 0):.1f}%")
                st.metric("Exit ₹/sqft", f"₹{sc.get('exit_price_per_sqft', 0):,.0f}")
                st.metric("Gross Yield", f"{sc.get('gross_yield_pct', 0):.2f}%")
                st.caption(sc.get("assumption", ""))

    # Score breakdown
    if score_card:
        st.markdown("### Score Breakdown")
        score_dims = {
            "Infrastructure Uplift": score_card.get("infrastructure_uplift", {}),
            "Connectivity": score_card.get("connectivity", {}),
            "Affordability": score_card.get("affordability", {}),
            "Rental Yield": score_card.get("rental_yield", {}),
            "Liquidity": score_card.get("liquidity", {}),
            "Regulatory Safety": score_card.get("regulatory_safety", {}),
            "Developer Trust": score_card.get("developer_trust", {}),
            "Execution Risk": score_card.get("execution_risk", {}),
            "Appreciation Potential": score_card.get("appreciation_potential", {}),
        }
        import plotly.graph_objects as go
        names, scores_vals = [], []
        for name, bd in score_dims.items():
            if bd and not bd.get("data_gap"):
                names.append(name)
                scores_vals.append(bd.get("normalized_score", 0))

        if names:
            fig = go.Figure(go.Bar(
                x=scores_vals, y=names,
                orientation="h",
                marker_color=["#16A34A" if s > 65 else "#CA8A04" if s > 45 else "#DC2626" for s in scores_vals],
            ))
            fig.update_layout(
                height=350, xaxis_range=[0, 100],
                xaxis_title="Score (0–100)",
                margin=dict(l=0, r=20, t=10, b=0),
                plot_bgcolor="white",
            )
            st.plotly_chart(fig, use_container_width=True)

    # Meta
    st.markdown("---")
    st.caption(
        f"Generated in {meta.get('processing_ms', 0):.0f}ms. "
        f"LLM used: {'Yes' if meta.get('llm_used') else 'No (template fallback)'}. "
        f"Sources: {', '.join(memo.get('data_sources_used', ['none']))}."
    )
    st.error(memo.get("disclaimer", ""))
