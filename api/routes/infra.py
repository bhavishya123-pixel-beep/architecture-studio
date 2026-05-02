"""API routes: infrastructure data."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from api.schemas import InfraType, InfraStatus

router = APIRouter(prefix="/infra", tags=["Infrastructure"])


@router.get("/projects")
async def list_infra_projects(
    infra_type: Optional[InfraType] = None,
    state: Optional[str] = None,
    status: Optional[InfraStatus] = None,
    city: Optional[str] = None,
    limit: int = Query(default=50, le=200),
):
    """List infrastructure projects with optional filters."""
    return {
        "message": "Connect DB layer for live data.",
        "filters": {
            "infra_type": infra_type,
            "state": state,
            "status": status,
            "city": city,
        },
        "note": "Run ingestion pipeline to populate database.",
    }


@router.get("/proximity")
async def get_infra_proximity(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius_km: float = Query(default=15.0, le=50.0),
):
    """
    Find infrastructure projects within radius_km of given coordinates.
    Uses PostGIS spatial query in production.
    """
    return {
        "center": {"lat": lat, "lon": lon},
        "radius_km": radius_km,
        "message": "PostGIS query required. Connect spatial database.",
    }
