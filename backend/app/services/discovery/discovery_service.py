"""FujiNova Discovery & Trip Engine.

Single source of truth: the canonical SQLite ``places`` table (all destinations).
Transport: the existing RAPTOR routing service (Fujikyu Bus GTFS-JP + Fujikyu Railway timetable).

Honesty rules (enforced in the data returned to the UI):
* Walking / bicycle / taxi / car distances are ESTIMATES (straight-line x detour factor) unless an
  OSRM-compatible provider is configured via ``OSRM_BASE_URL``.  Every figure carries a ``provenance``.
* Public-transport availability comes from the GTFS/railway graph.  Exact departures, durations and
  fares come from RAPTOR.  Nothing is invented; when no connection exists the result says so.
* Crowd levels are SIMULATED / FORECAST (no live telemetry).
* No verified restaurant or bicycle-rental dataset exists in this project; meals and rentals are
  reported as ``NO_VERIFIED_DATA`` rather than fabricated.
"""
from __future__ import annotations

import json
import math
import os
import re
import urllib.request
from dataclasses import dataclass
from datetime import date as date_cls, datetime, timedelta
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

from backend.app.core.database import get_db_connection

# --------------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------------
SURFACE_MODES = {"walk", "bike", "taxi", "car"}
TRANSIT_MODES = {"fujikyu_bus", "bus", "train", "mixed"}
ALL_MODES = SURFACE_MODES | TRANSIT_MODES

MODE_LABELS = {
    "walk": "Walking",
    "bike": "Rented bicycle",
    "fujikyu_bus": "Fujikyu Bus",
    "bus": "Other buses",
    "train": "Train",
    "taxi": "Taxi",
    "mixed": "Mixed public transport",
    "car": "Private vehicle",
}

SURFACE_PROFILE = {
    # detour factor converts straight-line km to estimated path km; speed in km/h
    "walk": {"detour": 1.3, "kmh": 4.8, "osrm": "foot"},
    "bike": {"detour": 1.3, "kmh": 14.0, "osrm": "bike"},
    "taxi": {"detour": 1.35, "kmh": 35.0, "osrm": "driving"},
    "car": {"detour": 1.35, "kmh": 35.0, "osrm": "driving"},
}

DISTANCE_BANDS = {
    "walk": [1, 3, 5, 10],
    "bike": [3, 5, 10, 20],
    "taxi": [5, 10, 20, 50],
    "car": [5, 10, 20, 50],
    "fujikyu_bus": [5, 10, 20, 50],
    "bus": [5, 10, 20, 50],
    "train": [5, 10, 20, 50],
    "mixed": [5, 10, 20, 50],
}

BOARDING_RADIUS_M = 1000.0
ALIGHT_RADIUS_M = 1200.0
WALK_M_PER_MIN = 80.0  # 4.8 km/h
MAX_LEGS = {"fujikyu_bus": 2, "bus": 2, "train": 2, "mixed": 3}
TOKYO_NOW_FALLBACK = datetime(2026, 1, 1, 9, 0)


# --------------------------------------------------------------------------------------
# Geometry helpers
# --------------------------------------------------------------------------------------
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def walk_minutes_for_m(dist_m: float) -> int:
    return max(1, int(round(dist_m * 1.3 / WALK_M_PER_MIN)))


def hhmm_to_min(s: str) -> int:
    parts = s.split(":")
    return int(parts[0]) * 60 + int(parts[1])


def min_to_hhmm(m: int) -> str:
    m = int(m)
    day_over = m // 1440
    m = m % 1440
    s = f"{m // 60:02d}:{m % 60:02d}"
    return s + (f" (+{day_over}d)" if day_over else "")


def parse_hours(text: Optional[str]) -> Optional[Tuple[int, int]]:
    """Parse an opening-hours string into (open_min, close_min). None when not parseable."""
    if not text:
        return None
    low = text.lower()
    if "24 hours" in low or "24h" in low or "24-hour" in low or "always" in low:
        return (0, 1440)
    m = re.search(r"(\d{1,2}):(\d{2})\s*(?:-|–|—|~|to)\s*(\d{1,2}):(\d{2})", text)
    if not m:
        return None
    return (int(m.group(1)) * 60 + int(m.group(2)), int(m.group(3)) * 60 + int(m.group(4)))


def place_open_status(place: Dict[str, Any], visit_date: date_cls, minute_of_day: int) -> Dict[str, Any]:
    """Return {'status': open|closed|unverified|seasonal_closure, 'note': str}."""
    st = place.get("opening_status")
    if st == "ALWAYS_OPEN":
        return {"status": "open", "note": place.get("opening_hours_text") or "Open all hours"}
    if st == "SEASONAL_CLOSURE":
        months = str(place.get("best_visit_months") or "")
        note = place.get("seasonal_closure") or "Seasonal closure applies"
        if months and str(visit_date.month) in re.findall(r"\d+", months):
            return {"status": "open", "note": f"In season ({note})"}
        return {"status": "seasonal_closure", "note": str(note)}
    if st == "TEMPORARILY_CLOSED":
        return {"status": "closed", "note": "Temporarily closed"}
    hours = parse_hours(place.get("opening_hours_text"))
    if hours:
        o, c = hours
        if o <= minute_of_day < c:
            return {"status": "open", "note": place.get("opening_hours_text") or ""}
        return {"status": "closed", "note": f"Opens {min_to_hhmm(o)}-{min_to_hhmm(c)}"}
    return {"status": "unverified", "note": "Opening hours not verified in database"}


# --------------------------------------------------------------------------------------
# Place access (canonical DB)
# --------------------------------------------------------------------------------------
def load_all_places() -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        rows = conn.execute("SELECT * FROM places ORDER BY place_id").fetchall()
        return [dict(r) for r in rows]


def get_place(place_id: str) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM places WHERE place_id = ?", (place_id,)).fetchone()
        return dict(row) if row else None


def catalogue_counts() -> Dict[str, int]:
    with get_db_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM places").fetchone()[0]
        famous = conn.execute("SELECT COUNT(*) FROM places WHERE discovery_type='FAMOUS'").fetchone()[0]
        hidden = conn.execute("SELECT COUNT(*) FROM places WHERE discovery_type='HIDDEN_GEM'").fetchone()[0]
    return {"total": total, "famous": famous, "hidden_gems": hidden}


# --------------------------------------------------------------------------------------
# Transit graph reachability (built from the existing routing service data, no 2nd engine)
# --------------------------------------------------------------------------------------
def _svc():
    from backend.app.services.routing.routing_service import get_routing_service
    s = get_routing_service()
    if not s._is_initialized:
        s.initialize()
    return s


@lru_cache(maxsize=1)
def _route_sequences() -> Dict[str, List[Tuple[str, ...]]]:
    svc = _svc()
    seqs: Dict[str, set] = {}
    for trip in svc.trips.values():
        seqs.setdefault(trip.route_id, set()).add(tuple(trip.stops_sequence))
    return {rid: list(v) for rid, v in seqs.items()}


def _route_ok(route_id: str, mode: str) -> bool:
    svc = _svc()
    r = svc.routes.get(route_id)
    if not r:
        return False
    if mode in ("fujikyu_bus", "bus"):
        return r.mode.value == "bus"
    if mode == "train":
        return r.mode.value == "rail"
    return True  # mixed


@lru_cache(maxsize=8)
def _ok_stops(mode: str) -> Tuple[Tuple[str, float, float], ...]:
    """Stops that are served by at least one route valid for this mode (computed once per mode)."""
    svc = _svc()
    out = []
    for sid, st in svc.stops.items():
        if any(_route_ok(r, mode) for r in svc.stop_to_routes.get(sid, ())):
            out.append((sid, st.lat, st.lon))
    return tuple(out)


@lru_cache(maxsize=4096)
def _stops_near_cached(lat5: float, lon5: float, radius_m: float, mode: str) -> Tuple[Tuple[float, str], ...]:
    out = []
    cos_lat = math.cos(math.radians(lat5))
    # cheap bounding box before haversine (1 deg lat ~ 111 km)
    deg = radius_m / 111000.0 * 1.2
    for sid, slat, slon in _ok_stops(mode):
        if abs(slat - lat5) > deg or abs(slon - lon5) * cos_lat > deg:
            continue
        d = haversine_km(lat5, lon5, slat, slon) * 1000.0
        if d <= radius_m:
            out.append((d, sid))
    out.sort()
    return tuple(out)


def _stops_near(lat: float, lon: float, radius_m: float, mode: str) -> List[Tuple[float, str]]:
    return list(_stops_near_cached(round(lat, 5), round(lon, 5), radius_m, mode))


@lru_cache(maxsize=256)
def _reach(lat4: float, lon4: float, mode: str) -> Tuple[Dict[str, int], Tuple[Tuple[float, str], ...]]:
    """Stops reachable from the origin by <= MAX_LEGS vehicle legs. Returns (stop -> legs, boarding)."""
    svc = _svc()
    boarding = _stops_near(lat4, lon4, BOARDING_RADIUS_M, mode)
    reach: Dict[str, int] = {}
    frontier: Dict[str, int] = {}
    for _, sid in boarding:
        reach[sid] = 0
        frontier[sid] = 0
    seqs = _route_sequences()
    max_legs = MAX_LEGS.get(mode, 2)
    for level in range(1, max_legs + 1):
        new: Dict[str, int] = {}
        for sid in frontier:
            for rid in svc.stop_to_routes.get(sid, ()):
                if not _route_ok(rid, mode):
                    continue
                for seq in seqs.get(rid, ()):
                    if sid in seq:
                        idx = seq.index(sid)
                        for t in seq[idx + 1:]:
                            if t not in reach and t not in new:
                                new[t] = level
        # walking footpath transfers (inter-stop connections) at no extra vehicle leg
        for sid in list(new):
            for fp in svc.footpaths.get(sid, ()):
                if fp.to_stop_id not in reach and fp.to_stop_id not in new:
                    new[fp.to_stop_id] = level
        reach.update(new)
        frontier = new
        if not frontier:
            break
    return reach, tuple(boarding)


def transit_reachability(origin_lat: float, origin_lon: float, place: Dict[str, Any], mode: str) -> Dict[str, Any]:
    reach, boarding = _reach(round(origin_lat, 4), round(origin_lon, 4), mode)
    if not boarding:
        return {"reachable": False, "reason": "No usable boarding stop within 1 km of the start point for this mode."}
    alights = _stops_near(place["latitude"], place["longitude"], ALIGHT_RADIUS_M, mode)
    best = None
    for d, sid in alights:
        legs = reach.get(sid)
        if legs is None:
            continue
        cand = (legs, d, sid)
        if best is None or cand < best:
            best = cand
    if best is None:
        why = "No stop within 1.2 km of the destination" if not alights else "No connection from the start point in the timetable graph"
        return {"reachable": False, "reason": why}
    legs, d, sid = best
    return {
        "reachable": True,
        "vehicle_legs": legs,
        "transfers": max(0, legs - 1),
        "alight_stop_id": sid,
        "alight_walk_m": round(d),
        "boarding_stop_id": boarding[0][1],
        "boarding_walk_m": round(boarding[0][0]),
    }


# --------------------------------------------------------------------------------------
# Leg computation (shared by discovery, route, timetable, recalibration)
# --------------------------------------------------------------------------------------
_OSRM_ERR: Dict[str, str] = {}


def _osrm_route(profile: str, a: Tuple[float, float], b: Tuple[float, float]) -> Optional[Dict[str, Any]]:
    base = os.getenv("OSRM_BASE_URL", "").strip().rstrip("/")
    if not base:
        return None
    url = f"{base}/route/v1/{profile}/{a[1]},{a[0]};{b[1]},{b[0]}?overview=full&geometries=geojson"
    try:
        with urllib.request.urlopen(url, timeout=4) as resp:  # noqa: S310 (configured provider)
            data = json.loads(resp.read().decode("utf-8"))
        route = data["routes"][0]
        coords = [[c[1], c[0]] for c in route["geometry"]["coordinates"]]
        return {"distance_km": route["distance"] / 1000.0, "minutes": route["duration"] / 60.0, "path": coords}
    except Exception as e:  # provider failure falls back to estimate
        _OSRM_ERR[profile] = str(e)
        return None


def surface_leg(a_lat: float, a_lon: float, b_lat: float, b_lon: float, mode: str) -> Dict[str, Any]:
    prof = SURFACE_PROFILE[mode]
    direct = haversine_km(a_lat, a_lon, b_lat, b_lon)
    routed = _osrm_route(prof["osrm"], (a_lat, a_lon), (b_lat, b_lon))
    if routed:
        dist, minutes, path, prov = routed["distance_km"], routed["minutes"], routed["path"], "ROUTED_OSRM"
    else:
        dist = direct * prof["detour"]
        minutes = dist / prof["kmh"] * 60.0
        path = [[a_lat, a_lon], [b_lat, b_lon]]
        prov = f"ESTIMATED_DETOUR_x{prof['detour']}"
    kind = {"walk": "walk", "bike": "bike", "taxi": "drive", "car": "drive"}[mode]
    return {
        "available": True,
        "minutes": max(1, int(round(minutes))),
        "distance_km": round(dist, 2),
        "direct_km": round(direct, 2),
        "path": path,
        "provenance": prov,
        "kind": kind,
    }


def _nearest_candidates(lat: float, lon: float, mode: str, radius_m: float, limit: int = 3) -> List[Tuple[float, str]]:
    return _stops_near(lat, lon, radius_m, mode)[:limit]


def _leg_path(svc, route_id: str, from_sid: str, to_sid: str) -> List[List[float]]:
    for seq in _route_sequences().get(route_id, ()):
        if from_sid in seq and to_sid in seq and seq.index(from_sid) < seq.index(to_sid):
            i, j = seq.index(from_sid), seq.index(to_sid)
            return [[svc.stops[s].lat, svc.stops[s].lon] for s in seq[i:j + 1] if s in svc.stops]
    a, b = svc.stops.get(from_sid), svc.stops.get(to_sid)
    return [[a.lat, a.lon], [b.lat, b.lon]] if a and b else []


def _journey_modes_ok(journey, mode: str) -> bool:
    modes = {str(getattr(l.mode, "value", l.mode)) for l in journey.legs}
    modes.discard("walk")
    if mode in ("fujikyu_bus", "bus"):
        return modes <= {"bus"} and bool(modes)
    if mode == "train":
        return modes <= {"rail"} and bool(modes)
    return bool(modes)


def transit_leg(
    a_lat: float, a_lon: float, b_lat: float, b_lon: float,
    mode: str, when: datetime, a_name: str = "Start", b_name: str = "Destination",
    max_results: int = 3,
) -> Dict[str, Any]:
    """Door-to-door public-transport leg using the real RAPTOR engine. Never invents a service."""
    from backend.app.services.routing.transit_models import RouteSearchRequest
    svc = _svc()
    origins = _nearest_candidates(a_lat, a_lon, mode, BOARDING_RADIUS_M, 3)
    dests = _nearest_candidates(b_lat, b_lon, mode, ALIGHT_RADIUS_M, 3)
    if not origins:
        return {"available": False, "reason": "No usable boarding stop within 1 km for this travel mode.", "provenance": "GTFS"}
    if not dests:
        return {"available": False, "reason": "No usable stop within 1.2 km of the destination for this travel mode.", "provenance": "GTFS"}

    best = None
    pairs = sorted(((od + dd, (od, osid), (dd, dsid)) for od, osid in origins[:2] for dd, dsid in dests[:2] if osid != dsid),
                   key=lambda x: x[0])
    for _, (od, osid), (dd, dsid) in pairs:
        ready = when + timedelta(minutes=walk_minutes_for_m(od))
        try:
            res = svc.search_routes(RouteSearchRequest(
                origin=osid, destination=dsid,
                departure_time=ready.strftime("%Y-%m-%d %H:%M:%S"),
                max_transfers=MAX_LEGS.get(mode, 2) - 1, max_results=max_results,
            ))
        except Exception:
            continue
        for j in res.journeys:
            if not _journey_modes_ok(j, mode):
                continue
            arrive_sec = j.legs[-1].arrival_timestamp_sec
            arr_min = arrive_sec / 60.0 + walk_minutes_for_m(dd)
            if best is None or arr_min < best["arr_min"]:
                best = {"journey": j, "o": (od, osid), "d": (dd, dsid), "arr_min": arr_min, "res": res, "alts": res.journeys}
        if best:
            break  # nearest working stop pair wins; avoids repeated expensive searches
    if not best:
        return {
            "available": False,
            "reason": "No scheduled service found for this mode on the selected date/time (the feed lists none that connect these stops).",
            "provenance": "GTFS-JP / Fujikyu Railway timetable",
        }

    j = best["journey"]
    (od, osid), (dd, dsid) = best["o"], best["d"]
    segments: List[Dict[str, Any]] = []
    ost, dst = svc.stops[osid], svc.stops[dsid]
    midnight = when.replace(hour=0, minute=0, second=0, microsecond=0)

    def clock(sec: int) -> str:
        return min_to_hhmm(int(sec // 60))

    first_dep_sec = j.legs[0].departure_timestamp_sec
    walk_in_min = walk_minutes_for_m(od)
    start_sec = int((when - midnight).total_seconds())
    segments.append({
        "kind": "walk", "label": f"Walk to {ost.stop_name_en or ost.stop_name_ja}",
        "from": {"name": a_name, "lat": a_lat, "lon": a_lon},
        "to": {"name": ost.stop_name_en or ost.stop_name_ja, "lat": ost.lat, "lon": ost.lon, "stop_id": osid},
        "minutes": walk_in_min, "distance_m": round(od * 1.3), "departure": clock(start_sec),
        "arrival": clock(start_sec + walk_in_min * 60), "path": [[a_lat, a_lon], [ost.lat, ost.lon]],
        "provenance": "ESTIMATED_WALK", "color": "#64748B",
    })
    wait = max(0, first_dep_sec - (start_sec + walk_in_min * 60)) // 60
    for leg in j.legs:
        lmode = str(getattr(leg.mode, "value", leg.mode))
        o_st, d_st = svc.stops.get(leg.origin_stop_id), svc.stops.get(leg.destination_stop_id)
        if lmode == "walk":
            path = [[o_st.lat, o_st.lon], [d_st.lat, d_st.lon]] if o_st and d_st else []
            kind = "walk"
        else:
            path = _leg_path(svc, leg.route_id or "", leg.origin_stop_id, leg.destination_stop_id)
            kind = "rail" if lmode == "rail" else "bus"
        stops_pts = []
        if lmode != "walk":
            for seq in _route_sequences().get(leg.route_id or "", ()):
                if leg.origin_stop_id in seq and leg.destination_stop_id in seq and seq.index(leg.origin_stop_id) < seq.index(leg.destination_stop_id):
                    i, k = seq.index(leg.origin_stop_id), seq.index(leg.destination_stop_id)
                    stops_pts = [{"stop_id": s, "name": svc.stops[s].stop_name_en or svc.stops[s].stop_name_ja,
                                  "lat": svc.stops[s].lat, "lon": svc.stops[s].lon} for s in seq[i:k + 1] if s in svc.stops]
                    break
        segments.append({
            "kind": kind,
            "label": f"{leg.operator} {leg.route_short_name or leg.route_long_name or ''}".strip(),
            "service": leg.route_long_name or leg.route_short_name,
            "operator": leg.operator,
            "headsign": leg.trip_headsign,
            "from": {"name": leg.origin_stop_name_en or leg.origin_stop_name, "lat": o_st.lat if o_st else None, "lon": o_st.lon if o_st else None, "stop_id": leg.origin_stop_id},
            "to": {"name": leg.destination_stop_name_en or leg.destination_stop_name, "lat": d_st.lat if d_st else None, "lon": d_st.lon if d_st else None, "stop_id": leg.destination_stop_id},
            "minutes": leg.duration_minutes, "departure": leg.departure_time, "arrival": leg.arrival_time,
            "dep_sec": leg.departure_timestamp_sec, "arr_sec": leg.arrival_timestamp_sec,
            "fare_jpy": leg.fare_jpy, "stops": stops_pts, "stops_count": leg.intermediate_stops_count + 2 if lmode != "walk" else 0,
            "path": path, "provenance": str(getattr(leg.provenance, "value", leg.provenance)),
            "provenance_badge": leg.provenance_badge, "color": leg.route_color or ("#0284C7" if kind == "bus" else "#D97706"),
            "time_type": "SCHEDULED",
        })
    last_arr_sec = j.legs[-1].arrival_timestamp_sec
    walk_out_min = walk_minutes_for_m(dd)
    segments.append({
        "kind": "walk", "label": f"Walk to {b_name}",
        "from": {"name": dst.stop_name_en or dst.stop_name_ja, "lat": dst.lat, "lon": dst.lon, "stop_id": dsid},
        "to": {"name": b_name, "lat": b_lat, "lon": b_lon},
        "minutes": walk_out_min, "distance_m": round(dd * 1.3), "departure": clock(last_arr_sec),
        "arrival": clock(last_arr_sec + walk_out_min * 60), "path": [[dst.lat, dst.lon], [b_lat, b_lon]],
        "provenance": "ESTIMATED_WALK", "color": "#64748B",
    })
    total_arr_sec = last_arr_sec + walk_out_min * 60
    alternatives = []
    for alt in best["alts"][:3]:
        if _journey_modes_ok(alt, mode):
            alternatives.append({
                "departure": alt.departure_time, "arrival": alt.arrival_time,
                "duration_minutes": alt.total_duration_minutes, "transfers": alt.transfers_count,
                "fare_jpy": alt.total_fare_jpy,
                "summary": " → ".join(f"{l.operator} {l.route_short_name or l.route_long_name}" for l in alt.legs if str(getattr(l.mode, 'value', l.mode)) != 'walk'),
            })
    return {
        "available": True,
        "minutes": int(round((total_arr_sec - start_sec) / 60.0)),
        "wait_minutes": int(wait),
        "arrive_sec": total_arr_sec,
        "start_sec": start_sec,
        "depart_clock": clock(start_sec),
        "arrive_clock": clock(total_arr_sec),
        "fare_jpy": j.total_fare_jpy,
        "transfers": j.transfers_count,
        "segments": segments,
        "alternatives": alternatives,
        "warnings": list(j.warnings),
        "provenance": "GTFS-JP static timetable (scheduled, not live)",
        "provenance_badges": list(j.provenance_badges),
        "search_date": best["res"].search_date,
        "time_type": "SCHEDULED",
    }


@lru_cache(maxsize=2048)
def _leg_cached(a_lat, a_lon, b_lat, b_lon, mode, when_iso, a_name, b_name):
    when = datetime.fromisoformat(when_iso)
    if mode in SURFACE_MODES:
        leg = surface_leg(a_lat, a_lon, b_lat, b_lon, mode)
        sec = int((when - when.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
        seg = {
            "kind": leg["kind"], "label": f"{MODE_LABELS[mode]} to {b_name}",
            "from": {"name": a_name, "lat": a_lat, "lon": a_lon}, "to": {"name": b_name, "lat": b_lat, "lon": b_lon},
            "minutes": leg["minutes"], "distance_km": leg["distance_km"], "path": leg["path"],
            "departure": min_to_hhmm(sec // 60), "arrival": min_to_hhmm(sec // 60 + leg["minutes"]),
            "provenance": leg["provenance"], "color": {"walk": "#64748B", "bike": "#16A34A", "drive": "#7C3AED"}[leg["kind"]],
        }
        return {
            "available": True, "minutes": leg["minutes"], "wait_minutes": 0, "arrive_sec": sec + leg["minutes"] * 60,
            "start_sec": sec, "fare_jpy": None, "transfers": 0, "segments": [seg], "alternatives": [],
            "warnings": (["Estimated with a detour factor; configure OSRM_BASE_URL for routed geometry."] if leg["provenance"].startswith("ESTIMATED") else []),
            "provenance": leg["provenance"], "distance_km": leg["distance_km"], "direct_km": leg["direct_km"],
            "time_type": "ESTIMATE",
        }
    return transit_leg(a_lat, a_lon, b_lat, b_lon, mode, when, a_name, b_name)


def compute_leg(a: Dict[str, Any], b: Dict[str, Any], mode: str, when: datetime) -> Dict[str, Any]:
    when = when.replace(second=0, microsecond=0)
    leg = _leg_cached(round(a["lat"], 5), round(a["lon"], 5), round(b["lat"], 5), round(b["lon"], 5),
                      mode, when.isoformat(), a["name"], b["name"])
    return json.loads(json.dumps(leg, default=str))  # deep copy, safe to mutate


# --------------------------------------------------------------------------------------
# Crowd helpers (simulated / forecast – never live)
# --------------------------------------------------------------------------------------
def crowd_for(place_id: str, scenario: str) -> Dict[str, Any]:
    from backend.app.services.crowd.crowd_service import crowd_service
    cs = crowd_service.get_place_crowd_status(place_id, scenario)  # type: ignore[arg-type]
    return {"level": cs.level, "score": cs.score, "classification": "SIMULATED", "advisory": cs.advisory,
            "peak_hours": cs.historical_peak_hours}


def forecast_for(place_id: str, d: date_cls, minute_of_day: int) -> Dict[str, Any]:
    from backend.app.services.crowd.seasonal_predictor import SeasonalCrowdForecast
    from datetime import time as dtime
    fc = SeasonalCrowdForecast.get_forecast(place_id, target_date=d, target_time=dtime(min(23, minute_of_day // 60), minute_of_day % 60))
    return {"score": fc["score"], "level": fc["level"], "level_label": fc["level_label"], "advisory": fc.get("advisory"),
            "provenance": "FORECAST"}


# --------------------------------------------------------------------------------------
# Recommendation / catalogue
# --------------------------------------------------------------------------------------
@dataclass
class DiscoveryQuery:
    origin_lat: float
    origin_lon: float
    origin_name: str = "Origin"
    mode: str = "fujikyu_bus"
    max_km: Optional[float] = None
    view: str = "recommended"  # recommended | catalogue
    discovery_type: Optional[str] = None  # FAMOUS | HIDDEN_GEM
    category: Optional[str] = None
    q: Optional[str] = None
    crowd: Optional[str] = None  # low | moderate | high
    crowd_pref: str = "balanced"  # quiet | balanced | popular
    scenario: str = "moderate"
    open_now: bool = False
    visit_date: Optional[str] = None
    departure_time: str = "09:30"
    time_budget_min: int = 300
    require_accessible: bool = False
    page: int = 1
    page_size: int = 12
    with_transit_details: bool = True


def _visit_dt(q: DiscoveryQuery) -> datetime:
    d = date_cls.fromisoformat(q.visit_date) if q.visit_date else datetime.now().date()
    h, m = (q.departure_time or "09:30").split(":")[:2]
    return datetime(d.year, d.month, d.day, int(h), int(m))


def _score_place(item: Dict[str, Any], q: DiscoveryQuery, place: Dict[str, Any]) -> Tuple[float, List[str]]:
    score = 0.0
    reasons: List[str] = []
    mins = item.get("travel_minutes")
    half_budget = max(20, q.time_budget_min / 2)
    if mins is not None:
        prox = max(0.0, 1.0 - mins / half_budget) * 28
        score += prox
        if mins <= 15:
            reasons.append(f"Very close ({mins} min by {MODE_LABELS[q.mode].lower()})")
        elif mins <= 40:
            reasons.append(f"{mins} min by {MODE_LABELS[q.mode].lower()}")
    if q.mode in TRANSIT_MODES and item.get("transit"):
        t = item["transit"]
        if t.get("transfers") == 0:
            score += 12
            reasons.append("Direct service, no transfer")
        else:
            score += 5
            reasons.append(f"{t.get('transfers')} transfer(s)")
    crowd = item["crowd"]["score"]
    if q.crowd_pref == "quiet":
        score += (100 - crowd) / 100 * 22
        if crowd < 40:
            reasons.append("Quiet (simulated crowd level)")
    elif q.crowd_pref == "popular":
        score += crowd / 100 * 10
    else:
        score += (100 - abs(crowd - 50)) / 100 * 10
    fv = place.get("fuji_view_rating") or 0
    score += fv * 3
    if fv >= 4:
        reasons.append(f"Mount Fuji view ★{fv}/5")
    if place.get("accessibility_status") == "VERIFIED_ACCESSIBLE":
        score += 6 if q.require_accessible else 3
        if q.require_accessible:
            reasons.append("Verified accessible")
    elif q.require_accessible:
        score -= 20
    if place.get("general_admission_type") == "FREE":
        score += 4
        reasons.append("Free admission")
    os_ = item["open"]["status"]
    if os_ == "closed":
        score -= 40
    elif os_ == "seasonal_closure":
        score -= 30
        reasons.append("Seasonal closure may apply")
    elif os_ == "open":
        score += 5
    if q.category and place.get("primary_category") == q.category:
        score += 6
        reasons.append(f"Matches category: {q.category}")
    if place.get("discovery_type") == "HIDDEN_GEM":
        reasons.append("Hidden gem")
    return round(score, 1), reasons[:4]


def _evaluate(place: Dict[str, Any], q: DiscoveryQuery, vdt: datetime) -> Dict[str, Any]:
    direct = haversine_km(q.origin_lat, q.origin_lon, place["latitude"], place["longitude"])
    mod = vdt.hour * 60 + vdt.minute
    item: Dict[str, Any] = {
        "place_id": place["place_id"], "name_en": place.get("name_en") or place["name_ja"], "name_ja": place["name_ja"],
        "latitude": place["latitude"], "longitude": place["longitude"],
        "primary_category": place["primary_category"], "discovery_type": place["discovery_type"],
        "fuji_view_rating": place.get("fuji_view_rating"), "image_url": place.get("image_url"),
        "accessibility_status": place.get("accessibility_status"),
        "general_admission_type": place.get("general_admission_type"),
        "general_admission_fee_jpy": place.get("general_admission_fee_jpy"),
        "estimated_visit_duration_minutes": place.get("estimated_visit_duration_minutes") or 60,
        "direct_km": round(direct, 2),
        "crowd": crowd_for(place["place_id"], q.scenario),
        "open": place_open_status(place, vdt.date(), mod),
        "region_id": place.get("region_id"),
    }
    mode = q.mode
    if mode in SURFACE_MODES:
        prof = SURFACE_PROFILE[mode]
        dist = direct * prof["detour"]
        item.update({
            "travel_km": round(dist, 2), "travel_minutes": max(1, int(round(dist / prof["kmh"] * 60))),
            "distance_basis": f"ESTIMATED_DETOUR_x{prof['detour']}", "reachable": True,
            "transport_note": f"{MODE_LABELS[mode]} estimate (straight line × {prof['detour']}); not a verified routed path.",
        })
        if mode == "bike":
            item["bike_rental"] = {"status": "NO_VERIFIED_DATA", "note": "No verified bicycle-rental dataset is configured; cycling time is a route estimate only."}
    else:
        tr = transit_reachability(q.origin_lat, q.origin_lon, place, mode)
        item["transit"] = tr
        item["reachable"] = bool(tr.get("reachable"))
        item["travel_km"] = None
        item["distance_basis"] = "DIRECT_KM_ONLY (distance along the route is not published in the timetable feed)"
        if tr["reachable"]:
            approx_walk = walk_minutes_for_m(tr["boarding_walk_m"]) + walk_minutes_for_m(tr["alight_walk_m"])
            item["travel_minutes"] = None
            item["walk_connection_minutes"] = approx_walk
            item["transport_note"] = (
                f"{MODE_LABELS[mode]}: connection exists in the timetable graph"
                f"{'' if tr['transfers'] == 0 else f' with {tr['transfers']} transfer(s)'}; "
                f"~{tr['alight_walk_m']} m walk from the alighting stop (estimate). Exact times shown when you pick the place."
            )
        else:
            item["travel_minutes"] = None
            item["transport_note"] = f"No {MODE_LABELS[mode].lower()} connection: {tr.get('reason')}"
    return item


def discover(q: DiscoveryQuery) -> Dict[str, Any]:
    if q.mode not in ALL_MODES:
        raise ValueError(f"Unsupported travel mode '{q.mode}'. Supported: {sorted(ALL_MODES)}")
    vdt = _visit_dt(q)
    places = load_all_places()
    counts = catalogue_counts()
    evaluated: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []
    for p in places:
        evaluated.append((p, _evaluate(p, q, vdt)))

    reachable_by_mode = sum(1 for _, it in evaluated if it["reachable"])

    # Distance/mode narrowing applies to the RECOMMENDED view only; the catalogue is never narrowed by it.
    def passes_common(p, it) -> bool:
        if q.discovery_type and p["discovery_type"] != q.discovery_type.upper():
            return False
        if q.category and p["primary_category"] != q.category:
            return False
        if q.q:
            needle = q.q.lower()
            hay = " ".join(str(p.get(k) or "") for k in ("name_ja", "name_en", "sub_category", "interests", "description", "municipality", "region_id")).lower()
            if needle not in hay:
                return False
        if q.crowd and it["crowd"]["level"].lower() != q.crowd.lower():
            return False
        if q.open_now and it["open"]["status"] in ("closed", "seasonal_closure"):
            return False
        if q.require_accessible and p.get("accessibility_status") != "VERIFIED_ACCESSIBLE":
            return False
        return True

    common = [(p, it) for p, it in evaluated if passes_common(p, it)]

    def within_distance(it) -> bool:
        if q.max_km is None:
            return True
        km = it["travel_km"] if it.get("travel_km") is not None else it["direct_km"]
        return km <= q.max_km

    recommended_pool = [(p, it) for p, it in common if it["reachable"] and within_distance(it)]
    for p, it in recommended_pool:
        it["score"], it["reasons"] = _score_place(it, q, p)
    recommended_pool.sort(key=lambda x: (-x[1]["score"], x[1]["direct_km"]))

    if q.view == "catalogue":
        listing = sorted(common, key=lambda x: x[1]["direct_km"])
        for p, it in listing:
            if "score" not in it:
                it["score"], it["reasons"] = _score_place(it, q, p)
            if not it["reachable"]:
                it["warning"] = it["transport_note"]
    else:
        listing = recommended_pool

    filtered_total = len(listing)
    page_size = max(1, min(60, q.page_size))
    total_pages = max(1, math.ceil(filtered_total / page_size))
    page = max(1, min(q.page, total_pages))
    page_items = [it for _, it in listing[(page - 1) * page_size: page * page_size]]

    if q.with_transit_details and q.mode in TRANSIT_MODES:
        origin = {"name": q.origin_name, "lat": q.origin_lat, "lon": q.origin_lon}
        for it in page_items[:12]:  # exact RAPTOR details for the first 12 cards; the rest use graph availability only
            if not it["reachable"]:
                continue
            leg = compute_leg(origin, {"name": it["name_en"], "lat": it["latitude"], "lon": it["longitude"]}, q.mode, vdt)
            if leg["available"]:
                it["travel_minutes"] = leg["minutes"]
                it["transit"].update({
                    "service_on_date": True, "next_departure": leg["segments"][1]["departure"] if len(leg["segments"]) > 1 else None,
                    "arrival": leg["arrive_clock"], "fare_jpy": leg["fare_jpy"], "transfers": leg["transfers"],
                    "time_type": "SCHEDULED",
                })
            else:
                it["transit"]["service_on_date"] = False
                it["transit"]["service_note"] = leg.get("reason")
                it["transport_note"] = f"Connection exists in the network graph, but {leg.get('reason')}"

    top_recommended = [it for _, it in recommended_pool[:8]]
    if q.view != "recommended" and top_recommended and q.with_transit_details and q.mode in TRANSIT_MODES:
        pass  # transit details for recommended strip are attached lazily by the UI via /route

    bands = DISTANCE_BANDS[q.mode]
    return {
        "counts": {
            "total": counts["total"], "famous": counts["famous"], "hidden_gems": counts["hidden_gems"],
            "reachable_by_mode": reachable_by_mode,
            "matching_filters": len(common),
            "recommended": len(recommended_pool),
            "showing": filtered_total,
        },
        "mode": q.mode, "mode_label": MODE_LABELS[q.mode],
        "origin": {"name": q.origin_name, "lat": q.origin_lat, "lon": q.origin_lon},
        "distance_bands_km": bands, "max_km": q.max_km,
        "explanation": (f"Recommendations updated for {MODE_LABELS[q.mode]} travel from {q.origin_name}"
                        + (f" within {q.max_km:g} km" if q.max_km else "") + "."),
        "distance_note": ("Walking/bicycle/road distances are estimates (straight-line × detour factor) unless a routing provider is configured."
                          if q.mode in SURFACE_MODES else
                          "Public-transport filtering uses straight-line distance as the radius; availability and times come from the timetable."),
        "view": q.view, "page": page, "page_size": page_size, "total_pages": total_pages,
        "items": page_items,
        "recommended_preview": top_recommended if q.view == "catalogue" else [],
        "categories": sorted({p["primary_category"] for p in places}),
        "crowd_classification": "SIMULATED (no live telemetry)",
        "visit_date": vdt.date().isoformat(),
    }


# --------------------------------------------------------------------------------------
# Single route (popup + map)
# --------------------------------------------------------------------------------------
def build_route(origin: Dict[str, Any], place_id: str, mode: str, when: datetime) -> Dict[str, Any]:
    place = get_place(place_id)
    if not place:
        raise ValueError(f"Place '{place_id}' not found in the canonical database.")
    dest = {"name": place.get("name_en") or place["name_ja"], "lat": place["latitude"], "lon": place["longitude"]}
    leg = compute_leg(origin, dest, mode, when)
    result: Dict[str, Any] = {
        "mode": mode, "mode_label": MODE_LABELS[mode], "origin": origin,
        "destination": {**dest, "place_id": place_id, "name_ja": place["name_ja"]},
        "departure_query": when.isoformat(timespec="minutes"),
    }
    if not leg["available"]:
        fallbacks = []
        for m in ("walk", "bike", "taxi"):
            f = surface_leg(origin["lat"], origin["lon"], dest["lat"], dest["lon"], m)
            fallbacks.append({"mode": m, "mode_label": MODE_LABELS[m], "minutes": f["minutes"], "distance_km": f["distance_km"], "provenance": f["provenance"],
                              "note": "Estimate only – not a scheduled service."})
        result.update({"available": False, "reason": leg.get("reason"), "fallback_estimates": fallbacks, "segments": [], "steps": [],
                       "summary": None, "warnings": ["No service is invented: pick another travel mode or time."]})
        return result
    segs = leg["segments"]
    steps = []
    for i, s in enumerate(segs, 1):
        if s["kind"] == "walk":
            steps.append(f"{i}. Walk {s['minutes']} min to {s['to']['name']}")
        elif s["kind"] in ("bus", "rail"):
            steps.append(f"{i}. Board {s['label']} at {s['from']['name']} ({s['departure']} scheduled) → alight at {s['to']['name']} ({s['arrival']} scheduled)")
        else:
            steps.append(f"{i}. {s['label']} ({s['minutes']} min, {s.get('distance_km')} km)")
    steps.append(f"{len(segs) + 1}. Begin sightseeing at {dest['name']}")
    fare = leg.get("fare_jpy")
    transit_segs = [s for s in segs if s["kind"] in ("bus", "rail")]
    result.update({
        "available": True, "segments": segs, "steps": steps,
        "alternatives": leg.get("alternatives", []),
        "summary": {
            "total_minutes": leg["minutes"], "wait_minutes": leg.get("wait_minutes", 0), "transfers": leg.get("transfers", 0),
            "fare_jpy": fare, "fare_status": "VERIFIED_GTFS_FARE" if fare is not None else "UNAVAILABLE",
            "depart": segs[0]["departure"], "arrive": segs[-1]["arrival"],
            "distance_km": leg.get("distance_km"), "direct_km": round(haversine_km(origin["lat"], origin["lon"], dest["lat"], dest["lon"]), 2),
            "time_type": leg.get("time_type"), "provenance": leg.get("provenance"),
            "live_arrival": "UNAVAILABLE (no GTFS-Realtime feed configured)" if transit_segs else None,
        },
        "warnings": leg.get("warnings", []),
    })
    return result


# --------------------------------------------------------------------------------------
# Timeline engine (itinerary + recalibration)
# --------------------------------------------------------------------------------------
def _meal_step(label: str, start_min: int, minutes: int, styles: List[str], where: str, experience: str, meal_type: str) -> Dict[str, Any]:
    return {
        "step_type": "MEAL", "meal_type": meal_type, "title": label, "location_name": where,
        "start_min": start_min, "end_min": start_min + minutes, "duration_minutes": minutes,
        "food_styles": styles, "food_experience": experience,
        "venue": None, "venue_status": "NO_VERIFIED_DATA",
        "notes": "No verified restaurant dataset is configured; FujiNova does not name a venue, hours or price it cannot verify. "
                 "Meal time is reserved near this stop.",
        "estimated_cost_jpy": None, "cost_status": "UNVERIFIED",
    }


def build_timeline(
    origin: Dict[str, Any], start_min: int, items: List[Dict[str, Any]], mode: str, d: date_cls,
    return_to_origin: bool = True, scenario: str = "moderate", start_at: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Sequentially build a timetable. items: {'kind':'place','place_id','minutes'} | {'kind':'meal',...}."""
    steps: List[Dict[str, Any]] = []
    cur_min = start_min
    here = start_at or origin
    total_fare = 0
    total_admission = 0
    unknown_admission = 0
    warnings: List[str] = []
    infeasible_reason: Optional[str] = None
    midnight = datetime(d.year, d.month, d.day)

    def add_leg(frm, to, label_suffix=""):
        nonlocal cur_min, total_fare, infeasible_reason
        leg = compute_leg(frm, to, mode, midnight + timedelta(minutes=cur_min))
        if not leg["available"]:
            infeasible_reason = f"No {MODE_LABELS[mode].lower()} connection to {to['name']}: {leg.get('reason')}"
            return False
        for s in leg["segments"]:
            smin = s["minutes"]
            if s["kind"] in ("bus", "rail"):
                dep_m = int(s["dep_sec"] // 60)
                if dep_m > cur_min:
                    steps.append({"step_type": "WAIT", "title": f"Wait for {s['label']} (scheduled departure {s['departure']})",
                                  "location_name": s["from"]["name"], "start_min": cur_min, "end_min": dep_m, "duration_minutes": dep_m - cur_min,
                                  "notes": "Scheduled timetable wait, not a live arrival.", "provenance": s.get("provenance")})
                    cur_min = dep_m
                steps.append({"step_type": "TRANSIT", "mode": s["kind"], "title": f"{s['label']}: {s['from']['name']} → {s['to']['name']}",
                              "location_name": s["from"]["name"], "to_name": s["to"]["name"], "start_min": cur_min,
                              "end_min": cur_min + smin, "duration_minutes": smin, "operator": s.get("operator"),
                              "route_name": s.get("service") or s.get("label"), "route_color": s.get("color"),
                              "fare_jpy": s.get("fare_jpy"), "time_type": "SCHEDULED", "provenance": s.get("provenance_badge") or s.get("provenance"),
                              "path": s.get("path"), "stops": s.get("stops"), "from": s["from"], "to": s["to"]})
                if s.get("fare_jpy"):
                    total_fare += int(s["fare_jpy"])
                cur_min += smin
            else:
                steps.append({"step_type": "WALK" if s["kind"] == "walk" else "TRAVEL", "mode": s["kind"], "title": s["label"],
                              "location_name": s["from"]["name"], "to_name": s["to"]["name"], "start_min": cur_min, "end_min": cur_min + smin,
                              "duration_minutes": smin, "distance_km": s.get("distance_km"), "distance_m": s.get("distance_m"),
                              "time_type": "ESTIMATE", "provenance": s.get("provenance"), "path": s.get("path"), "from": s["from"], "to": s["to"]})
                cur_min += smin
        return True

    ok = True
    for it in items:
        if it["kind"] == "place":
            p = get_place(it["place_id"])
            if not p:
                continue
            node = {"name": p.get("name_en") or p["name_ja"], "lat": p["latitude"], "lon": p["longitude"]}
            if (here["lat"], here["lon"]) != (node["lat"], node["lon"]):
                if not add_leg(here, node):
                    ok = False
                    break
            os_ = place_open_status(p, d, cur_min % 1440)
            hrs = parse_hours(p.get("opening_hours_text"))
            if os_["status"] == "closed" and hrs and cur_min % 1440 < hrs[0] and p.get("opening_status") == "REGULAR_HOURS":
                wait = hrs[0] - cur_min % 1440
                warnings.append(f"{node['name']} opens at {min_to_hhmm(hrs[0])}; arrival {min_to_hhmm(cur_min)} is early.")
            elif os_["status"] in ("closed", "seasonal_closure"):
                warnings.append(f"{node['name']}: {os_['note']} (check before visiting).")
            minutes = int(it.get("minutes") or p.get("estimated_visit_duration_minutes") or 60)
            fc = forecast_for(p["place_id"], d, cur_min % 1440)
            fee = p.get("general_admission_fee_jpy")
            if p.get("general_admission_type") == "FREE":
                adm, adm_status = 0, "FREE"
            elif fee is not None:
                adm, adm_status = int(fee), "VERIFIED"
                total_admission += adm
            else:
                adm, adm_status = None, "UNKNOWN"
                unknown_admission += 1
            steps.append({
                "step_type": "SIGHTSEEING", "place_id": p["place_id"], "title": f"Explore {node['name']}", "location_name": node["name"],
                "name_ja": p["name_ja"], "image_url": p.get("image_url"), "discovery_type": p["discovery_type"],
                "start_min": cur_min, "end_min": cur_min + minutes, "duration_minutes": minutes, "planned_minutes": minutes,
                "admission_jpy": adm, "admission_status": adm_status, "crowd_forecast": fc, "open": os_,
                "lat": node["lat"], "lon": node["lon"], "notes": f"Mount Fuji view ★{p.get('fuji_view_rating')}/5",
            })
            cur_min += minutes
            here = node
        elif it["kind"] == "meal":
            minutes = int(it.get("minutes") or 45)
            steps.append(_meal_step(it["title"], cur_min, minutes, it.get("styles", []), here["name"], it.get("experience", "local"), it["meal_type"]))
            cur_min += minutes
    if ok and return_to_origin and (here["lat"], here["lon"]) != (origin["lat"], origin["lon"]):
        # return leg: label so UI can distinguish
        before = len(steps)
        if add_leg(here, origin):
            for s in steps[before:]:
                s["is_return"] = True
        else:
            ok = False

    for idx, s in enumerate(steps, 1):
        s["step_number"] = idx
        s["step_id"] = f"s{idx}_{s['step_type'].lower()}"
        s["start"] = min_to_hhmm(s["start_min"])
        s["end"] = min_to_hhmm(s["end_min"])
    return {
        "steps": steps, "end_min": cur_min, "return_time": min_to_hhmm(cur_min), "feasible_transport": ok,
        "infeasible_reason": infeasible_reason, "warnings": warnings,
        "cost": {"transit_fares_jpy": total_fare, "verified_admissions_jpy": total_admission,
                 "places_with_unknown_admission": unknown_admission,
                 "note": "Fares from GTFS where available; meals and unverified admissions are excluded rather than guessed."},
    }


def _nearby_candidates(main: Dict[str, Any], exclude: List[str], limit_km: float, prefer: Optional[str],
                       scenario: str, d: date_cls, minute_of_day: int, count: int = 6) -> List[Dict[str, Any]]:
    cands = []
    for p in load_all_places():
        if p["place_id"] in exclude:
            continue
        km = haversine_km(main["latitude"], main["longitude"], p["latitude"], p["longitude"])
        if km > limit_km:
            continue
        if prefer and p["discovery_type"] != prefer:
            continue
        st = place_open_status(p, d, minute_of_day)
        if st["status"] in ("closed", "seasonal_closure"):
            continue
        cr = crowd_for(p["place_id"], scenario)
        score = (p.get("fuji_view_rating") or 0) * 3 + (100 - cr["score"]) * 0.12 - km * 2
        cands.append((score, km, p, cr))
    cands.sort(key=lambda x: -x[0])
    return [{"place": p, "km": round(km, 2), "crowd": cr} for _, km, p, cr in cands[:count]]


def plan_trip(params: Dict[str, Any]) -> Dict[str, Any]:
    origin = {"name": params.get("origin_name", "Origin"), "lat": float(params["origin_lat"]), "lon": float(params["origin_lon"])}
    mode = params.get("mode", "fujikyu_bus")
    if mode not in ALL_MODES:
        raise ValueError(f"Unsupported travel mode '{mode}'.")
    d = date_cls.fromisoformat(params["date"]) if params.get("date") else datetime.now().date()
    dep_min = hhmm_to_min(params.get("departure_time", "09:30"))
    budget = int(params.get("time_budget_min", 300))
    scenario = params.get("scenario", "moderate")
    main = get_place(params["place_id"])
    if not main:
        raise ValueError(f"Place '{params['place_id']}' not found.")
    meals = params.get("meals") or {"breakfast": False, "lunch": budget >= 180, "dinner": False}
    styles = params.get("food_styles") or []
    experience = params.get("food_experience") or "local"
    ability = params.get("walking_ability", "normal")
    deadline = dep_min + budget

    visit_main = int(main.get("estimated_visit_duration_minutes") or 60)
    if ability == "limited":
        visit_main = max(30, int(visit_main * 0.75))

    base_items: List[Dict[str, Any]] = [{"kind": "place", "place_id": main["place_id"], "minutes": visit_main}]

    def with_meals(place_items, tl):
        """Insert meals according to the clock after a first pass."""
        items = list(place_items)
        if meals.get("breakfast") and dep_min < 9 * 60 + 30:
            items.insert(0, {"kind": "meal", "meal_type": "breakfast", "title": "Breakfast", "minutes": 30, "styles": styles, "experience": experience})
        return items

    items = with_meals(base_items, None)
    tl = build_timeline(origin, dep_min, items, mode, d, True, scenario)
    if not tl["feasible_transport"]:
        return {
            "feasible": False, "unavailable_reason": tl["infeasible_reason"], "origin": origin, "mode": mode,
            "mode_label": MODE_LABELS[mode], "destination": {"place_id": main["place_id"], "name": main.get("name_en") or main["name_ja"]},
            "steps": [], "date": d.isoformat(),
            "fallback_options": [{"mode": m, "mode_label": MODE_LABELS[m], **{k: v for k, v in surface_leg(origin["lat"], origin["lon"], main["latitude"], main["longitude"], m).items() if k in ("minutes", "distance_km", "provenance")}} for m in ("walk", "bike", "taxi")],
            "message": "No verified connection was found, so no timetable was generated. Estimates for other modes are shown instead.",
        }

    # Add nearby extras greedily while the whole trip still fits (incl. return connection)
    max_extras = 0 if budget < 180 else (1 if budget < 300 else (2 if budget < 420 else 3))
    chosen_ids = [main["place_id"]]
    cands = _nearby_candidates(main, chosen_ids, 8.0, None, scenario, d, (tl["end_min"] - 60) % 1440, 8)
    for c in cands:
        if len(chosen_ids) - 1 >= max_extras:
            break
        p = c["place"]
        trial_items = list(base_items) + [{"kind": "place", "place_id": x, "minutes": None} for x in chosen_ids[1:]]
        trial_items.append({"kind": "place", "place_id": p["place_id"], "minutes": min(60, int(p.get("estimated_visit_duration_minutes") or 45))})
        trial_items = with_meals(trial_items, None)
        trial = build_timeline(origin, dep_min, trial_items, mode, d, True, scenario)
        # lunch space: reserve 45 min if lunch requested and budget allows
        reserve = 45 if meals.get("lunch") and budget >= 180 else 0
        if trial["feasible_transport"] and trial["end_min"] + reserve <= deadline:
            chosen_ids.append(p["place_id"])
            base_items = trial_items if not meals.get("breakfast") else [i for i in trial_items if i["kind"] == "place"]
            base_items = [i for i in trial_items if i["kind"] == "place"]
    place_items = [{"kind": "place", "place_id": main["place_id"], "minutes": visit_main}] + [
        {"kind": "place", "place_id": pid, "minutes": None} for pid in chosen_ids[1:]
    ]
    # Place lunch after the visit that crosses the 11:30–13:30 window (so it fits location and time)
    final_items = with_meals(place_items, None)
    tl = build_timeline(origin, dep_min, final_items, mode, d, True, scenario)
    if meals.get("lunch") and budget >= 180:
        best_idx, best_gap = None, 10**9
        for idx, it in enumerate(final_items):
            if it["kind"] != "place":
                continue
            end_after = next((s["end_min"] for s in tl["steps"] if s.get("place_id") == it["place_id"]), None)
            if end_after is None:
                continue
            gap = abs(end_after - 12 * 60 - 30)
            if 11 * 60 <= end_after <= 14 * 60 and gap < best_gap:
                best_idx, best_gap = idx, gap
        if best_idx is not None:
            final_items.insert(best_idx + 1, {"kind": "meal", "meal_type": "lunch", "title": "Lunch", "minutes": 45, "styles": styles, "experience": experience})
            tl = build_timeline(origin, dep_min, final_items, mode, d, True, scenario)
    if meals.get("dinner") and tl["end_min"] >= 17 * 60 + 30:
        final_items.append({"kind": "meal", "meal_type": "dinner", "title": "Dinner", "minutes": 60, "styles": styles, "experience": experience})
        tl = build_timeline(origin, dep_min, final_items, mode, d, True, scenario)

    feasible = tl["feasible_transport"] and tl["end_min"] <= deadline
    result = {
        "feasible": feasible, "plan_id": f"trip_{origin['name'][:6]}_{main['place_id']}_{dep_min}",
        "title": f"{budget // 60}h {budget % 60:02d}m plan: {main.get('name_en') or main['name_ja']}",
        "origin": origin, "mode": mode, "mode_label": MODE_LABELS[mode], "date": d.isoformat(),
        "departure_time": min_to_hhmm(dep_min), "return_time": tl["return_time"], "deadline": min_to_hhmm(deadline),
        "time_budget_minutes": budget, "total_minutes": tl["end_min"] - dep_min,
        "destination": {"place_id": main["place_id"], "name": main.get("name_en") or main["name_ja"], "name_ja": main["name_ja"]},
        "steps": tl["steps"], "warnings": tl["warnings"], "cost": tl["cost"],
        "preferences": {"food_styles": styles, "food_experience": experience, "meals": meals, "walking_ability": ability,
                        "travellers": params.get("travellers", 1), "budget_jpy": params.get("budget_jpy")},
        "extras_added": len(chosen_ids) - 1,
        "crowd_classification": "FORECAST (seasonal model, not live telemetry)",
    }
    if not feasible:
        over = tl["end_min"] - deadline
        result["revision"] = {
            "reason": f"The plan runs {over} min past your {budget // 60}h {budget % 60:02d}m budget (return {tl['return_time']}).",
            "suggestions": ["Increase the time budget", "Shorten the main visit", "Choose an earlier departure",
                            "Pick a destination closer to the start"],
        }
    return result


# --------------------------------------------------------------------------------------
# Recalibration (early / late)
# --------------------------------------------------------------------------------------
def recalibrate(params: Dict[str, Any]) -> Dict[str, Any]:
    """Re-plan the remainder of the day from the user's current place & clock.

    params: origin_*, mode, date, now_min/now_time, deadline_time (original return), current_place_id,
            remaining: [{place_id, minutes}], planned_end_time (of the just-finished activity), meal_pending(bool),
            scenario
    """
    origin = {"name": params.get("origin_name", "Origin"), "lat": float(params["origin_lat"]), "lon": float(params["origin_lon"])}
    mode = params.get("mode", "fujikyu_bus")
    d = date_cls.fromisoformat(params["date"]) if params.get("date") else datetime.now().date()
    now_min = hhmm_to_min(params["now_time"])
    planned_end = hhmm_to_min(params["planned_end_time"])
    deadline = hhmm_to_min(params["deadline_time"])
    scenario = params.get("scenario", "moderate")
    cur = get_place(params["current_place_id"])
    if not cur:
        raise ValueError("Unknown current_place_id")
    here = {"name": cur.get("name_en") or cur["name_ja"], "lat": cur["latitude"], "lon": cur["longitude"]}
    delta = planned_end - now_min  # positive = ahead of schedule, negative = late
    remaining = params.get("remaining") or []
    visited = set(params.get("visited_place_ids") or []) | {cur["place_id"]}
    meal_pending = bool(params.get("meal_pending", False))
    styles = params.get("food_styles") or []
    experience = params.get("food_experience") or "local"

    def timeline_for(rem_items: List[Dict[str, Any]], extra: Optional[List[Dict[str, Any]]] = None, meal_first=False):
        items: List[Dict[str, Any]] = []
        if meal_first:
            items.append({"kind": "meal", "meal_type": "lunch", "title": "Lunch (earlier)", "minutes": 45, "styles": styles, "experience": experience})
        for e in (extra or []):
            items.append(e)
        for r in rem_items:
            items.append({"kind": "place", "place_id": r["place_id"], "minutes": r.get("minutes")})
        return build_timeline(origin, now_min, items, mode, d, True, scenario, start_at=here)

    original_tl = timeline_for(remaining)
    base_summary = {
        "return_time": original_tl["return_time"], "feasible": original_tl["feasible_transport"] and original_tl["end_min"] <= deadline,
        "steps": original_tl["steps"], "infeasible_reason": original_tl["infeasible_reason"],
    }
    situation = "early" if delta >= 10 else ("late" if delta <= -10 else "on_time")
    options: List[Dict[str, Any]] = []

    def option(oid, label, why, tl, extra_diff=None):
        fits = tl["feasible_transport"] and tl["end_min"] <= deadline
        return {
            "id": oid, "label": label, "why": why, "return_time": tl["return_time"], "fits_deadline": fits,
            "minutes_vs_deadline": deadline - tl["end_min"], "steps": tl["steps"], "warnings": tl["warnings"],
            "transport_ok": tl["feasible_transport"], "infeasible_reason": tl["infeasible_reason"],
            "differences": extra_diff or [], "cost": tl["cost"],
        }

    if situation in ("early", "on_time") and delta > 0:
        saved = delta
        spare_end = deadline - original_tl["end_min"] if original_tl["feasible_transport"] else saved
        usable = max(0, min(spare_end, 10**6))
        # 1 & 2: nearby hidden gem / famous destination that fits
        for oid, label, prefer in (("nearby_hidden_gem", "Visit a nearby hidden gem", "HIDDEN_GEM"),
                                   ("nearby_famous", "Visit another famous destination", "FAMOUS")):
            cands = _nearby_candidates(cur, list(visited) + [r["place_id"] for r in remaining], 10.0, prefer, scenario, d, now_min % 1440, 6)
            picked = None
            for c in cands:
                p = c["place"]
                minutes = min(45, int(p.get("estimated_visit_duration_minutes") or 45))
                tl = timeline_for(remaining, [{"kind": "place", "place_id": p["place_id"], "minutes": minutes}])
                if tl["feasible_transport"] and tl["end_min"] <= deadline:
                    picked = (c, tl)
                    break
            if picked:
                c, tl = picked
                p = c["place"]
                options.append(option(oid, f"{label}: {p.get('name_en') or p['name_ja']}",
                                      f"{c['km']} km away, crowd {c['crowd']['level'].lower()} (simulated), Fuji view ★{p.get('fuji_view_rating')}/5; "
                                      f"the connection and return fit before {min_to_hhmm(deadline)}.",
                                      tl, [f"Added: {p.get('name_en') or p['name_ja']}"]))
            else:
                options.append({"id": oid, "label": label, "why": "No candidate fits the remaining time with a verified connection and return.",
                                "unavailable": True})
        cafe_tl = timeline_for(remaining, [{"kind": "meal", "meal_type": "cafe", "title": "Café break", "minutes": min(30, max(15, saved)), "styles": ["Cafés & Desserts"], "experience": experience}])
        options.append(option("cafe_break", "Take a café break", f"Uses {min(30, max(15, saved))} of your {saved} spare minutes; no venue is named because no verified café data exists.", cafe_tl, ["Added: café break"]))
        if meal_pending:
            lunch_tl = timeline_for(remaining, meal_first=True)
            options.append(option("lunch_earlier", "Have lunch earlier", "You are ahead of schedule, so the meal moves to now and later stops shift accordingly.", lunch_tl, ["Meal moved earlier"]))
        ret_tl = timeline_for([])
        options.append(option("return_earlier", "Return earlier", "Skips the remaining activities and heads back now.", ret_tl,
                              [f"Removed: {r['place_id']}" for r in remaining] or ["No remaining activities"]))
    elif situation == "late" or delta < 0:
        late = -delta
        options.append(option("keep_plan", "Keep the original plan", f"You are {late} min behind; this shows the real impact on later connections.", original_tl, []))
        for r in remaining:
            rest = [x for x in remaining if x["place_id"] != r["place_id"]]
            tl = timeline_for(rest)
            options.append(option(f"skip_{r['place_id']}", f"Skip {(get_place(r['place_id']) or {}).get('name_en', r['place_id'])}", "Removes this stop; the destination you selected is never deleted automatically.", tl,
                                  [f"Removed: {r['place_id']}"]))
        short = [{"place_id": r["place_id"], "minutes": min(30, int(r.get("minutes") or 45))} for r in remaining]
        options.append(option("shorten", "Shorten sightseeing (max 30 min each)", "Keeps every stop but trims time at each.", timeline_for(short), ["Shortened remaining visits"]))
        if mode in TRANSIT_MODES:
            alt_mode = "mixed" if mode != "mixed" else "taxi"
            tl = build_timeline(origin, now_min, [{"kind": "place", "place_id": r["place_id"], "minutes": r.get("minutes")} for r in remaining], alt_mode, d, True, scenario, start_at=here)
            options.append(option("other_transport", f"Use another connection ({MODE_LABELS[alt_mode]})", "Alternative transport recalculated from your position.", tl, [f"Transport: {MODE_LABELS[alt_mode]}"]))
        options.append(option("recalculate_all", "Recalculate my entire trip", "Re-plans the remainder from your current place and clock.", original_tl, []))
    else:
        options.append(option("keep_plan", "Keep the original plan", "You are within 10 minutes of schedule.", original_tl, []))

    return {
        "situation": situation, "delta_minutes": delta, "current_place": here["name"],
        "headline": (f"You finished {here['name']} {delta} minutes earlier than planned!" if situation == "early" else
                     f"You are running {-delta} minutes behind schedule at {here['name']}." if situation == "late" else
                     f"You are on schedule at {here['name']}."),
        "extra_minutes": max(0, delta), "deadline": min_to_hhmm(deadline), "now": min_to_hhmm(now_min),
        "original_remaining": base_summary, "options": options,
        "note": "Times are scheduled/estimated; nothing is live. You choose whether to apply a revision.",
    }


# --------------------------------------------------------------------------------------
# Crowd-aware timing
# --------------------------------------------------------------------------------------
def crowd_timing(origin: Dict[str, Any], place_id: str, mode: str, d: date_cls, preferred_min: int, scenario: str = "moderate") -> Dict[str, Any]:
    place = get_place(place_id)
    if not place:
        raise ValueError("Unknown place")
    base = forecast_for(place_id, d, preferred_min)
    hours = parse_hours(place.get("opening_hours_text")) or ((0, 1440) if place.get("opening_status") == "ALWAYS_OPEN" else (9 * 60, 17 * 60))
    slots = []
    for m in range(8 * 60, 18 * 60 + 1, 60):
        fc = forecast_for(place_id, d, m)
        arrive_ok, reason = True, None
        if not (hours[0] <= m < hours[1]):
            arrive_ok, reason = False, f"Outside opening hours ({min_to_hhmm(hours[0])}-{min_to_hhmm(hours[1])})"
        transport = None
        if arrive_ok:
            leave = max(0, m - 60)
            # probe: depart so that we arrive ~m; use leg from departure = m-45
            leg = compute_leg(origin, {"name": place.get("name_en") or place["name_ja"], "lat": place["latitude"], "lon": place["longitude"]},
                              mode, datetime(d.year, d.month, d.day) + timedelta(minutes=max(0, m - 45)))
            if leg["available"]:
                arr = int(leg["arrive_sec"] // 60)
                transport = {"available": True, "depart": min_to_hhmm(int(leg["start_sec"] // 60)), "arrive": min_to_hhmm(arr), "time_type": leg.get("time_type")}
                if arr >= hours[1]:
                    arrive_ok, reason = False, "Arrival would be after closing"
            else:
                arrive_ok, reason = False, leg.get("reason")
                transport = {"available": False, "reason": leg.get("reason")}
        slots.append({"time": min_to_hhmm(m), "minute": m, "crowd_score": fc["score"], "crowd_level": fc["level_label"], "feasible": arrive_ok,
                      "infeasible_reason": reason, "transport": transport, "provenance": "FORECAST"})
    feasible = [s for s in slots if s["feasible"]]
    earlier = [s for s in feasible if s["minute"] < preferred_min]
    later = [s for s in feasible if s["minute"] > preferred_min]
    best_earlier = min(earlier, key=lambda s: s["crowd_score"]) if earlier else None
    best_later = min(later, key=lambda s: s["crowd_score"]) if later else None
    alts = []
    for p in _nearby_candidates(place, [place_id], 12.0, None, scenario, d, preferred_min, 6):
        c = p["place"]
        alts.append({"place_id": c["place_id"], "name_en": c.get("name_en") or c["name_ja"], "km": p["km"],
                     "crowd_level": p["crowd"]["level"], "crowd_score": p["crowd"]["score"], "classification": "SIMULATED"})
    alts.sort(key=lambda a: a["crowd_score"])
    busy = base["score"] >= 70
    return {
        "place_id": place_id, "name_en": place.get("name_en") or place["name_ja"], "date": d.isoformat(),
        "preferred_time": min_to_hhmm(preferred_min), "forecast_at_preferred": base, "is_busy": busy,
        "message": (f"{place.get('name_en') or place['name_ja']} is expected to be {base['level_label'].lower()} around {min_to_hhmm(preferred_min)}."),
        "options": {
            "A_visit_earlier": best_earlier, "B_visit_later": best_later,
            "C_other_attraction_first": alts[0] if alts else None,
            "D_quieter_alternatives": alts[:3],
        },
        "slots": slots,
        "classification": "FORECAST / SIMULATED – not verified live telemetry",
    }
