"""FujiNova Extended Place Data Models."""
from typing import Optional, Literal, List
from pydantic import BaseModel, Field


class Place(BaseModel):
    # Basic identification
    place_id: str = Field(..., description="Unique slug identifier (e.g. 'kawaguchiko_oishi_park')")
    name_ja: str = Field(..., description="Official Japanese name")
    name_en: Optional[str] = Field(None, description="English name if officially available")
    alternate_names: Optional[str] = Field(None, description="Comma-separated alternative names or aliases")
    official_address: Optional[str] = Field(None, description="Official street address or postal locality")
    municipality: Optional[str] = Field(None, description="City, town, or village (e.g. 'Fujikawaguchiko', 'Fujiyoshida')")
    prefecture: Optional[str] = Field("Yamanashi", description="Prefecture (Yamanashi, Shizuoka, Kanagawa)")
    description: Optional[str] = Field(None, description="Detailed visitor description")
    short_description: Optional[str] = Field(None, description="Concise one-line summary")
    
    # Spatial & Geography
    latitude: float = Field(..., ge=-90.0, le=90.0, description="WGS84 Latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="WGS84 Longitude")
    coords_source: str = Field(..., description="Source of coordinates (e.g. 'MLIT_P12', 'MUNICIPAL_GIS', 'OPENSTREETMAP')")
    elevation_m: Optional[int] = Field(None, description="Elevation in meters above sea level")
    region_id: Optional[str] = Field(None, description="Geographic region key (e.g. 'kawaguchiko', 'fujiyoshida', 'yamanakako', 'kofu')")
    
    # Classification & Discovery
    primary_category: str = Field(..., description="e.g. 'viewpoint', 'shrine', 'museum', 'nature', 'cultural', 'onsen', 'park'")
    sub_category: Optional[str] = Field(None, description="e.g. 'botanical_garden', 'historic_shrine', 'cave', 'pass', 'waterfall'")
    discovery_type: Literal['FAMOUS', 'HIDDEN_GEM', 'LOCAL_FAVOURITE', 'SEASONAL'] = Field('FAMOUS', description="Catalogue tier")
    popularity_classification: Optional[str] = Field(None, description="Popularity badge (e.g. 'TOP_VIEWPOINT', 'QUIET_SANCTUARY')")
    seasonal_tags: Optional[str] = Field(None, description="Comma-separated seasonal keywords (e.g. 'sakura,autumn_foliage,winter_fuji')")
    interests: Optional[str] = Field(None, description="Comma-separated interest tags (e.g. 'viewpoint,nature,photography,hiking')")
    recommended_for: Optional[str] = Field(None, description="Recommended traveler types (e.g. 'couples,families,photographers,hikers')")
    
    # Opening Hours
    opening_status: Literal['ALWAYS_OPEN', 'REGULAR_HOURS', 'SEASONAL_CLOSURE', 'TEMPORARILY_CLOSED', 'UNKNOWN']
    opening_hours_text: Optional[str] = Field(None, description="Verified operating hours or NULL if ALWAYS_OPEN/UNKNOWN")
    opening_hours_source: str = Field(..., description="Agency or URL proving opening hours")
    seasonal_closure: Optional[str] = Field(None, description="Notes on winter or seasonal closures")
    best_visit_months: Optional[str] = Field(None, description="Optimal visiting months (e.g. 'Apr-Nov', 'Year-round')")
    
    # Admission & Pricing
    general_admission_type: Literal['FREE', 'PAID', 'UNKNOWN']
    general_admission_fee_jpy: Optional[int] = Field(None, ge=0, description="General admission in JPY; NULL if FREE/UNKNOWN")
    optional_activities_fee_desc: Optional[str] = Field(None, description="Optional paid services or special exhibitions")
    admission_fee_source: str = Field(..., description="Agency or URL proving fee structure")
    fee_last_verified: Optional[str] = Field(None, description="ISO date of fee verification")
    
    # Accessibility
    accessibility_status: Literal['VERIFIED_ACCESSIBLE', 'PARTIAL_STEPS', 'STEEP_STAIRS', 'INACCESSIBLE', 'UNKNOWN']
    accessibility_evidence: Optional[str] = Field(None, description="Documented evidence for accessibility rating")
    stair_step_count: Optional[int] = Field(None, ge=0, description="Known physical step count (e.g. 398 for Chureito)")
    wheelchair_suitability: Optional[str] = Field(None, description="Detailed wheelchair accessibility evaluation")
    accessibility_source: str = Field(..., description="Source proving accessibility status")
    
    # Photography & Images
    image_url: Optional[str] = Field(None, description="High-quality direct photograph URL (permissively licensed or official)")
    image_source_url: Optional[str] = Field(None, description="Original web page containing the verified photograph")
    image_attribution: Optional[str] = Field(None, description="Author or photographer attribution credit")
    image_license: Optional[str] = Field(None, description="License type (e.g. 'CC-BY-SA 4.0', 'Unsplash License', 'Public Domain')")
    image_alt_text: Optional[str] = Field(None, description="Accessible image description")
    image_verified_at: Optional[str] = Field(None, description="ISO date when image was verified")
    photo_search_url: Optional[str] = Field(None, description="Original reference search URL from catalog PDF")
    
    # Transportation & Access
    nearest_bus_stops: Optional[str] = Field(None, description="Nearest verified bus stop names")
    nearest_railway_stations: Optional[str] = Field(None, description="Nearest railway stations")
    gtfs_stop_ids: Optional[str] = Field(None, description="Comma-separated GTFS-JP stop IDs if within transit boundary")
    transport_operators: Optional[str] = Field(None, description="Operating transport transit companies (e.g. 'Fujikyu Bus', 'JR East')")
    transit_access_status: Optional[str] = Field("VERIFIED_TRANSIT", description="Status of public transit connectivity")
    walking_distance_to_nearest_stop: Optional[str] = Field(None, description="Walking time/distance from closest transit stop")
    
    # Tourism & Experience Metrics
    estimated_visit_duration_minutes: Optional[int] = Field(60, description="Recommended visit duration in minutes")
    fuji_view_rating: int = Field(..., ge=1, le=5, description="1 to 5 rating of line-of-sight to Mt. Fuji")
    best_time_to_visit: Optional[str] = Field(None, description="Recommended time of day (e.g. 'Early morning', 'Sunset')")
    indoor_alternative: bool = Field(..., description="True if suitable during rain or zero summit visibility")
    family_friendly: Optional[bool] = Field(True, description="Suitable for traveling with children")
    elderly_friendly: Optional[bool] = Field(True, description="Suitable for older travelers with limited mobility")
    facilities_available: Optional[str] = Field(None, description="Available facilities (restrooms, parking, cafe, gift shop)")
    
    # Crowd Analytics
    expected_crowd_profile: Optional[str] = Field(None, description="General crowd profile description")
    weekday_crowd_profile: Optional[str] = Field(None, description="Weekday baseline crowd")
    weekend_crowd_profile: Optional[str] = Field(None, description="Weekend crowd surge expectation")
    seasonal_crowd_profile: Optional[str] = Field(None, description="Peak season crowd notes")
    crowd_prediction_method: Optional[str] = Field("CALIBRATED_HEURISTIC", description="Data provenance for crowd forecasting")
    crowd_confidence: Optional[int] = Field(90, description="Crowd model confidence percentage (0-100)")
    
    # Data Governance & Provenance
    provenance_tier: Literal['OFFICIAL_GOV', 'OFFICIAL_OPERATOR', 'COMMUNITY_OSM', 'UNVERIFIED']
    source_url: str = Field(..., description="Direct reference URL")
    required_attribution: str = Field(..., description="Mandatory attribution string for data reuse")
    source_retrieval_date: str = Field(..., description="ISO date YYYY-MM-DD when data was scraped/retrieved")
    last_verified_date: str = Field(..., description="ISO date YYYY-MM-DD of last audit verification")


class PlaceMarker(BaseModel):
    """Lightweight projection for map and 3D digital twin markers."""
    place_id: str
    name_ja: str
    name_en: Optional[str]
    latitude: float
    longitude: float
    primary_category: str
    discovery_type: str
    fuji_view_rating: int
    image_url: Optional[str]
    region_id: Optional[str]
    opening_status: str
    general_admission_type: str

