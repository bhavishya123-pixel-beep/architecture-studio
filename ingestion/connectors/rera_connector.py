"""
RERA Portal Connector
──────────────────────
Fetches project data from state RERA portals.
Each portal has a slightly different structure; this module
handles MahaRERA, UP-RERA, Karnataka-RERA, and Telangana-RERA.

All requests use public search endpoints only.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

import httpx

from etl.transformers.normalizer import normalize_rera
from api.schemas import RERARecord
from config.sources import SOURCE_REGISTRY

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "IndiaREIS/1.0 (Research; contact: admin@example.com)",
}
TIMEOUT = 30


async def fetch_rera_projects(
    portal_id: str,
    city: Optional[str] = None,
    project_name: Optional[str] = None,
    limit: int = 50,
) -> list[RERARecord]:
    """
    Fetch RERA project data from a specific state portal.
    portal_id must be a key in SOURCE_REGISTRY.
    """
    if portal_id not in SOURCE_REGISTRY:
        logger.error(f"Unknown portal: {portal_id}")
        return []

    source = SOURCE_REGISTRY[portal_id]
    records = []

    fetcher = PORTAL_FETCHERS.get(portal_id)
    if fetcher is None:
        logger.warning(f"No fetcher implemented for {portal_id}. Using generic.")
        fetcher = _generic_rera_fetcher

    try:
        raw_list = await fetcher(source.base_url, city=city, project_name=project_name, limit=limit)
        for raw in raw_list:
            raw["rera_portal"] = portal_id
            raw["source_url"] = source.base_url
            try:
                records.append(normalize_rera(raw, source_id=portal_id))
            except Exception as e:
                logger.warning(f"RERA normalize error ({portal_id}): {e}")

    except Exception as e:
        logger.error(f"RERA fetch error for {portal_id}: {e}")

    logger.info(f"RERA {portal_id}: {len(records)} records")
    return records


async def _maharera_fetcher(base_url: str, city=None, project_name=None, limit=50) -> list[dict]:
    """
    MahaRERA public project search API.
    Returns list of raw dicts.
    """
    params = {"pagesize": limit, "status": "1"}  # 1 = registered
    if city:
        params["district"] = city
    if project_name:
        params["projectname"] = project_name

    async with httpx.AsyncClient(timeout=TIMEOUT, headers=HEADERS) as client:
        resp = await client.get(f"{base_url}/api/v1/projects", params=params)
        resp.raise_for_status()
        data = resp.json()

    raw_list = []
    for item in data.get("data", [])[:limit]:
        raw_list.append({
            "rera_number": item.get("RegistrationNo"),
            "project_name": item.get("ProjectName"),
            "developer_name": item.get("PromoterName"),
            "asset_type": "residential",
            "state": "Maharashtra",
            "city": item.get("District"),
            "locality": item.get("Taluka"),
            "pin_code": item.get("PinCode"),
            "rera_status": "registered" if item.get("Status") == "1" else "expired",
            "registration_date": item.get("RegistrationDate"),
            "promised_possession_date": item.get("ProposedCompletionDate"),
            "total_units": item.get("TotalUnits"),
            "units_sold": item.get("UnitsSold"),
            "complaint_count": item.get("ComplaintCount"),
            "published_date": datetime.utcnow().isoformat(),
        })
    return raw_list


async def _generic_rera_fetcher(base_url: str, city=None, project_name=None, limit=50) -> list[dict]:
    """
    Generic fallback: returns empty list. Connector teams implement portal-specific fetchers.
    """
    logger.info(f"Generic fetcher called for {base_url} — returning empty (implement portal-specific fetcher)")
    return []


# Registry of portal-specific fetchers
PORTAL_FETCHERS = {
    "rera_maharashtra": _maharera_fetcher,
    # Add other portals as implemented:
    # "rera_karnataka": _krera_fetcher,
    # "rera_up": _uprera_fetcher,
}
