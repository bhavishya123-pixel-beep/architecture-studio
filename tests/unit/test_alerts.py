"""Unit tests for the alert rules engine."""

import pytest
from datetime import datetime, date
from copy import deepcopy

from api.schemas import RERARecord, MarketPriceRecord, MacroSignalRecord, RERAStatus, AssetType, SourceTier
from alerts.rules.alert_rules import (
    check_possession_slip, check_rera_status_change,
    check_price_spike, check_yield_compression,
    check_macro_rate_change, check_launch_spike,
)
from tests.fixtures.demo_data import DEMO_RERA, DEMO_PRICES, DEMO_MACRO


class TestPossessionSlip:
    def test_no_alert_when_no_previous(self):
        assert check_possession_slip(DEMO_RERA[0], None) is None

    def test_no_alert_when_date_unchanged(self):
        assert check_possession_slip(DEMO_RERA[0], DEMO_RERA[0]) is None

    def test_alert_when_date_pushed(self):
        current = deepcopy(DEMO_RERA[0])
        prev = deepcopy(DEMO_RERA[0])
        current.promised_possession_date = date(2026, 6, 30)
        prev.promised_possession_date = date(2025, 12, 31)
        alert = check_possession_slip(current, prev)
        assert alert is not None
        assert "slipped" in alert.title.lower()
        assert alert.data["slip_days"] == 181

    def test_high_severity_for_large_slip(self):
        current = deepcopy(DEMO_RERA[0])
        prev = deepcopy(DEMO_RERA[0])
        current.promised_possession_date = date(2027, 1, 1)
        prev.promised_possession_date = date(2025, 12, 31)
        alert = check_possession_slip(current, prev)
        assert alert.severity.value == "high"


class TestRERAStatusChange:
    def test_no_alert_for_same_status(self):
        assert check_rera_status_change(DEMO_RERA[0], DEMO_RERA[0]) is None

    def test_high_alert_for_revocation(self):
        current = deepcopy(DEMO_RERA[0])
        current.rera_status = RERAStatus.REVOKED
        alert = check_rera_status_change(current, DEMO_RERA[0])
        assert alert is not None
        assert alert.severity.value == "high"
        assert "REVOKED" in alert.title

    def test_medium_alert_for_expiry(self):
        prev = deepcopy(DEMO_RERA[0])
        current = deepcopy(DEMO_RERA[0])
        current.rera_status = RERAStatus.EXPIRED
        alert = check_rera_status_change(current, prev)
        assert alert is not None


class TestPriceSpike:
    def test_no_alert_for_small_change(self):
        prev = deepcopy(DEMO_PRICES[0])
        prev.price_per_sqft = 9000
        assert check_price_spike(DEMO_PRICES[0], prev) is None

    def test_alert_on_large_spike(self):
        current = deepcopy(DEMO_PRICES[0])
        prev = deepcopy(DEMO_PRICES[0])
        current.price_per_sqft = 11000
        prev.price_per_sqft = 9000
        alert = check_price_spike(current, prev)
        assert alert is not None
        assert "spike" in alert.title.lower()
        assert alert.data["change_pct"] > 15

    def test_alert_on_large_drop(self):
        current = deepcopy(DEMO_PRICES[0])
        prev = deepcopy(DEMO_PRICES[0])
        current.price_per_sqft = 7000
        prev.price_per_sqft = 9200
        alert = check_price_spike(current, prev)
        assert alert is not None
        assert "drop" in alert.title.lower()


class TestYieldCompression:
    def test_no_alert_when_yield_stable(self):
        assert check_yield_compression(DEMO_PRICES[0], DEMO_PRICES[0]) is None

    def test_alert_on_compression(self):
        current = deepcopy(DEMO_PRICES[0])
        prev = deepcopy(DEMO_PRICES[0])
        current.gross_yield_pct = 2.5
        prev.gross_yield_pct = 3.4
        alert = check_yield_compression(current, prev)
        assert alert is not None
        assert alert.data["yield_delta"] < -0.5


class TestMacroRateChange:
    def test_no_alert_for_small_change(self):
        current = deepcopy(DEMO_MACRO[0])
        prev = deepcopy(DEMO_MACRO[0])
        current.value = 6.25
        prev.value = 6.35  # only 10 bps
        assert check_macro_rate_change(current, prev) is None

    def test_alert_on_25bps_cut(self):
        current = deepcopy(DEMO_MACRO[0])
        prev = deepcopy(DEMO_MACRO[0])
        current.value = 6.00
        prev.value = 6.25
        alert = check_macro_rate_change(current, prev)
        assert alert is not None
        assert "cut" in alert.title.lower()

    def test_no_alert_for_non_repo_signal(self):
        sig = deepcopy(DEMO_MACRO[1])  # CPI signal
        assert check_macro_rate_change(sig, None) is None


class TestLaunchSpike:
    def test_alert_when_launches_double(self):
        current = deepcopy(DEMO_PRICES[0])
        prev = deepcopy(DEMO_PRICES[0])
        current.new_launches_units = 1200
        prev.new_launches_units = 520
        alert = check_launch_spike(current, prev)
        assert alert is not None

    def test_no_alert_for_moderate_increase(self):
        current = deepcopy(DEMO_PRICES[0])
        prev = deepcopy(DEMO_PRICES[0])
        current.new_launches_units = 700
        prev.new_launches_units = 520
        assert check_launch_spike(current, prev) is None
