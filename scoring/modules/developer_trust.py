"""
Developer Trust Score
──────────────────────
Rates a developer based on RERA compliance track record,
on-time delivery rate, complaint intensity, and project completion ratios.

Score: 0–100
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from api.schemas import DeveloperRecord, RERARecord, ScoreBreakdown
from config.settings import get_settings

settings = get_settings()


def compute_developer_trust_score(
    developer: Optional[DeveloperRecord],
    developer_rera_projects: list[RERARecord],
) -> ScoreBreakdown:
    w = settings.score_weights["developer_trust"]

    if developer is None and not developer_rera_projects:
        return ScoreBreakdown(
            raw_value=50.0,
            normalized_score=50.0,
            weight=w,
            weighted_contribution=50.0 * w,
            explanation="No developer history data. Neutral score assigned.",
            data_gap=True,
            confidence=0.3,
        )

    score = 60.0  # start at neutral-positive
    lines: list[str] = []
    evidence_ids: list[UUID] = []
    conf = 0.6

    if developer:
        evidence_ids.append(developer.id)
        conf = developer.confidence

        # On-time delivery rate
        if developer.on_time_delivery_rate_pct is not None:
            otr = developer.on_time_delivery_rate_pct
            if otr >= 90:
                score += 20.0
                lines.append(f"OTD rate {otr:.0f}% (+20)")
            elif otr >= 70:
                score += 10.0
                lines.append(f"OTD rate {otr:.0f}% (+10)")
            elif otr >= 50:
                score += 0.0
            else:
                score -= 20.0
                lines.append(f"OTD rate {otr:.0f}% (-20)")

        # Avg possession delay
        if developer.avg_possession_delay_days is not None:
            d = developer.avg_possession_delay_days
            if d > 730:
                score -= 25.0
                lines.append(f"Avg delay {d:.0f}d (>2yr) (-25)")
            elif d > 365:
                score -= 15.0
                lines.append(f"Avg delay {d:.0f}d (-15)")
            elif d > 180:
                score -= 5.0

        # Project completion ratio
        if developer.completed_projects and developer.total_projects:
            ratio = developer.completed_projects / developer.total_projects
            if ratio >= 0.80:
                score += 10.0
                lines.append(f"Completion ratio {ratio:.0%} (+10)")
            elif ratio < 0.40:
                score -= 15.0
                lines.append(f"Completion ratio {ratio:.0%} (-15)")

        # RERA complaint density
        if developer.rera_complaints_total and developer.total_projects:
            cpd = developer.rera_complaints_total / developer.total_projects
            if cpd > 50:
                score -= 20.0
                lines.append(f"Complaints/project={cpd:.0f} (-20)")
            elif cpd > 20:
                score -= 10.0
            elif cpd < 5:
                score += 5.0
                lines.append(f"Low complaints ({cpd:.0f}/proj) (+5)")

    # Cross-check with individual RERA records
    for r in developer_rera_projects:
        evidence_ids.append(r.id)
        if r.possession_delay_days and r.possession_delay_days > 365:
            score -= 3.0

    score = max(0.0, min(score, 100.0))

    return ScoreBreakdown(
        raw_value=score,
        normalized_score=round(score, 2),
        weight=w,
        weighted_contribution=round(score * w, 4),
        explanation="Developer trust: " + "; ".join(lines[:5]),
        evidence_ids=evidence_ids,
        data_gap=developer is None,
        confidence=round(conf, 3),
    )
