"""FujiNova Database-Backed Conversation Session Manager & Multi-Turn Context Memory."""
import time
import json
import uuid
import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from backend.app.models.traveller import TravellerProfile
from backend.app.core.database import get_db_connection


class ChatTurn(BaseModel):
    role: str  # "user", "assistant", "system", "tool"
    content: str
    timestamp: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionState(BaseModel):
    session_id: str
    created_at: float = Field(default_factory=time.time)
    last_active: float = Field(default_factory=time.time)
    messages: List[ChatTurn] = Field(default_factory=list)
    profile: Dict[str, Any] = Field(default_factory=lambda: TravellerProfile().model_dump())
    active_itinerary: Optional[Dict[str, Any]] = None
    language_preference: str = "en"
    asked_questions: List[str] = Field(default_factory=list)
    identified_places: List[Dict[str, Any]] = Field(default_factory=list)
    identified_journeys: List[Dict[str, Any]] = Field(default_factory=list)
    identified_alternatives: List[Dict[str, Any]] = Field(default_factory=list)


class ConversationSummary(BaseModel):
    conversation_id: str
    title: str
    created_at: str
    updated_at: str
    last_message_at: str
    archived: bool = False
    pinned: bool = False
    preview: str = ""
    message_count: int = 0


class SessionManager:
    """Hybrid in-memory cache and persistent SQLite conversation manager."""

    def __init__(self, max_context_messages: int = 12):
        self.sessions: Dict[str, SessionState] = {}
        self.max_context_messages = max_context_messages

    def _now_iso(self) -> str:
        return datetime.datetime.now(datetime.timezone.utc).isoformat()

    def get_or_create(self, session_id: str) -> SessionState:
        if session_id not in self.sessions:
            # Check SQLite if this conversation exists
            state = SessionState(session_id=session_id)
            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT role, content, timestamp, metadata FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC;",
                        (session_id,)
                    )
                    rows = cursor.fetchall()
                    for r in rows:
                        meta = {}
                        try:
                            meta = json.loads(r["metadata"] or "{}")
                        except Exception:
                            pass
                        state.messages.append(
                            ChatTurn(
                                role=r["role"],
                                content=r["content"],
                                timestamp=float(r["timestamp"]) if str(r["timestamp"]).replace(".", "", 1).isdigit() else time.time(),
                                metadata=meta
                            )
                        )
            except Exception:
                pass
            self.sessions[session_id] = state

        session = self.sessions[session_id]
        session.last_active = time.time()
        return session

    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        session = self.get_or_create(session_id)
        now_ts = time.time()
        now_iso = self._now_iso()
        meta = metadata or {}

        session.messages.append(
            ChatTurn(role=role, content=content, timestamp=now_ts, metadata=meta)
        )

        # Persist to SQLite
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Ensure conversation record exists
                title = "New Trip Inquiry"
                if role == "user":
                    clean_first = content.strip().split("\n")[0][:45]
                    if len(clean_first) > 3:
                        title = clean_first

                cursor.execute("""
                INSERT INTO conversations (conversation_id, title, created_at, updated_at, last_message_at, archived, pinned)
                VALUES (?, ?, ?, ?, ?, 0, 0)
                ON CONFLICT(conversation_id) DO UPDATE SET
                    updated_at = excluded.updated_at,
                    last_message_at = excluded.last_message_at;
                """, (session_id, title, now_iso, now_iso, now_iso))

                msg_id = f"msg_{uuid.uuid4().hex[:12]}"
                cursor.execute("""
                INSERT INTO messages (message_id, conversation_id, role, content, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?);
                """, (msg_id, session_id, role, content, str(now_ts), json.dumps(meta)))
                conn.commit()
        except Exception as e:
            # Fallback gracefully without breaking streaming turn
            pass

    def get_context_messages(self, session_id: str) -> List[Dict[str, str]]:
        """Return the windowed conversational history formatted for the LLM."""
        session = self.get_or_create(session_id)
        recent = session.messages[-self.max_context_messages:]
        return [
            {"role": m.role if m.role in ("user", "assistant", "system") else "assistant", "content": m.content}
            for m in recent
        ]

    def list_conversations(self, search_query: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve persisted conversations with previews and counts."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                query = """
                SELECT c.conversation_id, c.title, c.created_at, c.updated_at, c.last_message_at,
                       c.archived, c.pinned,
                       COUNT(m.message_id) as message_count,
                       (SELECT content FROM messages WHERE conversation_id = c.conversation_id ORDER BY timestamp DESC LIMIT 1) as preview
                FROM conversations c
                LEFT JOIN messages m ON c.conversation_id = m.conversation_id
                """
                params = []
                if search_query and search_query.strip():
                    query += " WHERE c.title LIKE ? OR preview LIKE ?"
                    sq = f"%{search_query.strip()}%"
                    params.extend([sq, sq])

                query += " GROUP BY c.conversation_id ORDER BY c.pinned DESC, c.updated_at DESC LIMIT ?;"
                params.append(limit)

                cursor.execute(query, params)
                rows = cursor.fetchall()
                results = []
                for r in rows:
                    results.append({
                        "conversation_id": r["conversation_id"],
                        "title": r["title"],
                        "created_at": r["created_at"],
                        "updated_at": r["updated_at"],
                        "last_message_at": r["last_message_at"],
                        "archived": bool(r["archived"]),
                        "pinned": bool(r["pinned"]),
                        "message_count": r["message_count"] or 0,
                        "preview": (r["preview"] or "")[:80]
                    })
                return results
        except Exception:
            return []

    def get_conversation_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Fetch all messages for a specific conversation."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT message_id, role, content, timestamp, metadata FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC;",
                    (session_id,)
                )
                rows = cursor.fetchall()
                messages = []
                for r in rows:
                    meta = {}
                    try:
                        meta = json.loads(r["metadata"] or "{}")
                    except Exception:
                        pass
                    messages.append({
                        "id": r["message_id"],
                        "sender": "hana" if r["role"] in ("assistant", "model") else "user",
                        "role": r["role"],
                        "text": r["content"],
                        "timestamp": r["timestamp"],
                        "metadata": meta
                    })
                return messages
        except Exception:
            return []

    def update_conversation(
        self,
        session_id: str,
        title: Optional[str] = None,
        pinned: Optional[bool] = None,
        archived: Optional[bool] = None
    ) -> bool:
        """Update metadata of a conversation."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                updates = ["updated_at = ?"]
                params: List[Any] = [self._now_iso()]

                if title is not None:
                    updates.append("title = ?")
                    params.append(title.strip())
                if pinned is not None:
                    updates.append("pinned = ?")
                    params.append(1 if pinned else 0)
                if archived is not None:
                    updates.append("archived = ?")
                    params.append(1 if archived else 0)

                params.append(session_id)
                cursor.execute(f"UPDATE conversations SET {', '.join(updates)} WHERE conversation_id = ?;", params)
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False

    def clear_session(self, session_id: str) -> bool:
        """Clear conversation in-memory and delete from database."""
        if session_id in self.sessions:
            del self.sessions[session_id]

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM messages WHERE conversation_id = ?;", (session_id,))
                cursor.execute("DELETE FROM conversations WHERE conversation_id = ?;", (session_id,))
                conn.commit()
                return True
        except Exception:
            return False


# Global singleton instance
session_manager = SessionManager()
