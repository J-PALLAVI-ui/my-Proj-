"""
FujiNova Station Distance & Comparison Matrix Service.
Provides high-speed lookup across all 8 hubs and 237 destinations for all 6 travel modes.
"""
import os
import json
from typing import Dict, Any, Optional, List

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
MATRIX_FILE = os.path.join(BASE_DIR, "backend/data/station_distance_matrix.json")

_MATRIX_CACHE: Optional[Dict[str, Any]] = None


def load_matrix() -> Dict[str, Any]:
    global _MATRIX_CACHE
    if _MATRIX_CACHE is None:
        if os.path.exists(MATRIX_FILE):
            with open(MATRIX_FILE, "r", encoding="utf-8") as f:
                _MATRIX_CACHE = json.load(f)
        else:
            _MATRIX_CACHE = {"hubs": {}, "routes": {}, "comparisons": {}}
    return _MATRIX_CACHE


def resolve_hub_id(hub_name_or_coords: str) -> str:
    s = (hub_name_or_coords or "").lower()
    if "5th" in s or "五合目" in s:
        return "mt_fuji_5th"
    if "shimoyoshida" in s or "下吉田" in s:
        return "shimoyoshida"
    if "highland" in s or "ハイランド" in s:
        return "fujiq_highland"
    if "fujisan" in s or "富士山駅" in s:
        return "fujisan"
    if "shin-fuji" in s or "新富士" in s:
        return "shin_fuji"
    if "mishima" in s or "三島" in s:
        return "mishima"
    if "gotemba" in s or "御殿場" in s:
        return "gotemba"
    # Default hub is Kawaguchiko
    return "kawaguchiko"


def get_route_details(origin_hub: str, place_id: str, mode: str = "fujikyu_bus") -> Optional[Dict[str, Any]]:
    matrix = load_matrix()
    hub_id = resolve_hub_id(origin_hub)
    key = f"{hub_id}:{place_id}"
    route = matrix.get("routes", {}).get(key)
    if not route:
        return None
    mode_info = route.get("modes", {}).get(mode, route.get("modes", {}).get("fujikyu_bus", {}))
    return {
        "hub_id": hub_id,
        "hub_name": matrix.get("hubs", {}).get(hub_id, {}).get("name", origin_hub),
        "place_id": place_id,
        "place_name": route.get("place_name"),
        "distance_km": mode_info.get("distance_km", route.get("road_km")),
        "duration_min": mode_info.get("duration_min", 30),
        "fare_jpy": mode_info.get("fare_jpy"),
        "line": mode_info.get("line"),
        "feasible": mode_info.get("feasible", True),
        "mode": mode,
    }


def get_origin_comparison(
    place_ids: List[str],
    origin_a: str = "Kawaguchiko Station",
    origin_b: str = "Mt. Fuji 5th Station"
) -> List[Dict[str, Any]]:
    matrix = load_matrix()
    hub_a = resolve_hub_id(origin_a)
    hub_b = resolve_hub_id(origin_b)
    hub_a_name = matrix.get("hubs", {}).get(hub_a, {}).get("name", origin_a)
    hub_b_name = matrix.get("hubs", {}).get(hub_b, {}).get("name", origin_b)

    results = []
    comparisons = matrix.get("comparisons", {})

    for pid in place_ids:
        place_comp = comparisons.get(pid, {})
        data_a = place_comp.get(hub_a, {"distance_km": 4.2, "duration_min": 12})
        data_b = place_comp.get(hub_b, {"distance_km": 28.7, "duration_min": 58})

        # Format human-friendly time
        def format_dur(m: int) -> str:
            if m < 60:
                return f"{m} min"
            h = m // 60
            mins = m % 60
            return f"{h} h {mins:02d} min" if mins else f"{h} h"

        results.append({
            "place_id": pid,
            "origin_a": {
                "hub_id": hub_a,
                "hub_name": hub_a_name,
                "distance_km": data_a.get("distance_km"),
                "duration_min": data_a.get("duration_min"),
                "formatted_time": format_dur(data_a.get("duration_min", 15)),
                "fare_jpy": data_a.get("fare_jpy", 340),
            },
            "origin_b": {
                "hub_id": hub_b,
                "hub_name": hub_b_name,
                "distance_km": data_b.get("distance_km"),
                "duration_min": data_b.get("duration_min"),
                "formatted_time": format_dur(data_b.get("duration_min", 60)),
                "fare_jpy": data_b.get("fare_jpy", 1570),
            }
        })
    return results
