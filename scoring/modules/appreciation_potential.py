"""
Appreciation Potential Score
──────────────────────────────
Combines price momentum, infrastructure pipeline timing,
macro tailwinds, and speculative premium detection.

Score: 0–100 (higher = more future appreciation expected)
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from api.schemas import (
    MarketPriceRecord, MacroSignalRecord, InfraProximity,
    InfraStatus, ScoreBreakdown,
)
from config.settings import get_settings

settings = get_settings()


def compute_appreciation_score(
    price_records: list[MarketPriceRecord],
    macro_signals: list[MacroSignalRecord],
    proximal_infra: list[InfraProximity],
) -> ScoreBreakdown:
    w = settings.score_weights["appreciation_potential"]

    if not price_records:
        return ScoreBreakdown(
            raw_value=0.0, normalized_score=0.0, weight=w,
            weighted_contribution=0.0,
            explanation="No price data available for appreciation estimate.",
            data_gap=True, confidence=0.0,
        )

    score = 50.0  # neutral baseline
    lines: list[str] = []
    evidence_ids: list[UUID] = []

    # 1. Price momentum signal
    for r in price_records:
        evidence_ids.append(r.id)
        if r.price_per_sqft_yoy_pct is not None:
            yoy = r.price_per_sqft_yoy_pct
            if yoy > 20:
                # Very high: check for speculative bubble
                score -= 5.0
                lines.append(f"YoY {yoy:.1f}% — speculative risk flag (-5)")
            elif yoy > 12:
                score += 10.0
                lines.append(f"YoY {yoy:.1f}% strong momentum (+10)")
            elif yoy > 7:
                score += 5.0
            elif yoy < 0:
                score -= 15.0
                lines.append(f"YoY {yoy:.1f}% price decline (-15)")
            elif yoy < 3:
                score -= 5.0

    # 2. Infrastructure pipeline timing — highest appreciation pre-completion
    for prox in proximal_infra:
        if prox.infra_status == InfraStatus.UNDER_CONSTRUCTION:
            score += 12.0
            lines.append(f"{prox.infra_name} under construction (+12)")
        elif prox.infra_status == InfraStatus.TENDERED:
            score += 6.0
        elif prox.infra_status == InfraStatus.APPROVED:
            score += 4.0

    # 3. Macro tailwinds
    for m in macro_signals:
        if m.signal_type == "repo_rate" and m.direction == "negative":
            # Rate cut → mortgage affordability improves → appreciation
            score += 8.0
            lines.append(f"Repo rate cut ({m.value:.2f}%) (+8)")
        elif m.signal_type == "repo_rate" and m.direction == "positive":
            score -= 5.0
        elif m.signal_type == "housing_cpi" and m.value > 6:
            score += 4.0
            lines.append(f"Housing CPI {m.value:.1f}% (+4)")
        elif m.signal_type == "credit_growth" and m.value > 15:
            score += 3.0

    score = max(0.0, min(score, 100.0))

    return ScoreBreakdown(
        raw_value=score,
        normalized_score=round(score, 2),
        weight=w,
        weighted_contribution=round(score * w, 4),
        explanation="Appreciation potential: " + " | ".join(lines[:5]),
        evidence_ids=evidence_ids,
        data_gap=False,
        confidence=0.65,
    )
