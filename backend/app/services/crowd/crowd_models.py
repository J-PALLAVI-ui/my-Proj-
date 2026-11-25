"""FujiNova CrowdSense Data Models."""
from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field, computed_field, model_validator
from backend.app.models.place import Place

CrowdLevel = Literal["LOW", "MODERATE", "HIGH"]
CrowdDataClassification = Literal["LIVE", "STATIC", "USER_REPORTED", "SIMULATED", "UNAVAILABLE", "UNKNOWN"]
CrowdPreference = Literal["quiet", "balanced", "popular"]
CrowdScenario = Literal["low", "moderate", "high"]


class PlaceCrowdStatus(BaseModel):
    """Crowd status for a specific attraction."""
    place_id: str
    level: CrowdLevel = Field(..., description="Categorical crowd density: LOW, MODERATE, HIGH")
    score: int = Field(..., ge=0, le=100, description="Normalized crowd index from 0 (empty) to 100 (capacity)")
    classification: CrowdDataClassification = Field("SIMULATED", description="Data provenance tier")
    classification_label: str = Field(..., description="Human-readable provenance badge (e.g. 'SIMULATED (High Weekend Scenario)')")
    is_simulated: bool = Field(True, description="True if based on demonstration scenario model rather than live sensor feed")
    historical_peak_hours: Optional[str] = Field(None, description="Typical rush window (e.g. '11:00 - 14:30')")
    trend: Optional[Literal["rising", "steady", "falling"]] = Field("steady", description="Crowd progression trend")
    advisory: Optional[str] = Field(None, description="Visitor guidance notes (e.g. 'Parking queues exceeding 20 min')")


class CrowdSystemStatusResponse(BaseModel):
    """System-level crowd sensing infrastructure status."""
    provider_configured: bool = Field(False, description="Whether live cellular/IoT sensor API credentials are configured")
    live_data_available: bool = Field(False, description="Whether real-time density observations are actively broadcasting")
    status_text: str = Field(..., description="Summary of crowd monitoring infrastructure")
    active_scenario: CrowdScenario = Field("high", description="Currently active demonstration scenario")
    available_scenarios: List[Dict[str, str]] = Field(..., description="Selectable scenario definitions")
    classification: CrowdDataClassification = Field("SIMULATED", description="Data classification")
    timestamp: str = Field(..., description="System evaluation timestamp")
    provenance: str = Field("FujiNova CrowdSense Calibrated Scenario Engine v1.0")
    hero_image_url: str = Field("https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?auto=format&fit=crop&w=1600&q=80")
    hero_image_attribution: str = Field("Photo by Masaaki Komori on Unsplash (Mount Fuji with cherry blossoms & Lake Kawaguchi)")
    places: List[Dict[str, Any]] = Field(default_factory=list, description="All verified destinations with crowd metrics and imagery")
    data_classification: str = Field("SIMULATED_BASELINE", description="Data classification label")
    real_time_telemetry_status: str = Field("UNAVAILABLE", description="Live sensor status")


class CrowdRecommendationRequest(BaseModel):
    """Request schema for crowd-aware alternative recommendations."""
    place_id: Optional[str] = Field(None, description="Selected origin destination to evaluate (e.g. 'kawaguchiko_oishi_park')")
    current_place_id: Optional[str] = Field(None, description="Alias for place_id")
    preference: CrowdPreference = Field("quiet", description="Visitor density tolerance: 'quiet', 'balanced', or 'popular'")
    scenario: CrowdScenario = Field("high", description="Demonstration scenario: 'low', 'moderate', or 'high'")
    requires_accessibility: Optional[bool] = Field(False, description="Filter for wheelchair/step-free accessibility")
    user_interests: Optional[List[str]] = Field(None, description="Optional tourist interests (e.g. ['viewpoint', 'onsen'])")
    limit: Optional[int] = Field(3, description="Maximum recommendations count")

    @model_validator(mode="before")
    @classmethod
    def resolve_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            pid = data.get("place_id") or data.get("current_place_id")
            if not pid:
                raise ValueError("Field 'place_id' (or 'current_place_id') is required.")
            data["place_id"] = pid
            data["current_place_id"] = pid
            if "preference" in data and isinstance(data["preference"], str):
                data["preference"] = data["preference"].lower()
            if "scenario" in data and isinstance(data["scenario"], str):
                data["scenario"] = data["scenario"].lower()
        return data


class CrowdAlternativeCard(BaseModel):
    """Recommended alternative attraction with crowd comparison metrics."""
    place: Place
    crowd_status: PlaceCrowdStatus
    distance_km: float = Field(..., description="Geodesic distance in km from original destination")
    crowd_reduction_pct: int = Field(..., description="Percentage crowd density reduction compared to original")
    recommendation_reason: str = Field(..., description="Deterministic justification for why this spot is suggested")
    match_factors: List[str] = Field(..., description="Key criteria satisfied (e.g. 'Similar Fuji View', 'Barrier-Free')")
    image_url: str = Field(..., description="High-resolution verified photograph URL")
    image_attribution: str = Field(..., description="Photo provenance and photographer attribution")

    @computed_field
    def place_id(self) -> str:
        return self.place.place_id

    @computed_field
    def name_ja(self) -> str:
        return self.place.name_ja

    @computed_field
    def name_en(self) -> str:
        return self.place.name_en or self.place.name_ja

    @computed_field
    def primary_category(self) -> str:
        return self.place.primary_category

    @computed_field
    def crowd_level(self) -> str:
        return self.crowd_status.level.lower()

    @computed_field
    def crowd_index(self) -> int:
        return self.crowd_status.score

    @computed_field
    def crowd_reduction_percent(self) -> int:
        return self.crowd_reduction_pct

    @computed_field
    def fuji_view_rating(self) -> int:
        return self.place.fuji_view_rating

    @computed_field
    def accessibility_status(self) -> str:
        return self.place.accessibility_status

    @computed_field
    def admission_type(self) -> str:
        return self.place.general_admission_type

    @computed_field
    def admission_fee_jpy(self) -> Optional[int]:
        return self.place.general_admission_fee_jpy

    @computed_field
    def match_score(self) -> int:
        return max(50, 100 - self.crowd_status.score)


class CrowdRecommendationResponse(BaseModel):
    """Response containing original destination crowd status and ranked alternatives."""
    selected_destination: Place
    selected_crowd_status: PlaceCrowdStatus
    preference: CrowdPreference
    scenario: CrowdScenario
    alternatives: List[CrowdAlternativeCard]
    total_alternatives: int
    classification: CrowdDataClassification = Field("SIMULATED")
    advisory_summary: str = Field(..., description="Summary advice for current preference & scenario")

    @computed_field
    def current_place_id(self) -> str:
        return self.selected_destination.place_id

    @computed_field
    def current_place_name(self) -> str:
        return self.selected_destination.name_en or self.selected_destination.name_ja

    @computed_field
    def current_crowd_level(self) -> str:
        return self.selected_crowd_status.level.lower()

    @computed_field
    def current_congestion_advisory(self) -> str:
        return self.selected_crowd_status.advisory or "Heavy tourist volume."

    @computed_field
    def current_scenario(self) -> str:
        return self.scenario

    @computed_field
    def data_classification(self) -> str:
        return "SIMULATED_BASELINE"

    @computed_field
    def real_time_telemetry_status(self) -> str:
        return "UNAVAILABLE"


class CrowdDivertRequest(BaseModel):
    current_place_id: str = Field(..., description="Currently crowded place ID (e.g. 'arakurayama_chureito')")
    preference: CrowdPreference = Field("quiet", description="Crowd preference")
    scenario: CrowdScenario = Field("high", description="Crowd scenario")
    target_alternative_id: Optional[str] = Field(None, description="Optional user-selected alternative place ID")


class CrowdDivertResponse(BaseModel):
    original_place_id: str
    original_place_name: str
    original_crowd_level: str
    diverted_alternative: CrowdAlternativeCard
    crowd_reduction_percent: int
    transit_connection: Optional[Dict[str, Any]] = None
    diversion_advice: str
    status: str = "success"
