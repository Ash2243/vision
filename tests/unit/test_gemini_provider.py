"""
Unit tests for GeminiProvider.

Mocks the Gemini SDK client entirely — no real API key or network
access is used or required. These tests verify our own role
translation and error-handling logic, not Gemini's behavior.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.models.chat import Message
from app.services.exceptions import AIProviderError
from app.services.providers.gemini_provider import GeminiProvider


def _fake_settings(api_key: str = "fake-key", model: str = "gemini-3.6-flash") -> MagicMock:
    settings = MagicMock()
    settings.GEMINI_API_KEY = api_key
    settings.GEMINI_MODEL = model
    return settings


@patch("app.services.providers.gemini_provider.get_settings")
def test_missing_api_key_raises_ai_provider_error(mock_get_settings: MagicMock) -> None:
    """Constructing GeminiProvider without an API key should fail fast and clearly."""
    mock_get_settings.return_value = _fake_settings(api_key="")

    with pytest.raises(AIProviderError):
        GeminiProvider()


@patch("app.services.providers.gemini_provider.genai.Client")
@patch("app.services.providers.gemini_provider.get_settings")
def test_generate_returns_response_text(
    mock_get_settings: MagicMock, mock_client_cls: MagicMock
) -> None:
    """A successful Gemini call should return the response's text."""
    mock_get_settings.return_value = _fake_settings()
    mock_response = MagicMock()
    mock_response.text = "Hello from Gemini"
    mock_client_cls.return_value.models.generate_content.return_value = mock_response

    provider = GeminiProvider()
    result = provider.generate([Message(role="user", content="Hi")])

    assert result == "Hello from Gemini"


@patch("app.services.providers.gemini_provider.genai.Client")
@patch("app.services.providers.gemini_provider.get_settings")
def test_assistant_role_translated_to_model(
    mock_get_settings: MagicMock, mock_client_cls: MagicMock
) -> None:
    """Our 'assistant' role must be sent to Gemini as 'model', never as 'assistant'."""
    mock_get_settings.return_value = _fake_settings()
    mock_response = MagicMock()
    mock_response.text = "ok"
    mock_client_cls.return_value.models.generate_content.return_value = mock_response

    provider = GeminiProvider()
    provider.generate(
        [
            Message(role="user", content="What is the diameter of the Sun?"),
            Message(role="assistant", content="~1.39 million km."),
            Message(role="user", content="What is its distance from Earth?"),
        ]
    )

    _, call_kwargs = mock_client_cls.return_value.models.generate_content.call_args
    sent_contents = call_kwargs["contents"]
    sent_roles = [c.role for c in sent_contents]

    assert sent_roles == ["user", "model", "user"]
    assert "assistant" not in sent_roles


@patch("app.services.providers.gemini_provider.genai.Client")
@patch("app.services.providers.gemini_provider.get_settings")
def test_system_instruction_passed_via_config_not_history(
    mock_get_settings: MagicMock, mock_client_cls: MagicMock
) -> None:
    """system_instruction should go through GenerateContentConfig, not as a content entry."""
    mock_get_settings.return_value = _fake_settings()
    mock_response = MagicMock()
    mock_response.text = "ok"
    mock_client_cls.return_value.models.generate_content.return_value = mock_response

    provider = GeminiProvider()
    provider.generate(
        [Message(role="user", content="Hi")],
        system_instruction="Be concise.",
    )

    _, call_kwargs = mock_client_cls.return_value.models.generate_content.call_args
    assert len(call_kwargs["contents"]) == 1  # system message never added as a content entry
    assert call_kwargs["config"].system_instruction == "Be concise."


@patch("app.services.providers.gemini_provider.genai.Client")
@patch("app.services.providers.gemini_provider.get_settings")
def test_no_system_instruction_means_no_config(
    mock_get_settings: MagicMock, mock_client_cls: MagicMock
) -> None:
    """When there's no system instruction, config should be None (unchanged from Sprint 4)."""
    mock_get_settings.return_value = _fake_settings()
    mock_response = MagicMock()
    mock_response.text = "ok"
    mock_client_cls.return_value.models.generate_content.return_value = mock_response

    provider = GeminiProvider()
    provider.generate([Message(role="user", content="Hi")])

    _, call_kwargs = mock_client_cls.return_value.models.generate_content.call_args
    assert call_kwargs["config"] is None


@patch("app.services.providers.gemini_provider.genai.Client")
@patch("app.services.providers.gemini_provider.get_settings")
def test_generate_raises_on_empty_response(
    mock_get_settings: MagicMock, mock_client_cls: MagicMock
) -> None:
    """An empty response.text from Gemini should raise AIProviderError, not return blank."""
    mock_get_settings.return_value = _fake_settings()
    mock_response = MagicMock()
    mock_response.text = ""
    mock_client_cls.return_value.models.generate_content.return_value = mock_response

    provider = GeminiProvider()
    with pytest.raises(AIProviderError):
        provider.generate([Message(role="user", content="Hi")])


@patch("app.services.providers.gemini_provider.genai.Client")
@patch("app.services.providers.gemini_provider.get_settings")
def test_generate_wraps_unexpected_exceptions(
    mock_get_settings: MagicMock, mock_client_cls: MagicMock
) -> None:
    """Any unexpected failure (network, SDK internals) must be translated, never leaked raw."""
    mock_get_settings.return_value = _fake_settings()
    mock_client_cls.return_value.models.generate_content.side_effect = RuntimeError("network down")

    provider = GeminiProvider()
    with pytest.raises(AIProviderError):
        provider.generate([Message(role="user", content="Hi")])
