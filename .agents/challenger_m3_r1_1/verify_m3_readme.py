import os
import re
import sys

README_PATH = r"c:\Users\solto\OneDrive\문서\KCS_Automation\README.md"
BASE_DIR = r"c:\Users\solto\OneDrive\문서\KCS_Automation"

def test_1_exists_and_non_empty():
    print("=== Test 1: README.md exists and non-empty ===")
    if not os.path.exists(README_PATH):
        print("FAIL: README.md does not exist.")
        return False
    size = os.path.getsize(README_PATH)
    print(f"README.md size: {size} bytes")
    if size == 0:
        print("FAIL: README.md is empty.")
        return False
    print("PASS: Test 1 passed.\n")
    return True

def parse_tree_from_readme(content):
    tree_match = re.search(r"```\s*\n(KCS_Automation/.*?)\n```", content, re.DOTALL)
    if not tree_match:
        print("FAIL: Could not find tree block in README.md")
        return []
    
    lines = tree_match.group(1).splitlines()
    paths = []
    stack = [BASE_DIR] # (indent_level, directory_path)
    
    # Root line: KCS_Automation/
    # We strip comments from each line
    for line in lines[1:]:
        # Remove comments starting with #
        code_part = line.split('#')[0]
        if not code_part.strip():
            continue
        
        # Calculate indentation / hierarchy depth based on tree characters
        # Tree connectors: ├──, └──, │
        # Clean line to find relative path component
        # Find position where entry name starts
        m = re.search(r"([├└]──\s*|│\s*)+", code_part)
        if not m:
            continue
        
        prefix = code_part[:m.end()]
        name = code_part[m.end():].strip()
        if not name:
            continue
        
        # Calculate depth by counting prefix components
        # 4 spaces per depth level usually
        # ├── at indent 0: len of prefix before ├── is 0 -> depth 1
        # │   ├── at indent 4: prefix before ├── is │   (4 chars) -> depth 2
        # │   │   ├── at indent 8: 8 chars -> depth 3
        indent_str = prefix
        # count occurrences of ├── or └──
        # We can also compute indent by counting leading characters / 4
        # Let's see: prefix like '├── ' has length 4. '│   ├── ' has length 8. '│   │   ├── ' has length 12.
        depth = len(prefix) // 4
        
        # Adjust stack to depth
        # stack has BASE_DIR at index 0 (depth 0)
        # So parent dir is stack[depth-1] if root is stack[0]
        # Wait, if depth is 1 (top level files in KCS_Automation), parent is BASE_DIR (stack[0]).
        # If depth is 2 (e.g. db/database.py), parent is stack[1] (e.g. KCS_Automation/db).
        
        # Maintain stack
        while len(stack) > depth:
            stack.pop()
            
        parent = stack[-1]
        is_dir = name.endswith('/')
        clean_name = name.rstrip('/')
        full_path = os.path.join(parent, clean_name)
        paths.append((full_path, is_dir, line.strip()))
        
        if is_dir:
            stack.append(full_path)
            
    return paths

def test_2_cross_check_ascii_tree():
    print("=== Test 2: Cross-check every path in ASCII tree against actual files on disk ===")
    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
        
    paths = parse_tree_from_readme(content)
    print(f"Parsed {len(paths)} tree entries from README.md")
    
    missing_count = 0
    for path, is_dir, orig_line in paths:
        exists = os.path.exists(path)
        if is_dir:
            is_correct_type = os.path.isdir(path)
        else:
            is_correct_type = os.path.isfile(path)
            
        status = "OK" if (exists and is_correct_type) else "MISSING/INVALID"
        if status != "OK":
            missing_count += 1
            print(f"[{status}] {path} (from: {orig_line})")
        else:
            print(f"[OK] {path}")
            
    if missing_count > 0:
        print(f"FAIL: {missing_count} paths in ASCII tree do not exist on disk!")
        return False
    print("PASS: All tree entries exist on disk.\n")
    return True

def test_3_forbidden_strings():
    print("=== Test 3: Check zero occurrences of 'Soltovity', 'backend/', or 'scratch_' ===")
    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
        
    forbidden = ['Soltovity', 'backend/', 'scratch_']
    failed = False
    for item in forbidden:
        count = content.count(item)
        if count > 0:
            print(f"FAIL: Found {count} occurrences of forbidden string '{item}'")
            failed = True
        else:
            print(f"PASS: 0 occurrences of '{item}'")
            
    if failed:
        return False
    print("PASS: Test 3 passed.\n")
    return True

def test_4_origin_note():
    print("=== Test 4: Check origin note 'echo \"# -\"' or '# -' exists in README.md ===")
    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
        
    has_echo = 'echo "# -"' in content
    has_hash_dash = '# -' in content
    
    print(f"Contains 'echo \"# -\"': {has_echo}")
    print(f"Contains '# -': {has_hash_dash}")
    
    if has_echo or has_hash_dash:
        print("PASS: Test 4 passed.\n")
        return True
    else:
        print("FAIL: Neither 'echo \"# -\"' nor '# -' origin note found in README.md")
        return False

def main():
    t1 = test_1_exists_and_non_empty()
    t2 = test_2_cross_check_ascii_tree()
    t3 = test_3_forbidden_strings()
    t4 = test_4_origin_note()
    
    if t1 and t2 and t3 and t4:
        print("ALL TESTS PASSED - VERDICT: APPROVE")
        sys.exit(0)
    else:
        print("TESTS FAILED - VERDICT: REJECT")
        sys.exit(1)

if __name__ == "__main__":
    main()
