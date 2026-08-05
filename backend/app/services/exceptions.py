"""
Service-layer exceptions.

AIProviderError is the one error type that crosses the boundary from
any AI provider back up to the HTTP layer. Providers translate their
own SDK-specific exceptions into this — callers (ChatService, routes)
never need to know or care which provider raised it, and main.py's
exception handler never needs to expose provider-specific details.
"""


class AIProviderError(Exception):
    """Raised when an AI provider fails to produce a response."""
