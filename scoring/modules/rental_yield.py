"""
Rental Yield Score
───────────────────
Normalizes gross and net rental yield relative to Indian market benchmarks.
Also accounts for absorption velocity (demand signal) and price momentum.

Score: 0–100
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from api.schemas import MarketPriceRecord, ScoreBreakdown
from config.settings import get_settings

settings = get_settings()

# Indian residential yield benchmarks (gross %)
YIELD_BENCHMARKS = {
    "luxury":     {"floor": 1.0, "median": 2.0, "ceiling": 3.5},
    "premium":    {"floor": 1.5, "median": 2.5, "ceiling": 4.0},
    "mid_income": {"floor": 2.0, "median": 3.0, "ceiling": 5.0},
    "affordable": {"floor": 2.5, "median": 3.5, "ceiling": 6.0},
}

DEFAULT_BENCHMARK = {"floor": 1.5, "median": 2.8, "ceiling": 5.0}


def _yield_score(gross_yield: float, segment: str) -> float:
    """Map gross yield to 0–100 score against segment benchmarks."""
    bm = YIELD_BENCHMARKS.get(segment, DEFAULT_BENCHMARK)
    floor, median, ceiling = bm["floor"], bm["median"], bm["ceiling"]

    if gross_yield <= floor:
        return max(0.0, (gross_yield / floor) * 30.0)
    elif gross_yield <= median:
        return 30.0 + ((gross_yield - floor) / (median - floor)) * 40.0
    elif gross_yield <= ceiling:
        return 70.0 + ((gross_yield - median) / (ceiling - median)) * 25.0
    else:
        # Above ceiling: check for outliers — could be genuine or data error
        return 95.0


def compute_rental_yield_score(
    price_records: list[MarketPriceRecord],
) -> ScoreBreakdown:
    if not price_records:
        return ScoreBreakdown(
            raw_value=0.0,
            normalized_score=0.0,
            weight=settings.score_weights["rental_yield"],
            weighted_contribution=0.0,
            explanation="No market price records available.",
            data_gap=True,
            confidence=0.0,
        )

    yield_scores: list[float] = []
    evidence_ids: list[UUID] = []
    lines: list[str] = []
    total_conf = 0.0

    for r in price_records:
        if r.gross_yield_pct is None:
            continue
        s = _yield_score(r.gross_yield_pct, r.segment)
        yield_scores.append(s * r.confidence * r.freshness_score)
        evidence_ids.append(r.id)
        total_conf += r.confidence
        lines.append(
            f"{r.locality} ({r.segment}): gross={r.gross_yield_pct:.2f}% → score={s:.1f}"
        )

    # Absorption bonus: high absorption = strong demand = yield support
    absorption_bonus = 0.0
    for r in price_records:
        if r.absorption_rate_pct is not None and r.absorption_rate_pct > 60:
            absorption_bonus = min(absorption_bonus + 5.0, 10.0)
            lines.append(f"Absorption {r.absorption_rate_pct:.0f}% (+bonus)")

    if not yield_scores:
        return ScoreBreakdown(
            raw_value=0.0,
            normalized_score=0.0,
            weight=settings.score_weights["rental_yield"],
            weighted_contribution=0.0,
            explanation="Yield data missing in all records.",
            evidence_ids=evidence_ids,
            data_gap=True,
            confidence=0.0,
        )

    raw = sum(yield_scores) / len(yield_scores)
    normalized = min(round(raw + absorption_bonus, 2), 100.0)
    avg_conf = total_conf / len(price_records)
    w = settings.score_weights["rental_yield"]

    return ScoreBreakdown(
        raw_value=round(raw, 4),
        normalized_score=normalized,
        weight=w,
        weighted_contribution=round(normalized * w, 4),
        explanation="Rental yield: " + " | ".join(lines[:5]),
        evidence_ids=evidence_ids,
        data_gap=False,
        confidence=round(avg_conf, 3),
    )
