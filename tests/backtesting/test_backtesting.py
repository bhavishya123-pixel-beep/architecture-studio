"""Backtesting tests: verify model meets accuracy thresholds."""

import pytest
from tests.backtesting.backtest_runner import run_all_backtests, run_backtest, HISTORICAL_CASES


class TestBacktesting:
    def test_all_cases_run_without_error(self):
        results = run_all_backtests()
        assert len(results) == len(HISTORICAL_CASES)

    def test_average_mape_below_threshold(self):
        results = run_all_backtests()
        avg_mape = sum(r.mape for r in results) / len(results)
        # Require MAPE < 30% for reasonable predictive value
        assert avg_mape < 30.0, f"Average MAPE {avg_mape:.1f}% exceeds 30% threshold"

    def test_hit_rate_above_threshold(self):
        results = run_all_backtests()
        avg_hit = sum(r.hit_rate for r in results) / len(results)
        # Require > 60% hit rate (better than random)
        assert avg_hit > 60.0, f"Average hit rate {avg_hit:.1f}% below 60% threshold"

    def test_hyderabad_orr_highest_cagr_corridor_ranked_first(self):
        # Kokapet (index 2) should have highest predicted score
        case = HISTORICAL_CASES[0]  # Hyderabad ORR
        max_score_idx = case.predicted_scores.index(max(case.predicted_scores))
        max_actual_idx = case.actual_price_cagr_pct.index(max(case.actual_price_cagr_pct))
        # Model's top pick should match actual top performer
        assert max_score_idx == max_actual_idx, (
            f"Model top: {case.corridors[max_score_idx]}, "
            f"Actual top: {case.corridors[max_actual_idx]}"
        )

    def test_all_results_have_positive_correlation(self):
        results = run_all_backtests()
        for r in results:
            if r.correlation is not None:
                assert r.correlation > 0, (
                    f"{r.case.event_name}: negative correlation {r.correlation}"
                )

    def test_lead_signal_meaningful(self):
        results = run_all_backtests()
        for r in results:
            assert r.avg_lead_months >= 6, (
                f"{r.case.event_name}: lead only {r.avg_lead_months}mo"
            )
