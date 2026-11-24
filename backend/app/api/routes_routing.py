"""
Transit Routing API Routes for FujiNova.
Provides deterministic multi-modal public transport routing (RAPTOR).
"""
from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional

from backend.app.services.routing.transit_models import (
    RouteSearchRequest,
    RouteSearchResponse,
    TransitStopSchema,
)
from backend.app.services.routing.routing_service import get_routing_service

router = APIRouter(prefix="/api/v1/routes", tags=["Transport Routing"])


@router.post(
    "/search",
    response_model=RouteSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search Public Transport Routes",
    description=(
        "Executes deterministic bicriteria RAPTOR routing connecting Fujikyu Bus GTFS-JP feeds "
        "and Fujikyu Railway Official Timetable (Rev. March 14, 2026). "
        "Zero-Hallucination: times, colors, stops, and fares are calculated from actual data."
    )
)
def search_transit_routes(request: RouteSearchRequest) -> RouteSearchResponse:
    service = get_routing_service()
    try:
        response = service.search_routes(request)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Routing calculation error: {str(e)}",
        )


@router.get(
    "/stops/resolve",
    response_model=TransitStopSchema,
    summary="Resolve Stop or Landmark Name",
    description="Resolves a stop name, station name, or landmark into a verified TransitStop."
)
def resolve_stop(
    query: str = Query(..., min_length=1, description="Stop or landmark name (JA or EN)")
) -> TransitStopSchema:
    service = get_routing_service()
    stop = service.resolve_stop(query)
    if not stop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stop or landmark '{query}' not found."
        )
    return TransitStopSchema(
        stop_id=stop.stop_id,
        stop_name_ja=stop.stop_name_ja,
        stop_name_en=stop.stop_name_en,
        lat=stop.lat,
        lon=stop.lon,
        is_railway=stop.is_railway,
    )
