"""Tests for Model Router, Retries, Policy Gates, and Failover (Acceptance Tests T1-04 through T1-10)."""
import pytest
import asyncio
from typing import AsyncIterator, List, Dict, Type
from pydantic import BaseModel, Field

from backend.app.core.config import settings
from backend.app.services.llm.base import (
    BaseLLMAdapter,
    AuthenticationError,
    RateLimitError,
    ServerError,
    TimeoutError,
    JSONSchemaValidationError,
    FailoverPolicyViolationError
)
from backend.app.services.llm.router import ModelRouter
from backend.app.services.llm.gemini_adapter import clean_json_markdown


class SampleOutput(BaseModel):
    summary: str
    items: List[str] = Field(default_factory=list)


class MockLLMAdapter(BaseLLMAdapter):
    """Configurable mock adapter for deterministic test scenarios."""

    def __init__(self, name: str = "mock"):
        self.name = name
        self.stream_calls = 0
        self.structured_calls = 0
        self.stream_side_effects = []
        self.structured_side_effects = []

    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str,
        temperature: float = None,
        timeout: float = None
    ) -> AsyncIterator[str]:
        self.stream_calls += 1
        if self.stream_side_effects:
            effect = self.stream_side_effects.pop(0)
            if isinstance(effect, Exception):
                raise effect
            for token in effect:
                yield token
        else:
            yield f"Response from {self.name}"

    async def generate_structured(
        self,
        messages: List[Dict[str, str]],
        response_model: Type[SampleOutput],
        system_instruction: str,
        temperature: float = None,
        timeout: float = None
    ) -> SampleOutput:
        self.structured_calls += 1
        if self.structured_side_effects:
            effect = self.structured_side_effects.pop(0)
            if isinstance(effect, Exception):
                raise effect
            return effect
        return response_model(summary=f"Parsed by {self.name}", items=["item1"])


@pytest.mark.asyncio
async def test_t1_04_rate_limit_retry_with_backoff():
    """T1-04: HTTP 429 Rate Limit triggers retries with exponential backoff on primary."""
    primary = MockLLMAdapter("primary")
    fallback = MockLLMAdapter("fallback")

    # Primary fails with RateLimitError twice, then succeeds on 3rd attempt
    primary.stream_side_effects = [
        RateLimitError("429 Quota exhausted"),
        RateLimitError("429 Quota exhausted"),
        ["Success", " ", "after", " ", "backoff"]
    ]

    router = ModelRouter(
        primary_adapter=primary,
        fallback_adapter=fallback,
        max_retries=2,
        backoff_base=0.01  # Fast backoff for unit tests
    )

    tokens = []
    async for t in router.stream_chat(
        messages=[{"role": "user", "content": "Hello"}],
        system_instruction="Be helpful"
    ):
        tokens.append(t)

    assert "".join(tokens) == "Success after backoff"
    assert primary.stream_calls == 3
    assert fallback.stream_calls == 0  # Primary recovered, no fallback used


@pytest.mark.asyncio
async def test_t1_05_server_error_and_failover_when_authorized(monkeypatch):
    """T1-05: HTTP 500/503 Service Unavailable retries and fails over to secondary when authorized."""
    monkeypatch.setattr(settings, "ENABLE_OPENAI_FALLBACK", True)
    monkeypatch.setattr(settings, "ALLOW_MULTI_VENDOR_FAILOVER", True)

    primary = MockLLMAdapter("primary")
    fallback = MockLLMAdapter("fallback")

    # Primary persistently fails with 500 ServerError
    primary.stream_side_effects = [
        ServerError("500 Internal Server Error"),
        ServerError("503 Service Unavailable"),
        ServerError("500 Internal Server Error")
    ]
    fallback.stream_side_effects = [["Fallback", " ", "response"]]

    router = ModelRouter(
        primary_adapter=primary,
        fallback_adapter=fallback,
        max_retries=2,
        backoff_base=0.01
    )

    tokens = []
    async for t in router.stream_chat(
        messages=[{"role": "user", "content": "Test"}],
        system_instruction="System"
    ):
        tokens.append(t)

    assert "".join(tokens) == "Fallback response"
    assert primary.stream_calls == 3
    assert fallback.stream_calls == 1


@pytest.mark.asyncio
async def test_t1_06_timeout_handled_cleanly():
    """T1-06: Timeout (> 12.0s or simulated TimeoutError) triggers retry and clean handling."""
    primary = MockLLMAdapter("primary")
    fallback = MockLLMAdapter("fallback")

    # Attempt 1 times out, attempt 2 succeeds
    primary.stream_side_effects = [
        TimeoutError("Call exceeded timeout threshold 12.0s"),
        ["Completed", " ", "promptly"]
    ]

    router = ModelRouter(
        primary_adapter=primary,
        fallback_adapter=fallback,
        max_retries=1,
        backoff_base=0.01
    )

    tokens = []
    async for t in router.stream_chat(
        messages=[{"role": "user", "content": "Fast query"}],
        system_instruction="System"
    ):
        tokens.append(t)

    assert "".join(tokens) == "Completed promptly"
    assert primary.stream_calls == 2


@pytest.mark.asyncio
async def test_t1_07_invalid_api_key_fails_immediately():
    """T1-07: Invalid API Key / 401/403 fails immediately without futile retries."""
    primary = MockLLMAdapter("primary")
    fallback = MockLLMAdapter("fallback")

    primary.stream_side_effects = [
        AuthenticationError("API_KEY_INVALID: 403 Forbidden")
    ]

    router = ModelRouter(
        primary_adapter=primary,
        fallback_adapter=fallback,
        max_retries=3,
        backoff_base=0.01
    )

    with pytest.raises(AuthenticationError) as exc_info:
        async for _ in router.stream_chat(
            messages=[{"role": "user", "content": "Hello"}],
            system_instruction="System"
        ):
            pass

    assert "API_KEY_INVALID" in str(exc_info.value)
    # Must NOT retry invalid key! Call count must be exactly 1
    assert primary.stream_calls == 1
    assert fallback.stream_calls == 0


def test_t1_08_malformed_json_markdown_cleaning():
    """T1-08: Malformed or markdown-wrapped JSON is cleaned and repaired."""
    markdown_wrapped = "```json\n{\"summary\": \"Cleaned\", \"items\": [\"a\", \"b\"]}\n```"
    cleaned = clean_json_markdown(markdown_wrapped)
    obj = SampleOutput.model_validate_json(cleaned)
    assert obj.summary == "Cleaned"
    assert obj.items == ["a", "b"]

    # Trailing prose wrapping
    prose_wrapped = "Here is the result:\n```\n{\"summary\": \"ProseWrapped\"}\n```\nHope that helps!"
    cleaned_prose = clean_json_markdown(prose_wrapped)
    obj_prose = SampleOutput.model_validate_json(cleaned_prose)
    assert obj_prose.summary == "ProseWrapped"


@pytest.mark.asyncio
async def test_t1_09_failover_policy_gate_blocks_cross_vendor(monkeypatch):
    """T1-09: Cross-vendor failover is strictly BLOCKED when policy flags are False."""
    # Explicitly ensure flags are False (the FujiNova default)
    monkeypatch.setattr(settings, "ENABLE_OPENAI_FALLBACK", False)
    monkeypatch.setattr(settings, "ALLOW_MULTI_VENDOR_FAILOVER", False)

    primary = MockLLMAdapter("primary")
    fallback = MockLLMAdapter("fallback")

    primary.stream_side_effects = [
        ServerError("500 Server Error"),
        ServerError("500 Server Error")
    ]

    router = ModelRouter(
        primary_adapter=primary,
        fallback_adapter=fallback,
        max_retries=1,
        backoff_base=0.01
    )

    with pytest.raises(FailoverPolicyViolationError) as exc_info:
        async for _ in router.stream_chat(
            messages=[{"role": "user", "content": "Sensitive tourism query"}],
            system_instruction="System"
        ):
            pass

    assert "disabled by policy" in str(exc_info.value)
    assert primary.stream_calls == 2
    # Ensure fallback was NEVER called, zero data egress to OpenAI
    assert fallback.stream_calls == 0


@pytest.mark.asyncio
async def test_t1_10_state_preservation_across_failover(monkeypatch):
    """T1-10: Structured extraction preserves input messages and state across failover."""
    monkeypatch.setattr(settings, "ENABLE_OPENAI_FALLBACK", True)
    monkeypatch.setattr(settings, "ALLOW_MULTI_VENDOR_FAILOVER", True)

    primary = MockLLMAdapter("primary")
    fallback = MockLLMAdapter("fallback")

    primary.structured_side_effects = [
        ServerError("500 Down")
    ]
    expected_output = SampleOutput(summary="State Preserved Across Failover", items=["loc_a", "loc_b"])
    fallback.structured_side_effects = [expected_output]

    router = ModelRouter(
        primary_adapter=primary,
        fallback_adapter=fallback,
        max_retries=0,
        backoff_base=0.01
    )

    messages = [
        {"role": "user", "content": "I am traveling with a wheelchair and love nature."}
    ]

    result = await router.extract_structured(
        messages=messages,
        response_model=SampleOutput,
        system_instruction="Extract profile"
    )

    assert result.summary == "State Preserved Across Failover"
    assert result.items == ["loc_a", "loc_b"]
    assert primary.structured_calls == 1
    assert fallback.structured_calls == 1
