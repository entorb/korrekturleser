"""Tests for FastAPI statistics endpoints."""

# ruff: noqa: PLR2004

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import jwt
from fastapi.testclient import TestClient

from shared.helper import my_get_env


class TestUsageStats:
    """Test /api/stats endpoint."""

    def test_stats_without_authentication(self, client: TestClient) -> None:
        """Test that stats require authentication."""
        response = client.get("/api/stats")

        assert response.status_code == 401

    @patch("shared.helper_db.sqlite_connection")
    def test_stats_with_valid_token(
        self,
        mock_sqlite: MagicMock,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """Test stats endpoint returns mock data in local mode."""
        # Mock SQLite connection for stats queries
        mock_con = MagicMock()
        mock_cursor = MagicMock()

        # Mock responses for both queries in correct order
        # First call: daily stats (4 columns: date, user_name, cnt_requests, cnt_tokens)
        # Second call: total stats (3 columns: user_name, cnt_requests, cnt_tokens)
        mock_cursor.fetchall.side_effect = [
            [("2025-12-01", "Torben", 0, 0)],  # Daily stats
            [("Torben", 0, 0)],  # Total stats
        ]
        mock_con.cursor.return_value = mock_cursor
        mock_sqlite.return_value.__enter__.return_value = mock_con

        response = client.get("/api/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "daily" in data
        assert "total" in data

        # In local mode, returns mock data with 0 values
        assert len(data["daily"]) == 1
        assert data["daily"][0]["user_name"] == "Torben"
        assert data["daily"][0]["cnt_requests"] == 0
        assert data["daily"][0]["cnt_tokens"] == 0

        assert len(data["total"]) == 1
        assert data["total"][0]["user_name"] == "Torben"
        assert data["total"][0]["cnt_requests"] == 0
        assert data["total"][0]["cnt_tokens"] == 0

    @patch("shared.helper_db.sqlite_connection")
    def test_stats_non_admin_user_gets_own_data(
        self, mock_sqlite: MagicMock, client: TestClient
    ) -> None:
        """Test stats endpoint returns user's own data for non-admin in local mode."""
        # Mock SQLite connection for stats queries
        mock_con = MagicMock()
        mock_cursor = MagicMock()

        # Mock responses for both queries in correct order
        # First call: daily stats (4 columns: date, user_name, cnt_requests, cnt_tokens)
        # Second call: total stats (3 columns: user_name, cnt_requests, cnt_tokens)
        mock_cursor.fetchall.side_effect = [
            [("2025-12-01", "NonAdmin", 0, 0)],  # Daily stats
            [("NonAdmin", 0, 0)],  # Total stats
        ]
        mock_con.cursor.return_value = mock_cursor
        mock_sqlite.return_value.__enter__.return_value = mock_con

        # Create a token for a different user (not admin)
        token_data = {
            "user_id": 2,
            "username": "NonAdmin",
            "exp": datetime.now(UTC) + timedelta(hours=24),
        }
        secret_key = my_get_env("FASTAPI_JWT_SECRET_KEY")
        fake_token = jwt.encode(token_data, secret_key, algorithm="HS256")

        response = client.get(
            "/api/stats", headers={"Authorization": f"Bearer {fake_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Non-admin should see their own data
        assert len(data["daily"]) == 1
        assert data["daily"][0]["user_name"] == "NonAdmin"
        assert len(data["total"]) == 1
        assert data["total"][0]["user_name"] == "NonAdmin"


class TestRootEndpoints:
    """Test root and health endpoints."""

    def test_root_endpoint(self, client: TestClient) -> None:
        """Test root endpoint returns API information."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert "version" in data
        assert "environment" in data
        assert "docs" in data

        assert data["message"] == "KI Korrekturleser API"
        assert data["version"] == "0.1.0"
        assert data["docs"] == "/docs"

    def test_health_endpoint(self, client: TestClient) -> None:
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "environment" in data

        assert data["status"] == "healthy"
