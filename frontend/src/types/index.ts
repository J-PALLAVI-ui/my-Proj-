export interface Place {
  place_id: string;
  name_ja: string;
  name_en?: string;
  latitude: number;
  longitude: number;
  coords_source: string;
  primary_category: string;
  sub_category?: string;
  opening_status: 'ALWAYS_OPEN' | 'REGULAR_HOURS' | 'SEASONAL_CLOSURE' | 'TEMPORARILY_CLOSED' | 'UNKNOWN';
  opening_hours_text?: string;
  opening_hours_source: string;
  general_admission_type: 'FREE' | 'PAID' | 'UNKNOWN';
  general_admission_fee_jpy?: number | null;
  optional_activities_fee_desc?: string | null;
  admission_fee_source: string;
  accessibility_status: 'VERIFIED_ACCESSIBLE' | 'PARTIAL_STEPS' | 'STEEP_STAIRS' | 'INACCESSIBLE' | 'UNKNOWN';
  accessibility_evidence?: string;
  stair_step_count?: number | null;
  accessibility_source: string;
  fuji_view_rating: number;
  indoor_alternative: boolean;
  discovery_type?: 'FAMOUS' | 'HIDDEN_GEM' | string;
  image_url?: string;
  region_id?: string;
  description?: string;
  provenance_tier: 'OFFICIAL_GOV' | 'OFFICIAL_OPERATOR' | 'COMMUNITY_OSM' | 'UNVERIFIED';
  source_url: string;
  required_attribution: string;
  source_retrieval_date: string;
  last_verified_date: string;
}

export interface TravellerProfile {
  origin_location?: string;
  party_composition?: string;
  has_elderly?: boolean;
  has_children?: boolean;
  mobility_limitations?: boolean;
  mobility_needs?: string;
  preferred_pace?: 'relaxed' | 'moderate' | 'active';
  interests?: string[];
  budget_tier?: 'budget' | 'standard' | 'luxury';
  trip_duration_days?: number;
  fuji_view_priority?: number;
  indoor_preference?: boolean;
}

export interface JourneyLeg {
  mode: 'bus' | 'rail' | 'walk';
  operator: string;
  route_id?: string;
  route_short_name?: string;
  route_long_name?: string;
  route_color: string;
  route_text_color: string;
  trip_headsign?: string;
  origin_stop_id: string;
  origin_stop_name: string;
  origin_stop_name_en: string;
  departure_time: string;
  departure_timestamp_sec: number;
  destination_stop_id: string;
  destination_stop_name: string;
  destination_stop_name_en: string;
  arrival_time: string;
  arrival_timestamp_sec: number;
  duration_minutes: number;
  intermediate_stops_count: number;
  intermediate_stops: string[];
  fare_jpy?: number | null;
  provenance: string;
  provenance_badge: string;
  advisory_notes?: string | null;
}

export interface Journey {
  journey_id: string;
  departure_time: string;
  arrival_time: string;
  total_duration_minutes: number;
  transfers_count: number;
  total_fare_jpy?: number | null;
  legs: JourneyLeg[];
  provenance_badges: string[];
  warnings: string[];
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'hana';
  text: string;
  places?: Place[];
  journeys?: Journey[];
  crowd_alternatives?: CrowdAlternativeCard[];
  timestamp: string;
}

export type CrowdLevel = 'low' | 'moderate' | 'high' | 'packed' | 'LOW' | 'MODERATE' | 'HIGH';
export type CrowdDataClassification = 'SIMULATED_BASELINE' | 'CALIBRATED_HEURISTIC' | 'REAL_TIME_TELEMETRY' | 'SIMULATED';
export type CrowdPreference = 'quiet' | 'balanced' | 'popular';
export type CrowdScenario = 'low' | 'moderate' | 'high';

export interface PlaceCrowdStatus {
  place_id: string;
  name_ja?: string;
  name_en?: string;
  scenario?: CrowdScenario;
  level?: string;
  score?: number;
  crowd_level?: CrowdLevel | string;
  crowd_index?: number;
  capacity_percentage?: number;
  congestion_advisory?: string;
  advisory?: string;
  data_classification?: CrowdDataClassification | string;
  real_time_telemetry_status?: string;
  image_url?: string;
  image_attribution?: string;
  fuji_view_rating?: number;
  accessibility_status?: string;
  primary_category?: string;
}

export interface CrowdAlternativeCard {
  place_id: string;
  name_ja: string;
  name_en: string;
  primary_category: string;
  crowd_level: CrowdLevel | string;
  crowd_index: number;
  crowd_reduction_percent: number;
  crowd_reduction_pct?: number;
  distance_km: number;
  fuji_view_rating: number;
  accessibility_status: string;
  admission_type?: string;
  admission_fee_jpy?: number | null;
  image_url: string;
  image_attribution: string;
  recommendation_reason: string;
  match_score?: number;
  place?: Place;
  crowd_status?: PlaceCrowdStatus;
}

export interface CrowdRecommendationResponse {
  current_place_id: string;
  current_place_name: string;
  current_crowd_level: CrowdLevel | string;
  current_congestion_advisory: string;
  current_scenario: CrowdScenario;
  data_classification: CrowdDataClassification | string;
  real_time_telemetry_status: string;
  alternatives: CrowdAlternativeCard[];
  selected_destination?: Place;
  selected_crowd_status?: PlaceCrowdStatus;
}

export interface CrowdSystemStatusResponse {
  active_scenario: CrowdScenario;
  available_scenarios: Array<{ id: string; name: string; description: string }> | any[];
  data_classification?: CrowdDataClassification | string;
  classification?: string;
  real_time_telemetry_status?: string;
  status_text?: string;
  places?: PlaceCrowdStatus[];
  hero_image_url?: string;
  hero_image_attribution?: string;
}

export interface ItineraryStop {
  stop_id: string;
  place_id: string;
  name_en: string;
  name_ja: string;
  category: string;
  fuji_view_rating: number;
  accessibility_status: string;
  estimated_arrival: string;
  duration_minutes: number;
  image_url: string;
  admission_info: string;
  notes?: string;
  transit_to_next?: {
    departure_time: string;
    arrival_time: string;
    duration_minutes: number;
    fare_jpy: number;
    transfers: number;
    operator: string;
    route_name: string;
    route_color: string;
  } | null;
}

export interface ItineraryDay {
  day_number: number;
  title: string;
  stops: ItineraryStop[];
}

export interface ItineraryPlan {
  plan_id: string;
  title: string;
  total_days: number;
  party_composition: string;
  mobility_needs?: string;
  budget_tier: string;
  pace: string;
  days: ItineraryDay[];
  summary_notes?: string;
}

export interface StepByStepLeg {
  step_number: number;
  step_type: 'WALK' | 'TRANSIT' | 'SIGHTSEEING' | 'MEAL' | 'RETURN' | string;
  title: string;
  instruction: string;
  location_name: string;
  departure_time?: string;
  arrival_time?: string;
  duration_minutes: number;
  distance_meters?: number;
  operator?: string;
  route_name?: string;
  route_color?: string;
  fare_jpy?: number;
  notes?: string;
  crowd_forecast?: SeasonalCrowdForecastData;
}

export interface PassComparisonOption {
  option_type: 'individual_tickets' | 'pass' | string;
  title: string;
  pass_id?: string;
  pass_price_jpy: number;
  uncovered_fares_jpy: number;
  total_cost_jpy: number;
  potential_savings_jpy: number;
  is_recommended: boolean;
  recommendation_reason: string;
  covered_legs_count: number;
  uncovered_legs_count: number;
  official_source_url: string;
}

export interface PassOptimizationResult {
  individual_tickets_cost_jpy: number;
  recommended_option: PassComparisonOption;
  all_options: PassComparisonOption[];
  adult_count: number;
  child_count: number;
  total_legs_evaluated: number;
  jr_pass_advisory: string;
  currency: string;
}

export interface SeasonalCrowdForecastData {
  place_id: string;
  score: number;
  level: 'VERY_LOW' | 'LOW' | 'MODERATE' | 'HIGH' | 'VERY_HIGH';
  level_label: string;
  badge_color: string;
  provenance: string;
  confidence_pct: number;
  is_weekend: boolean;
  day_type: string;
  active_events: string[];
  time_evaluated: string;
  date_evaluated: string;
  advisory: string;
  recommend_quieter_alternative: boolean;
}

export interface TimeBudgetedItineraryResponse {
  itinerary_id: string;
  title: string;
  start_location: string;
  destination_name: string;
  time_budget_hours: number;
  total_duration_minutes: number;
  departure_time: string;
  return_time: string;
  is_feasible: boolean;
  steps: StepByStepLeg[];
  cost_summary: PassOptimizationResult;
  crowd_summary?: SeasonalCrowdForecastData;
  variations: Array<{
    id: string;
    label: string;
    description: string;
  }>;
}


