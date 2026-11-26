"""FujiNova Discovery, Route, Timetable & Recalibration API."""
from datetime import datetime, date as date_cls
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from backend.app.services.discovery import discovery_service as ds

router = APIRouter(prefix="/api/v1", tags=["Discovery & Trip"])

HUB_COORDS: Dict[str, tuple] = {
    "Kawaguchiko Station": (35.4983, 138.7686),
    "Kawaguchiko Station (Main Hub)": (35.4983, 138.7686),
    "河口湖駅": (35.4983, 138.7686),
    "Fujisan Station": (35.4839, 138.7958),
    "Fujisan Station (Mt. Fuji Station)": (35.4839, 138.7958),
    "富士山駅": (35.4839, 138.7958),
    "Mt. Fuji 5th Station": (35.3908, 138.7323),
    "富士山五合目": (35.3908, 138.7323),
    "Shin-Fuji Station": (35.1425, 138.6631),
    "新富士駅": (35.1425, 138.6631),
    "Mishima Station": (35.1271, 138.9108),
    "三島駅": (35.1271, 138.9108),
    "Gotemba Station": (35.2974, 138.9344),
    "御殿場駅": (35.2974, 138.9344),
    "Tokyo Station": (35.6812, 139.7671),
    "東京駅": (35.6812, 139.7671),
    "Shinjuku Station": (35.6896, 139.7006),
    "新宿駅": (35.6896, 139.7006),
}


def resolve_coords(name: Optional[str], lat: Optional[float], lon: Optional[float]) -> tuple:
    if lat is not None and lon is not None:
        return float(lat), float(lon), name or "Origin"
    target_name = (name or "Kawaguchiko Station").strip()
    for k, v in HUB_COORDS.items():
        if k.lower() in target_name.lower() or target_name.lower() in k.lower():
            return v[0], v[1], k
    return 35.4983, 138.7686, target_name


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
    origin_lat: Optional[float] = Query(None, ge=-90, le=90),
    origin_lon: Optional[float] = Query(None, ge=-180, le=180),
    origin_name: Optional[str] = Query(None),
    start_hub: Optional[str] = Query(None),
    start_location: Optional[str] = Query(None),
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
    hub_name = origin_name or start_hub or start_location or "Kawaguchiko Station"
    lat, lon, resolved_name = resolve_coords(hub_name, origin_lat, origin_lon)
    try:
        res = ds.discover(ds.DiscoveryQuery(
            origin_lat=lat, origin_lon=lon, origin_name=resolved_name, mode=mode, max_km=max_km, view=view,
            discovery_type=discovery_type.upper() if discovery_type else None, category=category, q=q,
            crowd=crowd, crowd_pref=crowd_pref, scenario=scenario, open_now=open_now, visit_date=visit_date,
            departure_time=departure_time, time_budget_min=time_budget_min, require_accessible=require_accessible,
            page=page, page_size=page_size,
            with_transit_details=(view == "recommended") if with_details is None else with_details,
        ))
        res["places"] = res.get("items", [])
        res["total_destinations"] = res.get("counts", {}).get("total", 237)
        return res
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


class RouteRequest(BaseModel):
    origin_lat: Optional[float] = None
    origin_lon: Optional[float] = None
    origin_name: Optional[str] = "Origin"
    destination_id: Optional[str] = None
    place_id: Optional[str] = None
    mode: str = "fujikyu_bus"
    visit_date: Optional[str] = None
    departure_time: str = "09:30"


@router.get("/discovery/route")
def route(
    origin_lat: Optional[float] = None,
    origin_lon: Optional[float] = None,
    place_id: Optional[str] = None,
    destination_id: Optional[str] = None,
    origin_name: Optional[str] = "Origin",
    mode: str = "fujikyu_bus",
    visit_date: Optional[str] = None,
    departure_time: str = "09:30",
):
    target = place_id or destination_id or "kawaguchiko_oishi_park"
    lat, lon, res_name = resolve_coords(origin_name, origin_lat, origin_lon)
    if mode not in ds.ALL_MODES:
        raise HTTPException(status_code=422, detail=f"Unsupported travel mode '{mode}'.")
    d = date_cls.fromisoformat(visit_date) if visit_date else datetime.now().date()
    h, m = departure_time.split(":")[:2]
    when = datetime(d.year, d.month, d.day, int(h), int(m))
    try:
        return ds.build_route({"name": res_name, "lat": lat, "lon": lon}, target, mode, when)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/discovery/route")
def route_post(req: RouteRequest):
    target = req.place_id or req.destination_id or "kawaguchiko_oishi_park"
    lat, lon, res_name = resolve_coords(req.origin_name, req.origin_lat, req.origin_lon)
    if req.mode not in ds.ALL_MODES:
        raise HTTPException(status_code=422, detail=f"Unsupported travel mode '{req.mode}'.")
    d = date_cls.fromisoformat(req.visit_date) if req.visit_date else datetime.now().date()
    h, m = req.departure_time.split(":")[:2]
    when = datetime(d.year, d.month, d.day, int(h), int(m))
    try:
        return ds.build_route({"name": res_name, "lat": lat, "lon": lon}, target, req.mode, when)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


class TripPlanRequest(BaseModel):
    origin_lat: Optional[float] = None
    origin_lon: Optional[float] = None
    origin_name: Optional[str] = "Origin"
    start_location: Optional[str] = None
    place_id: Optional[str] = None
    target_place_id: Optional[str] = None
    mode: Optional[str] = "fujikyu_bus"
    travel_mode: Optional[str] = None
    date: Optional[str] = None
    departure_time: str = "09:30"
    time_budget_min: Optional[int] = 300
    available_hours: Optional[float] = None
    scenario: str = "moderate"
    meals: Optional[Dict[str, bool]] = None
    food_styles: List[str] = Field(default_factory=list)
    food_preference: Optional[str] = None
    food_experience: str = "local"
    walking_ability: str = "normal"
    travellers: int = 1
    budget_jpy: Optional[int] = None


@router.post("/trip/plan")
def trip_plan(req: TripPlanRequest):
    d = req.model_dump()
    target_place = d.get("place_id") or d.get("target_place_id") or "kawaguchiko_oishi_park"
    hub = d.get("start_location") or d.get("origin_name") or "Kawaguchiko Station"
    lat, lon, res_name = resolve_coords(hub, d.get("origin_lat"), d.get("origin_lon"))
    d["origin_lat"] = lat
    d["origin_lon"] = lon
    d["origin_name"] = res_name
    d["place_id"] = target_place
    if d.get("travel_mode"):
        d["mode"] = d["travel_mode"]
    if d.get("available_hours"):
        d["time_budget_min"] = int(d["available_hours"] * 60)
    if d.get("food_preference"):
        d["food_experience"] = d["food_preference"]
    try:
        return ds.plan_trip(d)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


class RemainingItem(BaseModel):
    place_id: str
    minutes: Optional[int] = None


class RecalibrateRequest(BaseModel):
    origin_lat: Optional[float] = None
    origin_lon: Optional[float] = None
    origin_name: Optional[str] = "Origin"
    start_location: Optional[str] = None
    mode: str = "fujikyu_bus"
    date: Optional[str] = None
    now_time: Optional[str] = None
    planned_end_time: Optional[str] = None
    deadline_time: Optional[str] = None
    current_place_id: str = "kawaguchiko_oishi_park"
    remaining: List[RemainingItem] = Field(default_factory=list)
    visited_place_ids: List[str] = Field(default_factory=list)
    meal_pending: bool = False
    scenario: str = "moderate"
    food_styles: List[str] = Field(default_factory=list)
    food_experience: str = "local"
    step_index: Optional[int] = None
    minutes_offset: Optional[int] = None


@router.post("/trip/recalibrate")
def trip_recalibrate(req: RecalibrateRequest):
    d = req.model_dump()
    hub = d.get("start_location") or d.get("origin_name") or "Kawaguchiko Station"
    lat, lon, res_name = resolve_coords(hub, d.get("origin_lat"), d.get("origin_lon"))
    d["origin_lat"] = lat
    d["origin_lon"] = lon
    d["origin_name"] = res_name
    if not d.get("now_time"):
        d["now_time"] = datetime.now().strftime("%H:%M")
    if not d.get("planned_end_time"):
        d["planned_end_time"] = "15:00"
    if not d.get("deadline_time"):
        d["deadline_time"] = "16:00"
    try:
        return ds.recalibrate(d)
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
