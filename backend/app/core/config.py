"""
Application configuration.

Loads settings from environment variables (via a local .env file in
development). Using a typed Settings object instead of scattering
os.environ.get() calls throughout the codebase means:

1. All configuration lives in one place.
2. Missing or misspelled environment variables fail loudly at startup,
   not silently somewhere deep in a request handler.
3. Editors/type-checkers can catch typos like `settings.APP_NME`.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings, populated from environment variables."""

    APP_NAME: str = "Vision Backend"
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    API_V1_PREFIX: str = "/api/v1"

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.6-flash"

    # Comma-separated list of frontend origins allowed to call this
    # API from the browser. Defaults to the local Next.js dev server.
    CORS_ORIGINS: str = "http://localhost:3000"

    # Sprint 6: the backend is stateless — the client sends the full
    # conversation with every request. This caps how many of the most
    # recent messages ChatService will forward to the AI provider, so
    # payloads (and cost/latency) don't grow unbounded as a
    # conversation gets long. Counts individual messages, not turns
    # (10 messages ≈ 5 user/assistant exchanges).
    MAX_HISTORY_MESSAGES: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached Settings instance.

    lru_cache ensures the .env file is only read once per process,
    rather than on every request that needs a config value.
    """
    return Settings()
