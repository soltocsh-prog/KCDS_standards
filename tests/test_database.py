import sqlite3
import os
import pytest
import sys

# Add backend directory to sys.path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.database import get_db_connection, init_db

def test_database_schema_expansion():
    """
    TDD Test: Verify that the database schema has been expanded
    with 'has_content' and 'content_json' columns.
    """
    # Re-initialize DB to ensure schema is created
    init_db()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(kcs_documents)")
    columns = {row['name']: row['type'] for row in cursor.fetchall()}
    conn.close()
    
    assert "has_content" in columns, "has_content column is missing in kcs_documents table"
    assert "content_json" in columns, "content_json column is missing in kcs_documents table"
    
    # Check default type/value for has_content
    # Depending on sqlite definition, it might be INTEGER/BOOLEAN
    assert columns["has_content"] in ["INTEGER", "BOOLEAN"]

def test_database_catalog_seeding():
    """
    TDD Test: Verify that seed_kcs_catalog() populates the catalog
    and initializes has_content to 0.
    """
    # Import the seeding function (it will be implemented in database.py)
    from db.database import seed_kcs_catalog
    
    # 1. Clear database to test fresh seeding
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM kcs_documents")
    conn.commit()
    conn.close()
    
    # 2. Run seeding
    seed_kcs_catalog()
    
    # 3. Verify that documents have been seeded
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM kcs_documents")
    count = cursor.fetchone()[0]
    
    # Seeding should populate at least the offline fallback list or KCSC catalog (e.g. > 5 items)
    assert count > 5, f"Seeding failed, only {count} documents in database"
    
    # Verify that a specific header like "10 00 00" exists
    cursor.execute("SELECT name, has_content, content_json FROM kcs_documents WHERE code = ?", ("10 00 00",))
    row = cursor.fetchone()
    
    assert row is not None, "Category header '10 00 00' was not seeded"
    assert row["has_content"] == 0, f"Expected initial has_content=0, got {row['has_content']}"
    assert row["content_json"] is None, f"Expected initial content_json=None, got {row['content_json']}"
    
    conn.close()
