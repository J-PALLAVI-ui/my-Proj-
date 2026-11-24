"""
Stage 2 Acceptance Tests: Routing API Endpoints & Hana Agent Transit Grounding.
Covers acceptance criteria:
- T2-17: Invalid / unknown stop error handling
- T2-18: REST API endpoints POST /api/v1/routes/search & GET /api/v1/routes/stops/resolve
- T2-19: Hana agent transport grounding & tool integration
"""
import pytest
from fastapi import HTTPException
from backend.app.api.routes_routing import search_transit_routes, resolve_stop
from backend.app.services.routing.transit_models import RouteSearchRequest
from backend.app.agent.hana import HanaAgent
from backend.app.services.llm.base import BaseLLMAdapter
from backend.app.services.llm.router import ModelRouter


# T2-17 & T2-18: API Routing Endpoint Tests
def test_t2_17_invalid_stop_error():
    req = RouteSearchRequest(
        origin="CompletelyFakeNonExistentStopXYZ",
        destination="Oishi Park",
        departure_time="09:00:00"
    )
    with pytest.raises(HTTPException) as exc_info:
        search_transit_routes(req)
    assert exc_info.value.status_code == 404
    assert "could not be identified" in exc_info.value.detail


def test_t2_18_routes_search_api():
    # 1. Test search endpoint
    req = RouteSearchRequest(
        origin="Kawaguchiko Station",
        destination="Oishi Park",
        departure_time="2026-11-09 09:00:00",
        max_transfers=1,
        max_results=2
    )
    res = search_transit_routes(req)
    assert res.origin.stop_name_ja == "河口湖駅"
    assert res.destination.stop_name_ja == "河口湖自然生活館"
    assert res.total_journeys_found >= 1
    j = res.journeys[0]
    assert j.departure_time == "09:00"
    assert j.arrival_time == "09:27"
    assert j.total_fare_jpy == 570
    assert j.legs[0].route_color == "#E60012"
    assert j.legs[0].provenance_badge == "[Official Fujikyu Bus GTFS-JP]"

    # 2. Test resolve stop endpoint
    stop_data = resolve_stop(query="Chureito Pagoda")
    assert stop_data.stop_id == "rail_shimoyoshida"
    assert stop_data.is_railway is True


# T2-19: Hana Agent Transit Grounding Integration
from backend.app.agent.hana import HanaAgent
from backend.app.services.routing.routing_service import get_routing_service


def test_t2_19_hana_transit_grounding():
    agent = HanaAgent()

    # 1. Test transit intent extraction from various user phrasings
    pair1 = agent.extract_transit_query("How do I reach Lake Kawaguchiko from Fujiyoshida?")
    assert pair1 is not None
    orig, dest, _ = pair1
    assert "Fujiyoshida" in orig
    assert "Kawaguchiko" in dest

    pair2 = agent.extract_transit_query("How do I travel from Kawaguchiko Station to Oishi Park at 9 AM?")
    assert pair2 is not None
    orig2, dest2, dep_time2 = pair2
    assert "Kawaguchiko" in orig2
    assert "Oishi" in dest2
    assert dep_time2 == "09:00:00"

    # 2. Test deterministic routing calculation for extracted query
    svc = get_routing_service()
    req = RouteSearchRequest(
        origin=orig2,
        destination=dest2,
        departure_time="2026-11-09 09:00:00",
        max_transfers=1,
        max_results=2
    )
    res = svc.search_routes(req)
    assert res.total_journeys_found >= 1

    j = res.journeys[0]
    assert j.departure_time == "09:00"
    assert j.arrival_time == "09:27"
    assert j.total_fare_jpy == 570
    assert j.legs[0].route_color == "#E60012"
    assert j.legs[0].route_short_name == "Red Line"
    assert j.legs[0].origin_stop_id == "0025_01"
    assert j.legs[0].destination_stop_id == "1857_01"
    assert j.legs[0].provenance_badge == "[Official Fujikyu Bus GTFS-JP]"
