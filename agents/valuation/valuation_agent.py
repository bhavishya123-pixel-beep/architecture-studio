"""
Valuation Agent
────────────────
Produces scenario-based investment analysis:
- Base / bull / bear price appreciation scenarios
- Gross and net yield estimates
- Holding period cash flow
- Transaction cost estimates
- Liquidity-adjusted return

Purely deterministic. LLM is not invoked here.
"""

from __future__ import annotations

import time
from typing import Optional

from agents.base import BaseAgent, AgentOutput
from api.schemas import MarketPriceRecord, MacroSignalRecord, InvestmentScenario


# India transaction cost estimates (% of deal value)
TRANSACTION_COSTS = {
    "stamp_duty_range": (3.0, 8.0),       # varies by state
    "registration_fee_pct": 1.0,
    "brokerage_pct": 1.0,
    "gst_on_uc_pct": 5.0,                 # only for under-construction
    "maintenance_deposit_months": 3,
}

# Net yield deduction assumptions
OPERATING_COST_RATIO = 0.20  # 20% of gross rent for maintenance, tax, vacancy


class ValuationAgent(BaseAgent):
    def __init__(self):
        super().__init__("ValuationAgent")

    async def run(
        self,
        price_records: list[MarketPriceRecord],
        macro_signals: list[MacroSignalRecord],
        holding_years: int = 5,
    ) -> AgentOutput:
        t0 = time.perf_counter()
        try:
            prices = [r.price_per_sqft for r in price_records if r.price_per_sqft]
            yields = [r.gross_yield_pct for r in price_records if r.gross_yield_pct]
            yoy_list = [r.price_per_sqft_yoy_pct for r in price_records if r.price_per_sqft_yoy_pct]

            if not prices:
                return self._ok(
                    result={"data_gap": True, "message": "No price data for valuation."},
                    confidence=0.0,
                )

            avg_price = sum(prices) / len(prices)
            avg_yield = sum(yields) / len(yields) if yields else None
            avg_yoy = sum(yoy_list) / len(yoy_list) if yoy_list else 7.0  # conservative default

            # Repo rate context
            repo_rate = None
            for m in macro_signals:
                if m.signal_type == "repo_rate":
                    repo_rate = m.value
                    break

            scenarios = self._build_scenarios(avg_price, avg_yield, avg_yoy, holding_years, repo_rate)
            transaction_costs = self._estimate_transaction_costs(avg_price)
            cashflow = self._cashflow_summary(avg_price, avg_yield, holding_years)

            ms = (time.perf_counter() - t0) * 1000
            return self._ok(
                result={
                    "entry_price_per_sqft": round(avg_price, 0),
                    "avg_gross_yield_pct": round(avg_yield, 2) if avg_yield else None,
                    "avg_net_yield_pct": round(avg_yield * (1 - OPERATING_COST_RATIO), 2) if avg_yield else None,
                    "historical_yoy_cagr": round(avg_yoy, 2),
                    "scenarios": [s.model_dump() for s in scenarios],
                    "transaction_costs_estimate": transaction_costs,
                    "cashflow_summary": cashflow,
                    "data_gap": False,
                },
                evidence_ids=[r.id for r in price_records],
                sources=list({r.source_id for r in price_records}),
                confidence=0.70,
                processing_ms=ms,
            )

        except Exception as e:
            return self._fail(str(e))

    def _build_scenarios(
        self,
        entry_price: float,
        gross_yield: Optional[float],
        hist_yoy: float,
        years: int,
        repo_rate: Optional[float],
    ) -> list[InvestmentScenario]:
        gy = gross_yield or 3.0
        ny = gy * (1 - OPERATING_COST_RATIO)

        def exit_price(cagr: float) -> float:
            return round(entry_price * ((1 + cagr / 100) ** years), 0)

        def simple_irr(cagr: float, net_y: float) -> float:
            # Simplified: geometric average of capital + income return
            return round(((1 + cagr / 100) * (1 + net_y / 100)) ** (1 / years) - 1) * 100

        # Bear: rate stays high, infra delayed, modest appreciation
        bear_cagr = max(hist_yoy * 0.4, 2.0)
        # Base: moderate infra uplift, stable macro
        base_cagr = max(hist_yoy * 0.85, 5.0)
        # Bull: infra completes on time, rate cut, strong absorption
        bull_cagr = hist_yoy * 1.3

        if repo_rate and repo_rate > 7.0:
            base_cagr *= 0.85  # adjust down for tight money

        return [
            InvestmentScenario(
                label="bear",
                assumption="Infrastructure delayed; rates stay elevated; weak absorption.",
                cagr_pct=round(bear_cagr, 2),
                holding_years=years,
                exit_price_per_sqft=exit_price(bear_cagr),
                gross_yield_pct=round(gy * 0.9, 2),
                net_yield_pct=round(ny * 0.9, 2),
            ),
            InvestmentScenario(
                label="base",
                assumption="Infrastructure completes with 1-year delay; rates moderate; steady demand.",
                cagr_pct=round(base_cagr, 2),
                holding_years=years,
                exit_price_per_sqft=exit_price(base_cagr),
                gross_yield_pct=round(gy, 2),
                net_yield_pct=round(ny, 2),
            ),
            InvestmentScenario(
                label="bull",
                assumption="Infrastructure on time; rate cut; strong migration and job creation.",
                cagr_pct=round(bull_cagr, 2),
                holding_years=years,
                exit_price_per_sqft=exit_price(bull_cagr),
                gross_yield_pct=round(gy * 1.1, 2),
                net_yield_pct=round(ny * 1.1, 2),
            ),
        ]

    def _estimate_transaction_costs(self, price_per_sqft: float) -> dict:
        # Assumes 1000 sqft unit for illustration
        deal_value = price_per_sqft * 1000
        avg_stamp = 6.0  # national average approximation
        return {
            "assumed_unit_sqft": 1000,
            "deal_value_approx": round(deal_value, 0),
            "stamp_duty_pct_range": TRANSACTION_COSTS["stamp_duty_range"],
            "stamp_duty_estimate": round(deal_value * avg_stamp / 100, 0),
            "registration_fee": round(deal_value * TRANSACTION_COSTS["registration_fee_pct"] / 100, 0),
            "brokerage": round(deal_value * TRANSACTION_COSTS["brokerage_pct"] / 100, 0),
            "total_cost_estimate": round(
                deal_value * (avg_stamp + 1.0 + 1.0) / 100, 0
            ),
            "note": "Actual stamp duty varies by state. Consult a tax advisor.",
        }

    def _cashflow_summary(
        self, price_per_sqft: float, gross_yield: Optional[float], years: int
    ) -> dict:
        gy = gross_yield or 3.0
        annual_gross_rent = price_per_sqft * 1000 * gy / 100
        annual_net_rent = annual_gross_rent * (1 - OPERATING_COST_RATIO)
        total_net_rental_income = annual_net_rent * years
        return {
            "annual_gross_rent_1000sqft": round(annual_gross_rent, 0),
            "annual_net_rent_1000sqft": round(annual_net_rent, 0),
            f"total_net_rental_{years}yr": round(total_net_rental_income, 0),
            "operating_cost_assumption": f"{OPERATING_COST_RATIO * 100:.0f}% of gross rent",
        }
