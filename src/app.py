"""Main file."""
# ruff: noqa: E402

import streamlit as st

from helper_db import db_select_id_user_from_geheimnis

# needs to be first streamlit command, so placed before the imports
st.set_page_config(page_title="KI Korrekturleser", page_icon=":robot:", layout="wide")


from helper import (
    create_navigation_menu,
    get_logger_from_filename,
    get_shared_state,
    init_dev_session_state,
)

logger = get_logger_from_filename(__file__)


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
        # this stops if user is unknown
        db_select_id_user_from_geheimnis(geheimnis=input_geheimnis)
        del st.session_state[key_geheimnis]
        st.rerun()
    st.stop()


def main() -> None:  # noqa: D103
    # init env
    env = get_shared_state()["ENV"]
    if env == "PROD":
        # init_sentry()
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

    st.markdown(
        "***Achtung***: *Die KI wird deine Eingaben zum Trainieren verwenden."
        " Nur für Dinge verwenden, die nicht streng geheim sind.*"
    )
    # run the page
    _ = create_navigation_menu()

    # footer
    if env == "PROD" and "USER_ID" in st.session_state:
        msg = (
            f"{st.session_state['USERNAME']} hat bisher"
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
