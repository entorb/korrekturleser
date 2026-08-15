"""Helper functions for creating diff visualizations."""

import difflib
import html

from shared.texts import LABEL_KI_TEXT, LABEL_MY_TEXT


def _highlight_chunks(text: str, opcodes: list, side: int, change_class: str) -> str:
    """
    Build highlighted HTML for one text column.

    Args:
        text: Column text
        opcodes: Character-level difflib opcodes
        side: 0 = original column (use i1/i2 ranges), 1 = AI column (use j1/j2)
        change_class: CSS class applied to changed chunks

    Returns:
        HTML string with escaped chunks, changed chunks wrapped in a span

    """
    result = []
    for tag, i1, i2, j1, j2 in opcodes:
        start, end = (i1, i2) if side == 0 else (j1, j2)
        chunk = text[start:end]
        if not chunk:  # Skip empty chunks
            continue
        if tag == "equal":
            result.append(html.escape(chunk))
        elif tag in ("replace", "insert", "delete"):
            result.append(f'<span class="{change_class}">{html.escape(chunk)}</span>')
    return "".join(result)


def create_diff_html(text_in: str, text_ai: str) -> str:
    """
    Create side-by-side comparison table with highlighted changes.

    Args:
        text_in: Original text
        text_ai: AI-improved text

    Returns:
        HTML string with two-column comparison table

    """
    # Get opcodes for character-level diff
    matcher = difflib.SequenceMatcher(None, text_in, text_ai)
    opcodes = matcher.get_opcodes()

    text_in_highlighted = _highlight_chunks(text_in, opcodes, 0, "diff-delete")
    text_ai_highlighted = _highlight_chunks(text_ai, opcodes, 1, "diff-insert")

    # Create two-column table with highlighted changes
    html_content = f"""
<table class="comparison-table">
    <thead>
        <tr>
            <th>{LABEL_MY_TEXT}</th>
            <th>{LABEL_KI_TEXT}</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>{text_in_highlighted}</td>
            <td>{text_ai_highlighted}</td>
        </tr>
    </tbody>
</table>
"""
    return html_content
