"""FujiNova Places API Routes & Search Query Services."""
import sqlite3
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status
from backend.app.core.database import get_db_connection
from backend.app.models.place import Place

router = APIRouter(prefix="/api/v1/places", tags=["Places"])


def search_places_db(
    query: Optional[str] = None,
    category: Optional[str] = None,
    accessibility_status: Optional[str] = None,
    indoor_alternative: Optional[bool] = None,
    opening_status: Optional[str] = None,
    min_fuji_view_rating: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search and filter places directly from the canonical SQLite database."""
    sql = "SELECT * FROM places WHERE 1=1"
    params: List[Any] = []

    if query:
        sql += " AND (name_ja LIKE ? OR name_en LIKE ? OR sub_category LIKE ?)"
        like_str = f"%{query}%"
        params.extend([like_str, like_str, like_str])

    if category:
        sql += " AND primary_category = ?"
        params.append(category)

    if accessibility_status:
        sql += " AND accessibility_status = ?"
        params.append(accessibility_status)

    if indoor_alternative is not None:
        sql += " AND indoor_alternative = ?"
        params.append(1 if indoor_alternative else 0)

    if opening_status:
        sql += " AND opening_status = ?"
        params.append(opening_status)

    if min_fuji_view_rating is not None:
        sql += " AND fuji_view_rating >= ?"
        params.append(min_fuji_view_rating)

    sql += " ORDER BY fuji_view_rating DESC, name_ja ASC LIMIT ? OFFSET ?;"
    params.extend([limit, offset])

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_place_by_id(place_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve single place by its canonical place_id."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM places WHERE place_id = ?;", (place_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


@router.get("", response_model=List[Place])
def list_places(
    query: Optional[str] = Query(None, description="Free text search on Japanese/English name or subcategory"),
    category: Optional[str] = Query(None, description="Filter by primary_category (viewpoint, museum, shrine, etc.)"),
    accessibility_status: Optional[str] = Query(None, description="Filter by accessibility_status"),
    indoor_alternative: Optional[bool] = Query(None, description="Filter places suitable as rainy day alternatives"),
    opening_status: Optional[str] = Query(None, description="Filter by opening status"),
    min_fuji_view_rating: Optional[int] = Query(None, ge=1, le=5, description="Minimum Fuji view rating (1-5)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List and filter verified places."""
    places = search_places_db(
        query=query,
        category=category,
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
