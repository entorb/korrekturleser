"""OpenAI LLM provider class."""

import logging
from pathlib import Path

from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

from .helper import my_get_env
from .llm_provider import LLMProvider, retry_with_exponential_backoff

logger = logging.getLogger(Path(__file__).stem)

PROVIDER = "OpenAI"
MODELS = [
    "gpt-5-nano",
    "gpt-5-mini",
    "gpt-5",
]


def get_openai_client() -> OpenAI:
    """Create and return an OpenAI client."""
    return OpenAI(api_key=my_get_env("OPENAI_API_KEY"))


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""

    def __init__(self) -> None:
        """Initialize OpenAI provider with instruction and model."""
        super().__init__(provider=PROVIDER, models=MODELS)

    def call(self, model: str, instruction: str, prompt: str) -> tuple[str, int]:
        """Call the LLM with retry logic."""
        self.check_model_valid(model)
        client = get_openai_client()
        messages = [
            {"role": "system", "content": instruction},
            {"role": "user", "content": prompt},
        ]

        def _api_call() -> ChatCompletion:
            response = client.chat.completions.create(
                model=model,
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
