"""Tests for shared/helper_db.py database functions."""

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

    @patch("shared.helper_db.sqlite_connection")
    def test_valid_credentials(self, mock_sqlite: MagicMock) -> None:
        """Test successful authentication with valid credentials."""
        # Mock SQLite cursor
        mock_con = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (
                1,
                "Torben",
                "$2b$12$YDgoJlHlpKxHRpum1b1rt.c06YscNeMhcMVaxH2wWNbsCsDouY2/a",
            )
        ]
        mock_con.cursor.return_value = mock_cursor
        mock_sqlite.return_value.__enter__.return_value = mock_con

        user_id, username = db_select_user_from_geheimnis("test")

        assert user_id == 1
        assert username == "Torben"

    @patch("shared.helper_db.sqlite_connection")
    def test_invalid_credentials(self, mock_sqlite: MagicMock) -> None:
        """Test authentication fails with wrong password."""
        # Mock SQLite cursor
        mock_con = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (
                1,
                "Torben",
                "$2b$12$YDgoJlHlpKxHRpum1b1rt.c06YscNeMhcMVaxH2wWNbsCsDouY2/a",
            )
        ]
        mock_con.cursor.return_value = mock_cursor
        mock_sqlite.return_value.__enter__.return_value = mock_con

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

    def test_insert_usage_mocked_llm(self) -> None:
        """Test usage insert is skipped when LLM is mocked."""
        # Should not raise any errors and should return early
        db_insert_usage(user_id=1, tokens=100)

    @patch("shared.helper_db.sqlite_connection")
    def test_insert_usage_local_mode(self, mock_sqlite: MagicMock) -> None:
        """Test usage insert writes to SQLite in local mode."""
        mock_con = MagicMock()
        mock_cursor = MagicMock()
        mock_con.cursor.return_value = mock_cursor
        mock_sqlite.return_value.__enter__.return_value = mock_con

        db_insert_usage(user_id=1, tokens=100)

        assert mock_cursor.execute.called
        assert mock_con.commit.called

        call_args = mock_cursor.execute.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        assert "INSERT INTO history" in query
        assert "ON CONFLICT" in query
        assert params[0] == dt.date.today().isoformat()  # noqa: DTZ011
        assert params[1] == 1
        assert params[2] == 100

    @patch("shared.helper_db.ENV", "PROD")
    @patch("shared.helper_db.db_connection")
    def test_insert_usage_in_production(self, mock_connection: MagicMock) -> None:
        """Test usage insert writes to MySQL in PROD mode."""
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

    @patch("shared.helper_db.sqlite_connection")
    def test_stats_total_returns_dataframe(self, mock_sqlite: MagicMock) -> None:
        """Test stats query returns DataFrame from SQLite in local mode."""
        mock_con = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("Torben", 10, 5000)]
        mock_con.cursor.return_value = mock_cursor
        mock_sqlite.return_value.__enter__.return_value = mock_con

        df = db_select_usage_stats_total(user_id=1)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert list(df.columns) == ["user_name", "cnt_requests", "cnt_tokens"]
        assert df.iloc[0]["user_name"] == "Torben"
        assert df.iloc[0]["cnt_requests"] == 10
        assert df.iloc[0]["cnt_tokens"] == 5000

    @patch("shared.helper_db.sqlite_connection")
    def test_stats_total_empty_result(self, mock_sqlite: MagicMock) -> None:
        """Test stats query returns empty DataFrame when no data."""
        mock_con = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_con.cursor.return_value = mock_cursor
        mock_sqlite.return_value.__enter__.return_value = mock_con

        df = db_select_usage_stats_total(user_id=1)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert list(df.columns) == ["user_name", "cnt_requests", "cnt_tokens"]

    @patch("shared.helper_db.sqlite_connection")
    def test_stats_daily_returns_dataframe(self, mock_sqlite: MagicMock) -> None:
        """Test daily stats returns DataFrame from SQLite in local mode."""
        mock_con = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("2025-12-01", "Torben", 5, 2500)]
        mock_con.cursor.return_value = mock_cursor
        mock_sqlite.return_value.__enter__.return_value = mock_con

        df = db_select_usage_stats_daily(user_id=1)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert list(df.columns) == ["date", "user_name", "cnt_requests", "cnt_tokens"]
        assert df.iloc[0]["date"] == "2025-12-01"
        assert df.iloc[0]["user_name"] == "Torben"

    @patch("shared.helper_db.sqlite_connection")
    def test_stats_daily_empty_result(self, mock_sqlite: MagicMock) -> None:
        """Test daily stats returns empty DataFrame when no data."""
        mock_con = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_con.cursor.return_value = mock_cursor
        mock_sqlite.return_value.__enter__.return_value = mock_con

        df = db_select_usage_stats_daily(user_id=1)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert list(df.columns) == ["date", "user_name", "cnt_requests", "cnt_tokens"]
