"""Tests for FastAPI text improvement endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestImproveText:
    """Test /api/text endpoint for text improvement."""

    def test_improve_without_authentication(self, client: TestClient) -> None:
        """Test that improvement requires authentication."""
        response = client.post(
            "/api/text",
            json={"text": "Hello world", "mode": "correct"},
        )

        assert response.status_code == 401

    def test_get_models_without_authentication(self, client: TestClient) -> None:
        """Test that getting config requires authentication."""
        response = client.get("/api/config/")
        assert response.status_code == 401

    def test_get_models_with_authentication(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test getting available models from config endpoint."""
        response = client.get("/api/config/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "models" in data
        assert "provider" in data
        assert isinstance(data["models"], list)
        assert len(data["models"]) > 0
        # Check that provider is one of the valid options
        assert data["provider"] in (
            "Mock",
            "Gemini",
            "Ollama",
            "OpenAI",
            "OpenAI_Azure",
        )

    def test_improve_with_correct_mode(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test text improvement with CORRECT mode."""
        response = client.post(
            "/api/text",
            json={"text": "Hello World", "mode": "correct"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert data["text_original"] == "Hello World"
        assert data["mode"] == "correct"
        assert data["tokens_used"] > 0  # Mock provider returns random tokens
        assert "model" in data
        assert "text_ai" in data  # Mock provider returns some text

    def test_improve_with_improve_mode(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test text improvement with IMPROVE mode."""
        response = client.post(
            "/api/text",
            json={"text": "Simple text", "mode": "improve"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["mode"] == "improve"
        assert "text_ai" in data
        assert data["tokens_used"] > 0

    def test_improve_with_summarize_mode(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test text improvement with SUMMARIZE mode."""
        long_text = "This is a very long text that needs to be summarized. " * 10

        response = client.post(
            "/api/text",
            json={"text": long_text, "mode": "summarize"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["mode"] == "summarize"
        assert "text_ai" in data
        assert data["tokens_used"] > 0

    def test_improve_with_specific_model(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test text improvement with a specific model."""
        # First get available models from config
        config_response = client.get("/api/config/", headers=auth_headers)
        assert config_response.status_code == 200
        models = config_response.json()["models"]

        # Use the first model
        response = client.post(
            "/api/text",
            json={"text": "Test text", "mode": "correct", "model": models[0]},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["model"] == models[0]
        assert "text_ai" in data

    def test_improve_with_expand_mode(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test text improvement with EXPAND mode."""
        response = client.post(
            "/api/text",
            json={"text": "- Point 1\n- Point 2", "mode": "expand"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["mode"] == "expand"
        assert "text_ai" in data
        assert len(data["text_ai"]) > 0
        assert data["tokens_used"] > 0

    def test_improve_with_translate_de_mode(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test text improvement with TRANSLATE_DE mode."""
        response = client.post(
            "/api/text",
            json={"text": "Hello world", "mode": "translate_de"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["mode"] == "translate_de"
        assert "text_ai" in data
        assert data["tokens_used"] > 0

    def test_improve_with_translate_en_mode(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test text improvement with TRANSLATE_EN mode."""
        response = client.post(
            "/api/text",
            json={"text": "Hallo Welt", "mode": "translate_en"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["mode"] == "translate_en"
        assert "text_ai" in data
        assert data["tokens_used"] > 0

    def test_improve_with_invalid_mode(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test text improvement with invalid mode."""
        response = client.post(
            "/api/text",
            json={"text": "Test text", "mode": "invalid_mode"},
            headers=auth_headers,
        )

        # Pydantic validation should fail
        assert response.status_code == 422

    def test_improve_with_empty_text(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test text improvement with empty text."""
        response = client.post(
            "/api/text",
            json={"text": "", "mode": "correct"},
            headers=auth_headers,
        )

        # Pydantic validation should fail (min_length=1)
        assert response.status_code == 422

    def test_improve_with_missing_text(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test text improvement with missing text field."""
        response = client.post(
            "/api/text",
            json={"mode": "correct"},
            headers=auth_headers,
        )

        # Pydantic validation should fail (required field)
        assert response.status_code == 422

    def test_improve_with_missing_mode(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test text improvement with missing mode field."""
        response = client.post(
            "/api/text",
            json={"text": "Test text"},
            headers=auth_headers,
        )

        # Pydantic validation should fail (required field)
        assert response.status_code == 422

    def test_improve_usage_tracking_in_local_mode(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test that text improvement works in local mode."""
        response = client.post(
            "/api/text",
            json={"text": "Test text", "mode": "correct"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["text_original"] == "Test text"
        assert "text_ai" in data
        assert data["tokens_used"] > 0


class TestInputValidation:
    """Test input validation for text improvement."""

    @pytest.mark.parametrize(
        "mode",
        [
            "correct",
            "improve",
            "summarize",
            "expand",
            "translate_de",
            "translate_en",
        ],
    )
    def test_all_modes_work(
        self,
        mode: str,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """Test that all improvement modes work correctly."""
        response = client.post(
            "/api/text",
            json={"text": "Test text", "mode": mode},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == mode
        assert "text_ai" in data
        assert data["tokens_used"] > 0
