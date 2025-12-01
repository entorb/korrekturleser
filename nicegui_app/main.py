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


def _auto_login_if_local() -> None:
    """Auto-login for local development."""
    if ENV != "PROD" and not SessionManager.is_authenticated():
        SessionManager.login(USER_ID_LOCAL, USER_NAME_LOCAL)
        logger.info("Auto-login for local development")


def _require_authentication() -> bool:
    """
    Ensure user is authenticated before accessing protected routes.

    Returns True if authenticated, False otherwise (and redirects to login).
    """
    _auto_login_if_local()

    if not SessionManager.is_authenticated():
        ui.navigate.to("/login")
        return False
    return True


# Define routes
@ui.page("/login")
def login_page() -> None:
    """Login page."""
    _auto_login_if_local()

    if SessionManager.is_authenticated():
        ui.navigate.to("/")
    else:
        create_login_page()


@ui.page("/")
def index_page() -> None:
    """Index page - text improvement page (requires authentication)."""
    if not _require_authentication():
        return
    create_text_page()


@ui.page("/stats")
def stats_page() -> None:
    """Statistics page (requires authentication)."""
    if not _require_authentication():
        return
    create_stats_page()


def main() -> None:
    """Run the application."""
    ui.run(
        title="KI Korrekturleser",
        favicon="🤖",
        storage_secret=NICEGUI_STORAGE_SECRET,
        host="localhost",  # only listen for requests from local machine.
        port=8505,
        reload=ENV != "PROD",
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
