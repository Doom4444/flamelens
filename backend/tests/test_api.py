import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify root endpoint returns 200 and basic API service info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["application"] == "FlameLens"
    assert data["status"] == "online"
    assert data["api_v1"] == "/api/v1"
    assert "version" in data
    assert "message" in data


def test_health_check_endpoint():
    """Verify health endpoint returns status healthy and application metadata."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["application"] == "FlameLens"
    assert "version" in data
    assert "environment" in data
    assert "timestamp" in data


def test_docs_accessible():
    """Verify OpenAPI Swagger documentation endpoint is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_accessible():
    """Verify ReDoc documentation endpoint is accessible."""
    response = client.get("/redoc")
    assert response.status_code == 200


def test_not_found_exception_handling():
    """Verify unmapped routes return structured JSON error rather than raw HTML."""
    response = client.get("/api/v1/unmapped-endpoint-test")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["type"] == "HTTPException"
    assert data["error"]["status_code"] == 404
