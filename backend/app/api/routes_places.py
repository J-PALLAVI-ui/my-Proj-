"""FujiNova Places API Routes & Search Query Services."""
import sqlite3
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query, status
from backend.app.core.database import get_db_connection
from backend.app.models.place import Place, PlaceMarker

router = APIRouter(prefix="/api/v1/places", tags=["Places"])


class PaginatedPlacesResponse(BaseModel):
    total_count: int
    page: int
    page_size: int
    has_next: bool
    results: List[Place]


class PlacesStatsResponse(BaseModel):
    total_destinations: int
    famous_destinations: int
    hidden_gems: int
    categories: Dict[str, int]
    regions: Dict[str, int]


def search_places_db(
    query: Optional[str] = None,
    category: Optional[str] = None,
    discovery_type: Optional[str] = None,
    region_id: Optional[str] = None,
    general_admission_type: Optional[str] = None,
    accessibility_status: Optional[str] = None,
    indoor_alternative: Optional[bool] = None,
    opening_status: Optional[str] = None,
    min_fuji_view_rating: Optional[int] = None,
    min_lat: Optional[float] = None,
    max_lat: Optional[float] = None,
    min_lon: Optional[float] = None,
    max_lon: Optional[float] = None,
    limit: int = 20,
    offset: int = 0,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search and filter places directly from the canonical SQLite database."""
    sql = "SELECT * FROM places WHERE 1=1"
    params: List[Any] = []

    if query and isinstance(query, str):
        sql += " AND (name_ja LIKE ? OR name_en LIKE ? OR sub_category LIKE ? OR interests LIKE ? OR description LIKE ?)"
        like_str = f"%{query}%"
        params.extend([like_str, like_str, like_str, like_str, like_str])

    if category and isinstance(category, str):
        sql += " AND primary_category = ?"
        params.append(category)

    if discovery_type and isinstance(discovery_type, str):
        sql += " AND discovery_type = ?"
        params.append(discovery_type.upper())

    if region_id and isinstance(region_id, str):
        sql += " AND region_id = ?"
        params.append(region_id.lower())

    if general_admission_type and isinstance(general_admission_type, str):
        sql += " AND general_admission_type = ?"
        params.append(general_admission_type.upper())

    if accessibility_status and isinstance(accessibility_status, str):
        sql += " AND accessibility_status = ?"
        params.append(accessibility_status)

    if indoor_alternative is not None and isinstance(indoor_alternative, (bool, int)):
        sql += " AND indoor_alternative = ?"
        params.append(1 if indoor_alternative else 0)

    if opening_status and isinstance(opening_status, str):
        sql += " AND opening_status = ?"
        params.append(opening_status)

    if min_fuji_view_rating is not None and isinstance(min_fuji_view_rating, (int, float)):
        sql += " AND fuji_view_rating >= ?"
        params.append(min_fuji_view_rating)

    if min_lat is not None and max_lat is not None and min_lon is not None and max_lon is not None:
        sql += " AND (latitude BETWEEN ? AND ?) AND (longitude BETWEEN ? AND ?)"
        params.extend([min_lat, max_lat, min_lon, max_lon])

    sql += " ORDER BY fuji_view_rating DESC, name_ja ASC LIMIT ? OFFSET ?;"
    params.extend([limit, offset])

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_places_count_db(
    query: Optional[str] = None,
    category: Optional[str] = None,
    discovery_type: Optional[str] = None,
    region_id: Optional[str] = None,
    general_admission_type: Optional[str] = None,
    accessibility_status: Optional[str] = None,
    indoor_alternative: Optional[bool] = None,
    opening_status: Optional[str] = None,
    min_fuji_view_rating: Optional[int] = None,
    min_lat: Optional[float] = None,
    max_lat: Optional[float] = None,
    min_lon: Optional[float] = None,
    max_lon: Optional[float] = None,
    db_path: Optional[str] = None
) -> int:
    """Retrieve total count of matching places for pagination."""
    sql = "SELECT COUNT(*) FROM places WHERE 1=1"
    params: List[Any] = []

    if query and isinstance(query, str):
        sql += " AND (name_ja LIKE ? OR name_en LIKE ? OR sub_category LIKE ? OR interests LIKE ? OR description LIKE ?)"
        like_str = f"%{query}%"
        params.extend([like_str, like_str, like_str, like_str, like_str])

    if category and isinstance(category, str):
        sql += " AND primary_category = ?"
        params.append(category)

    if discovery_type and isinstance(discovery_type, str):
        sql += " AND discovery_type = ?"
        params.append(discovery_type.upper())

    if region_id and isinstance(region_id, str):
        sql += " AND region_id = ?"
        params.append(region_id.lower())

    if general_admission_type and isinstance(general_admission_type, str):
        sql += " AND general_admission_type = ?"
        params.append(general_admission_type.upper())

    if accessibility_status and isinstance(accessibility_status, str):
        sql += " AND accessibility_status = ?"
        params.append(accessibility_status)

    if indoor_alternative is not None and isinstance(indoor_alternative, (bool, int)):
        sql += " AND indoor_alternative = ?"
        params.append(1 if indoor_alternative else 0)

    if opening_status and isinstance(opening_status, str):
        sql += " AND opening_status = ?"
        params.append(opening_status)

    if min_fuji_view_rating is not None and isinstance(min_fuji_view_rating, (int, float)):
        sql += " AND fuji_view_rating >= ?"
        params.append(min_fuji_view_rating)

    if min_lat is not None and max_lat is not None and min_lon is not None and max_lon is not None:
        sql += " AND (latitude BETWEEN ? AND ?) AND (longitude BETWEEN ? AND ?)"
        params.extend([min_lat, max_lat, min_lon, max_lon])

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchone()[0]


def get_place_by_id(place_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve single place by its canonical place_id."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM places WHERE place_id = ?;", (place_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


@router.get("/markers", response_model=List[PlaceMarker])
def get_map_markers(
    category: Optional[str] = Query(None, description="Filter markers by category"),
    discovery_type: Optional[str] = Query(None, description="Filter by discovery_type (FAMOUS or HIDDEN_GEM)"),
    region_id: Optional[str] = Query(None, description="Filter by region (e.g. kawaguchiko, fujiyoshida)"),
    min_fuji_view: Optional[int] = Query(None, ge=1, le=5),
    limit: int = Query(300, ge=1, le=500)
):
    """Returns lightweight map markers for 2D Map and 3D Digital Twin rendering without full payload."""
    sql = """
    SELECT place_id, name_ja, name_en, latitude, longitude,
           primary_category, discovery_type, fuji_view_rating,
           image_url, region_id, opening_status, general_admission_type
    FROM places WHERE 1=1
    """
    params: List[Any] = []

    if category:
        sql += " AND primary_category = ?"
        params.append(category)

    if discovery_type:
        sql += " AND discovery_type = ?"
        params.append(discovery_type.upper())

    if region_id:
        sql += " AND region_id = ?"
        params.append(region_id.lower())

    if min_fuji_view is not None:
        sql += " AND fuji_view_rating >= ?"
        params.append(min_fuji_view)

    sql += " ORDER BY fuji_view_rating DESC, name_ja ASC LIMIT ?;"
    params.append(limit)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


@router.get("/stats", response_model=PlacesStatsResponse)
def get_places_statistics():
    """Retrieve live counts and distribution metrics across the destination database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM places;")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM places WHERE discovery_type = 'FAMOUS';")
        famous = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM places WHERE discovery_type = 'HIDDEN_GEM';")
        hidden = cursor.fetchone()[0]

        cursor.execute("SELECT primary_category, COUNT(*) FROM places GROUP BY primary_category;")
        categories = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute("SELECT region_id, COUNT(*) FROM places WHERE region_id IS NOT NULL GROUP BY region_id;")
        regions = {row[0]: row[1] for row in cursor.fetchall()}

        return PlacesStatsResponse(
            total_destinations=total,
            famous_destinations=famous,
            hidden_gems=hidden,
            categories=categories,
            regions=regions
        )


@router.get("/search", response_model=PaginatedPlacesResponse)
def search_places_paginated(
    query: Optional[str] = Query(None, description="Free text search on name, tags, or description"),
    category: Optional[str] = Query(None, description="Category filter"),
    discovery_type: Optional[str] = Query(None, description="FAMOUS or HIDDEN_GEM"),
    region_id: Optional[str] = Query(None, description="Region identifier"),
    general_admission_type: Optional[str] = Query(None, description="FREE or PAID"),
    accessibility_status: Optional[str] = Query(None),
    indoor_alternative: Optional[bool] = Query(None),
    opening_status: Optional[str] = Query(None),
    min_fuji_view_rating: Optional[int] = Query(None, ge=1, le=5),
    min_lat: Optional[float] = Query(None),
    max_lat: Optional[float] = Query(None),
    min_lon: Optional[float] = Query(None),
    max_lon: Optional[float] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """Paginated search endpoint with total count metadata and rich filtering."""
    offset = (page - 1) * page_size
    total_count = get_places_count_db(
        query=query,
        category=category,
        discovery_type=discovery_type,
        region_id=region_id,
        general_admission_type=general_admission_type,
        accessibility_status=accessibility_status,
        indoor_alternative=indoor_alternative,
        opening_status=opening_status,
        min_fuji_view_rating=min_fuji_view_rating,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon
    )
    results = search_places_db(
        query=query,
        category=category,
        discovery_type=discovery_type,
        region_id=region_id,
        general_admission_type=general_admission_type,
        accessibility_status=accessibility_status,
        indoor_alternative=indoor_alternative,
        opening_status=opening_status,
        min_fuji_view_rating=min_fuji_view_rating,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
        limit=page_size,
        offset=offset
    )
    has_next = (offset + len(results)) < total_count

    return PaginatedPlacesResponse(
        total_count=total_count,
        page=page,
        page_size=page_size,
        has_next=has_next,
        results=results
    )


@router.get("", response_model=List[Place])
def list_places(
    query: Optional[str] = Query(None, description="Free text search on Japanese/English name or subcategory"),
    category: Optional[str] = Query(None, description="Filter by primary_category (viewpoint, museum, shrine, etc.)"),
    discovery_type: Optional[str] = Query(None, description="FAMOUS or HIDDEN_GEM"),
    region_id: Optional[str] = Query(None, description="Region identifier"),
    general_admission_type: Optional[str] = Query(None, description="FREE or PAID"),
    accessibility_status: Optional[str] = Query(None, description="Filter by accessibility_status"),
    indoor_alternative: Optional[bool] = Query(None, description="Filter places suitable as rainy day alternatives"),
    opening_status: Optional[str] = Query(None, description="Filter by opening status"),
    min_fuji_view_rating: Optional[int] = Query(None, ge=1, le=5, description="Minimum Fuji view rating (1-5)"),
    limit: int = Query(20, ge=1, le=300),
    offset: int = Query(0, ge=0)
):
    """List and filter verified places (backwards-compatible array response)."""
    places = search_places_db(
        query=query,
        category=category,
        discovery_type=discovery_type,
        region_id=region_id,
        general_admission_type=general_admission_type,
        accessibility_status=accessibility_status,
        indoor_alternative=indoor_alternative,
        opening_status=opening_status,
        min_fuji_view_rating=min_fuji_view_rating,
        limit=limit,
        offset=offset
    )
    return places


@router.get("/{place_id}", response_model=Place)
def get_place(place_id: str):
    """Get detailed verified place metadata by ID."""
    place = get_place_by_id(place_id)
    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Place with ID '{place_id}' not found in verified database."
        )
    return place
