"""OpenAI LLM provider class."""

import logging
from pathlib import Path
from typing import Any

from mistralai.client import Mistral
from mistralai.client.models.chatcompletionresponse import ChatCompletionResponse

from .helper import my_get_env
from .llm_provider import LLMProvider, retry_with_exponential_backoff

logger = logging.getLogger(Path(__file__).stem)

PROVIDER = "Mistral"
MODELS = [
    "mistral-medium-latest",
    "mistral-large-latest",
]


def get_mistral_client() -> Mistral:
    """Create and return an Mistral client."""
    return Mistral(api_key=my_get_env("MISTRAL_API_KEY"))


class MistralProvider(LLMProvider):
    """Mistral LLM provider."""

    def __init__(self) -> None:
        """Initialize OpenAI provider with instruction and model."""
        super().__init__(provider=PROVIDER, models=MODELS)

    def call(self, model: str, instruction: str, prompt: str) -> tuple[str, int]:
        """Call the LLM with retry logic."""
        self.check_model_valid(model)
        client = get_mistral_client()
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": instruction},
            {"role": "user", "content": prompt},
        ]

        def _api_call() -> ChatCompletionResponse:
            response = client.chat.complete(
                model=model,
                messages=messages,  # type: ignore
            )
            return response

        response = retry_with_exponential_backoff(_api_call, provider_name=PROVIDER)()

        s = str(response.choices[0].message.content) or ""
        tokens = 0
        if (
            hasattr(response, "usage")
            and response.usage
            and response.usage.total_tokens
        ):
            tokens = response.usage.total_tokens
        return s, tokens
