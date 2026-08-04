"""
Integration test for the chat endpoint.

Covers the happy path (valid message → placeholder response) and the
validation path (missing message → 422), since request validation is
one of Sprint 2's explicit deliverables.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_chat_returns_placeholder_response() -> None:
    """A valid message should get a 200 with an echoed placeholder response."""
    response = client.post("/api/v1/chat", json={"message": "Hello Vision"})

    assert response.status_code == 200
    assert response.json() == {
        "response": "Vision received your message.",
        "message": "Hello Vision",
    }


def test_chat_rejects_missing_message() -> None:
    """A request body without `message` should fail validation with 422."""
    response = client.post("/api/v1/chat", json={})

    assert response.status_code == 422


def test_chat_rejects_non_string_message() -> None:
    """A `message` field that isn't a string should fail validation with 422."""
    response = client.post("/api/v1/chat", json={"message": 12345})

    assert response.status_code == 422
