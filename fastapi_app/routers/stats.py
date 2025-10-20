"""Statistics router for usage tracking and reporting."""

import datetime as dt
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
    db_select_usage_stats_daily,
    db_select_usage_stats_total,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def get_all_stats(
    current_user: Annotated[UserInfoInternal, Depends(get_current_user)],
) -> UsageStatsResponse:
    """
    Get usage statistics (daily and total).

    - Admin (user_id=1): Returns stats for all users
    - Non-admin: Returns stats only for the current user (single row)
    - PROD: Queries database, Local: Returns mock data with all values set to 0

    Args:
        current_user: Authenticated user (injected by dependency)

    Returns:
        UsageStatsResponse: Daily and total usage statistics

    """
    if where_am_i() == "PROD":
        try:
            # Get daily statistics as list of rows
            # Admin gets all users, non-admin gets only their own data
            daily_df = db_select_usage_stats_daily(user_id=current_user.user_id)
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
            total_df = db_select_usage_stats_total(user_id=current_user.user_id)
            total_stats = [
                TotalUsage(
                    user_name=row["user_name"],
                    cnt_requests=row["cnt_requests"],
                    cnt_tokens=row["cnt_tokens"],
                )
                for _, row in total_df.iterrows()
            ]

            # For non-admin users, filter to only their own data
            if current_user.user_id != 1:
                daily_stats = [
                    stat
                    for stat in daily_stats
                    if stat.user_name == current_user.user_name
                ]
                total_stats = [
                    stat
                    for stat in total_stats
                    if stat.user_name == current_user.user_name
                ]

            logger.debug("User %s accessed usage statistics", current_user.user_name)

            return UsageStatsResponse(daily=daily_stats, total=total_stats)

        except Exception as e:
            logger.exception("Error fetching usage stats")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch usage statistics: {e!s}",
            ) from e
    else:
        # Local mode: return mock data for current user
        today = dt.datetime.now(dt.UTC).date()
        daily_stats = [
            DailyUsage(
                date=today,
                user_name=current_user.user_name,
                cnt_requests=0,
                cnt_tokens=0,
            )
        ]
        total_stats = [
            TotalUsage(
                user_name=current_user.user_name,
                cnt_requests=0,
                cnt_tokens=0,
            )
        ]

        return UsageStatsResponse(daily=daily_stats, total=total_stats)
