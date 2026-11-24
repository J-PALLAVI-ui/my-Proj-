"""Tests for FujiNova Chat SSE Streaming API Endpoint."""
import pytest
from fastapi.testclient import TestClient


def test_chat_sse_stream_endpoint(client: TestClient, monkeypatch):
    """Verify POST /api/v1/chat/stream streams SSE events."""
    payload = {
        "session_id": "test_sse_session_1",
        "message": "Hello Hana! I am planning a trip with my family."
    }

    response = client.post("/api/v1/chat/stream", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    body = response.text
    assert "event: token" in body or "event: done" in body or "event: error" in body

    # Verify session retrieval
    session_resp = client.get("/api/v1/chat/sessions/test_sse_session_1")
    assert session_resp.status_code == 200
    session_data = session_resp.json()
    assert session_data["session_id"] == "test_sse_session_1"
    assert "profile" in session_data
