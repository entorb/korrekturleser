"""Statistics page for NiceGUI application."""

import logging
from pathlib import Path

from nicegui import app, ui

from shared.helper import format_config_dataframe, format_session_dataframe
from shared.helper_db import (
    db_select_usage_stats_daily,
    db_select_usage_stats_total,
)

from .config_nice import BASE_URL
from .helper_nicegui import (
    SESSION_CNT_REQUESTS,
    SESSION_CNT_TOKENS,
    SessionManager,
)

logger = logging.getLogger(Path(__file__).stem)


def create_stats_page() -> None:
    """Create statistics page."""
    if not SessionManager.is_authenticated():
        ui.navigate.to(f"{BASE_URL}/login")
        return

    # Header
    with ui.header().classes("items-center").style("background-color: #1976d2;"):
        ui.label("Statistik").classes("text-h5")
        ui.space()
        ui.label(SessionManager.get_user_name()).classes("mr-2")
        ui.button(icon="arrow_back", on_click=lambda: ui.navigate.to(BASE_URL)).props(
            "flat round"
        ).tooltip("Zurück (Esc)")
        ui.button(
            icon="logout",
            on_click=lambda: (
                SessionManager.logout(),
                ui.navigate.to(f"{BASE_URL}/login"),
            ),
        ).props("flat round").tooltip("Abmelden")

    # Escape key handler for navigation back to text
    ui.keyboard(
        on_key=lambda e: ui.navigate.to(BASE_URL) if e.key == "Escape" else None
    )

    # Main content
    with ui.column().classes("w-full p-4"):
        # Top row: Sum and Daily Usage
        with ui.row().classes("w-full gap-4"):
            # Total usage
            with ui.card().classes("flex-1"):
                ui.label("Sum").classes("text-h6 mb-4")
                try:
                    df_total = db_select_usage_stats_total(
                        user_id=SessionManager.get_user_id()
                    )
                    if not df_total.empty:
                        ui.table.from_pandas(df_total)
                    else:
                        ui.label("Keine Daten verfügbar")
                except Exception as e:
                    logger.exception("Error loading total stats")
                    ui.label(f"Fehler: {e!s}").classes("text-red")

            # Daily usage
            with ui.card().classes("flex-1"):
                ui.label("Daily Usage").classes("text-h6 mb-4")
                try:
                    df_daily = db_select_usage_stats_daily(
                        user_id=SessionManager.get_user_id()
                    )
                    if not df_daily.empty:
                        ui.table.from_pandas(df_daily)
                    else:
                        ui.label("Keine Daten verfügbar")
                except Exception as e:
                    logger.exception("Error loading daily stats")
                    ui.label(f"Fehler: {e!s}").classes("text-red")

        # Bottom row: Config and Session
        with ui.row().classes("w-full gap-4"):
            # Config
            with ui.card().classes("flex-1"):
                ui.label("Config").classes("text-h6 mb-4")
                df_config = format_config_dataframe()
                ui.table.from_pandas(df_config)

            # Session
            with ui.card().classes("flex-1"):
                ui.label("Session").classes("text-h6 mb-4")
                # Session stats including storage
                session_data = {
                    "USER_ID": SessionManager.get_user_id(),
                    "USER_NAME": SessionManager.get_user_name(),
                    SESSION_CNT_REQUESTS: app.storage.user.get(SESSION_CNT_REQUESTS, 0),
                    SESSION_CNT_TOKENS: app.storage.user.get(SESSION_CNT_TOKENS, 0),
                }
                df_session = format_session_dataframe(session_data)
                ui.table.from_pandas(df_session)
