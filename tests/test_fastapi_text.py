"""Tests for FastAPI text improvement endpoints."""

# ruff: noqa: PLR2004

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestImproveModes:
    """Test /api/text/modes endpoint."""

    def test_get_available_modes(self, client: TestClient) -> None:
        """Test getting available improvement modes."""
        response = client.get("/api/text/modes")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "modes" in data
        assert "descriptions" in data

        # Verify all modes are present
        expected_modes = [
            "correct",
            "improve",
            "summarize",
            "expand",
            "translate_de",
            "translate_en",
        ]
        assert set(data["modes"]) == set(expected_modes)

        # Verify descriptions exist for each mode
        for mode in expected_modes:
            assert mode in data["descriptions"]
            assert len(data["descriptions"][mode]) > 0


class TestImproveText:
    """Test /api/text/ endpoint for text improvement."""

    def test_improve_without_authentication(self, client: TestClient) -> None:
        """Test that improvement requires authentication."""
        response = client.post(
            "/api/text/",
            json={"text": "Hello world", "mode": "correct"},
        )

        assert response.status_code == 403

    @patch("fastapi_app.routers.text.get_cached_llm_provider")
    def test_improve_with_correct_mode(
        self, mock_llm: MagicMock, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test text improvement with CORRECT mode."""
        # Mock LLM response
        mock_provider = MagicMock()
        mock_provider.call.return_value = ("Corrected text.", 150)
        mock_llm.return_value = mock_provider

        response = client.post(
            "/api/text/",
            json={"text": "Hello World", "mode": "correct"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert data["text_original"] == "Hello World"
        assert data["text_ai"] == "Corrected text."
        assert data["mode"] == "correct"
        assert data["tokens_used"] == 150
        assert "model" in data

        # Verify LLM was called
        mock_llm.assert_called_once()
        mock_provider.call.assert_called_once_with("Hello World")

    @patch("fastapi_app.routers.text.get_cached_llm_provider")
    def test_improve_with_improve_mode(
        self, mock_llm: MagicMock, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test text improvement with IMPROVE mode."""
        mock_provider = MagicMock()
        mock_provider.call.return_value = ("Enhanced text with better wording.", 200)
        mock_llm.return_value = mock_provider

        response = client.post(
            "/api/text/",
            json={"text": "Simple text", "mode": "improve"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["mode"] == "improve"
        assert data["text_ai"] == "Enhanced text with better wording."
        assert data["tokens_used"] == 200

    @patch("fastapi_app.routers.text.get_cached_llm_provider")
    def test_improve_with_summarize_mode(
        self, mock_llm: MagicMock, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test text improvement with SUMMARIZE mode."""
        mock_provider = MagicMock()
        mock_provider.call.return_value = ("- Key point 1\n- Key point 2", 100)
        mock_llm.return_value = mock_provider

        long_text = "This is a very long text that needs to be summarized. " * 10

        response = client.post(
            "/api/text/",
            json={"text": long_text, "mode": "summarize"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["mode"] == "summarize"
        assert "Key point" in data["text_ai"]

    @patch("fastapi_app.routers.text.get_cached_llm_provider")
    def test_improve_with_expand_mode(
        self, mock_llm: MagicMock, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test text improvement with EXPAND mode."""
        mock_provider = MagicMock()
        mock_provider.call.return_value = (
            "This is a fully expanded text based on the bullet points.",
            180,
        )
        mock_llm.return_value = mock_provider

        response = client.post(
            "/api/text/",
            json={"text": "- Point 1\n- Point 2", "mode": "expand"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["mode"] == "expand"
        assert len(data["text_ai"]) > 0

    @patch("fastapi_app.routers.text.get_cached_llm_provider")
    def test_improve_with_translate_de_mode(
        self, mock_llm: MagicMock, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test text improvement with TRANSLATE_DE mode."""
        mock_provider = MagicMock()
        mock_provider.call.return_value = ("Hallo Welt", 50)
        mock_llm.return_value = mock_provider

        response = client.post(
            "/api/text/",
            json={"text": "Hello world", "mode": "translate_de"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["mode"] == "translate_de"
        assert data["text_ai"] == "Hallo Welt"

    @patch("fastapi_app.routers.text.get_cached_llm_provider")
    def test_improve_with_translate_en_mode(
        self, mock_llm: MagicMock, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test text improvement with TRANSLATE_EN mode."""
        mock_provider = MagicMock()
        mock_provider.call.return_value = ("Hello world", 50)
        mock_llm.return_value = mock_provider

        response = client.post(
            "/api/text/",
            json={"text": "Hallo Welt", "mode": "translate_en"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["mode"] == "translate_en"
        assert data["text_ai"] == "Hello world"

    def test_improve_with_invalid_mode(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test text improvement with invalid mode."""
        response = client.post(
            "/api/text/",
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
            "/api/text/",
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
            "/api/text/",
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
            "/api/text/",
            json={"text": "Test text"},
            headers=auth_headers,
        )

        # Pydantic validation should fail (required field)
        assert response.status_code == 422

    @patch("fastapi_app.routers.text.get_cached_llm_provider")
    def test_improve_llm_error_handling(
        self, mock_llm: MagicMock, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test error handling when LLM fails."""
        mock_provider = MagicMock()
        mock_provider.call.side_effect = Exception("LLM API error")
        mock_llm.return_value = mock_provider

        response = client.post(
            "/api/text/",
            json={"text": "Test text", "mode": "correct"},
            headers=auth_headers,
        )

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Failed to improve text" in data["detail"]

    @patch("fastapi_app.routers.text.get_cached_llm_provider")
    @patch("fastapi_app.routers.text.db_insert_usage")
    def test_improve_usage_tracking_in_local_mode(
        self,
        mock_db_insert: MagicMock,
        mock_llm: MagicMock,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """Test that usage is NOT tracked in local mode."""
        mock_provider = MagicMock()
        mock_provider.call.return_value = ("Improved text", 100)
        mock_llm.return_value = mock_provider

        response = client.post(
            "/api/text/",
            json={"text": "Test text", "mode": "correct"},
            headers=auth_headers,
        )

        assert response.status_code == 200

        # In local/test mode, db_insert_usage should NOT be called
        mock_db_insert.assert_not_called()


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
    @patch("fastapi_app.routers.text.get_cached_llm_provider")
    def test_all_modes_work(
        self,
        mock_llm: MagicMock,
        mode: str,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """Test that all improvement modes work correctly."""
        mock_provider = MagicMock()
        mock_provider.call.return_value = ("Result text", 100)
        mock_llm.return_value = mock_provider

        response = client.post(
            "/api/text/",
            json={"text": "Test text", "mode": mode},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == mode
