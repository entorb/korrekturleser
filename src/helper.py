"""Helper Functions."""

from pathlib import Path
from typing import TYPE_CHECKING

import bcrypt
import streamlit as st

if TYPE_CHECKING:
    from streamlit.navigation.page import StreamlitPage

PATH_ON_WEBSERVER = "/home/entorb/korrekturleser"


@st.cache_resource
def get_shared_state() -> dict[str, str]:
    """
    Shared state dict.

    Prefilled with ENV (= where the app is running).
    """
    d: dict[str, str] = {}
    d["ENV"] = "PROD" if Path(PATH_ON_WEBSERVER).is_dir() else "Local"
    return d


def init_dev_session_state() -> None:
    """Set session variables needed for local dev without login."""
    st.session_state["USER_ID"] = 1
    st.session_state["USERNAME"] = "Torben"
    st.session_state["cnt_requests"] = 0
    st.session_state["cnt_tokens"] = 0


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


def verify_geheimnis(geheimnis: str, hashed_geheimnis: str) -> bool:
    """Verify a plain text secret against a hashed secret."""
    return bcrypt.checkpw(geheimnis.encode("utf-8"), hashed_geheimnis.encode("utf-8"))
