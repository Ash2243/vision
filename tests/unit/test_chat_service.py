"""
Unit tests for ChatService.

Mocks GeminiProvider so these test ChatService's own logic
(system-instruction extraction, history trimming) — not Gemini
itself, and no real API key needed.
"""

from unittest.mock import MagicMock, patch

from app.models.chat import Message
from app.services.chat_service import ChatService


def _service_with_mock_provider(max_history: int = 10):
    """Build a ChatService with GeminiProvider mocked out."""
    with patch("app.services.chat_service.GeminiProvider") as mock_provider_cls, patch(
        "app.services.chat_service.get_settings"
    ) as mock_get_settings:
        mock_get_settings.return_value.MAX_HISTORY_MESSAGES = max_history
        service = ChatService()
        return service, mock_provider_cls.return_value


def test_generate_response_delegates_to_provider() -> None:
    """A simple single-message conversation should pass straight through."""
    service, mock_provider = _service_with_mock_provider()
    mock_provider.generate.return_value = "Hello from Gemini"

    messages = [Message(role="user", content="Hi")]
    result = service.generate_response(messages)

    assert result == "Hello from Gemini"
    sent_messages, sent_kwargs = mock_provider.generate.call_args
    assert sent_messages[0] == messages
    assert sent_kwargs["system_instruction"] is None


def test_system_message_extracted_and_not_sent_as_history() -> None:
    """System messages should be pulled into system_instruction, not left in history."""
    service, mock_provider = _service_with_mock_provider()
    mock_provider.generate.return_value = "ok"

    messages = [
        Message(role="system", content="Be concise."),
        Message(role="user", content="Hi"),
    ]
    service.generate_response(messages)

    sent_messages, sent_kwargs = mock_provider.generate.call_args
    assert sent_kwargs["system_instruction"] == "Be concise."
    assert all(m.role != "system" for m in sent_messages[0])
    assert len(sent_messages[0]) == 1


def test_multiple_system_messages_joined() -> None:
    """More than one system message should be joined, not just the last one used."""
    service, mock_provider = _service_with_mock_provider()
    mock_provider.generate.return_value = "ok"

    messages = [
        Message(role="system", content="Be concise."),
        Message(role="system", content="Be friendly."),
        Message(role="user", content="Hi"),
    ]
    service.generate_response(messages)

    _, sent_kwargs = mock_provider.generate.call_args
    assert sent_kwargs["system_instruction"] == "Be concise.\nBe friendly."


def test_history_trimmed_to_max_history_messages() -> None:
    """Only the most recent MAX_HISTORY_MESSAGES should be forwarded."""
    service, mock_provider = _service_with_mock_provider(max_history=4)
    mock_provider.generate.return_value = "ok"

    # 6 alternating messages; only the last 4 should survive, and
    # since index -4 lands on "user", no adjustment is needed.
    messages = [
        Message(role="user", content="1"),
        Message(role="assistant", content="2"),
        Message(role="user", content="3"),
        Message(role="assistant", content="4"),
        Message(role="user", content="5"),
        Message(role="assistant", content="6"),
    ]
    service.generate_response(messages)

    sent_messages, _ = mock_provider.generate.call_args
    contents = [m.content for m in sent_messages[0]]
    assert contents == ["3", "4", "5", "6"]


def test_trimmed_history_never_starts_with_assistant() -> None:
    """
    If a naive slice would start with an assistant message, the
    leading assistant message(s) must be dropped so Gemini always
    receives a conversation opening with a user turn.
    """
    service, mock_provider = _service_with_mock_provider(max_history=3)
    mock_provider.generate.return_value = "ok"

    # Last 3 of this list would naively be: assistant("2"), user("3"), assistant("4")
    # — starts with assistant, so "2" must be dropped too.
    messages = [
        Message(role="user", content="1"),
        Message(role="assistant", content="2"),
        Message(role="user", content="3"),
        Message(role="assistant", content="4"),
    ]
    service.generate_response(messages)

    sent_messages, _ = mock_provider.generate.call_args
    contents = [m.content for m in sent_messages[0]]
    assert contents == ["3", "4"]
    assert sent_messages[0][0].role == "user"


def test_single_first_message_works() -> None:
    """A brand-new conversation with just one user message should work unchanged."""
    service, mock_provider = _service_with_mock_provider()
    mock_provider.generate.return_value = "ok"

    messages = [Message(role="user", content="What is the diameter of the Sun?")]
    service.generate_response(messages)

    sent_messages, _ = mock_provider.generate.call_args
    assert len(sent_messages[0]) == 1
    assert sent_messages[0][0].role == "user"
