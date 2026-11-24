"""Tests for FujiNova Database Schema, Seed Verification, and Query API (Acceptance Tests T1-02 & T1-03)."""
import sqlite3
from backend.app.core.database import init_db, get_db_connection
from backend.data.seed_places import seed_database
from backend.app.api.routes_places import search_places_db, get_place_by_id


def test_t1_02_database_initialization(tmp_path):
    """T1-02: SQLite DB initialization creates canonical places table with WAL mode and indexes."""
    db_file = str(tmp_path / "test_init.db")
    init_db(db_file)

    # Check WAL mode
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode;")
        mode = cursor.fetchone()[0]
        assert mode.lower() == "wal"

    # Check foreign keys via get_db_connection
    with get_db_connection(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys;")
        fk = cursor.fetchone()[0]
        assert fk == 1

        # Check places table schema columns
        cursor.execute("PRAGMA table_info(places);")
        columns = {row[1]: row[2] for row in cursor.fetchall()}

        required_columns = [
            "place_id", "name_ja", "name_en", "latitude", "longitude",
            "coords_source", "primary_category", "sub_category",
            "opening_status", "opening_hours_text", "opening_hours_source",
            "general_admission_type", "general_admission_fee_jpy",
            "optional_activities_fee_desc", "admission_fee_source",
            "accessibility_status", "accessibility_evidence", "stair_step_count",
            "accessibility_source", "fuji_view_rating", "indoor_alternative",
            "provenance_tier", "source_url", "required_attribution",
            "source_retrieval_date", "last_verified_date"
        ]
        for col in required_columns:
            assert col in columns, f"Missing required column: {col}"

        # Check indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
        indexes = [row[0] for row in cursor.fetchall()]
        assert "idx_places_spatial" in indexes
        assert "idx_places_category" in indexes
        assert "idx_places_indoor" in indexes
        assert "idx_places_access" in indexes
        assert "idx_places_status" in indexes


def test_t1_03_seed_ingestion_and_constraints(test_db):
    """T1-03: Seed data ingestion loads exactly 35 verified places with field-level provenance."""
    with get_db_connection(test_db) as conn:
        cursor = conn.cursor()

        # Count must be exactly 35
        cursor.execute("SELECT COUNT(*) FROM places;")
        count = cursor.fetchone()[0]
        assert count == 35, f"Expected 35 places, got {count}"

        # Verify no nulls in critical provenance and safety fields
        cursor.execute("""
            SELECT place_id, name_ja, latitude, longitude, coords_source,
                   primary_category, opening_status, general_admission_type,
                   accessibility_status, fuji_view_rating, provenance_tier,
                   source_url, required_attribution
            FROM places
            WHERE name_ja IS NULL
               OR latitude IS NULL
               OR longitude IS NULL
               OR coords_source IS NULL
               OR primary_category IS NULL
               OR opening_status IS NULL
               OR general_admission_type IS NULL
               OR accessibility_status IS NULL
               OR fuji_view_rating IS NULL
               OR provenance_tier IS NULL
               OR source_url IS NULL
               OR required_attribution IS NULL;
        """)
        invalid_rows = cursor.fetchall()
        assert len(invalid_rows) == 0, f"Found rows with missing mandatory fields: {invalid_rows}"

        # Verify coordinates are in valid Fuji / Yamanashi geographic bounds (lat: 35.0-36.0, lon: 138.2-139.2)
        cursor.execute("SELECT place_id, latitude, longitude FROM places WHERE latitude < 35.0 OR latitude > 36.0 OR longitude < 138.2 OR longitude > 139.2;")
        out_of_bounds = cursor.fetchall()
        assert len(out_of_bounds) == 0, f"Places out of expected geographic bounds: {out_of_bounds}"

        # Verify Lake Motosu Nakanokura Pass trail admission is FREE (addressing previous contradiction)
        cursor.execute("SELECT general_admission_type, general_admission_fee_jpy FROM places WHERE place_id = 'motosuko_viewpoint';")
        pass_row = cursor.fetchone()
        assert pass_row is not None
        assert pass_row[0] == "FREE"
        assert pass_row[1] is None

        # Verify Arakurayama Sengen Park step count is exactly 398
        cursor.execute("SELECT stair_step_count, accessibility_status FROM places WHERE place_id = 'arakurayama_chureito';")
        arakura = cursor.fetchone()
        assert arakura is not None
        assert arakura[0] == 398
        assert arakura[1] == "STEEP_STAIRS"


def test_places_search_and_filter_api(test_db, client):
    """Verify search_places_db and API query filtering."""
    # Search by keyword
    results = search_places_db(query="Oishi", db_path=test_db)
    assert len(results) >= 1
    assert any("大石公園" in r["name_ja"] for r in results)

    # Filter by category
    museums = search_places_db(category="museum", db_path=test_db)
    assert len(museums) == 7
    for m in museums:
        assert m["primary_category"] == "museum"

    # Filter by barrier-free accessible
    accessible = search_places_db(accessibility_status="VERIFIED_ACCESSIBLE", db_path=test_db)
    assert len(accessible) == 20
    for a in accessible:
        assert a["accessibility_status"] == "VERIFIED_ACCESSIBLE"

    # Filter by indoor alternative
    indoor = search_places_db(indoor_alternative=True, db_path=test_db)
    assert len(indoor) > 0
    for i in indoor:
        assert i["indoor_alternative"] in (1, True)

    # API endpoint check
    resp = client.get("/api/v1/places?category=viewpoint")
    assert resp.status_code == 200
    places = resp.json()
    assert len(places) == 6
    assert all(p["primary_category"] == "viewpoint" for p in places)

    # Single place detail
    resp_single = client.get("/api/v1/places/kawaguchiko_oishi_park")
    assert resp_single.status_code == 200
    place = resp_single.json()
    assert place["name_ja"] == "大石公園"
    assert place["name_en"] == "Oishi Park"
    assert place["fuji_view_rating"] == 5

    # 404 for unknown place
    resp_404 = client.get("/api/v1/places/non_existent_place_xyz")
    assert resp_404.status_code == 404
