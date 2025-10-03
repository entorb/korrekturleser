"""Helper Functions."""

from logging import Logger
from pathlib import Path
from typing import TYPE_CHECKING

import streamlit as st
from streamlit.logger import get_logger

if TYPE_CHECKING:
    from streamlit.navigation.page import StreamlitPage


@st.cache_resource
def get_shared_state() -> dict[str, str]:
    """
    Shared state dict.

    Prefilled with ENV = where the app is running.
    """
    d: dict[str, str] = {}
    d["ENV"] = "PROD" if Path("/home/entorb/korrekturleser").is_dir() else "Local"
    return d


def init_dev_session_state() -> None:
    """Set session variables needed for local dev without login."""
    st.session_state["USER_ID"] = 1
    st.session_state["USERNAME"] = "Torben"


def get_logger_from_filename(file: str) -> Logger:
    """Return logger using filename name."""
    page = Path(file).stem
    return get_logger(page)


def create_navigation_menu() -> str:
    """Create and populate navigation menu."""
    lst: list[StreamlitPage] = []
    for p in sorted(Path("src/reports").glob("*.py")):
        f = p.stem
        if f.startswith("_"):
            continue
        t = f[4:].replace("_", " ").title()
        # stats page for debugging only visible for me
        if f.startswith("r99") and st.session_state["USER_ID"] != 1:
            continue

        lst.append(st.Page(page=f"reports/{f}.py", title=t))
    pg = st.navigation(lst)
    pg.run()
    return pg.url_path


# def init_sentry() -> None:
#     """Initialize Sentry exception tracking/alerting."""
#     import sentry_sdk

#     sentry_sdk.init(
#         dsn=st.secrets["SENTRY_DSN"],
#         environment=st.session_state["ENV"],
#         send_default_pii=True,
#         traces_sample_rate=0.0,
#     )
