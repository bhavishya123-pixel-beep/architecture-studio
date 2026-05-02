"""
Liquidity Score
────────────────
Measures how easily an asset can be sold. Based on:
- Absorption rate (velocity of sales in the micro-market)
- Days on market
- Inventory months outstanding
- Transaction volume trend
- Asset type and price ticket

Score: 0–100
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from api.schemas import MarketPriceRecord, ScoreBreakdown
from config.settings import get_settings

settings = get_settings()


def compute_liquidity_score(
    price_records: list[MarketPriceRecord],
) -> ScoreBreakdown:
    if not price_records:
        return ScoreBreakdown(
            raw_value=0.0,
            normalized_score=0.0,
            weight=settings.score_weights["liquidity"],
            weighted_contribution=0.0,
            explanation="No market data; liquidity cannot be estimated.",
            data_gap=True,
            confidence=0.0,
        )

    scores: list[float] = []
    evidence_ids: list[UUID] = []
    lines: list[str] = []
    total_conf = 0.0

    for r in price_records:
        s = 50.0  # neutral base
        evidence_ids.append(r.id)
        total_conf += r.confidence

        # Absorption rate signal (0–100%)
        if r.absorption_rate_pct is not None:
            if r.absorption_rate_pct >= 80:
                s += 25.0
                lines.append(f"Absorption {r.absorption_rate_pct:.0f}% (+25)")
            elif r.absorption_rate_pct >= 60:
                s += 15.0
            elif r.absorption_rate_pct >= 40:
                s += 5.0
            elif r.absorption_rate_pct < 20:
                s -= 15.0
                lines.append(f"Low absorption {r.absorption_rate_pct:.0f}% (-15)")

        # Days on market
        if r.days_on_market is not None:
            if r.days_on_market < 30:
                s += 15.0
                lines.append(f"DOM={r.days_on_market:.0f}d (+15)")
            elif r.days_on_market < 90:
                s += 5.0
            elif r.days_on_market > 180:
                s -= 20.0
                lines.append(f"DOM={r.days_on_market:.0f}d (-20)")

        # Unsold inventory overhang
        if r.unsold_inventory_months is not None:
            if r.unsold_inventory_months < 6:
                s += 10.0
            elif r.unsold_inventory_months < 12:
                s += 0.0
            elif r.unsold_inventory_months > 24:
                s -= 20.0
                lines.append(f"Inventory={r.unsold_inventory_months:.0f}mo (-20)")
            elif r.unsold_inventory_months > 18:
                s -= 10.0

        s = max(0.0, min(s, 100.0))
        scores.append(s * r.confidence * r.freshness_score)

    normalized = round(sum(scores) / len(scores), 2) if scores else 0.0
    avg_conf = total_conf / len(price_records)
    w = settings.score_weights["liquidity"]

    return ScoreBreakdown(
        raw_value=normalized,
        normalized_score=min(normalized, 100.0),
        weight=w,
        weighted_contribution=round(normalized * w, 4),
        explanation="Liquidity: " + " | ".join(lines[:5]) or "Moderate market depth estimated.",
        evidence_ids=evidence_ids,
        data_gap=False,
        confidence=round(avg_conf, 3),
    )
