"""
Investment Memo Summarizer
───────────────────────────
Uses Anthropic Claude to generate narrative memo sections.
Input data is always pre-computed structured JSON — the LLM
synthesizes and explains, never invents facts.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from api.schemas import LocationScoreCard
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

SYSTEM_PROMPT = """You are a rigorous real estate investment analyst specializing in Indian markets.
You receive structured data (scores, prices, infrastructure records, RERA status) computed
by analytical systems. Your role is to:

1. Synthesize the data into clear, evidence-backed investment memo sections.
2. Never invent statistics, approval dates, project names, or yield figures not present in the data.
3. If data is missing, explicitly state so — do not substitute with assumptions.
4. Write in a calm, professional, evidence-first tone.
5. Flag speculative risks clearly.
6. Include the disclaimer that this is analytical support, not investment advice.

Output ONLY valid JSON with these keys:
summary, thesis, location_facts, infrastructure_tailwinds, market_evidence,
valuation_context, legal_rera_status, risks, watch_conditions
"""


async def generate_memo_sections(
    city: str,
    state: str,
    locality: str,
    scorecard: LocationScoreCard,
    market: dict,
    macro: dict,
    rera: dict,
    valuation: dict,
    risk: dict,
    llm_client: Any,
) -> dict[str, str]:
    """
    Generate memo text sections via the Anthropic Claude API.
    Returns a dict of section_name → narrative text.
    """
    data_bundle = {
        "location": {"city": city, "state": state, "locality": locality},
        "investment_score": {
            "final_score": scorecard.final_score,
            "final_confidence": scorecard.final_confidence,
            "data_completeness_pct": scorecard.data_completeness_pct,
            "human_review_required": scorecard.human_review_required,
            "infrastructure_uplift": scorecard.infrastructure_uplift.model_dump() if scorecard.infrastructure_uplift else None,
            "connectivity": scorecard.connectivity.model_dump() if scorecard.connectivity else None,
            "regulatory_safety": scorecard.regulatory_safety.model_dump() if scorecard.regulatory_safety else None,
            "rental_yield": scorecard.rental_yield.model_dump() if scorecard.rental_yield else None,
            "liquidity": scorecard.liquidity.model_dump() if scorecard.liquidity else None,
            "appreciation_potential": scorecard.appreciation_potential.model_dump() if scorecard.appreciation_potential else None,
        },
        "market_snapshot": market.get("snapshot", {}),
        "market_anomalies": market.get("anomalies", []),
        "macro_context": macro.get("latest_signals", {}),
        "macro_outlook": macro.get("real_estate_macro_outlook", "neutral"),
        "rera_summary": rera.get("summary", {}),
        "rera_flagged": rera.get("flagged", []),
        "valuation_scenarios": valuation.get("scenarios", []),
        "risk_level": risk.get("overall_risk_level", "UNKNOWN"),
        "risk_flags": risk.get("risk_flags", []),
    }

    user_message = (
        f"Generate an investment memo for {locality}, {city}, {state}. "
        f"Use only the following data — do not add information not present here:\n\n"
        f"{json.dumps(data_bundle, indent=2, default=str)}\n\n"
        f"Return a JSON object with keys: summary, thesis, location_facts, "
        f"infrastructure_tailwinds, market_evidence, valuation_context, "
        f"legal_rera_status, risks, watch_conditions."
    )

    try:
        response = llm_client.messages.create(
            model=settings.llm_model,
            max_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        content = response.content[0].text
        # Strip markdown code fences if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        return json.loads(content.strip())

    except json.JSONDecodeError as e:
        logger.error(f"LLM returned invalid JSON: {e}")
        return _empty_sections()
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return _empty_sections()


def _empty_sections() -> dict[str, str]:
    return {
        "summary": "LLM narrative unavailable. See structured score data.",
        "thesis": "",
        "location_facts": "",
        "infrastructure_tailwinds": "",
        "market_evidence": "",
        "valuation_context": "",
        "legal_rera_status": "",
        "risks": "",
        "watch_conditions": "",
    }
