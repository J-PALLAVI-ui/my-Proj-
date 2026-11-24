"""FujiNova CrowdSense API Router."""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, status
from backend.app.services.crowd.crowd_models import (
    CrowdScenario,
    CrowdSystemStatusResponse,
    CrowdRecommendationRequest,
    CrowdRecommendationResponse,
    PlaceCrowdStatus,
)
from backend.app.services.crowd.crowd_service import crowd_service
from backend.app.services.crowd.recommendation_service import recommendation_service

router = APIRouter(prefix="/api/v1/crowd", tags=["CrowdSense"])


@router.get("/status", response_model=CrowdSystemStatusResponse)
def get_crowd_system_status(scenario: CrowdScenario = Query("high", description="Current demonstration scenario")):
    """Inspect crowd data provider availability and active demonstration scenarios."""
    return crowd_service.get_system_status(active_scenario=scenario)


@router.post("/recommendations", response_model=CrowdRecommendationResponse)
def get_crowd_recommendations(request: CrowdRecommendationRequest):
    """Calculate deterministic quieter alternative destinations matching visitor preferences."""
    try:
        return recommendation_service.get_recommendations(request)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating crowd alternatives: {str(e)}"
        )


@router.get("/places/{place_id}", response_model=PlaceCrowdStatus)
def get_single_place_crowd_status(
    place_id: str,
    scenario: CrowdScenario = Query("high", description="Simulated crowd scenario: 'low', 'moderate', or 'high'")
):
    """Retrieve simulated crowd score and advisory for a specific destination."""
    return crowd_service.get_place_crowd_status(place_id=place_id, scenario=scenario)


@router.get("/places", response_model=Dict[str, PlaceCrowdStatus])
def get_all_places_crowd_status(
    scenario: CrowdScenario = Query("high", description="Simulated crowd scenario: 'low', 'moderate', or 'high'")
):
    """Retrieve simulated crowd metrics across all 35 destinations under selected scenario."""
    return crowd_service.get_all_places_crowd_status(scenario=scenario)
