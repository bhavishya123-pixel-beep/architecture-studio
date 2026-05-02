"""
Synthetic demo dataset for development and testing.
Covers 5 Indian cities, 10 corridors, multiple projects.
Based on realistic but entirely fabricated data — never use for actual investment decisions.
"""

from __future__ import annotations

from datetime import datetime, date, timedelta
from uuid import uuid4

from api.schemas import (
    InfrastructureRecord, RERARecord, MarketPriceRecord,
    MacroSignalRecord, DeveloperRecord, InfraProximity,
    InfraType, InfraStatus, RERAStatus, AssetType, SourceTier,
    GeoPoint,
)


# ── Infrastructure records ────────────────────────────────────────────────────

DEMO_INFRA: list[InfrastructureRecord] = [
    InfrastructureRecord(
        source_id="nhai_projects", source_tier=SourceTier.OFFICIAL,
        confidence=0.90, freshness_score=1.0,
        infra_type=InfraType.RING_ROAD, name="Hyderabad ORR Phase 3 Extension",
        state="Telangana", city="Hyderabad", corridor="ORR",
        status=InfraStatus.UNDER_CONSTRUCTION,
        length_km=12.4, cost_crore=2800.0,
        start_point="Kokapet Junction", end_point="Narsingi Junction",
        geo_line=[GeoPoint(lat=17.37, lon=78.38), GeoPoint(lat=17.36, lon=78.34)],
        announcement_date=date(2023, 8, 15),
        approval_date=date(2024, 2, 10),
        expected_completion_date=date(2026, 6, 30),
        executing_agency="HMDA",
        project_id_official="HYD-ORR-P3-EXT-2024",
        published_date=datetime(2024, 2, 15),
    ),
    InfrastructureRecord(
        source_id="metro_announcements", source_tier=SourceTier.OFFICIAL,
        confidence=0.88, freshness_score=1.0,
        infra_type=InfraType.METRO, name="Bengaluru Metro Phase 2B — Sarjapur Extension",
        state="Karnataka", city="Bengaluru", corridor="Metro Phase 2",
        status=InfraStatus.APPROVED,
        length_km=18.5, cost_crore=5200.0,
        start_point="Silk Board", end_point="Sarjapur",
        announcement_date=date(2023, 3, 20),
        approval_date=date(2024, 1, 18),
        expected_completion_date=date(2027, 12, 31),
        executing_agency="BMRCL",
        project_id_official="BLR-METRO-2B-2024",
        published_date=datetime(2024, 1, 20),
    ),
    InfrastructureRecord(
        source_id="nhai_projects", source_tier=SourceTier.OFFICIAL,
        confidence=0.92, freshness_score=0.9,
        infra_type=InfraType.EXPRESSWAY, name="Pune Ring Road — Eastern Section",
        state="Maharashtra", city="Pune", corridor="PRR",
        status=InfraStatus.TENDERED,
        length_km=35.0, cost_crore=8500.0,
        start_point="Wagholi", end_point="Uruli Kanchan",
        announcement_date=date(2022, 11, 5),
        tender_date=date(2024, 3, 1),
        expected_completion_date=date(2028, 3, 31),
        executing_agency="MSRDC",
        project_id_official="PUNE-PRR-EAST-2024",
        published_date=datetime(2024, 3, 5),
    ),
    InfrastructureRecord(
        source_id="nhai_projects", source_tier=SourceTier.OFFICIAL,
        confidence=0.95, freshness_score=1.0,
        infra_type=InfraType.EXPRESSWAY, name="Delhi-Meerut Regional Rapid Transit",
        state="Uttar Pradesh", city="Ghaziabad", corridor="RRTS Corridor 1",
        status=InfraStatus.UNDER_CONSTRUCTION,
        length_km=82.0, cost_crore=30274.0,
        start_point="Sarai Kale Khan", end_point="Meerut South",
        announcement_date=date(2019, 3, 8),
        construction_start_date=date(2019, 10, 1),
        expected_completion_date=date(2025, 6, 30),
        executing_agency="NCRTC",
        project_id_official="NCRTC-DELHI-MEERUT-2019",
        published_date=datetime(2024, 6, 1),
    ),
    InfrastructureRecord(
        source_id="airport_aai", source_tier=SourceTier.OFFICIAL,
        confidence=0.87, freshness_score=0.95,
        infra_type=InfraType.AIRPORT, name="Navi Mumbai International Airport — Phase 1",
        state="Maharashtra", city="Navi Mumbai", corridor="Trans-Harbour",
        status=InfraStatus.UNDER_CONSTRUCTION,
        length_km=None, cost_crore=16700.0,
        announcement_date=date(2019, 2, 18),
        construction_start_date=date(2021, 11, 16),
        expected_completion_date=date(2026, 12, 31),
        executing_agency="CIDCO",
        project_id_official="AAI-NMIA-PH1-2021",
        published_date=datetime(2024, 8, 10),
    ),
]


# ── RERA records ──────────────────────────────────────────────────────────────

DEMO_RERA: list[RERARecord] = [
    RERARecord(
        source_id="rera_telangana", source_tier=SourceTier.OFFICIAL,
        confidence=0.92, freshness_score=1.0,
        rera_registration_number="P02400012345",
        rera_portal="TSRERA",
        project_name="Prestige Kokapet Towers",
        developer_name="Prestige Estates Projects Ltd",
        asset_type=AssetType.RESIDENTIAL,
        state="Telangana", city="Hyderabad", locality="Kokapet",
        pin_code="500075",
        geo_point=GeoPoint(lat=17.373, lon=78.381),
        rera_status=RERAStatus.REGISTERED,
        registration_date=date(2022, 5, 15),
        registration_expiry=date(2027, 5, 14),
        promised_possession_date=date(2025, 12, 31),
        total_units=640, units_sold=498, units_remaining=142,
        complaint_count=3, active_complaints=0,
        published_date=datetime(2024, 10, 1),
    ),
    RERARecord(
        source_id="rera_karnataka", source_tier=SourceTier.OFFICIAL,
        confidence=0.91, freshness_score=1.0,
        rera_registration_number="PRM/KA/RERA/1251/308/PR/201823",
        rera_portal="K-RERA",
        project_name="Brigade Cornerstone Utopia",
        developer_name="Brigade Enterprises Ltd",
        asset_type=AssetType.RESIDENTIAL,
        state="Karnataka", city="Bengaluru", locality="Whitefield",
        pin_code="560066",
        geo_point=GeoPoint(lat=12.965, lon=77.751),
        rera_status=RERAStatus.REGISTERED,
        registration_date=date(2018, 12, 1),
        promised_possession_date=date(2024, 6, 30),
        revised_possession_date=date(2024, 12, 31),
        total_units=5274, units_sold=4890,
        complaint_count=18, active_complaints=2,
        published_date=datetime(2024, 9, 15),
    ),
    RERARecord(
        source_id="rera_maharashtra", source_tier=SourceTier.OFFICIAL,
        confidence=0.90, freshness_score=0.9,
        rera_registration_number="P51700045678",
        rera_portal="MahaRERA",
        project_name="Demo Heights Phase 2",
        developer_name="Demo Developer Pvt Ltd",
        asset_type=AssetType.RESIDENTIAL,
        state="Maharashtra", city="Pune", locality="Wagholi",
        pin_code="412207",
        rera_status=RERAStatus.EXPIRED,
        registration_date=date(2019, 4, 10),
        registration_expiry=date(2022, 4, 9),
        promised_possession_date=date(2022, 12, 31),
        total_units=280, units_sold=140,
        complaint_count=22, active_complaints=8,
        published_date=datetime(2024, 6, 1),
    ),
]


# ── Market price records ──────────────────────────────────────────────────────

DEMO_PRICES: list[MarketPriceRecord] = [
    MarketPriceRecord(
        source_id="propequity_feed", source_tier=SourceTier.VERIFIED,
        confidence=0.78, freshness_score=1.0,
        city="Hyderabad", state="Telangana",
        locality="Kokapet", pin_code="500075",
        asset_type=AssetType.RESIDENTIAL, segment="premium",
        price_per_sqft=9200, price_per_sqft_yoy_pct=15.2, price_per_sqft_qoq_pct=3.8,
        monthly_rent_per_sqft=26.0, gross_yield_pct=3.39, net_yield_pct=2.71,
        inventory_units=1840, absorption_rate_pct=78.0,
        days_on_market=45.0, new_launches_units=520,
        unsold_inventory_months=8.5,
        observation_period="2024-Q4",
        published_date=datetime(2025, 1, 15),
    ),
    MarketPriceRecord(
        source_id="propequity_feed", source_tier=SourceTier.VERIFIED,
        confidence=0.77, freshness_score=1.0,
        city="Bengaluru", state="Karnataka",
        locality="Sarjapur Road", pin_code="560035",
        asset_type=AssetType.RESIDENTIAL, segment="mid_income",
        price_per_sqft=7200, price_per_sqft_yoy_pct=12.5, price_per_sqft_qoq_pct=2.9,
        monthly_rent_per_sqft=20.5, gross_yield_pct=3.42, net_yield_pct=2.73,
        inventory_units=3200, absorption_rate_pct=71.0,
        days_on_market=55.0, new_launches_units=800,
        unsold_inventory_months=10.5,
        observation_period="2024-Q4",
        published_date=datetime(2025, 1, 10),
    ),
    MarketPriceRecord(
        source_id="propequity_feed", source_tier=SourceTier.VERIFIED,
        confidence=0.76, freshness_score=1.0,
        city="Pune", state="Maharashtra",
        locality="Hinjawadi", pin_code="411057",
        asset_type=AssetType.RESIDENTIAL, segment="mid_income",
        price_per_sqft=6800, price_per_sqft_yoy_pct=9.8, price_per_sqft_qoq_pct=2.1,
        monthly_rent_per_sqft=18.5, gross_yield_pct=3.26, net_yield_pct=2.61,
        inventory_units=2400, absorption_rate_pct=65.0,
        days_on_market=68.0, new_launches_units=420,
        unsold_inventory_months=13.0,
        observation_period="2024-Q4",
        published_date=datetime(2025, 1, 12),
    ),
    MarketPriceRecord(
        source_id="propequity_feed", source_tier=SourceTier.VERIFIED,
        confidence=0.79, freshness_score=0.85,
        city="Mumbai", state="Maharashtra",
        locality="Thane West", pin_code="400601",
        asset_type=AssetType.RESIDENTIAL, segment="mid_income",
        price_per_sqft=13500, price_per_sqft_yoy_pct=8.5, price_per_sqft_qoq_pct=1.9,
        monthly_rent_per_sqft=28.0, gross_yield_pct=2.49, net_yield_pct=1.99,
        inventory_units=5800, absorption_rate_pct=62.0,
        days_on_market=72.0, new_launches_units=1200,
        unsold_inventory_months=14.5,
        observation_period="2024-Q3",
        published_date=datetime(2024, 10, 15),
    ),
]


# ── Macro signals ─────────────────────────────────────────────────────────────

DEMO_MACRO: list[MacroSignalRecord] = [
    MacroSignalRecord(
        source_id="rbi_mpc", source_tier=SourceTier.OFFICIAL,
        confidence=0.98, freshness_score=1.0,
        signal_type="repo_rate", value=6.25, unit="pct",
        period="2025-02", direction="negative",
        yoy_change=-0.25,
        rbi_commentary="MPC cut repo rate by 25 bps on improving inflation outlook.",
        published_date=datetime(2025, 2, 7),
    ),
    MacroSignalRecord(
        source_id="mospi_cpi", source_tier=SourceTier.OFFICIAL,
        confidence=0.97, freshness_score=1.0,
        signal_type="cpi", value=5.1, unit="pct",
        period="2025-01", direction="negative",
        yoy_change=-1.4,
        published_date=datetime(2025, 2, 12),
    ),
    MacroSignalRecord(
        source_id="mospi_cpi", source_tier=SourceTier.OFFICIAL,
        confidence=0.95, freshness_score=1.0,
        signal_type="housing_cpi", value=4.8, unit="pct",
        period="2025-01", direction="neutral",
        yoy_change=-0.3,
        published_date=datetime(2025, 2, 12),
    ),
]


# ── Developer records ─────────────────────────────────────────────────────────

DEMO_DEVELOPERS: list[DeveloperRecord] = [
    DeveloperRecord(
        source_id="rera_telangana", source_tier=SourceTier.OFFICIAL,
        confidence=0.85, freshness_score=0.95,
        name="Prestige Estates Projects Ltd",
        state="Karnataka",
        total_projects=52, completed_projects=38, ongoing_projects=12, delayed_projects=6,
        rera_complaints_total=42,
        avg_possession_delay_days=95.0,
        on_time_delivery_rate_pct=73.0,
        published_date=datetime(2024, 11, 1),
    ),
    DeveloperRecord(
        source_id="rera_maharashtra", source_tier=SourceTier.OFFICIAL,
        confidence=0.82, freshness_score=0.90,
        name="Demo Developer Pvt Ltd",
        state="Maharashtra",
        total_projects=8, completed_projects=3, ongoing_projects=4, delayed_projects=4,
        rera_complaints_total=45,
        avg_possession_delay_days=385.0,
        on_time_delivery_rate_pct=38.0,
        published_date=datetime(2024, 7, 1),
    ),
]


# ── Infra proximity (pre-computed for Kokapet, Hyderabad) ─────────────────────

DEMO_PROXIMITY_KOKAPET: list[InfraProximity] = [
    InfraProximity(
        infra_id=DEMO_INFRA[0].id,
        infra_name="Hyderabad ORR Phase 3 Extension",
        infra_type=InfraType.RING_ROAD,
        infra_status=InfraStatus.UNDER_CONSTRUCTION,
        distance_km=1.2,
        influence_zone="direct",
        travel_time_current_min=35.0,
        travel_time_post_infra_min=18.0,
        uplift_weight=0.95,
    ),
    InfraProximity(
        infra_id=uuid4(),
        infra_name="Financial District Metro Station",
        infra_type=InfraType.METRO,
        infra_status=InfraStatus.OPERATIONAL,
        distance_km=3.5,
        influence_zone="secondary",
        travel_time_current_min=20.0,
        travel_time_post_infra_min=20.0,
        uplift_weight=0.60,
    ),
]
