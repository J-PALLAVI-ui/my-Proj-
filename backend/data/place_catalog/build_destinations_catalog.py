"""
FujiNova Canonical Catalog Assembly & Verification Script.

Generates the unified collection of 235+ destinations, ensuring:
- All 35 existing seed records are 100% preserved
- At least 100 verified Famous destinations
- At least 100 verified Hidden Gem destinations
- Strict schema validation with Pydantic Place model
- Idempotent SQLite database seeding
"""
import os
import sys
import json
import logging
from typing import Dict, Any, List

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.data.seed_data import PLACES_SEED_DATA
from backend.app.models.place import Place

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("fujinova.builder")

OUTPUT_JSON = os.path.join(os.path.dirname(__file__), "canonical_destinations.json")
OUTPUT_PY = os.path.abspath(os.path.join(os.path.dirname(__file__), "../expanded_places_data.py"))
