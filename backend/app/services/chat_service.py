"""
Chat service.

Sprint 6: receives the full client-supplied conversation history (the
backend holds no state of its own — see MAX_HISTORY_MESSAGES), splits
out any system-role messages to pass to Gemini as a system
instruction rather than as conversation turns, trims the remaining
history to a bounded window, and delegates to GeminiProvider.
"""

from app.core.config import get_settings
from app.models.chat import Message
from app.services.providers.gemini_provider import GeminiProvider


class ChatService:
    """Encapsulates the logic for producing a response to a chat message."""

    def __init__(self) -> None:
        self._provider = GeminiProvider()
        self._max_history = get_settings().MAX_HISTORY_MESSAGES

    def generate_response(self, messages: list[Message]) -> str:
        """
        Generate a response for the given conversation.

        `messages` is the client-supplied conversation so far
        (oldest first). Any provider failure surfaces as
        AIProviderError, which main.py's exception handler converts
        into a safe HTTP response — this method doesn't need its own
        try/except, and chat.py doesn't need to change.
        """
        system_instruction = self._extract_system_instruction(messages)
        conversation = [m for m in messages if m.role != "system"]
        conversation = self._trim_history(conversation, self._max_history)

        return self._provider.generate(conversation, system_instruction=system_instruction)

    @staticmethod
    def _extract_system_instruction(messages: list[Message]) -> str | None:
        """
        Pull out any system-role messages and join them into a single
        instruction string, rather than letting them sit in the
        conversation history sent to Gemini as regular turns.
        """
        system_parts = [m.content for m in messages if m.role == "system"]
        return "\n".join(system_parts) if system_parts else None

    @staticmethod
    def _trim_history(conversation: list[Message], limit: int) -> list[Message]:
        """
        Keep at most `limit` most recent messages.

        A naive conversation[-limit:] slice can land on an assistant
        message as the new first entry (e.g. if the window cuts
        between a user/assistant pair) — Gemini requires the
        conversation it receives to open with a user turn, so any
        leading assistant messages left over after slicing are
        dropped.
        """
        trimmed = conversation[-limit:]
        while trimmed and trimmed[0].role == "assistant":
            trimmed = trimmed[1:]
        return trimmed
