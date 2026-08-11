import sys
import os
from pathlib import Path

target_dir = Path(r"c:\Users\solto\OneDrive\문서\KCS_Automation")
sys.path.insert(0, str(target_dir))

modules_to_test = [
    "main",
    "generate_cli",
    "db.database",
    "services.ai_recommender",
    "services.document_generator",
    "services.document_orchestrator",
    "services.hml_bridge",
    "services.hml_generator",
    "services.kcsc_api_client",
    "services.jinja2_generator.jinja2_hml_generator",
]

print("Testing runtime imports from KCS_Automation root...")
success_count = 0
for mod in modules_to_test:
    try:
        __import__(mod)
        print(f"[SUCCESS] Import '{mod}'")
        success_count += 1
    except Exception as e:
        print(f"[FAIL] Import '{mod}': {e}")

print(f"\nResults: {success_count}/{len(modules_to_test)} modules imported successfully.")
