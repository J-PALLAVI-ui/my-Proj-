"""FujiNova Travel Search & Regional Intelligence Router."""
from typing import Optional, List
from fastapi import APIRouter, Query
from pydantic import BaseModel

from backend.app.api.routes_places import search_places_db
from backend.app.services.rag.retriever import retriever as rag_retriever
from backend.app.services.live_info.weather_service import get_weather_info
from backend.app.services.live_info.advisory_service import get_current_advisories

router = APIRouter(prefix="/api/v1/travel", tags=["Travel Intelligence"])


@router.get("/search")
def travel_search(
    q: str = Query(..., min_length=1, description="Search term for destinations or regional knowledge"),
    limit: int = Query(5, ge=1, le=20)
):
    """Search verified places and regional knowledge documents."""
    places = search_places_db(name_query=q, limit=limit)
    knowledge = rag_retriever.retrieve(query=q, top_k=limit)
    return {
        "query": q,
        "places_found": len(places),
        "places": places,
        "knowledge_found": len(knowledge),
        "knowledge_chunks": knowledge
    }


@router.get("/weather")
def travel_weather(month: Optional[int] = Query(None, ge=1, le=12, description="Month (1-12)")):
    """Retrieve Mount Fuji & Kawaguchiko seasonal climate and weather forecast."""
    return get_weather_info(month=month)


@router.get("/advisories")
def travel_advisories():
    """Retrieve active regional travel advisories and seasonal alerts."""
    return {"advisories": get_current_advisories()}
