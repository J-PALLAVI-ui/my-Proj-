"""FujiNova Stage 3 CrowdSense Backend Tests."""
import pytest
from fastapi import HTTPException
from backend.app.api.routes_crowd import (
    get_crowd_system_status,
    get_crowd_recommendations,
    get_single_place_crowd_status,
    get_all_places_crowd_status,
)
from backend.app.services.crowd.crowd_service import crowd_service
from backend.app.services.crowd.recommendation_service import recommendation_service, haversine_distance_km
from backend.app.services.crowd.crowd_models import CrowdRecommendationRequest


def test_t3_01_crowd_system_status_api():
    """Verify crowd status endpoint reports simulated demo mode when real telemetry is absent."""
    res = get_crowd_system_status(scenario="high")
    assert res.provider_configured is False
    assert res.live_data_available is False
    assert "UNAVAILABLE" in res.status_text
    assert res.classification == "SIMULATED"
    assert res.active_scenario == "high"
    assert len(res.available_scenarios) == 3


def test_t3_02_crowd_scenarios_deterministic():
    """Verify that Low, Moderate, and High scenarios produce deterministic calibrated scores."""
    high_oishi = crowd_service.get_place_crowd_status("kawaguchiko_oishi_park", "high")
    assert high_oishi.level == "HIGH"
    assert high_oishi.score == 88
    assert high_oishi.is_simulated is True
    assert "SIMULATED" in high_oishi.classification_label

    mod_oishi = crowd_service.get_place_crowd_status("kawaguchiko_oishi_park", "moderate")
    assert mod_oishi.score < high_oishi.score
    assert mod_oishi.score == int(88 * 0.62)

    low_oishi = crowd_service.get_place_crowd_status("kawaguchiko_oishi_park", "low")
    assert low_oishi.score < mod_oishi.score
    assert low_oishi.score == int(88 * 0.32)


def test_t3_03_crowd_recommendations_quiet_preference():
    """Verify Oishi Park quiet preference recommends tranquil lakeside alternatives."""
    req = CrowdRecommendationRequest(
        place_id="kawaguchiko_oishi_park",
        preference="quiet",
        scenario="high",
        requires_accessibility=True
    )
    res = get_crowd_recommendations(req)

    assert res.selected_destination.place_id == "kawaguchiko_oishi_park"
    assert res.selected_crowd_status.level == "HIGH"
    assert res.total_alternatives > 0
    assert len(res.alternatives) <= 5

    # Original destination must never be in alternatives
    cand_ids = [alt.place.place_id for alt in res.alternatives]
    assert "kawaguchiko_oishi_park" not in cand_ids

    # Top alternative should be significantly quieter than Oishi Park (88)
    top = res.alternatives[0]
    assert top.crowd_status.score < 88
    assert top.crowd_reduction_pct > 0
    assert len(top.recommendation_reason) > 10
    assert top.image_url.startswith("https://")
    assert len(top.image_attribution) > 0


def test_t3_04_crowd_recommendations_invalid_place():
    """Verify 404 is returned when requesting alternatives for a non-existent place."""
    req = CrowdRecommendationRequest(
        place_id="non_existent_fake_place_123",
        preference="quiet",
        scenario="high"
    )
    with pytest.raises(HTTPException) as exc_info:
        get_crowd_recommendations(req)
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()


def test_t3_05_crowd_accessibility_filter():
    """Verify that requiring accessibility excludes steep stairs places."""
    req = CrowdRecommendationRequest(
        place_id="kawaguchiko_oishi_park",
        preference="quiet",
        scenario="high",
        requires_accessibility=True
    )
    res = get_crowd_recommendations(req)
    for alt in res.alternatives:
        assert alt.place.accessibility_status != "STEEP_STAIRS"
        assert alt.place.accessibility_status != "INACCESSIBLE"


def test_t3_06_haversine_distance():
    """Verify mathematical distance calculation."""
    # Oishi Park (35.5236, 138.7452) to Kawaguchiko Station (35.4981, 138.7686) is approx 3.6 km
    dist = haversine_distance_km(35.5236, 138.7452, 35.4981, 138.7686)
    assert 3.0 < dist < 4.5


def test_t3_07_hana_crowd_intent_and_grounding():
    """Verify Hana extracts crowd queries and grounds recommendations deterministically."""
    from backend.app.agent.hana import extract_crowd_query, agent
    from backend.app.services.crowd.crowd_models import CrowdRecommendationRequest, CrowdPreference, CrowdScenario

    # 1. Intent extraction
    query = "Is Oishi Park crowded today? Are there quieter alternatives?"
    res = extract_crowd_query(query)
    assert res is not None
    target_name, pref = res
    assert "oishi" in target_name
    assert pref == "quiet"

    # 2. Place ID resolution
    pid = agent.resolve_place_id(target_name)
    assert pid == "kawaguchiko_oishi_park"

    # 3. Grounded crowd intelligence calculation
    req = CrowdRecommendationRequest(
        place_id=pid,
        preference="quiet",
        scenario="high"
    )
    rec_res = recommendation_service.get_recommendations(req)
    assert rec_res.selected_destination.place_id == "kawaguchiko_oishi_park"
    assert rec_res.selected_crowd_status.level == "HIGH"
    assert len(rec_res.alternatives) > 0

    top_alt = rec_res.alternatives[0]
    assert top_alt.crowd_reduction_pct > 0
    assert len(top_alt.recommendation_reason) > 10
    assert top_alt.place.fuji_view_rating >= 4
