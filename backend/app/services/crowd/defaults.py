"""Deterministic fallback popularity for destinations without a hand-calibrated crowd profile.

Previously every un-profiled destination (most of the 237) received the identical crowd score,
which made the crowd filter and quiet-preference ranking meaningless.  The fallback now derives
from the canonical database (discovery type, Fuji view rating) so results differ per place.
All values remain SIMULATED / FORECAST – never live telemetry.
"""
from functools import lru_cache
from typing import Dict, Any


@lru_cache(maxsize=1)
def _meta() -> Dict[str, Dict[str, Any]]:
    try:
        from backend.app.core.database import get_db_connection
        with get_db_connection() as conn:
            rows = conn.execute(
                "SELECT place_id, discovery_type, fuji_view_rating, primary_category, popularity_classification FROM places"
            ).fetchall()
        return {r["place_id"]: dict(r) for r in rows}
    except Exception:
        return {}


def clear_cache() -> None:
    _meta.cache_clear()


def default_popularity(place_id: str) -> int:
    """Return a 0-100 high-scenario popularity score for an un-profiled place."""
    m = _meta().get(place_id)
    if not m:
        return 35
    base = 58 if m.get("discovery_type") == "FAMOUS" else 26
    rating = m.get("fuji_view_rating") or 3
    base += (rating - 3) * 4
    cat = m.get("primary_category")
    if cat in ("onsen", "park"):
        base += 3
    if cat in ("museum", "shrine"):
        base -= 2
    pop = str(m.get("popularity_classification") or "").lower()
    if "high" in pop or "major" in pop:
        base += 10
    elif "low" in pop or "hidden" in pop:
        base -= 6
    # deterministic per-place jitter (0-9) so neighbours are not identical
    jitter = sum(ord(c) for c in place_id) % 10
    return int(max(8, min(95, base + jitter - 4)))
