"""Authentication router for login and user management."""

import logging

from fastapi import APIRouter, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from fastapi_app.helper_fastapi import create_access_token
from fastapi_app.schemas import (
    LoginRequest,
    TokenResponse,
)
from shared.helper import where_am_i
from shared.helper_db import (
    db_select_user_from_geheimnis,
)

logger = logging.getLogger(__name__)

ENV = where_am_i()

router = APIRouter()
limiter = Limiter(key_func=get_remote_address, enabled=ENV == "PROD")


@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, login_request: LoginRequest) -> TokenResponse:  # noqa: ARG001
    """
    Authenticate user with secret and return JWT token.

    Rate limited

    Args:
        request: FastAPI request object (for rate limiting)
        login_request: Login credentials containing secret

    Returns:
        TokenResponse: JWT token

    Raises:
        HTTPException: If credentials are invalid or rate limit exceeded

    """
    # Verify credentials
    user_id, user_name = db_select_user_from_geheimnis(geheimnis=login_request.secret)

    if user_id == 0:
        logger.warning("Failed login attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Create JWT token (includes user_id and username)
    token_data = {"user_id": user_id, "username": user_name}
    access_token = create_access_token(data=token_data)

    logger.info("Login of user %s (%d)", user_name, user_id)

    return TokenResponse(
        access_token=access_token,
    )
