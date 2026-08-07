"""
Request and response schemas for the /chat endpoint.

Kept in their own file (rather than inline in the route) so that:
1. The route file stays focused on request handling, not data shape.
2. These schemas can be reused later — e.g. by tests, or by other
   routes that need to accept/return a chat message.

Sprint 6: ChatRequest now carries the full conversation (messages),
not a single isolated message — this is what lets follow-up
questions refer back to earlier turns, while the backend itself
stays stateless (the client is the source of truth for history).
"""

from typing import Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    """
    A single turn in a conversation.

    role is one of the domain roles the whole app (frontend, API,
    services) uses — translation to any specific AI provider's own
    role vocabulary (e.g. Gemini's "model" instead of "assistant")
    happens inside that provider, not here.
    """

    role: Literal["user", "assistant", "system"] = Field(
        ..., description="Who sent this message."
    )
    content: str = Field(..., description="The message text.")


class ChatRequest(BaseModel):
    """Incoming request body for POST /api/v1/chat."""

    messages: list[Message] = Field(
        ...,
        min_length=1,
        description="The conversation so far, oldest first. Must contain at least one message.",
    )


class ChatResponse(BaseModel):
    """Response body for POST /api/v1/chat."""

    response: str = Field(..., description="Vision's reply.")
