"""Tests for shared/llm_provider.py retry and provider logic."""

from unittest.mock import patch

import pytest

from shared.llm_provider import (
    LLMProvider,
    MockProvider,
    get_llm_provider,
    retry_with_exponential_backoff,
)


def test_retry_succeeds_after_transient_failure() -> None:
    """Function failing once succeeds on retry with backoff."""
    calls = {"count": 0}

    def flaky() -> str:
        calls["count"] += 1
        if calls["count"] == 1:
            msg = "boom"
            raise ConnectionError(msg)
        return "ok"

    with patch("shared.llm_provider.time.sleep") as mock_sleep:
        result = retry_with_exponential_backoff(flaky)()

    assert result == "ok"
    assert calls["count"] == 2
    mock_sleep.assert_called_once_with(1)


def test_retry_exhausts_attempts_and_raises() -> None:
    """Function failing always raises after max_retries attempts."""
    attempts = {"count": 0}

    def always_fails() -> None:
        attempts["count"] += 1
        msg = "always"
        raise ConnectionError(msg)

    with (
        patch("shared.llm_provider.time.sleep") as mock_sleep,
        pytest.raises(ConnectionError, match="always"),
    ):
        retry_with_exponential_backoff(always_fails, max_retries=3)()

    assert attempts["count"] == 3
    # backoff sleeps: 1s then 2s (2^0, 2^1)
    assert [call.args[0] for call in mock_sleep.call_args_list] == [1, 2]


def test_retry_no_sleep_on_first_success() -> None:
    """Successful first attempt does not sleep."""
    with patch("shared.llm_provider.time.sleep") as mock_sleep:
        result = retry_with_exponential_backoff(lambda: "ok")()

    assert result == "ok"
    mock_sleep.assert_not_called()


def test_retry_zero_max_retries_raises_runtime_error() -> None:
    """max_retries=0 falls through to the guard RuntimeError."""

    def func() -> None:
        msg = "never called"
        raise AssertionError(msg)

    with pytest.raises(RuntimeError, match="retry logic failed unexpectedly"):
        retry_with_exponential_backoff(func, max_retries=0)()


class TestLLMProvider:
    """Test the base LLMProvider class."""

    def test_check_model_valid_accepts_known_model(self) -> None:
        provider = LLMProvider(provider="Test", models=["a", "b"])
        provider.check_model_valid("a")

    def test_check_model_valid_rejects_unknown_model(self) -> None:
        provider = LLMProvider(provider="Test", models=["a", "b"])
        with pytest.raises(ValueError, match="not a valid model"):
            provider.check_model_valid("c")

    def test_get_models_returns_list(self) -> None:
        provider = LLMProvider(provider="Test", models=["a", "b"])
        assert provider.get_models() == ["a", "b"]

    def test_call_not_implemented(self) -> None:
        provider = LLMProvider(provider="Test", models=["a"])
        with pytest.raises(NotImplementedError):
            provider.call("a", "instr", "prompt")


class TestMockProvider:
    """Test the MockProvider."""

    def test_mock_provider_configuration(self) -> None:
        provider = MockProvider()
        assert provider.provider == "Mocked"
        assert provider.get_models() == ["random"]


class TestGetLLMProvider:
    """Test the provider factory."""

    def test_unknown_provider_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown LLM provider"):
            get_llm_provider("NotAProvider")
