"""FujiNova Health & Diagnostics Router."""
from fastapi import APIRouter, status
from backend.app.core.config import settings
from backend.app.core.database import get_db_connection

router = APIRouter(prefix="/api/v1", tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Verify backend API and database readiness."""
    db_status = "disconnected"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            if cursor.fetchone()[0] == 1:
                db_status = "connected (SQLite WAL)"
    except Exception as e:
        db_status = f"error: {str(e)}"

    is_ok = db_status == "connected (SQLite WAL)"
    return {
        "status": "ok" if is_ok else "degraded",
        "database": db_status,
        "environment": settings.FUJINOVA_ENV,
        "primary_model": settings.FUJINOVA_PRIMARY_MODEL,
        "fallback_model_enabled": settings.ENABLE_OPENAI_FALLBACK,
        "openai_fallback_enabled": settings.ENABLE_OPENAI_FALLBACK
    }
