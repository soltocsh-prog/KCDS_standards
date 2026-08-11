import os
import sys

kcs_path = r"c:\Users\solto\OneDrive\문서\KCS_Automation"
solt_path = r"c:\Users\solto\OneDrive\문서\Soltovity"

docs_to_check = [
    os.path.join(kcs_path, 'CONTEXT.md'),
    os.path.join(kcs_path, 'migration_guide.md'),
    os.path.join(kcs_path, 'docs', 'REQUIREMENTS.md'),
    os.path.join(kcs_path, 'docs', 'samples', 'kcs_142010_api_response.json'),
    os.path.join(kcs_path, 'docs', 'samples', 'kcs_14_20_10.json'),
    os.path.join(solt_path, 'CONTEXT.md'),
    os.path.join(solt_path, 'migration_guide.md'),
    os.path.join(solt_path, 'PROJECT.md')
]

# Also check README.md in KCS_Automation if exists
if os.path.exists(os.path.join(kcs_path, 'README.md')):
    docs_to_check.append(os.path.join(kcs_path, 'README.md'))

print(f"Checking {len(docs_to_check)} documents...")

bom_found = []
utf8_errors = []
missing_files = []

for filepath in docs_to_check:
    if not os.path.exists(filepath):
        missing_files.append(filepath)
        print(f"MISSING: {filepath}")
        continue
    
    with open(filepath, 'rb') as f:
        content = f.read()
    
    # Check UTF-8 BOM (\xef\xbb\xbf)
    has_bom = content.startswith(b'\xef\xbb\xbf')
    if has_bom:
        bom_found.append(filepath)
        
    # Check strict UTF-8 decode
    try:
        text = content.decode('utf-8')
        print(f"OK: {os.path.basename(filepath)} ({len(content)} bytes, BOM={has_bom})")
    except Exception as e:
        utf8_errors.append((filepath, str(e)))
        print(f"FAIL UTF-8: {os.path.basename(filepath)} -> {e}")

print("\n=== SUMMARY ===")
print(f"Total checked: {len(docs_to_check)}")
print(f"Missing files: {len(missing_files)}")
print(f"BOM found count: {len(bom_found)}")
print(f"UTF-8 decode errors: {len(utf8_errors)}")
