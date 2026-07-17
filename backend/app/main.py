"""
Application entrypoint.

Creates the FastAPI app, wires up logging and configuration, and
mounts the versioned API router. Run locally with:

    uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging()

app = FastAPI(title=settings.APP_NAME)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)
