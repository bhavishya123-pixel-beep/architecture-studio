"""Data source registry. Every source is declared here with its tier, URL, and fetch config."""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional


class SourceTier(IntEnum):
    OFFICIAL = 1      # government portals, central bank
    VERIFIED = 2      # registered listing platforms, exchanges
    SECONDARY = 3     # news, commentary, unverified feeds


@dataclass(frozen=True)
class DataSource:
    id: str
    name: str
    tier: SourceTier
    base_url: str
    description: str
    fetch_type: str          # "api" | "scrape" | "pdf" | "rss" | "manual"
    refresh_cadence: str     # human label: "daily" | "weekly" | "on-release"
    requires_auth: bool = False
    auth_env_key: Optional[str] = None
    notes: str = ""


SOURCE_REGISTRY: dict[str, DataSource] = {
    # ── Infrastructure ────────────────────────────────────────────────────
    "nhai_projects": DataSource(
        id="nhai_projects",
        name="NHAI Project Dashboard",
        tier=SourceTier.OFFICIAL,
        base_url="https://www.nhai.gov.in/en-us/content/projects",
        description="NHAI live project listings: NH widening, greenfield expressways, ring roads",
        fetch_type="scrape",
        refresh_cadence="daily",
        notes="Parse project tables; extract state, length, cost, status, tender date",
    ),
    "morth_roads": DataSource(
        id="morth_roads",
        name="MoRTH Road Project Updates",
        tier=SourceTier.OFFICIAL,
        base_url="https://morth.nic.in/road-development",
        description="Ministry of Road Transport highway and road project notices",
        fetch_type="scrape",
        refresh_cadence="weekly",
    ),
    "gatishakti": DataSource(
        id="gatishakti",
        name="PM GatiShakti NMP Portal",
        tier=SourceTier.OFFICIAL,
        base_url="https://pmgatishakti.gov.in",
        description="National Master Plan for multi-modal connectivity",
        fetch_type="scrape",
        refresh_cadence="weekly",
    ),
    "metro_announcements": DataSource(
        id="metro_announcements",
        name="DMRC / Metro Rail Authority Press Releases",
        tier=SourceTier.OFFICIAL,
        base_url="https://www.dmrc.org/web/pressrelease.php",
        description="Metro phase expansion, new corridors, station commissioning notices",
        fetch_type="scrape",
        refresh_cadence="daily",
        notes="Combine with city-specific metro rail authority feeds",
    ),
    "airport_aai": DataSource(
        id="airport_aai",
        name="AAI Airport Expansion News",
        tier=SourceTier.OFFICIAL,
        base_url="https://www.aai.aero/en/news-updates",
        description="Airport Authority of India: new terminals, greenfield airports, capacity expansion",
        fetch_type="scrape",
        refresh_cadence="weekly",
    ),

    # ── RERA Portals ─────────────────────────────────────────────────────
    "rera_maharashtra": DataSource(
        id="rera_maharashtra",
        name="MahaRERA",
        tier=SourceTier.OFFICIAL,
        base_url="https://maharera.mahaonline.gov.in",
        description="Maharashtra RERA project registrations, complaints, possession status",
        fetch_type="scrape",
        refresh_cadence="daily",
    ),
    "rera_karnataka": DataSource(
        id="rera_karnataka",
        name="K-RERA",
        tier=SourceTier.OFFICIAL,
        base_url="https://rera.karnataka.gov.in",
        description="Karnataka RERA project database",
        fetch_type="scrape",
        refresh_cadence="daily",
    ),
    "rera_delhi": DataSource(
        id="rera_delhi",
        name="RERA Delhi",
        tier=SourceTier.OFFICIAL,
        base_url="https://rera.delhi.gov.in",
        description="Delhi RERA project registrations and order database",
        fetch_type="scrape",
        refresh_cadence="daily",
    ),
    "rera_up": DataSource(
        id="rera_up",
        name="UP RERA",
        tier=SourceTier.OFFICIAL,
        base_url="https://www.up-rera.in",
        description="Uttar Pradesh RERA — covers NCR periphery, Noida, Greater Noida, Lucknow",
        fetch_type="scrape",
        refresh_cadence="daily",
    ),
    "rera_telangana": DataSource(
        id="rera_telangana",
        name="TSRERA",
        tier=SourceTier.OFFICIAL,
        base_url="https://rera.telangana.gov.in",
        description="Telangana State RERA — covers Hyderabad metro",
        fetch_type="scrape",
        refresh_cadence="daily",
    ),
    "rera_gujarat": DataSource(
        id="rera_gujarat",
        name="GujRERA",
        tier=SourceTier.OFFICIAL,
        base_url="https://gujrera.gujarat.gov.in",
        description="Gujarat RERA — covers Ahmedabad, Surat, Vadodara",
        fetch_type="scrape",
        refresh_cadence="daily",
    ),

    # ── Macro / Economic ─────────────────────────────────────────────────
    "rbi_mpc": DataSource(
        id="rbi_mpc",
        name="RBI Monetary Policy Committee Resolutions",
        tier=SourceTier.OFFICIAL,
        base_url="https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx",
        description="RBI MPC rate decisions, housing credit commentary, CPI context",
        fetch_type="scrape",
        refresh_cadence="on-release",
    ),
    "rbi_housing_index": DataSource(
        id="rbi_housing_index",
        name="RBI House Price Index",
        tier=SourceTier.OFFICIAL,
        base_url="https://www.rbi.org.in/scripts/AnnualReportMainPage.aspx",
        description="RBI quarterly Housing Price Index across 50 cities",
        fetch_type="pdf",
        refresh_cadence="quarterly",
    ),
    "mospi_cpi": DataSource(
        id="mospi_cpi",
        name="MOSPI CPI Releases",
        tier=SourceTier.OFFICIAL,
        base_url="https://mospi.gov.in/consumer-price-indices",
        description="CPI general + housing sub-component inflation",
        fetch_type="pdf",
        refresh_cadence="monthly",
    ),
    "india_budget": DataSource(
        id="india_budget",
        name="India Union Budget Infrastructure Section",
        tier=SourceTier.OFFICIAL,
        base_url="https://indiabudget.gov.in",
        description="Annual budget: capex, infra allocation, housing scheme announcements",
        fetch_type="pdf",
        refresh_cadence="on-release",
    ),

    # ── Listing / Market Feeds (Verified) ────────────────────────────────
    "propequity_feed": DataSource(
        id="propequity_feed",
        name="PropEquity Licensed Data Feed",
        tier=SourceTier.VERIFIED,
        base_url="https://propequity.in",
        description="Licensed residential price, absorption, launch data across cities",
        fetch_type="api",
        refresh_cadence="weekly",
        requires_auth=True,
        auth_env_key="PROPEQUITY_API_KEY",
        notes="Requires paid subscription. Use only if license is active.",
    ),
    "govt_open_data": DataSource(
        id="govt_open_data",
        name="India Open Government Data Portal",
        tier=SourceTier.OFFICIAL,
        base_url="https://data.gov.in",
        description="Open datasets: land records, land use, urban surveys, NHB indices",
        fetch_type="api",
        refresh_cadence="varies",
        requires_auth=True,
        auth_env_key="DATA_GOV_IN_API_KEY",
    ),

    # ── News / Secondary ─────────────────────────────────────────────────
    "hindu_realestate": DataSource(
        id="hindu_realestate",
        name="The Hindu BusinessLine Real Estate",
        tier=SourceTier.SECONDARY,
        base_url="https://www.thehindubusinessline.com/economy/real-estate/",
        description="News reports on project launches, infra deals, regulatory changes",
        fetch_type="rss",
        refresh_cadence="daily",
        notes="Secondary only. Use for enrichment; never as primary source.",
    ),
    "economic_times_infra": DataSource(
        id="economic_times_infra",
        name="Economic Times Infrastructure",
        tier=SourceTier.SECONDARY,
        base_url="https://economictimes.indiatimes.com/industry/transportation/railways",
        description="Railway, metro, airport news — for enrichment only",
        fetch_type="rss",
        refresh_cadence="daily",
        notes="Secondary. Cross-validate with official NHAI/AAI/metro sources.",
    ),
}


def get_sources_by_tier(tier: SourceTier) -> list[DataSource]:
    return [s for s in SOURCE_REGISTRY.values() if s.tier == tier]


def get_source(source_id: str) -> DataSource:
    if source_id not in SOURCE_REGISTRY:
        raise KeyError(f"Unknown source: {source_id}")
    return SOURCE_REGISTRY[source_id]
