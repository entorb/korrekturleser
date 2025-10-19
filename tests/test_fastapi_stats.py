"""Tests for FastAPI statistics endpoints."""

# ruff: noqa: PLR2004

from datetime import UTC, datetime, timedelta

import jwt
from fastapi.testclient import TestClient

from shared.helper import my_get_env


class TestUsageStats:
    """Test /api/stats endpoint."""

    def test_stats_without_authentication(self, client: TestClient) -> None:
        """Test that stats require authentication."""
        response = client.get("/api/stats")

        assert response.status_code == 403

    def test_stats_with_valid_token(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """Test stats endpoint returns mock data in local mode."""
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

    def test_stats_non_admin_user_gets_own_data(self, client: TestClient) -> None:
        """Test stats endpoint returns user's own data for non-admin in local mode."""
        # Create a token for a different user (not admin)
        token_data = {
            "user_id": 2,
            "username": "NonAdmin",
            "exp": datetime.now(UTC) + timedelta(hours=24),
        }
        secret_key = my_get_env("JWT_SECRET_KEY")
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
