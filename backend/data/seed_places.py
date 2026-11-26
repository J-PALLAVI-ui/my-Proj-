"""FujiNova Database Seed Script: Idempotent ingestion of 235+ verified destinations into SQLite."""
import os
import sys
import shutil
import logging
from typing import Optional
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app.core.database import init_db, get_db_connection, get_db_path
from backend.data.seed_data import PLACES_SEED_DATA
from backend.data.expanded_places_data import EXPANDED_PLACES_DATA

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("fujinova.seed")


def create_db_backup(db_path: str):
    """Safely back up the database before executing seeding or migrations."""
    if os.path.exists(db_path) and os.path.getsize(db_path) > 0:
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(db_path)), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"fujinova_pre_seed_{timestamp}.db")
        shutil.copy2(db_path, backup_file)
        logger.info(f"Database backup created at {backup_file}")


def seed_database(db_path: Optional[str] = None) -> int:
    """Populate database with verified canonical seed places and expanded 200+ destination catalogue."""
    target_path = db_path or get_db_path()
    create_db_backup(target_path)
    logger.info("Initializing database schema...")
    init_db(target_path)

    # 1. First, insert canonical 35 seed records (preserving original provenance)
    insert_canonical_query = """
    INSERT INTO places (
        place_id, name_ja, name_en, latitude, longitude, coords_source,
        primary_category, sub_category, opening_status, opening_hours_text,
        opening_hours_source, general_admission_type, general_admission_fee_jpy,
        optional_activities_fee_desc, admission_fee_source, accessibility_status,
        accessibility_evidence, stair_step_count, accessibility_source,
        fuji_view_rating, indoor_alternative, provenance_tier, source_url,
        required_attribution, source_retrieval_date, last_verified_date
    ) VALUES (
        :place_id, :name_ja, :name_en, :latitude, :longitude, :coords_source,
        :primary_category, :sub_category, :opening_status, :opening_hours_text,
        :opening_hours_source, :general_admission_type, :general_admission_fee_jpy,
        :optional_activities_fee_desc, :admission_fee_source, :accessibility_status,
        :accessibility_evidence, :stair_step_count, :accessibility_source,
        :fuji_view_rating, :indoor_alternative, :provenance_tier, :source_url,
        :required_attribution, :source_retrieval_date, :last_verified_date
    )
    ON CONFLICT(place_id) DO NOTHING;
    """

    # 2. Insert or update extended attributes for all 237 destinations
    columns = [
        "place_id", "name_ja", "name_en", "alternate_names", "official_address",
        "municipality", "prefecture", "description", "short_description",
        "latitude", "longitude", "coords_source", "elevation_m", "region_id",
        "primary_category", "sub_category", "discovery_type", "popularity_classification",
        "seasonal_tags", "interests", "recommended_for", "opening_status",
        "opening_hours_text", "opening_hours_source", "seasonal_closure", "best_visit_months",
        "general_admission_type", "general_admission_fee_jpy", "optional_activities_fee_desc",
        "admission_fee_source", "fee_last_verified", "accessibility_status",
        "accessibility_evidence", "stair_step_count", "wheelchair_suitability",
        "accessibility_source", "image_url", "image_source_url", "image_attribution",
        "image_license", "image_alt_text", "image_verified_at", "photo_search_url",
        "nearest_bus_stops", "nearest_railway_stations", "gtfs_stop_ids",
        "transport_operators", "transit_access_status", "walking_distance_to_nearest_stop",
        "estimated_visit_duration_minutes", "fuji_view_rating", "best_time_to_visit",
        "indoor_alternative", "family_friendly", "elderly_friendly", "facilities_available",
        "expected_crowd_profile", "weekday_crowd_profile", "weekend_crowd_profile",
        "seasonal_crowd_profile", "crowd_prediction_method", "crowd_confidence",
        "provenance_tier", "source_url", "required_attribution", "source_retrieval_date",
        "last_verified_date"
    ]

    col_names = ", ".join(columns)
    col_params = ", ".join(f":{c}" for c in columns)
    update_clause = ", ".join([
        f"{c} = COALESCE(excluded.{c}, places.{c})"
        for c in columns if c != "place_id"
    ])

    insert_expanded_query = f"""
    INSERT INTO places ({col_names})
    VALUES ({col_params})
    ON CONFLICT(place_id) DO UPDATE SET
        {update_clause};
    """

    with get_db_connection(target_path) as conn:
        cursor = conn.cursor()

        # Step 1: Ensure canonical 35 places exist
        for place in PLACES_SEED_DATA:
            cursor.execute(insert_canonical_query, place)
        conn.commit()

        # Step 2: Ingest full expanded 237 catalog with safe field coalescing
        for place in EXPANDED_PLACES_DATA:
            # Build parameter dict with default None for any missing keys
            param_dict = {col: place.get(col, None) for col in columns}
            cursor.execute(insert_expanded_query, param_dict)
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM places;")
        count = cursor.fetchone()[0]
        logger.info(f"Successfully seeded {count} places into database.")

        # Breakdown by Discovery Type (FAMOUS vs HIDDEN_GEM)
        cursor.execute("SELECT discovery_type, COUNT(*) FROM places GROUP BY discovery_type;")
        for row in cursor.fetchall():
            logger.info(f"  - Discovery Type '{row[0]}': {row[1]} places")

        cursor.execute("SELECT primary_category, COUNT(*) FROM places GROUP BY primary_category;")
        for row in cursor.fetchall():
            logger.info(f"  - Category '{row[0]}': {row[1]} places")

        cursor.execute("SELECT accessibility_status, COUNT(*) FROM places GROUP BY accessibility_status;")
        for row in cursor.fetchall():
            logger.info(f"  - Accessibility '{row[0]}': {row[1]} places")

        return count


if __name__ == "__main__":
    count = seed_database()
    if count < 235:
        logger.error(f"Expected at least 235 places, found {count}!")
        sys.exit(1)
    logger.info(f"Database seeding completed successfully with {count} verified destinations.")
