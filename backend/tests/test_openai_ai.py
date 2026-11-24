"""Tests for FujiNova Real AI Integration, General AI Assistant, RAG, and Live Services."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.app.agent.hana import HanaAgent
from backend.app.services.rag.retriever import rag_retriever
from backend.app.services.live_info.weather_service import get_weather_info
from backend.app.services.live_info.advisory_service import get_current_advisories
from backend.app.services.itinerary.itinerary_service import generate_itinerary, modify_itinerary
from backend.app.services.conversation.session_manager import session_manager
from backend.app.services.llm.openai_adapter import OpenAIAdapter
from backend.app.services.llm.base import BaseLLMAdapter
from backend.app.services.llm.router import ModelRouter


class MockEchoLLMAdapter(BaseLLMAdapter):
    """Echo adapter simulating real LLM streaming for testing."""

    def __init__(self, canned_response="I am Hana, your AI travel companion."):
        self.canned_response = canned_response

    async def stream_generate(self, messages, system_instruction, temperature=None, timeout=None):
        for token in self.canned_response.split(" "):
            yield token + " "

    async def generate_structured(self, messages, response_model, system_instruction, temperature=None, timeout=None):
        return response_model()


@pytest.fixture
def mock_agent():
    adapter = MockEchoLLMAdapter(canned_response="Machine learning is broad, whereas deep learning uses deep neural networks.")
    router = ModelRouter(primary_adapter=adapter, fallback_adapter=adapter, max_retries=0)
    agent = HanaAgent(model_router=router)
    return agent


@pytest.mark.asyncio
async def test_general_query_answering_no_forced_travel(mock_agent):
    """Hana must answer general queries (ML vs DL) directly without forcing into travel itineraries."""
    session_id = "test_general_ai_01"
    response_tokens = []
    async for token in mock_agent.chat(
        session_id=session_id,
        user_message="What is the difference between machine learning and deep learning?"
    ):
        response_tokens.append(token)
    
    full_text = "".join(response_tokens)
    assert "Machine learning" in full_text or "neural" in full_text
    # Ensure it didn't generate a travel itinerary for this pure CS question
    state = mock_agent.get_or_create_state(session_id)
    assert state.get("active_itinerary") is None


def test_rag_regional_knowledge_retrieval():
    """RAG retriever should retrieve relevant chunks for Five Lakes & UNESCO history."""
    chunks = rag_retriever.retrieve("Mount Fuji UNESCO World Heritage, geology and history", top_k=3)
    assert len(chunks) > 0
    assert any("UNESCO" in c["title"] or "Geology" in c["title"] or "UNESCO" in c["content"] for c in chunks)
    
    formatted = rag_retriever.format_grounding_context(chunks)
    assert "REGIONAL KNOWLEDGE" in formatted
    assert chunks[0]["attribution"] in formatted


def test_project_code_rag_retrieval():
    """RAG retriever should retrieve relevant codebase architecture and RAPTOR algorithm chunks."""
    tech_chunks = rag_retriever.retrieve("Explain RAPTOR public transit algorithm in FujiNova", top_k=2)
    assert len(tech_chunks) > 0
    assert any("RAPTOR" in c["title"] or "GTFS" in c["content"] for c in tech_chunks)


def test_live_weather_and_visibility():
    """Weather service returns verified climate and visibility likelihood."""
    dec_weather = get_weather_info(month=12)
    assert dec_weather["month"] == "December"
    assert "fuji_visibility_probability" in dec_weather
    assert "temperature_range_celsius" in dec_weather
    assert "packing_recommendations" in dec_weather
    assert "77%" in dec_weather["fuji_visibility_probability"]


def test_live_advisories():
    """Advisory service returns seasonal warnings and transit passes."""
    advisories = get_current_advisories()
    assert len(advisories) >= 2
    assert any("Summit" in a["title"] or "Winter" in a["title"] for a in advisories)


def test_multi_day_itinerary_generation_and_modification():
    """Itinerary service generates multi-day plan and allows dynamic edits."""
    plan = generate_itinerary(
        party_type="family",
        duration_days=2,
        mobility_needs="none",
        interests=["viewpoint", "nature"],
        budget_tier="standard",
        pace="moderate"
    )
    assert plan.total_days == 2
    assert len(plan.days) == 2
    day1_stops_before = len(plan.days[0].stops)
    assert day1_stops_before >= 2
    
    # Modify: Remove a stop
    updated = modify_itinerary(plan, action="remove_stop", target=1)
    assert len(updated.days[0].stops) == day1_stops_before - 1
    
    # Modify: Make cheaper
    cheaper = modify_itinerary(plan, action="make_cheaper")
    assert cheaper.plan_id == plan.plan_id


def test_conversation_session_manager():
    """Multi-turn memory preserves context messages and clears cleanly."""
    sid = "test_memory_session_99"
    session_manager.clear_session(sid)
    
    session_manager.add_message(sid, "user", "Hello Hana")
    session_manager.add_message(sid, "assistant", "Konnichiwa! How can I help?")
    session_manager.add_message(sid, "user", "I want to visit Lake Motosu.")
    
    msgs = session_manager.get_context_messages(sid)
    assert len(msgs) == 3
    assert msgs[0]["content"] == "Hello Hana"
    assert msgs[2]["content"] == "I want to visit Lake Motosu."
    
    # Clear session
    session_manager.clear_session(sid)
    assert len(session_manager.get_context_messages(sid)) == 0


def test_openai_adapter_configuration():
    """OpenAI Adapter loads environment settings correctly and validates parameters."""
    adapter = OpenAIAdapter(api_key="test-key-placeholder", model="gpt-4o-mini")
    assert adapter.api_key == "test-key-placeholder"
    assert adapter.model == "gpt-4o-mini"
    assert adapter.max_output_tokens >= 500
