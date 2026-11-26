"""FujiNova Discovery, Route, Timetable & Recalibration API."""
from datetime import datetime, date as date_cls
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.app.services.discovery import discovery_service as ds

router = APIRouter(prefix="/api/v1", tags=["Discovery & Trip"])


@router.get("/discovery/modes")
def list_modes():
    """Travel modes with distance bands and an honest data-availability disclosure."""
    return {
        "modes": [
            {"id": m, "label": ds.MODE_LABELS[m], "bands_km": ds.DISTANCE_BANDS[m],
             "kind": "transit" if m in ds.TRANSIT_MODES else "surface"}
            for m in ["walk", "bike", "fujikyu_bus", "bus", "train", "taxi", "mixed", "car"]
        ],
        "capabilities": {
            "gtfs_bus_timetable": True, "railway_timetable": True, "gtfs_realtime": False,
            "pedestrian_routing_provider": bool(__import__("os").getenv("OSRM_BASE_URL")),
            "bicycle_rental_dataset": False, "restaurant_dataset": False, "taxi_fare_provider": False,
            "other_bus_operators_in_feed": False,
        },
        "notes": [
            "Only Fujikyu Bus appears in the loaded GTFS feed, so 'Other buses' currently resolves to the same operator.",
            "Walking/cycling/road figures are estimates unless OSRM_BASE_URL is configured.",
        ],
    }


@router.get("/discovery/recommend")
def recommend(
    origin_lat: float = Query(..., ge=-90, le=90),
    origin_lon: float = Query(..., ge=-180, le=180),
    origin_name: str = Query("Origin"),
    mode: str = Query("fujikyu_bus"),
    max_km: Optional[float] = Query(None, gt=0, le=200),
    view: str = Query("recommended", pattern="^(recommended|catalogue)$"),
    discovery_type: Optional[str] = Query(None, pattern="^(FAMOUS|HIDDEN_GEM|famous|hidden_gem)$"),
    category: Optional[str] = None,
    q: Optional[str] = None,
    crowd: Optional[str] = Query(None, pattern="^(low|moderate|high|LOW|MODERATE|HIGH)$"),
    crowd_pref: str = Query("balanced", pattern="^(quiet|balanced|popular)$"),
    scenario: str = Query("moderate", pattern="^(low|moderate|high)$"),
    open_now: bool = False,
    visit_date: Optional[str] = None,
    departure_time: str = "09:30",
    time_budget_min: int = Query(300, ge=30, le=1440),
    require_accessible: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=60),
    with_details: Optional[bool] = Query(None, description="Attach exact RAPTOR times/fares to the first 12 cards (default: recommended view only)"),
):
    try:
        return ds.discover(ds.DiscoveryQuery(
            origin_lat=origin_lat, origin_lon=origin_lon, origin_name=origin_name, mode=mode, max_km=max_km, view=view,
            discovery_type=discovery_type.upper() if discovery_type else None, category=category, q=q,
            crowd=crowd, crowd_pref=crowd_pref, scenario=scenario, open_now=open_now, visit_date=visit_date,
            departure_time=departure_time, time_budget_min=time_budget_min, require_accessible=require_accessible,
            page=page, page_size=page_size,
            with_transit_details=(view == "recommended") if with_details is None else with_details,
        ))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/discovery/route")
def route(
    origin_lat: float, origin_lon: float, place_id: str, origin_name: str = "Origin",
    mode: str = "fujikyu_bus", visit_date: Optional[str] = None, departure_time: str = "09:30",
):
    if mode not in ds.ALL_MODES:
        raise HTTPException(status_code=422, detail=f"Unsupported travel mode '{mode}'.")
    d = date_cls.fromisoformat(visit_date) if visit_date else datetime.now().date()
    h, m = departure_time.split(":")[:2]
    when = datetime(d.year, d.month, d.day, int(h), int(m))
    try:
        return ds.build_route({"name": origin_name, "lat": origin_lat, "lon": origin_lon}, place_id, mode, when)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


class TripPlanRequest(BaseModel):
    origin_lat: float
    origin_lon: float
    origin_name: str = "Origin"
    place_id: str
    mode: str = "fujikyu_bus"
    date: Optional[str] = None
    departure_time: str = "09:30"
    time_budget_min: int = Field(300, ge=30, le=1440)
    scenario: str = "moderate"
    meals: Optional[Dict[str, bool]] = None
    food_styles: List[str] = Field(default_factory=list)
    food_experience: str = "local"
    walking_ability: str = "normal"
    travellers: int = 1
    budget_jpy: Optional[int] = None


@router.post("/trip/plan")
def trip_plan(req: TripPlanRequest):
    try:
        return ds.plan_trip(req.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


class RemainingItem(BaseModel):
    place_id: str
    minutes: Optional[int] = None


class RecalibrateRequest(BaseModel):
    origin_lat: float
    origin_lon: float
    origin_name: str = "Origin"
    mode: str = "fujikyu_bus"
    date: Optional[str] = None
    now_time: str
    planned_end_time: str
    deadline_time: str
    current_place_id: str
    remaining: List[RemainingItem] = Field(default_factory=list)
    visited_place_ids: List[str] = Field(default_factory=list)
    meal_pending: bool = False
    scenario: str = "moderate"
    food_styles: List[str] = Field(default_factory=list)
    food_experience: str = "local"


@router.post("/trip/recalibrate")
def trip_recalibrate(req: RecalibrateRequest):
    try:
        return ds.recalibrate(req.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/discovery/crowd-timing")
def crowd_timing(
    origin_lat: float, origin_lon: float, place_id: str, origin_name: str = "Origin", mode: str = "fujikyu_bus",
    visit_date: Optional[str] = None, preferred_time: str = "10:00", scenario: str = "moderate",
):
    d = date_cls.fromisoformat(visit_date) if visit_date else datetime.now().date()
    try:
        return ds.crowd_timing({"name": origin_name, "lat": origin_lat, "lon": origin_lon}, place_id, mode, d,
                               ds.hhmm_to_min(preferred_time), scenario)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
