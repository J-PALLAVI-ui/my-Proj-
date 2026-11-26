"""FujiNova Intelligent Deterministic Crowd Recommendation Engine.

Selects and ranks alternative destinations based on visitor crowd preference,
category affinity, geodesic proximity, verified accessibility, and Fuji visibility.
"""
import math
from typing import List, Dict, Any, Optional
from backend.app.models.place import Place
from backend.app.api.routes_places import get_place_by_id, search_places_db
from backend.app.services.crowd.crowd_models import (
    CrowdPreference,
    CrowdScenario,
    CrowdRecommendationRequest,
    CrowdRecommendationResponse,
    CrowdAlternativeCard,
    PlaceCrowdStatus,
)
from backend.app.services.crowd.crowd_service import crowd_service
from backend.app.services.crowd.attraction_images import get_attraction_image


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points on Earth in kilometers."""
    r = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(r * c, 1)


# Category affinity mappings
AFFINITY_MAP = {
    "viewpoint": {"viewpoint": 1.0, "nature": 0.85, "park": 0.8, "cultural": 0.5},
    "nature": {"nature": 1.0, "viewpoint": 0.85, "park": 0.8, "onsen": 0.6},
    "shrine": {"shrine": 1.0, "cultural": 0.85, "museum": 0.6},
    "cultural": {"cultural": 1.0, "museum": 0.9, "shrine": 0.8, "viewpoint": 0.5},
    "museum": {"museum": 1.0, "cultural": 0.9, "nature": 0.4},
    "onsen": {"onsen": 1.0, "nature": 0.7, "viewpoint": 0.6},
    "park": {"park": 1.0, "viewpoint": 0.85, "nature": 0.8}
}


class RecommendationService:
    """Calculates deterministic alternatives when tourists encounter crowded locations."""

    def get_recommendations(
        self,
        request: CrowdRecommendationRequest
    ) -> CrowdRecommendationResponse:
        """Evaluate origin destination and return ranked alternative choices."""
        target_id = request.place_id or request.current_place_id
        if not target_id:
            target_id = "kawaguchiko_oishi_park"

        orig_place_dict = get_place_by_id(target_id)
        if not orig_place_dict:
            raise ValueError(f"Destination '{target_id}' not found in verified database.")

        orig_place = Place.model_validate(orig_place_dict)
        orig_crowd = crowd_service.get_place_crowd_status(target_id, request.scenario)

        # Retrieve all places in database
        all_places_dicts = search_places_db(limit=300)
        candidates = [
            Place.model_validate(p) for p in all_places_dicts
            if p["place_id"] != target_id
        ]

        scored_cards: List[CrowdAlternativeCard] = []

        for cand in candidates:
            # 1. Accessibility Filter
            if request.requires_accessibility:
                if cand.accessibility_status in ("STEEP_STAIRS", "INACCESSIBLE"):
                    continue

            # 2. Geodesic distance
            dist_km = haversine_distance_km(
                orig_place.latitude, orig_place.longitude,
                cand.latitude, cand.longitude
            )

            # Limit candidate radius within 35 km (covers the Fuji Five Lakes + Kofu Basin region)
            if dist_km > 35.0:
                continue

            # 3. Candidate crowd status
            cand_crowd = crowd_service.get_place_crowd_status(cand.place_id, request.scenario)

            # Crowd reduction percentage relative to original
            if orig_crowd.score > cand_crowd.score:
                reduction_pct = int(((orig_crowd.score - cand_crowd.score) / max(orig_crowd.score, 1)) * 100)
            else:
                reduction_pct = 0

            # 4. Multi-factor scoring
            # Base preference weighting
            if request.preference == "quiet":
                # Heavily penalize high crowd, reward low score
                crowd_factor = max(0.0, (100 - cand_crowd.score) / 100.0) * 45.0
            elif request.preference == "balanced":
                # Balanced: moderate score acceptable, views & distance matter
                crowd_factor = max(0.0, (85 - cand_crowd.score) / 85.0) * 30.0
            else:
                # Popular fine: crowd barely matters
                crowd_factor = max(0.0, (100 - cand_crowd.score) / 100.0) * 15.0

            # Proximity factor with progressive distance tiers:
            # Tier 1 (<= 5km): Lakeside & immediate neighbors get maximum proximity advantage
            # Tier 2 (<= 12km): Adjacent lake shores & scenic routes
            # Tier 3 (<= 30km): Wider Fuji Five Lakes region
            if dist_km <= 5.0:
                prox_factor = 25.0 + max(0.0, (5.0 - dist_km) / 5.0) * 10.0  # 25-35 pts
            elif dist_km <= 12.0:
                prox_factor = 15.0 + max(0.0, (12.0 - dist_km) / 7.0) * 10.0  # 15-25 pts
            else:
                prox_factor = max(0.0, (30.0 - dist_km) / 18.0) * 15.0  # 0-15 pts

            # Category affinity factor (up to 20 points)
            affinities = AFFINITY_MAP.get(orig_place.primary_category, {orig_place.primary_category: 1.0})
            cat_affinity = affinities.get(cand.primary_category, 0.4)
            cat_factor = cat_affinity * 20.0

            # Fuji view preservation (up to 15 points)
            view_factor = (cand.fuji_view_rating / 5.0) * 15.0

            # Accessibility bonus (5 points)
            access_factor = 5.0 if cand.accessibility_status == "VERIFIED_ACCESSIBLE" else 0.0

            total_score = crowd_factor + prox_factor + cat_factor + view_factor + access_factor

            # Filter candidates: for quiet preference, candidate should actually be quieter or low crowd
            if request.preference == "quiet" and cand_crowd.level == "HIGH":
                continue

            # 5. Formulate human-readable recommendation justification
            reasons = []
            match_factors = []

            if reduction_pct > 0:
                reasons.append(f"{reduction_pct}% lower crowd density than {orig_place.name_en or orig_place.name_ja}")
                match_factors.append(f"{reduction_pct}% Quieter")
            else:
                reasons.append(f"Calm {cand_crowd.level.lower()} crowd index ({cand_crowd.score}/100)")
                match_factors.append(f"Crowd {cand_crowd.score}/100")

            if cand.fuji_view_rating >= 4:
                reasons.append(f"magnificent {cand.fuji_view_rating}/5 Mount Fuji view")
                match_factors.append(f"Fuji View {cand.fuji_view_rating}/5")

            if cand.accessibility_status == "VERIFIED_ACCESSIBLE":
                reasons.append("verified barrier-free step-free paths")
                match_factors.append("Barrier-Free Accessible")
            elif cand.stair_step_count and cand.stair_step_count > 0:
                match_factors.append(f"{cand.stair_step_count} Steps")

            if dist_km <= 5.0:
                reasons.append(f"just {dist_km} km away")
                match_factors.append(f"Only {dist_km} km away")
            elif dist_km <= 15.0:
                reasons.append(f"{dist_km} km scenic connection across the lakes")
                match_factors.append(f"{dist_km} km away")

            if cand.general_admission_type == "FREE":
                match_factors.append("Free Admission")

            justification = f"{reasons[0].capitalize()}. Features {', '.join(reasons[1:])}."
            if cand_crowd.advisory:
                justification += f" Note: {cand_crowd.advisory}"

            # Prioritize authentic photo and attribution from verified place database
            cand_img = cand.image_url
            cand_attr = cand.required_attribution
            if not cand_img:
                img_info = get_attraction_image(cand.place_id)
                cand_img = img_info.get("url")
                cand_attr = img_info.get("attribution")

            card = CrowdAlternativeCard(
                place=cand,
                crowd_status=cand_crowd,
                distance_km=dist_km,
                crowd_reduction_pct=reduction_pct,
                recommendation_reason=justification,
                match_factors=match_factors,
                image_url=cand_img or "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=1200&q=80",
                image_attribution=cand_attr or "FujiNova Verified Destination"
            )
            scored_cards.append((total_score, card))

        # Sort descending by total_score, tie-break on distance
        scored_cards.sort(key=lambda x: (x[0], -x[1].distance_km), reverse=True)
        top_alternatives = [item[1] for item in scored_cards[:5]]

        # Advisory summary
        if orig_crowd.level == "HIGH":
            advisory = (
                f"{orig_place.name_en or orig_place.name_ja} is heavily congested in the {request.scenario} scenario "
                f"(Crowd Index: {orig_crowd.score}/100). The {len(top_alternatives)} alternatives below offer tranquil "
                f"experiences with similar natural and cultural appeal."
            )
        elif orig_crowd.level == "MODERATE":
            advisory = (
                f"{orig_place.name_en or orig_place.name_ja} has moderate visitor traffic ({orig_crowd.score}/100). "
                f"You can explore these quieter nearby gems if you prefer extra serenity."
            )
        else:
            advisory = (
                f"{orig_place.name_en or orig_place.name_ja} currently enjoys low visitor presence ({orig_crowd.score}/100). "
                f"Nearby complementary destinations are shown below."
            )

        return CrowdRecommendationResponse(
            selected_destination=orig_place,
            selected_crowd_status=orig_crowd,
            preference=request.preference,
            scenario=request.scenario,
            alternatives=top_alternatives,
            total_alternatives=len(top_alternatives),
            classification="SIMULATED",
            advisory_summary=advisory
        )


recommendation_service = RecommendationService()
