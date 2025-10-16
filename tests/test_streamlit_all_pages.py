"""Test: Open all Pages/Reports."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from shared.config import USER_ID_LOCAL, USER_NAME_LOCAL

pages = sorted(Path("streamlit_app/reports").glob("*.py"))


@pytest.mark.parametrize("path", pages)
def test_all_pages(path: Path) -> None:
    """Open all pages and check for errors and warnings."""
    at = AppTest.from_file(str(path))
    at.session_state["USER_ID"] = USER_ID_LOCAL
    at.session_state["USER_NAME"] = USER_NAME_LOCAL
    at.session_state["ai_response"] = ""
    at.session_state["cnt_requests"] = 0
    at.session_state["cnt_tokens"] = 0
    at.run(timeout=120)
    assert not at.exception, path.stem + ": " + str(at.exception)
    assert not at.error, path.stem + ": " + str(at.error)
    assert not at.warning, path.stem + ": " + str(at.warning)
