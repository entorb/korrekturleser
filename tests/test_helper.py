"""Tests for shared/helper.py."""

from unittest.mock import patch

import pytest

from shared import helper


class TestMyGetEnv:
    """Test environment variable access helper."""

    def test_missing_env_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        key = "TEST_MISSING_ENV_KEY"
        monkeypatch.delenv(key, raising=False)
        helper.my_get_env.cache_clear()
        with pytest.raises(ValueError, match="Environment variable"):
            helper.my_get_env(key)


class TestAutoLoginForLocalDev:
    """Test local development auto-login."""

    def test_logs_in_when_local_and_unauthenticated(self) -> None:
        calls = []

        def fake_login(user_id: int, user_name: str) -> None:
            calls.append((user_id, user_name))

        with patch("shared.helper.where_am_i", return_value="Local"):
            helper.auto_login_for_local_dev(
                is_authenticated_fn=lambda: False,
                login_fn=fake_login,
                user_id=1,
                user_name="Torben",
            )

        assert calls == [(1, "Torben")]

    def test_no_login_when_already_authenticated(self) -> None:
        def fail_login(*_args, **_kwargs) -> None:
            pytest.fail("login called")

        with patch("shared.helper.where_am_i", return_value="Local"):
            helper.auto_login_for_local_dev(
                is_authenticated_fn=lambda: True,
                login_fn=fail_login,
                user_id=1,
                user_name="Torben",
            )

    def test_no_login_in_production(self) -> None:
        def fail_login(*_args, **_kwargs) -> None:
            pytest.fail("login called")

        with patch("shared.helper.where_am_i", return_value="PROD"):
            helper.auto_login_for_local_dev(
                is_authenticated_fn=lambda: False,
                login_fn=fail_login,
                user_id=1,
                user_name="Torben",
            )
