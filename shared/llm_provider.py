"""Classes for different LLM providers."""

import logging
import random
import time
from functools import lru_cache
from pathlib import Path

from .config import LLM_MODEL, LLM_PROVIDER
from .helper import my_get_env, where_am_i

logger = logging.getLogger(Path(__file__).stem)
ENV = where_am_i()


@lru_cache(maxsize=1)
def get_gemini_client():  # noqa: ANN201
    """Get cached Gemini client."""
    from google import genai  # pip install google-genai  # noqa: PLC0415

    api_key = my_get_env("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)


@lru_cache(maxsize=1)
def get_openai_client_default_azure_creds():  # noqa: ANN201
    """Create and return an Azure OpenAI client."""
    from azure.identity import (  # noqa: PLC0415
        DefaultAzureCredential,
        get_bearer_token_provider,
    )
    from openai import AzureOpenAI  # noqa: PLC0415

    return AzureOpenAI(
        api_version=my_get_env("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=my_get_env("AZURE_OPENAI_URL"),
        azure_ad_token_provider=get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        ),
    )


@lru_cache(maxsize=1)
def get_openai_client():  # noqa: ANN201
    """Create and return an OpenAI API client."""
    from openai import OpenAI  # noqa: PLC0415

    return OpenAI(api_key=my_get_env("OPENAI_API_KEY"))


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


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider."""

    def __init__(self, instruction: str, model: str) -> None:
        """Initialize Gemini provider with instruction and model."""
        super().__init__(instruction, model)
        self.provider = "Gemini"
        self.models = {
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash",
            "gemini-2.5-pro",
        }
        self.check_model_valid(model)

    def call(self, prompt: str) -> tuple[str, int]:
        """Call the LLM."""
        from google.genai import types as genai_types  # noqa: PLC0415

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


class AzureOpenAIProvider(LLMProvider):
    """Azure OpenAI LLM provider."""

    def __init__(self, instruction: str, model: str) -> None:
        """Initialize Azure OpenAI provider with instruction and model."""
        super().__init__(instruction, model)
        self.provider = "AzureOpenAI"
        self.models = {
            "gpt-5-nano",
            "gpt-5-mini",
            "gpt-5",
        }
        self.check_model_valid(model)

    def call(self, prompt: str) -> tuple[str, int]:
        """Call the LLM."""
        client = get_openai_client_default_azure_creds()
        messages = [
            {"role": "system", "content": self.instruction},
            {"role": "user", "content": prompt},
        ]
        response = None
        tokens = 0
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore
        )

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


class OpenAIProvider(LLMProvider):
    """OpenAI API LLM provider."""

    def __init__(self, instruction: str, model: str) -> None:
        """Initialize Azure OpenAI provider with instruction and model."""
        super().__init__(instruction, model)
        self.provider = "OpenAI"
        self.models = {
            "gpt-5-nano",
            "gpt-5-mini",
            "gpt-5",
        }
        self.check_model_valid(model)

    def call(self, prompt: str) -> tuple[str, int]:
        """Call the LLM."""
        client = get_openai_client()
        messages = [
            {"role": "system", "content": self.instruction},
            {"role": "user", "content": prompt},
        ]
        response = None
        tokens = 0
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore
        )

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


# Ollama available only locally, not on webserver
if LLM_PROVIDER == "Ollama" and ENV != "PROD":
    from ollama import ChatResponse, chat  # uv add --dev ollama

    class OllamaProvider(LLMProvider):
        """Ollama LLM provider for local models."""

        def __init__(self, instruction: str, model: str) -> None:
            """Initialize Ollama provider with instruction and model."""
            super().__init__(instruction, model)
            self.provider = "Ollama"
            self.models = {
                "llama3.2:1b",
                "llama3.2:3b",
                "deepseek-r1:1.5b",
                "deepseek-r1:8b",
                "deepseek-r1:7b",
            }
            self.check_model_valid(model)

        def call(self, prompt: str) -> tuple[str, int]:
            """Call the LLM."""
            response: ChatResponse = chat(
                model=self.model,
                stream=False,
                # think=True,
                messages=[
                    {"role": "system", "content": self.instruction},
                    {"role": "user", "content": prompt},
                ],
            )
            tokens = 0  # not returned by ollama
            return str(response.message.content), tokens


@lru_cache(maxsize=10)
def get_cached_llm_provider(
    provider_name: str = LLM_PROVIDER, model: str = LLM_MODEL, instruction: str = ""
) -> LLMProvider:
    """
    Get cached LLM provider.

    Uses @lru_cache to reuse the same provider instance across requests
    with the same parameters (provider, model, instruction).
    """
    if provider_name == "Gemini":
        return GeminiProvider(instruction=instruction, model=model)

    if provider_name == "Mock":
        return MockProvider(instruction=instruction, model=model)

    if provider_name == "OpenAI_AzureDefaultAzureCredential":
        return AzureOpenAIProvider(instruction=instruction, model=model)

    if provider_name == "OpenAI":
        return OpenAIProvider(instruction=instruction, model=model)

    if provider_name == "Ollama":
        return OllamaProvider(instruction=instruction, model=model)

    msg = f"Unknown LLM provider: {provider_name}"
    raise ValueError(msg)


if __name__ == "__main__":
    # run this file directly to test LLM providers
    # uv run python -m shared.llm_provider
    instruction = "Talk like a pirate. Give a short answer. "
    prompt = "What is the capital of Germany?"

    print(f"{ENV=}")

    # switch here
    if ENV != "PROD":
        llm_provider = get_cached_llm_provider(instruction=instruction)
        llm_provider.print_llm_and_model()
        print(llm_provider.call(prompt))
