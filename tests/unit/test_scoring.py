"""Unit tests for all scoring modules."""

import pytest
from uuid import uuid4

from api.schemas import (
    InfraProximity, RERARecord, MarketPriceRecord, DeveloperRecord,
    InfraType, InfraStatus, RERAStatus, AssetType, SourceTier, GeoPoint,
)
from scoring.modules.infrastructure_uplift import compute_infra_uplift_score
from scoring.modules.regulatory_safety import compute_regulatory_safety_score
from scoring.modules.rental_yield import compute_rental_yield_score
from scoring.modules.liquidity import compute_liquidity_score
from scoring.modules.developer_trust import compute_developer_trust_score
from scoring.modules.execution_risk import compute_execution_risk_score
from scoring.modules.connectivity import compute_connectivity_score
from scoring.modules.affordability import compute_affordability_score
from scoring.modules.appreciation_potential import compute_appreciation_score
from scoring.engine import build_location_scorecard
from tests.fixtures.demo_data import (
    DEMO_INFRA, DEMO_RERA, DEMO_PRICES, DEMO_MACRO,
    DEMO_DEVELOPERS, DEMO_PROXIMITY_KOKAPET,
)


# ── Infrastructure Uplift ─────────────────────────────────────────────────────

class TestInfraUpliftScore:
    def test_no_infra_returns_data_gap(self):
        result = compute_infra_uplift_score([])
        assert result.data_gap is True
        assert result.normalized_score == 0.0

    def test_under_construction_scores_higher_than_announced(self):
        base_prox = InfraProximity(
            infra_id=uuid4(), infra_name="Test", infra_type=InfraType.METRO,
            infra_status=InfraStatus.UNDER_CONSTRUCTION,
            distance_km=1.0, influence_zone="direct", uplift_weight=1.0,
        )
        announced_prox = InfraProximity(
            infra_id=uuid4(), infra_name="Test", infra_type=InfraType.METRO,
            infra_status=InfraStatus.ANNOUNCED,
            distance_km=1.0, influence_zone="direct", uplift_weight=1.0,
        )
        score_uc = compute_infra_uplift_score([base_prox]).normalized_score
        score_an = compute_infra_uplift_score([announced_prox]).normalized_score
        assert score_uc > score_an

    def test_closer_infra_scores_higher(self):
        near = InfraProximity(
            infra_id=uuid4(), infra_name="Near Metro", infra_type=InfraType.METRO,
            infra_status=InfraStatus.UNDER_CONSTRUCTION,
            distance_km=0.5, influence_zone="direct", uplift_weight=1.0,
        )
        far = InfraProximity(
            infra_id=uuid4(), infra_name="Far Metro", infra_type=InfraType.METRO,
            infra_status=InfraStatus.UNDER_CONSTRUCTION,
            distance_km=12.0, influence_zone="corridor", uplift_weight=1.0,
        )
        assert compute_infra_uplift_score([near]).normalized_score > compute_infra_uplift_score([far]).normalized_score

    def test_cancelled_infra_contributes_zero(self):
        cancelled = InfraProximity(
            infra_id=uuid4(), infra_name="Cancelled", infra_type=InfraType.HIGHWAY,
            infra_status=InfraStatus.CANCELLED,
            distance_km=1.0, influence_zone="direct", uplift_weight=1.0,
        )
        result = compute_infra_uplift_score([cancelled])
        assert result.normalized_score == pytest.approx(0.0, abs=1.0)

    def test_score_bounded_0_100(self):
        proxes = [
            InfraProximity(
                infra_id=uuid4(), infra_name=f"P{i}", infra_type=InfraType.METRO,
                infra_status=InfraStatus.UNDER_CONSTRUCTION,
                distance_km=0.1, influence_zone="direct", uplift_weight=1.0,
            )
            for i in range(10)
        ]
        result = compute_infra_uplift_score(proxes)
        assert 0.0 <= result.normalized_score <= 100.0

    def test_demo_proximity_kokapet_scores_high(self):
        result = compute_infra_uplift_score(DEMO_PROXIMITY_KOKAPET)
        # Kokapet has ring road under construction 1.2km away — meaningful uplift signal
        assert result.normalized_score > 30.0
        assert not result.data_gap


# ── Regulatory Safety ─────────────────────────────────────────────────────────

class TestRegulatorySafetyScore:
    def test_no_rera_returns_neutral_with_gap(self):
        result = compute_regulatory_safety_score([])
        assert result.data_gap is True
        assert result.normalized_score == pytest.approx(50.0)

    def test_revoked_rera_scores_low(self):
        rera = DEMO_RERA[2]  # expired RERA with complaints
        result = compute_regulatory_safety_score([rera])
        assert result.normalized_score < 60.0

    def test_clean_registered_rera_scores_high(self):
        rera = DEMO_RERA[0]  # Prestige Kokapet — registered, low complaints
        result = compute_regulatory_safety_score([rera])
        assert result.normalized_score >= 60.0

    def test_score_bounded_0_100(self):
        result = compute_regulatory_safety_score(DEMO_RERA)
        assert 0.0 <= result.normalized_score <= 100.0


# ── Rental Yield ─────────────────────────────────────────────────────────────

class TestRentalYieldScore:
    def test_no_data_returns_gap(self):
        result = compute_rental_yield_score([])
        assert result.data_gap is True

    def test_high_yield_scores_higher(self):
        low_yield = MarketPriceRecord(
            source_id="test", source_tier=SourceTier.VERIFIED,
            confidence=0.8, freshness_score=1.0,
            city="Mumbai", state="Maharashtra", locality="Test",
            asset_type=AssetType.RESIDENTIAL, segment="mid_income",
            gross_yield_pct=1.5, observation_period="2024-Q4",
            published_date=__import__("datetime").datetime.utcnow(),
        )
        high_yield = MarketPriceRecord(
            source_id="test", source_tier=SourceTier.VERIFIED,
            confidence=0.8, freshness_score=1.0,
            city="Mumbai", state="Maharashtra", locality="Test",
            asset_type=AssetType.RESIDENTIAL, segment="mid_income",
            gross_yield_pct=4.5, observation_period="2024-Q4",
            published_date=__import__("datetime").datetime.utcnow(),
        )
        s_low = compute_rental_yield_score([low_yield]).normalized_score
        s_high = compute_rental_yield_score([high_yield]).normalized_score
        assert s_high > s_low

    def test_demo_prices_all_score_positive(self):
        for r in DEMO_PRICES:
            result = compute_rental_yield_score([r])
            assert result.normalized_score >= 0.0

    def test_score_bounded(self):
        result = compute_rental_yield_score(DEMO_PRICES)
        assert 0.0 <= result.normalized_score <= 100.0


# ── Liquidity ─────────────────────────────────────────────────────────────────

class TestLiquidityScore:
    def test_high_absorption_scores_high(self):
        r = DEMO_PRICES[0]  # 78% absorption
        result = compute_liquidity_score([r])
        assert result.normalized_score > 50.0

    def test_low_absorption_penalized(self):
        from datetime import datetime
        r = MarketPriceRecord(
            source_id="test", source_tier=SourceTier.VERIFIED,
            confidence=0.8, freshness_score=1.0,
            city="Test", state="Test", locality="Test",
            asset_type=AssetType.RESIDENTIAL, segment="mid_income",
            absorption_rate_pct=10.0, days_on_market=240.0,
            unsold_inventory_months=28.0,
            observation_period="2024-Q4", published_date=datetime.utcnow(),
        )
        result = compute_liquidity_score([r])
        assert result.normalized_score < 50.0


# ── Developer Trust ───────────────────────────────────────────────────────────

class TestDeveloperTrustScore:
    def test_no_data_returns_neutral(self):
        result = compute_developer_trust_score(None, [])
        assert result.normalized_score == pytest.approx(50.0, abs=5)
        assert result.data_gap is True

    def test_high_otr_developer_scores_well(self):
        dev = DEMO_DEVELOPERS[0]  # Prestige: 73% OTR
        result = compute_developer_trust_score(dev, [])
        assert result.normalized_score > 55.0

    def test_poor_developer_scores_low(self):
        dev = DEMO_DEVELOPERS[1]  # Demo Developer: 38% OTR, 385-day avg delay
        result = compute_developer_trust_score(dev, [])
        assert result.normalized_score < 50.0


# ── Execution Risk ────────────────────────────────────────────────────────────

class TestExecutionRiskScore:
    def test_revoked_rera_scores_low(self):
        result = compute_execution_risk_score([DEMO_RERA[2]])  # expired
        assert result.normalized_score < 70.0

    def test_clean_project_scores_high(self):
        result = compute_execution_risk_score([DEMO_RERA[0]])  # Prestige Kokapet
        assert result.normalized_score > 60.0


# ── Affordability ─────────────────────────────────────────────────────────────

class TestAffordabilityScore:
    def test_affordable_city_at_benchmark_scores_mid(self):
        result = compute_affordability_score([DEMO_PRICES[2]])  # Hinjawadi
        assert 40.0 <= result.normalized_score <= 90.0

    def test_expensive_segment_scores_neutral(self):
        from datetime import datetime
        r = MarketPriceRecord(
            source_id="test", source_tier=SourceTier.VERIFIED,
            confidence=0.8, freshness_score=1.0,
            city="Mumbai", state="Maharashtra", locality="South Mumbai",
            asset_type=AssetType.RESIDENTIAL, segment="luxury",
            price_per_sqft=85000, observation_period="2024-Q4",
            published_date=datetime.utcnow(),
        )
        result = compute_affordability_score([r])
        # Luxury segment gets neutral score ~50; allow for confidence/freshness weighting
        assert 30.0 <= result.normalized_score <= 60.0


# ── Full ScoreCard ────────────────────────────────────────────────────────────

class TestFullScoreCard:
    def test_kokapet_scorecard(self):
        card = build_location_scorecard(
            city="Hyderabad", state="Telangana", locality="Kokapet",
            proximal_infra=DEMO_PROXIMITY_KOKAPET,
            rera_records=[DEMO_RERA[0]],
            price_records=[DEMO_PRICES[0]],
            macro_signals=DEMO_MACRO,
            developer=DEMO_DEVELOPERS[0],
        )
        assert card.final_score is not None
        assert 0.0 <= card.final_score <= 100.0
        assert card.data_completeness_pct > 50.0
        assert card.final_confidence is not None

    def test_empty_data_returns_graceful_card(self):
        card = build_location_scorecard(
            city="Unknown", state="Unknown", locality="Unknown",
        )
        assert card is not None
        # Score should still be computed with available (zero) data

    def test_weights_sum_approximately_1(self):
        from config.settings import get_settings
        s = get_settings()
        total = sum(s.score_weights.values())
        assert total == pytest.approx(1.0, abs=0.001)
