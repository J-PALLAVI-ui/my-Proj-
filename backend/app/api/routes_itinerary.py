"""FujiNova Itinerary API Router."""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.agent.hana import agent as hana_agent
from backend.app.services.itinerary.itinerary_service import (
    ItineraryPlan, generate_itinerary, modify_itinerary
)

router = APIRouter(prefix="/api/v1/itinerary", tags=["Itinerary"])


class ItineraryGenerateRequest(BaseModel):
    session_id: Optional[str] = None
    party_type: str = Field("couple", description="solo, couple, family_with_kids, multigenerational, friends")
    duration_days: int = Field(1, ge=1, le=5)
    mobility_needs: Optional[str] = Field(None, description="none, wheelchair, stroller, slow_walking, no_stairs")
    interests: List[str] = Field(default_factory=list)
    budget_tier: str = Field("standard", description="budget, standard, luxury")
    pace: str = Field("moderate", description="relaxed, moderate, active")


class ItineraryUpdateRequest(BaseModel):
    session_id: Optional[str] = None
    plan: Optional[ItineraryPlan] = None
    action: str = Field(..., description="remove_stop, add_stop, replace_stop, make_cheaper, reduce_walking")
    target: Optional[Any] = None
    place_id: Optional[str] = None
    day: int = 1
    after_index: Optional[int] = None
    old_place_id: Optional[str] = None
    new_place_id: Optional[str] = None


@router.post("/generate", response_model=ItineraryPlan)
def api_generate_itinerary(request: ItineraryGenerateRequest):
    """Generate a structured, grounded multi-day itinerary."""
    plan = generate_itinerary(
        party_type=request.party_type,
        duration_days=request.duration_days,
        mobility_needs=request.mobility_needs,
        interests=request.interests,
        budget_tier=request.budget_tier,
        pace=request.pace
    )
    if request.session_id:
        state = hana_agent.get_or_create_state(request.session_id)
        state["active_itinerary"] = plan.model_dump()
    return plan


@router.post("/update", response_model=ItineraryPlan)
def api_update_itinerary(request: ItineraryUpdateRequest):
    """Modify an existing itinerary."""
    plan = request.plan
    if not plan and request.session_id:
        state = hana_agent.get_or_create_state(request.session_id)
        if state.get("active_itinerary"):
            plan = ItineraryPlan.model_validate(state["active_itinerary"])

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active itinerary found to modify. Please generate an itinerary first."
        )

    updated_plan = modify_itinerary(
        plan=plan,
        action=request.action,
        target=request.target,
        place_id=request.place_id,
        day=request.day,
        after_index=request.after_index,
        old_place_id=request.old_place_id,
        new_place_id=request.new_place_id
    )

    if request.session_id:
        state = hana_agent.get_or_create_state(request.session_id)
        state["active_itinerary"] = updated_plan.model_dump()

    return updated_plan


@router.get("/session/{session_id}")
def api_get_session_itinerary(session_id: str):
    """Retrieve active itinerary for the given session."""
    state = hana_agent.get_or_create_state(session_id)
    if not state.get("active_itinerary"):
        return {"session_id": session_id, "has_itinerary": False, "itinerary": None}
    return {
        "session_id": session_id,
        "has_itinerary": True,
        "itinerary": state["active_itinerary"]
    }
