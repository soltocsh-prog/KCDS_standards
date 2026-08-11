from fastapi.testclient import TestClient
import pytest
import os
import sys

# Add backend directory to sys.path so we can import main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# We expect main.py to exist and have an 'app' instance
from main import app

client = TestClient(app)

def test_get_kcs_documents():
    """
    Test that the /api/kcs/documents endpoint returns a list of KCS documents,
    specifically ensuring it returns at least 2 KCS 21* documents as per requirements.
    """
    response = client.get("/api/kcs/documents")
    assert response.status_code == 200
    
    data = response.json()
    assert "documents" in data
    
    docs = data["documents"]
    assert len(docs) >= 2
    
    # Check that at least some documents are KCS 21* (가설공사) type
    kcs_21_docs = [doc for doc in docs if doc.get("code", "").startswith("21")]
    assert len(kcs_21_docs) >= 2, "Expected at least 2 KCS 21* documents"
    
    for doc in docs:
        assert "code" in doc
        assert "name" in doc

def test_merge_kcs_documents_success():
    """
    Test successful merging of multiple KCS documents.
    """
    payload = {"codes": ["21 10 00", "21 60 05"]}
    response = client.post("/api/kcs/merge", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "merged_document" in data
    assert "warnings" in data
    assert "download_url" in data
    assert data["download_url"] is not None
    assert data["download_url"].startswith("/api/kcs/download/merged_")
    
    # Check if page_break is inserted
    merged = data["merged_document"]
    # We expect Doc 1, Page Break, Doc 2. (Length = 3)
    assert len(merged) == 3
    assert merged[0]["code"] == "21 10 00"
    assert merged[1]["type"] == "page_break"
    assert merged[2]["code"] == "21 60 05"

def test_merge_kcs_documents_partial_success():
    """
    Test that invalid codes are skipped and warnings are returned.
    """
    payload = {"codes": ["21 10 00", "invalid_code"]}
    response = client.post("/api/kcs/merge", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    merged = data["merged_document"]
    # Only 1 document should be processed, no page break
    assert len(merged) == 1
    assert merged[0]["code"] == "21 10 00"
    
    # "invalid_code" should be in warnings
    assert "warnings" in data
    assert len(data["warnings"]) > 0
    assert any("invalid_code" in w or "not found" in w.lower() for w in data["warnings"])
    assert "download_url" in data
    assert data["download_url"] is not None



