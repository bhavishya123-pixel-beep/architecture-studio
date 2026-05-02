"""
Unified Pydantic v2 schemas for every record type in the system.
These are the canonical data contracts between all layers.
"""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


# ─────────────────────────────────────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────────────────────────────────────

class AssetType(str, Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    MIXED_USE = "mixed_use"
    PLOTTED = "plotted"
    INDUSTRIAL = "industrial"
    WAREHOUSE = "warehouse"
    RETAIL = "retail"

class InfraType(str, Enum):
    HIGHWAY = "highway"
    EXPRESSWAY = "expressway"
    RING_ROAD = "ring_road"
    BYPASS = "bypass"
    METRO = "metro"
    RAILWAY = "railway"
    FREIGHT_CORRIDOR = "freight_corridor"
    AIRPORT = "airport"
    INDUSTRIAL_CORRIDOR = "industrial_corridor"
    LOGISTICS_PARK = "logistics_park"
    SEZ = "sez"
    SMART_CITY = "smart_city"
    PORT = "port"
    DATA_CENTER_ZONE = "data_center_zone"

class InfraStatus(str, Enum):
    ANNOUNCED = "announced"
    APPROVED = "approved"
    TENDERED = "tendered"
    UNDER_CONSTRUCTION = "under_construction"
    OPERATIONAL = "operational"
    STALLED = "stalled"
    CANCELLED = "cancelled"

class RERAStatus(str, Enum):
    REGISTERED = "registered"
    EXPIRED = "expired"
    REVOKED = "revoked"
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    UNKNOWN = "unknown"

class SourceTier(int, Enum):
    OFFICIAL = 1
    VERIFIED = 2
    SECONDARY = 3

class AlertSeverity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class AlertType(str, Enum):
    INFRA_ANNOUNCED = "infra_announced"
    INFRA_APPROVED = "infra_approved"
    INFRA_COMPLETED = "infra_completed"
    RERA_CHANGE = "rera_change"
    POSSESSION_SLIP = "possession_slip"
    PRICE_SPIKE = "price_spike"
    YIELD_COMPRESSION = "yield_compression"
    YIELD_EXPANSION = "yield_expansion"
    LAUNCH_SPIKE = "launch_spike"
    MACRO_RATE_CHANGE = "macro_rate_change"
    LEGAL_NOTICE = "legal_notice"
    DATA_STALE = "data_stale"


# ─────────────────────────────────────────────────────────────────────────────
# Base mixin
# ─────────────────────────────────────────────────────────────────────────────

class AuditMixin(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    source_id: str = Field(..., description="References SOURCE_REGISTRY key")
    source_url: Optional[str] = None
    source_tier: SourceTier
    raw_snapshot_path: Optional[str] = Field(
        default=None,
        description="Path in raw zone to immutable source capture",
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence in this record's accuracy [0,1]",
    )
    freshness_score: float = Field(
        default=1.0, ge=0.0, le=1.0,
        description="Decays over time; 1.0 = fresh today, 0.0 = stale",
    )
    data_gap: bool = Field(
        default=False,
        description="True if critical fields are missing; block downstream scores",
    )
    notes: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# Geospatial
# ─────────────────────────────────────────────────────────────────────────────

class GeoPoint(BaseModel):
    lat: float = Field(ge=-90.0, le=90.0)
    lon: float = Field(ge=-180.0, le=180.0)

class GeoPolygon(BaseModel):
    """Simplified polygon: list of (lat, lon) rings."""
    exterior: list[tuple[float, float]]
    holes: list[list[tuple[float, float]]] = Field(default_factory=list)

class InfraProximity(BaseModel):
    infra_id: UUID
    infra_name: str
    infra_type: InfraType
    infra_status: InfraStatus
    distance_km: float
    influence_zone: str  # "direct" | "secondary" | "corridor"
    travel_time_current_min: Optional[float] = None
    travel_time_post_infra_min: Optional[float] = None
    uplift_weight: float = Field(ge=0.0, le=1.0)


# ─────────────────────────────────────────────────────────────────────────────
# Infrastructure Record
# ─────────────────────────────────────────────────────────────────────────────

class InfrastructureRecord(AuditMixin):
    infra_type: InfraType
    name: str
    description: Optional[str] = None
    state: str
    city: Optional[str] = None
    corridor: Optional[str] = None
    status: InfraStatus
    length_km: Optional[float] = None
    cost_crore: Optional[float] = None
    start_point: Optional[str] = None
    end_point: Optional[str] = None
    geo_line: Optional[list[GeoPoint]] = None
    geo_polygon: Optional[GeoPolygon] = None
    announcement_date: Optional[date] = None
    approval_date: Optional[date] = None
    tender_date: Optional[date] = None
    construction_start_date: Optional[date] = None
    expected_completion_date: Optional[date] = None
    actual_completion_date: Optional[date] = None
    executing_agency: Optional[str] = None
    project_id_official: Optional[str] = None
    tender_number: Optional[str] = None
    published_date: datetime = Field(default_factory=datetime.utcnow)


# ─────────────────────────────────────────────────────────────────────────────
# RERA Project Record
# ─────────────────────────────────────────────────────────────────────────────

class RERARecord(AuditMixin):
    rera_registration_number: str
    rera_portal: str  # e.g. "MahaRERA", "K-RERA"
    project_name: str
    developer_name: str
    asset_type: AssetType
    state: str
    city: str
    locality: Optional[str] = None
    pin_code: Optional[str] = None
    geo_point: Optional[GeoPoint] = None
    rera_status: RERAStatus
    registration_date: Optional[date] = None
    registration_expiry: Optional[date] = None
    promised_possession_date: Optional[date] = None
    revised_possession_date: Optional[date] = None
    actual_possession_date: Optional[date] = None
    total_units: Optional[int] = None
    units_sold: Optional[int] = None
    units_remaining: Optional[int] = None
    total_built_area_sqft: Optional[float] = None
    carpet_area_range_sqft: Optional[tuple[float, float]] = None
    complaint_count: Optional[int] = None
    active_complaints: Optional[int] = None
    possession_delay_days: Optional[int] = None
    published_date: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def compute_possession_delay(self) -> "RERARecord":
        if self.promised_possession_date and not self.actual_possession_date:
            today = date.today()
            if today > self.promised_possession_date:
                self.possession_delay_days = (today - self.promised_possession_date).days
        return self


# ─────────────────────────────────────────────────────────────────────────────
# Market Price Record
# ─────────────────────────────────────────────────────────────────────────────

class MarketPriceRecord(AuditMixin):
    city: str
    state: str
    locality: str
    pin_code: Optional[str] = None
    geo_point: Optional[GeoPoint] = None
    asset_type: AssetType
    segment: str  # "affordable" | "mid_income" | "premium" | "luxury"
    price_per_sqft: Optional[float] = None
    price_per_sqft_yoy_pct: Optional[float] = None
    price_per_sqft_qoq_pct: Optional[float] = None
    monthly_rent_per_sqft: Optional[float] = None
    gross_yield_pct: Optional[float] = None
    net_yield_pct: Optional[float] = None
    inventory_units: Optional[int] = None
    absorption_rate_pct: Optional[float] = None  # units sold / units launched in period
    days_on_market: Optional[float] = None
    new_launches_units: Optional[int] = None
    unsold_inventory_months: Optional[float] = None
    observation_period: str  # e.g. "2024-Q4", "2025-01"
    published_date: datetime = Field(default_factory=datetime.utcnow)


# ─────────────────────────────────────────────────────────────────────────────
# Developer Record
# ─────────────────────────────────────────────────────────────────────────────

class DeveloperRecord(AuditMixin):
    developer_id: Optional[str] = None
    name: str
    registered_name: Optional[str] = None
    state: Optional[str] = None
    total_projects: Optional[int] = None
    completed_projects: Optional[int] = None
    ongoing_projects: Optional[int] = None
    delayed_projects: Optional[int] = None
    rera_complaints_total: Optional[int] = None
    avg_possession_delay_days: Optional[float] = None
    on_time_delivery_rate_pct: Optional[float] = None
    website: Optional[str] = None
    published_date: datetime = Field(default_factory=datetime.utcnow)


# ─────────────────────────────────────────────────────────────────────────────
# Macro Signal Record
# ─────────────────────────────────────────────────────────────────────────────

class MacroSignalRecord(AuditMixin):
    signal_type: str  # "repo_rate" | "cpi" | "housing_cpi" | "credit_growth" | "employment"
    value: float
    unit: str          # "pct" | "index" | "crore"
    period: str        # "2025-01" | "2025-Q1"
    yoy_change: Optional[float] = None
    qoq_change: Optional[float] = None
    direction: str = "neutral"  # "positive" | "negative" | "neutral"
    rbi_commentary: Optional[str] = None
    published_date: datetime = Field(default_factory=datetime.utcnow)


# ─────────────────────────────────────────────────────────────────────────────
# Scores
# ─────────────────────────────────────────────────────────────────────────────

class ScoreBreakdown(BaseModel):
    raw_value: float
    normalized_score: float = Field(ge=0.0, le=100.0)
    weight: float
    weighted_contribution: float
    explanation: str
    evidence_ids: list[UUID] = Field(default_factory=list)
    data_gap: bool = False
    confidence: float = Field(ge=0.0, le=1.0)

class LocationScoreCard(BaseModel):
    location_id: UUID = Field(default_factory=uuid4)
    city: str
    state: str
    locality: str
    pin_code: Optional[str] = None
    geo_point: Optional[GeoPoint] = None
    computed_at: datetime = Field(default_factory=datetime.utcnow)

    infrastructure_uplift: Optional[ScoreBreakdown] = None
    connectivity: Optional[ScoreBreakdown] = None
    affordability: Optional[ScoreBreakdown] = None
    rental_yield: Optional[ScoreBreakdown] = None
    liquidity: Optional[ScoreBreakdown] = None
    regulatory_safety: Optional[ScoreBreakdown] = None
    developer_trust: Optional[ScoreBreakdown] = None
    execution_risk: Optional[ScoreBreakdown] = None
    appreciation_potential: Optional[ScoreBreakdown] = None

    final_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    final_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    data_completeness_pct: float = 0.0
    human_review_required: bool = False
    disclaimer: str = (
        "Scores are analytical estimates based on available data. "
        "Not financial advice. Conduct independent due diligence."
    )

    def compute_final(self, weights: dict[str, float]) -> None:
        total_weight = 0.0
        weighted_sum = 0.0
        confidence_sum = 0.0
        n_scores = 0
        n_complete = 0

        score_fields = [
            "infrastructure_uplift", "connectivity", "affordability",
            "rental_yield", "liquidity", "regulatory_safety",
            "developer_trust", "execution_risk", "appreciation_potential",
        ]

        for field_name in score_fields:
            breakdown: Optional[ScoreBreakdown] = getattr(self, field_name)
            n_scores += 1
            if breakdown is not None and not breakdown.data_gap:
                w = weights.get(field_name, 0.0)
                weighted_sum += breakdown.normalized_score * w
                total_weight += w
                confidence_sum += breakdown.confidence
                n_complete += 1

        if total_weight > 0:
            self.final_score = round(weighted_sum / total_weight, 2)
            self.final_confidence = round(confidence_sum / n_complete, 3) if n_complete else 0.0
        self.data_completeness_pct = round(n_complete / n_scores * 100, 1)
        # Flag for human review if completeness < 60% or score is very high
        if self.data_completeness_pct < 60 or (self.final_score or 0) > 85:
            self.human_review_required = True


# ─────────────────────────────────────────────────────────────────────────────
# Alert
# ─────────────────────────────────────────────────────────────────────────────

class Alert(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    body: str
    location: Optional[str] = None
    city: Optional[str] = None
    affected_project_ids: list[UUID] = Field(default_factory=list)
    affected_infra_ids: list[UUID] = Field(default_factory=list)
    evidence_ids: list[UUID] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    data: dict[str, Any] = Field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# Investment Memo
# ─────────────────────────────────────────────────────────────────────────────

class InvestmentScenario(BaseModel):
    label: str           # "base" | "bull" | "bear"
    assumption: str
    cagr_pct: float
    holding_years: int
    exit_price_per_sqft: float
    gross_yield_pct: float
    net_yield_pct: float
    irr_estimate_pct: Optional[float] = None

class InvestmentMemo(BaseModel):
    memo_id: UUID = Field(default_factory=uuid4)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: str = "OrchestratorAgent"

    # Location context
    city: str
    state: str
    locality: str
    project_name: Optional[str] = None
    rera_number: Optional[str] = None
    developer: Optional[str] = None
    asset_type: Optional[AssetType] = None

    # Memo sections
    summary: str
    thesis: str
    location_facts: str
    infrastructure_tailwinds: str
    market_evidence: str
    valuation_context: str
    legal_rera_status: str
    risks: str
    watch_conditions: str

    # Scores
    score_card: Optional[LocationScoreCard] = None

    # Scenarios
    scenarios: list[InvestmentScenario] = Field(default_factory=list)

    # Meta
    confidence_level: str  # "high" | "medium" | "low"
    data_sources_used: list[str] = Field(default_factory=list)
    evidence_ids: list[UUID] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    disclaimer: str = (
        "This memo is generated by an automated analytical system. "
        "It does not constitute investment advice or a guarantee of returns. "
        "Data may be incomplete. Consult a SEBI-registered advisor and "
        "conduct independent legal due diligence before any transaction."
    )
