"""FujiNova Gemini LLM Adapter (google-genai SDK)."""
import json
import re
import asyncio
from typing import AsyncIterator, List, Dict, Any, Type, TypeVar, Optional
from pydantic import BaseModel, ValidationError
from google import genai
from google.genai import types
from google.genai.errors import APIError

from backend.app.core.config import settings
from backend.app.services.llm.base import (
    BaseLLMAdapter,
    AuthenticationError,
    RateLimitError,
    ServerError,
    TimeoutError,
    JSONSchemaValidationError,
    LLMError
)

T = TypeVar("T", bound=BaseModel)


def clean_json_markdown(text: str) -> str:
    """Strip markdown code fence wrappers from JSON string."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    return text


class GeminiAdapter(BaseLLMAdapter):
    """Gemini Adapter using the official google-genai SDK."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL or settings.FUJINOVA_PRIMARY_MODEL or "gemini-flash-lite-latest"
        self._client: Optional[genai.Client] = None

    def _get_client(self) -> genai.Client:
        if not self.api_key or self.api_key.strip() in ("", "YOUR_GOOGLE_AI_STUDIO_KEY"):
            raise AuthenticationError("GEMINI_API_KEY is not configured or is a placeholder.")
        if not self._client:
            self._client = genai.Client(api_key=self.api_key, http_options={"api_version": "v1beta"})
        return self._client

    def _format_contents(self, messages: List[Dict[str, str]]) -> List[types.Content]:
        """Convert standard message dicts to Gemini Content objects."""
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])]
                )
            )
        return contents

    def _map_api_error(self, e: Exception) -> LLMError:
        """Map provider errors to unified FujiNova error taxonomy."""
        if isinstance(e, (AuthenticationError, RateLimitError, ServerError, TimeoutError, LLMError)):
            return e
        if isinstance(e, APIError):
            code = getattr(e, "code", None)
            msg = str(e)
            if code in (401, 403) or "API_KEY_INVALID" in msg:
                return AuthenticationError(f"Gemini authentication failed: {msg}")
            if code == 429 or "RESOURCE_EXHAUSTED" in msg:
                return RateLimitError(f"Gemini rate limit exceeded: {msg}")
            if code and code >= 500:
                return ServerError(f"Gemini server error: {msg}", status_code=code)
        if isinstance(e, (asyncio.TimeoutError, TimeoutError)):
            return TimeoutError(f"Gemini request timed out: {str(e)}")
        return LLMError(f"Gemini invocation error: {str(e)}", retryable=False)

    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str,
        temperature: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> AsyncIterator[str]:
        """Stream conversational responses from Gemini."""
        client = self._get_client()
        temp = temperature if temperature is not None else settings.FUJINOVA_TEMPERATURE
        tout = timeout if timeout is not None else settings.FUJINOVA_TIMEOUT_SECONDS

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temp
        )
        contents = self._format_contents(messages)

        try:
            async def _stream():
                stream = await client.aio.models.generate_content_stream(
                    model=self.model,
                    contents=contents,
                    config=config
                )
                async for chunk in stream:
                    if chunk.text:
                        yield chunk.text

            async with asyncio.timeout(tout):
                async for token in _stream():
                    yield token

        except Exception as e:
            raise self._map_api_error(e)

    async def generate_structured(
        self,
        messages: List[Dict[str, str]],
        response_model: Type[T],
        system_instruction: str,
        temperature: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> T:
        """Generate typed structured output conforming to a Pydantic model."""
        client = self._get_client()
        temp = temperature if temperature is not None else settings.FUJINOVA_TEMPERATURE
        tout = timeout if timeout is not None else settings.FUJINOVA_TIMEOUT_SECONDS

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temp,
            response_mime_type="application/json",
            response_schema=response_model
        )
        contents = self._format_contents(messages)

        try:
            async with asyncio.timeout(tout):
                response = await client.aio.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=config
                )

            raw_text = response.text or "{}"
            cleaned_text = clean_json_markdown(raw_text)

            try:
                return response_model.model_validate_json(cleaned_text)
            except (ValidationError, json.JSONDecodeError) as parse_err:
                # Attempt repair: search for outermost JSON object
                json_match = re.search(r"(\{.*\})", cleaned_text, re.DOTALL)
                if json_match:
                    try:
                        return response_model.model_validate_json(json_match.group(1))
                    except Exception:
                        pass
                raise JSONSchemaValidationError(
                    f"Failed to validate response against {response_model.__name__}: {str(parse_err)}. Raw text: {raw_text}"
                )

        except Exception as e:
            if isinstance(e, JSONSchemaValidationError):
                raise
            raise self._map_api_error(e)
