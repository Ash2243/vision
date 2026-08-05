"""
Gemini provider.

Wraps Google's Gemini API behind a plain generate(prompt) -> str
method. Sprint 4 scope: a single concrete provider, no abstract base
class or multi-provider switching yet — that's explicitly deferred to
a later sprint per the Sprint 4 brief.
"""

import logging

from google import genai
from google.genai import errors as genai_errors

from app.core.config import get_settings
from app.services.exceptions import AIProviderError

logger = logging.getLogger(__name__)


class GeminiProvider:
    """Sends prompts to Google Gemini and returns plain text responses."""

    def __init__(self) -> None:
        settings = get_settings()

        if not settings.GEMINI_API_KEY:
            # Fails fast and clearly if .env is misconfigured, rather
            # than surfacing a confusing SDK auth error later.
            raise AIProviderError(
                "Gemini is not configured. Set GEMINI_API_KEY in .env."
            )

        self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self._model = settings.GEMINI_MODEL

    def generate(self, prompt: str) -> str:
        """
        Send a prompt to Gemini and return the plain text response.

        Raises AIProviderError on any failure. Callers never see raw
        SDK exceptions, HTTP status details, or the API key — only a
        safe, generic message suitable for surfacing to a client.
        """
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
            )
        except genai_errors.APIError as exc:
            logger.error("Gemini API error (code=%s): %s", exc.code, exc.message)
            raise AIProviderError(
                "The AI provider failed to generate a response."
            ) from exc
        except Exception as exc:  # noqa: BLE001 — intentionally broad:
            # any unexpected failure (network, SDK internals, etc.)
            # must still be translated, never leaked raw to the caller.
            logger.error("Unexpected error calling Gemini: %s", exc)
            raise AIProviderError(
                "The AI provider failed to generate a response."
            ) from exc

        if not response.text:
            logger.warning("Gemini returned an empty response.")
            raise AIProviderError("The AI provider returned an empty response.")

        return response.text
