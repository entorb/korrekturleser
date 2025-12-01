"""Helper Functions for Streamlit app."""

from pathlib import Path
from typing import TYPE_CHECKING

import streamlit as st

from shared.config import USER_ID_LOCAL, USER_NAME_LOCAL
from shared.helper import auto_login_for_local_dev, where_am_i

if TYPE_CHECKING:
    from streamlit.navigation.page import StreamlitPage

ENV = where_am_i()


def init_dev_session_state() -> None:
    """Set session variables needed for local dev without login."""

    def is_authenticated() -> bool:
        return "USER_ID" in st.session_state

    def login(user_id: int, user_name: str) -> None:
        st.session_state["USER_ID"] = user_id
        st.session_state["USER_NAME"] = user_name
        st.session_state["cnt_requests"] = 0
        st.session_state["cnt_tokens"] = 0

    auto_login_for_local_dev(is_authenticated, login, USER_ID_LOCAL, USER_NAME_LOCAL)


def create_navigation_menu() -> str:
    """Create and populate navigation menu."""
    lst: list[StreamlitPage] = []
    for p in sorted(Path("streamlit_app/reports").glob("*.py")):
        f = p.stem
        if f.startswith("_"):
            continue
        t = f[4:].replace("_", " ").title()
        # playground only visible for me
        if f.startswith("r99") and st.session_state["USER_ID"] != 1:
            continue

        lst.append(st.Page(page=f"reports/{f}.py", title=t))
    pg = st.navigation(lst)
    pg.run()
    return pg.url_path
