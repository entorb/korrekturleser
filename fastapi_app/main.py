"""FastAPI application main file."""

import logging
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from fastapi_app.routers import auth, config, stats, text
from shared.helper import ENV, init_logging

if TYPE_CHECKING:
    from starlette.types import ASGIApp, Receive, Scope, Send

# Configure logging
init_logging()
logger = logging.getLogger(__name__)

if ENV == "PROD":
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_sdk.init(
        dsn="https://478915eebf07672bfe0d1fba879c3217@o4507139041525760.ingest.de.sentry.io/4512292150378576",
        integrations=[
            LoggingIntegration(capture_sentry_logs=True),
        ],
    )

# Create rate limiter (disabled during testing)
limiter = Limiter(key_func=get_remote_address, enabled=(ENV == "PROD"))

# Create FastAPI app
app = FastAPI(
    title="KI Korrekturleser API",
    description="AI-powered text correction and improvement API",
    version="0.1.0",
)


class RootPathMiddleware:
    """
    Set root_path like deprecated FastAPI(root_path=...).

    Not uvicorn --root-path: that prepends it to path, but proxy already keeps prefix.
    """

    def __init__(self, app: ASGIApp) -> None:  # noqa: D107
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:  # noqa: D102
        # same root for prod and dev to make debugging easier
        scope["root_path"] = "/be/korrekturleser"
        await self.app(scope, receive, send)


app.add_middleware(RootPathMiddleware)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

# Configure CORS
if ENV == "PROD":
    origins = ["https://entorb.net"]
else:
    origins = [
        "http://localhost:4173",  # Vue Prod server
        "http://localhost:5173",  # Vue Dev server
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(config.router, prefix="/api/config", tags=["Configuration"])
app.include_router(text.router, prefix="/api/text", tags=["Text Operations"])
app.include_router(stats.router, prefix="/api/stats", tags=["Statistics"])


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "KI Korrekturleser API",
        "version": "0.1.0",
        "environment": ENV,
        "docs": "/docs",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "environment": ENV}


# https://entorb.net/be/korrekturleser/sentry-test
@app.get("/sentry-test")
async def trigger_error() -> None:
    """Test."""
    _ = 1 / 0
