"""Statistics page for NiceGUI application."""

import logging
from pathlib import Path

import pandas as pd
from nicegui import app, ui

from shared.config import LLM_MODEL, LLM_PROVIDER
from shared.helper import where_am_i
from shared.helper_db import (
    db_select_usage_stats_daily,
    db_select_usage_stats_total,
)

from .helper_nicegui import (
    SESSION_CNT_REQUESTS,
    SESSION_CNT_TOKENS,
    SessionManager,
)

logger = logging.getLogger(Path(__file__).stem)
ENV = where_am_i()


def create_stats_page() -> None:
    """Create statistics page."""
    if not SessionManager.is_authenticated():
        ui.navigate.to("/login")
        return

    # Header
    with ui.header().classes("items-center").style("background-color: #1976d2;"):
        ui.button(icon="arrow_back", on_click=lambda: ui.navigate.to("/")).props(
            "flat round"
        ).tooltip("Zurück (Esc)")
        ui.label("Statistik").classes("text-h5")
        ui.space()
        ui.label(SessionManager.get_user_name()).classes("mr-2")
        ui.button(
            icon="logout",
            on_click=lambda: (SessionManager.logout(), ui.navigate.to("/login")),
        ).props("flat round").tooltip("Abmelden")

    # Escape key handler for navigation back to text
    ui.keyboard(on_key=lambda e: ui.navigate.to("/") if e.key == "Escape" else None)

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
                config_data = {
                    "ENV": ENV,
                    "LLM_PROVIDER": LLM_PROVIDER,
                    "LLM_PROD_MODEL": LLM_MODEL,
                }
                # Convert to DataFrame with sorted items
                config_items = sorted([(k, str(v)) for k, v in config_data.items()])
                df_config = pd.DataFrame(config_items, columns=["key", "value"])
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
                session_items = sorted([(k, str(v)) for k, v in session_data.items()])
                df_session = pd.DataFrame(session_items, columns=["key", "value"])
                ui.table.from_pandas(df_session)
