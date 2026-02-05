"""Azure LLM provider class."""

import logging
from pathlib import Path

from azure.identity import (
    DefaultAzureCredential,
    get_bearer_token_provider,
)
from openai import AzureOpenAI
from openai.types.chat.chat_completion import ChatCompletion

from .helper import my_get_env
from .llm_provider import LLMProvider, retry_with_exponential_backoff

logger = logging.getLogger(Path(__file__).stem)

PROVIDER = "AzureOpenAI"
MODELS = [
    "gpt-5-nano",
    "gpt-5-mini",
    "gpt-5",
]


def get_openai_client_default_azure_creds() -> AzureOpenAI:
    """Create and return an Azure OpenAI client."""
    return AzureOpenAI(
        api_version=my_get_env("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=my_get_env("AZURE_OPENAI_URL"),
        azure_ad_token_provider=get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        ),
    )


class AzureOpenAIProvider(LLMProvider):
    """Azure OpenAI LLM provider."""

    def __init__(self) -> None:
        """Initialize Azure OpenAI provider with instruction and model."""
        super().__init__(provider=PROVIDER, models=MODELS)

    def call(self, model: str, instruction: str, prompt: str) -> tuple[str, int]:
        """Call the LLM with retry logic."""
        self.check_model_valid(model)
        client = get_openai_client_default_azure_creds()
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

        s = response.choices[0].message.content or ""
        tokens = (
            response.usage.total_tokens
            if hasattr(response, "usage") and response.usage
            else 0
        )
        return s, tokens
