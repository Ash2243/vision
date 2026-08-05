"""
Chat service.

Sprint 4: delegates response generation to GeminiProvider — Vision's
first real AI integration. chat.py is unaware of this change; it
still just calls generate_response(message) exactly as before.
"""

from app.services.providers.gemini_provider import GeminiProvider


class ChatService:
    """Encapsulates the logic for producing a response to a chat message."""

    def __init__(self) -> None:
        self._provider = GeminiProvider()

    def generate_response(self, message: str) -> str:
        """
        Generate a response for the given message using Gemini.

        Any provider failure surfaces as AIProviderError, which
        main.py's exception handler converts into a safe HTTP
        response — this method doesn't need its own try/except, and
        chat.py doesn't need to change at all.
        """
        return self._provider.generate(message)
