"""Configuration router for app settings."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from fastapi_app.helper_fastapi import get_current_user
from fastapi_app.schemas import ConfigResponse, UserInfoInternal
from shared.config import LLM_PROVIDER_DEFAULT, LLM_PROVIDERS
from shared.llm_provider import get_llm_provider

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def get_config(
    _: Annotated[UserInfoInternal, Depends(get_current_user)],
    provider: str | None = None,
) -> ConfigResponse:
    """
    Get application configuration.

    Args:
        provider: Optional provider to get config for, defaults to default provider

    Returns:
        ConfigResponse: Current LLM provider, available models, and all providers

    """
    selected_provider = provider if provider else LLM_PROVIDER_DEFAULT
    llm_provider = get_llm_provider(selected_provider)
    return ConfigResponse(
        provider=selected_provider,
        models=llm_provider.get_models(),
        providers=LLM_PROVIDERS,
    )
