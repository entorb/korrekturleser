"""Tests to verify that Mock LLM provider is used in tests."""

# ruff: noqa: PLR2004

import os

from shared.config import LLM_PROVIDER_DEFAULT
from shared.llm_provider import MockProvider, get_llm_provider

MOCK_PROVIDER = "Mock"
MOCK_MODEL = "random"


class TestMockLLMProvider:
    """Test that Mock LLM provider is used in all tests."""

    def test_environment_variables_are_set(self) -> None:
        """Test that test environment variables are set correctly."""
        # Verify that the conftest.py fixture set these variables
        assert os.environ.get("LLM_PROVIDERS") == MOCK_PROVIDER
        assert os.environ.get("LLM_MODEL") == MOCK_MODEL

    def test_config_uses_mock_provider(self) -> None:
        """Test that config module picks up Mock provider."""
        assert LLM_PROVIDER_DEFAULT == "Mock"

    def test_llm_provider_is_mock_instance(self) -> None:
        """Test that get_cached_llm_provider returns MockProvider instance."""
        provider = get_llm_provider(provider_name=LLM_PROVIDER_DEFAULT)

        # Verify it's actually a MockProvider instance
        assert isinstance(provider, MockProvider)

    def test_mock_provider_returns_expected_format(self) -> None:
        """Test that MockProvider returns expected response format."""
        provider = get_llm_provider(provider_name=LLM_PROVIDER_DEFAULT)
        assert isinstance(provider, MockProvider)
        response_text, tokens_used = provider.call(
            "model", "instruction", "Test prompt"
        )

        # Verify response format
        assert response_text is not None
        assert tokens_used > 0
        assert isinstance(response_text, str)
        assert len(response_text) > 0
        assert "Mocked" in response_text  # Mock responses contain "Mocked"
        assert isinstance(tokens_used, int)
        assert 50 <= tokens_used <= 200  # Mock provider returns random tokens 50-200
