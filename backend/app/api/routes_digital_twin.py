"""FujiNova 3D Digital Twin Region & Spatial Intelligence API."""
import math
from typing import Dict, Any, List
from fastapi import APIRouter, Query, status

from backend.app.models.place import Place
from backend.app.api.routes_places import search_places_db
from backend.app.services.crowd.crowd_service import crowd_service
from backend.app.services.crowd.crowd_models import CrowdScenario
from backend.app.services.crowd.attraction_images import get_attraction_image
from backend.app.services.live_info.weather_service import get_weather_info
from backend.app.services.routing.routing_service import get_routing_service

router = APIRouter(prefix="/api/v1/digital-twin", tags=["Digital Twin 3D"])

# Mount Fuji Summit Reference Origin (Center of 3D Scene)
FUJI_SUMMIT_LAT = 35.3606
FUJI_SUMMIT_LON = 138.7274

# Geographic projection scale: 1 degree lat ~ 110.9 km, 1 degree lon ~ 90.7 km
# We map 1 km to ~3.2 Three.js world units
SCALE_KM_TO_3D = 3.2
KM_PER_DEG_LAT = 110.9
KM_PER_DEG_LON = 90.7


def project_lat_lon_to_3d(lat: float, lon: float) -> Dict[str, float]:
    """Projects geographic WGS84 coordinates into Three.js 3D world space (X = East, Z = South)."""
    delta_lat = lat - FUJI_SUMMIT_LAT
    delta_lon = lon - FUJI_SUMMIT_LON

    # Three.js: +X = East, -X = West, -Z = North, +Z = South
    x = delta_lon * KM_PER_DEG_LON * SCALE_KM_TO_3D
    z = -(delta_lat * KM_PER_DEG_LAT * SCALE_KM_TO_3D)

    # Estimate base altitude: closer to Fuji summit gets elevated
    dist_to_summit = math.sqrt(x * x + z * z)
    if dist_to_summit < 35.0:
        altitude = max(1.2, 38.0 * math.exp(-dist_to_summit * 0.08))
    elif z < -30.0:  # Northern Misaka ridge
        altitude = 3.0 + math.sin(x * 0.1) * 1.5
    else:
        altitude = 1.2 + math.sin(x * 0.05 + z * 0.05) * 0.6

    return {"x": round(x, 2), "z": round(z, 2), "altitude": round(altitude, 2)}


# The 5 Fuji Lakes with geographic centers and dimension scales
FUJI_FIVE_LAKES = [
    {
        "id": "lake_kawaguchiko",
        "name_en": "Lake Kawaguchiko",
        "name_ja": "河口湖",
        "latitude": 35.5167,
        "longitude": 138.7500,
        "elevation_m": 833,
        "area_km2": 5.7,
        "radius_x": 16.0,
        "radius_z": 7.5,
        "color": 0x0284c7,
    },
    {
        "id": "lake_saiko",
        "name_en": "Lake Saiko",
        "name_ja": "西湖",
        "latitude": 35.5000,
        "longitude": 138.6833,
        "elevation_m": 900,
        "area_km2": 2.1,
        "radius_x": 11.0,
        "radius_z": 6.0,
        "color": 0x0284c7,
    },
    {
        "id": "lake_yamanakako",
        "name_en": "Lake Yamanakako",
        "name_ja": "山中湖",
        "latitude": 35.4167,
        "longitude": 138.8667,
        "elevation_m": 980,
        "area_km2": 6.8,
        "radius_x": 18.0,
        "radius_z": 12.0,
        "color": 0x0284c7,
    },
    {
        "id": "lake_shojiko",
        "name_en": "Lake Shojiko",
        "name_ja": "精進湖",
        "latitude": 35.4833,
        "longitude": 138.6000,
        "elevation_m": 900,
        "area_km2": 0.5,
        "radius_x": 6.0,
        "radius_z": 5.0,
        "color": 0x0284c7,
    },
    {
        "id": "lake_motosuko",
        "name_en": "Lake Motosuko",
        "name_ja": "本栖湖",
        "latitude": 35.4667,
        "longitude": 138.5833,
        "elevation_m": 900,
        "area_km2": 4.7,
        "radius_x": 12.0,
        "radius_z": 11.0,
        "color": 0x0284c7,
    },
]


@router.get(
    "/data",
    status_code=status.HTTP_200_OK,
    summary="Get 3D Digital Twin Region Spatial Dataset",
    description="Returns Mount Fuji topography, 5 Lakes, 35 verified destinations, and Fujikyu transit routes."
)
def get_digital_twin_data(
    scenario: CrowdScenario = Query("high", description="Simulated crowd scenario")
) -> Dict[str, Any]:
    # 1. Retrieve all verified places (up to 300)
    raw_places = search_places_db(limit=300)
    places = [Place.model_validate(p) if isinstance(p, dict) else p for p in raw_places]
    crowd_statuses = crowd_service.get_all_places_crowd_status(scenario=scenario)

    landmarks_3d = []
    for p in places:
        proj = project_lat_lon_to_3d(p.latitude, p.longitude)
        cs = crowd_statuses.get(p.place_id)
        img_info = get_attraction_image(p.place_id)
        img_url = p.image_url or img_info["url"]
        img_attr = p.required_attribution or img_info.get("attribution", "")

        admission_str = p.general_admission_type.title()
        if p.general_admission_fee_jpy:
            admission_str = f"¥{p.general_admission_fee_jpy:,}"

        landmarks_3d.append({
            "id": p.place_id,
            "name_en": p.name_en,
            "name_ja": p.name_ja,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "x": proj["x"],
            "z": proj["z"],
            "altitude": proj["altitude"],
            "category": p.primary_category,
            "sub_category": p.sub_category,
            "fuji_rating": p.fuji_view_rating or 4,
            "crowd_level": cs.level.lower() if cs else "moderate",
            "crowd_score": cs.score if cs else 50,
            "hours": p.opening_hours_text or "Check schedules",
            "admission": admission_str,
            "description": p.accessibility_evidence or f"Verified attraction located in {p.name_en}.",
            "image_url": img_url,
            "image_attribution": img_attr,
            "accessibility_status": p.accessibility_status,
            "wheelchair": p.accessibility_status == "VERIFIED_ACCESSIBLE",
        })

    # 2. Project Five Lakes into 3D coordinates
    projected_lakes = []
    for lk in FUJI_FIVE_LAKES:
        proj = project_lat_lon_to_3d(lk["latitude"], lk["longitude"])
        projected_lakes.append({
            **lk,
            "x": proj["x"],
            "z": proj["z"],
            "y": 0.35,
        })

    # 3. Fujikyu Railway key stations with projected coordinates
    railway_stations = [
        {"name_en": "Kawaguchiko Station", "name_ja": "河口湖駅", "lat": 35.4981, "lon": 138.7690, "is_terminal": True},
        {"name_en": "Fujikyu-Highland Station", "name_ja": "富士急ハイランド駅", "lat": 35.4883, "lon": 138.7770, "is_terminal": False},
        {"name_en": "Fujisan Station", "name_ja": "富士山駅", "lat": 35.4839, "lon": 138.7958, "is_terminal": True},
        {"name_en": "Gekkouji Station", "name_ja": "月江寺駅", "lat": 35.4925, "lon": 138.8028, "is_terminal": False},
        {"name_en": "Shimoyoshida Station (Chureito)", "name_ja": "下吉田駅", "lat": 35.4983, "lon": 138.8078, "is_terminal": False},
        {"name_en": "Tsurushi Station", "name_ja": "都留市駅", "lat": 35.5539, "lon": 138.9056, "is_terminal": False},
        {"name_en": "Otsuki Station", "name_ja": "大月駅", "lat": 35.6133, "lon": 138.9422, "is_terminal": True},
    ]
    for st in railway_stations:
        p = project_lat_lon_to_3d(st["lat"], st["lon"])
        st["x"] = p["x"]
        st["z"] = p["z"]
        st["altitude"] = p["altitude"]

    # 4. Weather and Environmental conditions
    weather = get_weather_info()

    return {
        "status": "ok",
        "origin": {
            "name": "Mount Fuji Summit (3,776m)",
            "latitude": FUJI_SUMMIT_LAT,
            "longitude": FUJI_SUMMIT_LON,
            "elevation_m": 3776,
        },
        "scenario": scenario,
        "data_provenance": "Official MLIT Geographic Data & GTFS-JP (Fujikyu Bus & Railway)",
        "landmarks": landmarks_3d,
        "lakes": projected_lakes,
        "railway_stations": railway_stations,
        "weather": {
            "month": weather["month"],
            "temperature": weather["temperature_range_celsius"],
            "visibility_probability": weather["fuji_visibility_probability"],
            "summary": weather["weather_summary"],
            "source": weather["data_source"],
        },
        "total_destinations": len(landmarks_3d),
    }
