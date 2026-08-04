"""
Request and response schemas for the /chat endpoint.

Kept in their own file (rather than inline in the route) so that:
1. The route file stays focused on request handling, not data shape.
2. These schemas can be reused later — e.g. by tests, or by other
   routes that need to accept/return a chat message.
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming request body for POST /api/v1/chat."""

    message: str = Field(..., description="The user's message to Vision.")


class ChatResponse(BaseModel):
    """Response body for POST /api/v1/chat."""

    response: str = Field(..., description="Vision's reply (placeholder for now).")
    message: str = Field(..., description="Echo of the original message received.")