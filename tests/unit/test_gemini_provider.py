"""
Unit tests for GeminiProvider.

Mocks the Gemini SDK client entirely — no real API key or network
access is used or required. These tests verify our own error-handling
and response logic, not Gemini's behavior.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.services.exceptions import AIProviderError
from app.services.providers.gemini_provider import GeminiProvider


def _fake_settings(api_key: str = "fake-key", model: str = "gemini-2.5-flash") -> MagicMock:
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
    result = provider.generate("Hi")

    assert result == "Hello from Gemini"


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
        provider.generate("Hi")


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
        provider.generate("Hi")
