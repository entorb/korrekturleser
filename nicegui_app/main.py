"""Main NiceGUI application for KI Korrekturleser."""

import logging
import sys
from pathlib import Path

import diff_match_patch as dmp_module
from nicegui import app, ui

# Add parent directory to path for shared module access
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.config import LLM_MODEL, LLM_PROVIDER, USER_ID_LOCAL, USER_NAME_LOCAL
from shared.helper import init_logging, where_am_i
from shared.helper_ai import MODE_CONFIGS
from shared.helper_db import (
    db_insert_usage,
    db_select_usage_stats_daily,
    db_select_usage_stats_total,
    db_select_user_from_geheimnis,
)
from shared.llm_provider import get_cached_llm_provider

init_logging()
logger = logging.getLogger(Path(__file__).stem)

ENV = where_am_i()

# Session storage keys
SESSION_USER_ID = "user_id"
SESSION_USER_NAME = "user_name"
SESSION_CNT_REQUESTS = "cnt_requests"
SESSION_CNT_TOKENS = "cnt_tokens"


class SessionManager:
    """Manage user session state."""

    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated."""
        return SESSION_USER_ID in app.storage.user

    @staticmethod
    def get_user_id() -> int:
        """Get current user ID."""
        return app.storage.user.get(SESSION_USER_ID, 0)

    @staticmethod
    def get_user_name() -> str:
        """Get current user name."""
        return app.storage.user.get(SESSION_USER_NAME, "")

    @staticmethod
    def login(user_id: int, user_name: str) -> None:
        """Log in user."""
        app.storage.user[SESSION_USER_ID] = user_id
        app.storage.user[SESSION_USER_NAME] = user_name
        app.storage.user[SESSION_CNT_REQUESTS] = 0
        app.storage.user[SESSION_CNT_TOKENS] = 0

    @staticmethod
    def logout() -> None:
        """Log out user."""
        app.storage.user.clear()

    @staticmethod
    def increment_usage(tokens: int) -> None:
        """Increment usage statistics."""
        app.storage.user[SESSION_CNT_REQUESTS] = (
            app.storage.user.get(SESSION_CNT_REQUESTS, 0) + 1
        )
        app.storage.user[SESSION_CNT_TOKENS] = (
            app.storage.user.get(SESSION_CNT_TOKENS, 0) + tokens
        )


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

        async def handle_login() -> None:
            """Handle login submission."""
            secret = secret_input.value
            if not secret:
                error_label.text = "Bitte Geheimnis eingeben"
                error_label.visible = True
                return

            # Verify credentials
            user_id, user_name = db_select_user_from_geheimnis(geheimnis=secret)
            if user_id == 0:
                error_label.text = "So nicht!"
                error_label.visible = True
                return

            # Login successful
            SessionManager.login(user_id, user_name)
            ui.navigate.to("/text")

        ui.button("Login", on_click=handle_login).classes("w-full").props(
            "color=primary"
        )

        # Add Enter key support
        secret_input.on("keydown.enter", handle_login)


def create_diff_html(text_in: str, text_ai: str) -> str:  # noqa: C901, PLR0912
    """Create GitHub-style diff visualization."""
    dmp = dmp_module.diff_match_patch()
    diffs = dmp.diff_main(text_in, text_ai)
    dmp.diff_cleanupSemantic(diffs)

    # Build GitHub-style diff HTML
    html_parts = [
        """
        <style>
        .github-diff {
            font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas,
                'Liberation Mono', monospace;
            font-size: 12px;
            line-height: 20px;
            border: 1px solid #d0d7de;
            border-radius: 6px;
            overflow: hidden;
            background-color: #ffffff;
        }
        .diff-line {
            display: block;
            padding: 0 10px;
            min-height: 20px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .diff-line-delete {
            background-color: #ffebe9;
            color: #1f2328;
        }
        .diff-line-delete .diff-marker {
            color: #d1242f;
        }
        .diff-line-insert {
            background-color: #dafbe1;
            color: #1f2328;
        }
        .diff-line-insert .diff-marker {
            color: #1a7f37;
        }
        .diff-line-equal {
            background-color: #ffffff;
            color: #656d76;
        }
        .diff-marker {
            display: inline-block;
            width: 20px;
            text-align: center;
            user-select: none;
        }
        .diff-content {
            display: inline;
        }
        </style>
        <div class="github-diff">
        """
    ]

    for op, text in diffs:
        if op == dmp_module.diff_match_patch.DIFF_DELETE:
            # Split into lines for better display
            lines = text.split("\n")
            for i, line in enumerate(lines):
                if i > 0:  # Add newline for all but first line
                    html_parts.append("\n")
                if line or i < len(lines) - 1:  # Skip empty last line
                    html_parts.append(
                        f'<span class="diff-line diff-line-delete">'
                        f'<span class="diff-marker">-</span>'
                        f'<span class="diff-content">{escape_html(line)}</span>'
                        f"</span>"
                    )
        elif op == dmp_module.diff_match_patch.DIFF_INSERT:
            lines = text.split("\n")
            for i, line in enumerate(lines):
                if i > 0:
                    html_parts.append("\n")
                if line or i < len(lines) - 1:
                    html_parts.append(
                        f'<span class="diff-line diff-line-insert">'
                        f'<span class="diff-marker">+</span>'
                        f'<span class="diff-content">{escape_html(line)}</span>'
                        f"</span>"
                    )
        else:  # EQUAL
            lines = text.split("\n")
            for i, line in enumerate(lines):
                if i > 0:
                    html_parts.append("\n")
                if line or i < len(lines) - 1:
                    html_parts.append(
                        f'<span class="diff-line diff-line-equal">'
                        f'<span class="diff-marker"> </span>'
                        f'<span class="diff-content">{escape_html(line)}</span>'
                        f"</span>"
                    )

    html_parts.append("</div>")
    return "".join(html_parts)


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def create_text_page() -> None:  # noqa: C901, PLR0915
    """Create main text improvement page."""
    if not SessionManager.is_authenticated():
        ui.navigate.to("/")
        return

    # State variables
    output_text = ""
    selected_mode = "correct"
    is_processing = False

    # Header
    with ui.header().classes("items-center"):
        ui.label("KI Korrekturleser").classes("text-h5")
        ui.space()
        ui.label(SessionManager.get_user_name()).classes("mr-4")
        ui.link("Stats", "/stats").classes("text-white no-underline")
        ui.link("Logout", "/").on("click", lambda: SessionManager.logout()).classes(
            "text-white no-underline ml-4"
        )

    # Escape key handler for navigation to stats
    ui.keyboard(
        on_key=lambda e: ui.navigate.to("/stats") if e.key == "Escape" else None
    )

    # Main content
    with ui.column().classes("w-full p-4"):
        # Warning message
        with ui.card().classes("w-full"):
            ui.markdown(
                "**Achtung**: *Die Google KI wird deine Eingaben zum Trainieren"
                " verwenden. Nur für Dinge verwenden, die nicht streng geheim sind.*"
            )

        # Input/Output section
        with ui.row().classes("w-full gap-4"):
            # Input column
            with ui.column().classes("flex-1"):
                ui.label("Mein Text").classes("text-subtitle1")
                input_textarea = (
                    ui.textarea(label="Text hier eingeben...", value="")
                    .classes("w-full")
                    .props("rows=15")
                )

                async def paste_from_clipboard() -> None:
                    """Paste from clipboard."""
                    # Note: clipboard paste requires user interaction in browser
                    ui.notify("Bitte mit Strg+V / Cmd+V einfügen")

                ui.button(icon="content_paste", on_click=paste_from_clipboard).props(
                    "flat size=sm"
                ).tooltip("Einfügen")

            # Output column (shown only after processing)
            output_column = ui.column().classes("flex-1")
            with output_column:
                ui.label("KI Text").classes("text-subtitle1")
                output_textarea = (
                    ui.textarea(
                        label="KI-verbesserter Text erscheint hier...", value=""
                    )
                    .classes("w-full")
                    .props("rows=15 readonly")
                )
                output_markdown = ui.markdown("")

                async def copy_to_clipboard() -> None:
                    """Copy output to clipboard."""
                    if output_textarea.value:
                        await ui.run_javascript(
                            f"navigator.clipboard.writeText({output_textarea.value!r})"
                        )
                        ui.notify("Kopiert!")

                copy_btn = ui.button(icon="content_copy", on_click=copy_to_clipboard)
                copy_btn.props("flat size=sm").tooltip("Kopieren")

            # Initially hide output column
            output_column.visible = False
            output_markdown.visible = False

        # Mode selector and process button
        with ui.row().classes("w-full gap-2 items-end"):
            mode_select = ui.select(
                options={
                    mode: config.description for mode, config in MODE_CONFIGS.items()
                },
                value="correct",
                label="Modus",
            ).classes("flex-1")

            process_spinner = ui.spinner(size="lg")
            process_spinner.visible = False

            async def process_text() -> None:
                """Process text with AI."""
                nonlocal is_processing, output_text, selected_mode

                if not input_textarea.value:
                    ui.notify("Bitte Text eingeben", type="warning")
                    return

                if is_processing:
                    return

                is_processing = True
                process_spinner.visible = True
                process_btn.props("disable")
                output_column.visible = False
                diff_container.clear()
                result_info.visible = False

                try:
                    selected_mode = mode_select.value
                    instruction = MODE_CONFIGS[selected_mode].instruction

                    # Get LLM provider and process
                    llm_provider = get_cached_llm_provider(
                        provider_name=LLM_PROVIDER,
                        model=LLM_MODEL,
                        instruction=instruction,
                    )
                    text_response, tokens = llm_provider.call(input_textarea.value)

                    # Update output
                    output_text = text_response
                    output_textarea.value = text_response

                    # Show output column
                    output_column.visible = True

                    # Show markdown for summarize mode, otherwise textarea
                    if selected_mode == "summarize":
                        output_textarea.visible = False
                        output_markdown.visible = True
                        output_markdown.content = text_response
                        copy_btn.visible = False
                    else:
                        output_textarea.visible = True
                        output_markdown.visible = False
                        copy_btn.visible = True

                    # Track usage
                    if ENV == "PROD":
                        db_insert_usage(
                            user_id=SessionManager.get_user_id(), tokens=tokens
                        )

                    SessionManager.increment_usage(tokens)

                    # Show result info
                    result_info.visible = True
                    result_info_label.text = (
                        f"Modell: {LLM_MODEL} | Token verbraucht: {tokens}"
                    )

                    # Show diff for correct and improve modes
                    if selected_mode in ("correct", "improve"):
                        diff_html = create_diff_html(
                            input_textarea.value, text_response
                        )
                        with diff_container:
                            ui.html(diff_html, sanitize=False)
                        diff_card.visible = True
                    else:
                        diff_card.visible = False

                    ui.notify("Verarbeitung erfolgreich", type="positive")

                except Exception as e:
                    logger.exception("Error processing text:")
                    ui.notify(f"Fehler: {e!s}", type="negative")

                finally:
                    is_processing = False
                    process_spinner.visible = False
                    process_btn.props(remove="disable")

            process_btn = ui.button(icon="smart_toy", on_click=process_text)
            process_btn.props("color=primary size=lg").tooltip("KI verarbeiten")

        # Result info
        result_info = ui.row().classes("w-full")
        with result_info:
            result_info_label = ui.label("")
        result_info.visible = False

        # Diff display
        diff_card = ui.card().classes("w-full mt-4")
        with diff_card:
            ui.label("Unterschied").classes("text-subtitle1 mb-2")
            diff_container = ui.column().classes("w-full overflow-x-auto")
        diff_card.visible = False


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
        storage_secret="korrekturleser-nicegui-secret-2025",  # noqa: S106
        port=8505,
        reload=ENV != "PROD",
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
