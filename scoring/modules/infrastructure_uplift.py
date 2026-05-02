"""
Infrastructure Uplift Score
────────────────────────────
Measures the degree to which a location is expected to benefit from
planned or under-construction infrastructure.

Deterministic computation — no LLM involvement.

Score: 0–100
"""

from __future__ import annotations

import math
from typing import Optional
from uuid import UUID

from api.schemas import (
    InfraProximity, InfraStatus, InfraType, ScoreBreakdown,
)
from config.settings import get_settings

settings = get_settings()

# How much weight each infra type carries for real-estate uplift
INFRA_TYPE_WEIGHTS: dict[InfraType, float] = {
    InfraType.METRO: 1.0,
    InfraType.EXPRESSWAY: 0.95,
    InfraType.HIGHWAY: 0.85,
    InfraType.RING_ROAD: 0.80,
    InfraType.BYPASS: 0.70,
    InfraType.AIRPORT: 0.90,
    InfraType.FREIGHT_CORRIDOR: 0.65,
    InfraType.INDUSTRIAL_CORRIDOR: 0.75,
    InfraType.LOGISTICS_PARK: 0.55,
    InfraType.RAILWAY: 0.60,
    InfraType.SEZ: 0.65,
    InfraType.SMART_CITY: 0.50,
    InfraType.PORT: 0.55,
    InfraType.DATA_CENTER_ZONE: 0.45,
}

# Status multiplier: how certain/near is the benefit?
STATUS_MULTIPLIERS: dict[InfraStatus, float] = {
    InfraStatus.OPERATIONAL: 0.60,        # already priced in, less future uplift
    InfraStatus.UNDER_CONSTRUCTION: 1.00, # highest uplift: near-term certainty
    InfraStatus.TENDERED: 0.85,
    InfraStatus.APPROVED: 0.70,
    InfraStatus.ANNOUNCED: 0.45,          # uncertain; might not materialize
    InfraStatus.STALLED: 0.15,
    InfraStatus.CANCELLED: 0.0,
}

# Distance decay: closer = more uplift
def _distance_decay(distance_km: float, infra_type: InfraType) -> float:
    """Sigmoid-based decay. Metro has tighter catchment than highway."""
    if infra_type == InfraType.METRO:
        # Metro: 90% uplift at 0.5 km, 50% at 1 km, 10% at 3 km
        scale = 1.5
    elif infra_type == InfraType.AIRPORT:
        # Airport: large influence zone
        scale = 8.0
    else:
        scale = 4.0
    return math.exp(-distance_km / scale)


def compute_infra_uplift_score(
    proximal_infra: list[InfraProximity],
    location_id: Optional[UUID] = None,
) -> ScoreBreakdown:
    """
    Args:
        proximal_infra: list of InfraProximity records for the target location
        location_id: optional ID for evidence linking
    Returns:
        ScoreBreakdown with normalized_score [0,100]
    """
    if not proximal_infra:
        return ScoreBreakdown(
            raw_value=0.0,
            normalized_score=0.0,
            weight=settings.score_weights["infrastructure_uplift"],
            weighted_contribution=0.0,
            explanation="No proximal infrastructure records found.",
            evidence_ids=[],
            data_gap=True,
            confidence=0.0,
        )

    # Accumulate uplift signal across all nearby infra
    total_signal = 0.0
    max_possible = 0.0
    evidence_ids: list[UUID] = []
    breakdown_lines: list[str] = []
    total_confidence = 0.0

    for prox in proximal_infra:
        type_w = INFRA_TYPE_WEIGHTS.get(prox.infra_type, 0.5)
        status_m = STATUS_MULTIPLIERS.get(prox.infra_status, 0.5)
        dist_decay = _distance_decay(prox.distance_km, prox.infra_type)

        signal = type_w * status_m * dist_decay * prox.uplift_weight
        max_signal = type_w * 1.0 * 1.0 * prox.uplift_weight

        total_signal += signal
        max_possible += max_signal
        evidence_ids.append(prox.infra_id)
        total_confidence += prox.uplift_weight

        breakdown_lines.append(
            f"{prox.infra_name} ({prox.infra_type.value}, "
            f"{prox.infra_status.value}, {prox.distance_km:.1f} km) "
            f"→ signal={signal:.3f}"
        )

    # Normalize to 0–100; cap at 100 even if clustered infra > 1
    if max_possible > 0:
        raw_ratio = min(total_signal / max_possible, 1.0)
    else:
        raw_ratio = 0.0

    normalized = round(raw_ratio * 100, 2)
    avg_confidence = total_confidence / len(proximal_infra) if proximal_infra else 0.0

    explanation = (
        f"Infra uplift from {len(proximal_infra)} nearby projects. "
        + " | ".join(breakdown_lines[:5])  # top 5 for readability
    )

    w = settings.score_weights["infrastructure_uplift"]
    return ScoreBreakdown(
        raw_value=round(total_signal, 4),
        normalized_score=normalized,
        weight=w,
        weighted_contribution=round(normalized * w, 4),
        explanation=explanation,
        evidence_ids=evidence_ids,
        data_gap=False,
        confidence=round(min(avg_confidence, 1.0), 3),
    )
