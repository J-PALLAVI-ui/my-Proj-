"""FujiNova Backend Configuration."""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # Server Environment
    FUJINOVA_ENV: str = Field("development", description="Environment: development, test, production")
    FUJINOVA_HOST: str = Field("127.0.0.1", description="Backend host address")
    FUJINOVA_PORT: int = Field(8000, description="Backend port number")
    DATABASE_URL: str = Field("sqlite:///./fujinova.db", description="SQLite connection string")

    # Primary Model Provider Configuration
    # Uses 'gemini-flash-lite-latest' as baseline, or 'openai' when OPENAI_API_KEY is configured
    FUJINOVA_PRIMARY_PROVIDER: str = Field("google", description="Primary AI provider ('google' or 'openai')")
    FUJINOVA_PRIMARY_MODEL: str = Field("gemini-flash-lite-latest", description="Primary model identifier")

    # OpenAI Configuration (Official OpenAI SDK)
    OPENAI_API_KEY: Optional[str] = Field(None, description="OpenAI API key")
    OPENAI_MODEL: str = Field("gpt-4o-mini", description="OpenAI model identifier (e.g. gpt-4o, gpt-4o-mini, gpt-4.5-preview)")
    OPENAI_MAX_OUTPUT_TOKENS: int = Field(1500, description="Max output tokens for response generation")
    OPENAI_TEMPERATURE: float = Field(0.7, description="Sampling temperature for OpenAI conversational generation")
    OPENAI_TIMEOUT_SECONDS: float = Field(25.0, description="OpenAI API request timeout in seconds")
    OPENAI_MAX_RETRIES: int = Field(2, description="Maximum retry attempts on rate limits/server errors")

    # Google Gemini Configuration (Supported Alternate Provider)
    GEMINI_API_KEY: Optional[str] = Field(None, description="Google AI Studio API key")
    GEMINI_MODEL: str = Field("gemini-flash-lite-latest", description="Gemini model identifier")

    # Secondary / Failover Configuration
    ENABLE_OPENAI_FALLBACK: bool = Field(False, description="Set to True only if explicitly enabling paid OpenAI failover")
    FUJINOVA_FALLBACK_PROVIDER: str = Field("openai", description="Fallback provider")
    FUJINOVA_FALLBACK_MODEL: str = Field("gpt-4o-mini", description="Fallback model identifier")

    # Operational Parameters
    FUJINOVA_TEMPERATURE: float = Field(0.7, description="Default sampling temperature")
    FUJINOVA_MAX_RETRIES: int = Field(2, description="Maximum provider retry attempts")
    FUJINOVA_TIMEOUT_SECONDS: float = Field(25.0, description="Provider request timeout in seconds")
    CORS_ALLOWED_ORIGINS: str = Field("", description="Comma-separated allowed CORS origins (e.g. https://fujinova.onrender.com)")

    # Privacy Policy Gate: If False, cross-vendor prompt transmission is rejected
    ALLOW_MULTI_VENDOR_FAILOVER: bool = Field(False, description="Explicit consent flag for cross-vendor failover")

    # Legacy alias support for backwards compatibility
    @property
    def effective_openai_model(self) -> str:
        return self.OPENAI_MODEL or self.FUJINOVA_FALLBACK_MODEL or "gpt-4o-mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
