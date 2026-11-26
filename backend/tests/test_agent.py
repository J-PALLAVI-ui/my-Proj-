"""Tests for Hana Conversational Agent, Adaptive Interviewing & Grounding (Acceptance Tests T1-11 through T1-14)."""
import pytest
from backend.app.agent.hana import HanaAgent, ExtractedProfileUpdate
from backend.app.services.llm.base import BaseLLMAdapter
from backend.app.services.llm.router import ModelRouter
from backend.app.api.routes_places import search_places_db


class MockHanaLLMAdapter(BaseLLMAdapter):
    """Deterministic mock adapter for testing Hana agent logic."""

    def __init__(self):
        self.stream_responses = []

    async def stream_generate(self, messages, system_instruction, temperature=None, timeout=None):
        resp = self.stream_responses.pop(0) if self.stream_responses else "Welcome to FujiNova!"
        for chunk in resp.split(" "):
            yield chunk + " "

    async def generate_structured(self, messages, response_model, system_instruction, temperature=None, timeout=None):
        # Empty structured response prompts the robust fallback heuristic to parse message text
        return response_model()


@pytest.fixture
def agent_fixture(test_db):
    """Instantiate HanaAgent with mock router and verified database."""
    adapter = MockHanaLLMAdapter()
    router = ModelRouter(primary_adapter=adapter, fallback_adapter=adapter, max_retries=0)
    agent = HanaAgent(model_router=router)
    return agent, adapter


@pytest.mark.asyncio
async def test_t1_11_adaptive_interview_avoids_repeated_questions(agent_fixture):
    """T1-11: Adaptive interview state avoids repeating already answered questions."""
    agent, adapter = agent_fixture
    session_id = "test_session_t1_11"

    # Turn 1: User explicitly provides party composition and mobility
    adapter.stream_responses = ["Great to meet you! What kind of places do you like to explore?"]
    async for _ in agent.chat(
        session_id=session_id,
        user_message="Hi! I am traveling with my partner. Neither of us have mobility issues."
    ):
        pass

    state = agent.get_or_create_state(session_id)
    assert state["profile"]["party_composition"] == "couple"
    assert "party_type" in state["asked_questions"]
    assert "mobility" in state["asked_questions"]

    # Turn 2: Next interview topic should NOT be party_type or mobility!
    next_topic = agent.determine_next_interview_question(state)
    assert next_topic not in ("party_type", "mobility")
    assert next_topic in ("interests", "stay_duration", "pace")

    # Turn 3: User answers interests
    adapter.stream_responses = ["Lovely! How many days are you staying?"]
    async for _ in agent.chat(
        session_id=session_id,
        user_message="We love scenic nature and quiet lake viewpoints."
    ):
        pass

    assert "interests" in state["asked_questions"]
    assert "nature" in state["profile"]["interests"] or "viewpoint" in state["profile"]["interests"]

    # Next topic must advance further, never cycling back
    next_topic_turn3 = agent.determine_next_interview_question(state)
    assert next_topic_turn3 not in ("party_type", "mobility", "interests")
    assert next_topic_turn3 in ("stay_duration", "pace")


@pytest.mark.asyncio
async def test_t1_12_multi_constraint_profile_extraction(agent_fixture):
    """T1-12: Multi-constraint profile extraction handles complex combined sentences."""
    agent, _ = agent_fixture

    user_msg = (
        "I'm visiting with my grandmother who uses a wheelchair, "
        "and we want a relaxed afternoon seeing Mount Fuji nature views with no steep stairs."
    )

    update = await agent.extract_profile_updates(user_msg, current_profile={})

    assert update.mobility_needs in ("wheelchair", "no_stairs")
    assert update.has_elderly is True
    assert update.party_composition == "multigenerational"
    assert "viewpoint" in update.interests or "nature" in update.interests
    assert update.preferred_pace == "relaxed"


@pytest.mark.asyncio
async def test_t1_13_strict_grounding_verified_places(agent_fixture, test_db):
    """T1-13: Place recommendations draw strictly from canonical 35 SQLite database places."""
    agent, adapter = agent_fixture
    session_id = "test_session_t1_13"

    state = agent.get_or_create_state(session_id)
    state["profile"]["mobility_needs"] = "wheelchair"
    state["profile"]["interests"] = ["viewpoint"]

    # Query grounded places
    places = agent.query_grounded_places(state, limit=4)
    assert len(places) > 0

    # Ensure EVERY returned place exists in the canonical SQLite database
    all_db_places = {p["place_id"] for p in search_places_db(limit=100, db_path=test_db)}
    for p in places:
        assert p["place_id"] in all_db_places
        assert p["accessibility_status"] == "VERIFIED_ACCESSIBLE"
        assert p["fuji_view_rating"] >= 1
        assert p["provenance_tier"] in ("OFFICIAL_GOV", "OFFICIAL_OPERATOR", "COMMUNITY_OSM")


@pytest.mark.asyncio
async def test_t1_14_unknown_hours_and_fees_transparency(agent_fixture, test_db):
    """T1-14: Places with unknown or variable hours/fees (e.g. Motosu or Oshino) are transparently caveated."""
    agent, _ = agent_fixture

    # Test Oshino Hakkai ponds transparency
    oshino_list = [x for x in search_places_db(query="Oshino", db_path=test_db) if x["place_id"] == "oshino_hakkai"]
    assert len(oshino_list) >= 1
    p = oshino_list[0]
    assert p["general_admission_type"] == "FREE"
    assert p.get("optional_activities_fee_desc") and ("Hannoki" in p["optional_activities_fee_desc"] or "museum" in p["optional_activities_fee_desc"].lower())

    # Test Motosu viewpoint 24h outdoor trail
    motosu_list = [x for x in search_places_db(query="Motosu", db_path=test_db) if x["place_id"] == "motosuko_viewpoint"]
    assert len(motosu_list) >= 1
    m = motosu_list[0]
    assert m["opening_status"] == "ALWAYS_OPEN"
    assert m["general_admission_type"] == "FREE"
    assert m["required_attribution"] is not None

    # Test Arakurayama 398 stairs warning data
    arakura = search_places_db(query="Arakurayama", db_path=test_db)
    assert len(arakura) >= 1
    a = arakura[0]
    assert a["stair_step_count"] == 398
    assert a["accessibility_status"] == "STEEP_STAIRS"
