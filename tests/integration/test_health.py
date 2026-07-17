"""
Integration test for the health endpoint.

This is an "integration" test rather than a "unit" test because it
spins up the full FastAPI app (routing, config loading, logging setup
all wired together) and confirms the pieces work correctly as a whole
— not just one function in isolation.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    """GET /api/v1/health should return 200 and {"status": "ok"}."""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
