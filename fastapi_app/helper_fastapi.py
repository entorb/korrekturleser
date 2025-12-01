"""FastAPI dependencies for authentication and authorization."""

from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from fastapi_app.schemas import UserInfoInternal
from shared.config import FASTAPI_JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_HOURS

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(hours=JWT_EXPIRE_HOURS)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, FASTAPI_JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),  # noqa: B008
) -> UserInfoInternal:
    """
    Validate JWT token and return current user information.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        UserInfo: Current user information

    Raises:
        HTTPException: If token is invalid or expired

    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(token, FASTAPI_JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: int | None = payload.get("user_id")
        username: str | None = payload.get("username")

        if user_id is None or username is None:
            raise credentials_exception

        return UserInfoInternal(user_id=user_id, user_name=username)

    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise credentials_exception from exc
