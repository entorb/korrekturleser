"""Helper: Database Access."""

import datetime as dt

import mysql.connector
import streamlit as st

from helper import get_logger_from_filename

logger = get_logger_from_filename(__file__)


def db_get_id_user_from_token(token: str) -> None:
    """
    Login: check if token is in DB and stores id, name to session_state.

    stops if user unknown.
    """
    try:
        with (
            mysql.connector.connect(
                host=st.secrets["DB_HOST"],
                user=st.secrets["DB_USER"],
                passwd=st.secrets["DB_PASS"],
                database=st.secrets["DB_DATABASE"],
            ) as con,
            con.cursor() as cursor,
        ):
            cursor.execute("SELECT id, name FROM user WHERE token = %s", (token,))
            row = cursor.fetchone()
            if row:
                st.session_state["USER_ID"] = int(row[0])  # type: ignore
                st.session_state["USERNAME"] = str(row[1])  # type: ignore
                db_get_usage_sums(user_id=st.session_state["USER_ID"])
            else:
                st.error("So nicht!")
                st.stop()

    except mysql.connector.Error:
        logger.exception("Database error during login")
        raise


def db_get_row(query: str, param: tuple) -> tuple | None:
    """Fetch a row from the DB."""
    try:
        with (
            mysql.connector.connect(
                host=st.secrets["DB_HOST"],
                user=st.secrets["DB_USER"],
                passwd=st.secrets["DB_PASS"],
                database=st.secrets["DB_DATABASE"],
            ) as con,
            con.cursor() as cursor,
        ):
            cursor.execute(query, param)
            row = cursor.fetchone()
            return row  # type: ignore

    except mysql.connector.Error:
        logger.exception("Database error during get_row")
        raise


def db_get_usage_sums(user_id: int) -> None:
    """Update sum of requests, sum of tokens into session_state."""
    query = "SELECT SUM(cnt_requests), SUM(cnt_tokens) FROM history WHERE user_id = %s"
    row = db_get_row(query=query, param=(user_id,))
    if row and row[0] is not None and row[1] is not None:
        st.session_state["cnt_requests"] = int(row[0])
        st.session_state["cnt_tokens"] = int(row[1])
    else:
        st.session_state["cnt_requests"] = 0
        st.session_state["cnt_tokens"] = 0


def db_insert_usage(user_id: int, tokens: int) -> None:
    """Insert/update usage stats in table history and session_state."""
    today = dt.date.today()  # noqa: DTZ011

    try:
        with (
            mysql.connector.connect(
                host=st.secrets["DB_HOST"],
                user=st.secrets["DB_USER"],
                passwd=st.secrets["DB_PASS"],
                database=st.secrets["DB_DATABASE"],
            ) as con,
            con.cursor() as cursor,
        ):
            # Use INSERT ... ON DUPLICATE KEY UPDATE
            # This requires a UNIQUE constraint on (date, user_id)
            query = """
INSERT INTO history (date, user_id, cnt_requests, cnt_tokens)
VALUES (%s, %s, 1, %s)
ON DUPLICATE KEY UPDATE
  cnt_requests = cnt_requests + 1,
  cnt_tokens = cnt_tokens + %s
"""
            cursor.execute(query, (today, user_id, tokens, tokens))
            con.commit()

    except mysql.connector.Error:
        logger.exception("Database error during insert.")
        raise

    st.session_state["cnt_requests"] += 1
    st.session_state["cnt_tokens"] += tokens
