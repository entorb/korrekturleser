"""FastAPI application main file."""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from fastapi_app.routers import auth, stats, text
from shared.helper import where_am_i

ENV = where_am_i()
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create rate limiter (disabled during testing)
limiter = Limiter(key_func=get_remote_address, enabled=os.getenv("TESTING") != "1")

# Create FastAPI app
app = FastAPI(
    title="KI Korrekturleser API",
    description="AI-powered text correction and improvement API",
    version="0.1.0",
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
origins = [
    "http://localhost:5173",  # Vue dev server
    "http://localhost:8080",  # Alternative Vue dev server
    "http://localhost:3000",  # Alternative frontend
]

if ENV == "PROD":
    # Add production domain when deployed
    origins.append("https://entorb.net")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(text.router, prefix="/api/text", tags=["Text Improvement"])
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
