"""Shared helper functions for both Streamlit and FastAPI apps."""

import os
from pathlib import Path

import bcrypt
from dotenv import load_dotenv

# to distinguish PROD vs. Local
# do not move to config, to prevent circular dependencies
PATH_ON_WEBSERVER = "/home/entorb/korrekturleser"

# Load environment variables from .env file in project root
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")


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


def where_am_i() -> str:
    """Return PROD or Local, depending on if the webserver dir is found."""
    return "PROD" if Path(PATH_ON_WEBSERVER).is_dir() else "Local"
