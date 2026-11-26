"""FujiNova Hana Conversational Agent: General-Purpose Intelligence & Grounded Regional Expert."""
import json
import re
import logging
from typing import Dict, Any, List, Optional, AsyncIterator, Tuple
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

from backend.app.models.traveller import TravellerProfile
from backend.app.api.routes_places import search_places_db, get_place_by_id
from backend.app.services.llm.router import ModelRouter, router as global_router
from backend.app.core.config import settings
from backend.app.services.routing.transit_models import RouteSearchRequest, JourneySchema
from backend.app.services.routing.routing_service import get_routing_service
from backend.app.services.crowd.crowd_models import CrowdRecommendationRequest
from backend.app.services.crowd.recommendation_service import recommendation_service
from backend.app.services.rag.retriever import retriever as rag_retriever
from backend.app.services.live_info.weather_service import get_weather_info, MONTHLY_CLIMATE_DATA
from backend.app.services.live_info.advisory_service import get_current_advisories
from backend.app.services.itinerary.itinerary_service import (
    ItineraryPlan, generate_itinerary, modify_itinerary
)
from backend.app.services.conversation.session_manager import session_manager

logger = logging.getLogger("fujinova.agent.hana")


class HanaState(TypedDict):
    """Execution state for Hana conversational agent."""
    session_id: str
    messages: List[Dict[str, str]]
    profile: Dict[str, Any]
    asked_questions: List[str]
    identified_places: List[Dict[str, Any]]
    identified_journeys: List[Dict[str, Any]]
    identified_crowd_alternatives: List[Dict[str, Any]]
    active_itinerary: Optional[Dict[str, Any]]
    next_question: Optional[str]


HANA_SYSTEM_INSTRUCTION = """You are Hana (ハナ), the intelligent, warm, highly capable AI companion for FujiNova.

CORE IDENTITY & CAPABILITIES:
1. GENERAL-PURPOSE INTELLIGENCE:
   - You are a full-fledged, versatile AI assistant similar to ChatGPT.
   - You answer unrestricted general knowledge questions with clarity, depth, and precision:
     science, machine learning, technology, programming, Japanese culture, history, world travel, calculations, and languages.
   - IMPORTANT: DO NOT force every conversation into travel planning. If the user asks about machine learning, programming errors, language translation, or world history, answer their question directly, thoroughly, and helpfully.
   - Only recommend travel destinations or itineraries when the user asks or when the conversation naturally touches upon Mount Fuji, tourism, or logistics.

2. SPECIALIZED MOUNT FUJI & JAPANESE TRAVEL EXPERT:
   - When discussing Mount Fuji, the Fuji Five Lakes (Kawaguchiko, Yamanakako, Saiko, Shojiko, Motosuko), and Yamanashi Prefecture:
     provide deep, authoritative, verified regional guidance grounded in real geography, official GTFS transit schedules, and seasonal conditions.
   - Clearly distinguish verified local database records from general travel advice.
   - For steep stairs (such as Arakurayama Sengen Park's 398 steps), always warn mobility-sensitive or elderly travellers.

3. MULTILINGUAL MASTERY:
   - Automatically detect the user's language and respond fluently in the same language.
   - Fluent support for English, Japanese (日本語), Hindi (हिन्दी), Tamil (தமிழ்), Kannada (ಕನ್ನಡ), Telugu (తెలుగు), and other global languages.
   - In Japanese, use natural, polite keigo (丁寧語: です・ます調) and accurate kanji for regional destinations (河口湖, 新倉山浅間公園, 忍野八海, 大石公園).
   - In Indian languages, use authentic, natural phrasing in native scripts.

4. MULTI-TURN CONVERSATIONAL MEMORY & ADAPTABILITY:
   - Remember previous turns, traveler counts, budgets, and preferences within the session.
   - Understand context references such as "there", "that place", "the previous option", and "make it cheaper".
   - Avoid repetitive robotic greetings in ongoing conversations.
"""


class ExtractedProfileUpdate(BaseModel):
    """Structured extraction schema from conversational user message."""
    party_composition: Optional[str] = Field(None, description="solo, couple, family_with_kids, multigenerational, friends")
    has_children: Optional[bool] = Field(None)
    has_elderly: Optional[bool] = Field(None)
    mobility_limitations: Optional[bool] = Field(None)
    mobility_needs: Optional[str] = Field(None, description="none, wheelchair, stroller, slow_walking, no_stairs")
    interests: List[str] = Field(default_factory=list, description="nature, viewpoint, museum, shrine, onsen, craft, photography")
    budget_tier: Optional[str] = Field(None, description="budget, standard, luxury")
    preferred_pace: Optional[str] = Field(None, description="relaxed, moderate, active")
    trip_duration_days: Optional[int] = Field(None)
    indoor_preference: Optional[bool] = Field(None)
    detected_intent: str = Field("chat", description="general_query, travel_query, transit_query, itinerary_request, crowd_query")


def has_word(text: str, *words: str) -> bool:
    """Check if any of the given words appear as discrete words in text."""
    pattern = r"\b(" + "|".join(re.escape(w) for w in words) + r")\b"
    return bool(re.search(pattern, text, re.IGNORECASE))


def heuristic_extract(text: str) -> ExtractedProfileUpdate:
    """Deterministic heuristic extraction from message text."""
    update = ExtractedProfileUpdate()
    lower = text.lower()

    if has_word(lower, "wheelchair"):
        update.mobility_needs = "wheelchair"
        update.mobility_limitations = True
    elif has_word(lower, "stroller"):
        update.mobility_needs = "stroller"
        update.mobility_limitations = True
    elif "stairs" in lower and any(w in lower for w in ["avoid", "cannot", "no", "without"]):
        update.mobility_needs = "no_stairs"
        update.mobility_limitations = True
    elif "no mobility issues" in lower or "neither of us have mobility issues" in lower or "fully mobile" in lower:
        update.mobility_limitations = False

    if has_word(lower, "grandmother", "grandfather", "elderly", "senior", "grandparents"):
        update.has_elderly = True
        update.party_composition = "multigenerational"
    elif has_word(lower, "partner", "husband", "wife", "boyfriend", "girlfriend", "couple"):
        update.party_composition = "couple"
    elif has_word(lower, "kids", "children", "baby", "infant", "toddler"):
        update.has_children = True
        update.party_composition = "family_with_kids"
    elif has_word(lower, "solo", "alone", "myself") or "by myself" in lower:
        update.party_composition = "solo"
    elif has_word(lower, "friends"):
        update.party_composition = "friends"

    interests = []
    if has_word(lower, "view", "views", "fuji", "photo", "photos", "photography", "scenic"):
        interests.append("viewpoint")
    if has_word(lower, "nature", "lake", "park", "quiet", "outdoor"):
        interests.append("nature")
    if has_word(lower, "museum", "art", "gallery", "craft"):
        interests.append("museum")
    if has_word(lower, "shrine", "temple", "culture", "historical"):
        interests.append("shrine")
    if has_word(lower, "onsen", "bath") or "hot spring" in lower or "hot springs" in lower:
        interests.append("onsen")
    update.interests = interests

    if has_word(lower, "slow", "relaxed", "gentle", "leisurely"):
        update.preferred_pace = "relaxed"
    elif has_word(lower, "fast", "packed", "active", "hike", "hiking"):
        update.preferred_pace = "active"

    if has_word(lower, "rain", "indoor", "storm"):
        update.indoor_preference = True

    # Detect duration
    m_dur = re.search(r"\b(\d+)\s*(?:-| )?(?:day|days)\b", lower)
    if m_dur:
        update.trip_duration_days = int(m_dur.group(1))

    # Detect Intent
    if any(kw in lower for kw in ["itinerary", "plan a trip", "plan my trip", "plan a 1-day", "plan a one-day", "plan a 2-day", "plan a two-day"]):
        update.detected_intent = "itinerary_request"
    elif any(kw in lower for kw in ["crowd", "crowded", "quiet", "busy", "alternative", "congestion", "peaceful"]):
        update.detected_intent = "crowd_query"
    elif any(kw in lower for kw in ["bus", "train", "reach", "get to", "go to", "transport", "fare", "route", "direction"]):
        update.detected_intent = "transit_query"
    elif any(kw in lower for kw in ["recommend", "where should", "suggest", "places", "visit"]):
        update.detected_intent = "travel_query"
    else:
        update.detected_intent = "general_query"

    return update


def parse_time_intent(text: str) -> Optional[str]:
    """Extracts requested departure time in HH:MM:SS format."""
    m = re.search(r"\b(?:at|around|by)?\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", text, re.IGNORECASE)
    if m:
        hour_str, min_str, am_pm = m.groups()
        hour = int(hour_str)
        minute = int(min_str) if min_str else 0
        if am_pm:
            if am_pm.lower() == "pm" and hour < 12:
                hour += 12
            elif am_pm.lower() == "am" and hour == 12:
                hour = 0
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return f"{hour:02d}:{minute:02d}:00"
    return None


def clean_stop_name(name: str) -> str:
    """Removes trailing time and adverbial tokens from landmark/stop queries."""
    cleaned = re.sub(r"\b(?:at|around|by)?\s*\d{1,2}(?::\d{2})?\s*(?:am|pm)?\b", "", name, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(?:today|tomorrow|morning|afternoon|evening|night)\b", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip(" ?,.;:")


def extract_transit_query(text: str) -> Optional[Tuple[str, str, Optional[str]]]:
    """Extracts origin, destination, and requested departure time from transport questions."""
    lower = text.lower()
    transit_keywords = ["bus", "train", "reach", "get to", "go to", "travel", "route", "direction", "fare", "ticket", "line", "transport"]
    if not (any(kw in lower for kw in transit_keywords) or ("from " in lower and " to " in lower)):
        return None

    dep_time = parse_time_intent(text)

    # Pattern 1: "from X to Y"
    m1 = re.search(r"from\s+([A-Za-z0-9\s\u3000-\u30ff\u4e00-\u9faf]+?)\s+to\s+([A-Za-z0-9\s\u3000-\u30ff\u4e00-\u9faf]+?)(?:\?|$|\.|\,)", text, re.IGNORECASE)
    if m1:
        orig = clean_stop_name(m1.group(1))
        dest = clean_stop_name(m1.group(2))
        if orig and dest and orig.lower() != dest.lower():
            return orig, dest, dep_time

    # Pattern 2: "reach/get to/go to Y from X"
    m2 = re.search(r"(?:reach|get to|go to|travel to|take(?:\s+\w+)*\s+to|to)\s+([A-Za-z0-9\s\u3000-\u30ff\u4e00-\u9faf]+?)\s+from\s+([A-Za-z0-9\s\u3000-\u30ff\u4e00-\u9faf]+?)(?:\?|$|\.|\,)", text, re.IGNORECASE)
    if m2:
        dest = clean_stop_name(m2.group(1))
        orig = clean_stop_name(m2.group(2))
        if orig and dest and orig.lower() != dest.lower():
            return orig, dest, dep_time

    # Pattern 3: "bus to Y" or "how do I get to Y" without "from"
    if "from " not in lower:
        m3 = re.search(r"(?:reach|get to|go to|travel to|visit|bus to|bus from kawaguchiko station to)\s+([A-Za-z0-9\s\u3000-\u30ff\u4e00-\u9faf]+?)(?:\?|$|\.|\,)", text, re.IGNORECASE)
        if m3:
            dest = clean_stop_name(m3.group(1))
            if dest and dest.lower() not in ["there", "here", "somewhere"]:
                return "Kawaguchiko Station", dest, dep_time

    return None


def extract_crowd_query(text: str) -> Optional[Tuple[str, str]]:
    """Detect inquiries regarding crowds, alternatives, or quiet destinations."""
    lower = text.lower()
    crowd_words = ["crowd", "crowded", "quiet", "busy", "alternative", "congestion", "less crowded", "peaceful", "serene"]
    if not any(w in lower for w in crowd_words):
        return None

    target = "oishi"
    if "chureito" in lower or "pagoda" in lower or "arakurayama" in lower:
        target = "arakurayama"
    elif "shoji" in lower:
        target = "shoji"
    elif "yamanakako" in lower:
        target = "yamanakako"
    elif "saiko" in lower:
        target = "saiko"

    pref = "quiet"
    if "popular" in lower:
        pref = "popular"
    elif "balanced" in lower:
        pref = "balanced"

    return target, pref


class HanaAgent:
    """Intelligent Hana AI Agent managing general conversation, multi-turn state, RAG, and tools."""

    def __init__(self, model_router: Optional[ModelRouter] = None):
        self.router = model_router or global_router
        self.sessions: Dict[str, HanaState] = {}

    def extract_transit_query(self, text: str) -> Optional[Tuple[str, str, Optional[str]]]:
        return extract_transit_query(text)

    def extract_crowd_query(self, text: str) -> Optional[Tuple[str, str]]:
        return extract_crowd_query(text)

    def resolve_place_id(self, target_name: str) -> str:
        matches = search_places_db(query=target_name, limit=1)
        if matches:
            return matches[0]["place_id"]
        name_lower = target_name.lower()
        if "oishi" in name_lower or "kawaguchiko_oishi_park" in name_lower:
            return "kawaguchiko_oishi_park"
        if "chureito" in name_lower or "arakurayama" in name_lower:
            return "arakurayama_chureito_pagoda"
        if "shoji" in name_lower:
            return "shoji_tatego_hama"
        if "yamanakako" in name_lower or "nagaike" in name_lower:
            return "lake_yamanakako_nagaike"
        if "saiko" in name_lower or "iyashi" in name_lower:
            return "saiko_iyashi_no_sato"
        return "kawaguchiko_oishi_park"

    def determine_next_interview_question(self, state: HanaState) -> Optional[str]:
        """Select the next unasked question topic without repeating already answered attributes."""
        profile = state["profile"]
        asked = set(state["asked_questions"])

        topics = [
            ("mobility", not profile.get("mobility_needs") and profile.get("mobility_limitations") is None and "mobility" not in asked),
            ("party_type", not profile.get("party_composition") and "party_type" not in asked),
            ("interests", not profile.get("interests") and "interests" not in asked),
            ("stay_duration", not profile.get("trip_duration_days") and "stay_duration" not in asked),
            ("pace", not profile.get("preferred_pace") and "pace" not in asked),
        ]

        for topic, is_needed in topics:
            if is_needed:
                return topic
        return None

    def get_or_create_state(self, session_id: str) -> HanaState:
        """Retrieve existing session state or initialize a fresh profile."""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "session_id": session_id,
                "messages": [],
                "profile": TravellerProfile().model_dump(),
                "asked_questions": [],
                "identified_places": [],
                "identified_journeys": [],
                "identified_crowd_alternatives": [],
                "active_itinerary": None,
                "next_question": None
            }
        return self.sessions[session_id]

    async def extract_profile_updates(self, user_message: str, current_profile: Dict[str, Any]) -> ExtractedProfileUpdate:
        """Extract profile constraints using heuristics and fast intent classifier."""
        return heuristic_extract(user_message)

    def update_profile(self, state: HanaState, update: ExtractedProfileUpdate) -> None:
        """Merge newly extracted fields into state profile."""
        profile = state["profile"]
        if update.party_composition and not profile.get("party_composition"):
            profile["party_composition"] = update.party_composition
            if "party_type" not in state["asked_questions"]:
                state["asked_questions"].append("party_type")

        if update.has_children is not None:
            profile["has_children"] = update.has_children
        if update.has_elderly is not None:
            profile["has_elderly"] = update.has_elderly

        if update.mobility_limitations is not None:
            profile["mobility_limitations"] = update.mobility_limitations
            if "mobility" not in state["asked_questions"]:
                state["asked_questions"].append("mobility")

        if update.mobility_needs and not profile.get("mobility_needs"):
            profile["mobility_needs"] = update.mobility_needs
            profile["mobility_limitations"] = True
            if "mobility" not in state["asked_questions"]:
                state["asked_questions"].append("mobility")

        if update.interests:
            existing = set(profile.get("interests", []))
            existing.update(update.interests)
            profile["interests"] = list(existing)
            if "interests" not in state["asked_questions"]:
                state["asked_questions"].append("interests")

        if update.budget_tier and not profile.get("budget_tier"):
            profile["budget_tier"] = update.budget_tier
            if "budget" not in state["asked_questions"]:
                state["asked_questions"].append("budget")

        if update.preferred_pace and not profile.get("preferred_pace"):
            profile["preferred_pace"] = update.preferred_pace
            if "pace" not in state["asked_questions"]:
                state["asked_questions"].append("pace")

        if update.trip_duration_days and not profile.get("trip_duration_days"):
            profile["trip_duration_days"] = update.trip_duration_days
            if "stay_duration" not in state["asked_questions"]:
                state["asked_questions"].append("stay_duration")

    def query_grounded_places(self, state: HanaState, limit: int = 4) -> List[Dict[str, Any]]:
        """Query canonical SQLite places matching profile constraints and discovery preferences."""
        profile = state["profile"]
        mobility = profile.get("mobility_needs")
        interests = profile.get("interests", [])

        # Check if user asked for hidden gems or famous places in recent messages
        discovery_type = None
        user_msgs = " ".join([m.get("content", "") for m in state.get("messages", [])[-2:]]).lower()
        if any(w in user_msgs for w in ["hidden gem", "hidden gems", "secret", "less known", "offbeat", "quiet spot"]):
            discovery_type = "HIDDEN_GEM"
        elif any(w in user_msgs for w in ["famous", "iconic", "must-visit", "top attraction", "popular"]):
            discovery_type = "FAMOUS"

        accessibility_status = None
        if mobility in ("wheelchair", "stroller") or profile.get("mobility_limitations"):
            accessibility_status = "VERIFIED_ACCESSIBLE"

        category = interests[0] if interests else None
        places = search_places_db(
            category=category,
            discovery_type=discovery_type,
            accessibility_status=accessibility_status,
            limit=limit
        )

        if not places and (category or discovery_type):
            places = search_places_db(
                discovery_type=discovery_type,
                accessibility_status=accessibility_status,
                limit=limit
            )

        if not places:
            places = search_places_db(
                category="viewpoint",
                accessibility_status=accessibility_status,
                limit=limit
            )

        state["identified_places"] = places
        return places

    async def chat(
        self,
        session_id: str,
        user_message: str,
        user_location: Optional[Dict[str, float]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[str]:
        """Process turn and stream Hana conversational response with general AI & grounded tools."""
        state = self.get_or_create_state(session_id)
        state["messages"].append({"role": "user", "content": user_message})

        # Save to persistent conversation manager
        session_manager.add_message(session_id, "user", user_message)

        # 1. Profile Extraction & State Update
        update = await self.extract_profile_updates(user_message, state["profile"])
        self.update_profile(state, update)

        lower_msg = user_message.lower()

        # 2. Check for Itinerary Generation / Modification Requests
        m_hours = re.search(r"\b(\d{1,2}(?:\.\d+)?)\s*(?:hour|hours|hr|hrs)\b", lower_msg)
        is_time_budget_query = (
            m_hours is not None
            and any(kw in lower_msg for kw in ["have", "trip", "itinerary", "plan", "spend", "time", "explore", "can do"])
        )

        is_itinerary_request = (
            is_time_budget_query
            or update.detected_intent == "itinerary_request"
            or any(kw in lower_msg for kw in ["itinerary", "plan a trip", "plan my trip", "one-day", "1-day", "2-day", "two-day", "3-day"])
        )
        is_itinerary_modify = (
            any(kw in lower_msg for kw in ["remove the", "make it cheaper", "cheaper", "reduce walking", "add another", "replace"])
            and state.get("active_itinerary") is not None
        )

        itinerary_context = ""
        if is_time_budget_query and m_hours:
            avail_h = float(m_hours.group(1))
            target_pid = "kawaguchiko_oishi_park"
            for candidate_k in ["arakurayama", "chureito", "oishi", "oshino", "iyashi", "shoji", "motosu", "yamanakako"]:
                if candidate_k in lower_msg:
                    target_pid = self.resolve_place_id(candidate_k)
                    break
            from backend.app.services.itinerary.itinerary_service import generate_time_budgeted_itinerary
            time_plan = generate_time_budgeted_itinerary(
                start_location="Kawaguchiko Station",
                target_place_id=target_pid,
                available_hours=avail_h,
                departure_time="09:30:00",
                adult_count=1,
                child_count=0,
                user_has_jr_pass="jr pass" in lower_msg
            )
            state["active_itinerary"] = time_plan.model_dump()
            itinerary_context = (
                f"\n\nVERIFIED TIME-BUDGETED ITINERARY PLAN ({avail_h:.0f} HOURS):\n"
                f"Title: {time_plan.title}\n"
                f"Schedule ({time_plan.departure_time} - {time_plan.return_time}, Total: {time_plan.total_duration_minutes} min):\n"
            )
            for st in time_plan.steps:
                itinerary_context += f"- Step {st.step_number} [{st.step_type}]: {st.title} ({st.departure_time} - {st.arrival_time}) | {st.instruction}\n"
            itinerary_context += (
                f"\nTransport Pass Recommendation: {time_plan.cost_summary['recommended_option']['title']} "
                f"(Total: ¥{time_plan.cost_summary['recommended_option']['total_cost_jpy']:,}).\n"
                f"JR Pass Advisory: {time_plan.cost_summary['jr_pass_advisory']}\n"
            )
        elif is_itinerary_modify:
            active_plan = ItineraryPlan.model_validate(state["active_itinerary"])
            if "remove" in lower_msg:
                # remove 3rd or index
                m_num = re.search(r"(\d+)(?:st|nd|rd|th)?", lower_msg)
                idx = int(m_num.group(1)) - 1 if m_num else 2
                modify_itinerary(active_plan, "remove_stop", target=idx)
            elif "cheaper" in lower_msg:
                modify_itinerary(active_plan, "make_cheaper")
            elif "walking" in lower_msg:
                modify_itinerary(active_plan, "reduce_walking")
            state["active_itinerary"] = active_plan.model_dump()
            itinerary_context = (
                f"\n\nUPDATED ITINERARY PLAN: '{active_plan.title}'. "
                f"You have successfully modified the itinerary according to the traveller's request. "
                f"Detail the updated destinations and connection plan in your response."
            )
        elif is_itinerary_request:
            dur = update.trip_duration_days or 1
            party = update.party_composition or "couple"
            plan = generate_itinerary(
                party_type=party,
                duration_days=dur,
                mobility_needs=update.mobility_needs,
                interests=update.interests,
                budget_tier=update.budget_tier or "standard",
                pace=update.preferred_pace or "moderate"
            )
            state["active_itinerary"] = plan.model_dump()
            stops_summary = ", ".join([f"{s.name_en} ({s.estimated_arrival})" for day in plan.days for s in day.stops])
            itinerary_context = (
                f"\n\nGENERATED ITINERARY PLAN: '{plan.title}' with {len(plan.days)} days. "
                f"Stops: {stops_summary}. "
                f"Present this structured itinerary clearly with timing, destination highlights, and transit connections."
            )

        # 3. Grounded Database Places (if asking for destinations/recommendations)
        is_asking_places = (
            update.detected_intent in ("travel_query", "itinerary_request")
            or any(kw in lower_msg for kw in ["recommend", "where should", "suggest", "places to visit", "hidden attractions"])
        )
        grounded_places = []
        if is_asking_places:
            grounded_places = self.query_grounded_places(state)

        # 4. Deterministic Public Transport Routing via RAPTOR
        transit_info = extract_transit_query(user_message)
        transit_context = ""
        state["identified_journeys"] = []
        if transit_info:
            orig_q, dest_q, dep_time_str = transit_info
            try:
                routing_svc = get_routing_service()
                req_dep_time = dep_time_str or "09:00:00"
                
                # Check if origin is GPS coordinates or "current/my location"
                m_coord = re.search(r"(-?\d{1,3}\.\d+)\s*,\s*(-?\d{1,3}\.\d+)", orig_q)
                is_current_loc = any(w in orig_q.lower() for w in ["current location", "my location", "here", "gps"])
                
                if m_coord:
                    u_lat, u_lon = float(m_coord.group(1)), float(m_coord.group(2))
                    res = routing_svc.search_route_from_location(
                        user_lat=u_lat,
                        user_lon=u_lon,
                        destination_query=dest_q,
                        departure_time_str=req_dep_time,
                        max_transfers=2,
                        max_results=2
                    )
                elif is_current_loc:
                    # Default GPS to Kawaguchiko central tourism hub
                    res = routing_svc.search_route_from_location(
                        user_lat=35.4981,
                        user_lon=138.7690,
                        destination_query=dest_q,
                        departure_time_str=req_dep_time,
                        max_transfers=2,
                        max_results=2
                    )
                else:
                    req = RouteSearchRequest(
                        origin=orig_q,
                        destination=dest_q,
                        departure_time=req_dep_time,
                        max_transfers=2,
                        max_results=2
                    )
                    res = routing_svc.search_routes(req)

                if res.journeys:
                    state["identified_journeys"] = [j.model_dump() for j in res.journeys]
                    transit_context = (
                        "\n\nVERIFIED PUBLIC TRANSPORT ROUTING (Calculated deterministically by RAPTOR engine):\n"
                        f"- Origin: {res.origin.stop_name_ja} ({res.origin.stop_name_en})\n"
                        f"- Destination: {res.destination.stop_name_ja} ({res.destination.stop_name_en})\n"
                    )
                    for j_idx, j in enumerate(res.journeys, start=1):
                        transit_context += (
                            f"\nJourney Option {j_idx}: Depart {j.departure_time} -> Arrive {j.arrival_time} "
                            f"(Duration: {j.total_duration_minutes} min, Transfers: {j.transfers_count}, "
                            f"Total Fare: {j.total_fare_jpy} JPY):\n"
                        )
                        for l_idx, leg in enumerate(j.legs, start=1):
                            transit_context += (
                                f"  * Leg {l_idx}: [{leg.mode.upper()}] {leg.operator} {leg.route_short_name} "
                                f"(Color: {leg.route_color}, Line: {leg.route_long_name})\n"
                                f"    - Board: {leg.origin_stop_name_en} ({leg.origin_stop_name}) at {leg.departure_time}\n"
                                f"    - Alight: {leg.destination_stop_name_en} ({leg.destination_stop_name}) at {leg.arrival_time}\n"
                                f"    - Duration: {leg.duration_minutes} min ({leg.intermediate_stops_count} intermediate stops)\n"
                                f"    - Fare: {leg.fare_jpy} JPY | Data Source: {leg.provenance_badge}\n"
                            )
            except Exception as e:
                logger.warning(f"Transit routing query error: {e}")

        # 5. CrowdSense Alternative Recommendations
        crowd_info = extract_crowd_query(user_message)
        crowd_context = ""
        state["identified_crowd_alternatives"] = []
        if crowd_info:
            target_name, pref = crowd_info
            target_pid = self.resolve_place_id(target_name)
            scen = "high"
            try:
                crowd_req = CrowdRecommendationRequest(
                    place_id=target_pid,
                    preference=pref,
                    scenario=scen,
                    limit=3
                )
                crowd_res = recommendation_service.get_recommendations(crowd_req)
                if crowd_res.alternatives:
                    state["identified_crowd_alternatives"] = [a.model_dump() for a in crowd_res.alternatives]
                    crowd_context = (
                        f"\n\nCROWDSENSE ADAPTIVE RECOMMENDATIONS (Scenario: {scen.upper()}, Preference: {pref}):\n"
                        f"Target Attraction: {crowd_res.current_place_name} ({crowd_res.current_crowd_level.upper()} crowd level).\n"
                    )
                    for alt in crowd_res.alternatives:
                        crowd_context += (
                            f"- Alternative: {alt.name_en} ({alt.name_ja}): Crowd Reduction: -{alt.crowd_reduction_percent}%, "
                            f"Fuji Rating: {alt.fuji_view_rating}/5, Distance: {alt.distance_km} km. "
                            f"Why: {alt.recommendation_reason}\n"
                        )
            except Exception as e:
                logger.warning(f"Crowd recommendation error: {e}")

        # 6. RAG Regional Knowledge Retrieval
        rag_chunks = rag_retriever.retrieve(user_message, top_k=2)
        rag_context = rag_retriever.format_grounding_context(rag_chunks)

        # 7. Weather & Seasonal Climate Data (if weather asked)
        weather_context = ""
        if any(w in lower_msg for w in ["weather", "temperature", "winter", "pack", "december", "rain", "climate", "season"]):
            # Extract month if mentioned
            m_month = re.search(r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\b", lower_msg)
            month_num = None
            if m_month:
                months_map = {"january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
                              "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12}
                month_num = months_map.get(m_month.group(1))
            w_data = get_weather_info(month_num)
            weather_context = (
                f"\n\nVERIFIED REGIONAL WEATHER & CLIMATE ({w_data['region']}, Month: {w_data['month']}):\n"
                f"- Temperature: {w_data['temperature_range_celsius']}\n"
                f"- Mount Fuji Visibility Probability: {w_data['fuji_visibility_probability']}\n"
                f"- Summary: {w_data['weather_summary']}\n"
                f"- Packing Advice: {w_data['packing_recommendations']}\n"
                f"- Source: {w_data['data_source']}\n"
            )

        # 8. Official Fujikyu Pass and JR Pass Advisories
        pass_context = ""
        if any(w in lower_msg for w in ["jr pass", "japan rail pass", "pass", "ticket", "cost", "how much", "fare"]):
            pass_context = (
                "\n\nOFFICIAL FUJIKYU PASS & FARE INTELLIGENCE:\n"
                "- JAPAN RAIL PASS (JR PASS) EXCLUSION: The Japan Rail Pass does NOT cover the private Fujikyu Railway line "
                "(Otsuki to Kawaguchiko / ¥1,170 one-way) or Fujikyu Sightseeing Buses. JR Pass holders must purchase separate tickets or a Fujikyu Pass.\n"
                "- Kawaguchiko, Saiko & Motosuko Sightseeing Bus Pass: 1-Day unlimited rides on Red, Green, Blue lines (Adult ¥1,500, Child ¥750).\n"
                "- Fujikko-go Sightseeing Bus Pass: 1-Day loop around Oshino Hakkai & Yamanakako (Adult ¥1,800, Child ¥900).\n"
                "- Mount Fuji & Fuji Five Lakes Passport: 2-Day Bus Pass is ¥3,300 (Child ¥1,650); with Fujikyu Railway Set is ¥4,700 (Child ¥2,350).\n"
            )

        # 9. Grounded Places Formatting
        grounding_places_text = ""
        if grounded_places:
            grounding_places_text = "\n\nVERIFIED DATABASE PLACES TO RECOMMEND (Ground all specifics here):\n"
            for p in grounded_places:
                grounding_places_text += (
                    f"- {p['name_ja']} ({p['name_en']}): Category={p['primary_category']}, "
                    f"Fuji Rating={p['fuji_view_rating']}/5, "
                    f"Hours={p['opening_hours_text']}, "
                    f"Admission={p['general_admission_type']} ({p.get('general_admission_fee_jpy', 0)} JPY), "
                    f"Access={p['accessibility_status']} ({p.get('accessibility_evidence')}, Steps: {p.get('stair_step_count')})\n"
                )

        # 10. Active UI State Context Grounding
        ui_context_text = ""
        if context:
            st = context.get("start_station") or context.get("start_location")
            tm = context.get("travel_mode")
            dest = context.get("destination") or context.get("selected_destination")
            step = context.get("active_workflow_step")
            hrs = context.get("time_budget_hours")
            ui_parts = []
            if st:
                ui_parts.append(f"Starting Hub: {st}")
            if tm:
                ui_parts.append(f"Selected Travel Mode: {tm}")
            if dest:
                ui_parts.append(f"Target Destination: {dest}")
            if hrs:
                ui_parts.append(f"Available Time Budget: {hrs} hours")
            if step:
                ui_parts.append(f"Current Screen: {step}")
            if ui_parts:
                ui_context_text = (
                    "\n\nTRAVELLER ACTIVE APP CONTEXT (The user is looking at this screen in FujiNova right now):\n"
                    + "\n".join(f"- {p}" for p in ui_parts)
                    + "\nGround your recommendations to their current starting hub, travel mode, and destination.\n"
                )

        full_system_prompt = (
            HANA_SYSTEM_INSTRUCTION
            + ui_context_text
            + rag_context
            + weather_context
            + grounding_places_text
            + transit_context
            + crowd_context
            + itinerary_context
            + pass_context
        )

        prompt_messages = [{"role": "system", "content": full_system_prompt}]
        # Window of recent conversation history
        recent_turns = session_manager.get_context_messages(session_id)
        if recent_turns:
            prompt_messages.extend(recent_turns)
        else:
            prompt_messages.extend(state["messages"][-6:])

        full_response = []
        try:
            async for token in self.router.stream_chat(
                messages=prompt_messages,
                system_instruction=full_system_prompt
            ):
                full_response.append(token)
                yield token

        except Exception as llm_err:
            logger.error(f"Primary LLM streaming error: {llm_err}")

            # Grounded fallback only when specific tools were explicitly requested
            if is_itinerary_request and state.get("active_itinerary"):
                plan = state["active_itinerary"]
                lines = [f"I have prepared your {plan['total_days']}-day itinerary for Mount Fuji and the Fuji Five Lakes:\n\n"]
                for d in plan["days"]:
                    lines.append(f"**Day {d['day_number']}: {d['title']}**\n")
                    for s in d["stops"]:
                        lines.append(f"- **{s['name_en']} ({s['name_ja']})** at {s['estimated_arrival']} — {s['admission_info']}. Fuji View: ★{s['fuji_view_rating']}/5.\n")
                lines.append("\nYou can view the full route and modify stops in the Journey panel.")
                fallback_msg = "".join(lines)
            elif transit_info and state.get("identified_journeys"):
                j = state["identified_journeys"][0]
                first_leg = j.get("legs", [{}])[0]
                op = first_leg.get("operator", "Bus")
                r_num = first_leg.get("route_short_name", "")
                r_name = first_leg.get("route_long_name", "")
                b_stop = f"{first_leg.get('origin_stop_name_en', '')} ({first_leg.get('origin_stop_name', '')})"
                d_time = first_leg.get("departure_time", "")
                a_stop = f"{first_leg.get('destination_stop_name_en', '')} ({first_leg.get('destination_stop_name', '')})"
                a_time = first_leg.get("arrival_time", "")
                dur = j.get("total_duration_minutes", 0)
                fare = j.get("total_fare_jpy", 0)
                fallback_msg = (
                    f"According to the official Fujikyu GTFS timetable, you can take the {op} (Route {r_num}: {r_name}).\n\n"
                    f"- **Board:** {b_stop} at **{d_time}**\n"
                    f"- **Alight:** {a_stop} at **{a_time}**\n"
                    f"- **Duration:** {dur} minutes\n"
                    f"- **Fare:** {fare} JPY\n\n"
                    f"The full connection details are displayed in the transit card below."
                )
            elif crowd_info and state.get("identified_crowd_alternatives"):
                alts = state["identified_crowd_alternatives"]
                alt_lines = ["Based on our CrowdSense simulation, here are quieter, high-rating alternatives to consider:\n\n"]
                for a in alts:
                    alt_lines.append(f"- **{a['name_en']} ({a['name_ja']})**: **-{a['crowd_reduction_percent']}% crowd reduction**. {a['recommendation_reason']}\n")
                alt_lines.append("\nYou can compare them directly or adapt your itinerary in the dashboard.")
                fallback_msg = "".join(alt_lines)
            elif any(w in lower_msg for w in ["weather", "temperature", "winter", "pack", "december", "rain", "climate", "season"]) and weather_context:
                w_info = get_weather_info()
                fallback_msg = (
                    f"**Weather & Climate for Mount Fuji & Kawaguchiko ({w_info['month']}):**\n\n"
                    f"- **Temperature:** {w_info['temperature_range_celsius']}\n"
                    f"- **Fuji Visibility:** {w_info['fuji_visibility_probability']}\n"
                    f"- **Conditions:** {w_info['weather_summary']}\n"
                    f"- **What to Pack:** {w_info['packing_recommendations']}\n\n"
                    f"*(Source: {w_info['data_source']})*"
                )
            else:
                fallback_msg = (
                    f"I apologize, but I encountered an error communicating with the AI service: {str(llm_err)}. "
                    "Please check your API key configuration in .env and verify that your Gemini API key is valid."
                )

            # Stream words with slight delay pacing
            for word in fallback_msg.split(" "):
                yield word + " "
                full_response.append(word + " ")

        final_content = "".join(full_response)
        state["messages"].append({"role": "model", "content": final_content})
        session_manager.add_message(session_id, "assistant", final_content)


# Global Hana agent singleton
agent = HanaAgent()
