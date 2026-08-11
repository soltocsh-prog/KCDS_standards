import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db.database import get_db_connection
from services.document_orchestrator import DocumentOrchestrator

app = FastAPI(title="KCS Automation API")

# Add CORS middleware to allow React frontend (Vite defaults to 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/kcs/documents")
def get_documents():
    """
    Retrieve the list of cached KCS documents from the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT code, name, version, has_content, updated_at FROM kcs_documents ORDER BY code ASC")
    rows = cursor.fetchall()
    conn.close()
    
    documents = [dict(row) for row in rows]
    return {"documents": documents}

from fastapi.responses import FileResponse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

class MergeRequest(BaseModel):
    codes: list[str]

@app.post("/api/kcs/merge")
async def merge_documents(request: MergeRequest):
    """
    Receives a list of KCS codes and orchestrates the merging process.
    """
    orchestrator = DocumentOrchestrator()
    result = await orchestrator.merge_documents(request.codes)
    return result


@app.get("/api/kcs/download/{filename}")
def download_file(filename: str):
    """
    Serves the generated HWP document for download.
    """
    file_path = os.path.join(OUTPUT_DIR, filename)
    # Security check to prevent directory traversal
    normalized_path = os.path.abspath(file_path)
    if not normalized_path.startswith(os.path.abspath(OUTPUT_DIR)):
        raise HTTPException(status_code=400, detail="Invalid file path")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path, filename=filename, media_type="application/octet-stream")


import json

class PresetCreate(BaseModel):
    name: str
    codes: list[str]

@app.get("/api/kcs/presets")
def get_presets():
    """
    Retrieve all saved presets (Add-on feature).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, codes_json, created_at FROM kcs_presets ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    presets = []
    for row in rows:
        preset = dict(row)
        preset['codes'] = json.loads(preset['codes_json'])
        del preset['codes_json']
        presets.append(preset)
        
    return {"presets": presets}

@app.post("/api/kcs/presets")
def create_preset(request: PresetCreate):
    """
    Save a new preset (Add-on feature).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    codes_json = json.dumps(request.codes)
    cursor.execute(
        "INSERT INTO kcs_presets (name, codes_json) VALUES (?, ?)",
        (request.name, codes_json)
    )
    preset_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": preset_id, "name": request.name, "message": "Preset saved successfully"}

@app.delete("/api/kcs/presets/{preset_id}")
def delete_preset(preset_id: int):
    """
    Delete a preset (Add-on feature).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM kcs_presets WHERE id = ?", (preset_id,))
    conn.commit()
    conn.close()
    return {"message": "Preset deleted successfully"}

