"""Shared helper functions for both Streamlit and FastAPI apps."""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

import bcrypt
from dotenv import load_dotenv

if TYPE_CHECKING:
    from collections.abc import Callable

    import pandas as pd

# to distinguish PROD vs. Local
# do not move to config, to prevent circular dependencies
PATH_ON_WEBSERVER = "/home/entorb/korrekturleser"

# Load environment variables from .env file in project root
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")


def init_logging() -> None:
    """Initialize and and configure the logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logging.getLogger("azure").setLevel(logging.WARNING)
    logging.getLogger("google_genai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("mysql").setLevel(logging.WARNING)
    logging.getLogger("tornado").setLevel(logging.WARNING)


@lru_cache(maxsize=1)
def my_get_env(key: str) -> str:
    """Get environment variable, throw exception if not set."""
    value = os.getenv(key)
    if not value:
        msg = f"Environment variable '{key}' missing."
        raise ValueError(msg)
    return value


def verify_geheimnis(geheimnis: str, hashed_geheimnis: str) -> bool:
    """Verify a plain text secret against a hashed secret."""
    return bcrypt.checkpw(geheimnis.encode("utf-8"), hashed_geheimnis.encode("utf-8"))


@lru_cache(maxsize=1)
def where_am_i() -> str:
    """Return PROD or Local, depending on if the webserver dir is found."""
    return "PROD" if Path(PATH_ON_WEBSERVER).is_dir() else "Local"


def auto_login_for_local_dev(
    is_authenticated_fn: Callable[[], bool],
    login_fn: Callable[[int, str], None],
    user_id: int,
    user_name: str,
) -> None:
    """
    Auto-login for local development if not in production and not already authenticated.

    Args:
        is_authenticated_fn: Function that returns True if user is authenticated
        login_fn: Function to call to log in user (takes user_id and user_name)
        user_id: User ID to use for auto-login
        user_name: User name to use for auto-login

    """
    if where_am_i() != "PROD" and not is_authenticated_fn():
        login_fn(user_id, user_name)
        logging.getLogger(__name__).info("Auto-login for local development")


def format_config_dataframe() -> pd.DataFrame:
    """
    Create DataFrame with config information (ENV, LLM_PROVIDER, LLM_MODEL).

    Returns:
        DataFrame with columns 'key' and 'value'

    """
    # Local import to avoid circular dependency
    import pandas as pd  # noqa: PLC0415

    from shared.config import LLM_PROVIDER_DEFAULT  # noqa: PLC0415

    config_data = {
        "ENV": where_am_i(),
        "LLM_PROVIDER_DEFAULT": LLM_PROVIDER_DEFAULT,
    }
    config_items = sorted([(k, str(v)) for k, v in config_data.items()])
    return pd.DataFrame(config_items, columns=["key", "value"])


def format_session_dataframe(session_dict: dict) -> pd.DataFrame:
    """
    Create DataFrame from session data dictionary.

    Args:
        session_dict: Dictionary with session data (keys and values)

    Returns:
        DataFrame with columns 'key' and 'value', sorted by key

    """
    # Local import to avoid circular dependency
    import pandas as pd  # noqa: PLC0415

    session_items = sorted([(k, str(v)) for k, v in session_dict.items()])
    return pd.DataFrame(session_items, columns=["key", "value"])
