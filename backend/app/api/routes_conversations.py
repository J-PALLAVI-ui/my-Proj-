"""FujiNova Persistent Conversations API Routes (Phase 5)."""
import uuid
import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.app.services.conversation.session_manager import session_manager
from backend.app.core.database import get_db_connection

router = APIRouter(prefix="/api/v1/conversations", tags=["Conversations"])


class CreateConversationRequest(BaseModel):
    title: Optional[str] = "New Conversation"
    session_id: Optional[str] = None


class UpdateConversationRequest(BaseModel):
    title: Optional[str] = None
    pinned: Optional[bool] = None
    archived: Optional[bool] = None


@router.get("", response_model=Dict[str, Any])
def list_conversations(
    q: Optional[str] = Query(None, description="Search term for title or message content"),
    limit: int = Query(50, ge=1, le=100)
):
    """Retrieve all conversations ordered by pinned and recent activity."""
    items = session_manager.list_conversations(search_query=q, limit=limit)
    return {
        "items": items,
        "total": len(items)
    }


@router.post("", response_model=Dict[str, Any])
def create_conversation(req: CreateConversationRequest):
    """Create a new persistent conversation."""
    cid = req.session_id or f"fn_{int(datetime.datetime.now().timestamp())}_{uuid.uuid4().hex[:6]}"
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    title = (req.title or "New Conversation").strip()

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO conversations (conversation_id, title, created_at, updated_at, last_message_at, archived, pinned)
            VALUES (?, ?, ?, ?, ?, 0, 0)
            ON CONFLICT(conversation_id) DO NOTHING;
            """, (cid, title, now_iso, now_iso, now_iso))
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error creating conversation: {e}")

    return {
        "conversation_id": cid,
        "title": title,
        "created_at": now_iso,
        "updated_at": now_iso
    }


@router.get("/{conversation_id}")
def get_conversation(conversation_id: str):
    """Get single conversation metadata."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT conversation_id, title, created_at, updated_at, last_message_at, archived, pinned FROM conversations WHERE conversation_id = ?;",
                (conversation_id,)
            )
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Conversation not found")
            return {
                "conversation_id": row["conversation_id"],
                "title": row["title"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "last_message_at": row["last_message_at"],
                "archived": bool(row["archived"]),
                "pinned": bool(row["pinned"])
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}/messages")
def get_conversation_messages(conversation_id: str):
    """Fetch complete persistent chat history for a conversation."""
    messages = session_manager.get_conversation_messages(conversation_id)
    return {
        "conversation_id": conversation_id,
        "messages": messages,
        "total": len(messages)
    }


@router.patch("/{conversation_id}")
def update_conversation(conversation_id: str, req: UpdateConversationRequest):
    """Rename, pin, or archive a conversation."""
    ok = session_manager.update_conversation(
        session_id=conversation_id,
        title=req.title,
        pinned=req.pinned,
        archived=req.archived
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Conversation not found or could not be updated")
    return {"status": "success", "conversation_id": conversation_id}


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str):
    """Permanently delete a conversation and its messages."""
    session_manager.clear_session(conversation_id)
    return {"status": "deleted", "conversation_id": conversation_id}
