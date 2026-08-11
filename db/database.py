import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'kcs_documents.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if table exists and inspect columns
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kcs_documents'")
    table_exists = cursor.fetchone()
    
    recreate = False
    if table_exists:
        cursor.execute("PRAGMA table_info(kcs_documents)")
        columns = [row['name'] for row in cursor.fetchall()]
        if 'has_content' not in columns or 'content_json' not in columns:
            recreate = True
            
    if recreate:
        cursor.execute("DROP TABLE kcs_documents")
        table_exists = False
        
    if not table_exists or recreate:
        # Create table for documents with content_json and has_content
        cursor.execute('''
            CREATE TABLE kcs_documents (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT,
                content_json TEXT,
                has_content BOOLEAN DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
    # Create kcs_presets table if it doesn't exist (Add-on feature)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kcs_presets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            codes_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def seed_kcs_catalog():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Fetch from KCSC API
    # Import api client dynamically to avoid circular dependency
    from services.kcsc_api_client import KcscApiClient
    api = KcscApiClient()
    
    metadata = {}
    try:
        metadata = api.get_all_kcs_metadata()
    except Exception as e:
        print(f"Failed to fetch KCS metadata from API during seeding: {e}")
        
    # 2. Insert into database
    if metadata:
        for code, info in metadata.items():
            # Code from CodeList api is like "101005"
            # Format to "XX XX XX" format for display
            if len(code) == 6:
                formatted_code = f"{code[0:2]} {code[2:4]} {code[4:6]}"
            else:
                formatted_code = code
                
            cursor.execute('''
                INSERT OR IGNORE INTO kcs_documents (code, name, version, has_content)
                VALUES (?, ?, ?, 0)
            ''', (formatted_code, info.get("name"), info.get("version")))
        conn.commit()
    else:
        # 3. Fallback offline seeding if API is unavailable or returns empty
        fallback_docs = [
            ("10 00 00", "공통공사", "2025"),
            ("10 10 05", "공사일반", "2025"),
            ("10 10 10", "공무행정요건", "2025"),
            ("10 10 15", "품질관리", "2025"),
            ("10 10 20", "자재관리", "2025"),
            ("10 10 25", "안전 및 보건 관리", "2025"),
            ("10 10 30", "환경관리", "2025"),
            ("10 10 35", "시공 및 준공요건", "2025"),
            ("10 20 05", "입지환경조사", "2025"),
            ("10 20 10", "해상조사", "2025"),
            ("11 00 00", "지반공사", "2025"),
            ("11 10 05", "지반공사 일반", "2025"),
            ("21 00 00", "가설공사", "2025"),
            ("40 10 00", "가설공사 일반", "2025"),
            ("40 20 00", "비계 및 안전시설물", "2025")
        ]
        for doc in fallback_docs:
            cursor.execute('''
                INSERT OR IGNORE INTO kcs_documents (code, name, version, has_content)
                VALUES (?, ?, ?, 0)
            ''', doc)
        conn.commit()
        
    conn.close()

# Initialize the DB when this module is imported
init_db()
try:
    # Check if table is empty before calling seed
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM kcs_documents")
    count = c.fetchone()[0]
    conn.close()
    if count == 0:
        seed_kcs_catalog()
except Exception as e:
    print(f"Auto-seeding failed on startup: {e}")
