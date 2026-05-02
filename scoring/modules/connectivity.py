"""
Connectivity Score
───────────────────
Measures current and future road/transit accessibility.
Inputs: proximal infra + optional travel-time data.

Score: 0–100
"""

from __future__ import annotations

from api.schemas import InfraProximity, InfraType, InfraStatus, ScoreBreakdown
from config.settings import get_settings

settings = get_settings()

CONNECTIVITY_TYPE_WEIGHT = {
    InfraType.METRO: 1.0,
    InfraType.HIGHWAY: 0.80,
    InfraType.EXPRESSWAY: 0.90,
    InfraType.RING_ROAD: 0.75,
    InfraType.BYPASS: 0.65,
    InfraType.RAILWAY: 0.70,
    InfraType.AIRPORT: 0.60,
    InfraType.FREIGHT_CORRIDOR: 0.40,
}


def compute_connectivity_score(
    proximal_infra: list[InfraProximity],
) -> ScoreBreakdown:
    w = settings.score_weights["connectivity"]

    if not proximal_infra:
        return ScoreBreakdown(
            raw_value=0.0, normalized_score=10.0, weight=w,
            weighted_contribution=10.0 * w,
            explanation="No infrastructure proximity data. Minimal connectivity assumed.",
            data_gap=True, confidence=0.2,
        )

    # Connectivity = sum of operational + near-operational infra reachability
    conn_score = 0.0
    lines = []
    evidence_ids = []

    for prox in proximal_infra:
        tw = CONNECTIVITY_TYPE_WEIGHT.get(prox.infra_type, 0.5)

        # Operational infra: contributes full connectivity
        if prox.infra_status == InfraStatus.OPERATIONAL:
            dist_factor = max(0.0, 1.0 - prox.distance_km / 15.0)
            contribution = tw * dist_factor * 20.0
            conn_score += contribution
            if contribution > 5:
                lines.append(
                    f"{prox.infra_name} (operational, {prox.distance_km:.1f}km) +{contribution:.1f}"
                )

        # Under construction: partial connectivity credit
        elif prox.infra_status == InfraStatus.UNDER_CONSTRUCTION:
            dist_factor = max(0.0, 1.0 - prox.distance_km / 20.0)
            contribution = tw * dist_factor * 10.0
            conn_score += contribution

        evidence_ids.append(prox.infra_id)

    # Travel time improvement bonus
    for prox in proximal_infra:
        if prox.travel_time_current_min and prox.travel_time_post_infra_min:
            improvement_pct = (
                (prox.travel_time_current_min - prox.travel_time_post_infra_min)
                / prox.travel_time_current_min * 100
            )
            if improvement_pct > 40:
                conn_score += 10.0
                lines.append(f"Travel-time cut {improvement_pct:.0f}% (+10)")
            elif improvement_pct > 20:
                conn_score += 5.0

    normalized = min(round(conn_score, 2), 100.0)

    return ScoreBreakdown(
        raw_value=conn_score,
        normalized_score=normalized,
        weight=w,
        weighted_contribution=round(normalized * w, 4),
        explanation="Connectivity: " + " | ".join(lines[:5]),
        evidence_ids=evidence_ids,
        data_gap=False,
        confidence=0.75,
    )
