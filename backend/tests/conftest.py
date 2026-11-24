"""Pytest Configuration and Test Fixtures."""
import os
import sys
import tempfile
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.core.config import settings
from backend.app.core.database import init_db, get_db_path
from backend.data.seed_places import seed_database
from backend.app.main import app


@pytest.fixture(scope="session", autouse=True)
def setup_main_test_db():
    """Ensure the default database for TestClient is initialized and seeded once per test session."""
    try:
        init_db()
        seed_database()
    except Exception:
        # DB already initialized and seeded
        pass


@pytest.fixture(scope="session")
def test_db():
    """Create an isolated temporary SQLite database populated with the 35 verified seed places."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    init_db(db_path)
    seed_database(db_path)

    yield db_path

    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def client():
    """FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client
