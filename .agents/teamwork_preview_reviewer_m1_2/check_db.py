import sqlite3
import os

db_dir = r"c:\Users\solto\OneDrive\문서\KCS_Automation\db"
dbs = ['kcs.db', 'kcs_documents.db', 'kcsc.db']

for db_name in dbs:
    db_path = os.path.join(db_dir, db_name)
    print(f"=== Testing {db_name} ===")
    if not os.path.exists(db_path):
        print(f"ERROR: {db_path} does not exist!")
        continue
    size = os.path.getsize(db_path)
    print(f"File size: {size} bytes")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA integrity_check;")
    res = cursor.fetchone()
    print(f"Integrity check: {res[0]}")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables: {tables}")
    for table in tables:
        tname = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {tname};")
        cnt = cursor.fetchone()[0]
        print(f"  Table '{tname}' count: {cnt}")
    conn.close()

# Also check database.py
db_py = os.path.join(db_dir, 'database.py')
print(f"=== Testing database.py ===")
print(f"Exists: {os.path.exists(db_py)}, Size: {os.path.getsize(db_py)} bytes")
