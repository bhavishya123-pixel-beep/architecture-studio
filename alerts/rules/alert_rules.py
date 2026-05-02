"""
Alert Rules Engine
───────────────────
Evaluates incoming data against defined alert conditions.
Each rule is a pure function: (data) → Alert | None.

Rules are composable and independently testable.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from api.schemas import (
    Alert, AlertType, AlertSeverity,
    MarketPriceRecord, RERARecord, MacroSignalRecord,
    InfrastructureRecord, InfraStatus,
)


def check_possession_slip(
    current: RERARecord,
    previous: Optional[RERARecord],
) -> Optional[Alert]:
    if previous is None:
        return None
    if (
        current.promised_possession_date
        and previous.promised_possession_date
        and current.promised_possession_date > previous.promised_possession_date
    ):
        slip_days = (current.promised_possession_date - previous.promised_possession_date).days
        severity = AlertSeverity.HIGH if slip_days > 180 else AlertSeverity.MEDIUM
        return Alert(
            alert_type=AlertType.POSSESSION_SLIP,
            severity=severity,
            title=f"Possession slipped: {current.project_name}",
            body=(
                f"{current.project_name} ({current.developer_name}) possession date "
                f"pushed by {slip_days} days. "
                f"New date: {current.promised_possession_date}. "
                f"RERA: {current.rera_registration_number}. "
                f"City: {current.city}."
            ),
            location=current.locality,
            city=current.city,
            evidence_ids=[current.id],
            source_ids=[current.source_id],
            data={"slip_days": slip_days},
        )
    return None


def check_rera_status_change(
    current: RERARecord,
    previous: Optional[RERARecord],
) -> Optional[Alert]:
    if previous is None or current.rera_status == previous.rera_status:
        return None
    from api.schemas import RERAStatus
    if current.rera_status == RERAStatus.REVOKED:
        return Alert(
            alert_type=AlertType.RERA_CHANGE,
            severity=AlertSeverity.HIGH,
            title=f"RERA REVOKED: {current.project_name}",
            body=(
                f"RERA registration for {current.project_name} ({current.city}) has been revoked. "
                f"RERA number: {current.rera_registration_number}. "
                f"Developer: {current.developer_name}. Immediate review required."
            ),
            location=current.locality,
            city=current.city,
            evidence_ids=[current.id],
            source_ids=[current.source_id],
        )
    return Alert(
        alert_type=AlertType.RERA_CHANGE,
        severity=AlertSeverity.MEDIUM,
        title=f"RERA status change: {current.project_name}",
        body=(
            f"RERA status changed: {previous.rera_status.value} → {current.rera_status.value}. "
            f"Project: {current.project_name}, City: {current.city}."
        ),
        city=current.city,
        evidence_ids=[current.id],
        source_ids=[current.source_id],
    )


def check_price_spike(
    current: MarketPriceRecord,
    previous: Optional[MarketPriceRecord],
    spike_threshold_pct: float = 15.0,
) -> Optional[Alert]:
    if previous is None or not current.price_per_sqft or not previous.price_per_sqft:
        return None
    change_pct = (current.price_per_sqft - previous.price_per_sqft) / previous.price_per_sqft * 100
    if abs(change_pct) >= spike_threshold_pct:
        direction = "spike" if change_pct > 0 else "drop"
        return Alert(
            alert_type=AlertType.PRICE_SPIKE,
            severity=AlertSeverity.HIGH if abs(change_pct) > 25 else AlertSeverity.MEDIUM,
            title=f"Price {direction}: {current.locality}, {current.city}",
            body=(
                f"Price {direction} of {change_pct:+.1f}% detected in {current.locality}. "
                f"Current: ₹{current.price_per_sqft:.0f}/sqft. "
                f"Previous: ₹{previous.price_per_sqft:.0f}/sqft. "
                f"Verify source before acting."
            ),
            location=current.locality,
            city=current.city,
            evidence_ids=[current.id],
            source_ids=[current.source_id],
            data={"change_pct": round(change_pct, 2)},
        )
    return None


def check_yield_compression(
    current: MarketPriceRecord,
    previous: Optional[MarketPriceRecord],
    compression_threshold_pct: float = 0.5,
) -> Optional[Alert]:
    if previous is None or not current.gross_yield_pct or not previous.gross_yield_pct:
        return None
    delta = current.gross_yield_pct - previous.gross_yield_pct
    if delta < -compression_threshold_pct:
        return Alert(
            alert_type=AlertType.YIELD_COMPRESSION,
            severity=AlertSeverity.MEDIUM,
            title=f"Yield compressed: {current.locality}",
            body=(
                f"Gross yield in {current.locality} fell from "
                f"{previous.gross_yield_pct:.2f}% to {current.gross_yield_pct:.2f}%. "
                f"Price may have run ahead of rental growth."
            ),
            location=current.locality,
            city=current.city,
            evidence_ids=[current.id],
            source_ids=[current.source_id],
            data={"yield_delta": round(delta, 3)},
        )
    return None


def check_macro_rate_change(
    current: MacroSignalRecord,
    previous: Optional[MacroSignalRecord],
) -> Optional[Alert]:
    if current.signal_type != "repo_rate" or previous is None:
        return None
    if not previous.value:
        return None
    delta = current.value - previous.value
    if abs(delta) >= 0.25:
        direction = "cut" if delta < 0 else "hike"
        return Alert(
            alert_type=AlertType.MACRO_RATE_CHANGE,
            severity=AlertSeverity.HIGH,
            title=f"RBI repo rate {direction}: {current.value:.2f}%",
            body=(
                f"RBI repo rate {'cut' if delta < 0 else 'hiked'} by {abs(delta)*100:.0f} bps "
                f"to {current.value:.2f}%. Previous: {previous.value:.2f}%. "
                f"{'Mortgage affordability improves.' if delta < 0 else 'Mortgage costs rise; demand may soften.'}"
            ),
            evidence_ids=[current.id],
            source_ids=[current.source_id],
            data={"delta_pct": round(delta, 2)},
        )
    return None


def check_infra_execution_start(
    current: InfrastructureRecord,
    previous: Optional[InfrastructureRecord],
) -> Optional[Alert]:
    if previous is None:
        return None
    if (
        previous.status != InfraStatus.UNDER_CONSTRUCTION
        and current.status == InfraStatus.UNDER_CONSTRUCTION
    ):
        return Alert(
            alert_type=AlertType.INFRA_APPROVED,
            severity=AlertSeverity.HIGH,
            title=f"Construction started: {current.name}",
            body=(
                f"{current.infra_type.value.title()} '{current.name}' has entered construction phase. "
                f"State: {current.state}. "
                f"Expected completion: {current.expected_completion_date}. "
                f"Source: {current.source_id}."
            ),
            city=current.city,
            affected_infra_ids=[current.id],
            evidence_ids=[current.id],
            source_ids=[current.source_id],
        )
    return None


def check_launch_spike(
    current: MarketPriceRecord,
    previous: Optional[MarketPriceRecord],
    spike_multiplier: float = 2.0,
) -> Optional[Alert]:
    if (
        previous is None
        or not current.new_launches_units
        or not previous.new_launches_units
        or previous.new_launches_units == 0
    ):
        return None
    ratio = current.new_launches_units / previous.new_launches_units
    if ratio >= spike_multiplier:
        return Alert(
            alert_type=AlertType.LAUNCH_SPIKE,
            severity=AlertSeverity.MEDIUM,
            title=f"Launch spike: {current.locality}",
            body=(
                f"New launches in {current.locality} jumped {ratio:.1f}× "
                f"({previous.new_launches_units} → {current.new_launches_units} units). "
                f"Monitor for supply overhang."
            ),
            location=current.locality,
            city=current.city,
            evidence_ids=[current.id],
            source_ids=[current.source_id],
            data={"ratio": round(ratio, 2)},
        )
    return None
