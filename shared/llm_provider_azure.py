"""Azure LLM provider class."""

import logging
import time
from functools import lru_cache
from pathlib import Path

from azure.identity import (
    DefaultAzureCredential,
    get_bearer_token_provider,
)
from openai import AzureOpenAI

from .helper import my_get_env, where_am_i
from .llm_provider import LLMProvider

logger = logging.getLogger(Path(__file__).stem)
ENV = where_am_i()

PROVIDER = "AzureOpenAI"
MODELS = {
    "gpt-5-nano",
    "gpt-5-mini",
    "gpt-5",
}


@lru_cache(maxsize=1)
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

    def __init__(self, instruction: str, model: str) -> None:
        """Initialize Azure OpenAI provider with instruction and model."""
        super().__init__(instruction, model)
        self.provider = PROVIDER
        self.models = MODELS
        self.check_model_valid(model)

    def call(self, prompt: str) -> tuple[str, int]:
        """Call the LLM with retry logic."""
        client = get_openai_client_default_azure_creds()
        messages = [
            {"role": "system", "content": self.instruction},
            {"role": "user", "content": prompt},
        ]
        response = None
        tokens = 0
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,  # type: ignore
                )
                break  # Exit retry loop if successful
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2**attempt
                    logger.warning(
                        "Azure OpenAI API error, retrying in %d seconds "
                        "(attempt %d/%d): %s",
                        wait_time,
                        attempt + 1,
                        max_retries,
                        str(e),
                    )
                    time.sleep(wait_time)
                else:
                    logger.exception(
                        "Azure OpenAI API failed after %d attempts", max_retries
                    )
                    raise
        assert response is not None
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
