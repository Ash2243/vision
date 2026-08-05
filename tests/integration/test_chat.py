"""
Integration test for the chat endpoint.

Sprint 4: /chat now calls Gemini via ChatService. To keep these tests
fast, deterministic, and independent of a real API key, we override
the get_chat_service dependency with fakes — this exercises the real
HTTP pipeline (routing, validation, response shaping, error handling)
without making a real network call.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api.v1.routes.chat import get_chat_service
from app.main import app
from app.services.exceptions import AIProviderError

client = TestClient(app)


class _FakeChatService:
    """Stands in for ChatService, returning a canned response."""

    def generate_response(self, message: str) -> str:
        return f"Echo: {message}"


class _FailingChatService:
    """Stands in for ChatService, simulating a provider failure."""

    def generate_response(self, message: str) -> str:
        raise AIProviderError("The AI provider failed to generate a response.")


@pytest.fixture(autouse=True)
def _clear_dependency_overrides() -> Iterator[None]:
    """Ensure each test starts clean and overrides never leak between tests."""
    yield
    app.dependency_overrides.clear()


def test_chat_returns_response_from_service() -> None:
    """A valid message should get a 200 with whatever ChatService returns."""
    app.dependency_overrides[get_chat_service] = lambda: _FakeChatService()

    response = client.post("/api/v1/chat", json={"message": "Hello Vision"})

    assert response.status_code == 200
    assert response.json() == {
        "response": "Echo: Hello Vision",
        "message": "Hello Vision",
    }


def test_chat_rejects_missing_message() -> None:
    """A request body without `message` should fail validation with 422 (unchanged from Sprint 2)."""
    # Overridden even though this test isn't about the service: without a
    # real GEMINI_API_KEY, constructing the real ChatService would raise
    # AIProviderError before validation ever gets a chance to run, which
    # would make this test about missing config instead of about
    # validation. The fake keeps this test isolated to what it claims to test.
    app.dependency_overrides[get_chat_service] = lambda: _FakeChatService()

    response = client.post("/api/v1/chat", json={})

    assert response.status_code == 422


def test_chat_rejects_non_string_message() -> None:
    """A `message` field that isn't a string should fail validation with 422 (unchanged from Sprint 2)."""
    app.dependency_overrides[get_chat_service] = lambda: _FakeChatService()

    response = client.post("/api/v1/chat", json={"message": 12345})

    assert response.status_code == 422


def test_chat_handles_provider_failure_without_leaking_details() -> None:
    """If the AI provider fails, the client gets a safe 502 — never a raw SDK error or a key."""
    app.dependency_overrides[get_chat_service] = lambda: _FailingChatService()

    response = client.post("/api/v1/chat", json={"message": "Hello"})

    assert response.status_code == 502
    body = response.json()
    assert "detail" in body
    assert "GEMINI_API_KEY" not in body["detail"]
    assert "traceback" not in body["detail"].lower()
