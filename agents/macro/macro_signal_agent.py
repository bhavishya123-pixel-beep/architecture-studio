"""
Macro Signal Agent
───────────────────
Processes RBI, MOSPI, and Budget macro data.
Produces a structured macro context that other agents consume.
"""

from __future__ import annotations

import time
from typing import Optional

from agents.base import BaseAgent, AgentOutput
from api.schemas import MacroSignalRecord


class MacroSignalAgent(BaseAgent):
    def __init__(self):
        super().__init__("MacroSignalAgent")

    async def run(
        self,
        macro_records: list[MacroSignalRecord],
    ) -> AgentOutput:
        t0 = time.perf_counter()
        try:
            context = self._build_macro_context(macro_records)
            ms = (time.perf_counter() - t0) * 1000

            return self._ok(
                result=context,
                evidence_ids=[r.id for r in macro_records],
                sources=list({r.source_id for r in macro_records}),
                confidence=0.92,
                processing_ms=ms,
            )
        except Exception as e:
            return self._fail(str(e))

    def _build_macro_context(self, records: list[MacroSignalRecord]) -> dict:
        by_type: dict[str, list[MacroSignalRecord]] = {}
        for r in records:
            by_type.setdefault(r.signal_type, []).append(r)

        latest: dict[str, dict] = {}
        for sig_type, recs in by_type.items():
            recs_sorted = sorted(recs, key=lambda x: x.published_date, reverse=True)
            r = recs_sorted[0]
            latest[sig_type] = {
                "value": r.value,
                "unit": r.unit,
                "period": r.period,
                "direction": r.direction,
                "yoy_change": r.yoy_change,
                "commentary": r.rbi_commentary,
                "source": r.source_id,
                "freshness_score": r.freshness_score,
            }

        # Derived interpretation for real estate
        repo_rate = latest.get("repo_rate", {}).get("value")
        cpi = latest.get("cpi", {}).get("value")
        housing_cpi = latest.get("housing_cpi", {}).get("value")

        re_macro_outlook = "neutral"
        notes = []

        if repo_rate is not None:
            if repo_rate < 6.0:
                re_macro_outlook = "positive"
                notes.append(f"Repo rate {repo_rate:.2f}% — accommodative; mortgage demand supported")
            elif repo_rate > 7.0:
                re_macro_outlook = "cautious"
                notes.append(f"Repo rate {repo_rate:.2f}% — elevated; affordability pressure")

        if housing_cpi is not None and housing_cpi > 6.0:
            notes.append(f"Housing CPI {housing_cpi:.1f}% — rental market inflationary")
            if re_macro_outlook != "cautious":
                re_macro_outlook = "positive"

        if cpi is not None and cpi > 7.0:
            notes.append(f"General CPI {cpi:.1f}% — high inflation constrains RBI rate relief")
            re_macro_outlook = "cautious"

        return {
            "latest_signals": latest,
            "real_estate_macro_outlook": re_macro_outlook,
            "analysis_notes": notes,
            "signals_count": len(records),
            "data_gap": len(records) == 0,
        }
