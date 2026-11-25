"""FujiNova CrowdSense API Router."""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, status
from backend.app.services.crowd.crowd_models import (
    CrowdScenario,
    CrowdSystemStatusResponse,
    CrowdRecommendationRequest,
    CrowdRecommendationResponse,
    CrowdDivertRequest,
    CrowdDivertResponse,
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


@router.post("/divert", response_model=CrowdDivertResponse)
def divert_crowded_destination(request: CrowdDivertRequest):
    """Calculates quiet alternative destination, transit connection, and encouraging travel advice."""
    try:
        rec_req = CrowdRecommendationRequest(
            place_id=request.current_place_id,
            preference=request.preference,
            scenario=request.scenario,
            limit=5
        )
        recs = recommendation_service.get_recommendations(rec_req)
        if not recs.alternatives:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No alternatives found for {request.current_place_id} under {request.scenario} scenario."
            )

        target_alt = None
        if request.target_alternative_id:
            for a in recs.alternatives:
                if a.place_id == request.target_alternative_id:
                    target_alt = a
                    break
        if not target_alt:
            target_alt = recs.alternatives[0]

        transit_info = None
        try:
            from backend.app.services.routing.routing_service import get_routing_service
            from backend.app.services.routing.transit_models import RouteSearchRequest
            routing_svc = get_routing_service()
            route_res = routing_svc.search_routes(RouteSearchRequest(
                origin=recs.current_place_name,
                destination=target_alt.name_en,
                max_transfers=2,
                max_results=1
            ))
            if route_res.journeys:
                transit_info = route_res.journeys[0].model_dump()
        except Exception:
            transit_info = None

        advice = (
            f"{recs.current_place_name} is currently experiencing {recs.current_crowd_level.upper()} visitor traffic. "
            f"Instead of spending time in long queues, we recommend {target_alt.name_en} (-{target_alt.crowd_reduction_percent}% crowd reduction). "
            f"You will enjoy a peaceful, high-quality perspective of Mount Fuji (★{target_alt.fuji_view_rating}/5) with a much more relaxed experience."
        )

        return CrowdDivertResponse(
            original_place_id=recs.current_place_id,
            original_place_name=recs.current_place_name,
            original_crowd_level=recs.current_crowd_level,
            diverted_alternative=target_alt,
            crowd_reduction_percent=target_alt.crowd_reduction_percent,
            transit_connection=transit_info,
            diversion_advice=advice,
            status="success"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing crowd diversion: {str(e)}"
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


@router.get("/forecast/{place_id}")
def get_seasonal_crowd_forecast(
    place_id: str,
    target_date: Optional[str] = None,
    target_time: Optional[str] = None,
    weather: Optional[str] = "clear"
):
    """
    Evaluates calendar, season, day of week, Japanese public holidays, and time-of-day
    to predict crowd density across 5 categories (Very Low, Low, Moderate, High, Very High).
    """
    from backend.app.services.crowd.seasonal_predictor import SeasonalCrowdForecast
    from datetime import date, time
    parsed_date = None
    parsed_time = None
    if target_date:
        try:
            parsed_date = date.fromisoformat(target_date)
        except Exception:
            pass
    if target_time:
        try:
            parts = target_time.split(":")
            parsed_time = time(int(parts[0]), int(parts[1]))
        except Exception:
            pass
    return SeasonalCrowdForecast.get_forecast(
        place_id=place_id,
        target_date=parsed_date,
        target_time=parsed_time,
        weather_condition=weather
    )
