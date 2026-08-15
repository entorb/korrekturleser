"""Tests for shared/helper_db.py database functions."""

import datetime as dt
import sqlite3
from unittest.mock import MagicMock, patch

import mysql.connector
import pandas as pd
import pytest

from shared import helper_db
from shared.helper_db import (
    MOCK_USER_SECRET_HASH,
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

    @patch("shared.helper_db.ENV", "PROD")
    @patch("shared.helper_db.db_select_rows")
    def test_authentication_prod_path(self, mock_db_select: MagicMock) -> None:
        """Test production path fetches and verifies rows from MySQL."""
        mock_db_select.return_value = [("1", "Torben", MOCK_USER_SECRET_HASH)]

        user_id, username = db_select_user_from_geheimnis("test")

        assert user_id == 1
        assert username == "Torben"
        mock_db_select.assert_called_once_with(
            query="SELECT id, name, secret_hashed FROM user ORDER BY id",
            param=(),
        )


class TestUsageTracking:
    """Test usage tracking functions."""

    def test_insert_usage_mocked_llm(self) -> None:
        """Test usage insert is skipped when LLM is mocked."""
        # Should not raise any errors and should return early
        db_insert_usage(user_id=1, tokens=100)

    @patch("shared.helper_db.sqlite_connection")
    def test_insert_usage_skipped_when_llm_mocked(self, mock_sqlite: MagicMock) -> None:
        """Test usage insert is skipped when default provider is 'Mocked'."""
        with patch("shared.helper_db.LLM_PROVIDER_DEFAULT", "Mocked"):
            db_insert_usage(user_id=1, tokens=100)
        mock_sqlite.assert_not_called()

    def test_insert_usage_sqlite_error_reraises(
        self, tmp_path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """SQLite write errors during usage insert are propagated."""
        db_path = tmp_path / "db.sqlite"
        monkeypatch.setattr(helper_db, "SQLITE_DB_PATH", db_path)
        monkeypatch.setattr(helper_db, "LLM_PROVIDER_DEFAULT", "Mistral")
        helper_db.init_sqlite_db()

        def boom(*_args, **_kwargs) -> None:
            msg = "write failed"
            raise sqlite3.Error(msg)

        monkeypatch.setattr(helper_db.sqlite3, "connect", boom)

        with pytest.raises(sqlite3.Error, match="write failed"):
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


class TestSQLiteDatabase:
    """Tests against a real SQLite database in a temp directory."""

    def test_init_sqlite_db_creates_schema(
        self, tmp_path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Database is created with user/history tables and mock user."""
        db_path = tmp_path / "db.sqlite"
        monkeypatch.setattr(helper_db, "SQLITE_DB_PATH", db_path)

        helper_db.init_sqlite_db()

        assert db_path.exists()
        con = sqlite3.connect(db_path)
        tables = {
            row[0]
            for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        assert {"user", "history"} <= tables
        assert con.execute("SELECT id, name FROM user").fetchone() == (1, "Torben")
        con.close()

    def test_init_sqlite_db_idempotent(
        self, tmp_path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Calling init again on an existing database is a no-op."""
        db_path = tmp_path / "db.sqlite"
        monkeypatch.setattr(helper_db, "SQLITE_DB_PATH", db_path)
        helper_db.init_sqlite_db()

        helper_db.init_sqlite_db()

        con = sqlite3.connect(db_path)
        rows = con.execute("SELECT COUNT(*) FROM user").fetchone()
        assert rows == (1,)
        con.close()

    def test_select_user_with_real_db(
        self, tmp_path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Authentication works end-to-end against a real SQLite database."""
        monkeypatch.setattr(helper_db, "SQLITE_DB_PATH", tmp_path / "db.sqlite")

        assert db_select_user_from_geheimnis("test") == (1, "Torben")
        assert db_select_user_from_geheimnis("wrong_password") == (0, "")

    def test_insert_usage_and_stats_real_db(
        self, tmp_path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Usage insert upserts and stats queries aggregate real data."""
        monkeypatch.setattr(helper_db, "SQLITE_DB_PATH", tmp_path / "db.sqlite")
        monkeypatch.setattr(helper_db, "LLM_PROVIDER_DEFAULT", "Mistral")

        helper_db.db_insert_usage(user_id=1, tokens=100)
        helper_db.db_insert_usage(user_id=1, tokens=50)

        total = db_select_usage_stats_total(user_id=1)
        assert total.iloc[0]["user_name"] == "Torben"
        assert total.iloc[0]["cnt_requests"] == 2
        assert total.iloc[0]["cnt_tokens"] == 150

        daily = db_select_usage_stats_daily(user_id=1)
        assert len(daily) == 1
        assert daily.iloc[0]["date"] == dt.date.today().isoformat()  # noqa: DTZ011
        assert daily.iloc[0]["cnt_requests"] == 2

    def test_sqlite_connection_error_reraises(
        self, tmp_path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Connection errors from sqlite_connection are propagated."""
        db_path = tmp_path / "db.sqlite"
        db_path.touch()
        monkeypatch.setattr(helper_db, "SQLITE_DB_PATH", db_path)

        def boom(*_args, **_kwargs) -> None:
            msg = "conn failed"
            raise sqlite3.Error(msg)

        monkeypatch.setattr(helper_db.sqlite3, "connect", boom)

        with (
            pytest.raises(sqlite3.Error, match="conn failed"),
            helper_db.sqlite_connection(),
        ):
            pass
