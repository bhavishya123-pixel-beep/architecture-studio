"""Unit tests for ETL normalization pipeline."""

import pytest
from datetime import datetime

from api.schemas import SourceTier, InfraStatus, RERAStatus
from etl.transformers.normalizer import (
    normalize_infra, normalize_rera, normalize_market_price, normalize_macro,
)
from etl.validators.schema_validator import (
    validate_infra, validate_rera, validate_market_price, validate_macro,
)


class TestNormalizeInfra:
    def _raw(self, **overrides):
        base = {
            "name": "Test Highway",
            "state": "Maharashtra",
            "status": "under construction",
            "infra_type": "highway",
            "length_km": "42.5",
            "cost_crore": "1200",
            "source_url": "https://nhai.gov.in/test",
            "published_date": "2024-06-01",
        }
        base.update(overrides)
        return base

    def test_basic_normalization(self):
        record = normalize_infra(self._raw(), "nhai_projects", SourceTier.OFFICIAL)
        assert record.name == "Test Highway"
        assert record.state == "Maharashtra"
        assert record.status == InfraStatus.UNDER_CONSTRUCTION
        assert record.length_km == 42.5
        assert record.cost_crore == 1200.0

    def test_official_source_high_confidence(self):
        record = normalize_infra(self._raw(), "nhai_projects", SourceTier.OFFICIAL)
        assert record.confidence >= 0.85

    def test_secondary_source_lower_confidence(self):
        record = normalize_infra(self._raw(), "economic_times_infra", SourceTier.SECONDARY)
        assert record.confidence < 0.7

    def test_announced_status_lower_confidence(self):
        record = normalize_infra(self._raw(status="announced"), "nhai_projects", SourceTier.OFFICIAL)
        uc_record = normalize_infra(self._raw(status="under construction"), "nhai_projects", SourceTier.OFFICIAL)
        assert record.confidence < uc_record.confidence

    def test_snapshot_created(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        import os
        os.makedirs("data/analytics", exist_ok=True)
        os.makedirs(f"data/raw/nhai_projects", exist_ok=True)
        record = normalize_infra(self._raw(), "nhai_projects", SourceTier.OFFICIAL)
        assert record.raw_snapshot_path is not None


class TestNormalizeRERA:
    def _raw(self, **overrides):
        base = {
            "rera_number": "P51700012345",
            "project_name": "Test Towers",
            "developer_name": "Test Dev Ltd",
            "asset_type": "residential",
            "state": "Maharashtra",
            "city": "Pune",
            "locality": "Hinjawadi",
            "rera_status": "registered",
            "registration_date": "2022-01-15",
            "promised_possession_date": "2025-12-31",
            "total_units": "200",
            "units_sold": "150",
            "complaint_count": "4",
            "published_date": "2024-10-01",
        }
        base.update(overrides)
        return base

    def test_basic_normalization(self):
        r = normalize_rera(self._raw(), "rera_maharashtra")
        assert r.rera_registration_number == "P51700012345"
        assert r.project_name == "Test Towers"
        assert r.rera_status == RERAStatus.REGISTERED
        assert r.total_units == 200
        assert r.units_sold == 150
        assert r.units_remaining == 50

    def test_possession_delay_computed(self):
        r = normalize_rera(
            self._raw(promised_possession_date="2023-06-30"),
            "rera_maharashtra"
        )
        # Date is in the past → should have delay
        assert r.possession_delay_days is not None and r.possession_delay_days > 0

    def test_revoked_status(self):
        r = normalize_rera(self._raw(rera_status="revoked"), "rera_maharashtra")
        assert r.rera_status == RERAStatus.REVOKED


class TestValidateInfra:
    def test_valid_record_passes(self):
        from tests.fixtures.demo_data import DEMO_INFRA
        result = validate_infra(DEMO_INFRA[0])
        assert result.passed is True

    def test_missing_name_fails(self):
        from tests.fixtures.demo_data import DEMO_INFRA
        import copy
        r = copy.deepcopy(DEMO_INFRA[0])
        r.name = ""
        result = validate_infra(r)
        assert result.passed is False
        assert any(i.field == "name" for i in result.errors)

    def test_freshness_decays_with_age(self):
        from tests.fixtures.demo_data import DEMO_INFRA
        import copy
        from datetime import datetime, timedelta
        r = copy.deepcopy(DEMO_INFRA[0])
        r.published_date = datetime.utcnow() - timedelta(days=200)
        result = validate_infra(r)
        assert result.freshness_score < 0.8


class TestValidateMarketPrice:
    def test_suspicious_low_price_warns(self):
        from tests.fixtures.demo_data import DEMO_PRICES
        import copy
        r = copy.deepcopy(DEMO_PRICES[0])
        r.price_per_sqft = 100.0
        result = validate_market_price(r)
        assert any(i.field == "price_per_sqft" for i in result.warnings)

    def test_negative_yield_fails(self):
        from tests.fixtures.demo_data import DEMO_PRICES
        import copy
        r = copy.deepcopy(DEMO_PRICES[0])
        r.gross_yield_pct = -1.0
        result = validate_market_price(r)
        assert result.passed is False
