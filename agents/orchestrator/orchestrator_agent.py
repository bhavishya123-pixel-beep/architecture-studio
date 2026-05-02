"""
Orchestrator Agent
───────────────────
The top-level coordinator. Calls all specialist agents, resolves
conflicts, invokes the LLM for narrative generation, and produces
the final InvestmentMemo.

LLM is used ONLY for narrative text — all scores come from specialist agents.
"""

from __future__ import annotations

import logging
import time
from typing import Optional

from agents.base import BaseAgent, AgentOutput
from agents.infrastructure.infra_watch_agent import InfraWatchAgent
from agents.rera.rera_compliance_agent import RERAComplianceAgent
from agents.macro.macro_signal_agent import MacroSignalAgent
from agents.market.market_data_agent import MarketDataAgent
from agents.valuation.valuation_agent import ValuationAgent
from agents.risk.risk_agent import RiskAgent
from api.schemas import (
    InvestmentMemo, LocationScoreCard, InfrastructureRecord,
    RERARecord, MarketPriceRecord, MacroSignalRecord, DeveloperRecord,
    InfraProximity, AssetType,
)
from scoring.engine import build_location_scorecard
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class OrchestratorAgent(BaseAgent):
    def __init__(self, llm_client=None):
        super().__init__("OrchestratorAgent")
        self.llm_client = llm_client
        self._infra_agent = InfraWatchAgent()
        self._rera_agent = RERAComplianceAgent()
        self._macro_agent = MacroSignalAgent()
        self._market_agent = MarketDataAgent()
        self._valuation_agent = ValuationAgent()
        self._risk_agent = RiskAgent()

    async def run(
        self,
        city: str,
        state: str,
        locality: str,
        pin_code: Optional[str] = None,
        project_name: Optional[str] = None,
        rera_records: Optional[list[RERARecord]] = None,
        price_records: Optional[list[MarketPriceRecord]] = None,
        macro_records: Optional[list[MacroSignalRecord]] = None,
        infra_records: Optional[list[InfrastructureRecord]] = None,
        proximal_infra: Optional[list[InfraProximity]] = None,
        developer: Optional[DeveloperRecord] = None,
        developer_rera: Optional[list[RERARecord]] = None,
        holding_years: int = 5,
    ) -> AgentOutput:
        t0 = time.perf_counter()

        rera_records = rera_records or []
        price_records = price_records or []
        macro_records = macro_records or []
        infra_records = infra_records or []
        proximal_infra = proximal_infra or []
        developer_rera = developer_rera or []

        try:
            # ── Run specialist agents ────────────────────────────────────────
            macro_out = await self._macro_agent.run(macro_records=macro_records)
            market_out = await self._market_agent.run(
                price_records=price_records, city=city, locality=locality
            )
            rera_out = await self._rera_agent.run(
                rera_records=rera_records, developer=developer
            )
            valuation_out = await self._valuation_agent.run(
                price_records=price_records,
                macro_signals=macro_records,
                holding_years=holding_years,
            )
            risk_out = await self._risk_agent.run(
                rera_records=rera_records,
                price_records=price_records,
                macro_signals=macro_records,
                developer=developer,
            )

            # ── Scoring engine ───────────────────────────────────────────────
            scorecard = build_location_scorecard(
                city=city, state=state, locality=locality,
                pin_code=pin_code,
                proximal_infra=proximal_infra,
                rera_records=rera_records,
                price_records=price_records,
                macro_signals=macro_records,
                developer=developer,
                developer_rera=developer_rera,
            )

            # ── LLM narrative generation ─────────────────────────────────────
            if self.llm_client:
                memo_text = await self._generate_memo_narrative(
                    city=city, state=state, locality=locality,
                    scorecard=scorecard,
                    market=market_out.result or {},
                    macro=macro_out.result or {},
                    rera=rera_out.result or {},
                    valuation=valuation_out.result or {},
                    risk=risk_out.result or {},
                )
            else:
                memo_text = self._fallback_narrative(
                    city, state, locality, scorecard,
                    market_out.result or {}, risk_out.result or {},
                )

            # ── Assemble memo ────────────────────────────────────────────────
            all_evidence = list(set(
                (macro_out.evidence_ids or [])
                + (market_out.evidence_ids or [])
                + (rera_out.evidence_ids or [])
                + (risk_out.evidence_ids or [])
            ))

            val_data = valuation_out.result or {}
            scenarios = val_data.get("scenarios", [])
            from api.schemas import InvestmentScenario
            scenario_objects = []
            for s in scenarios:
                try:
                    scenario_objects.append(InvestmentScenario(**s))
                except Exception:
                    pass

            risk_data = risk_out.result or {}
            confidence_level = (
                "high" if (scorecard.final_confidence or 0) > 0.75
                else "medium" if (scorecard.final_confidence or 0) > 0.50
                else "low"
            )

            memo = InvestmentMemo(
                city=city,
                state=state,
                locality=locality,
                project_name=project_name,
                developer=developer.name if developer else None,
                summary=memo_text.get("summary", ""),
                thesis=memo_text.get("thesis", ""),
                location_facts=memo_text.get("location_facts", ""),
                infrastructure_tailwinds=memo_text.get("infrastructure_tailwinds", ""),
                market_evidence=memo_text.get("market_evidence", ""),
                valuation_context=memo_text.get("valuation_context", ""),
                legal_rera_status=memo_text.get("legal_rera_status", ""),
                risks=memo_text.get("risks", ""),
                watch_conditions=memo_text.get("watch_conditions", ""),
                score_card=scorecard,
                scenarios=scenario_objects,
                confidence_level=confidence_level,
                data_sources_used=list(
                    {r.source_id for r in rera_records + price_records + macro_records}
                ),
                evidence_ids=all_evidence,
            )

            ms = (time.perf_counter() - t0) * 1000
            return self._ok(
                result=memo.model_dump(mode="json"),
                evidence_ids=all_evidence,
                confidence=scorecard.final_confidence or 0.0,
                llm_used=self.llm_client is not None,
                processing_ms=ms,
            )

        except Exception as e:
            logger.exception("Orchestrator failed")
            return self._fail(str(e))

    async def _generate_memo_narrative(
        self, city, state, locality, scorecard, market, macro, rera, valuation, risk
    ) -> dict[str, str]:
        """Call LLM to generate memo text sections. All data is pre-computed."""
        from llm.summarizers.memo_summarizer import generate_memo_sections
        return await generate_memo_sections(
            city=city, state=state, locality=locality,
            scorecard=scorecard, market=market, macro=macro,
            rera=rera, valuation=valuation, risk=risk,
            llm_client=self.llm_client,
        )

    def _fallback_narrative(
        self, city, state, locality, scorecard, market, risk
    ) -> dict[str, str]:
        """Template-based narrative when LLM is unavailable."""
        score = scorecard.final_score
        completeness = scorecard.data_completeness_pct
        risk_level = risk.get("overall_risk_level", "UNKNOWN")

        snap = market.get("snapshot", {})
        avg_price = snap.get("avg_price_per_sqft", "N/A")
        avg_yield = snap.get("avg_gross_yield_pct", "N/A")
        yoy = snap.get("avg_price_yoy_pct", "N/A")

        return {
            "summary": (
                f"{locality}, {city} ({state}) scored {score}/100 on the investment "
                f"attractiveness index (data completeness: {completeness:.0f}%). "
                f"Risk level: {risk_level}."
            ),
            "thesis": (
                f"The location shows potential based on infrastructure proximity, "
                f"market data, and regulatory signals. Further investigation warranted."
            ),
            "location_facts": (
                f"City: {city}, State: {state}, Locality: {locality}."
            ),
            "infrastructure_tailwinds": (
                "See infrastructure score breakdown for proximity and status details."
            ),
            "market_evidence": (
                f"Avg price: ₹{avg_price}/sqft. "
                f"Gross yield: {avg_yield}%. "
                f"YoY price change: {yoy}%."
            ),
            "valuation_context": (
                "See scenario analysis in the scenarios section."
            ),
            "legal_rera_status": (
                "See RERA compliance section for project-level status."
            ),
            "risks": risk.get("regulatory_safety_explanation", ""),
            "watch_conditions": (
                "Monitor infrastructure completion milestones and RERA status changes."
            ),
        }
