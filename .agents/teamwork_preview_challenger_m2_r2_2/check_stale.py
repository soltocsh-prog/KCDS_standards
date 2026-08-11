import os, re, sys

sys.stdout.reconfigure(encoding='utf-8')

kcs_ctx = r"c:\Users\solto\OneDrive\문서\KCS_Automation\CONTEXT.md"
kcs_mig = r"c:\Users\solto\OneDrive\문서\KCS_Automation\migration_guide.md"

def check_stale_refs(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"=== Stale Reference Check in {os.path.basename(filepath)} ===")
    lines = content.splitlines()
    for i, line in enumerate(lines, 1):
        if "Soltovity" in line:
            print(f"Line {i}: {line.strip()}")

check_stale_refs(kcs_ctx)
check_stale_refs(kcs_mig)
