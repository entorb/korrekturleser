"""Login page for NiceGUI application."""

from nicegui import ui

from shared.helper_db import db_select_user_from_geheimnis

from .helper_nicegui import SessionManager


def create_login_page() -> None:
    """Create login page."""
    with (
        ui.column().classes("w-full items-center justify-center min-h-screen"),
        ui.card().classes("w-96"),
    ):
        ui.label("KI Korrekturleser").classes("text-h4 text-center mb-4")

        secret_input = ui.input(
            label="Geheimnis", password=True, password_toggle_button=True
        ).classes("w-full")

        error_label = ui.label("").classes("text-red text-center")
        error_label.visible = False

        def handle_login() -> None:
            """Handle login submission."""
            secret = secret_input.value
            if not secret:
                error_label.text = "Bitte Geheimnis eingeben"
                error_label.visible = True
                return

            # Verify credentials
            user_id, username = db_select_user_from_geheimnis(secret_input.value)
            if user_id > 0:
                SessionManager.login(user_id, username)
                ui.notify("Login erfolgreich!", type="positive")
                ui.navigate.to("/")
            else:
                ui.notify("Falsches Passwort", type="negative")

        ui.button("Login", on_click=handle_login).classes("w-full").props(
            "color=primary"
        )

        # Add Enter key support
        secret_input.on("keydown.enter", handle_login)
