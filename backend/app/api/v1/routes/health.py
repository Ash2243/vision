"""
Health check endpoint.

Used to confirm the API is running and reachable — by developers
locally, and later by the Chrome Extension or any monitoring tooling.
Deliberately has no dependencies on other services, so it stays
reliable even if other parts of the app later fail.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return a simple OK status to confirm the API is alive."""
    return {"status": "ok"}
