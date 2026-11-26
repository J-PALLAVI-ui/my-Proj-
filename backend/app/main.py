"""FujiNova FastAPI Application Factory."""
import os
from typing import Any, Dict, List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.api.routes_health import router as health_router
from backend.app.api.routes_places import router as places_router
from backend.app.api.routes_chat import router as chat_router
from backend.app.api.routes_routing import router as routing_router
from backend.app.api.routes_crowd import router as crowd_router, divert_crowded_destination
from backend.app.api.routes_digital_twin import router as digital_twin_router, get_digital_twin_data
from backend.app.api.routes_itinerary import router as itinerary_router, api_generate_itinerary, api_update_itinerary, ItineraryGenerateRequest, ItineraryUpdateRequest
from backend.app.api.routes_travel import router as travel_router, travel_search, travel_weather
from backend.app.api.routes_discovery import router as discovery_router
from backend.app.api.routes_conversations import (
    router as conversations_router,
    list_conversations as api_list_conversations,
    create_conversation as api_create_conversation,
    get_conversation as api_get_conversation,
    get_conversation_messages as api_get_conversation_messages,
    update_conversation as api_update_conversation,
    delete_conversation as api_delete_conversation,
    CreateConversationRequest,
    UpdateConversationRequest
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event: initialize database on startup and seed 35 verified places."""
    init_db()
    try:
        from backend.data.seed_places import seed_database
        seed_database()
    except Exception as e:
        print(f"Startup seed notice: {e}")
    yield


app = FastAPI(
    title="FujiNova API",
    description="Conversational, Location-Aware & Crowd-Sensitive Tourism API for Mount Fuji & Yamanashi",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Configuration: Support Netlify production & preview domains, and preserve localhost
default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://my-proj-eprz.netlify.app",
    "https://agent-6b080547420fc4e73afd124a--my-proj-eprz.netlify.app",
]

cors_env = os.getenv("CORS_ALLOWED_ORIGINS", settings.CORS_ALLOWED_ORIGINS)
if cors_env.strip():
    for origin in cors_env.split(","):
        cleaned = origin.strip().rstrip("/")
        if cleaned and cleaned not in default_origins:
            default_origins.append(cleaned)

is_wildcard = "*" in default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if is_wildcard else default_origins,
    allow_credentials=not is_wildcard,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers (v1 standard)
app.include_router(health_router)
app.include_router(places_router)
app.include_router(chat_router)
app.include_router(routing_router)
app.include_router(crowd_router)
app.include_router(digital_twin_router)
app.include_router(itinerary_router)
app.include_router(travel_router)
app.include_router(discovery_router)
app.include_router(conversations_router)

# Direct Compatibility Endpoints (as inspected in /docs)
from backend.app.api.routes_health import health_check
from backend.app.api.routes_places import list_places
from backend.app.api.routes_routing import search_transit_routes
from backend.app.api.routes_chat import chat_stream_endpoint, ChatMessageRequest
from backend.app.services.routing.transit_models import RouteSearchRequest
from backend.app.services.crowd.crowd_models import CrowdRecommendationRequest, CrowdScenario
from backend.app.services.crowd.crowd_service import crowd_service
from backend.app.services.crowd.recommendation_service import recommendation_service

@app.get("/health", tags=["Health Compatibility"])
async def root_health():
    return await health_check()

@app.get("/api/attractions", tags=["Places Compatibility"])
def api_attractions(limit: int = 100, offset: int = 0):
    places = list_places(limit=limit, offset=offset)
    return {"items": places, "total": len(places), "limit": limit, "offset": offset}

@app.get("/api/transport", tags=["Transport Compatibility"])
def api_transport():
    from backend.app.services.routing.routing_service import get_routing_service
    svc = get_routing_service()
    key_stops = [
        {"stop_id": s.stop_id, "name_ja": s.stop_name_ja, "name_en": s.stop_name_en, "is_railway": s.is_railway}
        for s in svc.stops.values()
        if s.is_railway or s.stop_id.startswith("0025") or s.stop_id.startswith("0001") or s.stop_id.startswith("1857")
    ]
    return {"stops": key_stops, "total": len(key_stops)}

@app.post("/api/transit/plan", tags=["Transport Compatibility"])
def api_transit_plan(request: RouteSearchRequest):
    return search_transit_routes(request)

@app.post("/api/chat", tags=["AI Compatibility"])
@app.post("/api/ai/chat", tags=["AI Compatibility"])
async def api_ai_chat(request: ChatMessageRequest):
    return await chat_stream_endpoint(request)

@app.post("/api/ai/adaptive/chat", tags=["AI Compatibility"])
async def api_ai_adaptive_chat(request: ChatMessageRequest):
    return await chat_stream_endpoint(request)

@app.post("/api/itinerary/generate", tags=["Itinerary Compatibility"])
def api_compat_generate_itinerary(request: ItineraryGenerateRequest):
    return api_generate_itinerary(request)

@app.post("/api/itinerary/update", tags=["Itinerary Compatibility"])
def api_compat_update_itinerary(request: ItineraryUpdateRequest):
    return api_update_itinerary(request)

@app.get("/api/travel/search", tags=["Travel Compatibility"])
def api_compat_travel_search(q: str, limit: int = 5):
    return travel_search(q=q, limit=limit)

@app.get("/api/travel/weather", tags=["Travel Compatibility"])
def api_compat_travel_weather(month: int = None):
    return travel_weather(month=month)

@app.get("/api/crowd/status", tags=["Crowd Compatibility"])
def api_crowd_status(scenario: CrowdScenario = "high"):
    return crowd_service.get_system_status(active_scenario=scenario)

@app.post("/api/crowd/recommendations", tags=["Crowd Compatibility"])
def api_crowd_recommendations(request: CrowdRecommendationRequest):
    try:
        return recommendation_service.get_recommendations(request)
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=404 if isinstance(e, ValueError) else 500, detail=str(e))

@app.post("/api/crowd/divert", tags=["Crowd Compatibility"])
def api_crowd_divert(request: Any = None):
    from backend.app.services.crowd.crowd_models import CrowdDivertRequest
    if isinstance(request, dict):
        parsed = CrowdDivertRequest.model_validate(request)
    elif request is None:
        parsed = CrowdDivertRequest(current_place_id="kawaguchiko_oishi_park")
    else:
        parsed = request
    return divert_crowded_destination(parsed)

@app.get("/api/digital-twin/data", tags=["Digital Twin Compatibility"])
def api_digital_twin_data(scenario: CrowdScenario = "high"):
    return get_digital_twin_data(scenario=scenario)

@app.post("/api/routes/nearby-stops", tags=["Transport Compatibility"])
@app.post("/api/location/nearby-stops", tags=["Transport Compatibility"])
def api_nearby_stops(request: Any = None):
    from backend.app.services.routing.transit_models import NearbyStopsRequest
    from backend.app.api.routes_routing import get_nearby_stops
    if isinstance(request, dict):
        parsed = NearbyStopsRequest.model_validate(request)
    else:
        parsed = request
    return get_nearby_stops(parsed)

@app.post("/api/routes/from-location", tags=["Transport Compatibility"])
def api_routes_from_location(request: Any = None):
    from backend.app.services.routing.transit_models import RouteFromLocationRequest
    from backend.app.api.routes_routing import plan_route_from_location
    if isinstance(request, dict):
        parsed = RouteFromLocationRequest.model_validate(request)
    else:
        parsed = request
    return plan_route_from_location(parsed)

@app.get("/api/crowd/places/{place_id}", tags=["Crowd Compatibility"])
def api_crowd_place(place_id: str, scenario: CrowdScenario = "high"):
    return crowd_service.get_place_crowd_status(place_id=place_id, scenario=scenario)

@app.get("/api/crowd/places", tags=["Crowd Compatibility"])
def api_crowd_all_places(scenario: CrowdScenario = "high"):
    return crowd_service.get_all_places_crowd_status(scenario=scenario)

@app.get("/api/crowd/forecast/{place_id}", tags=["Crowd Compatibility"])
def api_crowd_forecast(place_id: str, target_date: Optional[str] = None, target_time: Optional[str] = None):
    from backend.app.api.routes_crowd import get_seasonal_crowd_forecast
    return get_seasonal_crowd_forecast(place_id=place_id, target_date=target_date, target_time=target_time)

@app.post("/api/itinerary/time-budget", tags=["Itinerary Compatibility"])
def api_compat_time_budget(request: Any = None):
    from backend.app.api.routes_itinerary import TimeBudgetItineraryRequest, api_time_budgeted_itinerary
    if isinstance(request, dict):
        parsed = TimeBudgetItineraryRequest.model_validate(request)
    elif request is None:
        parsed = TimeBudgetItineraryRequest()
    else:
        parsed = request
    return api_time_budgeted_itinerary(parsed)

@app.post("/api/itinerary/optimize-passes", tags=["Itinerary Compatibility"])
def api_compat_optimize_passes(request: Any = None):
    from backend.app.api.routes_itinerary import PassOptimizeRequest, api_optimize_passes
    if isinstance(request, dict):
        parsed = PassOptimizeRequest.model_validate(request)
    else:
        parsed = request
    return api_optimize_passes(parsed)


@app.get("/api/conversations", tags=["Conversations Compatibility"])
def api_compat_list_conversations(q: str = None, limit: int = 50):
    return api_list_conversations(q=q, limit=limit)

@app.post("/api/conversations", tags=["Conversations Compatibility"])
def api_compat_create_conversation(req: CreateConversationRequest):
    return api_create_conversation(req)

@app.get("/api/conversations/{conversation_id}", tags=["Conversations Compatibility"])
def api_compat_get_conversation(conversation_id: str):
    return api_get_conversation(conversation_id)

@app.get("/api/conversations/{conversation_id}/messages", tags=["Conversations Compatibility"])
def api_compat_get_conversation_messages(conversation_id: str):
    return api_get_conversation_messages(conversation_id)

@app.patch("/api/conversations/{conversation_id}", tags=["Conversations Compatibility"])
def api_compat_update_conversation(conversation_id: str, req: UpdateConversationRequest):
    return api_update_conversation(conversation_id, req)

@app.delete("/api/conversations/{conversation_id}", tags=["Conversations Compatibility"])
def api_compat_delete_conversation(conversation_id: str):
    return api_delete_conversation(conversation_id)


@app.get("/")
async def root():
    return {
        "project": "FujiNova",
        "description": "AI Travel Companion for Mount Fuji & Yamanashi",
        "version": "0.1.0",
        "health_check": "/api/v1/health",
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", os.getenv("FUJINOVA_PORT", 8000)))
    host = os.getenv("FUJINOVA_HOST", "0.0.0.0")
    uvicorn.run("backend.app.main:app", host=host, port=port, reload=False)
