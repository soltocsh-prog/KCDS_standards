import os

files_to_check = [
    (r"c:\Users\solto\OneDrive\문서\KCS_Automation\CONTEXT.md", "KCS CONTEXT.md"),
    (r"c:\Users\solto\OneDrive\문서\KCS_Automation\migration_guide.md", "KCS migration_guide.md"),
    (r"c:\Users\solto\OneDrive\문서\KCS_Automation\docs\REQUIREMENTS.md", "KCS REQUIREMENTS.md"),
    (r"c:\Users\solto\OneDrive\문서\KCS_Automation\docs\samples\kcs_142010_api_response.json", "KCS sample 1"),
    (r"c:\Users\solto\OneDrive\문서\KCS_Automation\docs\samples\kcs_14_20_10.json", "KCS sample 2"),
    (r"c:\Users\solto\OneDrive\문서\Soltovity\CONTEXT.md", "Soltovity CONTEXT.md"),
    (r"c:\Users\solto\OneDrive\문서\Soltovity\migration_guide.md", "Soltovity migration_guide.md"),
    (r"c:\Users\solto\OneDrive\문서\Soltovity\PROJECT.md", "Soltovity PROJECT.md"),
]

print("=== DETAILED DOC CHECK ===")
for path, label in files_to_check:
    if not os.path.exists(path):
        print(f"MISSING: [{label}] {path}")
        continue
    with open(path, 'rb') as f:
        data = f.read()
    bom = data.startswith(b'\xef\xbb\xbf')
    try:
        text = data.decode('utf-8')
        print(f"PASS: [{label}] size={len(data)} bytes, BOM={bom}, lines={len(text.splitlines())}")
    except Exception as e:
        print(f"FAIL: [{label}] UTF-8 error: {e}")

print("\n=== COMPARING CONTEXT.MD & MIGRATION_GUIDE.MD BETWEEN SOLTOVITY & KCS_AUTOMATION ===")

kcs_ctx_p = r"c:\Users\solto\OneDrive\문서\KCS_Automation\CONTEXT.md"
solt_ctx_p = r"c:\Users\solto\OneDrive\문서\Soltovity\CONTEXT.md"

kcs_mig_p = r"c:\Users\solto\OneDrive\문서\KCS_Automation\migration_guide.md"
solt_mig_p = r"c:\Users\solto\OneDrive\문서\Soltovity\migration_guide.md"

def read_utf8(p):
    with open(p, 'r', encoding='utf-8') as f:
        return f.read()

kcs_ctx = read_utf8(kcs_ctx_p)
solt_ctx = read_utf8(solt_ctx_p)

kcs_mig = read_utf8(kcs_mig_p)
solt_mig = read_utf8(solt_mig_p)

print(f"KCS CONTEXT.md length: {len(kcs_ctx)} chars | Soltovity CONTEXT.md length: {len(solt_ctx)} chars")
print(f"KCS migration_guide.md length: {len(kcs_mig)} chars | Soltovity migration_guide.md length: {len(solt_mig)} chars")

if kcs_ctx == solt_ctx:
    print("CONTEXT.md is IDENTICAL in both folders.")
else:
    print("CONTEXT.md DIFFERENCE detected! Investigating...")

if kcs_mig == solt_mig:
    print("migration_guide.md is IDENTICAL in both folders.")
else:
    print("migration_guide.md DIFFERENCE detected! Investigating...")
