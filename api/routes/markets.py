"""API routes: market data endpoints."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from api.schemas import LocationScoreCard, MarketPriceRecord
from scoring.engine import build_location_scorecard

router = APIRouter(prefix="/markets", tags=["Markets"])


class ScoreRequest(BaseModel):
    city: str
    state: str
    locality: str
    pin_code: Optional[str] = None


class ScoreResponse(BaseModel):
    score_card: LocationScoreCard
    disclaimer: str


@router.post("/score", response_model=ScoreResponse)
async def get_location_score(req: ScoreRequest):
    """
    Compute investment attractiveness score for a location.
    Pass any available contextual data; missing data is handled gracefully.
    """
    # In production, these records come from the DB layer
    scorecard = build_location_scorecard(
        city=req.city,
        state=req.state,
        locality=req.locality,
        pin_code=req.pin_code,
    )
    from config.settings import get_settings
    return ScoreResponse(
        score_card=scorecard,
        disclaimer=get_settings().disclaimer,
    )


@router.get("/cities")
async def list_cities():
    """Return list of cities with market data coverage."""
    return {
        "cities": [
            "Mumbai", "Delhi", "Bengaluru", "Hyderabad",
            "Pune", "Chennai", "Kolkata", "Ahmedabad",
            "Noida", "Gurugram", "Navi Mumbai", "Thane",
        ],
        "note": "Coverage varies by data source availability.",
    }


@router.get("/{city}/summary")
async def city_summary(city: str):
    """High-level market summary for a city."""
    return {
        "city": city,
        "message": "Connect DB layer to return live summary.",
        "disclaimer": "Data requires live database connection.",
    }
