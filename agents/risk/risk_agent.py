"""
Risk Agent
───────────
Aggregates all risk signals into a structured risk report.
Covers regulatory, execution, market, and liquidity risk.
Flags projects requiring human review.
"""

from __future__ import annotations

import time
from typing import Optional

from agents.base import BaseAgent, AgentOutput
from api.schemas import RERARecord, DeveloperRecord, MarketPriceRecord, MacroSignalRecord
from scoring.modules.regulatory_safety import compute_regulatory_safety_score
from scoring.modules.execution_risk import compute_execution_risk_score
from scoring.modules.liquidity import compute_liquidity_score


class RiskAgent(BaseAgent):
    def __init__(self):
        super().__init__("RiskAgent")

    async def run(
        self,
        rera_records: list[RERARecord],
        price_records: list[MarketPriceRecord],
        macro_signals: list[MacroSignalRecord],
        developer: Optional[DeveloperRecord] = None,
    ) -> AgentOutput:
        t0 = time.perf_counter()
        try:
            reg_score = compute_regulatory_safety_score(rera_records)
            exec_score = compute_execution_risk_score(rera_records, developer)
            liq_score = compute_liquidity_score(price_records)

            # Macro risk overlay
            macro_risk = self._macro_risk(macro_signals)

            # Overall risk level
            avg_risk_score = (
                reg_score.normalized_score * 0.35
                + exec_score.normalized_score * 0.35
                + liq_score.normalized_score * 0.20
                + macro_risk["score"] * 0.10
            )

            risk_level = (
                "HIGH" if avg_risk_score < 40
                else "MEDIUM" if avg_risk_score < 65
                else "LOW"
            )

            human_review = (
                avg_risk_score < 35
                or reg_score.normalized_score < 30
                or exec_score.normalized_score < 30
            )

            evidence_ids = (
                reg_score.evidence_ids
                + exec_score.evidence_ids
                + liq_score.evidence_ids
            )

            ms = (time.perf_counter() - t0) * 1000
            return self._ok(
                result={
                    "overall_risk_level": risk_level,
                    "overall_risk_score": round(avg_risk_score, 2),
                    "human_review_required": human_review,
                    "regulatory_safety_score": reg_score.normalized_score,
                    "regulatory_safety_explanation": reg_score.explanation,
                    "execution_risk_score": exec_score.normalized_score,
                    "execution_risk_explanation": exec_score.explanation,
                    "liquidity_score": liq_score.normalized_score,
                    "liquidity_explanation": liq_score.explanation,
                    "macro_risk": macro_risk,
                    "risk_flags": self._collect_flags(rera_records, developer),
                    "disclaimer": (
                        "Risk scores are analytical estimates, not legal assessments. "
                        "Conduct independent legal due diligence."
                    ),
                },
                evidence_ids=list(set(evidence_ids)),
                confidence=round(
                    (reg_score.confidence + exec_score.confidence + liq_score.confidence) / 3, 3
                ),
                processing_ms=ms,
            )

        except Exception as e:
            return self._fail(str(e))

    def _macro_risk(self, signals: list[MacroSignalRecord]) -> dict:
        score = 70.0  # neutral baseline
        notes = []
        for s in signals:
            if s.signal_type == "repo_rate":
                if s.value > 7.5:
                    score -= 15
                    notes.append(f"High repo rate {s.value:.2f}%")
                elif s.value < 5.5:
                    score += 5
        return {"score": max(0.0, min(score, 100.0)), "notes": notes}

    def _collect_flags(
        self,
        rera_records: list[RERARecord],
        developer: Optional[DeveloperRecord],
    ) -> list[str]:
        flags = []
        for r in rera_records:
            from api.schemas import RERAStatus
            if r.rera_status == RERAStatus.REVOKED:
                flags.append(f"RERA_REVOKED:{r.project_name}")
            if r.possession_delay_days and r.possession_delay_days > 730:
                flags.append(f"EXTREME_DELAY:{r.project_name}:{r.possession_delay_days}d")
        if developer and developer.delayed_projects and developer.total_projects:
            if developer.delayed_projects / developer.total_projects > 0.5:
                flags.append(f"DEVELOPER_HIGH_DELAY_RATE:{developer.name}")
        return flags
