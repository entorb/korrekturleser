"""Tests for FastAPI statistics endpoints."""

# ruff: noqa: PLR2004

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import jwt
import pandas as pd
from fastapi.testclient import TestClient

from shared.helper import my_get_env


class TestMyUsage:
    """Test /api/stats/my-usage endpoint."""

    def test_my_usage_without_authentication(self, client: TestClient) -> None:
        """Test that my-usage requires authentication."""
        response = client.get("/api/stats/my-usage")

        assert response.status_code == 403

    def test_my_usage_with_valid_token(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test my-usage endpoint with valid token."""
        response = client.get("/api/stats/my-usage", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure (user_id not included)
        assert "user_name" in data
        assert "total_requests" in data
        assert "total_tokens" in data

        # Verify types
        assert isinstance(data["user_name"], str)
        assert isinstance(data["total_requests"], int)
        assert isinstance(data["total_tokens"], int)

        # Verify user data (mock mode)
        assert data["user_name"] == "Torben"

        # Mock mode returns 0 for usage
        assert data["total_requests"] == 0
        assert data["total_tokens"] == 0

    @patch("fastapi_app.routers.stats.db_select_usage_of_user")
    def test_my_usage_error_handling(
        self, mock_db: MagicMock, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test error handling when database fails."""
        mock_db.side_effect = Exception("Database error")

        response = client.get("/api/stats/my-usage", headers=auth_headers)

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Failed to fetch user usage" in data["detail"]


class TestUsageStats:
    """Test /api/stats/all-users endpoint (admin only)."""

    def test_stats_without_authentication(self, client: TestClient) -> None:
        """Test that stats require authentication."""
        response = client.get("/api/stats/all-users")

        assert response.status_code == 403

    def test_stats_with_valid_admin_token_in_local_mode(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test stats endpoint returns data in local mode (with actual values)."""
        # User ID 1 is admin, in local mode stats should show actual values
        response = client.get("/api/stats/all-users", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "daily" in data
        assert "total" in data

    @patch("fastapi_app.routers.stats.ENV", "PROD")
    @patch("fastapi_app.routers.stats.db_select_usage_stats_daily")
    @patch("fastapi_app.routers.stats.db_select_usage_stats_total")
    def test_stats_with_admin_in_prod_mode(
        self,
        mock_total: MagicMock,
        mock_daily: MagicMock,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """Test stats endpoint works for admin in PROD mode."""
        # Mock daily stats
        daily_data = pd.DataFrame(
            [
                {
                    "date": "2025-01-15",
                    "user_name": "Torben",
                    "cnt_requests": 10,
                    "cnt_tokens": 1000,
                },
                {
                    "date": "2025-01-14",
                    "user_name": "Torben",
                    "cnt_requests": 5,
                    "cnt_tokens": 500,
                },
            ]
        )
        mock_daily.return_value = daily_data

        # Mock total stats - columns match what DB returns
        total_data = pd.DataFrame(
            [
                {
                    "user_name": "Torben",
                    "cnt_requests": 15,
                    "cnt_tokens": 1500,
                }
            ]
        )
        mock_total.return_value = total_data

        response = client.get("/api/stats/all-users", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "daily" in data
        assert "total" in data

        # Verify daily stats - in PROD mode, values should be 0
        assert len(data["daily"]) == 2
        assert data["daily"][0]["user_name"] == "Torben"
        assert data["daily"][0]["cnt_requests"] == 0
        assert data["daily"][0]["cnt_tokens"] == 0

        # Verify total stats - in PROD mode, values should be 0
        assert len(data["total"]) == 1
        assert data["total"][0]["user_name"] == "Torben"
        assert data["total"][0]["total_requests"] == 0
        assert data["total"][0]["total_tokens"] == 0

    @patch("fastapi_app.routers.stats.ENV", "PROD")
    def test_stats_non_admin_user_denied_in_prod(self, client: TestClient) -> None:
        """Test stats endpoint denies non-admin users even in PROD."""
        # Create a token for a different user (not admin)
        # We need to mock the user verification since we can't create other users

        # Create token for non-admin user (user_id=2)
        token_data = {
            "user_id": 2,
            "username": "NonAdmin",
            "exp": datetime.now(UTC) + timedelta(hours=24),
        }
        secret_key = my_get_env("JWT_SECRET_KEY")
        fake_token = jwt.encode(token_data, secret_key, algorithm="HS256")

        response = client.get(
            "/api/stats/all-users", headers={"Authorization": f"Bearer {fake_token}"}
        )

        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        assert "admin user" in data["detail"]

    @patch("fastapi_app.routers.stats.ENV", "PROD")
    @patch("fastapi_app.routers.stats.db_select_usage_stats_daily")
    def test_stats_error_handling(
        self,
        mock_daily: MagicMock,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """Test error handling when database fails."""
        mock_daily.side_effect = Exception("Database error")

        response = client.get("/api/stats/all-users", headers=auth_headers)

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Failed to fetch usage statistics" in data["detail"]

    @patch("fastapi_app.routers.stats.ENV", "PROD")
    @patch("fastapi_app.routers.stats.db_select_usage_stats_daily")
    @patch("fastapi_app.routers.stats.db_select_usage_stats_total")
    def test_stats_with_empty_data(
        self,
        mock_total: MagicMock,
        mock_daily: MagicMock,
        client: TestClient,
        auth_headers: dict[str, str],
    ) -> None:
        """Test stats endpoint with empty database."""
        # Return empty DataFrames
        mock_daily.return_value = pd.DataFrame(
            columns=["date", "user_name", "cnt_requests", "cnt_tokens"]
        )
        mock_total.return_value = pd.DataFrame(
            columns=["user_name", "cnt_requests", "cnt_tokens"]
        )

        response = client.get("/api/stats/all-users", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should return empty lists
        assert data["daily"] == []
        assert data["total"] == []


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
