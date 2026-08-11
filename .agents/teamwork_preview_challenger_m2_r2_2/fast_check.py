import os

kcs_dir = r"c:\Users\solto\OneDrive\문서\KCS_Automation"
solt_dir = r"c:\Users\solto\OneDrive\문서\Soltovity"

def check_md_and_json(base_dir, name):
    print(f"=== CHECKING {name} MD/JSON/DOC FILES ===")
    targets = []
    for root, dirs, files in os.walk(base_dir):
        # skip git, agents, venv, pycache, etc.
        dirs[:] = [d for d in dirs if d not in ('.git', '.agents', '__pycache__', '.pytest_cache', 'venv', '.venv')]
        for f in files:
            if f.endswith(('.md', '.json', '.txt')):
                targets.append(os.path.join(root, f))
                
    boms = []
    errors = []
    for fp in targets:
        rel = os.path.relpath(fp, base_dir)
        with open(fp, 'rb') as f:
            b = f.read()
        if b.startswith(b'\xef\xbb\xbf'):
            boms.append(rel)
        try:
            b.decode('utf-8')
        except Exception as e:
            errors.append((rel, str(e)))
            
    print(f"Total files checked: {len(targets)}")
    print(f"BOM count: {len(boms)}")
    if boms:
        print(f"BOM files: {boms}")
    print(f"Decode errors: {len(errors)}")
    if errors:
        for r, err in errors:
            print(f"  {r}: {err}")

check_md_and_json(kcs_dir, "KCS_Automation")
check_md_and_json(solt_dir, "Soltovity")
