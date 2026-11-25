"""FujiNova Itinerary API Router."""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.agent.hana import agent as hana_agent
from backend.app.services.itinerary.itinerary_service import (
    ItineraryPlan,
    generate_itinerary,
    modify_itinerary,
    generate_time_budgeted_itinerary,
    TimeBudgetedItineraryResponse,
)
from backend.app.services.routing.pass_optimizer import PassOptimizer, PassOptimizationResult

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


class TimeBudgetItineraryRequest(BaseModel):
    start_location: str = Field("Kawaguchiko Station", description="Origin hub, station, or GPS coordinate")
    target_place_id: str = Field("kawaguchiko_oishi_park", description="Primary destination place_id")
    available_hours: float = Field(5.0, ge=1.0, le=12.0, description="Available duration for total trip (1 to 12 hours)")
    departure_time: str = Field("09:30:00", description="Departure time in HH:MM:SS or HH:MM format")
    party_composition: str = Field("couple", description="solo, couple, family_with_kids, multigenerational, friends")
    adult_count: int = Field(1, ge=1, le=20)
    child_count: int = Field(0, ge=0, le=20)
    user_has_jr_pass: bool = Field(False, description="Whether traveler holds a Japan Rail Pass")
    prefer_quiet: bool = Field(True, description="Whether to prioritize less-crowded destinations")
    session_id: Optional[str] = None


class PassOptimizeRequest(BaseModel):
    legs: List[Dict[str, Any]]
    adult_count: int = 1
    child_count: int = 0
    user_has_jr_pass: bool = False


@router.post("/time-budget", response_model=TimeBudgetedItineraryResponse)
def api_time_budgeted_itinerary(request: TimeBudgetItineraryRequest):
    """
    Generates a realistic, time-budgeted journey connecting verified Fujikyu transit,
    sightseeing, dining breaks, secondary destinations, and return transport.
    """
    plan = generate_time_budgeted_itinerary(
        start_location=request.start_location,
        target_place_id=request.target_place_id,
        available_hours=request.available_hours,
        departure_time=request.departure_time,
        party_composition=request.party_composition,
        adult_count=request.adult_count,
        child_count=request.child_count,
        user_has_jr_pass=request.user_has_jr_pass,
        prefer_quiet=request.prefer_quiet
    )
    if request.session_id:
        state = hana_agent.get_or_create_state(request.session_id)
        state["active_itinerary"] = plan.model_dump()
    return plan


@router.post("/optimize-passes", response_model=PassOptimizationResult)
def api_optimize_passes(request: PassOptimizeRequest):
    """
    Compares total individual fares against official Fujikyu sightseeing passes and
    recommends the cheapest valid pass with potential savings and JR pass advisories.
    """
    return PassOptimizer.evaluate_itinerary_costs(
        legs=request.legs,
        adult_count=request.adult_count,
        child_count=request.child_count,
        user_has_jr_pass=request.user_has_jr_pass
    )
