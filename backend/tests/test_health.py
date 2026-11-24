"""Tests for FujiNova Health and Info Endpoints (Acceptance Test T1-01)."""
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Verify root endpoint provides API metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "FujiNova"
    assert data["version"] == "0.1.0"
    assert "/api/v1/health" in data["health_check"]


def test_health_check_endpoint(client: TestClient):
    """T1-01: Health check endpoint returns 200 OK with status: ok, database check, and model info."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected (SQLite WAL)"
    assert "primary_model" in data
    assert "fallback_model_enabled" in data
