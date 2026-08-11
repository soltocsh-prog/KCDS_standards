import os
import re

kcs_dir = r"c:\Users\solto\OneDrive\문서\KCS_Automation"
solt_dir = r"c:\Users\solto\OneDrive\문서\Soltovity"
project_md = r"c:\Users\solto\OneDrive\문서\Soltovity\PROJECT.md"

print("=== 1. ALL FILES IN KCS_AUTOMATION UTF-8 & BOM SCAN ===")
all_kcs_files = []
bom_files = []
decode_err_files = []

for root, dirs, files in os.walk(kcs_dir):
    # skip .git if present
    if '.git' in root:
        continue
    for f in files:
        full_p = os.path.join(root, f)
        rel_p = os.path.relpath(full_p, kcs_dir).replace('\\', '/')
        all_kcs_files.append(rel_p)
        with open(full_p, 'rb') as fp:
            content = fp.read()
        if content.startswith(b'\xef\xbb\xbf'):
            bom_files.append(rel_p)
        try:
            content.decode('utf-8')
        except Exception as e:
            decode_err_files.append((rel_p, str(e)))

print(f"Total files in KCS_Automation: {len(all_kcs_files)}")
print(f"BOM files: {bom_files}")
print(f"Decode error files: {decode_err_files}")

print("\n=== 2. PROJECT.MD TREE vs ACTUAL FILES IN KCS_AUTOMATION ===")

with open(project_md, 'r', encoding='utf-8') as f:
    project_content = f.read()

# Extract tree block from PROJECT.md
tree_match = re.search(r'```\nKCS_Automation/\n(.*?)```', project_content, re.DOTALL)
if tree_match:
    tree_text = tree_match.group(1)
    print("Found tree block in PROJECT.md.")
    
    # Parse items in tree
    # Lines look like: ├── main.py                     # description
    # or │   ├── database.py
    # Let's extract paths
    tree_lines = tree_text.strip().split('\n')
    
    expected_paths = []
    current_path = []
    
    # Simple manual list of expected relative file/dir paths from the tree block:
    # ├── main.py
    # ├── generate_cli.py
    # ├── requirements.txt
    # ├── run_services.bat
    # ├── README.md
    # ├── CONTEXT.md
    # ├── migration_guide.md
    # ├── docs/
    # │   ├── REQUIREMENTS.md
    # │   └── samples/
    # │       ├── kcs_142010_api_response.json
    # │       └── kcs_14_20_10.json
    # ├── db/
    # │   ├── database.py
    # │   ├── kcs.db
    # │   ├── kcs_documents.db
    # │   └── kcsc.db
    # ├── services/
    # │   ├── document_orchestrator.py
    # │   ├── hml_bridge.py
    # │   ├── hml_generator.py
    # │   ├── hml_generator_recovered.py
    # │   ├── kcsc_api_client.py
    # │   ├── ai_recommender.py
    # │   ├── document_generator.py
    # │   └── jinja2_generator/
    # │       ├── jinja2_hml_generator.py
    # │       └── templates/
    # │           └── base_template.hml.j2
    # ├── templates/
    # │   ├── base_template.hml
    # │   ├── base_template2.hml
    # │   └── table_snippet.xml.j2
    # └── tests/
    #     ├── conftest.py
    #     ├── test_ai_recommendation.py
    #     ├── test_api_endpoints.py
    #     ├── test_database.py
    #     ├── test_document_generation.py
    #     ├── test_hml_bridge.py
    #     ├── test_hml_generator.py
    #     ├── test_hml_table_image_deep_dive.py
    #     ├── test_jinja2_hml_generator.py
    #     ├── test_kcsc_api.py
    #     └── features/
    #         ├── ai_recommendation.feature
    #         ├── document_generation.feature
    #         └── kcsc_api.feature
    
    # Let's extract filenames from tree lines
    tree_files = []
    for line in tree_lines:
        clean_line = re.sub(r'#.*$', '', line).strip()
        clean_line = re.sub(r'^[│├└──\s]+', '', clean_line).strip()
        if clean_line and not clean_line.endswith('/'):
            tree_files.append(clean_line)
    
    print(f"Extracted {len(tree_files)} file entries from tree block.")
    
    # Check if each tree file exists in KCS_Automation
    missing_from_disk = []
    actual_file_names = set(os.path.basename(p) for p in all_kcs_files)
    for tf in tree_files:
        if tf not in actual_file_names:
            missing_from_disk.append(tf)
            
    print(f"Tree items missing from disk: {missing_from_disk}")
    
    # Check if any actual files in KCS_Automation (except README.md if planned M3) are missing from tree
    extra_on_disk = []
    for rel_p in all_kcs_files:
        fname = os.path.basename(rel_p)
        if fname not in tree_files:
            extra_on_disk.append(rel_p)
            
    print(f"Actual files on disk not in tree block: {extra_on_disk}")

else:
    print("ERROR: Could not find tree block in PROJECT.md")
