"""
Unit test for ChatService.

Mocks GeminiProvider so this test verifies ChatService's delegation
logic only — not Gemini itself, and no real API key needed.
"""

from unittest.mock import MagicMock, patch

from app.services.chat_service import ChatService


@patch("app.services.chat_service.GeminiProvider")
def test_generate_response_delegates_to_provider(mock_provider_cls: MagicMock) -> None:
    """ChatService.generate_response should call GeminiProvider.generate and return its result."""
    mock_provider_cls.return_value.generate.return_value = "Hello from Gemini"

    service = ChatService()
    result = service.generate_response("Hi")

    assert result == "Hello from Gemini"
    mock_provider_cls.return_value.generate.assert_called_once_with("Hi")
