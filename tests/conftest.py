"""Shared pytest fixtures for all tests."""

# ruff: noqa: PLR2004

import os

# CRITICAL: Set environment variables BEFORE any imports that use config
# This ensures that shared.config loads with Mock LLM settings
os.environ["LLM_PROVIDERS"] = "Mock"
os.environ["LLM_MODEL"] = "random"

import pytest
from fastapi.testclient import TestClient

from fastapi_app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Create a single TestClient for the entire test session."""
    return TestClient(app)


@pytest.fixture(scope="session")
def auth_token(client: TestClient) -> str:
    """Fixture to get authentication token (shared across session)."""
    response = client.post("/api/auth/login", json={"secret": "test"})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="session")
def auth_headers(auth_token: str) -> dict[str, str]:
    """Fixture to get authorization headers (shared across session)."""
    return {"Authorization": f"Bearer {auth_token}"}
