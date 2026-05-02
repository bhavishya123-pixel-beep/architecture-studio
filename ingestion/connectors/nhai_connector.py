"""
NHAI Project Dashboard Connector
──────────────────────────────────
Scrapes NHAI's project listings and normalizes to InfrastructureRecord.
Uses controlled, respectful scraping with explicit source attribution.

Only fetches public data from nhai.gov.in.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional
import httpx
from bs4 import BeautifulSoup

from etl.transformers.normalizer import normalize_infra
from api.schemas import InfrastructureRecord, SourceTier

logger = logging.getLogger(__name__)

NHAI_BASE = "https://www.nhai.gov.in"
HEADERS = {
    "User-Agent": "IndiaREIS/1.0 (Research; contact: admin@example.com)",
    "Accept": "text/html",
}
REQUEST_TIMEOUT = 30
CRAWL_DELAY_SECONDS = 2  # respectful delay between requests


async def fetch_nhai_projects(limit: int = 100) -> list[InfrastructureRecord]:
    """
    Fetch NHAI project listings and return normalized InfrastructureRecord list.
    Falls back to empty list on network errors — never crashes the pipeline.
    """
    records: list[InfrastructureRecord] = []

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, headers=HEADERS) as client:
            resp = await client.get(f"{NHAI_BASE}/en-us/content/projects")
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            raw_projects = _parse_project_table(soup)

        for raw in raw_projects[:limit]:
            try:
                record = normalize_infra(raw, source_id="nhai_projects", source_tier=SourceTier.OFFICIAL)
                records.append(record)
            except Exception as e:
                logger.warning(f"Failed to normalize NHAI record: {e} | raw={raw}")

        logger.info(f"NHAI connector: {len(records)} records fetched")

    except httpx.HTTPStatusError as e:
        logger.error(f"NHAI HTTP error: {e.response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"NHAI network error: {e}")
    except Exception as e:
        logger.error(f"NHAI connector unexpected error: {e}")

    return records


def _parse_project_table(soup: BeautifulSoup) -> list[dict]:
    """
    Parse NHAI project table HTML into list of raw dicts.
    Structure is best-effort; fields may be None if the page changes.
    """
    projects = []

    # NHAI tables typically have columns: Project Name, State, Length, Cost, Status
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        headers = []
        for i, row in enumerate(rows):
            cells = row.find_all(["th", "td"])
            if i == 0:
                headers = [c.get_text(strip=True).lower() for c in cells]
                continue
            if not headers or not cells:
                continue

            row_data = {headers[j]: cells[j].get_text(strip=True) for j in range(min(len(headers), len(cells)))}

            # Map to our expected raw dict keys
            project = {
                "name": row_data.get("project name") or row_data.get("name", ""),
                "state": row_data.get("state", ""),
                "length_km": row_data.get("length (km)") or row_data.get("length", ""),
                "cost_crore": row_data.get("cost (cr)") or row_data.get("cost", ""),
                "status": row_data.get("status", "announced"),
                "infra_type": "highway",
                "source_url": f"{NHAI_BASE}/en-us/content/projects",
                "published_date": datetime.utcnow().isoformat(),
                "executing_agency": "NHAI",
            }
            if project["name"]:
                projects.append(project)

    return projects
