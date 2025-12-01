"""Helper functions and classes for NiceGUI application."""

import diff_match_patch as dmp_module
from nicegui import app

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

    @staticmethod
    def get_request_count() -> int:
        """Get current request count."""
        return app.storage.user.get(SESSION_CNT_REQUESTS, 0)

    @staticmethod
    def get_token_count() -> int:
        """Get current token count."""
        return app.storage.user.get(SESSION_CNT_TOKENS, 0)


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _format_diff_line(line: str, line_type: str, marker: str) -> str:
    """
    Format a single diff line with appropriate styling.

    Args:
        line: The text content of the line
        line_type: The CSS class suffix (delete, insert, or equal)
        marker: The diff marker character (-, +, or space)

    Returns:
        HTML string for the formatted diff line

    """
    return (
        f'<span class="diff-line diff-line-{line_type}">'
        f'<span class="diff-marker">{marker}</span>'
        f'<span class="diff-content">{escape_html(line)}</span>'
        f"</span>"
    )


def _process_diff_lines(
    html_parts: list[str], lines: list[str], line_type: str, marker: str
) -> None:
    """
    Process multiple lines and append formatted diff HTML to parts list.

    Args:
        html_parts: List to append HTML strings to
        lines: Lines to process
        line_type: The CSS class suffix (delete, insert, or equal)
        marker: The diff marker character (-, +, or space)

    """
    for i, line in enumerate(lines):
        if i > 0:  # Add newline for all but first line
            html_parts.append("\n")
        if line or i < len(lines) - 1:  # Skip empty last line
            html_parts.append(_format_diff_line(line, line_type, marker))


def _get_diff_style() -> str:
    """Return CSS styles for GitHub-style diff visualization."""
    return """
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


def create_diff_html(text_in: str, text_ai: str) -> str:
    """Create GitHub-style diff visualization."""
    dmp = dmp_module.diff_match_patch()
    diffs = dmp.diff_main(text_in, text_ai)
    dmp.diff_cleanupSemantic(diffs)

    # Build GitHub-style diff HTML
    html_parts = [_get_diff_style()]

    for op, text in diffs:
        lines = text.split("\n")
        if op == dmp_module.diff_match_patch.DIFF_DELETE:
            _process_diff_lines(html_parts, lines, "delete", "-")
        elif op == dmp_module.diff_match_patch.DIFF_INSERT:
            _process_diff_lines(html_parts, lines, "insert", "+")
        else:  # EQUAL
            _process_diff_lines(html_parts, lines, "equal", " ")

    html_parts.append("</div>")
    return "".join(html_parts)
