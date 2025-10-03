"""Logout."""

import streamlit as st

st.title("Tschüss " + st.session_state["USERNAME"])

del st.session_state["USER_ID"]
del st.session_state["USERNAME"]
st.rerun()

# st.button("Logout", on_click=logout)
