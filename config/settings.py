"""Central configuration. All environment variables land here via pydantic-settings."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = "India Real Estate Intelligence OS"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    disclaimer: str = (
        "This platform provides analytical support only. It does not constitute "
        "financial advice, legal advice, or guaranteed investment returns. "
        "Always conduct independent due diligence before transacting."
    )

    # ── Database ─────────────────────────────────────────────────────────────
    postgres_dsn: str = Field(
        default="postgresql://reisuser:reispass@localhost:5432/reis",
        validation_alias="POSTGRES_DSN",
    )
    duckdb_path: str = Field(default="data/analytics/reis_analytics.duckdb")
    redis_url: str = Field(default="redis://localhost:6379/0")

    # ── Vector Store ─────────────────────────────────────────────────────────
    vector_store_type: str = "faiss"  # "faiss" | "chroma"
    chroma_host: Optional[str] = None
    faiss_index_path: str = "data/vectors/reis.index"
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    # ── LLM ──────────────────────────────────────────────────────────────────
    anthropic_api_key: Optional[str] = Field(default=None, validation_alias="ANTHROPIC_API_KEY")
    llm_model: str = "claude-sonnet-4-6"
    llm_max_tokens: int = 4096
    llm_temperature: float = 0.1  # low temp for analytical tasks

    # ── Ingestion schedule (cron expressions) ────────────────────────────────
    nhai_crawl_schedule: str = "0 6 * * *"          # daily 6 AM
    rera_crawl_schedule: str = "0 7 * * *"          # daily 7 AM
    rbi_crawl_schedule: str = "0 8 * * 1"           # Monday 8 AM
    news_crawl_schedule: str = "0 */4 * * *"        # every 4 hours
    price_feed_schedule: str = "0 9 * * *"          # daily 9 AM
    alert_evaluation_schedule: str = "*/15 * * * *" # every 15 min

    # ── Scoring weights (must sum to 1.0) ────────────────────────────────────
    score_weights: dict = {
        "infrastructure_uplift": 0.20,
        "connectivity": 0.12,
        "affordability": 0.10,
        "rental_yield": 0.12,
        "liquidity": 0.08,
        "regulatory_safety": 0.15,
        "developer_trust": 0.10,
        "execution_risk": 0.08,
        "appreciation_potential": 0.05,
    }

    # ── Geo influence radii (km) ──────────────────────────────────────────────
    geo_direct_radius_km: float = 3.0
    geo_secondary_radius_km: float = 7.0
    geo_corridor_radius_km: float = 15.0
    metro_walkable_radius_km: float = 1.0
    airport_logistics_radius_km: float = 10.0

    # ── Freshness decay thresholds (days) ────────────────────────────────────
    freshness_green_days: int = 30
    freshness_yellow_days: int = 90
    freshness_red_days: int = 180

    # ── Source tiers ─────────────────────────────────────────────────────────
    # 1 = official government, 2 = verified listing/exchange, 3 = news/secondary
    source_tier_weights: dict = {1: 1.0, 2: 0.7, 3: 0.4}

    # ── API ──────────────────────────────────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    jwt_secret: str = Field(default="change-me-in-production", validation_alias="JWT_SECRET")

    # ── Dashboard ────────────────────────────────────────────────────────────
    dashboard_port: int = 8501

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "populate_by_name": True}


@lru_cache
def get_settings() -> Settings:
    return Settings()
