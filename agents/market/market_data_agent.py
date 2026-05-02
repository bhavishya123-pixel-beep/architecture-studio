"""
Market Data Agent
──────────────────
Compiles market price, rent, absorption, and supply data
for a given city/locality. Surfaces anomalies and data gaps.
"""

from __future__ import annotations

import time
from typing import Optional

from agents.base import BaseAgent, AgentOutput
from api.schemas import MarketPriceRecord, AssetType


class MarketDataAgent(BaseAgent):
    def __init__(self):
        super().__init__("MarketDataAgent")

    async def run(
        self,
        price_records: list[MarketPriceRecord],
        city: Optional[str] = None,
        locality: Optional[str] = None,
    ) -> AgentOutput:
        t0 = time.perf_counter()
        try:
            if city:
                price_records = [r for r in price_records if r.city.lower() == city.lower()]
            if locality:
                price_records = [
                    r for r in price_records
                    if locality.lower() in r.locality.lower()
                ]

            if not price_records:
                return self._ok(
                    result={
                        "data_gap": True,
                        "message": f"No market data for {city}/{locality}",
                    },
                    confidence=0.0,
                )

            snapshot = self._build_snapshot(price_records)
            anomalies = self._detect_anomalies(price_records)

            ms = (time.perf_counter() - t0) * 1000
            return self._ok(
                result={
                    "snapshot": snapshot,
                    "anomalies": anomalies,
                    "records_analyzed": len(price_records),
                    "data_gap": False,
                },
                evidence_ids=[r.id for r in price_records],
                sources=list({r.source_id for r in price_records}),
                confidence=self._avg_confidence(price_records),
                processing_ms=ms,
            )
        except Exception as e:
            return self._fail(str(e))

    def _build_snapshot(self, records: list[MarketPriceRecord]) -> dict:
        prices = [r.price_per_sqft for r in records if r.price_per_sqft]
        rents = [r.monthly_rent_per_sqft for r in records if r.monthly_rent_per_sqft]
        yields = [r.gross_yield_pct for r in records if r.gross_yield_pct]
        absorptions = [r.absorption_rate_pct for r in records if r.absorption_rate_pct]
        yoy_changes = [r.price_per_sqft_yoy_pct for r in records if r.price_per_sqft_yoy_pct]

        def safe_avg(lst): return round(sum(lst) / len(lst), 2) if lst else None
        def safe_range(lst): return (min(lst), max(lst)) if lst else None

        return {
            "avg_price_per_sqft": safe_avg(prices),
            "price_range": safe_range(prices),
            "avg_rent_per_sqft_monthly": safe_avg(rents),
            "avg_gross_yield_pct": safe_avg(yields),
            "avg_absorption_rate_pct": safe_avg(absorptions),
            "avg_price_yoy_pct": safe_avg(yoy_changes),
            "total_inventory": sum(r.inventory_units or 0 for r in records),
            "total_new_launches": sum(r.new_launches_units or 0 for r in records),
            "unsold_months_avg": safe_avg(
                [r.unsold_inventory_months for r in records if r.unsold_inventory_months]
            ),
            "latest_period": max(r.observation_period for r in records),
            "segments_covered": list({r.segment for r in records}),
        }

    def _detect_anomalies(self, records: list[MarketPriceRecord]) -> list[str]:
        anomalies = []
        prices = [r.price_per_sqft for r in records if r.price_per_sqft]
        yields = [r.gross_yield_pct for r in records if r.gross_yield_pct]
        yoy = [r.price_per_sqft_yoy_pct for r in records if r.price_per_sqft_yoy_pct]

        if yoy and max(yoy) > 25:
            anomalies.append(f"Extremely high YoY price growth {max(yoy):.1f}% — verify source")
        if yields and min(yields) < 1.0:
            anomalies.append(f"Yield dip below 1% ({min(yields):.2f}%) — speculative premium likely")
        if yields and max(yields) > 12:
            anomalies.append(f"Yield spike {max(yields):.1f}% — data quality check recommended")

        # Price-rent decoupling
        for r in records:
            if r.price_per_sqft and r.monthly_rent_per_sqft:
                implied_yield = (r.monthly_rent_per_sqft * 12) / r.price_per_sqft * 100
                if r.gross_yield_pct and abs(implied_yield - r.gross_yield_pct) > 2.0:
                    anomalies.append(
                        f"{r.locality}: price/rent imply {implied_yield:.2f}% yield "
                        f"vs reported {r.gross_yield_pct:.2f}% — cross-check needed"
                    )

        return anomalies

    def _avg_confidence(self, records: list[MarketPriceRecord]) -> float:
        if not records:
            return 0.0
        return round(sum(r.confidence for r in records) / len(records), 3)
