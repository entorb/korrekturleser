"""Helper functions for creating diff visualizations."""

import difflib
import html


def create_diff_html(text_in: str, text_ai: str) -> str:  # noqa: C901
    """
    Create side-by-side comparison table with highlighted changes.

    Args:
        text_in: Original text
        text_ai: AI-improved text

    Returns:
        HTML string with two-column comparison table

    """

    def highlight_original(text: str, opcodes: list) -> str:
        """Highlight deletions in original text."""
        result = []
        for tag, i1, i2, _j1, _j2 in opcodes:
            chunk = text[i1:i2]
            if not chunk:  # Skip empty chunks
                continue
            if tag == "equal":
                result.append(html.escape(chunk))
            elif tag in ("replace", "delete"):
                result.append(f'<span class="diff-delete">{html.escape(chunk)}</span>')
        return "".join(result)

    def highlight_ai(text: str, opcodes: list) -> str:
        """Highlight insertions in AI text."""
        result = []
        for tag, _i1, _i2, j1, j2 in opcodes:
            chunk = text[j1:j2]
            if not chunk:  # Skip empty chunks
                continue
            if tag == "equal":
                result.append(html.escape(chunk))
            elif tag in ("replace", "insert"):
                result.append(f'<span class="diff-insert">{html.escape(chunk)}</span>')
        return "".join(result)

    # Get opcodes for character-level diff
    matcher = difflib.SequenceMatcher(None, text_in, text_ai)
    opcodes = matcher.get_opcodes()

    text_in_highlighted = highlight_original(text_in, opcodes)
    text_ai_highlighted = highlight_ai(text_ai, opcodes)

    # Create two-column table with highlighted changes
    html_content = f"""
<table class="comparison-table">
    <thead>
        <tr>
            <th>Original</th>
            <th>KI Text</th>
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
