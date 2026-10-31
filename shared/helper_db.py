"""Helper: Database Access."""

import datetime as dt
import logging
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
from dotenv import load_dotenv

from .config import LLM_PROVIDER_DEFAULT
from .helper import ENV, verify_geheimnis

if TYPE_CHECKING:
    from collections.abc import Generator

# Load environment variables from .env file in project root
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

logger = logging.getLogger(Path(__file__).stem)

# Mock data for local development
# Password: "test" -> bcrypt hash
MOCK_USER_SECRET_HASH = "$2b$12$YDgoJlHlpKxHRpum1b1rt.c06YscNeMhcMVaxH2wWNbsCsDouY2/a"  # noqa: S105
MOCK_USERS = [
    (1, "Torben", MOCK_USER_SECRET_HASH),
]

# DB_PATH: relative to project root, or absolute
SQLITE_DB_PATH = Path(__file__).parent.parent / os.getenv("DB_PATH", "db.sqlite")


def init_sqlite_db() -> None:
    """
    Initialize SQLite database.

    Creates db.sqlite if it doesn't exist with user and history tables.
    """
    if SQLITE_DB_PATH.exists():
        return

    logger.info("Creating SQLite database: %s", SQLITE_DB_PATH)

    con = sqlite3.connect(SQLITE_DB_PATH)
    cursor = con.cursor()

    cursor.execute("PRAGMA journal_mode=DELETE")

    # Create user table
    cursor.execute("""
        CREATE TABLE user (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            secret_hashed TEXT NOT NULL UNIQUE
        )
    """)

    # Create history table
    cursor.execute("""
        CREATE TABLE history (
            date TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            cnt_requests INTEGER NOT NULL,
            cnt_tokens INTEGER NOT NULL,
            UNIQUE(date, user_id)
        )
    """)

    # Create indexes
    cursor.execute("CREATE INDEX idx_history_date ON history(date)")
    cursor.execute("CREATE INDEX idx_history_user_id ON history(user_id)")

    # Mock user with known password: never on PROD
    if ENV != "PROD":
        cursor.executemany(
            "INSERT INTO user (id, name, secret_hashed) VALUES (?, ?, ?)", MOCK_USERS
        )

    con.commit()
    con.close()
    logger.info("SQLite database created successfully")


@contextmanager
def sqlite_connection() -> Generator[sqlite3.Connection]:
    """
    Context manager for SQLite database connections.

    Ensures database exists and provides a connection with automatic cleanup.
    """
    init_sqlite_db()
    con = None
    try:
        con = sqlite3.connect(SQLITE_DB_PATH, timeout=10)
        # Enable foreign keys for SQLite
        con.execute("PRAGMA foreign_keys = ON")
        yield con
    except sqlite3.Error:
        logger.exception("SQLite connection error")
        raise
    finally:
        if con is not None:
            con.close()


# Selects


def _verify_secret(rows: list, geheimnis: str) -> tuple[int, str]:
    """
    Return (user_id, username) for the first row matching the secret.

    Args:
        rows: Rows of (id, name, secret_hashed)
        geheimnis: The user's plaintext secret (password)

    Returns:
        (user_id, username) if a row matches, (0, "") otherwise

    """
    for row in rows:
        if len(row) == 3:  # noqa: PLR2004
            user_id, username, secret_hashed = row[0], row[1], row[2]
            if verify_geheimnis(geheimnis, str(secret_hashed)):
                return int(user_id), str(username)
    return 0, ""


def db_select_user_from_geheimnis(geheimnis: str) -> tuple[int, str]:
    """
    Authenticate user by verifying secret against bcrypt-hashed passwords.

    Args:
        geheimnis: The user's plaintext secret (password)

    Returns:
        (user_id, username) if authentication succeeds, (0, "") otherwise

    Note: Uses O(n) verification as bcrypt's salted hashing prevents direct
    database queries. Acceptable for small user bases (<10 users).

    """
    with sqlite_connection() as con:
        cursor = con.cursor()
        cursor.execute("SELECT id, name, secret_hashed FROM user ORDER BY id")
        rows = cursor.fetchall()
    return _verify_secret(rows, geheimnis)


# update AI usage


def db_insert_usage(user_id: int, tokens: int) -> None:
    """Insert/update usage stats in table history."""
    # Skip DB insert when using mocked LLM provider
    if LLM_PROVIDER_DEFAULT == "Mock":
        logger.debug("Mocked LLM: Skipping usage insert")
        return

    today = dt.date.today()  # noqa: DTZ011

    try:
        with sqlite_connection() as con:
            cursor = con.cursor()
            cursor.execute(
                """
                INSERT INTO history (date, user_id, cnt_requests, cnt_tokens)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(date, user_id) DO UPDATE SET
                    cnt_requests = cnt_requests + 1,
                    cnt_tokens = cnt_tokens + ?
                """,
                (today.isoformat(), user_id, tokens, tokens),
            )
            con.commit()
    except sqlite3.Error:
        logger.exception("SQLite error during insert")
        raise


# queries for stats page


def _select_stats(sql: str, user_id: int, col_names: pd.Index) -> pd.DataFrame:
    """Run stats query; user 1 (admin) sees all users."""
    try:
        with sqlite_connection() as con:
            cursor = con.cursor()
            if user_id == 1:
                cursor.execute(sql.replace("WHERE u.id = ?", ""))
            else:
                cursor.execute(sql, (user_id,))
            res = cursor.fetchall()
    except sqlite3.Error:
        logger.exception("SQLite error during stats query")
        raise
    if not res:
        return pd.DataFrame(columns=col_names)
    return pd.DataFrame(res, columns=col_names)


def db_select_usage_stats_total(user_id: int) -> pd.DataFrame:
    """SELECT user_name, sum(cnt_requests), sum(cnt_tokens)."""
    sql = """
SELECT u.name, SUM(h.cnt_requests) AS cnt_requests, SUM(h.cnt_tokens) AS cnt_tokens
FROM user u
JOIN history h on h.user_id = u.id
WHERE u.id = ?
GROUP BY u.name
ORDER BY cnt_tokens DESC, u.name ASC
"""
    return _select_stats(
        sql, user_id, pd.Index(["user_name", "cnt_requests", "cnt_tokens"])
    )


def db_select_usage_stats_daily(user_id: int) -> pd.DataFrame:
    """SELECT date, user_name, cnt_requests, cnt_tokens."""
    sql = """
SELECT h.date, u.name, h.cnt_requests, h.cnt_tokens
FROM user u
JOIN history h ON h.user_id = u.id
WHERE u.id = ?
ORDER BY h.date DESC, u.name ASC
LIMIT 100
"""
    return _select_stats(
        sql, user_id, pd.Index(["date", "user_name", "cnt_requests", "cnt_tokens"])
    )


if __name__ == "__main__":
    res = db_select_usage_stats_total(1)
    print(res.to_csv())
