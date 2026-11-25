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
    NearbyStopsRequest,
    NearbyStopsResponse,
    RouteFromLocationRequest,
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


@router.post(
    "/nearby-stops",
    response_model=NearbyStopsResponse,
    status_code=status.HTTP_200_OK,
    summary="Find Nearest Verified Public Transit Stops",
    description="Locates closest bus stops and railway stations to the traveller's GPS coordinates."
)
def get_nearby_stops(request: NearbyStopsRequest) -> NearbyStopsResponse:
    service = get_routing_service()
    stops = service.find_nearby_stops(
        lat=request.latitude,
        lon=request.longitude,
        max_distance_meters=request.max_distance_meters,
        limit=request.limit,
    )
    return NearbyStopsResponse(
        user_latitude=request.latitude,
        user_longitude=request.longitude,
        nearby_stops=stops,
        total_found=len(stops),
    )


@router.post(
    "/from-location",
    response_model=RouteSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Plan Route From Current GPS Coordinates",
    description="Calculates walking leg to closest boarding stop and public transit to the destination."
)
def plan_route_from_location(request: RouteFromLocationRequest) -> RouteSearchResponse:
    service = get_routing_service()
    try:
        return service.search_route_from_location(
            user_lat=request.latitude,
            user_lon=request.longitude,
            destination_query=request.destination,
            departure_time_str=request.departure_time,
            max_transfers=request.max_transfers,
            max_results=request.max_results,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Route from location calculation error: {str(e)}",
        )
