"""Text processing page for NiceGUI application."""

import asyncio
import logging
from pathlib import Path
from typing import NamedTuple

from nicegui import ui

from nicegui_app.config_nice import BASE_URL
from shared.config import LLM_PROVIDER
from shared.helper_db import db_insert_usage
from shared.helper_diff import create_diff_html as create_diff_table
from shared.llm_provider import get_llm_provider
from shared.mode_configs import MODE_CONFIGS
from shared.texts import GOOGLE_DISCLAIMER, LABEL_KI_TEXT, LABEL_MY_TEXT

from .helper_nicegui import SessionManager

logger = logging.getLogger(Path(__file__).stem)


class OutputElements(NamedTuple):
    """Container for output UI elements."""

    column: ui.column
    textarea: ui.textarea
    markdown: ui.markdown
    copy_btn: ui.button


class ProcessingState:
    """Manage processing state."""

    def __init__(self) -> None:
        """Initialize processing state."""
        self.is_processing = False
        self.output_text = ""
        self.selected_mode = "correct"


class UIElements(NamedTuple):
    """Container for UI elements."""

    spinner: ui.spinner
    button: ui.button
    result_info: ui.row
    result_label: ui.label
    diff_container: ui.column
    diff_card: ui.card


def _create_header() -> None:
    """Create page header with navigation."""
    with ui.header().classes("items-center").style("background-color: #1976d2;"):
        ui.label("KI Korrekturleser").classes("text-h5 font-weight-bold")
        ui.space()
        ui.label(SessionManager.get_user_name()).classes("mr-2")
        ui.button(
            icon="settings", on_click=lambda: ui.navigate.to(f"{BASE_URL}/stats")
        ).props("flat round").tooltip("Statistik")
        ui.button(
            icon="logout",
            on_click=lambda: (
                SessionManager.logout(),
                ui.navigate.to(f"{BASE_URL}/login"),
            ),
        ).props("flat round").tooltip("Abmelden")


def _create_input_column() -> ui.textarea:
    """Create input column and return textarea."""
    with ui.column().classes("flex-1"):
        input_textarea = (
            ui.textarea(placeholder="Text hier eingeben...", value="")
            .classes("w-full")
            .props("outlined rows=15")
        )

        async def paste_from_clipboard() -> None:
            """Paste clipboard content into textarea."""
            clipboard_text = await ui.run_javascript("navigator.clipboard.readText()")
            if clipboard_text:
                input_textarea.value = clipboard_text
                ui.notify("Eingefügt!", type="positive")
            else:
                ui.notify("Zwischenablage ist leer", type="warning")

        with ui.row().classes("w-full items-center justify-between mb-2"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("account_circle", size="md").classes("text-primary")
                ui.label(LABEL_MY_TEXT).classes("text-subtitle1")
            ui.button(
                icon="content_paste",
                on_click=paste_from_clipboard,
            ).props("flat round size=sm").tooltip("Einfügen")

        input_textarea.move()

    return input_textarea


def _create_output_column() -> OutputElements:
    """Create output column and return UI elements."""
    output_column = ui.column().classes("flex-1")
    with output_column:
        with ui.row().classes("w-full items-center justify-between mb-2"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("auto_fix_high", size="md").classes("text-primary")
                ui.label(LABEL_KI_TEXT).classes("text-subtitle1")
            copy_btn = (
                ui.button(icon="content_copy")
                .props("flat round size=sm")
                .tooltip("Kopieren")
            )
        output_textarea = (
            ui.textarea(placeholder="KI-verbesserter Text erscheint hier...", value="")
            .classes("w-full")
            .props("outlined rows=15")
        )
        output_markdown = ui.markdown("")

        async def copy_to_clipboard() -> None:
            """Copy output to clipboard."""
            if output_textarea.value:
                await ui.run_javascript(
                    f"navigator.clipboard.writeText({output_textarea.value!r})"
                )
                ui.notify("Kopiert!", type="positive")

        copy_btn.on("click", copy_to_clipboard)

    output_column.visible = False
    output_markdown.visible = False
    return OutputElements(output_column, output_textarea, output_markdown, copy_btn)


def _update_output_display(
    mode: str, output: OutputElements, text_response: str
) -> None:
    """Update output display based on mode."""
    output.column.visible = True

    if mode == "summarize":
        output.textarea.visible = False
        output.markdown.visible = True
        output.markdown.content = text_response
        output.copy_btn.visible = False
    else:
        output.textarea.visible = True
        output.markdown.visible = False
        output.textarea.value = text_response
        output.copy_btn.visible = True


def _update_diff_display(
    mode: str,
    input_text: str,
    output_text: str,
    diff_container: ui.column,
    diff_card: ui.card,
) -> None:
    """Update diff display for correct and improve modes."""
    diff_container.clear()
    if mode in ("correct", "improve"):
        # Read CSS file and inject it
        css_path = Path(__file__).parent.parent / "shared" / "helper_diff.css"
        css_content = css_path.read_text(encoding="utf-8")

        # Get diff table HTML (without CSS)
        table_html = create_diff_table(input_text, output_text)

        with diff_container:
            # Add CSS and HTML separately
            ui.add_head_html(f"<style>{css_content}</style>")
            ui.html(table_html, sanitize=False)
        diff_card.visible = True
    else:
        diff_card.visible = False


def _process_with_llm(mode: str, input_text: str) -> tuple[str, int, str]:
    """Process text with LLM and return response, tokens, and model name."""
    instruction = MODE_CONFIGS[mode].instruction
    llm_provider = get_llm_provider(LLM_PROVIDER)
    models = llm_provider.get_models()
    model = SessionManager.get_model() or models[0]
    text_response, tokens = llm_provider.call(
        model=model, instruction=instruction, prompt=input_text
    )
    return text_response, tokens, model


def _track_usage(tokens: int) -> None:
    """Track usage in database and session."""
    db_insert_usage(user_id=SessionManager.get_user_id(), tokens=tokens)
    SessionManager.increment_usage(tokens)


def create_text_page() -> None:
    """Create main text improvement page."""
    if not SessionManager.is_authenticated():
        ui.navigate.to(f"{BASE_URL}/login")
        return

    state = ProcessingState()

    _create_header()

    _create_main_content(state)


def _create_main_content(state: ProcessingState) -> None:
    """Create the main content area with input and output columns."""
    with ui.column().classes("w-full p-6 gap-4"):
        if LLM_PROVIDER == "Gemini":
            with ui.card().classes("w-full bg-blue-50"):
                ui.markdown(GOOGLE_DISCLAIMER).classes("text-caption")

        # Create UI elements
        input_textarea, output = _create_io_section()
        mode_select, process_btn, process_spinner = _create_control_section()
        diff_card, diff_container = _create_diff_display()
        result_info, result_info_label = _create_result_info()

        # Group UI elements
        ui_elements = UIElements(
            process_spinner,
            process_btn,
            result_info,
            result_info_label,
            diff_container,
            diff_card,
        )

        # Setup process handler
        async def process_text() -> None:
            """Process text with AI."""
            await _handle_text_processing(
                state, input_textarea, output, mode_select, ui_elements
            )

        process_btn.on("click", process_text)

        # Add Ctrl+Enter (Windows/Linux) and Cmd+Enter (Mac) keyboard shortcuts
        input_textarea.on("keydown.ctrl.enter", process_text)
        input_textarea.on("keydown.meta.enter", process_text)


def _create_io_section() -> tuple[ui.textarea, OutputElements]:
    """Create input/output section."""
    with ui.row().classes("w-full gap-4"):
        input_textarea = _create_input_column()
        output = _create_output_column()

    return input_textarea, output


def _create_control_section() -> tuple[ui.select, ui.button, ui.spinner]:
    """Create control section with mode selector and process button."""
    control_row = ui.row().classes("w-full gap-2 items-end mt-4")
    with control_row:
        mode_select = (
            ui.select(
                options={
                    mode: config.description for mode, config in MODE_CONFIGS.items()
                },
                value="correct",
                label="Modus",
            )
            .classes("flex-grow-1")
            .props("outlined")
        )
        process_spinner = ui.spinner(size="lg", color="primary")
        process_spinner.visible = False
        process_btn = ui.button(icon="auto_fix_high")
        process_btn.props("color=primary size=large unelevated round")  # .style(

    return mode_select, process_btn, process_spinner


def _create_result_info() -> tuple[ui.row, ui.label]:
    """Create result info section."""
    result_info = ui.row().classes("w-full")
    with result_info:
        result_info_label = ui.label("")
    result_info.visible = False
    return result_info, result_info_label


def _create_diff_display() -> tuple[ui.card, ui.column]:
    """Create diff display section."""
    diff_card = ui.card().classes("w-full mt-4")
    with diff_card:
        ui.label("Unterschied").classes("text-subtitle1 mb-2")
        diff_container = ui.column().classes("w-full overflow-x-auto")
    diff_card.visible = False
    return diff_card, diff_container


async def _handle_text_processing(
    state: ProcessingState,
    input_textarea: ui.textarea,
    output: OutputElements,
    mode_select: ui.select,
    ui_elements: UIElements,
) -> None:
    """Handle text processing workflow."""
    if not input_textarea.value:
        ui.notify("Bitte Text eingeben", type="warning")
        return

    if state.is_processing:
        return

    _start_processing(state, output, ui_elements)

    try:
        await _execute_processing(
            state, input_textarea, output, mode_select, ui_elements
        )
    except Exception as e:
        logger.exception("Error processing text:")
        ui.notify(f"Fehler: {e!s}", type="negative")
    finally:
        _finish_processing(state, ui_elements)


def _start_processing(
    state: ProcessingState, output: OutputElements, ui_elements: UIElements
) -> None:
    """Set UI state for processing start."""
    state.is_processing = True
    ui_elements.spinner.visible = True
    ui_elements.button.props("disable")
    output.column.visible = False
    ui_elements.diff_container.clear()
    ui_elements.result_info.visible = False


async def _execute_processing(
    state: ProcessingState,
    input_textarea: ui.textarea,
    output: OutputElements,
    mode_select: ui.select,
    ui_elements: UIElements,
) -> None:
    """Execute the processing logic."""
    selected_mode = mode_select.value
    if not selected_mode or selected_mode not in MODE_CONFIGS:
        ui.notify("Ungültiger Modus", type="warning")
        return

    state.selected_mode = selected_mode
    # Run LLM processing in executor to keep UI responsive
    text_response, tokens, model = await asyncio.to_thread(
        _process_with_llm, selected_mode, input_textarea.value
    )
    state.output_text = text_response

    _update_output_display(selected_mode, output, text_response)
    _track_usage(tokens)

    ui_elements.result_info.visible = True
    ui_elements.result_label.text = (
        f"LLM: {LLM_PROVIDER} | Model: {model} | Tokens: {tokens}"
    )

    _update_diff_display(
        selected_mode,
        input_textarea.value,
        text_response,
        ui_elements.diff_container,
        ui_elements.diff_card,
    )

    ui.notify("Verarbeitung erfolgreich", type="positive")


def _finish_processing(state: ProcessingState, ui_elements: UIElements) -> None:
    """Set UI state for processing completion."""
    state.is_processing = False
    ui_elements.spinner.visible = False
    ui_elements.button.props(remove="disable")
