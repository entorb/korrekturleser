"""Tests for shared/helper_db.py database functions."""

# ruff: noqa: PLR2004

import datetime as dt
from unittest.mock import MagicMock, patch

import mysql.connector
import pandas as pd
import pytest

from shared.helper_db import (
    db_insert_usage,
    db_select_usage_stats_daily,
    db_select_usage_stats_total,
    db_select_user_from_geheimnis,
)


class TestAuthentication:
    """Test user authentication functions."""

    def test_valid_credentials(self) -> None:
        """Test successful authentication with valid credentials."""
        user_id, username = db_select_user_from_geheimnis("test")

        assert user_id == 1
        assert username == "Torben"

    def test_invalid_credentials(self) -> None:
        """Test authentication fails with wrong password."""
        user_id, username = db_select_user_from_geheimnis("wrong_password")

        assert user_id == 0
        assert username == ""

    @patch("shared.helper_db.ENV", "PROD")
    @patch("shared.helper_db.db_select_rows")
    def test_authentication_database_error(self, mock_db_select: MagicMock) -> None:
        """Test that database errors are propagated."""
        mock_db_select.side_effect = mysql.connector.Error("Connection failed")

        with pytest.raises(mysql.connector.Error, match="Connection failed"):
            db_select_user_from_geheimnis("test")


class TestUsageTracking:
    """Test usage tracking functions."""

    def test_insert_usage_mock_mode(self) -> None:
        """Test usage insert is a no-op in mock mode."""
        db_insert_usage(user_id=1, tokens=100)

    @patch("shared.helper_db.ENV", "PROD")
    @patch("shared.helper_db.db_connection")
    def test_insert_usage_in_production(self, mock_connection: MagicMock) -> None:
        """Test usage insert writes to database in PROD mode."""
        mock_con = MagicMock()
        mock_cursor = MagicMock()
        mock_con.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connection.return_value.__enter__.return_value = mock_con

        db_insert_usage(user_id=1, tokens=100)

        assert mock_cursor.execute.called
        assert mock_con.commit.called

        call_args = mock_cursor.execute.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        assert "INSERT INTO history" in query
        assert "ON DUPLICATE KEY UPDATE" in query
        assert params[0] == dt.date.today()  # noqa: DTZ011
        assert params[1] == 1
        assert params[2] == 100


class TestUsageStats:
    """Test usage statistics functions."""

    def test_stats_total_returns_empty_dataframe(self) -> None:
        """Test stats query returns empty DataFrame in mock mode."""
        df = db_select_usage_stats_total(user_id=1)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert list(df.columns) == ["user_name", "cnt_requests", "cnt_tokens"]

    def test_stats_daily_returns_empty_dataframe(self) -> None:
        """Test daily stats returns empty DataFrame in mock mode."""
        df = db_select_usage_stats_daily(user_id=1)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert list(df.columns) == ["date", "user_name", "cnt_requests", "cnt_tokens"]
