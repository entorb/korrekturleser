"""Ollama LLM provider class."""

import logging
from pathlib import Path

from ollama import ChatResponse, chat  # uv add --dev ollama

from .llm_provider import LLMProvider, retry_with_exponential_backoff

logger = logging.getLogger(Path(__file__).stem)

PROVIDER = "Ollama"
MODELS = [
    "mistral",
    "llama3.2:1b",
    "llama3.2:3b",
    "deepseek-r1:1.5b",
    "deepseek-r1:8b",
    "deepseek-r1:7b",
]


class OllamaProvider(LLMProvider):
    """Ollama LLM provider for local models."""

    def __init__(self) -> None:
        """Initialize Ollama provider with instruction and model."""
        super().__init__(provider=PROVIDER, models=MODELS)

    def call(self, model: str, instruction: str, prompt: str) -> tuple[str, int]:
        """Call the LLM with retry logic."""
        self.check_model_valid(model)

        def _api_call() -> ChatResponse:
            response = chat(
                model=model,
                stream=False,
                messages=[
                    {"role": "system", "content": instruction},
                    {"role": "user", "content": prompt},
                ],
            )
            return response

        response = retry_with_exponential_backoff(_api_call, provider_name=PROVIDER)()

        tokens = 0  # not returned by ollama
        return str(response.message.content), tokens
