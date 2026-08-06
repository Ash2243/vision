"""
Application entrypoint.

Creates the FastAPI app, wires up logging and configuration, mounts
the versioned API router, enables CORS for the frontend, and
registers error handling for AI provider failures. Run locally with:

    uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.services.exceptions import AIProviderError

settings = get_settings()
configure_logging()

app = FastAPI(title=settings.APP_NAME)

# Required for the Next.js frontend (Sprint 5) to call this API from
# the browser — without it, every request is blocked client-side
# regardless of whether the backend itself works correctly.
# CORS_ORIGINS is a comma-separated list read from .env, so allowed
# origins differ between local dev and a future production deploy
# without a code change.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",")],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.exception_handler(AIProviderError)
async def ai_provider_error_handler(request: Request, exc: AIProviderError) -> JSONResponse:
    """
    Convert AIProviderError into a safe HTTP response.

    Centralizing this here (rather than in chat.py or ChatService)
    means every route that ever raises AIProviderError gets the same
    safe handling for free, and no route needs its own try/except.
    Returns 502 (Bad Gateway): this backend, acting as a gateway to
    Gemini, got a failure from that upstream service. The response
    body is always the generic exception message — AIProviderError
    is only ever raised with safe, pre-sanitized text (see
    gemini_provider.py), never with raw SDK output or secrets.
    """
    return JSONResponse(status_code=502, content={"detail": str(exc)})
