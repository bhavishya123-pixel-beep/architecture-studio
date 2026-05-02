"""
ETL normalization pipeline.
Transforms raw scraped/parsed dicts into typed Pydantic records with
provenance tags, confidence scores, and freshness.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from api.schemas import (
    InfrastructureRecord, RERARecord, MarketPriceRecord,
    DeveloperRecord, MacroSignalRecord, SourceTier,
    InfraType, InfraStatus, RERAStatus, AssetType,
)
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _coerce_float(v: Any) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(str(v).replace(",", "").strip())
    except (ValueError, TypeError):
        return None


def _coerce_date(v: Any) -> Optional[datetime]:
    if not v:
        return None
    formats = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%B %Y", "%b %Y", "%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(str(v).strip(), fmt)
        except ValueError:
            continue
    return None


def _save_raw_snapshot(raw: dict, source_id: str) -> str:
    """Persist raw dict to raw zone; return relative path."""
    snapshot_dir = Path(settings.duckdb_path).parent.parent / "raw" / source_id
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    content = json.dumps(raw, default=str, ensure_ascii=False)
    hash_key = hashlib.md5(content.encode()).hexdigest()[:12]
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    fpath = snapshot_dir / f"{ts}_{hash_key}.json"
    fpath.write_text(content, encoding="utf-8")
    return str(fpath)


def normalize_infra(raw: dict, source_id: str, source_tier: SourceTier) -> InfrastructureRecord:
    snapshot_path = _save_raw_snapshot(raw, source_id)

    # Map raw status strings to enum
    status_map = {
        "announced": InfraStatus.ANNOUNCED,
        "approved": InfraStatus.APPROVED,
        "tendered": InfraStatus.TENDERED,
        "under construction": InfraStatus.UNDER_CONSTRUCTION,
        "operational": InfraStatus.OPERATIONAL,
        "stalled": InfraStatus.STALLED,
        "cancelled": InfraStatus.CANCELLED,
    }
    raw_status = str(raw.get("status", "")).lower().strip()
    status = status_map.get(raw_status, InfraStatus.ANNOUNCED)

    infra_type_map = {
        "highway": InfraType.HIGHWAY,
        "expressway": InfraType.EXPRESSWAY,
        "ring road": InfraType.RING_ROAD,
        "bypass": InfraType.BYPASS,
        "metro": InfraType.METRO,
        "railway": InfraType.RAILWAY,
        "freight corridor": InfraType.FREIGHT_CORRIDOR,
        "airport": InfraType.AIRPORT,
        "industrial corridor": InfraType.INDUSTRIAL_CORRIDOR,
        "logistics park": InfraType.LOGISTICS_PARK,
        "sez": InfraType.SEZ,
    }
    raw_type = str(raw.get("infra_type", "")).lower().strip()
    infra_type = infra_type_map.get(raw_type, InfraType.HIGHWAY)

    # Confidence: official sources start at 0.9; secondary at 0.5
    base_confidence = {
        SourceTier.OFFICIAL: 0.90,
        SourceTier.VERIFIED: 0.70,
        SourceTier.SECONDARY: 0.50,
    }[source_tier]

    # Reduce confidence for unconfirmed statuses
    if status == InfraStatus.ANNOUNCED:
        base_confidence *= 0.9

    return InfrastructureRecord(
        source_id=source_id,
        source_url=raw.get("source_url"),
        source_tier=source_tier,
        raw_snapshot_path=snapshot_path,
        confidence=round(base_confidence, 3),
        infra_type=infra_type,
        name=str(raw.get("name", "")).strip(),
        description=raw.get("description"),
        state=str(raw.get("state", "")).strip(),
        city=raw.get("city"),
        corridor=raw.get("corridor"),
        status=status,
        length_km=_coerce_float(raw.get("length_km")),
        cost_crore=_coerce_float(raw.get("cost_crore")),
        start_point=raw.get("start_point"),
        end_point=raw.get("end_point"),
        announcement_date=_coerce_date(raw.get("announcement_date")),
        expected_completion_date=_coerce_date(raw.get("expected_completion_date")),
        actual_completion_date=_coerce_date(raw.get("actual_completion_date")),
        executing_agency=raw.get("executing_agency"),
        project_id_official=raw.get("project_id"),
        published_date=_coerce_date(raw.get("published_date")) or datetime.utcnow(),
    )


def normalize_rera(raw: dict, source_id: str) -> RERARecord:
    snapshot_path = _save_raw_snapshot(raw, source_id)

    status_map = {
        "registered": RERAStatus.REGISTERED,
        "expired": RERAStatus.EXPIRED,
        "revoked": RERAStatus.REVOKED,
        "not required": RERAStatus.NOT_REQUIRED,
        "pending": RERAStatus.PENDING,
    }
    raw_status = str(raw.get("rera_status", "")).lower().strip()
    rera_status = status_map.get(raw_status, RERAStatus.UNKNOWN)

    asset_map = {
        "residential": AssetType.RESIDENTIAL,
        "commercial": AssetType.COMMERCIAL,
        "mixed": AssetType.MIXED_USE,
        "plotted": AssetType.PLOTTED,
    }
    raw_asset = str(raw.get("asset_type", "residential")).lower().strip()
    asset_type = asset_map.get(raw_asset, AssetType.RESIDENTIAL)

    total = _coerce_float(raw.get("total_units"))
    sold = _coerce_float(raw.get("units_sold"))

    return RERARecord(
        source_id=source_id,
        source_url=raw.get("source_url"),
        source_tier=SourceTier.OFFICIAL,
        raw_snapshot_path=snapshot_path,
        confidence=0.92,
        rera_registration_number=str(raw.get("rera_number", "")).strip(),
        rera_portal=raw.get("rera_portal", source_id),
        project_name=str(raw.get("project_name", "")).strip(),
        developer_name=str(raw.get("developer_name", "")).strip(),
        asset_type=asset_type,
        state=str(raw.get("state", "")).strip(),
        city=str(raw.get("city", "")).strip(),
        locality=raw.get("locality"),
        pin_code=str(raw.get("pin_code", "")).strip() or None,
        rera_status=rera_status,
        registration_date=_coerce_date(raw.get("registration_date")),
        registration_expiry=_coerce_date(raw.get("registration_expiry")),
        promised_possession_date=_coerce_date(raw.get("promised_possession_date")),
        revised_possession_date=_coerce_date(raw.get("revised_possession_date")),
        actual_possession_date=_coerce_date(raw.get("actual_possession_date")),
        total_units=int(total) if total else None,
        units_sold=int(sold) if sold else None,
        units_remaining=int(total - sold) if (total and sold) else None,
        complaint_count=_coerce_float(raw.get("complaint_count")) and int(_coerce_float(raw.get("complaint_count"))),
        published_date=_coerce_date(raw.get("published_date")) or datetime.utcnow(),
    )


def normalize_market_price(raw: dict, source_id: str, source_tier: SourceTier) -> MarketPriceRecord:
    snapshot_path = _save_raw_snapshot(raw, source_id)

    base_conf = {
        SourceTier.OFFICIAL: 0.88,
        SourceTier.VERIFIED: 0.72,
        SourceTier.SECONDARY: 0.45,
    }[source_tier]

    return MarketPriceRecord(
        source_id=source_id,
        source_url=raw.get("source_url"),
        source_tier=source_tier,
        raw_snapshot_path=snapshot_path,
        confidence=base_conf,
        city=str(raw.get("city", "")).strip(),
        state=str(raw.get("state", "")).strip(),
        locality=str(raw.get("locality", "")).strip(),
        pin_code=raw.get("pin_code"),
        asset_type=AssetType(raw.get("asset_type", "residential")),
        segment=raw.get("segment", "mid_income"),
        price_per_sqft=_coerce_float(raw.get("price_per_sqft")),
        price_per_sqft_yoy_pct=_coerce_float(raw.get("price_yoy_pct")),
        price_per_sqft_qoq_pct=_coerce_float(raw.get("price_qoq_pct")),
        monthly_rent_per_sqft=_coerce_float(raw.get("rent_per_sqft")),
        gross_yield_pct=_coerce_float(raw.get("gross_yield_pct")),
        net_yield_pct=_coerce_float(raw.get("net_yield_pct")),
        inventory_units=_coerce_float(raw.get("inventory_units")) and int(_coerce_float(raw.get("inventory_units"))),
        absorption_rate_pct=_coerce_float(raw.get("absorption_rate_pct")),
        days_on_market=_coerce_float(raw.get("days_on_market")),
        new_launches_units=_coerce_float(raw.get("new_launches")) and int(_coerce_float(raw.get("new_launches"))),
        unsold_inventory_months=_coerce_float(raw.get("unsold_months")),
        observation_period=str(raw.get("period", "")),
        published_date=_coerce_date(raw.get("published_date")) or datetime.utcnow(),
    )


def normalize_macro(raw: dict, source_id: str) -> MacroSignalRecord:
    snapshot_path = _save_raw_snapshot(raw, source_id)

    direction_map = {"up": "positive", "down": "negative", "stable": "neutral"}
    raw_dir = str(raw.get("direction", "stable")).lower()
    direction = direction_map.get(raw_dir, "neutral")

    return MacroSignalRecord(
        source_id=source_id,
        source_url=raw.get("source_url"),
        source_tier=SourceTier.OFFICIAL,
        raw_snapshot_path=snapshot_path,
        confidence=0.95,
        signal_type=str(raw.get("signal_type", "")),
        value=float(raw.get("value", 0)),
        unit=str(raw.get("unit", "pct")),
        period=str(raw.get("period", "")),
        yoy_change=_coerce_float(raw.get("yoy_change")),
        qoq_change=_coerce_float(raw.get("qoq_change")),
        direction=direction,
        rbi_commentary=raw.get("commentary"),
        published_date=_coerce_date(raw.get("published_date")) or datetime.utcnow(),
    )
