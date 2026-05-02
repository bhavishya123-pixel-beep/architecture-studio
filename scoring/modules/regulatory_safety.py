"""
Regulatory Safety Score
────────────────────────
Evaluates legal and compliance risk for a project/location based on
RERA status, complaint history, possession delays, and approvals.

Score: 0 (maximum risk) → 100 (clean/safe)
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from api.schemas import RERARecord, RERAStatus, ScoreBreakdown
from config.settings import get_settings

settings = get_settings()


def compute_regulatory_safety_score(
    rera_records: list[RERARecord],
) -> ScoreBreakdown:
    if not rera_records:
        return ScoreBreakdown(
            raw_value=0.0,
            normalized_score=50.0,  # neutral: no data, not penalized but not rewarded
            weight=settings.score_weights["regulatory_safety"],
            weighted_contribution=50.0 * settings.score_weights["regulatory_safety"],
            explanation="No RERA records found. Score is neutral pending data.",
            data_gap=True,
            confidence=0.0,
        )

    penalty = 0.0
    bonus = 0.0
    evidence_ids: list[UUID] = []
    lines: list[str] = []
    total_conf = 0.0

    for r in rera_records:
        evidence_ids.append(r.id)
        total_conf += r.confidence

        # RERA status
        if r.rera_status == RERAStatus.REVOKED:
            penalty += 40.0
            lines.append(f"{r.project_name}: RERA REVOKED (-40)")
        elif r.rera_status == RERAStatus.EXPIRED:
            penalty += 20.0
            lines.append(f"{r.project_name}: RERA expired (-20)")
        elif r.rera_status == RERAStatus.REGISTERED:
            bonus += 15.0
            lines.append(f"{r.project_name}: RERA registered (+15)")
        elif r.rera_status == RERAStatus.UNKNOWN:
            penalty += 10.0
            lines.append(f"{r.project_name}: RERA status unknown (-10)")

        # Possession delay
        if r.possession_delay_days:
            delay = r.possession_delay_days
            if delay > 730:
                penalty += 25.0
                lines.append(f"  Possession delay {delay}d (>2yr) (-25)")
            elif delay > 365:
                penalty += 15.0
                lines.append(f"  Possession delay {delay}d (>1yr) (-15)")
            elif delay > 180:
                penalty += 8.0
                lines.append(f"  Possession delay {delay}d (>6mo) (-8)")
            elif delay > 0:
                penalty += 3.0
                lines.append(f"  Possession delay {delay}d (-3)")

        # Complaint intensity
        if r.complaint_count and r.total_units:
            complaint_rate = r.complaint_count / max(r.total_units, 1)
            if complaint_rate > 0.20:
                penalty += 20.0
                lines.append(f"  Complaint rate {complaint_rate:.1%} (>20%) (-20)")
            elif complaint_rate > 0.10:
                penalty += 10.0
                lines.append(f"  Complaint rate {complaint_rate:.1%} (-10)")
            elif complaint_rate > 0.05:
                penalty += 5.0
                lines.append(f"  Complaint rate {complaint_rate:.1%} (-5)")

        # Active complaints
        if r.active_complaints and r.active_complaints > 0:
            penalty += min(r.active_complaints * 2, 20)
            lines.append(f"  Active complaints: {r.active_complaints}")

    # Base score = 100 - net_penalty + min(bonus, 20)
    net_penalty = min(penalty, 95.0)
    raw = max(0.0, 100.0 - net_penalty + min(bonus, 20.0))
    normalized = min(round(raw, 2), 100.0)

    avg_conf = total_conf / len(rera_records)
    w = settings.score_weights["regulatory_safety"]

    return ScoreBreakdown(
        raw_value=raw,
        normalized_score=normalized,
        weight=w,
        weighted_contribution=round(normalized * w, 4),
        explanation="Regulatory safety: " + "; ".join(lines[:8]),
        evidence_ids=evidence_ids,
        data_gap=False,
        confidence=round(avg_conf, 3),
    )
