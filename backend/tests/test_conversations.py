"""Tests for Persistent Conversations API & Database Storage (Phase 5)."""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.conversation.session_manager import session_manager

client = TestClient(app)


def test_create_and_list_conversations():
    """Test creating and listing conversations."""
    # Create conversation
    res = client.post("/api/v1/conversations", json={"title": "Test Weekend Trip"})
    assert res.status_code == 200
    data = res.json()
    assert "conversation_id" in data
    cid = data["conversation_id"]
    assert data["title"] == "Test Weekend Trip"

    # List conversations
    res_list = client.get("/api/v1/conversations")
    assert res_list.status_code == 200
    items = res_list.json()["items"]
    assert any(c["conversation_id"] == cid for c in items)

    # Clean up
    client.delete(f"/api/v1/conversations/{cid}")


def test_conversation_messages_persistence():
    """Test message persistence and retrieval."""
    res = client.post("/api/v1/conversations", json={"title": "Chat History Test"})
    cid = res.json()["conversation_id"]

    # Add messages through session manager
    session_manager.add_message(cid, "user", "How do I get to Lake Motosu?")
    session_manager.add_message(cid, "assistant", "Take the Blue Line bus from Kawaguchiko Station.")

    # Retrieve via API
    res_msgs = client.get(f"/api/v1/conversations/{cid}/messages")
    assert res_msgs.status_code == 200
    msgs = res_msgs.json()["messages"]
    assert len(msgs) == 2
    assert msgs[0]["text"] == "How do I get to Lake Motosu?"
    assert msgs[1]["text"] == "Take the Blue Line bus from Kawaguchiko Station."
    assert msgs[0]["sender"] == "user"
    assert msgs[1]["sender"] == "hana"

    # Clean up
    client.delete(f"/api/v1/conversations/{cid}")


def test_update_and_delete_conversation():
    """Test renaming, pinning, and deleting conversation."""
    res = client.post("/api/v1/conversations", json={"title": "Initial Title"})
    cid = res.json()["conversation_id"]

    # Rename and pin
    res_patch = client.patch(f"/api/v1/conversations/{cid}", json={"title": "Updated Title", "pinned": True})
    assert res_patch.status_code == 200

    # Verify update
    res_get = client.get(f"/api/v1/conversations/{cid}")
    assert res_get.status_code == 200
    assert res_get.json()["title"] == "Updated Title"
    assert res_get.json()["pinned"] is True

    # Delete
    res_del = client.delete(f"/api/v1/conversations/{cid}")
    assert res_del.status_code == 200

    # Verify not found
    res_check = client.get(f"/api/v1/conversations/{cid}")
    assert res_check.status_code == 404
