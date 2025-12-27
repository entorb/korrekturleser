"""Ollama LLM provider class."""

import logging
from pathlib import Path

from ollama import ChatResponse, chat  # uv add --dev ollama

from .helper import where_am_i
from .llm_provider import LLMProvider, retry_with_exponential_backoff

logger = logging.getLogger(Path(__file__).stem)
ENV = where_am_i()

PROVIDER = "Ollama"
MODELS = {
    "llama3.2:1b",
    "llama3.2:3b",
    "deepseek-r1:1.5b",
    "deepseek-r1:8b",
    "deepseek-r1:7b",
}


class OllamaProvider(LLMProvider):
    """Ollama LLM provider for local models."""

    def __init__(self, instruction: str, model: str) -> None:
        """Initialize Ollama provider with instruction and model."""
        super().__init__(instruction, model)
        self.provider = PROVIDER
        self.models = MODELS
        self.check_model_valid(model)

    def call(self, prompt: str) -> tuple[str, int]:
        """Call the LLM with retry logic."""

        def _api_call() -> ChatResponse:
            response = chat(
                model=self.model,
                stream=False,
                # think=True,
                messages=[
                    {"role": "system", "content": self.instruction},
                    {"role": "user", "content": prompt},
                ],
            )
            return response

        response = retry_with_exponential_backoff(_api_call, provider_name=PROVIDER)()

        tokens = 0  # not returned by ollama
        return str(response.message.content), tokens
