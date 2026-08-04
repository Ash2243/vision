"""
Chat endpoint.

Sprint 2 scope: accept a validated message, return a placeholder
response. No AI model is called here yet — this route exists to
establish the request/response pipeline that later sprints will
plug real logic into.
"""

from fastapi import APIRouter

from app.models.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """
    Accept a chat message and return a placeholder response.

    Pydantic validates the incoming body against ChatRequest before
    this function body even runs — an invalid payload (e.g. missing
    `message`, or `message` not a string) is automatically rejected
    with a 422 response, no manual validation code needed here.
    """
    return ChatResponse(
        response="Vision received your message.",
        message=request.message,
    )
