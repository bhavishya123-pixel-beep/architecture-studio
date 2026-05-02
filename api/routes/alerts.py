"""API routes: alert feed and watchlist."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query
from pydantic import BaseModel

from api.schemas import Alert, AlertSeverity, AlertType

router = APIRouter(prefix="/alerts", tags=["Alerts"])


class WatchlistEntry(BaseModel):
    city: str
    locality: str
    project_name: Optional[str] = None
    rera_number: Optional[str] = None
    alert_types: list[AlertType] = []


# In-memory store (replace with Redis/DB in production)
_watchlist: list[WatchlistEntry] = []
_alert_feed: list[Alert] = []


@router.get("/feed")
async def get_alert_feed(
    severity: Optional[AlertSeverity] = None,
    alert_type: Optional[AlertType] = None,
    city: Optional[str] = None,
    limit: int = Query(default=50, le=200),
):
    """Return recent alerts, optionally filtered."""
    feed = _alert_feed
    if severity:
        feed = [a for a in feed if a.severity == severity]
    if alert_type:
        feed = [a for a in feed if a.alert_type == alert_type]
    if city:
        feed = [a for a in feed if a.city and a.city.lower() == city.lower()]
    return {
        "total": len(feed),
        "alerts": [a.model_dump(mode="json") for a in feed[:limit]],
    }


@router.post("/watchlist")
async def add_to_watchlist(entry: WatchlistEntry):
    """Add a location or project to the watchlist."""
    _watchlist.append(entry)
    return {"message": "Added to watchlist", "watchlist_size": len(_watchlist)}


@router.get("/watchlist")
async def get_watchlist():
    """Return current watchlist."""
    return {"watchlist": [e.model_dump() for e in _watchlist]}


@router.delete("/watchlist/{index}")
async def remove_from_watchlist(index: int):
    if index < 0 or index >= len(_watchlist):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Index out of range")
    removed = _watchlist.pop(index)
    return {"message": "Removed", "entry": removed.model_dump()}
