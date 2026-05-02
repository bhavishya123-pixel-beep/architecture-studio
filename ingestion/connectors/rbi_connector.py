"""
RBI / MOSPI Macro Data Connector
──────────────────────────────────
Fetches monetary policy decisions, housing price index, and CPI data.
All from official RBI and MOSPI public releases.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from etl.transformers.normalizer import normalize_macro
from api.schemas import MacroSignalRecord

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "IndiaREIS/1.0 (Research; contact: admin@example.com)"}
TIMEOUT = 30


async def fetch_rbi_repo_rate() -> Optional[MacroSignalRecord]:
    """Fetch latest RBI repo rate from MPC resolution page."""
    url = "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx"
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, headers=HEADERS) as client:
            resp = await client.get(url)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        # RBI press releases typically mention "repo rate at X.XX per cent"
        text = soup.get_text()
        match = re.search(r"repo rate.*?(\d+\.\d+)\s*per\s*cent", text, re.IGNORECASE)

        if match:
            rate = float(match.group(1))
            raw = {
                "signal_type": "repo_rate",
                "value": rate,
                "unit": "pct",
                "period": datetime.utcnow().strftime("%Y-%m"),
                "direction": "stable",
                "source_url": url,
                "published_date": datetime.utcnow().isoformat(),
            }
            return normalize_macro(raw, source_id="rbi_mpc")

    except Exception as e:
        logger.error(f"RBI repo rate fetch failed: {e}")

    return None


async def fetch_mospi_cpi() -> list[MacroSignalRecord]:
    """Fetch latest CPI headline and housing sub-component from MOSPI."""
    url = "https://mospi.gov.in/consumer-price-indices"
    records = []

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, headers=HEADERS) as client:
            resp = await client.get(url)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text()

        # Parse general CPI
        cpi_match = re.search(r"CPI.*?(\d+\.\d+)\s*(?:per cent|%)", text, re.IGNORECASE)
        if cpi_match:
            raw = {
                "signal_type": "cpi",
                "value": float(cpi_match.group(1)),
                "unit": "pct",
                "period": datetime.utcnow().strftime("%Y-%m"),
                "source_url": url,
                "published_date": datetime.utcnow().isoformat(),
            }
            records.append(normalize_macro(raw, source_id="mospi_cpi"))

        # Parse housing sub-component if available
        housing_match = re.search(
            r"housing.*?(\d+\.\d+)\s*(?:per cent|%)", text, re.IGNORECASE
        )
        if housing_match:
            raw = {
                "signal_type": "housing_cpi",
                "value": float(housing_match.group(1)),
                "unit": "pct",
                "period": datetime.utcnow().strftime("%Y-%m"),
                "source_url": url,
                "published_date": datetime.utcnow().isoformat(),
            }
            records.append(normalize_macro(raw, source_id="mospi_cpi"))

    except Exception as e:
        logger.error(f"MOSPI CPI fetch failed: {e}")

    return records
