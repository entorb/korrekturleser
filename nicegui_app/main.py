"""Main NiceGUI application for KI Korrekturleser."""

import logging
import sys
from pathlib import Path

from nicegui import ui

# Add parent directory to path for shared module access
sys.path.insert(0, str(Path(__file__).parent.parent))

from nicegui_app.helper_nicegui import SessionManager
from nicegui_app.page_login import create_login_page
from nicegui_app.page_stats import create_stats_page
from nicegui_app.page_text import create_text_page
from shared.config import USER_ID_LOCAL, USER_NAME_LOCAL
from shared.helper import init_logging, my_get_env, where_am_i

init_logging()
logger = logging.getLogger(Path(__file__).stem)

ENV = where_am_i()
NICEGUI_STORAGE_SECRET = my_get_env("NICEGUI_STORAGE_SECRET")


# Define routes
@ui.page("/")
def index_page() -> None:
    """Index page - redirects to login or text."""
    # Auto-login for local development
    if ENV != "PROD" and not SessionManager.is_authenticated():
        SessionManager.login(USER_ID_LOCAL, USER_NAME_LOCAL)

    if SessionManager.is_authenticated():
        ui.navigate.to("/text")
    else:
        create_login_page()


@ui.page("/text")
def text_page() -> None:
    """Text improvement page."""
    create_text_page()


@ui.page("/stats")
def stats_page() -> None:
    """Statistics page."""
    create_stats_page()


def main() -> None:
    """Run the application."""
    ui.run(
        title="KI Korrekturleser",
        favicon="🤖",
        storage_secret=NICEGUI_STORAGE_SECRET,
        host="127.0.0.1",  # only listen for requests from local machine.
        port=8505,
        reload=ENV != "PROD",
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
