import os
import sys
import pytest

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import db.database
# Override the database path globally for all tests to protect production data
TEST_DB_PATH = os.path.join(os.path.dirname(__file__), 'kcs_documents_test.db')
db.database.DB_PATH = TEST_DB_PATH

@pytest.fixture(scope="session", autouse=True)
def test_db_session():
    from db.database import init_db, seed_kcs_catalog
    
    # Ensure any legacy test db is removed
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass
            
    # Initialize and seed the isolated test database
    init_db()
    seed_kcs_catalog()
    
    yield
    
    # Cleanup after the test session finishes
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass
