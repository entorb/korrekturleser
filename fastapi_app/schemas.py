"""Pydantic schemas for request and response validation."""

import datetime as dt

from pydantic import BaseModel, Field

from shared.helper_ai import TextMode


# Authentication schemas
class LoginRequest(BaseModel):
    """Login request schema."""

    secret: str = Field(..., min_length=1, description="User secret")


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str = "bearer"  # noqa: S105


class ConfigResponse(BaseModel):
    """Configuration response schema."""

    llm_provider: str
    models: list[str] = Field(..., min_length=1, description="List of available models")


class UserInfoInternal(BaseModel):
    """Current user information (internal use only)."""

    user_id: int
    user_name: str


# Text improvement schemas
class TextRequest(BaseModel):
    """Text improvement request schema."""

    text: str = Field(..., min_length=1, description="Text to improve")
    mode: TextMode = Field(..., description="AI text operation mode")  # pyright: ignore[reportInvalidTypeForm]
    model: str | None = Field(
        None, description="LLM model to use (optional, defaults to first available)"
    )


class TextResponse(BaseModel):
    """Text improvement response schema."""

    text_original: str
    text_ai: str
    mode: TextMode  # pyright: ignore[reportInvalidTypeForm]
    tokens_used: int
    model: str
    provider: str


# Statistics schemas
class DailyUsage(BaseModel):
    """Daily usage statistics."""

    date: dt.date
    user_name: str
    cnt_requests: int
    cnt_tokens: int


class TotalUsage(BaseModel):
    """Total usage statistics."""

    user_name: str
    cnt_requests: int
    cnt_tokens: int


class UsageStatsResponse(BaseModel):
    """Usage statistics response."""

    daily: list[DailyUsage]
    total: list[TotalUsage]
