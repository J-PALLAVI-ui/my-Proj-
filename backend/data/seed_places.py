"""FujiNova Database Seed Script: Ingests 35 verified places into SQLite."""
import sys
import logging
from typing import Optional
from backend.app.core.database import init_db, get_db_connection
from backend.data.seed_data import PLACES_SEED_DATA

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("fujinova.seed")


def seed_database(db_path: Optional[str] = None) -> int:
    """Populate database with verified seed places."""
    logger.info("Initializing database schema...")
    init_db(db_path)

    insert_query = """
    INSERT OR REPLACE INTO places (
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
    );
    """

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        for place in PLACES_SEED_DATA:
            cursor.execute(insert_query, place)
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM places;")
        count = cursor.fetchone()[0]
        logger.info(f"Successfully seeded {count} places into database.")

        # Quick breakdown
        cursor.execute("SELECT primary_category, COUNT(*) FROM places GROUP BY primary_category;")
        for row in cursor.fetchall():
            logger.info(f"  - Category '{row[0]}': {row[1]} places")

        cursor.execute("SELECT accessibility_status, COUNT(*) FROM places GROUP BY accessibility_status;")
        for row in cursor.fetchall():
            logger.info(f"  - Accessibility '{row[0]}': {row[1]} places")

        return count


if __name__ == "__main__":
    count = seed_database()
    if count != 35:
        logger.error(f"Expected 35 places, found {count}!")
        sys.exit(1)
    logger.info("Database seeding completed successfully.")
