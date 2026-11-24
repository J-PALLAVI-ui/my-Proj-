"""FujiNova Place Data Models."""
from typing import Optional, Literal
from pydantic import BaseModel, Field


class Place(BaseModel):
    place_id: str = Field(..., description="Unique slug identifier (e.g. 'kawaguchiko_oishi_park')")
    name_ja: str = Field(..., description="Official Japanese name")
    name_en: Optional[str] = Field(None, description="English name if officially available")
    
    # Spatial
    latitude: float = Field(..., ge=-90.0, le=90.0, description="WGS84 Latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="WGS84 Longitude")
    coords_source: str = Field(..., description="Source of coordinates (e.g. 'MLIT_P12', 'MUNICIPAL_GIS')")
    
    # Classification
    primary_category: str = Field(..., description="e.g. 'viewpoint', 'shrine', 'museum', 'nature', 'cultural', 'onsen', 'park'")
    sub_category: Optional[str] = Field(None, description="e.g. 'botanical_garden', 'historic_shrine', 'cave'")
    
    # Opening Hours
    opening_status: Literal['ALWAYS_OPEN', 'REGULAR_HOURS', 'SEASONAL_CLOSURE', 'TEMPORARILY_CLOSED', 'UNKNOWN']
    opening_hours_text: Optional[str] = Field(None, description="Verified operating hours or NULL if ALWAYS_OPEN/UNKNOWN")
    opening_hours_source: str = Field(..., description="Agency or URL proving opening hours")
    
    # Admission & Pricing
    general_admission_type: Literal['FREE', 'PAID', 'UNKNOWN']
    general_admission_fee_jpy: Optional[int] = Field(None, ge=0, description="General admission in JPY; NULL if FREE/UNKNOWN")
    optional_activities_fee_desc: Optional[str] = Field(None, description="Optional paid services or special exhibitions")
    admission_fee_source: str = Field(..., description="Agency or URL proving fee structure")
    
    # Accessibility
    accessibility_status: Literal['VERIFIED_ACCESSIBLE', 'PARTIAL_STEPS', 'STEEP_STAIRS', 'INACCESSIBLE', 'UNKNOWN']
    accessibility_evidence: Optional[str] = Field(None, description="Documented evidence for accessibility rating")
    stair_step_count: Optional[int] = Field(None, ge=0, description="Known physical step count (e.g. 398 for Chureito)")
    accessibility_source: str = Field(..., description="Source proving accessibility status")
    
    # Environmental & Travel Context
    fuji_view_rating: int = Field(..., ge=1, le=5, description="1 to 5 rating of line-of-sight to Mt. Fuji")
    indoor_alternative: bool = Field(..., description="True if suitable during rain or zero summit visibility")
    
    # Data Governance & Provenance
    provenance_tier: Literal['OFFICIAL_GOV', 'OFFICIAL_OPERATOR', 'COMMUNITY_OSM', 'UNVERIFIED']
    source_url: str = Field(..., description="Direct reference URL")
    required_attribution: str = Field(..., description="Mandatory attribution string for data reuse")
    source_retrieval_date: str = Field(..., description="ISO date YYYY-MM-DD when data was scraped/retrieved")
    last_verified_date: str = Field(..., description="ISO date YYYY-MM-DD of last audit verification")
