"""FujiNova Traveller Profile Schema."""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class TravellerProfile(BaseModel):
    origin_location: Optional[str] = Field(None, description="Starting hub (e.g. 'Kawaguchiko Station', 'Shinjuku', 'Otsuki')")
    party_composition: Optional[str] = Field(None, description="e.g. 'solo', 'couple', 'family_with_kids', 'multigenerational', 'friends'")
    has_elderly: bool = Field(False, description="True if travelling with seniors/grandparents")
    has_children: bool = Field(False, description="True if travelling with children/infants")
    mobility_limitations: Optional[bool] = Field(None, description="True if travelling with wheelchairs, strollers, or avoiding steep stairs")
    mobility_needs: Optional[str] = Field(None, description="Detailed mobility requirement: 'wheelchair', 'stroller', 'no_stairs'")
    preferred_pace: Optional[Literal['relaxed', 'moderate', 'active']] = Field(None, description="Desired daily travel pace")
    interests: List[str] = Field(default_factory=list, description="List of user interests: viewpoint, nature, shrine, museum, onsen, cultural")
    budget_tier: Optional[Literal['budget', 'standard', 'luxury']] = Field(None, description="Budget tier")
    trip_duration_days: Optional[int] = Field(None, ge=1, le=14, description="Length of trip in days")
    fuji_view_priority: int = Field(5, ge=1, le=5, description="1 to 5 priority of viewing Mount Fuji summit")
    indoor_preference: bool = Field(False, description="True if preferring indoor activities (e.g. due to weather or mobility)")
    interview_completed: bool = Field(False, description="True when minimum viable constraints have been extracted")
