"""FujiNova Deterministic CrowdSense Service.

Implements calibrated baseline crowd models across Low, Moderate, and High
demonstration scenarios for all 35 verified FujiNova tourist destinations.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.app.services.crowd.crowd_models import (
    PlaceCrowdStatus,
    CrowdSystemStatusResponse,
    CrowdScenario,
    CrowdLevel,
)

# Calibrated baseline crowd indices (0-100) for High (peak weekend) scenario
# Format: (score, peak_hours, advisory)
_HIGH_SCENARIO_PROFILES: Dict[str, Dict[str, Any]] = {
    # Hotspots
    "kawaguchiko_oishi_park": {
        "score": 88,
        "peak": "10:30 - 15:30",
        "advisory": "High tour bus arrivals; lakefront promenade heavily congested.",
        "trend": "rising"
    },
    "arakurayama_chureito": {
        "score": 94,
        "peak": "09:00 - 16:00",
        "advisory": "Observation deck queue exceeding 35 min; 398 stairs crowded.",
        "trend": "rising"
    },
    "oshino_hakkai": {
        "score": 90,
        "peak": "11:00 - 15:00",
        "advisory": "Wakuike pond perimeter crowded with large tour groups.",
        "trend": "steady"
    },
    "kawaguchiko_ropeway": {
        "score": 92,
        "peak": "10:00 - 16:00",
        "advisory": "Ropeway boarding queue: 45+ minute wait.",
        "trend": "rising"
    },
    "fujiq_central_park": {
        "score": 84,
        "peak": "11:00 - 17:00",
        "advisory": "Major attraction concourses at peak capacity.",
        "trend": "steady"
    },
    # Moderate popularity
    "kawaguchiko_living_center": {
        "score": 72,
        "peak": "11:00 - 15:30",
        "advisory": "Gift shop and cafe busy; outdoor terraces moderately filled.",
        "trend": "steady"
    },
    "kitaguchi_sengen_shrine": {
        "score": 52,
        "peak": "11:00 - 14:00",
        "advisory": "Main shrine courtyard active; cedar forest trails remain peaceful.",
        "trend": "steady"
    },
    "yamanakako_hananomiyako": {
        "score": 65,
        "peak": "11:30 - 14:30",
        "advisory": "Central flower viewing path active; outer park areas uncrowded.",
        "trend": "steady"
    },
    "hottarakashi_onsen": {
        "score": 68,
        "peak": "05:30 - 07:30, 16:30 - 18:30",
        "advisory": "Sunrise and sunset peak bathing periods.",
        "trend": "rising"
    },
    "saiko_iyashi_nenba": {
        "score": 46,
        "peak": "12:00 - 14:30",
        "advisory": "Thatched village paths unhurried; comfortable walking room.",
        "trend": "steady"
    },
    "narusawa_ice_cave": {
        "score": 58,
        "peak": "11:00 - 15:00",
        "advisory": "Stairway descent requires 10-15 min queue entry spacing.",
        "trend": "steady"
    },
    "fugaku_wind_cave": {
        "score": 54,
        "peak": "11:00 - 15:00",
        "advisory": "Steady family visitor flow; spacious horizontal path.",
        "trend": "steady"
    },
    "kawaguchiko_herbkan": {
        "score": 48,
        "peak": "12:00 - 15:00",
        "advisory": "Greenhouse workshop moderately occupied.",
        "trend": "steady"
    },
    "katsunuma_budo_no_oka": {
        "score": 50,
        "peak": "13:00 - 16:00",
        "advisory": "Wine cellar tasting salon active.",
        "trend": "steady"
    },
    "oshino_shinobi_no_sato": {
        "score": 48,
        "peak": "11:00 - 14:30",
        "advisory": "Ninja trick mansion performance sessions booked.",
        "trend": "steady"
    },
    "kawaguchiko_tic": {
        "score": 75,
        "peak": "09:00 - 12:00",
        "advisory": "Station plaza active with arriving train passengers.",
        "trend": "rising"
    },
    # Tranquil & quiet alternatives (Hidden Gems)
    "kawaguchiko_yagizaki_park": {
        "score": 22,
        "peak": "14:00 - 16:00",
        "advisory": "Peaceful southern shore; uncrowded lakefront promenade with benches.",
        "trend": "steady"
    },
    "shojiko_tategohama": {
        "score": 12,
        "peak": "10:00 - 12:00",
        "advisory": "Serene natural shoreline; minimal foot traffic and open views.",
        "trend": "steady"
    },
    "motosuko_viewpoint": {
        "score": 26,
        "peak": "10:00 - 13:00",
        "advisory": "Deep blue shoreline; unhurried photography atmosphere.",
        "trend": "steady"
    },
    "kawaguchiko_art_museum": {
        "score": 20,
        "peak": "13:00 - 15:00",
        "advisory": "Quiet lakeside sculpture lawn; peaceful cafe overlooking water.",
        "trend": "steady"
    },
    "kawaguchiko_music_forest": {
        "score": 38,
        "peak": "12:00 - 15:00",
        "advisory": "Spacious European gardens with open pathways and seating.",
        "trend": "steady"
    },
    "itchiku_kubota_museum": {
        "score": 32,
        "peak": "11:30 - 14:00",
        "advisory": "Meditative moss garden and quiet gallery atmosphere.",
        "trend": "steady"
    },
    "yamanakako_nagaike_park": {
        "score": 24,
        "peak": "14:00 - 16:00",
        "advisory": "Tranquil open waterfront; unobstructed Mount Fuji water perspective.",
        "trend": "steady"
    },
    "saiko_bat_cave": {
        "score": 18,
        "peak": "11:00 - 14:00",
        "advisory": "Spacious nature center; uncrowded woodland boardwalk trail.",
        "trend": "steady"
    },
    "fujisan_heritage_center": {
        "score": 16,
        "peak": "11:00 - 14:00",
        "advisory": "Air-conditioned modernist exhibition hall with open viewing terrace.",
        "trend": "steady"
    },
    "narusawa_fuji_museum": {
        "score": 24,
        "peak": "11:00 - 14:00",
        "advisory": "Road station adjacent; free admission and open exhibits.",
        "trend": "steady"
    },
    "yamanakako_kirara": {
        "score": 28,
        "peak": "13:00 - 15:30",
        "advisory": "Extensive wetland boardwalk and open-air plaza; very spacious.",
        "trend": "steady"
    },
    "yamanakako_asahigaoka": {
        "score": 30,
        "peak": "11:00 - 14:00",
        "advisory": "Lakeside wooded trails with ample room.",
        "trend": "steady"
    },
    "kofu_takeda_shrine": {
        "score": 28,
        "peak": "11:00 - 14:00",
        "advisory": "Shaded castle moat grounds; tranquil historic walking trail.",
        "trend": "steady"
    },
    "kofu_kai_zenkoji": {
        "score": 22,
        "peak": "11:00 - 13:30",
        "advisory": "Reverent temple atmosphere; quiet underground tunnel walk.",
        "trend": "steady"
    },
    "fuefuki_misaka_orchard": {
        "score": 25,
        "peak": "10:00 - 14:00",
        "advisory": "Expansive agricultural orchards with gentle visitor numbers.",
        "trend": "steady"
    },
    "yamanashi_pref_museum": {
        "score": 18,
        "peak": "13:00 - 15:00",
        "advisory": "Spacious cultural exhibition halls; step-free and barrier-free.",
        "trend": "steady"
    },
    "yamanashi_pref_art_museum": {
        "score": 20,
        "peak": "13:00 - 15:00",
        "advisory": "Quiet Millet gallery and serene sculpture courtyard.",
        "trend": "steady"
    },
    "kofu_maizuru_castle": {
        "score": 22,
        "peak": "14:00 - 16:30",
        "advisory": "Historic stone walls with expansive views; low visitor density.",
        "trend": "steady"
    },
    "kofu_yumura_footbath": {
        "score": 15,
        "peak": "15:00 - 18:00",
        "advisory": "Neighborhood thermal footbath; relaxed community feel.",
        "trend": "steady"
    }
}


def _score_to_level(score: int) -> CrowdLevel:
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "MODERATE"
    return "LOW"


def _scale_score(base_high_score: int, scenario: CrowdScenario) -> int:
    """Scale score deterministically according to selected scenario."""
    if scenario == "high":
        return base_high_score
    if scenario == "moderate":
        # Moderate scenario: compressed downwards
        return max(8, int(base_high_score * 0.62))
    # Low scenario: early morning / quiet weekday
    return max(5, int(base_high_score * 0.32))


class CrowdService:
    """Provides deterministic crowd status for demonstration scenarios and tracks data availability."""

    def __init__(self):
        self.live_provider_active = False

    def get_place_crowd_status(
        self,
        place_id: str,
        scenario: CrowdScenario = "high"
    ) -> PlaceCrowdStatus:
        """Calculate deterministic crowd metrics for a destination under chosen scenario."""
        from backend.app.services.crowd.defaults import default_popularity
        profile = _HIGH_SCENARIO_PROFILES.get(
            place_id,
            {"score": default_popularity(place_id), "peak": "12:00 - 14:00", "advisory": "Standard visitor presence.", "trend": "steady"}
        )

        scaled_score = _scale_score(profile["score"], scenario)
        level = _score_to_level(scaled_score)

        scenario_titles = {
            "low": "Low Crowd (Weekday / Morning)",
            "moderate": "Moderate Crowd (Standard Day)",
            "high": "High Crowd (Peak Weekend / Holiday)"
        }
        scenario_title = scenario_titles.get(scenario, "Demonstration Scenario")

        return PlaceCrowdStatus(
            place_id=place_id,
            level=level,
            score=scaled_score,
            classification="SIMULATED",
            classification_label=f"SIMULATED ({scenario_title})",
            is_simulated=True,
            historical_peak_hours=profile.get("peak"),
            trend=profile.get("trend", "steady"),
            advisory=profile.get("advisory")
        )

    def get_all_places_crowd_status(
        self,
        scenario: CrowdScenario = "high"
    ) -> Dict[str, PlaceCrowdStatus]:
        """Return crowd metrics for all 35 destinations under the active scenario."""
        result = {}
        for place_id in _HIGH_SCENARIO_PROFILES:
            result[place_id] = self.get_place_crowd_status(place_id, scenario)
        return result

    def get_system_status(self, active_scenario: CrowdScenario = "high") -> CrowdSystemStatusResponse:
        """Inspect live data availability vs calibrated demonstration scenarios."""
        from backend.app.api.routes_places import search_places_db
        from backend.app.services.crowd.attraction_images import get_attraction_image, HERO_IMAGE

        try:
            all_places = search_places_db(limit=500)
        except Exception:
            all_places = []

        places_enriched = []
        for p in all_places:
            pid = p.get("place_id")
            if not pid:
                continue
            cs = self.get_place_crowd_status(pid, active_scenario)
            img = get_attraction_image(pid)
            places_enriched.append({
                "place_id": pid,
                "name_ja": p.get("name_ja", ""),
                "name_en": p.get("name_en") or p.get("name_ja", ""),
                "primary_category": p.get("primary_category", "viewpoint"),
                "fuji_view_rating": p.get("fuji_view_rating", 3),
                "accessibility_status": p.get("accessibility_status", "UNKNOWN"),
                "level": cs.level,
                "score": cs.score,
                "crowd_level": cs.level.lower(),
                "crowd_index": cs.score,
                "advisory": cs.advisory,
                "congestion_advisory": cs.advisory or "Standard visitor presence.",
                "image_url": img.get("url", ""),
                "image_attribution": img.get("attribution", ""),
            })

        return CrowdSystemStatusResponse(
            provider_configured=False,
            live_data_available=False,
            status_text="UNAVAILABLE: Live cellular or IoT crowd telemetry is not configured. Active in Calibrated Demonstration Mode.",
            active_scenario=active_scenario,
            available_scenarios=[
                {"id": "low", "name": "Low Crowd", "description": "Early morning or quiet weekday off-peak travel"},
                {"id": "moderate", "name": "Moderate Crowd", "description": "Typical clear-weather travel flow"},
                {"id": "high", "name": "High Crowd", "description": "Peak autumn/cherry-blossom weekend afternoon with tour bus arrivals"}
            ],
            classification="SIMULATED",
            timestamp=datetime.now().isoformat(),
            provenance="FujiNova CrowdSense Calibrated Scenario Engine v1.0",
            hero_image_url=HERO_IMAGE["url"],
            hero_image_attribution=HERO_IMAGE["attribution"],
            places=places_enriched,
            data_classification="SIMULATED_BASELINE",
            real_time_telemetry_status="UNAVAILABLE"
        )


# Global singleton
crowd_service = CrowdService()
