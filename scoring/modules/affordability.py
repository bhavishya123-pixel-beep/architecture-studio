"""
Affordability Score
────────────────────
Measures how accessible the market is to target buyer segments.
Higher score = more affordable relative to segment benchmarks.
"""

from __future__ import annotations

from api.schemas import MarketPriceRecord, ScoreBreakdown
from config.settings import get_settings

settings = get_settings()

# City-level rough price benchmarks (₹/sqft) for scoring
# Source: approximations from NHB/RBI housing price indices
CITY_BENCHMARKS: dict[str, dict] = {
    "mumbai":     {"affordable": 8000, "mid": 15000, "premium": 30000},
    "delhi":      {"affordable": 6000, "mid": 12000, "premium": 25000},
    "bengaluru":  {"affordable": 5000, "mid": 9000,  "premium": 18000},
    "hyderabad":  {"affordable": 4500, "mid": 8000,  "premium": 16000},
    "pune":       {"affordable": 5000, "mid": 9000,  "premium": 17000},
    "chennai":    {"affordable": 4500, "mid": 8500,  "premium": 16000},
    "kolkata":    {"affordable": 4000, "mid": 7000,  "premium": 14000},
    "ahmedabad":  {"affordable": 3500, "mid": 6500,  "premium": 13000},
    "default":    {"affordable": 4000, "mid": 8000,  "premium": 16000},
}


def compute_affordability_score(
    price_records: list[MarketPriceRecord],
) -> ScoreBreakdown:
    w = settings.score_weights["affordability"]

    if not price_records:
        return ScoreBreakdown(
            raw_value=0.0, normalized_score=50.0, weight=w,
            weighted_contribution=50.0 * w,
            explanation="No price data. Neutral affordability assumed.",
            data_gap=True, confidence=0.0,
        )

    scores = []
    lines = []
    evidence_ids = []

    for r in price_records:
        evidence_ids.append(r.id)
        if r.price_per_sqft is None:
            continue

        city_key = r.city.lower()
        bm = CITY_BENCHMARKS.get(city_key, CITY_BENCHMARKS["default"])
        price = r.price_per_sqft
        segment = r.segment

        if segment in ("affordable", "mid_income"):
            threshold = bm["affordable"] if segment == "affordable" else bm["mid"]
            ratio = price / threshold
            if ratio <= 0.8:
                s = 90.0
                lines.append(f"{r.locality}: ₹{price:.0f}/sqft well below {segment} threshold (+90)")
            elif ratio <= 1.0:
                s = 75.0
            elif ratio <= 1.2:
                s = 55.0
            elif ratio <= 1.5:
                s = 35.0
            else:
                s = 15.0
                lines.append(f"{r.locality}: ₹{price:.0f}/sqft significantly above benchmark (-)")
        else:
            # Premium/luxury: affordability metric less relevant; score neutrally
            s = 50.0

        scores.append(s * r.confidence * r.freshness_score)

    if not scores:
        return ScoreBreakdown(
            raw_value=0.0, normalized_score=50.0, weight=w,
            weighted_contribution=50.0 * w,
            explanation="Price data present but not usable for affordability.",
            evidence_ids=evidence_ids, data_gap=True, confidence=0.3,
        )

    normalized = round(sum(scores) / len(scores), 2)
    avg_conf = sum(r.confidence for r in price_records) / len(price_records)

    return ScoreBreakdown(
        raw_value=normalized,
        normalized_score=min(normalized, 100.0),
        weight=w,
        weighted_contribution=round(normalized * w, 4),
        explanation="Affordability: " + " | ".join(lines[:4]) or "Within benchmark range.",
        evidence_ids=evidence_ids,
        data_gap=False,
        confidence=round(avg_conf, 3),
    )
