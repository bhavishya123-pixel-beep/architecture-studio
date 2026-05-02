"""
Scoring Engine
───────────────
Orchestrates all scoring modules to produce a LocationScoreCard.
This is purely deterministic Python — no LLM calls here.
"""

from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from api.schemas import (
    LocationScoreCard, InfraProximity, RERARecord,
    MarketPriceRecord, MacroSignalRecord, DeveloperRecord, GeoPoint,
)
from config.settings import get_settings
from scoring.modules.infrastructure_uplift import compute_infra_uplift_score
from scoring.modules.connectivity import compute_connectivity_score
from scoring.modules.affordability import compute_affordability_score
from scoring.modules.rental_yield import compute_rental_yield_score
from scoring.modules.liquidity import compute_liquidity_score
from scoring.modules.regulatory_safety import compute_regulatory_safety_score
from scoring.modules.developer_trust import compute_developer_trust_score
from scoring.modules.execution_risk import compute_execution_risk_score
from scoring.modules.appreciation_potential import compute_appreciation_score

logger = logging.getLogger(__name__)
settings = get_settings()


def build_location_scorecard(
    city: str,
    state: str,
    locality: str,
    pin_code: Optional[str] = None,
    geo_point: Optional[GeoPoint] = None,
    proximal_infra: Optional[list[InfraProximity]] = None,
    rera_records: Optional[list[RERARecord]] = None,
    price_records: Optional[list[MarketPriceRecord]] = None,
    macro_signals: Optional[list[MacroSignalRecord]] = None,
    developer: Optional[DeveloperRecord] = None,
    developer_rera: Optional[list[RERARecord]] = None,
) -> LocationScoreCard:
    """
    Build a complete LocationScoreCard for a given location.
    Missing data is handled gracefully: scores with data_gap=True
    are excluded from the weighted final score.
    """
    proximal_infra = proximal_infra or []
    rera_records = rera_records or []
    price_records = price_records or []
    macro_signals = macro_signals or []
    developer_rera = developer_rera or []

    card = LocationScoreCard(
        city=city,
        state=state,
        locality=locality,
        pin_code=pin_code,
        geo_point=geo_point,
    )

    # ── Score each dimension ──────────────────────────────────────────────────
    try:
        card.infrastructure_uplift = compute_infra_uplift_score(proximal_infra)
    except Exception as e:
        logger.error(f"InfraUplift score failed: {e}")

    try:
        card.connectivity = compute_connectivity_score(proximal_infra)
    except Exception as e:
        logger.error(f"Connectivity score failed: {e}")

    try:
        card.affordability = compute_affordability_score(price_records)
    except Exception as e:
        logger.error(f"Affordability score failed: {e}")

    try:
        card.rental_yield = compute_rental_yield_score(price_records)
    except Exception as e:
        logger.error(f"RentalYield score failed: {e}")

    try:
        card.liquidity = compute_liquidity_score(price_records)
    except Exception as e:
        logger.error(f"Liquidity score failed: {e}")

    try:
        card.regulatory_safety = compute_regulatory_safety_score(rera_records)
    except Exception as e:
        logger.error(f"RegSafety score failed: {e}")

    try:
        card.developer_trust = compute_developer_trust_score(developer, developer_rera)
    except Exception as e:
        logger.error(f"DevTrust score failed: {e}")

    try:
        card.execution_risk = compute_execution_risk_score(rera_records, developer)
    except Exception as e:
        logger.error(f"ExecRisk score failed: {e}")

    try:
        card.appreciation_potential = compute_appreciation_score(
            price_records, macro_signals, proximal_infra
        )
    except Exception as e:
        logger.error(f"AppreciationPotential score failed: {e}")

    # ── Compute final weighted score ──────────────────────────────────────────
    card.compute_final(settings.score_weights)

    logger.info(
        f"ScoreCard: {city}/{locality} → final={card.final_score}, "
        f"completeness={card.data_completeness_pct}%, "
        f"human_review={card.human_review_required}"
    )
    return card
