"""Statistics page for NiceGUI application."""

import logging
from pathlib import Path

from nicegui import app, ui

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
        ui.navigate.to("/")
        return

    # Header
    with ui.header().classes("items-center"):
        ui.label("Statistik").classes("text-h5")
        ui.space()
        ui.label(SessionManager.get_user_name()).classes("mr-4")
        ui.link("← Zurück", "/text").classes("text-white no-underline")
        ui.link("Logout", "/").on("click", lambda: SessionManager.logout()).classes(
            "text-white no-underline ml-4"
        )

    # Escape key handler for navigation back to text
    ui.keyboard(on_key=lambda e: ui.navigate.to("/text") if e.key == "Escape" else None)

    # Main content
    with ui.column().classes("w-full p-4"):
        with ui.card().classes("w-full"):
            ui.label("Session Statistik").classes("text-h6 mb-4")

            # Session stats
            stats_grid = ui.grid(columns=2).classes("w-full gap-4")
            with stats_grid:
                ui.label("Anfragen:").classes("font-bold")
                ui.label(str(app.storage.user.get(SESSION_CNT_REQUESTS, 0)))
                ui.label("Token:").classes("font-bold")
                ui.label(str(app.storage.user.get(SESSION_CNT_TOKENS, 0)))

        # Production stats (if available)
        if ENV == "PROD":
            try:
                with ui.row().classes("w-full gap-4"):
                    # Daily usage
                    with ui.card().classes("flex-1"):
                        ui.label("Tägliche Nutzung").classes("text-h6 mb-4")
                        df_daily = db_select_usage_stats_daily(
                            user_id=SessionManager.get_user_id()
                        )
                        if not df_daily.empty:
                            ui.table.from_pandas(df_daily)
                        else:
                            ui.label("Keine Daten verfügbar")

                    # Total usage
                    with ui.card().classes("flex-1"):
                        ui.label("Gesamt").classes("text-h6 mb-4")
                        df_total = db_select_usage_stats_total(
                            user_id=SessionManager.get_user_id()
                        )
                        if not df_total.empty:
                            ui.table.from_pandas(df_total)
                        else:
                            ui.label("Keine Daten verfügbar")

            except Exception as e:
                logger.exception("Error loading stats:")
                ui.notify(f"Fehler beim Laden der Statistiken: {e!s}", type="warning")
