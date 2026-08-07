"""
Chat endpoint.

Sprint 3 scope: this route is now "thin" — it only handles HTTP
concerns (accepting the validated request, shaping the response).
All business logic lives in ChatService.
"""

from fastapi import APIRouter, Depends

from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()


def get_chat_service() -> ChatService:
    """
    Provide a ChatService instance.

    A small dependency function rather than a module-level global so
    that tests (or a future Sprint) can swap in a different service
    implementation without touching this route.
    """
    return ChatService()


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """
    Accept a conversation and return Vision's response.

    Delegates response generation to ChatService — this function's
    only job is to receive the validated request, call the service,
    and shape the result into a ChatResponse.
    """
    reply = service.generate_response(request.messages)
    return ChatResponse(response=reply)
