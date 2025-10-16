"""Main file."""

# ruff: noqa: E402
import logging
from pathlib import Path

import streamlit as st

# needs to be first streamlit command, so placed before the imports
st.set_page_config(page_title="KI Korrekturleser", page_icon=":robot:", layout="wide")

from shared.helper import where_am_i
from shared.helper_db import db_select_usage_of_user, db_select_user_from_geheimnis
from streamlit_app.helper_streamlit import (
    create_navigation_menu,
    init_dev_session_state,
)

logger = logging.getLogger(Path(__file__).stem)

ENV = where_am_i()


def login() -> None:
    """Login logic."""
    key_geheimnis = "geheimnis"
    with st.form("Login"):
        cols = st.columns((1, 1, 2), vertical_alignment="bottom")
        input_geheimnis = cols[0].text_input(
            "Geheimnis", type="password", key=key_geheimnis
        )
        submit = cols[1].form_submit_button(label="Login")

    if submit and input_geheimnis:
        # Verify credentials and get user info
        user_id, username = db_select_user_from_geheimnis(geheimnis=input_geheimnis)
        if user_id == 0:
            st.error("So nicht!")
            st.stop()
        st.session_state["USER_ID"] = user_id
        st.session_state["USER_NAME"] = username

        # Get and store usage stats
        st.session_state["cnt_requests"], st.session_state["cnt_tokens"] = (
            db_select_usage_of_user(user_id=user_id)
        )

        del st.session_state[key_geheimnis]
        st.rerun()
    st.stop()


def main() -> None:  # noqa: D103
    if ENV == "PROD":
        pass
    else:
        # for local running I skip the login and set the session infos
        init_dev_session_state()

    # login if needed
    if "USER_ID" not in st.session_state:
        # stops if user is unknown
        login()

    # init session_state
    if "ai_response" not in st.session_state:
        st.session_state["ai_response"] = ""

    # run the page
    _ = create_navigation_menu()

    # footer
    if ENV == "PROD" and "USER_ID" in st.session_state:
        msg = (
            f"{st.session_state['USER_NAME']} hat bisher"
            f" {st.session_state['cnt_requests']} Anfragen"
            f" mit {st.session_state['cnt_tokens']} Token gestellt."
        )
        st.write(msg)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("Exception:")
        st.exception(e)
        st.stop()
