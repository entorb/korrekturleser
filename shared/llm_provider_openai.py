"""OpenAI LLM provider class."""

import logging
from functools import lru_cache
from pathlib import Path

from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

from .helper import my_get_env, where_am_i
from .llm_provider import LLMProvider, retry_with_exponential_backoff

logger = logging.getLogger(Path(__file__).stem)
ENV = where_am_i()

PROVIDER = "OpenAI"
MODELS = {
    "gpt-5-nano",
    "gpt-5-mini",
    "gpt-5",
}


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    """Create and return an OpenAI client."""
    return OpenAI(api_key=my_get_env("OPENAI_API_KEY"))


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""

    def __init__(self, instruction: str, model: str) -> None:
        """Initialize OpenAI provider with instruction and model."""
        super().__init__(instruction, model)
        self.provider = PROVIDER
        self.models = MODELS
        self.check_model_valid(model)

    def call(self, prompt: str) -> tuple[str, int]:
        """Call the LLM with retry logic."""
        client = get_openai_client()
        messages = [
            {"role": "system", "content": self.instruction},
            {"role": "user", "content": prompt},
        ]

        def _api_call() -> ChatCompletion:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore
            )
            return response

        response = retry_with_exponential_backoff(_api_call, provider_name=PROVIDER)()

        s = (
            response.choices[0].message.content
            if response.choices[0].message.content
            else ""
        )
        tokens = (
            response.usage.total_tokens
            if hasattr(response, "usage") and response.usage
            else 0
        )
        return s, tokens
