"""
Gemini provider.

Wraps Google's Gemini API. Sprint 6 scope: accepts a conversation
(list of Message) instead of a single prompt string, and translates
our domain roles into Gemini's own vocabulary. Still a single
concrete provider — no abstract base class or multi-provider
switching yet, per the Sprint 4 brief and unchanged since.
"""

import logging

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from app.core.config import get_settings
from app.models.chat import Message
from app.services.exceptions import AIProviderError

logger = logging.getLogger(__name__)

# Our domain uses "user" / "assistant" (and "system", handled
# separately — see ChatService). Gemini expects "user" / "model".
# ChatService only ever passes user/assistant messages here (system
# messages are filtered out before this point), so this map only
# needs to cover those two.
_ROLE_TO_GEMINI = {
    "user": "user",
    "assistant": "model",
}


class GeminiProvider:
    """Sends a conversation to Google Gemini and returns a plain text response."""

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

    def generate(
        self,
        messages: list[Message],
        system_instruction: str | None = None,
    ) -> str:
        """
        Send a conversation to Gemini and return the plain text response.

        `messages` should contain only user/assistant turns, oldest
        first — ChatService is responsible for stripping out system
        messages and trimming history before calling this. Raises
        AIProviderError on any failure; callers never see raw SDK
        exceptions, HTTP status details, or the API key.
        """
        contents = [
            types.Content(
                role=_ROLE_TO_GEMINI[m.role],
                parts=[types.Part.from_text(text=m.content)],
            )
            for m in messages
        ]

        config = (
            types.GenerateContentConfig(system_instruction=system_instruction)
            if system_instruction
            else None
        )

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=contents,
                config=config,
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
