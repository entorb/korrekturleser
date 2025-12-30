"""Helper functions and classes for NiceGUI application."""

from nicegui import app

# Session storage keys
SESSION_USER_ID = "user_id"
SESSION_USER_NAME = "user_name"
SESSION_CNT_REQUESTS = "cnt_requests"
SESSION_CNT_TOKENS = "cnt_tokens"
SESSION_LLM_MODEL = "llm_model"


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

    @staticmethod
    def get_model() -> str | None:
        """Get selected LLM model."""
        return app.storage.user.get(SESSION_LLM_MODEL)

    @staticmethod
    def set_model(model: str) -> None:
        """Set selected LLM model."""
        app.storage.user[SESSION_LLM_MODEL] = model
