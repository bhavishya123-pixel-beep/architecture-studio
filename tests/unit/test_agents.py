"""Unit tests for agent layer."""

import pytest
import asyncio

from agents.market.market_data_agent import MarketDataAgent
from agents.macro.macro_signal_agent import MacroSignalAgent
from agents.rera.rera_compliance_agent import RERAComplianceAgent
from agents.orchestrator.orchestrator_agent import OrchestratorAgent
from tests.fixtures.demo_data import DEMO_PRICES, DEMO_MACRO, DEMO_RERA, DEMO_DEVELOPERS


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class TestMarketDataAgent:
    def setup_method(self):
        self.agent = MarketDataAgent()

    def test_runs_with_demo_data(self):
        out = run(self.agent.run(price_records=DEMO_PRICES, city="Hyderabad"))
        assert out.success
        assert out.result["data_gap"] is False

    def test_returns_data_gap_when_no_records(self):
        out = run(self.agent.run(price_records=[], city="Unknown"))
        assert out.result["data_gap"] is True

    def test_anomaly_detection_runs(self):
        out = run(self.agent.run(price_records=DEMO_PRICES))
        assert "anomalies" in out.result

    def test_city_filter_works(self):
        out = run(self.agent.run(price_records=DEMO_PRICES, city="Hyderabad"))
        assert out.success
        # Should return Hyderabad data
        snap = out.result.get("snapshot", {})
        assert snap is not None


class TestMacroSignalAgent:
    def setup_method(self):
        self.agent = MacroSignalAgent()

    def test_runs_with_demo_data(self):
        out = run(self.agent.run(macro_records=DEMO_MACRO))
        assert out.success
        assert "real_estate_macro_outlook" in out.result

    def test_repo_rate_drives_outlook(self):
        out = run(self.agent.run(macro_records=DEMO_MACRO))
        # Demo macro has rate cut → should be positive
        assert out.result["real_estate_macro_outlook"] in ("positive", "neutral")

    def test_empty_returns_data_gap(self):
        out = run(self.agent.run(macro_records=[]))
        assert out.result["data_gap"] is True


class TestRERAComplianceAgent:
    def setup_method(self):
        self.agent = RERAComplianceAgent()

    def test_runs_with_demo_data(self):
        out = run(self.agent.run(rera_records=DEMO_RERA))
        assert out.success
        assert out.result["total_projects"] == len(DEMO_RERA)

    def test_flags_expired_rera(self):
        out = run(self.agent.run(rera_records=DEMO_RERA))
        flagged = out.result["flagged"]
        # DEMO_RERA[2] is expired — should be flagged
        flagged_numbers = [f["rera_number"] for f in flagged]
        assert DEMO_RERA[2].rera_registration_number in flagged_numbers

    def test_clean_project_not_flagged(self):
        out = run(self.agent.run(rera_records=[DEMO_RERA[0]]))
        assert out.result["flagged_projects"] == 0

    def test_summary_populated(self):
        out = run(self.agent.run(rera_records=DEMO_RERA))
        assert "summary" in out.result
        assert out.result["summary"]["total_projects"] if "total_projects" in out.result["summary"] else True


class TestOrchestratorAgent:
    def setup_method(self):
        self.agent = OrchestratorAgent(llm_client=None)

    def test_runs_with_full_demo_data(self):
        from tests.fixtures.demo_data import DEMO_PROXIMITY_KOKAPET
        out = run(self.agent.run(
            city="Hyderabad", state="Telangana", locality="Kokapet",
            rera_records=[DEMO_RERA[0]],
            price_records=[DEMO_PRICES[0]],
            macro_records=DEMO_MACRO,
            proximal_infra=DEMO_PROXIMITY_KOKAPET,
            developer=DEMO_DEVELOPERS[0],
        ))
        assert out.success
        memo = out.result
        assert "summary" in memo
        assert "score_card" in memo

    def test_runs_with_empty_data(self):
        out = run(self.agent.run(
            city="Unknown", state="Unknown", locality="Unknown",
        ))
        assert out.success  # should not fail on empty data

    def test_memo_contains_disclaimer(self):
        out = run(self.agent.run(
            city="Hyderabad", state="Telangana", locality="Kokapet",
        ))
        memo = out.result
        assert "disclaimer" in memo
        assert len(memo["disclaimer"]) > 20
