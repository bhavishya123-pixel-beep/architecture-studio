"""
Schema validation and data quality checks for all incoming records.
Returns a ValidationResult with pass/fail, warnings, and field-level issues.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Any, Optional
from uuid import UUID

from api.schemas import (
    InfrastructureRecord, RERARecord, MarketPriceRecord,
    DeveloperRecord, MacroSignalRecord,
)
from config.settings import get_settings


settings = get_settings()


@dataclass
class FieldIssue:
    field: str
    severity: str  # "error" | "warning"
    message: str


@dataclass
class ValidationResult:
    record_id: Optional[UUID]
    record_type: str
    passed: bool
    issues: list[FieldIssue] = field(default_factory=list)
    freshness_score: float = 1.0
    confidence_adjustment: float = 0.0  # subtract from raw confidence

    @property
    def errors(self) -> list[FieldIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[FieldIssue]:
        return [i for i in self.issues if i.severity == "warning"]


def _freshness(published_date: datetime) -> float:
    age_days = (datetime.utcnow() - published_date).days
    if age_days <= settings.freshness_green_days:
        return 1.0
    elif age_days <= settings.freshness_yellow_days:
        return 0.8
    elif age_days <= settings.freshness_red_days:
        return 0.5
    return 0.2


def validate_infra(record: InfrastructureRecord) -> ValidationResult:
    issues = []

    if not record.name or len(record.name.strip()) < 3:
        issues.append(FieldIssue("name", "error", "Infrastructure name too short or empty"))
    if not record.state:
        issues.append(FieldIssue("state", "error", "State is required"))
    if record.cost_crore is not None and record.cost_crore < 0:
        issues.append(FieldIssue("cost_crore", "error", "Cost cannot be negative"))
    if record.length_km is not None and record.length_km <= 0:
        issues.append(FieldIssue("length_km", "warning", "Length should be positive"))
    if record.expected_completion_date and record.announcement_date:
        if record.expected_completion_date < record.announcement_date:
            issues.append(FieldIssue(
                "expected_completion_date", "error",
                "Completion date precedes announcement date",
            ))
    if record.status.value in ("announced", "approved") and not record.announcement_date:
        issues.append(FieldIssue("announcement_date", "warning", "Missing announcement date"))

    freshness = _freshness(record.published_date)
    conf_adj = 0.0 if not issues else (0.1 * len([i for i in issues if i.severity == "error"]))

    return ValidationResult(
        record_id=record.id,
        record_type="InfrastructureRecord",
        passed=len([i for i in issues if i.severity == "error"]) == 0,
        issues=issues,
        freshness_score=freshness,
        confidence_adjustment=conf_adj,
    )


def validate_rera(record: RERARecord) -> ValidationResult:
    issues = []

    if not record.rera_registration_number:
        issues.append(FieldIssue("rera_registration_number", "error", "RERA number required"))
    if not record.project_name:
        issues.append(FieldIssue("project_name", "error", "Project name required"))
    if not record.developer_name:
        issues.append(FieldIssue("developer_name", "error", "Developer name required"))
    if record.units_sold and record.total_units:
        if record.units_sold > record.total_units:
            issues.append(FieldIssue("units_sold", "error", "Units sold exceeds total units"))
    if record.possession_delay_days and record.possession_delay_days > 1825:  # 5 years
        issues.append(FieldIssue(
            "possession_delay_days", "warning",
            f"Extreme delay: {record.possession_delay_days} days — verify source",
        ))
    if record.rera_status.value == "registered" and not record.registration_date:
        issues.append(FieldIssue("registration_date", "warning", "Registration date missing for active RERA"))

    freshness = _freshness(record.published_date)
    conf_adj = 0.05 * len([i for i in issues if i.severity == "error"])

    return ValidationResult(
        record_id=record.id,
        record_type="RERARecord",
        passed=len([i for i in issues if i.severity == "error"]) == 0,
        issues=issues,
        freshness_score=freshness,
        confidence_adjustment=conf_adj,
    )


def validate_market_price(record: MarketPriceRecord) -> ValidationResult:
    issues = []

    if not record.city:
        issues.append(FieldIssue("city", "error", "City required"))
    if not record.locality:
        issues.append(FieldIssue("locality", "error", "Locality required"))
    if record.price_per_sqft is not None:
        if record.price_per_sqft < 500:
            issues.append(FieldIssue("price_per_sqft", "warning", "Price < ₹500/sqft — likely stale or erroneous"))
        if record.price_per_sqft > 500000:
            issues.append(FieldIssue("price_per_sqft", "warning", "Price > ₹5L/sqft — verify source"))
    if record.gross_yield_pct is not None:
        if record.gross_yield_pct > 20:
            issues.append(FieldIssue("gross_yield_pct", "warning", "Yield > 20% is suspicious; verify"))
        if record.gross_yield_pct < 0:
            issues.append(FieldIssue("gross_yield_pct", "error", "Yield cannot be negative"))
    if record.absorption_rate_pct is not None and not (0 <= record.absorption_rate_pct <= 100):
        issues.append(FieldIssue("absorption_rate_pct", "error", "Absorption rate must be 0–100%"))

    freshness = _freshness(record.published_date)
    conf_adj = 0.05 * len([i for i in issues if i.severity == "error"])

    return ValidationResult(
        record_id=record.id,
        record_type="MarketPriceRecord",
        passed=len([i for i in issues if i.severity == "error"]) == 0,
        issues=issues,
        freshness_score=freshness,
        confidence_adjustment=conf_adj,
    )


def validate_macro(record: MacroSignalRecord) -> ValidationResult:
    issues = []

    if not record.signal_type:
        issues.append(FieldIssue("signal_type", "error", "Signal type required"))
    if record.signal_type == "repo_rate" and not (0 < record.value < 30):
        issues.append(FieldIssue("value", "warning", f"Repo rate {record.value}% outside expected range"))

    freshness = _freshness(record.published_date)

    return ValidationResult(
        record_id=record.id,
        record_type="MacroSignalRecord",
        passed=len([i for i in issues if i.severity == "error"]) == 0,
        issues=issues,
        freshness_score=freshness,
    )
