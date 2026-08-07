"""
Integration test for the chat endpoint.

Sprint 6: /chat now accepts a `messages` array instead of a single
`message` string. To keep these tests fast, deterministic, and
independent of a real API key, we override the get_chat_service
dependency with fakes — this exercises the real HTTP pipeline
(routing, validation, response shaping, error handling) without
making a real network call.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api.v1.routes.chat import get_chat_service
from app.main import app
from app.models.chat import Message
from app.services.exceptions import AIProviderError

client = TestClient(app)


class _FakeChatService:
    """Stands in for ChatService, returning a canned response."""

    def generate_response(self, messages: list[Message]) -> str:
        last_user = messages[-1].content
        return f"Echo: {last_user}"


class _FailingChatService:
    """Stands in for ChatService, simulating a provider failure."""

    def generate_response(self, messages: list[Message]) -> str:
        raise AIProviderError("The AI provider failed to generate a response.")


@pytest.fixture(autouse=True)
def _clear_dependency_overrides() -> Iterator[None]:
    """Ensure each test starts clean and overrides never leak between tests."""
    yield
    app.dependency_overrides.clear()


def test_chat_returns_response_from_service() -> None:
    """A valid single-message conversation should get a 200 with whatever ChatService returns."""
    app.dependency_overrides[get_chat_service] = lambda: _FakeChatService()

    response = client.post(
        "/api/v1/chat", json={"messages": [{"role": "user", "content": "Hello Vision"}]}
    )

    assert response.status_code == 200
    assert response.json() == {"response": "Echo: Hello Vision"}


def test_chat_accepts_multi_turn_conversation() -> None:
    """A conversation with prior user/assistant turns should be accepted as-is."""
    app.dependency_overrides[get_chat_service] = lambda: _FakeChatService()

    response = client.post(
        "/api/v1/chat",
        json={
            "messages": [
                {"role": "user", "content": "What is the diameter of the Sun?"},
                {"role": "assistant", "content": "~1.39 million km."},
                {"role": "user", "content": "What is its distance from Earth?"},
            ]
        },
    )

    assert response.status_code == 200
    assert response.json() == {"response": "Echo: What is its distance from Earth?"}


def test_chat_rejects_empty_messages_array() -> None:
    """An empty messages array should fail validation (min_length=1) with 422."""
    app.dependency_overrides[get_chat_service] = lambda: _FakeChatService()

    response = client.post("/api/v1/chat", json={"messages": []})

    assert response.status_code == 422


def test_chat_rejects_missing_messages_field() -> None:
    """A request body without `messages` at all should fail validation with 422."""
    app.dependency_overrides[get_chat_service] = lambda: _FakeChatService()

    response = client.post("/api/v1/chat", json={})

    assert response.status_code == 422


def test_chat_rejects_invalid_role() -> None:
    """A message with a role outside user/assistant/system should fail validation with 422."""
    app.dependency_overrides[get_chat_service] = lambda: _FakeChatService()

    response = client.post(
        "/api/v1/chat", json={"messages": [{"role": "narrator", "content": "Hi"}]}
    )

    assert response.status_code == 422


def test_chat_handles_provider_failure_without_leaking_details() -> None:
    """If the AI provider fails, the client gets a safe 502 — never a raw SDK error or a key."""
    app.dependency_overrides[get_chat_service] = lambda: _FailingChatService()

    response = client.post(
        "/api/v1/chat", json={"messages": [{"role": "user", "content": "Hello"}]}
    )

    assert response.status_code == 502
    body = response.json()
    assert "detail" in body
    assert "GEMINI_API_KEY" not in body["detail"]
    assert "traceback" not in body["detail"].lower()
