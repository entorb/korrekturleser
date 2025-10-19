"""Statistics router for usage tracking and reporting."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from fastapi_app.helper_fastapi import get_current_user
from fastapi_app.schemas import (
    DailyUsage,
    TotalUsage,
    UsageStatsResponse,
    UserInfoInternal,
)
from shared.helper import where_am_i
from shared.helper_db import (
    db_select_usage_of_user,
    db_select_usage_stats_daily,
    db_select_usage_stats_total,
)

logger = logging.getLogger(__name__)

router = APIRouter()
ENV = where_am_i()


@router.get("/")
async def get_usage_stats(
    current_user: Annotated[UserInfoInternal, Depends(get_current_user)],
) -> UsageStatsResponse:
    """
    Get usage statistics (daily and total).

    Only available in PROD environment and only for user_id=1 (admin).

    Args:
        current_user: Authenticated user (injected by dependency)

    Returns:
        UsageStatsResponse: Daily and total usage statistics

    Raises:
        HTTPException: If not in PROD or user is not admin

    """
    # Restrict to admin user (same as Streamlit app)
    if current_user.user_id != 1:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Statistics only available for admin user.",
        )

    if ENV != "PROD":
        raise HTTPException(
            status_code=503,
            detail="Statistics only available in production environment",
        )

    try:
        # Get daily statistics as list of rows
        daily_df = db_select_usage_stats_daily()
        daily_stats = [
            DailyUsage(
                date=row["date"],
                user_name=row["user_name"],
                cnt_requests=row["cnt_requests"],
                cnt_tokens=row["cnt_tokens"],
            )
            for _, row in daily_df.iterrows()
        ]

        # Get total statistics as list of rows
        total_df = db_select_usage_stats_total()
        total_stats = [
            TotalUsage(
                user_name=row["user_name"],
                total_requests=row["cnt_requests"],
                total_tokens=row["cnt_tokens"],
            )
            for _, row in total_df.iterrows()
        ]

        logger.debug("User %s accessed usage statistics", current_user.user_name)

        return UsageStatsResponse(daily=daily_stats, total=total_stats)

    except Exception as e:
        logger.exception("Error fetching usage stats")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch usage statistics: {e!s}",
        ) from e


@router.get("/my-usage")
async def get_my_usage(
    current_user: Annotated[UserInfoInternal, Depends(get_current_user)],
) -> dict[str, int | str]:
    """
    Get current user's usage statistics.

    Args:
        current_user: Authenticated user (injected by dependency)

    Returns:
        Dictionary with user's request and token counts

    """
    try:
        cnt_requests, cnt_tokens = db_select_usage_of_user(user_id=current_user.user_id)
    except Exception as e:
        logger.exception("Error fetching user usage")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch user usage: {e!s}",
        ) from e
    else:
        return {
            "user_name": current_user.user_name,
            "total_requests": cnt_requests,
            "total_tokens": cnt_tokens,
        }
