"""Gemini LLM provider class."""

import logging
from functools import lru_cache
from pathlib import Path

from google.genai import types as genai_types
from google.genai.client import Client
from google.genai.types import GenerateContentResponse

from .helper import my_get_env
from .llm_provider import LLMProvider, retry_with_exponential_backoff

logger = logging.getLogger(Path(__file__).stem)

PROVIDER = "Gemini"
MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
]


@lru_cache(maxsize=1)
def get_gemini_client() -> Client:
    """Get cached Gemini client."""
    from google import genai  # pip install google-genai  # noqa: PLC0415

    api_key = my_get_env("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider."""

    def __init__(self) -> None:
        """Initialize Gemini provider with instruction and model."""
        super().__init__(provider=PROVIDER, models=MODELS)

    def call(self, model: str, instruction: str, prompt: str) -> tuple[str, int]:
        """Call the LLM with retry logic."""
        self.check_model_valid(model)
        client = get_gemini_client()

        def _api_call() -> GenerateContentResponse:
            response = client.models.generate_content(
                model=model,
                config=genai_types.GenerateContentConfig(
                    system_instruction=instruction
                ),
                contents=prompt,
            )
            return response

        response = retry_with_exponential_backoff(_api_call, provider_name=PROVIDER)()

        if (
            response
            and response.usage_metadata
            and response.usage_metadata.total_token_count
        ):
            tokens = response.usage_metadata.total_token_count
        else:
            logger.warning("No token consumption retrieved.")
            tokens = 0

        s = str(response.text) if response else ""
        return s, tokens
