"""Gemini LLM provider class."""

import logging
import time
from functools import lru_cache
from pathlib import Path

from google.genai import types as genai_types
from google.genai.client import Client

from .helper import my_get_env, where_am_i
from .llm_provider import LLMProvider

logger = logging.getLogger(Path(__file__).stem)
ENV = where_am_i()

PROVIDER = "Gemini"
MODELS = {
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
}


@lru_cache(maxsize=1)
def get_gemini_client() -> Client:
    """Get cached Gemini client."""
    from google import genai  # pip install google-genai  # noqa: PLC0415

    api_key = my_get_env("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider."""

    def __init__(self, instruction: str, model: str) -> None:
        """Initialize Gemini provider with instruction and model."""
        super().__init__(instruction, model)
        self.provider = PROVIDER
        self.models = MODELS
        self.check_model_valid(model)

    def call(self, prompt: str) -> tuple[str, int]:
        """Call the LLM."""
        assert self.instruction is not None

        client = get_gemini_client()

        response = None
        tokens = 0
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=self.model,
                    config=genai_types.GenerateContentConfig(
                        system_instruction=self.instruction
                    ),
                    contents=prompt,
                )
                break  # Exit retry loop if successful
            except Exception as e:
                if attempt < max_retries - 1 and "The model is overloaded" in str(e):
                    wait_time = 2**attempt
                    logger.warning(
                        "Model overloaded, retrying in %d seconds (attempt %d/%d)...",
                        wait_time,
                        attempt + 1,
                        max_retries,
                    )
                    time.sleep(wait_time)
                else:
                    raise

        if (
            response
            and response.usage_metadata
            and response.usage_metadata.total_token_count
        ):
            logger.debug(
                "tokens: %d prompt + %d candidates = %d",
                response.usage_metadata.prompt_token_count,
                response.usage_metadata.candidates_token_count,
                response.usage_metadata.total_token_count,
            )
            tokens = response.usage_metadata.total_token_count
        else:
            logger.warning("No token consumption retrieved.")
        s = str(response.text) if response else ""
        return s, tokens
