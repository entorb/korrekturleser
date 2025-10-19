"""Text improvement router for AI-powered text operations."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from fastapi_app.helper_fastapi import get_current_user
from fastapi_app.schemas import (
    ImproveRequest,
    ImproveResponse,
    ModesResponse,
    TextMode,
    UserInfoInternal,
)
from shared.config import (
    INSTRUCTION_CORRECT,
    INSTRUCTION_EXPAND,
    INSTRUCTION_IMPROVE,
    INSTRUCTION_SUMMARIZE,
    INSTRUCTION_TRANSLATE_DE,
    INSTRUCTION_TRANSLATE_EN,
    LLM_MODEL,
    LLM_PROVIDER,
)
from shared.helper import where_am_i
from shared.helper_db import db_insert_usage
from shared.llm_provider import get_cached_llm_provider

logger = logging.getLogger(__name__)

router = APIRouter()
ENV = where_am_i()

# Map modes to instructions
MODE_INSTRUCTIONS = {
    TextMode.CORRECT: INSTRUCTION_CORRECT,
    TextMode.IMPROVE: INSTRUCTION_IMPROVE,
    TextMode.SUMMARIZE: INSTRUCTION_SUMMARIZE,
    TextMode.EXPAND: INSTRUCTION_EXPAND,
    TextMode.TRANSLATE_DE: INSTRUCTION_TRANSLATE_DE,
    TextMode.TRANSLATE_EN: INSTRUCTION_TRANSLATE_EN,
}


@router.post("/")
async def improve_text(
    request: ImproveRequest,
    current_user: Annotated[UserInfoInternal, Depends(get_current_user)],
) -> ImproveResponse:
    """
    Improve text using AI based on the selected mode.

    Args:
        request: Text improvement request with text and mode
        current_user: Authenticated user (injected by dependency)

    Returns:
        ImproveResponse: Improved text and metadata

    Raises:
        HTTPException: If LLM processing fails

    """
    # Get instruction for mode
    instruction = MODE_INSTRUCTIONS.get(request.mode)
    if not instruction:
        raise HTTPException(status_code=400, detail=f"Invalid mode: {request.mode}")

    logger.debug(
        "User %s requested %s for text length %d",
        current_user.user_name,
        request.mode,
        len(request.text),
    )

    try:
        # Get LLM provider
        llm_provider = get_cached_llm_provider(
            provider_name=LLM_PROVIDER,
            model=LLM_MODEL,
            instruction=instruction,
        )

        # Call LLM
        improved_text, tokens_used = llm_provider.call(request.text)

        # Log usage in production
        if ENV == "PROD":
            db_insert_usage(user_id=current_user.user_id, tokens=tokens_used)

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
            model=LLM_MODEL,
        )

    except Exception as e:
        logger.exception("Error improving text")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to improve text: {e!s}",
        ) from e


@router.get("/modes")
async def get_modes() -> ModesResponse:
    """
    Get available improvement modes.

    Returns:
        ModesResponse with available modes and descriptions

    """
    return ModesResponse(
        modes=[mode.value for mode in TextMode],
        descriptions={
            "correct": "Korrigiere Grammatik und Rechtschreibung",
            "improve": "Verbessere den Text",
            "summarize": "Fasse den Text zu Stichwörtern zusammen",
            "expand": "Erstelle einen Text aus Stichwörtern",
            "translate_de": "Übersetzen -> DE",
            "translate_en": "Übersetzen -> EN",
        },
    )
