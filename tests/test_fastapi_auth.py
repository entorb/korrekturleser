"""Tests for FastAPI authentication endpoints."""

from datetime import UTC, datetime, timedelta

import jwt
from fastapi.testclient import TestClient

from fastapi_app.helper_fastapi import create_access_token
from fastapi_app.routers import auth
from shared.helper import my_get_env


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_login_with_valid_credentials(self, client: TestClient) -> None:
        """Test successful login with valid credentials."""
        response = client.post("/api/auth/login", json={"secret": "test"})

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "access_token" in data
        assert "token_type" in data

        # Verify token type
        assert data["token_type"] == "bearer"  # noqa: S105

        # Verify token is not empty
        assert len(data["access_token"]) > 0

    def test_login_with_invalid_credentials(self, client: TestClient) -> None:
        """Test login fails with invalid credentials."""
        response = client.post("/api/auth/login", json={"secret": "wrong_password"})

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Invalid credentials"

    def test_login_with_empty_secret(self, client: TestClient) -> None:
        """Test login validation with empty secret."""
        response = client.post("/api/auth/login", json={"secret": ""})

        # Pydantic validation should fail (min_length=1)
        assert response.status_code == 422

    def test_login_with_missing_secret(self, client: TestClient) -> None:
        """Test login validation with missing secret field."""
        response = client.post("/api/auth/login", json={})

        # Pydantic validation should fail (required field)
        assert response.status_code == 422

    def test_login_rate_limiting_configuration(self) -> None:
        """
        Verify that login endpoint has rate limiting configured.

        Note: Rate limiting is active only on PROD.
        In production, the endpoint is limited to 5 requests per minute per IP.
        This test verifies only that the configuration exists.
        """
        # Verify the limiter is configured
        assert hasattr(auth, "limiter")

        # Verify the login endpoint has the rate limit decorator
        login_func = auth.login

        # Check that slowapi decorator is applied (it adds _rate_limit_key attribute)
        assert hasattr(login_func, "__wrapped__") or "limit" in str(login_func)


class TestTokenExpiration:
    """Test JWT token expiration and validation."""

    def test_token_contains_user_data(self, client: TestClient) -> None:
        """Test that JWT token contains correct user data."""
        # Login to get token
        login_response = client.post("/api/auth/login", json={"secret": "test"})
        token = login_response.json()["access_token"]

        # Decode token (without verification for testing)
        secret_key = my_get_env("FASTAPI_JWT_SECRET_KEY")
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])

        # Verify payload contains correct data
        assert payload["username"] == "Torben"
        assert "exp" in payload  # Expiration time

    def test_token_expiration_time(self, client: TestClient) -> None:
        """Test that token has correct expiration time (24 hours)."""
        # Login to get token
        login_response = client.post("/api/auth/login", json={"secret": "test"})
        token = login_response.json()["access_token"]

        # Decode token
        secret_key = my_get_env("FASTAPI_JWT_SECRET_KEY")
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])

        # Check expiration is approximately 24 hours from now
        exp_time = datetime.fromtimestamp(payload["exp"], tz=UTC)
        now = datetime.now(UTC)
        time_diff = exp_time - now

        # Should be close to 24 hours (within 1 minute tolerance)
        expected_hours = 24
        assert (
            timedelta(hours=expected_hours, minutes=-1)
            < time_diff
            < timedelta(hours=expected_hours, minutes=+1)
        )

    def test_create_access_token_with_expires_delta(self) -> None:
        """Custom expiration delta is honored."""
        token = create_access_token(
            {"user_id": 1, "username": "Torben"},
            expires_delta=timedelta(minutes=5),
        )
        secret_key = my_get_env("FASTAPI_JWT_SECRET_KEY")
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])

        exp_time = datetime.fromtimestamp(payload["exp"], tz=UTC)
        time_diff = exp_time - datetime.now(UTC)
        assert timedelta(minutes=4) < time_diff < timedelta(minutes=6)

    def test_expired_token_returns_401(self, client: TestClient) -> None:
        """An expired token is rejected with a dedicated error."""
        token_data = {
            "user_id": 1,
            "username": "Torben",
            "exp": datetime.now(UTC) - timedelta(hours=1),
        }
        secret_key = my_get_env("FASTAPI_JWT_SECRET_KEY")
        expired_token = jwt.encode(token_data, secret_key, algorithm="HS256")

        response = client.get(
            "/api/stats", headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Token has expired"

    def test_token_missing_user_id_returns_401(self, client: TestClient) -> None:
        """A token without the user_id claim is rejected."""
        token_data = {"username": "Torben"}
        secret_key = my_get_env("FASTAPI_JWT_SECRET_KEY")
        token = jwt.encode(token_data, secret_key, algorithm="HS256")

        response = client.get(
            "/api/stats", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"
