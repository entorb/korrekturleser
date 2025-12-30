"""Configuration router for app settings."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from fastapi_app.helper_fastapi import get_current_user
from fastapi_app.schemas import ConfigResponse, UserInfoInternal
from shared.config import LLM_PROVIDER
from shared.llm_provider import get_llm_provider

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def get_config(
    _: Annotated[UserInfoInternal, Depends(get_current_user)],
) -> ConfigResponse:
    """
    Get application configuration.

    Returns:
        ConfigResponse: Current LLM provider and available models

    """
    llm_provider = get_llm_provider(LLM_PROVIDER)
    return ConfigResponse(llm_provider=LLM_PROVIDER, models=llm_provider.get_models())
