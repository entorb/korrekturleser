"""Authentication router for login and user management."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from fastapi_app.helper_fastapi import create_access_token, get_current_user
from fastapi_app.schemas import (
    LoginRequest,
    TokenResponse,
    UserInfoInternal,
    UserInfoResponse,
)
from shared.helper import where_am_i
from shared.helper_db import db_select_usage_of_user, db_select_user_from_geheimnis

logger = logging.getLogger(__name__)

ENV = where_am_i()

router = APIRouter()
limiter = Limiter(key_func=get_remote_address, enabled=ENV == "PROD")


@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, login_request: LoginRequest) -> TokenResponse:  # noqa: ARG001
    """
    Authenticate user with secret and return JWT token.

    Rate limit: 5 login attempts per minute per IP address.

    Args:
        request: FastAPI request object (for rate limiting)
        login_request: Login credentials containing secret

    Returns:
        TokenResponse: JWT token and user information

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

    # Get usage statistics
    cnt_requests, cnt_tokens = db_select_usage_of_user(user_id=user_id)

    # Create JWT token (includes user_id and username)
    token_data = {"user_id": user_id, "username": user_name}
    access_token = create_access_token(data=token_data)

    logger.info("User %s (ID: %d) logged in successfully", user_name, user_id)

    return TokenResponse(
        access_token=access_token,
        user_name=user_name,
        cnt_requests=cnt_requests,
        cnt_tokens=cnt_tokens,
    )


@router.get("/me")
async def get_me(
    current_user: Annotated[UserInfoInternal, Depends(get_current_user)],
) -> UserInfoResponse:
    """
    Get current authenticated user information.

    Args:
        current_user: Injected by dependency

    Returns:
        UserInfoResponse: Current user information (without user_id)

    """
    return UserInfoResponse(user_name=current_user.user_name)
