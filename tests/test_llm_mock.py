"""Tests to verify that Mock LLM provider is used in tests."""

# ruff: noqa: PLR2004

import os

from shared.config import LLM_MODEL, LLM_PROVIDER
from shared.llm_provider import MockProvider, get_cached_llm_provider


class TestMockLLMProvider:
    """Test that Mock LLM provider is used in all tests."""

    def test_environment_variables_are_set(self) -> None:
        """Test that test environment variables are set correctly."""
        # Verify that the conftest.py fixture set these variables
        assert os.environ.get("LLM_PROVIDER") == "Mock"
        assert os.environ.get("LLM_MODEL") == "random"

    def test_config_uses_mock_provider(self) -> None:
        """Test that config module picks up Mock provider."""
        assert LLM_PROVIDER == "Mock"
        assert LLM_MODEL == "random"

    def test_llm_provider_is_mock_instance(self) -> None:
        """Test that get_cached_llm_provider returns MockProvider instance."""
        provider = get_cached_llm_provider(instruction="Test instruction")

        # Verify it's actually a MockProvider instance
        assert isinstance(provider, MockProvider)
        assert provider.provider == "Mocked"
        assert provider.model == "random"

    def test_mock_provider_returns_expected_format(self) -> None:
        """Test that MockProvider returns expected response format."""
        provider = get_cached_llm_provider(instruction="Test instruction")
        response_text, tokens_used = provider.call("Test prompt")

        # Verify response format
        assert isinstance(response_text, str)
        assert len(response_text) > 0
        assert "Mocked" in response_text  # Mock responses contain "Mocked"
        assert isinstance(tokens_used, int)
        assert 50 <= tokens_used <= 200  # Mock provider returns random tokens 50-200

    def test_mock_provider_never_makes_real_api_calls(self) -> None:
        """Test that MockProvider doesn't require API keys."""
        # If this was a real provider, it would fail without GEMINI_API_KEY
        # Mock provider should work regardless
        provider = MockProvider(instruction="Test", model="random")
        response_text, tokens_used = provider.call("Test prompt")

        # Should work without any API keys
        assert response_text is not None
        assert tokens_used > 0
