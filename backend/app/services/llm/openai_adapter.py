"""FujiNova OpenAI Official SDK Adapter (Modern AsyncOpenAI)."""
import json
import re
import asyncio
import logging
from typing import AsyncIterator, List, Dict, Any, Type, TypeVar, Optional
from pydantic import BaseModel, ValidationError
import openai
from openai import AsyncOpenAI

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
from backend.app.services.llm.gemini_adapter import clean_json_markdown

logger = logging.getLogger("fujinova.llm.openai")
T = TypeVar("T", bound=BaseModel)


class OpenAIAdapter(BaseLLMAdapter):
    """OpenAI Adapter using the official AsyncOpenAI SDK with streaming and structured generation."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.effective_openai_model
        self.max_output_tokens = settings.OPENAI_MAX_OUTPUT_TOKENS
        self._client: Optional[AsyncOpenAI] = None

    def _get_client(self) -> AsyncOpenAI:
        key = self.api_key or settings.OPENAI_API_KEY
        if not key or key.strip() in ("", "YOUR_OPENAI_API_KEY", "your_api_key_here"):
            raise AuthenticationError("OPENAI_API_KEY is not configured or contains placeholder text.")
        if not self._client:
            self._client = AsyncOpenAI(api_key=key.strip())
        return self._client

    def _map_api_error(self, e: Exception) -> LLMError:
        """Map OpenAI exceptions to unified FujiNova error taxonomy."""
        if isinstance(e, (AuthenticationError, RateLimitError, ServerError, TimeoutError, LLMError)):
            return e
        if isinstance(e, openai.AuthenticationError):
            return AuthenticationError(f"OpenAI authentication failed: {str(e)}")
        if isinstance(e, openai.RateLimitError):
            return RateLimitError(f"OpenAI rate limit exceeded: {str(e)}")
        if isinstance(e, openai.InternalServerError):
            return ServerError(f"OpenAI server error: {str(e)}", status_code=500)
        if isinstance(e, (openai.APITimeoutError, asyncio.TimeoutError)):
            return TimeoutError(f"OpenAI request timed out: {str(e)}")
        return LLMError(f"OpenAI invocation error: {str(e)}", retryable=False)

    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str,
        temperature: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> AsyncIterator[str]:
        """Stream conversational responses from OpenAI with modern AsyncOpenAI client."""
        client = self._get_client()
        temp = temperature if temperature is not None else settings.OPENAI_TEMPERATURE
        tout = timeout if timeout is not None else settings.OPENAI_TIMEOUT_SECONDS
        model_name = self.model or settings.effective_openai_model

        # Ensure system instruction is the first message
        formatted_messages = []
        if system_instruction:
            formatted_messages.append({"role": "system", "content": system_instruction})

        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role in ("system", "user", "assistant"):
                formatted_messages.append({"role": role, "content": content})
            elif role == "model":
                formatted_messages.append({"role": "assistant", "content": content})
            else:
                formatted_messages.append({"role": "user", "content": content})

        try:
            async def _stream():
                # Chat completions streaming
                stream = await client.chat.completions.create(
                    model=model_name,
                    messages=formatted_messages,
                    temperature=temp,
                    max_tokens=settings.OPENAI_MAX_OUTPUT_TOKENS,
                    stream=True,
                    timeout=tout
                )
                async for chunk in stream:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if delta and delta.content:
                            yield delta.content

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
        """Generate typed structured output using OpenAI JSON mode / schema validation."""
        client = self._get_client()
        temp = temperature if temperature is not None else settings.OPENAI_TEMPERATURE
        tout = timeout if timeout is not None else settings.OPENAI_TIMEOUT_SECONDS
        model_name = self.model or settings.effective_openai_model

        sys_msg = (
            f"{system_instruction}\n"
            f"You MUST respond with a valid JSON object matching the schema:\n"
            f"{json.dumps(response_model.model_json_schema())}"
        )
        formatted_messages = [{"role": "system", "content": sys_msg}]
        for m in messages:
            role = "assistant" if m.get("role") in ("model", "assistant") else "user"
            formatted_messages.append({"role": role, "content": m.get("content", "")})

        try:
            async with asyncio.timeout(tout):
                response = await client.chat.completions.create(
                    model=model_name,
                    messages=formatted_messages,
                    temperature=temp,
                    max_tokens=settings.OPENAI_MAX_OUTPUT_TOKENS,
                    response_format={"type": "json_object"},
                    timeout=tout
                )

            raw_text = response.choices[0].message.content or "{}"
            cleaned_text = clean_json_markdown(raw_text)

            try:
                return response_model.model_validate_json(cleaned_text)
            except (ValidationError, json.JSONDecodeError) as parse_err:
                json_match = re.search(r"(\{.*\})", cleaned_text, re.DOTALL)
                if json_match:
                    try:
                        return response_model.model_validate_json(json_match.group(1))
                    except Exception:
                        pass
                raise JSONSchemaValidationError(
                    f"Failed to validate OpenAI response against {response_model.__name__}: {str(parse_err)}"
                )

        except Exception as e:
            if isinstance(e, JSONSchemaValidationError):
                raise
            raise self._map_api_error(e)
