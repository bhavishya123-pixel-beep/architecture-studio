"""
Execution Risk Score
─────────────────────
Estimates the probability of project non-delivery, delay, or quality failure.
Lower score = higher risk. Score: 0–100 (100 = safest).

Inverted from penalty model: start at 100, deduct for risk signals.
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from api.schemas import RERARecord, DeveloperRecord, RERAStatus, ScoreBreakdown
from config.settings import get_settings

settings = get_settings()


def compute_execution_risk_score(
    rera_records: list[RERARecord],
    developer: Optional[DeveloperRecord] = None,
) -> ScoreBreakdown:
    w = settings.score_weights["execution_risk"]

    if not rera_records and developer is None:
        return ScoreBreakdown(
            raw_value=50.0, normalized_score=50.0, weight=w,
            weighted_contribution=50.0 * w,
            explanation="Insufficient data for execution risk. Neutral assigned.",
            data_gap=True, confidence=0.2,
        )

    penalty = 0.0
    lines: list[str] = []
    evidence_ids: list[UUID] = []

    for r in rera_records:
        evidence_ids.append(r.id)

        if r.rera_status == RERAStatus.REVOKED:
            penalty += 50.0
            lines.append(f"{r.project_name}: RERA revoked (-50)")
            continue

        if r.rera_status == RERAStatus.EXPIRED:
            penalty += 20.0
            lines.append(f"{r.project_name}: RERA expired (-20)")

        if r.possession_delay_days:
            d = r.possession_delay_days
            if d > 1095:   # 3yr
                penalty += 30.0
                lines.append(f"Delay {d}d >3yr (-30)")
            elif d > 730:
                penalty += 20.0
                lines.append(f"Delay {d}d >2yr (-20)")
            elif d > 365:
                penalty += 12.0
            elif d > 180:
                penalty += 5.0

        if r.total_units and r.units_sold:
            sold_ratio = r.units_sold / r.total_units
            if sold_ratio < 0.20 and r.rera_status == RERAStatus.REGISTERED:
                penalty += 10.0
                lines.append(f"Low sales absorption {sold_ratio:.0%} (-10)")

    if developer:
        evidence_ids.append(developer.id)
        if developer.delayed_projects and developer.total_projects:
            delay_ratio = developer.delayed_projects / developer.total_projects
            if delay_ratio > 0.5:
                penalty += 20.0
                lines.append(f"Developer: {delay_ratio:.0%} projects delayed (-20)")
            elif delay_ratio > 0.3:
                penalty += 10.0

    score = max(0.0, min(100.0 - penalty, 100.0))
    avg_conf = (
        sum(r.confidence for r in rera_records) / len(rera_records)
        if rera_records else 0.5
    )

    return ScoreBreakdown(
        raw_value=score,
        normalized_score=round(score, 2),
        weight=w,
        weighted_contribution=round(score * w, 4),
        explanation="Execution risk: " + "; ".join(lines[:5]) or "No critical risk flags.",
        evidence_ids=evidence_ids,
        data_gap=False,
        confidence=round(avg_conf, 3),
    )
