import difflib
import sys

sys.stdout.reconfigure(encoding='utf-8')

def analyze_diff(path1, path2, label):
    print(f"==================== ANALYSIS FOR {label} ====================")
    with open(path1, 'r', encoding='utf-8') as f1, open(path2, 'r', encoding='utf-8') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()
    
    print(f"File 1 ({path1}): {len(lines1)} lines")
    print(f"File 2 ({path2}): {len(lines2)} lines")
    
    # Print head of File 1
    print("\n--- HEAD OF FILE 1 (Soltovity) ---")
    for l in lines1[:15]:
        print(l.rstrip())
        
    print("\n--- HEAD OF FILE 2 (KCS_Automation) ---")
    for l in lines2[:15]:
        print(l.rstrip())

analyze_diff(r"c:\Users\solto\OneDrive\문서\Soltovity\CONTEXT.md", r"c:\Users\solto\OneDrive\문서\KCS_Automation\CONTEXT.md", "CONTEXT.md")
print("\n" + "="*60 + "\n")
analyze_diff(r"c:\Users\solto\OneDrive\문서\Soltovity\migration_guide.md", r"c:\Users\solto\OneDrive\문서\KCS_Automation\migration_guide.md", "migration_guide.md")
