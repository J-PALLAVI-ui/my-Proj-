"""FujiNova Database Connection & Schema Management."""
import os
import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional
from backend.app.core.config import settings


def get_db_path() -> str:
    """Extract filesystem path from DATABASE_URL."""
    url = settings.DATABASE_URL
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "")
    return url


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize SQLite database with WAL mode and canonical tables."""
    target_path = db_path or get_db_path()
    os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)

    with sqlite3.connect(target_path) as conn:
        cursor = conn.cursor()
        # Enable Write-Ahead Logging for high concurrent read performance
        cursor.execute("PRAGMA journal_mode = WAL;")
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Create canonical places table with field-level provenance
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS places (
            place_id TEXT PRIMARY KEY,
            name_ja TEXT NOT NULL,
            name_en TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            coords_source TEXT NOT NULL,
            primary_category TEXT NOT NULL,
            sub_category TEXT,
            opening_status TEXT NOT NULL CHECK(
                opening_status IN ('ALWAYS_OPEN', 'REGULAR_HOURS', 'SEASONAL_CLOSURE', 'TEMPORARILY_CLOSED', 'UNKNOWN')
            ),
            opening_hours_text TEXT,
            opening_hours_source TEXT NOT NULL,
            general_admission_type TEXT NOT NULL CHECK(
                general_admission_type IN ('FREE', 'PAID', 'UNKNOWN')
            ),
            general_admission_fee_jpy INTEGER,
            optional_activities_fee_desc TEXT,
            admission_fee_source TEXT NOT NULL,
            accessibility_status TEXT NOT NULL CHECK(
                accessibility_status IN ('VERIFIED_ACCESSIBLE', 'PARTIAL_STEPS', 'STEEP_STAIRS', 'INACCESSIBLE', 'UNKNOWN')
            ),
            accessibility_evidence TEXT,
            stair_step_count INTEGER,
            accessibility_source TEXT NOT NULL,
            fuji_view_rating INTEGER NOT NULL CHECK(fuji_view_rating BETWEEN 1 AND 5),
            indoor_alternative BOOLEAN NOT NULL,
            provenance_tier TEXT NOT NULL CHECK(
                provenance_tier IN ('OFFICIAL_GOV', 'OFFICIAL_OPERATOR', 'COMMUNITY_OSM', 'UNVERIFIED')
            ),
            source_url TEXT NOT NULL,
            required_attribution TEXT NOT NULL,
            source_retrieval_date TEXT NOT NULL,
            last_verified_date TEXT NOT NULL
        );
        """)

        # Indexes for fast spatial and attribute filtering
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_places_spatial ON places (latitude, longitude);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_places_category ON places (primary_category);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_places_indoor ON places (indoor_alternative);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_places_access ON places (accessibility_status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_places_status ON places (opening_status);")

        # Persistent Conversations and Messages Schema (Phase 5)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            last_message_at TEXT NOT NULL,
            archived INTEGER DEFAULT 0,
            pinned INTEGER DEFAULT 0
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            metadata TEXT DEFAULT '{}',
            FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE
        );
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages (conversation_id, timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conv_updated ON conversations (updated_at DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conv_pinned ON conversations (pinned DESC, updated_at DESC);")
        conn.commit()


@contextmanager
def get_db_connection(db_path: Optional[str] = None) -> Generator[sqlite3.Connection, None, None]:
    """Provide a transactional SQLite database connection."""
    target_path = db_path or get_db_path()
    conn = sqlite3.connect(target_path, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
