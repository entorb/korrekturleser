"""Classes for different LLM providers."""

import logging
import random
from functools import lru_cache
from pathlib import Path

from .config import LLM_MODEL, LLM_PROVIDER
from .helper import where_am_i

logger = logging.getLogger(Path(__file__).stem)
ENV = where_am_i()


class LLMProvider:
    """Class for different LLM providers."""

    def __init__(self, instruction: str, model: str) -> None:
        """Init the LLM with model and context instruction."""
        self.provider = "NONE"
        self.instruction = instruction
        self.models = {"NONE"}
        self.model = model

    def check_model_valid(self, model: str) -> None:
        """Raise ValueError if model is not valid."""
        if model not in self.models:
            msg = (
                f"Model '{model}' is not a valid model for provider '{self.provider}'. "
                f"Valid models: {self.models}"
            )
            raise ValueError(msg)

    def print_llm_and_model(self) -> None:
        """Print out the LLM and the model."""
        s = f"LLM: {self.provider} {self.model}"
        print(s)
        logger.info(s)

    def call(self, prompt: str) -> tuple[str, int]:
        """
        Call the LLM with prompt.

        Returns a tuple containing the response text and the number of tokens consumed.
        """
        raise NotImplementedError


class MockProvider(LLMProvider):
    """Mocking LLM provider for local dev and tests."""

    def __init__(self, instruction: str, model: str) -> None:
        """Initialize Mock provider with instruction and model."""
        super().__init__(instruction, model)
        self.provider = "Mocked"
        self.models = {"random"}
        self.check_model_valid(model)

    def call(self, prompt: str) -> tuple[str, int]:
        """Call the LLM."""
        tokens = random.randint(50, 200)  # noqa: S311
        response = f"Mocked {prompt} response"
        return response, tokens


@lru_cache(maxsize=10)
def get_cached_llm_provider(
    provider_name: str = LLM_PROVIDER, model: str = LLM_MODEL, instruction: str = ""
) -> LLMProvider:
    """
    Get cached LLM provider.

    Uses @lru_cache to reuse the same provider instance across requests
    with the same parameters (provider, model, instruction).

    Args:
        provider_name: Name of the LLM provider to use
        model: Model name to use
        instruction: System instruction for the LLM

    Returns:
        An instance of LLMProvider

    Raises:
        ValueError: If the provider name is unknown
        ImportError: If the provider module cannot be imported

    """
    logger.debug("Getting LLM provider: %s, model: %s", provider_name, model)

    if provider_name == "Gemini":
        from .llm_provider_gemini import GeminiProvider  # noqa: PLC0415

        return GeminiProvider(instruction=instruction, model=model)

    if provider_name == "Mock":
        return MockProvider(instruction=instruction, model=model)

    if provider_name == "OpenAI_AzureDefaultAzureCredential":
        from .llm_provider_azure import AzureOpenAIProvider  # noqa: PLC0415

        return AzureOpenAIProvider(instruction=instruction, model=model)

    if provider_name == "OpenAI":
        from .llm_provider_openai import OpenAIProvider  # noqa: PLC0415

        return OpenAIProvider(instruction=instruction, model=model)

    if provider_name == "Ollama":
        from .llm_provider_ollama import OllamaProvider  # noqa: PLC0415

        return OllamaProvider(instruction=instruction, model=model)

    msg = f"Unknown LLM provider: {provider_name}"
    logger.error(msg)
    raise ValueError(msg)


if __name__ == "__main__":
    # run this file directly to test LLM providers
    # uv run python -m shared.llm_provider
    instruction = "Talk like a pirate. Give a short answer. "
    prompt = "What is the capital of Germany?"

    print(f"{ENV=}")

    llm_provider = get_cached_llm_provider(
        provider_name=LLM_PROVIDER, model=LLM_MODEL, instruction=instruction
    )
    llm_provider.print_llm_and_model()
    response, tokens = llm_provider.call(prompt)
    print(f"Response: {response}")
    print(f"Tokens: {tokens}")
