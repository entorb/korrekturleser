"""Helper: Database Access."""

import datetime as dt
import logging
from collections.abc import Generator
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

import mysql.connector
import pandas as pd
from dotenv import load_dotenv
from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.pooling import MySQLConnectionPool, PooledMySQLConnection

from shared.helper import my_get_env, verify_geheimnis, where_am_i

# Load environment variables from .env file in project root
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

logger = logging.getLogger(Path(__file__).stem)

# Mock data for local development (when database is not available)
# Password: "test" -> bcrypt hash
MOCK_USER_SECRET_HASH = "$2b$12$YDgoJlHlpKxHRpum1b1rt.c06YscNeMhcMVaxH2wWNbsCsDouY2/a"  # noqa: S105
MOCK_USERS = [
    (1, "Torben", MOCK_USER_SECRET_HASH),
]
ENV = where_am_i()


# 1. MySQL functions
@lru_cache(maxsize=1)
def get_db_pool() -> MySQLConnectionPool:
    """Get cached database connection pool."""
    return MySQLConnectionPool(
        pool_name="korrekturleser_pool",
        pool_size=3,
        host=my_get_env("DB_HOST"),
        user=my_get_env("DB_USER"),
        passwd=my_get_env("DB_PASS"),
        database=my_get_env("DB_DATABASE"),
    )


@contextmanager
def db_connection() -> Generator[
    PooledMySQLConnection | MySQLConnectionAbstract, None, None
]:
    """
    Context manager for database connections from pool.

    Yields a database connection and ensures proper cleanup (returns to pool).
    """
    pool = get_db_pool()
    con = None
    try:
        con = pool.get_connection()
        yield con
    except mysql.connector.Error:
        logger.exception("Database connection error")
        raise
    finally:
        if con is not None and con.is_connected():
            con.close()  # Returns connection to pool


def db_select_1row(query: str, param: tuple) -> tuple | None:
    """Fetch a single row from the DB as a tuple."""
    try:
        with db_connection() as con, con.cursor(dictionary=False) as cursor:
            cursor.execute(query, param)
            row = cursor.fetchone()
            return row  # type: ignore[return-value]

    except mysql.connector.Error:
        logger.exception("Database error during select_1row for query: \n%s", query)
        raise


def db_select_rows(query: str, param: tuple) -> list[tuple]:
    """Fetch multiple rows from the DB as tuples."""
    try:
        with db_connection() as con, con.cursor(dictionary=False) as cursor:
            cursor.execute(query, param)
            rows = cursor.fetchall()
            return rows if rows else []  # type: ignore[return-value]

    except mysql.connector.Error:
        logger.exception("Database error during select_row for query: \n%s", query)
        raise


# 2. Selects


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
    # Mock mode for local development
    if ENV != "PROD":
        logger.debug("Mock mode: Using mock user data")
        for user_id, username, secret_hashed in MOCK_USERS:
            if verify_geheimnis(geheimnis, secret_hashed):
                return user_id, username
        return 0, ""

    # Fetch id, name, and hashed secrets in a single query
    query = "SELECT id, name, secret_hashed FROM user ORDER BY id"
    rows = db_select_rows(query=query, param=())

    # Verify the provided secret against each user's hashed secret
    for row in rows:
        if len(row) == 3:  # noqa: PLR2004
            user_id, username, secret_hashed = row[0], row[1], row[2]
            if verify_geheimnis(geheimnis, str(secret_hashed)):
                return int(user_id), str(username)

    # No matching user found
    return 0, ""


# update AI usage


def db_insert_usage(user_id: int, tokens: int) -> None:
    """Insert/update usage stats in table history."""
    if ENV != "PROD":
        logger.debug("Mock mode: Skipping usage insert")
        return

    today = dt.date.today()  # noqa: DTZ011

    # Note: This requires a UNIQUE constraint on (date, user_id)
    query = """
INSERT INTO history (date, user_id, cnt_requests, cnt_tokens)
VALUES (%s, %s, 1, %s)
ON DUPLICATE KEY UPDATE
  cnt_requests = cnt_requests + 1,
  cnt_tokens = cnt_tokens + %s
"""
    try:
        with db_connection() as con, con.cursor(dictionary=False) as cursor:
            cursor.execute(query, (today, user_id, tokens, tokens))
            con.commit()

    except mysql.connector.Error:
        logger.exception("Database error during insert\n%s", query)
        raise


# queries for stats page


def db_select_usage_stats_total(user_id: int) -> pd.DataFrame:
    """SELECT user_name, sum(cnt_requests), sum(cnt_tokens)."""
    col_names = ["user_name", "cnt_requests", "cnt_tokens"]

    if ENV != "PROD":
        logger.debug("Mock mode: Returning empty stats")
        return pd.DataFrame(columns=col_names)

    sql = """
SELECT u.name, SUM(h.cnt_requests) AS cnt_requests, SUM(h.cnt_tokens) AS cnt_tokens
FROM user u
JOIN history h on h.user_id = u.id
WHERE u.id = %s
GROUP BY u.name
ORDER BY cnt_tokens DESC, u.name ASC
"""
    # user 1 (admin get's to see all users usages)
    if user_id == 1:
        sql = sql.replace("WHERE", "-- WHERE", 1)
    res = db_select_rows(sql, param=(user_id,))

    if not res:
        return pd.DataFrame(columns=col_names)
    return pd.DataFrame(res, columns=col_names)


def db_select_usage_stats_daily(user_id: int) -> pd.DataFrame:
    """SELECT date, user_name, cnt_requests, cnt_tokens."""
    col_names = ["date", "user_name", "cnt_requests", "cnt_tokens"]

    if ENV != "PROD":
        logger.info("Mock mode: Returning empty stats")
        return pd.DataFrame(columns=col_names)

    sql = """
SELECT h.date, u.name, h.cnt_requests, h.cnt_tokens
FROM user u
JOIN history h ON h.user_id = u.id
WHERE u.id = %s
ORDER BY h.date DESC, u.name ASC
"""
    # user 1 (admin get's to see all users usages)
    if user_id == 1:
        sql = sql.replace("WHERE", "-- WHERE", 1)
    res = db_select_rows(sql, param=(user_id,))
    if not res:
        return pd.DataFrame(columns=col_names)
    return pd.DataFrame(res, columns=col_names)


if __name__ == "__main__":
    res = db_select_usage_stats_total(1)
    print(res.to_csv())
