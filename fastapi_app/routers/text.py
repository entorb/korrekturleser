"""Text improvement router for AI-powered text operations."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from fastapi_app.helper_fastapi import get_current_user
from fastapi_app.schemas import (
    ImproveRequest,
    ImproveResponse,
    ModelsResponse,
    UserInfoInternal,
)
from shared.config import LLM_PROVIDER
from shared.helper_ai import MODE_CONFIGS
from shared.helper_db import db_insert_usage
from shared.llm_provider import get_llm_provider

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/models")
async def get_available_models(
    _: Annotated[UserInfoInternal, Depends(get_current_user)],
) -> ModelsResponse:
    """Get available LLM models for the current provider."""
    try:
        llm_provider = get_llm_provider(LLM_PROVIDER)
        models = llm_provider.get_models()
        return ModelsResponse(models=models, provider=LLM_PROVIDER)
    except (ValueError, ImportError) as e:
        msg = "Failed to get LLM provider:"
        logger.exception(msg)
        raise HTTPException(
            status_code=500, detail="LLM service is not properly configured"
        ) from e


@router.post("/")
async def improve_text(
    request: ImproveRequest,
    current_user: Annotated[UserInfoInternal, Depends(get_current_user)],
) -> ImproveResponse:
    """Improve text using AI based on the selected mode."""
    # Validate input
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    # Get instruction for mode
    mode_config = MODE_CONFIGS.get(request.mode)
    if not mode_config:
        raise HTTPException(status_code=400, detail=f"Invalid mode: {request.mode}")

    instruction = mode_config.instruction

    logger.debug(
        "User %s requested %s for text length %d",
        current_user.user_name,
        request.mode,
        len(request.text),
    )

    try:
        # Get LLM provider with explicit error handling
        try:
            llm_provider = get_llm_provider(LLM_PROVIDER)
            models = llm_provider.get_models()
            # Use model from request, or default to first available
            model = (
                request.model
                if request.model and request.model in models
                else models[0]
            )
        except (ValueError, ImportError) as e:
            msg = "Failed to get LLM provider:"
            logger.exception(msg)
            raise HTTPException(
                status_code=500, detail="LLM service is not properly configured"
            ) from e

        # Call LLM with timeout protection (if using async)
        improved_text, tokens_used = llm_provider.call(
            model=model, instruction=instruction, prompt=request.text
        )

        # Validate response
        if not improved_text:
            msg = "LLM returned empty response"
            raise ValueError(msg)  # noqa: TRY301

        try:
            db_insert_usage(user_id=current_user.user_id, tokens=tokens_used)
        except Exception:
            logger.exception("Failed to log usage:")

        logger.debug(
            "Successfully improved text for %s, used %d tokens",
            current_user.user_name,
            tokens_used,
        )

        return ImproveResponse(
            text_original=request.text,
            text_ai=improved_text,
            mode=request.mode,
            tokens_used=tokens_used,
            model=model,
            provider=LLM_PROVIDER,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error improving text")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to improve text: {e!s}",
        ) from e
