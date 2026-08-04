"""
Combines all API v1 route modules into a single router.

New route files (e.g. ingest.py in a future sprint) get added here —
main.py never needs to know about individual routes, only about this
one combined router.
"""

from fastapi import APIRouter

from app.api.v1.routes import health, chat

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(chat.router, tags=["chat"])