"""Pydantic schemas for request and response validation."""

import datetime as dt
from enum import Enum

from pydantic import BaseModel, Field


# Authentication schemas
class LoginRequest(BaseModel):
    """Login request schema."""

    secret: str = Field(..., min_length=1, description="User secret")


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str = "bearer"  # noqa: S105


class UserInfoInternal(BaseModel):
    """Current user information (internal use only)."""

    user_id: int
    user_name: str


class UserInfoResponse(BaseModel):
    """User information response."""

    user_name: str


# Text improvement schemas
class TextMode(str, Enum):
    """Available improvement modes."""

    CORRECT = "correct"  # Korrigieren
    IMPROVE = "improve"  # Verbessern
    SUMMARIZE = "summarize"  # Zusammenfassen
    EXPAND = "expand"  # Text aus Stichpunkten
    TRANSLATE_DE = "translate_de"  # Übersetzen -> DE
    TRANSLATE_EN = "translate_en"  # Übersetzen -> EN


class ImproveRequest(BaseModel):
    """Text improvement request schema."""

    text: str = Field(..., min_length=1, description="Text to improve")
    mode: TextMode = Field(..., description="Improvement mode")


class ImproveResponse(BaseModel):
    """Text improvement response schema."""

    text_original: str
    text_ai: str
    mode: TextMode
    tokens_used: int
    model: str


class ModesResponse(BaseModel):
    """Available improvement modes response schema."""

    modes: list[str] = Field(..., description="List of available mode identifiers")
    descriptions: dict[str, str] = Field(..., description="Descriptions for each mode")


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


# Error schemas
class ErrorResponse(BaseModel):
    """Error response schema."""

    detail: str
