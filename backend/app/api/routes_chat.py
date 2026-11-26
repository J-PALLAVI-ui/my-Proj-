"""FujiNova Chat API: Server-Sent Events (SSE) Streaming Router with Itinerary & Multi-Turn Memory."""
import json
import asyncio
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.app.agent.hana import agent as hana_agent
from backend.app.services.conversation.session_manager import session_manager

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


class ChatMessageRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=128, description="Unique client session identifier")
    message: str = Field(..., min_length=1, max_length=4000, description="Traveller conversational message")
    user_location: Optional[Dict[str, float]] = Field(None, description="Optional GPS coordinates (lat, lon)")
    context: Optional[Dict[str, Any]] = Field(None, description="Active UI context: station, mode, plan, step")


@router.post("/stream")
async def chat_stream_endpoint(request: ChatMessageRequest):
    """Stream Hana conversational responses with grounded places, itineraries, and transit via SSE."""
    async def sse_generator():
        try:
            state = hana_agent.get_or_create_state(request.session_id)

            # 1. Stream tokens live
            async for token in hana_agent.chat(
                session_id=request.session_id,
                user_message=request.message,
                user_location=request.user_location,
                context=request.context,
            ):
                payload = json.dumps({"token": token}, ensure_ascii=False)
                yield f"event: token\ndata: {payload}\n\n"

            # 2. Stream generated/updated itinerary plan if active
            active_itinerary = state.get("active_itinerary")
            if active_itinerary:
                itinerary_payload = json.dumps(active_itinerary, ensure_ascii=False)
                yield f"event: itinerary\ndata: {itinerary_payload}\n\n"

            # 3. Stream grounded place cards if queried
            identified_places = state.get("identified_places", [])
            if identified_places:
                places_payload = json.dumps(identified_places, ensure_ascii=False)
                yield f"event: places\ndata: {places_payload}\n\n"

            # 4. Stream deterministic transit journeys if calculated
            identified_journeys = state.get("identified_journeys", [])
            if identified_journeys:
                journeys_payload = json.dumps(identified_journeys, ensure_ascii=False)
                yield f"event: transit\ndata: {journeys_payload}\n\n"

            # 5. Stream CrowdSense alternatives if calculated
            identified_crowd = state.get("identified_crowd_alternatives", [])
            if identified_crowd:
                crowd_payload = json.dumps(identified_crowd, ensure_ascii=False)
                yield f"event: crowd_alternatives\ndata: {crowd_payload}\n\n"

            # 6. Stream done event with current profile & itinerary state
            done_payload = json.dumps({
                "session_id": request.session_id,
                "profile": state.get("profile", {}),
                "has_itinerary": bool(active_itinerary),
                "next_question": state.get("next_question")
            }, ensure_ascii=False)
            yield f"event: done\ndata: {done_payload}\n\n"

        except Exception as e:
            err_payload = json.dumps({"error": str(e)}, ensure_ascii=False)
            yield f"event: error\ndata: {err_payload}\n\n"

    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/sessions/{session_id}")
async def get_session_state(session_id: str):
    """Retrieve existing session messages, extracted profile, and grounded places."""
    state = hana_agent.get_or_create_state(session_id)
    return {
        "session_id": session_id,
        "message_count": len(state["messages"]),
        "profile": state["profile"],
        "asked_questions": state["asked_questions"],
        "identified_places": state["identified_places"],
        "identified_journeys": state.get("identified_journeys", []),
        "identified_crowd_alternatives": state.get("identified_crowd_alternatives", []),
        "active_itinerary": state.get("active_itinerary")
    }


@router.delete("/sessions/{session_id}")
async def clear_session_state(session_id: str):
    """Clear conversation history and reset session state for a new conversation."""
    session_manager.clear_session(session_id)
    if session_id in hana_agent.sessions:
        del hana_agent.sessions[session_id]
    return {"status": "cleared", "session_id": session_id}
