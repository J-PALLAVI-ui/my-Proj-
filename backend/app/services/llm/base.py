"""FujiNova LLM Service: Abstract Base Adapter Interface."""
from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Dict, Any, Type, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMError(Exception):
    """Base exception for LLM operations."""
    def __init__(self, message: str, status_code: Optional[int] = None, retryable: bool = False):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.retryable = retryable


class AuthenticationError(LLMError):
    """401/403 Invalid or missing API key (non-retryable)."""
    def __init__(self, message: str):
        super().__init__(message, status_code=401, retryable=False)


class RateLimitError(LLMError):
    """429 Rate limit / quota exceeded (retryable)."""
    def __init__(self, message: str):
        super().__init__(message, status_code=429, retryable=True)


class ServerError(LLMError):
    """5xx Model provider server error (retryable)."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message, status_code=status_code, retryable=True)


class TimeoutError(LLMError):
    """Provider call exceeded timeout threshold (retryable)."""
    def __init__(self, message: str):
        super().__init__(message, status_code=408, retryable=True)


class JSONSchemaValidationError(LLMError):
    """Structured response did not conform to schema."""
    def __init__(self, message: str):
        super().__init__(message, retryable=True)


class FailoverPolicyViolationError(Exception):
    """Cross-vendor failover attempted without explicit configuration and privacy consent."""
    pass


class BaseLLMAdapter(ABC):
    """Contract for LLM model providers."""

    @abstractmethod
    async def stream_generate(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str,
        temperature: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> AsyncIterator[str]:
        """Stream conversational text chunks asynchronously."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        messages: List[Dict[str, str]],
        response_model: Type[T],
        system_instruction: str,
        temperature: Optional[float] = None,
        timeout: Optional[float] = None
    ) -> T:
        """Generate structured data conforming to a Pydantic schema."""
        pass
