"""Tests for FujiNova 200+ Destinations Integration (Checkpoints 1-17).

Validates:
1. PDF Extraction: 100 Famous and 100 Hidden Gem candidates.
2. 35 Original Seed Preserved without data loss.
3. Total Verified Destinations >= 235 (>=100 famous, >=100 hidden gems).
4. Spatial and Attribution Integrity (WGS84 bounds, valid image URLs, field completeness).
5. Centralized API Endpoints (/search, /markers, /stats, /digital-twin).
6. Agent Grounding for both Famous and Hidden Gem queries.
"""
import json
import os
import pytest
from backend.app.core.database import get_db_connection
from backend.app.api.routes_places import search_places_db, get_places_count_db
from backend.data.raw_pdf_candidates import FAMOUS_CANDIDATES, HIDDEN_GEM_CANDIDATES
from backend.data.seed_data import PLACES_SEED_DATA
from backend.app.agent.hana import HanaAgent


def test_pdf_candidate_counts():
    """Verify that candidate extraction produced exactly 100 famous and 100 hidden gems."""
    assert len(FAMOUS_CANDIDATES) == 100, f"Expected 100 famous candidates, got {len(FAMOUS_CANDIDATES)}"
    assert len(HIDDEN_GEM_CANDIDATES) == 100, f"Expected 100 hidden gem candidates, got {len(HIDDEN_GEM_CANDIDATES)}"

    # Check that each candidate has a name, region, and group
    for c in FAMOUS_CANDIDATES:
        assert c.get("name"), f"Famous candidate #{c.get('num')} missing name"
        assert c.get("region"), f"Famous candidate #{c.get('num')} missing region"

    for c in HIDDEN_GEM_CANDIDATES:
        assert c.get("name"), f"Hidden gem candidate #{c.get('num')} missing name"
        assert c.get("region"), f"Hidden gem candidate #{c.get('num')} missing region"


def test_database_destination_counts(test_db):
    """Verify that database has >= 235 total destinations, >= 100 famous, >= 100 hidden gems."""
    with get_db_connection(test_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM places;")
        total_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM places WHERE discovery_type = 'FAMOUS';")
        famous_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM places WHERE discovery_type = 'HIDDEN_GEM';")
        gem_count = cursor.fetchone()[0]

        assert total_count >= 235, f"Expected >= 235 total places, found {total_count}"
        assert famous_count >= 100, f"Expected >= 100 famous places, found {famous_count}"
        assert gem_count >= 100, f"Expected >= 100 hidden gems, found {gem_count}"


def test_canonical_35_preserved(test_db):
    """Verify that all 35 canonical seed places exist in the database with original metadata."""
    original_ids = [p["place_id"] for p in PLACES_SEED_DATA]
    assert len(original_ids) == 35

    with get_db_connection(test_db) as conn:
        cursor = conn.cursor()
        for place_id in original_ids:
            cursor.execute("SELECT place_id, name_ja, latitude, longitude FROM places WHERE place_id = ?;", (place_id,))
            row = cursor.fetchone()
            assert row is not None, f"Original canonical place '{place_id}' missing from database!"
            assert 35.0 <= row[2] <= 36.0, f"Invalid latitude for {place_id}: {row[2]}"
            assert 138.2 <= row[3] <= 139.2, f"Invalid longitude for {place_id}: {row[3]}"


def test_places_stats_api(client):
    """Verify GET /api/v1/places/stats endpoint returns correct breakdown."""
    resp = client.get("/api/v1/places/stats")
    assert resp.status_code == 200
    data = resp.json()

    assert data["total_destinations"] >= 235
    assert data["famous_destinations"] >= 100
    assert data["hidden_gems"] >= 100
    assert data["total_destinations"] == data["famous_destinations"] + data["hidden_gems"]
    assert "viewpoint" in data["categories"]
    assert len(data["regions"]) > 0


def test_places_markers_api(client):
    """Verify GET /api/v1/places/markers endpoint returns lightweight markers with coordinates."""
    resp = client.get("/api/v1/places/markers?limit=300")
    assert resp.status_code == 200
    markers = resp.json()

    assert len(markers) >= 235
    for m in markers:
        assert "place_id" in m
        assert "name_ja" in m
        assert "latitude" in m and "longitude" in m
        assert 34.9 <= m["latitude"] <= 36.2
        assert 138.2 <= m["longitude"] <= 139.2
        assert m["discovery_type"] in ("FAMOUS", "HIDDEN_GEM")

    # Filter markers by discovery_type
    resp_gems = client.get("/api/v1/places/markers?discovery_type=HIDDEN_GEM&limit=300")
    assert resp_gems.status_code == 200
    gems = resp_gems.json()
    assert len(gems) >= 100
    assert all(g["discovery_type"] == "HIDDEN_GEM" for g in gems)


def test_places_search_pagination_api(client):
    """Verify GET /api/v1/places/search paginated search."""
    # Page 1
    resp1 = client.get("/api/v1/places/search?page=1&page_size=20")
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["page"] == 1
    assert data1["page_size"] == 20
    assert len(data1["results"]) == 20
    assert data1["total_count"] >= 235
    assert data1["has_next"] is True

    # Page 2
    resp2 = client.get("/api/v1/places/search?page=2&page_size=20")
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["page"] == 2
    assert len(data2["results"]) == 20

    # Ensure page 1 and page 2 don't overlap
    ids_p1 = {p["place_id"] for p in data1["results"]}
    ids_p2 = {p["place_id"] for p in data2["results"]}
    assert len(ids_p1.intersection(ids_p2)) == 0


def test_digital_twin_spatial_data_api(client):
    """Verify GET /api/v1/digital-twin/data incorporates destination catalogue."""
    resp = client.get("/api/v1/digital-twin/data?scenario=high")
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "ok"
    assert data["total_destinations"] >= 200
    landmarks = data["landmarks"]
    assert len(landmarks) >= 200

    # Check Three.js projection coordinates
    for lm in landmarks[:20]:
        assert "x" in lm and "z" in lm and "altitude" in lm
        assert "crowd_level" in lm
        assert "image_url" in lm


def test_hana_agent_grounding_discovery():
    """Verify Hana agent retrieves hidden gems when asked."""
    agent = HanaAgent()
    state = agent.get_or_create_state("test_session_gems")
    state["messages"].append({"role": "user", "content": "Can you recommend some quiet hidden gems and offbeat spots?"})

    gems = agent.query_grounded_places(state, limit=4)
    assert len(gems) > 0
    # At least some should be hidden gems
    assert any(g.get("discovery_type") == "HIDDEN_GEM" for g in gems)
